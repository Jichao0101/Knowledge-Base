---
title: Agent Workflow Implementation Current
summary: 当前 Agent Workflow 主题的落点映射：cutepower 的 contracts、skills、scripts 与桥接层写在 plugin 内；项目区只保留 current、baseline 与 cutepower record。
status: pending_review
doc_role: current
truth_role: current
current_kind: implementation
lifecycle_state: active
default_entry: false
sync_required_when:
  - cutepower 落点变化
  - 保留的项目资产集合变化
  - runtime gate 或验证脚本变化
retrieval_priority: current
supersedes: []
merged_into: []
current_replacement: []
related_code: []
related_plugins:
  - plugins/cutepower
sources:
  - plugins/cutepower/.codex-plugin/plugin.json
  - plugins/cutepower/README.md
  - plugins/cutepower/contracts/contract-index.yaml
  - plugins/cutepower/scripts/validate-contracts.js
  - plugins/cutepower/scripts/test-runtime-gates.js
  - 02_Projects/Agent Workflow/cutepower P1插件落地与运行时门禁收敛记录-2026-04-17.md
scope: 适用于快速定位当前 cutepower 资产写在哪些 plugin 和项目文件中。
risks:
  - 若继续把 legacy plugin 或 legacy project record 视为实现入口，会恢复错误落点。
updated_at: 2026-04-17
---

## 0.1 Plugin-side Mapping

- 插件根目录：`plugins/cutepower`
- plugin manifest：`plugins/cutepower/.codex-plugin/plugin.json`
- 极薄入口：`plugins/cutepower/AGENTS.md`
- 安装入口：`plugins/cutepower/README.codex.md`、`plugins/cutepower/.codex/INSTALL.md`
- active governance truth：
  - `plugins/cutepower/contracts/contract-index.yaml`
  - `plugins/cutepower/contracts/gate-matrix.yaml`
  - `plugins/cutepower/contracts/role-contracts.yaml`
  - `plugins/cutepower/contracts/review-boundaries.yaml`
  - `plugins/cutepower/contracts/writeback-levels.yaml`
  - `plugins/cutepower/contracts/routing-table.yaml`
- validation / runtime gate：
  - `plugins/cutepower/scripts/validate-contracts.js`
  - `plugins/cutepower/scripts/runtime-gates.js`
  - `plugins/cutepower/scripts/test-runtime-gates.js`

## 0.2 Active Skill Mapping

P0：

- `plugins/cutepower/skills/using-cutepower/SKILL.md`
- `plugins/cutepower/skills/cute-scope-plan/SKILL.md`
- `plugins/cutepower/skills/cute-repo-change/SKILL.md`
- `plugins/cutepower/skills/cute-code-review/SKILL.md`
- `plugins/cutepower/skills/cute-writeback/SKILL.md`

P1：

- `plugins/cutepower/skills/cute-board-run/SKILL.md`
- `plugins/cutepower/skills/cute-functional-review/SKILL.md`
- `plugins/cutepower/skills/cute-incident-investigation/SKILL.md`

thin agent descriptors：

- `plugins/cutepower/agents/scope-plan.toml`
- `plugins/cutepower/agents/repo-change.toml`
- `plugins/cutepower/agents/code-review.toml`
- `plugins/cutepower/agents/writeback.toml`

## 0.3 Project-side Mapping

current：

- `workflow_overview_current`
- `workflow_interface_current`
- `workflow_design_current`
- `workflow_spec_current`
- `workflow_implementation_current`
- `workflow_validation_current`

baseline：

- `cutepower_p0_implementation_baseline.md`
- `cutepower_p1_board_functional_incident_baseline.md`

record：

- `cutepower P1插件落地与运行时门禁收敛记录-2026-04-17.md`

## 0.4 Removed Assets

以下资产不再属于当前落点：

- 原三侧项目记录
- Chaospower 项目记录
- 原三侧正式知识文档
- `plugins/chaospower` 作为当前实现入口

## 0.5 Current Recovery Note

恢复当前 cutepower 状态时，应先读 plugin truth，再用本文件确认项目区保留了哪些 current / baseline / record 资产；
不需要再恢复已删除的原三侧或 Chaospower 记录。
