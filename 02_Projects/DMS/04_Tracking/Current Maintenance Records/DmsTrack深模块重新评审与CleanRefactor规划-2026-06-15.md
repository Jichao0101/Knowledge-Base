---
title: DmsTrack 深模块重新评审与 Clean Refactor 规划
summary: 对 feat/ljc/track_0609 与 br_develop_forJ6b 的 track.h/track.cpp 进行深模块评审并执行 clean refactor 前两步；结论为停止在实验分支继续叠加结构重构，从稳定基线新开 clean branch，已完成 Face 等价 solver 与 Body 全局 assignment；2026-06-16 补充吸收 Body 四态 edge、body/hand 独立生命周期和 head-first 方案整理要求。
status: reviewed
doc_role: review_record
truth_role: project_review
scope: DmsTrack public/private API、body/hand phase 边界、assignment 抽象、生命周期与 clean refactor 规划，以及 2026-06-15 clean branch 阶段 1/2 实施回写；不包含板端验证。
sources:
  - /home/jichao/dms/include/utils/track.h
  - /home/jichao/dms/source/utils/track.cpp
  - br_develop_forJ6b
  - feat/ljc/track_0609
  - 02_Projects/DMS/04_Tracking/tracking_overview_current.md
  - 02_Projects/DMS/04_Tracking/tracking_design_current.md
  - 02_Projects/DMS/04_Tracking/tracking_spec_current.md
  - 02_Projects/DMS/04_Tracking/tracking_implementation_current.md
  - 02_Projects/DMS/04_Tracking/tracking_validation_current.md
risks:
  - 阶段 1/2 已执行 QNX `Utils` 与 `sdk` 构建，但未执行 runtime replay、单元测试或板端验证。
  - Body/Hand 全局 assignment 已作为目标行为落地；在 loss 完成场景标定前，已有 body track 和 initialized hand slot 只接受可靠 tracking edge，tracking 不可靠则 miss，不启用 acquisition fallback 重新绑定。acquisition 仅用于新 body owner 或未初始化 hand slot。
  - 2026-06-16 方案层新增 Body Reacquire 目标，但当前代码尚未验证；不得把四态 edge 视为已闭环实现。
  - Hand owner 消失后的 hand lifecycle 仍需专项实现与验证。
updated_at: 2026-06-16
---

# 1 结论摘要

## 1.1 已由代码证实

- `DmsTrack` public API 在稳定基线和实验分支均只有 `Init()`、`Update()`；调用方不需要编排 face/body/hand 内部步骤。
- 实验分支 private header 从基线的少量 phase-level 方法扩张为完整的 solve/apply/advance/finalize/project/publish 执行脚本。
- `1237f6c6` 将稳定基线的 driver-first、逐 owner greedy body matching 改为全局 Hungarian；这是算法行为变化。
- 稳定基线 Face 已使用全局 Hungarian；实验分支将相同的 expanded matrix、dummy edge 和 strict `< dummyLoss` 语义提炼为通用 solver。
- 实验分支 Hand 已从 owner 内 first/second pass 改为跨 owner、跨左右 slot 的单次全局 assignment。
- `FrameBodyView`、`HandSlotKey`、`HandAssignmentRow` 都是单帧中间表示，却被放入 private header。
- `AssignmentResult` 仅为 solver index 结果，但因 step helper 签名而前置声明到 namespace header。
- 当前 hand miss 只推进本帧 allowed owner 对应的 assignment rows；owner 消失后，已初始化 slot 可能不再推进 miss，空 owner state 也无法删除。
- 稳定基线已包含与实验分支 `3f7d35a8` patch-equivalent 的 driver recognition 修复，不应重复 cherry-pick。

## 1.2 设计判断

- 当前模块是“外部接口深、内部组织浅”的混合模块。
- 主要问题不是 public API，而是 private header surface 和内部阶段边界。
- `feat/ljc/track_0609` 已进入补救式重构：宽拆分后连续追加 sentinel、状态、语义和抽象删除修补。
- 不建议继续在该分支叠加结构改动；建议从 `br_develop_forJ6b` 新开 clean branch。
- 当前分支作为统一 solver、Body cost 和 Hand slot row 的算法参考，同时作为过宽 private surface 的结构反例；不作为 clean refactor 的直接基底。
- Face/Body/Hand 统一的是 assignment 求解机制，不是强制统一 row 方向、领域 gating、cost 解释或 lifecycle。
- Body 全局 Hungarian 和 Hand 全局 slot assignment 是本次明确目标，必须作为有意行为变更分阶段实现，而非继续附着在可读性重构中。

## 1.3 尚需验证

- Body tracking cost、acquisition cost、driver priority 与 `dummyLoss` 是否处于可比较尺度。
- Face 接入通用 solver 后，在 tie 和遍历顺序场景是否保持稳定基线行为。
- body owner 消失后 hand 应立即清理、按 missThreshold 延迟清理，还是保留其他 bounded grace period。
- 除明确允许的 Body/Hand assignment delta 外，clean branch 是否与稳定基线保持逐帧输出等价。

# 2 当前分支是否建议继续

**结论：停止继续结构重构。**

理由：

1. private header 声明数由约 21 增至约 67，复杂性主要从长函数转移到更多 helper 和中间类型。
2. 9 个主要提交同时混合结构、算法、sentinel、状态和 driver 行为修复。
3. 后续提交反复新增、重命名和删除 assignment wrapper，说明抽象边界未稳定。
4. 缺少 tracker 专项行为测试，无法安全证明多轮结构变化等价。
5. 已发现 global assignment 和 orphan hand lifecycle 两个不能按“可读性优化”处理的高风险事项；前者现已确认是目标行为，后者仍是必须先闭合的生命周期缺口。

# 3 Public API 深浅判断

| API | 高层意图 | 是否暴露内部步骤 | 判断 |
|---|---|---|---|
| `DmsTrack::Init()` | 加载配置并初始化 tracker | 否 | 深接口，保留 |
| `DmsTrack::Update()` | 完成单帧全部跟踪状态更新与结果发布 | 否 | 深接口，保留 |

Public API 已足够深，不建议改变。调用方只表达“初始化”和“更新一帧”，没有承担 assignment、lifecycle、finalize 或 publish 编排。

# 4 Private Header Surface 审计

## 4.1 事实

- 稳定基线 private section 主要保留长期状态、配置加载、基础判定和 face/body/hand phase-level 方法。
- 实验分支 body 暴露 collect/predict/solve/apply/advance/finalize/project/publish。
- 实验分支 hand 暴露 collect/allowed/predict/build row/solve/apply/advance/cleanup/reset/erase/finalize/publish。
- 这些 helper 由唯一上层方法按固定顺序调用，参数高度重叠，且多数没有独立复用、失败边界或替换点。

## 4.2 判断

private header 已成为执行脚本目录，而不是稳定内部契约。建议 header 只保留：

- 长期状态字段；
- `loadConfigFromJson`、`allocateFaceTrackId` 等稳定成员职责；
- `updateFaceTracks`、`selectDriverFace`、`updateBodyTracks`、`updateHandTracks` 等 phase-level 方法；
- 只有确实跨 phase 且承载稳定契约的最小类型。

其余 pure helper、solver、row、临时 key 和单帧中间结构应降级到 `.cpp` anonymous namespace、函数局部 struct 或 lambda。

# 5 当前低收益抽象清单

- `AssignmentResult` 的 header 前置声明。
- `HandSlotKey` 作为 private header 类型。
- `HandAssignmentRow` 作为 private header 类型。
- `FrameBodyView` 的 `View` 命名和 header 可见性。
- 已删除的 `AssignmentPolicyMatrix`、`AssignmentCandidate`、`AssignmentRejection`。
- solve/apply/advance/finalize/project/publish 全套 step-level member methods。
- 历史 `publishAllowedHandSlots` 及其 eligibility 搬运结构。

# 6 候选抽象必要性审计表

| 抽象 | 是否承载新不变量/生命周期 | 结论 | 最低必要可见性 | 替代方案 |
|---|---|---|---|---|
| `FrameBodyView` | 仅表达本帧已 finalize 的 body snapshot；不拥有状态 | 降级，且不应叫 View | 函数局部或 `.cpp` internal | 局部 finalized body map；`const std::map<track_id, TrackInfo>`；局部 snapshot vector |
| `HandSlotKey` | 只组合 owner id 与左右标志 | 降级或删除 | 函数局部 | `std::pair<track_id, HandSide>`；局部索引；若保留使用 enum 而非 `bool isRight` |
| `HandAssignmentRow` | 不承载稳定领域不变量，混合 solver index、状态指针、body snapshot 指针 | 删除 header 版本 | 函数局部 | 局部 row struct/lambda；直接按稳定 row 顺序解释 |
| `AssignmentResult` | 隐藏 expanded Hungarian dummy 细节，且 Face/Body/Hand 均需要解释 unmatched detection | 保留最小版本并降级 | `.cpp` anonymous namespace | `rightByLeft` + 必要的 `unmatchedRight`；不保留 match object、unmatchedLeft 和无消费方的 cost |
| `AssignmentPolicyMatrix` | 无独立策略生命周期，主要搬运矩阵 | 删除 | 无 | evaluator + 局部 matrix |
| `AssignmentCandidate` | 单边候选搬运 | 删除 | 无 | 局部变量或直接 evaluator |
| `AssignmentRejection` | 仅服务诊断分类 | 删除 | 无 | 必要时局部计数/日志，不进入结构契约 |
| `publishAllowedHandSlots` | 将 finalize、sanitize、lifecycle 和 publish 混合 | 用职责更深的 hand phase 替代 | private phase-level 或 `.cpp` local | finalize 内负责状态副作用，publish 只写 output |

## 6.1 `FrameBodyView` 结论

它解决的真实问题是：hand 不应把 caller-owned legacy output map 当作内部可变事实源。这个问题成立，但不证明需要一个 header-level `View` 类型。

优先方案：

1. body phase 在局部形成 finalized body map/snapshot；
2. 将其以 `const` 引用传给 hand phase；
3. 同一份 finalized 表示再投影到 legacy body output；
4. 类型仅在 `.cpp` 或函数局部存在。

若只需要 `track_id -> TrackInfo`，直接复用 `std::map<track_id, TrackInfo>` 更清楚。只有未来 snapshot 承载额外且必须一致维护的不变量时，才重新审计专用类型。

## 6.2 `HandSlotKey` 结论

`ownerFaceId + bool isRight` 没有形成足够深的领域对象。若局部 set 查重确实需要 key，可局部保留；若保留，建议用 `enum class HandSide { Left, Right }` 表达方向，避免裸 bool。但本次 clean refactor 不应以新增 enum 为前置条件。

## 6.3 `HandAssignmentRow` 结论

它只是单帧 solver row 解释器，应移出 header。该结构同时携带：

- solver row identity；
- persistent mutable slot pointer；
- frame snapshot pointer；
- left/right 方向。

这不是稳定跨 phase 契约，而是局部算法实现细节。

## 6.4 `AssignmentResult` 结论

统一 solver 需要隐藏 expanded Hungarian 的 dummy 行列和 forbidden edge 解析，Face 又需要未匹配 detection 用于 bootstrap，因此一个最小 `.cpp` internal result 有实际收益。建议只保留 `rightByLeft[left] = right/-1` 和必要的 `unmatchedRight`；`unmatchedLeft` 可由 `-1` 直接表达，match object 与 cost 不应成为稳定结果契约。

# 7 Body 层级问题与建议接口

## 7.1 当前问题

- `updateBodyTracks` 内部流程被完整复制到 header。
- global Hungarian 是明确目标，但改变了稳定基线的 driver-first greedy ownership，必须用目标冲突样例和 delta 白名单验证。
- finalize、projection、publish 的 side-effect 边界虽有价值，但不需要全部成为 member API。
- header 注释仍提到 greedy ownership，而实现已是 global Hungarian，形成事实矛盾。

## 7.2 Assignment 设计

- Body 左侧实体为当前 face/body owner，右侧实体为本帧 body detections。
- 每条边由 body phase evaluator 决定；solver 不理解 driver、tracking 或 acquisition。
- 已有 body owner 在同一全局矩阵中同时计算 tracking cost 与 geometry acquisition cost，但 evaluator 必须保留层级：tracking loss 低于可靠门槛时优先延续已有 body track；在 loss 完成标定前，已有 body owner 的 tracking 不可靠时不允许 acquisition fallback，直接走 miss。acquisition 只用于新 owner 首次绑定。
- driver priority 必须显式编码在 gating/cost 中；owner 遍历顺序只能作为确定性 tie-break，不能替代优先级契约。
- 必须确认 tracking loss、acquisition loss、driver bonus/bias 与 `dummyLoss` 的量纲和有效区间。否则两类错误都会发生：错误但低于门槛的 tracking edge 会延续错误 track；若未来打开 initialized fallback，过宽或未标定的 acquisition edge 也可能把 owner 绑定到其他人的 body。

## 7.3 建议接口

推荐 private header 只保留：

```text
updateBodyStateFromDetections(...)
finalizeBodyStateForFrame(...)
```

也可以进一步只保留一个：

```text
updateBodyTracks(...)
```

由该 phase 内部完成：

```text
collect -> predict -> match -> apply -> advance/retire -> finalize
```

finalized body snapshot 作为局部结果交给 hand 与 legacy publish。`publish` 只写 output；所有 sanitize 和 lifecycle side effect 必须在 finalize 结束。

# 8 Hand 层级问题与建议接口

## 8.1 当前问题

- header 暴露完整 hand 执行脚本。
- row/key/result 主要服务单个调用链。
- 只有 allowed owners 进入 row 并推进 miss，owner 消失后的 initialized slots 可能长期悬挂。
- left-before-right 是行为不变量，但当前通过 row 构造细节隐式维持。

## 8.2 Assignment 与 Lifecycle 设计

- Hand 左侧实体为当前 eligible owners 的 hand slots，右侧实体为本帧 hand detections。
- 每个 owner 固定按 left-before-right 构造 slot；该顺序必须进入测试，不依赖注释保证。
- initialized slot 使用 prediction match cost，uninitialized slot 使用 owner body anchor acquisition cost；owner/body gating 属于 hand evaluator。
- assignment candidate rows 与 lifecycle sweep 必须分离：未进入本帧候选 rows 的 initialized slot 仍需按明确策略推进 miss、reset 或 cleanup。
- publish 只能读取 finalized slot state；不得用 publish eligibility 反向定义 assignment 或 lifecycle 候选域。

## 8.3 建议接口

推荐 private header 只保留：

```text
updateHandSlotStateFromDetections(...)
finalizeHandStateForFrame(...)
```

或只保留：

```text
updateHandTracks(...)
```

phase 内部必须显式拥有：

- owner eligibility；
- left-before-right 顺序；
- assignment；
- matched/unmatched lifecycle；
- owner 消失时的 bounded cleanup；
- retired-owner handoff；
- sanitize/finalize；
- pure publish。

`publishHandTracks` 若保留为 helper，只允许读取 finalized state 并写 output，不得推进 hit/miss、reset、erase 或 sanitize。

# 9 当前分支可 Cherry-Pick 的改动类型

**不建议整提交 cherry-pick。**

可选择性重做的行为：

- `1237f6c6` 中通用 solver 的 expanded matrix、有限 forbidden cost、dummy edge 与 strict `< dummyLoss` 语义。
- `1237f6c6` 中 Body 全局 owner-to-detection assignment 的 cost evaluator 思路。
- `1237f6c6` 及后续提交中 Hand 全局 slot-to-detection assignment 与 left-before-right row 顺序。
- `d72a75be` 中“sanitize 失败只对本帧已命中项推进 miss”的语义。
- `d72a75be`/`dc475f00` 中 finalize 负责状态副作用、publish 只写 output 的边界。
- `4155bfde` 中“不使用 caller-owned legacy output map 作为 body -> hand 内部事实源”的目标。

不需要 cherry-pick：

- `3f7d35a8` driver recognition 修复，稳定基线已有 patch-equivalent 提交 `bcdbe8e5`。

# 10 应丢弃或重做的改动类型

- `804ff0f1`、`76490b4d` 引入的 step-level helper 展开。
- `1237f6c6` 及后续提交的算法实现不得整提交 cherry-pick；应在 clean branch 按独立阶段重做并保留可审计的行为 delta。
- `41abae61` 中与 helper 展开混合的 sentinel/生命周期结构。
- `88620616`、`dc475f00` 继续围绕既有 step tree 的包装删除与重命名。
- header-level `FrameBodyView`、`HandSlotKey`、`HandAssignmentRow`、`AssignmentResult`。
- `AssignmentPolicyMatrix`、`AssignmentCandidate`、`AssignmentRejection`。
- 任何为保持上述抽象而增加的解释层或长注释。

# 11 Clean Refactor 分阶段计划

| 阶段 | 要做 | 不做 | 验证方式 | 停止条件 |
|---|---|---|---|---|
| 0 契约与行为基线 | 从 `br_develop_forJ6b` 新开分支；记录 SHA、配置、关键序列逐帧输出；明确 Face 等价、Body/Hand 有意 delta | 不重构、不搬实验分支结构 | map key/box/type、driver id、hit/miss、左右顺序快照与 delta 白名单 | 无法定义 Body/Hand 冲突场景期望或缺少可重放输入 |
| 1 Face 驱动 solver 落地 | 从现有 Face Hungarian 提取 `.cpp` internal 通用 solver；保持 Face 原有 row 方向和行为 | 不改 Body/Hand，不强制三 phase row 同向，不引入 header result | 空/矩形/tie/forbidden/NaN/Inf、strict `< dummyLoss`、逐帧 Face 等价 | Face 出现非预期差异或 solver 契约需要领域知识 |
| 2 Body 全局 assignment | 以 owner 对 detection 的全局矩阵替代逐 owner greedy；显式实现 tracking/acquisition/driver cost | 不同时改 Hand、finalize/publish 或 public API | greedy/global 冲突样例、driver 竞争、reacquisition、cost scale、runtime diff 白名单 | ownership 期望不明确、cost 尺度不可解释或非目标输出漂移 |
| 3 Hand 全局 slot assignment | 以所有 eligible left/right slots 对 detections 的全局矩阵替代 owner 内 two-pass | 不把 eligibility 当 lifecycle，不新增 header row/key | 跨 owner 竞争、左右交叉、initialized/acquisition、tie、left-before-right | slot identity、side 或 owner 绑定出现不可解释变化 |
| 4 Hand lifecycle 闭环 | 独立 sweep 所有 initialized slots；明确 owner 消失后的 miss/reset/cleanup；重做 matched-only sanitize miss | 不在 publish 中推进状态 | face/body 消失、120+ owner turnover、retired anchor、每帧最多一次 hit/miss | grace policy 不明确、ID 泄漏或重复推进仍存在 |
| 5 Phase 与表示收敛 | 收敛 face/body/hand phase-level member；solver/evaluator/row/result/snapshot 留 `.cpp`；finalize 有副作用、publish pure | 不新增 View/Payload/Context 到 header，不改变目标算法 | header surface 对比、side-effect tests、normalized replay | private header 仍暴露固定步骤脚本或局部类型缺乏收益 |
| 6 集成验证 | 本地构建、专项测试、runtime replay、独立 review；后续板端验证 | 不用编译代替行为验证 | 非白名单 frame diff、代表性视频、J6B 验证 | 任一非目标行为差异 |

# 12 风险分级

## 12.1 低风险结构整理

- pure geometry/cost helper 移入 `.cpp`。
- 单函数局部 alias、lambda、临时容器。
- private header 删除单帧临时类型和唯一调用 step helper。
- 在行为快照保护下合并固定顺序 helper。

## 12.2 中风险边界重组

- finalize 与 publish 副作用边界调整。
- body finalized snapshot 不再经 legacy output map 回流。
- owner 消失后的 hand lifecycle 明确化。
- phase-level helper 收敛和内部状态访问重排。

## 12.3 高风险行为或契约变更

- greedy body ownership 改 global Hungarian，这是本次明确目标。
- hand first/second pass 改统一全局 assignment，这是本次明确目标。
- 改变 `dummyLoss` 严格 `<` 语义。
- 改变 sentinel、output map key、driver identity、left-before-right。
- 改 public API、class ABI/layout 兼容承诺。

# 13 验证策略

必须覆盖：

- Public API/header diff 和必要的 ABI/layout 检查。
- Hungarian 空矩阵、矩形矩阵、tie、forbidden、NaN/Inf、严格 `< dummyLoss`。
- sentinel 不进入 map key 或 vector index。
- driver/back-passenger intrusion、smaller remote face、larger recovered driver。
- body owner 竞争、global optimum 与 driver priority；不得再以 driver-first greedy 等价为验收目标。
- left/right 固定顺序和对称检测 tie。
- 跨 owner hand 竞争与单个 detection 不得重复分配。
- 每帧 hit/miss 最多推进一次。
- face/body 消失后的 hand cleanup 与 ID 复用，至少覆盖 120 次 owner turnover。
- sanitize 对 matched/unmatched 的差异。
- baseline/candidate 逐帧四类 map 归一化对比。
- 本地 warning build、J6B build、runtime replay、独立 review。

后续板端建议：

- driver intrusion 与遮挡恢复；
- body loss 与 reacquisition；
- crossed hands 和多人干扰；
- 输出 key 漂移、identity swap、crash；
- 固化 binary/config hash、日志和序列化输出。

# 14 尚需补充的信息

- Body/Hand 全局 assignment 的代表性冲突样例、期望 owner/slot 和允许 delta 白名单。
- Body tracking/acquisition cost 与 Hand tracking/acquisition cost 的配置范围和标定依据。
- owner body 不可发布或消失时，hand 的期望 grace period。
- 可用于逐帧对比的 replay 输入、车型配置与预期 delta 白名单。
- 是否要求对 `DmsTrack` private layout 保持二进制兼容；若要求，必须单独做 ABI 评估。

# 15 最终建议

1. 停止在 `feat/ljc/track_0609` 上继续叠加结构重构。
2. 从 `br_develop_forJ6b` 新开 clean branch。
3. 不整提交 cherry-pick 当前实验链；复用其 solver/cost/row 设计证据，在 clean branch 分阶段重做。
4. 先用稳定基线 Face Hungarian 建立通用 solver，并证明 Face 行为等价。
5. 再独立完成 Body 全局 owner assignment 和 Hand 全局 slot assignment，每阶段只开放一类行为 delta。
6. Hand assignment 后必须单独闭合 owner 消失 lifecycle，不能只推进本帧 eligible rows。
7. 最后收敛 private header 到 phase-level 接口；solver、row、key、result 和单帧 snapshot 使用最低必要可见性。
8. 统一 assignment 是明确目标，但必须按高风险算法变更治理，不能伪装成可读性优化。

# 16 实施回写：阶段 1/2 Clean Refactor

## 16.1 分支与代码范围

- 代码仓：`/home/jichao/dms`
- 当前分支：`feat/ljc/track_0615`
- 已有阶段 1 提交：`460c54ef refactor:extract cpp-internal assignment solver for face equivalence`
- 本次阶段 2 修改文件：
  - `/home/jichao/dms/source/utils/track.cpp`
- 未修改：
  - `/home/jichao/dms/include/utils/track.h`
  - public `DmsTrack::Init/Update`
  - Face solver 行为
  - Hand assignment/lifecycle

## 16.2 阶段 2 实施内容

Body matching 已从逐 owner greedy 抢占 detection 改为一次性 owner-to-body-detection 全局 assignment：

- 左侧实体：本帧有效 `ownerFaceIds`，driver face 仍排在第一位作为确定性 row 顺序和 tie-break 输入。
- 右侧实体：本帧 body detections。
- solver：复用 `.cpp` anonymous namespace 内的 `SolveAssignment`，保持 expanded matrix、dummy edge、forbidden finite cost 和 strict `< dummyLoss` 语义。
- cost：
  - 已有 body track 使用预测框与 detection 的 `computeMatchLoss`。
  - acquisition 使用 `FaceBelongsToBody + FaceAnchorLoss`。
  - driver acquisition 使用 `kDriverBodyAssignmentBonus = -0.25f`，非 driver acquisition 使用 `kBodyAcquireBias = 0.5f`。
  - evaluator 不再平权比较 tracking/acquisition：已有 body track 只接受 strict `< body.dummyLoss` 的 tracking edge；tracking 不可靠则本帧 miss，不使用 acquisition 重新绑定。无 body track 的新 owner 才使用 acquisition。
  - 该保守层级只是实现约束，不等于 loss 已标定完成；tracking/acquisition/dummyLoss 的尺度仍必须用冲突样例验证，标定后才能重新讨论 initialized fallback。
- Hand matching 同步按同一原则收敛：所有 eligible left/right slots 进入一次全局 assignment；initialized slot 只接受 reliable prediction tracking，tracking 不可靠则 miss；uninitialized slot 只走 body-anchor acquisition。
- Body/Hand 输出阶段改为 `PrepareTrackForOutput` 后纯写 output map；sanitize failure 只在 finalize 中对本帧 matched body/slot 推进 miss，publish 不再隐式推进 lifecycle。

## 16.3 Cost 标定风险

本阶段不再以 driver-first greedy 等价为验收目标。当前实现已避免 tracking/acquisition 平权竞争，并在 loss 未标定前关闭已有 body / initialized hand 的 acquisition fallback。剩余风险是：若 tracking loss 对错误检测仍低于 `dummyLoss`，仍会错误延续旧 track；若后续重新打开 initialized fallback，acquisition gate 或 bias 过宽也可能把 owner 误绑定到其他轨迹。该风险必须进入后续验证白名单，不能用静态审查或编译证明运行效果。

## 16.4 验证结果

- `git diff --check`：通过。
- QNX 环境加载前直接 `cmake --build build --target Utils`：失败，原因是当前 shell 未定义 `QNX_HOST` 与 `QNX_TARGET`，属于环境问题。
- 加载 `/home/jichao/qnx800/qnxsdp-env.sh` 后：
  - `cmake --build build --target Utils`：通过，最终 `[100%] Built target Utils`。
  - `cmake --build build --target sdk`：通过，最终 `[100%] Built target sdk`。
- 独立只读 explorer 确认阶段 1 已落地，Body/Hand 尚未迁移。
- 独立只读 reviewer 未发现编译/API/header 抽象漂移问题；用户进一步指出 tracking/acquisition 两类 loss 均需标定，已记录为后续 runtime 验证项。

## 16.5 下一步

下一步仍按阶段计划进入：

1. 补 Body/Hand tracking 与 acquisition loss 标定样例，覆盖 tracking 错误低损失、新 owner acquisition 误绑定、未来 initialized fallback 误绑定、driver/non-driver 竞争和 crowded multi-body/hand 场景。
2. 阶段 4：Hand owner disappearance lifecycle 闭环。
3. 阶段 5：phase 与局部表示收敛。

在继续扩大行为变化前，应补充或至少明确 Body/Hand global assignment 的冲突样例、driver 竞争样例、hand 左右交叉样例和 runtime diff 白名单，否则本轮只能声明“构建通过和设计目标实现”，不能声明运行效果闭环。

# 17 方案整理补充：Body 四态 edge 与独立生命周期

2026-06-16 对 Tracking 方案做整理后，本评审记录补充以下设计输入：

1. `座舱多目标跟踪实现.md` 已从 Tracking 当前工作区归档到 `90_Archive/02_Projects/DMS/04_Tracking/`，只作为历史 body-first baseline 与参数推导参考。
2. `head-first跟踪方案.md` 继承历史方案中 body/face/hand 生命周期独立的正确原则：owner identity 来自 face/head，body/hand 继承 owner key，但内部生命周期按自身 detection、motion state、hit/miss、handoff 和 cleanup 推进。
3. 该继承不恢复 body-first identity。body/hand 不能反向决定 driver identity，也不能通过 raw body box 扩大 owner。
4. Body 全局 assignment 的最终 edge 解释应收敛为 Track / Reacquire / Bootstrap / Forbidden：
   - Track：owner 有 body track，tracking loss 可信，face consistency 不明显冲突；执行 `CorrectMotion` 与 `AdvanceHit`，保持生命周期连续。
   - Reacquire：owner 有 body track，tracking loss 不可信，acquisition loss 高可信；保持 ownerFaceId，重置或强校正 motionState，不把 `hitCount` 重置为 1，已稳定输出时保持输出连续。
   - Bootstrap：owner 没有 body track，acquisition loss 可信；新建 body evidence，`hitCount` 从 1 开始，按 `hitThreshold` 决定是否输出。
   - Forbidden：tracking 和 acquisition 都不可信，或 face consistency 冲突；owner unmatched，已有 body 执行 `AdvanceMiss`，必要时 retire。
5. 标定前的当前保守实现仍只打开 Track / Bootstrap；Reacquire 必须等待 tracking/acquisition loss、driver/non-driver bias、face consistency gate 和 runtime diff 白名单完成后再打开。
6. Hand lifecycle 阶段必须独立 sweep 所有 initialized slots。assignment rows 只代表本帧候选域，不得替代 owner 消失、body 不可发布、face 短时消失、new owner handoff 和 id 复用前 cleanup 的生命周期规则。

## 17.1 对分阶段计划的修正

后续阶段顺序应先解耦生命周期，再做 loss 标定和 Reacquire 打开。原因是：若 face 短时消失时 body/hand owner 根本不进入候选域，loss instrumentation 无法覆盖“脸部遮挡但 body/hand 可继续跟踪”的核心场景，标定结果会缺失最关键的输入分布。

- 阶段 2A：Conservative Body global assignment。保持当前 Track / Bootstrap 策略；已有 body track 的 tracking 不可信时仍 miss，不打开 Reacquire。
- 阶段 3A：Conservative Hand global slot assignment。保持 initialized slot 只走 tracking、uninitialized slot 只走 acquisition；不把 hand acquisition fallback 扩展到 initialized slot。
- 阶段 4A：Owner / body / hand 独立生命周期闭环。先保证 face 短时消失、body 仍连续、hand slot 未进入 assignment row、新 stable owner 接管和 face id 复用前 cleanup 都有 bounded lifecycle 规则。
- 阶段 4B：Loss instrumentation + replay 标定。在 4A 候选域闭合后采集 tracking/acquisition loss、driver/non-driver bias、face consistency gate、dummyLoss 和 hand slot lifecycle sweep 相关分布。
- 阶段 4C：Body Reacquire 打开。只在 4B 标定后实现 Reacquire，并验证 ownerFaceId、hitCount、输出连续性和 motion reset/strong correction。
- 阶段 4D：评估 Hand 是否需要类似 Reacquire。先基于 4A/4B 的 hand slot 数据判断需求，不默认把 Body Reacquire 机械复制到 hand。
- 阶段 5：phase/header 表示收敛。四态 edge classifier 默认留在 `updateBodyTracks` 的 `.cpp` 局部实现，不新增 header-level Edge/Mode/Context 抽象；若后续确需 enum，也必须先补抽象必要性审计。
