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
  - 90_Archive/02_Projects/DMS/04_Tracking/Current Maintenance Records/Tracking方案优化与历史实现归档记录-2026-06-16.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack基线对比与HeadFirst路线收缩设计记录-2026-06-16.md
  - /home/jichao/dms/source/utils/track.cpp
scope: 适用于恢复当前 Tracking 的设计真相，重点描述目标、边界、层级、生命周期和设计原则；不单独承担完整实现规范职责。
risks:
  - 文档明确区分“当前设计目标”和“当前代码已证实行为”；对未被代码静态证据完全支撑的项保持保守表述。
updated_at: 2026-08-12
---

## 0.1 Current Goal

当前代码采用 `face-first` 架构：Face track 先建立身份、分配 track id 并选择唯一驾驶员；Body 随后以 Face track 为 owner 更新；Hand 最后在已发布的 DRIVER Body evidence 范围内维护左右槽位。对外仍输出 `body / face / left_hand / right_hand` 四类 legacy 结果。

`face-first` 描述的是身份与执行主线，不表示 Hand 可以绕过 Body：Face 是身份和 key 的唯一来源，Body 是 Face 与 Hand/人体下游之间的关联证据，Hand 仍依赖 Body ROI。当前代码没有 2m/5m profile 分流，也没有把 Body 收缩为仅 selected driver owner。完整代码对应见 [[02_Projects/DMS/04_Tracking/tracking_implementation_current]]。

本文件以待合入主分支的 `feat/ljc/track_0812@244e5300` 为当前事实；运行效果和板端/视频回放仍以 [[02_Projects/DMS/04_Tracking/tracking_validation_current]] 的证据边界为准。

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

1. owner 列表先放入当前 DRIVER Face，再放入其他 `missCount==0 && hitCount>0` 的 Face；这个顺序让 DRIVER 优先占用 Body detection。
2. 若 owner 已有 Body track，先做 CV 预测，并在未使用 detection 中最小化 `L_body = 10 × (1-IoU) + cornerDistance`；最小值必须小于 `body.dummyLoss`。
3. 已有轨迹匹配失败或 owner 尚无 Body 时，进入 Face-anchor selection：Face 中心必须落在 Body 横向扩张 15%、顶部扩张 10%、向下 60% 高度的 ROI 内，再最小化 Face 中心到 Body 顶部 1/4 anchor 的归一化横纵距离之和。当前该回退没有额外 dummy 阈值。
4. 命中后 Body 继承 owner Face 的 key 和人员类型；首次绑定初始化 CV，后续用 detection 修正并把滤波后的框作为 `box`；随后推进 hit。
5. owner Face 消失或本帧未命中时推进 miss；Face 消失或 Body miss 达门槛时转入 `m_retiredBodyTracks` 并从 active Body 删除。

### 0.2.3 Hand Slot Association

1. Hand owner 只来自本帧已发布且稳定类型为 DRIVER 的 Body evidence。每个 owner 固定维护 left/right 两个 slot，Hand 不分配独立 id。
2. 所有已初始化 Hand slot 先用恒加速度模型预测。CA 状态为 `[cx, cy, w, h, vx, vy, ax, ay, vw, vh]`。
3. first pass 在每个 owner 内先过滤 Body ROI 中的 Hand detection，再构造 `max(2, candidateCount)` 方阵。未初始化 slot 使用左右 anchor loss；已初始化 slot 使用：

   `L_hand = 5 × normalizedCenterDistance + sizeContinuity + 1.5 × (1-IoU) + 0.75 × sideAnchorLoss`

   detection 越出 Body ROI 时额外加 `1.0`。左槽惩罚落在 Body 中线右侧的候选，右槽反之。匈牙利结果必须小于 `hand.dummyLoss` 才算命中。
4. first pass 未命中的已初始化 slot 进入 second pass。second pass 把所有 unmatched slot 与所有 Hand detection 放入 `(slotCount+detectionCount)` 方阵，仍要求 owner Body ROI。代码写有“本帧 Body evidence 缺失时回退 `m_bodyTracks`”的表达式；但 unmatched slot 已被 `allowedHandOwners` 过滤，而 allowed owner 正是从本帧 Body evidence 构造，因此正常不变量下应直接取得本帧 Body。合法命中修正 CA 并推进 hit，否则推进 miss。
5. 达到 `hand.missThreshold` 的 slot 被 reset；若新 Body 与 retired Body 满足 `IoU>0.15` 或归一化中心距 `<0.35`，则清理同区域旧 owner 的 orphan Hand。
6. 发布要求：owner 是本帧 allowed DRIVER Body、slot 已初始化、hit 达门槛、Hand 仍位于 owner Body ROI；left/right 分别写入不同 map，但 key 都等于 `ownerFaceId`。miss 预测框不对外发布。

## 0.3 Current Internal Architecture Boundary

- public `DmsTrack::Init/Update` 已经形成深接口，不应为内部 phase 重构新增 public API。
- 当前 header private surface 除长期状态、配置/ID 基础能力和四个 phase-level 方法外，还包含 Hand 的 owner 更新、未匹配恢复、孤儿/过期清理、发布四个职责明确的 private 子阶段。
- 不把 `solve/apply/advance/finalize/project/publish` 全套执行脚本展开为 header-level private helper；只有在确有独立契约、复用、测试或失败边界时才提升为 private method。
- `FrameBodyView`、`HandAssignmentRow`、`AssignmentResult`、`BodyEdgeMode`、`LifecycleContext/Payload/Eligibility` 不属于当前稳定抽象；优先使用 `.cpp` anonymous namespace、函数局部 struct/lambda、局部 map/vector 或既有 `TrackInfo`。
- face occlusion 下游已有接口和逻辑判断，track 内部当前不新增 face occlusion 业务分支。

## 0.4 Current Layering

- phase 内部按三段式组织：frame-local computation、persistent state transition、output projection；分层不要求 face/body/hand 机械拥有同形 stage。
- frame-local computation 只处理当前帧输入、候选集、loss、assignment 和输出资格判断；结果不得跨帧保存，不得提升为 header 类型。
- persistent state transition 是唯一允许修改 `m_faceTracks`、`m_bodyTracks`、`m_handTracks`、`m_retiredBodyTracks`、`motionState`、`hitCount`、`missCount` 和 cleanup 的阶段。
- output projection 只读取已完成状态并写 legacy maps；除 sanitize 明确归属于 finalize 外，publish 不得推进 hit/miss、retire、reset 或 owner migration。
- 当前 Hand 直接读取本帧 Body legacy map；second pass 保留内部 Body fallback 代码，但正常 allowed-owner 不变量下不应依赖该分支。这一输入契约不应在可读性重构中擅自替换。
- 通用 solver 只统一 expanded matrix、dummy、forbidden 和结果解析，不统一各 phase 的 row 方向、领域 gating、cost 或 lifecycle；最小 `AssignmentResult`、solver row 和 slot key 降级到 `.cpp` 或函数局部。
- `face`：当前 driver identity 的主入口，负责稳定 DRIVER Face 选择和后续 Face 模型输入。
- `body`：当前代码中的 face-owned body/torso evidence，不再单独决定 driver identity。
- `hand`：当前代码中按 face-owned Body evidence id 维护 `left/right` 两个槽位；稳定 DRIVER Body owner 参与主更新、second pass 和发布。
- `retired body`：仅作为旧 evidence/hand 槽位清理的历史锚点，不是新的主入口。
- ID 数值来源与生命周期所有权分离：`bodyId / handId` 初始继承 `faceId` 数值和 map key，但 body/hand 不应成为独立 identity lifecycle owner。body/hand 只允许 bounded evidence cache，并在 owner 确认退休、id 复用或 handoff 完成前收敛 cleanup。

## 0.5 Current Lifecycle

### 0.5.1 body/torso evidence

- 以 `body` 检测作为 evidence 输入。
- 当前所有 active face track 都可作为 body/torso evidence owner；selected driver owner 只获得处理顺序优先级。
- Body association 先尝试已有轨迹的预测匹配，失败后允许基于 face anchor 做检测选择；这一路径的身份误绑定风险必须通过后续行为修改单独处理，不能混入本轮可读性重构。
- Body global assignment、Track/Reacquire/Bootstrap/Forbidden 四态 edge、Reacquire cost band 和 initialized acquisition fallback 均降级为历史实验或未来重启项；只有在多 owner body evidence 成为明确业务目标且具备 replay、loss 分布、冲突样例和 diff 白名单后才重新评估。
- face owner 尚未绑定 body 或已有轨迹匹配失败时，face-anchor selection 可承担获取或重新选择。
- 命中时 `hitCount` 增长并清零 `missCount`，丢失时 `hitCount` 衰减、`missCount` 增长。
- bounded cache 只允许短期保留 box、motion state、hit/miss，用于 face 恢复后的平滑；当前已有 body 的 tracking 失败后仍可能走 face-anchor selection，但不得 owner migration 或反向影响 driver identity。
- `missCount` 达阈值后清理或转入 bounded cleanup anchor；该 anchor 只服务 hand slot 清理，不是独立 identity lifecycle。
- 达到稳定阈值的 `body` evidence 才对外输出，legacy map key 使用 Face trackId。
- body 的稳定输出不能单独成为 driver identity 的主来源。

### 0.5.2 face

- Face 先于 Body evidence 更新，使用自身预测、size continuity 和 distance gate 匹配当前 Face detection。
- 未匹配 Face detection 通过 Face id 分配入口创建新 identity。
- DRIVER Face 由 `selectDriverFace` 基于 driver ROI、小脸过滤、front passenger 排除、size continuity 和位置 loss 选择。
- 区域级唯一性和运行中 id 连续性仍必须放到 validation 中判定，不在 design 中假装闭合。

### 0.5.3 hand

- 稳定 DRIVER body evidence 维护 `left/right` 两个槽位，而不是统一 hand 池或跨 owner global slot assignment。
- 槽位初始化依赖 DRIVER face-owned Body evidence；初始化后只作为该 owner 的 bounded cache，不反向创建、扩大或迁移 owner。
- 未命中时 hand 内部可短期保留状态以支持遮挡恢复；对外输出仍要求当前允许发布的 DRIVER body evidence 或等价 owner 证据。
- bounded hand cache 只允许短期保留 box、motion state、hit/miss，用于 face 恢复后的平滑；不得发布为有效 hand，不得 acquisition/bootstrap，不得 owner migration，不得反向影响 driver identity。
- 新 stable driver body evidence 若接管同一区域，应清理旧 orphan hand 槽位。
- 当前设计保留左右槽位的短期状态连续性，但不保留完整 independent identity lifecycle；body/hand 不继续承担 identity-like continuation。

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
- `244e5300` 只重组内部叙事结构和补充简短中文注释，没有解决主驾 body 消失后误跟副驾、同一只手左右槽反复归属等行为问题。
- Body 已有轨迹一旦 tracking loss 超过 dummyLoss，会立即进入无额外阈值的 Face-anchor selection；邻近乘员 Body 同时满足 Face ROI 时，存在错误重绑定风险。
- Hand left/right 两行共享同一 owner 的候选集，侧别主要由 `HandAnchorLoss` 与历史预测共同区分；双手交叉、单手跨过 Body 中线或检测短时丢失时，仍可能发生左右槽交换。
- Hand 只有 allowed DRIVER Body owner 的未命中 slot 会进入 second pass 并推进 miss；owner 暂时不再 allowed、但内部 Body track 尚未删除时，旧 slot 可能停止推进 miss，需要后续单独修正并验证。
- face 区域级唯一输出运行验证：未闭合
- left_hand / right_hand 区域级唯一输出运行验证：未闭合
- 运行时 replay / 视频证据：未闭合
- face-first 第一阶段实现：已本地编译通过；2026-06-12 后排误跟踪主驾问题样本已完成板端回灌验证，更广泛代表性样本仍未闭合

## 0.9 Historical Mapping

- baseline 设计由 [[座舱乘员多目标跟踪方案]] 提供。
- body/face/hand 解耦、retired body handoff 清理、左右手槽位和连续性优化来自 2026-03-25 与 2026-03-31 的 delta 收敛；2026-06-16 方案整理明确继承其“身份 owner 与部件生命周期分离”原则，但不继承 body-first identity 主线。
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
