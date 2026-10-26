---
type: knowledge
status: reviewed
domain: 模型工具与平台
summary: 对照torch.profiler时间线与Nsight Compute硬件指标，解释CPU/GPU时间、阶段归属、热点选择与瓶颈验证。
sources:
  - 04_Sources/模型工程/2026-10-21_Nsight Compute官方文档来源记录.md
scope: NVIDIA CUDA应用的热点kernel诊断；适用于模型算子、计算库及自定义CUDA程序。
risks:
  - 文档核对不代表本机实测；GPU、驱动、工具版本和权限须现场确认。
  - 单kernel指标不能直接代表端到端性能，采集也可能改变缓存、时钟和并发。
review_basis: 2026-10-21核对NVIDIA官方文档；2026-10-26补核PyTorch与NVIDIA文档中的观测口径，复核已有trace的原始事件与关联；ncu表仍为模拟值，未新执行GPU采集。
updated_at: 2026-10-26
---

# 1 Nsight Compute基础与性能分析

## 1.1 从时间线走到硬件指标

分析GPU性能时，首先遇到的往往是一个时间问题：某次模型调用为什么需要这么久？`torch.profiler`导出的trace可以把这次调用展开为CPU算子、CUDA提交和GPU活动。找到耗时最长的kernel之后，问题才变成：它为什么需要这么长时间，是计算吞吐、存储访问还是指令依赖限制了它？Nsight Compute（命令行`ncu`、界面`ncu-ui`）主要回答后一个问题。

所以，torch trace并非只看CPU，ncu也并非只给一个GPU耗时。前者擅长连接框架语义和执行时序，后者提供选定GPU工作内部的计数器证据。若还要追踪CPU线程调度、系统活动或复杂的跨stream依赖，可以补充Nsight Systems；是否真正变快，则回到不带profiler的benchmark。

| 当前问题 | 主要证据 |
|---|---|
| 哪个算子慢，它由哪个阶段提交？ | torch.profiler的CPU/CUDA时间线与输入shape |
| GPU在等谁，主机和不同stream如何协作？ | 已有trace；不足时补Nsight Systems |
| 已定位的kernel内部受什么限制？ | Nsight Compute的计算、存储与调度指标 |
| 优化是否缩短任务完成时间？ | 固定输入与生成条件的独立benchmark |

本文先读取一组真实trace事件，再解释如何把这个对象带到ncu中。两种报告之间最重要的连接是**同一份工作及其调用身份**，不是相同的事件ID。[PyTorch Profiler API](https://docs.pytorch.org/docs/2.14/profiler.html)、[NVIDIA工具指南](https://docs.nvidia.com/nsight-compute/NsightCompute/index.html)

## 1.2 先读一条真实GPU事件，再找出谁提交了它

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

### 1.2.1 cat是类别，name是这个事件的名字

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

### 1.2.2 从kernel沿关联字段回到CPU

从最后一条kernel开始看，它的`correlation=15321`与`cuLaunchKernel`一致，因此能找到这次GPU工作的提交调用。两条事件的`External id=5452`又与`aten::mm`一致，于是找到了框架算子。最后检查CPU的进程/线程和时间范围：`aten::mm`位于同线程的`experiment/language_prefill`标记内，这才把GPU工作归到prefill。

注意阶段标记的External id是5146，而算子的是5452。阶段归属通过CPU嵌套关系建立，不要求这两个ID相等。

CPU事件的`pid/tid`用于定位进程和线程；GPU轨道中的同名字段须结合metadata和`device/stream`解释，不能把GPU的tid当成CPU线程号，更不能当成kernel里的线程索引。关联ID也应限定在当前报告的进程、设备和上下文内，不跨运行直接复用。

这个例子展示了一条可核对的关联链。现实中一个CPU算子可能启动多个kernel，编译融合也可能改变对应关系，因此解析时要保留一对多关系。只有时间接近、或者只有名字相同，都不够完成归属。[Nsight Systems关联与分析说明](https://docs.nvidia.com/nsight-systems/AnalysisGuide/index.html)

### 1.2.3 同一次矩阵乘法，CPU和GPU耗时为什么不同

这次`aten::mm`的CPU区间只有16.539µs，其中Driver API占3.709µs；关联的GPU kernel却运行1967.384µs，约1.967ms。API返回到kernel开始之间还有2945.761µs，约2.946ms。这个差值描述提交与开始的间隔，片段没有包含前序GPU工作和依赖，因此不能直接叫作“launch开销”或GPU空闲。

`experiment/language_prefill`的178884.387µs是整个CPU阶段区间，包含许多未展示的算子；这里1.967ms只属于选中的一次GEMM。不能把单kernel耗时当成完整prefill，也不能把阶段长度与其中算子时间相加。

这并不矛盾。CPU侧要做框架分派、准备参数并向CUDA提交任务；提交后GPU可能仍在处理前面的工作。CPU算子的区间不保证等待该kernel完成。若CPU随后进入同步等待，这段等待又与GPU执行重叠，所以CPU算子、launch API、GPU kernel和同步等待不能简单相加。

阅读PyTorch汇总表也遵循同样原则：`CPU total`包含子算子，`Self CPU`排除子算子，但二者都不是CPU忙碌周期；区间里的阻塞也可能计入。CUDA/device列是按工具规则归属的设备累计量，不自动等于请求墙钟时间。汇总表适合找候选，具体归因要回到时间线。[PyTorch profiler教程](https://docs.pytorch.org/tutorials/recipes/recipes/profiler_recipe.html)

因此，普通benchmark应先预热、同步清除前序工作，再开始墙钟计时，并在末尾等待目标GPU工作完成。阶段标记本身不需要逐阶段同步，否则会改变CPU/GPU重叠。CUDA Event用于测stream上事件之间的设备时间，其中也可能有等待和空隙；跨stream测量必须先建立明确的依赖关系。[CUDA异步执行说明](https://docs.pytorch.org/docs/2.14/notes/cuda.html)

### 1.2.4 shape和启动参数把模型工作连接到GPU工作

`Input Dims`给出`[4781,4096] × [4096,12288]`，`Input type`显示两个输入为BF16。这描述了矩阵乘法的工作规模。GPU侧`grid=[304,6,1]`表示1824个block，`block=[256,1,1]`表示每block 256个线程。

每线程232个寄存器，粗算每block为59392个32位寄存器；共享内存73728 bytes，即72KiB。片段中的`blocks per SM=16.581818`与该设备110个SM下的1824/110相符，表示启动工作量按SM平均，不是同时驻留16.58个block。`est. achieved occupancy %=0`也不能当作实测零驻留：这是trace导出的估算字段，仅凭它不能判定未执行或零利用率，实际occupancy需结合采集方式和计数器解释。

输入shape来自框架算子，`grid/block`来自kernel启动，二者不在同一抽象层。一个矩阵会被实现切成多个tile，由许多block处理；不能把grid某一维直接解释成batch。启动了很多block，也不代表它们同时驻留在SM中。

trace中的寄存器和共享内存字段只是资源配置。它们可以结合设备上限估算驻留容量，却不能证明实际occupancy，更不能说明算力或带宽已饱和。至此，trace告诉了我们“谁执行了什么、用了多久、怎样启动”，还没有回答“为什么这个kernel不能更快”。

## 1.3 从这条trace选择ncu的采集对象

同名kernel会在不同层、不同shape中反复出现。进入ncu前，应带上阶段、算子shape、dtype、名称、grid/block以及实例选择依据。trace的External id或correlation只服务本次采集，不是下一次ncu的调用序号。

如果当前实例位置尚不明确，可以先用basic取得预热后短窗口的调用清单。应用需实际发出NVTX push/pop标记`measure`；torch的`record_function`不会仅凭同名区间就成为NVTX。hook决定在哪里发出标记，本身不是计时器。

```bash
ncu --nvtx --nvtx-include 'measure/' --set basic \
  --kernel-name-base demangled -o measure_basic python workload.py
```

这轮不限制调用数量，代价随窗口内kernel数增长；basic也可能发生重放。核对实例之后，再限制范围和数量，采full或指定sections。已能可靠筛选时不必重新采整个窗口。

```bash
ncu --nvtx --nvtx-include 'measure/' --set full \
  --kernel-name-base demangled \
  --kernel-name "${TARGET_KERNEL:?填写已确认的名称或regex表达式}" \
  --launch-skip "${TARGET_SKIP:?填写已确认的匹配skip}" \
  --launch-count "${TARGET_COUNT:?填写采集数量}" \
  -o kernel_full python workload.py
```

`workload.py`是占位程序，环境变量必须先填写。skip/count针对符合过滤条件的调用，不是batch或训练step，报告全局ID不能直接当作skip。改变阶段或名称过滤后要重新核对匹配序列；不确定时先用相同过滤条件的basic验证。count=1只表示采一个已确认实例，不表示默认第一个就是目标。[CLI过滤说明](https://docs.nvidia.com/nsight-compute/NsightComputeCli/index.html)

范围和指标量是两个独立选择。Metric是单个指标，Section把指标组织成分析主题，Set组合多个Section。full适合少量已确认热点；也可以先看`SpeedOfLight`、`LaunchStats`和`Occupancy`，再按问题增加`ComputeWorkloadAnalysis`、`MemoryWorkloadAnalysis`、`SchedulerStats`或`SourceCounters`，无需每次采全套。

## 1.4 ncu报告里的数字怎样连起来读

下面继续以矩阵乘法为背景，但**目前没有与上述trace配对的真实ncu报告**。因此，下表仍是独立的模拟报告摘录，仅解释字段，不假装这些硬件数值来自刚才的真实kernel；也不据此计算两次运行的性能差异。

```text
模拟报告：一个已选定的GEMM实例（非上文trace的实测后续）

Section                 Metric                            Unit          Value
Speed Of Light          Duration                          ms             2.10
Speed Of Light          SM Throughput                     %             35.00
Speed Of Light          Memory Throughput                 %             80.00
Memory Workload         DRAM Throughput                   %             18.00
Memory Workload         L2 Throughput                     %             80.00
Launch Statistics       Grid Size                         blocks       1024
Launch Statistics       Block Size                        threads       256
Launch Statistics       Registers Per Thread              register       64
Launch Statistics       Dynamic Shared Memory Per Block   byte        32768
Launch Statistics       Static Shared Memory Per Block    byte            0
Occupancy               Theoretical Occupancy             %             50.00
Occupancy               Achieved Occupancy                %             45.00
Scheduler Statistics    Eligible Warps Per Scheduler      warp            0.40
```

先用`ncu-ui REPORT_PATH`打开报告，在Summary选择一个launch，再到Details看各section。要判断某一百分比的含义，应打开Metric Details查其底层指标、单位和公式；也可用`ncu --import REPORT_PATH --page raw --csv`导出原始指标表。缺少某个section可能是未采集或不支持，不应填成0。[报告界面说明](https://docs.nvidia.com/nsight-compute/NsightCompute/index.html)

### 1.4.1 先读耗时，再看计算和存储各自做了多少工作

`Duration=2.10ms`是该实例在ncu采集条件下的设备执行时长。它是后面各种速率的时间背景，不是整个ncu进程的运行时间，也不包含完整请求链路。

接着看`SM Throughput=35%`。这个数是SM侧吞吐汇总，应继续查看哪些计算管线贡献了它，不能翻译成“只有35%的SM工作”。同样，`Memory Throughput=80%`是存储相关吞吐汇总，不直接等于DRAM带宽。本例DRAM为18%、L2为80%，所以值得下钻L2；这两个百分比分别有自己的上限和统计口径，不相加，也不相减。

底层名字能帮助我们找回分母。例如`dram__throughput.avg.pct_of_peak_sustained_elapsed`表示DRAM吞吐经过相应聚合、按持续峰值和elapsed时间口径归一化。18%不是显存容量占用了18%。`gpu__time_duration.sum`是时间指标，需先看单位；指标名及可用性以当前GPU和工具版本为准。

### 1.4.2 再看工作能否驻留，驻留后能否发射

模拟报告启动1024个block，每个256线程。每线程64个寄存器，粗算每block需要16384个32位寄存器；动态共享内存32KiB，静态为0。实际分配还有粒度与保留资源，必须结合设备上限，才能估算同时驻留多少block。

`Theoretical Occupancy=50%`描述配置允许的驻留warp比例；`Achieved Occupancy=45%`描述采集中实际驻留情况。45/50并不等于算力效率90%。例如`sm__warps_active.avg.pct_of_peak_sustained_active`采用active周期口径，也不能直接与elapsed口径的吞吐百分比作比值。

驻留只是“在SM上有位置”，不是“下一条指令已就绪”。`Eligible Warps Per Scheduler=0.40`表示每scheduler平均可发射warp数，平均值可以小于1，却不能翻译成40%空闲时间。此时应结合发射情况、指令依赖与访存等待继续看`SchedulerStats`和`SourceCounters`；某种stall占比高，也不一定主导总体耗时。

这组模拟数据支持的表述是：DRAM吞吐不高，L2相对更高，值得继续检查存储层级和可发射工作。它还不足以宣布唯一瓶颈。减少寄存器或许增加驻留，也可能引入spill或重计算；是否改善，最终仍要看耗时。

## 1.5 用Roofline判断上限，用其他指标解释差距

读完吞吐和调度指标后，Roofline提供一个定量参照：这份工作在当前计算路径和存储流量下，理论上能有多快？定义同一范围的计算量为FLOPs、某一级存储流量为Bytes、执行时间为T：

```text
算术强度 I = FLOPs / Bytes      （FLOP/byte）
实际性能 P = FLOPs / T          （FLOP/s）
简化上界 = min(计算峰值, 带宽 × I)
```

横轴是每搬运一字节做多少计算，纵轴是每秒完成多少计算。带宽形成斜线，所选计算路径形成水平上限。若一个点离屋顶很远，位置在交点哪一侧都不足以确定真实瓶颈，还要回到访存、并行规模、指令与依赖证据。[Roofline说明](https://developer.nvidia.com/blog/accelerating-hpc-applications-with-nsight-compute-roofline-analysis/)

例如另一个纯教学算例：100 GFLOP、20 GB实际DRAM流量、10ms执行时间，得到I=5 FLOP/byte、P=10 TFLOP/s。假设相应计算上限100 TFLOP/s、DRAM带宽2 TB/s，则简化屋顶为10 TFLOP/s；接近这一屋顶才支持带宽限制。如果只达到2 TFLOP/s，还需解释差距。

这里的“相应”十分重要。BF16 Tensor Core和普通FP32路径不能混用上限；DRAM、L2、L1的Bytes必须分别计量，输入tensor大小不等于实际DRAM流量。框架按shape估算的FLOPs也不一定等于硬件实际工作量，padding等可能增加执行量。Roofline不能回答后端是否支持batch，或为什么按图拆分调用，那仍需检查实现路径。[官方性能排查](https://docs.nvidia.com/nsight-compute/ComputeTriage/index.html)

## 1.6 回到时间线和真实任务，检查结论是否成立

即使ncu选对了kernel，它看到的环境也可能与原trace不同。计数器不总能一次采齐，工具可能多次重放、保存恢复内存、串行化调用、清理缓存或控制时钟。因此，应保留replay模式、pass数、cache/clock设置及过滤条件，先解释测量差异，再解释瓶颈。[Profiling Guide](https://docs.nvidia.com/nsight-compute/ProfilingGuide/index.html)

Kernel replay重放单个kernel；Application replay重跑应用，要求各轮调用能够可靠对应；Range replay采一段CUDA工作，结果归属整个范围。默认kernel采集即使用了NVTX过滤，也不会自动变成整个阶段的累计Roofline。涉及主机协作、多stream并发或API限制时，需确认所选模式是否保留必要关系；关闭缓存清理也不自动恢复真实缓存历史。

回看trace时，还要区分累计时间与完成时间。例如三个假设GPU活动分别为`[0,4]`、`[2,6]`和`[7,8]`ms：累计是9ms，活动并集是7ms，最早开始到最晚结束的跨度是8ms。累计大于跨度来自重叠，跨度比并集多1ms来自空隙。若加入memcpy等活动，必须说明并集的事件范围；7/8的活动覆盖率不是SM利用率。

遇到空隙，先检查后续kernel何时提交。提交晚，应查主机准备、调度或同步；提交早，应查队列、跨stream事件和资源依赖。不能只凭GPU空隙宣布CPU瓶颈，也不能只凭活动连续宣布算力满载。CPU标记可能早于关联GPU工作结束，归属仍要沿关联链追溯，不能按CPU阶段的时间边界截断GPU事件。

完成一次分析时，把对象、测量条件、观察、假设及待验证点写成相连的解释，再做受控修改。换后端后调用更少、耗时更短，可以报告已测改善；算法、分块、复用和调用组织可能一起变化，唯一归因仍需额外证据。最后用相同任务合同检查输出正确性，再由独立benchmark比较吞吐、延迟和容量。利用率下降也可能伴随耗时缩短，不能以某个百分比提高代替优化目标。

## 1.7 实际使用前的检查与来源

开始前查询`ncu --version`、`--help`、`--list-sets`、`--list-sections`和`--query-metrics`，记录GPU、驱动、应用版本与输入精度；在线文档不能代替当前环境的支持情况。出现`ERR_NVGPUCTRPERM`表示计数器访问受限，容器内CUDA可用或用户为root都不自动保证授权；按驱动和管理员策略处理。[权限说明](https://developer.nvidia.com/ERR_NVGPUCTRPERM)

torch profiler采CPU/CUDA活动时，shape、stack及显存记录需按问题启用，这些选项会增加开销；显存分配记录不是带宽数据。`with_flops`只是部分算子的公式估算。只在关联、工作量及采集有效性明确时解释硬件原因；权限拒绝、缺项或对象不明时，保留已有trace事实，不用它替代缺失计数器。

官方依据、真实trace的来源和提取规则见[[04_Sources/模型工程/2026-10-21_Nsight Compute官方文档来源记录]]。本文真实JSON片段经过本地解析与关联复核，没有重新运行GPU；ncu表、重叠时间线和Roofline算例仍为明确标注的模拟数据。PyTorch说明参考本次核对的2.14文档，命令与字段以实际安装版本为准。
