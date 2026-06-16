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
- `track.h` 本身未变，因此当前问题不是 public API 设计失败，而是 `.cpp` 内部行为扩张和 private surface 认知接口过宽。

设计判断：

- `DmsTrack` 外部接口已是深接口；问题不在 public API。
- 当前分支从 clean refactor 进入了行为扩张链：为修复一个 assignment 行为变化，引入更多 lifecycle 和 cleanup 约束。
- `1401fc338107f05b9cf` 更适合作为后续方案的稳定骨架：face-first identity、driver face-bound evidence、body/hand 不反向创建 identity。
- 当前推荐路线应收缩为：
  - face/head 是唯一 identity 主线；
  - 2m 默认 face/head-only；
  - 5m 在 driver face/head 选定后，只做 driver-bound body/hand evidence；
  - body/hand 只允许 bounded evidence cache，不默认完整 independent lifecycle。
- face occlusion 下游已有接口和判断逻辑，track 内部不需要新增 face occlusion 业务分支。
- 组织架构也应回到 `1401fc338107f05b9cf` 的 private surface：保留 phase-level 方法，不再把 step helper 树、row/view/payload/result/edge mode 提升为 header 认知接口。

# 2 基线与当前分支对比

| 维度 | `1401fc338107f05b9cf` 基线 | `feat/ljc/track_0615` 当前分支 | 结论 |
|---|---|---|---|
| public API | `Init/Update` | 未变 | API 已足够深 |
| header surface | phase-level private 方法和长期状态 | 未变 | 不需要改 header |
| Face matching | 手写 expanded Hungarian matrix | `SolveAssignment` 包装 | 可保留或删除；不作为目标 |
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
- 这次路线收缩的重点不是“再找一个更大的抽象”，而是停止把单帧临时概念和 step 脚本继续固化到 header/private surface。

`SolveAssignment` 不作为必须保留项。若后续 clean branch 中只有 Face 使用该 helper，且直接调用 Hungarian 更清晰，则允许删除；若保留，只能作为 `.cpp` internal 薄工具：

- 允许职责：expanded matrix、dummy edge、forbidden edge、strict `< dummyLoss`、结果解析；
- 不允许职责：Body 四态 edge、Reacquire cost band、lifecycle policy、owner migration、统一架构目标。

# 4 主分支接口与组织架构优化

`1401fc338107f05b9cf` 的组织骨架比当前分支更适合作为后续实现基底。它的价值不只是行为更保守，也在于接口和抽象层级更清晰。

### 4.1.1 Public API

主分支 public API 只有：

- `DmsTrack::Init()`
- `DmsTrack::Update(...)`

这两个接口已经隐藏配置读取、状态初始化、face/body/hand 更新、driver 选择、legacy map 输出和清理逻辑。后续不应为了 2m/5m、body evidence 或 hand evidence 新增 public phase API；profile 分流和 evidence 策略应留在 `Update()` 内部。

### 4.1.2 Private Header Surface

主分支 `track.h` private surface 保留的是长期状态与 phase-level 方法：

- 长期状态：`m_bodyTracks`、`m_retiredBodyTracks`、`m_faceTracks`、`m_handTracks`
- 配置与基础能力：`loadConfigFromJson`、`allocateFaceTrackId`、`computeMatchLoss`、ROI/类型判定
- phase-level 方法：`updateFaceTracks`、`selectDriverFace`、`updateBodyTracks`、`updateHandTracks`

该结构应作为后续组织架构基线。不要把实现拆成 `solve/apply/advance/finalize/project/publish` 全套 private member 脚本，也不要把 solver row、edge mode、snapshot、eligibility 或 lifecycle context 放进 header。

### 4.1.3 `.cpp` Internal 与函数局部边界

后续内部机制按最低必要可见性放置：

| 机制                            | 建议位置                                       | 理由                                |
| ----------------------------- | ------------------------------------------ | --------------------------------- |
| Hungarian / `SolveAssignment` | `.cpp` anonymous namespace 或直接调用 Hungarian | 算法工具，不是 DmsTrack 状态契约；helper 可删可留 |
| Face/Body/Hand cost evaluator | phase 函数局部 lambda 或 `.cpp` helper          | 只服务当前 phase，不应进 header            |
| Hand slot row/key             | 函数局部                                       | 单帧 solver 解释器，不承载长期不变量            |
| Body finalized snapshot       | 局部 map/vector 或 `.cpp` internal            | 只用于同帧 hand/publish，不跨帧保存          |
| Profile 分流结果                  | 局部变量或轻量 private helper                     | 已有 public API 或稳定类型               |
| Bounded cache cleanup         | phase 内部逻辑                                 | 不新增 lifecycle context/payload     |

### 4.1.4 推荐内部流程

组织结构上建议保持一个清晰的 phase-level 主流程：

```text
Update
  -> clear legacy maps
  -> updateFaceTracks
  -> selectDriverFace
  -> publish face/head
  -> updateBodyTracks only when profile enables driver body evidence
  -> updateHandTracks only when profile enables driver hand evidence
```

`updateBodyTracks` 内部应表达一个完整领域动作，而不是暴露多个 step helper：

```text
driver face evidence
  -> choose/update driver-bound body evidence
  -> age or clear bounded body cache
  -> publish compatible body map if allowed
```

`updateHandTracks` 同理：

```text
driver body evidence
  -> update left/right slots for driver only
  -> age or clear bounded hand cache
  -> publish compatible hand maps if allowed
```

### 4.1.5 抽象取舍

组织架构优化的核心不是增加类型，而是减少跨层传播的临时概念。

应保留或允许：

- `TrackInfo` 作为已有轨迹状态载体；
- `TrackParameters` / `TrackThresholds` 作为配置载体；
- `HandTrackState` / `HandSideState` 作为长期 hand slot 状态；
- `.cpp` internal `SolveAssignment` 作为薄工具。

应拒绝或暂缓：

- header-level `FrameBodyView`
- header-level `HandAssignmentRow`
- `AssignmentResult` 作为稳定跨 phase 契约
- `BodyEdgeMode`
- `LifecycleContext` / `Payload` / `Eligibility`
- 为 2m/5m profile 新增 public 或半 public 类型

只有当未来出现真实的新不变量、独立生命周期、跨 phase 稳定复用或独立测试边界时，才重新做抽象必要性审计。

### 4.1.6 Phase 内部三段式约束

后续实现不再通过新增 Row/View/Context/Result 类型解决层次混杂，而是在每个 phase 内部区分三段：

- frame-local computation：只处理当前帧输入、候选集、loss、assignment、profile 判断和输出资格判断；其结果不得跨帧保存，不得提升为 header 类型。
- persistent state transition：唯一允许修改 `m_faceTracks`、`m_bodyTracks`、`m_handTracks`、`m_retiredBodyTracks`、`motionState`、`hitCount`、`missCount` 和 cleanup 的阶段。
- output projection：只读取已完成状态并写 legacy maps；除 sanitize 明确归属于 finalize 外，publish 不得推进 hit/miss、retire、reset 或 owner migration。

bounded cache 只允许短期保留 box、motion state、hit/miss，用于 face 恢复后的平滑；不得发布为有效 body/hand，不得 acquisition/bootstrap，不得 owner migration，不得反向影响 driver identity。

# 5 推荐后续主线

推荐主线：

```text
1401fc338107f05b9cf 稳定骨架
  -> 可选保留 Face solver 等价迁移
  -> 增加 2m/5m 第一层分流
  -> 2m face/head-only
  -> 5m driver face/head selected
  -> driver-bound body evidence
  -> driver-bound left/right hand evidence
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

# 6 分阶段计划

| 阶段 | 范围 | 保持条件 | 验证 | 停止条件 |
|---|---|---|---|---|
| 0 路线冻结 | 停止继续扩展 `feat/ljc/track_0615` 的 assignment/lifecycle 规则 | 不新增 Row/View/Payload/Edge 类型 | 代码静态对比 | 需要新增类型才能解释方案 |
| 1 组织骨架回归 | 保持主分支 `track.h` private surface 和 phase-level 方法 | 不新增 private step helper 脚本 | header diff、代码审查 | 需要新增跨 phase Row/View/Payload |
| 2 Face 等价迁移 | 可从 `1401fc` 或 `460c54ef` clean branch 开始 | 只影响 Face solver 表达 | Face diff、编译 | Face 输出无法证明等价 |
| 3 2m/5m 分流 | 从 `track_params.json` 车型配置判定是否启用 body/hand | 2m 不输出陈旧 body/hand | 2m 样例 | 分流条件不清 |
| 4 5m Body evidence | selected driver face -> best body evidence | body 不反向影响 identity | driver body 样例 | 需要多 owner 竞争 |
| 5 5m Hand evidence | driver body -> left/right hand evidence | hand 不迁移 owner | 左右手样例 | 需要跨 owner hand |
| 6 Bounded cache | face miss 时 body/hand 只短期保留 box/motion/hit/miss，不发布有效 body/hand | 不 acquisition/bootstrap/迁移 owner | face 短遮挡/恢复/id reuse | cache 变成独立 lifecycle |
| 7 复杂链路重启评审 | 仅评估是否需要 global assignment/Reacquire | 有 replay、loss 分布和冲突样例 | diff 白名单 | 缺少运行证据 |

# 7 抽象必要性审计

当前方案不要求新增类型。

| 候选类型或抽象 | 结论 | 替代方案 | 重新评估条件 |
|---|---|---|---|
| `SolveAssignment` | 可保留也可删除 | 直接调用 Hungarian 也可 | 多处重复 expanded matrix 且 helper 更清晰 |
| `BodyAssignmentRow` | 不新增 | driver-only 局部变量 | 明确多 owner body 需求 |
| `BodyEdgeMode` | 暂缓 | 局部 if/成本判断 | replay 证明 Reacquire 必需 |
| `HandAssignmentRow` | 仅函数局部 | owner 下 left/right 局部处理 | 确认 cross-owner hand 是业务目标 |
| `AssignmentResult` | 暂不提升 | `std::vector<int>` / 局部结果 | 多处稳定复用且减少错误 |
| `FrameBodyView` | 暂不作为稳定类型 | `TrackInfo`、局部 map/vector | 需要承载新不变量 |
| `LifecycleContext/Payload` | 不新增 | 现有状态 + 局部变量 | 不适用 |

# 8 写回决策

本记录替代 2026-06-15/2026-06-16 的扩张路线作为当前推荐路线。

以下记录已归档为历史实验路线，不再作为默认阅读入口：

- `90_Archive/02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack深模块重新评审与CleanRefactor规划-2026-06-15.md`
- `90_Archive/02_Projects/DMS/04_Tracking/Current Maintenance Records/Tracking方案优化与历史实现归档记录-2026-06-16.md`

归档含义：

- 保留历史可追溯性；
- 不否认其中记录的当时代码事实；
- 但其“统一 assignment + independent lifecycle + Reacquire”路线不再作为当前推荐方案。

# 9 未闭合项

- 未执行 runtime replay。
- 未新增单元测试。
- 未执行板端验证。
- 2m/5m profile 分流尚未实现。
- face occlusion 已由下游接口和逻辑判断处理，track 内部不新增对应业务分支。
- 组织架构回归仍需在后续代码实现中验证：`track.h` 不新增 step-level helper，不新增跨 phase row/view/payload/result。
- 若未来重启 Body/Hand global assignment，必须另行立项并补运行证据。
