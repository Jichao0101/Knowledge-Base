---
type: project_record
status: draft
project: agent-trajectory
module: trajectory-system-design
summary: "在开发初期没有 Agent Runtime 控制权时，用 Skill 层实现 Agent Execution Event Sourcing、Snapshot、状态重建、Failure Taxonomy、Skill Mining 和 Benchmark Generation 的阶段性方案。"
sources:
  - "2026-07-07 当前对话：工业 agent 任务轨迹库、Trace Capture、State Reconstruction、Skill Mining 与 Benchmark Generation 方案讨论"
scope: "agent-trajectory 项目的初始架构设计；覆盖工业 agent 任务轨迹库、轻量 observability、轨迹蒸馏、状态重建、skill mining 和 benchmark generation。"
risks:
  - "当前方案尚未经过真实 trajectory 采集、人工 reconstruction review 或 holdout benchmark 验证。"
  - "Skill 层只能采集外部可观察事件，不能声称等价于 Agent Runtime hidden state。"
updated_at: 2026-07-07
---

# 1 Agent 执行事件溯源与轨迹蒸馏系统初始设计

## 1.1 迁移记录

本方案作为 agent-trajectory 项目的初始设计记录。项目当前入口为 [[02_Projects/agent-trajectory/agent_trajectory_overview_current]]。后续实现、验证和阶段记录应优先写入该项目；正式知识提升仍需真实轨迹、人工 review 和 holdout 验证。

## 1.2 背景

工业 agent 的早期建设需要高质量任务轨迹库。理想方案是通过 Wrapper Agent 或 Agent Runtime 统一采集任务执行过程，但开发初期往往没有 Runtime 控制权，也无法稳定截获内部 planner、tool call、memory、state transition 和 evaluation 信号。

因此，阶段性方案是把 Trace Capture 的定位从普通日志采集提升为 **Agent Execution Event Sourcing Layer**：用 Skill 层记录 agent 执行过程中的关键事件、快照、因果关系和不确定性，再通过后续 State Reconstruction、Failure Taxonomy、Skill Mining 和 Benchmark Generation，把轨迹转化为可复盘、可重建、可评估和可蒸馏的资产。

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
Agent Execution Event Sourcing Layer
  |
  +-- Snapshot Skill
  |
  +-- Trace Collector Skill
  |
  +-- Artifact Indexer
  |
  v
Raw Trajectory Store
  |
  v
State Extractor
  |
  v
State Reconstruction Skill
  |
  v
Failure Taxonomy
  |
  v
FSM / Policy Graph
  |
  v
Skill Mining + Benchmark Generation
```

关键调整：

- Snapshot Skill 应前置，作为事件溯源层的基础设施，而不是只在后处理阶段补充。
- Trace Capture 定位为 Agent Execution Event Sourcing Layer，强调事件序列、因果链和状态演化。
- Failure Taxonomy 是一级资产，和 FSM / Policy Graph、Skill Mining 并列维护。
- Skill Mining 前应先做 Pattern Mining，避免把单次偶然路径固化为 skill。

## 1.5 Trajectory Schema 建议

### 1.5.1 顶层结构

```yaml
trajectory_id:
task:
  user_request:
  interpreted_intent:
  constraints:
  success_criteria:
context:
  workspace:
  environment:
  permissions:
  relevant_files:
  prior_artifacts:
events:
  - event_id:
    timestamp:
    actor:
    event_type:
    state_before:
    observation:
    action:
    output:
    evidence:
    uncertainty:
    causal_link:
    state_after:
    failure_tags:
outcome:
  status:
  artifacts:
  verification:
  unresolved_items:
review:
  reviewer:
  state_fidelity:
  decision_recoverability:
  continuation_usefulness:
  counterfactual_stability:
  notes:
```

### 1.5.2 事件类型

早期事件类型应保持少而稳定：

| event_type | 含义 |
|---|---|
| observe | 读取文件、搜索、查看环境、理解输入 |
| reason | 显式推理、计划、权衡、假设形成 |
| decide | 做出路径选择或排除某个路径 |
| act | 修改文件、运行命令、调用工具、生成 artifact |
| verify | 测试、lint、review、截图、人工检查 |
| fail | 命令失败、假设失败、验证不通过、路径回退 |
| handoff | 交接给 reviewer、subagent、人工或后续阶段 |

### 1.5.3 causal_link

`causal_link` 用于记录为什么当前 event 会导致下一个 event，避免轨迹退化为时间顺序日志。

建议字段：

```yaml
causal_link:
  caused_next_event: true
  rationale: "上一事件暴露了缺失的状态快照，因此下一步先补充 workspace snapshot。"
  dependency:
    - "event_id:evt_003"
    - "artifact:git_diff_before_patch"
  alternative_considered:
    - "直接进入 state reconstruction"
  why_alternative_rejected:
    - "缺少快照会导致 reconstruction 无法验证真实状态"
```

记录重点不是写长篇解释，而是保留“当前动作为什么合理地引出下一步”的最小因果证据。

### 1.5.4 uncertainty

`uncertainty` 用于保留 agent 当时的不确定性，避免后验叙事把假设写成事实。

建议字段：

```yaml
uncertainty:
  level: low | medium | high
  unknowns:
    - "是否存在已有重复候选"
  assumptions:
    - "当前内容尚未经过人工审核，因此应进入 03_Inbox"
  evidence_gap:
    - "没有外部 benchmark 或本地运行数据验证"
  mitigation:
    - "先写为 pending_review candidate，并保留 promotion blockers"
```

## 1.6 Snapshot Skill 前置设计

Snapshot Skill 应在 Trace Collector 之前或同步执行，用于保证 trajectory 可重建。

最小 snapshot 内容：

- workspace 路径、repo、branch、commit、dirty state。
- 权限边界和可访问路径。
- 任务相关文件列表和 hash。
- 关键 artifact 指针，例如 diff、patch、报告、测试输出。
- 关键命令及输出摘要。
- 失败命令、错误信息和回退路径。

Snapshot 不需要完整复制所有上下文，但必须能支撑后续 reviewer 判断 state 是否真实。

## 1.7 Phase 规划

### 1.7.1 Phase 1：Execution Event Sourcing MVP

目标：获得 50 条高质量 trajectory 和 200 条普通 trajectory，而不是只追求数量。

范围：

- Trace Collector Skill。
- 前置的最小 Snapshot Skill。
- Raw Trajectory Store。
- trajectory schema。
- 人工标注模板。
- 基础质量评分 rubric。

验收：

- 80% 轨迹能回答“做了什么、为什么做、结果如何”。
- 至少 50 条轨迹能被第三方 reviewer 复盘。
- 每条高质量轨迹有 artifact 或 evidence 指针。
- 每条高质量轨迹包含 `causal_link` 和 `uncertainty`。

### 1.7.2 Phase 2：State Reconstruction

目标：人工 review 100 条 trajectory，验证 reconstructed state 是否可靠。

新增组件：

- State Reconstruction Skill。
- State Extractor。
- State schema。
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

### 1.7.3 Phase 3：Pattern Mining、Skill Mining 和 Benchmark Generation

目标：从高质量 trajectory 中挖掘可复用流程，生成 candidate skill 和 benchmark。

推荐链路：

```text
Trajectory
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

## 1.8 Failure Taxonomy 作为一级资产

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
- 指导 Snapshot Skill 增加必要字段。
- 生成 benchmark 的 negative cases。
- 作为 skill mining 的禁止条件和风险标签。

## 1.9 质量门禁

一条高质量 trajectory 至少应满足：

- 有明确 task intent 和 success criteria。
- 有最小可验证 snapshot。
- event sequence 能区分 observe、reason、decide、act、verify、fail。
- 关键 event 有 causal_link。
- 关键假设有 uncertainty。
- outcome 有验证证据或明确 unresolved_items。
- failure tags 不因最终成功而被删除。

候选 skill 的门禁：

- 不直接从单条成功 trajectory 提升。
- 必须包含适用范围、触发条件、反例或风险。
- 必须能映射到 benchmark evaluation。
- 未经过 holdout 验证前只保留为 candidate skill。

## 1.10 风险与边界

- Skill 层观测不到完整 Runtime 内部状态，因此 reconstructed state 只能声称“基于外部事件和 artifact 的可恢复状态”，不能声称等价于真实 hidden state。
- `causal_link` 和 `uncertainty` 会增加记录成本，需要控制字段粒度，避免压垮采集流程。
- Snapshot 如果过重，会干扰任务执行；如果过轻，会导致状态不可验证。
- 过早 Skill Mining 容易把偶然路径固化为错误规范。
- Benchmark 如果没有 evaluation，只是样例集，不能用于优化 agent。
- Failure Taxonomy 需要定期合并同义项，否则会碎片化。

## 1.11 Promotion Blockers

该候选目前不得直接提升到正式知识区，阻塞项包括：

- 尚未有真实 trajectory 采集数据验证。
- State Reconstruction 指标尚未在 100 条轨迹上人工 review。
- Counterfactual Stability 指标尚未形成稳定 rubric。
- Failure Taxonomy 尚未经过真实失败样本校准。
- Skill Mining 和 Benchmark Generation 尚未在 holdout tasks 上验证收益。
