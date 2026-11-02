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

Torch Profiler把模型算子与CPU/GPU执行关联起来，Nsight Compute进一步通过选定GPU工作的硬件指标，帮助区分这些性能限制。使用它的前提是热点已经与实际任务关联，否则即使某个kernel被优化，完整任务也未必受益。框架到kernel的关联方法见[[01_Knowledge/性能分析/PyTorch Profiler与框架执行分析]]。

本文先明确采什么，再介绍采集操作，随后解释报告，并用官网案例连接指标与原因。硬件机制的进一步推导见[[01_Knowledge/性能分析/GPU执行与存储瓶颈分析]]。

## 1.2 采集前先作两个决定

### 1.2.1 选择哪一次执行

同名kernel可能在不同层、不同shape中反复执行。本文把一次具体的kernel启动称为“执行实例”；选择实例时，用阶段、输入shape、dtype、grid/block和调用位置共同确定身份。这样才能把硬件报告与待优化的模型工作对应起来。

框架trace的External id和correlation用于原采集内部的事件关联；下一轮ncu使用自己的调用清单，需要重新找到对应实例。若实例位置不清楚，应先取得短窗口内的调用清单，核对以后再做详细采集。

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

在单kernel报告中，Duration描述选定执行实例的设备耗时。接着阅读这个实例的计算管线吞吐和各级存储吞吐，选择需要下钻的资源；再结合驻留与发射指标，解释吞吐形成的原因。各项指标共同约束解释范围。

| 观测 | 它回答什么 | 不能据此推出什么 |
|---|---|---|
| Duration | 本次采集条件下的设备工作时长 | 完整请求时长、采集进程总耗时 |
| SM Throughput | SM相关管线吞吐相对于相应上限 | 有多少百分比SM正在工作 |
| Memory Throughput | 存储侧汇总吞吐；需继续分层 | 必然等于DRAM带宽 |
| DRAM/L2 Throughput | 各层自己的吞吐与归一化口径 | 两者百分比可以相加或相减 |
| Theoretical/Achieved Occupancy | 配置允许与实际观测的驻留warp比例 | 算力效率，或越高越快 |
| Eligible Warps Per Scheduler | 平均可发射warp数 | 空闲周期百分比 |

例如dram__throughput.avg.pct_of_peak_sustained_elapsed需按持续峰值及elapsed周期解释；sm__warps_active.avg.pct_of_peak_sustained_active使用active周期。分母不同，不能直接相除。缺项可能是未采集或不支持，不应填0。指标名以设备和版本查询为准。[Profiling Guide](https://docs.nvidia.com/nsight-compute/ProfilingGuide/)

### 1.4.3 把指标组织成能够被反驳的解释

读完字段以后，需要把报告中的数字连接起来。首先固定待解释的现象，例如“同一投影在batch增大时，工作量与耗时近似同比增长”。这个现象说明单位工作处理效率变化不大，却不能区分计算、访存和等待。NCU的作用是补上区分这些机制所需的证据，而不是为已有猜测寻找一个高百分比。

比较B1与B16的NCU报告时，先确认两个执行实例来自同一模块的同一种投影，精度一致，输入规模分别符合各自batch，并核对重放、缓存和时钟条件。随后将每个实例的Duration与其工作量一起读：对于`[M,K] × [K,N]`的GEMM，用2MNK估算逻辑计算量，除以该实例的设备耗时，得到逻辑计算吞吐。DRAM、L2等层级的实际数据搬运量则读取对应计数器；缓存复用和中间访问决定了它们与输入tensor大小之间的差异。

如果计算吞吐看起来较高，应继续确认高的是哪条计算管线，是否与实际精度和Tensor Core路径相符，并用匹配的计算屋顶判断是否接近可持续上限。耗时与FLOPs同比增长说明处理效率近似稳定；管线指标和匹配的吞吐上限进一步支持计算资源限制的判断。反过来，若某级存储吞吐较高，应检查该级实际流量和访问组织，再判断耗时是否与这部分数据处理相符；DRAM不高并不排除L2、共享内存或访存延迟限制。

如果计算与各级存储吞吐都不高，就应转向“为什么发射不出足够的工作”。此时将实际驻留、eligible warps、发射情况和等待原因连起来看：驻留少时，检查工作规模及寄存器、共享内存等容量约束；驻留多而就绪少时，追查数据或指令依赖；等待集中在某类访问时，再进入对应存储与源码证据。低occupancy本身不是根因，高occupancy也不能排除等待。

因此，可信的局部结论应说明证据怎样排除了替代解释。例如“在该shape和采集条件下，目标管线接近相应上限，工作量增长与耗时增长相符，支持计算吞吐限制”，比“SM指标高，所以整个模型compute-bound”更准确。证据尚不足时，写成“支持某假设，仍缺哪项观测”，并据此选择下一次采集。Roofline、存储层级与调度之间的机制见[[01_Knowledge/性能分析/GPU执行与存储瓶颈分析]]。

## 1.5 官网报告案例：驻留充分，为什么仍发射不足

下面使用NVIDIA于2021-01-27发表的[ADO Part 2正文](https://developer.nvidia.com/blog/analysis-driven-optimization-analyzing-and-improving-performance-with-nvidia-nsight-compute-part-2/)。工作负载为向量平均后做矩阵向量乘法，实例为gpu_version2；硬件V100-SXM2-32GB，CUDA 11.1、驱动455.23.05。它不是前篇真实模型trace的后续报告，也未在本地复现。

| 同一分析阶段的观测 | 官网值 |
|---|---:|
| 每scheduler平均active warps | 16.00 |
| 每scheduler平均eligible warps | 0.69 |
| 每warp平均LG Throttle等待 | 82.8 cycles |
| 每warp平均两次发射间隔 | 109.1 cycles |
| 向量平均操作所对应源码访问行的理想transactions | 134,217,728 |
| 同一源码访问行的实际transactions | 1,073,741,824 |

先读第一对数字：每scheduler平均有16个active warps，却只有0.69个eligible warps。这说明驻留的工作很多，但在观测时刻能够发射的工作很少，因此不能优先把问题解释为“没有足够的驻留warp”。16.00与0.69均为采集期间每scheduler的warp数量均值，分别描述驻留数量和就绪数量。

接着看这些warp在等什么。LG Throttle为82.8 cycles，而平均两次发射间隔为109.1 cycles，提示本地/全局内存指令相关队列压力值得追查。这里的周期统计用于定位等待类型，不直接换算为整个kernel中可消除的墙钟比例，更不能据此宣布DRAM带宽已满。

最后沿源码关联到向量平均操作的内存访问行。该行实际transactions为1,073,741,824，理想transactions为134,217,728，二者之比为8。同一有用访问需要比理想情况更多的事务，提供了访问组织低效的具体证据。三层观察连起来才形成解释：驻留已有一定规模，但可发射工作不足；等待指向访存指令压力；源码访问的额外事务又支持合并效率不足这一机制。仅有第一对数字，只能定位到“就绪不足”，还到不了最后的访存判断。

由此得到的干预预测是：改善目标访问组织后，额外事务应减少，相关等待和kernel绝对耗时也应改善。若该访问行的transactions下降，而kernel耗时不变，就应重新检查这处访问对总耗时的影响；若只看到耗时下降而其他机制也改变，则可以确认收益，不能确认唯一原因。这段推导复用官网观测，预测本身不冒充本地完成的实验。

原文对早期两轮profiling明确提醒N不同，因此这里不拿跨轮报告duration计算加速比。不拼入其他报告的SOL、寄存器或共享内存数值。旧案例帮助理解证据链，当前指标定义仍按官方工具文档核对；不将V100上限和阈值套到其他GPU。

## 1.6 从报告结论回到真实任务

硬件判断首先描述NCU实际采集的执行实例。要形成阶段判断，需要回到原trace，把阶段、kernel名称、输入shape和启动配置相同的调用归为一组，检查组内调用位置与耗时分布，再评估已采实例对这组调用的代表性。

随后计算这组调用在阶段中的时间贡献。以无重叠的教学情形为例：某组kernel累计执行7ms，所属设备阶段持续10ms，则该组占阶段时间的70%，值得优先诊断。这个比例用于安排分析顺序；阶段中其余工作仍需按各自shape和执行路径解释。多stream情形则先检查重叠与依赖，再评估局部优化对阶段完成时间的影响。

同样，不能把几次NCU重放后的Duration按原调用数直接相加，宣称得到正常运行的阶段时长。各组调用的次数与阶段时间贡献来自原trace，计算、访存和调度机制的证据来自受控NCU采集；阶段、模块、shape和启动配置将两类报告对应起来。多stream情况下还要检查这些工作是否位于任务完成的关键依赖路径：累计时间很高、但被其他工作完全覆盖的kernel，加速后可能不缩短请求。

对报告的解释应形成可验证的预测。例如，若认为请求过多造成访存队列压力，改变访问组织后应检查请求、等待和绝对耗时是否按预期变化，而不仅是某个占比是否下降。减少寄存器可能增加驻留，却也可能引入spill；任何局部改善都需要复测。

ncu报告与原时间线不一致时，先检查对象与采集扰动，再解释硬件原因。最终以相同任务合同下的正确性和独立benchmark检验收益，不能用采集过程中的主机计时替代正常执行时间。

对闭源计算库，通常可以分析其受支持CUDA kernel，但不一定获得库源码行号。API Stream提供交互式API/kernel导航，不等同系统时间线；源码级分析需要相应行信息。[UI指南](https://docs.nvidia.com/nsight-compute/NsightCompute/index.html)

官方依据及案例边界见[[04_Sources/性能分析/2026-10-27_性能分析系列官方文档依据]]。本页官网案例替换了原教学模拟表，未新增模型GPU实测；真实模型trace保留在框架篇，旧来源说明保留在[[04_Sources/模型工程/2026-10-21_Nsight Compute官方文档来源记录]]。
