---
title: cutepower Validation Current
summary: 当前 cutepower 已验证 artifact-driven runtime、host runtime capability、install/uninstall 脱钩旧 hook 配置，以及主线去 hook 化后的本地测试链。
status: pending_review
doc_role: current
truth_role: current
current_kind: validation
lifecycle_state: active
default_entry: false
sync_required_when:
  - validation 结论变化
  - install / uninstall 覆盖面变化
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
  - /mnt/d/cutepower/scripts/task-intake.js
  - /mnt/d/cutepower/scripts/host-runtime.js
  - /mnt/d/cutepower/scripts/runtime-gates.js
  - /mnt/d/cutepower/scripts/governance-response.js
  - /mnt/d/cutepower/scripts/run-artifacts.js
  - /mnt/d/cutepower/scripts/install-plugin.js
  - /mnt/d/cutepower/scripts/uninstall-plugin.js
  - /mnt/d/cutepower/scripts/test-task-profile.js
  - /mnt/d/cutepower/scripts/test-task-intake.js
  - /mnt/d/cutepower/scripts/test-host-runtime.js
  - /mnt/d/cutepower/scripts/test-runtime-gates.js
  - /mnt/d/cutepower/scripts/test-install-plugin.js
  - /mnt/d/cutepower/scripts/test-uninstall-plugin.js
  - /mnt/d/cutepower/README.md
  - /mnt/d/cutepower/docs/runtime-hardening.md
  - 02_Projects/cutepower/cutepower 主线去hook化与知识库项目收口记录-2026-04-23.md
scope: 适用于判断当前 cutepower 哪些边界已被验证，以及哪些历史 hook 假设已经失效。
risks:
  - 当前验证仍以本地 repo tests 为主，不等于所有宿主表面的真实验收。
updated_at: 2026-04-23
---

## 0.1 Validated

- install 不创建旧 runtime 配置文件
- uninstall 不依赖旧 runtime 配置文件清理
- `task-intake` 不再把 hook integration repair 当主线路由
- `host-runtime` 仍能从 persisted `runtime_gate` 生成 session capability
- `runtime-gates` 以 capability、phase、artifact existence 判定动作准入
- completion gate 文案与语义已从旧 `Stop hook` 收口到 completion gate
- `plugin.json` 已移除 runtime hook metadata，宿主入口保留在 `agents/openai.yaml`

## 0.2 Not Validated Here

- 所有 Codex 宿主表面对 `agents/openai.yaml` 的真实兼容性
- future cuteagents 与 cutepower 并列后的跨项目恢复链
