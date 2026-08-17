---
type: project_overview
status: active
project: AI-Career-Transition
summary: 以知识库已有 DMS 感知、模型训练、端侧部署和 Agent 工程项目为实践背景，向多模态 AI、VLM、Agent Systems 和 ML Systems 迁移的长期学习与作品建设项目。
sources:
  - 2026-07-17 用户确认的学习目标、项目背景与隐私边界
  - 2026-07-21 第一阶段 LLM 主动学习对话与迁移检查
  - 2026-07-21 第二阶段 LLM 训练机制主动学习评测
  - 2026-07-24 第二阶段续测、系统学习文档与滚动检查点结构决策
  - 2026-07-25 Adam/AdamW 闭卷检查与最小训练实践进度
  - 2026-08-01 TinyCausalLM 单步训练运行与训练恢复主动学习续测
  - 2026-08-04 TinyCausalLM 单 batch 过拟合、确定性评估、checkpoint 轨迹恢复与阶段收尾
  - 2026-08-06 Phase 1-A closure 续测、范围豁免决定与 Phase 1-B 切换确认
  - 2026-08-09 Phase 1-B 主动学习、传统评测实践范围豁免与 Phase 1-C 切换确认
  - 2026-08-10 AI Career 主动学习方法修正、学习文档索引创建与 Phase 1-C 教学骨架建立
  - 2026-08-11 Phase 1-C baseline 可复现性、case 证据边界、分组门禁和本地实践准备主动学习
  - 2026-08-11 Phase 1-C baseline 合同续测、Colab 环境切换与实践顺序确认
  - 2026-08-14 Qwen2.5-VL-3B 单图 smoke test 用户运行报告
  - 2026-08-15 Qwen2.5-VL-3B 5-case zero-shot、输入身份审计与固定 ROI 诊断用户运行报告
  - 2026-08-17 Qwen2.5-VL-3B prompt 定义、顺序敏感性、单眼 ROI 与模型任务分层主动学习诊断
  - 2026-08-17 Qwen3.5-4B 输出协议、INT4、受限 max_pixels 与 T4 可部署配置诊断
  - 02_Projects/DMS/03_Model_Training/model_training_overview_current.md
  - 02_Projects/DMS/08_EyeStatus/eyestatus_overview_current.md
  - 02_Projects/agent-trajectory/agent_trajectory_overview_current.md
  - 02_Projects/AI-Career-Transition/00_规划/AI职业转型整体学习方案.md
  - 02_Projects/AI-Career-Transition/30_实践记录/P01C_VLM单图SmokeTest_2026-08-14_实践记录.md
  - 02_Projects/AI-Career-Transition/30_实践记录/P01C_VLMZeroShot初始基线_2026-08-15_实践记录.md
  - 02_Projects/AI-Career-Transition/30_实践记录/P01C_VLMPrompt与单眼ROI诊断_2026-08-17_实践记录.md
  - 02_Projects/AI-Career-Transition/30_实践记录/P01C_Qwen3.5代际替换与资源约束诊断_2026-08-17_实践记录.md
scope: 职业方向、能力补齐、学习路线、作品建设、阶段验证与求职准备。
risks:
  - 学习范围横跨模型、系统和 Agent，若缺少阶段性交付，容易再次退化为零散学习或 vibe coding。
  - 本项目记录的是规划和阶段证据，不代表目标能力已经掌握或项目已经完成生产验证。
updated_at: 2026-08-17
---

# 1 AI 职业转型项目总览

## 1.1 项目目标

本项目用于管理从知识库已有的 DMS/OMS 感知、模型训练、数据处理、量化与端侧部署、后处理，以及 Agent workflow 和 trajectory 工程项目，向多模态 AI、VLM 应用、Agent Systems 和 ML Systems 迁移的长期路线。

这些项目是学习路线的真实工程背景和可复用资产，但不在本项目中映射为个人学历、雇主、任职时长或具体任职履历。DMS/OMS 用于提供图像、状态、端侧约束、业务动作和验证场景，不作为长期职业边界。

## 1.2 目标岗位

按优先级维护以下目标：

1. 多模态 AI / VLM 应用工程师。
2. AI Agent Systems / LLM 应用系统工程师。
3. ML Systems / 模型推理与部署工程师。
4. 智能座舱端云协同 AI 工程师。

暂不将以下方向作为主攻目标：

- LLM 基础模型预训练研究。
- 只围绕 DMS/OMS 单任务模型继续纵向收窄。
- 只依赖 Prompt、API 调用或框架拼装的通用应用开发。

## 1.3 核心路线

核心能力组合为：

```text
DMS/OMS 视觉感知与端侧部署项目基础
    + Transformer / VLM / 多模态理解
    + Agent runtime / evaluation / observability
    + ML Systems / 端云路由 / 可靠性
    = 可落地的多模态 AI 系统能力
```

技术判断采用分层模型：

- 常驻低层感知继续允许使用小型 CNN、ViT 或混合模型。
- 时序状态估计逐步引入轻量 Transformer 或多模态状态模型。
- 语义理解、解释、交互和长尾推理使用本地或云端 VLM/LLM。
- 业务动作通过带权限、状态和验证门禁的 Agent 工具调用完成。
- 端云分工必须由延迟、成本、隐私、网络可用性和任务风险共同决定，不能仅以“座舱延迟要求较低”为依据。

## 1.4 项目入口

- 主学习方案：[[02_Projects/AI-Career-Transition/00_规划/AI职业转型整体学习方案]]
- 学习文档维护规范：[[02_Projects/AI-Career-Transition/00_规划/学习文档维护规范]]
- 学习文档索引：[[02_Projects/AI-Career-Transition/10_学习文档/学习文档索引]]
- 当前阶段固定检查点：[[02_Projects/AI-Career-Transition/20_学习记录/当前阶段学习检查点]]
- Phase 0 系统学习文档：[[02_Projects/AI-Career-Transition/10_学习文档/P01A-01_LLM推理机制_学习文档]]
- Phase 0 能力诊断记录：[[02_Projects/AI-Career-Transition/20_学习记录/P00_能力诊断_学习记录]]
- Phase 1 训练机制系统学习文档：[[02_Projects/AI-Career-Transition/10_学习文档/P01A-02_LLM训练机制_学习文档]]
- Phase 1-A 学习记录：[[02_Projects/AI-Career-Transition/20_学习记录/P01A_LLM机制与训练_学习记录]]
- Phase 1-B 评测基本功系统学习文档：[[02_Projects/AI-Career-Transition/10_学习文档/P01B-01_AI评测基本功_学习文档]]
- Phase 1-B 学习记录：[[02_Projects/AI-Career-Transition/20_学习记录/P01B_AI评测基本功_学习记录]]
- Phase 1-C VLM 系统学习文档：[[02_Projects/AI-Career-Transition/10_学习文档/P01C-01_VLM基线与Benchmark_学习文档]]
- Phase 1-C 学习记录：[[02_Projects/AI-Career-Transition/20_学习记录/P01C_VLM基线与Benchmark_学习记录]]
- Agent Systems 系统学习骨架：[[02_Projects/AI-Career-Transition/10_学习文档/P03-01_Agent系统_学习文档]]
- Agent Systems 学习记录：[[02_Projects/AI-Career-Transition/20_学习记录/P03_Agent系统_学习记录]]
- 实践记录索引：[[02_Projects/AI-Career-Transition/30_实践记录/实践记录索引]]

后续阶段实验、作品和求职记录优先留在本项目目录。只有形成长期稳定、经过审核并具有明确适用边界的可复用结论后，才评估是否提升到正式知识区。

## 1.5 当前状态

- 已完成职业方向定位和 12 个月学习路线优化。
- 已完成第一阶段 LLM 最小推理机制主动诊断；概念解释、边界辨析与 VLM 输入迁移达到对话诊断意义上的可用理解。
- Phase 1 的 LLM 训练机制子主线已经完成；cross-entropy、SFT masking、基础梯度流、训练循环可靠性、混合精度以及 Adam/AdamW 闭卷主干已形成，但这不等同于原学习方案中 Phase 1-A 的全部理论与实践任务已经完成。
- 已生成并更新 [[02_Projects/AI-Career-Transition/10_学习文档/P01A-02_LLM训练机制_学习文档]]；`/home/jichao/test/llm_practice.py` 已完成 `nn.Module` 形式 TinyCausalLM 的单步更新、单 batch 过拟合、确定性 eval 和 CPU 内存 checkpoint 轨迹恢复。
- 后续阶段统一从 [[02_Projects/AI-Career-Transition/20_学习记录/当前阶段学习检查点]] 恢复；阶段完成后先生成持久系统学习文档，再滚动更新该固定检查点。
- 2026-08-04 用户运行报告确定性 eval loss 为 `0.0916125476360321`、有效 token accuracy 为 `3/3`；checkpoint 恢复分支与参考分支的 loss、gradient norm、LM Head delta 和最终参数最大差值均为 0。本结论同时经过静态代码审查，但未由代理独立复跑。
- 2026-08-06 用户确认 `Phase 1-A closure` 在面向 Agent 开发与 AI Infra 的调整范围内完成：架构、Transformer 主干、采样、位置编码、证据边界和自回归生成机制达到对话诊断意义上的 working。
- Phase 1-A 的独立 attention 实现、真实采样实验和手写完整 GPT 记为 `waived_by_scope`；真实 tokenizer 到输出文本闭环及真实模型证据对照仍为 `not_verified`，不得改写为运行完成。
- Phase 1-B“评测基本功与练习集”已按调整范围关闭：任务类型、评分方法、评测合同、abstain/失败标签、评分一致性与留出集污染达到对话诊断意义上的 working。
- Phase 1-B 的四类 seed case 只形成对话草案；持久化、隔天重复评分、确定性规则基线和逐 case 运行由用户标记为 `waived_by_scope`，不得改写为已执行或已建立 benchmark。
- 当前主阶段已切换为 Phase 1-C“VLM 基线与 benchmark 草案”：先建立 VLM 输入到输出的数据流，再运行开源小型 VLM 的最小图像问答基线。
- 已新增 [[02_Projects/AI-Career-Transition/10_学习文档/学习文档索引]] 管理历史学习文档归类；[[02_Projects/AI-Career-Transition/10_学习文档/P01C-01_VLM基线与Benchmark_学习文档]] 已由教学草案转为 `active` 的阶段学习文档，但这不代表 Phase 1-C 已完成。
- Phase 1-C 的 baseline 可复现合同、执行/case/聚合/门禁分层、留出集污染、分组与安全关键组门禁、逐样本审计要求以及单图 case 证据边界已达到对话诊断意义上的 `working`。
- Phase 1-C 后续诊断补齐了输入内容身份、Qwen 处理器封装、结构化输出、执行失败分母、ROI 一致性、确定性解码和 CUDA 环境证据边界；baseline 理论合同已达到 `working`，实际 zero-shot 已运行但语义能力失败，整体因缺少独立留出集、few-shot 范围决定和完整模型身份而保持 `partial`。
- 目标运行环境已由 WSL RTX 4050 调整为 Google Colab T4。用户已报告并保存 Python、PyTorch、PyTorch CUDA runtime、依赖、driver、GPU 和显存快照；模型文件 hash、精确 revision 和许可证快照尚未冻结。
- 原实践顺序为单图 smoke test、冻结小型 case 集、zero-shot baseline、错误分类和 few-shot 对比；2026-08-17 完成 prompt/input contract 诊断后，不再用泛化理论诊断或 prompt 搜索替代真实 baseline，也不把严格多模态 few-shot 设为当前默认阻塞项。
- 2026-08-14 用户报告已在 Google Colab 使用 Qwen2.5-VL-3B-Instruct 完成单图 smoke test：链路执行成功，归一化后双眼状态与用户标注一致，耗时 `13.581s`，峰值显存 allocated `8.631 GiB`、reserved `9.137 GiB`；原始输出带 Markdown 代码围栏，因此严格裸 JSON 未通过。完整边界见 [[02_Projects/AI-Career-Transition/30_实践记录/P01C_VLM单图SmokeTest_2026-08-14_实践记录]]。
- 2026-08-15 用户冻结允许单个 `json` 代码围栏的归一化合同，修复答案示例泄露和 `expected` 全局变量问题，并在 5 个内部授权 case 上完成 zero-shot 初始基线。execution/parse success 均为 100%，case exact match 与 per-eye accuracy 均为 20%；模型对所有眼睛输出 `closed`。不同原图和处理后 tensor 的 MD5 排除了重复输入，固定人脸 ROI 仍未修复 clear-open 失败。完整证据见 [[02_Projects/AI-Career-Transition/30_实践记录/P01C_VLMZeroShot初始基线_2026-08-15_实践记录]]。
- 2026-08-17 用户在同一 5-case 开发集上完成文本示例、标签定义顺序和单眼 ROI 诊断。文本示例版本的 case/per-eye 指标为 `40%/50%`，两种定义顺序分别为 `20%/30%` 与 `40%/50%`，单眼 ROI 合同为 `40%` per-eye accuracy；预测分布分别转移到 `open/narrow`、`closed/open` 和 `abstain/open`，证明结果对 prompt 与输入合同敏感。完整证据见 [[02_Projects/AI-Career-Transition/30_实践记录/P01C_VLMPrompt与单眼ROI诊断_2026-08-17_实践记录]]。
- 随后用户在相同全图开发集上尝试 Qwen3.5-4B。首次 5/5 输出在自然语言分析阶段结束且没有形成 JSON；后续 T4 可运行配置同时采用 INT4 与受限 `max_pixels`，用户定性报告未见改善。该结果只支持“当前硬件上的可部署配置没有观察到收益”，不能作为纯模型代际能力结论。完整边界见 [[02_Projects/AI-Career-Transition/30_实践记录/P01C_Qwen3.5代际替换与资源约束诊断_2026-08-17_实践记录]]。
- 本轮主动学习已闭合 prompt 敏感性、小样本指标边界、ROI 混杂变量、失败 baseline 停止规则和模型任务分层。用户能够说明专用感知模型负责低层细粒度事实，VLM 负责全局语义与长尾辅助，时序状态层形成稳定状态，策略门禁决定报警或动作。
- 上述结果均为用户报告、代理未独立复跑。当前 5 个 case 已参与错误分析，只能作为开发/诊断集；它们证明初始 zero-shot baseline 已运行并失败，不代表稳定 benchmark、最终分组能力或正式门禁已经完成。
- 当前停止继续枚举 prompt、ROI、量化、像素预算和模型版本来提高开发集分数。文本类别示例只作为 prompt 敏感性诊断，不记为严格多模态 few-shot；下一步完成 Phase 1-C 范围收尾并进入分层多模态系统设计，未来若建设可移交 benchmark 再冻结未查看留出集和完整模型/input contract。
- Agent Systems 系统学习文档继续作为后续学习骨架，不在本次切换中替代 Phase 1-C 主线。
- `global_step` 持久化、磁盘 checkpoint、错误 label mask、变长 micro-batch、性能测量和生产训练加固作为后续工程项保留，不阻塞本次学习主线切换。
- 当前不创建五份 current 文档组；待本项目形成持续迭代的设计、实现和验证事实后再评估 current 化。
- 不声明 `single_pass_recoverable: true`。

## 1.6 更新规则

- 每月更新阶段进度、产物和验证结果，不只记录学习时长。
- 只有具备代码、测试、指标、失败分析或真实运行证据的内容才计入能力完成度。
- AI 辅助生成的代码必须经过独立讲解、关键模块闭卷重写或故障定位验证，才能计入能力完成度。
- 可以记录已授权的项目名称、技术事实和验证证据，但不记录学历、雇主、任职时长、个人与项目的任职关系或其他可识别个人的信息。
- 职业方向发生变化时先更新本总览，再调整详细学习方案和作品路线。
