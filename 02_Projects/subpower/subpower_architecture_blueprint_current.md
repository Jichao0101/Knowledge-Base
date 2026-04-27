---
type: project
status: current
domain: 工程工作流
topic: subpower 架构蓝图
project: subpower
created_at: 2026-04-27
updated_at: 2026-04-27
source_repos:
  - /mnt/d/subpower
  - /mnt/d/cutepower
  - /mnt/d/knowledgeBase/plugins/agent-workflow-migrator
scope: 独立的 subagent-first 三侧工作流编排 runtime 设计蓝图。
risks:
  - 将 subpower 过早膨胀为固定端到端 workflow engine
  - 将 subpower 主状态耦合到 cutepower run artifacts
  - runtime gate 承担业务语义判断
  - reviewer 独立性只停留在文档约束而缺少 invocation 与 artifact 检查
---

# 1 subpower 架构蓝图 current

## 1.1 摘要

`subpower` 是一个独立的 subagent-first 三侧工作流编排 runtime。它不是 `cutepower` 的替代品。

```text
cutepower = skill-first governance plugin
subpower = subagent-first orchestration runtime
```

`cutepower` 负责约束主代理是否遵守合法技能流程、contracts、runtime admission gate、review/writeback/board evidence 等治理边界。

`subpower` 负责约束哪个子代理在什么状态下可以接手任务，知识库 / 代码库 / 板端三侧状态如何同步，子代理之间如何交接 artifact，板端失败如何进入独立评估，主代理如何基于评估动态选择返工路径。

核心模型是：

```text
workflow patterns + decision points + runtime gates + run artifacts
```

workflow 是可复用执行模式，不是固定写死的端到端脚本。

## 1.2 与 cutepower 的边界

`cutepower` 已经解决：

- `contracts/` 作为治理真源；
- `skills/` 作为 skill-first 流程纪律层；
- `AGENTS.md` 与 `agents/*.toml` 作为薄 runtime bridge；
- `scripts/runtime-gates.js` 作为 action-front admission check；
- `.cutepower/run/<session_id>/` 作为 repo-local run-state；
- procedural review、writeback、board evidence gate。

`cutepower` 不应膨胀为完整 subagent orchestration system。原因是它当前的抽象核心是 skill chain admission，而不是 agent identity、handoff packet、side-state、board failure assessment 和动态返工路由。

`subpower` 独立负责：

- 子代理 role boundary；
- invocation identity 与 reviewer independence 检查；
- knowledge / repo / board side-state transition；
- 子代理间 handoff packet；
- board failure assessment；
- main route decision；
- closure matrix 与 writeback precondition。

兼容结论：

- `.subpower/run/<session_id>/` 是 subpower authoritative state。
- `.cutepower/run/<session_id>/` 只能通过 optional adapter 只读导入。
- 导入后的 cutepower 上游上下文写入 `upstream_cutepower_context.json`，不得作为 live runtime state 反复读取。
- `task_profile`、`evidence_manifest`、`review_decision` 可以共享 schema 概念。
- `agent_invocation_manifest`、`side_state`、`handoff_packet`、`board_failure_review`、`main_route_decision`、`closure_matrix` 必须由 subpower 独立定义。

## 1.3 硬约束

- 主代理是 workflow composer / routing decision owner。
- 主代理不得伪造 reviewer 结论。
- coder 不得自审通过。
- reviewer 不得直接修改代码。
- board-runner 没有 `board_target.json` 不得执行。
- board-runner 不得自行关闭任务。
- board validation failed 后，必须先产生 `board_failure_review.json`，再由主代理产生 `main_route_decision.json`。
- runtime gate 只判断结构合法性：role、phase、artifact、schema、independence、board target、evidence、route、closure、writeback。
- runtime gate 不判断业务语义、根因正确性、实现质量优劣或验收标准是否合理。

## 1.4 仓库架构

推荐仓库结构：

```text
subpower/
├── .codex-plugin/
│   └── plugin.json
├── README.md
├── README.codex.md
├── AGENTS.md
├── agents/
├── contracts/
├── schemas/
│   └── run-artifacts/
├── scripts/
├── skills/
└── docs/
```

目录职责：

- `.codex-plugin/`：插件分发元数据，用于未来作为 Codex plugin 安装。
- `agents/`：可实例化子代理骨架，只引用 contracts，不作为 policy truth。
- `contracts/`：active truth source，定义角色、workflow pattern、decision point、gate、artifact requirement、side-state、route policy、closure policy。
- `schemas/`：run artifact 与 contract 的 schema。
- `scripts/`：runtime gate、artifact IO、contract validation、optional cutepower adapter、负向测试。
- `skills/`：主代理入口与使用纪律，不复制 contracts 规则文本。
- `.subpower/run/<session_id>/`：subpower repo-local runtime state，必须被 ignore，不进入插件包的版本历史。

## 1.5 MVP agent set

MVP agent：

- `workflow-orchestrator`：主代理职责模式，负责 workflow 组合、route decision、side-state、closure check。
- `knowledge-planner`：任务定性、scope planning、implementation plan、verification plan、board target planning。
- `repo-implementer`：授权范围内的代码修改与本地验证。
- `repo-reviewer`：独立审查代码、验证证据、board failure assessment。
- `board-runner`：board target 绑定、执行、artifact 采集、validation result 输出。

延后 agent：

- `failure-analyst`：复杂根因分析或多轮返工不收敛。
- `verification-manager`：复杂验证矩阵。
- `knowledge-auditor`：候选知识转正审查。
- `knowledge-closer`：完整知识写回执行。
- `source-ingestor`：外部来源采集。

## 1.6 MVP workflow patterns

### 1.6.1 incident_investigation

用于从现象、日志、trace、指标、dump、错误码等板端或运行证据进入调查。输出 evidence、假设和 `next_workflow_recommendation`，再由主代理路由到 `bug_fix`、`board_validation`、`functional_review`、`knowledge_writeback` 或 escalation。

### 1.6.2 bug_fix

planner 确认范围，implementer 修改并本地验证，reviewer 独立审查。若任务要求板端证据，则主代理进入 `board_validation`。

### 1.6.3 board_validation

board-runner 基于 `board_target.json` 执行并输出 `board_validation_result.json`。如果结果为 failed，repo-reviewer 必须输出 `board_failure_review.json`，主代理再输出 `main_route_decision.json`。

### 1.6.4 functional_review

只读功能符合度审核。MVP 中只保留 contract-level route target，不做完整实现。

### 1.6.5 knowledge_writeback

闭环写回模式。MVP 只验证 closure/writeback gate，不自动完成正式知识库写回。

## 1.7 Decision points

必须支持：

- `board_validation_failed`
- `code_review_failed`
- `evidence_insufficient`
- `scope_mismatch`
- `environment_unstable`
- `requirement_ambiguous`
- `closure_blocked`

`board_validation_failed` 的最小结构：

```yaml
required_assessor: repo-reviewer
required_artifacts:
  - board_validation_result
  - evidence_manifest
  - board_failure_review
decision_owner: workflow-orchestrator
allowed_routes:
  - coder_rework
  - planner_rework
  - collect_more_evidence
  - rerun_board_validation
  - escalate_to_user
  - close_as_environment_issue
```

## 1.8 Runtime gates

MVP gates：

- `role_gate`
- `phase_gate`
- `artifact_gate`
- `schema_gate`
- `independence_gate`
- `board_target_gate`
- `evidence_gate`
- `route_gate`
- `closure_gate`
- `writeback_gate`

gate 的职责是阻断结构非法动作，例如：

- coder 自己生成 `review_decision.json` 并 close；
- reviewer 直接修改代码；
- board-runner 没有 `board_target.json` 就执行；
- board validation failed 后没有 `board_failure_review.json` 就进入 coder rework；
- `main_route_decision` 指向非法 route；
- 没有 evidence 就 close；
- 没有 closure matrix 就 writeback。

## 1.9 MVP run artifacts

MVP 必需：

- `task_profile.json`
- `workflow_plan.json`
- `agent_invocation_manifest.json`
- `side_state.json`
- `handoff_packet.json`
- `implementation_plan.json`
- `code_change_manifest.json`
- `review_decision.json`
- `board_target.json`（需要板端时）
- `board_validation_result.json`（执行板端时）
- `board_failure_review.json`（板端失败时）
- `main_route_decision.json`（decision point route 时）
- `evidence_manifest.json`
- `closure_matrix.json`

延后：

- `incident_report.json`
- `root_cause_hypotheses.json`
- `next_workflow_recommendation.json`
- `writeback_receipt.json`
- `writeback_declined.json`
- `upstream_cutepower_context.json`

## 1.10 三侧状态模型

```yaml
sides:
  knowledge:
    state: context_pending | context_ready | writeback_pending | writeback_done | synced | blocked
  repo:
    state: untouched | planned | changed | locally_verified | reviewed | rework_required | merged_ready | blocked
  board:
    state: not_required | target_pending | target_bound | executed | evidence_collected | failed | passed | blocked
```

允许 close 的基本条件：

- evidence 存在；
- review 存在且满足 closure 要求；
- side-state 不冲突；
- closure matrix 无 blocker；
- board-required 任务必须 board passed，或存在 reviewed terminal route，例如 `close_as_environment_issue`。

## 1.11 插件化要求

subpower 仓库既是本地开发源，也是未来插件分发源。实现上必须区分：

- development source：当前 Git 仓库；
- staged plugin source：复制到用户或 repo plugin 目录的可发现插件；
- installed runtime：用户在 `/plugins` 中安装后的 runtime。

因此：

- `.codex-plugin/plugin.json` 必须进入版本库；
- `skills/`、`agents/`、`contracts/`、`schemas/`、`scripts/`、`docs/` 必须可随插件一起分发；
- `.subpower/run/`、临时日志、coverage、依赖目录不得进入版本库；
- 不应在版本库 `.gitignore` 中全局忽略 `.codex/`，避免未来需要发布 `.codex/INSTALL.md` 或其他安装文档时被误忽略。

## 1.12 第一阶段实现切片

```text
task_profile
 -> workflow_plan: bug_fix + board_validation
 -> repo-implementer handoff
 -> repo-reviewer review_decision
 -> board-runner board_validation_result failed
 -> repo-reviewer board_failure_review
 -> main_route_decision
 -> route_gate accepts/rejects
 -> closure_gate blocks until evidence complete
```

这个切片验证 subpower 的核心价值：独立子代理交接、三侧 evidence、失败评估、主代理动态路由和结构化 runtime gate。
