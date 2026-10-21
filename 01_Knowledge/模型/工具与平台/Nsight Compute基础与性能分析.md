---
type: knowledge
status: reviewed
domain: 模型工具与平台
summary: 从选择热点到解读硬件指标，说明Nsight Compute的采集方法、Roofline与结论边界。
sources:
  - 04_Sources/模型工程/2026-10-21_Nsight Compute官方文档来源记录.md
scope: NVIDIA CUDA应用的热点kernel诊断；适用于模型算子、计算库及自定义CUDA程序。
risks:
  - 文档核对不代表本机实测；GPU、驱动、工具版本和权限须现场确认。
  - 单kernel指标不能直接代表端到端性能，采集也可能改变缓存、时钟和并发。
review_basis: 2026-10-21核对NVIDIA官方文档；命令示例未在GPU上运行。
updated_at: 2026-10-21
---

# Nsight Compute基础与性能分析

## 1 先明确它回答什么问题

Nsight Compute是CUDA kernel性能分析工具，命令行为`ncu`，图形界面为`ncu-ui`。它把一次选定执行与硬件指标关联起来，帮助解释“这段GPU计算为什么慢”。报告可以保存、重开和设置比较基线。[官方UI指南](https://docs.nvidia.com/nsight-compute/NsightCompute/index.html)

使用时先分清三个问题：

| 问题 | 优先使用的证据 | 得到什么 |
|---|---|---|
| 整个任务实际快多少？ | 无profiler的benchmark | 固定工作量的完成时间、吞吐或延迟 |
| 时间花在哪，CPU/GPU如何重叠？ | Nsight Systems或已有时间线 | 热点、提交间隙、依赖及并发 |
| 热点kernel内部受什么限制？ | Nsight Compute | 计算管线、存储和调度方面的线索 |

已有可靠trace定位了热点时，可以直接进入kernel诊断。不必每次重做全量时间线；也不要把整个模型所有调用一开始都用完整指标集采一遍。此顺序是面向工程使用的整理方法，不是必须串行执行的工具规定。[官方排查指南](https://docs.nvidia.com/nsight-compute/ComputeTriage/index.html)

## 2 一份报告的对象与指标

### 2.1 先确认测的是哪一次执行

同名kernel会被不同层、不同shape反复调用。比较时记录设备、阶段、调用实例、输入shape、dtype和grid/block；不能仅按名称把它们混在一起。输入shape和模型阶段可能需要由应用日志或标记补充，不应假设报告自动恢复了全部模型语义。

```text
模型模块/框架算子
→ 后端选择kernel实现
→ 带具体参数的一次launch
→ grid中的blocks分配到SM
→ 驻留warp等待或发射指令
→ 计算与存储资源完成工作
```

这条链用于组织判断：总block多，不代表同时驻留多；驻留多，不代表都就绪；GPU持续运行，不代表某条计算管线饱和。

### 2.2 Section和Set怎么选

Metric是具体指标，Section把相关指标组织成一个分析主题，Set再组合多个Section。先用小范围采集确认方向，再增加问题所需的Section；可用项以`ncu --list-sections`为准。[Profiling Guide](https://docs.nvidia.com/nsight-compute/ProfilingGuide/index.html)

| 常见Section | 先回答的问题 |
|---|---|
| `LaunchStats` | 启动规模和每block资源配置是什么？ |
| `Occupancy` | 配置允许驻留多少warp，运行中实际驻留情况如何？ |
| `SpeedOfLight` | 计算与内存吞吐的总体线索是什么？ |
| `ComputeWorkloadAnalysis` | 哪条计算管线承担主要工作？ |
| `MemoryWorkloadAnalysis` | 哪级存储、访问流量或内存指令吞吐值得继续查？ |
| `SchedulerStats` | 驻留warp中有多少可发射，发射是否受阻？ |
| `SourceCounters` | 源码/指令位置和等待采样能否进一步定位？ |

### 2.3 百分比先看对象和分母

例如`sm__throughput.avg.pct_of_peak_sustained_elapsed`包含硬件对象、指标名称、聚合方式及相对峰值的时间口径。先查看Metric Details及本机指标说明；`active`与`elapsed`分母不同，不能直接混比。[CLI指标结构](https://docs.nvidia.com/nsight-compute/NsightComputeCli/index.html)

| 概念 | 含义 | 不应解释为 |
|---|---|---|
| theoretical occupancy | 当前配置与资源约束允许的驻留warp比例 | 运行全程实际占用 |
| achieved occupancy | 按工具定义统计的实际驻留比例 | 计算单元利用率 |
| eligible warp | 已满足下一条指令发射条件的warp | 已经发射 |
| pipeline throughput | 特定执行管线的处理速率或相对上限比例 | 所有计算资源都满载 |
| DRAM throughput | 设备显存层级的数据吞吐 | 所有存储层级的利用率 |

Occupancy高低应结合耗时判断。减少寄存器可能增加驻留，也可能引入spill或重计算；不能只追求某个百分比提高。某种stall比例大也不一定意味着它主导耗时，应先看调度是否缺少可发射工作；Tensor指令一次承担大量运算，发射率也不能直接等同计算吞吐。[官方排查指南](https://docs.nvidia.com/nsight-compute/ComputeTriage/index.html)

## 3 如何开始一次小范围采集

### 3.1 先核对环境

```bash
ncu --version
ncu --help
ncu --list-sets
ncu --list-sections
ncu --query-metrics
```

同时记录GPU、驱动、应用版本、输入规模和精度。在线文档可能比本机新，平台/GPU支持与已知问题应看对应版本的[Release Notes](https://docs.nvidia.com/nsight-compute/ReleaseNotes/index.html)。本笔记核对时在线页面首项为2026.3.1，不据此推定本机支持这些功能。

若出现`ERR_NVGPUCTRPERM`，表示性能计数器权限受限，不表示模型运行失败。容器内CUDA可用也不保证可以采计数器；按实际驱动和管理员策略处理。[NVIDIA权限说明](https://developer.nvidia.com/nvidia-development-tools-solutions-err_nvgpuctrperm-permission-issue-performance-counters)

### 3.2 过滤调用，再选择指标

下面的`workload.py`是占位程序，`TARGET_KERNEL`需替换为目标kernel名称的匹配表达式。示例只演示语法，未在本机执行：

```bash
ncu --set basic \
  --kernel-name-base demangled \
  --kernel-name 'regex:TARGET_KERNEL' \
  --launch-skip 10 --launch-count 1 \
  -o kernel_basic python workload.py
```

这里跳过的是**符合kernel过滤条件的10次launch**，不是10个batch或10个训练step。次数须依据调用序列确定，不能把这个示例数字当成预热标准。采集后确认命中的确实是预期阶段、shape和调用实例。[CLI过滤选项](https://docs.nvidia.com/nsight-compute/NsightComputeCli/index.html)

若应用已经使用NVTX push/pop范围`measure`标出完成预热后的目标区间，可用：

```bash
ncu --nvtx --nvtx-include 'measure/' \
  --section SpeedOfLight --section LaunchStats --section Occupancy \
  --launch-count 1 -o kernel_target python workload.py
```

`measure/`的尾部斜杠表示push/pop范围；start/end范围语法不同。应用必须实际发出NVTX标记，仅有其他profiler的阶段名称不保证该过滤可用。这个示例采区间内一个匹配调用，不是整个区间的累计报告。

需要额外指标时，沿用同一调用过滤条件，增加已确认存在的`--section`；不必直接切换成`--set full`。Roofline也应先查询并选取匹配计算路径的Section，不假设某个Set在所有版本都包含同一组图表。

### 3.3 打开报告进行比较

`-o`指定输出基名，使用工具实际生成的报告路径。常见文件后缀为`.ncu-rep`，实际格式以所用版本为准。把真实路径替换到下面命令：

```bash
ncu-ui REPORT_PATH
ncu --import REPORT_PATH --page raw --csv
```

在UI中先核对执行对象与采集设置，再查看Details和指标公式；需要源码归属时还需相应line information与源码，缺少时不能直接将SASS位置对应到Python代码。Baseline比较用于同口径报告之间的差异分析，不会自动证明因果或端到端收益。[UI报告指南](https://docs.nvidia.com/nsight-compute/NsightCompute/index.html)

## 4 Roofline：先看上限，再查差距

定义同一工作范围内的计算量为FLOPs，某一级存储的数据流量为Bytes，执行时间为T：

```text
算术强度 I = FLOPs / Bytes          单位 FLOP/byte
实际性能 P = FLOPs / T              单位 FLOP/s
简化性能上界 = min(计算峰值, 带宽 × I)
```

横轴表示每搬运一字节能做多少计算，纵轴表示每秒完成多少计算。斜线来自带宽约束，水平线来自所选计算路径上限。两者交点划分模型中的潜在限制区域；一个点远低于屋顶时，不能仅按它在交点左边或右边就宣布实际瓶颈。[NVIDIA Roofline基础说明](https://developer.nvidia.com/blog/accelerating-hpc-applications-with-nsight-compute-roofline-analysis/)

阅读时按三个步骤核对：

1. **计算口径匹配。** Tensor Core与普通FP32路径不能混用峰值；数学工作量也可能与硬件实际执行量不同，例如边界padding。
2. **存储层级匹配。** DRAM、L2、L1的数据流量不同，各层级的算术强度应使用对应Bytes。不能将输入tensor大小当成实际DRAM流量。
3. **继续解释差距。** 接近相应屋顶支持资源限制的判断；远低于屋顶时，再查并行规模、等待、指令路径或数据访问效率。频率与采集条件也要一致。[官方Roofline排查](https://docs.nvidia.com/nsight-compute/ComputeTriage/index.html)

教学算例：若同一kernel完成100 GFLOP，DRAM实际流量为20 GB，执行10 ms，则I=5 FLOP/byte、P=10 TFLOP/s。假设适用计算峰值为100 TFLOP/s、DRAM带宽为2 TB/s，则简化屋顶为10 TFLOP/s。该点接近所设带宽屋顶；若实际只达2 TFLOP/s，就还需解释与屋顶之间的差距。这里采用十进制单位和假设参数，不对应具体设备。

Roofline不能回答框架是否支持batch、调用为何被拆分，也不能单独证明换后端会加速；这些问题需要调用路径或受控对照补充。

## 5 为什么采集结果可能偏离正常运行

硬件计数器并非总能一次全部采齐，多pass采集可能需要replay。选择时明确分析对象：[Profiling Guide](https://docs.nvidia.com/nsight-compute/ProfilingGuide/index.html)

| 模式 | 重放对象 | 使用前确认 |
|---|---|---|
| Kernel replay | 单次kernel，必要时保存/恢复相关内存 | 是否依赖主机协作或其他并发工作 |
| Application replay | 整个应用重复运行 | 各轮执行和调用匹配是否足够确定，初始化成本是否可接受 |
| Range replay | 一段CUDA工作 | 支持的API范围与区间定义；结果归属整个range而非单个kernel |

采集可能串行化调用、控制时钟或清理缓存。关闭缓存清理也不自动恢复真实状态：多轮replay的缓存历史可能不同。比较时保留replay、cache/clock控制、采集pass数及过滤设置；不要把工具进程运行总时间当成任务吞吐。

若目标依赖多stream并发，不应只凭隔离kernel结果推断整体性能；先确认采集方式是否保留所需关系。若报告耗时与正常trace差异明显，先排查采集条件，再解释硬件瓶颈。

## 6 从报告到可验证结论

以下是使用上述概念组织分析的记录模板：

| 要素 | 应写清的内容 |
|---|---|
| 对象 | 哪个阶段、哪个shape、哪次调用；为何代表热点 |
| 可信性 | 版本、权限、过滤、replay和正常耗时对照 |
| 观察 | 绝对耗时、工作量、相关计算/存储/调度指标 |
| 假设 | 哪个资源或依赖可能限制性能，以及尚未排除什么 |
| 干预 | 只改变什么；预计哪个指标和时间会变化 |
| 验证 | 结果正确性、热点耗时、无profiler端到端收益 |

例如，计算管线吞吐高，可以优先核对该指令路径是否限制时间；DRAM吞吐低，不能直接排除L2、访存延迟或依赖问题；occupancy低，也不能单独作为优化目标。工具的规则提示用于选择下一项检查，不能代替实测结论。

当更换实现后调用更少、kernel更快时，先报告已测收益；算法、分块、复用和调用组织可能同时变化，唯一归因需要额外证据。减少总工作量甚至可能同时降低某项利用率并缩短耗时，因此最终以正确性和任务完成时间判断是否采用。

## 7 来源与验证范围

来源、读取日期及审核范围见[[04_Sources/模型工程/2026-10-21_Nsight Compute官方文档来源记录]]。本文是官方文档核对后的通用方法整理，未执行GPU profiling，未验证具体应用的瓶颈。命令按本机`--help`与对应版本文档调整。
