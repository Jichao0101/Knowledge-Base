---
type: project_practice_record
status: user_reported
project: AI-Career-Transition
learning_stage: Phase 1-C - VLM baseline and benchmark draft
practice_kind: prompt_and_single_eye_roi_diagnostic
summary: 记录 Qwen2.5-VL-3B-Instruct 在既有 5-case 开发集上的文本示例、标签定义顺序和单眼 ROI 诊断；结果证明预测分布对 prompt 与输入合同敏感，但没有形成稳定的细粒度眼态分类能力。
sources:
  - 2026-08-17 用户提供的 Google Colab prompt 对比、逐 case 输出和单眼 ROI 运行结果
  - 2026-08-17 用户确认眼部框来自生产环境验收标注，并已人工校验裁剪 ROI
  - 02_Projects/AI-Career-Transition/30_实践记录/P01C_VLMZeroShot初始基线_2026-08-15_实践记录.md
  - 02_Projects/AI-Career-Transition/20_学习记录/P01C_VLM基线与Benchmark_学习记录.md
scope: 既有 5-case 开发集上的文本任务定义、定义顺序敏感性、双眼联合输出与单眼 ROI 输入诊断。
risks:
  - 结果由用户在 Colab 运行并粘贴，代理未访问模型、原图、标注、裁剪图或运行环境进行独立复跑。
  - 5 个 case 已参与 prompt 和错误分析，只能作为开发/诊断集；准确率变化不能外推为泛化能力提升。
  - 文本示例只是在 prompt 中提供类别语义，不是带示例图片的严格多模态 few-shot。
  - 单眼 ROI 同时改变视觉输入、任务粒度、prompt 和输出 schema，不能把结果变化唯一归因于裁剪。
  - 模型文件 hash、精确 revision、许可证快照、ROI 坐标与裁剪图 hash 尚未冻结。
updated_at: 2026-08-17
---

# 1 Phase 1-C VLM Prompt 与单眼 ROI 诊断

## 1.1 实践合同

- 目标：在不继续追求开发集高分的前提下，检查文本类别定义、定义顺序和单眼 ROI 输入是否改变既有 zero-shot 失败模式。
- 非目标：不声明稳定 benchmark、泛化性能、模型内部特征激活机制或参数规模归因；不执行 3B/7B 选型对比。
- 输入：沿用 2026-08-15 已参与错误分析的 5 个内部授权 case。
- 标签：`open | closed | narrow | abstain`。
- 解码：用户代码保持 `do_sample=false`、`num_beams=1`、`max_new_tokens=64` 和 seed `47`。
- 输出归一化：允许单个 `json` Markdown 代码围栏，归一化后解析固定 JSON schema。

用户粘贴的本轮 `25/25` 次原始输出均为单个 `json` Markdown 代码围栏，归一化后全部解析成功；下表保存对应解析值、期望值和评分结果。原始空白与缩进不作为评分合同的一部分。

本记录承接 [[02_Projects/AI-Career-Transition/30_实践记录/P01C_VLMZeroShot初始基线_2026-08-15_实践记录]]。原始 zero-shot 在相同 5-case 上的 case exact match 和 per-eye accuracy 均为 `20%`，并对 `10/10` 只眼睛预测 `closed`。

## 1.2 文本示例诊断

prompt 增加三个文字示例：

1. 眼睑明显分开、眼球区域和眼部轮廓足以辨认时为 `open`。
2. 墨镜透光度过低、无法辨认眼睑开合和眼球区域时为 `abstain`。
3. 上下眼睑仍有狭窄缝隙但不是完全闭合时为 `narrow`。

用户报告结果：

| case | expected | parsed output | pass |
|---|---|---|---:|
| 1 | `closed / closed` | `narrow / narrow` | false |
| 2 | `abstain / open` | `open / open` | false |
| 3 | `open / open` | `open / open` | true |
| 4 | `abstain / abstain` | `narrow / narrow` | false |
| 5 | `narrow / narrow` | `narrow / narrow` | true |

聚合结果：

- case exact match：`2/5 = 40%`。
- per-eye accuracy：`5/10 = 50%`。
- 预测分布：`open 4/10`、`narrow 6/10`，不再输出 `closed` 或 `abstain`。
- 平均推理时间：`11.098s/case`。
- 峰值显存 allocated：`8.843 GiB`；reserved：约 `9.328 GiB`。

本轮打破了原始 `closed` 类预测坍缩，但预测集中到文字示例中的 `open/narrow`。这支持“输出对任务语义示例敏感”，不支持“准确率提升已经证明分类能力提升”，也不支持模型内部已激活瞳孔或眼白等具体视觉特征的机制结论。

## 1.3 标签定义顺序诊断

后续 prompt 不再提供 A/B/C 示例，只保留四个标签的文字定义，并改变定义顺序。

### 1.3.1 顺序 A：abstain → closed → narrow → open

| case | expected | parsed output | pass |
|---|---|---|---:|
| 1 | `closed / closed` | `closed / closed` | true |
| 2 | `abstain / open` | `open / open` | false |
| 3 | `open / open` | `closed / closed` | false |
| 4 | `abstain / abstain` | `closed / closed` | false |
| 5 | `narrow / narrow` | `closed / closed` | false |

- case exact match：`1/5 = 20%`。
- per-eye accuracy：`3/10 = 30%`。
- 预测分布：`closed 8/10`、`open 2/10`。
- 平均推理时间：`7.988s/case`。

### 1.3.2 顺序 B：open → closed → narrow → abstain

| case | expected | parsed output | pass |
|---|---|---|---:|
| 1 | `closed / closed` | `closed / closed` | true |
| 2 | `abstain / open` | `open / open` | false |
| 3 | `open / open` | `open / open` | true |
| 4 | `abstain / abstain` | `closed / closed` | false |
| 5 | `narrow / narrow` | `closed / closed` | false |

- case exact match：`2/5 = 40%`。
- per-eye accuracy：`5/10 = 50%`。
- 预测分布：`closed 6/10`、`open 4/10`。
- 平均推理时间：`7.874s/case`。

两种顺序只改变文字定义排列，case 3 的双眼预测便从 `closed/closed` 变为 `open/open`。由于只有 5 个 case，一个 case 即对应 20 个百分点的 case accuracy，不能把 `40%` 当成稳定能力增益。两种定义 prompt 也都没有输出 `narrow` 或 `abstain`，说明类别边界仍不稳定。

## 1.4 单眼 ROI 诊断

用户从与原图同名的 JSON 标注中读取两个眼部框，按画面横坐标区分左右，分别裁剪为单眼图片，再用单字段 schema 独立推理。用户说明眼部框来自生产环境验收标注，并已人工校验裁剪 ROI；代理未读取这些文件或裁剪图。

单眼 prompt 输出：

```json
{"eye_state": "open | closed | narrow | abstain"}
```

逐眼结果：

| case | 眼睛 | expected | parsed output | pass |
|---|---|---|---|---:|
| 1 | left | `closed` | `open` | false |
| 1 | right | `closed` | `abstain` | false |
| 2 | left | `abstain` | `abstain` | true |
| 2 | right | `open` | `abstain` | false |
| 3 | left | `open` | `abstain` | false |
| 3 | right | `open` | `open` | true |
| 4 | left | `abstain` | `abstain` | true |
| 4 | right | `abstain` | `abstain` | true |
| 5 | left | `narrow` | `abstain` | false |
| 5 | right | `narrow` | `abstain` | false |

聚合结果：

- normalized JSON parse success：`10/10 = 100%`。
- per-eye accuracy：`4/10 = 40%`。
- 预测分布：`abstain 8/10`、`open 2/10`，未输出 `closed` 或 `narrow`。
- 平均推理时间：`1.030s/eye`。
- 峰值显存 allocated：`7.030 GiB`；reserved：`9.271 GiB`。

单眼 ROI 没有提高相对上一版全图定义 prompt 的 per-eye accuracy，并把主要预测分布转移到 `abstain`。但该实验同时改变了视觉输入、双眼联合任务、prompt 和输出 schema，因此最强允许结论是“单眼 ROI + 单眼任务合同没有修复当前失败”，不能把结果唯一归因于 ROI，也不能证明模型普遍缺少图像分类能力。

## 1.5 主动学习诊断与系统迁移

围绕上述结果完成的主动学习诊断形成以下边界：

1. prompt 定义、示例和顺序是 baseline 配置的一部分，不能在调试后仍把原开发集当作独立泛化证据。
2. 准确率变化需要结合样本量、预测分布和逐 case 变化解释；小样本上的单次提高不是能力提升证明。
3. ROI 实验若同时改变任务粒度、prompt 和 schema，只能评价整个新输入合同，不能隔离裁剪的单一因果作用。
4. 失败 baseline 可以用于确定模型适用边界，不要求为了提高开发集分数持续调 prompt。
5. 生产系统中，专用感知模型适合输出眼态、视线和头姿等低层结构化事实；VLM 更适合全局语义、长尾解释和多源上下文辅助；时序状态机负责持续时间、滤波和滞回；策略门禁决定报警或动作。

## 1.6 阶段结论与停止规则

- Qwen2.5-VL-3B-Instruct 的加载、预处理、结构化生成、归一化、解析和资源记录链路可运行。
- 在当前全图和单眼任务合同下，细粒度眼态结果对 prompt 与输入合同敏感，且类别分布不稳定。
- 现有 5-case 已充分承担开发/诊断用途，不再通过枚举 prompt 顺序或继续裁剪来追求开发集分数。
- 文本类别示例完成的是 prompt 敏感性诊断，不记为带图像示范的严格多模态 few-shot。
- 若未来需要形成可移交 benchmark，再独立冻结模型身份、未查看留出集、ROI/input contract 和门禁；这不是当前学习收尾的默认阻塞项。

## 1.7 未验证项

1. 模型文件 hash、精确 checkpoint revision 和许可证快照。
2. ROI 坐标、裁剪尺寸、裁剪图内容 hash 与代理独立复跑。
3. 带图像示范的多模态 few-shot 与独立未查看留出集表现。
4. 专用眼态模型、VLM 语义层、时序状态和策略门禁的端到端集成验证。
