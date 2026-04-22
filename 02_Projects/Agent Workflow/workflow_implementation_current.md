---
title: Agent Workflow Implementation Current
summary: 当前 Agent Workflow 主题的落点映射：cutepower 的 contracts、skills、scripts、repo-local run state 与宿主 hook 桥接写在 plugin 内；hooks 的实际接入落在安装目标环境，而不是开发仓库 repo 本身。
status: pending_review
doc_role: current
truth_role: current
current_kind: implementation
lifecycle_state: active
default_entry: false
sync_required_when:
  - cutepower 落点变化
  - 保留的项目资产集合变化
  - runtime gate、宿主 hook 或安装脚本变化
retrieval_priority: current
supersedes: []
merged_into: []
current_replacement: []
related_code: []
related_plugins:
  - cutepower
sources:
  - /mnt/d/cutepower/.codex-plugin/plugin.json
  - /mnt/d/cutepower/README.md
  - /mnt/d/cutepower/README.codex.md
  - /mnt/d/cutepower/docs/runtime-hardening.md
  - /mnt/d/cutepower/contracts/contract-index.yaml
  - /mnt/d/cutepower/scripts/validate-contracts.js
  - /mnt/d/cutepower/scripts/runtime-gates.js
  - /mnt/d/cutepower/scripts/task-intake.js
  - /mnt/d/cutepower/scripts/host-runtime.js
  - /mnt/d/cutepower/scripts/codex-hooks.js
  - /mnt/d/cutepower/scripts/run-artifacts.js
  - /mnt/d/cutepower/scripts/install-plugin.js
  - /mnt/d/cutepower/agents/openai.yaml
  - 02_Projects/Agent Workflow/cutepower runtime hardening闭环工件与phase强制记录-2026-04-22.md
scope: 适用于快速定位当前 cutepower 资产写在哪些 plugin 和项目文件中，以及宿主 hooks 实际由谁安装和接入。
risks:
  - 若继续把开发仓库 repo 自身的 `.codex/hooks.json` 视为正式 runtime 入口，会恢复错误落点。
  - 若宿主运行器忽略安装目标中的 hooks/config，仍无法得到绝对不可绕过的前门。
updated_at: 2026-04-22
---

## 0.1 Plugin-side Mapping

- 仓库根目录：`/mnt/d/cutepower`
- plugin manifest：`/mnt/d/cutepower/.codex-plugin/plugin.json`
- 极薄入口：`/mnt/d/cutepower/AGENTS.md`
- 安装入口：`/mnt/d/cutepower/README.codex.md`、`/mnt/d/cutepower/.codex/INSTALL.md`
- active governance truth：
  - `/mnt/d/cutepower/contracts/contract-index.yaml`
  - `/mnt/d/cutepower/contracts/gate-matrix.yaml`
  - `/mnt/d/cutepower/contracts/role-contracts.yaml`
  - `/mnt/d/cutepower/contracts/review-boundaries.yaml`
  - `/mnt/d/cutepower/contracts/writeback-levels.yaml`
  - `/mnt/d/cutepower/contracts/routing-table.yaml`
  - `/mnt/d/cutepower/contracts/task-normalization.yaml`
- validation / runtime gate：
  - `/mnt/d/cutepower/scripts/validate-contracts.js`
  - `/mnt/d/cutepower/scripts/runtime-gates.js`
  - `/mnt/d/cutepower/scripts/test-runtime-gates.js`
- default entry / intake / host bridge：
  - `/mnt/d/cutepower/scripts/task-intake.js`
  - `/mnt/d/cutepower/scripts/host-runtime.js`
  - `/mnt/d/cutepower/scripts/codex-hooks.js`
  - `/mnt/d/cutepower/scripts/test-task-intake.js`
  - `/mnt/d/cutepower/scripts/test-host-runtime.js`
  - `/mnt/d/cutepower/scripts/test-codex-hooks.js`
  - `/mnt/d/cutepower/agents/openai.yaml`
  - `/mnt/d/cutepower/.codex-plugin/plugin.json`
- run-state / artifact schema：
  - `/mnt/d/cutepower/scripts/run-artifacts.js`
  - `/mnt/d/cutepower/schemas/run-artifacts/`
- install-time host integration：
  - `/mnt/d/cutepower/scripts/install-plugin.js`
  - `/mnt/d/cutepower/scripts/test-install-plugin.js`

## 0.2 Active Skill Mapping

P0：

- `/mnt/d/cutepower/skills/using-cutepower/SKILL.md`
- `/mnt/d/cutepower/skills/cute-scope-plan/SKILL.md`
- `/mnt/d/cutepower/skills/cute-repo-change/SKILL.md`
- `/mnt/d/cutepower/skills/cute-code-review/SKILL.md`
- `/mnt/d/cutepower/skills/cute-writeback/SKILL.md`

P1：

- `/mnt/d/cutepower/skills/cute-board-run/SKILL.md`
- `/mnt/d/cutepower/skills/cute-functional-review/SKILL.md`
- `/mnt/d/cutepower/skills/cute-incident-investigation/SKILL.md`

thin agent descriptors：

- `/mnt/d/cutepower/agents/scope-plan.toml`
- `/mnt/d/cutepower/agents/repo-change.toml`
- `/mnt/d/cutepower/agents/code-review.toml`
- `/mnt/d/cutepower/agents/writeback.toml`

## 0.3 Host Hook Mapping

- 开发仓库本身不再承载正式 repo-level hooks 配置。
- 宿主 hooks 的正式接入点由安装脚本写入目标环境：
  - personal install：`~/.codex/config.toml`、`~/.codex/hooks.json`
  - repo install：`<target-root>/.codex/config.toml`、`<target-root>/.codex/hooks.json`
- 安装脚本负责：
  - 打开 `codex_hooks = true`
  - 合并 `UserPromptSubmit`、`PreToolUse`、`Stop`
  - 让 hook command 指向已安装插件里的 `scripts/codex-hooks.js`
- `scripts/codex-hooks.js` 自身只做桥接：
  - `UserPromptSubmit` 调 `host-runtime.js`
  - `PreToolUse` 调 `runtime-gates.js`
  - `Stop` 做 completion gate
  - state 按 workspace 写入 `/tmp`

## 0.4 Run-state Mapping

- 显式会话的 repo-local run state 写到 `.cutepower/run/<session_id>/`
- preflight artifacts：
  - `task_profile.json`
  - `route_resolution.json`
  - `runtime_gate.json`
  - `context_requirements.json`
  - `blocking_gaps.json`
- closure artifacts：
  - `evidence_manifest.json`
  - `review_decision.json`
  - `writeback_receipt.json`
  - `writeback_declined.json`

## 0.5 Project-side Mapping

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
- `cutepower 默认入口接管修复记录-2026-04-21.md`
- `cutepower 宿主hooks接入与安装目标注入记录-2026-04-22.md`
- `cutepower runtime hardening闭环工件与phase强制记录-2026-04-22.md`

## 0.6 Removed / Non-current Assets

以下资产不再属于当前正式落点：

- 开发仓库 repo 自身的 `.codex/config.toml`
- 开发仓库 repo 自身的 `.codex/hooks.json`
- 原三侧项目记录
- Chaospower 项目记录
- 原三侧正式知识文档
- legacy Chaospower 路径作为当前实现入口
- `.agents/plugins/marketplace.json` 中的 `agent-workflow-migrator` 入口

## 0.7 Current Recovery Note

恢复当前 cutepower 状态时，应先读 plugin truth，再用本文件确认：

- plugin 内有哪些 contracts / scripts / skills 仍是 active truth
- hooks 是通过安装目标接入，而不是通过开发仓库 repo 自身接入
- repo-local run state 与 artifact schema 已进入当前实现落点
- 项目区只保留 current / baseline / cutepower record 三类资产
