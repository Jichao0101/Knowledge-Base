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
