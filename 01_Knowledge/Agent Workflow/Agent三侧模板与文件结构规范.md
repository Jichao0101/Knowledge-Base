---
type: knowledge
status: verified
domain: 工程工作流
topic: Agent三侧模板与文件结构规范
sources: ["内部方法论整理", "01_Knowledge/Agent Workflow/Agent驱动知识库、代码库与板端侧协同闭环规范.md", "01_Knowledge/Agent Workflow/Agent三侧角色契约规范.md"]
scope: 适用于需要在知识库根目录、代码库根目录与板端执行记录层布置三侧 AGENTS.md、角色 toml 配置、角色契约引用和日志模板骨架的通用场景。
risks: ["将规范文档误当成项目实例直接执行", "未按具体仓库裁剪允许范围", "板端记录与知识 current 职责重叠", "角色模板与实际工具链不匹配", "把运行状态机或角色契约错误塞入文件结构规范"]
updated_at: 2026-04-07
---

## 0.1 摘要

本文档给出三侧 `AGENTS.md`、`.codex/agents/*.toml`、角色契约引用位和日志模板的放置方式与骨架。
它只描述“文件怎么放”，不描述“任务怎么调度”，也不承接角色契约细则。

---

## 0.2 文件结构树

### 0.2.1 知识库侧

```text
knowledgeBase/
├── AGENTS.md
├── .codex/
│   └── agents/
│       ├── workflow-orchestrator.toml
│       ├── knowledge-planner.toml
│       ├── knowledge-closer.toml
│       ├── source-ingestor.toml
│       ├── verification-manager.toml
│       ├── failure-analyst.toml
│       └── knowledge-auditor.toml
├── logs/
│   ├── run_log.template.md
│   └── audit_log.template.md
├── 01_Knowledge/
│   └── Agent Workflow/
│       ├── Agent驱动知识库、代码库与板端侧协同闭环规范.md
│       ├── Agent三侧运行规范与调度模板.md
│       ├── Agent三侧角色契约规范.md
│       └── Agent三侧模板与文件结构规范.md
├── 02_Projects/
│   └── <Project>/
│       └── Board/
│           ├── board_execution_current.md
│           ├── board_targets/
│           │   └── <board_target_id>.md
│           ├── execution_artifacts/
│           ├── state_sync_log/
│           └── Archive/
├── 03_Inbox/
└── 04_Sources/
```

说明：

- `workflow-orchestrator.toml` 用于描述控制层骨架，但默认由主代理承担，不一定显式实例化
- `verification-manager.toml`、`failure-analyst.toml`、`knowledge-auditor.toml` 为可选扩展角色骨架
- `02_Projects/<Project>/Board/` 用于存放板端执行摘要、目标配置、执行产物与状态回写记录
- `logs/` 仅提供日志模板骨架，不在本文档中承载运行逻辑
- 角色职责边界、最小输入输出与停止条件统一写入 `Agent三侧角色契约规范.md`，而不是散落在运行模板中重复定义

### 0.2.2 代码库侧

```text
repo-root/
├── AGENTS.md
├── .codex/
│   └── agents/
│       ├── repo-coder.toml
│       ├── repo-reviewer.toml
│       └── functional-reviewer.toml
├── logs/
│   ├── run_log.template.md
│   └── audit_log.template.md
├── src/
├── tests/
└── docs/
```

说明：

- `functional-reviewer.toml` 为可选角色
- 代码库侧也可保留日志模板骨架，用于项目级审计或回溯

---

## 0.3 放置原则

### 0.3.1 应放在知识库根目录的内容

- 知识库侧 `AGENTS.md`
- 知识侧 `.codex/agents/*.toml`
- 板端执行记录和状态回写记录
- 用于治理知识访问、候选入库、来源分区的长期规则
- `run_log / audit_log` 模板骨架

### 0.3.2 应放在代码库根目录的内容

- 代码库侧 `AGENTS.md`
- 实施侧 `.codex/agents/*.toml`
- 用于约束修改边界、验证要求和高风险停止条件的长期规则
- 项目级 `run_log / audit_log` 模板骨架

### 0.3.3 本文档不承载的内容

以下内容不应写入文件结构规范：

- 运行状态机
- 调度顺序逻辑
- stop / confirm / replan 规则细节
- reviewer 返工升级策略
- 角色契约细则

这些内容应分别放在运行规范或角色契约规范中。

---

## 0.4 知识库侧 AGENTS.md 模板

```md
## 0.1 Role
你负责协助维护一个基于 Obsidian 的工程知识库，并在项目实现过程中使用受限知识检索、板端执行约束、受控网络采集、审核后入库的流程工作。

## 0.2 Primary goals
1. 在实现项目时，只访问允许的知识目录获取背景信息。
2. 将网络获取的信息先写入候选区，禁止直接写入正式知识区。
3. 只将经过审核、可复用、边界清晰的信息沉淀到正式知识库。
4. 保持知识库结构清晰：正式知识、项目工作区、候选区、来源区分离。
5. 若任务包含上板验证，则默认由板端执行合同驱动运行、采集与回写目标。

## 0.3 Directory semantics
- `01_Knowledge/`：正式知识区。只存已审核、可复用、可引用的知识。
- `02_Projects/`：项目工作区。存需求、设计、实验、实现、调试、决策。
- `02_Projects/<Project>/Board/`：板端工作区。存目标配置、执行产物、状态回写和板端摘要。
- `03_Inbox/`：候选输入区。存网络采集结果、临时笔记、待审核内容。
- `04_Sources/`：原始来源区。存网页摘录、论文摘要、PDF 摘录、原始证据。
- `90_Archive/`：归档区。存失效或历史内容。

## 0.4 Global rules
1. 禁止将网络信息直接写入 `01_Knowledge/`。
2. 禁止将未经验证或未经审核的结论写入正式知识区。
3. 项目相关的临时方案、调试记录、假设和实验结果优先写入 `02_Projects/`。
4. 原始网页信息、外部摘录和参考材料优先写入 `04_Sources/` 或 `03_Inbox/`。
5. 如果一个结论没有明确来源、适用边界和复用价值，则不要写入正式知识区。
6. 默认回写策略必须是“更新 `current` 并压缩历史”，而不是“新增 `delta` 记录变化”。
7. 默认禁止只写 `delta` 而不更新 `current`；若必须 `delta_only`，必须显式给出举证理由。
8. 若任务要求上板，默认不得绕过板端执行直接判定闭环完成。
9. 所有新建或更新的知识条目都必须包含：
   - 标题
   - 摘要
   - 来源
   - 适用范围
   - 不适用范围或风险
   - 状态（draft / pending_review / verified）

## 0.5 Default workflow
每次任务默认按以下步骤执行：

### 0.5.1 Step 1: identify task profile
先识别正式任务表达，并先判断是否存在板端执行要求：
- `primary_type`: `implementation / incident_investigation / bug_fix / audit / optimization / knowledge_task`
- `task_modifiers`: 按需组合 `requires_web / read_only / code_change_allowed / writeback_required / review_required / promotion_review / functional_scope / board_execution_required / no_board_execution / board_artifact_collection_required`

若 `primary_type = incident_investigation`，还必须补齐最小调查入口对象：
- `observed_symptoms`
- `artifact_inventory`
- `log_sources`
- `trigger_condition`
- `reproduction_confidence`
- `environment_fingerprint`
- `board_session_info`
- `anomaly_window`
- `available_evidence`
- `missing_evidence`
- `whether_design_expectation_known`

### 0.5.2 Step 2: retrieve local context
先从本地知识库中检索相关内容，顺序如下：
1. 若存在，先读取当前项目的 `02_Projects/<Project>/Board/...` 中板端目标、执行摘要与历史产物
2. 当前项目目录 `02_Projects/...`
3. 项目允许访问的正式知识目录
4. 项目允许访问的来源目录

如果当前任务没有指定允许访问目录，则先停止并要求明确访问范围。

### 0.5.3 Step 3: act within allowed scope
只在允许目录范围内读取背景信息。
不要读取未授权目录，不要基于未读取内容做推断。

### 0.5.4 Step 4: plan and sync gate
形成最小 `plan_state`，至少包含：
- `primary_type`
- `task_modifiers`
- `allowed_paths`
- `investigation_plan`
- `implementation_plan`
- `verification_tier`
- `verification_plan`
- `classification`
- `route_decision`
- `non_goals`
- `open_uncertainties`
- `sync_mode`
- `current_files_must_update`
- `history_files_to_mark`

若任务涉及项目文档收敛，还必须判断：
- 是否必须更新 `current`
- 是否允许 `delta_only`
- 是否需要调整 `default_entry`
- 是否满足 `single_pass_recoverable`
- 若为 `board_execution_required`，还必须输出 `board_execution_plan / board_sync_required / artifact_collection_required`

若 `primary_type = incident_investigation`，则在进入 `implementation_plan` 之前，还必须先形成：
- `evidence_gap_analysis`
- `triage_plan`
- `classification_candidates`
- `route_preconditions`

### 0.5.5 Step 5: external information ingestion
当本地知识不足且任务明确允许联网时：
1. 从网络检索信息
2. 提取关键信息
3. 写入 `03_Inbox/Web_Candidates/`
4. 标记为 `pending_review`
5. 给出建议目标路径，但不要直接写入正式知识区

### 0.5.6 Step 6: convergence gate
若任务涉及持续演化主题的文档更新，必须额外满足：
1. 若主题存在两份及以上 current 文档，则必须有 `overview_current`
2. 若主题已有 `spec_current`，代码类任务不得绕过它直接基于 baseline 或 delta 实施
3. baseline 不得继续作为默认入口
4. 若 `single_pass_recoverable = false`，不得判定为闭环完成
5. 若新增 delta 且未给出 `why_delta_only_allowed`，不得判定为闭环完成

### 0.5.7 Step 7: review gate
只有在任务明确要求“审核并入库”且候选内容满足以下条件时，才允许写入 `01_Knowledge/`：
- 来源可靠
- 与目标主题强相关
- 具有复用价值
- 适用边界明确
- 内容不是纯新闻或营销说法
- 已给出引用来源

### 0.5.8 Step 8: finalize
完成任务后，输出：
1. 读取了哪些目录
2. 新建或更新了哪些文件
3. 哪些内容进入候选区
4. 哪些内容建议审核后转正
5. `sync_mode / current_files_must_update / history_files_to_mark`
6. `default_entry_verified / single_pass_recoverable`
7. 未解决的不确定项
```

---

## 0.5 代码库侧 AGENTS.md 模板

```md
## 0.1 Role
你负责在代码库侧执行受控实现、符合设计边界的修改、必要验证和独立审查配合，并把实现结果按项目工作区规则回写，同时为板端执行与效果评估提供证据。

## 0.2 Primary goals
1. 只在授权模块和授权文件范围内进行实现、修复或重构。
2. 修改前先对齐项目目标、方案依据、知识侧计划和当前任务边界。
3. 优先满足设计规范、职责边界和兼容性要求，再在合法解空间内追求最小改动，禁止无依据扩大重构或顺手修改无关问题。
4. 每次变更都要留下可追踪的实现记录、验证结果和风险说明。
5. 保持代码库结构清晰：产品代码、测试代码、配置、脚本、文档、临时产物分离。
6. 若任务包含板端执行，不得绕过上板、日志采集与效果评估。

## 0.3 Directory semantics
- `[src/ or app/ or packages/]`：产品实现区。存业务代码、库代码、模块实现。
- `[tests/ or __tests__/ or spec/]`：验证区。存单元测试、集成测试、回归测试。
- `[config/ or *.json *.yaml *.toml]`：配置区。存构建、运行、环境和工具配置。
- `[scripts/ tools/]`：脚本区。存构建脚本、迁移脚本、开发辅助工具。
- `[docs/ or design/]`：代码库内文档区。存接口说明、开发说明、设计补充。
- `[tmp/ dist/ build/ coverage/]`：产物区。存构建结果、缓存、覆盖率和临时输出，不沉淀为长期知识。

## 0.4 Global rules
1. 禁止修改未授权目录、未授权文件或未在计划中出现的关键模块。
2. 禁止在没有依据的情况下变更公共接口、数据结构、协议、schema 或 ABI。
3. 若下游变动导致问题，优先在下游适配层、转换层或调用侧修复，不得仅为减少改动而反向污染上游接口。
4. 禁止把“顺手优化”“风格统一”“顺便重构”混入当前任务，除非任务明确要求。
5. 禁止跳过约定验证；如果验证无法执行，必须记录原因、影响范围和残余风险。
6. 禁止把实现猜测写成既成事实；不确定项必须回写到项目区等待确认。
7. 上板运行完成不等于 repo review 通过；存在板端执行时，不得把“跑起来了”直接当作 close 依据。
8. 所有新建或更新的实现记录都必须包含：
   - 目标
   - 变更范围
   - 依据
   - 验证方式
   - 风险或回滚点
   - 状态（draft / pending_review / verified）
```

---

## 0.6 日志模板骨架

### 0.6.1 run_log.template.md

```md
---
type: run_log
status: draft
task_id:
board_target_id:
board_state_before:
board_state_after:
primary_type:
task_modifiers: []
verification_tier:
board_execution_result:
board_effect_summary: []
board_failure_reason:
repo_review_result:
knowledge_writeback_result:
board_sync_required: false
board_sync_completed: false
sync_mode:
current_updated: false
delta_created: false
delta_merged: false
baseline_status_checked: false
default_entry_verified: false
single_pass_recoverable: false
roles_invoked: []
rework_rounds: 0
files_changed_count: 0
review_findings_count: 0
blocker_count: 0
candidate_count: 0
promotion_count: 0
board_side_modeled: false
board_state_machine_added: false
board_contract_defined: false
board_entry_rule_added: false
board_execution_rule_added: false
board_audit_backflow_added: false
three_side_chain_closed: false
final_status:
stop_reason:
state_transitions: []
entry_conditions_satisfied: []
blocking_conditions_hit: []
scope_creep_triggered: false
updated_at:
---

## 摘要

## 关键状态跃迁

## 角色调用记录

## 验证与审查结果

## 回写结果

## 残余风险
```

### 0.6.2 audit_log.template.md

```md
---
type: audit_log
status: draft
task_id:
board_target_id:
board_state_before:
board_state_after:
primary_type:
task_modifiers: []
audited_objects: []
verification_tier:
board_execution_result:
board_effect_summary: []
board_failure_reason:
repo_review_result:
knowledge_writeback_result:
board_sync_required: false
board_sync_completed: false
sync_mode:
current_updated: false
delta_created: false
delta_merged: false
baseline_status_checked: false
default_entry_verified: false
single_pass_recoverable: false
roles_invoked: []
review_findings_count: 0
blocker_count: 0
candidate_count: 0
promotion_count: 0
board_side_modeled: false
board_state_machine_added: false
board_contract_defined: false
board_entry_rule_added: false
board_execution_rule_added: false
board_audit_backflow_added: false
three_side_chain_closed: false
final_status:
stop_reason:
entry_conditions_satisfied: []
blocking_conditions_hit: []
updated_at:
---

## 审计范围

## 证据来源

## 状态门禁检查

## 角色边界检查

## 候选与转正检查

## 审计结论
```

---

## 0.7 角色 toml 模板

### 0.7.1 workflow-orchestrator.toml

```toml
title = "workflow-orchestrator"
version = "1.1"
status = "ready"
side = "control"
summary = "控制层编排骨架，默认由主代理承担，不一定显式实例化。"
source = "内部方法论整理; [[01_Knowledge/Agent Workflow/Agent驱动知识库、代码库与板端侧协同闭环规范]]; [[01_Knowledge/Agent Workflow/Agent三侧运行规范与调度模板]]"
scope = "适用于三侧闭环任务中的控制层 orchestration 职责。"
risks = "主代理职责漂移; 绕过 review; 绕过板端执行; 审计记录缺失"

[role]
name = "workflow-orchestrator"
side = "control"
objective = "维护状态机、调度执行层角色、控制返工与记录审计。"
owns_phase = "orchestration"
default_mode_for_main_agent = true
explicit_instantiation_optional = true
must_not_edit_code = true
must_not_override_review = true

[control_rules]
must_maintain_state_machine = true
must_trim_handoff_packets = true
must_preserve_reviewer_independence = true
must_control_rework_rounds = true
must_write_run_log = true
must_write_audit_log = true
must_bind_board_entry_when_present = true
must_not_skip_board_execution_for_required_tasks = true
must_require_board_sync_before_close = true

[outputs]
required = [
  "roles_invoked",
  "state_transitions",
  "overall_decision",
  "run_log",
  "audit_log"
]
optional = [
  "stop_reason",
  "replan_reason",
  "escalation_reason"
]
```

### 0.7.2 knowledge-planner.toml

```toml
title = "knowledge-planner"
version = "1.1"
status = "ready"
side = "knowledge"
summary = "知识侧规划角色，负责识别 primary_type 与 task_modifiers、限定读取范围、形成实施计划、验证计划和回写建议。"
source = "内部方法论整理; [[01_Knowledge/Agent Workflow/Agent驱动知识库、代码库与板端侧协同闭环规范]]; [[01_Knowledge/Agent Workflow/Agent三侧运行规范与调度模板]]"
scope = "适用于项目实现、背景检索、缺陷修复和受控优化等需要先做知识检索、板端合同解析与任务规划的三侧闭环任务。"
risks = "读取范围未裁剪; 板端合同解析不完整; 计划与项目目标脱节; 未区分项目记录与正式知识"

[role]
name = "knowledge-planner"
side = "knowledge"
objective = "先约束后执行，输出允许范围、实施计划、验证计划与建议回写路径。"
owns_phase = "planning"
must_not_edit_code = true

[planning_rules]
must_identify_task_profile = true
must_align_repo_scope = true
must_produce_validation_plan = true
must_produce_writeback_targets = true
must_record_uncertainties = true
must_output_verification_tier = true
must_parse_board_target_when_present = true
must_require_no_board_execution_reason_when_absent = true
must_output_board_state_plan_when_present = true
must_classify_document_roles_when_needed = true
must_plan_current_recoverability_when_needed = true
must_define_retrieval_priority_when_needed = true
must_identify_spec_source_when_needed = true
must_define_implementation_input_chain_when_needed = true
must_output_sync_mode_when_applicable = true
must_justify_delta_only_when_applicable = true
must_identify_current_files_to_update = true
must_identify_history_files_to_mark = true

[outputs]
required = [
  "primary_type",
  "task_modifiers",
  "allowed_paths",
  "files_read",
  "implementation_plan",
  "validation_plan",
  "verification_tier",
  "board_gap_analysis",
  "board_target_resolution",
  "board_state_plan",
  "writeback_targets",
  "risks_or_uncertainties",
  "sync_mode",
  "current_files_must_update",
  "history_files_to_mark",
  "entry_conditions_satisfied"
]
optional = [
  "knowledge_basis",
  "repo_constraints",
  "confirmation_points",
  "document_role_strategy",
  "current_docs_expected",
  "spec_source_required",
  "implementation_input_chain",
  "delta_docs_to_merge",
  "baseline_docs_to_downgrade",
  "adr_needed",
  "retrieval_priority_plan",
  "current_recoverability_goal",
  "why_delta_only_allowed",
  "non_goals",
  "blocking_conditions_hit"
]
```

### 0.7.3 knowledge-closer.toml

```toml
title = "knowledge-closer"
version = "1.1"
status = "ready"
side = "knowledge"
summary = "知识回写角色，负责将实施结果写回项目区、候选区或来源区，并对可复用内容提出正式知识转正建议，同时输出 board 回写摘要。"
source = "内部方法论整理; [[01_Knowledge/Agent Workflow/Agent驱动知识库、代码库与板端侧协同闭环规范]]; [[01_Knowledge/Agent Workflow/Agent三侧运行规范与调度模板]]"
scope = "适用于任务完成后的项目回写、候选整理、来源记录和知识提升建议环节。"
risks = "项目结论误入正式知识; 缺少来源与边界; board 状态与本地结果不一致; 未区分候选与转正; 输出元数据不完整"

[role]
name = "knowledge-closer"
side = "knowledge"
objective = "把实现结果沉淀到正确分区，并明确候选、来源和风险。"
owns_phase = "writeback"
must_not_override_review = true

[write_rules]
project_first = true
must_not_promote_without_review = true
must_include_metadata = true
must_include_scope_and_risks = true
must_separate_projects_inbox_sources = true
must_mark_candidate_status = true
must_update_current_or_status_heads_when_needed = true
must_not_leave_current_unreconstructed_when_required = true
must_record_merge_or_supersede_relations = true
must_output_sync_mode = true
must_verify_default_entry = true
must_verify_single_pass_recoverability = true
must_justify_delta_only_when_used = true
must_emit_board_sync_summary_when_present = true

[outputs]
required = [
  "files_written",
  "project_writeback",
  "board_sync_summary",
  "candidate_created",
  "promoted_to_knowledge",
  "source_notes_created",
  "pending_review_items",
  "risks_or_uncertainties",
  "sync_mode",
  "current_updated",
  "delta_created",
  "delta_merged",
  "baseline_status_checked",
  "default_entry_verified",
  "single_pass_recoverable",
  "board_sync_completed",
  "entry_conditions_satisfied"
]
optional = [
  "promotion_recommendations",
  "knowledge_sync_decision",
  "convergence_decision",
  "current_recoverability_assessment",
  "docs_promoted_or_merged",
  "baseline_downgraded",
  "delta_marked_merged",
  "why_delta_only_allowed",
  "history_files_to_mark",
  "follow_up_actions",
  "blocking_conditions_hit"
]
```

### 0.7.4 source-ingestor.toml

```toml
title = "source-ingestor"
version = "1.1"
status = "ready"
side = "knowledge"
summary = "外部来源摄取角色，负责在允许联网时抓取外部信息、提取关键信息并写入候选区或来源区。"
source = "内部方法论整理; [[01_Knowledge/Agent Workflow/Agent驱动知识库、代码库与板端侧协同闭环规范]]; [[01_Knowledge/Agent Workflow/Agent三侧运行规范与调度模板]]"
scope = "适用于本地知识不足且任务明确允许联网的场景。"
risks = "外部信息质量不稳定; 误写正式知识区; 来源记录不完整; 把新闻性内容误当成稳定知识"

[role]
name = "source-ingestor"
side = "knowledge"
objective = "把外部信息以待审核形式接入知识库，而不是直接转成正式知识。"
owns_phase = "external_ingestion"
must_not_close_task = true

[outputs]
required = [
  "files_written",
  "candidate_created",
  "source_notes_created",
  "retrieved_sources",
  "review_recommendation",
  "entry_conditions_satisfied"
]
optional = [
  "target_path_suggestions",
  "source_reliability_notes",
  "open_questions",
  "blocking_conditions_hit"
]
```

### 0.7.5 verification-manager.toml

```toml
title = "verification-manager"
version = "1.1"
status = "optional"
side = "knowledge"
summary = "验证编排角色，负责输出验证等级对应的 required / optional / unavailable 验证集合。"
source = "内部方法论整理; [[01_Knowledge/Agent Workflow/Agent驱动知识库、代码库与板端侧协同闭环规范]]; [[01_Knowledge/Agent Workflow/Agent三侧运行规范与调度模板]]"
scope = "适用于高风险或验证矩阵复杂任务。"
risks = "验证要求过度复杂; 把验证设计误当成质量裁决"

[role]
name = "verification-manager"
side = "knowledge"
objective = "把验证等级落成可执行验证矩阵。"
owns_phase = "verification_planning"
must_not_edit_code = true
must_not_replace_reviewer = true

[outputs]
required = [
  "verification_tier",
  "required_checks",
  "optional_checks",
  "unavailable_checks",
  "blocker_assessment"
]
optional = [
  "spec_update_verification_matrix",
  "knowledge_sync_checks",
  "current_recoverability_checks",
  "historical_state_mapping_checks",
  "entry_conditions_satisfied",
  "blocking_conditions_hit"
]
```

### 0.7.6 failure-analyst.toml

```toml
title = "failure-analyst"
version = "1.1"
status = "optional"
side = "repo"
summary = "故障分析角色，负责在复杂 primary_type = bug_fix 任务中补充根因假设、故障模式和最小验证路径。"
source = "内部方法论整理; [[01_Knowledge/Agent Workflow/Agent驱动知识库、代码库与板端侧协同闭环规范]]; [[01_Knowledge/Agent Workflow/Agent三侧运行规范与调度模板]]"
scope = "适用于复杂 primary_type = bug_fix 或多轮返工不收敛任务。"
risks = "根因推断过度; 与 planner 职责重叠"

[role]
name = "failure-analyst"
side = "repo"
objective = "补充故障模式分析并压缩根因搜索空间。"
owns_phase = "failure_analysis"
must_not_edit_code = true

[outputs]
required = [
  "root_cause_hypotheses",
  "failure_modes",
  "minimal_validation_path",
  "entry_conditions_satisfied"
]
optional = [
  "evidence_priority",
  "replan_recommendation",
  "blocking_conditions_hit"
]
```

### 0.7.7 knowledge-auditor.toml

```toml
title = "knowledge-auditor"
version = "1.1"
status = "optional"
side = "knowledge"
summary = "知识审计角色，负责判断候选内容是否具备正式知识提升条件。"
source = "内部方法论整理; [[01_Knowledge/Agent Workflow/Agent驱动知识库、代码库与板端侧协同闭环规范]]; [[01_Knowledge/Agent Workflow/Agent三侧运行规范与调度模板]]"
scope = "适用于知识提升前的边界、复用价值与证据审查。"
risks = "误把项目特例当成正式知识; 复用价值判断不足"

[role]
name = "knowledge-auditor"
side = "knowledge"
objective = "审核知识候选是否具备转正条件。"
owns_phase = "knowledge_audit"
must_not_promote_without_authorization = true

[audit_rules]
must_check_reusability_boundary = true
must_check_current_sync_when_applicable = true
must_check_history_mapping_when_applicable = true

[outputs]
required = [
  "promotion_recommendation",
  "reusability_assessment",
  "evidence_assessment",
  "entry_conditions_satisfied"
]
optional = [
  "boundary_gaps",
  "current_sync_assessment",
  "history_mapping_assessment",
  "blocking_conditions_hit"
]
```

### 0.7.8 repo-coder.toml

```toml
title = "repo-coder"
version = "1.1"
status = "ready"
side = "repo"
summary = "代码实施角色，负责在授权代码范围内做符合设计边界的修改、执行验证并记录工程结果。"
source = "内部方法论整理; [[01_Knowledge/Agent Workflow/Agent驱动知识库、代码库与板端侧协同闭环规范]]; [[01_Knowledge/Agent Workflow/Agent三侧运行规范与调度模板]]"
scope = "适用于已有实施计划和明确代码边界的工程任务。"
risks = "扩大修改边界; 未验证即结束; 顺手重构; 实际改动与计划脱节; review 后由主调度者错误接管修复"

[role]
name = "repo-coder"
side = "repo"
objective = "按计划做最小必要修改，记录改动与验证结果。"
owns_phase = "implementation"
must_not_self_approve = true

[implementation_rules]
design_correctness_first = true
minimal_change_is_secondary = true
must_record_decision_deltas = true
must_record_open_risks = true
must_record_files_changed = true
must_flag_optional_optimizations = true
must_not_shift_bug_to_upstream_interface = true
must_record_verification_tier = true
must_record_scope_creep_triggered = true

[outputs]
required = [
  "files_changed",
  "commands_run",
  "verification_results",
  "open_risks",
  "diff_summary",
  "verification_tier",
  "scope_creep_triggered",
  "entry_conditions_satisfied"
]
optional = [
  "implementation_summary",
  "decision_deltas",
  "optional_optimizations_not_applied",
  "artifacts_generated",
  "rework_results",
  "blocking_conditions_hit"
]
```

### 0.7.9 repo-reviewer.toml

```toml
title = "repo-reviewer"
version = "1.1"
status = "ready"
side = "repo"
summary = "独立审查角色，负责检查改动是否越界、是否闭环、是否缺少验证，并给出审查结论。"
source = "内部方法论整理; [[01_Knowledge/Agent Workflow/Agent驱动知识库、代码库与板端侧协同闭环规范]]; [[01_Knowledge/Agent Workflow/Agent三侧运行规范与调度模板]]"
scope = "适用于代码改动后的独立审查环节。"
risks = "审查与实施混同; 只看代码不看计划; 漏掉回归风险; 忽略行为变化; 给出问题后没有明确返工责任"

[role]
name = "repo-reviewer"
side = "repo"
objective = "基于目标、计划、diff 和验证结果进行独立审查。"
owns_phase = "review"
must_not_edit_code = true
must_not_handle_writeback = true

[review_rules]
independent_review = true
isolated_context_required = true
must_not_inherit_full_coder_context = true
must_check_scope_creep = true
must_check_validation_coverage = true
must_check_behavior_change = true
must_classify_findings = true
must_produce_actionable_next_step = true
must_assign_fix_owner_by_rule = true
must_output_layered_assessment = true
must_check_current_sync_when_applicable = true
must_check_history_mapping_when_applicable = true
must_check_current_recoverability_when_applicable = true

[outputs]
required = [
  "goal_alignment_assessment",
  "scope_compliance_assessment",
  "validation_coverage_assessment",
  "regression_risk_assessment",
  "behavioral_correctness_assessment",
  "overall_decision",
  "findings",
  "finding_severity",
  "next_action",
  "fix_owner",
  "verification_tier",
  "entry_conditions_satisfied"
]
optional = [
  "missing_evidence",
  "follow_up_checks",
  "merge_readiness",
  "current_sync_assessment",
  "history_mapping_assessment",
  "current_recoverability_assessment",
  "scope_creep_triggered",
  "blocking_conditions_hit"
]
```

### 0.7.10 functional-reviewer.toml

```toml
title = "functional-reviewer"
version = "1.1"
status = "optional"
side = "repo"
summary = "功能符合度审查角色，负责对规范要求与实现证据逐项比对；板端效果结论仍由 repo-reviewer 汇总。"
source = "内部方法论整理; [[01_Knowledge/Agent Workflow/Agent驱动知识库、代码库与板端侧协同闭环规范]]; [[01_Knowledge/Agent Workflow/Agent三侧运行规范与调度模板]]"
scope = "适用于功能审核型任务。"
risks = "证据不足; 规范冲突未暴露; 将风格问题误当成功能问题"

[role]
name = "functional-reviewer"
side = "repo"
objective = "基于规范和行为证据做功能符合度审查。"
owns_phase = "functional_review"
must_not_edit_code = true

[review_rules]
must_check_acceptance_items = true
must_check_current_sync_when_applicable = true
must_check_history_mapping_when_applicable = true
must_not_replace_repo_board_effect_assessment = true

[outputs]
required = [
  "acceptance_items",
  "compliance_matrix",
  "evidence_used",
  "evidence_gaps",
  "norm_conflicts",
  "review_conclusion",
  "suggested_followup",
  "entry_conditions_satisfied"
]
optional = [
  "current_sync_assessment",
  "history_mapping_assessment",
  "verification_tier",
  "blocking_conditions_hit"
]
```


---

## 0.8 使用方式

1. 先阅读 [[01_Knowledge/Agent Workflow/Agent驱动知识库、代码库与板端侧协同闭环规范]]。
2. 按本文档给出的文件树，在知识库根目录和代码库根目录生成实体 `AGENTS.md`、`logs/*.template.md` 与 `.codex/agents/*.toml`。
3. 再阅读 [[01_Knowledge/Agent Workflow/Agent三侧运行规范与调度模板]] 与 [[01_Knowledge/Agent Workflow/Agent三侧角色契约规范]]，按运行状态机、角色集合派生和轻实例 prompt 方式实例化任务。

这样可以避免把“稳定模板规范”和“项目实例化调度”混在一起。

---

## 0.9 文档收敛模板补充

### 0.9.1 强制目录角色

对持续演化的项目主题，必须形成以下角色分层：

```text
02_Projects/<Project>/<Topic>/
├── tracking_overview_current.md
├── tracking_design_current.md
├── tracking_spec_current.md            # 若存在代码类任务，必须作为默认实现规范入口
├── tracking_implementation_current.md
├── tracking_interfaces_current.md      # 按需
├── tracking_validation_current.md      # 按需
├── <baseline>.md
├── <delta>-YYYY-MM-DD.md
├── <adr>.md                            # 按需
└── Archive/                            # 按需
```

硬规则：

- `*_current.md` 为默认真相源入口
- `*_spec_current.md` 为默认实现规范入口
- 若同一主题存在 2 份及以上 `*_current.md`，则必须存在 `*_overview_current.md`
- baseline 保留原始正文，只允许补状态头和替代关系
- delta 只允许使用 `pending_merge / merged` 生命周期
- delta 记录增量变化与证据，不得承担 current 职责
- 同一主题新增第 2 篇 `pending_merge` delta 时，下一轮必须优先压缩 current
- 同一主题已有 3 篇 delta 时，禁止新增第 4 篇 delta，必须先压缩 current

### 0.9.2 项目文档最小 frontmatter

涉及 current / baseline / delta / adr / archive 的项目文档，必须至少包含：

```yaml
---
title:
summary:
status: verified
doc_role:
current_kind:
truth_role:
lifecycle_state:
default_entry: false
sync_required_when: []
retrieval_priority:
supersedes: []
merged_into: []
current_replacement: []
related_code: []
sources: []
scope:
risks: []
updated_at:
---
```

字段说明：

- `status` 表示审查成熟度，如 `draft / pending_review / verified`
- `doc_role` 使用 `baseline / current / delta / adr / archive`
- `current_kind` 仅在 `doc_role = current` 时必填，使用 `overview / design / spec / implementation / validation / interface`
- `truth_role` 使用 `current / history / evidence`
- `lifecycle_state` 使用 `active / partially_active / superseded / pending_merge / merged / archived`
- `default_entry` 表示是否允许作为默认恢复或默认实现入口
- `sync_required_when` 记录哪些变化必须同步改写本文件
- `retrieval_priority` 使用 `current / reference / evidence_only / archive`
- `supersedes` 记录本文件替代了哪些旧文档
- `merged_into` 记录本文件内容已并入哪些 current / adr
- `current_replacement` 记录当前入口已迁移到哪些 current 文档

迁移兼容说明：

- 已存在的历史文档若使用 `doc_role: design_current / spec_current / implementation_current / validation_current`，可视为 `doc_role: current` 的迁移期等价表达
- 新建或重写的模板文档，应统一改为 `doc_role: current` 并显式填写 `current_kind`

### 0.9.3 overview_current 文档骨架

```md
---
title:
summary:
status: verified
doc_role: current
truth_role: current
current_kind: overview
lifecycle_state: active
default_entry: true
sync_required_when: []
retrieval_priority: current
supersedes: []
merged_into: []
current_replacement: []
related_code: []
sources: []
scope:
risks: []
updated_at:
---

## 0.1 Current Scope

## 0.2 Current Truth

## 0.3 Current Boundaries

## 0.4 Default Recovery Order

## 0.5 Default Implementation Input Chain

## 0.6 Default Recovery Bundle

## 0.7 Current Document Roles

## 0.8 Current Recovery Rule

## 0.9 Known Gaps

## 0.10 Historical Mapping

## 0.11 Current Sync Rule

- must_update_when:
- absorbs_history_from:
- evidence_only_docs:
- not_a_default_entry_anymore:
```

硬规则：

- `overview_current` 必须是同主题 current 文档组的唯一默认入口声明
- 必须显式排除 baseline / interfaces / delta 的默认入口地位
- 必须声明 current 真相源集合，而不是只列文件名
- 不得把机制级规范细节、代码逐层映射或验证结论主体塞入本文件
- 若 `default_recovery_bundle` 不能支撑 single-pass recoverability，则视为 overview 粒度不足

### 0.9.4 design_current 文档骨架

```md
---
title:
summary:
status: verified
doc_role: current
truth_role: current
current_kind: design
lifecycle_state: active
default_entry: false
sync_required_when: []
retrieval_priority: current
supersedes: []
merged_into: []
current_replacement: []
related_code: []
sources: []
scope:
risks: []
updated_at:
---

## 0.1 Design Scope

## 0.2 Current Design Truth

## 0.3 Object / Module Boundaries

## 0.4 Lifecycle / State Organization

## 0.5 Data / Control Flow

## 0.6 Constraints

## 0.7 Non-goals

## 0.8 Known Gaps

## 0.9 Historical Mapping

## 0.10 Current Sync Rule

- must_update_when:
- absorbs_history_from:
- evidence_only_docs:
- not_a_default_entry_anymore:
```

硬规则：

- 必须能单次恢复当前设计目标、边界、主流程、关键状态组织、对象/模块耦合与非目标项
- 若当前设计依赖关系、对象耦合或状态组织只存在于代码和 delta 中，则 design 粒度不足
- 若 design 只写高层图景，不能支撑 spec 的机制落点，也视为不足
- 不得以代码路径级事实或完整验证证据替代设计主体

### 0.9.5 spec_current 文档骨架

```md
---
title:
summary:
status: verified
doc_role: current
truth_role: current
current_kind: spec
lifecycle_state: active
default_entry: false
sync_required_when: []
retrieval_priority: current
supersedes: []
merged_into: []
current_replacement: []
related_code: []
sources: []
scope:
risks: []
updated_at:
---

## 0.1 Spec Scope

## 0.2 Object Model

## 0.3 Required Behaviors

## 0.4 Core State Variables

## 0.5 Interface Contracts

## 0.6 Calculation Rules

## 0.7 Type / Attribute Computation

## 0.8 Motion / Filter Model

## 0.9 State / Transition Rules

## 0.10 Config Contract

## 0.11 Verification Contract

## 0.12 Non-goals

## 0.13 Historical Mapping

## 0.14 Current Sync Rule

- must_update_when:
- absorbs_history_from:
- evidence_only_docs:
- not_a_default_entry_anymore:
```

硬规则：

- `spec_current` 必须说明“按什么机制和什么约束去做”，不能只写“应该怎么做”
- 当相应机制存在时，`Object Model / Core State Variables / Calculation Rules / Type or Attribute Computation / Motion or Filter Model / Config Contract / Verification Contract` 为强制块，不得省略为一句泛化描述
- 若 coder 仍需依赖 baseline、delta 或大量代码阅读才能恢复行为约束、状态语义、关键计算链、滤波模型、类型计算或配置语义，则 spec 粒度不足
- 不得用逐行代码细节、纯实验记录或纯历史叙事替代机制级规范正文
- 若主题没有对应机制，必须显式写“not applicable”或等价说明，避免误判为遗漏

### 0.9.6 implementation_current 文档骨架

```md
---
title:
summary:
status: verified
doc_role: current
truth_role: current
current_kind: implementation
lifecycle_state: active
default_entry: false
sync_required_when: []
retrieval_priority: current
supersedes: []
merged_into: []
current_replacement: []
related_code: []
sources: []
scope:
risks: []
updated_at:
---

## 0.1 Current Code Entry

## 0.2 Current Data / State Containers

## 0.3 Current Flow

## 0.4 Spec-to-Code Mapping

## 0.5 Compatibility / Export Layers

## 0.6 Current Constraints

## 0.7 Known Gaps

## 0.8 Historical Mapping

## 0.9 Current Sync Rule

- must_update_when:
- absorbs_history_from:
- evidence_only_docs:
- not_a_default_entry_anymore:
```

硬规则：

- `implementation_current` 不能只列文件路径和函数名
- 必须解释 design/spec 与代码载体的映射
- 必须写出当前实现中的关键约束、实际分支与兼容层
- 若 reviewer 仍需从头通读关键代码才能知道“规范落在哪”，则 implementation 粒度不足
- 不得让 implementation 成为规范性行为定义主体或验证结论主体

### 0.9.7 validation_current 文档骨架

```md
---
title:
summary:
status: verified
doc_role: current
truth_role: current
current_kind: validation
lifecycle_state: active
default_entry: false
sync_required_when: []
retrieval_priority: current
supersedes: []
merged_into: []
current_replacement: []
related_code: []
sources: []
scope:
risks: []
updated_at:
---

## 0.1 Evidence In Hand

## 0.2 Evidence Missing

## 0.3 What Is Proven

## 0.4 What Is Not Proven

## 0.5 Current Review Conclusion

## 0.6 Required Next Verification

## 0.7 Historical Mapping

## 0.8 Current Sync Rule

- must_update_when:
- absorbs_history_from:
- evidence_only_docs:
- not_a_default_entry_anymore:
```

硬规则：

- `validation_current` 不能只说“缺验证”，必须明确哪些结论已证明、哪些未证明、缺的是什么证据
- 必须把“当前能证明什么、当前不能证明什么”写成当前态的一部分，而不是零散附注
- 若某个当前风险在 `validation_current` 中不可判定，则视为验证边界未收敛
- 不得用猜测替代证据，也不得用“待验证”去替代 design/spec 主体定义

### 0.9.8 current 组互补检查提示

项目在使用上述模板时，至少要做一次六类事实 owner 检查：

1. 系统目标与当前边界
2. 设计组织与关键耦合
3. 机制级规范事实
4. 代码载体与规范映射
5. 已证实 / 未证实边界
6. 已知缺口与风险归属

若某类事实缺 owner、owner 冲突、或主要内容落在错误 current 文档中，则 current 组不得判定为已收敛。

### 0.9.9 delta 文档骨架

```md
---
title:
summary:
status: verified
doc_role: delta
truth_role: evidence
lifecycle_state: pending_merge
default_entry: false
sync_required_when: []
retrieval_priority: evidence_only
supersedes: []
merged_into: []
current_replacement: []
related_code: []
sources: []
scope:
risks: []
updated_at:
---

## 0.1 Change

## 0.2 Evidence

## 0.3 Impact On Current

## 0.4 Merge Decision

- sync_mode:
- target_current_docs: []
- history_files_to_mark: []
- why_delta_only_allowed:
```

### 0.9.10 baseline 文档头部约束

baseline 默认不要求重写正文，但文首应明确：

- 自身属于 `doc_role: baseline`
- `truth_role: history`
- `default_entry: false`
- `retrieval_priority: reference`
- 当前是否 `partially_active / superseded / archived`
- 哪些 `overview_current / design_current / spec_current / implementation_current / validation_current` 替代了其当前入口职责
- 本文件不接受滚动式正文续写

### 0.9.11 日志模板补充字段

`run_log` 与 `audit_log` 模板在涉及文档收敛任务时，必须增加：

- `sync_mode`
- `current_updated`
- `delta_created`
- `delta_merged`
- `baseline_status_checked`
- `default_entry_verified`
- `single_pass_recoverable`

### 0.9.12 board side 存放原则

board side 信息默认属于项目工作区，而不是正式知识区。推荐放置在：

```text
02_Projects/<Project>/Board/
├── board_execution_current.md
├── board_targets/
│   └── <board_target_id>.md
├── execution_artifacts/
├── state_sync_log/
└── Archive/
```

职责分层：

- `board_execution_current.md`：描述当前板端模型、状态映射与默认执行规则
- `board_targets/<board_target_id>.md`：承接单个板端目标的连接方式、执行命令、采集路径与状态历史
- `execution_artifacts/`：存板端日志、trace、指标、录像、效果截图与外部证据索引
- `state_sync_log/`：记录 board 状态迁移与本地运行日志映射
- `Archive/`：存放关闭或废弃的板端目标快照

硬规则：

- board 记录不能替代 knowledge current 说明“系统现在是什么”
- knowledge current 不能承担单卡生命周期记录
- board evidence 可以引用 knowledge / repo 证据，但不得覆盖其真相源职责

### 0.9.13 board target 最小 frontmatter

```yaml
---
title:
summary:
status: pending_review
board_target_id:
board_type:
ssh_target:
workspace_path:
deploy_artifacts: []
run_commands: []
collect_paths: []
expected_signals: []
timeout_policy:
reset_or_recovery_steps: []
linked_repo_scope: []
linked_knowledge_scope: []
writeback_targets: []
board_state_before:
board_state_after:
board_execution_result:
repo_review_result:
knowledge_writeback_result:
board_sync_required: true
board_sync_completed: false
sources: []
updated_at:
---
```

### 0.9.14 board target 正文骨架

```md
## 0.1 Target

## 0.2 SSH / Deploy Contract

## 0.3 Linked Knowledge Current

## 0.4 Linked Repo Scope

## 0.5 Execution Artifacts

## 0.6 State Transition

- board_state_before:
- board_state_after:
- board_execution_result:
- board_failure_reason:

## 0.7 Writeback Targets

## 0.8 Audit Summary
```
