---
title: cutepower Spec Current
summary: 当前项目级强规则是：cutepower 的 current 只能描述现状，contracts 是唯一治理真相源，artifact-driven runtime 是唯一主线执行模型，知识库项目名也固定为 cutepower。
status: pending_review
doc_role: current
truth_role: current
current_kind: spec
lifecycle_state: active
default_entry: false
sync_required_when:
  - 真相源优先级变化
  - runtime entry 或 capability model 变化
  - 项目区 current / baseline / record 规则变化
retrieval_priority: current
supersedes: []
merged_into: []
current_replacement: []
related_code: []
related_plugins:
  - cutepower
sources:
  - /mnt/d/cutepower/contracts/
  - /mnt/d/cutepower/scripts/task-intake.js
  - /mnt/d/cutepower/scripts/host-runtime.js
  - /mnt/d/cutepower/scripts/runtime-gates.js
  - /mnt/d/cutepower/scripts/governance-response.js
  - /mnt/d/cutepower/scripts/run-artifacts.js
  - /mnt/d/cutepower/agents/openai.yaml
scope: 适用于定义 cutepower 当前项目区同步规则、真相源优先级与禁止行为，不替代 contracts 本身。
risks:
  - 若 project spec 与 repo contracts 漂移，会再次形成两套治理语义。
  - 若 historical record 被误读为 current rule，会恢复旧 hook 叙事。
updated_at: 2026-04-23
---

## 0.1 Required Behaviors

- cutepower 的运行治理优先读取 `/mnt/d/cutepower/contracts/`
- 工程类自然语言请求默认先走 `/mnt/d/cutepower/scripts/task-intake.js`
- 显式模式下的宿主上下文注入以 `/mnt/d/cutepower/agents/openai.yaml` 和 `/mnt/d/cutepower/scripts/host-runtime.js` 为准
- 高风险动作准入以 `/mnt/d/cutepower/scripts/runtime-gates.js` 为准
- repo-local run state 与 `schemas/run-artifacts/` 是当前 runtime source of truth
- current、baseline、record 必须放在 `02_Projects/cutepower/`

## 0.2 Prohibited Behaviors

- 不允许把 `Agent Workflow` 继续作为 cutepower 的项目名
- 不允许恢复 `codex-hooks.js` / `codex-host-adapter.js` / `test-codex-hooks.js` 为 current truth
- 不允许把 `.codex/hooks.json` 视为 install 成功判定或 uninstall 清理对象
- 不允许把 README、baseline 或 record 提升为高于 contracts 的规则源
- 不允许把 cuteagents 提前混入当前 cutepower current 语义
