---
type: project
status: current
domain: 工程工作流
topic: subpower 架构蓝图
project: subpower
created_at: 2026-04-27
updated_at: 2026-05-02
source_repos:
  - /mnt/d/subpower
  - /mnt/d/knowledgeBase/plugins/agent-workflow-migrator
scope: 独立的 subagent-first 三侧工作流编排 runtime 设计蓝图。
risks:
  - 将 subpower 过早膨胀为固定端到端 workflow engine
  - 将 subpower 主状态耦合到外部 orchestration runtime artifacts
  - runtime gate 承担业务语义判断
  - reviewer 独立性只停留在文档约束而缺少 invocation 与 artifact 检查
  - 用户明确要求 subpower 时，主线程绕过 artifact spine 与角色分离直接完成关键职责
  - synthetic fixture、declared-only evidence、host-only fallback 或 structural report 被误报为完整 subagent-first execution
---

# 1 subpower 架构蓝图 current

## 1.1 摘要

`subpower` 是一个独立的 subagent-first 三侧工作流编排 runtime。

`subpower` 负责约束哪个子代理在什么状态下可以接手任务，知识库 / 代码库 / 板端三侧状态如何同步，子代理之间如何交接 artifact，板端失败如何进入独立评估，主代理如何基于评估动态选择返工路径。

核心模型是：

```text
workflow patterns + decision points + runtime gates + run artifacts
```

workflow 是可复用执行模式，不是固定写死的端到端脚本。

## 1.2 独立性边界

`subpower` 独立负责：

- 子代理 role boundary；
- invocation identity 与 reviewer independence 检查；
- knowledge / repo / board side-state transition；
- 子代理间 handoff packet；
- board failure assessment；
- main route decision；
- closure matrix 与 writeback precondition。

边界结论：

- `.subpower/run/<session_id>/` 是 subpower authoritative state。
- subpower 不读取外部 orchestration runtime 的 run-state。
- subpower 不生成外部上游 context artifact。
- subpower 不保留外部 runtime adapter。
- `task_profile`、`evidence_manifest`、`review_decision` 可以采用相似概念，但 schema 必须由 subpower 独立定义。
- `agent_invocation_manifest`、`side_state`、`handoff_packet`、`board_failure_review`、`main_route_decision`、`closure_matrix` 必须由 subpower 独立定义。
- subpower README 与仓库 docs 面向用户保持自包含，不写入外部实现依赖或兼容说明。

## 1.3 硬约束

- 主代理是 workflow composer / routing decision owner。
- 用户明确要求 `use subpower` / `按 subpower 处理` 时，默认进入 subagent-first orchestration。
- 主代理默认只做编排、证据收集、gate enforcement 和最终汇总，不替代 repo implementation、independent review、board validation、failure analysis 或 knowledge writeback assessment。
- 如果 runtime 无法实际派生子代理，只能进入 degraded / non-complete host-only fallback，不能声称 complete subpower execution。
- 主代理参与任何关键职责必须写入 `subagent_execution_status.json` 的 host participation 记录；关键职责参与会限制 complete claim。
- 主代理不得伪造 reviewer 结论。
- coder 不得自审通过。
- reviewer 不得直接修改代码。
- board-runner 没有 `board_target.json` 不得执行。
- board-runner 不得自行关闭任务。
- board validation failed 后，必须先产生 `board_failure_review.json`，再由主代理产生 `main_route_decision.json`。
- runtime gate 只判断结构合法性：role、phase、artifact、schema、independence、board target、evidence、route、closure、writeback。
- runtime gate 不判断业务语义、根因正确性、实现质量优劣或验收标准是否合理。
- declared-only evidence、synthetic fixture、host-only fallback、demo、structural validation 或单纯测试通过，只能作为结构证据，不能支持完整 subagent-first execution claim。

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
│   ├── contracts/
│   └── run-artifacts/
├── fixtures/
├── scripts/
├── skills/
└── docs/
```

目录职责：

- `.codex-plugin/`：插件分发元数据，用于未来作为 Codex plugin 安装。
- `agents/`：可实例化子代理骨架，只引用 contracts，不作为 policy truth。
- `contracts/`：active truth source，定义角色、workflow pattern、decision point、gate、artifact requirement、side-state、route policy、closure policy。
- `schemas/`：run artifact 与 contract 的 schema。
- `fixtures/`：可回归验证的真实工作流 artifact 样例。
- `scripts/`：runtime gate、artifact IO、contract validation、staging install、负向测试与回归入口。
- `skills/`：主代理入口与使用纪律，不复制 contracts 规则文本。
- `.subpower/run/<session_id>/`：subpower repo-local runtime state，必须被 ignore，不进入插件包的版本历史。

## 1.5 MVP agent set

MVP agent：

- `workflow-orchestrator`：主代理职责模式，负责 workflow 组合、route decision、side-state、closure check。
- `knowledge-planner`：任务定性、scope planning、implementation plan、verification plan、board target planning。
- `repo-implementer`：授权范围内的代码修改与本地验证。
- `repo-reviewer`：独立审查代码、验证证据、board failure assessment。
- `board-runner`：board target 绑定、执行、artifact 采集、validation result 输出。

第二阶段已纳入的 post-MVP agent：

- `failure-analyst`：复杂根因分析或多轮返工不收敛。
- `verification-manager`：复杂验证矩阵。
- `knowledge-closer`：closure 通过后的知识写回执行。

仍延后 agent：

- `knowledge-auditor`：候选知识转正审查。
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
- `subagent_execution_gate`
- `board_target_gate`
- `evidence_gate`
- `route_gate`
- `closure_gate`
- `writeback_gate`

gate 的职责是阻断结构非法动作，例如：

- coder 自己生成 `review_decision.json` 并 close；
- reviewer 直接修改代码；
- explicit subpower invocation 缺少 `subagent_execution_status.json`；
- `subagent_execution_status.json` 与 prompt/task/workflow 中的 subpower marker 冲突；
- host-only fallback 声称 complete subpower execution；
- synthetic fixture、declared-only、host-only、insufficient evidence 被用于 complete claim；
- 主线程 critical host participation 未披露，或披露后仍声称 complete subagent-first execution；
- duplicate role invocation 通过“干净的第一个 role invocation”掩盖实际 artifact producer 与其他关键角色 actor 重合；
- board-runner 没有 `board_target.json` 就执行；
- `board_validation_result.json` 存在但缺少 `board_session.json`；
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
- `board_session.json`（执行板端时）
- `board_validation_result.json`（执行板端时）
- `board_failure_review.json`（板端失败时）
- `main_route_decision.json`（decision point route 时）
- `evidence_manifest.json`
- `closure_matrix.json`
- `subagent_execution_status.json`
- `writeback_plan.json`
- `writeback_receipt.json` 或 `writeback_declined.json`

延后：

- `incident_report.json`
- `root_cause_hypotheses.json`
- `next_workflow_recommendation.json`
- `writeback_receipt.json`
- `writeback_declined.json`

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
- `scripts/install-plugin.js` 只是 staging utility，不代表正式发布流程；
- 默认不得覆盖已有 target，只有 `--force` 可覆盖；
- staging package 不得包含 `.subpower/run/`、`node_modules/`、`coverage/`、`logs/`、`tmp/`。

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

## 1.13 第二阶段实现状态

第二阶段已完成：

- 移除外部 runtime adapter 与兼容文档，subpower 仓库文档保持自包含；
- 新增 `scripts/install-plugin.js`，支持 personal / repo scope staging、dry-run、force、结构化 JSON summary；
- 新增 `scripts/schema-validator.js`，实现轻量 JSON schema subset：`type`、`required`、`properties`、`enum`、`items`、`additionalProperties`、nested object、arrays；
- `runtime-gates.js` 已调用 schema validator，不再只做 required-field 粗检；
- 增强 `board_failure_review`、`main_route_decision`、`closure_matrix` 等 artifact schema；
- 新增 `failure-analyst`、`verification-manager`、`knowledge-closer` 及对应 role / gate / workflow optional participant 边界；
- 新增 `fixtures/bugfix-board-failure-rework/`，覆盖板端失败后 reviewer assessment 再 route 的 coder/planner rework 路径；
- 新增 `scripts/test-all.js` 作为全量回归入口；
- 新增无外部 runtime dependency 的负向扫描测试。

当前验证命令：

```bash
node scripts/validate-contracts.js
node scripts/test-runtime-gates.js
node scripts/test-decision-points.js
node scripts/test-agent-boundaries.js
node scripts/test-run-artifacts.js
node scripts/test-schema-validator.js
node scripts/test-install-plugin.js
node scripts/test-fixtures.js
node scripts/test-all.js
```

以上在 2026-04-28 第二阶段收尾时已通过。

## 1.14 真实任务治理加固状态

2026-05-02 已完成一轮面向真实任务执行偏差的治理加固。

触发问题：

- 用户明确要求 `按 subpower 处理` 时，主线程仍可能直接执行 implementation、review、board validation、failure analysis 或 knowledge writeback assessment；
- 执行前未建立完整或最小 artifact spine；
- 未记录 repo-implementer、repo-reviewer、board-runner、verification-manager、knowledge-closer 等角色派生证据；
- 主线程参与关键职责后缺少结构化披露；
- host-only fallback、declared-only evidence、synthetic fixture、structural validation 或 demo 可能被包装成完整 subagent-first execution。

本轮收紧后的核心语义：

- `prompt_context`、`task_profile`、`workflow_plan` 中的 subpower marker 会与 `subagent_execution_status.subpower_invoked` 交叉校验；
- `execution_evidence_status: complete` 只表示 spawned subagents + concrete runtime handoff/spawn evidence + non-degraded status；
- `synthetic_fixture`、`declared_only`、`host_only`、`insufficient` 与 `host_only_fallback` 均为 non-complete / degraded execution evidence；
- runtime report 同时输出 structural gate readiness 与 complete execution support，避免把结构通过误读为流程完成；
- complete claim 必须有 `agent_invocation_manifest.json` 中关键角色的 concrete producer evidence；
- `board_validation_result.json` 存在时，closure/writeback/complete claim 必须同时具备 `board_session.json`；
- writeback candidate、plan、receipt、declined 均必须由 `knowledge-closer` 角色生产；
- critical host participation 即使已披露，也不能支持 complete subagent-first execution claim；
- critical actor separation 检查基于实际生产关键 artifact 的 invocation，而不是只看某个 role 的第一个 invocation，从而阻断 duplicate role invocation 绕过。

本轮新增或更新的回归覆盖：

- explicit subpower 缺少 execution status；
- status artifact 与 explicit invocation marker 冲突；
- host-only fallback 声称 complete execution；
- declared-only / synthetic fixture / non-concrete producer evidence 支持 complete claim；
- board validation result 缺少 board session；
- writeback plan 或 terminal artifact 由错误角色生产；
- 主线程 critical role participation 披露后仍声称 complete claim；
- board-runner、knowledge-closer、verification-manager 通过 duplicate invocation 复用 implementer/reviewer actor。

已验证命令：

```bash
node scripts/subpower.js validate
node scripts/subpower.js test
node scripts/test-all.js
node scripts/test-subagent-execution.js
git diff --check
```

上述命令在 2026-05-02 治理加固后通过。

仍存在的边界：

- 仓库只能验证 artifact 中记录的 evidence type、producer、actor 与 gate 关系；
- 仓库自身不能加密证明某个 `runtime_spawn` / `runtime_handoff` evidence ref 一定来自真实 runtime；
- 真实子代理派生证据仍需要外层 Codex / agent runtime 提供可信 invocation record。
