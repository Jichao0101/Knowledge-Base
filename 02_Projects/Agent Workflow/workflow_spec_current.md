---
title: Agent Workflow Spec Current
summary: 当前 Agent Workflow 主题的项目级强规则：cutepower plugin 是唯一 active truth；显式 runtime hardening 现在以 repo-local artifacts、phase machine、session capability 与 stop completion gate 落地。
status: pending_review
doc_role: current
truth_role: current
current_kind: spec
lifecycle_state: active
default_entry: false
sync_required_when:
  - cutepower 真相源优先级变化
  - current / baseline / record 规则变化
  - runtime gate 或 writeback 语义变化
retrieval_priority: current
supersedes: []
merged_into: []
current_replacement: []
related_code: []
related_plugins:
  - cutepower
sources:
  - /mnt/d/cutepower/contracts/contract-index.yaml
  - /mnt/d/cutepower/contracts/writeback-levels.yaml
  - /mnt/d/cutepower/contracts/review-boundaries.yaml
  - /mnt/d/cutepower/scripts/runtime-gates.js
  - /mnt/d/cutepower/scripts/task-intake.js
  - /mnt/d/cutepower/scripts/host-runtime.js
  - /mnt/d/cutepower/scripts/codex-hooks.js
  - /mnt/d/cutepower/scripts/run-artifacts.js
  - /mnt/d/cutepower/.codex-plugin/plugin.json
scope: 适用于定义 cutepower 当前项目区同步规则、真相源优先级与禁止行为，不替代 plugin contracts 本身。
risks:
  - 若 project spec 与 plugin contracts 发生漂移，会再次形成两套治理语义。
  - 若 record 被当成当前规则源，会破坏 single-pass recoverability。
updated_at: 2026-04-22
---

## 0.1 Required Behaviors

- cutepower 的运行治理必须优先读取 `/mnt/d/cutepower/contracts/`
- 工程类自然语言请求默认先走 `/mnt/d/cutepower/scripts/task-intake.js`
- 运行时高风险拒绝路径必须以 `/mnt/d/cutepower/scripts/runtime-gates.js` 为准
- 显式模式下，repo-local run state 与 `schemas/run-artifacts/` 是 artifact existence / shape 的当前实现载体
- 显式模式下，business execution / review / writeback 必须依赖宿主签发或 hook 安全派生的 session capability
- 显式模式下，stop 必须作为 completion gate，而不是纯摘要输出
- skills、`AGENTS.md`、`agents/*.toml` 只能作为薄桥接，不得复制治理正文
- 任何影响当前态语义的 cutepower 变更，必须同步更新 current 组
- 任何 cutepower-specific 实施或硬化事件，必须写入 cutepower-specific record
- baseline 只保留为历史参考，不得重新回升为默认实现入口

## 0.2 Prohibited Behaviors

- 不允许恢复原三侧或 Chaospower 为 current truth
- 不允许把宿主知识库目录、项目目录或候选区语义写进 cutepower plugin
- 不允许把 README、baseline 或 record 当作高于 contracts 的规则源
- 不允许把 reviewer、incident-investigator 或主代理扩回越权角色
- 不允许把 current 写成事件时间线或 patch 回放
- 不允许在 intake 返回 `blocked` 或 `clarification_required` 时静默绕过 cutepower
- 不允许在 explicit mode 下把 unmapped tool event 当 warn 后继续执行

## 0.3 Verification Contract

- current 组是否仍能 single-pass recover 当前 cutepower 状态
- current 是否只描述当前态，而不是复制 contracts
- current 是否只引用仍然存在的知识、plugin 和项目资产
- record 是否只承接 cutepower-specific 事件

## 0.4 Writeback Contract

- 先更新 plugin 真相源：contracts / skills / scripts / thin bridge
- 再更新 current 组，反映新的当前态
- 若本轮存在具体实现、硬化或验证事件，再补 cutepower-specific record
- baseline 仅在“冻结一轮实施边界”时更新，不作为普通 writeback 载体

## 0.5 Latest Governance Update

- `task-intake` 已把 preflight 输出从 session 提示提升为 repo-local artifacts，并为显式会话分配 `session_id`
- `host-runtime` 已签发包含 `session_id`、`route_id`、`phase`、`allowed_actions` 与 `artifact_dir` 的 session capability
- `runtime-gates` 已把 capability / phase / artifact existence-schema 检查前置到 protected execution
- `codex-hooks` 已将 explicit mode 的 unmapped tool event 从 warn 收紧为 default deny
- stop hook 已从 summary 收紧为 completion gate，缺少 `evidence_manifest`、`review_decision`、`writeback_receipt|writeback_declined` 时不得判定完成

## 0.6 Active Truth Source Priority

优先级从高到低：

1. `/mnt/d/cutepower/contracts/`
2. `/mnt/d/cutepower/scripts/task-intake.js`
3. `/mnt/d/cutepower/scripts/runtime-gates.js`
4. `/mnt/d/cutepower/scripts/run-artifacts.js` 与 `/mnt/d/cutepower/schemas/run-artifacts/`
5. `/mnt/d/cutepower/skills/`
6. `/mnt/d/cutepower/.codex-plugin/plugin.json`、`agents/openai.yaml`、`README.md`、`AGENTS.md`、`agents/*.toml`
7. `02_Projects/Agent Workflow/workflow_*_current.md`
8. `02_Projects/Agent Workflow/cutepower_*_baseline.md`
9. `02_Projects/Agent Workflow/cutepower *_记录*.md`
10. `01_Knowledge/Agent Workflow/*.md` 通用模式知识

若高优先级与低优先级冲突，以高优先级为准。
