---
title: DmsTrack updateHandTracks 第二阶段可读性优化方案
summary: 在 head-first、2m/5m 分流、driver-bound body evidence 与 body-to-hand snapshot 已落地后，评估 updateHandTracks 的层级混杂问题，并规划不改变行为的可读性优化步骤。
status: planned
doc_role: refactor_plan
truth_role: project_plan
scope: DMS Tracking updateHandTracks 第二阶段可读性优化方案；只规划结构整理，不声明运行效果闭合，不改变功能规范。
sources:
  - /home/jichao/dms/include/utils/track.h
  - /home/jichao/dms/source/utils/track.cpp
  - 02_Projects/DMS/04_Tracking/tracking_spec_current.md
  - 02_Projects/DMS/04_Tracking/tracking_implementation_current.md
  - 02_Projects/DMS/04_Tracking/tracking_validation_current.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack BodyToHand Finalized Snapshot隔离闭环记录-2026-06-17.md
risks:
  - 本方案只针对阅读复杂度，不应借机改变 hand matching、lifecycle、cleanup 或 publish 条件。
  - 若新增 Row/View/Payload/Result 类型，容易把复杂度转移到新的认知接口，必须重新执行 interface guard。
updated_at: 2026-06-17
---

# 1 功能完成度评估

已完成到代码落地与本地验证级别：

- `2m/5m camera_type` 分流。
- `2m` 关闭并清理 body/hand。
- `5m` body evidence 收缩为 selected driver face-bound。
- hand 内部 body 输入已从 legacy `curResult->m_bodyTrackResultMap` 隔离为 body phase 返回的局部 finalized driver body evidence snapshot。
- public `DmsTrack::Init/Update` 未变。

未闭合：

- runtime replay。
- 单元测试。
- 板端验证。
- hand owner source、left/right slot、多人干扰、face miss / owner retire / id reuse 下的 bounded cache 序列证据。

因此当前结论是：方案功能代码路径已落地，但运行效果未验收。

# 2 updateHandTracks 当前问题

`updateHandTracks` 的主要问题不是“缺少抽象”，而是多个层级混在同一个函数中：

- 高层策略：只允许 driver body evidence 作为 hand owner。
- 候选构造：从 hand detections 中筛 body 几何范围内候选。
- assignment 机制：Hungarian、row/col、dummy loss。
- 状态推进：slot hit/miss、initialized reset、cleanup。
- 输出投影：left/right legacy map publish。
- 历史清理：retired body anchor 清 orphan hand。

这些层级混杂导致阅读者需要同时持有业务规则、solver 细节、slot lifecycle、legacy 输出和 cleanup。机械拆出 `Row/View/Payload/Result` 只会转移复杂度；合理目标是让主流程只表达 phase-level 语义，把低层机制收敛到局部 helper 或 lambda。

# 3 抽象原则

允许：

- 保持 `DmsTrack::Init/Update` public API 不变。
- 保持 `updateHandTracks` 作为 phase-level private 方法。
- 使用局部 lambda 或 `.cpp` internal helper 整理单一机制。
- 使用现有 `TrackInfo`、`HandTrackState`、`HandSideState`、`std::map`、`std::set`、`std::vector`。

禁止或暂缓：

- 新增 header-level `Row/View/Payload/Result/Context`。
- 新增 `FrameHandView`、`HandPublishPayload`、`LifecycleContext`。
- 把固定执行脚本展开为 private header step helper 树。
- 在可读性优化中改变 matching、miss、cleanup、publish 条件。

# 4 分步方案

## Step 1：整理 hand publish 段

目标：

- 只整理 `updateHandTracks` 底部 left/right publish 与 fallback publish 的重复结构。
- 不改变输出条件、输出 stage tag、occupied set 语义或 fallback 行为。
- 优先使用函数局部 lambda，不新增 header 方法或类型。

验证：

- `git diff --check -- source/utils/track.cpp`
- `bash scripts/compile_j6b.sh`
- 独立 review 确认行为等价和抽象未漂移。

## Step 2：整理 unmatched slot advance

目标：

- 把 second pass 后 unmatched slot 的 miss 推进和无候选时的 miss 推进收敛到局部机制。
- 不改变何时 `AdvanceMiss`、不改变 `matchedSlots` 和 `unmatchedSlots` 的候选域。

验证：

- 静态 diff 审计确认 `AdvanceMiss` 次数和触发条件不扩大。
- J6B 编译。

## Step 3：整理 driver owner candidate collection

目标：

- 让主流程更清楚地区分：
  - allowed owner 收集
  - slot prediction
  - body-constrained hand candidates
- 不新增稳定 owner view 类型。

验证：

- 静态 diff 审计确认 allowed owner 仍只来自 `driverBodyEvidence` 且 stable `DRIVER`。
- J6B 编译。

## Step 4：可选整理 retired-owner cleanup

目标：

- 将 orphan hand cleanup 与 expired slot cleanup 的阅读位置收敛。
- 不改变 `m_retiredBodyTracks` 删除条件。

停止条件：

- 若需要新增稳定 cleanup context、payload 或跨 phase 类型，停止并重新做 deep-module review。

# 5 当前推荐执行

当前只执行 Step 1：整理 hand publish 段。

理由：

- 风险最低。
- 不触碰 solver、候选域、miss 推进和 cleanup。
- 可以立刻降低 `updateHandTracks` 末段重复阅读成本。
- 若 Step 1 无法做到行为等价，后续步骤不应继续。
