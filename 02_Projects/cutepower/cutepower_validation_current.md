---
title: cutepower Validation Current
summary: 当前 cutepower 已验证 contracts-first routing、dispatcher preflight、skill order gating、host runtime capability 与 skill discipline 文档完整性；核心 runtime read path 已与 `analysis` phase 的当前主线对齐。
status: pending_review
doc_role: current
truth_role: current
current_kind: validation
lifecycle_state: active
default_entry: false
sync_required_when:
  - validation 结论变化
  - dispatcher / skill route matrix 覆盖面变化
  - host runtime / runtime gate 语义变化
retrieval_priority: current
supersedes: []
merged_into: []
current_replacement: []
related_code: []
related_plugins:
  - cutepower
sources:
  - /mnt/d/cutepower/scripts/validate-contracts.js
  - /mnt/d/cutepower/scripts/task-profile.js
  - /mnt/d/cutepower/scripts/task-intake.js
  - /mnt/d/cutepower/scripts/host-runtime.js
  - /mnt/d/cutepower/scripts/runtime-gates.js
  - /mnt/d/cutepower/scripts/run-artifacts.js
  - /mnt/d/cutepower/scripts/test-task-profile.js
  - /mnt/d/cutepower/scripts/test-task-intake.js
  - /mnt/d/cutepower/scripts/test-host-runtime.js
  - /mnt/d/cutepower/scripts/test-runtime-gates.js
  - /mnt/d/cutepower/scripts/test-skill-routing.js
  - /mnt/d/cutepower/scripts/test-skill-docs.js
  - /mnt/d/cutepower/README.md
scope: 适用于判断当前 cutepower 哪些 dispatcher、routing、runtime gate 边界已被验证。
risks:
  - 当前验证仍以本地 repo tests 为主，不等于所有宿主表面的真实验收。
updated_at: 2026-04-23
---

## 0.1 Validated

- `validate-contracts` 会校验 `routing-table`、`skill_route_matrix`、`protected_execution_skills` 的一致性
- `task-profile` 会产出 route 与 governed skill chain
- `task-intake` 会持久化 `dispatch_manifest` 并让 governed route 从 dispatcher 开始
- `host-runtime` 会携带新的 preflight artifact contract
- `runtime-gates` 会基于 capability、phase、artifact continuity 与 `dispatch_manifest.next_skill` 判定准入
- read-only audit 的 authorized read path 已与当前 `analysis` phase 对齐
- skill 文档完整性由 `test-skill-docs.js` 覆盖

## 0.2 Validation Entries

- `node scripts/validate-contracts.js`
- `node scripts/test-task-profile.js`
- `node scripts/test-task-intake.js`
- `node scripts/test-host-runtime.js`
- `node scripts/test-runtime-gates.js`
- `node scripts/test-skill-routing.js`
- `node scripts/test-skill-docs.js`

## 0.3 Not Validated Here

- 所有 Codex 宿主表面对 `agents/openai.yaml` 的真实兼容性
- future cuteagents 与 cutepower 并列后的跨项目恢复链
