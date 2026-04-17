---
title: Agent Workflow Overview Current
summary: cutepower 已成为 Agent Workflow 当前唯一的运行资产与项目演化对象；本文件定义默认恢复顺序、当前真相源集合与项目侧同步边界。
status: pending_review
doc_role: current
truth_role: current
current_kind: overview
lifecycle_state: active
default_entry: true
default_entry_verified: true
sync_mode: current_patch
current_files_must_update:
  - 02_Projects/Agent Workflow/workflow_overview_current.md
  - 02_Projects/Agent Workflow/workflow_interface_current.md
  - 02_Projects/Agent Workflow/workflow_design_current.md
  - 02_Projects/Agent Workflow/workflow_spec_current.md
  - 02_Projects/Agent Workflow/workflow_implementation_current.md
  - 02_Projects/Agent Workflow/workflow_validation_current.md
history_files_to_mark: []
single_pass_recoverable: true
sync_required_when:
  - cutepower active truth source 变化
  - P0/P1 scope 或 runtime gate 边界变化
  - 默认恢复顺序变化
  - 项目区 current / baseline / record 分工变化
retrieval_priority: current
supersedes: []
merged_into: []
current_replacement: []
related_code: []
related_plugins:
  - plugins/cutepower
sources:
  - plugins/cutepower/README.md
  - plugins/cutepower/contracts/contract-index.yaml
  - plugins/cutepower/scripts/runtime-gates.js
  - 01_Knowledge/Agent Workflow/Plugin-first与Contracts-first治理插件设计模式.md
  - 01_Knowledge/Agent Workflow/运行时门禁与独立审查边界模式.md
  - 02_Projects/Agent Workflow/cutepower_p0_implementation_baseline.md
  - 02_Projects/Agent Workflow/cutepower_p1_board_functional_incident_baseline.md
  - 02_Projects/Agent Workflow/cutepower P1插件落地与运行时门禁收敛记录-2026-04-17.md
scope: 适用于恢复 Agent Workflow 当前围绕 cutepower 的默认入口、恢复链、真相源集合与项目侧同步边界，不覆盖 cutepower 之外的旧三侧体系。
risks:
  - 若把 baseline 或 README 当作高于 contracts 的规则源，会重新造成真相源分裂。
  - 若后续继续把非 cutepower 项目记录写回本目录，会再次污染当前恢复链。
updated_at: 2026-04-17
---

## 0.1 Current Scope

Agent Workflow 当前不再维护原三侧文档体系，也不再维护 Chaospower 过渡态。
当前唯一 active 运行资产是 `plugins/cutepower`。

当前范围固定为：

- cutepower P0 五个基础 skills
- cutepower P1 三个扩展 skills
- 对应 contracts / schemas / validation / runtime gates
- 项目区 current + baseline + cutepower-specific record

本主题当前不包含：

- 原三侧长篇制度文档
- Chaospower 过渡插件
- P2 能力扩展
- 宿主知识库目录语义

## 0.2 Default Recovery Order

1. [[02_Projects/Agent Workflow/workflow_overview_current]]
2. [[02_Projects/Agent Workflow/workflow_interface_current]]
3. [[02_Projects/Agent Workflow/workflow_design_current]]
4. [[02_Projects/Agent Workflow/workflow_spec_current]]
5. [[02_Projects/Agent Workflow/workflow_implementation_current]]
6. [[02_Projects/Agent Workflow/workflow_validation_current]]

## 0.3 Default Recovery Bundle

- `workflow_overview_current`
- `workflow_interface_current`
- `workflow_design_current`
- `workflow_spec_current`
- `workflow_implementation_current`
- `workflow_validation_current`

## 0.4 Current Truth

- `plugins/cutepower/contracts/`：治理真相源
- `plugins/cutepower/scripts/runtime-gates.js`：执行期门禁真相源
- `plugins/cutepower/skills/`：消费 contracts 的运行资产
- `plugins/cutepower/README.md`、`AGENTS.md`、`agents/*.toml`：薄桥接与安装入口
- 项目区 current：描述当前 cutepower 如何被组织、实现与验证
- 项目区 baseline / record：历史与事件追溯，不进入默认恢复链

## 0.5 Current Boundaries

- project current 不覆盖 plugin contracts
- baseline 只承载历史实施边界，不再作为默认实现入口
- modification record 只承载 cutepower-specific 事件闭环
- 正式知识区只保留通用模式，不回流 plugin active truth
- `plugins/agent-workflow-migrator` 不属于当前 cutepower 真相源

## 0.6 Current Document Roles

- `workflow_design_current`：当前分层、边界与 non-goals
- `workflow_interface_current`：当前最小启动提示词模板与入口使用边界
- `workflow_spec_current`：当前项目级强规则与真相源优先级
- `workflow_implementation_current`：当前落点映射与保留资产
- `workflow_validation_current`：当前验证结论、残余风险与下一轮验证

## 0.7 Known Gaps

- isolated vault 下的完整 Codex 发现链路仍未做端到端验证
- `.agents/plugins/marketplace.json` 仍未将 cutepower 设为当前知识库默认可安装插件
- `plugins/agent-workflow-migrator` 仍保留 legacy payload，尚未清理

## 0.8 Historical Mapping

- 原三侧知识文档已从 `01_Knowledge/Agent Workflow` 移除
- 原三侧与 Chaospower 项目记录已从 `02_Projects/Agent Workflow` 移除
- 当前项目区只保留 cutepower current、cutepower baseline 和 cutepower record

## 0.9 Sync Contract

- must_update_when:
  - cutepower contracts / skills / runtime gates 发生边界变化
  - current truth source priority 变化
  - 当前保留的 project artifacts 集合变化
  - cutepower 验证结论变化
