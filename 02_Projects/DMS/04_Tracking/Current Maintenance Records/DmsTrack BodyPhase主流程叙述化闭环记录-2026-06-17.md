---
title: DmsTrack BodyPhase 主流程叙述化闭环记录
summary: 记录按照 Face/Body/Hand 主流程叙述化修订方案执行的 Body phase 小步：将 updateBodyTracks 主体收敛为检测收集、owner 收集、match/acquire、advance/retire、publish snapshot 的状态机摘要。
status: closed
doc_role: implementation_record
truth_role: project_record
scope: /home/jichao/dms/include/utils/track.h 与 /home/jichao/dms/source/utils/track.cpp 中 Body phase 内部组织；不改变 body matching、state update、miss/retire、publish snapshot 行为。
sources:
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack FaceBodyHand主流程叙述化重构修订方案-2026-06-17.md
  - /home/jichao/dms/include/utils/track.h
  - /home/jichao/dms/source/utils/track.cpp
updated_at: 2026-06-17
---

# 1 本步范围

- 方案阶段：阶段 2 Body 主流程叙述化。
- 代码范围：
  - `/home/jichao/dms/include/utils/track.h`
  - `/home/jichao/dms/source/utils/track.cpp`
- 本步只整理 `updateBodyTracks` 内部主流程叙述，不改变 body matching、state update、miss/retire、publish snapshot 行为。
- 未修改：
  - public `DmsTrack::Init/Update`
  - legacy body output map ABI 与 key
  - Face/Hand phase 主逻辑
  - matching loss、dummy loss、gate 条件

# 2 实现内容

新增 `DmsTrack` private helper：

- `collectEligibleBodyOwners(...)`
- `matchOrAcquireDriverBodyEvidence(...)`
- `advanceAndRetireBodyEvidence(...)`
- `publishDriverBodyEvidenceSnapshot(...)`

`updateBodyTracks` 主体收敛为：

```text
collect body detections
collect eligible body owners
match/acquire driver body evidence
advance/retire body evidence
publish driver body evidence snapshot
```

# 3 Interface Guard 结论

- public API 变化：无。
- private header API 变化：有，新增 4 个 Body phase-level private helper。
- 新增稳定类型：无。
- 新增 Row/View/Payload/Result/Context：无。
- 行为意图变化：无。
- private interface 成本判断：新增 helper 操作 `m_bodyTracks`、`m_retiredBodyTracks`、`m_faceTracks` 和 `m_parameters`，表达稳定 Body phase 子流程；如果强行留在 `.cpp` helper 需要传入过多长期状态。新增 private surface 换来了 `updateBodyTracks` 的状态机摘要，可读性收益大于成本。

# 4 行为不变量

- body detection 收集仍按 `m_detResultMap` 迭代并筛选 `kBodyClassId`。
- eligible owner 条件仍为 `driverFaceId >= 0`、face 存在、`missCount == 0`、`hitCount > 0`。
- `SelectTrackedBodyDetection` 与 `SelectFaceAnchoredBodyDetection` 调用条件和参数不变。
- matched body 仍更新 `m_bodyTracks[ownerFaceId]`、person type counts、motion state、`predBox` 和 `AdvanceHit`。
- unmatched / non-current / dead owner 仍执行 miss 推进，dead/expired body 仍写入 `m_retiredBodyTracks` 后 erase。
- driver body evidence snapshot 仍通过 `PublishSanitizedTrack(curResult->m_bodyTrackResultMap, ownerFaceId, ...)` 发布，stage tag 不变。

# 5 验证

- `git -C /home/jichao/dms diff --check -- include/utils/track.h source/utils/track.cpp`：通过。
- `bash scripts/compile_j6b.sh`：通过，最终 `[100%] Built target sdk`。
- 独立 repo-reviewer：通过，结论 `approve`，无 findings。

# 6 后续

- 下一步进入 Hand phase 主流程叙述化。
- Hand 阶段必须移除或下沉 `updateHandTrackState` / `processSlot` 复杂局部闭包，优先让 `updateHandTracks` 主体读成 first pass、second pass、cleanup、publish 的 phase 摘要。
