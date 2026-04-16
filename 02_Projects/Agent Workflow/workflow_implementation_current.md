---
title: Agent Workflow Implementation Current
summary: Agent Workflow 当前规则在知识规范、项目文档与 Chaospower 插件中的落点映射。
status: verified
doc_role: current
truth_role: current
current_kind: implementation
lifecycle_state: active
default_entry: false
sync_required_when:
  - 规范落点变化
  - 项目 current 组变化
retrieval_priority: current
supersedes: []
merged_into: []
current_replacement: []
related_code: []
related_plugins:
  - plugins/chaospower
  - plugins/agent-workflow-migrator
sources:
  - 01_Knowledge/Agent Workflow/Agent驱动知识库、代码库与板端侧协同闭环规范.md
  - 01_Knowledge/Agent Workflow/Agent三侧运行规范与调度模板.md
  - 01_Knowledge/Agent Workflow/Agent三侧模板与文件结构规范.md
  - plugins/chaospower/docs/Chaospower active contract index.md
scope: 适用于快速定位 Agent Workflow 当前规则写在哪些文档里。
risks:
  - 当前 Chaospower 插件已有 P0 skill，但仍没有脚本化 lint 或完整插件安装校验器。
updated_at: 2026-04-15
---

## 0.1 Knowledge-side Mapping

- 上位规则：`Agent驱动知识库、代码库与板端侧协同闭环规范`
- 运行门禁：`Agent三侧运行规范与调度模板`
- 模板与字段：`Agent三侧模板与文件结构规范`
- 上述文档在 Chaospower P0 运行时中降级为解释性依据与 legacy reference，不覆盖 active skill

## 0.1A Plugin-side Mapping

- 插件根目录：`plugins/chaospower`
- 插件 manifest：`plugins/chaospower/.codex-plugin/plugin.json`
- 极薄入口：`plugins/chaospower/AGENTS.md`
- active truth source：`plugins/chaospower/docs/Chaospower active contract index.md`
- P0 skills：
  - `plugins/chaospower/skills/using-chaospower/SKILL.md`
  - `plugins/chaospower/skills/chaos-scope-plan/SKILL.md`
  - `plugins/chaospower/skills/chaos-repo-change/SKILL.md`
  - `plugins/chaospower/skills/chaos-code-review/SKILL.md`
  - `plugins/chaospower/skills/chaos-writeback/SKILL.md`
- thin agent descriptors：
  - `plugins/chaospower/agents/scope-plan.toml`
  - `plugins/chaospower/agents/repo-change.toml`
  - `plugins/chaospower/agents/code-review.toml`
  - `plugins/chaospower/agents/writeback.toml`
- migration-only plugin：`plugins/agent-workflow-migrator`

## 0.2 Project-side Mapping

- 默认入口：`workflow_overview_current`
- 当前分工：`workflow_design_current`
- 当前强规则：`workflow_spec_current`
- 落点映射：`workflow_implementation_current`
- 当前验证：`workflow_validation_current`

## 0.3 Modification Records

- `Agent Workflow-current与修改记录分工收敛记录-2026-04-13.md`
- `Agent Workflow-DMS Tracking 文档体系诊断记录-2026-04-13.md`
- `Chaospower P0 skill-first 第一阶段落地收敛记录-2026-04-15.md`
