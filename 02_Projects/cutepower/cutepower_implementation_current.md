---
title: cutepower Implementation Current
summary: 当前 cutepower 的实现落点已经收口到 plugin-first + artifact-driven runtime：install/uninstall 只管 staged plugin 与 marketplace，主线不再包含旧 hook 文件链或 `.codex/hooks.json` 配置操作。
status: pending_review
doc_role: current
truth_role: current
current_kind: implementation
lifecycle_state: active
default_entry: false
sync_required_when:
  - 运行资产文件集合变化
  - install / uninstall 行为变化
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
  - /mnt/d/cutepower/.codex/INSTALL.md
  - /mnt/d/cutepower/contracts/
  - /mnt/d/cutepower/agents/openai.yaml
  - /mnt/d/cutepower/scripts/validate-contracts.js
  - /mnt/d/cutepower/scripts/task-intake.js
  - /mnt/d/cutepower/scripts/host-runtime.js
  - /mnt/d/cutepower/scripts/runtime-gates.js
  - /mnt/d/cutepower/scripts/governance-response.js
  - /mnt/d/cutepower/scripts/run-artifacts.js
  - /mnt/d/cutepower/scripts/install-plugin.js
  - /mnt/d/cutepower/scripts/uninstall-plugin.js
  - /mnt/d/cutepower/scripts/test-install-plugin.js
  - /mnt/d/cutepower/scripts/test-uninstall-plugin.js
  - 02_Projects/cutepower/cutepower 主线去hook化与知识库项目收口记录-2026-04-23.md
scope: 适用于快速定位当前 cutepower 资产写在哪里，以及哪些旧 hook 资产已经退出主线。
risks:
  - `agents/openai.yaml` 的宿主字段仍然是当前真实协议面，不能误删。
  - historical records 中仍会出现旧 hook 文件名，那是历史证据而非 current truth。
updated_at: 2026-04-23
---

## 0.1 Active Assets

- plugin manifest：`/mnt/d/cutepower/.codex-plugin/plugin.json`
- agent metadata：`/mnt/d/cutepower/agents/openai.yaml`
- contracts：`/mnt/d/cutepower/contracts/`
- intake：`/mnt/d/cutepower/scripts/task-intake.js`
- host runtime：`/mnt/d/cutepower/scripts/host-runtime.js`
- action gate：`/mnt/d/cutepower/scripts/runtime-gates.js`
- governance verdict：`/mnt/d/cutepower/scripts/governance-response.js`
- run state：`/mnt/d/cutepower/scripts/run-artifacts.js` + `/mnt/d/cutepower/schemas/run-artifacts/`
- install / uninstall：`/mnt/d/cutepower/scripts/install-plugin.js`、`/mnt/d/cutepower/scripts/uninstall-plugin.js`

## 0.2 Removed From Mainline

- `scripts/codex-hooks.js`
- `scripts/codex-host-adapter.js`
- `scripts/test-codex-hooks.js`
- `scripts/hook-response.js`
- `plugin.json.runtime.sessionContextHook`
- install / uninstall 对 `.codex/hooks.json` 的写入与清理

## 0.3 Validation Entries

- `node scripts/test-install-plugin.js`
- `node scripts/test-uninstall-plugin.js`
- `node scripts/test-host-runtime.js`
- `node scripts/validate-contracts.js`
- `node scripts/test-runtime-gates.js`
- `node scripts/test-task-profile.js`
- `node scripts/test-task-intake.js`
