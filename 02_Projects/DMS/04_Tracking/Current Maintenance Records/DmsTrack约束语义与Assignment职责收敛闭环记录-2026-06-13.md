---
title: DmsTrack 约束语义与 Assignment 职责收敛闭环记录
type: project_record
status: verified
project: DMS
module: Tracking
summary: 收敛 DmsTrack 禁止匹配语义、assignment solver 副作用、Face/Body/Hand gating 与 publish lifecycle 职责；通过独立审查、git diff check 和 J6B 编译。
sources:
  - /home/jichao/dms/include/utils/track.h
  - /home/jichao/dms/source/utils/track.cpp
  - /tmp/subpower-dms-track-semantic-20260613/code_change_manifest.json
  - /tmp/subpower-dms-track-semantic-20260613/review_decision.json
  - /tmp/subpower-dms-track-semantic-20260613/evidence_manifest.json
  - /tmp/subpower-dms-track-semantic-20260613/closure_matrix.json
scope: 仅适用于当前 DMS Tracking 的 assignment policy、solver、输出准备和生命周期职责边界。
risks:
  - 未新增可隔离的 track 专项自动化测试。
  - 未执行 runtime replay 或板端验证。
  - 编译与静态审查不能证明多帧运行效果、ID 连续性或区域级唯一性。
updated_at: 2026-06-13
---

# 1 问题与目标

本轮处理以下内部语义风险：

1. `OptionalCost.hasValue == false`、forbidden cost 和 `rejectCost` threshold 重复表达“禁止匹配”，调试时难以确认实际生效的 gate。
2. assignment policy、cost、gate 和 decision 混在 `costFn` 中，Body 路径还通过 lambda 写入外部结构。
3. Face、Body、Hand 的 gating 分散，组合顺序和拒绝原因不清晰。
4. publish 路径同时承担输出、sanitize 和 lifecycle transition，存在职责混合及同帧重复推进 miss 的风险。

本轮目标是统一约束语义层、评估并移除 `OptionalCost`、纯化 solver、收敛 policy，并把 lifecycle transition 移出 publish。

# 2 实施结论

## 2.1 Assignment 约束语义

- 删除内部 `OptionalCost` 和业务 forbidden-cost sentinel。
- policy 层使用 `AssignmentCandidate` 表达 allowed、cost 和 rejection reason。
- 非有限 cost、严格不满足 `< dummyLoss` 的 cost，以及业务 gate 拒绝统一在 policy 构建阶段形成 rejected edge。
- Hungarian 使用独立的算法 infinity，不再承担业务“禁止匹配”语义。
- 保留 `dummyLoss` 配置键和严格 `<` 接受边界，避免配置与行为契约迁移。

## 2.2 Solver 纯化

- `SolveAssignment` 改为消费预计算的 policy matrix。
- solver 不再调用业务 `costFn`，不更新 track，不写外部 decision 容器。
- Body 的 tracking/acquisition loss 和 `BodyMatchDecision` 在显式 policy 循环中计算。
- Body 仍保持 `min(trackLoss, acquireLoss)` 行为。

## 2.3 Policy 收敛与可观测性

- Face、Body、Hand assignment gate 分别集中到各自 policy matrix 构建阶段。
- rejection reason 覆盖 missing owner、small driver face、distance gate、outside body、non-finite cost 和 reject-cost threshold。
- 仅当存在 unmatched entity 且至少有 rejected edge 时，使用 `LOGD` 输出 `policy_edge_rejection_totals`，避免把正常 assignment 竞争误写成单一拒绝原因。

## 2.4 Publish 与 Lifecycle 边界

- sanitize 与内部状态准备由 owner/update 阶段完成。
- sanitize 成功时，clamp 后的 `box/predBox` 写回内部 track，保持后续帧的状态连续性。
- sanitize 失败时，owner 阶段推进 lifecycle，并且该 track 不进入本帧 publish eligibility 集合。
- Face、Body、Hand publish 函数只消费本帧 eligibility 集合并写 output map，不调用 `AdvanceHit`、`AdvanceMiss`，也不修改 hit/miss counter。
- 显式 matched evidence 保证常规路径每帧至多推进一次 miss。

# 3 保持不变的边界

- `DmsTrack::Init()`、`DmsTrack::Update()` 和 legacy 四类 output map 接口不变。
- 帧级更新顺序和 driver owner 优先顺序不变。
- `dummyLoss` 配置字段不变。
- Face、Body、Hand 的严格 `< dummyLoss` 接受语义不变。
- Hand left/right slot 顺序和 owner key 语义不变。
- 用户已有的 `scripts/compile_j6b.sh` 修改未被本轮覆盖或回退。

# 4 Review 与返工

Subpower 流程执行 planner、repo-implementer、repo-reviewer、verification-manager 和 knowledge-closer 分离。

- 第一轮 review 发现内部 clamp 状态丢失、rejection reason 不可观测、publish 仍推进 lifecycle，路由到 coder rework。
- 第二轮 review 发现 sanitize 失败后非法 track 仍可能进入 output map，以及 rejection summary 可能产生误导，继续路由到 coder rework。
- 最终独立 repo review：`approved`，无 blocking findings。
- Subpower independence、route、evidence、closure gates 均为 ready。

# 5 验证证据

- `git diff --check`：通过。
- `bash scripts/compile_j6b.sh`：通过，最终输出 `[100%] Built target sdk`。
- 构建产物：`/home/jichao/dms/build/main/sdk`，AArch64 ELF。
- C/C++ compiler warning/error：未发现。
- 构建日志仍有仓库既有 CMake developer/deprecation warnings。
- 仓库当前 J6B 配置 `ctest -N` 为 `Total Tests: 0`。
- 仓库未提供可直接复用的 `clang-tidy` 或 `cppcheck` 配置。

# 6 证据边界

- `focused_track_tests: not_available`
- `runtime_replay: not_executed`
- `board_validation: not_required`

本轮证据足以关闭“按既定范围完成约束语义、solver、policy 和 publish/lifecycle 职责收敛，并通过编译、现有静态门禁和独立审查”的任务。

本轮不能关闭：

- `dummyLoss` equality、NaN/Inf、全 unmatched 等专项运行边界；
- sanitize eligibility 和单帧单次 miss 的自动化回归；
- 多帧 ID 连续性、区域级唯一性和代表性样本效果验收。

# 7 知识分层结论

本记录与当前 DMS Tracking 实现强绑定，保留在项目区作为维护闭环证据。

由于缺少专项运行测试和板端验证，本轮不提升到 `01_Knowledge/`，也不声明为通用 assignment solver 设计模式。
