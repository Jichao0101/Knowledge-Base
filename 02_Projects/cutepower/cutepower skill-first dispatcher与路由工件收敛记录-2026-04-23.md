---
title: cutepower skill-first dispatcher与路由工件收敛记录
summary: 记录 cutepower 在 2026-04-23 完成的 skill-first discipline 收敛：将 using-cutepower 升级为 mandatory dispatcher，引入 skill_route_matrix 与 dispatch_manifest，并把技能顺序约束接入 runtime gate。
status: pending_review
doc_role: record
truth_role: record
lifecycle_state: active
default_entry: false
retrieval_priority: high
related_plugins:
  - cutepower
sources:
  - 02_Projects/cutepower/cutepower_design_current.md
  - 02_Projects/cutepower/cutepower_implementation_current.md
  - 02_Projects/cutepower/cutepower_validation_current.md
  - /mnt/d/cutepower/contracts/task-normalization.yaml
  - /mnt/d/cutepower/contracts/routing-table.yaml
  - /mnt/d/cutepower/contracts/skill_route_matrix.yaml
  - /mnt/d/cutepower/scripts/task-profile.js
  - /mnt/d/cutepower/scripts/task-intake.js
  - /mnt/d/cutepower/scripts/host-runtime.js
  - /mnt/d/cutepower/scripts/runtime-gates.js
  - /mnt/d/cutepower/scripts/validate-contracts.js
  - /mnt/d/cutepower/scripts/test-task-profile.js
  - /mnt/d/cutepower/scripts/test-task-intake.js
  - /mnt/d/cutepower/scripts/test-host-runtime.js
  - /mnt/d/cutepower/scripts/test-runtime-gates.js
  - /mnt/d/cutepower/scripts/test-skill-routing.js
  - /mnt/d/cutepower/scripts/test-skill-docs.js
  - /mnt/d/cutepower/skills/using-cutepower/SKILL.md
  - /mnt/d/cutepower/docs/skill-workflow-map.md
scope: 适用于追溯 cutepower 如何从 runtime-gates 主导的治理收敛到 skill-first discipline + contracts-first truth + runtime-gate enforcement 的分层结构。
updated_at: 2026-04-23
---

# 1 目标

本轮不是把 cutepower 改造成 superpowers 镜像，而是在不恢复 hook、不引入 subagent-first orchestration 的前提下，把入口纪律、技能路由、阶段切换与输出工件约束显式化。

# 2 关键问题

- 之前 `contracts/` 与 `runtime-gates` 已经比较强，但 skill discipline 仍偏薄。
- `using-cutepower` 更像入口说明，不是强制 dispatcher。
- `routing-table.skill_chain` 能描述顺序，但不能描述 skill 级前置工件、前驱和 stop 条件。
- runtime 能拦越权动作，但不能直接判定“是不是跳过了当前应该进入的 skill”。

# 3 本轮实现

## 3.1 新增 contracts 层路由纪律

- 新增 `contracts/skill_route_matrix.yaml`
- 新增 `schemas/skill-route-matrix.schema.json`
- `contract-index.yaml` 与 `validate-contracts.js` 已接入新 contract

该 matrix 只表达结构化路由纪律：

- route 对应哪些 ordered skills
- 每个 skill 所处 phase
- 允许的前驱 skill
- skill 进入前需要哪些 artifacts
- skill 执行后应产出哪些 artifacts

它没有复制 `role-contracts`、`review-boundaries` 或 `writeback-levels` 的规则文本，因此仍符合 contracts-first truth。

## 3.2 using-cutepower 升级为 mandatory dispatcher

- `task-normalization.yaml` 新增 `mandatory_dispatcher_skill`
- `protected_execution_skills` 扩展到所有 governed execution skills
- `using-cutepower/SKILL.md` 改写为 mandatory dispatcher discipline

结果是：

- governed task 先进入 dispatcher
- dispatcher 持久化 preflight artifacts
- downstream skill 只按 `dispatch_manifest.next_skill` 合法进入

## 3.3 intake 与 route truth 对齐

- `task-intake.js` 现在消费 `task-profile.js` 的 contracts-first normalization 结果
- intake 新增 `dispatch_manifest`
- 只读 audit 仍保留显式只读语义纠偏，但不再维护一套独立主路由真相

这使入口 routing 不再与 contracts 漂移。

## 3.4 runtime gate 增加 skill 顺序约束

- `runtime-gates.js` 把 `dispatch_manifest` 纳入 required preflight artifacts
- 新增 governed skill transition check

现在 runtime 不只检查 capability、phase、artifact existence，还会检查：

- 当前 skill 是否等于 `dispatch_manifest.next_skill`
- 当前 phase 是否与 dispatcher 声明一致

因此“用户点名某个 downstream skill 直接跳转”会在运行时被阻断。

## 3.5 skills 补齐统一章节

P0/P1 skills 统一补齐：

- `When This Skill Is Legal`
- `Required Input Artifacts`
- `Workflow`
- `Required Outputs`
- `Phase Exit / Next Skill`
- `Stop Conditions`

这里的目标不是让 skill 成为 policy truth，而是给人类和主代理一个稳定、可读、可测试的 workflow discipline 层。

# 4 新增或变化的核心工件

- `task_profile.json`
- `route_resolution.json`
- `dispatch_manifest.json`
- `runtime_gate.json`

`dispatch_manifest` 是这轮新增的关键桥梁工件：它连接 dispatcher、skill routing 和 runtime enforcement。

# 5 验证

本轮新增或更新后通过的验证：

- `node scripts/validate-contracts.js`
- `node scripts/test-task-profile.js`
- `node scripts/test-task-intake.js`
- `node scripts/test-host-runtime.js`
- `node scripts/test-runtime-gates.js`
- `node scripts/test-skill-routing.js`
- `node scripts/test-skill-docs.js`

# 6 非目标保持不变

- 不恢复 hook 方案
- 不把知识库或 external docs 变回 active truth source
- 不让 skills 自己成为 policy truth
- 不引入 subagent-first 主线
- 不引入后台守护进程
