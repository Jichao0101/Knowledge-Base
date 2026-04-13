---
title: Tracking Implementation Current
summary: Tracking 当前实现文档，记录代码入口、关键状态载体、spec-to-code mapping、兼容层与未闭合点。
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
  - 02_Projects/DMS/04_Tracking/tracking_interfaces_evidence.md
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
  - 02_Projects/DMS/04_Tracking/多目标跟踪快速运动恢复阶段预测更新一致性修复闭环记录-2026-04-05.md
  - 02_Projects/DMS/04_Tracking/跟踪框越界导致板端coredump调查与修复闭环记录-2026-04-07.md
  - /home/jichao/dms/include/utils/track.h
  - /home/jichao/dms/source/utils/track.cpp
  - /home/jichao/dms/etc/track_params.json
scope: 适用于恢复当前 Tracking 在代码中的主要实现结构、接口事实与行为，不覆盖全部调试历史。
risks:
  - 本文档基于代码静态读取恢复当前实现，没有在本轮重新编译确认。
updated_at: 2026-04-07
---

## 0.1 Core Entry

- 入口类：`UtilsDomain::DmsTrack`
- 主要入口函数：`Init`、`Update`
- 每帧更新顺序固定为：
  1. 清空 `m_bodyTrackResultMap / m_faceTrackResultMap / m_leftHandTrackResultMap / m_rightHandTrackResultMap`
  2. `updateBodyTracks`
  3. `updateFaceTracks`
  4. `updateHandTracks`
- 配置入口固定从 `/home/jichao/dms/etc/track_params.json` 读取，并先应用 `DEFAULT`，再按车型节点覆盖。

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
- 关键状态语义：
  - `m_bodyTracks` 承载当前 active body 轨迹
  - `m_retiredBodyTracks` 承载旧 body 的清理锚点
  - `m_faceTracks` 承载 face 子轨迹
  - `m_bodyHandTracks` 承载每个 body 的 left/right hand 槽位

## 0.3 Motion Models

- body：恒速度 KF
- face：恒速度 KF
- hand：恒加速度 KF，状态包含位置、尺寸、速度、加速度和尺寸变化速度
- body / face / hand 仍先做预测用于匹配，但 2026-04-05 起对“快速运动后恢复正常位姿”的更新路径增加了预测残留抑制：
  - face：命中检测后最终输出框直接使用检测框，不再把 `CorrectMotion` 结果写回输出框
  - hand：命中检测后最终输出框直接使用检测框；2026-04-07 起 miss 时不再沿 `predBox` 向下游输出
  - body：命中检测后改为检测主导融合；当预测与检测出现反向/过冲时，直接回到检测框并重建运动状态
- 2026-04-07 起 body / face / hand 在写入 `AtomicResult::*TrackResultMap` 前统一经过 track 内部 sanitize/clamp；非法框直接丢弃，不再透传给下游

配置来自 `/home/jichao/dms/etc/track_params.json`，按 `DEFAULT` 或车型节点加载 body / face / hand 的 threshold 与 kalman 参数。

## 0.4 Spec-to-Code Mapping

- 人员类型投票与稳定解析 -> `AccumulatePersonVote` / `ResolveStablePersonType`
- 配置读取与 `DEFAULT` / 车型覆盖 -> `loadConfigFromJson`
- body id 分配 -> `allocateBodyTrackId`
- body 主流程 -> `updateBodyTracks`
- face orphan cleanup / fallback / driver small-face filtering -> `updateFaceTracks`
- hand 左右槽位、second pass、miss 不输出策略 -> `updateHandTracks`
- 统一输出 sanitize/clamp 与非法框过滤 -> `SanitizeDetectBoxToImage` / `PublishSanitizedTrack`
- 导出兼容层 -> `fuse_algorithm.cpp`、`handpose_model.cpp`、`humanpose_model.cpp`
- 预测残留抑制 -> body / face / hand 命中更新路径中的 detection-dominant update 与 motion-state 重建点；实现上落在各自命中更新分支，而不是独立的统一导出层

## 0.5 Matching And Lifecycle

### 0.5.1 body

- body 使用扩展方阵 + 匈牙利匹配。
- 真实匹配代价高于 `dummyLoss` 时，倾向于“不匹配”。
- 新 body 通过 `allocateBodyTrackId` 分配 id。
- body 匹配仍使用预测框参与关联；命中检测后的更新不再完全沿校正后的滤波框输出，而是用检测主导融合，并在明显反向/过冲时抑制旧速度残留。

### 0.5.2 face

- face 在 body 邻域内优先匹配。
- 若已有 face 轨迹，优先按预测框与检测框匹配。
- 若没有当前 body 命中，也会对未匹配 face 做全局二次匹配。
- face 命中检测后，输出框完全使用检测框；若出现明显反向/过冲，则重建 CV state，避免下一帧继续沿旧方向外推。

### 0.5.3 hand

- hand 先按 body 局部候选与左右槽位做一次分配。
- 之后对未匹配槽位做 second pass 全局匹配。
- hand miss 时只推进内部 miss 生命周期，不再把 `predBox` 推进到对外输出框。
- hand / face / body 现在统一按命中门限决定是否允许对外输出；hand 不再保留短 miss window 输出。
- hand 命中检测后，输出框完全使用检测框；miss 路径不再向下游输出预测框。
- 命中检测且出现明显反向/过冲时，会重建 CA state，降低旧加速度对下一帧预测的延续。

## 0.6 Current Implementation Constraints

- face / hand 的 key 语义仍围绕 `bodyId` 建模，说明当前系统仍以 body 为统一身份锚点。
- retired body 只作为 handoff 和 orphan child 清理的历史锚点，不直接对外输出。
- 当前实现为了保留解耦 child，会有 orphan face / hand 兜底输出路径，这也是区域级唯一性尚未完全闭合的直接原因。
- `m_humanTrackResultMap` 只在导出层作为 body 兼容映射，不是 tracking 上游事实源。
- 当前实现并未把 `tracking_interfaces_evidence` 提升为默认实现输入；其接口事实已经并入本文件和 spec。

## 0.7 Known Gaps

- 代码里存在“body 关联最佳 child + orphan child fallback 输出”的双路径。
- 运行级验证仍待补。
- 仅靠本文件和 code facts 可以恢复当前实现框架，但不能把运行级区域唯一性当成已闭合结论。

## 0.8 Historical Mapping

- 03-24 delta 落地了 body/face/hand 主框架。
- 03-25 delta 收敛了上游事实源、左右手槽位、retired body handoff 清理与输出契约。
- 03-31 delta 收敛了 hand continuity 优化与短 miss 输出。
- 04-05 delta 收敛了快速运动恢复阶段的预测残留抑制。
- 04-07 delta 收敛了 tracking 输出框统一 sanitize/clamp，并把 hand miss 输出语义对齐到 face/body。
- 原 `tracking_interfaces_evidence` 的当前有效接口事实已并入本文件。

## 0.9 Current Sync Rule

- must_update_when:
  - `DmsTrack::Update` 的主顺序变化
  - `m_bodyTracks / m_retiredBodyTracks / m_faceTracks / m_bodyHandTracks` 结构变化
  - `AtomicResult` 四类 tracking map 或 body 兼容映射变化
  - hand miss 输出策略、统一 sanitize/clamp 或 orphan fallback / hand second pass 逻辑变化
  - `track_params.json` 的 DEFAULT 读取或车型覆盖规则变化
- absorbs_history_from:
  - `座舱多目标跟踪实现.md`
  - `多目标跟踪实现闭环记录-2026-03-24.md`
  - `多目标跟踪设计失配修复闭环记录-2026-03-25.md`
  - `多目标跟踪生命周期与手部关联设计失配修复闭环记录-2026-03-25.md`
  - `多目标跟踪手部连续性优化闭环记录-2026-03-31.md`
  - `多目标跟踪快速运动恢复阶段预测更新一致性修复闭环记录-2026-04-05.md`
  - `tracking_interfaces_evidence.md`
- evidence_only_docs:
  - `tracking_interfaces_evidence.md`
- not_a_default_entry_anymore:
  - `座舱多目标跟踪实现.md`
  - `多目标跟踪实现闭环记录-2026-03-24.md`
