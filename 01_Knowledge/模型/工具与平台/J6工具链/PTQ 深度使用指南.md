---
type: knowledge
status: verified
unit_type: workflow_pattern
domain: 模型
topic: PTQ 深度使用指南
sources:
  - https://horizonrobotics.feishu.cn/wiki/D3gDwcL79iTwaik222ac7L1onub
scope: 适用于 J6 工具链下基于 PTQ 的模型转换、校准、部署与精度调优。
risks: 仍保留少量富文本标签与 sheet placeholder；具体命令参数需结合工具链版本核对。
source_task: 评估并将 J6 工具链候选文档提升到知识库
evidence:
  - 来源文档：03_Inbox/PTQ_深度使用指南_对外.md
updated_at: 2026-03-30
---

摘要：面向 J6 PTQ 链路的实战指南，覆盖 fast-perf、config.yaml 配置、校准部署、性能与精度平衡以及常见问题处理。

<callout emoji="hippopotamus" background-color="light-orange" border-color="light-orange">
这份指南聚焦开发者使用 PTQ 时的实际需求，从 “解决什么问题”“怎么用 PTQ 解决” 的角度，提供实战步骤与技巧，手册（[训练后量化PTQ](https://docs.oe.horizon.auto/guide/ptq/ptq_workflow.html)）中已有的通用内容将直接引用在线链接，避免重复。
</callout>

## 0.1 一、快速评测：摸透模型性能上限
### 0.1.1 解决的核心问题
开发者拿到 float ONNX 模型后，首要需求是快速了解模型在地平线 J6 平台上的**最高运行性能**，无需投入大量时间配置参数，同时获取可复用的基础配置文件。
### 0.1.2 PTQ 实战操作
直接使用<text bgcolor="dark-gray">`hb_compile`</text>工具的<text bgcolor="dark-gray">`--fast-perf`</text>参数，一步完成性能评测与基础配置生成。
执行命令：
```python
hb_compile --march nash-b -m xxx.onnx --fast-perf  --skip compile
```

- 核心作用：
  1. 自动将 BPU 可执行算子优先分配到 BPU（<text bgcolor="light-yellow">int8 精度</text>），最大化性能。
  1. 自动删除模型首尾冗余算子（如 Quantize/Dequantize、Cast、Transpose、Reshape 等），减少性能损耗。
  1. 输出两个关键结果：板端最高性能数据<text bgcolor="light-yellow">（上板实测）</text>、基础版<text bgcolor="dark-gray">`config.yaml`</text>（默认生成路径在<text bgcolor="light-yellow">.fast_perf</text>目录下，后续可直接修改使用）。
### 0.1.3 参考手册
详细原理与参数细节可查看：[<text color="blue">hb_compile 工具模型转换说明</text>](https://docs.oe.horizon.auto/guide/ptq/ptq_tool/hb_compile/convert.html)
## 0.2 二、校准部署：快速生成与修改 config.yaml
### 0.2.1 解决的核心问题
开发者需要基于快速评测结果，配置模型校准参数（如校准数据路径、输入格式），完成从浮点模型到可部署模型的转换，同时避免从零编写<text bgcolor="dark-gray">`config.yaml`</text>的繁琐工作。
### 0.2.2 PTQ 实战操作
#### 0.2.2.1 （1）快速生成基础 config.yaml
无需手动创建，直接复用 “快速评测” 步骤中<text bgcolor="dark-gray">`--fast-perf`</text>参数输出的基础版<text bgcolor="dark-gray">`config.yaml`</text>（默认生成路径在.fast_perf目录下），该文件已包含<text bgcolor="dark-gray">`march`</text>（平台型号）、<text bgcolor="dark-gray">`onnx_model`</text>（模型路径）等核心配置，减少 70% 以上的基础配置工作量。
#### 0.2.2.2 （2）按需修改关键配置项
根据实际部署需求，修改<text bgcolor="dark-gray">`config.yaml`</text>中的核心模块，以下为常见场景示例：

<lark-table rows="6" cols="3" column-widths="184,291,686">

  <lark-tr>
    <lark-td>
      配置模块
    </lark-td>
    <lark-td>
      核心修改项
    </lark-td>
    <lark-td>
      场景示例
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      calibration_parameters
    </lark-td>
    <lark-td>
      cal_data_dir（校准数据路径）、
      quant_config（量化配置文件路径）
    </lark-td>
    <lark-td>
      若校准数据存于./calib_data，则设置cal_data_dir: ./calib_data
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td rowspan="2">
      input_parameters
    </lark-td>
    <lark-td rowspan="2">
      input_shape（输入尺寸）、
      norm_type（预处理方式）、
      input_type_rt（运行时输入类型）、
      <text bgcolor="light-yellow">input_batch（多 batch 数）</text>
      <text bgcolor="light-yellow">separate_batch</text>
    </lark-td>
    <lark-td rowspan="2">
      ```python
      灰度图输入场景：input_type_rt: gray，norm_type: data_mean_and_scale，并补充mean_value: 116.28和scale_value: 0.01750700280112。
      ```
      ```python
      多 batch=5 场景：input_batch: 5，separate_batch: True；输入尺寸设input_shape: 1x256x640x1（NCHW 格式）
      ```
    </lark-td>
  </lark-tr>
  <lark-tr>
  </lark-tr>
  <lark-tr>
    <lark-td>
      compiler_parameters
    </lark-td>
    <lark-td>
      compile_mode（编译目标：latency 延迟 /throughput 吞吐量）、
      core_num（使用核心数）
    </lark-td>
    <lark-td>
      追求低延迟时，设置compile_mode: latency；
      多核心部署时，调整core_num: 2（查看用户手册确认OE版本是否已支持多核编译功能）
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      model_parameters
    </lark-td>
    <lark-td>
      working_dir（输出目录）、
      <text bgcolor="light-yellow">remove_node_type</text>（需删除的冗余算子）
      <text bgcolor="light-yellow">enable_vpu  量化反量化vpu</text>
    </lark-td>
    <lark-td>
      ```python
      需删除 Softmax 算子时，设置remove_node_type: Quantize;Transpose;Dequantize;Cast;Reshape;Softmax
      ```
    </lark-td>
  </lark-tr>
</lark-table>

#### 0.2.2.3 （3）执行校准部署命令
完成配置后，执行标准转换命令：<text bgcolor="dark-gray">`hb_compile -c config.yaml`</text><text bgcolor="dark-gray"> --skip compile </text>，工具将自动完成模型校准、量化与编译，最终输出可部署的<text bgcolor="dark-gray">`.hbm`</text>模型文件。
### 0.2.3 参考手册
完整配置项说明与更多场景示例：[<text color="blue">PTQ 精度调优实战</text>](https://docs.oe.horizon.auto/guide/ptq/ptq_usage/precision_tuning_practice.html)
## 0.3 三、模型部署：平衡性能与精度的实战流程
### 0.3.1 解决的核心问题
开发者在部署时需兼顾**性能（速度）** 与**精度（模型效果）** ，避免出现 “性能达标但精度不足” 或 “精度够但速度太慢” 的问题，需找到最优性价比的混合精度方案。
### 0.3.2 PTQ 实战三步法
#### 0.3.2.1 第一步：用 fast-perf 确认性能上限
执行<text bgcolor="dark-gray">`hb_compile --march nash-b -m xxx.onnx --fast-perf`</text>，获取 int8 精度下的最高性能（如推理延迟、吞吐量），作为性能基准。
#### 0.3.2.2 第二步：用全 int16 确认精度上限
修改<text bgcolor="dark-gray">`config.yaml`</text>关联的<text bgcolor="dark-gray">`quant_config.json`</text>，将模型所有算子设置为 int16 精度（通过<text bgcolor="dark-gray">`model_config`</text>配置<text bgcolor="dark-gray">`"all_node_type": "int16"`</text>），执行<text bgcolor="dark-gray">`hb_compile -c config.yaml`</text>，测试模型精度，作为精度基准。
#### 0.3.2.3 第三步：用 hmct-debugger 调混合精度
1. 问题定位：使用<text bgcolor="dark-gray">`hmct-debugger`</text>工具，分析哪些算子用 int8 时精度损耗大（如 Softmax、MatMul），哪些算子用 int8 无明显精度影响（如 Conv、Add）。
2. 混合配置：在<text bgcolor="dark-gray">`quant_config.json`</text>中，对精度敏感算子单独设置 int16，其余用 int8。示例配置如下：
```json
{
    "model_config": {
        "all_node_type": "int8"
    },
    "op_config": {
        "Conv": {"qtype":"int8"},
        "Mul": {"qtype":"int8"},
        "Add": {"qtype":"int8"}
    },
    "node_config": {
        "/transformer/encoder_1/layers.0/self_attn/MatMul_1": {"input0":"int16", "input1":"int8"},
        "/transformer/encoder_1/layers.0/self_attn/Softmax": {"qtype":"int16"}
    }
}
```

1. 验证效果：执行<text bgcolor="dark-gray">`hb_compile -c config.yaml`</text>，测试混合精度模型的性能与精度，确保性能接近 int8 上限、精度接近 int16 上限。
### 0.3.3 3. 参考手册
- hmct-debugger 使用指南：[<text color="blue">精度debug工具</text>](https://docs.oe.horizon.auto/guide/ptq/ptq_tool/accuracy_debug.html)
- 混合精度配置示例：[<text color="blue">PTQ 精度调优实战</text>](https://docs.oe.horizon.auto/guide/ptq/ptq_usage/precision_tuning_practice.html)
## 0.4 四、常见问题与 PTQ 解决方案
### 0.4.1 问题 1：模型转换后精度掉太多
- **PTQ 解决方法**：
  - 开启权重偏差校正（bias correction）主要针对GEEM算子；
  - Per-channel、asymmetric 验证
  - 对敏感算子改用 int16 或 fp16
- **操作步骤**：
  1. 在<text bgcolor="dark-gray">`quant_config.json`</text>的<text bgcolor="dark-gray">`weight`</text>模块添加 <text bgcolor="dark-gray">`"bias_correction": {"num_sample": 1, "metric": "cosine-similarity"}`</text>；
  1. 在<text bgcolor="dark-gray">`node_config`</text>中指定敏感算子（如 MatMul、Softmax）的<text bgcolor="dark-gray">`qtype`</text>为 int16 或 fp16
  [配置某个节点的计算精度](https://doc.oe.horizon.auto/guide/ptq/ptq_tool/hb_compile/quant_config.html#%E9%85%8D%E7%BD%AE%E6%9F%90%E4%B8%AA%E8%8A%82%E7%82%B9%E7%9A%84%E8%AE%A1%E7%AE%97%E7%B2%BE%E5%BA%A6)
### 0.4.2 问题 2：多输入模型（如多特征图）配置复杂
- **PTQ 解决方法**：复用<text bgcolor="dark-gray">`--fast-perf`</text>基础配置，用<text bgcolor="light-yellow">分号</text>分隔多输入参数
- **操作步骤**：在<text bgcolor="dark-gray">`input_parameters`</text>中设置：
  - <text bgcolor="dark-gray">`input_name: input0;input1;input2`</text>
  - <text bgcolor="dark-gray">`input_shape: 1x1x1296x1600;50176;18816`</text>并对应配置<text bgcolor="dark-gray">`input_type_rt`</text>和<text bgcolor="dark-gray">`norm_type`</text>
### 0.4.3 问题 3：校准结果不稳定
- **PTQ 解决方法**：
  - 增加校准样本数；
  - 启用多校准方法搜索
- **操作步骤**：
  1. 在<text bgcolor="dark-gray">`config.yaml`</text>中调整<text bgcolor="dark-gray">`calibration_parameters`</text>的样本量；
  1. 在<text bgcolor="dark-gray">`quant_config.json`</text>的<text bgcolor="dark-gray">`activation`</text>模块设置<text bgcolor="dark-gray">`calibration_type: ["max", "kl"]`</text>校准方式，配置多组量化参数，启用<text bgcolor="dark-gray">`modelwise_search`</text>会同时对多组量化参数做搜索，找到一个量化损失最小的校准方法。
## 0.5 五、关键配置文件模板
### 0.5.1 config.yaml 模板
```yaml
calibration_parameters:
  cal_data_dir: random_calib_data/_transformer_decoder_layer_1_Add_1_output_0  # 校准数据路径
  quant_config: quant_config.json  # 关联量化配置文件

compiler_parameters:
  advice: 0
  balance_factor: 0   # 0：throughput， 100：latency
  compile_mode: latency  # 编译目标：latency（低延迟）/throughput（高吞吐）
  core_num: 1  # 使用核心数，需匹配硬件支持
  jobs: 96
  max_time_per_fc: 0  # 最小执行单元 function call
  optimize_level: O2  # 编译器优化级别

input_parameters:
  input_name: _transformer_decoder_layer_1_Add_1_output_0  # 输入节点名
  input_type_train: bgr
  input_layout_train: NCHW  # 输入数据格式
  input_shape: 1x256x640x3
  input_type_rt: nv12
  norm_type: no_preprocess  # 预处理方式：无预处理
  input_batch: 5  # 多batch设置
  separate_batch: True  # 开启多batch分离

model_parameters:
  march: nash-b  # 平台型号，nash-m平台需改为nash-m
  onnx_model: ./attention_no_bn.onnx  # ONNX模型路径
  output_model_file_prefix: attention_no_bn_int8_nash_b  # 输出模型前缀
  remove_node_type: Quantize;Transpose;Dequantize;Cast;Reshape;Softmax  # 需删除的冗余算子
  working_dir: output_int8_softmax_int16  # 输出目录
```

### 0.5.2 含校准搜索与混合精度的 quant_config.json 模板
```bash
{
  "model_config": {
    "all_node_type": "int16",  # 默认所有算子int16
    "model_output_type": "int16"  # 模型输出int16
  },
  "op_config": {
    "Conv": {"qtype": "int8"},  # Conv算子int8
    "Mul": {"qtype": "int8"},   # Mul算子int8
    "MatMul": {"qtype": "int8"},# MatMul算子默认int8
    "Reshape": {"qtype": "int8"},# Reshape算子int8
    "Transpose": {"qtype": "int8"},# Transpose算子int8
    "Add": {"qtype": "int8"}    # Add算子int8
  },
  "node_config": {
    # 混合精度：特定MatMul节点输入0设int16，输入1设int8
    "/transformer/encoder_1/layers.0/self_attn/MatMul_1": {"input0": "int16", "input1": "int8"},
    "/transformer/encoder_1/layers.1/self_attn/MatMul_1": {"input0": "int16", "input1": "int8"},
    "/transformer/encoder_1/layers.2/self_attn/MatMul_1": {"input0": "int16", "input1": "int8"}
  },
  "activation": {
    "calibration_type": ["max", "kl"],  # 校准参数搜索：同时启用max和kl
    "num_bin": [1024, 2048],  # kl校准参数（多值用于搜索）
    "max_num_bin": 16384,     # kl校准最大bin数
    "max_percentile": [0.99995, 1.0],  # max校准百分位（多值用于搜索）
    "per_channel": [true, false],  # 是否开启per-channel量化（多值用于搜索）
    "asymmetric": [true, false]    # 是否开启非对称量化（多值用于搜索）
  },
  "weight": {
    "bias_correction": {
      "num_sample": 1,  # 参与bias correction的样本数
      "metric": "cosine-similarity"  # 偏差校正误差度量方法
    }
  },
  "modelwise_search": {
    "metric": "cosine-similarity"  # 模型层面校准搜索：用余弦相似度选最优校准方法
  },
  "layerwise_search": {
    "metric": "cosine-similarity"  # 节点层面校准搜索：逐层选最优校准方法（优先级高于modelwise）
  }
}
```

## 0.6 六、附录：核心参数与 quant_config 配置详解
### 0.6.1 核心参数总表
<sheet token="KziYsX5J1hSYJctlNRlchMKAnvf_XgSJaW"/>

### 0.6.2 quant_config 配置说明
编译模型时可以通过quant_config进行量化参数的配置，支持在model_config、op_config、subgraph_config、node_config四个层面配置模型量化参数：
- model_config：配置模型总体的量化参数，key是自定义名称。
- op_config：配置某类算子的量化参数，key是算子的类型。
- subgraph_config：配置某个子图的量化参数，key是子图的名字。
- node_config：配置某个具体节点的量化参数，key是节点的名字。
配置时四个层面存在优先级关系，配置粒度越小优先级越高，即优先级model_config < op_config < subgraph_config < node_config，当某个节点同时被多个维度配置时，优先级高的维度最终生效。
#### 0.6.2.1 激活参数配置
- calibration_type：校准方式支持max、kl、[max、kl]
- num_bin、max_num_bin：这些是kl量化的参数
- max_percentile：用于max校准百分位
- per_channel：是否开启per-channel量化
- asymmetric：是否开启非对称量化
<callout emoji="cow2" background-color="light-orange" border-color="light-orange">
注：如果配置了多个校准方法,会启动Modelwise搜索方法，从多个候选校准模型中找出最优的量化模型；如果配置了Layerwise参数，则启动Layerwise搜索方法，逐层搜索最优的量化参数。
</callout>

#### 0.6.2.2 权重校准参数配置
- num_sample：配置参与bias correction的样本数
- metric：偏差校正误差度量方法cosine-similarity、mse、mae、mre、sqnr以及chebyshev，默认值cosine-similarity。
#### 0.6.2.3 校准参数搜索方法
- modelwise_search：在模型层面对量化参数进行搜索，该方法允许一次性配置多种校准方法，通过比较量化前后模型输出的量化损失metric（可配置），找到一个量化损失最小的校准方法。
- layerwise_search：在节点层面对量化参数进行搜索，该方法会根据每个节点量化前后模型输出，计算量化损失metric（可配置），为该节点分配量化损失最小的校准方法。
<callout emoji="dog2" background-color="light-orange" border-color="light-orange">
注：多个校准方法时modelwise_search和layerwise_search可以都不配置，但默认会执行modelwise_search的逻辑(metric会采用默认的cosine-similarity)。
</callout>

<callout emoji="unicorn_face" background-color="light-orange" border-color="light-orange">
注：modelwise和layerwise同时配置的时候，layerwise优先级高。
</callout>

#### 0.6.2.4 参考手册
- **quant_config 详细配置指南：**[<text color="blue">quant_config 配置指南</text>](https://docs.oe.horizon.auto/guide/ptq/ptq_tool/hb_compile/quant_config.html)