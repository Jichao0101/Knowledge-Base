---
title: Agent Workflow Design Current
summary: Agent Workflow 项目化管理的当前设计，说明规范层、项目层、current 与 modification records 的职责边界。
status: verified
doc_role: current
truth_role: current
current_kind: design
lifecycle_state: active
default_entry: false
sync_required_when:
  - current 与 modification records 分工变化
  - 规范层与项目层分工变化
  - 文档 owner 变化
retrieval_priority: current
supersedes: []
merged_into: []
current_replacement: []
related_code: []
sources:
  - 02_Projects/Agent Workflow/workflow_overview_current.md
  - 01_Knowledge/Agent Workflow/Agent驱动知识库、代码库与板端侧协同闭环规范.md
scope: 适用于恢复 Agent Workflow 主题当前如何被知识规范与项目文档共同管理。
risks:
  - 部分 project-side owner 仍处于第一轮抽象，后续可能继续细化。
updated_at: 2026-04-13
---

## 0.1 Current Goal

Agent Workflow 当前目标不是继续扩张规范数量，而是把“稳定规范”和“演化过程管理”分开。

## 0.2 Current Layering

- `01_Knowledge/Agent Workflow`：稳定规则、模板、状态机、契约
- `02_Projects/Agent Workflow`：演化主题 current、诊断记录、调整记录、验证记录

## 0.3 current 与 modification-record 分工

- `current`：
  - 当前态语义
  - 机制规则与约束
  - 当前真相源索引
- `modification record`：
  - 触发事件与动机
  - route / decision / accepted change
  - verification boundary
  - review / closure decision
  - target current docs

## 0.4 Non-goals

- 不把 current 写成 changelog
- 不把 modification record 写成 patch 回放
- 不把知识规范原样复制到项目 current 中

## 0.5 Owner Rules

- overview owner：默认入口、恢复链、真相源集合
- design owner：主题分层、职责边界、owner 分配
- spec owner：强规则、写回门禁、record taxonomy
- implementation owner：这些规则当前落在哪些知识规范与项目文档
- validation owner：哪些规则已被项目实例验证，哪些仍缺落地证据

## 0.6 Known Gaps

- 还没有统一把 modification-record 模板推广到所有既有主题
- 还没有对更多项目主题执行一次 current + record taxonomy 收敛
