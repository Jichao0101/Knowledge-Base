---
title: Agent Workflow Interface Current
summary: 当前 cutepower 的最小启动入口说明。采用类 superpower 模式，用户只提供任务事实与边界，是否启用 cutepower 以及启用哪些 skills 由 agent 自行判断。
status: pending_review
doc_role: current
truth_role: current
current_kind: interface
lifecycle_state: active
default_entry: false
sync_required_when:
  - cutepower 启动方式变化
  - 最小提示词字段变化
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
  - /mnt/d/cutepower/skills/using-cutepower/SKILL.md
  - /mnt/d/cutepower/skills/cute-scope-plan/SKILL.md
  - /mnt/d/cutepower/contracts/routing-table.yaml
  - /mnt/d/cutepower/contracts/gate-matrix.yaml
  - 02_Projects/Agent Workflow/workflow_overview_current.md
scope: 适用于在当前项目中以最小提示词方式启动 cutepower 或让 agent 自行决定是否启用 cutepower，不覆盖 plugin contracts 本身。
risks:
  - 若把此模板写成固定执行链，会偏离当前类 superpower 模式。
  - 若缺少 allowed_paths、repo_scope 或 board_target 等事实字段，agent 可能误判是否启用 cutepower。
updated_at: 2026-04-17
---

## 0.1 Purpose

当前 cutepower 的入口模式不是“用户预编排固定 skill chain”，而是：

- 用户提供任务目标、路径、板端目标和边界
- agent 自行判断是否需要启用 cutepower
- 若启用，再由 agent 自行决定使用哪些 cutepower skills

因此入口提示词应尽量短，只提供事实与约束，不固定执行模式。

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

## 0.3 Usage Rule

- 默认不强制启动 cutepower
- agent 应根据 skill description、contracts 与任务事实自行判断是否启用 cutepower
- 若启用，不预设固定 skill chain
- 一旦启用，仍需遵守 cutepower contracts 与 runtime gates

## 0.4 Optional Force-use Variant

只有在你明确要求“本任务必须使用 cutepower”时，才额外补一句：

```text
本任务应使用 cutepower 处理。
```

除此之外，不需要再补“执行要求”段落。

## 0.5 Field Notes

- `knowledge_paths`
  - 只在任务确实需要读知识时提供
- `project_paths`
  - 当前项目工作区路径
- `repo_root`
  - 代码仓根目录
- `repo_scope`
  - 本轮允许修改的代码范围；只读任务写 `none`
- `board_target`
  - 需要板端执行时给出；否则写 `no_board_execution`
- `allowed_paths`
  - 这是本轮最关键的边界输入

## 0.6 Non-goals

- 不在提示词里写固定 route
- 不在提示词里写固定 role chain
- 不把 README、baseline 或 project current 当作高于 contracts 的规则源
- 不把宿主知识库目录语义写回 cutepower plugin
