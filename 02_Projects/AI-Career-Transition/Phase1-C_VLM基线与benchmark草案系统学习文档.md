---
type: project_learning_artifact
status: active
project: AI-Career-Transition
learning_stage: Phase 1-C - VLM baseline and benchmark draft
summary: 记录 Phase 1-C 的 VLM 数据流教学骨架、主动学习闭合证据、最小图像问答 baseline 设计、benchmark case 边界与待执行实践。
sources:
  - 2026-08-10 用户修正主动学习方法：知识大面积缺失时先教学骨架，再用主动重建和诊断题检查吸收
  - 2026-08-10 Phase 1-C VLM 数据流与视频持续闭眼任务主动学习对话
  - 2026-08-11 Phase 1-C baseline 可复现性、任务合同、分组门禁、case 证据边界、模型选择与本地环境主动学习对话
  - 02_Projects/AI-Career-Transition/当前阶段学习检查点.md
  - 02_Projects/AI-Career-Transition/多模态AI职业转型学习方案.md
  - 02_Projects/AI-Career-Transition/AI评测基本功系统学习文档.md
scope: VLM 输入输出数据流、视觉 token、projector、token 压缩、视频采样、图像问答 baseline、任务集来源边界、zero-shot/few-shot 和分组评测。
risks:
  - 本文是 Phase 1-C 学习材料，不代表已经运行开源 VLM、建立 benchmark 或完成阶段门禁。
  - 模型选择、依赖版本和具体命令会变化；运行 baseline 前必须重新固定模型、环境、输入样本和可复现命令。
  - 小型任务集只能使用公开、合成或明确授权数据；外部数据需要先建立来源记录。
updated_at: 2026-08-11
---

# 1 Phase 1-C VLM 基线与 benchmark 草案系统学习文档

## 1.1 如何使用本文

本文采用“教学骨架优先”的主动学习节奏。每个模块先给出最小可用解释，再通过闭卷画图、对比题、边界题或实践任务检查吸收情况。

默认闭环是：

```text
教学骨架
→ 主动重建
→ 缺口诊断
→ 微型补课
→ 迁移或实践题
→ 阶段证据记录
```

本文已从教学草案转为持续维护的 Phase 1-C 阶段学习文档，但不是 Phase 1-C 完成证明。阶段完成仍以 [[02_Projects/AI-Career-Transition/当前阶段学习检查点]] 的完成门禁为准。

## 1.2 覆盖区

| 覆盖区 | 必须能回答的问题 | 当前状态 |
|---|---|---|
| 单图 VLM 数据流 | 图片如何变成 LLM 可读取的输入序列 | 对话诊断已验证 |
| projector 与 token 压缩 | 维度对齐和 token 数量压缩为什么不是一回事 | 对话诊断已验证 |
| 视觉证据与问题语义 | LLM 如何通过 attention 关联图片区域和文本问题 | 对话诊断已验证 |
| 视频与多帧输入 | 空间分辨率、时间采样和上下文预算如何取舍 | 部分闭合 |
| 最小 VLM baseline | 如何运行一个可复现的图像问答最小基线 | 设计已验证，运行待执行 |
| benchmark 草案 | case 来源、期望行为、证据边界和失败标签如何定义 | 对话诊断已验证，case 未落盘 |
| 分组评测与微调边界 | 如何解释错误，什么时候不该微调 | 对话诊断已验证，结果待执行 |

## 1.3 2026-08-10 主动学习诊断结果

本轮诊断属于 Phase 1-C 的学习进度证据，不是阶段完成证明。

已闭合内容：

1. 能说明图片经 image encoder / ViT 形成 visual tokens，再经 projector 对齐到 LLM embedding 维度，并与 text token embeddings 组成连续输入序列。
2. 能区分普通 projector 的维度对齐作用和 token 数量压缩；能用 `576 x 1024 -> 576 x 4096` 解释 token 数不变、特征维度变化。
3. 能说明 VLM 通过 attention 在文本问题 token 与相关视觉 patch 之间建立关联；训练阶段学习 `Wq/Wk/Wv`，推理阶段用固定参数生成当前输入的 `Q/K/V` 和 attention weights。
4. 能把“单帧闭眼检测”和“10 秒内持续闭眼超过 2 秒”区分为空间判别与时序证据任务，并指出后者需要连续时长、帧段或时间范围作为可复核证据。

仍需继续检查的内容：

1. 视频采样密度、帧间隔和漏检风险之间的定量关系还需要结合具体输入预算继续练习。
2. “持续闭眼超过 2 秒”的 4 至 8 个最小 benchmark case 尚未完整落盘。
3. 开源小型 VLM baseline 未运行，因此不能声明模型输入输出、失败类型、zero-shot/few-shot 或分组评测已验证。

## 1.4 2026-08-11 主动学习诊断结果

本轮把“知道 baseline 名词”推进到“能够设计可复现、可评分、可审计的最小实验”。结论仍属于对话诊断证据，不替代模型运行记录。

已达到对话诊断意义上的 `working`：

1. 能列出 baseline 的关键固定项：输入图片、模型、推理配置、运行次数和输出格式，并进一步补齐随机种子。
2. 能区分 `execution_success`、单次 case 通过/失败、聚合指标和 baseline 门禁；错误答案不能因高温度或小模型能力有限而改记为任务成功。
3. 能说明评测合同和通过阈值必须在运行前冻结；查看测试错误并修改 prompt 后，原测试集已成为开发集，最终 few-shot 证据必须来自未参与调参的独立留出集。
4. 能说明总体 accuracy 或 macro accuracy 都不能替代关键组门禁；需要同时报告每组样本量、每组 accuracy、总体指标、macro 指标、worst-group 指标和安全关键组最低阈值。
5. 能说明仅保存最终 accuracy 不足以成为可靠证据，必须保存逐样本输入、原始输出和评分结果，才能复核分组指标、失败标签与 abstain 判断。
6. 已为单帧闭眼任务提出闭眼、睁眼、眯眼和眩光四类最小 case，并把判断边界修正为“任务所需眼部状态证据是否可辨认”，不把瞳孔可见性当作唯一必要条件。
7. 能解释第一个 baseline 应优先选择本地可运行、版本和推理配置清晰的模型；小模型 smoke test 只验证链路，不能代表另一 checkpoint 的能力结果。

本轮仍未验证：

1. 尚未冻结真实模型 revision、依赖版本、图片预处理、prompt 模板和完整解码配置。
2. 尚未运行 smoke test 或 2B 级 VLM baseline，未保存逐样本输出、显存峰值和失败记录。
3. 四类 case 仍是对话设计，尚未使用公开、合成或明确授权图片落盘。
4. 视频采样密度、帧间隔与持续事件漏检风险仍需在真实输入预算下验证。

# 2 单图 VLM 数据流

## 2.1 教学骨架

典型单图 VLM 不是把图片直接塞进 LLM。它先把图片变成一串视觉表示，再把这些表示转换到 LLM 能处理的 embedding 空间。

最小数据流是：

```text
图片
→ image encoder / ViT
→ visual tokens
→ projector
→ visual embeddings aligned to LLM dimension
→ 与 text token embeddings 组成同一输入序列
→ LLM autoregressive decoding
→ 文本答案
```

与纯 LLM 相比，VLM 多了三类关键对象：

| 对象 | 作用 | 常见误解 |
|---|---|---|
| image encoder | 从图片 patch 或区域中提取视觉 token | 不一定是 CNN；当前学习重点是 ViT 式视觉 token |
| visual tokens | 承载图片中不同 patch、区域或压缩后的视觉信息 | 通常不是一个全局图片向量 |
| projector | 把视觉 token 的特征维度对齐到 LLM embedding 维度 | 不等同于必然减少 token 数量 |

进入 LLM 前，视觉 token 和文本 token 会组成一个连续上下文。例如：

```text
[<image_token_1>, <image_token_2>, ..., <image_token_N>,
 "驾驶员", "有没有", "闭眼", "?"]
```

真正进入模型的是这些 token 对应的 embedding。视觉 token 和文本 token 不是同一种来源，但进入 LLM 后都参与 attention。

## 2.2 主动重建检查

闭卷画出单图 VLM 数据流，并标出三个 shape：

1. image encoder 输出：`N x D_v`
2. projector 输出：`N x D_llm`
3. 与文本拼接后的总序列长度：`N + T`

检查点：如果 image encoder 输出 `576 x 1024`，LLM embedding 维度是 `4096`，普通 projector 更可能输出 `576 x 4096`，而不是自动减少为更少 token。

# 3 projector 与 token 压缩

## 3.1 教学骨架

VLM 里有两个不同问题：

1. **维度不匹配**：视觉特征维度和 LLM embedding 维度不同。
2. **序列太长**：图片或视频产生太多 visual tokens，超过上下文预算或推理成本预算。

projector 主要解决第一个问题。token 压缩主要解决第二个问题。

| 问题 | 例子 | 常见处理 |
|---|---|---|
| 维度不匹配 | `1024 -> 4096` | linear / MLP projector |
| token 太多 | `576 tokens` 或多帧乘上帧数 | 降分辨率、patch merge、pooling、resampler、ROI 选择、关键帧选择 |

两者可以组合，但不能混为一个机制。一个普通 projector 可以只改变每个 token 的维度，不改变 token 数量。

## 3.2 边界检查

如果任务需要精确读小字、仪表或细粒度表情，高压缩会丢证据。如果任务只需要粗粒度场景判断，高分辨率和大量 token 可能只是增加成本。

判断规则：先问任务需要什么证据，再决定保留空间细节、时间覆盖还是全局语义。

# 4 视觉证据与问题语义如何关联

## 4.1 教学骨架

视觉 token 和文本 token 进入 LLM 后，模型通过 attention 让不同位置读取相关上下文。

训练阶段，模型学习如何用参数从 token 表示生成有用的 `Q/K/V`。推理阶段参数固定，当前图片和问题会生成本次的 `Q/K/V` 与 attention weights。

对问题“驾驶员有没有闭眼？”，合理的证据关联应该是：

| 类型 | 应关注 | 不应成为主要证据 |
|---|---|---|
| 视觉 token | 驾驶员脸部、眼部、眼睑状态相关区域 | 座椅、车窗、衣服等背景 |
| 文本 token | “驾驶员”“闭眼”“有没有” | 与任务无关的模板词 |
| 输出 token | 回答 yes/no 或描述证据时读取相关视觉和文本 token | 只依赖先验猜测 |

attention 不是可直接等同于人工解释的全部证据，但它提供了“哪些输入 token 参与当前生成”的机制基础。

## 4.2 主动重建检查

用一句话解释：

> 为什么 VLM 不是先做完一个独立视觉分类，再把分类结果交给 LLM？

合格答案应提到：视觉 token 可以作为上下文参与语言生成，文本问题会影响模型读取哪些视觉证据。

# 5 视频与多帧输入约束

## 5.1 教学骨架

视频可以看成多帧图片，但不能把所有帧的所有 patch 都塞进上下文。视频任务必须同时控制：

1. **空间证据**：每帧哪些区域需要保留。
2. **时间证据**：哪些时间点或连续片段需要保留。
3. **token 预算**：总 visual tokens 是否超出上下文和成本限制。

对“驾驶员是否持续闭眼超过 2 秒”，关键不是最高画质，而是足够可靠的时间覆盖和眼部状态证据。

可行策略：

| 策略 | 保留什么 | 丢弃什么 | 适用原因 |
|---|---|---|---|
| 均匀采样 | 覆盖整段视频的时间点 | 过密重复帧 | 判断是否存在持续片段 |
| ROI 裁剪 | 人脸、眼部区域 | 车窗、座椅等背景 | 降低空间 token 成本 |
| 低 FPS + 连续片段 | 时间连续性 | 极细空间纹理 | 适合时序阈值任务 |
| 关键帧/候选片段 | 可能闭眼的时间段 | 明显无关片段 | 适合先有轻量检测器或规则筛选时 |

## 5.2 边界检查

如果 10 秒视频只取 8 帧，帧间距约为 `10 / 7 = 1.43s`。三帧连续闭眼可支持“超过 2 秒”的判断，但可能漏掉刚好 2 秒左右且落在采样间隔之间的事件。

因此，在上下文预算固定时，持续时长任务通常优先提高时间采样密度，而不是盲目提高每帧空间分辨率。前提是当前空间分辨率仍足以判断眼部状态。

# 6 图像问答与 benchmark 草案

## 6.1 教学骨架

benchmark 草案不是“收集一些图片然后问模型”。每个 case 至少要写清：

| 字段 | 说明 |
|---|---|
| input | 图片、视频、问题和必要上下文 |
| expected_behavior | 模型应该回答什么类型的结论 |
| evidence_requirement | 结论必须由哪些可复核证据支持 |
| abstain_condition | 什么时候应该说证据不足 |
| failure_label | 错误时如何分类 |
| source_boundary | 数据来自公开、合成还是明确授权来源 |

对单帧闭眼检测，评分可以主要检查当前帧眼部状态是否判断正确。对“10 秒内持续闭眼超过 2 秒”，评分不能只看 yes/no，还要检查连续时长、帧段或时间范围是否可复核。

## 6.2 最小 case 类型

“持续闭眼超过 2 秒”至少需要四类最小 case：

| case 类型 | 目的 | 例子 |
|---|---|---|
| 正常通过 | 检查模型能识别明确持续闭眼 | 眼部连续闭合约 2.5 秒，画面清晰 |
| 未超过阈值 | 防止把瞬时闭眼判成疲劳 | 闭眼 0.5 秒或眨眼 |
| 证据不足 | 检查模型是否会拒答或降置信 | 眼部被遮挡、视频帧率太低、关键片段缺失 |
| 容易误判 | 暴露边界和失败类型 | 低光、墨镜、头部偏转、闭眼片段被采样漏掉 |

若模型回答“是，驾驶员闭眼了”，但没有连续时长、帧段或时间范围，这不应算完全通过。若合同允许部分通过，可标记为 `partial: evidence_missing`；若合同要求可复核连续时长，则为 `fail: evidence_missing`。

# 7 最小 VLM baseline 计划

## 7.1 baseline 目标

Phase 1-C 的第一个 baseline 目标不是追求高分，而是证明链路可复现：

```text
固定模型与版本
→ 固定输入样本
→ 固定 prompt 模板
→ 运行 zero-shot
→ 记录逐样本输出
→ 按 case 合同人工或规则化评分
→ 分类失败样本
```

模型选择先看四个条件：

1. 能在本地或可控环境中运行，资源成本可接受。
2. 支持图片问答，输入格式和依赖明确。
3. 许可证和模型来源允许学习实验。
4. 能固定版本、命令、输入和输出记录。

具体模型和命令在运行前再确定；不在本文中提前声明已经选型或已经验证。

## 7.2 zero-shot 与 few-shot 顺序

先运行 zero-shot，观察模型是否基本理解输入和任务。再运行 few-shot，检查示例是否改善格式、证据引用或边界判断。

只有当错误分类显示“模型缺少任务边界或样式示例”时，few-shot 才有意义。只有当错误分类显示主要误差可能通过学习目标域模式改善，且 baseline 与评分规则已经稳定时，才考虑参数高效微调。

## 7.3 可复现与可审计记录合同

运行前至少冻结并记录：

- 模型 ID、精确 revision、权重精度和许可证状态。
- 图片文件、内容 hash、预处理配置和 prompt/chat template。
- `do_sample`、temperature、top-p/top-k、最大输出长度、随机种子和重复次数。
- 每个 case 的 `expected_behavior`、证据要求、abstain 条件、失败标签和分组门禁。
- Python、PyTorch、Transformers、CUDA runtime、驱动、GPU 与显存配置。

运行后至少保存：

- 每次执行状态与耗时。
- 每个样本的原始输出、规范化结果、评分结论和失败标签。
- 每组样本量、每组 accuracy、总体/macro/worst-group 指标。
- 是否满足运行前冻结的总体与关键组门禁。

## 7.4 2026-08-11 本地实践准备状态

用户提供的目标设备为约 6 GB 显存的 NVIDIA GeForce RTX 4050。只读环境检查确认当前工作环境是 WSL2，磁盘空间充足；默认 Python 3.13 环境未安装 PyTorch、Transformers、Accelerate 或 Pillow。既有 `openmmlab` 环境包含 Python 3.8、PyTorch 2.4.1 和 CUDA 12.4 构建，但缺少 Transformers/Accelerate，不作为本次 VLM baseline 的默认环境。

当前代理沙箱无法访问 GPU，因此以上只证明环境清点完成，不能证明目标 WSL 会话中的 CUDA 可用。为避免污染既有训练环境，下一步优先建立独立 Python 3.11 实验环境；环境创建、依赖安装、模型下载和 GPU 推理均尚未执行。

# 8 当前下一步

下一次继续 Phase 1-C 时，不再重复已闭合的数据流和 baseline 设计问答，直接进入实践：

1. 在目标 WSL 会话确认 `nvidia-smi` 与 `torch.cuda.is_available()`。
2. 建立隔离的 Python 3.11 VLM 实验环境并固定依赖版本。
3. 使用画面清晰、答案明确、来源合规的单图完成 smoke test，先验证加载、预处理、prompt、推理与记录链路。
4. 再运行目标小型 VLM checkpoint，保存可复现配置、逐样本原始输出和显存峰值。
5. 链路稳定后才把闭眼、睁眼、眯眼和眩光设计落实为 4 个最小 case；不从微调开始。

在完成最小 baseline 前，不把任何 case 集称为 benchmark。
