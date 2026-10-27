---
type: knowledge
status: reviewed
domain: 性能分析
summary: 选择代表性kernel并解释采集条件、报告字段和官方调度访存案例。
sources:
  - 04_Sources/性能分析/2026-10-27_性能分析系列官方文档依据.md
  - 04_Sources/模型工程/2026-10-21_Nsight Compute官方文档来源记录.md
scope: NVIDIA CUDA kernel诊断；CLI示例为Bash语法，未在本机执行。
risks:
  - 文档审核不等于本机实测；工具版本、硬件、权限和输入条件须现场确认。
  - 教学推导、官方历史案例和项目trace不能互相冒充，单指标不能证明唯一瓶颈。
review_basis: 2026-10-27按用户确认的系列方案拆分既有内容并核对官方文档；无新增GPU运行。
updated_at: 2026-10-27
---

# 1 Nsight Compute基础与性能分析

## 1.1 从“哪个kernel慢”进入“为什么慢”

框架或系统时间线已经告诉我们哪些GPU工作占用了时间，但还不能充分解释这些工作内部的限制。一个kernel可能没有足够的并行工作，也可能受计算管线、存储访问或指令依赖影响；相同的耗时表象可以来自不同机制。

Nsight Compute通过选定GPU工作的硬件指标，帮助区分这些解释。使用它的前提是热点已经与实际任务关联，否则即使某个kernel被优化，完整任务也未必受益。框架到kernel的关联方法见[[01_Knowledge/性能分析/PyTorch Profiler与框架执行分析]]。

本文先明确采什么，再介绍采集操作，随后解释报告，并用官网案例连接指标与原因。硬件机制的进一步推导见[[01_Knowledge/性能分析/GPU执行与存储瓶颈分析]]。

## 1.2 采集前先作两个决定

### 1.2.1 选择哪一次执行

同名kernel可能在不同层、不同shape中反复执行，不能用名称代替实例身份。选择对象时应带上阶段、shape、dtype、grid/block和调用位置，确认它代表的是要优化的工作。

框架trace的External id和correlation只在原采集中建立关联，不能直接用作下一轮ncu的调用序号。若实例位置不清楚，应先取得短窗口内的调用清单，核对以后再做详细采集。

### 1.2.2 为这个问题采哪些指标

采集范围与指标数量是两个独立选择：前者决定观察哪些执行，后者决定每次执行记录多少信息。

ncu把单个指标称为Metric，将相关指标组织为Section，再用Set组合多个Section。可以先了解启动规模、资源占用和总体吞吐，再根据问题补充计算、存储或调度信息。这样，详细采集有明确目的，而不是把所有计数器都打开以后再寻找解释。

采集本身也会改变执行条件。计数器可能需要多次重放；缓存、时钟和并发也可能与正常运行不同。因此，报告中的数值必须与采集方式一起解释，不能把每次采集都视为同一运行条件。

## 1.3 采集操作

### 1.3.1 检查环境与支持范围

先查询`ncu --version`和`--help`，再通过`--list-sets`、`--list-sections`、`--query-metrics`确认当前版本能采什么。记录GPU、驱动、应用版本与输入精度。

遇到`ERR_NVGPUCTRPERM`应按驱动和管理员策略处理。CUDA程序能够运行、容器内是root，都不自动表示有性能计数器权限。[权限说明](https://developer.nvidia.com/ERR_NVGPUCTRPERM)

### 1.3.2 先核对实例，再缩小采集范围

下列命令为Bash示例，workload.py是待替换的应用。应用必须实际发出NVTX push/pop范围`measure`；torch的`record_function`不会仅凭同名区间就成为NVTX。hook决定在哪里发出标记，本身不是计时器。

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

### 1.3.3 按问题选择section和重放方式

`basic`和`full`决定指标集合，不负责选择模型阶段。已确认少量热点时可以采full；也可以先用`SpeedOfLight`、`LaunchStats`和`Occupancy`，再按问题增加`ComputeWorkloadAnalysis`、`MemoryWorkloadAnalysis`、`SchedulerStats`或`SourceCounters`。

Kernel replay重放单个kernel；Application replay重跑应用，要求各轮调用能够可靠对应；Range replay采一段CUDA工作，结果归属整个范围。使用NVTX过滤不会自动把单kernel报告变成整个阶段的累计Roofline。

涉及主机协作或多stream并发时，确认所选模式保留了需要研究的关系。保存replay模式、pass数、cache/clock设置和过滤条件；关闭缓存清理也不自动恢复正常运行的缓存历史。[Profiling Guide](https://docs.nvidia.com/nsight-compute/ProfilingGuide/)

## 1.4 读报告：先确认范围，再连接指标

### 1.4.1 找到选定的执行结果

用ncu-ui打开报告，在Summary确认launch，再到Details阅读各section。先核对对象和采集条件是否正确，再解释指标。若需要导出字段，可使用：

```bash
ncu --import REPORT_PATH --page raw --csv
```

REPORT_PATH是实际报告路径，不假定扩展名跨版本一致。Metric Details用于查底层名称、单位和公式；遇到缺项，应先确认是否采集或支持，不要补成0。

### 1.4.2 从耗时读到吞吐，再读到调度

Duration给出这次工作的时间背景。随后看计算和存储各自完成了多少工作，判断值得下钻哪一侧；最后结合驻留与发射情况，解释资源为什么没有被充分使用。这是一条逐步缩小假设的阅读路径，不是用某个百分比直接判定瓶颈。

| 观测 | 它回答什么 | 不能据此推出什么 |
|---|---|---|
| Duration | 本次采集条件下的设备工作时长 | 完整请求时长、采集进程总耗时 |
| SM Throughput | SM相关管线吞吐相对于相应上限 | 有多少百分比SM正在工作 |
| Memory Throughput | 存储侧汇总吞吐；需继续分层 | 必然等于DRAM带宽 |
| DRAM/L2 Throughput | 各层自己的吞吐与归一化口径 | 两者百分比可以相加或相减 |
| Theoretical/Achieved Occupancy | 配置允许与实际观测的驻留warp比例 | 算力效率，或越高越快 |
| Eligible Warps Per Scheduler | 平均可发射warp数 | 空闲周期百分比 |

例如dram__throughput.avg.pct_of_peak_sustained_elapsed需按持续峰值及elapsed周期解释；sm__warps_active.avg.pct_of_peak_sustained_active使用active周期。分母不同，不能直接相除。缺项可能是未采集或不支持，不应填0。指标名以设备和版本查询为准。[Profiling Guide](https://docs.nvidia.com/nsight-compute/ProfilingGuide/)

## 1.5 官网报告案例：驻留充分，为什么仍发射不足

下面使用NVIDIA于2021-01-27发表的[ADO Part 2正文](https://developer.nvidia.com/blog/analysis-driven-optimization-analyzing-and-improving-performance-with-nvidia-nsight-compute-part-2/)。工作负载为向量平均后做矩阵向量乘法，实例为gpu_version2；硬件V100-SXM2-32GB，CUDA 11.1、驱动455.23.05。它不是前篇真实模型trace的后续报告，也未在本地复现。

| 同一分析阶段的观测 | 官网值 |
|---|---:|
| 每scheduler平均active warps | 16.00 |
| 每scheduler平均eligible warps | 0.69 |
| 每warp平均LG Throttle等待 | 82.8 cycles |
| 每warp平均两次发射间隔 | 109.1 cycles |
| 目标访问行的理想transactions | 134,217,728 |
| 目标访问行的实际transactions | 1,073,741,824 |

原文先发现驻留warp多但就绪少，再沿LG Throttle和源码关联检查访存；目标行的实际/理想transactions为8，支持访存合并效率不足的诊断。这不是“occupancy低”，也不能将0.69直接换成69%利用率。

原文对早期两轮profiling明确提醒N不同，因此这里不拿跨轮报告duration计算加速比。不拼入其他报告的SOL、寄存器或共享内存数值。旧案例帮助理解证据链，当前指标定义仍按官方工具文档核对；不将V100上限和阈值套到其他GPU。

## 1.6 从报告结论回到真实任务

对报告的解释应形成可验证的预测。例如，若认为请求过多造成访存队列压力，改变访问组织后应检查请求、等待和绝对耗时是否按预期变化，而不仅是某个占比是否下降。减少寄存器可能增加驻留，却也可能引入spill；任何局部改善都需要复测。

ncu报告与原时间线不一致时，先检查对象与采集扰动，再解释硬件原因。最终以相同任务合同下的正确性和独立benchmark检验收益，不能用采集过程中的主机计时替代正常执行时间。

对闭源计算库，通常可以分析其受支持CUDA kernel，但不一定获得库源码行号。API Stream提供交互式API/kernel导航，不等同系统时间线；源码级分析需要相应行信息。[UI指南](https://docs.nvidia.com/nsight-compute/NsightCompute/index.html)

官方依据及案例边界见[[04_Sources/性能分析/2026-10-27_性能分析系列官方文档依据]]。本页官网案例替换了原教学模拟表，未新增模型GPU实测；真实模型trace保留在框架篇，旧来源说明保留在[[04_Sources/模型工程/2026-10-21_Nsight Compute官方文档来源记录]]。
