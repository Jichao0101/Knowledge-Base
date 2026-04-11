---
type: knowledge
status: verified
domain: 工程工作流
topic: Agent三侧运行规范与调度模板
sources: ["内部方法论整理", "01_Knowledge/Agent Workflow/Agent驱动知识库、代码库与板端侧协同闭环规范.md", "01_Knowledge/Agent Workflow/Agent三侧模板与文件结构规范.md"]
scope: 适用于需要将三侧闭环规则包装成可运行流程，包括板端目标绑定、状态推进、调度 prompt、角色输入输出契约与回写要求的场景。
risks: ["运行规范过重导致单次任务负担过大", "板端执行被退化为附属说明", "项目特例被误提升为通用步骤", "角色契约与实际工具链不一致", "扩展角色加入后模板不同步导致制度与运行脱节"]
updated_at: 2026-04-07
---

## 0.1 摘要

本文档定义三侧闭环的运行层，回答“系统怎么跑起来”。
它承接任务入口、状态门禁、角色调度、返工升级、日志记录和 prompt 模板。

---

## 0.2 方案评价

三层文档的分工如下：

- 上位规范：制度、边界、门槛
- 运行规范：状态机、调度、返工、模板
- 文件结构规范：文件树、骨架、字段

---

## 0.3 任务入口

每个任务在进入系统时，至少要明确以下输入对象：

- `task_goal`：本轮目标
- `board_target`：若任务包含上板环节，则其为板端执行入口
- `primary_type`：主类型
- `task_modifiers`：修饰属性集合
- `allowed_paths`：允许读取与写入的目录
- `repo_scope`：代码库允许修改范围
- `confirmation_policy`：哪些步骤需要确认
- `output_contract`：需要交付哪些结果
- `verification_tier`：本轮要求的验证等级

### 0.3.1 板端入口原则

- 若任务包含智驾芯片板端测试，则必须显式给出 `board_target`
- `knowledge-planner` 必须先解析 `board_target`，再生成 knowledge / repo 侧计划
- 没有板端执行时，必须显式声明 `no_board_execution`
- 任何 `implementation / incident_investigation / bug_fix / optimization / functional_tuning` 任务，只要要求上板验证，不得绕过板端直接判定闭环完成

### 0.3.2 标准任务表达

正式入口统一使用“主类型 + 修饰属性”：

- `primary_type`: `implementation / incident_investigation / bug_fix / audit / optimization / knowledge_task`
- `task_modifiers`: `requires_web / read_only / code_change_allowed / writeback_required / review_required / promotion_review / functional_scope / failure_investigation / board_execution_required / no_board_execution / board_artifact_collection_required`

常见组合：

- 背景检索：`knowledge_task` + `read_only`
- 联网研究：`knowledge_task` + `requires_web` + `read_only`
- 项目实现：`implementation` + `code_change_allowed` + `review_required`
- 板端调查：`incident_investigation` + `failure_investigation` + `review_required` + `board_artifact_collection_required`
- 缺陷修复：`bug_fix` + `code_change_allowed` + `review_required`
- 受控优化：`optimization` + `code_change_allowed` + `review_required`
- 板端实现：`implementation` + `code_change_allowed` + `review_required` + `board_execution_required` + `board_artifact_collection_required`
- 功能审核：`audit` + `functional_scope` + `read_only`
- 知识提升：`knowledge_task` + `promotion_review` + `writeback_required`

### 0.3.3 进入条件

任务启动前必须满足：

- 已给出目标
- 若要求板端执行，已给出 `board_target` 与最小执行字段
- 已给出知识库允许访问范围
- 若涉及代码修改，已给出代码库修改范围
- 若允许联网，已明确联网权限
- 已给出或可推导 `verification_tier`

若上述条件缺失，应先补全条件，而不是直接执行。

### 0.3.4 0.3.3A board-first 正式入口模式

当任务的已知信息主要来自板端现象、日志、trace、指标、视频、dump 或错误码，而不是人工已定义清楚的问题说明时，应使用 `primary_type = incident_investigation`。

`incident_investigation` 是与 plan-first 并列的正式入口模式，不是 `bug_fix` 的附属说明。  
它负责先完成：

- 现象归档
- artifacts 绑定
- 证据裁剪
- 异常聚类
- 根因假设生成
- 问题分类
- 路由决策

再决定是否转入既有 `bug_fix / optimization / audit` 主链。

该主类型不要求任务一开始就具备：

- `expected_behavior`
- `actual_behavior`
- `acceptance_criteria`
- `fix_plan`
- `optimization_basis`

但要求具备最小调查入口对象：

- `observed_symptoms`
- `artifact_inventory`
- `log_sources`
- `trigger_condition`
- `reproduction_confidence`
- `signal_expectations`
- `environment_fingerprint`
- `board_session_info`
- `anomaly_window`
- `issue_scope_guess`
- `available_evidence`
- `missing_evidence`
- `whether_design_expectation_known`

若 investigation 完成后形成稳定分类，再转入既有主链；若结论为 `insufficient_evidence / board_environment_issue / design_mismatch / missing_observability`，允许不进入代码修复。

### 0.3.5 board execution contract

每个正式进入三侧闭环的 `board_target` 至少应包含：

- `board_target_id`
- `board_type`: `chip_board | vehicle_controller | simulator_board | other_embedded_target`
- `ssh_target`
- `workspace_path`
- `deploy_artifacts`
- `run_commands`
- `collect_paths`
- `expected_signals`
- `timeout_policy`
- `reset_or_recovery_steps`
- `linked_repo_scope`
- `linked_knowledge_scope`
- `writeback_targets`

派生规则：

- 若存在 `board_target`，则 `task_goal`、`repo_scope`、`allowed_paths`、`verification_tier` 与 `artifact_expectations` 应优先从板端合同派生，再由 planner 收敛
- 只有 `knowledge_task + read_only` 或显式声明的 `no_board_execution` 任务，允许脱离板端执行
- `run_log / audit_log` 的摘要字段应可映射回 `board_target` 的执行状态、采集结果与失败原因

---

## 0.4 运行状态机

标准状态推进如下：

1. `task_received`
2. `scope_confirmed`
3. `board_bound`
4. `context_retrieved`
5. `plan_ready`
6. `execution_approved`
7. `implementation_done`
8. `board_executed`
9. `repo_review_done`
10. `knowledge_sync_checked`
11. `convergence_ready`
12. `rework_needed`（条件态）
13. `writeback_done`
14. `board_sync_done`
15. `closed`

当 `primary_type = incident_investigation` 时，在 `context_retrieved` 与 `plan_ready` 之间插入 investigation 前置状态：

1. `symptom_received`
2. `artifact_bound`
3. `evidence_collected`
4. `triage_ready`
5. `hypothesis_generated`
6. `classification_decided`
7. `routed_to_bug_fix | routed_to_optimization | routed_to_audit | routed_to_env_issue | investigation_closed`

### 0.4.1 状态说明

#### 0.4.1.1 `task_received`

接收任务目标，判断是否信息不足。

#### 0.4.1.2 `scope_confirmed`

确认 knowledge、repo 与 board 侧允许范围。

#### 0.4.1.3 `board_bound`

确认是否存在 `board_target`，并完成板端入口绑定、字段解析、连通性前置检查或“无板端执行”说明。

#### 0.4.1.4 `context_retrieved`

完成项目区、正式知识区、来源区的受控检索。

#### 0.4.1.5 0.4.1.4A investigation 前置状态

当 `primary_type = incident_investigation` 时，不直接从 `context_retrieved` 进入 `plan_ready`，而是先经过以下状态：

- `symptom_received`：已接收板端现象与最小调查入口对象
- `artifact_bound`：已绑定本轮调查使用的 artifacts、日志来源、异常时间窗与环境指纹
- `evidence_collected`：已完成最小证据采集、去噪与裁剪，能够形成可审查证据包
- `triage_ready`：已完成现象归档、异常聚类、信息缺口识别与 probe 优先级排序
- `hypothesis_generated`：已生成至少一个可检验假设，并附带支持与反证证据
- `classification_decided`：已形成问题分类、route decision、route blockers

只有到达 `classification_decided` 且通过以下门禁后，才允许进入既有 `plan_ready`：

- `evidence_sufficiency != insufficient`
- `route_correctness != unresolved`
- `classification_confidence != low`
- 若拟转 `bug_fix / optimization`，则 `whether_design_expectation_known != unknown`
- 若 `reproduction_confidence = one_off`，则必须存在高价值确定性证据，否则应停留在 investigation 或关闭

#### 0.4.1.6 `plan_ready`

输出实施计划、验证计划、回写路径和不确定项。

进入条件：

- 已有 `primary_type`
- 已有 `task_modifiers`
- 若 `board_execution_required`，已解析 `board_target`
- 已有 `allowed_paths`
- 若涉及代码，已有 `repo_scope`
- 已有 `implementation_plan`
- 已有 `verification_plan`
- 已有 `board_execution_plan`
- 已有 `non_goals`
- 已有 `open_uncertainties`
- 已有 `verification_tier`

阻断条件：

- 允许范围不清
- 板端入口存在但未解析
- 任务语义混杂
- 非目标项缺失
- 验证集合未区分 `required / optional / unavailable`

#### 0.4.1.7 `execution_approved`

若任务要求确认，则在此节点停下；若无需确认，可继续执行。

#### 0.4.1.8 `implementation_done`

代码修改、知识整理或外部信息采集已完成。

进入条件：

- 已记录 `files_changed` 或明确无代码改动
- 已记录 `commands_run`
- 已记录 `verification_results`
- 已记录 `decision_deltas`
- 已记录 `open_risks`
- 若 `board_execution_required`，已记录 `board_execution_artifacts`
- 如存在，已记录 `optional_optimizations`

阻断条件：

- 验证结果缺失
- 实施偏差未记录
- 风险未展开
- 变更已触发 `scope_creep_trigger`

#### 0.4.1.9 `board_executed`

完成板端部署、运行、日志采集与效果产物收集。

进入条件：

- 若 `board_execution_required`，已记录 `board_state_before`
- 已记录 `board_state_after`
- 已记录 `board_run_commands`
- 已记录 `board_execution_artifacts`
- 若失败，已记录 `board_failure_reason`

阻断条件：

- 要求上板但没有执行记录
- 产物采集缺失
- 板端失败但未给出失败原因

#### 0.4.1.10 `repo_review_done`

完成 repo 侧独立审查，确认改动是否满足实现目标、范围与验证要求。

进入条件：

- 已记录 `repo_review_result`
- 已记录 `findings`
- 已记录 `finding_severity`
- 已记录 `next_action`
- 已记录 `fix_owner`
- 若 `board_execution_required`，已记录 `board_effect_assessment`

阻断条件：

- 关键验证缺失
- 板端证据缺失但仍试图下结论
- 审查输入未裁剪
- reviewer 独立性破坏

#### 0.4.1.11 `knowledge_sync_checked`

完成 `knowledge_sync_check`，并输出强制同步决议，确认本轮变化是否要求同步更新 `current / delta / adr / 状态头 / default_entry`。

进入条件：

- 已评估设计、实现、接口、约束或状态机是否发生变化
- 已输出 `sync_mode: current_rewrite | current_patch | delta_only | adr_only`
- 已输出 `current_files_must_update`
- 已输出 `history_files_to_mark`
- 若 `sync_mode = delta_only`，已输出 `why_delta_only_allowed`

阻断条件：

- 变化已触发文档失配但未给出同步决策
- 明显只追加 delta 而未判断 current 是否过期
- 使用 `delta_only` 但未给出举证
- 需要更新的 current 未列入同步决议

#### 0.4.1.12 `convergence_ready`

确认 writeback 后当前态可被单次恢复，历史文档不会继续与 current 竞争主入口。

进入条件：

- 已确认 current 是否足以恢复当前主要设计
- 已确认历史文档完成最小状态标记
- 已确认默认检索顺序不会优先命中 superseded baseline
- 已确认 `default_entry` 与 `retrieval_priority` 已校验
- 已确认 `single_pass_recoverable = true`

阻断条件：

- 仍需依赖 baseline + 多篇 delta 才能恢复当前态
- 历史文档未做最小状态映射
- current 缺少关键主题
- 仍存在应降级但未降级的 baseline / delta
- default entry 仍指向 baseline 或 delta

#### 0.4.1.13 `rework_needed`

repo review 已基于代码、日志和板端效果证据给出需要修改的发现，任务返回实施环节，等待原 `repo-coder` 返工并重新验证。

#### 0.4.1.14 `writeback_done`

结果已按分区规则写回项目区、候选区或来源区。

进入条件：

- 已记录 `files_written`
- 已记录 `target_zone`
- 已记录 `candidate_created / promoted_to_knowledge / source_notes_created`
- 已记录 `pending_items`
- 已记录 `residual_risks`
- 若 `board_execution_required`，已记录 `board_sync_required`
- 已记录 `sync_mode`
- 已记录 `current_updated`
- 已记录 `delta_created`
- 已记录 `delta_merged`
- 已记录 `baseline_status_checked`
- 已记录 `default_entry_verified`
- 已记录 `single_pass_recoverable`

阻断条件：

- 未通过 review
- 板端执行任务缺少 repo review 效果结论
- 写回分区不明
- 未审内容拟写入正式知识区
- 缺少来源与边界
- 需要更新的 current 未更新
- 新增 delta 但未说明为何允许 `delta_only`
- 历史文档未标记 `merged_into / supersedes / lifecycle_state`
- `default_entry` 未校验
- `single_pass_recoverable = false`

#### 0.4.1.15 `board_sync_done`

完成板端结果回写，确认状态、日志摘要、效果评估与失败信息已同步。

进入条件：

- 若 `board_execution_required`，已记录 `board_sync_completed = true`
- 已记录 `board_state_after`
- 已记录 `repo_review_result`

阻断条件：

- 需要回填板端但未执行
- 板端状态与本地结论冲突

#### 0.4.1.16 `closed`

形成最终摘要与残留风险列表。

---

### 0.4.2 板端状态机与三侧映射

板端侧至少应支持以下状态或等价抽象：

- `board_ready`
- `package_deployed`
- `running`
- `artifacts_collected`
- `analyzed`
- `failed`
- `completed`

默认映射规则：

- `board_ready`
  - repo 侧：已完成实施计划，尚未部署
  - knowledge 侧：允许只有板端准备约束，不允许写入效果结论
- `package_deployed`
  - repo 侧：构建产物已准备并已部署到板端
  - knowledge 侧：允许记录部署方式与运行前约束
- `running`
  - repo 侧：`repo-coder` 已触发板端运行，尚未完成产物采集
  - knowledge 侧：允许记录中间观察与运行异常
- `artifacts_collected`
  - repo 侧：日志、trace、指标、录像或效果产物已回收
  - knowledge 侧：允许更新 `validation_current` 或等价验证记录，但不得判定闭环完成
- `analyzed`
  - repo 侧：`repo-reviewer` 已基于板端证据完成效果分析
  - knowledge 侧：允许进入 knowledge sync、writeback 与候选沉淀
- `failed`
  - repo 侧：必须回到原 `repo-coder` 返工
  - knowledge 侧：允许记录 `board_failure_reason`、失败证据和未闭环事项
- `completed`
  - repo 侧：不再存在待返工 blocker
  - knowledge 侧：`writeback_done` 与 `board_sync_done` 都已完成

强制状态切换规则：

- `board_ready -> package_deployed` 需要板端合同字段完整并完成 planner 收敛
- `package_deployed -> running` 需要 `execution_approved`
- `running -> artifacts_collected` 需要 `board_executed`
- `artifacts_collected -> analyzed` 需要 `repo_review_done`
- 任一执行阶段到 `failed` 需要明确 `board_failure_reason`
- `analyzed -> completed` 需要 `writeback_done` 与 `board_sync_done`

必须回写板端记录的状态切换：

- 进入 `package_deployed`
- 进入 `running`
- 进入 `artifacts_collected`
- 进入 `analyzed`
- 进入 `failed`
- 进入 `completed`

repo review 与板端执行的关系：

- 板端已运行不等于质量已通过
- `repo-reviewer` 负责汇总代码验证、板端日志分析和效果评估，形成最终结论
- knowledge writeback 完成不等于板端侧已完成，必须完成板端同步

---

## 0.5 主代理调度契约与子代理调用顺序

### 0.5.1 主代理调度契约

在三侧闭环任务中，Codex 主代理默认承担 `workflow-orchestrator` 职责。

主代理负责：

- 接收任务
- 识别 `primary_type`
- 识别 `task_modifiers`
- 检查进入条件
- 维护状态对象
- 决定是否调用子代理
- 裁剪子代理输入
- 控制 reviewer 独立性
- 控制返工轮次
- 决定 `stop / confirm / replan / escalate / close`
- 汇总最终输出
- 维护 `run_log / audit_log`

主代理默认不得：

- 直接修改代码
- 直接替代 reviewer 做质量裁决
- 绕过 review 直接进入 knowledge writeback
- 把未审内容直接写入正式知识区

### 0.5.2 主代理对子代理的默认调用顺序

以下顺序描述的是主代理在 orchestration 模式下对子代理的默认调用顺序。  
`workflow-orchestrator` 默认由主代理承担，不作为普通子代理列入调用链。

默认子代理顺序：

1. `knowledge-planner`
2. `repo-coder`
3. `repo-reviewer`
4. `knowledge-closer`

条件分支：

- 若本地知识不足且允许联网：插入 `source-ingestor`，并在其后重新经过 `knowledge-planner` 收敛计划
- 若 `primary_type = incident_investigation`：在 `knowledge-planner` 之后优先插入 `failure-analyst`，必要时再调用 `repo-coder` 做 instrumentation / probe / capture，再进入 `repo-reviewer`
- 若 `primary_type = bug_fix` 且根因复杂：可插入 `failure-analyst`
- 若为高风险任务或验证矩阵复杂：可插入 `verification-manager`
- 若为功能符合度审核：可使用 `functional-reviewer` 补充 `repo-reviewer`
- 若任务涉及正式知识提升审查：可插入 `knowledge-auditor`
- 若显式声明 `no_board_execution`：可跳过板端执行，但必须记录原因

### 0.5.3 reviewer 独立性要求

为降低上下文污染，`repo-reviewer` 或 `functional-reviewer` 的调度应满足：

1. 使用独立的 reviewer 实例或独立会话阶段。
2. 输入尽量裁剪为任务目标、验收标准、实施计划、diff、验证结果和必要代码上下文。
3. 不默认传入 `repo-coder` 的完整自然语言推理、排查草稿或无界历史对话。
4. reviewer 只负责质量判定，不负责直接修改代码或提前执行知识回写。

### 0.5.4 coder 到 reviewer 的最小交接包

推荐交给 reviewer 的最小材料为：

- `task_goal`
- `acceptance_criteria`
- `implementation_plan`
- `diff_summary`
- `verification_results`
- `necessary_code_context`
- `verification_tier`
- 若涉及板端执行，再补 `board_target`、`board_state_before`、`board_run_commands`、`board_execution_artifacts`

若无法构造上述最小交接包，应视为审查前置条件不足，而不是让 reviewer 继承全量执行上下文。

### 0.5.5 review 后返工责任

默认规则：

1. reviewer 负责判定，不负责修改。
2. 若审查结论要求代码变更，返工责任默认归原 `repo-coder`。
3. 若板端执行失败或效果不达标，返工责任同样默认归原 `repo-coder`。
4. 主代理负责调度、裁剪审查结论、维持状态机，不直接吸收返工实现。
5. 只有当原 coder 不可恢复、连续返工不收敛或返工已超出授权范围时，才切换修复责任人或回到 planner。

推荐返工交接包：

- `review_conclusion`
- `findings`
- `finding_severity`
- `next_action`
- `affected_files`
- `verification_gaps`
- `board_failure_reason`

循环控制要求：

- 默认保留原 coder 会话直到审查通过或明确终止
- 每轮返工后必须重新执行受影响验证
- 每轮返工后必须再次使用独立 reviewer；若涉及板端执行，也必须重新收集受影响板端证据
- 连续返工超过 2 轮时，默认升级为重新规划或人工确认

---

## 0.6 子代理调用矩阵

### 0.6.1 `knowledge_task + read_only`

- 主代理职责：确认允许范围、裁剪检索目标、维护轻量状态与输出
- 必须显式调用的子代理：`knowledge-planner`
- 条件启用的子代理：`source-ingestor`
- 可被主代理轻量吸收的职责：最终汇总、轻量 writeback 建议

### 0.6.2 `knowledge_task + requires_web + read_only`

- 主代理职责：确认联网授权、限定候选落区、控制不进入正式知识
- 必须显式调用的子代理：`knowledge-planner`、`source-ingestor`
- 条件启用的子代理：`knowledge-auditor`
- 可被主代理轻量吸收的职责：候选整理摘要

### 0.6.3 `implementation + code_change_allowed + review_required`

- 主代理职责：维护状态机、控制默认链路与返工轮次
- 必须显式调用的子代理：`knowledge-planner`、`repo-coder`、`repo-reviewer`、`knowledge-closer`
- 条件启用的子代理：`source-ingestor`、`verification-manager`
- 可被主代理轻量吸收的职责：轻量确认点判断

若为 `board_execution_required`，必须执行上板运行、产物采集和基于板端证据的 `repo-reviewer` 分析，缺一不可。

### 0.6.4 `bug_fix + code_change_allowed + review_required`

- 主代理职责：确认预期行为、实际行为与根因路径是否充分
- 必须显式调用的子代理：`knowledge-planner`、`repo-coder`、`repo-reviewer`、`knowledge-closer`
- 条件启用的子代理：`failure-analyst`、`source-ingestor`、`verification-manager`
- 可被主代理轻量吸收的职责：返工轮次控制

若为 `board_execution_required`，必须增加板端执行与日志采集步骤。

### 0.6.5 0.6.4A `incident_investigation + review_required`

- 主代理职责：维护 investigation 状态机、控制 triage 门禁、控制 route decision、控制 reviewer 独立性
- 必须显式调用的子代理：`knowledge-planner`、`failure-analyst`、`repo-reviewer`、`knowledge-closer`
- 条件启用的子代理：`repo-coder`、`verification-manager`、`source-ingestor`
- 可被主代理轻量吸收的职责：调查摘要编排、route decision 汇总

该模式默认不要求先改代码。  
若 investigation 需要补采样、补 trace、补日志或复现实验，可调用 `repo-coder` 做 instrumentation 或 probe，但不默认进入业务修复。

### 0.6.6 `optimization + code_change_allowed + review_required`

- 主代理职责：控制不演化为结构性重构，维护收益验证门禁
- 必须显式调用的子代理：`knowledge-planner`、`repo-coder`、`repo-reviewer`、`knowledge-closer`
- 条件启用的子代理：`verification-manager`、`source-ingestor`
- 可被主代理轻量吸收的职责：收益对比摘要

若为 `board_execution_required`，必须增加板端执行与日志采集步骤。

### 0.6.7 `audit + functional_scope + read_only`

- 主代理职责：确认规范来源、证据优先级与只读边界
- 必须显式调用的子代理：`knowledge-planner`、`functional-reviewer`
- 条件启用的子代理：`source-ingestor`、`knowledge-closer`
- 可被主代理轻量吸收的职责：验收条目整理

若审核对象同时要求板端效果评估，则 `functional-reviewer` 只负责规范符合度，不替代 `repo-reviewer` 基于板端证据做最终裁决。

### 0.6.8 `knowledge_task + promotion_review + writeback_required`

- 主代理职责：确认候选来源、边界、风险与证据链
- 必须显式调用的子代理：`knowledge-closer`
- 条件启用的子代理：`knowledge-auditor`、`source-ingestor`
- 可被主代理轻量吸收的职责：候选汇总、转正建议编排

---

## 0.7 verification_tier

### 0.7.1 分级定义

- `V0`：仅要求文档核对、结构检查或知识整理一致性校验
- `V1`：要求最小功能验证或最小复现验证
- `V2`：要求受影响范围回归验证，包含相关测试、静态检查或集成验证
- `V3`：要求高风险多维验证，包含核心行为、回归、兼容性、边界条件或性能证据闭环

### 0.7.2 角色责任

- planner 必须输出 `verification_tier`
- planner 必须输出 `required / optional / unavailable` 验证集合
- coder 必须按 tier 执行可执行验证并记录不可执行原因
- reviewer 必须检查是否按 tier 执行

### 0.7.3 blocker 规则

- `required` 验证缺失：默认构成 blocker
- `optional` 验证缺失：不自动构成 blocker，但必须记录风险
- `unavailable` 验证：必须说明原因、影响范围和替代证据

### 0.7.4 board-first 验证补充

当 `primary_type = incident_investigation` 时，验证集合至少应覆盖：

- `reproduction_verification`
- `evidence_sufficiency_check`
- `hypothesis_discrimination_check`
- `route_correctness_check`
- `post_instrumentation_validation`

若后续分流到 `bug_fix`，再追加 `fix_validation`；若后续分流到 `optimization`，再追加 `gain_validation`。

特殊规则：

- `evidence_sufficiency_check` 对 investigation 任务始终为 `required`
- 当结论为 `insufficient` 时，不得硬凑修复方案
- 当关键验证为 `unavailable` 且设计预期为 `unknown / partially_known` 时，只能输出 `minimal_verifiable_path`

---

## 0.8 scope creep trigger

若满足以下任一条件，主代理必须 `stop / confirm / replan`：

- 修改文件数超过预设上限
- 新增模块超过预设上限
- 涉及公共接口签名变更
- 涉及 schema / ABI / serialization format
- 涉及跨层调用链变化
- 新增外部依赖
- 原定 `primary_type = bug_fix` 演化为 `refactor / redesign`
- 原定 `primary_type = optimization` 演化为结构性重构

推荐策略：

- 轻微超出且仍在授权边界内：`allow_minor_expansion_with_record`
- 影响计划与验证门禁：`replan_required`
- 影响任务语义或授权边界：`stop_and_confirm`

---

## 0.9 角色输入输出契约

### 0.9.1 knowledge-planner

输入：

- 任务目标
- 可选的板端执行范围与连接策略
- 知识侧允许范围
- 项目侧允许范围
- 可选的来源范围与联网策略

输出：

- 主类型与修饰属性
- `investigation_plan`
- `board_gap_analysis`
- `board_target_resolution`
- 已读取文件
- 实施计划
- 验证计划
- `board_execution_plan`
- `classification_candidates`
- `route_preconditions`
- `verification_tier`
- `required / optional / unavailable` 验证集合
- 回写建议
- 未解决不确定项

停止条件：

- 未获得允许范围
- `board_execution_required` 但未获得最小板端合同
- 无法确定 `primary_type` 或 `task_modifiers`
- 需要联网但未授权

当 `primary_type = incident_investigation` 时，`knowledge-planner` 应优先输出 `investigation_plan`、`evidence_gap_analysis`、`triage_plan` 与 `classification_candidates`，而不是直接输出 `implementation_plan`。

### 0.9.2 repo-coder

输入：

- 任务目标
- 计划
- 代码库允许修改范围
- 验证命令
- 不做事项
- `verification_tier`

输出：

- 修改文件
- `instrumentation_changes`
- `probe_results`
- `post_instrumentation_artifacts`
- 实施结果
- 板端部署与运行记录
- 板端产物采集记录
- 执行过的验证
- 未解决技术风险
- 对审查发现的返工结果
- `scope_creep_triggered`

停止条件：

- 需修改禁止目录
- 需做接口级变更
- 无法完成最小验证
- reviewer 发现需要返工但返工内容已超出当前授权范围

当 `primary_type = incident_investigation` 时，`repo-coder` 的优先职责是 instrumentation、probe、capture、最小复现实验与证据补强，而不是默认直接修复业务逻辑。

### 0.9.3 repo-reviewer

输入：

- 任务目标
- 计划与验收标准
- diff 摘要
- 验证结果
- 板端日志、trace、指标或效果产物
- 必要代码上下文
- `verification_tier`

输出：

- `goal_alignment_assessment`
- `route_correctness_assessment`
- `evidence_sufficiency_assessment`
- `hypothesis_closure_assessment`
- `scope_compliance_assessment`
- `validation_coverage_assessment`
- `regression_risk_assessment`
- `behavioral_correctness_assessment`
- `board_effect_assessment`
- `overall_decision`
- `repo_review_result`
- `findings`
- `finding_severity`
- `next_action`
- `fix_owner`

停止条件：

- 关键验证缺失
- 板端证据要求存在但缺失
- 修改目标与计划不一致
- 审查输入未裁剪且无法保证独立性

当 `primary_type = incident_investigation` 时，`repo-reviewer` 必须额外审查：

- 问题分类是否成立
- 证据是否足够支撑分流
- 假设是否闭环
- 是否误将环境问题当代码问题
- 是否允许得出“暂不改代码”的结论

### 0.9.4 functional-reviewer

输入：

- 任务目标
- 规范输入
- 验收条目
- 代码或运行证据
- 必要上下文

输出：

- `acceptance_items`
- `compliance_matrix`
- `evidence_used`
- `evidence_gaps`
- `norm_conflicts`
- `review_conclusion`
- `suggested_followup`

停止条件：

- 规范输入不足
- 证据不足以支撑判定
- 规范冲突未被显式标注

### 0.9.5 verification-manager

输入：

- 任务目标
- 风险边界
- 实施计划
- 已执行验证

输出：

- 验证矩阵
- tier 对应验证要求
- 缺失验证分类
- blocker 判断

停止条件：

- 无法定义验证目标
- 验证证据无法映射到风险边界

### 0.9.6 failure-analyst

输入：

- `expected_behavior` 或 `whether_design_expectation_known`
- `actual_behavior` 或 `observed_symptoms`
- `reproduction_path` 或 `trigger_condition`
- 日志、trace、指标、视频、dump、错误码与相关代码线索

输出：

- `hypothesis_set`
- `hypothesis_confidence`
- `evidence_priority`
- `supporting_evidence_map`
- `contradicting_evidence_map`
- `noise_signals`
- `observability_gaps`
- `next_probe_actions`
- `minimal_verifiable_path`
- 是否需要 replan

停止条件：

- 预期行为与设计预期均不可得，且无法形成可判别假设
- 证据不足以形成可检验假设

### 0.9.7 knowledge-auditor

输入：

- 候选条目
- 来源与证据
- 适用边界
- 风险
- 来源任务

输出：

- 提升建议
- 复用价值判断
- 边界补全建议
- 是否仍应停留在候选区

停止条件：

- 候选缺少来源
- 边界与风险缺失
- 无法判断其是否只是项目特例

### 0.9.8 knowledge-closer

输入：

- 任务目标
- 实际修改
- 验证结果
- 审查结论

输出：

- 项目回写内容
- `investigation_summary`
- `evidence_boundary`
- `unresolved_hypotheses`
- `route_decision`
- board 回写摘要
- 知识候选
- 来源记录
- 未闭环事项
- `run_log`
- `audit_log`

停止条件：

- 无法确定分区位置
- 结论缺少来源或边界

当 `primary_type = incident_investigation` 时，即使未进入修复或优化主链，也必须回写“为何当前轮只调查、不修复”。

---

## 0.10 确认点、停止条件与返工升级

### 0.10.1 以下场景建议强制确认

- 首次定义允许访问范围
- 涉及公共接口变化
- 涉及 schema / ABI / 数据结构兼容性变化
- 涉及批量重构或删除逻辑
- 计划与原始需求明显偏离
- 需要将内容提升为 `01_Knowledge/`
- reviewer 独立性被破坏但仍试图直接给出审查裁决

### 0.10.2 以下场景必须停止

- 未明确允许范围
- 无法验证核心改动
- 外部信息未经审核却拟入正式知识区
- 发现任务目标本身矛盾
- `scope_creep_trigger` 已命中且未确认处理策略

### 0.10.3 返工升级规则

- review 不通过后默认由原 `repo-coder` 返工
- 可影响返工路径的角色：`repo-reviewer`、`functional-reviewer`、`verification-manager`
- 连续返工超过 2 轮时，默认升级为 `replan` 或人工确认
- 当根因假设失效、`scope_creep_trigger` 命中、返工超出授权范围时，应回 `knowledge-planner`，而不是继续原地循环

---

## 0.11 run_log / audit_log

运行记录至少应包含以下字段：

- `task_id`
- `board_target_id`
- `board_state_before`
- `board_state_after`
- `entry_mode`
- `primary_type`
- `task_modifiers`
- `verification_tier`
- `roles_invoked`
- `rework_rounds`
- `files_changed_count`
- `review_findings_count`
- `blocker_count`
- `candidate_count`
- `promotion_count`
- `board_execution_result`
- `board_effect_summary`
- `board_failure_reason`
- `symptom_category`
- `reproduction_confidence`
- `design_expectation_status`
- `classification`
- `classification_confidence`
- `route_decision`
- `route_blockers`
- `evidence_sufficiency`
- `hypothesis_count`
- `top_hypothesis_confidence`
- `repo_review_result`
- `knowledge_writeback_result`
- `board_sync_required`
- `board_sync_completed`
- `sync_mode`
- `current_updated`
- `delta_created`
- `delta_merged`
- `baseline_status_checked`
- `default_entry_verified`
- `single_pass_recoverable`
- `final_status`
- `stop_reason`

建议补充：

- `state_transitions`
- `entry_conditions_satisfied`
- `blocking_conditions_hit`
- `scope_creep_triggered`
- `board_side_modeled`
- `board_state_machine_added`
- `board_contract_defined`
- `board_entry_rule_added`
- `board_execution_rule_added`
- `board_audit_backflow_added`
- `three_side_chain_closed`

---

## 0.12 调度 prompt 设计原则

调度 prompt 只负责实例化本轮任务，不负责重写长期制度。

一个合格的调度 prompt 应包含：

- 本轮任务目标
- 板端执行目标或无板端执行声明
- 输入材料
- 允许范围
- 是否允许联网
- 是否需要确认
- 输出要求
- reviewer 是否独立调度以及 reviewer 的输入边界
- review 未通过时由谁返工以及返工轮次上限
- `verification_tier`
- `scope_creep_policy`
- `extended_roles`
- board execution contract 是否完整
- 板端执行、日志分析与回写由谁负责

一个不合格的调度 prompt 往往会：

- 临时定义长期角色
- 重复知识分区规则
- 重复仓库级验证制度
- 同时塞入过多特例和例外
- 让 reviewer 直接继承 coder 的完整上下文叙述
- 把 board side 退化成最后一步的同步备注

---

## 0.13 调度 prompt 模板

### 0.13.1 通用型

```text
按 Agent 三侧运行规范执行本次任务。

技术基准：
- [[01_Knowledge/Agent Workflow/Agent驱动知识库、代码库与板端侧协同闭环规范]]
- [[01_Knowledge/Agent Workflow/Agent三侧运行规范与调度模板]]

任务目标：
[填写目标]

板端描述：
- board_target_id:
- board_type: chip_board | vehicle_controller | simulator_board | other_embedded_target
- ssh_target:
- workspace_path:
- deploy_artifacts:
- run_commands:
- collect_paths:
- expected_signals:
- timeout_policy:
- reset_or_recovery_steps:
- linked_repo_scope:
- linked_knowledge_scope:
- writeback_targets:
- 若无板端执行，必须填写 `no_board_execution_reason`

主类型：
[填写 primary_type]

任务修饰属性：
[填写 task_modifiers]

允许范围：
- 知识库读取：[填写路径]
- 项目区读写：[填写路径]
- 代码库修改：[填写路径]

联网策略：
[允许 / 禁止 / 条件允许]

main_agent_mode:
- orchestration

planner_mode:
- explicit / lightweight_absorbed

writeback_mode:
- explicit / recommendation_only

verification_tier:
- V0 / V1 / V2 / V3

scope_creep_policy:
- stop_and_confirm / replan_required / allow_minor_expansion_with_record

extended_roles:
- failure-analyst: enabled / disabled
- verification-manager: enabled / disabled
- functional-reviewer: enabled / disabled
- knowledge-auditor: enabled / disabled

确认策略：
[填写确认点与停止条件]

主代理职责：
- 维护状态机与状态门禁
- 决定角色调用顺序
- 裁剪交接包
- 控制 reviewer 独立性
- 控制返工轮次
- 汇总最终输出

主代理不得：
- 直接修改代码
- 替代 reviewer 做质量裁决
- 绕过 review 进入 knowledge writeback
- 把未审内容直接写入正式知识区

说明：
以下顺序描述的是主代理在 orchestration 模式下对子代理的默认调用顺序。
workflow-orchestrator 默认由主代理承担，不作为普通子代理列入调用链。

子代理调用顺序：
1. 先调用 knowledge-planner，先解析板端描述或无板端执行声明，再输出主类型、修饰属性、已读取范围、实施计划、验证计划、board_execution_plan、verification_tier、验证集合、建议回写路径。
2. 如本地知识不足且允许联网，再调用 source-ingestor，结果只写候选区或来源区；之后重新经过 knowledge-planner 收敛计划。
3. 如验证矩阵复杂，再调用 verification-manager 补充 required / optional / unavailable 验证集合。
4. 再调用 repo-coder，仅在授权范围内实施修改、部署到板端并执行最小验证。
5. 再调用 repo-reviewer，使用独立 reviewer 实例，仅接收任务目标、验收标准、计划、diff、验证结果、板端日志/指标/效果产物和必要代码上下文，独立检查越界风险、验证覆盖、板端效果与行为变化。
6. 若 repo review 不通过，则将裁剪后的审查结论返回原 repo-coder 返工；超过 2 轮、根因失效或 scope creep 触发时，回 planner 或 stop / confirm / escalate。
7. 仅在 repo review 通过后调用 knowledge-closer，按分区规则回写结果并同步板端摘要。

输出要求：
- roles_invoked
- state_transitions
- rework_rounds
- overall_decision
- verification_tier
- files_read
- files_written
- implementation_plan
- verification_results
- review_conclusion
- board_execution_result
- writeback_targets
- risks_or_uncertainties
- board_gap_analysis
- three_side_model_summary
- board_execution_contract
- execution_chain_changes
- template_changes
- rule_changes_summary
- run_log / audit_log（如适用）
```

### 0.13.2 功能审核型

```text
按 Agent 三侧运行规范执行本次功能审核任务。

技术基准：
- [[01_Knowledge/Agent Workflow/Agent驱动知识库、代码库与板端侧协同闭环规范]]
- [[01_Knowledge/Agent Workflow/Agent三侧运行规范与调度模板]]

任务目标：
[填写要审核的功能或能力]

审核对象：
[功能模块 / 接口 / 状态机 / 页面行为 / 算法行为]

规范输入：
[填写技术规范、设计要求、验收标准、接口契约、时序约束、边界条件]

实现输入：
[填写代码路径 / diff / 可执行产物 / 测试结果 / 日志 / trace / 截图]

板端描述：
[若本次审核涉及上板验证，填写 ssh_target / run_commands / collect_paths / expected_signals；否则写 no_board_execution]

主类型：
audit

任务修饰属性：
[functional_scope, read_only]

允许范围：
- 知识库读取：[填写路径]
- 项目区读写：[填写路径]
- 代码库读取：[填写路径]
- 代码库修改：默认禁止

联网策略：
[允许 / 禁止 / 条件允许]

main_agent_mode:
- orchestration

planner_mode:
- explicit / lightweight_absorbed

writeback_mode:
- explicit / recommendation_only

verification_tier:
- V0 / V1 / V2 / V3

scope_creep_policy:
- stop_and_confirm / replan_required / allow_minor_expansion_with_record

extended_roles:
- failure-analyst: disabled
- verification-manager: disabled
- functional-reviewer: enabled
- knowledge-auditor: enabled / disabled

主代理职责：
- 确认规范来源与允许范围
- 维护状态对象
- 控制 reviewer 独立性
- 汇总审核结论与后续动作

主代理不得：
- 直接修改代码
- 用 coder/planner 解释替代证据
- 绕过 review 直接写入正式知识区

说明：
以下顺序描述的是主代理在 orchestration 模式下对子代理的默认调用顺序。
workflow-orchestrator 默认由主代理承担，不作为普通子代理列入调用链。

证据优先级：
- 行为证据 > 规范文本 > 代码证据 > coder/planner 解释

子代理调用顺序：
1. 先调用 knowledge-planner 的轻量模式，仅完成规范来源确认、允许范围确认、验收条目整理与 verification_tier 输出。
2. 如本地规范不足且允许联网，再调用 source-ingestor，结果只写候选区或来源区。
3. 调用 functional-reviewer，输出规范符合度判断。
4. 若任务包含板端验证，则由 repo-coder 完成上板运行与产物采集，再由 repo-reviewer 汇总板端证据。
5. reviewer 必须输出 acceptance_items、compliance_matrix、evidence_used、evidence_gaps、norm_conflicts、review_conclusion、suggested_followup。
6. 若审核不通过，不直接修代码；建议转入 `primary_type = bug_fix / optimization` 或 redesign 时，由主代理 stop / confirm / replan。
7. 若审核通过且需要沉淀，再调用 knowledge-closer；若涉及正式知识提升审查，可插入 knowledge-auditor。

输出要求：
- roles_invoked
- state_transitions
- rework_rounds
- overall_decision
- verification_tier
- files_read
- audit_scope
- acceptance_items
- compliance_matrix
- evidence_used
- evidence_gaps
- review_conclusion
- suggested_followup
- writeback_targets
- risks_or_uncertainties
- run_log / audit_log（如适用）
```

### 0.13.3 板端异常调查型

```text
按 Agent 三侧运行规范执行本次板端异常调查任务。

技术基准：
- [[01_Knowledge/Agent Workflow/Agent驱动知识库、代码库与板端侧协同闭环规范]]
- [[01_Knowledge/Agent Workflow/Agent三侧运行规范与调度模板]]

任务目标：
[填写调查目标]

主类型：
incident_investigation

任务修饰属性：
[failure_investigation, review_required, board_artifact_collection_required, board_execution_required | no_board_execution, code_change_allowed | read_only]

观测现象：
- observed_symptoms:
- symptom_category:
- severity_guess:
- first_seen_at:
- seen_frequency:

板端描述：
- board_target_id:
- board_type: chip_board | vehicle_controller | simulator_board | other_embedded_target
- ssh_target:
- workspace_path:
- deploy_artifacts:
- run_commands:
- collect_paths:
- board_session_info:
- environment_fingerprint:
- 若无板端执行，必须填写 `no_board_execution_reason`

已有 artifacts：
- artifact_inventory:
- log_sources:
- anomaly_window:
- available_evidence:
- missing_evidence:

触发与复现：
- trigger_condition:
- reproduction_confidence:
- issue_scope_guess:
- whether_design_expectation_known:
- signal_expectations:

允许范围：
- 知识库读取：[填写路径]
- 项目区读写：[填写路径]
- 代码库修改：[填写路径]

联网策略：
[允许 / 禁止 / 条件允许]

main_agent_mode:
- orchestration

planner_mode:
- explicit

writeback_mode:
- explicit / recommendation_only

verification_tier:
- V1 / V2 / V3

scope_creep_policy:
- stop_and_confirm / replan_required / allow_minor_expansion_with_record

extended_roles:
- failure-analyst: enabled
- verification-manager: enabled / disabled
- functional-reviewer: disabled
- knowledge-auditor: enabled / disabled

主代理职责：
- 维护 investigation 状态机
- 控制 triage、classification 与 route decision 门禁
- 控制 reviewer 独立性
- 控制返工轮次与是否只允许 instrumentation

主代理不得：
- 在问题未定性时强行推进业务修复
- 直接修改代码
- 绕过 review 进入 knowledge writeback

子代理调用顺序：
1. 先调用 knowledge-planner，输出 investigation_plan、evidence_gap_analysis、triage_plan、classification_candidates、verification_tier、required / optional / unavailable 验证集合。
2. 必须调用 failure-analyst，输出 hypothesis_set、hypothesis_confidence、evidence_priority、noise_signals、next_probe_actions、minimal_verifiable_path。
3. 如需要最小观测增强、补日志、补 trace、补 dump 或复现实验，再调用 repo-coder，但其职责优先是 instrumentation、probe、capture，不默认修复业务逻辑。
4. 如验证矩阵复杂，再调用 verification-manager，补充 evidence sufficiency、hypothesis discrimination 与 route correctness 对应验证集合。
5. 调用 repo-reviewer，仅接收任务目标、现象描述、调查计划、关键证据、假设集、分流建议、必要 diff、验证结果与板端 artifacts，独立审查证据充分性、分类正确性、路由正确性，以及“是否允许暂不改代码”。
6. 若 route decision 已明确且门禁满足，则转入既有 `bug_fix / optimization / audit` 模板；若结论为 `insufficient_evidence / out_of_scope env_issue`，可直接 `investigation_closed`。
7. 调查轮结束后调用 knowledge-closer，回写 investigation_summary、evidence_boundary、unresolved_hypotheses、route_decision、followup_required。

输出要求：
- roles_invoked
- state_transitions
- rework_rounds
- overall_decision
- verification_tier
- files_read
- files_written
- investigation_plan
- classification
- classification_confidence
- route_decision
- route_blockers
- minimal_verifiable_path
- verification_results
- review_conclusion
- writeback_targets
- risks_or_uncertainties
- run_log / audit_log（如适用）
```

### 0.13.4 缺陷修复型

```text
按 Agent 三侧运行规范执行本次缺陷修复任务。

技术基准：
- [[01_Knowledge/Agent Workflow/Agent驱动知识库、代码库与板端侧协同闭环规范]]
- [[01_Knowledge/Agent Workflow/Agent三侧运行规范与调度模板]]

任务目标：
[填写缺陷目标]

缺陷类型：
[runtime_bug / functional_bug / design_mismatch]

预期行为：
[填写设计要求、验收标准或方案约束]

实际行为：
[填写当前表现、错误输出、偏差现象]

已知证据：
[日志 / 截图 / 复现输入 / 指标异常 / 相关代码线索]

板端描述：
[若本次修复要求上板复现或验证，填写 ssh_target / deploy_artifacts / run_commands / collect_paths / expected_signals；否则写 no_board_execution]

主类型：
bug_fix

任务修饰属性：
[code_change_allowed, review_required]

允许范围：
- 知识库读取：[填写路径]
- 项目区读写：[填写路径]
- 代码库修改：[填写路径]

联网策略：
[允许 / 禁止 / 条件允许]

main_agent_mode:
- orchestration

planner_mode:
- explicit

writeback_mode:
- explicit / recommendation_only

verification_tier:
- V1 / V2 / V3

scope_creep_policy:
- stop_and_confirm / replan_required / allow_minor_expansion_with_record

extended_roles:
- failure-analyst: enabled / disabled
- verification-manager: enabled / disabled
- functional-reviewer: disabled
- knowledge-auditor: enabled / disabled

主代理职责：
- 检查预期行为、实际行为、根因假设与最小验证路径
- 维护返工轮次
- 决定是否 replan 或 escalate

主代理不得：
- 直接修改代码
- 替代 reviewer 做质量裁决
- 在 review 前进入 writeback

说明：
以下顺序描述的是主代理在 orchestration 模式下对子代理的默认调用顺序。
workflow-orchestrator 默认由主代理承担，不作为普通子代理列入调用链。

子代理调用顺序：
1. knowledge-planner 输出主类型、修饰属性、已读取范围、根因假设、最小验证路径、修复计划、verification_tier、建议回写路径。
2. 若根因复杂或多轮返工不收敛，可插入 failure-analyst，补充根因假设、证据优先级和最小验证路径。
3. 如本地知识不足且允许联网，再调用 source-ingestor，结果只写候选区或来源区；之后重新经过 knowledge-planner 收敛计划。
4. 如验证矩阵复杂，再调用 verification-manager。
5. 调用 repo-coder，仅在授权范围内实施符合设计边界的修复，并执行最小必要验证与相关回归验证。
6. 调用 repo-reviewer，仅接收任务目标、预期行为、实际行为、验收标准、实施计划、diff、验证结果和必要代码上下文，独立检查根因是否闭环、改动是否越界、验证是否覆盖行为失配、是否仍存在回归风险。
7. 若绑定板端执行，则在 repo-coder 完成上板、采集日志与效果产物后，由 repo-reviewer 统一判断板端效果是否达标。
8. 若 review 不通过，默认返回原 repo-coder 返工；根因假设失效、scope creep 触发或返工超出授权范围时，回 planner。
9. 仅在 review 通过后，knowledge-closer 回写调试记录、修复结论、failure_mode 候选和未闭环事项；如涉及正式知识提升审查，可插入 knowledge-auditor。

输出要求：
- roles_invoked
- state_transitions
- rework_rounds
- overall_decision
- verification_tier
- files_read
- files_written
- root_cause_hypotheses
- implementation_plan
- verification_results
- review_conclusion
- writeback_targets
- risks_or_uncertainties
- run_log / audit_log（如适用）
```

### 0.13.5 受控优化型

```text
按 Agent 三侧运行规范执行本次受控优化任务。

技术基准：
- [[01_Knowledge/Agent Workflow/Agent驱动知识库、代码库与板端侧协同闭环规范]]
- [[01_Knowledge/Agent Workflow/Agent三侧运行规范与调度模板]]

任务目标：
[填写优化目标]

优化类型：
[performance / memory / latency / maintainability / build / test]

优化依据：
[填写瓶颈证据、基线数据、重复问题或明确设计依据]

基线现状：
[填写当前耗时、资源占用、复杂度或维护问题]

目标指标：
[填写希望改善的指标或约束]

非目标项：
[填写明确不做事项]

板端描述：
[若本次优化要求上板收益验证，填写 ssh_target / deploy_artifacts / run_commands / collect_paths / expected_signals；否则写 no_board_execution]

主类型：
optimization

任务修饰属性：
[code_change_allowed, review_required]

允许范围：
- 知识库读取：[填写路径]
- 项目区读写：[填写路径]
- 代码库修改：[填写路径]

联网策略：
[允许 / 禁止 / 条件允许]

main_agent_mode:
- orchestration

planner_mode:
- explicit

writeback_mode:
- explicit / recommendation_only

verification_tier:
- V1 / V2 / V3

scope_creep_policy:
- stop_and_confirm / replan_required / allow_minor_expansion_with_record

extended_roles:
- failure-analyst: disabled
- verification-manager: enabled
- functional-reviewer: disabled
- knowledge-auditor: enabled / disabled

主代理职责：
- 控制 scope creep
- 检查优化依据、收益验证和语义回归验证
- 决定是否需要 replan 或 stop_and_confirm

主代理不得：
- 直接修改代码
- 替代 reviewer 给出质量裁决
- 绕过 review 直接沉淀优化结论

说明：
以下顺序描述的是主代理在 orchestration 模式下对子代理的默认调用顺序。
workflow-orchestrator 默认由主代理承担，不作为普通子代理列入调用链。

子代理调用顺序：
1. knowledge-planner 输出优化依据、风险边界、非目标项、验证计划、verification_tier 和回写建议。
2. 如本地知识不足且允许联网，再调用 source-ingestor，结果只写候选区或来源区；之后重新经过 knowledge-planner 收敛计划。
3. 调用 verification-manager，补充收益验证、语义回归验证和 tier 对应验证集合。
4. 调用 repo-coder，仅在授权范围内实施边界内优化，并完成收益验证与语义回归验证。
5. 调用 repo-reviewer，仅接收任务目标、目标指标、非目标项、实施计划、diff、验证结果和必要代码上下文，独立检查是否越界、是否改变核心语义、优化收益是否有证据、是否引入新的回归风险。
6. 若绑定板端执行，则在 repo-coder 完成上板、采集指标与效果产物后，由 repo-reviewer 统一判断板端收益是否成立。
7. 若 review 不通过，默认返回原 repo-coder；若优化演化为结构性重构或验证不足构成 blocker，则 stop / confirm / replan。
8. 仅在 review 通过后，knowledge-closer 回写项目优化记录、可复用候选和未闭环事项；如涉及正式知识提升审查，可插入 knowledge-auditor。

输出要求：
- roles_invoked
- state_transitions
- rework_rounds
- overall_decision
- verification_tier
- files_read
- files_written
- optimization_basis
- implementation_plan
- verification_results
- review_conclusion
- writeback_targets
- risks_or_uncertainties
- run_log / audit_log（如适用）
```

---

## 0.14 回写输出格式

任务结束时，统一输出：

### 0.14.1 Summary

- primary_type:
- task_modifiers:
- allowed_paths:
- files_read:
- files_written:
- sync_mode:
- current_files_must_update:
- history_files_to_mark:
- default_entry_verified:
- single_pass_recoverable:

### 0.14.2 Review status

- candidate_created:
- promoted_to_knowledge:
- source_notes_created:
- current_updated:
- delta_created:
- delta_merged:
- baseline_status_checked:

### 0.14.3 Risks / uncertainties

- ...

### 0.14.4 Board sync status

- board_target_id:
- board_state_before:
- board_state_after:
- board_execution_result:
- repo_review_result:
- board_sync_required:
- board_sync_completed:
- board_failure_reason:

---

## 0.15 使用建议

建议按以下顺序使用三篇文档：

1. 先读 [[01_Knowledge/Agent Workflow/Agent驱动知识库、代码库与板端侧协同闭环规范]]，明确原则和边界。
2. 读本文档，按运行状态机和调度模板组织任务。
3. 读 [[01_Knowledge/Agent Workflow/Agent三侧模板与文件结构规范]]，在根目录生成所需文件骨架。

---

## 0.16 文档收敛运行补充

### 0.16.1 适用前提

当任务涉及设计演化、实现状态更新、审核结论收敛、文档体系整理或历史记录压缩时，主代理必须把“文档收敛与状态更新”视为闭环的一部分，而不是可选附加项。

### 0.16.2 计划阶段新增输出

`knowledge-planner` 在 `plan_ready` 前必须补充：

- `document_role_strategy`
- `current_docs_expected`
- `current_role_gap_assessment`
- `current_complementarity_checks`
- `spec_source_required`
- `implementation_input_chain`
- `default_recovery_bundle`
- `default_truth_sources`
- `delta_docs_to_merge`
- `baseline_docs_to_downgrade`
- `adr_needed`
- `retrieval_priority_plan`
- `current_recoverability_goal`
- `single_pass_blockers`
- `sync_mode`
- `why_delta_only_allowed`
- `current_files_must_update`
- `history_files_to_mark`

其中 `document_role_strategy` 至少要回答：

- 哪些文档是 `baseline`
- 哪些文档是 `overview_current / design_current / spec_current / implementation_current / validation_current`
- 哪些文档是 `delta`
- 哪些文档应转为 `archive` 或 `superseded`
- 哪些文档应保持 `default_entry = true`
- 哪些关键事实应上收为 `design/spec`
- 哪些关键事实应下沉为 `implementation/validation`
- 哪些材料只保留为 `evidence_only`
- 哪些 current 文档构成默认真相源集合

### 0.16.3 状态机新增检查点

标准状态机在 `implementation_done` 与 `writeback_done` 之间增加显式门禁：

1. `knowledge_sync_checked`
2. `convergence_ready`

进入 `knowledge_sync_checked` 的前提：

- 已评估代码、设计、接口、约束或状态机是否变化
- 已判断 `current / adr / delta` 是否需要同步更新
- 已输出 `sync_mode / current_files_must_update / history_files_to_mark`
- 若为 `delta_only`，已给出合法举证

进入 `convergence_ready` 的前提：

- 已确认当前态是否可被单次恢复
- 已确认默认实现输入链是否可由 current 文档独立成立
- 已逐项检查 `overview / design / spec / implementation / validation` 是否各自承担主职责
- 已确认历史文档是否完成最小状态标记
- 已确认 default retrieval 不再以历史 baseline 作为主入口
- 已确认 `default_entry_verified = true`
- 已确认 `single_pass_recoverable = true`
- 已确认关键事实未只存在于 baseline / delta / 大段代码阅读中

若这两个门禁未通过，不得进入 `writeback_done`。

### 0.16.4 角色补充职责放置规则

与文档收敛相关的角色补充职责，应写入 [[01_Knowledge/Agent Workflow/Agent三侧模板与文件结构规范]] 中对应角色的 `toml` 模板，而不是写在运行模板里重复定义。
本文档只保留状态机、门禁、输入输出与调度要求。

### 0.16.5 默认检索顺序

在 orchestration 模式下，主代理组织上下文时默认按以下顺序读取：

1. `overview_current / design_current / spec_current`
2. `implementation_current / validation_current`
3. pending delta
4. adr / decision ledger
5. merged delta
6. superseded baseline / archive

若当前目录未形成该顺序，planner 应把“建立 current 入口”列入实施计划。

若同一主题存在 2 份及以上 current 文档而缺少 `overview_current`，planner 不得把该主题判定为已收敛，必须把建立 `overview_current` 列入实施计划。

### 0.16.6 current 可恢复性最低标准

若任务要求文档收敛，则 writeback 前至少满足以下问题可由单次 current 检索回答：

1. 当前模块目标与边界是什么
2. 当前设计如何组织模块、对象、状态与主流程
3. 当前版本必须遵守的机制级规范事实是什么
4. 当前主要代码入口、实现载体与规范映射是什么
5. 当前已证明和未证明什么
6. 当前已知限制、风险和未闭环项是什么
7. 哪些历史文档只保留为证据，不再代表当前真相

硬判定至少包括：

1. `overview_current` 可单次确定默认入口、默认恢复顺序、默认实现输入链、`default_recovery_bundle` 与 current 真相源集合
2. `design_current` 可单次恢复当前设计目标、边界、主流程、关键状态组织、对象/模块耦合与非目标项
3. `spec_current` 可单次恢复当前版本必须遵守的机制级规范事实；若存在状态、计算、类型、滤波、配置或验证机制，对应规范块不得缺位
4. `implementation_current` 可单次恢复主要代码入口、关键实现载体、design/spec 到代码的映射、兼容层与已知不完全闭合点
5. `validation_current` 可单次恢复当前证据、缺失证据、已证实/未证实边界、review 结论与下一轮验证要求
6. baseline 和 delta 只用于追溯来源，而不是补 current 主体缺口
7. 关键状态变量、关键计算口径、关键接口事实、关键验证缺口不得只存在于代码或 delta 中

若出现以下任一情况，必须判定 `single_pass_recoverable = false`：

- coder / reviewer / verifier 仍需默认依赖 baseline 或两篇及以上 delta
- 为恢复关键当前事实仍需大段、无裁剪的代码通读
- 关键事实虽然写入 current，但落在错误 `current_kind`，导致默认恢复链无法稳定裁剪
- `default_recovery_bundle` 不能独立回答 design/spec/implementation/validation 边界问题

### 0.16.7 默认实现输入链最低标准

若任务要求“按规范实现代码”，则 writeback 或执行前至少满足：

1. `design_current` 能说明目标、边界、对象/模块组织、关键状态与设计约束
2. `spec_current` 能说明必须满足的行为、接口、状态规则、配置语义、验证合同与非目标项；不能只写“应该怎么做”，还必须写“按什么机制和什么约束去做”
3. `implementation_current` 能说明当前代码事实、关键实现载体、spec-to-code mapping 与修改落点
4. `validation_current` 能说明当前证据边界、已证实/未证实结论与所需验证
5. coder 不再需要读取 baseline、两篇及以上 delta 或大段代码才能补齐关键实现约束

若主题已存在 `spec_current`，则 `implementation / bug_fix / optimization` 类任务中 coder 不得绕过 `spec_current` 直接基于 baseline 或 delta 实施。
历史补丁驱动开发应被视为 blocker，而不是可接受捷径。

### 0.16.8 current 角色边界检查

planner、reviewer 与 knowledge-auditor 至少要用以下六类事实做一次 owner 检查：

1. 系统目标与当前边界
2. 设计组织与关键耦合
3. 机制级规范事实
4. 代码载体与规范映射
5. 已证实 / 未证实边界
6. 已知缺口与风险归属

检查规则：

- 每类关键事实必须有且仅有一个 primary owner current 文档
- `overview_current` 负责声明与裁剪，不负责承接机制细节、代码映射或证据结论主体
- `implementation_current` 不得成为规范性行为定义主体
- `validation_current` 不得用来定义行为、设计或实现主体事实
- 若事实无 owner、owner 冲突、或 owner 放错位置导致恢复链失稳，则不得通过收敛门禁

### 0.16.9 orchestration 任务模板补充

涉及文档收敛的任务，在“实施计划”和“验证计划”中至少增加两段：

- 规范更新阶段：更新角色分层、状态头、收敛规则、knowledge sync 与检索优先级
- 文档收敛阶段：建立/更新 current，标记 baseline 与 delta 状态，验证 current 可恢复性

输出要求还应补充：

- `document_role_strategy`
- `implementation_input_chain`
- `default_recovery_bundle`
- `spec_source_required`
- `current_recoverability_assessment`
- `knowledge_sync_decision`
- `convergence_decision`
- `sync_mode`
- `current_files_must_update`
- `current_role_gap_assessment`
- `current_complementarity_checks`
- `default_truth_sources`
- `single_pass_blockers`
- `history_files_to_mark`
- `default_entry_verified`
- `single_pass_recoverable`

### 0.16.10 项目级 current 重写任务模板

后续若要按本规范重写某个项目主题的 current 文档组，可直接复用以下任务骨架：

```md
# 任务名称
重写 <Topic> current 文档组，使其满足 single-pass recoverability

# 主类型
knowledge_task

# 任务修饰属性
- writeback_required
- review_required
- verification_required

# 允许范围
- 知识库读取：
  - 01_Knowledge/Agent Workflow/**
  - 02_Projects/<Project>/<Topic>/**
- 项目区读写：
  - 02_Projects/<Project>/<Topic>/**
- 代码库修改：
  - 禁止

# 联网策略
禁止

# 执行要求
1. 先检查 `overview_current / design_current / spec_current / implementation_current / validation_current` 的粒度缺口、owner 冲突和错误落位。
2. 再按最新模板重写 current 文档组，明确：
   - overview 的唯一默认入口、默认恢复顺序、默认实现输入链、truth-source set、历史角色映射
   - design 的边界、对象/模块组织、生命周期/状态组织、数据/控制流、约束、非目标项
   - spec 的 object model、required behaviors、state/config/interface/verification contracts，以及存在时的 calculation / type / filter 机制
   - implementation 的 code entry、state containers、flow、spec-to-code mapping、compatibility layers、known gaps
   - validation 的 evidence in hand、evidence missing、what is proven、what is not proven、review conclusion、required next verification
3. 再验证 `single_pass_recoverable`：
   - 不得依赖 baseline 或两篇及以上 delta 补 current 主体缺口
   - 关键状态变量、关键计算口径、关键接口事实、关键验证缺口不得只存在于代码或 delta 中
   - 默认恢复 bundle 必须足以单次恢复当前态
4. 最后做独立审查并写回：
   - 检查 current 组是否整体收紧，而不是只补 spec
   - 检查角色边界是否被破坏
   - 检查 recoverability 判定是否更严格而非更松
   - 仅在 review 通过后写回

# 输出要求
- current_series_gap_analysis
- rewritten_files
- single_pass_recoverability_assessment
- current_role_boundary_check
- verification_results
- review_conclusion
- remaining_risks
```

### 0.16.11 板端测试在环任务模板

```text
按 Agent 三侧运行规范执行本次板端测试在环任务。

技术基准：
- [[01_Knowledge/Agent Workflow/Agent驱动知识库、代码库与板端侧协同闭环规范]]
- [[01_Knowledge/Agent Workflow/Agent三侧运行规范与调度模板]]
- [[01_Knowledge/Agent Workflow/Agent三侧模板与文件结构规范]]

任务名称：
[填写名称]

板端描述：
- board_target_id:
- board_type: chip_board | vehicle_controller | simulator_board | other_embedded_target
- ssh_target:
- workspace_path:
- deploy_artifacts:
- run_commands:
- collect_paths:
- expected_signals:
- timeout_policy:
- reset_or_recovery_steps:
- linked_repo_scope:
- linked_knowledge_scope:
- writeback_targets:

主类型：
implementation | bug_fix | optimization | functional_tuning

任务修饰属性：
- board_execution_required
- board_artifact_collection_required
- review_required
- verification_required
- code_change_allowed 或 read_only

允许范围：
- 知识库读取：`01_Knowledge/Agent Workflow/**` 与本任务授权的 current 文档
- 项目区读写：仅限本任务授权路径
- 代码库修改：仅限板端描述声明的 `linked_repo_scope`
- 外部系统访问：按任务显式声明
- 联网：按任务显式声明

主代理职责：
- 先解析板端描述并确认是否允许进入实施
- 组织 knowledge current -> repo plan -> board execution -> repo review 的三侧主链
- 保持板端执行与 repo review 的证据边界清晰
- 只在 repo review 与 knowledge writeback 都满足后推进 close

默认执行链：
1. knowledge-planner：解析板端描述、读取 knowledge current、输出实施计划、board_execution_plan、verification_plan。
2. verification-manager：输出最小验证矩阵与板端产物采集要求。
3. repo-coder：在授权范围内修改 repo 或配置，部署到板端、执行测试并生成验证证据。
4. repo-reviewer：独立检查实现正确性、越界风险、验证覆盖、板端日志和效果指标。
5. knowledge-closer：回写 knowledge current / validation / evidence，输出板端回写摘要。

硬门禁：
- 有板端执行要求时不得绕过上板直接判定完成
- 板端运行完成不等于 repo review 通过
- 板端失败或效果不达标必须给出 `board_failure_reason`
- board 未同步完成不得判定 `closed`

输出要求：
- roles_invoked
- state_transitions
- rework_rounds
- overall_decision
- verification_tier
- files_read
- files_written
- implementation_plan
- verification_results
- review_conclusion
- board_execution_result
- writeback_targets
- risks_or_uncertainties
- board_gap_analysis
- three_side_model_summary
- board_execution_contract
- execution_chain_changes
- template_changes
- codex_followup_prompt
- run_log
- audit_log
```
