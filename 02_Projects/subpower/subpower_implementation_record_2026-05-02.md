---
type: project_record
status: current
domain: 工程工作流
topic: subpower 真实任务治理加固记录
project: subpower
created_at: 2026-05-02
updated_at: 2026-05-02
source_repo: /mnt/d/subpower
related_blueprint: /mnt/d/Knowledge-Base/02_Projects/subpower/subpower_architecture_blueprint_current.md
scope: 记录 subpower 在真实任务执行中防止 host-direct execution 绕过治理的加固结果。
risks:
  - runtime_spawn / runtime_handoff 的真实性仍依赖外层 agent runtime 提供可信记录
  - runtime gate 只能验证结构与证据关系，不判断业务修复质量
  - host-only fallback 可以记录降级执行，但不能被误报为完整 subagent-first execution
---

# 1 subpower 真实任务治理加固记录 2026-05-02

## 1.1 本轮目标

本轮目标是评估并优化 `/mnt/d/subpower` 在真实任务执行中的流程治理能力，重点修复：

- 用户明确要求 `按 subpower 处理` 时，主线程仍可能绕过 artifact spine 与角色分离，直接完成代码修改、编译、板端验证、统计或知识库写回；
- 缺少 repo-implementer、repo-reviewer、board-runner / verification-manager、knowledge-closer 等角色派生证据；
- 主线程参与关键职责后缺少结构化披露；
- host-only fallback、declared-only evidence、synthetic fixture、structural validation 或 demo 被误称为完整 subagent-first execution。

本轮不执行真实板端验证，不直接写外部 Knowledge-Base，不新增 `subpower run` 或自动业务 runner。

## 1.2 审计结论

审计发现的主要治理缺口：

- `subagent_execution_status.subpower_invoked` 曾可能掩盖 `prompt_context`、`task_profile` 或 `workflow_plan` 中的 explicit subpower marker；
- `board_session.json` 已有 schema 和文档语义，但 board validation / closure / writeback gate 没有把它作为 board execution spine 的必需证据；
- minimal artifact spine 主要是文档建议，complete claim 与 runtime report 对 structural-ready 和 complete-execution 的区分不够显式；
- role separation 原本主要硬检 implementer 与 reviewer，board-runner、verification-manager、knowledge-closer 等关键角色存在更弱的 actor-separation 检查；
- writeback terminal artifacts 的 producer role 检查不足；
- duplicate role invocation 可用“干净的第一个 role invocation”掩盖实际 artifact producer 与其他关键角色 actor 重合。

## 1.3 已完成修复

仓库：`/mnt/d/subpower`

已修改：

- `scripts/runtime-gates.js`
- `scripts/runtime-report.js`
- `scripts/test-subagent-execution.js`
- `scripts/test-runtime-report.js`
- `scripts/test-fixtures.js`
- `scripts/test-full-flow-fixture.js`
- `scripts/test-incident-bugfix-board-writeback-fixture.js`
- `docs/runtime-gates.md`
- `fixtures/incident-bugfix-board-writeback/board_session.failed.json`
- `fixtures/incident-bugfix-board-writeback/board_session.passed.json`

核心修复：

- cross-check `prompt_context`、`task_profile`、`workflow_plan` 中的 subpower marker 与 `subagent_execution_status.subpower_invoked`；
- 新增 execution classification，使 runtime report 明确区分 structural gate readiness 与 complete execution support；
- 将 `synthetic_fixture`、`declared_only`、`host_only`、`insufficient`、`host_only_fallback` 标记为 non-complete / degraded execution evidence；
- `board_validation_result.json` 存在时，closure、writeback 与 complete claim 必须具备 `board_session.json`；
- complete claim producer requirements 纳入 `board_session`、`writeback_plan`、`writeback_receipt`、`writeback_declined`；
- writeback candidate、plan、receipt、declined 均要求 `knowledge-closer` producer role；
- 主线程 critical host participation 即使 disclosed，也阻断 complete subagent-first execution claim；
- critical actor separation 改为检查实际生产关键 artifact 的 invocation，阻断 duplicate role invocation 绕过。

## 1.4 新增回归覆盖

新增或强化的测试覆盖：

- explicit subpower 缺少 `subagent_execution_status.json`；
- `subagent_execution_status.subpower_invoked:false` 与 task/prompt/workflow subpower marker 冲突；
- host-only fallback 声称 complete subpower execution；
- declared-only / synthetic fixture / non-concrete producer evidence 支持 complete claim；
- spawned subagents + synthetic fixture 只能 structural-ready，不能 complete-supported；
- board validation result 缺少 board session；
- writeback plan 或 terminal artifact 由错误角色生产；
- disclosed critical host participation 仍声称 complete claim；
- duplicate board-runner / knowledge-closer / verification-manager invocation 复用 implementer 或 reviewer actor。

## 1.5 已验证命令

```bash
node scripts/subpower.js validate
node scripts/subpower.js test
node scripts/test-all.js
node scripts/test-subagent-execution.js
git diff --check
```

以上命令在本轮加固后通过。

独立 reviewer 复核结论：

- duplicate role invocation 绕过已修复；
- `criticalActorSeparationVerdict()` 已基于实际 producer invocation 与所有 concrete critical role invocation 做 actor comparison；
- 未发现阻塞问题。

## 1.6 当前限制

- 仓库可以验证 artifact 中的 evidence type、producer role、agent actor、artifact spine 与 gate 关系；
- 仓库不能单独证明 `runtime_spawn` / `runtime_handoff` evidence ref 的真实性；
- 真实完整 subagent-first execution 仍需要外层 Codex / agent runtime 提供可信 invocation record；
- runtime gate 仍不判断业务根因、实现质量或板端验收标准是否充分。

## 1.7 知识写回状态

本记录属于项目区阶段性实现记录，保留在 `02_Projects/subpower/`。

不提升到 `01_Knowledge/` 的原因：

- 本轮内容仍与 subpower 项目实现强绑定；
- runtime 可信 invocation record 的外层机制仍有边界；
- 尚未经过正式知识提升审核。
