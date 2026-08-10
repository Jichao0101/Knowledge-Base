---
type: project_learning_index
status: active
project: AI-Career-Transition
summary: 管理 AI Career Transition 项目的学习方案、滚动检查点、阶段系统学习文档和并行专题骨架，避免历史学习文档散落在同一层后难以恢复。
sources:
  - 2026-08-10 用户提出 AI Career 历史学习文档需要归类，并确认优先通过文档管理而非立即批量重命名处理
  - 02_Projects/AI-Career-Transition/AI职业转型项目总览.md
  - 02_Projects/AI-Career-Transition/当前阶段学习检查点.md
scope: AI Career Transition 项目的学习文档入口、阶段归类、恢复顺序和命名规则。
risks:
  - 本索引只管理项目学习文档，不替代阶段学习文档、滚动检查点或项目总览中的事实边界。
  - 既有文件暂不批量重命名，避免破坏已有 wiki 链接；阶段归类以本索引为准。
updated_at: 2026-08-10
---

# 1 AI 职业转型学习文档索引

## 1.1 用途

本索引用于解决 AI Career Transition 项目学习材料的恢复和归类问题。项目目录下的历史文档暂不批量搬移或重命名；先通过阶段索引明确每份文档的职责、阶段和读取顺序。

文档职责分为四类：

| 类型 | 作用 | 当前文件 |
|---|---|---|
| 项目入口 | 管理目标岗位、路线、状态和更新规则 | [[02_Projects/AI-Career-Transition/AI职业转型项目总览]] |
| 主学习方案 | 管理 12 个月路线、主动学习方法、阶段门禁和复盘规则 | [[02_Projects/AI-Career-Transition/多模态AI职业转型学习方案]] |
| 滚动检查点 | 指向当前阶段、恢复顺序、当前门禁和未完成项 | [[02_Projects/AI-Career-Transition/当前阶段学习检查点]] |
| 阶段学习文档 | 保存每个阶段的教学骨架、主动学习闭合记录和实践边界 | 下方阶段表 |

## 1.2 阶段文档表

| 阶段 | 文档 | 状态 | 说明 |
|---|---|---|---|
| Phase 0 | [[02_Projects/AI-Career-Transition/LLM最小推理机制系统学习文档]] | active | LLM 最小推理数据流、生成机制、VLM 输入迁移和 Phase 1-A closure 边界。 |
| Phase 1 | [[02_Projects/AI-Career-Transition/LLM训练机制系统学习文档]] | active | next-token 训练、loss、mask、梯度、AdamW、混合精度和 checkpoint 最小实践。 |
| Phase 1-B | [[02_Projects/AI-Career-Transition/AI评测基本功系统学习文档]] | active | 任务类型、评分方法、评测合同、可靠性边界和 seed case 范围关闭记录。 |
| Phase 1-C | [[02_Projects/AI-Career-Transition/Phase1-C_VLM基线与benchmark草案系统学习文档]] | draft | VLM 数据流、图像/视频 token 预算、最小 VLM baseline、benchmark 草案和分组评测。 |
| 并行专题 | [[02_Projects/AI-Career-Transition/Agent开发系统学习文档]] | draft | Agent Systems 学习骨架；作为后续 Agent Systems 主线背景，不替代 Phase 1-C。 |

## 1.3 当前恢复顺序

当前主阶段为 Phase 1-C。恢复时按以下顺序读取：

1. [[02_Projects/AI-Career-Transition/当前阶段学习检查点]]：确认当前阶段、完成门禁和未完成项。
2. [[02_Projects/AI-Career-Transition/多模态AI职业转型学习方案]] 的 `1.3.4 主动学习使用规则` 与 `1.5.3 阶段 C`：确认学习方法和阶段范围。
3. [[02_Projects/AI-Career-Transition/Phase1-C_VLM基线与benchmark草案系统学习文档]]：进入 Phase 1-C 的教学骨架、主动检查和实践计划。
4. 需要评测边界时回读 [[02_Projects/AI-Career-Transition/AI评测基本功系统学习文档]]，但不恢复已豁免的传统 seed case 脚本练习。

## 1.4 命名与维护规则

后续新增阶段学习文档优先在文件名中加入阶段，例如 `Phase1-C_...系统学习文档.md`。既有文档暂不重命名；如果未来确实需要统一命名，应先做链接影响检查，再执行结构迁移和索引同步。

阶段文档的定位规则：

- 阶段学习文档可以包含教学骨架、主动学习诊断、微型补课、实践计划和阶段边界。
- 滚动检查点只保存当前恢复指针和门禁，不承载完整教学材料。
- 项目总览只记录项目状态和入口，不展开教学内容。
- 对话中的 `working` 不替代运行证据；阶段完成仍需满足当前检查点中的完成门禁。
