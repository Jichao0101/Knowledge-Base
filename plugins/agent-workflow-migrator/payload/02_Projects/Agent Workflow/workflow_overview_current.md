---
title: Agent Workflow Overview Current
summary: Agent Workflow 项目化演化主题的默认入口，定义当前目标、恢复顺序、当前真相源集合与 modification records 的使用边界。
status: verified
doc_role: current
truth_role: current
current_kind: overview
lifecycle_state: active
default_entry: true
default_entry_verified: true
sync_mode: current_patch
current_files_must_update:
  - 02_Projects/Agent Workflow/workflow_overview_current.md
  - 02_Projects/Agent Workflow/workflow_design_current.md
  - 02_Projects/Agent Workflow/workflow_spec_current.md
  - 02_Projects/Agent Workflow/workflow_implementation_current.md
  - 02_Projects/Agent Workflow/workflow_validation_current.md
history_files_to_mark: []
single_pass_recoverable: true
sync_required_when:
  - Agent Workflow 当前目标变化
  - 默认恢复顺序变化
  - current 与 modification records 分工变化
  - 规范落点或项目化管理边界变化
retrieval_priority: current
supersedes: []
merged_into: []
current_replacement: []
related_code: []
sources:
  - 01_Knowledge/Agent Workflow/Agent驱动知识库、代码库与板端侧协同闭环规范.md
  - 01_Knowledge/Agent Workflow/Agent三侧运行规范与调度模板.md
  - 01_Knowledge/Agent Workflow/Agent三侧模板与文件结构规范.md
scope: 适用于恢复 Agent Workflow 作为持续演化主题时的当前入口、默认读取链与项目化管理边界。
risks:
  - 当前实现主要落在知识规范文档中，项目区 current 组仍是第一轮收敛版本。
updated_at: 2026-04-13
---

## 0.1 Current Scope

本主题不再只作为知识规范主题维护，也作为 `02_Projects/Agent Workflow` 的项目化演化对象维护。

默认恢复顺序固定为：

1. [[02_Projects/Agent Workflow/workflow_overview_current]]
2. [[02_Projects/Agent Workflow/workflow_design_current]]
3. [[02_Projects/Agent Workflow/workflow_spec_current]]
4. [[02_Projects/Agent Workflow/workflow_implementation_current]]
5. [[02_Projects/Agent Workflow/workflow_validation_current]]

## 0.2 Default Recovery Bundle

- `workflow_overview_current`
- `workflow_design_current`
- `workflow_spec_current`
- `workflow_implementation_current`
- `workflow_validation_current`

## 0.3 Current Truth

- 知识规范负责稳定制度、状态机、模板和角色契约
- 项目区 current 负责说明 Agent Workflow 当前是如何被组织、调整、验证与持续演化管理的
- modification records 负责记录某次收敛、重构、诊断、审计或验证事件

## 0.4 Current Boundaries

- `current` 只承载当前态与稳定语义
- `modification records` 只承载事件闭环、动机、验证边界、追溯索引与残余风险
- 本主题当前不涉及代码实现修改，不涉及 board 执行

## 0.5 Current Document Roles

- `workflow_design_current`：负责 Workflow 当前分层、owner 和 project/knowledge 分工
- `workflow_spec_current`：负责 current / modification records / writeback / recoverability 的强规则
- `workflow_implementation_current`：负责规则当前落在哪些知识规范和项目文档
- `workflow_validation_current`：负责当前已落地、未落地和待验证事项

## 0.6 Current Recovery Rule

- 规范正文是稳定规则真相源
- 项目区 current 是“这套规则目前如何被管理和收敛”的真相源
- modification records 不进入默认恢复链，只用于追溯具体演化事件

## 0.7 Known Gaps

- 本主题的项目化 current 组刚建立，后续仍需补更多 validation 记录
- 修改记录类型虽然已进入规范，但项目侧模板还未完全批量落地到其他主题

## 0.8 Historical Mapping

- 2026-04-13 前，Agent Workflow 主要只在 `01_Knowledge/Agent Workflow` 下作为规范主题维护
- 自 2026-04-13 起，开始在 `02_Projects/Agent Workflow` 下建立 current + modification-record 管理方式

## 0.9 Sync Contract

- must_update_when:
  - Workflow 规范层的 current / delta / recoverability 规则变化
  - 本主题的项目化管理边界变化
  - default recovery chain 变化
