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
  - 02_Projects/DMS/03_Model_Training/model_training_overview_current.md
  - 02_Projects/DMS/08_EyeStatus/eyestatus_overview_current.md
  - 02_Projects/agent-trajectory/agent_trajectory_overview_current.md
  - 02_Projects/AI-Career-Transition/多模态AI职业转型学习方案.md
scope: 职业方向、能力补齐、学习路线、作品建设、阶段验证与求职准备。
risks:
  - 学习范围横跨模型、系统和 Agent，若缺少阶段性交付，容易再次退化为零散学习或 vibe coding。
  - 本项目记录的是规划和阶段证据，不代表目标能力已经掌握或项目已经完成生产验证。
updated_at: 2026-08-06
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

- 主学习方案：[[02_Projects/AI-Career-Transition/多模态AI职业转型学习方案]]
- Phase 0 系统学习文档：[[02_Projects/AI-Career-Transition/LLM最小推理机制系统学习文档]]
- 当前阶段固定检查点：[[02_Projects/AI-Career-Transition/当前阶段学习检查点]]
- Phase 1 训练机制系统学习文档：[[02_Projects/AI-Career-Transition/LLM训练机制系统学习文档]]
- Agent Systems 系统学习骨架：[[02_Projects/AI-Career-Transition/Agent开发系统学习文档]]

后续阶段实验、作品和求职记录优先留在本项目目录。只有形成长期稳定、经过审核并具有明确适用边界的可复用结论后，才评估是否提升到正式知识区。

## 1.5 当前状态

- 已完成职业方向定位和 12 个月学习路线优化。
- 已完成第一阶段 LLM 最小推理机制主动诊断；概念解释、边界辨析与 VLM 输入迁移达到对话诊断意义上的可用理解。
- Phase 1 阶段 A 的 LLM 训练机制学习主线已经完成；cross-entropy、SFT masking、基础梯度流、训练循环可靠性、混合精度以及 Adam/AdamW 闭卷主干已形成。
- 已生成并更新 [[02_Projects/AI-Career-Transition/LLM训练机制系统学习文档]]；`/home/jichao/test/llm_practice.py` 已完成 `nn.Module` 形式 TinyCausalLM 的单步更新、单 batch 过拟合、确定性 eval 和 CPU 内存 checkpoint 轨迹恢复。
- 后续阶段统一从 [[02_Projects/AI-Career-Transition/当前阶段学习检查点]] 恢复；阶段完成后先生成持久系统学习文档，再滚动更新该固定检查点。
- 2026-08-04 用户运行报告确定性 eval loss 为 `0.0916125476360321`、有效 token accuracy 为 `3/3`；checkpoint 恢复分支与参考分支的 loss、gradient norm、LM Head delta 和最终参数最大差值均为 0。本结论同时经过静态代码审查，但未由代理独立复跑。
- 当前焦点切换到 Phase 1 阶段 B“评测基本功与练习集”：先定义一个小型可复核任务和 3 至 5 个 seed cases，再验证 rubric 与最简单基线；不得提前称为 benchmark。
- `global_step` 持久化、磁盘 checkpoint、错误 label mask、变长 micro-batch、性能测量和生产训练加固作为后续工程项保留，不阻塞本次学习主线切换。
- 当前不创建五份 current 文档组；待本项目形成持续迭代的设计、实现和验证事实后再评估 current 化。
- 不声明 `single_pass_recoverable: true`。

## 1.6 更新规则

- 每月更新阶段进度、产物和验证结果，不只记录学习时长。
- 只有具备代码、测试、指标、失败分析或真实运行证据的内容才计入能力完成度。
- AI 辅助生成的代码必须经过独立讲解、关键模块闭卷重写或故障定位验证，才能计入能力完成度。
- 可以记录已授权的项目名称、技术事实和验证证据，但不记录学历、雇主、任职时长、个人与项目的任职关系或其他可识别个人的信息。
- 职业方向发生变化时先更新本总览，再调整详细学习方案和作品路线。
