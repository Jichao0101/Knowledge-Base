---
title: cutepower Implementation Current
summary: 当前 cutepower 的实现落点已经收口到 plugin-first + skill-first dispatcher + artifact-driven runtime：contracts 负责真相，skills 负责人类可读纪律，runtime gate 负责执行约束。
status: pending_review
doc_role: current
truth_role: current
current_kind: implementation
lifecycle_state: active
default_entry: false
sync_required_when:
  - 运行资产文件集合变化
  - dispatcher / skill route matrix 变化
  - validation entry 变化
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
  - /mnt/d/cutepower/contracts/
  - /mnt/d/cutepower/skills/
  - /mnt/d/cutepower/scripts/validate-contracts.js
  - /mnt/d/cutepower/scripts/task-profile.js
  - /mnt/d/cutepower/scripts/task-intake.js
  - /mnt/d/cutepower/scripts/host-runtime.js
  - /mnt/d/cutepower/scripts/runtime-gates.js
  - /mnt/d/cutepower/scripts/run-artifacts.js
  - /mnt/d/cutepower/docs/skill-workflow-map.md
scope: 适用于快速定位当前 cutepower 资产写在哪里，以及 dispatcher、skill routing、runtime gate 现在如何配合。
risks:
  - `contracts/` 仍是唯一 active truth；current 文档不能替代它。
  - skill 文本若与 `skill_route_matrix` 漂移，会削弱 skill-first discipline。
updated_at: 2026-04-23
---

## 0.1 Active Assets

- plugin manifest：`/mnt/d/cutepower/.codex-plugin/plugin.json`
- contracts：`/mnt/d/cutepower/contracts/`
- skill route matrix：`/mnt/d/cutepower/contracts/skill_route_matrix.yaml`
- skills：`/mnt/d/cutepower/skills/`
- task profiling：`/mnt/d/cutepower/scripts/task-profile.js`
- intake / dispatcher：`/mnt/d/cutepower/scripts/task-intake.js`
- host runtime：`/mnt/d/cutepower/scripts/host-runtime.js`
- action gate：`/mnt/d/cutepower/scripts/runtime-gates.js`
- run state：`/mnt/d/cutepower/scripts/run-artifacts.js`
- workflow map：`/mnt/d/cutepower/docs/skill-workflow-map.md`

## 0.2 Core Runtime Artifacts

- `task_profile.json`
- `route_resolution.json`
- `dispatch_manifest.json`
- `runtime_gate.json`

其中 `dispatch_manifest.json` 是当前 dispatcher 和 runtime gate 对齐 skill order 的关键工件。

## 0.3 Validation Entries

- `node scripts/validate-contracts.js`
- `node scripts/test-task-profile.js`
- `node scripts/test-task-intake.js`
- `node scripts/test-host-runtime.js`
- `node scripts/test-runtime-gates.js`
- `node scripts/test-skill-routing.js`
- `node scripts/test-skill-docs.js`
