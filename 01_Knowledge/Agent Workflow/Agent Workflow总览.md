---
type: knowledge_topic_index
status: active
domain: Agent Workflow
scope: Agent Workflow 正式知识入口；用于主题分流，不替代具体条目。
updated_at: 2026-06-05
---

# Agent Workflow 总览

本主题收录 agent 工程化、workflow/plugin 治理、current 文档组维护、知识升格和运行边界相关的正式知识。

## 1 入口分组

| 分组 | 条目 | 用途 |
|---|---|---|
| current 文档维护 | [[01_Knowledge/Agent Workflow/Current文档组生命周期维护与可恢复性规则]] | 项目区 current 文档组 creation、hardening、patch、rewrite 的生命周期规则 |
| 知识升格 | [[01_Knowledge/Agent Workflow/知识升格来源类型评估规则]] | 判断候选内容能否进入正式知识 |
| 运行治理 | [[01_Knowledge/Agent Workflow/运行时门禁与独立审查边界模式]] | route、review、writeback 等边界的运行期门禁模式 |
| 插件治理 | [[01_Knowledge/Agent Workflow/Plugin-first与Contracts-first治理插件设计模式]] | plugin-first 与 contracts-first 的治理插件设计 |
| Skill 开发 | [[01_Knowledge/Agent Workflow/Codex Skill开发与脚本化边界规范]] | skill 与脚本边界、可复用能力开发 |
| 生产级 Agent | [[01_Knowledge/Agent Workflow/生产级Agent的可控设计模式]] | 控制流、状态、工具接口、人类审批和可恢复设计 |
| Human layer | [[01_Knowledge/Agent Workflow/Human layer 的合理性与边界]] | 人类确认层的适用范围与边界 |

## 2 使用边界

- 本主题只沉淀可复用知识，不替代具体 plugin/runtime contract。
- 具体项目执行记录应留在 `02_Projects`。
- 外部 agent 方法论应先进入 `03_Inbox` 或 `04_Sources`，审核后再提升。

## 3 待结构化项

- 后续需要核验本主题新增条目的互相引用，避免重复定义运行治理。
- 若从候选区继续提升 HumanLayer 相关内容，应同步更新本索引和候选索引。
