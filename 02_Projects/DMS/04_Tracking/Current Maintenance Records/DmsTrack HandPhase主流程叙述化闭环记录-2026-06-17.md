---
title: DmsTrack HandPhase 主流程叙述化闭环记录
summary: 记录按照 Face/Body/Hand 主流程叙述化修订方案执行的 Hand phase 小步：将 updateHandTracks 主体收敛为检测收集、owner 收集、predict、first pass、second pass、cleanup、publish 的状态机摘要。
status: closed
doc_role: implementation_record
truth_role: project_record
scope: /home/jichao/dms/include/utils/track.h 与 /home/jichao/dms/source/utils/track.cpp 中 Hand phase 内部组织；不改变 hand first pass、second pass、cleanup 或 publish 行为。
sources:
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack FaceBodyHand主流程叙述化重构修订方案-2026-06-17.md
  - /home/jichao/dms/include/utils/track.h
  - /home/jichao/dms/source/utils/track.cpp
updated_at: 2026-06-17
---

# 1 本步范围

- 方案阶段：阶段 3 Hand 主流程叙述化。
- 代码范围：
  - `/home/jichao/dms/include/utils/track.h`
  - `/home/jichao/dms/source/utils/track.cpp`
- 本步移除 `updateHandTracks` 中长期存在的复杂局部闭包，把主流程整理成 high-level phase 摘要。
- 未修改：
  - public `DmsTrack::Init/Update`
  - legacy left/right hand output map ABI 与 key
  - hand first pass / second pass matching 语义
  - miss、cleanup、publish、fallback publish 行为
  - Face/Body phase 主逻辑

# 2 实现内容

新增 `DmsTrack` private helper：

- `predictExistingHandSlots()`
- `updateOwnedHandSlotsFromBodyConstrainedDetections(...)`
- `recoverUnmatchedHandSlots(...)`
- `cleanupOrphanAndExpiredHandSlots(...)`
- `publishDriverBoundHandSlots(...)`

新增 `.cpp` anonymous namespace helper：

- `ApplyHandFirstPassSlot(...)`

`updateHandTracks` 主体收敛为：

```text
collect hand detections
collect allowed driver hand owners
predict existing hand slots
first pass: update owner-local left/right slots from body-constrained detections
second pass: recover unmatched initialized slots under owner body constraint
cleanup orphan/expired hand slots and retired body cache
publish driver-bound left/right hand slots
```

# 3 Interface Guard 结论

- public API 变化：无。
- private header API 变化：有，新增 5 个 Hand phase-level private helper。
- 新增稳定类型：无。
- 新增 Row/View/Payload/Result/Context：无。
- 行为意图变化：无。
- private interface 成本判断：新增 helper 操作 `m_handTracks`、`m_bodyTracks`、`m_retiredBodyTracks` 和 `m_parameters`，表达稳定 Hand phase 子流程；若强行保留在主函数局部闭包，会继续隐藏依赖并打断主流程阅读。新增 private surface 可读性收益大于成本。

# 4 行为不变量

- hand detection 收集仍按 `m_detResultMap` 迭代并筛选 `kHandClassId`。
- allowed owners 仍来自 `CollectAllowedHandOwners(driverBodyEvidence)`。
- first pass cost matrix、Hungarian row assignment、`usedDetections`、`matchedSlots`、slot init/update、`AdvanceHit`、person type propagation 不变。
- `candidateIdxs.empty()` 在新 helper 中为 `continue`，等价于原 per-owner lambda 的 `return`。
- second pass recovery matrix、dummy edges、used detection gate 和 miss 推进不变。
- cleanup orphan/expired slot 与 retired body cache 行为不变。
- primary/fallback publish、occupied left/right ids、stage tag、输出 key 等于 owner face id 不变。

# 5 验证

- `git -C /home/jichao/dms diff --check -- include/utils/track.h source/utils/track.cpp`：通过。
- `bash scripts/compile_j6b.sh`：通过，最终 `[100%] Built target sdk`。
- 独立 repo-reviewer：通过，结论 `approve`，无 findings。

# 6 后续

- Face/Body/Hand 主流程叙述化三个阶段均已完成。
- 后续若再处理 hand first/second pass 或 publish/fallback publish 边界，应先做行为等价审计，不默认合并 fallback。
