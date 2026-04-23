---
title: cutepower 宿主hooks接入与安装目标注入记录
summary: 记录 cutepower 在 2026-04-22 完成的 explicit runtime lock、review/writeback 强约束、host bridge、Codex lifecycle hooks 接入，以及 hooks 从开发仓库迁移到安装目标环境的实现与边界。
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
  - /mnt/d/cutepower/contracts/role-contracts.yaml
  - /mnt/d/cutepower/contracts/review-boundaries.yaml
  - /mnt/d/cutepower/contracts/writeback-levels.yaml
  - /mnt/d/cutepower/.codex-plugin/plugin.json
  - /mnt/d/cutepower/agents/openai.yaml
  - /mnt/d/cutepower/scripts/task-intake.js
  - /mnt/d/cutepower/scripts/runtime-gates.js
  - /mnt/d/cutepower/scripts/host-runtime.js
  - /mnt/d/cutepower/scripts/codex-hooks.js
  - /mnt/d/cutepower/scripts/install-plugin.js
  - /mnt/d/cutepower/scripts/test-task-intake.js
  - /mnt/d/cutepower/scripts/test-runtime-gates.js
  - /mnt/d/cutepower/scripts/test-host-runtime.js
  - /mnt/d/cutepower/scripts/test-codex-hooks.js
  - /mnt/d/cutepower/scripts/test-install-plugin.js
scope: 适用于追溯本轮完整修改：显式 cutepower 模式运行时锁、宿主 host bridge、Codex hooks 接入，以及 install-target hooks merge 行为。
risks:
  - 当前实现仍依赖宿主实际启用并执行目标环境的 hooks 配置。
  - PreToolUse 对纯通用工具事件仍存在启发式映射边界。
updated_at: 2026-04-22
---

# 1 cutepower 宿主hooks接入与安装目标注入记录

## 1.1 本轮问题定义

本轮要解决的不是 cutepower 完全缺少规则，而是两层缺口：

- 第一层：即使已有 contracts、intake、runtime gates，显式“按 cutepower 执行”时仍可能先读业务代码、先改 repo、先自检再补说明。
- 第二层：即使插件内规则已经加固，如果宿主 runtime 不先调用 hook、不注入前门上下文、不在动作前调用 runtime-gates，agent 仍能绕过 cutepower 正式链路。

因此本轮目标分成两段：

- 先把 explicit mode 收成插件内的强运行时闭环
- 再把宿主 hooks 接入补到正式安装目标环境，而不是开发仓库 repo 本身

## 1.2 插件内运行时加固

### 1.2.1 explicit mode runtime lock

- `task-normalization.yaml` 增加：
  - `explicit_mode_keywords`
  - `pre_intake_allowed_actions`
  - `protected_actions_before_ready`
- `task-intake.js` 增加：
  - `execution_mode`
  - `runtime_lock`
- `runtime-gates.js` 增加：
  - explicit mode 前置锁
  - 未 ready 前只允许 `runtime_discovery_read`
  - 拒绝 `business_context_read`、`repo_write`、`board_execute`、`review_decision`、writeback 相关动作与受保护 skill

### 1.2.2 review 独立性

- `review-boundaries.yaml` 增加：
  - `author_self_review_forbidden`
  - `require_explicit_reviewer_identity`
- `runtime-gates.js` 执行期强校验：
  - reviewer stage / instance 必须显式存在
  - author 与 reviewer 不能同实例
  - 不允许 full author context / reasoning 继承
  - 最小证据包必须齐全

### 1.2.3 writeback 生效独立性

- `writeback-levels.yaml` 把 `project_current_update` 收紧为：
  - `writeback_state_reached`
  - `route_writeback_requirements_satisfied`
  - `independent_writeback_adjudication`
  - route 级 `review_pass_recorded`
- `runtime-gates.js` 要求：
  - `actor_role_id`
  - `completed_preconditions`
  - `project_current_update` 必须有 `adjudicator_instance_id`
  - adjudicator 不能等于 author

## 1.3 宿主桥接与 lifecycle hooks

### 1.3.1 host bridge

- 新增 `scripts/host-runtime.js`
- 显式模式下先跑 intake，再产出：
  - `session_context` 摘要
  - `required_preflight_outputs`
  - `action_guard`
- 这份 `action_guard` 后续供动作前 gate 复用，避免“session 前门”和“动作 gate”变成两套真相

### 1.3.2 Codex hooks wrapper

- 新增 `scripts/codex-hooks.js`
- 事件映射：
  - `UserPromptSubmit`
    - 调 `host-runtime.js`
    - 识别 explicit mode
    - 记录 warning 与 required outputs
  - `PreToolUse`
    - 调 `runtime-gates.js`
    - 对业务读取 / repo write / review / writeback 做动作前准入
  - `Stop`
    - 汇总 denied / unmapped 事件
- hook state 不写 `.codex/`，而按 workspace 写入 `/tmp`，避免写配置目录时被权限卡住

## 1.4 hooks 接入位置修正

### 1.4.1 被修正掉的错误思路

中途一度在开发仓库 `/mnt/d/cutepower` 下生成了 repo-level `.codex/config.toml` 与 `.codex/hooks.json`，但这个方向不对。

原因：

- hooks 的正式生效位置应该是“其他用户安装插件后的目标环境”
- 开发仓库本身只是开发内容，不应充当所有宿主 runtime 的正式 hook 配置载体

### 1.4.2 最终实现

- 删除开发仓库 repo 自身的 hooks 配置
- `scripts/install-plugin.js` 负责把 hooks merge 到安装目标：
  - personal install：`~/.codex/config.toml`、`~/.codex/hooks.json`
  - repo install：`<target-root>/.codex/config.toml`、`<target-root>/.codex/hooks.json`
- 安装脚本会：
  - 启用 `codex_hooks = true`
  - 合并 cutepower 的 `UserPromptSubmit` / `PreToolUse` / `Stop`
  - 让 command 指向安装后的 `plugins/cutepower/scripts/codex-hooks.js`
  - 保留用户已有 config 与无关 hooks
  - 重复安装时不重复追加 cutepower hooks

## 1.5 已完成验证

- `node scripts/validate-contracts.js`
- `node scripts/test-task-intake.js`
- `node scripts/test-runtime-gates.js`
- `node scripts/test-host-runtime.js`
- `node scripts/test-codex-hooks.js`
- `node scripts/test-install-plugin.js`

覆盖到的重点包括：

- explicit mode 未 intake 前不允许业务读取
- 未 route resolved 前不允许 repo-change
- blocked / clarification_required 不得静默 fallback
- runtime discovery 不误判为业务读取
- author 自检不能当独立 review
- 缺 reviewer stage / instance 时 review fail
- writeback 缺 passes / preconditions 时拒绝
- `project_log_write` 与 `project_current_update` 约束差异有效
- 安装目标会得到正式 hooks/config 接入
- 安装会保留已有 hooks/config，且重复安装不重复注入

## 1.6 当前仍未闭环项

- 仍需一次真实 Codex 会话中的 hooks 发现与端到端任务执行验收
- `PreToolUse` 对纯通用工具事件仍是启发式映射，尚未做到对所有 review/writeback 语义的结构化识别
- 因此当前结论应表达为：
  - 插件内强约束闭环已完成
  - 宿主 hooks 接入路径已完成
  - 是否达到“绝对不可绕过”仍取决于宿主运行器实际执行目标环境的 hooks，并提供足够结构化的 tool event metadata
