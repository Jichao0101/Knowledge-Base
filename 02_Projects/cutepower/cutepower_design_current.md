---
title: cutepower Design Current
summary: cutepower 当前设计中心是 skill-first discipline + contracts-first truth + runtime-gate enforcement；dispatcher、skill route matrix 与 artifact-driven runtime 共同形成当前主线，而不是旧的 hook-front lifecycle 设计。
status: pending_review
doc_role: current
truth_role: current
current_kind: design
lifecycle_state: active
default_entry: false
sync_required_when:
  - contracts-first 边界变化
  - skill-first dispatcher 变化
  - artifact-driven gating 变化
  - 项目层命名与分层变化
retrieval_priority: current
supersedes: []
merged_into: []
current_replacement: []
related_code: []
related_plugins:
  - cutepower
sources:
  - 02_Projects/cutepower/cutepower_overview_current.md
  - /mnt/d/cutepower/README.md
  - /mnt/d/cutepower/docs/runtime-hardening.md
  - /mnt/d/cutepower/docs/skill-workflow-map.md
  - /mnt/d/cutepower/contracts/
  - /mnt/d/cutepower/scripts/task-intake.js
  - /mnt/d/cutepower/scripts/host-runtime.js
  - /mnt/d/cutepower/scripts/runtime-gates.js
  - /mnt/d/cutepower/scripts/governance-response.js
  - /mnt/d/cutepower/scripts/run-artifacts.js
scope: 适用于恢复当前 cutepower 的项目设计分层、skill discipline、角色边界与当前非目标。
risks:
  - 若把 current 写成 contracts 替代品，会削弱 contracts-first 主轴。
  - 若把 skill prose 误当 enforcement，会模糊 runtime gate 的职责边界。
  - 若把 future cuteagents 预先混入 cutepower current，会污染项目边界。
updated_at: 2026-04-23
---

## 0.1 Design Goal

当前目标是维护一个以 `using-cutepower` 为 mandatory dispatcher 的 skill-first 治理项目，而不是继续维护泛化的 Agent Workflow 总设计。

## 0.2 Layering

- `contracts/`：active governance truth source
- `contracts/skill_route_matrix.yaml`：route 到 skill 的结构化工作流约束
- `skills/`：消费 contracts 的 workflow discipline 层
- `scripts/task-intake.js`：默认入口、preflight 与 dispatcher artifact 生成
- `scripts/host-runtime.js`：session capability 注入
- `scripts/runtime-gates.js`：执行期 action gate + skill order gate
- `scripts/governance-response.js`：统一治理裁决对象
- `scripts/run-artifacts.js` + `schemas/run-artifacts/`：repo-local runtime state
- `README*` / `docs/skill-workflow-map.md` / `AGENTS.md` / `agents/*.toml`：薄桥接与人类可读总览

## 0.3 Current Mainline

- governed task 先进入 `using-cutepower`
- intake 产出 `task_profile`、`route_resolution`、`dispatch_manifest`、`runtime_gate`
- downstream skill 只能按 `dispatch_manifest.next_skill` 合法进入
- runtime gate 继续对 capability、phase、artifact continuity 与 skill order 做硬约束

## 0.4 Explicit Non-goals

- 恢复 hook 文件链作为主线
- 把 install/uninstall 重新做成 hook 配置管理器
- 把 knowledge-base 目录结构塞回 plugin
- 把 subagent-first orchestration 写回 cutepower 主线
- 把 cuteagents 与 cutepower 混写在同一个 current 集合里
