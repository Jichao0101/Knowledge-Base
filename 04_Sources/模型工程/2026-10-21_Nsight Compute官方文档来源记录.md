---
type: source_card
status: active
source_type: web
summary: NVIDIA Nsight Compute官方文档的主题索引与核对边界，支持基础知识整理。
scope: 工具定位、CLI过滤、报告解读、Roofline、replay及测量有效性。
risks:
  - 在线文档随版本更新；本次没有运行ncu或采集GPU计数器。
  - 官方排查提示不是跨设备通用的瓶颈判定阈值。
updated_at: 2026-10-21
---

# NVIDIA Nsight Compute官方文档来源记录

## 来源与用途

2026-10-21读取以下官方页面。在线Release Notes首项为2026.3.1；这仅标识本次网页内容，不代表本机版本。使用时通过本机查询核对参数和功能。

| 标识 | 官方来源 | 本次核对主题 |
|---|---|---|
| S1 | [Profiling Guide](https://docs.nvidia.com/nsight-compute/ProfilingGuide/index.html) | Sets and Sections、Replay、SchedulerStats、Reproducibility |
| S2 | [CLI Guide](https://docs.nvidia.com/nsight-compute/NsightComputeCli/index.html) | Quickstart、NVTX Filtering、launch过滤、metrics查询、导入报告 |
| S3 | [UI User Guide](https://docs.nvidia.com/nsight-compute/NsightCompute/index.html) | 报告视图、baseline比较、Metric Details与Roofline |
| S4 | [Compute Triage Guide](https://docs.nvidia.com/nsight-compute/ComputeTriage/index.html) | 指标可信性、计算/内存/延迟分支、Tensor路径及Roofline误读 |
| S5 | [Release Notes](https://docs.nvidia.com/nsight-compute/ReleaseNotes/index.html) | 功能、平台/GPU支持、已知问题；在线版本范围 |
| S6 | [性能计数器权限说明](https://developer.nvidia.com/nvidia-development-tools-solutions-err_nvgpuctrperm-permission-issue-performance-counters) | ERR_NVGPUCTRPERM；设备可用与计数器权限不是同一条件 |
| S7 | [NVIDIA Roofline基础文章](https://developer.nvidia.com/blog/accelerating-hpc-applications-with-nsight-compute-roofline-analysis/) | 2020-11-18正文中的算术强度与计算吞吐；不采用网页附加的AI摘要作为证据 |

## 核对摘要

- S1：采集粒度及replay会影响结果；选更少的调用和指标可减少开销。Kernel、application、range模式的重放对象不同。
- S2：命令先区分“采哪些调用”和“采哪些指标”；NVTX过滤要求应用实际插桩，push/pop范围与start/end范围语法有别。
- S3：报告支持跨结果比较及指标公式查看；Roofline有多种定义与层级，应核对所选图表。
- S4：先判断采集可信性，再缩小性能假设；单一百分比不足以确定原因，优化需回到绝对耗时。
- S5/S6：支持范围与权限必须在实际环境核对，不能由CUDA程序运行成功推出profiling可用。
- S7：算术强度采用FLOPs/bytes，性能采用FLOPs/time；历史文章用于模型解释，不照搬其版本默认选项。

## 审核与使用边界

本次按上述原文交叉核对概念、CLI语法与结论边界，面向通用使用整理，不引用任何项目实验结果。在线文档关于报告扩展名和Roofline所属set存在版本沿革信息，因此不将某一默认扩展名或set成员固化为跨版本保证。命令仅完成文档级核对，未验证本机安装、权限、GPU支持或运行结果。

正式整理目标：[[01_Knowledge/模型/工具与平台/Nsight Compute基础与性能分析]]。

## 2026-10-26补充核对：torch trace、CPU/GPU时间与硬件诊断

本次为正式条目的工具对比、异步时间线及教学案例补充来源。保留前次核对记录；以下概念经官方原文核对后用于通用解释，不引入项目实测结论。

| 标识 | 官方来源 | 核对事实与使用边界 |
|---|---|---|
| S8 | [PyTorch 2.14 Profiler API](https://docs.pytorch.org/docs/2.14/profiler.html) | CPU/CUDA activities；record_shapes保存算子输入shape；with_flops按公式估算部分算子工作量；export_chrome_trace导出事件；shape/stack采集有额外开销。不是硬件带宽/实际FLOP计数器。stable链接本次重定向2.14，不代表用户环境版本。 |
| S9 | [PyTorch Profiler教程](https://docs.pytorch.org/tutorials/recipes/recipes/profiler_recipe.html) | Self CPU排除子算子、CPU total包含子算子；汇总可按输入shape分组，汇总表与时间线用途不同。 |
| S10 | [PyTorch 2.14 CUDA semantics](https://docs.pytorch.org/docs/2.14/notes/cuda.html) | CUDA异步执行、同步计时与CUDA Event；同stream顺序及跨stream依赖须明确。CPU返回不等于设备任务完成。 |
| S11 | [Nsight Systems分析指南](https://docs.nvidia.com/nsight-systems/AnalysisGuide/index.html) | CUDA API、kernel和内存活动分别统计；runtime与GPU活动有correlation关联；累计百分比不等于应用墙钟占比。不可跨工具假定ID格式一致。 |
| S1/S2复核 | [NCU Profiling Guide](https://docs.nvidia.com/nsight-compute/ProfilingGuide/index.html)、[CLI Guide](https://docs.nvidia.com/nsight-compute/NsightComputeCli/index.html) | basic/full决定指标量，过滤决定调用范围；launch-skip/count使用匹配调用计数。重放与时钟/缓存控制限制对正常时间线的直接外推。 |

审核结论：以“时间线确定执行关系，计数器分析热点内部，benchmark检验任务收益”组织补充；CPU标记不作GPU同步边界。0.4/6.0/6.2ms异步算例、9/7/8ms重叠算例及B1/B16案例均为原创教学假设，数字仅用于推导，未运行模型或profiling。各工具功能随版本和采集配置变化，不把表格当成穷尽功能清单。

正式条目的本次新增范围：1.1～1.4、3.2的实例选择说明、6.1～6.2及验证范围。原有性能事实与来源关系保持；用户已明确要求评估后补充正式条目。


## 2026-10-26示例形式修订：直接读取trace JSON与ncu字段

按用户澄清，正式条目原batch扩展流程案例由1.6.1的trace JSON字段解读、1.6.2的ncu结果解读替代，交接清单顺延1.6.3。替代原因是原案例未展示实际输出结构；原批量扩展示例仅为教学假设，不是需保留的实验事实。前一来源记录保留以说明本次修订关系。

补核来源：[Kineto JSON导出实现](https://github.com/pytorch/kineto/blob/main/libkineto/src/output_json.cpp)的fmtTs、writeCompleteEvent、flow及metadata输出；[NVIDIA UI指南](https://docs.nvidia.com/nsight-compute/NsightCompute/index.html)的Summary、Details与结果选择；指标解释沿用S1/S3/S4。Kineto main不是固定版本接口，示例只抽取常见字段布局，不声称可解析任意版本导出。

教学JSON采用人为给定的CPU阶段、算子、launch、kernel及关联ID，kernel名teaching_gemm为虚构；时间单位µs，事件区间及嵌套关系可手工复算。ncu表为按section重排的模拟值，不是原始命令输出。两者仅假设经过同一任务实例核对，不能凭相同stream或名称跨报告确认身份。

审核范围：逐字段解释、单位/分母区别、ID关联边界、CPU/GPU重复计时、存储汇总与DRAM分层、occupancy与eligible warps差别。数值计算与JSON语法做本地检查；无真实GPU采集，不能用示例确定实际应用瓶颈。


## 2026-10-26真实trace替换及阅读顺序修订

按用户明确要求，本次以真实片段替代上一节所述模拟trace，并将正文重排为时间线、实例选择、ncu指标、Roofline与验证的连续解释。此前“trace示例均为模拟”的说明由本条替代；原ncu数值依然是独立教学模拟，未与真实kernel建立实测配对。cat是事件类别，name是具体事件名，二者共同描述同一个事件；纠正原表把两个字段混同四种事件的表述。

原始来源：`/mnt/d/qwen_models/sample_eval/s02_sample_eval/operator/profile_b1/rank0/trace.json`。本次只读解析已有云端采集产物，未重跑模型。提取规则：选择首条Input Dims为`[[4781,4096],[4096,12288]]`的aten::mm；按External id=5452唯一关联到目标CUTLASS kernel，再按correlation=15321唯一找到cuda_driver/cuLaunchKernel；按相同CPU pid/tid及完整时间包含关系找到experiment/language_prefill（External id=5146）。四条原始事件中未出现关联歧义。

正文嵌入真实事件的字段子集，保留原始时间戳、持续时间、名称、ID、shape、dtype及所展示的启动参数，不平移时间或改名；只省略其他事件和未讲解字段。CPU算子16.539µs，Driver API 3.709µs，GPU kernel1967.384µs；API返回到kernel开始2945.761µs。grid=[304,6,1]共1824 blocks，block=[256,1,1]；232寄存器/线程、73728 bytes共享内存。blocks per SM=16.581818与trace设备110 SM的1824/110一致，是平均工作量，不是实测驻留。估算occupancy字段为0，不提升为实测硬件结论。

前述官方来源仍用于字段与测量机制解释；实际例子只说明这份trace可观察到什么，不据此推广模型瓶颈。全文通用条目不依赖项目记录作为学习前置；原始产物路径集中在本来源记录，未写入hash。验证范围为JSON子集一致性、关联唯一性、嵌套和算术；ncu模拟数值与真实trace明确分开。
