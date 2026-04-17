---
title: Agent Workflow Spec Current
summary: 当前 Agent Workflow 主题的项目级强规则：cutepower plugin 是唯一 active truth，project current 只做同步说明，baseline 与 record 只做历史追溯。
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
  - plugins/cutepower
sources:
  - plugins/cutepower/contracts/contract-index.yaml
  - plugins/cutepower/contracts/writeback-levels.yaml
  - plugins/cutepower/contracts/review-boundaries.yaml
  - plugins/cutepower/scripts/runtime-gates.js
  - 01_Knowledge/Agent Workflow/Plugin-first与Contracts-first治理插件设计模式.md
  - 01_Knowledge/Agent Workflow/运行时门禁与独立审查边界模式.md
scope: 适用于定义 cutepower 当前项目区同步规则、真相源优先级与禁止行为，不替代 plugin contracts 本身。
risks:
  - 若 project spec 与 plugin contracts 发生漂移，会再次形成两套治理语义。
  - 若 record 被当成当前规则源，会破坏 single-pass recoverability。
updated_at: 2026-04-17
---

## 0.1 Required Behaviors

- cutepower 的运行治理必须优先读取 `plugins/cutepower/contracts/`
- 运行时高风险拒绝路径必须以 `plugins/cutepower/scripts/runtime-gates.js` 为准
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

- cutepower 已完成 P1 contracts、schemas、validation 与三项 P1 skills 落地
- runtime gate 已覆盖 legacy reviewer、review 态 board_execute、非 board route artifact_collect、incident repo_write、模糊 pass 状态等关键拒绝路径
- cutepower 已去除宿主知识库目录语义，不再携带 `01_Knowledge / 02_Projects / 03_Inbox` 绑定
- 项目区已移除原三侧与 Chaospower 记录，仅保留 cutepower assets

## 0.6 Active Truth Source Priority

优先级从高到低：

1. `plugins/cutepower/contracts/`
2. `plugins/cutepower/scripts/runtime-gates.js`
3. `plugins/cutepower/skills/`
4. `plugins/cutepower/README.md`、`AGENTS.md`、`agents/*.toml`
5. `02_Projects/Agent Workflow/workflow_*_current.md`
6. `02_Projects/Agent Workflow/cutepower_*_baseline.md`
7. `02_Projects/Agent Workflow/cutepower P1插件落地与运行时门禁收敛记录-2026-04-17.md`
8. `01_Knowledge/Agent Workflow/*.md` 通用模式知识

若高优先级与低优先级冲突，以高优先级为准。
