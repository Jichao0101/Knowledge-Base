---
title: cutepower Overview Current
summary: 当前知识库中的 active 项目是 cutepower，而不是笼统的 Agent Workflow。cutepower 代表 skill-first 路线；未来若出现 subagent-first 的 cuteagents，应作为并列项目存在。
status: pending_review
doc_role: current
truth_role: current
current_kind: overview
lifecycle_state: active
default_entry: true
default_entry_verified: true
sync_mode: current_patch
current_files_must_update:
  - 02_Projects/cutepower/cutepower_overview_current.md
  - 02_Projects/cutepower/cutepower_interface_current.md
  - 02_Projects/cutepower/cutepower_design_current.md
  - 02_Projects/cutepower/cutepower_spec_current.md
  - 02_Projects/cutepower/cutepower_implementation_current.md
  - 02_Projects/cutepower/cutepower_validation_current.md
history_files_to_mark: []
single_pass_recoverable: true
sync_required_when:
  - cutepower active truth source 变化
  - 默认入口与显式入口边界变化
  - runtime gate、artifact model 或 install model 变化
  - 项目目录归属变化
retrieval_priority: current
supersedes: []
merged_into: []
current_replacement: []
related_code: []
related_plugins:
  - cutepower
sources:
  - /mnt/d/cutepower/README.md
  - /mnt/d/cutepower/docs/runtime-hardening.md
  - /mnt/d/cutepower/contracts/
  - /mnt/d/cutepower/scripts/task-intake.js
  - /mnt/d/cutepower/scripts/host-runtime.js
  - /mnt/d/cutepower/scripts/runtime-gates.js
  - /mnt/d/cutepower/scripts/governance-response.js
  - /mnt/d/cutepower/scripts/run-artifacts.js
  - /mnt/d/cutepower/agents/openai.yaml
  - 02_Projects/cutepower/cutepower 主线去hook化与知识库项目收口记录-2026-04-23.md
scope: 适用于恢复当前 cutepower 项目的真相源、默认恢复顺序与项目区边界。
risks:
  - 若继续把 Agent Workflow 当项目名，会把后续 cuteagents 与 cutepower 混成一个主题桶。
  - 若把 historical record 当 current truth，会重新引入已删除的 hook 主线假设。
updated_at: 2026-04-23
---

## 0.1 Current Scope

当前知识库项目是 `cutepower`，不是 `Agent Workflow`。

这里的 cutepower 指向一个已经独立成仓、以 plugin + contracts + skills 为中心的 skill-first 治理项目：

- 仓库：`/mnt/d/cutepower`
- active truth：`contracts/`
- runtime 入口：`agents/openai.yaml` + `scripts/task-intake.js` + `scripts/host-runtime.js`
- action gate：`scripts/runtime-gates.js`
- repo-local run state：`.cutepower/run/<session_id>/`

未来若出现 subagent-first 的 `cuteagents`，它应作为与 `cutepower` 并列的独立项目，而不是继续塞回同一个 `Agent Workflow` 项目目录。

## 0.2 Default Recovery Order

1. [[02_Projects/cutepower/cutepower_overview_current]]
2. [[02_Projects/cutepower/cutepower_interface_current]]
3. [[02_Projects/cutepower/cutepower_design_current]]
4. [[02_Projects/cutepower/cutepower_spec_current]]
5. [[02_Projects/cutepower/cutepower_implementation_current]]
6. [[02_Projects/cutepower/cutepower_validation_current]]

## 0.3 Current Bundle

- current：仅描述当前 cutepower 状态与恢复链
- baseline：仅保留历史实施边界
- record：仅保留 cutepower-specific 事件证据

## 0.4 Not In Scope

- 原 Agent Workflow 总项目叙事
- 旧 `codex-hooks.js` / `codex-host-adapter.js` / `test-codex-hooks.js` 主线
- 把知识库目录语义写回 cutepower plugin
