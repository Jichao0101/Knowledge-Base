---
title: DmsTrack 5m Driver-bound Body Evidence 收缩闭环记录
summary: 将 DmsTrack 5m body evidence 收缩为只服务 selected driver face；非 driver body cache 不再获取或发布，只走 miss/cleanup。
status: reviewed
doc_role: implementation_record
truth_role: project_record
scope: DMS Tracking 5m driver-bound body evidence 单步代码实现、编译验证、独立 review 与知识库写回；不包含 runtime replay、单元测试或板端验证。
sources:
  - /home/jichao/dms/source/utils/track.cpp
  - 02_Projects/DMS/04_Tracking/tracking_spec_current.md
  - 02_Projects/DMS/04_Tracking/tracking_implementation_current.md
  - 02_Projects/DMS/04_Tracking/tracking_validation_current.md
  - 02_Projects/DMS/04_Tracking/subpower_runs/2026-06-17_driver_bound_body_evidence/
risks:
  - 本轮只完成本地编译和独立静态 review；未执行 5m runtime replay、单元测试或板端验证。
  - 非 driver body/hand cache 会按 miss threshold 延迟清理，期间不发布；驻留时长仍需后续日志或 replay 确认。
updated_at: 2026-06-17
---

# 1 变更摘要

本轮在上一单步 `camera_type` profile 分流之后，继续实现 2026-06-16 收缩路线中的 5m driver-bound body evidence。

代码变更：

- `updateBodyTracks` 不再把非 driver face owner 加入 body acquisition owner 集合。
- `m_bodyTracks` 中 owner 不是当前 `driverFaceId` 的旧 body track 会推进 miss，并通过既有 miss threshold 清理。
- body publish 阶段新增 `ownerFaceId == driverFaceId` 门槛，非 driver body cache 不再写入 `m_bodyTrackResultMap`。
- `driverFaceId < 0` 时不 fallback 到其他 face owner 获取或发布 body evidence。

# 2 边界

保持不变：

- `DmsTrack::Init` / `DmsTrack::Update` public API。
- `2m` profile split 行为。
- face/head 匹配与 driver face selection。
- Hand assignment 主体结构；hand 仍只消费已发布的 DRIVER body map。

未引入：

- Header 变更。
- 新 Row/View/Payload/Result 类型。
- Body global assignment、Hand global slot assignment、Reacquire 或 independent lifecycle 扩张。

# 3 验证

- `git -C /home/jichao/dms diff --check -- source/utils/track.cpp`：通过。
- `bash scripts/compile_j6b.sh`：通过，最终输出 `[100%] Built target sdk`。
- 独立 repo-reviewer：`approved`，无 blocking findings。

未执行：

- runtime replay。
- 单元测试。
- 板端验证；本次任务边界声明不涉及板端验证。

# 4 残余风险与后续验证

- 仍需补 5m 样本 replay，确认只发布 selected driver face-bound body evidence。
- 仍需确认非 driver body/hand cache 的 miss threshold 驻留不会影响内存、id 复用或后续 owner takeover。
- 仍需补 hand owner source 和 left/right slot 的序列统计验证。

# 5 写回决策

本记录写入项目区 `02_Projects/DMS/04_Tracking/Current Maintenance Records/`。本轮内容仍是 DMS Tracking 项目绑定实现事实，不提升到 `01_Knowledge/`。
