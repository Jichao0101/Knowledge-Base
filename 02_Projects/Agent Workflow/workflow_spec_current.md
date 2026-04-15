---
title: Agent Workflow Spec Current
summary: Agent Workflow 当前项目化管理规范，明确 current / modification records / writeback / recoverability 的执行规则。
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
sources:
  - 01_Knowledge/Agent Workflow/Agent驱动知识库、代码库与板端侧协同闭环规范.md
  - 01_Knowledge/Agent Workflow/Agent三侧运行规范与调度模板.md
  - 01_Knowledge/Agent Workflow/Agent三侧模板与文件结构规范.md
scope: 适用于 Agent Workflow 自身演化的项目化 writeback 与记录收敛。
risks:
  - 本规范当前只覆盖知识库内项目文档，不扩展到外部代码库主题。
updated_at: 2026-04-15
---

## 0.1 Required Behaviors

- 若规则变化影响当前态语义，必须更新 current
- 若发生具体收敛、诊断、审计或验证事件，必须创建或更新 modification record
- modification record 必须声明 `record_type` 与 `target_current_docs`
- `delta_only` 只允许用于纯证据或纯追溯补充
- 高风险动作必须遵守正式规范中的默认 deny、核心门禁状态与 writeback 分层
- `project_log_write / project_current_update / knowledge_promotion` 必须按风险分层执行，不得混用一个 writeback gate

## 0.2 Prohibited Behaviors

- 不允许 current 承载事件时间线
- 不允许 modification record 复制代码、配置或 patch 细节
- 不允许 active delta 长期滞留

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
