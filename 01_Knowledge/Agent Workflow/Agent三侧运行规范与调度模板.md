---
type: knowledge
status: verified
domain: 工程工作流
topic: Agent三侧运行规范与调度模板
sources: ["内部方法论整理", "01_Knowledge/Agent Workflow/Agent驱动知识库、代码库与板端侧协同闭环规范.md", "01_Knowledge/Agent Workflow/Agent三侧模板与文件结构规范.md", "01_Knowledge/Agent Workflow/Agent三侧角色契约规范.md"]
scope: 适用于需要将三侧闭环规则包装成可运行流程，包括板端目标绑定、状态推进、角色集合派生、返工升级和轻实例 prompt 约束的场景。
risks: ["运行规范过重导致单次任务负担过大", "板端执行被退化为附属说明", "项目特例被误提升为通用步骤", "角色契约与运行规范重复维护", "扩展角色加入后分层失效导致制度与运行脱节"]
updated_at: 2026-04-07
---

## 0.1 摘要

本文档定义三侧闭环的运行层，回答“系统怎么跑起来”。
它承接任务入口、状态门禁、角色调度、返工升级、日志记录和轻实例 prompt 规则。

---

## 0.2 方案评价

三层文档的分工如下：

- 上位规范：制度、边界、门槛
- 运行规范：状态机、调度、返工、任务属性到角色集合的派生
- 角色契约：角色边界、最小输入输出、停止条件与独立性要求
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

## 0.6 任务属性到角色集合的派生矩阵

本章只定义“什么任务默认需要哪些角色、哪些扩展角色按条件启用、哪些门禁不可跳过”。  
角色边界、最小输入输出与停止条件，统一下沉到 [[01_Knowledge/Agent Workflow/Agent三侧角色契约规范]]。

### 0.6.1 `knowledge_task + read_only`

- required_roles: `knowledge-planner`
- conditional_roles: `source-ingestor`
- hard_gates:
  - 未明确允许范围不得进入执行
  - 若允许联网，外部信息只允许进入候选区或来源区

### 0.6.2 `knowledge_task + requires_web + read_only`

- required_roles: `knowledge-planner`、`source-ingestor`
- conditional_roles: `knowledge-auditor`
- hard_gates:
  - 未授权联网不得启动 `source-ingestor`
  - 未经审查不得把外部信息写入正式知识区

### 0.6.3 `implementation + code_change_allowed + review_required`

- required_roles: `knowledge-planner`、`repo-coder`、`repo-reviewer`、`knowledge-closer`
- conditional_roles: `source-ingestor`、`verification-manager`
- hard_gates:
  - 主代理不得吸收 `repo-coder` 实施职责
  - review 未通过不得 writeback
  - 若为 `board_execution_required`，必须完成上板运行、产物采集和基于板端证据的 `repo-reviewer` 分析

### 0.6.4 `bug_fix + code_change_allowed + review_required`

- required_roles: `knowledge-planner`、`repo-coder`、`repo-reviewer`、`knowledge-closer`
- conditional_roles: `failure-analyst`、`source-ingestor`、`verification-manager`
- hard_gates:
  - reviewer 必须独立实例或独立会话阶段
  - review 未通过默认返工给原 `repo-coder`
  - 若为 `board_execution_required`，不得跳过板端复现与验证

### 0.6.5 `incident_investigation + review_required`

- required_roles: `knowledge-planner`、`failure-analyst`、`repo-reviewer`、`knowledge-closer`
- conditional_roles: `repo-coder`、`verification-manager`、`source-ingestor`
- hard_gates:
  - investigation 默认不要求先改代码
  - `repo-coder` 优先承担 instrumentation / probe / capture，不默认修复业务逻辑
  - 证据不足时允许 `investigation_closed`，不强行转入修复链

### 0.6.6 `optimization + code_change_allowed + review_required`

- required_roles: `knowledge-planner`、`repo-coder`、`repo-reviewer`、`knowledge-closer`
- conditional_roles: `verification-manager`、`source-ingestor`
- hard_gates:
  - 不得把受控优化演化为结构性重构而不触发 `scope_creep`
  - 收益验证和语义回归验证缺一不可

### 0.6.7 `audit + functional_scope + read_only`

- required_roles: `knowledge-planner`、`functional-reviewer`
- conditional_roles: `source-ingestor`、`knowledge-closer`、`repo-reviewer`
- hard_gates:
  - `functional-reviewer` 只负责规范符合度，不替代 `repo-reviewer` 做板端效果裁决
  - 证据不足时不得硬判定符合度

### 0.6.8 `knowledge_task + promotion_review + writeback_required`

- required_roles: `knowledge-closer`
- conditional_roles: `knowledge-auditor`、`source-ingestor`
- hard_gates:
  - 候选缺少来源、边界或风险时不得提升为正式知识
  - 主代理不得绕过审查直接转正

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

## 0.9 角色契约放置规则

角色契约已从运行规范中抽出，统一放在：

- [[01_Knowledge/Agent Workflow/Agent三侧角色契约规范]]

本文档不再重复定义各角色的：

- 职责边界
- 最小输入输出
- 停止条件
- reviewer 独立性细则

运行规范只保留：

- 何时需要哪些角色
- 何时必须阻断
- 何时需要返工、replan 或 escalate

若需要实例化角色骨架，则同步参考：

- [[01_Knowledge/Agent Workflow/Agent三侧模板与文件结构规范]] 中的 `.codex/agents/*.toml`

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

- 问题描述
- 当前任务目标
- 必要输入材料或已知证据
- `primary_type`
- `task_modifiers`
- `board_target` 或 `no_board_execution`
- `allowed_paths`
- `repo_scope`（若涉及代码）
- 联网策略
- 必要边界
- 成功标准
- 输出要求

一个不合格的调度 prompt 往往会：

- 临时定义长期角色
- 重复知识分区规则
- 重复仓库级验证制度
- 重复 reviewer 独立性、writeback gate 和 board gate 的制度文本
- 同时塞入过多特例和例外
- 把默认调用顺序写成冗长剧本
- 让 reviewer 直接继承 coder 的完整上下文叙述
- 把 board side 退化成最后一步的同步备注

---

## 0.13 轻实例 prompt 推荐方式

默认不再推荐复制整段“大展开模板”作为实例 prompt。  
推荐方式是：实例 prompt 只描述**本轮问题、目标、任务属性、必要边界和成功标准**，其余制度、门禁、角色契约和状态机从长期层派生。

### 0.13.1 推荐最小结构

一个推荐的实例 prompt 至少包含：

1. 任务对象
2. 任务背景
3. 任务目标
4. `primary_type`
5. `task_modifiers`
6. `board_target` 或 `no_board_execution`
7. `allowed_paths`
8. `repo_scope`（若涉及代码）
9. 联网策略
10. 本轮特例边界
11. 成功标准
12. 输出要求

### 0.13.2 推荐实例 prompt

```text
按 Agent 三侧运行规范执行本次任务。

任务对象：
- [填写目标对象]

任务背景：
[填写当前问题、现状、已知症状、已有上下文]

任务目标：
1. [填写本轮目标]
2. [填写希望优化、修复、审查或收敛的点]

任务属性：
- primary_type: [implementation / bug_fix / audit / optimization / knowledge_task / incident_investigation]
- task_modifiers: [按需填写]
- board_target: [若无则写 no_board_execution]
- allowed_paths:
  - [知识库读取范围]
  - [项目区读写范围]
  - [代码库修改范围；若无则写 read_only]
- verification_tier: [若已知则填写；未知可由主代理收敛]

联网策略：
[允许 / 禁止 / 条件允许]

本轮特例边界：
- [只写本轮需要额外强调的边界；若无可省略]

成功标准：
- [填写完成判据]
- [填写不可接受结果]

输出要求：
1. context_used
2. problem_diagnosis
3. execution_or_dispatch_recommendation
4. expected_writeback_or_followup
5. risks_or_uncertainties
```

### 0.13.3 对实例 prompt 的补充规则

- 不要重写长期制度
- 不要重写主代理职责和禁止事项
- 不要把默认角色调用顺序写成完整剧本
- 不要把 reviewer 独立性、writeback gate、board gate 重复抄入每轮 prompt
- 若本轮必须启用特定扩展角色，只写“本轮特例边界”即可

### 0.13.4 何时允许补充任务特例

以下信息可作为本轮特例补充进实例 prompt：

- `board_target` 的特例字段
- 特定 reviewer 必须启用
- 特定路径禁止触碰
- 本轮只允许 instrumentation、不允许业务修复
- 必须保留的证据优先级
- 特定成功标准或阻断条件

其余长期规则默认从：

- [[01_Knowledge/Agent Workflow/Agent驱动知识库、代码库与板端侧协同闭环规范]]
- [[01_Knowledge/Agent Workflow/Agent三侧角色契约规范]]
- [[01_Knowledge/Agent Workflow/Agent三侧模板与文件结构规范]]
- `AGENTS.md`

中读取，不在实例 prompt 中重复展开。

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
2. 读本文档，按任务入口、状态机和角色集合派生规则组织任务。
3. 读 [[01_Knowledge/Agent Workflow/Agent三侧角色契约规范]]，明确角色边界和最小交接要求。
4. 读 [[01_Knowledge/Agent Workflow/Agent三侧模板与文件结构规范]]，在根目录生成所需文件骨架。

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

与文档收敛相关的角色补充职责，应先写入 [[01_Knowledge/Agent Workflow/Agent三侧角色契约规范]]，再同步到 [[01_Knowledge/Agent Workflow/Agent三侧模板与文件结构规范]] 中对应角色的 `toml` 骨架。
本文档只保留状态机、门禁、角色集合派生与调度要求。

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

### 0.16.9 orchestration 实例提示补充

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

### 0.16.10 项目级 current 重写任务骨架

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
2. 再按最新轻实例 prompt 方式与 current 规范重写 current 文档组，明确：
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

### 0.16.11 板端测试在环任务骨架

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
