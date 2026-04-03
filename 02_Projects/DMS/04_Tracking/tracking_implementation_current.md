---
title: Tracking Implementation Current
summary: Tracking 当前实现文档，记录当前代码结构、关键状态容器、更新顺序、卡尔曼模型、匹配流程和当前实现边界。
status: verified
doc_role: current
truth_role: current
current_kind: implementation
lifecycle_state: active
default_entry: false
sync_required_when:
  - 关键状态容器变化
  - 更新顺序变化
  - 上游结果 map 或下游兼容映射变化
  - hand continuity 的实现路径变化
retrieval_priority: current
supersedes:
  - 02_Projects/DMS/04_Tracking/座舱多目标跟踪实现.md
  - 02_Projects/DMS/04_Tracking/多目标跟踪实现闭环记录-2026-03-24.md
  - 02_Projects/DMS/04_Tracking/tracking_interfaces_current.md
merged_into: []
current_replacement: []
related_code:
  - /home/jichao/dms/include/utils/track.h
  - /home/jichao/dms/source/utils/track.cpp
  - /home/jichao/dms/etc/track_params.json
sources:
  - 02_Projects/DMS/04_Tracking/座舱多目标跟踪实现.md
  - 02_Projects/DMS/04_Tracking/多目标跟踪实现闭环记录-2026-03-24.md
  - 02_Projects/DMS/04_Tracking/多目标跟踪设计失配修复闭环记录-2026-03-25.md
  - 02_Projects/DMS/04_Tracking/多目标跟踪生命周期与手部关联设计失配修复闭环记录-2026-03-25.md
  - 02_Projects/DMS/04_Tracking/多目标跟踪手部连续性优化闭环记录-2026-03-31.md
  - /home/jichao/dms/include/utils/track.h
  - /home/jichao/dms/source/utils/track.cpp
  - /home/jichao/dms/etc/track_params.json
scope: 适用于恢复当前 Tracking 在代码中的主要实现结构、接口事实与行为，不覆盖全部调试历史。
risks:
  - 本文档基于代码静态读取恢复当前实现，没有在本轮重新编译确认。
updated_at: 2026-04-03
---

## 0.1 Core Entry

- 入口类：`UtilsDomain::DmsTrack`
- 主要入口函数：`Init`、`Update`
- 每帧更新顺序：
  1. 清空 `m_bodyTrackResultMap / m_faceTrackResultMap / m_leftHandTrackResultMap / m_rightHandTrackResultMap`
  2. `updateBodyTracks`
  3. `updateFaceTracks`
  4. `updateHandTracks`

## 0.2 Current State Containers

- 长期内部状态：
  - `m_bodyTracks`
  - `m_retiredBodyTracks`
  - `m_faceTracks`
  - `m_bodyHandTracks`
- 对外结果：
  - `AtomicResult::m_bodyTrackResultMap`
  - `AtomicResult::m_faceTrackResultMap`
  - `AtomicResult::m_leftHandTrackResultMap`
  - `AtomicResult::m_rightHandTrackResultMap`
- 下游兼容与消费：
  - `humanpose_model.cpp` 直接消费 `m_bodyTrackResultMap`
  - `handpose_model.cpp` 分别消费 `m_leftHandTrackResultMap` 与 `m_rightHandTrackResultMap`
  - `fuse_algorithm.cpp` 将 body 兼容映射到 `m_humanTrackResultMap`

## 0.3 Motion Models

- body：恒速度 KF
- face：恒速度 KF
- hand：恒加速度 KF，状态包含位置、尺寸、速度、加速度和尺寸变化速度

配置来自 `/home/jichao/dms/etc/track_params.json`，按 `DEFAULT` 或车型节点加载 body / face / hand 的 threshold 与 kalman 参数。

## 0.4 Matching And Lifecycle

### 0.4.1 body

- body 使用扩展方阵 + 匈牙利匹配。
- 真实匹配代价高于 `dummyLoss` 时，倾向于“不匹配”。
- 新 body 通过 `allocateBodyTrackId` 分配 id。

### 0.4.2 face

- face 在 body 邻域内优先匹配。
- 若已有 face 轨迹，优先按预测框与检测框匹配。
- 若没有当前 body 命中，也会对未匹配 face 做全局二次匹配。

### 0.4.3 hand

- hand 先按 body 局部候选与左右槽位做一次分配。
- 之后对未匹配槽位做 second pass 全局匹配。
- 手部 miss 时会把 `box` 推进到 `predBox`，而不是冻结在最后检测框。
- `ShouldOutputHandTrack` 允许短 miss window 继续输出。

## 0.5 Current Implementation Constraints

- face / hand 的 key 语义仍围绕 `bodyId` 建模，说明当前系统仍以 body 为统一身份锚点。
- retired body 只作为 handoff 和 orphan child 清理的历史锚点，不直接对外输出。
- 当前实现为了保留解耦 child，会有 orphan face / hand 兜底输出路径，这也是区域级唯一性尚未完全闭合的直接原因。

## 0.6 Known Gaps

- 代码里存在“body 关联最佳 child + orphan child fallback 输出”的双路径。
- 运行级验证仍待补。

## 0.7 Historical Mapping

- 03-24 delta 落地了 body/face/hand 主框架。
- 03-25 delta 收敛了上游事实源、左右手槽位、retired body handoff 清理与输出契约。
- 03-31 delta 收敛了 hand continuity 优化与短 miss 输出。
- 原 `tracking_interfaces_current` 的当前有效接口事实已并入本文件。

## 0.8 Current Sync Rule

- must_update_when:
  - `DmsTrack::Update` 的主顺序变化
  - `m_bodyTracks / m_retiredBodyTracks / m_faceTracks / m_bodyHandTracks` 结构变化
  - `AtomicResult` 四类 tracking map 或 body 兼容映射变化
  - `ShouldOutputHandTrack`、orphan fallback 或 hand second pass 逻辑变化
- absorbs_history_from:
  - `座舱多目标跟踪实现.md`
  - `多目标跟踪实现闭环记录-2026-03-24.md`
  - `多目标跟踪设计失配修复闭环记录-2026-03-25.md`
  - `多目标跟踪生命周期与手部关联设计失配修复闭环记录-2026-03-25.md`
  - `多目标跟踪手部连续性优化闭环记录-2026-03-31.md`
  - `tracking_interfaces_current.md`
- evidence_only_docs:
  - `tracking_interfaces_current.md`
- not_a_default_entry_anymore:
  - `座舱多目标跟踪实现.md`
  - `多目标跟踪实现闭环记录-2026-03-24.md`
