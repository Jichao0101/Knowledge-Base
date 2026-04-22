---
title: cutepower runtime hardening闭环工件与phase强制记录
summary: 记录 cutepower 在 2026-04-22 完成的 runtime hardening：把 hooks / host runtime 从“可遵循”提升为“默认不可跳过”，并引入 repo-local run artifacts、phase machine、session capability 与 stop completion gate。
status: pending_review
doc_role: modification_record
record_type: implementation_record
truth_role: evidence
lifecycle_state: pending_merge
default_entry: false
retrieval_priority: evidence_only
target_current_docs:
  - 02_Projects/Agent Workflow/workflow_overview_current.md
  - 02_Projects/Agent Workflow/workflow_interface_current.md
  - 02_Projects/Agent Workflow/workflow_design_current.md
  - 02_Projects/Agent Workflow/workflow_spec_current.md
  - 02_Projects/Agent Workflow/workflow_implementation_current.md
  - 02_Projects/Agent Workflow/workflow_validation_current.md
related_plugins:
  - cutepower
sources:
  - /mnt/d/cutepower/contracts/task-normalization.yaml
  - /mnt/d/cutepower/contracts/gate-matrix.yaml
  - /mnt/d/cutepower/contracts/role-contracts.yaml
  - /mnt/d/cutepower/contracts/review-boundaries.yaml
  - /mnt/d/cutepower/contracts/writeback-levels.yaml
  - /mnt/d/cutepower/scripts/task-intake.js
  - /mnt/d/cutepower/scripts/host-runtime.js
  - /mnt/d/cutepower/scripts/runtime-gates.js
  - /mnt/d/cutepower/scripts/codex-hooks.js
  - /mnt/d/cutepower/scripts/run-artifacts.js
  - /mnt/d/cutepower/schemas/run-artifacts/task_profile.json
  - /mnt/d/cutepower/schemas/run-artifacts/route_resolution.json
  - /mnt/d/cutepower/schemas/run-artifacts/runtime_gate.json
  - /mnt/d/cutepower/schemas/run-artifacts/context_requirements.json
  - /mnt/d/cutepower/schemas/run-artifacts/blocking_gaps.json
  - /mnt/d/cutepower/schemas/run-artifacts/evidence_manifest.json
  - /mnt/d/cutepower/schemas/run-artifacts/review_decision.json
  - /mnt/d/cutepower/schemas/run-artifacts/writeback_receipt.json
  - /mnt/d/cutepower/schemas/run-artifacts/writeback_declined.json
  - /mnt/d/cutepower/scripts/test-task-intake.js
  - /mnt/d/cutepower/scripts/test-host-runtime.js
  - /mnt/d/cutepower/scripts/test-runtime-gates.js
  - /mnt/d/cutepower/scripts/test-codex-hooks.js
  - /mnt/d/cutepower/docs/runtime-hardening.md
scope: 适用于追溯本轮 runtime hardening：闭环工件、phase machine、session capability、default deny unmapped event 与 stop completion gate。
risks:
  - 当前 capability 仍是 repo-local token，不是外部签名或远程鉴权。
  - 通用 tool event 映射仍有启发式边界。
updated_at: 2026-04-22
---

# 1 cutepower runtime hardening闭环工件与phase强制记录

## 1.1 本轮问题定义

本轮不是在 contracts 外再补一层“说明”，而是把已有 runtime lock 真正落成不可跳过的执行约束。

改造前存在两类缺口：

- hook 只能提醒“应该走 cutepower”，但未映射事件仍可能继续执行
- 即使 review 已完成，`task_profile`、`route_resolution`、`runtime_gate`、`evidence_manifest`、`review_decision`、`writeback_receipt` 等闭环工件仍可能只停留在 session context 或人工补写层

## 1.2 主要实现

### 1.2.1 repo-local run state

- 新增 `.cutepower/run/<session_id>/`
- `task-intake.js` 在显式会话里直接分配 `session_id`
- preflight 输出不再只存在于 `session_context`，而是写成真实 artifact：
  - `task_profile.json`
  - `route_resolution.json`
  - `runtime_gate.json`
  - `context_requirements.json`
  - `blocking_gaps.json`

### 1.2.2 stable schema

- 新增 `scripts/run-artifacts.js`
- 新增 `schemas/run-artifacts/`
- runtime gate 现在可以校验 artifact existence 与基础 shape，而不是只依赖字符串提示

### 1.2.3 phase machine

- 运行态 phase 现在显式区分：
  - `session_initialized`
  - `intake_accepted`
  - `route_resolved`
  - `gate_ready`
  - `review_active`
  - `writeback_ready`
  - `completed`
  - `declined`
  - `blocked`
  - `clarification_required`
- `runtime-gates.js` 会对 protected execution 做 phase admission

### 1.2.4 session capability

- `host-runtime.js` 现在签发 `session_capability`
- capability 绑定：
  - `session_id`
  - `route_id`
  - `phase`
  - `allowed_actions`
  - `artifact_dir`
  - `issued_at`
  - `expires_at`
- business execution / review / writeback 缺 capability 时默认拒绝

### 1.2.5 default deny 与 completion gate

- `codex-hooks.js` 的 `PreToolUse` 现在对 unmapped event 直接 deny
- `Stop` 不再只输出 denied/unmapped summary
- 显式模式任务若缺以下闭环产物，stop 失败：
  - `evidence_manifest`
  - `review_decision`，当 route 需要 review
  - `writeback_receipt` 或 `writeback_declined`，当 route 需要 writeback

## 1.3 验证覆盖

- `node scripts/test-task-profile.js`
- `node scripts/test-task-intake.js`
- `node scripts/test-host-runtime.js`
- `node scripts/test-runtime-gates.js`
- `node scripts/test-codex-hooks.js`

覆盖重点：

- unmapped event 被拒绝
- 缺 capability 被拒绝
- 缺 `task_profile` artifact 时 protected execution 被拒绝
- phase 不匹配时 writeback 被拒绝
- 缺闭环工件时 stop 失败
- 完整闭环时 stop 成功

## 1.4 当前边界

- contracts 仍然是治理真相源，record 不复制 contracts 规则正文
- 当前实现没有引入外部数据库或远程服务
- reviewer / writeback adjudication 独立性没有被放宽
- “绝对不可绕过”仍取决于宿主是否实际执行安装目标环境里的 hooks，并向 hook 提供足够结构化的 tool event metadata
