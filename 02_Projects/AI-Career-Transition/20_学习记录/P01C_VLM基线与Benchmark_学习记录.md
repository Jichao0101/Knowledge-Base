---
type: project_learning_record
status: closed_by_scope
project: AI-Career-Transition
learning_stage: Phase 1-C - VLM baseline and benchmark draft
record_role: durable_stage_learning_record
summary: 保存 Phase 1-C 的主动学习诊断、VLM zero-shot 与文本 few-shot prompting、prompt/输入合同敏感性、模型替换与资源约束、模型任务边界和范围关闭结论；不承载完整教学正文。
sources:
  - 2026-08-10 Phase 1-C VLM 数据流与视频持续闭眼任务主动学习对话
  - 2026-08-11 Phase 1-C baseline 可复现性、任务合同、分组门禁、case 证据边界、模型选择与本地环境主动学习对话
  - 2026-08-11 Phase 1-C baseline 合同续测与 Colab 实践路线确认
  - 2026-08-14 Qwen2.5-VL-3B 单图 smoke test 用户运行报告
  - 2026-08-15 Qwen2.5-VL-3B 5-case zero-shot、输入身份审计与固定 ROI 诊断用户运行报告
  - 2026-08-17 Qwen2.5-VL-3B 文本示例、定义顺序与单眼 ROI 诊断用户运行报告
  - 2026-08-17 prompt 敏感性、因果证据边界、停止规则与模型任务分层主动学习诊断
  - 2026-08-17 Qwen3.5-4B 输出协议、INT4、受限 max_pixels 与 T4 可部署配置用户运行报告
  - 2026-08-20 用户确认 Qwen3.5 替换前已完成 Qwen2.5 文本 few-shot prompting，并确认 Phase 1-C 范围关闭
  - 02_Projects/AI-Career-Transition/10_学习文档/P01C-01_VLM基线与Benchmark_学习文档.md
  - 02_Projects/AI-Career-Transition/20_学习记录/当前阶段学习检查点.md
  - 02_Projects/AI-Career-Transition/30_实践记录/P01C_VLM单图SmokeTest_2026-08-14_实践记录.md
  - 02_Projects/AI-Career-Transition/30_实践记录/P01C_VLMZeroShot初始基线_2026-08-15_实践记录.md
  - 02_Projects/AI-Career-Transition/30_实践记录/P01C_VLMPrompt与单眼ROI诊断_2026-08-17_实践记录.md
  - 02_Projects/AI-Career-Transition/30_实践记录/P01C_Qwen3.5代际替换与资源约束诊断_2026-08-17_实践记录.md
scope: Phase 1-C 的个人诊断题、诊断结论、证据状态、实践准备和恢复任务。
risks:
  - 对话诊断达到 working 不等于真实模型运行、benchmark 建立或阶段门禁完成。
  - 本记录中的 WSL 和 Colab 环境信息均为阶段快照；执行前必须重新验证并保存实际运行证据。
  - 当前 5 个图像 case 为内部授权开发/诊断集；每组仅 1 个样本，不能视为稳定 benchmark 或最终留出集。
  - 单图 smoke test 与 zero-shot 基线均为用户报告的运行证据，代理未独立复跑；模型 hash 和精确 checkpoint 身份尚未冻结。
  - 文本示例属于 few-shot prompting，但不包含图像-文本多模态 demonstration；实验使用已参与错误分析的开发集，不能作为泛化或严格多模态 few-shot 证据。
  - 单眼 ROI 同时改变输入、任务粒度、prompt 和输出 schema；其结果不能隔离为 ROI 的单一因果效应。
  - Qwen3.5 最终可运行配置同时采用 INT4 与受限 max_pixels，且缺少最终逐 case 数值，不能作为纯模型代际能力结论。
single_pass_recoverable: false
updated_at: 2026-08-20
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
| 最小 VLM baseline | closed_by_scope | 单图 smoke test、5-case zero-shot、文本 few-shot prompting、单眼 ROI 和 Qwen3.5 资源约束替换均有 user_reported 证据；链路可运行，但未形成稳定细粒度眼态能力 |
| benchmark 草案 | partial | 5 个内部授权 case 已形成开发/诊断集，但每组仅 1 个且已参与错误分析，不能作为最终留出集 |
| 分组评测与微调边界 | working | 已运行文本 few-shot prompting，并能识别开发集污染、prompt 顺序敏感性、ROI 混杂变量和停止规则；严格多模态 demonstration、独立留出集和正式 benchmark 门禁尚未完成 |

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

## 1.7 2026-08-14 单图 smoke test

用户在 Google Colab 使用本地 Google Drive 模型目录中的 Qwen2.5-VL-3B-Instruct 完成两次单图推理：首次开放描述验证多模态生成链路；随后使用双眼状态 JSON prompt 和用户提供的左右眼 `closed` 标注完成任务特定 smoke test。

任务特定运行结果：

- `execution_success = true`。
- 归一化后左右眼均为 `closed`，与用户提供标注一致。
- 耗时 `13.581s`。
- 峰值显存 allocated `8.631 GiB`，reserved `9.137 GiB`。
- 原始输出带 Markdown 代码围栏，因此 `raw_format_success = false`；去除围栏后 `semantic_pass_after_normalization = true`。
- 用户代码已设置 `do_sample=false`、`num_beams=1`、`max_new_tokens=64` 和 seed `47`。
- 当前评分函数依赖全局 `expected`；扩展多 case 前需要改为显式参数。

完整配置、原始输出和证据边界见 [[02_Projects/AI-Career-Transition/30_实践记录/P01C_VLM单图SmokeTest_2026-08-14_实践记录]]。本次结果不等于 zero-shot baseline 已运行，也不支持聚合 accuracy。

## 1.8 2026-08-15 zero-shot 初始基线

用户修复了 smoke-test prompt 中的答案示例泄露，并把 `expected` 改为 `infer_qwen_vl` 的显式参数。输出合同现允许一个可选的 `json` Markdown 代码围栏：先归一化再解析，但仍要求 JSON 只有 `left_eye` 和 `right_eye` 两个枚举字段。

用户报告的 Colab 环境为 Python `3.12.13`、PyTorch `2.11.0+cu128`、PyTorch CUDA runtime `12.8`、Transformers `5.15.0`、Accelerate `1.14.0`、`qwen-vl-utils 0.0.14`、Pillow `11.3.0`、Tesla T4、driver `580.82.07`。`nvidia-smi` 显示 CUDA `13.0`，这里只解释为驱动支持上限。

5 个内部授权 case 在统一 zero-shot 配置下全部执行并成功解析，但模型对 10 只眼睛均预测为 `closed`：

- execution success：`5/5 = 100%`。
- normalized JSON parse success：`5/5 = 100%`。
- case exact match：`1/5 = 20%`。
- per-eye accuracy：`2/10 = 20%`。
- 平均推理时间：`6.841s`。
- 5 个原图 MD5 和处理后 tensor MD5 均不同，排除了循环中重复输入同一图片/tensor。
- case 3 使用固定人脸 ROI 后仍把 `open/open` 误判为 `closed/closed`；耗时从全图的 `6.094s` 降至 `1.723s`，但语义错误未修复。

当前错误分类为 `closed` 类预测坍缩。证据支持“Qwen2.5-VL-3B-Instruct 在当前任务合同和域上不能可靠完成细粒度眼态 zero-shot 分类”，但不支持把唯一根因写成参数量不足。完整逐 case 证据见 [[02_Projects/AI-Career-Transition/30_实践记录/P01C_VLMZeroShot初始基线_2026-08-15_实践记录]]。

## 1.9 2026-08-17 prompt 与单眼 ROI 诊断

用户在既有 5-case 开发集上继续完成三类用户运行诊断：

1. 增加 `open/abstain/narrow` 文字示例后，case exact match 从 `20%` 变为 `40%`，per-eye accuracy 从 `20%` 变为 `50%`，预测分布从 `closed 10/10` 转为 `open 4/10 + narrow 6/10`。
2. 只调整四个标签定义顺序时，两版 case exact match 分别为 `20%` 和 `40%`，per-eye accuracy 分别为 `30%` 和 `50%`；clear-open case 的输出随顺序从 `closed/closed` 变为 `open/open`。
3. 使用经生产标注验收并由用户人工校验的单眼 ROI、单眼 prompt 和单字段 schema 后，per-eye accuracy 为 `4/10 = 40%`，预测分布转为 `abstain 8/10 + open 2/10`。

上述结果均来自用户报告，代理未独立复跑。完整配置、逐 case 结果和证据边界见 [[02_Projects/AI-Career-Transition/30_实践记录/P01C_VLMPrompt与单眼ROI诊断_2026-08-17_实践记录]]。

主动学习诊断闭合了以下内容：

- 能说明 prompt 定义、示例和顺序会改变类别分布；小开发集准确率提高不能证明泛化能力提升。
- 能区分“结果支持某假设”和“结果证明唯一根因”；ROI 失败不能直接推出模型普遍没有分类能力。
- 能识别单眼 ROI 实验同时改变视觉输入、任务粒度、prompt 和 schema，不能隔离裁剪的单一因果作用。
- 能判断继续枚举 prompt/ROI 已偏离学习路线，并将失败 baseline 转化为模型任务边界。
- 能迁移到分层系统：专用模型承担低层细粒度感知，VLM 提供全局语义和长尾辅助，时序状态层形成稳定状态，策略门禁决定报警或动作。

当前最强阶段结论是：Qwen2.5-VL-3B-Instruct 的多模态执行与结构化输出链路可运行，但当前细粒度眼态结果对 prompt 和输入合同敏感，不适合作为安全相关眼态事实的唯一来源。该结论不等于模型参数规模是唯一根因，也不外推到其他 VLM、任务或数据域。

## 1.10 2026-08-17 Qwen3.5 代际替换与资源约束诊断

用户随后尝试用参数规模接近的 Qwen3.5-4B 在相同 5-case 全图任务上替换 Qwen2.5-VL-3B。首次运行的五个输出均生成自然语言图像分析，并在最终 JSON 前结束，解析全部失败；这属于输出协议/预算失败，语义分类应记为 `not_evaluated`，不能计为分类准确率 0。

为适应 Tesla T4，后续可运行配置同时采用 INT4 量化版本并限制 `max_pixels`。用户报告结果没有优化，但未提供最终逐 case 输出、准确率、量化方案或像素上限。因此当前只支持以下结论：

- 当前 T4 可部署的 Qwen3.5-4B 配置没有观察到明确收益。
- 模型代际、权重精度和像素预算同时变化，不能把结果解释为纯模型能力比较。
- 对全图小目标眼态任务，降低像素预算可能进一步压缩关键证据，但本轮不能确定其单一因果贡献。
- 模型替换需要重新验证 chat template、思考/直接回答模式和输出预算；不能只替换权重路径。

完整证据边界见 [[02_Projects/AI-Career-Transition/30_实践记录/P01C_Qwen3.5代际替换与资源约束诊断_2026-08-17_实践记录]]。

本轮进一步闭合了“模型能力比较”和“硬件可部署配置比较”的区别。当前停止继续搜索 Qwen3.5 量化、像素预算或 prompt 组合，下一步转向分层多模态系统设计。

## 1.11 阶段关闭前的恢复任务（历史）

1. 冻结当前 5 个 case 为开发/诊断集；不再用它们声明最终泛化性能。
2. 停止继续枚举 prompt 顺序、ROI、量化、像素预算或模型版本来提高这 5 个开发 case 的分数。
3. 文本类别示例后来由用户确认归类为文本 few-shot prompting；它仍不是包含图像示例的严格多模态 demonstration，独立留出集也未执行。
4. 若未来进入可移交 benchmark，再补未查看留出集、模型文件 hash、精确 checkpoint 身份、许可证快照、冻结 ROI/input contract 和更充足的分组样本。
5. 后续学习转向“专用感知事实 + VLM 语义增强 + 时序状态 + 策略门禁”的分层多模态系统设计；SFT 和量化部署只在新的任务合同与资源目标需要时作为条件分支打开。

当前 5 个开发 case 不称为 benchmark；只有未来重新冻结独立数据、模型身份、输入合同和正式门禁后，才评估是否建立可移交 benchmark。

## 1.12 2026-08-20 Phase 1-C 范围关闭决定

用户确认：替换 Qwen3.5 前，Qwen2.5 已使用带类别示例的 prompt 完成 few-shot prompting。Phase 1-C 原门禁要求最简单的 zero-shot 与 few-shot 基线，并未要求 demonstration 必须包含图像，因此该实验计入文本 few-shot prompting baseline。

阶段以 `closed_by_scope` 关闭：

1. VLM 数据流、输入/输出合同、可复现 baseline、失败分类、分组评测边界和模型任务分层已达到当前路线需要的认知深度。
2. 单图 smoke test、zero-shot、文本 few-shot prompting、prompt/ROI 和资源受限模型替换均已有用户运行证据。
3. 微调是错误分类支持时才打开的条件分支；未来 OMS SFT/PEFT 在新任务合同下重新决策。
4. 当前 5 个 case 仍是开发/诊断集；严格多模态 demonstration、独立留出集、模型 hash 和代理独立复跑保持未验证。

下一阶段转入 [[02_Projects/AI-Career-Transition/10_学习文档/P02A-01_VLM模型工程认知_学习文档]]。本关闭决定不把失败 baseline 改写为模型能力通过，也不把范围豁免改写为实践完成。
