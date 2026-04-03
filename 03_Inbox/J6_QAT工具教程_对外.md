# 背景
J6 QAT 工具较 J5 QAT 工具有较大的变化，在正式阅读此文档前，请先阅读相关文档：https://doc.oe.horizon.auto/guide/plugin/introduce.html
推荐重点阅读的章节：
1. 快速入门：https://doc.oe.horizon.auto/guide/plugin/qat_quickstart/qat_quickstart.html
1. QConfig 详解：https://doc.oe.horizon.auto/guide/plugin/user_guide/qconfig.html
1. prepare 详解：https://doc.oe.horizon.auto/guide/plugin/user_guide/prepare.html
1. 量化精度调优指南：https://doc.oe.horizon.auto/guide/plugin/user_guide/precision_tuning.html
本文以上述文档为基础，结合具体的使用示例介绍工具用法，希望能够使算法同学以更低的成本上手 QAT 工具。介绍的内容包括浮点模型改造， 校准，QAT，精度调优， 性能优化，一致性验证等。<text bgcolor="light-yellow">J6E/M部署仅需关注第2-7节，J6P部署还需关注第8节。</text>
# 浮点模型改造
##  插入QuantStub
在输入处插入`QuantStub`。`QuantStub`用于分割模型的不同部分，标志着部署部分的起点位置。
```python
class BaseHeNet(BaseModule):
    def __init__(...):
        ...
        # 如果知道输入的值域，推荐指定scale，避免scale统计方法在输入处就产生较大误差。
        # scale可以在构造QuantStub对象时指定，也可以通过qconfig指定fixed scale
        # 因为我们知道输入的值域为[-1, 1]，所以分子为1，又因为使用的是int8量化，所以分母为128。
        # 推荐对输入做0为中心的归一化操作，原因：
        # 1. 我们使用的是对称量化，如果输入值域只有正半轴，那么将浪费一半的量化表示空间
        # 2. 归一化输入训出的模型中，数值范围更小，对量化更友好。
        self.quant = QuantStub(scale=1/128)

    def forward(self, x):
        if isinstance(x, Sequence) and len(x) == 1:
            x = x[0]
        x = self.quant(x)
        x = self.patch_embed(x)
        ...
        return outs
```

## ** 插入DequantStub**
在输出处插入`DeQuantStub`。`DeQuantStub`用于分割模型的不同部分，标志着部署部分的结束位置。
```python
class RegLayer(nn.Module):
    def __init__(...):
        ...
        # 理论上多个输出可以共用一个dequant，但是推荐不共用，对后面查看debug结果更友好
        for i in range(len(self.task_heads)):
            self.add_module(
                "dequant%d" % (i), DeQuantStub()
            )

    def forward(self, x):
        ...
        for i, (_, task_head) in enumerate(self.task_heads.items()):
            out = task_head(reg_feat)
            out = getattr(self, "dequant%d" % (i))(out)
            if self.num_reg > 1:
                out = out.view(out.shape[0], out.shape[1], self.num_reg, -1)
            outs.append(out)
        return outs
```

<callout emoji="bulb" background-color="light-orange" border-color="light-orange">
部分老用户使用 <text bgcolor="light-yellow">eager 模式</text>，需要手动做算子替换（换 FloatFunctional 等）和融合（写 fuse_model 方法），此用法仍然兼容，但在新的 Plugin 中，我们更推荐使用更加易用的 jit-strip 模式，不需要手动算子替换和融合。<text bgcolor="light-yellow">除jit-strip模式，其他模式都不再维护。</text>
</callout>

##  算子替换（使用 jit / jit-strip 模式不用考虑）
QAT 需要在部分算子（不包括输出数值范围可根据输入数值范围推算出来的算子）前后插入伪量化节点，对于 function 类算子，这一点无法实现。需要将其替换为 FloatFunctional()，plugin 将在此 module 中插入伪量化节点。
```python
class MapQRTransformerDecoderLayer(nn.Module):
    def __init__(...):
        self.tgt_add0 = FloatFunctional()
        self.tgt_add1 = FloatFunctional()
        self.pos_add = FloatFunctional()
        self.ffn_add = FloatFunctional()

    def with_pos_embed(self, tensor, pos):
        return tensor if pos is None else self.pos_add.add(tensor, pos)

    def forward_ffn(self, tgt):
        tgt2 = self.linear2(self.dropout3(self.activation(self.linear1(tgt))))
        tgt = self.ffn_add.add(tgt, self.dropout4(tgt2))
        tgt = self.norm3(tgt)
        return tgt

    def forward(...):
        tgt = self.tgt_add0.add(tgt, tgt2)
        tgt = self.norm11(tgt)
        tgt2 = self.cross_attn(self.with_pos_embed(tgt.unsqueeze(2), query_pos).flatten(1, 2), value=src, reference_points=reference_points, spatial_shapes=src_spatial_shapes)
        # view这种function算子不需要替换
        tgt2 = tgt2.view(bs, n_queries, -1)
        tgt2 = self.output_proj(tgt2)
        tgt = self.tgt_add1.add(tgt, self.dropout2(tgt2))
        tgt = self.norm2(tgt)
        tgt = self.forward_ffn(tgt)
        return tgt
```

##  算子融合（使用 jit / jit-strip 模式不用考虑）
某些算子（conv，bn，add，relu）在部署时会被融合为一个算子，在 qat 阶段需要将其融合，避免在中间插入量化节点。如果没有做融合，对模型的精度和性能会产生轻微影响。
```python
class MapQRTransformerDecoderLayer(nn.Module):
    def __init__(...):
        ...
        self.output_proj = nn.Sequential(
            nn.Linear(d_model * num_pts_per_polyline, d_model * num_pts_per_polyline // 2),
            nn.ReLU(),
            nn.Linear(d_model * num_pts_per_polyline // 2, d_model),
            nn.ReLU(),
            nn.Linear(d_model, d_model),
        )
    def forward_ffn(self, tgt):
        tgt2 = self.linear2(self.dropout3(self.activation(self.linear1(tgt))))
        ...
        return tgt

    def fuse_model(self):
        fuse_list = ["output_proj.0", "output_proj.1"]
        torch.quantization.fuse_modules(self, fuse_list, inplace=True, fuser_func=fuser_func)

        fuse_list = ["output_proj.2", "output_proj.3"]
        torch.quantization.fuse_modules(self, fuse_list, inplace=True, fuser_func=fuser_func)

        fuse_list = ["linear1", "activation"]
        torch.quantization.fuse_modules(self, fuse_list, inplace=True, fuser_func=fuser_func)
```

# Prepare
prepare 是将浮点模型变为 calibration / qat 模型的过程。prepare 过程会进行获取模型计算图/算子替换/算子融合/插入伪量化节点/模型结构检查等操作。J6 QAT 工具只推荐大家使用 JIT_STRIP 模式。除 JIT_STRIP 模式外，其他模式都不再维护。
## 3.1 Plugin接口
```plaintext
import horizon_plugin_pytorch as horizon
qat_model = horizon.quantization.prepare(
    float_model,
    example_inputs=example_inputs, # 用于 trace 模型，获取计算图。
    qconfig_setter=(
        default_calibration_qconfig_setter, # qconfig 模板，用法见这里
    ),
    method=horizon.quantization.PrepareMethod.JIT_STRIP,  # 如果没有历史包袱，推荐使用 jit-strip，各模式区别见这里
)
```

## 3.3 QConfig
模型的量化方式由 qconfig 决定，在prepare qat / calibration 模型之前，需要先确定模型的 qconfig，prepare 根据 qconfig 插入量化节点。
```python
class QConfig(
    namedtuple("QConfig", ["activation", "weight", "input", "output"]),
    TorchQconfig,
):
```

最初是为了对齐 torch 社区，只有 activation 和 weight 相关的配置。社区最早的实现不考虑异构计算，所以只要每一个算子（包括 QuantStub）的输出是量化的，整个模型就是全部量化的。现在为了适配混合 fp16 / fp32，新增了 input 和 output 字段，output 字段与原先的 activation 字段语意一致。input / weight / output（activation）对应算子输入/权重/输出量化节点的配置。
QConfig 的展开介绍，见这里
### 3.3.1 FakeQuantize
对于 fake quantize，首先需要确定 observer，一般 qat 用 MinMaxObserver， calibration 用 MSEObserver（精调校准也可以用其他 observer），observer 都在 <text bgcolor="light-yellow">horizon_plugin_pytorch/quantization/observer_v2.py</text>，常用的参数包括 dtype / averaging_constant。
```python
from horizon_plugin_pytorch.quantization.qconfig import QConfig
from horizon_plugin_pytorch.quantization.fake_quantize import FakeQuantize
from horizon_plugin_pytorch.quantization.observer_v2 import MinMaxObserver, FixedScaleObserver, MSEObserver
from horizon_plugin_pytorch.dtype import qint8

fq_constructor_1 = FakeQuantize.with_args(
    observer=MinMaxObserver,   # 适用于 qat 阶段的 input / output / weight 和 calibration 阶段的 weight。
    averaging_constant=0.01,   # calibration 后进行 qat 时，可将 input / output 的 averaging_constant 置为 0 以固定 scale。
    dtype=qint8,  # 量化类型，考虑算子的支持情况进行设置。
    qscheme=torch.per_channel_symmetric,  # 只有 weight 支持 per channel 量化。
    ch_axis=0,  # per channel 量化时指定 channel。
)
```

不同的 observer 还有一些各自特有的参数，可以结合 observer 的参数注释进行调整，一般不是精度调优的重点。
```plaintext
class MSEObserver(ObserverBase):
    r"""MSE observer.

    Observer module for computing the quantization parameters based on the
    Mean Square Error (MSE) between the original tensor and the quantized one.

    This observer linear searches the quantization scales that minimize MSE.

    Args:
        stride: Searching stride. Larger value gives smaller search space,
            which means less computing time but possibly poorer accuracy.
            Default is 1. Suggests no greater than 20.
        averaging_constant: Averaging constant for min/max.
        ch_axis: Channel axis.
        dtype: Quantized data type.
        qscheme: Quantization scheme to be used.
        quant_min: Min quantization value. Will follow dtype if unspecified.
        quant_max: Max quantization value. Will follow dtype if unspecified.
        is_sync_quantize: If sync statistics when training with multiple
            devices.
        factory_kwargs: kwargs which are passed to factory functions for
            min_val and max_val.
        pow_quantization: Whether to use power-of-two quantization.
    """

    @typechecked
    def __init__(
        self,
        stride: int = 1,
        averaging_constant: float = 0.01,
        ch_axis: int = -1,
        dtype: Union[torch.dtype, QuantDType] = qint8,
        qscheme: torch.qscheme = torch.per_tensor_symmetric,
        quant_min: int = None,
        quant_max: int = None,
        is_sync_quantize: bool = True,
        factory_kwargs: Dict = None,
        memory_estimate_ratio: float = None,
        pow_quantization: bool = False,
    ):
```

### 3.3.2 FakeCast
FakeCast 用于标志浮点计算，常用参数只有 dtype。溢出时clip这些工具都会自动做。
```plaintext
import torch
from horizon_plugin_pytorch.quantization.qconfig import QConfig
from horizon_plugin_pytorch.quantization.fake_cast import FakeCast

qconfig = QConfig(
    input=FakeCast.with_args(dtype=torch.float16),
    ...
)
```

### 3.3.3 设置方法
<callout emoji="bulb" background-color="light-orange" border-color="light-orange">
1. 部分老用户习惯使用 set_qconfig 方法，<text bgcolor="light-yellow">此用法仍然兼容但不再维护，我们更推荐使用模板</text>。没有特殊需求，不要混用两种用法。使用 qconfig setter 时需确认模型中没有写 set_qconfig 方法。
1. 使用芯片浮点算力有一套新的 qconfig 模板流程，已经完成开发，但还需要优化且文档还不完善，因为 J6E/M 可用的浮点算力不多，不能像J6P一样大规模使用浮点，所以建议还是先用 qconfig 的方式配置少量浮点。J6P使用的浮点模板参考第8节
</callout>

```python
from horizon_plugin_pytorch.quantization.qconfig_template import (
    default_qat_qconfig_setter,
    sensitive_op_qat_8bit_weight_16bit_fixed_act_qconfig_setter, #固定激活，不固定权重
    ModuleNameQconfigSetter,
)

table = torch.load("output_0-0_dataindex_1_sensitive_ops.pt")

module_name_to_qconfig = {
    "op_1": get_qconfig(),
    "_generated_add_0": QConfig(
        output=FakeQuantize.with_args(
            observer=FixedScaleObserver,
            dtype=qint16,
            scale=OP2_MAX/QINT16_MAX,
        )
    ),
}

qat_model = prepare(
    model,
    example_inputs=example_input,
    qconfig_setter=( # qconfig 模板，支持传入多个模板，优先级从高到低。reference_qconfig
        ModuleNameQconfigSetter(module_name_to_qconfig), # 自定义模板
        sensitive_op_qat_8bit_weight_16bit_fixed_act_qconfig_setter(table, topk=20), # 敏感度模板
        default_qat_fixed_qconfig_setter, # 默认模板
    ),
)
set_model_state
CALIBRATION  VLIDATION  QAT
```

# 新版模板 fp16
[【地平线 J6工具链入门教程】QAT新版qconfig量化模板使用教程 - 地平线开发者社区](https://developer.horizon.auto/blog/13112)
