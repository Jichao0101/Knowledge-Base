---
type: project_practice_record
status: user_reported
project: AI-Career-Transition
learning_stage: Phase 1-C - VLM baseline and benchmark draft
practice_kind: model_generation_substitution_and_resource_constraint_diagnostic
summary: 记录 Qwen3.5-4B 在既有 5-case 全图开发集上的代际替换尝试；首次运行因长分析输出未在预算内形成 JSON，后续可运行配置同时采用 INT4 与受限 max_pixels，用户报告结果未见改善，因此只能评价当前 T4 可部署配置，不能隔离模型代际能力。
sources:
  - 2026-08-17 用户提供的 Qwen3.5-4B 五个 case 原始截断输出、格式失败、耗时和显存结果
  - 2026-08-17 用户报告的 Qwen3.5-4B INT4、受限 max_pixels 全图重跑及“结果未优化”定性结论
  - 02_Projects/AI-Career-Transition/30_实践记录/P01C_VLMZeroShot初始基线_2026-08-15_实践记录.md
  - 02_Projects/AI-Career-Transition/30_实践记录/P01C_VLMPrompt与单眼ROI诊断_2026-08-17_实践记录.md
scope: 既有 5-case 全图开发集上的 Qwen2.5-VL-3B 与 Qwen3.5-4B 替换可行性、输出协议和 T4 资源约束诊断。
risks:
  - 全部结果来自用户在 Colab 的运行与转述，代理未访问模型、图片、运行环境或完整 notebook 独立复跑。
  - Qwen3.5 最终可运行配置同时改变模型代际、权重精度和像素预算，不是纯模型能力对照。
  - 用户没有提供 INT4 具体量化方案、max_pixels 数值、最终逐 case 输出或聚合指标，因此“未见改善”只能作为定性工程结果。
  - 5 个 case 已参与多轮 prompt、ROI 和错误分析，只能作为开发/诊断集。
  - 模型精确 revision、文件 hash、processor 配置和许可证快照仍未冻结。
updated_at: 2026-08-17
---

# 1 Phase 1-C Qwen3.5 代际替换与资源约束诊断

## 1.1 实践目的

本轮原计划用参数规模接近的新一代多模态模型替换 Qwen2.5-VL-3B，并在相同 5-case 全图任务上检查模型代际是否改善细粒度眼态分类。

理想的受控比较只改变模型 checkpoint，保持图片、prompt、输出 schema、预处理、像素预算、权重精度和解码合同一致。但实际运行受到 Tesla T4 显存约束，最终没有满足这一条件。

## 1.2 首次全图运行：输出协议失败

首次 Qwen3.5-4B 全图运行的五个输出都从自然语言图像分析开始，并在形成最终 JSON 前结束。归一化解析结果均为 `None`，失败标签均为 `invalid_output_format`。

| case | expected | elapsed | peak allocated | peak reserved | 结果 |
|---|---|---:|---:|---:|---|
| 1 | `closed / closed` | `7.169s` | `10.087 GiB` | `10.168 GiB` | 分析文本中断，未形成 JSON |
| 2 | `abstain / open` | `7.398s` | `10.086 GiB` | `10.168 GiB` | 分析文本中断，未形成 JSON |
| 3 | `open / open` | `7.500s` | `10.086 GiB` | `10.168 GiB` | 分析文本中断，未形成 JSON |
| 4 | `abstain / abstain` | `7.152s` | `10.086 GiB` | `10.168 GiB` | 分析文本中断，未形成 JSON |
| 5 | `narrow / narrow` | `7.791s` | `10.086 GiB` | `10.168 GiB` | 分析文本中断，未形成 JSON |

这些 case 的语义分类状态应记为 `not_evaluated`，不能把五次格式失败换算成模型眼态分类准确率为 0。运行现象说明模型替换还需要重新验证 chat template、思考/直接回答模式和输出 token 预算，不能只替换权重路径。

## 1.3 T4 可运行配置

用户后续报告：Qwen3.5-4B 的视觉输入与模型显存需求使当前 T4 环境无法维持原计划配置，因此改用 INT4 量化版本，并限制输入 `max_pixels`。输入仍采用全图，避免再引入单眼 ROI 任务合同。

用户定性结论为“结果并没有优化”。由于尚未提供最终逐 case 原始输出、解析结果、准确率、INT4 方案和 `max_pixels` 数值，本记录不补写数值结果，也不判断哪一个变量造成失败。

## 1.4 允许结论

本轮最强允许结论是：

> 在当前 Tesla T4 资源边界下，Qwen3.5-4B 需要采用 INT4 和受限像素预算才能完成当前实验配置；这一可部署配置在既有 5-case 开发集上未观察到用户可见的改进。

不能据此声称：

- Qwen3.5-4B 原始精度下不优于 Qwen2.5-VL-3B。
- INT4 是未改善的唯一原因。
- 限制 `max_pixels` 是未改善的唯一原因。
- 新模型普遍缺少细粒度视觉分类能力。

模型参数量接近也不保证显存占用、视觉 token 预算和推理链路相同。模型代际、量化精度与像素预算同时变化时，结果回答的是“当前硬件上的可部署配置是否产生收益”，不是纯粹的模型能力比较。

## 1.5 停止决定

当前不继续围绕这 5 个开发 case 搜索量化方案、`max_pixels`、prompt 或新模型版本。Qwen3.5 替换结果作为部署资源边界与实验混杂变量案例保留，下一步回到分层多模态系统：

```text
专用感知模型输出低层细粒度事实
→ VLM 提供全局语义和长尾辅助
→ 时序状态层执行滤波、持续时间与滞回
→ 策略门禁决定报警或动作
```

若未来具备更大显存，并能保持相同权重精度、像素预算、prompt 和预处理，再考虑补做纯模型代际对照；该实验不作为当前学习路线的阻塞项。
