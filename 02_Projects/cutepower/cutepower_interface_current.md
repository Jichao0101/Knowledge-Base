---
title: cutepower Interface Current
summary: 当前 cutepower 的宿主入口以 `agents/openai.yaml` 为 surface metadata，再由 `task-intake`、`host-runtime`、`runtime-gates` 和 repo-local artifacts 组成正式前门；旧 hook 文件链已退出主线。
status: pending_review
doc_role: current
truth_role: current
current_kind: interface
lifecycle_state: active
default_entry: false
sync_required_when:
  - 宿主入口字段变化
  - intake 或 host runtime 语义变化
  - 显式模式与默认模式边界变化
retrieval_priority: current
supersedes: []
merged_into: []
current_replacement: []
related_code: []
related_plugins:
  - cutepower
sources:
  - /mnt/d/cutepower/README.md
  - /mnt/d/cutepower/README.codex.md
  - /mnt/d/cutepower/.codex/INSTALL.md
  - /mnt/d/cutepower/agents/openai.yaml
  - /mnt/d/cutepower/scripts/task-intake.js
  - /mnt/d/cutepower/scripts/host-runtime.js
  - /mnt/d/cutepower/scripts/runtime-gates.js
  - /mnt/d/cutepower/scripts/run-artifacts.js
  - /mnt/d/cutepower/contracts/task-normalization.yaml
  - /mnt/d/cutepower/contracts/gate-matrix.yaml
  - 02_Projects/cutepower/cutepower_overview_current.md
scope: 适用于说明当前 cutepower 如何被宿主显式启用，以及默认入口如何落到 artifact-driven runtime。
risks:
  - `agents/openai.yaml` 仍是宿主协议字段，不能误删。
  - 如果把旧 hooks 配置当入口，会误读当前实现边界。
updated_at: 2026-04-23
---

## 0.1 Entry Model

当前入口分两层：

- 默认层：工程任务默认先尝试走 `scripts/task-intake.js`
- 显式层：当任务明确要求按 cutepower 执行时，宿主通过 `agents/openai.yaml` 中的 `session_context_hook` 调用 `scripts/host-runtime.js`

当前主线不再依赖以下旧资产：

- `scripts/codex-hooks.js`
- `scripts/codex-host-adapter.js`
- `scripts/test-codex-hooks.js`
- `.codex/hooks.json` 写入或清理

## 0.2 Runtime Flow

1. `task-intake` 解析 prompt，分配 `session_id`
2. preflight artifacts 写入 `.cutepower/run/<session_id>/`
3. `host-runtime` 读取 `runtime_gate` 并签发 `session_capability`
4. `runtime-gates` 根据 capability、phase、artifact existence 决定后续动作是否放行
5. 完成态依赖 closure artifacts，而不是旧 `Stop hook` 语义

## 0.3 Install Boundary

- install / uninstall 只负责 staged plugin copy 与 marketplace entry
- install 不写 `.codex/hooks.json`
- uninstall 不清 `.codex/hooks.json`
- `.codex-plugin/plugin.json` 不再携带 `runtime.sessionContextHook`
