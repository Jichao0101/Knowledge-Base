---
title: cutepower 宿主hooks硬门禁与host-adapter拆分记录
summary: 记录 cutepower 在 2026-04-23 完成的最小可落地架构重构：拆出宿主协议适配层、引入统一内部治理裁决对象、把 UserPromptSubmit 和 PreToolUse 收紧为 hard-stop，并让 Stop 只能在合法闭环下 completed。
status: pending_review
doc_role: modification_record
record_type: implementation_record
truth_role: evidence
lifecycle_state: pending_merge
default_entry: false
retrieval_priority: evidence_only
target_current_docs:
  - 02_Projects/cutepower/cutepower_interface_current.md
  - 02_Projects/cutepower/cutepower_implementation_current.md
  - 02_Projects/cutepower/cutepower_validation_current.md
related_plugins:
  - cutepower
sources:
  - /mnt/d/cutepower/contracts/task-normalization.yaml
  - /mnt/d/cutepower/contracts/gate-matrix.yaml
  - /mnt/d/cutepower/scripts/task-intake.js
  - /mnt/d/cutepower/scripts/host-runtime.js
  - /mnt/d/cutepower/scripts/runtime-gates.js
  - /mnt/d/cutepower/scripts/hook-response.js
  - /mnt/d/cutepower/scripts/codex-host-adapter.js
  - /mnt/d/cutepower/scripts/codex-hooks.js
  - /mnt/d/cutepower/scripts/test-task-intake.js
  - /mnt/d/cutepower/scripts/test-host-runtime.js
  - /mnt/d/cutepower/scripts/test-runtime-gates.js
  - /mnt/d/cutepower/scripts/test-codex-hooks.js
  - /mnt/d/cutepower/scripts/test-uninstall-plugin.js
  - /mnt/d/cutepower/README.md
  - /mnt/d/cutepower/docs/runtime-hardening.md
scope: 适用于追溯本轮最小架构重构：host adapter 拆分、统一治理裁决对象、hard-stop 门禁、artifact 准入条件、Stop completed 闭环条件。
risks:
  - tool event 语义识别仍然是启发式，不是宿主结构化动作模型。
  - Stop 目前仍是最小闭环校验，functional review 相关 requirements/context artifact 还没有进一步细分强制。
updated_at: 2026-04-23
---

# 1 cutepower 宿主hooks硬门禁与host-adapter拆分记录

## 1.1 本轮问题定义

本轮要解决的不是再补一层提示，而是把 cutepower 的前门做成代码路径上的硬约束。

改造前的主要失配有三类：

- `codex-hooks.js` 同时承担 stdin/stdout、宿主协议映射、动作推断、治理门禁与 stop 收尾，宿主兼容问题会直接拖垮治理语义。
- `UserPromptSubmit` 和 `PreToolUse` 虽然有 gate 判断，但失败状态和宿主 `decision/status` 没有被一个统一内部对象约束，导致 hook fail 后仍可能退化成继续执行。
- `.cutepower/run/<session_id>/` 的 preflight artifacts 只在 README 里是“应存在”，代码里并没有被严格当成进入下游阶段的硬前置条件。

## 1.2 主要实现

### 1.2.1 宿主适配层拆分

- 新增 `scripts/codex-host-adapter.js`
- 该文件职责收敛为：
  - 读取 stdin
  - 解析 hook event / payload
  - 调用内部治理逻辑
  - 将内部治理裁决映射成宿主兼容 JSON
  - 将详细异常写 stderr
  - 保证 stdout 只输出一个合法 JSON 对象
- `scripts/codex-hooks.js` 退化成 CLI 壳，只负责调用 adapter

### 1.2.2 统一内部治理裁决对象

- `scripts/hook-response.js` 新增内部治理裁决对象构造与宿主映射函数
- 统一字段包括：
  - `gate_result`
  - `stage`
  - `allowed_to_continue`
  - `reason`
  - `missing_artifacts`
  - `required_artifacts`
  - `allowed_actions`
  - `diagnostics`
- `task-intake`、`runtime-gates`、`Stop` 校验都先产出内部裁决，再由 adapter 映射到宿主 `decision/status`

### 1.2.3 preflight artifact 变成真实准入条件

- `task-intake.js` 现在会为显式接管会话分配 `session_id` 并把以下最小集合写到 `.cutepower/run/<session_id>/`：
  - `task_profile.json`
  - `route_resolution.json`
  - `runtime_gate.json`
- 这些文件写不出来或缺失时，`UserPromptSubmit` 直接 hard-stop，不再返回看起来可继续的 capability

### 1.2.4 capability 与 PreToolUse hard-stop

- `host-runtime.js` 现在负责：
  - 读取持久化的 `runtime_gate.json`
  - 构建 host runtime 视图
  - 只在 ready 且 managed 的 session 上签发 `session_capability`
  - 校验 capability 与 session/route/capability 是否绑定一致
- `runtime-gates.js` 现在在 `PreToolUse` 上强制：
  - 缺 capability 直接 deny
  - 缺 `task_profile` / `route_resolution` / `runtime_gate` 直接 deny
  - `runtime_gate_status != ready` 直接 deny/decline
  - unmapped 低风险只允许 not_applicable；unmapped 高风险执行直接 deny

### 1.2.5 Stop completed 收紧

- `Stop` 不再尝试掩盖前面阶段的失败
- 只有以下合法闭环条件满足时才返回 `completed`：
  - preflight artifacts 完整
  - `evidence_manifest`
  - `review_decision`
  - `writeback_receipt` 或 `writeback_declined`
  - `terminal_phase` 合法
- 对 blocked terminal state 仍允许合法完成，但必须是明确的 blocked closure 组合
- 前置失败或 closure artifact 不全时，只能 `skipped`，不会伪装成 `completed`

## 1.3 验证覆盖

已执行：

- `node scripts/test-task-intake.js`
- `node scripts/test-host-runtime.js`
- `node scripts/test-runtime-gates.js`
- `node scripts/test-codex-hooks.js`
- `node scripts/test-uninstall-plugin.js`

覆盖重点：

- `UserPromptSubmit` 失败后不会签发 capability，后续 `PreToolUse` 同 session 被明确拒绝
- 缺 `runtime_gate.json` 时不能进入下游 tool 阶段
- 高风险 unmapped tool event 不再 pass-through
- `Stop` 在缺 `review_decision` 或其他 closure artifact 时不能 completed
- uninstall 后 cutepower 自己注入的 hooks 确实从配置中移除，且不误删其他 hooks

## 1.4 当前边界

- contracts 仍然是治理真相源；本记录只描述实现修改，不复制 contracts 正文。
- `functional review` 所需 requirements package / evidence context 目前还没有在 runtime gate 里扩成更细的强制 artifact 集。
- tool action 分类仍是启发式实现；如果宿主后续提供更结构化的 tool metadata，仍建议把风险判定从命令字符串规则升级过去。
