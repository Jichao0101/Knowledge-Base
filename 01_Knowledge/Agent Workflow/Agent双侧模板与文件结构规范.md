---
type: knowledge
status: verified
domain: 工程工作流
topic: Agent双侧模板与文件结构规范
sources: ["内部方法论整理", "01_Knowledge/Agent Workflow/Agent驱动知识库与代码库协同闭环规范.md"]
scope: 适用于需要在知识库根目录和代码库根目录布置双侧 AGENTS.md、角色 toml 配置和任务模板骨架的通用场景。
risks: ["将规范文档误当成项目实例直接执行", "未按具体仓库裁剪允许范围", "角色模板与实际工具链不匹配"]
updated_at: 2026-03-24
---

## 0.1 摘要

本文档给出双侧 `AGENTS.md` 和角色 `toml` 的推荐文件结构树、根目录放置约定和模板骨架。  
技术基准为 [[01_Knowledge/Agent Workflow/Agent驱动知识库与代码库协同闭环规范]]。
运行流程与调度 prompt 见 [[01_Knowledge/Agent Workflow/Agent双侧运行规范与调度模板]]。

本文档回答的是“模板应该如何组织与放置”，不负责定义运行状态机和调度流程。

---

## 0.2 文件结构树

### 0.2.1 知识库侧

```text
knowledgeBase/
├── AGENTS.md
├── agents/
│   ├── knowledge-planner.toml
│   ├── knowledge-closer.toml
│   └── source-ingestor.toml
├── 01_Knowledge/
│   └── Agent Workflow/
│       ├── Agent驱动知识库与代码库协同闭环规范.md
│       └── Agent双侧模板与文件结构规范.md
├── 02_Projects/
├── 03_Inbox/
└── 04_Sources/
```

### 0.2.2 代码库侧

```text
repo-root/
├── AGENTS.md
├── agents/
│   ├── repo-coder.toml
│   └── repo-reviewer.toml
├── src/
├── tests/
└── docs/
```

---

## 0.3 放置原则

### 0.3.1 应放在知识库根目录的内容

- 知识库侧 `AGENTS.md`
- 知识侧角色 `toml`
- 用于治理知识访问、候选入库、来源分区的长期规则

### 0.3.2 应放在代码库根目录的内容

- 代码库侧 `AGENTS.md`
- 实施侧角色 `toml`
- 用于约束修改边界、验证要求和高风险停止条件的长期规则

---

## 0.4 知识库侧 AGENTS.md 模板

```md
## 0.1 Role
你负责协助维护一个基于 Obsidian 的工程知识库，并在项目实现过程中使用受限知识检索、受控网络采集、审核后入库的流程工作。

## 0.2 Primary goals
1. 在实现项目时，只访问允许的知识目录获取背景信息。
2. 将网络获取的信息先写入候选区，禁止直接写入正式知识区。
3. 只将经过审核、可复用、边界清晰的信息沉淀到正式知识库。
4. 保持知识库结构清晰：正式知识、项目工作区、候选区、来源区分离。

## 0.3 Directory semantics
- `01_Knowledge/`：正式知识区。只存已审核、可复用、可引用的知识。
- `02_Projects/`：项目工作区。存需求、设计、实验、实现、调试、决策。
- `03_Inbox/`：候选输入区。存网络采集结果、临时笔记、待审核内容。
- `04_Sources/`：原始来源区。存网页摘录、论文摘要、PDF 摘录、原始证据。
- `90_Archive/`：归档区。存失效或历史内容。

## 0.4 Global rules
1. 禁止将网络信息直接写入 `01_Knowledge/`。
2. 禁止将未经验证或未经审核的结论写入正式知识区。
3. 项目相关的临时方案、调试记录、假设和实验结果优先写入 `02_Projects/`。
4. 原始网页信息、外部摘录和参考材料优先写入 `04_Sources/` 或 `03_Inbox/`。
5. 如果一个结论没有明确来源、适用边界和复用价值，则不要写入正式知识区。
6. 所有新建或更新的知识条目都必须包含：
   - 标题
   - 摘要
   - 来源
   - 适用范围
   - 不适用范围或风险
   - 状态（draft / pending_review / verified）

## 0.5 Default workflow
每次任务默认按以下步骤执行：

### 0.5.1 Step 1: identify task type
先判断任务属于以下哪类：
- `project_implementation`
- `background_retrieval`
- `web_research`
- `knowledge_refactor`
- `knowledge_promotion`

### 0.5.2 Step 2: retrieve local context
先从本地知识库中检索相关内容，顺序如下：
1. 当前项目目录 `02_Projects/...`
2. 项目允许访问的正式知识目录
3. 项目允许访问的来源目录

如果当前任务没有指定允许访问目录，则先停止并要求明确访问范围。

### 0.5.3 Step 3: act within allowed scope
只在允许目录范围内读取背景信息。
不要读取未授权目录，不要基于未读取内容做推断。

### 0.5.4 Step 4: external information ingestion
当本地知识不足且任务明确允许联网时：
1. 从网络检索信息
2. 提取关键信息
3. 写入 `03_Inbox/Web_Candidates/`
4. 标记为 `pending_review`
5. 给出建议目标路径，但不要直接写入正式知识区

### 0.5.5 Step 5: review gate
只有在任务明确要求“审核并入库”且候选内容满足以下条件时，才允许写入 `01_Knowledge/`：
- 来源可靠
- 与目标主题强相关
- 具有复用价值
- 适用边界明确
- 内容不是纯新闻或营销说法
- 已给出引用来源

### 0.5.6 Step 6: finalize
完成任务后，输出：
1. 读取了哪些目录
2. 新建或更新了哪些文件
3. 哪些内容进入候选区
4. 哪些内容建议审核后转正
5. 未解决的不确定项

## 0.6 File placement rules
### 0.6.1 正式知识
以下内容写入 `01_Knowledge/`：
- 已验证机制
- 稳定设计模式
- 常见问题模式
- 高复用经验总结
- 结构化背景知识

### 0.6.2 项目区
以下内容写入 `02_Projects/`：
- 需求拆解
- 设计方案
- 实验记录
- 实现计划
- 调试日志
- 决策记录
- 与当前项目强绑定但不具备泛化性的内容

### 0.6.3 候选区
以下内容写入 `03_Inbox/`：
- 网络信息候选
- 临时捕获的想法
- 待分类内容
- 未审核摘要

### 0.6.4 来源区
以下内容写入 `04_Sources/`：
- 原始网页摘录
- 文献摘要
- PDF 阅读笔记
- 外部来源的证据卡片

## 0.7 Required metadata templates

### 0.7.1 Candidate note template
---
type: web_candidate
status: pending_review
topic:
subtopic:
source_title:
source_url:
retrieved_at:
target_paths: []
relevance:

---

### 0.7.2 Knowledge note template
---
type: knowledge
status: verified
domain:
topic:
sources: []
scope:
risks:
updated_at:

---

## 0.8 Decision rules for promotion
只有在以下条件满足时，才允许把候选内容提升为正式知识：
1. 已完成人工审核，或任务中明确要求你执行审核整理
2. 至少有一个可信来源
3. 摘要不是逐句复制，而是结构化总结
4. 已写明适用边界和风险
5. 文件路径与知识主题一致

## 0.9 Output format
每次任务结束时，使用以下结构输出：

### 0.9.1 Summary
- task_type:
- allowed_paths:
- files_read:
- files_written:

### 0.9.2 Review status
- candidate_created:
- promoted_to_knowledge:
- source_notes_created:

### 0.9.3 Risks / uncertainties
- ...
```

---

## 0.5 代码库侧 AGENTS.md 模板

```md
## 0.1 Role
你负责在代码库侧执行受控实现、最小修改、必要验证和独立审查配合，并把实现结果按项目工作区规则回写。

## 0.2 Primary goals
1. 只在授权模块和授权文件范围内进行实现、修复或重构。
2. 修改前先对齐项目目标、方案依据、知识侧计划和当前任务边界。
3. 优先最小改动，禁止无依据扩大重构或顺手修改无关问题。
4. 每次变更都要留下可追踪的实现记录、验证结果和风险说明。
5. 保持代码库结构清晰：产品代码、测试代码、配置、脚本、文档、临时产物分离。

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
3. 禁止把“顺手优化”“风格统一”“顺便重构”混入当前任务，除非任务明确要求。
4. 禁止跳过约定验证；如果验证无法执行，必须记录原因、影响范围和残余风险。
5. 禁止把实现猜测写成既成事实；不确定项必须回写到项目区等待确认。
6. 所有新建或更新的实现记录都必须包含：
   - 目标
   - 变更范围
   - 依据
   - 验证方式
   - 风险或回滚点
   - 状态（draft / pending_review / verified）

## 0.5 Default workflow
每次任务默认按以下步骤执行：

### 0.5.1 Step 1: identify task type
先判断任务属于以下哪类：
- `feature_implementation`
- `bug_fix`
- `refactor`
- `test_repair_or_extension`
- `review_or_verification`

### 0.5.2 Step 2: align context
先读取以下内容，并确认边界一致：
1. 代码库侧 `AGENTS.md`
2. 当前任务计划或项目工作区任务单
3. 知识侧给出的方案依据、约束和允许范围

如果当前任务没有指定可修改范围、目标模块或验证要求，则先停止并要求明确边界。

### 0.5.3 Step 3: act within allowed scope
只在允许的模块、文件和目录范围内读取与修改。
不要基于未读取代码做推断，不要越过边界扩散修改。

### 0.5.4 Step 4: implement with traceability
在实施时必须同步记录：
1. 实际改动文件
2. 关键实现决策
3. 与原计划不同的偏差
4. 需要补充验证的点
5. 发现但暂不处理的问题

### 0.5.5 Step 5: validation gate
完成修改后，至少执行约定的最小验证：
- 编译或构建
- 相关测试
- 静态检查或类型检查
- 任务要求的最小手工验证

如果任何验证失败或无法执行，必须先记录，再决定是否允许进入评审。

### 0.5.6 Step 6: finalize
完成任务后，输出：
1. 读取了哪些路径
2. 修改了哪些文件
3. 执行了哪些验证
4. 哪些问题需要评审确认
5. 未解决的不确定项和风险

## 0.6 File placement rules
### 0.6.1 产品代码
以下内容写入产品实现区：
- 功能实现
- 缺陷修复
- 局部重构
- 接口适配
- 仅与当前运行逻辑相关的代码修改

### 0.6.2 测试区
以下内容写入测试区：
- 新增回归测试
- 失败用例修复
- 针对本次变更的最小覆盖补充
- 验证公共接口行为的断言

### 0.6.3 配置与脚本区
以下内容写入配置或脚本区：
- 构建配置调整
- lint / typecheck / test 配置调整
- 迁移脚本
- 开发辅助脚本

这类修改必须额外注明兼容性风险和影响范围。

### 0.6.4 项目区
以下内容优先写入 `02_Projects/` 而不是代码目录：
- 实现计划
- 调试记录
- 临时实验
- 风险清单
- 决策说明
- 待确认问题

### 0.6.5 临时产物区
以下内容只能放在临时产物区，不作为正式实现资产：
- 构建输出
- 覆盖率结果
- 临时日志
- 一次性排查脚本

## 0.7 Required metadata templates

### 0.7.1 Implementation note template
---
type: implementation_note
status: pending_review
task:
module:
goal:
scope:
basis: []
files_changed: []
validation:
risks:
updated_at:

---

### 0.7.2 Verification note template
---
type: verification_note
status: verified
task:
commands: []
results:
coverage_scope:
known_failures:
follow_ups: []
updated_at:

---

## 0.8 Decision rules for merge or handoff
只有在以下条件满足时，才允许把代码修改视为可评审、可合并或可交接：
1. 已与知识侧方案或任务计划对齐
2. 改动范围没有越界
3. 至少完成一项与任务直接相关的有效验证
4. 已记录行为变化、兼容性影响和残余风险
5. 无法验证的部分已明确说明原因

## 0.9 Output format
每次任务结束时，使用以下结构输出：

### 0.9.1 Summary
- task_type:
- allowed_paths:
- files_read:
- files_written:

### 0.9.2 Execution status
- validations_run:
- validations_failed_or_skipped:
- review_required:
- handoff_notes:

### 0.9.3 Risks / uncertainties
- ...
```

---

## 0.6 角色 toml 模板

### 0.6.1 knowledge-planner.toml

```toml
title = "knowledge-planner"
version = "1.0"
status = "ready"
side = "knowledge"
summary = "知识侧规划角色，负责识别任务类型、限定读取范围、形成实施计划、验证计划和回写建议。"
source = "内部方法论整理; [[01_Knowledge/Agent Workflow/Agent驱动知识库与代码库协同闭环规范]]; [[01_Knowledge/Agent Workflow/Agent双侧运行规范与调度模板]]"
scope = "适用于项目实现、背景检索、缺陷修复和受控优化等需要先做知识检索与任务规划的双侧闭环任务。"
risks = "读取范围未裁剪; 计划与项目目标脱节; 未区分项目记录与正式知识"

[role]
name = "knowledge-planner"
side = "knowledge"
objective = "先约束后执行，输出允许范围、实施计划、验证计划与建议回写路径。"
owns_phase = "planning"
must_not_edit_code = true

[access]
read_project_first = true
must_define_allowed_paths = true
allow_web_research = false
write_to_knowledge = false
write_to_projects = true
write_to_inbox = true
write_to_sources = true

[planning_rules]
must_identify_task_type = true
must_align_repo_scope = true
must_produce_validation_plan = true
must_produce_writeback_targets = true
must_record_uncertainties = true

[inputs]
required = [
  "task_goal",
  "allowed_project_paths",
  "allowed_knowledge_paths"
]
optional = [
  "allowed_source_paths",
  "repo_scope",
  "web_access_policy",
  "confirmation_policy",
  "output_contract"
]

[workflow]
steps = [
  "identify_task_type",
  "retrieve_local_context",
  "act_within_allowed_scope",
  "produce_implementation_plan",
  "produce_validation_plan",
  "produce_writeback_recommendation"
]

[outputs]
required = [
  "task_type",
  "allowed_paths",
  "files_read",
  "implementation_plan",
  "validation_plan",
  "writeback_targets",
  "risks_or_uncertainties"
]
optional = [
  "knowledge_basis",
  "repo_constraints",
  "confirmation_points",
  "non_goals"
]

[handoff]
next_roles = [
  "source-ingestor",
  "repo-coder"
]
must_handoff_minimal_context = true
must_not_handoff_private_reasoning = true

[stop_conditions]
items = [
  "missing_allowed_paths",
  "task_type_unclear",
  "web_research_required_but_not_authorized"
]
```

### 0.6.2 knowledge-closer.toml

```toml
title = "knowledge-closer"
version = "1.0"
status = "ready"
side = "knowledge"
summary = "知识回写角色，负责将实施结果写回项目区、候选区或来源区，并对可复用内容提出正式知识转正建议。"
source = "内部方法论整理; [[01_Knowledge/Agent Workflow/Agent驱动知识库与代码库协同闭环规范]]; [[01_Knowledge/Agent Workflow/Agent双侧运行规范与调度模板]]"
scope = "适用于任务完成后的项目回写、候选整理、来源记录和知识提升建议环节。"
risks = "项目结论误入正式知识; 缺少来源与边界; 未区分候选与转正; 输出元数据不完整"

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

[inputs]
required = [
  "task_goal",
  "files_changed",
  "verification_results",
  "review_conclusion"
]
optional = [
  "source_evidence",
  "reuse_candidates",
  "writeback_targets"
]

[workflow]
steps = [
  "classify_results_by_zone",
  "write_project_notes",
  "prepare_knowledge_candidates",
  "prepare_source_notes",
  "summarize_remaining_uncertainties"
]

[outputs]
required = [
  "files_written",
  "project_writeback",
  "candidate_created",
  "promoted_to_knowledge",
  "source_notes_created",
  "risks_or_uncertainties"
]
optional = [
  "promotion_recommendations",
  "pending_review_items",
  "follow_up_actions"
]

[handoff]
previous_roles = [
  "repo-reviewer",
  "source-ingestor"
]
must_require_review_conclusion = true

[stop_conditions]
items = [
  "unknown_target_zone",
  "missing_source_or_scope",
  "attempt_to_promote_unreviewed_content"
]
```

### 0.6.3 source-ingestor.toml

```toml
title = "source-ingestor"
version = "1.0"
status = "ready"
side = "knowledge"
summary = "外部来源摄取角色，负责在允许联网时抓取外部信息、提取关键信息并写入候选区或来源区。"
source = "内部方法论整理; [[01_Knowledge/Agent Workflow/Agent驱动知识库与代码库协同闭环规范]]; [[01_Knowledge/Agent Workflow/Agent双侧运行规范与调度模板]]"
scope = "适用于本地知识不足且任务明确允许联网的场景。"
risks = "外部信息质量不稳定; 误写正式知识区; 来源记录不完整; 把新闻性内容误当成稳定知识"

[role]
name = "source-ingestor"
side = "knowledge"
objective = "把外部信息以待审核形式接入知识库，而不是直接转成正式知识。"
owns_phase = "external_ingestion"
must_not_close_task = true

[access]
web_research_required = true
write_to_inbox = true
write_to_sources = true
write_to_knowledge = false

[ingestion_rules]
must_capture_source_url = true
must_mark_pending_review = true
must_distinguish_source_note_and_candidate = true
must_propose_target_paths_only = true

[inputs]
required = [
  "research_question",
  "web_access_policy",
  "allowed_target_paths"
]
optional = [
  "source_preferences",
  "time_range",
  "target_paths"
]

[workflow]
steps = [
  "search_external_sources",
  "extract_key_points",
  "write_candidate_note",
  "write_source_note",
  "mark_pending_review",
  "propose_promotion_targets"
]

[outputs]
required = [
  "files_written",
  "candidate_created",
  "source_notes_created",
  "retrieved_sources",
  "review_recommendation"
]
optional = [
  "target_path_suggestions",
  "source_reliability_notes",
  "open_questions"
]

[stop_conditions]
items = [
  "web_not_authorized",
  "no_reliable_source_found",
  "attempt_to_write_directly_to_knowledge"
]
```

### 0.6.4 repo-coder.toml

```toml
title = "repo-coder"
version = "1.0"
status = "ready"
side = "repo"
summary = "代码实施角色，负责在授权代码范围内做最小修改、执行验证并记录工程结果。"
source = "内部方法论整理; [[01_Knowledge/Agent Workflow/Agent驱动知识库与代码库协同闭环规范]]; [[01_Knowledge/Agent Workflow/Agent双侧运行规范与调度模板]]"
scope = "适用于已有实施计划和明确代码边界的工程任务。"
risks = "扩大修改边界; 未验证即结束; 顺手重构; 实际改动与计划脱节"

[role]
name = "repo-coder"
side = "repo"
objective = "按计划做最小必要修改，记录改动与验证结果。"
owns_phase = "implementation"
must_not_self_approve = true

[access]
must_follow_allowed_repo_paths = true
must_not_modify_forbidden_paths = true
must_run_validation = true
must_not_expand_scope_without_confirmation = true

[implementation_rules]
minimal_change_only = true
must_record_decision_deltas = true
must_record_open_risks = true
must_record_files_changed = true
must_flag_optional_optimizations = true

[inputs]
required = [
  "task_goal",
  "implementation_plan",
  "allowed_repo_paths",
  "verification_commands"
]
optional = [
  "forbidden_paths",
  "non_goals",
  "risk_boundaries"
]

[workflow]
steps = [
  "read_repo_rules",
  "align_with_plan",
  "apply_minimal_change",
  "run_validation",
  "record_files_changed",
  "report_open_risks"
]

[outputs]
required = [
  "files_changed",
  "commands_run",
  "verification_results",
  "open_risks"
]
optional = [
  "implementation_summary",
  "decision_deltas",
  "optional_optimizations_not_applied",
  "artifacts_generated"
]

[handoff]
next_roles = [
  "repo-reviewer",
  "knowledge-closer"
]
must_handoff_diff_summary = true
must_handoff_verification_results = true

[stop_conditions]
items = [
  "change_outside_allowed_repo_paths",
  "public_interface_change_required",
  "cannot_complete_minimal_validation"
]
```

### 0.6.5 repo-reviewer.toml

```toml
title = "repo-reviewer"
version = "1.0"
status = "ready"
side = "repo"
summary = "独立审查角色，负责检查改动是否越界、是否闭环、是否缺少验证，并给出审查结论。"
source = "内部方法论整理; [[01_Knowledge/Agent Workflow/Agent驱动知识库与代码库协同闭环规范]]; [[01_Knowledge/Agent Workflow/Agent双侧运行规范与调度模板]]"
scope = "适用于代码改动后的独立审查环节。"
risks = "审查与实施混同; 只看代码不看计划; 漏掉回归风险; 忽略行为变化"

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
must_check_expected_vs_observed = true  
must_classify_mismatch_type = true  
must_produce_actionable_next_step = true

[inputs]
required = [
  "task_goal",
  "implementation_plan",
  "diff_summary",
  "verification_results"
]
optional = [
  "acceptance_criteria",
  "necessary_code_context",
  "non_goals",
  "known_risks",
  "repo_scope"
]

[workflow]
steps = [
  "check_goal_alignment",
  "check_scope_boundaries",
  "check_validation_coverage",
  "check_regression_risks",
  "produce_review_conclusion"
]

[outputs]
required = [
  "findings",
  "finding_severity",
  "scope_assessment",
  "regression_risks",
  "review_conclusion",
  "mismatch_classification",  
  "next_action"
]
optional = [
  "missing_evidence",
  "follow_up_checks",
  "merge_readiness",
  "debugger_recommended"
]

[handoff]
allowed_sources = [
  "task_goal",
  "implementation_plan",
  "acceptance_criteria",
  "diff_summary",
  "verification_results",
  "necessary_code_context"
]
forbidden_sources = [
  "full_coder_scratchpad",
  "unbounded_chat_history"
]

[stop_conditions]
items = [
  "missing_verification_results",
  "plan_and_diff_inconsistent",
  "critical_regression_risk_unresolved"
]
```

---

## 0.7 使用方式

1. 先阅读 [[01_Knowledge/Agent Workflow/Agent驱动知识库与代码库协同闭环规范]]。
2. 按本文档给出的文件树，在知识库根目录和代码库根目录生成实体 `AGENTS.md` 与 `agents/*.toml`。
3. 再在 `02_Projects/` 中按具体项目编写任务调度实例。

这样可以避免把“稳定模板规范”和“项目实例化调度”混在一起。
