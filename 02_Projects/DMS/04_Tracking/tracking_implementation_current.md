---
title: Tracking Implementation Current
summary: Tracking 当前实现文档，记录当前代码仓中 DmsTrack 的入口、状态、Face/Body/Hand phase、profile gate、body-to-hand snapshot 和验证缺口；不枚举历史提交或预期方案。
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
  - 90_Archive/02_Projects/DMS/04_Tracking/座舱多目标跟踪实现.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪实现闭环记录-2026-03-24.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/tracking_interfaces_evidence.md
merged_into: []
current_replacement: []
related_code:
  - /home/jichao/dms/include/utils/track.h
  - /home/jichao/dms/source/utils/track.cpp
  - /home/jichao/dms/etc/track_params.json
  - /home/jichao/dms/etc/track_params_2m.json
sources:
  - 90_Archive/02_Projects/DMS/04_Tracking/座舱多目标跟踪实现.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪实现闭环记录-2026-03-24.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪设计失配修复闭环记录-2026-03-25.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪生命周期与手部关联设计失配修复闭环记录-2026-03-25.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪手部连续性优化闭环记录-2026-03-31.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪快速运动恢复阶段预测更新一致性修复闭环记录-2026-04-05.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/跟踪框越界导致板端coredump调查与修复闭环记录-2026-04-07.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/2m摄像头后排head误绑定主驾修复闭环记录-2026-05-08.md
  - /home/jichao/dms/include/utils/track.h
  - /home/jichao/dms/source/utils/track.cpp
  - /home/jichao/dms/etc/track_params.json
  - /home/jichao/dms/etc/track_params_2m.json
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/head-first优先于body-first跟踪主线决策记录-2026-05-09.md
  - 02_Projects/DMS/04_Tracking/head-first跟踪方案.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/head-first跟踪代码重构闭环记录-2026-05-23.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack内部结构与可读性重构分析-2026-06-08.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack基线对比与HeadFirst路线收缩设计记录-2026-06-16.md
  - 90_Archive/02_Projects/DMS/04_Tracking/Current Maintenance Records/Tracking方案优化与历史实现归档记录-2026-06-16.md
scope: 适用于恢复当前 Tracking 在代码中的主要实现结构、接口事实与行为，不覆盖全部调试历史。
risks:
  - 本文档基于当前代码静态读取、既有编译/审查记录和有限板端样本证据；仍不等价于完整代表性样本集验收。
  - 历史方案、评审结论和每步提交证据保留在 Current Maintenance Records 与 subpower_runs 中，不作为本文主内容。
updated_at: 2026-06-17
---

## 0.1 Core Entry

- 入口类：`UtilsDomain::DmsTrack`
- 主要入口函数：`Init`、`Update`
- 每帧 `Update` 当前顺序为：清空四类 legacy track map -> `updateFaceTracks` -> `selectDriverFace` -> 发布 face map -> 按 profile 执行 `updateBodyTracks` -> 按 profile 执行 `updateHandTracks`。
- `DmsTrack::Init/Update` 是当前 public tracker API；2m/5m profile、driver body evidence 和 hand body input snapshot 都没有新增 public API。
- 配置入口固定从 `/home/jichao/dms/etc/track_params.json` 读取，先应用 `DEFAULT`，再按车型节点覆盖。
- 代码已实现 head-first driver selection、driver face-bound body/torso evidence、基于 `camera_type` 的 2m/5m 第一层 profile 分流，以及 body-to-hand finalized snapshot 隔离。
- head-first 设计细节见 [[head-first跟踪方案]]；本文记录当前实现事实。

## 0.2 Current State Containers

- 长期内部状态：
  - `m_bodyTracks`
  - `m_retiredBodyTracks`
  - `m_faceTracks`
  - `m_bodyHandTracks`
- 对外结果：
  - `AtomicResult::m_bodyTrackResultMap`（legacy output projection；不再作为 hand 内部输入）
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
  - `m_bodyHandTracks` 承载以 head-owned body evidence id 为 key 的 left/right hand 槽位

## 0.3 Profile Gate

- `TrackParameters` 当前包含 `enableBodyTracking` 与 `enableHandTracking`，默认 `true`。
- `loadConfigFromJson` 读取 `camera_type`；`camera_type == "2m"` 时关闭 body/hand tracking，其他值保持 body/hand 开启。
- `Update` 在 body disabled 时清理 `m_bodyTracks` 与 `m_retiredBodyTracks`；在 hand disabled 时清理 `m_handTracks`。
- face/head update、driver face selection 和 face output 不受 body/hand profile gate 关闭影响。

## 0.4 Motion Models

- body：恒速度 KF。
- face：恒速度 KF。
- hand：恒加速度 KF，状态包含位置、尺寸、速度、加速度和尺寸变化速度。
- body / face / hand 均使用预测作为匹配输入；命中后输出优先使用检测或检测主导修正结果，miss 路径不向下游发布 hand 预测框。
- body / face / hand 写入 `AtomicResult::*TrackResultMap` 前经过 track 内部 sanitize/clamp；非法框直接丢弃。

配置来自 `/home/jichao/dms/etc/track_params.json`，按 `DEFAULT` 或车型节点加载 body / face / hand 的 threshold 与 kalman 参数。

## 0.5 Spec-to-Code Mapping

- 人员类型投票与稳定解析 -> `AccumulatePersonVote` / `ResolveStablePersonType`
- 配置读取与 `DEFAULT` / 车型覆盖 -> `loadConfigFromJson`
- head/face id 分配 -> `allocateFaceTrackId`
- driver face/head 选择 -> `selectDriverFace`
- driver face-bound body evidence -> `updateBodyTracks`
- face/head 常规匹配、driver small-face filtering、face continuity gate -> `updateFaceTracks`
- driver face 防后排误绑定 -> `selectDriverFace`、`FaceSmallerThanReferenceLoss`、`FaceLargerThanReferenceGain`、`TrackParameters::driverFaceAnchor*`
- hand 左右槽位、body-constrained candidate、second pass、miss 不输出策略 -> `updateHandTracks`
- 统一输出 sanitize/clamp 与非法框过滤 -> `SanitizeDetectBoxToImage` / `PublishSanitizedTrack`
- 导出兼容层 -> `fuse_algorithm.cpp`、`handpose_model.cpp`、`humanpose_model.cpp`
- 2m/5m profile gate -> `TrackParameters::enableBodyTracking` / `enableHandTracking`
- body-to-hand finalized snapshot -> `updateBodyTracks` 返回值与 `updateHandTracks(..., driverBodyEvidence)` 参数

## 0.6 Matching And Lifecycle

### 0.6.1 face

- face/head 不再依附 body 邻域启动，先于 body evidence 更新。
- 已有 face 轨迹按预测框与 face detection 做匈牙利匹配。
- face 匹配损失综合 IoU、距离和 size continuity；driver 相关使用更严格的 `distanceLoss <= 0.45`，其他为 `0.65`，且总分必须小于 face `dummyLoss`。
- 未匹配 face detection 通过 `allocateFaceTrackId` 创建新的 head/face track。
- face 命中后更新 CV state、hit/miss 和 person type vote。
- `selectDriverFace` 负责最终 driver identity；被选中的 face track 强制投影为 `DRIVER`，旧 driver face 若本帧未被选中会退出 `DRIVER`。
- driver face selection 拒绝稳定 `BACK_PASSENGER` 候选，并用配置化 preferred anchor、变小惩罚和变大增益抑制后排误绑定。

### 0.6.2 body

- body/torso 不再独立分配 id；`m_bodyTracks` 以 selected driver face/head trackId 为 key。
- `updateBodyTracks` 只构造当前 selected driver face owner；非 driver face 不参与 body acquisition。
- 已有 driver body track 先按自身 motion prediction 与 body detection 匹配；若 tracking loss 不满足 `body.dummyLoss`，当前代码会回退到基于当前 driver face 几何的 acquisition/reacquisition。
- acquisition 候选必须满足 `FaceBelongsToBody`，并使用 `FaceAnchorLoss` 在候选 body 中选择。
- 非当前 driver owner 的旧 body cache 推进 miss，不发布；miss 达阈值或 owner face 不存在时转入 `m_retiredBodyTracks` 并从 active body map 删除。
- body publish 显式要求 `ownerFaceId == driverFaceId`、body 达到 hit threshold、owner face 达到 face hit threshold；发布 key 使用 driver face/head trackId。
- `updateBodyTracks` 返回 `std::map<track_id, TrackInfo>`，只包含本帧已经成功 sanitize/publish 的 driver body evidence。

### 0.6.3 hand

- `updateHandTracks` 只消费 `updateBodyTracks` 返回的 `driverBodyEvidence`，不再从 `curResult->m_bodyTrackResultMap` 反读 body 输入。
- allowed hand owner 只来自 stable `DRIVER` 的 driver body evidence。
- hand 先按 driver body evidence 约束的候选与左右槽位做一次分配；之后对未匹配槽位做 second pass，但仍必须受当前 owner body evidence 几何约束。
- hand miss 时只推进内部 miss 生命周期，不再把 `predBox` 推进到对外输出框。
- hand / face / body 现在统一按命中门限决定是否允许对外输出；hand 不再保留短 miss window 输出。
- hand 命中检测后，输出框使用检测框；miss 路径不向下游输出预测框。
- 命中检测且出现明显反向/过冲时，会重建 CA state，降低旧加速度对下一帧预测的延续。
- 当前实现中 `updateHandTracks` 使用函数局部 lambda 组织 owner 收集、slot 预测、body-constrained candidate 收集、unmatched miss、过期 slot reset 和 publish 条件；这些 lambda 是当前 `.cpp` 局部机制，不是稳定 private API。

## 0.7 Current Implementation Constraints

- face / body / hand 对外仍使用 legacy 四类 map；同一 driver occupant 的 body/hand key 当前来源于 driver face/head trackId。
- hand 代码中的 legacy 变量名仍包含 `bodyId`；当前语义应理解为 head-owned body evidence id，不代表 body identity owner。
- retired body 只作为 handoff 和 orphan child 清理的历史锚点，不直接对外输出。
- 当前实现保留 head/hand 的内部连续性；hand 对外输出 key 已收敛为当前 driver head-owned body evidence id，但区域级唯一性仍需运行验证。
- `m_humanTrackResultMap` 只在导出层作为 body 兼容映射，不是 tracking 上游事实源。
- 当前实现并未把 `tracking_interfaces_evidence` 提升为默认实现输入；其接口事实已经并入本文件和 spec。
- `curResult->m_bodyTrackResultMap` 只承担每帧 clear 和 body output projection，不承担 hand 内部 body truth source。
- `track.h` 当前 private surface 保持 phase-level 方法；局部 collect/predict/publish/miss 机制没有提升为 header-level step helper。

## 0.8 Known Gaps

- 2m/5m profile 分流、5m driver-bound body evidence 和 body-to-hand snapshot 已有本地编译与静态审查证据，但缺少 runtime replay、单元测试和代表性视频验证。
- 代码里仍存在 hand slot 内部 fallback 输出路径，但输出 key 已要求回到当前 driver head-owned body evidence id。
- `updateHandTracks` 仍是高复杂度函数，局部 lambda 提高了结构性，但没有真正降低所有 phase 的阅读复杂度。
- 仅靠本文件和 code facts 可以恢复当前实现框架，但不能把运行级区域唯一性当成已闭合结论。
- head-first 第一轮已实现并本地编译通过；任何后续优化仍必须保持“代码事实”和“运行效果验证”分离。
- HumanPose 当前由 driver body map 触发并产出 `m_humanPoseResult`；这不是 OccupantTrack，也不是 person/part 状态层。

## 0.9 Historical References

- 历史实现、方案取舍、每步验证和 superseded plan 只在 `Current Maintenance Records/`、`subpower_runs/` 与结构审计中追溯。
- 本文不再按日期枚举历史提交；若需要追溯 2026-06-17 三笔 hand lambda 提交、整体架构评审或基线路线收缩，读取对应维护记录。
- 原 `tracking_interfaces_evidence` 的当前有效接口事实已并入本文和 spec；该文件保留为 evidence/reference only。

## 0.10 Current Sync Rule

- must_update_when:
  - `DmsTrack::Update` 的主顺序变化
  - `m_bodyTracks / m_retiredBodyTracks / m_faceTracks / m_bodyHandTracks` 结构变化
  - `AtomicResult` 四类 tracking map 或 body 兼容映射变化
  - hand miss 输出策略、统一 sanitize/clamp 或 orphan fallback / hand second pass 逻辑变化
  - `track_params.json` 的 DEFAULT 读取或车型覆盖规则变化
  - head-first driver selection、profile 选择、head-bound body/torso、hand owner source 任一实现落地
- evidence_only_docs:
  - `tracking_interfaces_evidence.md`
- not_a_default_entry_anymore:
  - `座舱多目标跟踪实现.md`
  - `多目标跟踪实现闭环记录-2026-03-24.md`
