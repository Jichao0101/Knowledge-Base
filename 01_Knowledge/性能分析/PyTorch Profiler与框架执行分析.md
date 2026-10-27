---
type: knowledge
status: reviewed
domain: 性能分析
summary: 从采集窗口、算子汇总和真实trace建立阶段到GPU执行的关联。
sources:
  - 04_Sources/性能分析/2026-10-27_性能分析系列官方文档依据.md
  - 04_Sources/模型工程/2026-10-21_Nsight Compute官方文档来源记录.md
scope: PyTorch CPU/CUDA工作负载；JSON解释仅针对所展示的Kineto事件。
risks:
  - 文档审核不等于本机实测；工具版本、硬件、权限和输入条件须现场确认。
  - 教学推导、官方历史案例和项目trace不能互相冒充，单指标不能证明唯一瓶颈。
review_basis: 2026-10-27按用户确认的系列方案拆分既有内容并核对官方文档；无新增GPU运行。
updated_at: 2026-10-27
---

# 1 PyTorch Profiler与框架执行分析

## 1.1 从“模型慢”定位到具体的工作

模型一次调用可能经历多个阶段，每个阶段又包含许多框架算子。GPU上看到的是这些算子最终触发的kernel，仅凭kernel名称，往往不知道它属于哪一层、处理了多大的输入，也不知道是谁提交了它。

torch.profiler的主要价值就是连接这两端：保留算子、输入shape和调用位置等框架信息，同时关联设备活动。分析因此可以从“哪个阶段慢”逐步缩小到“哪种输入下的哪个算子值得检查”，而不是直接面对一长串GPU函数名。

Nsight Systems同样能观察CPU和GPU，但更适合补充线程调度和跨组件时序。因此，选择工具的依据是还缺哪一层解释，而不是把两者分别当作CPU工具与GPU工具。

## 1.2 采集：让报告代表你要分析的执行过程

### 1.2.1 先选观察窗口

长训练不必全程采集。若研究稳定训练速度，就先让模型与后端完成预热，再选取具有代表性的迭代；若研究启动慢，则单独观察加载、编译或首次分配。两类问题对应不同窗口，混在一起取平均会掩盖各自的原因。

窗口也不能只追求短。它需要包含目标工作及理解其前后关系所需的上下文。例如，只留下一个GPU事件而丢掉提交线程和前序依赖，就难以解释它为何延迟开始。

### 1.2.2 再决定需要保留哪些信息

确定窗口之后，再根据要回答的问题增加观测信息。下表是配置时使用的选项，不是每次采集都应开启的清单。

| 要回答的问题 | 选项 | 使用边界 |
|---|---|---|
| 同名算子是否处理了不同规模的输入？ | `record_shapes` | 保留输入shape；额外引用可能影响tensor生命周期 |
| 这个算子由哪处代码调用？ | `with_stack` | 记录调用位置，有额外采集开销 |
| 哪个阶段发生分配或释放？ | `profile_memory` | 观察内存分配行为，不测访存带宽 |
| 支持的算子大致做了多少浮点工作？ | `with_flops` | 公式估算，不是硬件实际执行计数 |

先取得足以定位问题的报告，再补充缺失信息。shape和stack等记录会改变采集成本，不应把开启所有选项后的耗时直接当作正常运行性能。[Profiler API](https://docs.pytorch.org/docs/2.14/profiler.html)

### 1.2.3 最后把窗口落实到训练循环

对于长循环，可以用`schedule`安排等待、预热和记录阶段；在每次迭代末调用`prof.step()`推动采集状态，并通过`on_trace_ready`保存完成的窗口。这些接口解决的是“何时记录和输出”，不是替代前面的窗口选择。

一个step对应什么由应用决定。分析训练时，应明确它是一轮micro-step还是完整参数更新，避免报告中的步数与任务吞吐的分母不一致。

## 1.3 阅读：先用汇总表筛选，再用时间线解释

报告打开后，先看哪些工作值得投入分析。设备累计时间可以帮助选择候选，但同名算子可能处理不同shape；因此，还要检查调用次数和输入分组，判断总时间高是因为单次慢，还是因为执行次数多。

读汇总列时要分清两种统计：`CPU total`包含子算子，`Self CPU`排除子算子。它们描述CPU侧区间，不是CPU忙碌周期，区间中的等待也可能被计入。设备时间是按工具规则归属的累计量，同样不自动等于请求墙钟时间。[Profiler教程](https://docs.pytorch.org/tutorials/recipes/recipes/profiler_recipe.html)

汇总表给出候选之后，再进入时间线追问：这个算子在什么阶段被调用，它提交了哪些GPU工作，GPU执行前是否存在排队或依赖？这一步需要关联字段和上下文，不能仅凭名称相同或时间接近建立对应关系。

下面用一个真实片段展示这一过程。重点不是记住JSON字段，而是沿着“GPU工作 → 提交调用 → 框架算子 → 模型阶段”找回同一份工作的身份。

## 1.4 先读一条真实GPU事件，再找出谁提交了它

以下片段来自已采集的单卡B1运行，保留事件的原始名称、时间、ID、shape及启动参数，只删除与本节无关的字段和其他事件。它不是完整trace，也不代表整个阶段只有一个kernel。

```json
{
  "traceEvents": [
    {
      "ph": "X", "cat": "user_annotation",
      "name": "experiment/language_prefill",
      "pid": 1998262, "tid": 1998262,
      "ts": 1281015341995.85, "dur": 178884.387,
      "args": {
        "External id": 5146
      }
    },
    {
      "ph": "X", "cat": "cpu_op",
      "name": "aten::mm",
      "pid": 1998262, "tid": 1998262,
      "ts": 1281015345206.296, "dur": 16.539,
      "args": {
        "External id": 5452,
        "Input type": ["c10::BFloat16", "c10::BFloat16"],
        "Input Dims": [[4781, 4096], [4096, 12288]]
      }
    },
    {
      "ph": "X", "cat": "cuda_driver",
      "name": "cuLaunchKernel",
      "pid": 1998262, "tid": 1998262,
      "ts": 1281015345218.466, "dur": 3.709,
      "args": {
        "External id": 5452,
        "correlation": 15321
      }
    },
    {
      "ph": "X", "cat": "kernel",
      "name": "void cutlass::Kernel2<cutlass_80_tensorop_bf16_s16816gemm_relu_bf16_256x128_32x3_tn_align8>(cutlass_80_tensorop_bf16_s16816gemm_relu_bf16_256x128_32x3_tn_align8::Params)",
      "pid": 0, "tid": 7,
      "ts": 1281015348167.936, "dur": 1967.384,
      "args": {
        "External id": 5452,
        "device": 0,
        "context": 1,
        "stream": 7,
        "correlation": 15321,
        "registers per thread": 232,
        "shared memory": 73728,
        "blocks per SM": 16.581818,
        "grid": [304, 6, 1],
        "block": [256, 1, 1],
        "est. achieved occupancy %": 0
      }
    }
  ]
}
```

### 1.4.1 cat是类别，name是这个事件的名字

JSON中的每个对象描述一个事件。`cat`回答“它属于哪一类”，`name`回答“这一类中的哪个具体事件”。两个字段一起描述一条事件，并不分别对应四种执行环节：

| `cat`的取值 | 本例`name`的取值 | 这条事件表示什么 |
|---|---|---|
| `user_annotation` | `experiment/language_prefill` | 应用标记的CPU阶段 |
| `cpu_op` | `aten::mm` | CPU侧框架算子调用 |
| `cuda_driver` | `cuLaunchKernel` | CPU侧CUDA Driver API调用 |
| `kernel` | `void cutlass::Kernel2<…>` | GPU执行的一次kernel |

本例实际使用`cuda_driver/cuLaunchKernel`；其他运行可能出现`cuda_runtime/cudaLaunchKernel`，应读原值，不能将两者混写。

例如，`cat="cpu_op"`且`name="aten::mm"`表示一条矩阵乘法的CPU框架算子事件；`cat="kernel"`且`name`为长CUTLASS名称，才是对应的GPU执行事件。prefill阶段名由应用标记产生，不是GPU硬件自动识别的模型阶段。

`ph="X"`表示这是一个带开始时间和持续时间的完整区间，结束时间为`ts+dur`。此类Kineto JSON的`ts/dur`以µs表示，原文件头部虽然有`displayTimeUnit="ms"`，这是显示单位，不能据此把JSON里的dur当成ms。真实trace还会包含metadata及flow事件：它们用于描述轨道或关联，不是每条都有可累加的`dur`。[Kineto导出实现](https://github.com/pytorch/kineto/blob/main/libkineto/src/output_json.cpp)

### 1.4.2 从kernel沿关联字段回到CPU

从最后一条kernel开始看，它的`correlation=15321`与`cuLaunchKernel`一致，因此能找到这次GPU工作的提交调用。两条事件的`External id=5452`又与`aten::mm`一致，于是找到了框架算子。最后检查CPU的进程/线程和时间范围：`aten::mm`位于同线程的`experiment/language_prefill`标记内，这才把GPU工作归到prefill。

注意阶段标记的External id是5146，而算子的是5452。阶段归属通过CPU嵌套关系建立，不要求这两个ID相等。

CPU事件的`pid/tid`用于定位进程和线程；GPU轨道中的同名字段须结合metadata和`device/stream`解释，不能把GPU的tid当成CPU线程号，更不能当成kernel里的线程索引。关联ID也应限定在当前报告的进程、设备和上下文内，不跨运行直接复用。

这个例子展示了一条可核对的关联链。现实中一个CPU算子可能启动多个kernel，编译融合也可能改变对应关系，因此解析时要保留一对多关系。只有时间接近、或者只有名字相同，都不够完成归属。[Nsight Systems关联与分析说明](https://docs.nvidia.com/nsight-systems/AnalysisGuide/index.html)

### 1.4.3 同一次矩阵乘法，CPU和GPU耗时为什么不同

这次`aten::mm`的CPU区间只有16.539µs，其中Driver API占3.709µs；关联的GPU kernel却运行1967.384µs，约1.967ms。API返回到kernel开始之间还有2945.761µs，约2.946ms。这个差值描述提交与开始的间隔，片段没有包含前序GPU工作和依赖，因此不能直接叫作“launch开销”或GPU空闲。

`experiment/language_prefill`的178884.387µs是整个CPU阶段区间，包含许多未展示的算子；这里1.967ms只属于选中的一次GEMM。不能把单kernel耗时当成完整prefill，也不能把阶段长度与其中算子时间相加。

这并不矛盾。CPU侧要做框架分派、准备参数并向CUDA提交任务；提交后GPU可能仍在处理前面的工作。CPU算子的区间不保证等待该kernel完成。若CPU随后进入同步等待，这段等待又与GPU执行重叠，所以CPU算子、launch API、GPU kernel和同步等待不能简单相加。

这也说明了前面为什么把汇总表用于筛选候选，而把时间线用于解释关系：累计统计已经折叠了提交、等待和重叠，必须回到事件本身才能区分。

因此，普通benchmark应先预热、同步清除前序工作，再开始墙钟计时，并在末尾等待目标GPU工作完成。阶段标记本身不需要逐阶段同步，否则会改变CPU/GPU重叠。CUDA Event用于测stream上事件之间的设备时间，其中也可能有等待和空隙；跨stream测量必须先建立明确的依赖关系。[CUDA异步执行说明](https://docs.pytorch.org/docs/2.14/notes/cuda.html)

### 1.4.4 shape和启动参数把模型工作连接到GPU工作

`Input Dims`给出`[4781,4096] × [4096,12288]`，`Input type`显示两个输入为BF16。这描述了矩阵乘法的工作规模。GPU侧`grid=[304,6,1]`表示1824个block，`block=[256,1,1]`表示每block 256个线程。

每线程232个寄存器，粗算每block为59392个32位寄存器；共享内存73728 bytes，即72KiB。片段中的`blocks per SM=16.581818`与该设备110个SM下的1824/110相符，表示启动工作量按SM平均，不是同时驻留16.58个block。`est. achieved occupancy %=0`也不能当作实测零驻留：这是trace导出的估算字段，仅凭它不能判定未执行或零利用率，实际occupancy需结合采集方式和计数器解释。

输入shape来自框架算子，`grid/block`来自kernel启动，二者不在同一抽象层。一个矩阵会被实现切成多个tile，由许多block处理；不能把grid某一维直接解释成batch。启动了很多block，也不代表它们同时驻留在SM中。

trace中的寄存器和共享内存字段只是资源配置。它们可以结合设备上限估算驻留容量，却不能证明实际occupancy，更不能说明算力或带宽已饱和。至此，trace告诉了我们“谁执行了什么、用了多久、怎样启动”，还没有回答“为什么这个kernel不能更快”。

## 1.5 分析到这里，下一步还缺什么

完成上述关联后，应该已经能说明目标阶段、输入shape、dtype、kernel名称及具体实例。这些信息足以定义下一次采集对象，而“耗时最高的kernel名字”通常还不够。

如果仍无法解释GPU为什么等待，就进入[[01_Knowledge/性能分析/Nsight Systems与CPU-GPU协同分析]]，补充主机和stream之间的关系；如果执行对象已经明确，而问题在于kernel内部为何低效，则进入[[01_Knowledge/性能分析/Nsight Compute基础与性能分析]]。跨运行时重新确认实例，不能复用旧报告的关联ID。

本页JSON沿用[[04_Sources/模型工程/2026-10-21_Nsight Compute官方文档来源记录]]中的真实字段和原关联核对，本次未重跑模型。整体计时与比较规则见[[01_Knowledge/性能分析/性能测量与瓶颈验证]]。
