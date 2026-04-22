---
title: Agent Workflow Interface Current
summary: 当前 cutepower 的入口说明。显式模式下，宿主 hooks 应先跑 host bridge，落盘 preflight artifacts，签发 session capability，再由 runtime gate 决定后续动作是否放行。
status: pending_review
doc_role: current
truth_role: current
current_kind: interface
lifecycle_state: active
default_entry: false
sync_required_when:
  - cutepower 启动方式变化
  - 宿主 hook 接入方式变化
  - 强制启用与自判断启用边界变化
retrieval_priority: current
supersedes: []
merged_into: []
current_replacement: []
related_code: []
related_plugins:
  - cutepower
sources:
  - /mnt/d/cutepower/README.md
  - /mnt/d/cutepower/docs/runtime-hardening.md
  - /mnt/d/cutepower/README.codex.md
  - /mnt/d/cutepower/.codex-plugin/plugin.json
  - /mnt/d/cutepower/agents/openai.yaml
  - /mnt/d/cutepower/skills/using-cutepower/SKILL.md
  - /mnt/d/cutepower/scripts/task-intake.js
  - /mnt/d/cutepower/scripts/host-runtime.js
  - /mnt/d/cutepower/scripts/codex-hooks.js
  - /mnt/d/cutepower/scripts/install-plugin.js
  - /mnt/d/cutepower/scripts/run-artifacts.js
  - /mnt/d/cutepower/contracts/routing-table.yaml
  - /mnt/d/cutepower/contracts/gate-matrix.yaml
  - 02_Projects/Agent Workflow/workflow_overview_current.md
scope: 适用于说明当前 cutepower 如何被宿主显式启用，以及默认入口与强制入口之间的边界。
risks:
  - 若把 hooks 接入误解为 repo 开发仓库配置，会偏离当前安装目标接入模式。
  - 若缺少 allowed_paths、repo_scope、board_target 或 reviewer/adjudication 身份，runtime 仍可能返回 blocked/clarification_required。
updated_at: 2026-04-22
---

## 0.1 Purpose

当前 cutepower 的入口已经分成两层：

- 默认层：工程任务默认先尝试走 cutepower intake
- 显式层：当用户明确要求“按 cutepower 执行”时，宿主 hooks 应先跑 cutepower host bridge，再把后续工具动作送到 runtime gate 做前置准入

因此入口模式不再只是“最小提示词提醒”，而是：

- 显式模式先 `UserPromptSubmit`
- 生成 `session_id`、`artifact_plan`、`session_context`
- 签发 `session_capability`
- 再由 `PreToolUse` 判断业务读取、repo-change、review、writeback 是否可执行
- `Stop` 检查是否合法终态以及闭环 artifacts 是否齐备

## 0.2 Default Prompt Template

```text
任务目标：
<一句话说明要做什么>

任务上下文：
- knowledge_paths:
  - <可读知识路径，可省略>
- project_paths:
  - <可读写项目路径>
- repo_root:
  - <代码仓路径；无则写 none>
- repo_scope:
  - <允许修改范围；只读任务写 none>
- board_target:
  - <板端目标；无则写 no_board_execution>

任务约束：
- allowed_paths:
  - <本轮允许访问路径>
- verification_tier:
  - <V0 | V1 | strict>
- non_goals:
  - <明确不做什么>
```

## 0.3 Explicit Cutepower Variant

当任务必须显式进入 cutepower 时，可以补一句：

```text
本任务按 cutepower 执行。
```

显式模式下，宿主应通过已安装的 `hooks.json` 触发：

- `UserPromptSubmit`
  - 调 `scripts/codex-hooks.js user-prompt-submit`
  - 再由其调用 `host-runtime.js`
- `PreToolUse`
  - 调 `scripts/codex-hooks.js pre-tool-use`
  - 再由其调用 `runtime-gates.js`
- `Stop`
  - 作为 completion gate，而不只是 summary

## 0.4 Usage Rule

- 对 `implementation`、`bug_fix`、`incident_investigation`、`audit` 类任务，默认入口应先尝试 cutepower intake
- 显式模式下：
  - `task_profile`、`route_resolution`、`runtime_gate`、`context_requirements`、`blocking_gaps` 会先落为 repo-local artifacts
  - `task_profile`、`route_resolution`、`runtime_gate` 未 ready 前，不应直接跳过到业务代码读取、repo 改码、review 或 writeback
  - 受保护动作必须依赖 capability + phase + artifact
  - 只有 `declined` 才允许退回普通直接执行
  - `clarification_required`、`blocked`、missing context 不得静默绕过
- review 独立性要求：
  - author 自检不算独立 review
  - 缺 reviewer stage / instance 时 review 不通过
- writeback 生效要求：
  - `project_current_update` 不能由 author 单方生效
  - 必须有 pass + gate + preconditions + 非 author adjudication

## 0.5 Host Integration Note

当前正式做法是：

- 由安装脚本把 cutepower hooks 合并到目标环境的 `.codex/config.toml` 与 `.codex/hooks.json`
- 不再把开发仓库自身当作正式 hooks 接入点
- 若宿主运行器忽略这些目标 hooks 配置，cutepower 仍会退回为“插件内强约束”，无法成为真正宿主级绝对前门

## 0.6 Non-goals

- 不在提示词里写固定 route
- 不在提示词里写固定 role chain
- 不把 README、baseline 或 project current 当作高于 contracts 的规则源
- 不把开发仓库 repo 自身的 `.codex/hooks.json` 当成正式 runtime 入口
