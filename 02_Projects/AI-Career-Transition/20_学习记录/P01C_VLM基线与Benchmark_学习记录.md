---
type: project_learning_record
status: active
project: AI-Career-Transition
learning_stage: Phase 1-C - VLM baseline and benchmark draft
record_role: durable_stage_learning_record
summary: 保存 Phase 1-C 的主动学习诊断、掌握状态、未验证项、实践环境准备状态和下一步恢复入口；不承载完整教学正文。
sources:
  - 2026-08-10 Phase 1-C VLM 数据流与视频持续闭眼任务主动学习对话
  - 2026-08-11 Phase 1-C baseline 可复现性、任务合同、分组门禁、case 证据边界、模型选择与本地环境主动学习对话
  - 2026-08-11 Phase 1-C baseline 合同续测与 Colab 实践路线确认
  - 02_Projects/AI-Career-Transition/10_学习文档/P01C-01_VLM基线与Benchmark_学习文档.md
  - 02_Projects/AI-Career-Transition/20_学习记录/当前阶段学习检查点.md
scope: Phase 1-C 的个人诊断题、诊断结论、证据状态、实践准备和恢复任务。
risks:
  - 对话诊断达到 working 不等于真实模型运行、benchmark 建立或阶段门禁完成。
  - 本记录中的 WSL 和 Colab 环境信息均为阶段快照；执行前必须重新验证并保存实际运行证据。
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
| 最小 VLM baseline | partial | 理论合同达到 working，真实运行仍为 not_verified |
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
8. 能说明本地路径或 Google Drive 挂载路径不等于版本身份；图片需要内容 hash，模型需要精确 revision 或文件 hash。
9. 能识别 Qwen VLM 示例中的预处理被 `process_vision_info` 和 processor 封装；“未手工 resize”不能记录成“无预处理”，必须冻结处理器版本和像素预算。
10. 能把双眼状态约束为可解析 JSON 枚举，区分 `invalid_output_format`、`invalid_label`、`incorrect_classification`、`unnecessary_abstention` 和 `failure_to_abstain`，并明确以最终输入画面左右定义左右眼。
11. 能区分执行成功率、成功样本条件 accuracy 和端到端 accuracy；能说明静默过滤 OOM 样本会产生选择偏差。
12. 能说明 ROI 裁剪会改变输入合同；若采用头部 ROI，应在运行前对全体样本统一冻结，并与全图 baseline 分开报告。
13. 能说明 `nvidia-smi` 中的 CUDA 信息是驱动支持上限，而 `torch.version.cuda` 才表示 PyTorch 构建使用的 CUDA runtime。
14. 能说明结构化首版 baseline 应优先使用 `do_sample: false` 的确定性解码，并冻结 `num_beams` 与 `max_new_tokens`。

仍未验证：

1. 用户已提出使用本地或 Google Drive 中的 Qwen2.5-VL-3B 级模型，但精确 checkpoint 身份、文件 hash、许可证快照和加载结果仍未验证。
2. 用户已指定一个带 MD5 的“眩光但眼部可辨认、双眼睁开”候选图片；实际 Colab 路径、标注文件内容和模型输入均未由代理读取或验证。
3. 当前目标环境已改为用户报告的 Google Colab T4 16 GB；Python、PyTorch、Transformers、`qwen-vl-utils`、CUDA runtime、驱动和实际 GPU 快照尚未保存。
4. 尚未运行 smoke test 或 VLM baseline，未保存逐样本原始输出、耗时、显存峰值和失败记录。
5. 四类 case 尚未形成冻结的小型评测集；zero-shot、错误分类和 few-shot 对比均未执行。
6. 视频采样密度、帧间隔与持续事件漏检风险仍需在真实输入预算下验证。

## 1.5 诊断题记录

### 1.5.1 单图数据流重建

闭卷画出单图 VLM 数据流，并标出：image encoder 输出 `N x D_v`、projector 输出 `N x D_llm`、拼接后的总序列长度 `N + T`。检查点是普通 projector 通常改变特征维度，不自动减少 token 数量。

### 1.5.2 视觉与语言关系重建

问题：为什么 VLM 不是先做完一个独立视觉分类，再把分类结果交给 LLM？

合格答案应说明：视觉 token 可以作为上下文参与语言生成，文本问题会影响模型读取哪些视觉证据。

## 1.6 2026-08-11 实践环境准备状态

用户提供的目标设备为约 6 GB 显存的 NVIDIA GeForce RTX 4050。只读环境检查确认当时工作环境是 WSL2，磁盘空间充足；默认 Python 3.13 环境未安装 PyTorch、Transformers、Accelerate 或 Pillow。既有 `openmmlab` 环境包含 Python 3.8、PyTorch 2.4.1 和 CUDA 12.4 构建，但缺少 Transformers/Accelerate，不作为本次 VLM baseline 的默认环境。

当时代理沙箱无法访问 GPU，因此以上只证明环境清点完成，不能证明目标 WSL 会话中的 CUDA 可用。隔离环境创建、依赖安装、模型下载和 GPU 推理均为 `not_verified`。

随后用户把目标运行环境改为 Google Colab，并报告计划使用 T4 16 GB GPU、Google Drive 挂载模型和数据。该信息是用户提供的目标配置，不是代理独立读取的运行证据；实际 GPU、驱动、PyTorch CUDA runtime、依赖版本、模型文件 hash、图片路径和标注仍需在实验开始时保存。

## 1.7 下一步恢复任务

1. 在 Colab 运行开始时保存 `nvidia-smi`、`torch.cuda.is_available()`、`torch.version.cuda`、Python 与关键包版本。
2. 固定实际模型目录、模型文件 hash、processor 配置、候选图片路径与 MD5、确切标注路径、JSON 输出协议和确定性解码参数。
3. 使用一张证据清晰、标注明确的图片完成 smoke test，验证加载、预处理、prompt、推理、JSON 解析与记录链路，并保存原始输出、耗时和显存峰值。
4. 链路稳定后冻结小型 case 集、评分规则和门禁，再运行 zero-shot baseline。
5. 先做 zero-shot 错误分类；只有错误表明示例可能改善格式、任务边界或证据使用时，再进行 few-shot 理论检查和独立对比。
6. few-shot 示例不得从已查看的最终留出集失败样本中挑选；不从微调开始。

在完成最小 baseline 前，不把任何 case 集称为 benchmark。
