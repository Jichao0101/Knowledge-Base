---
type: project_learning_record
status: active
project: AI-Career-Transition
learning_stage: Phase 1-C - VLM baseline and benchmark draft
record_role: durable_stage_learning_record
summary: 保存 Phase 1-C 的主动学习诊断、掌握状态、未验证项、本地实践准备状态和下一步恢复入口；不承载完整教学正文。
sources:
  - 2026-08-10 Phase 1-C VLM 数据流与视频持续闭眼任务主动学习对话
  - 2026-08-11 Phase 1-C baseline 可复现性、任务合同、分组门禁、case 证据边界、模型选择与本地环境主动学习对话
  - 02_Projects/AI-Career-Transition/10_学习文档/P01C-01_VLM基线与Benchmark_学习文档.md
  - 02_Projects/AI-Career-Transition/20_学习记录/当前阶段学习检查点.md
scope: Phase 1-C 的个人诊断题、诊断结论、证据状态、实践准备和恢复任务。
risks:
  - 对话诊断达到 working 不等于真实模型运行、benchmark 建立或阶段门禁完成。
  - 本记录中的环境信息是 2026-08-11 快照；执行前必须重新验证。
  - 四类图像 case 仍是设计，未落盘为公开、合成或明确授权数据集。
single_pass_recoverable: false
updated_at: 2026-08-11
---

# 1 Phase 1-C VLM 基线与 Benchmark 学习记录

## 1.1 文档职责

本文保存会随学习推进而变化的个人状态：诊断题、回答结论、薄弱点、实践准备和下一步。稳定教学内容见 [[02_Projects/AI-Career-Transition/10_学习文档/P01C-01_VLM基线与Benchmark_学习文档]]；当前恢复指针和阶段门禁见 [[02_Projects/AI-Career-Transition/20_学习记录/当前阶段学习检查点]]。

## 1.2 当前覆盖状态

| 覆盖区 | 当前状态 | 证据边界 |
|---|---|---|
| 单图 VLM 数据流 | working | 对话诊断，不是模型运行证据 |
| projector 与 token 压缩 | working | 对话诊断 |
| 视觉证据与问题语义 | working | 对话诊断 |
| 视频与多帧输入 | partial | 定量采样边界待真实输入预算验证 |
| 最小 VLM baseline | partial | 设计已形成，运行未执行 |
| benchmark 草案 | partial | case 边界已形成，图片未落盘 |
| 分组评测与微调边界 | working | 评测设计已理解，结果未执行 |

## 1.3 2026-08-10 主动学习诊断

已闭合内容：

1. 能说明图片经 image encoder / ViT 形成 visual tokens，再经 projector 对齐到 LLM embedding 维度，并与 text token embeddings 组成连续输入序列。
2. 能区分普通 projector 的维度对齐作用和 token 数量压缩；能用 `576 x 1024 -> 576 x 4096` 解释 token 数不变、特征维度变化。
3. 能说明 VLM 通过 attention 在文本问题 token 与相关视觉 patch 之间建立关联；训练阶段学习 `Wq/Wk/Wv`，推理阶段用固定参数生成当前输入的 `Q/K/V` 和 attention weights。
4. 能把“单帧闭眼检测”和“10 秒内持续闭眼超过 2 秒”区分为空间判别与时序证据任务，并指出后者需要连续时长、帧段或时间范围作为可复核证据。

仍需继续检查：

1. 视频采样密度、帧间隔和漏检风险之间的定量关系还需要结合具体输入预算继续练习。
2. “持续闭眼超过 2 秒”的 4 至 8 个最小 benchmark case 尚未完整落盘。
3. 开源小型 VLM baseline 未运行，因此不能声明模型输入输出、失败类型、zero-shot/few-shot 或分组评测已验证。

## 1.4 2026-08-11 主动学习诊断

已达到对话诊断意义上的 `working`：

1. 能列出 baseline 的关键固定项：输入图片、模型、推理配置、运行次数、输出格式和随机种子。
2. 能区分 `execution_success`、单次 case 通过/失败、聚合指标和 baseline 门禁；错误答案不能因高温度或小模型能力有限而改记为任务成功。
3. 能说明评测合同和通过阈值必须在运行前冻结；查看测试错误并修改 prompt 后，原测试集已成为开发集，最终 few-shot 证据必须来自未参与调参的独立留出集。
4. 能说明总体 accuracy 或 macro accuracy 都不能替代关键组门禁；需要同时报告每组样本量、每组 accuracy、总体指标、macro 指标、worst-group 指标和安全关键组最低阈值。
5. 能说明仅保存最终 accuracy 不足以成为可靠证据，必须保存逐样本输入、原始输出和评分结果，才能复核分组指标、失败标签与 abstain 判断。
6. 已为单帧闭眼任务提出闭眼、睁眼、眯眼和眩光四类最小 case，并把判断边界修正为“任务所需眼部状态证据是否可辨认”，不把瞳孔可见性当作唯一必要条件。
7. 能解释第一个 baseline 应优先选择本地可运行、版本和推理配置清晰的模型；小模型 smoke test 只验证链路，不能代表另一 checkpoint 的能力结果。

仍未验证：

1. 尚未冻结真实模型 revision、依赖版本、图片预处理、prompt 模板和完整解码配置。
2. 尚未运行 smoke test 或 2B 级 VLM baseline，未保存逐样本输出、显存峰值和失败记录。
3. 四类 case 仍是对话设计，尚未使用公开、合成或明确授权图片落盘。
4. 视频采样密度、帧间隔与持续事件漏检风险仍需在真实输入预算下验证。

## 1.5 诊断题记录

### 单图数据流重建

闭卷画出单图 VLM 数据流，并标出：image encoder 输出 `N x D_v`、projector 输出 `N x D_llm`、拼接后的总序列长度 `N + T`。检查点是普通 projector 通常改变特征维度，不自动减少 token 数量。

### 视觉与语言关系重建

问题：为什么 VLM 不是先做完一个独立视觉分类，再把分类结果交给 LLM？

合格答案应说明：视觉 token 可以作为上下文参与语言生成，文本问题会影响模型读取哪些视觉证据。

## 1.6 2026-08-11 本地实践准备状态

用户提供的目标设备为约 6 GB 显存的 NVIDIA GeForce RTX 4050。只读环境检查确认当时工作环境是 WSL2，磁盘空间充足；默认 Python 3.13 环境未安装 PyTorch、Transformers、Accelerate 或 Pillow。既有 `openmmlab` 环境包含 Python 3.8、PyTorch 2.4.1 和 CUDA 12.4 构建，但缺少 Transformers/Accelerate，不作为本次 VLM baseline 的默认环境。

当时代理沙箱无法访问 GPU，因此以上只证明环境清点完成，不能证明目标 WSL 会话中的 CUDA 可用。隔离环境创建、依赖安装、模型下载和 GPU 推理均为 `not_verified`。

## 1.7 下一步恢复任务

1. 在目标 WSL 会话确认 `nvidia-smi` 与 `torch.cuda.is_available()`。
2. 建立隔离的 Python 3.11 VLM 实验环境并固定依赖版本。
3. 使用画面清晰、答案明确、来源合规的单图完成 smoke test，先验证加载、预处理、prompt、推理与记录链路。
4. 再运行目标小型 VLM checkpoint，保存可复现配置、逐样本原始输出和显存峰值。
5. 链路稳定后才把闭眼、睁眼、眯眼和眩光设计落实为 4 个最小 case；不从微调开始。

在完成最小 baseline 前，不把任何 case 集称为 benchmark。
