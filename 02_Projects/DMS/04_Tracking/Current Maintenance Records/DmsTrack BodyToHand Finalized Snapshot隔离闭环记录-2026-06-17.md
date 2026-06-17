---
title: DmsTrack Body-to-Hand Finalized Snapshot 隔离闭环记录
summary: 将 hand 阶段内部 body 输入从 legacy body output map 隔离为 body 阶段返回的局部 finalized driver body evidence snapshot。
status: reviewed
doc_role: implementation_record
truth_role: project_record
scope: DMS Tracking body-to-hand finalized snapshot 单步代码实现、编译验证、interface guard 审计、独立 review 与知识库写回；不包含 runtime replay、单元测试或板端验证。
sources:
  - /home/jichao/dms/include/utils/track.h
  - /home/jichao/dms/source/utils/track.cpp
  - 02_Projects/DMS/04_Tracking/tracking_spec_current.md
  - 02_Projects/DMS/04_Tracking/tracking_implementation_current.md
  - 02_Projects/DMS/04_Tracking/tracking_validation_current.md
  - 02_Projects/DMS/04_Tracking/subpower_runs/2026-06-17_body_to_hand_snapshot/
risks:
  - 本轮只完成本地编译和独立静态 review；未执行 runtime replay、单元测试或板端验证。
  - hand 现在只消费 body phase 发布成功后的 driver snapshot；若未来需要使用未发布、未达到输出阈值或 sanitize 前的内部 body 状态，需要重新评审契约。
updated_at: 2026-06-17
---

# 1 变更摘要

本轮按 `interface-abstraction-implementation-guard` 守门执行，实现 `body-to-hand finalized snapshot` 隔离。

代码变更：

- `updateBodyTracks` 返回 `std::map<track_id, TrackInfo>` 类型的局部 driver body evidence snapshot。
- 只有 `PublishSanitizedTrack` 成功写入 legacy body output map 后，同一份 finalized/sanitized `TrackInfo` 才进入该 snapshot。
- `updateHandTracks` 新增 private 参数 `const std::map<track_id, TrackInfo>& driverBodyEvidence`。
- hand 阶段内部的 allowed owner、body box、second pass、orphan cleanup、publish/fallback 全部改为只读 `driverBodyEvidence`。
- `curResult->m_bodyTrackResultMap` 在 `track.cpp` 中只保留每帧 clear 与 body phase publish 角色，不再作为 hand 内部 body 输入源。

# 2 接口与抽象守门结论

保持不变：

- `DmsTrack::Init` / `DmsTrack::Update` public API。
- 四类 legacy map ABI。
- Hand matching 与 lifecycle 主体行为。
- 2m/5m profile split 与 5m driver-bound body evidence。

允许且已执行：

- 修改 private phase-level 方法签名。
- 使用已有 `std::map<track_id, TrackInfo>` 作为局部 phase result。

未引入：

- 新 Row/View/Payload/Result/View 类型。
- Header-level step helper tree。
- 新跨模块契约。

# 3 验证

- `rg -n "curResult->m_bodyTrackResultMap" /home/jichao/dms/source/utils/track.cpp`：仅剩 clear 与 body publish。
- `git -C /home/jichao/dms diff --check -- include/utils/track.h source/utils/track.cpp`：通过。
- `bash scripts/compile_j6b.sh`：通过，最终输出 `[100%] Built target sdk`。
- 独立 repo-reviewer：`approved`，无 blocking findings；API/抽象审计通过。

未执行：

- runtime replay。
- 单元测试。
- 板端验证；本次任务边界声明不涉及板端验证。

# 4 残余风险与后续验证

- 仍需补 5m 样本 replay，确认 hand owner source 与 left/right slot 在 finalized body snapshot 下保持预期。
- 仍需补多人干扰与 hand 大幅运动场景，确认 hand 不跨 owner 迁移。
- 若未来需要 hand 消费未发布 body 状态，必须重新做接口/抽象评审并更新 current 文档。

# 5 写回决策

本记录写入项目区 `02_Projects/DMS/04_Tracking/Current Maintenance Records/`。本轮内容仍是 DMS Tracking 项目绑定实现事实，不提升到 `01_Knowledge/`。
