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
  - "02_Projects/agent-trajectory/agent_trajectory_p0_implementation_and_hook_registration-2026-07-09.md"
  - "02_Projects/agent-trajectory/agent_trajectory_scheduler_and_layered_parse_update-2026-07-09.md"
updated_at: 2026-07-09
---

# 1 Agent Trajectory 项目总览 Current

## 1.1 当前状态

本项目当前处于 `created_but_not_fully_verified` 状态，用于指导工业 agent 任务轨迹库、轻量可观测性和轨迹蒸馏系统的后续实现。

当前已形成项目级阶段性方案，并已完成 P0 最小实现、全局 passive hook 注册和 hook 外 scheduler 调度入口；真实本地 queue 已通过 scheduler 消费并刷新 Phase 0 report，但尚未完成长期 daemon、真实多任务 hook overhead、丢失率或 recoverability 验证。本 current 文档只记录当前状态、事实源、关键决策和验证缺口；详细设计、schema、phase 计划、Failure Taxonomy 和质量门禁以 [[02_Projects/agent-trajectory/agent_trajectory_initial_design]] 为事实源，P0 实现和注册结果以 [[02_Projects/agent-trajectory/agent_trajectory_p0_implementation_and_hook_registration-2026-07-09]] 为事实源，hook / collector / distiller 分层调度和 scheduler 实现以 [[02_Projects/agent-trajectory/agent_trajectory_scheduler_and_layered_parse_update-2026-07-09]] 为事实源。

本项目不声明 `single_pass_recoverable: true`。

## 1.2 当前事实源

默认事实源：

1. [[02_Projects/agent-trajectory/agent_trajectory_initial_design]]
2. [[02_Projects/agent-trajectory/agent_trajectory_p0_implementation_and_hook_registration-2026-07-09]]
3. [[02_Projects/agent-trajectory/agent_trajectory_scheduler_and_layered_parse_update-2026-07-09]]

当前方案摘要：

- 早期没有 Agent Runtime 控制权，不能稳定截获内部 planner、tool call、memory、state transition 和 evaluation 信号。
- 阶段性路线是先建设外部可观察事件的 trajectory 系统，不声称 Skill 层轨迹等价于 agent hidden state。
- 当前方案已明确 hook / collector / distiller 三层边界：hook 同步路径只做 allowlist + fail-open enqueue，collector 在 hook 外近实时或定时消费 payload 并生成 raw events，Semantic Distillation 后续按 trajectory/session 异步批处理。
- P0 已在 `/home/jichao/agent-trajectory` 完成 stdlib-only 最小实现：hook adapter enqueue、collector service raw event 落盘、baseline snapshot/artifact refs、feasibility report 和 raw event schema。
- P0 已注册全局 passive Codex hook，collector root 固定为 `/home/jichao/agent-trajectory`，通过 allowlist 采集 `/home/jichao/dms`、`/mnt/d/Knowledge-Base` 和 `/home/jichao/agent-trajectory`。
- P0 后已新增 `collector.scheduler` 和 `collector.cli schedule`：支持受锁保护的 `run_once`、`--loop --interval`、`--limit` 和 `--write-report`，推荐由 timer 或轻量 loop 在 hook 外运行，避免每次 hook 抓取后同步解析。

## 1.3 当前关键决策

- Collector 不作为 skill 落地；skill 用于后处理、回放、蒸馏、复盘和 skill mining，collector 作为观察者应做成 service。
- Codex hook 能力必须先做 feasibility spike，验证 payload、tool pre/post correlation、event ordering、权限和低延迟 enqueue 是否足够。
- Raw trajectory 由 hook adapter 触发并投递到 Trajectory Collector Service。
- Repo-local hook 只适合自测 collector；跨业务任务采集采用全局 passive hook + allowlist，避免只观测 agent-trajectory 仓库本身。
- Codex hook 包装器必须 fail-open，stdout 保持单一合法 JSON 对象 `{}`，同步路径只做 allowlist 判断和 enqueue，不运行 collector service 或 LLM。
- 每次 hook 抓取后不得同步解析；collector 解析应由 hook 外 timer、loop 或后续 daemon 执行，distiller 语义解析继续按 session/trajectory 批处理。
- Raw collection 同步路径禁止调用 LLM，只记录结构化原始事实、snapshot id 和 artifact 指针。
- Collector 当前增量边界依赖 `storage/collector_state.json` 的 `last_queue_line`；正常重复运行 scheduler 只处理新增 queue 行，但 raw event append 后、state 保存前仍存在崩溃导致重复处理的窗口。
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
3. [[02_Projects/agent-trajectory/agent_trajectory_p0_implementation_and_hook_registration-2026-07-09]]
4. [[02_Projects/agent-trajectory/agent_trajectory_scheduler_and_layered_parse_update-2026-07-09]]
5. 后续新增的 phase design、implementation、validation 或 trajectory schema 文档

不要从历史运行工件、raw trajectory、benchmark 样例或派生报告直接开始，除非任务明确要求追溯。

## 1.5 当前验证缺口

已完成但仍需真实任务验证：

- P0 最小 collector 实现、raw event schema、hook adapter、global passive hook wrapper、allowlist 和 report 生成。
- 单元测试与手动模拟 payload 到 raw event/report 的链路验证。
- Hook 外 scheduler 已完成实现和测试，`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v` 8 个测试通过。
- 真实本地 queue 已通过 `python3 -m collector.scheduler --root /home/jichao/agent-trajectory --limit 100 --write-report` 消费 90 条 queued payload，report 显示 `total_events = 91`、`raw_collection_llm_call_count = 0`、`tool_correlation.phase0_blocker = false`、`ordering.monotonic_sequence_valid = true`。

尚未完成：

- 真实新 Codex 会话中的 trajectory 采集数据验证。
- Codex hook feasibility spike 的真实 payload/correlation/ordering 结论。
- hook overhead、raw event 丢失率和真实 LLM call count 统计。
- collector service、event ordering guarantee 和 tool pre/post correlation 的长期真实任务验证。
- scheduler 长期 timer/daemon 稳定性、queue backlog、重复 `queued_envelope_id` 统计和 crash 幂等加固。
- raw event stream、snapshot、artifact index 和 distilled claims 的生产级落盘验证。
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
