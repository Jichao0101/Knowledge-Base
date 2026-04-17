---
title: cutepower P1 board functional incident baseline
summary: cutepower P1 实施基线的历史快照，保留 board-run、functional-review、incident-investigation 的收敛边界；不再作为当前 plugin 实现或测试入口。
status: verified
doc_role: baseline
truth_role: history
lifecycle_state: superseded
default_entry: false
retrieval_priority: reference
current_replacement:
  - plugins/cutepower/contracts/
  - plugins/cutepower/skills/
  - plugins/cutepower/scripts/runtime-gates.js
  - plugins/cutepower/README.md
scope: 适用于追溯 cutepower P1 三个核心能力的设计收敛边界，不再作为当前 plugin 实现或测试入口。
related_plugins:
  - plugins/cutepower
sources:
  - 02_Projects/Agent Workflow/cutepower_p0_implementation_baseline.md
  - 02_Projects/Agent Workflow/cutepower P1插件落地与运行时门禁收敛记录-2026-04-17.md
  - plugins/cutepower/contracts/role-contracts.yaml
  - plugins/cutepower/contracts/gate-matrix.yaml
  - plugins/cutepower/contracts/review-boundaries.yaml
  - plugins/cutepower/contracts/writeback-levels.yaml
  - plugins/cutepower/contracts/routing-table.yaml
  - 01_Knowledge/Agent Workflow/Plugin-first与Contracts-first治理插件设计模式.md
  - 01_Knowledge/Agent Workflow/运行时门禁与独立审查边界模式.md
updated_at: 2026-04-17
---

> Status note:
> 本文件已降级为历史 baseline。cutepower 当前 active truth 以 `plugins/cutepower/contracts/`、`skills/`、`runtime-gates.js` 与安装/README 文档为准；后续测试不应再将本文件当作默认实现输入。

# 1 目标与范围

本轮目标是停止继续泛化讨论，将已经收敛的 P1 方向冻结成一份可实施 baseline，作为下一轮真实实现的唯一项目入口。

P1 选择以下三个能力，是因为它们直接覆盖当前两类核心生产力场景：

- `cute-board-run`：提供板端复现、重跑、artifact 重采集的共享底座
- `cute-functional-review`：提供需求 / 接口 / 行为验收能力
- `cute-incident-investigation`：提供从症状与 artifact 出发的真实调查闭环

本轮明确不做：

- 不实现任何代码、skill、schema 或 contract 文件
- 不新增 P2 能力
- 不新增复杂 hooks 或运行时 enforcement
- 不重写 P0 主轴或替换现有 5 个 P0 skills
- 不把 legacy 文档重新提升为 active truth source
- 不把 incident investigation 写成万能总 skill
- 不让 functional review 与 code review 混叠
- 不让 board-run 取代 review 或 repo-change

# 2 P1 skill 结构

## 2.1 保留的 P0 skills

- `using-cutepower`
- `cute-scope-plan`
- `cute-repo-change`
- `cute-code-review`
- `cute-writeback`

## 2.2 新增的 P1 skills

- `cute-board-run`
- `cute-functional-review`
- `cute-incident-investigation`

## 2.3 2.2A reviewer 命名策略

本轮固定采用方案 B：

- P1 后续一律统一使用 `repo-reviewer` / `functional-reviewer`
- 不再保留“`reviewer` 既可能表示通用 reviewer，也可能表示代码审查者”的模糊状态

映射要求：

- `role-contracts` 在 P1 实现时应将现有 P0 `reviewer` 明确重命名为 `repo-reviewer`
- `routing-table` 在 P1 新增 route 时只允许引用 `repo-reviewer` 与 `functional-reviewer`
- `review-boundaries` 中 `repo_review` 对应 `repo-reviewer`，`functional_review` 对应 `functional-reviewer`

## 2.4 依赖关系

- `cute-board-run` 是基础 skill，为 `cute-functional-review` 与 `cute-incident-investigation` 提供统一的板端运行与 artifact 采集能力
- `cute-functional-review` 可依赖 `cute-board-run` 获取行为证据，但不依赖 `cute-repo-change`
- `cute-incident-investigation` 可依赖 `cute-board-run` 做复现与重采集；当 probe 明确且允许 debug 修改时，再发起对 `cute-repo-change` 的请求
- `cute-code-review` 对应 `repo-reviewer`，`cute-functional-review` 对应 `functional-reviewer`，两者保持并列 reviewer 关系，不互相替代
- `cute-writeback` 仍是项目区收口角色，不被 `cute-board-run` 或 `cute-incident-investigation` 吞并

## 2.5 推荐调用模式

- implementation / bug_fix 且要求上板验证：
  - `cute-scope-plan -> cute-repo-change -> cute-board-run -> cute-code-review -> cute-writeback`
- audit + functional_scope 且要求板端证据：
  - `cute-scope-plan -> cute-board-run -> cute-functional-review -> cute-writeback`
- incident_investigation：
  - `cute-scope-plan -> cute-incident-investigation`
  - 调查过程中可条件性插入 `cute-board-run`
  - 若需要 debug 级修改，则由 `cute-incident-investigation -> cute-repo-change -> cute-board-run`
  - 若发生 repo 修改，后续必须进入 `cute-code-review`

# 3 cute-board-run 边界

## 3.1 应负责什么

- 绑定并解析 `board_target`
- 执行部署、运行、重跑、回收与最小恢复步骤
- 采集日志、trace、dump、指标、输出文件等 artifact
- 生成统一的板端执行摘要与 artifact manifest
- 输出可被 reviewer 或 investigator 复用的板端证据包

## 3.2 不应负责什么

- 不做根因判断
- 不做需求符合度裁决
- 不做代码质量裁决
- 不修改 repo
- 不直接执行 writeback
- 不宣布任务闭环完成

## 3.3 最小输入

- `board_target`
- `deploy_artifacts`
- `run_commands`
- `collect_paths`
- `expected_signals`
- `timeout_policy`
- `reset_or_recovery_steps`
- `artifact_expectations`

## 3.4 最小输出 artifact

- `board_run_report`
- `artifact_manifest`
- `signal_observations`
- `execution_status`
- `board_failure_reason`
- `environment_fingerprint`

## 3.5 复用方式

- `cute-functional-review` 使用它获取验收所需行为证据
- `cute-incident-investigation` 使用它做复现、重采集与带 probe 的 rerun
- `cute-code-review` 可读取其输出作为 review evidence，但不由 `cute-board-run` 代替 review

# 4 cute-functional-review 边界

## 4.1 应负责什么

- 对需求、接口约束、行为边界与验收项做只读审查
- 输出 `acceptance_items`、`compliance_matrix`、`evidence_used`、`evidence_gaps`
- 当证据不足时明确给出 `blocked` 或 `evidence_gap`，而不是硬判符合

## 4.2 不应负责什么

- 不修改代码
- 不替代 `cute-code-review` 做总体工程质量裁决
- 不主导根因调查
- 不直接决定 writeback

## 4.3 为什么需要板端运行能力

- 很多功能型验收项依赖真实运行行为，而不是静态代码可判定
- 行为证据、接口回灌结果、板端日志与输出 artifact 常是验收主证据
- 没有板端证据时，functional review 只能给出证据不足，而不能稳定产出符合度结论

## 4.4 为什么不能拥有 repo 修改权限

- reviewer 一旦可以直接修改代码，独立性会失效
- functional review 的职责是判“是否符合需求 / 接口 / 行为”，不是修复实现
- 修改请求应回流给 `cute-repo-change` 或转入 `cute-incident-investigation`

## 4.5 最小输入

- `requirements_package`
- `acceptance_items`
- `interface_contracts`
- `evidence_package`
- `board_target` 或 `no_board_execution`
- `relevant_code_context`

## 4.6 最小输出 artifact

- `acceptance_items`
- `compliance_matrix`
- `evidence_used`
- `evidence_gaps`
- `review_conclusion`
- `suggested_followup`

## 4.7 与 cute-code-review 的边界

- `cute-functional-review`：判断需求 / 接口 / 行为是否符合
- `cute-code-review`：判断实现是否正确、越界、回归风险是否可接受、验证是否充分
- 前者不替代后者的工程质量裁决，后者也不替代前者的验收符合度结论

## 4.8 reviewer 独立性硬约束

- `cute-code-review` 与 `cute-functional-review` 必须使用独立 reviewer 阶段或独立 reviewer 实例
- reviewer 输入必须是裁剪后的最小证据包，不得直接继承 coder / investigator 的全量上下文、自然语言推理或排查草稿
- `repo-reviewer` 的最小 evidence package 至少包含：
  - `task_goal`
  - `implementation_plan`
  - `diff_summary`
  - `verification_results`
  - `verification_tier`
  - `necessary_code_context`
  - 若涉及板端：`board_run_report`、`artifact_manifest`、`board_failure_reason`
- `functional-reviewer` 的最小 evidence package 至少包含：
  - `requirements_package`
  - `acceptance_items`
  - `interface_contracts`
  - `evidence_package`
  - 若涉及板端：`board_run_report`、`artifact_manifest`、`signal_observations`
- 若关键证据缺失但仍可指出缺口，应输出 `blocked` 或 `evidence_gap`
- 若证据已足以证明未达成要求，应输出 `rework_required`
- 上述约束应直接映射到 `review-boundaries` 扩展，不得只留在 skill 描述层

# 5 cute-incident-investigation 边界

## 5.1 应负责什么

- 从症状、日志、trace、dump、artifact 出发形成可检验假设
- 识别证据缺口与最小 rerun / probe 路径
- 组织复现、重采集、异常分流与 route 决策
- 在证据不足时允许调查闭环为 `insufficient_evidence`、`environment_issue` 或 `missing_observability`

## 5.2 不应负责什么

- 不直接持有 repo 写权限
- 不直接替代 `cute-code-review` 或 `cute-functional-review`
- 不直接执行最终 writeback 裁决
- 不默认承担业务逻辑修复
- 不作为 implementation / review / writeback 的万能总 skill

## 5.3 为什么需要 artifact read / rerun / probe

- incident 入口通常是板端现象与证据，而不是完整需求包
- 不读取 artifact 无法建立可检验假设
- 不允许 rerun 无法确认现象稳定性与触发条件
- 不允许 probe 无法补齐 observability 缺口，调查只能停留在猜测

## 5.4 何时可以发起 debug 级 repo change 请求

必须同时满足：

- 当前证据不足以区分两个及以上主要假设
- probe 目标明确，且属于 instrumentation / logging / assert / capture 一类 debug 修改
- 修改范围在已授权 `repo_scope` 内
- 已定义 rerun 与回收计划
- 本轮目标仍是调查闭环，而不是顺手扩大为业务重构

明确约束：

- `cute-incident-investigation` 只发起请求，不直接落地 repo 写入
- 实际 repo 修改仍由 `cute-repo-change` 完成
- 只要发生 repo 修改，后续必须进入 `cute-code-review`

## 5.5 最小输入

- `observed_symptoms`
- `artifact_inventory`
- `log_sources`
- `trigger_condition`
- `reproduction_confidence`
- `environment_fingerprint`
- `board_target` 或 `no_board_execution`
- `repo_scope`
- `verification_tier`

## 5.6 最小输出 artifact

- `hypothesis_set`
- `evidence_gaps`
- `probe_plan`
- `rerun_summary`
- `route_decision`
- `next_required_skill`

## 5.7 handoff 规则

- handoff 给 `cute-code-review`：
  - 已发生 repo 修改
  - 调查结论涉及代码缺陷或 probe 修改有效
- handoff 给 `cute-functional-review`：
  - 争议点落在需求、接口约束或行为边界
  - 需要对验收项做明确符合度裁决
- handoff 给 `cute-writeback`：
  - 调查已闭环为证据不足、环境问题、可复现问题摘要或已明确下游 route

# 6 core contracts 扩展点

P1 只允许扩展现有五类 core contracts，不新开大类 contract。

## 6.1 role-contracts

需要新增：

- `board-operator`
- `functional-reviewer`
- `incident-investigator`
- `repo-reviewer`

约束：

- 现有 P0 `reviewer` 在 P1 实现时应正式收口为 `repo-reviewer`，不再作为新 route 的角色名
- `board-operator` 允许 `board_execute`、`artifact_collect`、`verification_read`、条件性 `verification_write`、`project_log_write`，不允许 `repo_write` 或 `review_decision`
- `repo-reviewer` 允许 `review_decision`、`verification_read`、受限 `artifact_collect`、`project_log_write`，不允许 `repo_write`、`verification_write` 或部署类 `board_execute`
- `functional-reviewer` 允许 `review_decision`、`verification_read`、受限 `artifact_collect`、`project_log_write`，不允许 `repo_write`、`verification_write` 或部署类 `board_execute`
- `incident-investigator` 允许 `verification_read`、条件性 `board_execute`、`artifact_collect`、`project_log_write`，不直接持有 `repo_write`

## 6.2 gate-matrix

需要新增 action：

- `board_execute`
- `artifact_collect`

约束：

- `cute-board-run` 的板端动作由 `board_execute` 与 `artifact_collect` 直接控制
- `verification_read` / `verification_write` 继续表示 repo 或验证侧读写动作；`board_execute` / `artifact_collect` 不替代它们，而是补充 board side 的独立动作轴
- `analysis` 可允许受控 `board_execute` 与 `artifact_collect`，用于 investigation 复现与取证
- `implementation` 可允许 `board_execute` 与 `artifact_collect`，用于改动后验证
- `review` 仅允许 `artifact_collect`，且只用于 reviewer 补齐缺失行为证据；review 态默认不允许部署类 `board_execute`
- reviewer 在 `review` 态不得借 `cute-board-run` 滑入实现、部署、调参或 rerun ownership；若需要新的部署、配置变更或写型验证，必须回退到 `cute-repo-change` 或重新进入 investigation / implementation 链
- `repo_write` 仍只由实现链路承担，不因 board 能力引入而下放给 reviewer 或 investigator
- `verification_write` 不得被解释为 reviewer 可通过 board-run 执行写型部署或修改型验证

## 6.3 review-boundaries

需要新增 review type：

- `functional_review`

最小要求：

- `required_evidence` 至少覆盖 `requirements_package`、`acceptance_items`、`evidence_package`
- `reviewer_cannot` 明确禁止 `edit_review_target`、`override_gate_matrix`
- `allowed_outcomes` 至少包含 `pass`、`rework_required`、`blocked`
- `repo_review` 与 `functional_review` 都必须要求独立 reviewer 阶段 / 实例与最小 evidence package
- 当证据缺失但缺口可描述时，允许输出 `blocked` 或 `evidence_gap`
- 不允许 reviewer 继承 coder / investigator 的全量推理过程替代证据包

## 6.4 writeback-levels

需要补充前置条件：

- `board_evidence_recorded_when_required`
- `investigation_route_recorded_when_required`
- `repo_review_passed_when_required`
- `functional_review_passed_when_required`

约束：

- 板端执行完成不等于可直接 writeback
- investigation 闭环为不足证据时，也必须先记录 route 与边界，再进入项目区收口
- P1 后续实现不得继续使用单一 `review_passed` 表达所有 route 的 writeback 前置条件

## 6.5 6.4A writeback pass matrix

route 到 pass / gate / writeback level 的映射固定如下：

- `bug_fix` with repo change
  - required_pass: `repo_review_passed`
  - required_gate: `review`
  - allowed_writeback_level: `project_current_update`
- `functional acceptance`
  - required_pass: `functional_review_passed`
  - required_gate: `review`
  - allowed_writeback_level: `project_current_update`
- `bug_fix` with repo change 且同时要求功能验收
  - required_pass: `repo_review_passed + functional_review_passed`
  - required_gate: `review`
  - allowed_writeback_level: `project_current_update`
- `incident_investigation` closed with `insufficient_evidence`
  - required_pass: `none`
  - required_gate: `analysis`
  - allowed_writeback_level: `project_log_write`
- `incident_investigation` closed as `environment_issue`
  - required_pass: `none`
  - required_gate: `analysis`
  - allowed_writeback_level: `project_log_write`
- `incident_investigation` produced candidate fix but not yet reviewed
  - required_pass: `none`
  - required_gate: `implementation`
  - allowed_writeback_level: `project_log_write`
  - forbidden_writeback_level: `project_current_update`

## 6.6 routing-table

需要新增 route：

- `implementation_board_validation`
- `bug_fix_board_validation`
- `audit_functional_read_only`
- `audit_functional_board`
- `incident_investigation_default`
- `incident_investigation_board`

约束：

- `board_execution_required` 场景下，route 应显式插入 `cute-board-run`
- `audit + functional_scope` 应显式路由到 `cute-functional-review`
- `incident_investigation` 不默认进入 `cute-repo-change`，只有 probe 条件满足时才分流
- 所有代码审查类新增 route 一律引用 `repo-reviewer`
- 所有功能验收类新增 route 一律引用 `functional-reviewer`
- 任何 `incident_investigation` route 若无 `repo_review_passed` 或 `functional_review_passed`，都不得把候选修复直接推进到 `project_current_update`

# 7 reviewer 验收清单

reviewer 至少应检查以下边界是否保持：

1. P0 主轴是否保持不变，没有借 P1 重写现有 5 个 P0 skills
2. `cute-board-run` 是否仍是基础执行 skill，而不是 review / repo_change / writeback 替代物
3. `cute-functional-review` 是否仍只做需求 / 接口 / 行为验收，没有获得 repo 修改权限
4. `cute-code-review` 与 `cute-functional-review` 是否仍保持独立 reviewer 边界
5. `cute-incident-investigation` 是否仍是调查 skill，而不是万能总 skill
6. `cute-incident-investigation` 是否明确“不直接持有 repo 写权限，repo 落地仍由 cute-repo-change 完成”
7. P1 contract 扩展是否只发生在既有五类 contracts 中，没有新增大类 contract
8. legacy 文档是否仍仅作为参考来源，没有回升为 active truth source
9. reviewer 命名是否已收口为 `repo-reviewer` / `functional-reviewer`
10. board action taxonomy 是否已收口为 `board_execute` / `artifact_collect` 与 `verification_read` / `verification_write` 的明确分层
11. route 的 writeback pass 语义是否已写成 `repo_review_passed` / `functional_review_passed` 的明确映射，而不是模糊的 `review_passed`
12. 是否没有引入 P2 能力、复杂 hooks 或运行时 enforcement
13. `cute-code-review` 与 `cute-functional-review` 是否要求独立 reviewer 阶段 / 实例与最小 evidence package

以下情况应直接判 `rework_required`：

- 把 `cute-functional-review` 与 `cute-code-review` 混成一个 reviewer
- 让 `cute-board-run` 直接承担 review、repo_change 或 writeback
- 让 `cute-incident-investigation` 直接持有 repo 写权限或最终裁决权
- 为 P1 新开大类 contract
- 把 legacy 长文重新写回 skills / AGENTS / toml / contracts 正文
- 继续保留 `reviewer` / `repo-reviewer` 双义命名
- 允许 reviewer 在 `review` 态通过 board-run 承担部署或实现职责
- 继续使用模糊的 `review_passed` 作为 P1 writeback 总前置条件
- 让 reviewer 继承 coder / investigator 的全量上下文替代最小 evidence package

# 8 当前状态

- current_status: `pending_review`
- implementation_gate: `allowed_after_p1_baseline_reviewed`
- review_focus:
  - 三个 P1 skill 的边界是否清晰且互不吞并
  - contract 扩展点是否足够支撑实现，但没有重新膨胀为长篇规则系统
  - board-run 是否被正确定义为基础 skill
  - incident investigation 是否保持调查闭环定位
