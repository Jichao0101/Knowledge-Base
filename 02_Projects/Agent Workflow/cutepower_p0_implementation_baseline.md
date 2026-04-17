---
title: cutepower P0 implementation baseline
summary: cutepower P0 第一阶段实施基线的历史快照，保留当时的实施边界与 reviewer 验收项；不再作为当前 plugin 实现或测试入口。
status: verified
doc_role: baseline
truth_role: history
lifecycle_state: superseded
default_entry: false
retrieval_priority: reference
current_replacement:
  - plugins/cutepower/contracts/
  - plugins/cutepower/skills/
  - plugins/cutepower/README.md
scope: 适用于追溯 cutepower P0 第一阶段的实施边界与 reviewer 验收项，不再作为当前 plugin 实现或测试入口。
related_plugins:
  - plugins/cutepower
sources:
  - 01_Knowledge/Agent Workflow/Plugin-first与Contracts-first治理插件设计模式.md
  - 02_Projects/Agent Workflow/workflow_overview_current.md
  - 02_Projects/Agent Workflow/workflow_design_current.md
  - 02_Projects/Agent Workflow/workflow_spec_current.md
  - 02_Projects/Agent Workflow/workflow_implementation_current.md
  - 02_Projects/Agent Workflow/cutepower P1插件落地与运行时门禁收敛记录-2026-04-17.md
updated_at: 2026-04-17
---

> Status note:
> 本文件已降级为历史 baseline。cutepower 当前 active truth 以 `plugins/cutepower/contracts/`、`skills/`、`scripts/` 和安装/README 文档为准；后续测试不应再将本文件当作默认实现输入。

# 1 目标与范围

本轮目标是将已经收敛的 cutepower P0 插件方案写成项目实施基线，并据此落地第一阶段最小可运行骨架。

本轮只做以下事情：

- 将 active 运行资产固定到 `plugins/cutepower`
- 将 core governance contracts 固定到 plugin 自带 `contracts/`
- 将 skills 压到“消费 contracts”的最小形态
- 将 `AGENTS.md` 与 `agents/*.toml` 压到桥接层
- 加入第一阶段最小 validation：`schema + lint + cross-reference check`
- 为 reviewer 提供稳定验收清单

# 2 本轮明确要实现的内容

1. 创建 `plugins/cutepower` 的 P0 最小目录骨架
2. 创建最小 plugin manifest
3. 创建以下 core contracts：
   - `gate-matrix`
   - `role-contracts`
   - `review-boundaries`
   - `writeback-levels`
   - `routing-table`
4. 创建 contract index，但仅作为索引
5. 创建最小 schemas
6. 创建 5 个 P0 skills：
   - `using-cutepower`
   - `cute-scope-plan`
   - `cute-repo-change`
   - `cute-code-review`
   - `cute-writeback`
7. 创建最小 `validate-contracts` 脚本
8. 创建最小 bridge `AGENTS.md`
9. 只为确实需要直接实例化的角色保留最小 `agents/*.toml`

# 3 本轮明确不实现的内容

- 不新增 P1/P2 skills
- 不实现复杂 hooks
- 不实现自动修复
- 不实现运行时自动 enforcement
- 不把 legacy 文档重新提升为 active truth source
- 不把治理正文重新写回 skill / AGENTS / toml
- 不让 overlay 放宽权限
- 不为所有 skill 强行创建 toml

# 4 第一阶段目录结构

```text
plugins/cutepower/
├── .codex-plugin/plugin.json
├── AGENTS.md
├── README.md
├── contracts/
│   ├── contract-index.yaml
│   ├── gate-matrix.yaml
│   ├── role-contracts.yaml
│   ├── review-boundaries.yaml
│   ├── writeback-levels.yaml
│   └── routing-table.yaml
├── schemas/
│   ├── contract-index.schema.json
│   ├── gate-matrix.schema.json
│   ├── role-contracts.schema.json
│   ├── review-boundaries.schema.json
│   ├── writeback-levels.schema.json
│   ├── routing-table.schema.json
│   └── overlay.schema.json
├── skills/
│   ├── using-cutepower/SKILL.md
│   ├── cute-scope-plan/SKILL.md
│   ├── cute-repo-change/SKILL.md
│   ├── cute-code-review/SKILL.md
│   └── cute-writeback/SKILL.md
├── agents/
│   ├── scope-plan.toml
│   ├── repo-change.toml
│   ├── code-review.toml
│   └── writeback.toml
└── scripts/
    └── validate-contracts.js
```

# 5 5 个 P0 skills

## 5.1 using-cutepower

- 只负责入口解析、route、handoff、gate summary
- 只引用 contract id，不复制规则正文
- 不承接角色边界、review 边界、writeback 规则正文

## 5.2 cute-scope-plan

- 负责产出任务 profile、allowed scope、verification tier、implementation plan
- 消费 `routing-table`、`gate-matrix`

## 5.3 cute-repo-change

- 负责授权范围内实现与实现侧验证
- 消费 `gate-matrix`、`role-contracts`

## 5.4 cute-code-review

- 负责独立 review 决策
- 消费 `review-boundaries`、`role-contracts`

## 5.5 cute-writeback

- 负责项目区 writeback 收口
- 消费 `writeback-levels`、`gate-matrix`

# 6 5 个 core contracts

## 6.1 gate-matrix

- 定义高风险动作与核心门禁状态的关系

## 6.2 role-contracts

- 定义角色允许动作、最小输入输出与停止条件

## 6.3 review-boundaries

- 定义 reviewer 可做/不可做、所需证据与结论类型

## 6.4 writeback-levels

- 定义 writeback 三层及前置条件

## 6.5 routing-table

- 定义 `primary_type + modifiers -> skill_chain / required_roles / required_gates`

# 7 四个关键边界的硬约束

## 7.1 contract-index

- 只做索引，不做规则正文
- 只包含 contract id、path、schema、version、status、precedence
- 不承接 explanation、example、migration、exception

## 7.2 using-cutepower

- 只做入口解析 / route / handoff / gate summary
- 不承接角色、review、writeback 的正文解释
- 只允许引用 contract id，不允许复制 contract 内容

## 7.3 overlay

- 只能 `restrict-only`
- 不得新增 role/state/action/gate
- 不得将 `deny` 提升为 `allow`
- 不得放宽 writeback 或 reviewer 独立性

## 7.4 agents/*.toml

- 只是 `compatibility bridge`
- 不是 active truth source
- 只保留最小实例化描述
- 不得写入门禁矩阵、角色正文、review 正文、writeback 正文

# 8 第一阶段最小 validation 范围

本轮最小 validation 只覆盖：

- `schema`
- `lint`
- `cross-reference check`

本轮不覆盖：

- 自动修复
- 复杂 hook enforcement
- 运行时权限拦截

# 9 reviewer 验收清单

1. 是否先有项目区 baseline 文档，再有实现
2. 实现是否与 baseline 一致
3. `contract-index` 是否仍为纯索引
4. `using-cutepower` 是否仍为纯入口
5. overlay schema 是否保持 `restrict-only` 边界
6. `agents/*.toml` 是否只作为 compatibility bridge
7. contracts 是否保持 machine-readable，不夹带长篇解释
8. `validate-contracts` 是否能检查 schema、lint、cross-reference
9. 是否没有新增 P1/P2 skills、复杂 hooks、运行时 enforcement

# 10 当前状态

- current_status: `pending_review`
- implementation_gate: `allowed_after_baseline_written`
- review_focus:
  - P0 范围是否被扩大
  - 边界是否被实现过程破坏
  - contracts 是否重新退化为长文
