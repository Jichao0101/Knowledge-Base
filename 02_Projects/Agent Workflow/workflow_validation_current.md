---
title: Agent Workflow Validation Current
summary: 当前 cutepower 已完成 explicit runtime lock、repo-local run artifact hardening、phase/capability 强约束、宿主 host bridge 与 Codex hooks completion gate；本文件记录已验证边界、未闭环项与下一轮验证重点。
status: pending_review
doc_role: current
truth_role: current
current_kind: validation
lifecycle_state: active
default_entry: false
sync_required_when:
  - validation 结论变化
  - 运行时门禁、宿主 hook 或安装接入覆盖面变化
  - 隔离测试、安装发现链路或真实会话结果变化
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
  - /mnt/d/cutepower/scripts/codex-hooks.js
  - /mnt/d/cutepower/scripts/runtime-gates.js
  - /mnt/d/cutepower/scripts/run-artifacts.js
  - /mnt/d/cutepower/scripts/install-plugin.js
  - /mnt/d/cutepower/scripts/test-task-profile.js
  - /mnt/d/cutepower/scripts/test-task-intake.js
  - /mnt/d/cutepower/scripts/test-host-runtime.js
  - /mnt/d/cutepower/scripts/test-codex-hooks.js
  - /mnt/d/cutepower/scripts/test-runtime-gates.js
  - /mnt/d/cutepower/scripts/test-install-plugin.js
  - /mnt/d/cutepower/README.md
  - /mnt/d/cutepower/docs/runtime-hardening.md
  - 02_Projects/Agent Workflow/cutepower runtime hardening闭环工件与phase强制记录-2026-04-22.md
scope: 适用于判断当前 cutepower 哪些边界已被验证，尤其是 explicit mode、repo-local run-state、host hook 与 completion gate 相关能力。
risks:
  - 若把当前 hook 自测当作完整宿主运行器验收，会高估当前成熟度。
updated_at: 2026-04-22
---

## 0.1 Validated

- cutepower 的 active governance 已收敛到 plugin contracts
- explicit mode 已具备 runtime lock：
  - 未 intake 前禁止 `business_context_read`
  - 未 route resolved 前禁止 `repo_write` / `repo-change`
  - runtime discovery 读取不会误判为业务读取
  - unmapped tool event 已从 warn 收紧为 deny
- runtime gate 已前置到动作前：
  - 读业务代码/知识
  - repo write
  - board action
  - review decision
  - writeback
- repo-local run-state 已落地：
  - `task_profile`、`route_resolution`、`runtime_gate`、`context_requirements`、`blocking_gaps` 已落盘为稳定 artifact
  - `evidence_manifest`、`review_decision`、`writeback_receipt|writeback_declined` 已进入闭环 artifact 集
  - `runtime-gates` 已检查 artifact existence 与 schema
- phase 与 capability 已进入执行约束：
  - protected business action / review / writeback 缺 capability 时拒绝
  - phase 不匹配时拒绝
  - preflight artifact 缺失时拒绝
- review 独立性已被执行期校验：
  - author 自检不能当独立 review
  - 缺 reviewer stage / instance 时 review fail/block
- writeback 生效独立性已被执行期校验：
  - 缺 required passes / preconditions 时拒绝
  - `project_current_update` 比 `project_log_write` 更严格
  - author 不能单方触发 current update
- `host-runtime.js` 已能生成：
  - `session_context` 摘要
  - `artifact_plan`
  - `action_guard`
  - `session_capability`
- `codex-hooks.js` 已能接到 Codex lifecycle：
  - `UserPromptSubmit`
  - `PreToolUse`
  - `Stop`
  - `Stop` 已变成 completion gate，而不是 summary-only
- 安装脚本已能把 hooks 接到安装目标环境：
  - personal：`~/.codex/`
  - repo：`<target-root>/.codex/`
- 安装脚本已验证：
  - 保留用户已有 config 值
  - 保留无关 hooks
  - 重复安装不重复注入 cutepower hooks

## 0.2 Covered By Automated Tests

- `node scripts/validate-contracts.js`
- `node scripts/test-task-profile.js`
- `node scripts/test-task-intake.js`
- `node scripts/test-runtime-gates.js`
- `node scripts/test-host-runtime.js`
- `node scripts/test-codex-hooks.js`
- `node scripts/test-install-plugin.js`

## 0.3 Not Yet Closed

- 还未完成一次真实 Codex 会话中的 hooks 发现、hook 触发与端到端任务执行验收
- `PreToolUse` 对纯通用工具事件仍是启发式映射，不能保证对所有 review/writeback 语义做到无损识别
- 当前 current 组尚未经过独立 review

## 0.4 Current Review Target

下一轮 reviewer 应重点检查：

- repo-local run-state 与 `schemas/run-artifacts/` 是否只承接执行闭环，而没有复制 contracts 规则正文
- `codex-hooks.js` 是否只做桥接，没有引入与 `task-intake` / `runtime-gates` 冲突的第二套规则
- 当前 current 组是否已同步 capability、phase、artifact 与 completion gate 的边界
- 记录文档是否清楚区分“已在插件内解决”和“仍需宿主运行器配合”的部分

## 0.5 Next Verification

- 在真实 Codex 会话中做一次 explicit mode 任务，确认：
  - `UserPromptSubmit` 先触发
  - `PreToolUse` 在业务读取前拦截
  - `Stop` 在缺闭环 artifacts 时拒绝完成
  - `declined`、`blocked`、`clarification_required` 的 fallback 行为符合预期
- 再执行一次 implementation / bug_fix 主链，验证 intake、route、review、writeback、artifact write 与 hooks 的联动结果
- 若后续宿主能提供更结构化的 tool event metadata，再验证 review/writeback 的 hook 映射是否可以从启发式升级为结构化判定
