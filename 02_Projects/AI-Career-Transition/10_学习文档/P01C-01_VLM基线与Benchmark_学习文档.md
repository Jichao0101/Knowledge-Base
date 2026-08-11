---
type: project_learning_document
status: active
project: AI-Career-Transition
learning_stage: Phase 1-C - VLM baseline and benchmark draft
summary: 系统说明 Phase 1-C 的 VLM 数据流、视觉 token、视频输入约束、图像问答 baseline、benchmark case 合同与可复现评测方法。
sources:
  - 2026-08-10 用户修正主动学习方法：知识大面积缺失时先教学骨架，再用主动重建和诊断题检查吸收
  - 2026-08-10 Phase 1-C VLM 数据流与视频持续闭眼任务主动学习对话
  - 2026-08-11 Phase 1-C baseline 可复现性、任务合同、分组门禁、case 证据边界、模型选择与本地环境主动学习对话
  - 02_Projects/AI-Career-Transition/20_学习记录/当前阶段学习检查点.md
  - 02_Projects/AI-Career-Transition/00_规划/AI职业转型整体学习方案.md
  - 02_Projects/AI-Career-Transition/10_学习文档/P01B-01_AI评测基本功_学习文档.md
scope: VLM 输入输出数据流、视觉 token、projector、token 压缩、视频采样、图像问答 baseline、任务集来源边界、zero-shot/few-shot 和分组评测。
risks:
  - 本文是 Phase 1-C 学习材料，不代表已经运行开源 VLM、建立 benchmark 或完成阶段门禁。
  - 模型选择、依赖版本和具体命令会变化；运行 baseline 前必须重新固定模型、环境、输入样本和可复现命令。
  - 小型任务集只能使用公开、合成或明确授权数据；外部数据需要先建立来源记录。
updated_at: 2026-08-11
---

# 1 Phase 1-C VLM 基线与 Benchmark 学习文档

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

本文只承载可复用的阶段教学内容。个人诊断题、回答结果、实践准备和下一步保存在 [[02_Projects/AI-Career-Transition/20_学习记录/P01C_VLM基线与Benchmark_学习记录]]；阶段完成仍以 [[02_Projects/AI-Career-Transition/20_学习记录/当前阶段学习检查点]] 的完成门禁为准。

## 1.2 覆盖区

| 覆盖区 | 必须理解或能够设计的内容 |
|---|---|
| 单图 VLM 数据流 | 图片如何变成 LLM 可读取的输入序列 |
| projector 与 token 压缩 | 维度对齐和 token 数量压缩为什么不是一回事 |
| 视觉证据与问题语义 | LLM 如何通过 attention 关联图片区域和文本问题 |
| 视频与多帧输入 | 空间分辨率、时间采样和上下文预算如何取舍 |
| 最小 VLM baseline | 如何运行一个可复现的图像问答最小基线 |
| benchmark 草案 | case 来源、期望行为、证据边界和失败标签如何定义 |
| 分组评测与微调边界 | 如何解释错误，什么时候不该微调 |

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
