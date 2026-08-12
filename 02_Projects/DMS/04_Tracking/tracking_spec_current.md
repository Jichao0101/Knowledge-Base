---
title: Tracking Spec Current
summary: Tracking 当前可执行规范文档，记录 face-first 行为约束、face-owned Body、DRIVER-Body-owned Hand、驾驶员 Face 过滤规则和可读性重构边界；保持四类 map ABI。
status: verified
doc_role: current
truth_role: current
current_kind: spec
lifecycle_state: active
default_entry: false
sync_required_when:
  - 默认实现输入链变化
  - 必须满足的行为约束变化
  - 接口事实源变化
  - verification hooks 变化
retrieval_priority: current
supersedes:
  - 02_Projects/DMS/04_Tracking/座舱乘员多目标跟踪方案.md
  - 90_Archive/02_Projects/DMS/04_Tracking/座舱多目标跟踪实现.md
merged_into: []
current_replacement: []
related_code:
  - /home/jichao/dms/include/utils/track.h
  - /home/jichao/dms/source/utils/track.cpp
  - /home/jichao/dms/include/models/atomic_result.h
  - /home/jichao/dms/source/models/handpose_model.cpp
  - /home/jichao/dms/source/models/humanpose_model.cpp
  - /home/jichao/dms/source/fuse_algos/fuse_algorithm.cpp
sources:
  - 02_Projects/DMS/04_Tracking/tracking_design_current.md
  - 02_Projects/DMS/04_Tracking/tracking_implementation_current.md
  - 02_Projects/DMS/04_Tracking/tracking_validation_current.md
  - 02_Projects/DMS/04_Tracking/座舱乘员多目标跟踪方案.md
  - 90_Archive/02_Projects/DMS/04_Tracking/座舱多目标跟踪实现.md
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
  - /home/jichao/dms/include/utils/track.h
  - /home/jichao/dms/source/utils/track.cpp
  - /home/jichao/dms/include/models/atomic_result.h
  - /home/jichao/dms/source/models/handpose_model.cpp
  - /home/jichao/dms/source/models/humanpose_model.cpp
  - /home/jichao/dms/source/fuse_algos/fuse_algorithm.cpp
scope: 适用于按当前规范修改 Tracking 代码时作为默认规范输入，不要求回读 baseline 才能获得关键实现约束。
risks:
  - 本规范只约束当前已收敛的设计与实现边界，不把仍未闭合的项伪装成已验收硬规则。
  - 若后续代码修改影响 `track.cpp`、`AtomicResult` 或导出链路，需先做 `knowledge_sync_check` 并同步更新本文件。
updated_at: 2026-08-12
---

## 0.1 Spec Scope

本文件回答“现在按什么规范实现 Tracking 代码”。默认实现输入链固定为：

1. [[02_Projects/DMS/04_Tracking/tracking_design_current]]
2. [[02_Projects/DMS/04_Tracking/tracking_spec_current]]
3. [[02_Projects/DMS/04_Tracking/tracking_implementation_current]]
4. [[02_Projects/DMS/04_Tracking/tracking_validation_current]]

baseline 和历史 delta 默认不进入实现输入链；`tracking_interfaces_evidence` 只作为接口证据，不作为默认输入链入口。

## 0.2 Object Model

- `DetectBox`：检测输入与跟踪输出的统一框语义，包含位置、尺寸、置信度、类别与索引。
- `RawBodyDetection`：body class 的原始检测框语义，视为包含头、躯干、手臂/手部的 person 外接证据；不得直接作为稳定 driver/person anchor。
- `FaceFirstDriver`：当前 driver identity 的主入口，来自 Face track 与业务配置约束；不是新增 ABI 类型。
- `BodyTorsoEvidence`：由 owner Face 约束后的 body/torso evidence；不单独决定 driver identity。
- `PersonType`：稳定人员类型，至少包含 `PERSON_UNKNOWN`、`DRIVER`、`FRONT_PASSENGER`、`BACK_PASSENGER`。
- `InstanceType`：跟踪实例类型，至少包含 `BODY`、`FACE`、`LEFT_HAND`、`RIGHT_HAND`。
- `TrackInfo`：单条轨迹核心载体，承载 `box`、`predBox`、即时/稳定人员类型、实例类型、生命周期计数、投票计数与 motion state。
- `AtomicResult`：帧级原子结果容器，承载 tracking legacy output map 与下游兼容导出字段；当前 Hand phase 读取其中本帧 `m_bodyTrackResultMap` 作为 body evidence。

## 0.3 Required Behaviors

- 当前代码事实中，Face 是 identity 主锚点；后续修改不得恢复 body-first identity 语义。
- `bodyId / handId` 初始继承 `faceId` 数值与 legacy map key；这只是身份与兼容输出 key 的继承，不代表 body/hand 是独立 identity owner。`feat/ljc/track_0615` 4A 代码已尝试让已有 body/hand 在 face miss/暂不存在时继续内部推进，但该路线降级为历史实验事实；推荐规范收缩为 bounded evidence cache，对外输出继续要求当前 face/body owner 证据。face occlusion 由下游既有接口和逻辑判断处理。
- 第一阶段实现必须保持 face-first driver identity：driver 由 Face track 与业务配置约束决定。
- 当前代码没有 camera profile gate；Face、Body、Hand phase 均按每帧主顺序执行。
- `body` 必须保持为 face-owned body/torso evidence，不得由 raw body center 单独决定 driver identity。
- 已有 `body` evidence 在 owner Face track 尚未删除期间必须先做自身预测匹配，Face 短时 miss 不得阻断该 tracking；selected driver 和既有 DRIVER Body 只获得检测占用顺序优先级。
- Face-anchor acquisition/reselection 只允许由当帧 `missCount==0 && hitCount>0` 的有效 Face 触发；Face 短时 miss 时不得用 stale Face anchor 获取 Body。
- Body global assignment、Track/Reacquire/Bootstrap/Forbidden 四态 edge 和 Reacquire cost band 不再作为当前 required behavior。若未来重新立项，必须先具备多 owner body evidence 业务需求、replay 运行数据、tracking/acquisition loss 分布、冲突样例和 diff 白名单。
- `body` evidence 输出只能在达到稳定阈值后对外暴露。
- 每条稳定 `body evidence` 的输出 key 使用其 face owner id；driver body 的唯一性仍需运行验证。
- Face 不应再被异常 raw Body box 扩大 owner；DRIVER Face reject 不能被同帧其他路径绕回。
- 当前代码中 Face 先于 Body evidence 初始化和匹配，并通过 `allocateFaceTrackId` 持有 identity；legacy key 投影应继承该 Face id。
- `face` 初始化后允许与 `body` 短时解耦，不得在 `body` 暂失时被无条件同步清理。
- Hand 必须按每个 face-owned Body evidence 的 `left/right` 两个槽位建模，不得退回统一 Hand truth source。
- Hand owner 必须受稳定 DRIVER Body/torso 约束；当前 owner 集合从 `curResult->m_bodyTrackResultMap` 构造。second pass 虽保留内部 `m_bodyTracks` fallback 表达式，但正常 allowed-owner 不变量下必须能够取得本帧 Body evidence。
- `hand` 初始化后只允许在所属 Body 生命周期内按槽位维护；Body 删除时必须同步删除同 owner 的 left/right Hand state。
- Face 短时 miss 时，Body 可继续内部 tracking；Hand 对外发布仍必须存在当前已发布且稳定为 DRIVER 的 Body evidence。Face 真正删除会级联删除 Body/Hand，不保留 orphan slot。
- 当前代码中 `hand` miss 只推进内部生命周期，不再向下游发布预测框；若后续重新引入短时预测输出，必须先更新 validation 风险并验证 handoff/handpose 消费影响。
- 不再维护 retired Body 空间锚点，也不允许新 Body 通过同区域判断接管或清理旧 Hand；旧 Hand 必须在原 Body 删除点完成级联清理。

## 0.4 Core State Variables

- `TrackThresholds.hitThreshold`：稳定输出门槛。
- `TrackThresholds.missThreshold`：删除门槛。
- `TrackThresholds.typeMinVotes`：稳定类型最小投票数。
- `TrackThresholds.typeRatioThreshold`：稳定类型占比阈值。
- `TrackThresholds.dummyLoss`：关联中的不匹配门槛。
- `TrackParameters.body / face / hand`：三类轨迹各自阈值。
- `TrackParameters.bodyKalman / faceKalman / handKalman`：三类运动模型配置。
- `TrackParameters.smallFaceAreaRatio`：driver 场景的小脸过滤阈值。
- `TrackParameters.driverFaceAnchor`：driver face 选择的 preferred anchor。
- `TrackParameters.driverFaceAnchorWeight`：driver face anchor loss 权重。
- `TrackParameters.driverFaceSmallerPenaltyWeight`：driver face 比 reference 变小时的惩罚权重。
- `TrackParameters.driverFaceLargerBonusWeight`：driver face 比 reference 变大时的恢复增益权重。
- `AtomicResult.m_bodyTrackResultMap`：body evidence legacy 输出，也是当前 Hand phase 的本帧 owner evidence 输入。
- `AtomicResult.m_faceTrackResultMap`：Face identity 输出。
- `AtomicResult.m_leftHandTrackResultMap`：left hand evidence legacy 输出。
- `AtomicResult.m_rightHandTrackResultMap`：right hand evidence legacy 输出。

## 0.5 Interface Contracts

- 上游 tracking 事实源必须维持为四类 map：
  - `m_bodyTrackResultMap`
  - `m_faceTrackResultMap`
  - `m_leftHandTrackResultMap`
  - `m_rightHandTrackResultMap`
- `m_humanTrackResultMap` 只可视为导出兼容层，不得再次反向塑造 tracking 上游设计。
- 左右手输出必须保持分离，不得在 tracking 内部重新定义统一 hand 真相源。
- `tracking_interfaces_evidence` 只保留接口证据，不是当前默认实现输入链入口。
- 第一阶段不得破坏四类 map ABI；face-first 的内部绑定关系必须投影回现有 map。
- Occupant/PersonTrack + PartTrack 不属于当前 required behavior，也不作为默认未来路线；若重新立项，需重新形成独立决策并更新 current 文档和 ABI 边界。
- `DmsTrack::Init/Update` 是当前唯一 public tracker API；内部可读性重构不得增加 public phase API。
- `track.h` private surface 以 `3a2ed302` 为当前组织基线：保留长期状态、配置/ID 基础能力、四个 phase-level 方法，以及 Hand 的 owner 更新、未匹配恢复、过期清理、发布四个职责明确的 private 子阶段。
- 不得把 `solve/apply/advance/finalize/project/publish` 全套步骤提升为 header-level private helper 脚本。只有当某个步骤拥有独立契约、独立复用、独立测试或独立失败边界时，才允许在实现前重新做抽象必要性审计。
- `FrameBodyView`、`HandAssignmentRow`、`AssignmentResult`、`BodyEdgeMode`、`LifecycleContext/Payload/Eligibility` 不属于当前规范要求的稳定类型；默认使用 `.cpp` internal、函数局部 struct/lambda、局部容器或已有 `TrackInfo` 表达。
- face occlusion 下游已具备接口与逻辑判断，track 内部不需要再做 face occlusion 业务分支。

## 0.6 Calculation Contracts

- assignment evaluator 返回真实 cost 或有限 forbidden cost；当前 forbidden cost 固定为 `1e6f`，所有配置化 `dummyLoss` 必须显著小于该值。
- Face 可复用 `.cpp` internal assignment solver，也可在只有 Face 使用且直接调用 Hungarian 更清晰时删除该 helper。solver 若存在，只负责矩阵扩展、dummy、forbidden 和 index 结果解析，不感知 track/owner/slot 领域语义。Body/Hand 不要求为了“统一 assignment”强制复用该 solver。
- Face 保持全局匹配语义；Body 按 face owner 逐一做 tracking/face-anchor selection；Hand 按稳定 DRIVER body owner 的 left/right 槽位关联。
- Body/Hand 的 tracking loss、acquisition loss 与 `dummyLoss` 仍需按场景标定；Body tracking 失败后只有当帧有效 Face 才允许 face-anchor selection。Hand 未匹配恢复仍是后续 owner 误绑定验证重点。
- assignment 结果只能是 `.cpp` 或函数局部短期契约，不得进入稳定 header、cleanup、finalize、projection 或 publish；最小结果只保留 `rightByLeft/-1` 与确有消费方的 `unmatchedRight`。
- Body 的 sanitize/lifecycle finalize 必须先于 legacy publish 和 Hand 读取 `m_bodyTrackResultMap`。Hand 没有 tracker 内部下游，不得为形式统一新增 `FrameHandView`、publish payload 或 eligibility。
- Hand assignment 的 unmatched 解释只针对本帧候选 rows；lifecycle 必须另行 sweep 所有 initialized slots，确保未进入候选 rows 的 owner/slot 也按明确策略推进或清理。
- Hand 对外发布仍需满足当前稳定门槛和 owner 条件，不得跨 owner 迁移或反向影响 driver identity；Body 删除必须在同一状态转换中删除同 owner Hand。
- owner 暂时不再可发布但 Body 尚存时，initialized Hand slot 的 miss/reset 策略仍需运行验证；不得因不再进入 assignment row 而永久停止 cleanup。assignment rows 只定义本帧候选匹配，不能替代生命周期收尾。
- publish helper 不得调用 `PrepareTrackForOutput`、`AdvanceMiss` 或 cleanup；除 sanitize 明确归属于 finalize 外，publish 不得推进 hit/miss、retire、reset 或 owner migration。
- `body` 和 `face` 使用恒速度运动模型。
- `hand` 使用恒加速度运动模型。
- 关联流程必须遵循预测、构造损失矩阵、匈牙利匹配、命中更新、未命中衰减的顺序。
- invalid track id、unmatched collection index、forbidden assignment edge 和 absent diagnostic loss 必须保持不同语义，不得重新复用同一裸值表达多个概念。
- `body` 命中后允许检测主导融合，但不能破坏稳定输出与生命周期计数语义。
- `face` 命中后输出使用检测框，预测状态只作为关联输入。
- `hand` 命中后输出使用检测框，miss 时不向下游输出预测框。

## 0.7 Type And Filter Contracts

- 当前代码中 driver identity source 来自 Face；Body/Hand 的人员类型是 evidence 向 legacy map 的投影。
- body center ROI 投票只能作为 fallback/evidence，不应作为主来源。
- `driver` 过滤可依据空间区域和稳定投票收敛，不可由单帧外观直接锁死。
- `smallFaceAreaRatio` 是 driver 场景的人脸过滤契约，用于抑制明显过小的人脸候选。
- driver face selection 必须拒绝稳定类型为 `BACK_PASSENGER` 的 face 候选；不得仅因单帧 `instantPersonType == DRIVER` 放行稳定后排候选。
- driver face size continuity 必须区分方向：候选比当前 driver reference 变小应作为强惩罚和拒绝依据；候选变大应作为主驾遮挡恢复的增益，不应被对称 size-loss 拒绝。
- driver face preferred anchor、anchor 权重、变小惩罚权重和变大增益权重必须来自结构化配置，不得散落硬编码。
- 本类后排误绑定修复不得通过收紧 face match `distanceLoss` 或 driver distance gate 实现。
- `hand` 侧的左右槽位必须维持方向区分和历史连续性约束。

## 0.8 Config Contracts

- 当前配置来源固定为 `/home/jichao/dms/etc/track_params.json`。
- 配置必须先加载 `DEFAULT`，再按车型节点覆盖。
- 当前 `track_params.json` 不承担 2m/5m Body/Hand phase gate；若未来引入 profile 分流，必须作为独立行为变更补充配置、日志和验证。
- 阈值、Kf 参数和区域配置必须通过结构化配置项读取，不能依赖手工散落常量。
- `track_params.json` 的 `presets.driver_face_anchor` 配置 driver face preferred anchor 与尺寸方向性权重；车型节点可覆盖坐标并继承 DEFAULT 权重。
- 配置变化若影响阈值、运动模型或区域约束，必须同步更新 current 文档。

## 0.9 Verification Contracts

- 若实现触及 `track.cpp` 的 body/face/hand 输出逻辑，至少重新检查 body 稳定输出门槛、driver 唯一化、face-owner 交接、hand owner/左右槽、bounded cache 清理和四类 map ABI。
- face-first 后续验证必须覆盖 Body owner source、主驾 Body 消失后的重绑定、Hand owner source、左右槽稳定性和 driver identity source 日志。
- face-first 后续优化必须以本 current 组为事实源；需要历史动机时再读取 [[head-first跟踪方案]]。
- 若实现宣称修复 face/hand 区域级唯一输出，必须在 `tracking_validation_current` 中更新证据状态。
- 若实现改变接口事实源或导出兼容边界，必须同步更新 `tracking_implementation_current` 与本文件。
- 若实现仍需要 baseline、两篇及以上 delta 或长段代码阅读才能恢复当前规范，则默认实现输入链判定不成立。

## 0.10 Non-goals

- 本规范不把“较好的 ID 连续性”直接定义为已验收效果，只约束当前机制与验证缺口的表达方式。
- 本规范不要求 baseline 继续作为实现输入。
- 本规范不要求本次文档覆盖所有仓外消费者契约。
- 本规范不把验证结果伪装成设计约束。
- 本规范不声称 face-first 运行效果已全面验收；仅记录第一轮实现已有本地编译证据。
- 本规范不把 Occupant/PersonTrack + PartTrack 作为当前第一阶段实现目标。
- 本规范不把 Occupant/PersonTrack + PartTrack 作为后续默认路线。

## 0.11 Historical Mapping

- baseline 的目标与初始思路来自 [[座舱乘员多目标跟踪方案]]。
- 早期实现说明来自已归档的 [[90_Archive/02_Projects/DMS/04_Tracking/座舱多目标跟踪实现]]。
- 当前有效规范来自 design/implementation/validation current 与 2026-03-25、2026-03-31、2026-04-05 的 delta 收敛，不再要求实现时回读 baseline。
- 2026-05-09 decision record 使用 head-first/body-first 对比术语；current 统一采用 face-first 口径，历史文件名不改写。
