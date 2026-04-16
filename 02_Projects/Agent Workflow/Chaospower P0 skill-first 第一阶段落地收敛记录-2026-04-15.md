---
title: Chaospower P0 skill-first 第一阶段落地收敛记录
summary: 将 Chaospower 压缩方案收敛为第一阶段最小可落地插件结构，只保留 using-chaospower、scope-plan、repo-change、code-review、writeback 五个 P0 skill，并更新 Agent Workflow current 组。
status: verified
doc_role: modification_record
record_type: implementation_record
truth_role: evidence
lifecycle_state: pending_merge
default_entry: false
retrieval_priority: evidence_only
target_current_docs:
  - 02_Projects/Agent Workflow/workflow_overview_current.md
  - 02_Projects/Agent Workflow/workflow_design_current.md
  - 02_Projects/Agent Workflow/workflow_spec_current.md
  - 02_Projects/Agent Workflow/workflow_implementation_current.md
  - 02_Projects/Agent Workflow/workflow_validation_current.md
related_plugins:
  - plugins/chaospower
sources:
  - plugins/chaospower/AGENTS.md
  - plugins/chaospower/README.md
  - plugins/chaospower/docs/Chaospower active contract index.md
  - plugins/chaospower/skills/using-chaospower/SKILL.md
  - plugins/chaospower/skills/chaos-scope-plan/SKILL.md
  - plugins/chaospower/skills/chaos-repo-change/SKILL.md
  - plugins/chaospower/skills/chaos-code-review/SKILL.md
  - plugins/chaospower/skills/chaos-writeback/SKILL.md
scope: 适用于追溯 Chaospower P0 第一阶段 skill-first 插件骨架的落地范围、验证边界和后续风险。
risks:
  - 尚未加入 marketplace，插件发现路径未验证。
  - 尚未在真实代码变更任务中跑完整 P0 链路。
  - P1/P2 能力未落地，不能覆盖联网、板端、incident triage、功能 review 或知识 promotion review。
updated_at: 2026-04-15
---

# 1 Chaospower P0 skill-first 第一阶段落地收敛记录

## 1.1 Task / Event

- task_type: `workflow_refactor_implementation`
- goal: 执行 Chaospower 第一阶段最小落地版，并将优化内容收敛回 `02_Projects/Agent Workflow` current 组。

## 1.2 Trigger / Motivation

- 既有三侧同步规范规则源头分散，AGENTS.md 和 toml 容易膨胀。
- 已形成 skill-first 压缩方案，需要先落地 P0 最小闭环，而不是一次性铺开所有候选 skill。

## 1.3 Accepted Change / Key Decision

- 新建 `plugins/chaospower` 插件 P0 结构。
- `using-chaospower` 只承载 route、gate、handoff、audit summary。
- 第一阶段 active skill 仅保留：
  - `using-chaospower`
  - `chaos-scope-plan`
  - `chaos-repo-change`
  - `chaos-code-review`
  - `chaos-writeback`
- `chaos-functional-review`、`chaos-source-ingest`、`chaos-board-run`、`chaos-incident-triage`、`chaos-knowledge-promotion-review` 延后。
- `agent-workflow-migrator` 只作为迁移工具，不作为 active workflow 规则源。

## 1.4 Verification Boundary

- 已验证：
  - `plugins/chaospower/.codex-plugin/plugin.json` 可被 JSON 解析。
  - P0 skill 均包含 `name` 与 `description` frontmatter。
  - `plugins/chaospower/skills/` 下只存在五个 P0 skill 目录。
- 未验证：
  - marketplace 注册与 UI 发现。
  - 真实代码变更任务中的完整 P0 链路。
  - `skill-creator` 的 `quick_validate.py`，因本地 Python 缺少 `yaml` 模块未能运行。

## 1.5 Impact On Current

- sync_mode: `current_patch`
- current_files_updated:
  - `workflow_overview_current`
  - `workflow_design_current`
  - `workflow_spec_current`
  - `workflow_implementation_current`
  - `workflow_validation_current`
- history_files_to_mark: []
- single_pass_recoverable: `true`

## 1.6 Review / Closure Decision

- closure_decision: `accepted_with_risks`
- residual_risks:
  - P0 结构已落地，但尚未完成 marketplace 和真实任务链路验证。
  - P1/P2 能力不能由 P0 skill 冒名覆盖。
