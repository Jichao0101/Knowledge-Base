---
title: Board-First调查型模板并入方案
summary: 在现有 Agent 三侧运行规范的 plan-first 主链之外，补充一个以板端现象、日志、trace、指标和异常产物为起点的正式入口模式，用于先完成 triage、证据裁剪、根因假设与问题分类，再分流进入 bug_fix、optimization、audit 或环境处理链路。
sources:
  - 01_Knowledge/Agent Workflow/Agent三侧运行规范与调度模板.md
  - 01_Knowledge/Agent Workflow/Agent驱动知识库、代码库与板端侧协同闭环规范.md
  - 01_Knowledge/Agent Workflow/Agent三侧模板与文件结构规范.md
scope: 适用于问题尚未被人工定义清楚，但已具备板端现象、日志、trace、指标、视频、dump、错误码等 board artifacts 的调查型任务。
not_applicable:
  - 人工已明确给出预期行为、实际行为、验收标准和修复计划的标准缺陷修复任务
  - 人工已明确给出优化依据、基线指标、目标指标和非目标项的标准受控优化任务
status: draft
updated_at: 2026-04-07
---

# 1 新增模式的必要性与问题定义

## 1.1 现有模板的不足

现有三侧运行规范中的 `bug_fix` 与 `optimization` 模板本质上属于 `plan-first` 入口，默认前提是人工已经先完成任务定性。

现有缺陷修复型模板依赖人工预先给出：

- `task_goal`
- `expected_behavior`
- `actual_behavior`
- `known_evidence`
- `acceptance_criteria`
- `fix_plan`

现有受控优化型模板依赖人工预先给出：

- `optimization_basis`
- `baseline_metrics`
- `target_metrics`
- `non_goals`
- `risk_boundary`
- `optimization_plan`

这类入口适用于“问题已经被人描述清楚”的任务，不适用于以下场景：

- 只知道板端出现异常，但尚不能准确描述其语义
- 只有日志、trace、指标、录像、dump、stdout/stderr、错误码
- 只有现象，没有稳定根因
- 需要先从板端 artifacts 中自行归因，再判断是 `bug_fix / optimization / audit / env_issue / replan`
- 需要先做 failure triage，再决定是否进入修复或优化链路

## 1.2 为什么不能把它退化成 bug_fix 的附加说明

board-first 调查型任务与标准 `bug_fix` 的根本区别在于：入口对象不是“已定义问题”，而是“待定性现象”。

若把它仅作为 `bug_fix` 附加说明，会产生四个制度缺口：

- 系统会错误要求人工先定义 `expected_behavior / actual_behavior / acceptance_criteria`
- `failure-analyst` 会被降级为 bug_fix 内的可选辅助，而不是主链前置角色
- reviewer 容易把“证据不足”误处理为“实现不足”，强行推动代码修改
- 状态机会跳过 triage、classification、hypothesis management，直接进入 implementation，导致闭环方向错误

因此，必须将其设计为与 `plan-first` 并列的正式入口模式，而不是现有模板的松散补丁。

# 2 新增正式入口模式

## 2.1 命名与定位

新增正式入口模式：

- `primary_type = incident_investigation`

定义：

- `incident_investigation` 是三侧闭环中的正式主类型，用于承接“问题尚未定义清楚，但已经存在板端现象或日志产物”的任务入口。
- 它不是 `bug_fix` 的子类型，也不是 `optimization` 的别名。
- 它负责在进入既有实施链路之前完成 `evidence framing -> triage -> hypothesis generation -> classification -> route decision`。

建议默认修饰属性：

- `read_only`
- `review_required`
- `failure_investigation`
- `board_artifact_collection_required`

按需增加：

- `board_execution_required`
- `code_change_allowed`
- `requires_web`
- `writeback_required`

## 2.2 与既有主类型的关系

`incident_investigation` 与现有主类型关系如下：

- 它位于 `bug_fix / optimization / audit` 之前，承担问题定性与分流
- 它本身不预设必须改代码
- 它允许输出“暂不改代码”“先补观测”“先补采样”“先确认设计预期”“判定为环境问题”
- 它完成后通过 `route_decision` 分流到既有模板链路

分流目标：

- `route_decision = bug_fix`
- `route_decision = optimization`
- `route_decision = audit`
- `route_decision = env_issue`
- `route_decision = deployment_issue`
- `route_decision = observability_gap`
- `route_decision = replan`
- `route_decision = close_insufficient_evidence`

## 2.3 关闭、转派与升级条件

`incident_investigation` 在以下条件下转派：

- 已形成可检验根因假设，且分类为代码缺陷：转 `bug_fix`
- 已确认核心行为正确，但存在性能收益空间：转 `optimization`
- 已确认问题本质是行为定义或设计预期不一致：转 `audit`
- 已确认主要问题来自板端环境、部署或打包：转环境链路，不直接进入 repo 修复

在以下条件下直接 `closed`：

- 证据不足且无法补采样，结论为 `insufficient_evidence`
- 异常属于一次性偶发现象，无法稳定复现，且没有足够高价值继续调查
- 已证明并非代码问题，且当前任务不要求继续处理环境或部署链路

在以下条件下必须 `replan / escalate`：

- 问题分类在多条主链之间摇摆且无法区分
- 需要跨模块或跨仓库结构性变更才能验证假设
- 缺少核心设计预期，且没有可用的知识上下文支撑
- 需要新增高成本观测、长周期实验或外部依赖

# 3 Board-First 入口对象补充

## 3.1 入口对象定义

在现有 `task entry` 基础上，`incident_investigation` 必须额外提供以下输入对象：

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

## 3.2 字段定义

### 3.2.1 `observed_symptoms`

记录人工已经观察到的现象，不要求先给出根因。

子字段：

- `symptom_summary`
- `symptom_category`: `board_runtime / deployment / environment / effect_quality / performance / crash / hang / timeout / data_mismatch / unknown`
- `first_seen_at`
- `seen_frequency`
- `user_visible_impact`
- `severity_guess`

### 3.2.2 `artifact_inventory`

枚举已存在证据，不要求其已整理完毕。

子字段：

- `artifact_type`: `log / trace / metrics / video / dump / stderr / stdout / error_code / screenshot / core / config_snapshot`
- `artifact_path_or_ref`
- `time_range`
- `source_host`
- `retention_status`
- `integrity_status`

### 3.2.3 `log_sources`

记录证据来源与采集入口。

子字段：

- `board_logs`
- `service_logs`
- `kernel_logs`
- `application_stdout`
- `application_stderr`
- `trace_channel`
- `metrics_channel`
- `video_channel`
- `dump_channel`

### 3.2.4 `trigger_condition`

记录异常被触发的上下文。

子字段：

- `trigger_type`: `always / intermittent / load_related / time_related / scene_related / deploy_related / startup_related / shutdown_related / unknown`
- `trigger_steps`
- `trigger_inputs`
- `trigger_dependencies`

### 3.2.5 `reproduction_confidence`

记录复现确定性。

取值：

- `stable`
- `semi_stable`
- `flaky`
- `one_off`
- `unknown`

### 3.2.6 `signal_expectations`

若已知设计预期，则给出预期信号；若未知，则显式标记未知。

子字段：

- `expectation_known`: `true | false`
- `expected_logs`
- `expected_metrics`
- `expected_outputs`
- `expected_timing`
- `expected_state_transitions`

### 3.2.7 `environment_fingerprint`

记录环境指纹，防止把环境问题误归为代码问题。

子字段：

- `firmware_version`
- `package_version`
- `build_id`
- `config_hash`
- `dependency_versions`
- `hardware_revision`
- `runtime_mode`
- `resource_snapshot`

### 3.2.8 `board_session_info`

记录本轮板端会话身份。

子字段：

- `board_target_id`
- `ssh_target`
- `workspace_path`
- `session_started_at`
- `session_operator`
- `deploy_artifacts`
- `run_commands`
- `collect_paths`

### 3.2.9 `anomaly_window`

定义异常时间窗。

子字段：

- `window_start`
- `window_end`
- `relative_to_trigger`
- `clock_alignment_status`

### 3.2.10 `issue_scope_guess`

仅允许写“怀疑范围”，不允许把猜测直接当成根因。

取值：

- `board_side_only`
- `deployment_path`
- `runtime_environment`
- `service_logic`
- `algorithm_effect`
- `performance_path`
- `cross_layer`
- `unknown`

### 3.2.11 `available_evidence` 与 `missing_evidence`

必须同时列出已有证据与缺口，避免系统默认“现有证据足够”。

### 3.2.12 `whether_design_expectation_known`

必须显式区分：

- `known`
- `partially_known`
- `unknown`

若为 `unknown`，则 investigation 不得直接产出确定性 `bug_fix` 方案，只能先产出分类建议、补证计划或审计路线。

## 3.3 入口对象判别维度

planner 必须基于入口对象显式判断以下维度：

- 设计预期是否已知：`known / partially_known / unknown`
- 复现状态：`stable / semi_stable / flaky / one_off / unknown`
- 异常类型：`board_anomaly / deployment_anomaly / environment_anomaly / effect_anomaly / performance_anomaly`

# 4 状态机补充

## 4.1 Board-First 专属状态

在现有状态机中新增 investigation 前置状态：

1. `symptom_received`
2. `artifact_bound`
3. `evidence_collected`
4. `triage_ready`
5. `hypothesis_generated`
6. `classification_decided`
7. `routed_to_bug_fix`
8. `routed_to_optimization`
9. `routed_to_audit`
10. `routed_to_env_issue`
11. `investigation_closed`

其中：

- `symptom_received` 到 `classification_decided` 为 board-first 专属状态
- `routed_to_*` 为从 board-first 转入既有主链的桥接状态
- `investigation_closed` 为不进入后续主链时的关闭态

## 4.2 与原有状态机的映射

映射关系如下：

- `task_received` 之后，若 `primary_type = incident_investigation`，进入 `symptom_received`
- `scope_confirmed` 保持不变
- `board_bound` 对应 `artifact_bound` 的前提条件
- `context_retrieved` 后，不直接进入 `plan_ready`，而是先进入 `evidence_collected`
- `triage_ready` 替代 plan-first 下的“问题已定义完成”前置条件
- `hypothesis_generated` 与 `classification_decided` 是进入既有 `plan_ready` 前的门禁
- 只有在 `classification_decided` 之后，才允许生成 `implementation_plan` 或 `audit_plan`
- 若分流到既有主链，则重新进入既有 `plan_ready -> execution_approved -> implementation_done -> board_executed -> repo_review_done -> writeback_done -> board_sync_done -> closed`

## 4.3 状态定义

### 4.3.1 `symptom_received`

已接收板端现象与最小入口对象，但尚未绑定 artifacts。

进入条件：

- 已给出 `observed_symptoms`
- 已给出 `board_target` 或 `no_board_execution` 理由
- 已给出 `allowed_paths`

阻断条件：

- 现象为空
- 无板端目标且无替代说明
- 允许范围不清

### 4.3.2 `artifact_bound`

已绑定本轮调查所用 artifacts 与采集来源。

进入条件：

- 已给出 `artifact_inventory`
- 已给出 `log_sources`
- 已给出 `anomaly_window`
- 已给出 `environment_fingerprint`

阻断条件：

- 关键 artifacts 无法定位
- 时间窗无法对齐
- 环境指纹缺失到无法排除部署或环境漂移

### 4.3.3 `evidence_collected`

已完成最小证据采集、去噪与裁剪。

进入条件：

- 已整理 `available_evidence`
- 已整理 `missing_evidence`
- 已完成最小异常片段截取
- 已标注高噪声与低可信信号

阻断条件：

- 只有全量原始日志，没有裁剪后的可审查证据
- 证据无法映射到异常时间窗
- 证据链中断

### 4.3.4 `triage_ready`

已可以进入问题定性，不代表已找到根因。

进入条件：

- 已完成现象归档
- 已完成异常聚类或同类现象归并
- 已完成初步分类候选
- 已识别信息缺口与补采样优先级

阻断条件：

- 现象仍混杂为多个未拆分事件
- 噪声与主异常未分离
- 没有下一步 probe 计划

### 4.3.5 `hypothesis_generated`

已生成可检验假设集，而不是单一拍脑袋结论。

进入条件：

- 至少一个 `root_cause_hypothesis`
- 每个假设对应 `supporting_evidence`
- 每个假设对应 `contradicting_evidence`
- 已给出 `hypothesis_confidence`
- 已给出 `next_probe_actions`

阻断条件：

- 只有结论，没有证据映射
- 只有现象复述，没有可检验假设
- 设计预期未知却产出确定性修复方案

### 4.3.6 `classification_decided`

已完成问题分类与分流决策。

进入条件：

- 已输出 `classification`
- 已输出 `route_decision`
- 已输出 `route_rationale`
- 已输出 `route_blockers`

阻断条件：

- 分类与证据不一致
- 分流目标不清
- 需要补观测但仍试图直接进入实现

### 4.3.7 `routed_to_bug_fix / routed_to_optimization / routed_to_audit / routed_to_env_issue`

表示 investigation 已完成前置收敛，进入对应主链。

桥接要求：

- 必须生成分流后的标准化入口对象
- 必须补齐目标主链所需字段
- 必须保留 investigation 的证据边界与未决假设

### 4.3.8 `investigation_closed`

不进入后续修复或优化链，直接以调查结论结束。

适用条件：

- `insufficient_evidence`
- `one_off low_value incident`
- `env_issue confirmed but out_of_scope`
- `design expectation unknown and cannot be resolved in current task`

## 4.4 从 investigation 进入既有主链的门禁

以下 blocker 任一命中，均不得从 investigation 进入 `bug_fix / optimization`：

- `evidence_sufficiency = insufficient`
- `classification_confidence = low`
- `route_correctness = unresolved`
- `design_expectation_status = unknown`
- `reproduction_confidence = one_off` 且无高价值确定性证据
- 环境漂移尚未排除
- 部署完整性尚未排除

# 5 角色职责补充

## 5.1 knowledge-planner

在 `incident_investigation` 模式下，`knowledge-planner` 不再默认从 `implementation_plan` 开始，而是先输出 `investigation_plan`。

新增职责：

- 完成 `evidence framing`
- 识别信息缺口
- 判断设计预期是否已知
- 组织 triage 顺序
- 给出初步分类候选
- 给出 `verification_tier`
- 给出 investigation 阶段的 `required / optional / unavailable` 验证集合

输出补充：

- `investigation_plan`
- `evidence_gap_analysis`
- `triage_plan`
- `classification_candidates`
- `route_preconditions`

## 5.2 failure-analyst

`failure-analyst` 在 board-first 模式下升级为核心角色，而不是 bug_fix 内的附属角色。

核心职责：

- 从日志、trace、指标、视频、错误码、dump 中提出根因假设
- 区分根因、表象、伴随噪声和环境问题
- 评估 `hypothesis_confidence`
- 排序 `evidence_priority`
- 产出 `next_probe_actions`

输出补充：

- `hypothesis_set`
- `hypothesis_confidence`
- `supporting_evidence_map`
- `contradicting_evidence_map`
- `noise_signals`
- `environmental_suspicions`
- `observability_gaps`

停止条件补充：

- 无法构造可检验假设
- 关键证据无法绑定到异常窗口
- 设计预期缺失导致所有假设不可判别

## 5.3 repo-coder

在 board-first 模式下，`repo-coder` 不默认先修代码。

允许承担的工作包括：

- 增强日志
- 增加统计
- 新增 trace 点
- 添加守卫
- 增加 dump / profile 钩子
- 做最小复现实验
- 做针对性采集脚本
- 做实验性验证

禁止默认行为：

- 在 `classification_decided` 前直接实施业务修复
- 在证据不足时“顺手修一个看起来可能有问题的点”

输出补充：

- `instrumentation_changes`
- `probe_results`
- `capture_scripts`
- `post_instrumentation_artifacts`
- `fix_deferred_reason`

## 5.4 repo-reviewer

在 board-first 模式下，`repo-reviewer` 不只审 diff，还要审调查闭环是否成立。

新增职责：

- 审查问题分类是否成立
- 审查证据是否足够支撑分流
- 审查假设是否闭环
- 审查是否把环境问题误当代码问题
- 审查“暂不改代码”的结论是否成立

可接受结论：

- `approve_route_to_bug_fix`
- `approve_route_to_optimization`
- `approve_route_to_audit`
- `approve_route_to_env_issue`
- `approve_more_instrumentation_only`
- `approve_close_with_insufficient_evidence`
- `reject_due_to_misclassification`

## 5.5 knowledge-closer

在 board-first 模式下，`knowledge-closer` 必须回写 investigation 结果，而不仅是修复结果。

必写内容：

- `investigation_summary`
- `evidence_boundary`
- `unresolved_hypotheses`
- `route_decision`
- `route_rationale`
- `followup_required`

若未进入既有主链，也必须完整记录“为什么当前轮只调查、不修复”。

# 6 分类与分流规则

## 6.1 分类集合

调查阶段至少支持以下分类：

- `code_defect`
- `design_mismatch`
- `missing_observability`
- `board_environment_issue`
- `deployment_or_packaging_issue`
- `performance_bottleneck`
- `flaky_low_reproducibility_issue`
- `insufficient_evidence`

## 6.2 分类后的处理规则

### 6.2.1 `code_defect`

- 后续链路：转 `bug_fix`
- 是否允许直接修代码：允许，但必须先完成最小根因闭环
- 是否必须先补采样或实验：当证据只能定位现象、不能定位缺陷路径时必须先补
- 是否要求重新规划：若修复范围明显扩大则要求

### 6.2.2 `design_mismatch`

- 后续链路：转 `audit`，必要时再转 redesign 或 bug_fix
- 是否允许直接修代码：默认不允许
- 是否必须先补采样或实验：通常不强制，重点是确认规范与预期
- 是否要求重新规划：是

### 6.2.3 `missing_observability`

- 后续链路：先进入观测增强子链，再回 `incident_investigation`
- 是否允许直接修代码：不允许直接修业务逻辑
- 是否必须先补采样或实验：必须
- 是否要求重新规划：通常不需要大 replan，但需输出 instrumentation plan

### 6.2.4 `board_environment_issue`

- 后续链路：转 `env_issue`
- 是否允许直接修代码：默认不允许
- 是否必须先补采样或实验：按需补环境指纹、资源快照、依赖状态
- 是否要求重新规划：若影响范围超过当前任务，要求

### 6.2.5 `deployment_or_packaging_issue`

- 后续链路：转部署或打包修复链路，可按项目制度映射为 `bug_fix`
- 是否允许直接修代码：仅允许修改部署、打包、配置相关内容
- 是否必须先补采样或实验：需要完成部署一致性验证
- 是否要求重新规划：若波及构建和发布链则要求

### 6.2.6 `performance_bottleneck`

- 后续链路：转 `optimization`
- 是否允许直接修代码：允许，但必须具备基线与收益验证路径
- 是否必须先补采样或实验：通常必须
- 是否要求重新规划：若优化需要结构性重构则要求

### 6.2.7 `flaky_low_reproducibility_issue`

- 后续链路：保留在 investigation 或转观测增强子链
- 是否允许直接修代码：默认不允许
- 是否必须先补采样或实验：必须
- 是否要求重新规划：当采样成本高或周期长时要求

### 6.2.8 `insufficient_evidence`

- 后续链路：可直接 `investigation_closed` 或 `replan`
- 是否允许直接修代码：不允许
- 是否必须先补采样或实验：若任务继续则必须
- 是否要求重新规划：是

# 7 验证机制补充

## 7.1 Board-First 验证结构

`incident_investigation` 下的验证集合至少包括：

- `reproduction_verification`
- `evidence_sufficiency_check`
- `hypothesis_discrimination_check`
- `route_correctness_check`
- `post_instrumentation_validation`
- `fix_validation`
- `gain_validation`

## 7.2 required / optional / unavailable 规则

### 7.2.1 `reproduction_verification`

- `required`：当任务声称可稳定或半稳定复现时
- `optional`：当问题已由强证据直接指向根因，即使复现弱
- `unavailable`：一次性故障且现场已消失

### 7.2.2 `evidence_sufficiency_check`

- `required`：所有 investigation 任务
- 结论允许为 `insufficient`
- 当结论为 `insufficient` 时，不得硬凑修复方案

### 7.2.3 `hypothesis_discrimination_check`

- `required`：存在两个及以上竞争假设时
- `optional`：单一高置信假设且无明显冲突证据时
- `unavailable`：缺乏足以区分假设的信号

### 7.2.4 `route_correctness_check`

- `required`：所有进入分流决策的 investigation 任务
- 目标是确认没有把环境问题路由到代码修复，没有把设计问题路由到性能优化

### 7.2.5 `post_instrumentation_validation`

- `required`：当采取“先补观测”方案时
- `optional`：未做 instrumentation 变更时

### 7.2.6 `fix_validation`

- 仅在最终转入 `bug_fix` 后成为 `required`

### 7.2.7 `gain_validation`

- 仅在最终转入 `optimization` 后成为 `required`

## 7.3 证据不足何时本身就是结论

以下情况允许把“证据不足”作为正式结论，而不是继续制造伪确定性：

- 关键 artifacts 已丢失且无法补采样
- 问题为 `one_off`，且无足够重现条件
- 设计预期未知，且当前任务无权限补齐设计依据
- 环境状态已变更，无法恢复现场

此时输出必须收敛为：

- 当前可确认事项
- 当前无法确认事项
- 最小可验证路径
- 继续调查所需新增条件

不得输出完整修复方案。

## 7.4 何时只能输出最小可验证路径

满足任一条件时，只能输出 `minimal_verifiable_path`：

- `classification_confidence < medium`
- `hypothesis_confidence < medium`
- 关键验证为 `unavailable`
- 设计预期为 `partially_known / unknown`
- 复现为 `flaky / one_off`

# 8 调度 Prompt 模板

## 8.1 板端异常调查型调度 Prompt

```md
# 任务名称
板端异常调查型 / Board-First Incident Investigation

# 主类型
incident_investigation

# 任务修饰属性
failure_investigation
review_required
board_artifact_collection_required
board_execution_required | no_board_execution
code_change_allowed | read_only
writeback_required
requires_web | no_web

# 任务目标
从板端现象、日志、trace、指标、dump、视频或错误码出发，先完成现象归档、证据裁剪、异常聚类、根因假设生成与问题分类，再决定后续进入 bug_fix、optimization、audit、env_issue 或 replan，不得在问题未定性时强行进入修复。

# 观测现象
- observed_symptoms:
- symptom_category:
- severity_guess:
- first_seen_at:
- seen_frequency:

# 板端描述
- board_target:
- board_target_id:
- ssh_target:
- workspace_path:
- deploy_artifacts:
- run_commands:
- collect_paths:
- board_session_info:
- environment_fingerprint:

# 已有 artifacts
- artifact_inventory:
- log_sources:
- anomaly_window:
- available_evidence:
- missing_evidence:

# 触发与复现
- trigger_condition:
- reproduction_confidence:
- issue_scope_guess:
- whether_design_expectation_known:
- signal_expectations:

# 允许范围
- allowed_paths:
- repo_scope:
- writable_targets:

# 权限与限制
- 是否允许代码修改:
- 是否允许只增加观测而不修复:
- 是否允许部署或重新采集:
- 是否允许联网:
- confirmation_policy:

# triage 与分类要求
1. 先调用 knowledge-planner，输出 investigation_plan、evidence_gap_analysis、triage_plan、classification_candidates、verification_tier、required/optional/unavailable 验证集合。
2. 若证据复杂或问题未定性，必须调用 failure-analyst，输出 hypothesis_set、hypothesis_confidence、evidence_priority、noise_signals、next_probe_actions。
3. 如需要最小观测增强或复现实验，再调用 repo-coder，但其职责优先是 instrumentation、probe、capture，不默认修复业务逻辑。
4. 调查完成后必须产出 classification、route_decision、route_rationale、route_blockers。
5. classification 至少在 code_defect、design_mismatch、missing_observability、board_environment_issue、deployment_or_packaging_issue、performance_bottleneck、flaky_low_reproducibility_issue、insufficient_evidence 中选择。

# reviewer 独立性要求
1. repo-reviewer 必须独立调度。
2. reviewer 输入必须裁剪为：任务目标、现象描述、调查计划、关键证据、假设集、分流建议、必要 diff、验证结果、板端 artifacts。
3. 不向 reviewer 传入 repo-coder 的完整排查对话。
4. reviewer 必须审查证据充分性、假设区分性、分类正确性、路由正确性，以及“是否允许暂不改代码”。

# route decision 输出要求
- classification:
- classification_confidence:
- route_decision:
- route_rationale:
- route_blockers:
- minimal_verifiable_path:
- followup_owner:

# writeback 要求
1. knowledge-closer 必须回写 investigation_summary、evidence_boundary、unresolved_hypotheses、route_decision、followup_required。
2. 若未进入修复或优化主链，也必须回写“为何当前轮只调查、不修复”。
3. 不得把未经审查的结论提升为正式知识。

# 完成判定
- 若 route_decision 已明确且门禁满足，则转入对应既有模板。
- 若结论为 insufficient_evidence 或 out_of_scope env_issue，可直接 investigation_closed。
- 若分类冲突或 scope creep 命中，则 replan / escalate。
```

# 9 与现有模板的衔接

## 9.1 何时使用现有缺陷修复型模板

满足以下条件时，直接使用现有 `bug_fix` 模板：

- 人工已清楚描述 `expected_behavior` 与 `actual_behavior`
- 已有足够证据支持缺陷语义
- 已有明确验收标准
- 已可直接进入修复计划

## 9.2 何时使用现有受控优化型模板

满足以下条件时，直接使用现有 `optimization` 模板：

- 优化目标和收益指标已定义
- 基线指标已知
- 非目标项清晰
- 问题本质不是“为什么异常发生”，而是“如何在已知正确语义下提升收益”

## 9.3 何时应先使用新的 board-first 模板

满足以下任一条件，应优先使用 `incident_investigation`：

- 只有板端现象或异常产物，没有清晰问题定义
- 根因未知，甚至不确定是不是代码问题
- 设计预期未知或仅部分已知
- 复现不稳定，需要先做 triage 与假设管理
- 当前最需要的是证据裁剪、分类与分流，而不是立即修改代码

## 9.4 board-first 结束后如何无缝转入既有模板

分流时必须生成目标主链的标准化入口对象：

### 9.4.1 转入 `bug_fix`

补齐：

- `expected_behavior`
- `actual_behavior`
- `known_evidence`
- `acceptance_criteria`
- `root_cause_hypothesis`
- `minimal_fix_scope`

### 9.4.2 转入 `optimization`

补齐：

- `optimization_basis`
- `baseline_metrics`
- `target_metrics`
- `non_goals`
- `gain_validation_plan`

### 9.4.3 转入 `audit`

补齐：

- `normative_sources`
- `acceptance_items`
- `design_expectation_gaps`
- `audit_scope`

## 9.5 run_log / audit_log 补充字段

建议新增以下字段：

- `entry_mode`: `plan_first | board_first`
- `symptom_category`
- `artifact_count`
- `reproduction_confidence`
- `design_expectation_status`
- `classification`
- `classification_confidence`
- `route_decision`
- `route_blockers`
- `evidence_sufficiency`
- `hypothesis_count`
- `top_hypothesis_confidence`
- `instrumentation_only_rounds`
- `investigation_closed_reason`

# 10 可直接并入运行规范文档的章节文本

## 10.1 在“0.3 任务入口”下新增章节

### 10.1.1 board-first 正式入口模式

当任务的已知信息主要来自板端现象、日志、trace、指标、视频、dump 或错误码，而不是人工已定义清楚的问题说明时，应使用 `primary_type = incident_investigation`。

该主类型负责先完成：

- 现象归档
- artifacts 绑定
- 证据裁剪
- 异常聚类
- 根因假设生成
- 问题分类
- 路由决策

再决定是否转入既有 `bug_fix / optimization / audit` 主链。

`incident_investigation` 不要求任务一开始就具备：

- `expected_behavior`
- `actual_behavior`
- `acceptance_criteria`
- `fix_plan`
- `optimization_basis`

但要求具备最小调查入口对象，包括：

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

若 investigation 完成后形成稳定分类，再转入既有主链；若结论为 `insufficient_evidence / env_issue / design_mismatch / observability_gap`，允许不进入代码修复。

## 10.2 在“0.4 运行状态机”下新增章节

### 10.2.1 0.4.1.5A investigation 前置状态

当 `primary_type = incident_investigation` 时，在 `context_retrieved` 与 `plan_ready` 之间新增前置状态：

1. `symptom_received`
2. `artifact_bound`
3. `evidence_collected`
4. `triage_ready`
5. `hypothesis_generated`
6. `classification_decided`
7. `routed_to_bug_fix | routed_to_optimization | routed_to_audit | routed_to_env_issue | investigation_closed`

只有到达 `classification_decided` 且通过 `evidence_sufficiency`、`hypothesis_discrimination` 与 `route_correctness` 门禁后，才允许进入既有 `plan_ready`。

## 10.3 在“0.6 子代理调用矩阵”下新增章节

### 10.3.1 0.6.4A `incident_investigation + review_required`

- 主代理职责：维护 investigation 状态机、控制 triage 门禁、控制 route decision、控制 reviewer 独立性
- 必须显式调用的子代理：`knowledge-planner`、`failure-analyst`、`repo-reviewer`、`knowledge-closer`
- 条件启用的子代理：`repo-coder`、`verification-manager`、`source-ingestor`
- 可被主代理轻量吸收的职责：调查摘要编排、route decision 汇总

若 investigation 需要补采样、补 trace、补日志或复现实验，可调用 `repo-coder` 做 instrumentation 或 probe，但不默认进入业务修复。

## 10.4 在“0.9 角色输入输出契约”下新增补充

### 10.4.1 0.9.1A knowledge-planner in incident mode

输出 `investigation_plan`，而不是直接输出 `implementation_plan`。

### 10.4.2 0.9.6A failure-analyst in incident mode

输出 `hypothesis_set / hypothesis_confidence / evidence_priority / next_probe_actions / observability_gaps / route_suggestion`。

### 10.4.3 0.9.2A repo-coder in incident mode

优先负责 instrumentation、probe、capture、最小复现实验与证据补强，而不是默认直接修复业务逻辑。

### 10.4.4 0.9.3A repo-reviewer in incident mode

必须审查：

- 分类是否成立
- 证据是否足够
- 假设是否闭环
- 是否误将环境问题当代码问题
- 是否允许得出“暂不改代码”的结论

### 10.4.5 0.9.8A knowledge-closer in incident mode

必须回写 `investigation_summary / evidence_boundary / unresolved_hypotheses / route_decision / followup_required`。

# 11 最小改动并入方案

若不希望大改现有文档，最少应做以下增量插入：

1. 在“0.3 任务入口”补一节 `0.3.5 board-first 正式入口模式`，新增 `primary_type = incident_investigation` 与入口字段集合。
2. 在“0.4 运行状态机”补一节 investigation 前置状态，新增 `symptom_received -> classification_decided -> routed_to_*`。
3. 在“0.6 子代理调用矩阵”新增 `incident_investigation + review_required` 一节。
4. 在“0.9 角色输入输出契约”补充 `knowledge-planner / failure-analyst / repo-coder / repo-reviewer / knowledge-closer` 的 incident mode 行为。
5. 在“0.11 run_log / audit_log”增加 `entry_mode / classification / route_decision / evidence_sufficiency / reproduction_confidence / design_expectation_status` 字段。
6. 在“0.13 调度 prompt 模板”新增一份“板端异常调查型”完整模板。

这组改动可以不重写现有 `bug_fix / optimization` 模板，只是在它们之前加一个正式分流入口。

# 12 推荐重构并入方案

若允许做体系化优化，建议把现有入口统一为“双入口单分流框架”：

## 12.1 统一入口层

统一为两类入口：

- `entry_mode = plan_first`
- `entry_mode = board_first`

统一保留既有 `primary_type`，但允许：

- `entry_mode = plan_first` 时直接进入 `bug_fix / optimization / audit / implementation`
- `entry_mode = board_first` 时先进入 `incident_investigation`，再分流到上述主链

## 12.2 统一 plan_state

将现有 `plan_state` 扩展为：

- `entry_mode`
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

这样 plan-first 与 board-first 共享同一个状态容器，只是必填字段不同。

## 12.3 统一验证门禁

所有主链统一经过两类门禁：

- 入口门禁：确认 `plan_ready` 或 `classification_decided`
- 执行门禁：确认 `implementation_done / board_executed / repo_review_done`

board-first 在入口门禁前多一段 investigation 状态机，plan-first 则直接进入 `plan_ready`。

## 12.4 统一 review 语义

把 reviewer 的职责统一成两层：

- `route review`：审查问题分类、证据充分性和分流正确性
- `change review`：审查实现正确性、验证覆盖和回归风险

这样 `repo-reviewer` 在 board-first 与 plan-first 中仍是同一角色，只是审查焦点不同。

## 12.5 统一 writeback

无论入口模式如何，`knowledge-closer` 都按统一结构回写：

- `task_summary`
- `evidence_boundary`
- `decision_summary`
- `verification_summary`
- `route_decision`
- `unresolved_items`

这样可以避免 plan-first 只回写修复、board-first 只回写调查，导致知识结构割裂。
