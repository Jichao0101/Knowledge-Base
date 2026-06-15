---
title: DmsTrack 深模块重新评审与 Clean Refactor 规划
summary: 对 feat/ljc/track_0609 与 br_develop_forJ6b 的 track.h/track.cpp 进行只读深模块评审；结论为停止在实验分支继续叠加结构重构，从稳定基线新开 clean branch，并只选择性重做已确认的行为修复。
status: reviewed
doc_role: review_record
truth_role: project_review
scope: DmsTrack public/private API、body/hand phase 边界、assignment 抽象、生命周期与 clean refactor 规划；不包含代码实现和板端验证。
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
  - 未执行编译、runtime replay、单元测试或板端验证。
  - global Hungarian body assignment 与 orphan hand lifecycle 的目标行为仍需需求或运行证据确认。
  - 本记录给出设计与路线判断，不授权直接修改代码。
updated_at: 2026-06-15
---

# 1 结论摘要

## 1.1 已由代码证实

- `DmsTrack` public API 在稳定基线和实验分支均只有 `Init()`、`Update()`；调用方不需要编排 face/body/hand 内部步骤。
- 实验分支 private header 从基线的少量 phase-level 方法扩张为完整的 solve/apply/advance/finalize/project/publish 执行脚本。
- `1237f6c6` 将稳定基线的 driver-first、逐 owner greedy body matching 改为全局 Hungarian；这是算法行为变化。
- `FrameBodyView`、`HandSlotKey`、`HandAssignmentRow` 都是单帧中间表示，却被放入 private header。
- `AssignmentResult` 仅为 solver index 结果，但因 step helper 签名而前置声明到 namespace header。
- 当前 hand miss 只推进本帧 allowed owner 对应的 assignment rows；owner 消失后，已初始化 slot 可能不再推进 miss，空 owner state 也无法删除。
- 稳定基线已包含与实验分支 `3f7d35a8` patch-equivalent 的 driver recognition 修复，不应重复 cherry-pick。

## 1.2 设计判断

- 当前模块是“外部接口深、内部组织浅”的混合模块。
- 主要问题不是 public API，而是 private header surface 和内部阶段边界。
- `feat/ljc/track_0609` 已进入补救式重构：宽拆分后连续追加 sentinel、状态、语义和抽象删除修补。
- 不建议继续在该分支叠加结构改动；建议从 `br_develop_forJ6b` 新开 clean branch。
- 当前分支只作为行为候选与反例样本，不作为 clean refactor 的结构基底。

## 1.3 尚需验证

- 是否产品上确实需要 global Hungarian body assignment。
- body owner 消失后 hand 应立即清理、按 missThreshold 延迟清理，还是保留其他 bounded grace period。
- selective reimplementation 后是否与稳定基线保持逐帧输出等价。

# 2 当前分支是否建议继续

**结论：停止继续结构重构。**

理由：

1. private header 声明数由约 21 增至约 67，复杂性主要从长函数转移到更多 helper 和中间类型。
2. 9 个主要提交同时混合结构、算法、sentinel、状态和 driver 行为修复。
3. 后续提交反复新增、重命名和删除 assignment wrapper，说明抽象边界未稳定。
4. 缺少 tracker 专项行为测试，无法安全证明多轮结构变化等价。
5. 已发现 global assignment 和 orphan hand lifecycle 两个不能按“可读性优化”处理的高风险问题。

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
| `AssignmentResult` | 主要隐藏 expanded Hungarian dummy 细节 | 降级 | `.cpp` internal 或函数局部 | `std::vector<int> rightByLeft`，未匹配为 `-1`；需要 cost 时并行局部 vector |
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

当前 matches + unmatchedLeft + unmatchedRight 对相邻 solve/apply helper 有便利，但其存在主要由 step helper 拆分驱动。若 phase-level helper重新收敛，优先使用 `rightByLeft[left] = right/-1`。只有多个不同算法调用点确实需要统一 match cost 和双侧 unmatched 结果时，才保留 `.cpp` internal result。

# 7 Body 层级问题与建议接口

## 7.1 当前问题

- `updateBodyTracks` 内部流程被完整复制到 header。
- global Hungarian 改变了稳定基线的 driver-first greedy ownership。
- finalize、projection、publish 的 side-effect 边界虽有价值，但不需要全部成为 member API。
- header 注释仍提到 greedy ownership，而实现已是 global Hungarian，形成事实矛盾。

## 7.2 建议接口

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

## 8.2 建议接口

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

- `d72a75be` 中“sanitize 失败只对本帧已命中项推进 miss”的语义。
- `d72a75be`/`dc475f00` 中 finalize 负责状态副作用、publish 只写 output 的边界。
- `4155bfde` 中“不使用 caller-owned legacy output map 作为 body -> hand 内部事实源”的目标。

不需要 cherry-pick：

- `3f7d35a8` driver recognition 修复，稳定基线已有 patch-equivalent 提交 `bcdbe8e5`。

# 10 应丢弃或重做的改动类型

- `804ff0f1`、`76490b4d` 引入的 step-level helper 展开。
- `1237f6c6` 的 global body/hand assignment，除非作为独立算法变更重新立项。
- `41abae61` 中与 helper 展开混合的 sentinel/生命周期结构。
- `88620616`、`dc475f00` 继续围绕既有 step tree 的包装删除与重命名。
- header-level `FrameBodyView`、`HandSlotKey`、`HandAssignmentRow`、`AssignmentResult`。
- `AssignmentPolicyMatrix`、`AssignmentCandidate`、`AssignmentRejection`。
- 任何为保持上述抽象而增加的解释层或长注释。

# 11 Clean Refactor 分阶段计划

| 阶段 | 要做 | 不做 | 验证方式 | 停止条件 |
|---|---|---|---|---|
| 0 行为基线 | 从 `br_develop_forJ6b` 新开分支；记录 SHA、配置、关键序列逐帧输出和生命周期 | 不重构 | map key/box/type、driver id、hit/miss、左右顺序快照 | 无法定义期望行为或缺少可重放输入 |
| 1 行为修复隔离 | 分别重做 matched-only sanitize miss 与 body-to-hand 内部状态隔离 | 不统一 assignment，不拆 helper 树 | 单项序列测试、baseline/candidate 差异白名单 | 出现非目标 assignment/output 差异 |
| 2 生命周期契约 | 明确 owner 消失后的 hand cleanup/miss 规则并独立实现 | 不伪装成可读性优化 | face/body 消失、120+ owner turnover、retired anchor 场景 | 产品规则不明确或 ID 泄漏仍存在 |
| 3 Phase-level 重构 | 收敛 face/body/hand phase；pure helper 留 `.cpp` | 不新增 View/Payload/Row/Result 到 header | header surface 对比、逐帧等价、编译 | private header 仍暴露固定步骤脚本 |
| 4 内部表示收敛 | row/key/result 局部化；复用 map/vector；publish pure | 不改 public API、key、dummyLoss、sentinel | assignment table tests、sanitize side-effect tests | 新类型不能证明不变量/复用收益 |
| 5 独立算法评估 | 仅在明确需求下评估 global Hungarian | 不与 clean refactor 合并 | greedy/global 冲突样例、tie、forbidden、runtime replay | ownership 期望不明确或回归不可解释 |
| 6 集成验证 | 本地构建、专项测试、runtime replay、独立 review；后续板端验证 | 不用编译代替运行等价 | normalized frame diff、代表性视频、J6B 验证 | 任一非白名单行为差异 |

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

- greedy body ownership 改 global Hungarian。
- hand first/second pass 改统一全局 assignment。
- 改变 `dummyLoss` 严格 `<` 语义。
- 改变 sentinel、output map key、driver identity、left-before-right。
- 改 public API、class ABI/layout 兼容承诺。

# 13 验证策略

必须覆盖：

- Public API/header diff 和必要的 ABI/layout 检查。
- Hungarian 空矩阵、矩形矩阵、tie、forbidden、NaN/Inf、严格 `< dummyLoss`。
- sentinel 不进入 map key 或 vector index。
- driver/back-passenger intrusion、smaller remote face、larger recovered driver。
- body owner 竞争、driver-first ownership。
- left/right 固定顺序和对称检测 tie。
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

- global Hungarian 是否为明确需求，而不是重构过程中形成的实现选择。
- owner body 不可发布或消失时，hand 的期望 grace period。
- 可用于逐帧对比的 replay 输入、车型配置与预期 delta 白名单。
- 是否要求对 `DmsTrack` private layout 保持二进制兼容；若要求，必须单独做 ABI 评估。

# 15 最终建议

1. 停止在 `feat/ljc/track_0609` 上继续叠加结构重构。
2. 从 `br_develop_forJ6b` 新开 clean branch。
3. 不整提交 cherry-pick 当前实验链；只按行为语义选择性重做。
4. 第一阶段只建立行为基线、修复 hand orphan lifecycle，并隔离 finalize/publish 与 body-to-hand 内部状态。
5. 第二阶段再把 private header 收敛到 phase-level 接口，单帧 row/key/result/snapshot 全部使用最低必要可见性。
6. global Hungarian 必须作为独立高风险算法变更评估，不能继续附着在“可读性重构”名下。

