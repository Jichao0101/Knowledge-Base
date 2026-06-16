---
title: DmsTrack 基线对比与 Head-first 路线收缩设计记录
summary: 对比稳定基线 1401fc338107f05b9cf 与 feat/ljc/track_0615 当前实现，确认 public API 未变、行为扩张集中在 track.cpp，并将后续路线收缩为 face/head identity、2m face-only、5m driver-bound body/hand evidence。
status: reviewed
doc_role: review_record
truth_role: project_review
scope: DmsTrack head-first 路线设计审查、基线对比、过时实验路线归档和后续分阶段实现建议；不包含代码修改、runtime replay、单元测试或板端验证。
sources:
  - /home/jichao/dms/include/utils/track.h
  - /home/jichao/dms/source/utils/track.cpp
  - 1401fc338107f05b9cf
  - feat/ljc/track_0615
  - 02_Projects/DMS/04_Tracking/head-first跟踪方案.md
  - 02_Projects/DMS/04_Tracking/tracking_overview_current.md
  - 02_Projects/DMS/04_Tracking/tracking_design_current.md
  - 02_Projects/DMS/04_Tracking/tracking_spec_current.md
  - 02_Projects/DMS/04_Tracking/tracking_implementation_current.md
  - 02_Projects/DMS/04_Tracking/tracking_validation_current.md
  - 90_Archive/02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack深模块重新评审与CleanRefactor规划-2026-06-15.md
  - 90_Archive/02_Projects/DMS/04_Tracking/Current Maintenance Records/Tracking方案优化与历史实现归档记录-2026-06-16.md
risks:
  - 本记录基于代码静态对比和设计评审；未执行 runtime replay、单元测试或板端验证。
  - 当前分支已有 Body global assignment、Hand global slot assignment 和 independent lifecycle 小步代码事实，但这些不再作为默认推荐路线。
  - 2m/5m 业务分流仍需后续实现和验证。
updated_at: 2026-06-16
---

# 1 结论摘要

对比 `1401fc338107f05b9cf` 与当前 `feat/ljc/track_0615` 后，新的推荐路线应收缩，而不是继续扩展统一 assignment 和独立 lifecycle。

已由代码证实：

- `include/utils/track.h` 从 `1401fc338107f05b9cf` 到当前分支未变化。
- public API 仍只有 `DmsTrack::Init()` 和 `DmsTrack::Update()`，调用方不需要编排 face/body/hand 内部步骤。
- 当前分支架构漂移集中在 `source/utils/track.cpp`。
- 当前分支在 `1401fc338107f05b9cf` 基础上依次叠加：
  - `.cpp` internal `SolveAssignment`
  - Body owner-to-detection global assignment
  - Hand global slot assignment
  - tracking-first / acquisition fallback
  - Body/Hand independent lifecycle 小步

设计判断：

- `DmsTrack` 外部接口已是深接口；问题不在 public API。
- 当前分支从 clean refactor 进入了行为扩张链：为修复一个 assignment 行为变化，引入更多 lifecycle 和 cleanup 约束。
- `1401fc338107f05b9cf` 更适合作为后续方案的稳定骨架：face-first identity、driver face-bound evidence、body/hand 不反向创建 identity。
- 当前推荐路线应收缩为：
  - face/head 是唯一 identity 主线；
  - 2m 默认 face/head-only；
  - 5m 在 driver face/head 选定后，只做 driver-bound body/hand evidence；
  - face missing 时优先报 face occlusion；
  - body/hand 只允许 bounded evidence cache，不默认完整 independent lifecycle。

# 2 基线与当前分支对比

| 维度 | `1401fc338107f05b9cf` 基线 | `feat/ljc/track_0615` 当前分支 | 结论 |
|---|---|---|---|
| public API | `Init/Update` | 未变 | API 已足够深 |
| header surface | phase-level private 方法和长期状态 | 未变 | 不需要改 header |
| Face matching | 手写 expanded Hungarian matrix | `SolveAssignment` 包装 | 可保留为 `.cpp` internal 工具 |
| Body owner 集合 | live face owners | live face owners + existing body owners | 当前分支引入 identity-like lifecycle 风险 |
| Body assignment | owner 顺序遍历，driver face 优先，`usedDetections` 防抢占 | owner-to-detection global assignment | 对 driver-only 目标过宽 |
| Face missing 时 Body | face owner 不存在则 body retire | body 可继续内部 tracking-only | 应收缩为 bounded cache |
| Hand owner | 当前已发布 DRIVER body owner | published owner + internal DRIVER body owner | 当前分支引入双层语义 |
| Hand assignment | per-owner left/right + owner-gated second pass | global slot assignment | 对 driver-only 目标过宽 |
| 输出 | face/body evidence gated | 仍 face/body evidence gated | 输出主线没变，内部复杂度增加 |
| 2m/5m | 无显式第一层分流 | 仍无显式第一层分流 | 应优先补分流 |

# 3 深模块判断

`DmsTrack` 是外部深、内部需要收敛的模块：

- public API 少且表达高层意图；
- 调用方不承担 solver、owner、slot、lifecycle、cleanup 的拼装；
- 后续不应新增 public API；
- private header 不应新增 row/view/payload/result/context；
- 内部实现应以 phase-level 语义表达，而不是把 solver row、edge mode 和 lifecycle sweep 变成稳定概念。

`SolveAssignment` 可保留，但只能作为 `.cpp` internal 薄工具：

- 允许职责：expanded matrix、dummy edge、forbidden edge、strict `< dummyLoss`、结果解析；
- 不允许职责：Body 四态 edge、Reacquire cost band、lifecycle policy、owner migration、统一架构目标。

# 4 推荐后续主线

推荐主线：

```text
1401fc338107f05b9cf 稳定骨架
  -> 可选保留 Face solver 等价迁移
  -> 增加 2m/5m 第一层分流
  -> 2m face/head-only
  -> 5m driver face/head selected
  -> driver-bound body evidence
  -> driver-bound left/right hand evidence
  -> face missing 时优先 face occlusion
  -> body/hand 只做 bounded evidence cache
```

不再作为默认路线：

- Body multi-owner global assignment；
- Hand cross-owner global slot assignment；
- Body/Hand 完整 independent lifecycle；
- Body Track/Reacquire/Bootstrap/Forbidden 四态 edge；
- Reacquire cost band；
- Hand Reacquire；
- 通过 orphan/retired anchor 继续补救 identity-like lifecycle。

# 5 分阶段计划

| 阶段 | 范围 | 保持条件 | 验证 | 停止条件 |
|---|---|---|---|---|
| 0 路线冻结 | 停止继续扩展 `feat/ljc/track_0615` 的 assignment/lifecycle 规则 | 不新增 Row/View/Payload/Edge 类型 | 代码静态对比 | 需要新增类型才能解释方案 |
| 1 Face 等价迁移 | 可从 `1401fc` 或 `460c54ef` clean branch 开始 | 只影响 Face solver 表达 | Face diff、编译 | Face 输出无法证明等价 |
| 2 2m/5m 分流 | 先判定是否启用 body/hand | 2m 不输出陈旧 body/hand | 2m 样例 | 分流条件不清 |
| 3 5m Body evidence | selected driver face -> best body evidence | body 不反向影响 identity | driver body 样例 | 需要多 owner 竞争 |
| 4 5m Hand evidence | driver body -> left/right hand evidence | hand 不迁移 owner | 左右手样例 | 需要跨 owner hand |
| 5 Bounded cache | face miss 时 body/hand 只短期保留，不发布 identity | face occlusion 优先 | face 短遮挡/恢复/id reuse | cache 变成独立 lifecycle |
| 6 复杂链路重启评审 | 仅评估是否需要 global assignment/Reacquire | 有 replay、loss 分布和冲突样例 | diff 白名单 | 缺少运行证据 |

# 6 抽象必要性审计

当前方案不要求新增类型。

| 候选类型或抽象 | 结论 | 替代方案 | 重新评估条件 |
|---|---|---|---|
| `SolveAssignment` | 保留 `.cpp` internal | 直接调用 Hungarian 也可 | 多处重复 expanded matrix 且等价可验证 |
| `BodyAssignmentRow` | 不新增 | driver-only 局部变量 | 明确多 owner body 需求 |
| `BodyEdgeMode` | 暂缓 | 局部 if/成本判断 | replay 证明 Reacquire 必需 |
| `HandAssignmentRow` | 仅函数局部 | owner 下 left/right 局部处理 | 确认 cross-owner hand 是业务目标 |
| `AssignmentResult` | 暂不提升 | `std::vector<int>` / 局部结果 | 多处稳定复用且减少错误 |
| `FrameBodyView` | 暂不作为稳定类型 | `TrackInfo`、局部 map/vector | 需要承载新不变量 |
| `LifecycleContext/Payload` | 不新增 | 现有状态 + 局部变量 | 不适用 |

# 7 写回决策

本记录替代 2026-06-15/2026-06-16 的扩张路线作为当前推荐路线。

以下记录已归档为历史实验路线，不再作为默认阅读入口：

- `90_Archive/02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack深模块重新评审与CleanRefactor规划-2026-06-15.md`
- `90_Archive/02_Projects/DMS/04_Tracking/Current Maintenance Records/Tracking方案优化与历史实现归档记录-2026-06-16.md`

归档含义：

- 保留历史可追溯性；
- 不否认其中记录的当时代码事实；
- 但其“统一 assignment + independent lifecycle + Reacquire”路线不再作为当前推荐方案。

# 8 未闭合项

- 未执行 runtime replay。
- 未新增单元测试。
- 未执行板端验证。
- 2m/5m profile 分流尚未实现。
- face occlusion 输出语义仍需与下游确认。
- 若未来重启 Body/Hand global assignment，必须另行立项并补运行证据。
