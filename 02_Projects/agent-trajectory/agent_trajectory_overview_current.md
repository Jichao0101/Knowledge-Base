---
type: project_current
status: created_but_not_fully_verified
project: agent-trajectory
module: overview
current_kind: overview
single_pass_recoverable: false
sources:
  - "2026-07-07 当前对话：工业 agent 任务轨迹库、Agent Execution Event Sourcing、State Reconstruction、Failure Taxonomy 与轨迹蒸馏方案讨论"
  - "2026-07-08 当前对话：hook 触发 raw trajectory、采集阶段禁用 LLM、异步 semantic distillation 与 evidence chain 方案优化"
  - "2026-07-08 当前对话：collector service、trajectory version、event ordering、decision point、分层 snapshot、state graph 与五类资产模型方案优化"
  - "02_Projects/agent-trajectory/agent_trajectory_initial_design.md"
updated_at: 2026-07-08
---

# 1 Agent Trajectory 项目总览 Current

## 1.1 当前状态

本项目当前处于 `created_but_not_fully_verified` 状态，用于指导工业 agent 任务轨迹库、轻量可观测性和轨迹蒸馏系统的后续实现。

当前已形成项目级阶段性方案，但尚未进入真实采集、实现验证或 recoverability verification。本 current 文档只记录当前状态、事实源、关键决策和验证缺口；详细设计、schema、phase 计划、Failure Taxonomy 和质量门禁以 [[02_Projects/agent-trajectory/agent_trajectory_initial_design]] 为事实源。

本项目不声明 `single_pass_recoverable: true`。

## 1.2 当前事实源

默认事实源：

1. [[02_Projects/agent-trajectory/agent_trajectory_initial_design]]

当前方案摘要：

- 早期没有 Agent Runtime 控制权，不能稳定截获内部 planner、tool call、memory、state transition 和 evaluation 信号。
- 阶段性路线是先建设外部可观察事件的 trajectory 系统，不声称 Skill 层轨迹等价于 agent hidden state。
- 当前方案已把同步采集层和异步语义蒸馏层分离：hook adapter 只轻量触发，collector service 负责 raw collection，Semantic Distillation 才使用 LLM。

## 1.3 当前关键决策

- Collector 不作为 skill 落地；skill 用于后处理、回放、蒸馏、复盘和 skill mining，collector 作为观察者应做成 service。
- Codex hook 能力必须先做 feasibility spike，验证 payload、tool pre/post correlation、event ordering、权限和低延迟 enqueue 是否足够。
- Raw trajectory 由 hook adapter 触发并投递到 Trajectory Collector Service。
- Raw collection 同步路径禁止调用 LLM，只记录结构化原始事实、snapshot id 和 artifact 指针。
- Raw event schema 必须包含 trajectory schema version、collector version 和 ordering metadata。
- Snapshot 分为 baseline、incremental 和 decision checkpoint 三层，避免每个 event 都做全量 snapshot。
- Raw event stream 和 Raw Event Store 必须 append-only，不被蒸馏结果覆盖。
- Raw events 不生成完整 causal_link；Distilled Causal Link 由异步 distiller 生成，human review 只审核关键 decision point。
- LLM 只用于异步 Semantic Distillation，输入为 raw event stream、snapshot 和 artifact index。
- Distilled trajectory 必须保存 claim-level evidence chain，保证 interpreted intent、causal_link、uncertainty、failure_tags 和 state hints 可追溯到 raw event、snapshot 或 artifact。
- State Reconstruction 初期输出 state graph，不直接抽象 FSM。
- 数据流当前收敛为五类资产：Raw Event Store、Snapshot Store、Distilled Experience Store、Failure Knowledge Base、Benchmark Repository。

## 1.4 默认恢复顺序

后续恢复本项目上下文时，默认按以下顺序读取：

1. `02_Projects/agent-trajectory/agent_trajectory_overview_current.md`
2. [[02_Projects/agent-trajectory/agent_trajectory_initial_design]]
3. 后续新增的 phase design、implementation、validation 或 trajectory schema 文档

不要从历史运行工件、raw trajectory、benchmark 样例或派生报告直接开始，除非任务明确要求追溯。

## 1.5 当前验证缺口

尚未完成：

- 真实 trajectory 采集数据验证。
- Codex hook feasibility spike。
- hook overhead、raw event 丢失率和 LLM call count 统计。
- collector service、event ordering guarantee 和 tool pre/post correlation 验证。
- raw event stream、snapshot、artifact index 和 distilled claims 的实际落盘验证。
- trajectory schema version 与 distillation run version 的重跑对比验证。
- decision point schema 与人工 review 流程验证。
- 分层 snapshot 成本和可重建性验证。
- 100 条轨迹的人工 State Reconstruction review。
- state graph 稳定性验证；FSM/policy graph 抽象暂不作为当前目标。
- Counterfactual Stability 指标 rubric 稳定化。
- Failure Taxonomy 基于真实失败样本校准。
- Skill Mining 和 Benchmark Generation 的 holdout 验证。
- 独立 recoverability verification。

因此当前状态保持 `created_but_not_fully_verified`，不得提升为正式知识，不得声明 `single_pass_recoverable: true`。
