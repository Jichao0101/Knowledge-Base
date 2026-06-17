---
title: DmsTrack FacePhase 主流程叙述化闭环记录
summary: 记录按照 Face/Body/Hand 主流程叙述化修订方案执行的 Face phase 小步：将 updateFaceTracks 主体收敛为预测、匹配应用、bootstrap、miss/erase 的状态机摘要。
status: closed
doc_role: implementation_record
truth_role: project_record
scope: /home/jichao/dms/include/utils/track.h 与 /home/jichao/dms/source/utils/track.cpp 中 Face phase 内部组织；不改变 Face matching、bootstrap、miss/erase 行为。
sources:
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack FaceBodyHand主流程叙述化重构修订方案-2026-06-17.md
  - /home/jichao/dms/include/utils/track.h
  - /home/jichao/dms/source/utils/track.cpp
updated_at: 2026-06-17
---

# 1 本步范围

- 方案阶段：阶段 1 Face 主流程叙述化。
- 代码范围：
  - `/home/jichao/dms/include/utils/track.h`
  - `/home/jichao/dms/source/utils/track.cpp`
- 本步只整理 `updateFaceTracks` 内部主流程叙述，不改变 Face matching、bootstrap、miss/erase 行为。
- 未修改：
  - public `DmsTrack::Init/Update`
  - legacy output map ABI
  - Body/Hand phase 主逻辑
  - Hungarian loss matrix 语义、dummy loss 语义或 gate 条件

# 2 实现内容

新增 `DmsTrack` private helper：

- `predictExistingFaceTracks(...)`
- `solveAndApplyFaceAssignments(...)`
- `bootstrapUnmatchedFaceDetections(...)`
- `advanceAndEraseUnmatchedFaceTracks(...)`

新增 `.cpp` anonymous namespace helper：

- `CollectDetectionsByClass(...)`

`updateFaceTracks` 主体收敛为：

```text
collect face detections
predict existing face tracks
solve/apply face assignments
bootstrap unmatched detections
advance/erase unmatched face tracks
```

# 3 Interface Guard 结论

- public API 变化：无。
- private header API 变化：有，新增 4 个 Face phase-level private helper。
- 新增稳定类型：无。
- 新增 Row/View/Payload/Result/Context：无。
- 行为意图变化：无。
- private interface 成本判断：新增 helper 操作 `m_faceTracks`、`m_parameters` 和 `allocateFaceTrackId`，如果强行留在 `.cpp` helper 需要传入过多长期状态；作为 private helper 能显著降低 `updateFaceTracks` 主流程阅读层级，收益大于 private surface 成本。

# 4 行为不变量

- `BuildFaceAssignmentLoss` 输入和 loss 语义不变。
- `hungarian` 调用不变。
- `usedDetections` 与 `matchedFaceTracks` 更新条件不变。
- `computePersonType` 调用位置和输入不变。
- matched face 仍执行 motion correct、box/predBox 更新、`AdvanceHit`、person vote 和 stable type resolve。
- unmatched detection 仍通过 `allocateFaceTrackId()` 创建新 face。
- unmatched face 仍执行 `AdvanceMiss`，达到 `m_parameters.face.missThreshold` 后 erase。

# 5 验证

- `git -C /home/jichao/dms diff --check -- include/utils/track.h source/utils/track.cpp`：通过。
- `bash scripts/compile_j6b.sh`：通过，最终 `[100%] Built target sdk`。
- 独立 repo-reviewer：通过，结论 `approve`，无 findings。

# 6 后续

- 下一步进入 Body phase 主流程叙述化。
- 若后续继续调整 private helper，应继续记录“可读性收益是否大于 private interface 成本”。
