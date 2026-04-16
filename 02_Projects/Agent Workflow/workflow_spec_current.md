---
title: Agent Workflow Spec Current
summary: Agent Workflow 当前项目化管理规范，明确 current / modification records / writeback / recoverability / Chaospower active truth source 的执行规则。
status: verified
doc_role: current
truth_role: current
current_kind: spec
lifecycle_state: active
default_entry: false
sync_required_when:
  - modification-record 规则变化
  - writeback 门禁变化
  - recoverability 判定变化
retrieval_priority: current
supersedes: []
merged_into: []
current_replacement: []
related_code: []
related_plugins:
  - plugins/chaospower
sources:
  - 01_Knowledge/Agent Workflow/Agent驱动知识库、代码库与板端侧协同闭环规范.md
  - 01_Knowledge/Agent Workflow/Agent三侧运行规范与调度模板.md
  - 01_Knowledge/Agent Workflow/Agent三侧模板与文件结构规范.md
  - plugins/chaospower/docs/Chaospower active contract index.md
scope: 适用于 Agent Workflow 自身演化的项目化 writeback 与记录收敛。
risks:
  - Chaospower P0 当前只覆盖 plan / repo-change / code-review / writeback，不覆盖板端和联网。
updated_at: 2026-04-15
---

## 0.1 Required Behaviors

- 若规则变化影响当前态语义，必须更新 current
- 若发生具体收敛、诊断、审计或验证事件，必须创建或更新 modification record
- modification record 必须声明 `record_type` 与 `target_current_docs`
- `delta_only` 只允许用于纯证据或纯追溯补充
- 高风险动作必须遵守正式规范中的默认 deny、核心门禁状态与 writeback 分层
- `project_log_write / project_current_update / knowledge_promotion` 必须按风险分层执行，不得混用一个 writeback gate
- Chaospower 运行时规则必须优先读取 `plugins/chaospower/skills/` 的 active skill
- `AGENTS.md` 只允许承载极薄入口和全局 hard stop
- `agents/*.toml` 只允许承载 description 与调用对应 skill 的薄 prompt
- legacy 文档、appendices 与 migration payload 不得覆盖 active skill

## 0.2 Prohibited Behaviors

- 不允许 current 承载事件时间线
- 不允许 modification record 复制代码、配置或 patch 细节
- 不允许 active delta 长期滞留
- 不允许把 P1/P2 未落地能力创建为空 skill 目录充当 active 规则
- 不允许把 `using-chaospower` 扩写成完整旧状态机或角色契约全文

## 0.3 Verification Contract

- current 是否仍能 single-pass recover
- modification record 是否说明动机、边界、验证与残余风险
- target current docs 是否明确

## 0.4 Writeback Contract

- 先更新知识规范
- 再更新本主题 project current
- 再将实例主题按更新后规则收敛

## 0.5 Latest Governance Update

- `主代理越权执行规范硬化优化记录-2026-04-15.md` 已通过独立 review 并提升到正式规范
- 本轮正式规范新增：
  - 高风险动作默认 deny
  - `verification_write / verification_read` 分界
  - 四核心门禁状态
  - 违规分级、冻结范围与恢复责任
  - writeback 三层：`project_log_write / project_current_update / knowledge_promotion`
- `Chaospower P0 skill-first 第一阶段落地收敛记录-2026-04-15.md` 将第一阶段运行时规则收敛到 `plugins/chaospower`
- P0 active skill 集固定为：
  - `using-chaospower`
  - `chaos-scope-plan`
  - `chaos-repo-change`
  - `chaos-code-review`
  - `chaos-writeback`

## 0.6 Active Truth Source Priority

优先级从高到低：

1. `plugins/chaospower/skills/`
2. `plugins/chaospower/docs/Chaospower active contract index.md`
3. `plugins/chaospower/AGENTS.md`
4. `plugins/chaospower/agents/*.toml`
5. `plugins/chaospower/docs/appendices/` 与 `01_Knowledge/Agent Workflow` legacy 规范
6. `plugins/agent-workflow-migrator` payload

若 active skill 与低优先级载体冲突，以 active skill 为准。
