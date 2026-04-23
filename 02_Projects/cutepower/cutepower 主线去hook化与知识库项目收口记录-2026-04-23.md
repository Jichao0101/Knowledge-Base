---
title: cutepower 主线去hook化与知识库项目收口记录
summary: 记录 cutepower 在 2026-04-23 完成的主线去 hook 化收口，以及知识库项目从 Agent Workflow 收口为 cutepower 的同步修改。
status: pending_review
doc_role: modification_record
record_type: implementation_record
truth_role: evidence
lifecycle_state: pending_merge
default_entry: false
retrieval_priority: evidence_only
target_current_docs:
  - 02_Projects/cutepower/cutepower_overview_current.md
  - 02_Projects/cutepower/cutepower_interface_current.md
  - 02_Projects/cutepower/cutepower_design_current.md
  - 02_Projects/cutepower/cutepower_spec_current.md
  - 02_Projects/cutepower/cutepower_implementation_current.md
  - 02_Projects/cutepower/cutepower_validation_current.md
related_plugins:
  - cutepower
sources:
  - /mnt/d/cutepower/.codex-plugin/plugin.json
  - /mnt/d/cutepower/agents/openai.yaml
  - /mnt/d/cutepower/contracts/task-normalization.yaml
  - /mnt/d/cutepower/scripts/task-intake.js
  - /mnt/d/cutepower/scripts/host-runtime.js
  - /mnt/d/cutepower/scripts/runtime-gates.js
  - /mnt/d/cutepower/scripts/governance-response.js
  - /mnt/d/cutepower/scripts/install-plugin.js
  - /mnt/d/cutepower/scripts/uninstall-plugin.js
  - /mnt/d/cutepower/scripts/test-task-intake.js
  - /mnt/d/cutepower/scripts/test-host-runtime.js
  - /mnt/d/cutepower/scripts/test-runtime-gates.js
  - /mnt/d/cutepower/scripts/test-install-plugin.js
  - /mnt/d/cutepower/scripts/test-uninstall-plugin.js
scope: 适用于追溯本轮两类收口：cutepower 主线去 hook 化，以及知识库项目从 Agent Workflow 改为 cutepower。
risks:
  - `agents/openai.yaml` 里的 `session_context_hook` 仍是当前宿主协议字段，不能误删。
  - 历史 records 仍保留旧 hook 语义，那些内容只应被读取为历史证据。
updated_at: 2026-04-23
---

# 1 cutepower 主线去hook化与知识库项目收口记录

## 1.1 本轮问题定义

本轮要解决的是两个会持续制造误判的问题：

- cutepower 仓库已经把 install/uninstall、runtime gate 与测试主线收口到 artifact-driven model，但知识库 current 仍把 `codex-hooks.js`、`hook-response.js`、`.codex/hooks.json` 当主线描述。
- 知识库项目名仍然是 `Agent Workflow`，这会把未来可能出现的 `cuteagents` 与当前 skill-first 的 cutepower 混进同一个项目桶。

## 1.2 仓库侧已同步的当前事实

- `scripts/codex-hooks.js`、`scripts/codex-host-adapter.js`、`scripts/test-codex-hooks.js` 已不在 cutepower 主线。
- install / uninstall 不再写入或清理 `.codex/hooks.json`。
- `task-intake` 不再接受 `hook_integration_fix` 作为主线路由。
- `runtime-gates` 与 completion 文案已收口到 runtime / completion gate。
- `scripts/governance-response.js` 已替代 `scripts/hook-response.js` 成为主线治理裁决对象。
- `.codex-plugin/plugin.json` 已移除 `runtime.sessionContextHook`；宿主 surface metadata 保留在 `agents/openai.yaml`。

## 1.3 知识库侧同步

- 项目目录从 `02_Projects/Agent Workflow/` 改为 `02_Projects/cutepower/`。
- 6 个 current 文件统一改名为 `cutepower_*_current.md`。
- current 文档全部改写为当前仓库事实，不再把 hook 文件链或 `.codex/hooks.json` 写成主线。
- historical records 保留为证据，但路径与 current 引用切换到新的 `02_Projects/cutepower/`。

## 1.4 项目边界结论

当前知识库应把 cutepower 看作一个独立项目：

- `cutepower`：skill-first
- `cuteagents`：如果未来出现，应作为 subagent-first 的并列项目

不应再把两者先收纳进一个笼统的 `Agent Workflow` current 项目名下。
