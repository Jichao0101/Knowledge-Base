---
title: DmsTrack HandPhase internal helper 可读性整理闭环记录
summary: 记录按照 DmsTrack 整体内部架构可读性优化方案执行的 Hand phase 小步：将 updateHandTracks 中若干局部机制 lambda 收敛为 .cpp internal helper，减少不同抽象层级在同一函数内继续堆叠。
status: closed
doc_role: implementation_record
truth_role: project_record
scope: /home/jichao/dms/source/utils/track.cpp 中 Hand phase 局部组织；不改变 hand solver、miss、cleanup 或 publish 行为。
sources:
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack整体内部架构可读性优化评审与方案-2026-06-17.md
  - /home/jichao/dms/source/utils/track.cpp
updated_at: 2026-06-17
---

# 1 本步范围

- 方案阶段：阶段 4 Hand phase 局部组织的第一小步。
- 代码范围：`/home/jichao/dms/source/utils/track.cpp`。
- 本步只把 `updateHandTracks` 中若干局部机制 lambda 移到 `.cpp` anonymous namespace helper：
  - allowed owner 收集。
  - hand slot 预测。
  - body-constrained hand candidate 收集。
  - unmatched slot miss 推进。
  - expired slot reset。
  - hand slot publish gate。
- 未修改：
  - `/home/jichao/dms/include/utils/track.h`
  - public `DmsTrack::Init/Update`
  - private phase 方法签名
  - hand solver 矩阵、matched/used 集合、cleanup、retired body 清理、stage tag、输出 map key

# 2 实现内容

新增 `.cpp` anonymous namespace helper：

- `CollectAllowedHandOwners(...)`
- `PredictHandSlot(...)`
- `CollectBodyConstrainedHandCandidates(...)`
- `AdvanceUnmatchedHandSlotMiss(...)`
- `ResetExpiredHandSlot(...)`
- `PublishHandSlot(...)`

保留在 `updateHandTracks` 内的内容：

- phase 级主流程顺序。
- first-pass slot assignment 的核心更新链。
- second-pass unmatched slot recovery。
- orphan/retired owner cleanup。
- primary/fallback publish 调用顺序。

# 3 Interface Guard 结论

- public API 变化：无。
- private header API 变化：无。
- 新增稳定类型：无。
- 新增 Row/View/Payload/Result/Context：无。
- 新增 helper 可见性：仅 `.cpp` anonymous namespace。
- 行为意图变化：无。
- 抽象判断：本步没有继续堆局部 lambda，也没有把 step helper 提升到 header；helper 只隐藏局部机制，主 phase 仍由 `updateHandTracks` 持有。

# 4 行为不变量

- allowed hand owner 仍只来自 `driverBodyEvidence` 中 stable DRIVER 的 owner。
- hand slot prediction 仍按 left 后 right 顺序执行，且只对 initialized slot 更新 `predBox`。
- candidate collection 仍使用当前 `handDetections`、实时 `usedDetections` 和 `bodyTrack.box`。
- unmatched slot miss 仍只推进对应 owner/side 的 `slot.track`。
- expired slot reset 仍以 `m_parameters.hand.missThreshold` 为门槛。
- publish gate 仍检查 initialized、occupied id、hit count 和 `HandBelongsToBody`，并保持 stage tag 与 frame size 不变。
- solver、`usedDetections`、`matchedSlots`、cleanup、`m_retiredBodyTracks` 未改。

# 5 验证

- `git -C /home/jichao/dms diff --check -- source/utils/track.cpp`：通过。
- `bash scripts/compile_j6b.sh`：通过，最终 `[100%] Built target sdk`。
- 独立 repo-reviewer：通过，结论 `approve`，无 findings。

# 6 后续

- 当前整体方案中的 Face/Body/Hand 三个代码小步均已完成。
- 后续如继续缩小 `updateHandTracks` 主函数，应先重新评估是否需要更大的 phase-level `.cpp` helper，而不是再新增局部 lambda 或搬运型类型。
