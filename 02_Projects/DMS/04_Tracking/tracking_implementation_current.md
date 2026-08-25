---
title: Tracking Implementation Current
summary: Tracking 当前实现文档，以 feat/ljc/track_0825@b0a8da10 为主线更新事实基线，逐步映射 face-first 的 Face、驾驶员选择、Body、Hand 归属门禁、已有轨迹匹配、空侧获取与实际左右发布流程。
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
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/head-first优先于body-first跟踪主线决策记录-2026-05-09.md
  - 02_Projects/DMS/04_Tracking/head-first跟踪方案.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/head-first跟踪代码重构闭环记录-2026-05-23.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack内部结构与可读性重构分析-2026-06-08.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack基线对比与HeadFirst路线收缩设计记录-2026-06-16.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack 当前分支跟踪架构可读性重构闭环记录-2026-08-12.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/Hand跟踪与空侧获取分离及实际左右发布映射记录-2026-08-17.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/副驾手误关联主驾Hand归属门禁修复与板端回灌验证记录-2026-08-25.md
  - 90_Archive/02_Projects/DMS/04_Tracking/Current Maintenance Records/Tracking方案优化与历史实现归档记录-2026-06-16.md
scope: 适用于恢复当前 Tracking 在代码中的主要实现结构、接口事实与行为，不覆盖全部调试历史。
risks:
  - 本文档基于当前代码静态读取、既有编译/审查记录和有限板端样本证据；仍不等价于完整代表性样本集验收。
  - 历史方案、评审结论和每步提交证据保留在 Current Maintenance Records 与 subpower_runs 中，不作为本文主内容。
updated_at: 2026-08-25
---

## 0.1 Core Entry

- 入口类：`UtilsDomain::DmsTrack`
- 主要入口函数：`Init`、`Update`
- 每帧 `Update` 当前顺序为：清空四类 legacy track map -> `updateFaceTracks` -> `selectDriverFace` -> 发布 face map -> `updateBodyTracks` -> `updateHandTracks`。
- `DmsTrack::Init/Update` 是当前 public tracker API；本轮只调整 private/internal 结构。
- 配置入口固定从 `/home/jichao/dms/etc/track_params.json` 读取，先应用 `DEFAULT`，再按车型节点覆盖。
- 代码已实现 face-first driver selection、face-owned Body evidence，以及 stable DRIVER Body-owned Hand slots；当前没有 `camera_type` profile gate 或 body-to-hand finalized snapshot。
- 历史设计来源见 [[head-first跟踪方案]]；current 统一采用 face-first 口径，本文记录当前实现事实。

### 0.1.1 Update 调用链

`DmsTrack::Update` 与代码的逐段对应如下：

| 顺序 | 代码入口 | 输入 | 持久状态变化 | 输出 |
|---|---|---|---|---|
| 1 | `Update` clear | 上一帧 `AtomicResult` 输出 | 不清空 tracker member | 清空四类 track map |
| 2 | `updateFaceTracks` | class 0 Face detection | `m_faceTracks`、Face CV、hit/miss、类型票数 | 暂不发布 |
| 3 | `selectDriverFace` | 稳定 active Face | 更新 `m_driverFaceId` | 唯一 DRIVER Face id |
| 4 | `Update` Face publish loop | `m_faceTracks` | 强制新 DRIVER、撤销旧 DRIVER | `m_faceTrackResultMap` |
| 5 | `updateBodyTracks` | class 2 Body detection、已有 Body owner、当帧有效 Face、driver id | `m_bodyTracks`、`m_handTracks` 删除级联、Body CV/hit/miss | `m_bodyTrackResultMap` |
| 6 | `updateHandTracks` | class 1 Hand detection、本帧 Body map | `m_handTracks`、Hand CA/hit/miss、retired cleanup | left/right Hand map |

该调用链是 `face-first`：Face 先产生 identity/key 和 DRIVER；Body/Hand 均不能创建或替换乘员 identity。Body 仍是 Hand 候选域和下游 `m_humanTrackResultMap` 的直接证据，不能从流程说明中省略。

## 0.2 Current State Containers

- 长期内部状态：
  - `m_bodyTracks`
  - `m_faceTracks`
  - `m_handTracks`
- 对外结果：
  - `AtomicResult::m_bodyTrackResultMap`（legacy output projection；也是当前 Hand phase 的本帧 body evidence 输入）
  - `AtomicResult::m_faceTrackResultMap`
  - `AtomicResult::m_leftHandTrackResultMap`
  - `AtomicResult::m_rightHandTrackResultMap`
- 下游兼容与消费：
  - `humanpose_model.cpp` 直接消费 `m_bodyTrackResultMap`
  - `handpose_model.cpp` 分别消费 `m_leftHandTrackResultMap` 与 `m_rightHandTrackResultMap`
  - `fuse_algorithm.cpp` 将 body 兼容映射到 `m_humanTrackResultMap`
- 关键状态语义：
  - `m_bodyTracks` 承载当前 active body 轨迹
  - `m_faceTracks` 承载 face 子轨迹
  - `m_handTracks` 承载以 face-owned Body evidence id 为 key 的 left/right Hand 槽位

## 0.3 Phase Execution Boundary

- 当前没有 `TrackParameters::enableBodyTracking / enableHandTracking`，也不读取 `camera_type` 控制 Body/Hand phase。
- Body 和 Hand 在每帧 Face/driver 选择后执行；6 月分支中的 profile gate 没有进入当前待合入分支。

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
- Face id 分配 -> `allocateFaceTrackId`
- DRIVER Face 选择 -> `selectDriverFace`
- face-owned Body evidence -> `updateBodyTracks`
- Face 常规匹配、DRIVER small-face filtering、Face continuity gate -> `updateFaceTracks`
- driver face 防后排误绑定 -> `selectDriverFace`、`FaceSmallerThanReferenceLoss`、`FaceLargerThanReferenceGain`、`TrackParameters::driverFaceAnchor*`
- hand 已有轨迹匹配、Body 候选域、空侧 acquisition、miss 不输出与实际左右发布 -> `updateHandTracks`
- 统一输出 sanitize/clamp 与非法框过滤 -> `SanitizeDetectBoxToImage` / `PublishSanitizedTrack`
- 导出兼容层 -> `fuse_algorithm.cpp`、`handpose_model.cpp`、`humanpose_model.cpp`
- Face 纯计算 helper -> `.cpp` anonymous namespace 的 `CollectDetectionsByClass` / `BuildFaceAssignmentLoss`
- Body 匹配与选择 helper -> `.cpp` anonymous namespace 的 `TrackBoxMatchLoss` / `PredictAndSelectTrackedBodyDetection` / `SelectFaceAnchoredBodyDetection`
- Hand private 子阶段 -> `trackExistingHands` / `acquireEmptyHandSlots` / `cleanupExpiredHandSlots` / `publishHands`

## 0.6 Matching And Lifecycle

### 0.6.1 face

1. `CollectDetectionsByClass(..., kFaceClassId)` 从 `m_detResultMap` 收集 class 0 Face。
2. 遍历 `m_faceTracks`，对每条轨迹调用 `PredictMotion(..., kDt)`；Face 使用 CV 状态 `[cx,cy,w,h,vx,vy]`，预测结果写入 `predBox`。
3. `BuildFaceAssignmentLoss` 构造 `(detectionCount + trackCount)` 方阵：
   - 左上角是真实 detection-track edge；
   - detection/track 两侧对角 dummy edge 为 `face.dummyLoss`；
   - 右下角 dummy-to-dummy 为 `0`；
   - 其余禁止边为 `1e6f`。
4. `BuildFaceTrackMatchScore` 计算真实 edge：

   `total = (1-IoU(pred,det)) + computeDistanceLoss(pred,det) + 2 × FaceSizeContinuityLoss(previousBox,det)`。

   `computeDistanceLoss` 不是中心距：它取左上角与右下角偏移的较大值，再除以两框联合包围框对角线。尺寸项是宽高对数比绝对值之和。
5. 稳定 DRIVER track 对小脸 detection 直接保留 forbidden cost。距离门禁对 DRIVER 为 `0.45`，其他为 `0.65`；`total >= face.dummyLoss` 同样禁止真实匹配。
6. `hungarian` 求全局最小匹配。只有 assignment 指向真实 track 且 edge cost 小于 dummyLoss 才命中。
7. 命中时 `CorrectMotion` 用 detection `[cx,cy,w,h]` 修正 CV；实现随后把 `box` 和 `predBox` 都设为 detection，而不是使用 corrected rect；再执行 `AdvanceHit`、即时人员分类、投票和稳定分类解析。
8. 未使用 detection 创建新 Face：`allocateFaceTrackId` 在 `[0,119]` 中避开 Face/Body/Hand 已占 key；初始化 CV、`hitCount=1`、`missCount=0` 并记录首次类型票。
9. 未命中 Face 执行 `AdvanceMiss`；`hitCount` 减一、`missCount` 加一；达到 `face.missThreshold` 时从 `m_faceTracks` 删除。

### 0.6.1.1 人员类型稳定化

- `computePersonType` 按 Face 中心点做即时分类：driver ROI 内通常为 DRIVER，但 driver ROI 内小脸直接为 BACK_PASSENGER；front-passenger ROI 内为 FRONT_PASSENGER；其余为 BACK_PASSENGER。
- `AccumulatePersonVote` 累计 `driverCount / frontPassengerCount / backPassengerCount`。
- `ResolveStablePersonType` 在总票数小于 `typeMinVotes` 时保持原 `stablePersonType`；达到门槛后，只有最高票占比不低于 `typeRatioThreshold` 才切换稳定类型。
- 因而“滤波”和“分类”是串联但独立的机制：CV 预测/修正保证框的空间连续性；ROI 即时分类与多帧投票决定人员类型。

### 0.6.1.2 真正驾驶员 Face 选择

`selectDriverFace` 不直接使用所有 Face detection，而是在更新完成的稳定 Face track 中二次过滤：

1. 要求 `missCount==0` 且 `hitCount>=face.hitThreshold`。
2. 要求中心在 driver ROI，且不在 front-passenger ROI。
3. 拒绝 `stablePersonType==BACK_PASSENGER` 和面积占比小于 `smallFaceAreaRatio` 的小脸。
4. 上一帧 DRIVER 若仍有效，作为尺寸参考；`FaceSmallerThanReferenceLoss > 0.70` 的候选拒绝。
5. 对剩余候选计算：

   `score = smallerPenaltyWeight×smallerLoss + anchorWeight×anchorLoss - largerBonusWeight×largerGain + continuityBonus`。

   `anchorLoss` 按 driver ROI 宽高归一化；上一帧同 id 的 `continuityBonus=-0.50`。取最低分 id。
6. `Update` 发布 Face 时把该 id 强制为 DRIVER；其他原 stable DRIVER 被改为 FRONT_PASSENGER 或 BACK_PASSENGER，并清零 `driverCount`，保证本帧只保留一个 DRIVER Face。

### 0.6.2 body

1. `CollectDetectionsByClass(..., kBodyClassId)` 收集 class 2 Body。Body 不分配独立 id，`m_bodyTracks` 的 key 继承 owner Face id。
2. 第一阶段遍历已有 Body：当前 DRIVER owner 优先，其次为仍标记 DRIVER 的 Body，再处理其他 Body。只要 owner Face track 尚在 `m_faceTracks`，Face 短时 miss 不阻断 Body tracking。
3. `PredictAndSelectTrackedBodyDetection` 调用 CV `PredictMotion`，再从未占用 detection 中最小化：

   `L_body_track = 10 × (1-IoU(predBody,detBody)) + computeDistanceLoss(predBody,detBody)`。

   最小 loss 不低于 `body.dummyLoss` 时视为 tracking 失败。
4. 第二阶段只遍历 `missCount==0 && hitCount>0` 的当帧有效 Face。已有 Body tracking 失败或尚未绑定 Body 时，`SelectFaceAnchoredBodyDetection` 执行获取/重获取。`FaceBelongsToBody` 要求 Face 中心位于 Body 横向扩张 15%、顶部扩张 10%、向下 60% 高度的区域；合格候选再最小化：

   `L_body_acquire = |faceCx-bodyCx|/bodyW + |faceCy-(bodyTop+0.25×bodyH)|/bodyH`。

   当前获取路径没有额外 dummyLoss 截断。
5. 命中后把 detection 标为 used。首次绑定用 detection 初始化 CV；已有轨迹用 `CorrectMotion` 修正，并将 corrected rect 回写为 Body `box`。人员类型直接继承 owner Face；随后 `AdvanceHit`。
6. 第三阶段统一应用命中；只有 Body tracking/acquisition 均未命中时才 `AdvanceMiss`。Face 短时 miss 但 Body tracking 命中时执行 `AdvanceHit`。Face 已删除或 Body `missCount>=body.missThreshold` 时，从 `m_bodyTracks` 删除 Body并同步 `m_handTracks.erase(ownerFaceId)`。
7. 发布要求 Body hit 达门槛、owner Face 仍存在且 Face hit 也达门槛。输出 key 是 owner Face id；DRIVER 和非 DRIVER 的稳定 Body 都可能发布。

### 0.6.3 hand

1. `updateHandTracks` 收集 class 1 Hand，并把本帧 `m_bodyTrackResultMap` 作为 `bodyEvidence`。只有 `stablePersonType==DRIVER` 的 Body key 进入 `allowedHandIds`；Hand 直接继承该 `trackId`。当前不再对 Body 做 30% 横向扩张。
2. 每个继承 id 在 `m_handTracks[trackId]` 下固定持有 left/right 两个 `HandSideState`。这里的 left/right 是图像坐标侧。已初始化 Hand 先用 CA `PredictMotion` 产生 `predBox`；CA 状态包含位置、尺寸、速度、加速度和尺寸速度。
3. `trackExistingHands` 是 first pass：
   - 对每个 allowed id 收集已经初始化的侧别；assignment row 表示已有 Hand track，不表示 Body 空槽；
   - `IsDriverHandCandidate` 先调用 `HandBelongsToBody`：要求 Hand/Body 面积比不小于 `minHandBodyAreaRatio=0.01`，且 Hand 中心位于 Body 或 `BoxIntersectionOverHand` 不小于 `minHandBodyOverlapRatio=0.5`；若另一非主驾 Body 包含 Hand 中心而主驾不包含，或其交叠占比更高，则拒绝主驾候选；
   - 构造 `(trackCount + candidateCount)` 方阵，真实边统一使用 `HandMatchLoss = 5×NormalizedCenterDistance + HandSizeContinuityLoss + 1.5×(1-IoU) + 0.75×HandAnchorLoss`；
   - 匈牙利 assignment 的 cost 必须严格小于 `hand.dummyLoss`。命中时修正 CA、把 `box/predBox` 设为 detection 并推进 hit；未命中时在本阶段直接 `AdvanceMiss`。
4. `acquireEmptyHandSlots` 是 second pass：只收集尚未初始化的图像侧，并只消费 first pass 后仍未使用且通过同一 `IsDriverHandCandidate` 门禁的 detection。每个 allowed id 构造 `(slotCount + candidateCount)` 方阵，真实边使用 `HandAnchorLoss`；命中后初始化 CA、`hitCount=1`、`missCount=0`。已有轨迹不进入这一矩阵，因此 acquisition 不能抢走已由 tracking 匹配的 detection。
5. `cleanupExpiredHandSlots`：miss 达 `hand.missThreshold` 的单侧状态 reset；两侧均未初始化时删除空 Hand state。Body 删除时已同步删除同 id Hand，因此不再执行 retired-body/orphan 空间清理。
6. `publishHands`：只遍历 allowed DRIVER id；Hand 必须 initialized、hit 达门槛且再次通过同一 `IsDriverHandCandidate` 门禁。发布保留继承 key，但交换内部图像侧到实际侧：image-left 写 `m_rightHandTrackResultMap` 并把输出副本设为 `RIGHT_HAND`，image-right 写 `m_leftHandTrackResultMap` 并设为 `LEFT_HAND`。`PublishSanitizedTrack` 仍作用于内部轨迹，保持非法框推进 miss 的既有副作用；miss 预测框不对外发布。

## 0.7 Current Implementation Constraints

- Face / Body / Hand 对外仍使用 legacy 四类 map；同一 driver occupant 的 Body/Hand key 当前来源于 DRIVER Face trackId。
- Hand 不创建独立 identity；`m_handTracks`、Body evidence 和输出 map 使用同一个继承 `trackId`。
- retired Body 容器和同区域 orphan Hand 清理路径已移除；Hand 生命周期在 Body 删除点收敛。
- 当前实现保留 Face/Hand 的内部连续性；Hand 对外输出 key 已收敛为当前 DRIVER face-owned Body evidence id，但区域级唯一性仍需运行验证。
- `m_humanTrackResultMap` 只在导出层作为 body 兼容映射，不是 tracking 上游事实源。
- 当前实现并未把 `tracking_interfaces_evidence` 提升为默认实现输入；其接口事实已经并入本文件和 spec。
- `curResult->m_bodyTrackResultMap` 同时承担 body output projection 和 Hand 本帧候选域输入。
- `track.h` 当前 private surface 新增四个 Hand 子阶段；Face/Body 的无状态计算 helper 保持在 `.cpp` anonymous namespace，避免扩大类接口。
- Hand owner 几何与竞争归属 helper 保持在 `.cpp` anonymous namespace；`track.h` 只增加两个内部配置参数，没有改变 `DmsTrack::Init/Update` 或外部 SDK ABI。

## 0.8 Known Gaps

- 修复已提交为 `b0a8da10`；提交前同内容构建产物已完成 J6B 编译、SDK 校验部署和 `/ota/dump` 999 帧回灌。当前没有新增单元测试，也未覆盖缺失的 `/ota/TC001` 与 `/ota/TC004`；6 月 profile/snapshot 路线不是当前实现。
- Body tracking 失败后会立即走无额外 dummy 门槛的 Face-anchor selection；这是主驾 Body 消失后可能选到副驾 Body 的直接风险点。
- tracking 与 acquisition 已分离，但手跨中线、双手交叉或长漏检后重新 acquisition 的稳定性仍需代表性序列验证。
- 图像侧到实际侧当前为固定交换；若输入链存在水平翻转，需要配置化或按输入方向选择映射。
- `updateHandTracks` 已拆出四个职责明确的 private 子阶段；`usedDetections` 是 tracking 到 acquisition 的关键阶段边界。
- 仅靠本文件和 code facts 可以恢复当前实现框架，但不能把运行级区域唯一性当成已闭合结论。
- face-first 第一轮已实现并本地编译通过；任何后续优化仍必须保持“代码事实”和“运行效果验证”分离。
- Body map 在导出层映射为 `m_humanTrackResultMap` 并供人体相关下游消费；这不是 OccupantTrack，也不是 person/part 状态层。

## 0.9 Historical References

- 历史实现、方案取舍、每步验证和 superseded plan 只在 `Current Maintenance Records/`、`subpower_runs/` 与结构审计中追溯。
- 本文不按日期枚举历史提交；若需要追溯 6 月方案与当前分支差异，读取对应维护记录和 2026-08-12 闭环记录。
- 原 `tracking_interfaces_evidence` 的当前有效接口事实已并入本文和 spec；该文件保留为 evidence/reference only。

## 0.10 Current Sync Rule

- must_update_when:
  - `DmsTrack::Update` 的主顺序变化
  - `m_bodyTracks / m_faceTracks / m_handTracks` 结构或删除级联变化
  - `AtomicResult` 四类 tracking map 或 body 兼容映射变化
  - hand miss 输出策略、统一 sanitize/clamp、已有轨迹匹配、空侧 acquisition 或发布映射变化
  - `track_params.json` 的 DEFAULT 读取或车型覆盖规则变化
  - face-first driver selection、face-owned Body、Hand 继承 id 来源或 private phase 边界任一变化
- evidence_only_docs:
  - `tracking_interfaces_evidence.md`
- not_a_default_entry_anymore:
  - `座舱多目标跟踪实现.md`
  - `多目标跟踪实现闭环记录-2026-03-24.md`
