---
type: project_record
status: draft
project: agent-trajectory
module: trajectory-system-design
summary: "在开发初期没有 Agent Runtime 控制权时，以 hook feasibility spike 为前置验证，用 hook adapter + collector service 采集 raw events，并通过分层 snapshot、异步 Semantic Distillation、decision point、state graph、Failure Knowledge Base 和 Benchmark Repository 构建阶段性 trajectory 系统。"
sources:
  - "2026-07-07 当前对话：工业 agent 任务轨迹库、Trace Capture、State Reconstruction、Skill Mining 与 Benchmark Generation 方案讨论"
  - "2026-07-08 当前对话：hook 触发 raw trajectory、采集阶段禁用 LLM、异步 semantic distillation 与 evidence chain 方案优化"
  - "2026-07-08 当前对话：collector service、trajectory version、event ordering、decision point、分层 snapshot、state graph 与五类资产模型方案优化"
  - "2026-07-09 当前对话：异步 Semantic Distillation 作为 repo-local 中文 skill 并软链接到用户级 skills 目录的实现方案"
scope: "agent-trajectory 项目的初始架构设计；覆盖工业 agent 任务轨迹库、轻量 observability、轨迹蒸馏、状态重建、skill mining 和 benchmark generation。"
risks:
  - "当前方案尚未经过真实 trajectory 采集、人工 reconstruction review 或 holdout benchmark 验证。"
  - "非 Runtime 级观测只能采集外部可观察事件，不能声称等价于 Agent Runtime hidden state。"
  - "Semantic Distillation 可能产生后验叙事，必须通过 evidence chain 约束，不能替代 raw event stream。"
  - "Codex hook 是否能提供足够的 tool input/output、session、ordering 和 correlation 信息尚未验证，collector service 落地前必须先做 hook feasibility spike。"
updated_at: 2026-07-09
---

# 1 Agent 执行事件溯源与轨迹蒸馏系统初始设计

## 1.1 迁移记录

本方案作为 agent-trajectory 项目的初始设计记录。项目当前入口为 [[02_Projects/agent-trajectory/agent_trajectory_overview_current]]。后续实现、验证和阶段记录应优先写入该项目；正式知识提升仍需真实轨迹、人工 review 和 holdout 验证。

## 1.2 背景

工业 agent 的早期建设需要高质量任务轨迹库。理想方案是通过 Wrapper Agent 或 Agent Runtime 统一采集任务执行过程，但开发初期往往没有 Runtime 控制权，也无法稳定截获内部 planner、tool call、memory、state transition 和 evaluation 信号。

因此，阶段性方案是把 Trace Capture 的定位从普通日志采集提升为 **Agent Execution Event Sourcing Layer**：先验证 Codex hook 是否足以支撑动作轨迹采集，再用 hook adapter 把可观察事件轻量投递给独立 collector service。collector service 负责无 LLM raw collection、event ordering、分层 snapshot 引用和 artifact 指针落盘；异步 Semantic Distillation 再使用 LLM 生成因果关系、不确定性、失败标签、decision point 和状态提示，并通过后续 State Graph Reconstruction、Failure Knowledge Base、Skill Mining 和 Benchmark Repository，把轨迹转化为可复盘、可重建、可评估和可蒸馏的资产。

该方案不追求完整复刻 agent 内部状态，而是优先构建能服务于人工 review、任务恢复、策略分析和 benchmark 生成的高质量 trajectory。

## 1.3 需求

### 1.3.1 核心目标

- 构建 100 到 500 条高质量任务 trajectory。
- 每条 trajectory 能回答：任务是什么、agent 看到了什么、做了什么、为什么这样做、有哪些不确定性、结果如何、失败或回退发生在哪里。
- 支持后续 State Reconstruction，验证轨迹能否重建真实状态。
- 沉淀 Failure Taxonomy 作为一级资产，而不是只记录成功样本。
- 从高质量轨迹中挖掘可复用 workflow、candidate skill 和 benchmark case。

### 1.3.2 非目标

- 不在早期强行替代 Agent Runtime。
- 不假设 Skill 层可以捕获所有内部 token、hidden state 或 planner 状态。
- 不把一次性成功路径直接提升为正式 skill。
- 不用低质量聊天记录替代工程轨迹。

## 1.4 总体架构

```text
Agent
  |
  v
Agent / shell / tool hooks
  |
  v
Hook Adapter
  |
  v
Trajectory Collector Service
  |
  +-- Ordering Buffer
  |
  +-- Snapshot Manager
  |
  +-- Artifact Indexer
  |
  v
Raw Event Store
  |
  +--> Snapshot Store
  |
  +--> Artifact Store
  |
  v
Async Distillation Queue
  |
  v
LLM Semantic Distiller
  |
  v
Distilled Experience Store
  |
  v
Decision Point Review
  |
  v
State Graph Reconstruction
  |
  v
Failure Knowledge Base
  |
  v
Skill Mining + Benchmark Repository
```

关键调整：

- Collector 不应设计成 skill。Skill 是 agent 主动调用的能力；collector 是观察者，必须低延迟、被动、不可遗忘，并避免污染 agent 决策空间。
- Hook adapter 只做轻量 enqueue，不承担排序、快照、蒸馏或复杂 I/O；collector service 才负责 raw event 事实采集、ordering、snapshot 引用和 artifact index。
- Collector service 不依赖具体 agent 自觉调用；如果 Codex hook payload、时序或权限无法支撑采集，则需要降级为 wrapper CLI、shell history + artifact scanner 或人工 task boundary marker。
- Raw collection 同步路径禁止调用 LLM，只记录结构化原始事实、snapshot id、artifact 指针和 ordering metadata。
- Raw Event Store 必须 append-only，不被蒸馏结果覆盖；后续 schema 或 distiller 算法升级时，通过 trajectory version 和 distillation run version 比较新旧蒸馏结果差异。
- LLM 只用于异步 Semantic Distillation，输入为 raw event stream、snapshot 和 artifact index，输出为带 evidence chain 的 distilled experience。
- 采集阶段不生成完整 causal_link；raw events 只保留 `event_id`、`parent_event_id`、`observations` 和 `artifacts`，Distilled Causal Link 由 distiller 生成。
- Human review 只审核关键 decision point，尤其关注为什么选择 A 而不是 B。
- State Reconstruction 初期输出 state graph，不直接抽象 FSM；等真实轨迹稳定后再从 state graph 中提炼 FSM 或 policy graph。
- 数据流收敛为五类资产：Raw Event Store、Snapshot Store、Distilled Experience Store、Failure Knowledge Base、Benchmark Repository。

## 1.5 Schema 建议

### 1.5.1 Raw trajectory schema

```yaml
trajectory_id:
trajectory_schema_version:
collector_version:
collector_instance_id:
source:
  agent_surface:
  hook_profile:
  workspace:
ordering:
  ordering_strategy:
  monotonic_sequence:
  wall_clock:
  ingest_clock:
  parent_event_index:
task:
  user_request:
  constraints:
  success_criteria:
events:
  - event_id:
    parent_event_id:
    sequence_no:
    timestamp:
    ingest_timestamp:
    actor:
    event_type:
    tool_name:
    observation:
    input_ref:
    output_ref:
    artifact_refs:
    snapshot_refs:
    ordering_barrier:
    raw_error:
outcome:
  status:
  artifact_refs:
  unresolved_items:
```

Raw trajectory 只保存事实层，不保存完整因果叙事。`trajectory_schema_version` 和 `collector_version` 必须保留，用于未来比较“同一批 raw events 经过新 distiller 算法重新蒸馏后”的差异。

### 1.5.2 Event ordering guarantee

多个 hook、tool result、artifact scanner 和 snapshot writer 可能异步到达，因此 collector service 必须显式记录 ordering guarantee：

- 每个 collector instance 生成单调递增 `sequence_no`。
- 每个 event 同时记录 wall-clock timestamp 和 ingest timestamp。
- `parent_event_id` 表达已知因果或嵌套关系，不能表达未知关系。
- 对 tool pre/post 这类成对事件，必须保留 correlation key；若 hook payload 无法提供稳定 correlation key，则该能力记为 Phase 0 blocker。
- 对并发事件，只能声明 partial order；不能为了线性日志强行捏造因果顺序。
- distiller 只能基于 raw ordering metadata 生成候选因果链，不能把 ingestion 顺序直接当成因果链。

### 1.5.3 Distilled experience schema

```yaml
distillation_run_id:
distiller_version:
source_trajectory_id:
source_trajectory_schema_version:
source_event_range:
distilled_task:
  interpreted_intent:
  constraints:
  success_criteria:
distilled_claims:
  - claim_id:
    claim_type:
    text:
    confidence:
    evidence_chain:
      raw_events:
      snapshots:
      artifacts:
    reviewer_status:
distilled_causal_links:
  - link_id:
    from_event_id:
    to_event_id:
    rationale:
    confidence:
    evidence_chain:
    reviewer_status:
decision_points:
  - decision_id:
    event_id:
    decision_question:
    chosen_option:
    alternatives_considered:
    rejection_reasons:
    evidence_chain:
    uncertainty:
    expected_outcome:
    actual_outcome:
    reviewer_status:
```

`distilled_claims`、`distilled_causal_links` 和 `decision_points` 只存在于语义蒸馏层，不写回 raw event stream。每个 claim 或 decision point 都必须能追溯到 raw event、snapshot 或 artifact，否则只能标记为低置信度假设，不能作为 state reconstruction 的事实依据。

### 1.5.4 事件类型

早期事件类型应保持少而稳定：

| event_type | 含义 |
|---|---|
| observe | 读取文件、搜索、查看环境、理解输入 |
| act | 修改文件、运行命令、调用工具、生成 artifact |
| verify | 测试、lint、review、截图、人工检查 |
| fail | 命令失败、假设失败、验证不通过、路径回退 |
| handoff | 交接给 reviewer、subagent、人工或后续阶段 |

Raw event 不再强制包含 `reason` 或 `decide`。这些语义应由 distiller 从 raw event、snapshot 和 artifact 中提取为 decision point，避免采集阶段把后验解释写入事实层。

### 1.5.5 uncertainty

`uncertainty` 用于保留 agent 当时的不确定性，避免后验叙事把假设写成事实。

建议字段：

```yaml
uncertainty:
  level: low | medium | high
  unknowns:
    - "是否存在已有重复候选"
  assumptions:
    - "当前 decision point 尚未经过人工审核，因此只能作为 distilled hypothesis"
  evidence_gap:
    - "没有外部 benchmark 或本地运行数据验证"
  mitigation:
    - "标记 reviewer_status: unreviewed，并保留 evidence gap"
```

## 1.6 Snapshot 前置设计

Snapshot 用于保证 trajectory 可重建，但不应每个 event 都做全量 snapshot。采集链路应通过 hook 获得 snapshot id、artifact id 和命令/工具输出摘要，不在同步路径中调用 LLM。

Snapshot 分三层：

| 层级 | 触发 | 内容 | 用途 |
|---|---|---|---|
| session baseline snapshot | trajectory 开始、resume 或环境变化 | workspace、repo、branch、commit、权限、环境、关键配置 | 给整条轨迹提供基础状态 |
| incremental snapshot | 文件修改、命令执行、artifact 生成后 | 文件 hash、diff、artifact refs、命令摘要、错误摘要 | 控制成本，支撑局部重建 |
| decision checkpoint snapshot | 关键 decision point 前后 | 与决策相关的上下文、候选路径、证据、状态差异 | 支撑人工 review 和 skill mining |

最小 snapshot 字段：

- workspace 路径、repo、branch、commit、dirty state。
- 权限边界和可访问路径。
- snapshot layer 和 parent snapshot id。
- 任务相关文件列表、hash 或 diff 引用。
- 关键 artifact 指针，例如 diff、patch、报告、测试输出。
- 关键命令及输出摘要。
- 失败命令、错误信息和回退路径。

Snapshot 不需要完整复制所有上下文，但必须能支撑后续 reviewer 判断 state 是否真实。全量 snapshot 只应出现在 baseline 或人工指定 checkpoint，不应成为每个事件的默认成本。

## 1.7 Phase 规划

### 1.7.1 Phase 0：Codex Hook Feasibility Spike

目标：先验证 Codex hook 是否能支撑 trajectory collector service，而不是假设 hook 一定足够。

验收问题：

- Hook 是否能覆盖 user prompt、tool pre/post、permission request、stop 等任务关键边界。
- Hook payload 是否包含足够的 tool name、input、output、session/thread、cwd、approval 和 error 信息。
- Tool pre/post 是否有稳定 correlation key；没有则无法可靠合并成一个工具事件。
- 多个 hook 并发触发时，collector 是否能建立 partial order 和 sequence number。
- Hook command 同步开销是否可控，能否只做轻量 enqueue。
- sandbox、权限和网络限制下，hook adapter 是否能可靠写入本地 queue 或连接本地 collector service。

Phase 0 不通过时，降级路线包括 wrapper CLI、shell history + artifact scanner、人工 task boundary marker，或等待 Runtime 级 observability。

### 1.7.2 Phase 1：Execution Event Sourcing MVP

目标：获得 50 条高质量 trajectory 和 200 条普通 trajectory，而不是只追求数量。

范围：

- Hook adapter。
- Trajectory Collector Service。
- Ordering Buffer。
- 分层 Snapshot Manager。
- Artifact Indexer。
- Append-only Raw Event Store。
- Raw trajectory schema v1。
- Raw trace segmentation 与 per-trajectory raw bundle。
- 人工标注模板。
- 基础质量评分 rubric。

P1 必须把当前 P0 的集中 raw event stream 演进为按 trajectory/session/task 分段的 Raw Event Store。当前集中写入 `trajectories/raw_events.jsonl` 只适合 P0 验证 hook payload、ordering、correlation 和 report 链路；长期 trajectory 库应避免多个 Codex 会话、多个任务或不同 workspace 静默混在同一条 raw event stream 中。开发阶段已决定不兼容 P0 集中 `trajectories/raw_events.jsonl` 和 `phase0_feasibility_report.json` 输出，P1 从 per-trajectory raw bundle 作为唯一 raw event store 开始。

推荐 P1 物理布局：

```text
trajectories/
  raw/
    <trajectory_id>/
      trajectory_meta.json
      raw_events.jsonl
      artifact_index.json
      snapshot_refs.json
  collection_report.json
```

其中 `storage/queue/hook_events.jsonl` 是 hook 原始 envelope 队列；`trajectories/raw/<trajectory_id>/raw_events.jsonl` 是 distiller、reviewer 和 state reconstruction 的默认 raw 输入；`trajectories/collection_report.json` 聚合所有 per-trajectory bundle。当前 P1 实现不生成全局 raw audit stream；若后续需要全局审计流，必须作为新设计显式加入，不得把它作为 distiller 主输入。

`trajectory_id` 创建和轮转规则必须显式实现。建议新建 trajectory 的触发条件包括：新 `session_id` 第一次出现，hook payload 中 `session_id` 或 `thread_id` 变化，workspace/cwd 跨 allowlist root 或跨项目变化，收到 `UserPromptSubmit` 且上一条 trajectory 已收到 `Stop`，空闲超过阈值，或人工 marker/capture policy 明确要求 start new trajectory。建议结束或冻结 trajectory 的触发条件包括：收到 `Stop` 且当前 trajectory 至少包含一个 user prompt 或 tool event，空闲超过阈值并已有可复盘事件，capture policy 判断为低质量且可归档或 TTL 清理，或人工 marker 明确 close trajectory。`Stop` 不应无条件删除或丢弃 trajectory；若后续同 session 又出现新 `UserPromptSubmit`，应创建新 trajectory 或明确记录 continuation/reopen 原因。

`trajectory_meta.json` 建议至少记录 `trajectory_id`、schema/version、created/closed time、open/closed/archived 状态、start/close reason、session/thread/workspace、user prompt event、stop event、idle timeout、quality tier、domain tags、capture/drop reason、first/last sequence、artifact index、snapshot refs 和 unresolved items。该 metadata 不替代 raw events，只记录分段、质量和恢复入口。

Collector service 应从当前单一 state 演进为 active trajectory manager：维护 `session_id/workspace -> active_trajectory_id` 映射；对每个 queued envelope 先判断所属 trajectory，再 append 到对应 raw bundle；保留 collector instance 单调 `sequence_no`，并增加每条 trajectory 内的局部 `trajectory_sequence_no`；对 tool pre/post 使用 correlation key 归属到同一 trajectory，缺失 correlation 时记录 blocker 或 uncertain correlation；对并发事件只声明 partial order，不用物理文件顺序伪造因果关系。若边界无法确定，应记录 `segmentation_uncertainty`，而不是把多个会话静默合入同一条 raw event stream。

P0 集中 raw event 文件不作为 P1 兼容输入。若需要处理 P0 已有集中 raw events，后续只能生成 migration proposal，不直接静默切分或混入 P1 raw bundle。

验收：

- Raw collection 路径 LLM call count 为 0。
- Collector 不依赖 agent 主动调用 skill。
- Hook p95 overhead 和 raw event 丢失率有记录。
- Tool pre/post 事件可关联；不可关联的比例有记录。
- 不同 session/workspace 或 `Stop` 后新任务默认进入不同 trajectory raw bundle。
- 每条进入 distiller 的 trajectory 都有 `trajectory_meta.json`、raw event 文件、artifact refs 和 snapshot refs。
- 不再生成全局 `trajectories/raw_events.jsonl`；collector report 聚合 `trajectories/raw/*/raw_events.jsonl` 并写入 `trajectories/collection_report.json`。
- 80% 轨迹能回答“做了什么、为什么做、结果如何”。
- 至少 50 条轨迹能被第三方 reviewer 复盘。
- 每条高质量轨迹有 artifact 或 evidence 指针。
- 每条高质量轨迹有关键 decision point 候选或明确说明没有决策价值。

### 1.7.3 异步 Semantic Distillation

目标：在不污染主任务上下文、不放大同步延迟的前提下，把 raw trajectory 转换为可 review、可重建、可挖掘的 distilled trajectory。

约束：

- LLM 只在异步 distiller 中使用，不进入 hook 和 raw collection 同步路径。
- distiller 输入为 per-trajectory raw bundle、snapshot 和 artifact index；若未来新增全局 ingest/raw audit stream，它只能用于排错、重放或重新生成 segmentation proposal。
- distiller 输出的 interpreted intent、Distilled Causal Link、decision point、uncertainty、failure_tags 和 state hints 必须保存 evidence chain。
- distilled trajectory 是派生产物，不得覆盖 append-only raw event stream。
- 每次 distillation run 必须保存 distiller version 和 source trajectory version，支持新旧算法重跑结果比较。
- Human review 只审核关键 decision point 和高影响 causal link，不审核所有事件。

实现形态：

- 异步 Semantic Distillation 应作为 repo-local skill 落地在 `/home/jichao/agent-trajectory/skills/semantic-distillation/SKILL.md`，并通过软链接暴露到用户级 `~/.codex/skills/semantic-distillation`。这样 skill 的版本、脚本和 trajectory schema 能随 agent-trajectory 仓库演进，同时 Codex runtime 仍能按普通 skill 发现和调用。
- Skill 文本和工作输出使用中文，避免把 distillation 产物写成英文运行说明；但 schema 字段名保持稳定英文，便于后续自动化消费。
- Skill 不替代 collector，也不被 hook、scheduler 或 daemon 自动同步调用；它只在用户或后续异步调度明确指定 `trajectory_id` 时运行。
- Distiller 的确定性准备步骤由仓库脚本承担，例如 `distiller/scripts/prepare_distillation.py` 只读取指定 `trajectories/raw/<trajectory_id>/` bundle，生成 `trajectories/distilled/<trajectory_id>/<distillation_run_id>/run_meta.json`、`evidence_index.json`、`distilled_experience.json` 和 `distilled_experience.md` 脚手架。
- LLM 或人工语义判断只补全 `distilled_experience.*` 中的任务意图、关键事实、decision point、failure tags、uncertainty、causal links 和可复用经验；每条语义结论必须引用 raw event、artifact、snapshot 或事件范围。
- 默认不扫描全部 raw bundle；若要批量蒸馏，应先由外部 daemon/scheduler 选择候选 trajectory，再逐条调用 skill 或确定性脚本，避免把低质量轨迹无差别蒸馏成知识候选。
- `reviewer_status` 默认保持 `unreviewed`；没有人工或授权 reviewer 复核时，不得把 distillation 结果提升为 verified fact、正式 skill 或正式知识。

### 1.7.4 Phase 2：State Graph Reconstruction

目标：人工 review 100 条 trajectory，验证 reconstructed state graph 是否可靠。早期不直接输出 FSM，因为状态集合和转移边界尚未稳定。

新增组件：

- State Graph Reconstruction Skill。
- State Extractor。
- State graph schema。
- Reconstruction report。
- 缺失事件类型统计。

评估指标：

| 指标 | 问题 |
|---|---|
| State Fidelity | 重建状态是否对应当时真实环境、文件、约束和任务进展？ |
| Decision Recoverability | reviewer 只看轨迹，能否理解 agent 为什么做这个动作？ |
| Continuation Usefulness | 新 agent 接手 reconstructed state 后，能否继续完成任务？ |
| Counterfactual Stability | 如果换一个合理路径，当前 state 是否仍然成立？ |

评分建议：

| 分数 | 含义 |
|---|---|
| 0 | 不可用，状态缺失或错误 |
| 1 | 可粗略理解，但无法继续执行 |
| 2 | 可继续执行，但需要额外人工判断 |
| 3 | 可无缝恢复，关键证据和下一步清晰 |

验收：

- 60% 以上轨迹达到 `score >= 2`。
- 20% 以上轨迹达到 `score = 3`。
- 形成导致不可恢复的 top failure modes。
- Counterfactual Stability 能暴露“只在单一路径成立”的脆弱状态。
- state graph 中的节点和边必须能回溯到 raw event、snapshot 或 distilled claim。

### 1.7.5 Phase 3：Pattern Mining、Skill Mining 和 Benchmark Generation

目标：从高质量 trajectory 中挖掘可复用流程，生成 candidate skill 和 benchmark。

推荐链路：

```text
Trajectory
  -> Decision Point
  -> Repeated Pattern
  -> Candidate Heuristic
  -> Validated Procedure
  -> Candidate Skill
  -> Benchmark Case
```

Skill Mining 不应直接从单条轨迹生成正式 skill。每个 candidate skill 至少需要：

- 来自 3 条以上相似成功轨迹，或明确标注为单例假设。
- 触发条件。
- 必读上下文。
- 禁止动作。
- 成功标准。
- 失败降级策略。
- 反例轨迹或失败边界。

Benchmark 结构：

```yaml
task:
  user_request:
  hidden_context:
  constraints:
state:
  initial_files:
  environment:
  prior_events:
  permissions:
action:
  expected_strategy:
  allowed_tools:
  forbidden_shortcuts:
evaluation:
  success_criteria:
  behavioral_checks:
  artifact_checks:
  regression_checks:
```

验收：

- 每个 candidate skill 有明确适用范围和不适用范围。
- 每个 benchmark 有可执行或可人工复核的 evaluation。
- mined skill 在 holdout tasks 上优于无 skill baseline。

## 1.8 五类资产模型

Trajectory 系统的产物收敛为五类资产，避免把原始事实、语义理解、边界知识和应用 benchmark 混在同一层：

| 资产 | 层级 | 说明 |
|---|---|---|
| Raw Event Store | 事实层 | append-only raw events、ordering metadata、tool input/output refs、artifact refs |
| Snapshot Store | 状态层 | baseline、incremental 和 decision checkpoint snapshot |
| Distilled Experience Store | 理解层 | interpreted intent、Distilled Causal Link、decision point、state hints、claim-level evidence chain |
| Failure Knowledge Base | 边界层 | failure taxonomy、negative cases、反例、不可恢复原因和误判模式 |
| Benchmark Repository | 应用层 | 可执行或可人工复核的 benchmark case、evaluation 和 holdout tasks |

层级约束：

- Raw Event Store 和 Snapshot Store 是事实源。
- Distilled Experience Store 是派生产物，不能覆盖 raw facts。
- Failure Knowledge Base 必须能追溯到失败轨迹或 review 证据。
- Benchmark Repository 必须有 evaluation，否则只是样例库。

## 1.9 Failure Taxonomy 作为一级资产

Failure Taxonomy 不应只是 Phase 2 的副产物，而应贯穿采集、重建、挖掘和评估。

建议初始分类：

| 类别 | 说明 |
|---|---|
| context_missing | 缺少关键文件、入口、环境或权限信息 |
| snapshot_insufficient | snapshot 不足以验证当时状态 |
| causal_gap | 事件之间缺少因果解释 |
| uncertainty_hidden | 假设、不确定性或证据缺口被后验叙事掩盖 |
| action_unverifiable | 动作结果没有 artifact、日志、diff 或测试证据 |
| decision_unrecoverable | reviewer 无法理解为什么选择该路径 |
| state_brittle | 状态只在单一路径成立，counterfactual 下不稳定 |
| evaluation_weak | outcome 没有可判分标准 |
| over_mined_skill | 从少量或偶然轨迹中提炼出过强 skill |
| success_bias | 只收成功样本，缺少失败、回退和误判样本 |

Failure Taxonomy 的用途：

- 反向修正 trajectory schema。
- 指导 Snapshot 增加必要字段。
- 生成 benchmark 的 negative cases。
- 作为 skill mining 的禁止条件和风险标签。

## 1.10 质量门禁

一条高质量 trajectory 至少应满足：

- 有明确 task intent 和 success criteria。
- 有最小可验证分层 snapshot。
- event sequence 能区分 observe、act、verify、fail、handoff。
- raw event 有 event_id、parent_event_id 或明确无父事件、ordering metadata、artifact refs。
- 关键 decision point 记录 chosen option、alternatives considered、rejection reasons 和 evidence chain。
- 关键因果关系由 distiller 生成 Distilled Causal Link，并保留置信度和证据链。
- 关键假设有 uncertainty。
- distilled claim 有 claim-level evidence chain。
- outcome 有验证证据或明确 unresolved_items。
- failure tags 不因最终成功而被删除。

候选 skill 的门禁：

- 不直接从单条成功 trajectory 提升。
- 必须包含适用范围、触发条件、反例或风险。
- 必须能映射到 benchmark evaluation。
- 未经过 holdout 验证前只保留为 candidate skill。

## 1.11 风险与边界

- 非 Runtime 级观测看不到完整内部状态，因此 reconstructed state 只能声称“基于外部事件和 artifact 的可恢复状态”，不能声称等价于真实 hidden state。
- Collector 不应作为 skill 落地；否则会依赖 agent 自觉调用，并把采集动作污染进决策空间。
- Hook adapter 是否足以支撑 collector service 尚未验证；必须先完成 Phase 0 feasibility spike。
- Hook command 若只能同步执行且并发启动，必须保持轻量 enqueue，避免把 collector I/O 和排序成本放进 hook path。
- 多个异步事件只能保证 partial order；不能把 ingestion 顺序伪装成因果顺序。
- Raw collection 同步路径不得调用 LLM；否则会污染任务上下文、增加不可控延迟，并把后验解释混入原始事实。
- Semantic Distillation 可能产生后验叙事，因此 distilled trajectory 必须保留 evidence chain，且不能替代 raw event stream。
- 采集阶段生成完整 causal_link 成本过高，应只在 distillation 阶段生成 Distilled Causal Link。
- Snapshot 如果过重，会干扰任务执行；如果过轻，会导致状态不可验证，因此必须分层。
- 过早抽象 FSM 容易固化不稳定状态边界；早期应使用 state graph。
- 过早 Skill Mining 容易把偶然路径固化为错误规范。
- Benchmark 如果没有 evaluation，只是样例集，不能用于优化 agent。
- Failure Taxonomy 需要定期合并同义项，否则会碎片化。

## 1.12 Promotion Blockers

该候选目前不得直接提升到正式知识区，阻塞项包括：

- 尚未有真实 trajectory 采集数据验证。
- Codex hook feasibility spike 尚未完成。
- collector service、event ordering guarantee、schema version 和分层 snapshot 尚未实现验证。
- State Reconstruction 指标尚未在 100 条轨迹上人工 review。
- Counterfactual Stability 指标尚未形成稳定 rubric。
- Failure Taxonomy 尚未经过真实失败样本校准。
- Skill Mining 和 Benchmark Generation 尚未在 holdout tasks 上验证收益。
