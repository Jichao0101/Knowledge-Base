---
title: Tracking Design Current
summary: Tracking 当前设计文档，记录 face-first 架构、Face/Body/Hand 完整跟踪流程、Face 稳定行为保护及 DmsTrack phase 可读性边界。
status: verified
doc_role: current
truth_role: current
current_kind: design
lifecycle_state: active
default_entry: false
sync_required_when:
  - 当前设计目标变化
  - body/face/hand 分层关系变化
  - 生命周期或 handoff 原则变化
  - 区域级唯一性边界变化
retrieval_priority: current
supersedes:
  - 02_Projects/DMS/04_Tracking/座舱乘员多目标跟踪方案.md
  - 90_Archive/02_Projects/DMS/04_Tracking/座舱多目标跟踪实现.md
merged_into: []
current_replacement: []
related_code:
  - /home/jichao/dms/include/utils/track.h
  - /home/jichao/dms/source/utils/track.cpp
sources:
  - 02_Projects/DMS/04_Tracking/座舱乘员多目标跟踪方案.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪设计失配修复闭环记录-2026-03-25.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪生命周期与手部关联设计失配修复闭环记录-2026-03-25.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪功能审核记录-2026-03-27.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪手部连续性优化闭环记录-2026-03-31.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪快速运动恢复阶段预测更新一致性修复闭环记录-2026-04-05.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/head-first优先于body-first跟踪主线决策记录-2026-05-09.md
  - 02_Projects/DMS/04_Tracking/head-first跟踪方案.md
  - 02_Projects/DMS/04_Tracking/tracking_implementation_current.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack基线对比与HeadFirst路线收缩设计记录-2026-06-16.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack 当前分支跟踪架构可读性重构闭环记录-2026-08-12.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/Face遮挡期间Body续跟与Hand级联生命周期修复闭环记录-2026-08-12.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/Hand跟踪与空侧获取分离及实际左右发布映射记录-2026-08-17.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/副驾手误关联主驾Hand归属门禁修复与板端回灌验证记录-2026-08-25.md
  - 90_Archive/02_Projects/DMS/04_Tracking/Current Maintenance Records/Tracking方案优化与历史实现归档记录-2026-06-16.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack基线对比与HeadFirst路线收缩设计记录-2026-06-16.md
  - /home/jichao/dms/source/utils/track.cpp
scope: 适用于恢复当前 Tracking 的设计真相，重点描述目标、边界、层级、生命周期和设计原则；不单独承担完整实现规范职责。
risks:
  - 文档明确区分“当前设计目标”和“当前代码已证实行为”；对未被代码静态证据完全支撑的项保持保守表述。
updated_at: 2026-08-25
---

## 0.1 Current Goal

当前代码采用 `face-first` 架构：Face track 先建立身份、分配 track id 并选择唯一驾驶员；Body 随后以 Face track 为 owner 更新；Hand 最后在已发布的 DRIVER Body evidence 范围内维护左右槽位。对外仍输出 `body / face / left_hand / right_hand` 四类 legacy 结果。

`face-first` 描述的是身份与执行主线，不表示 Hand 可以绕过 Body：Face 是身份和 key 的唯一来源，Body 是 Face 与 Hand/人体下游之间的关联证据，Hand 仍依赖 Body ROI。当前代码没有 2m/5m profile 分流，也没有把 Body 收缩为仅 selected driver owner。完整代码对应见 [[02_Projects/DMS/04_Tracking/tracking_implementation_current]]。

本文件以当前主线更新基线 `feat/ljc/track_0825@b0a8da10` 为实现事实；运行效果和板端/视频回放仍以 [[02_Projects/DMS/04_Tracking/tracking_validation_current]] 的证据边界为准。

本文件只回答“当前设计是什么”，不回答全部“按什么精确规则实现代码”；实现级硬约束收敛到 [[02_Projects/DMS/04_Tracking/tracking_spec_current]]。

## 0.2 Complete Face-first Frame Flow

每帧由 `DmsTrack::Update` 按以下顺序执行：

1. 清空四类输出 map，但保留 `m_faceTracks / m_bodyTracks / m_handTracks` 等跨帧状态。
2. `updateFaceTracks`：Face CV 卡尔曼预测 → 构造 detection-to-track 损失矩阵 → 匈牙利匹配 → 命中修正、新建轨迹、miss/删除 → 人员类型投票。
3. `selectDriverFace`：只在当前稳定且未 miss 的 Face track 中过滤并评分，选出唯一 `m_driverFaceId`。
4. Face publish：被选中的 Face 强制投影为 `DRIVER`；旧 DRIVER 若未再次选中则退出 DRIVER；达到 hit 门槛的 Face 写入 `m_faceTrackResultMap`。
5. `updateBodyTracks`：按“驾驶员 Face 优先、其余 active Face 随后”的 owner 顺序更新 Body；所有 owner 共享 `usedDetections`，同一个 Body detection 只能被一个 owner 使用。
6. Body publish：达到 Body hit 门槛且 owner Face 也达到 Face hit 门槛后，以 `ownerFaceId` 为 key 写入 `m_bodyTrackResultMap`。
7. `updateHandTracks`：从本帧 Body 输出中只选择 `stablePersonType == DRIVER` 的 owner，预测左右 Hand slot，执行 owner 内 first pass 和全局 unmatched second pass，随后 cleanup 并发布。

因此当前设计的主依赖为：

`Face identity/id -> face-owned Body evidence -> DRIVER Body constrained left/right Hand slots`

### 0.2.1 Face Matching And Driver Selection

Face phase 的算法契约如下：

1. 对每条既有 Face track 调用恒速度卡尔曼 `PredictMotion(dt=1)`，得到 `predBox`。CV 状态为 `[cx, cy, w, h, vx, vy]`；预测只用于关联，不直接作为命中后的输出框。
2. 设本帧 Face detection 数为 `m`、既有 Face track 数为 `n`，构造 `(m+n) × (m+n)` 方阵。左上角是 detection-track 真实代价；两个对角 dummy block 使用 `face.dummyLoss` 表示拒绝；右下角补零；其余 forbidden edge 为 `1e6f`。
3. detection `d` 与 track `t` 的真实代价为：

   `L_face = (1 - IoU(predBox_t, d)) + cornerDistance(predBox_t, d) + 2 × sizeContinuity(box_t, d)`

   其中 `cornerDistance` 取两框左上角距离与右下角距离的较大值，再除以两框联合包围框的对角线；`sizeContinuity = |log(w_d / w_t)| + |log(h_d / h_t)|`。
4. 若原 track 已稳定为 DRIVER，候选 detection 是小脸，则该 edge 直接 forbidden；此外 DRIVER track 的 `cornerDistance` 必须不大于 `0.45`，其他 track 不大于 `0.65`；总损失还必须小于 `face.dummyLoss`。
5. 匈牙利算法在完整方阵上求全局最小匹配。合法命中后，用 detection 测量修正 CV 状态，但 `box/predBox` 都回写为 detection；`AdvanceHit` 令 `hitCount` 饱和加一并把 `missCount` 清零。
6. 未使用 detection 通过 `allocateFaceTrackId` 建立新 Face track，初始 `hitCount=1`、`missCount=0`、CV 速度为零；id 在 `[0,119]` 中循环分配，并避开仍被 Face/Body/Hand 状态占用的 key。
7. 未命中 track 执行 `AdvanceMiss`：`hitCount=max(hitCount-1,0)`、`missCount++`；达到 `face.missThreshold` 后删除。
8. 每次 Face 命中或新建时，先用 ROI 得到即时分类：中心在 driver ROI 为 DRIVER，但 driver ROI 内面积占比小于 `smallFaceAreaRatio` 的小脸记为 BACK_PASSENGER；中心在 front-passenger ROI 为 FRONT_PASSENGER；否则为 BACK_PASSENGER。
9. 即时分类累计到三类票数。总票数达到 `typeMinVotes` 后，只有最高票占比达到 `typeRatioThreshold` 才更新 `stablePersonType`；否则保留原稳定分类。卡尔曼负责空间连续性，投票负责人员类型的时间稳定性，两者不是同一步决策。
10. `selectDriverFace` 只检查 `missCount==0` 且 `hitCount>=face.hitThreshold` 的稳定 Face。候选必须位于 driver ROI、不位于 front-passenger ROI、稳定类型不是 BACK_PASSENGER、且不是小脸。
11. 若上一帧 DRIVER Face 仍有效，以它为尺寸参考；候选相对参考框变小的单向 loss 超过 `0.70` 时直接拒绝。剩余候选按下式取最低分：

    `score = smallerPenaltyWeight × smallerLoss + anchorWeight × anchorLoss - largerBonusWeight × largerGain + continuityBonus`

    `anchorLoss` 是 Face 中心到配置 `driverFaceAnchor` 的归一化距离；上一帧同 id 的 `continuityBonus=-0.50`；变大是恢复增益而不是惩罚。最终只有最低分 Face 成为真正的驾驶员 Face。

### 0.2.2 Body Association

1. 已有 Body 先进入 tracking 阶段；当前 DRIVER owner 优先，其次是仍标记 DRIVER 的已有 Body，再处理其他已有 Body。只要 Face track 尚在 `m_faceTracks`，Face 短时 miss 不阻断 Body 自身 tracking。
2. 已有 Body 做 CV 预测，并在未使用 detection 中最小化 `L_body = 10 × (1-IoU) + cornerDistance`；最小值必须小于 `body.dummyLoss`。
3. 只有 `missCount==0 && hitCount>0` 的当帧有效 Face 可以进入 acquisition 阶段。已有 Body tracking 失败或 owner 尚无 Body 时，以 Face-anchor selection 从剩余 detection 中获取；当前该路径没有额外 dummy 阈值。
4. 命中后 Body 继承 owner Face 的 key 和人员类型；首次绑定初始化 CV，后续用 detection 修正并把滤波后的框作为 `box`；随后推进 hit。
5. Body tracking/acquisition 均未命中时推进 miss；Face track 真正删除，或 Body miss 达门槛时删除 Body，并同步删除同 owner Hand。Face 仅短时 miss 时不会单独触发 Body miss 或删除。

### 0.2.3 Hand Slot Association

1. Hand 只继承本帧已发布且稳定类型为 DRIVER 的 Body `trackId`。同一继承 id 下维护 left/right 两个侧别状态，Hand 不分配独立 identity id；Body 只提供该 id 下的几何候选域。
2. 所有已初始化 Hand track 先用恒加速度模型预测。CA 状态为 `[cx, cy, w, h, vx, vy, ax, ay, vw, vh]`。
3. `trackExistingHands` 先处理已有 Hand track：每个 assignment row 都代表一条已初始化轨迹，只使用 `HandMatchLoss` 与通过 owner gate 的候选构造 `(trackCount + candidateCount)` 方阵。owner gate 要求 Hand/Body 面积比至少 `0.01`，且 Hand 中心位于 Body 或交叠占 Hand 面积至少 `0.5`；若另一非主驾 Body 的中心包含或交叠证据更强，则拒绝该主驾候选：

   `L_hand = 5 × normalizedCenterDistance + sizeContinuity + 1.5 × (1-IoU) + 0.75 × sideAnchorLoss`

   匹配结果必须严格小于 `hand.dummyLoss`；命中则修正 CA 并推进 hit，未命中则在这一阶段直接推进 miss。空侧不进入该矩阵，不能与已有轨迹竞争 detection。
4. `acquireEmptyHandSlots` 只消费 tracking 后仍未使用且通过同一 owner gate 的 detection，并只为尚未初始化的图像 left/right 侧构造 `(slotCount + candidateCount)` 方阵。这里使用 `HandAnchorLoss`，按 Body 中线和纵向中心初始化空侧；合法结果必须严格小于 `hand.dummyLoss`。
5. 达到 `hand.missThreshold` 的单侧状态被 reset；两侧均未初始化时删除空 Hand state。Body 删除时同步删除同 id 的完整 Hand state，不保留 retired Body 空间锚点或 orphan Hand。
6. 发布要求：继承 id 属于本帧稳定 DRIVER Body、Hand 已初始化、hit 达门槛且再次通过同一 owner gate。内部 left/right 是图像坐标侧；对外按驾驶员实际侧交换映射：image-left 写 `m_rightHandTrackResultMap/RIGHT_HAND`，image-right 写 `m_leftHandTrackResultMap/LEFT_HAND`，map key 始终保持继承 id。miss 预测框不对外发布。

## 0.3 Current Internal Architecture Boundary

- public `DmsTrack::Init/Update` 已经形成深接口，不应为内部 phase 重构新增 public API。
- 当前 header private surface 除长期状态、配置/ID 基础能力和四个 phase-level 方法外，还包含 Hand 的已有轨迹匹配、空侧获取、过期清理、发布四个职责明确的 private 子阶段。
- 不把 `solve/apply/advance/finalize/project/publish` 全套执行脚本展开为 header-level private helper；只有在确有独立契约、复用、测试或失败边界时才提升为 private method。
- `FrameBodyView`、`HandAssignmentRow`、`AssignmentResult`、`BodyEdgeMode`、`LifecycleContext/Payload/Eligibility` 不属于当前稳定抽象；优先使用 `.cpp` anonymous namespace、函数局部 struct/lambda、局部 map/vector 或既有 `TrackInfo`。
- face occlusion 下游已有接口和逻辑判断，track 内部当前不新增 face occlusion 业务分支。

## 0.4 Current Layering

- phase 内部按三段式组织：frame-local computation、persistent state transition、output projection；分层不要求 face/body/hand 机械拥有同形 stage。
- frame-local computation 只处理当前帧输入、候选集、loss、assignment 和输出资格判断；结果不得跨帧保存，不得提升为 header 类型。
- persistent state transition 是唯一允许修改 `m_faceTracks`、`m_bodyTracks`、`m_handTracks`、`motionState`、`hitCount`、`missCount` 和 cleanup 的阶段。
- output projection 只读取已完成状态并写 legacy maps；除 sanitize 明确归属于 finalize 外，publish 不得推进 hit/miss、retire、reset 或 owner migration。
- 当前 Hand 直接读取本帧 Body legacy map；已有轨迹匹配与空侧 acquisition 都只在同一继承 id 的 Body 候选域内运行，不再回退内部 Body track。
- 通用 solver 只统一 expanded matrix、dummy、forbidden 和结果解析，不统一各 phase 的 row 方向、领域 gating、cost 或 lifecycle；最小 `AssignmentResult`、solver row 和 slot key 降级到 `.cpp` 或函数局部。
- `face`：当前 driver identity 的主入口，负责稳定 DRIVER Face 选择和后续 Face 模型输入。
- `body`：当前代码中的 face-owned body/torso evidence，不再单独决定 driver identity。
- `hand`：当前代码中按 face-bound Body evidence id 维护图像 `left/right` 两个侧别状态；稳定 DRIVER Body 提供候选域，tracking 后再执行空侧 acquisition 和发布。
- ID 数值来源与生命周期所有权分离：`bodyId / handId` 初始继承 `faceId` 数值和 map key，但 body/hand 不成为独立 identity lifecycle owner；Face 真正删除时级联删除 Body，Body 删除时级联删除 Hand。

## 0.5 Current Lifecycle

### 0.5.1 body/torso evidence

- 以 `body` 检测作为 evidence 输入。
- 已有 Body 只要 owner Face track 尚未删除，即使 Face 短时 miss 也继续做自身预测匹配；selected driver 和既有 DRIVER Body 获得处理顺序优先级。
- 只有当帧有效 Face 可触发首次 acquisition 或 tracking 失败后的 Face-anchor reacquisition；这一路径的身份误绑定风险仍需运行验证。
- Body global assignment、Track/Reacquire/Bootstrap/Forbidden 四态 edge、Reacquire cost band 和 initialized acquisition fallback 均降级为历史实验或未来重启项；只有在多 owner body evidence 成为明确业务目标且具备 replay、loss 分布、冲突样例和 diff 白名单后才重新评估。
- face owner 尚未绑定 body 或已有轨迹匹配失败时，face-anchor selection 可承担获取或重新选择。
- 命中时 `hitCount` 增长并清零 `missCount`，丢失时 `hitCount` 衰减、`missCount` 增长。
- Face 短时 miss 不单独给 Body 增加 miss；Body tracking 未命中才推进 `AdvanceMiss`。Face track 真正删除或 Body `missCount` 达阈值后删除 Body，并级联删除 Hand。
- 达到稳定阈值的 `body` evidence 才对外输出，legacy map key 使用 Face trackId。
- body 的稳定输出不能单独成为 driver identity 的主来源。

### 0.5.2 face

- Face 先于 Body evidence 更新，使用自身预测、size continuity 和 distance gate 匹配当前 Face detection。
- 未匹配 Face detection 通过 Face id 分配入口创建新 identity。
- DRIVER Face 由 `selectDriverFace` 基于 driver ROI、小脸过滤、front passenger 排除、size continuity 和位置 loss 选择。
- 区域级唯一性和运行中 id 连续性仍必须放到 validation 中判定，不在 design 中假装闭合。

### 0.5.3 hand

- 稳定 DRIVER Body evidence 下按同一继承 id 维护 `left/right` 两个内部图像侧状态，而不是统一 hand 池或跨 id global assignment。
- 已有 Hand track 优先匹配；空侧只从剩余 detection 获取，避免 acquisition 与连续轨迹在同一矩阵中竞争。
- Hand 候选域不再依赖 30% 横向扩张 Body；tracking、acquisition、publish 共享面积/中心/交叠门禁，并使用同帧其他 Body 作为竞争归属证据，避免非主驾小手进入或维持主驾 Hand。
- 空侧初始化依赖 DRIVER face-bound Body evidence；初始化后只作为该 id 的 bounded cache，不反向创建、扩大或迁移身份。
- 未命中时 hand 内部可短期保留状态以支持遮挡恢复；对外输出仍要求当前允许发布的 DRIVER body evidence 或等价 owner 证据。
- Hand 在 Body 存活期间可按自身 hit/miss 保留短期槽位状态；Body 删除时同 owner Hand 整体删除，不允许跨 Body 生命周期继续存活或迁移 owner。
- 当前设计保留左右槽位在同一 Body 生命周期内的短期连续性，不保留 retired-body/orphan Hand lifecycle。

## 0.6 Current Identity And Region Rules

- 当前代码中的 driver identity source 来自 Face track；Body/Hand 的 `stablePersonType` 是向 legacy map 投影的 evidence 标签。
- body center ROI 只能作为非最终先验/evidence，不能继续作为主来源。
- `driver` 目标的最终输出唯一由 face-first 的 `selectDriverFace` 表达。
- driver face selection 对后排探头的防护以稳定人员类型、尺寸方向性和 driver face anchor 共同表达：稳定 BACK_PASSENGER 不进入 driver 候选；比当前 driver reference 变小是强惩罚，变大是恢复增益；preferred anchor 作为配置项表达主驾头枕/主驾脸偏好位置。
- driver face selection 不通过收紧 `distanceLoss` 解决本类问题，避免主驾转头或遮挡恢复时因 KF 预测和观测距离偏大而误拒真实主驾。
- `face / body / hand` 当前达到同 key legacy map 投影；是否已经形成运行级区域最终唯一，需要 validation 依据代码和运行证据单独判定。
- 当前设计不把运行时效果验收等同于静态结构设计。

## 0.7 Current Constraints

- `body` 是历史实现主锚点；当前代码已把它降级为 face-owned evidence。
- `hand` 连续性已做特化优化，但仍存在需要运行样本验证的 owner 稳定性风险。
- Occupant/PersonTrack + PartTrack 已评估为非目标方案；当前不采用，不作为第一阶段或后续默认路线。
- 未来 hand tracking 增强优先考虑 HumanPose-assisted hand association，而不是引入完整 OccupantTrack。
- 对“较好的 ID 连续性”只能确认机制已存在，不能确认效果已验收。
- 若要按规范直接实施代码，必须同时读取 [[02_Projects/DMS/04_Tracking/tracking_spec_current]]。
- 设计文件不承载 `sync_mode`、`default_entry_verified` 这类回写决策字段；这类字段只在 overview/validation 中收口。

## 0.8 Known Gaps

- 6 月分支提出的 2m/5m profile、selected-driver-only Body 和 body-to-hand snapshot 没有进入当前待合入分支，只保留为历史设计证据。
- `04da47b8` 已修复 acquisition 与已有 Hand track 同矩阵竞争导致的侧别重建路径；`13efd826` 已在发布边界把图像侧映射为驾驶员实际侧。用户报告单次运行验收通过，但系统性序列验证仍未完成。
- Body 已有轨迹一旦 tracking loss 超过 dummyLoss，会立即进入无额外阈值的 Face-anchor selection；邻近乘员 Body 同时满足 Face ROI 时，存在错误重绑定风险。
- 已有 Hand track 只使用连续性损失，空侧 acquisition 只使用剩余 detection 与 anchor；双手交叉、单手跨过 Body 中线或长时间检测丢失后的重新获取仍需代表性序列验证。
- 实际左右发布映射当前假设输入图像方向固定；若车型或预处理存在水平翻转，必须验证或配置化映射，不能把单次验收推广到所有输入方向。
- 当前 `0.01/0.5` owner gate 只在 `/ota/dump` 单一数据集完成目标样本验证；主驾手贴近 Body 边界、多人 Body 重叠和更多车型的召回风险仍需统计。
- face 区域级唯一输出运行验证：未闭合
- left_hand / right_hand 区域级唯一输出运行验证：未闭合
- 运行时 replay / 视频证据：未闭合
- face-first 第一阶段实现：已本地编译通过；2026-06-12 后排误跟踪主驾问题样本已完成板端回灌验证，更广泛代表性样本仍未闭合

## 0.9 Historical Mapping

- baseline 设计由 [[座舱乘员多目标跟踪方案]] 提供。
- 2026-03-25 与 2026-03-31 的 retired-body handoff 清理作为历史 delta 保留；当前 `3a2ed302` 已用 Body 删除点级联 Hand 的契约替代该实现，不继承 body-first identity 主线。
- 2026-04-05 的快速运动恢复修复只影响实现与验证边界，不改变本文件的设计职责。
- 2026-05-09 决策记录将 body-first 归档为历史主线；本文统一使用 face-first 描述当前代码口径，历史文件名保持不变。

## 0.10 Current Sync Rule

- must_update_when:
  - 主锚点从 body 改变
  - child 解耦策略或 handoff 清理规则改变
  - driver 唯一化或区域级唯一性边界改变
  - hand continuity 的设计目标或风险表述改变
- absorbs_history_from:
  - `座舱乘员多目标跟踪方案.md`
  - `多目标跟踪设计失配修复闭环记录-2026-03-25.md`
  - `多目标跟踪生命周期与手部关联设计失配修复闭环记录-2026-03-25.md`
  - `多目标跟踪功能审核记录-2026-03-27.md`
  - `多目标跟踪手部连续性优化闭环记录-2026-03-31.md`
  - `多目标跟踪快速运动恢复阶段预测更新一致性修复闭环记录-2026-04-05.md`
- evidence_only_docs:
  - `多目标跟踪功能审核记录-2026-03-27.md`
  - `tracking_interfaces_evidence.md`
- not_a_default_entry_anymore:
  - `座舱乘员多目标跟踪方案.md`
  - `座舱多目标跟踪实现.md`
