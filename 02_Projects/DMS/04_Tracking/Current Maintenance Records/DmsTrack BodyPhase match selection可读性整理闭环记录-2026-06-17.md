---
title: DmsTrack BodyPhase match selection 可读性整理闭环记录
summary: 记录按照 DmsTrack 整体内部架构可读性优化方案执行的 Body phase 小步：将 updateBodyTracks 中 tracked body match 与 face-anchored acquisition 两段候选选择收敛为 .cpp internal helper，保持 body evidence 行为和接口不变。
status: closed
doc_role: implementation_record
truth_role: project_record
scope: /home/jichao/dms/source/utils/track.cpp 中 Body phase 局部组织；不覆盖 Hand phase 后续阶段。
sources:
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack整体内部架构可读性优化评审与方案-2026-06-17.md
  - /home/jichao/dms/source/utils/track.cpp
updated_at: 2026-06-17
---

# 1 本步范围

- 方案阶段：阶段 3 Body phase 局部组织的第一小步。
- 代码范围：`/home/jichao/dms/source/utils/track.cpp`。
- 本步只整理 `updateBodyTracks` 内 body detection 选择机制：
  - 已有 body track 的 tracking match。
  - tracking miss 后基于 face 几何的 acquisition match。
- 未修改：
  - `/home/jichao/dms/include/utils/track.h`
  - public `DmsTrack::Init/Update`
  - private phase 方法签名
  - body acquisition/retire/publish 规则
  - profile gate、Face phase、Hand phase

# 2 实现内容

- 新增 `.cpp` anonymous namespace helper：
  - `TrackBoxMatchLoss(...)`
  - `SelectTrackedBodyDetection(...)`
  - `SelectFaceAnchoredBodyDetection(...)`
- `DmsTrack::computeMatchLoss(...)` 保留为既有 private API 壳函数，内部复用 `TrackBoxMatchLoss(...)`，避免本步顺手删除 header private surface。
- `updateBodyTracks` 中原有两段候选扫描改为 helper 调用，主流程保留：
  - 已有 body track 先走 motion prediction + tracking match。
  - tracking match 失败或尚未绑定 body 时，再走 face-anchored acquisition。
  - 命中后仍进入原有 state update、hit、miss/retire、publish 流程。

# 3 Interface Guard 结论

- public API 变化：无。
- private header API 变化：无。
- 新增稳定类型：无。
- 新增 Row/View/Payload/Result/Context：无。
- 新增 helper 可见性：仅 `.cpp` anonymous namespace。
- 行为意图变化：无。
- 抽象判断：本步 helper 只隐藏 Body phase 内稳定的 detection 选择机制，不承载跨 phase 状态，不把固定执行脚本暴露到 header。

# 4 行为不变量

- `PredictMotion` 仍只在已有 body track 的 tracking match 阶段执行，并继续更新 `bodyTrack.predBox`。
- `usedDetections` 过滤条件不变。
- tracking loss 仍为 `10.0f * iouLoss + distanceLoss`。
- tracking match 仍以 `m_parameters.body.dummyLoss` 作为拒绝门槛。
- face acquisition 仍要求 `FaceBelongsToBody(detections[detIdx], faceTrack.box)`。
- face acquisition loss 仍为 `FaceAnchorLoss(detections[detIdx], faceTrack.box)`。
- `bestTrackLoss` / `bestAcquireLoss` 仍供原有日志输出。
- miss/retire/publish/profile/hand 逻辑未改。

# 5 验证

- `git -C /home/jichao/dms diff --check -- source/utils/track.cpp`：通过。
- `bash scripts/compile_j6b.sh`：通过，最终 `[100%] Built target sdk`。
- 独立 repo-reviewer：通过，结论 `approve`，无 findings。
  - reviewer 确认 header 无 diff，新增 helper 位于 anonymous namespace。
  - reviewer 确认 `TrackBoxMatchLoss` 与原 `computeMatchLoss` 公式一致。
  - reviewer 确认 tracking match 保留检测顺序、`usedDetections` 过滤、严格 `<` tie 行为、`bestTrackLoss` 更新、`dummyLoss >=` 拒绝门槛，以及 `PredictMotion` / `predBox` 副作用。
  - reviewer 确认 face acquisition 保留 face-to-body filter、anchor loss、`usedDetections`、检测顺序和 `bestAcquireLoss` 语义。

# 6 后续

- 下一步可继续按照整体方案评估 Hand phase 局部组织。
- 若后续需要删除 private `computeMatchLoss` 或改变 body acquisition/retire/publish 行为，必须重新执行 `interface-abstraction-implementation-guard`。
