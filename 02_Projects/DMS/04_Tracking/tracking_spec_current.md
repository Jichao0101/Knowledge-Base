---
title: Tracking Spec Current
summary: Tracking 当前可执行规范文档，记录 head-first 行为约束、body/hand 独立生命周期、Body 四态 edge、driver face 防后排误绑定规则和 clean refactor 边界；保持四类 map ABI，不把实验分支中间类型提升为规范。
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
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/Tracking方案优化与历史实现归档记录-2026-06-16.md
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
updated_at: 2026-06-16
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
- `HeadFirstDriver`：当前 driver identity 的主入口，来自 head/face track 与业务配置约束；不是新增 ABI 类型。
- `BodyTorsoEvidence`：由 driver head 约束后的 body/torso evidence；不单独决定 driver identity。
- `PersonType`：稳定人员类型，至少包含 `PERSON_UNKNOWN`、`DRIVER`、`FRONT_PASSENGER`、`BACK_PASSENGER`。
- `InstanceType`：跟踪实例类型，至少包含 `BODY`、`FACE`、`LEFT_HAND`、`RIGHT_HAND`。
- `TrackInfo`：单条轨迹核心载体，承载 `box`、`predBox`、即时/稳定人员类型、实例类型、生命周期计数、投票计数与 motion state。
- `AtomicResult`：帧级原子结果容器，承载 tracking legacy output map 与下游兼容导出字段；不得作为 hand 阶段内部 body truth source。
- finalized body snapshot：body 阶段生成的单帧只读事实，必须在同一帧供 hand 和 legacy body publish 使用，不得作为 member 或跨帧状态保存；允许直接使用局部 `const map/vector`，不要求专用 `FrameBodyView` 类型。

## 0.3 Required Behaviors

- 当前代码事实中，`head/face` 是 identity 主锚点；后续修改不得恢复 body-first identity 语义。
- `bodyId / handId` 初始继承 `faceId` 数值与 legacy map key；这只是身份与兼容输出 key 的继承，不代表 body/hand 生命周期归属 face。稳定基线中 body 在 face owner 消失时立即退休属于当前代码事实，不是推荐最终形态；后续必须明确 bounded 规则，再让 body/hand 在 face 短时消失时按自身 motion continuity、hit/miss、handoff 和 cleanup 独立推进。
- 第一阶段实现必须保持 head-first driver identity：driver 优先由 head/face track 与业务配置约束决定。
- 2m profile 默认应关闭 body/hand tracking 链路，避免无业务必要的 body/hand 状态污染输出。
- `body` 必须保持为 driver head-bound body/torso evidence，不得由 raw body center 单独决定 driver identity。
- `body` evidence 对已有 head 执行“预测 -> 全局关联 -> edge 分类 -> 更新/生命周期衰减”；clean branch 中已有 body owner 的 tracking cost 与 head geometry acquisition cost 同时进入同一全局 assignment，但在 loss 标定完成前，已有 body owner 只允许 tracking edge 命中，tracking 不可靠则 miss，不允许 acquisition fallback 重新绑定。
- Body edge 必须按四态解释：Track 表示已有 body track 的可靠 tracking 延续；Reacquire 表示已有 owner 在 tracking 不可信但 acquisition 高可信时保留 ownerFaceId 并强校正或重置 motion state；Bootstrap 表示无 body track owner 的首次 acquisition；Forbidden 表示 tracking/acquisition 均不可信或 face consistency 冲突。标定前 Reacquire 必须关闭；标定后打开时不得重置稳定 `hitCount` 到 1，已稳定输出的 owner 应保持输出连续。
- `body` evidence 输出只能在达到稳定阈值后对外暴露。
- `driver body evidence` 最终输出必须唯一且 key 使用 driver headId。
- `face/head` 不应再被异常 raw body box 扩大 owner；driver face/head reject 不能被同帧 second-pass 绕回。
- 当前代码中 `face/head` 先于 body evidence 初始化和匹配，并通过 `allocateFaceTrackId` 持有 identity；legacy key 投影应继承该 headId。
- `face` 初始化后允许与 `body` 短时解耦，不得在 `body` 暂失时被无条件同步清理。
- `hand` 必须按每个 head-owned body evidence 的 `left/right` 两个槽位建模，不得退回统一 hand truth source。
- hand owner 必须受 driver head-bound body/torso 或业务搜索区域约束；raw body box 不得单独扩大 hand owner。hand 阶段不得读取 `curResult->m_bodyTrackResultMap` 作为内部输入，应消费 body 阶段产生的局部 finalized body snapshot。
- `hand` 初始化后允许按槽位独立存活。
- hand 内部状态可在 face 短时消失后保留原始继承 id，并按 bounded lifecycle 独立推进；对外发布仍必须存在当前已发布且稳定为 DRIVER 的 body evidence 或等价 owner 证据。owner 已确认退休、新 owner 接管或 id 复用前，必须执行 cleanup，不能永久保留 orphan slot。
- 当前代码中 `hand` miss 只推进内部生命周期，不再向下游发布预测框；若后续重新引入短时预测输出，必须先更新 validation 风险并验证 handoff/handpose 消费影响。
- 新 stable head-owned body evidence 在同一区域接管时，应基于 retired evidence anchor 清理 orphan hand 槽位。

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
- `AtomicResult.m_bodyTrackResultMap`：body evidence legacy 输出；只能作为 output projection，不得反向参与 hand assignment、cleanup 或 publish eligibility。
- `AtomicResult.m_faceTrackResultMap`：face/head identity 输出。
- `AtomicResult.m_leftHandTrackResultMap`：left hand evidence legacy 输出。
- `AtomicResult.m_rightHandTrackResultMap`：right hand evidence legacy 输出。
- `TrackProfile`：后续仍需显式区分 2m/5m 或业务模式启用链路；当前代码尚未实现该状态。

## 0.5 Interface Contracts

- 上游 tracking 事实源必须维持为四类 map：
  - `m_bodyTrackResultMap`
  - `m_faceTrackResultMap`
  - `m_leftHandTrackResultMap`
  - `m_rightHandTrackResultMap`
- `m_humanTrackResultMap` 只可视为导出兼容层，不得再次反向塑造 tracking 上游设计。
- 左右手输出必须保持分离，不得在 tracking 内部重新定义统一 hand 真相源。
- `tracking_interfaces_evidence` 只保留接口证据，不是当前默认实现输入链入口。
- 第一阶段不得破坏四类 map ABI；head-first 的内部绑定关系必须投影回现有 map。
- Occupant/PersonTrack + PartTrack 不属于当前 required behavior，也不作为默认未来路线；若重新立项，需重新形成独立决策并更新 current 文档和 ABI 边界。

## 0.6 Calculation Contracts

- assignment evaluator 返回真实 cost 或有限 forbidden cost；当前 forbidden cost 固定为 `1e6f`，所有配置化 `dummyLoss` 必须显著小于该值。
- Face/Body/Hand 必须复用同一 `.cpp` internal assignment solver；solver 只负责矩阵扩展、dummy、forbidden 和 index 结果解析，不感知 track/owner/slot 领域语义。
- Face 保持全局匹配语义；Body 已在 clean branch 落地全局 owner-to-body-detection Hungarian；Hand 目标仍为全局 hand-slot-to-detection assignment。
- Body/Hand 的 tracking loss、acquisition loss、driver/non-driver bias 与 `dummyLoss` 必须按场景标定；若 tracking loss 对错误检测仍低于门槛，会错误延续旧 track。未标定前，已有 body track 和 initialized hand slot 不得用 acquisition fallback 重新绑定；若未来重新打开该 fallback，必须先证明 acquisition gate/bias 和 face consistency gate 不会把 owner 误绑定到几何更合理但身份错误的检测。Body Reacquire 一旦打开，必须保持 ownerFaceId、稳定 hitCount 和可输出连续性，只允许重置或强校正 motion state。
- assignment 结果只能是 `.cpp` 或函数局部短期契约，不得进入稳定 header、cleanup、finalize、projection 或 publish；最小结果只保留 `rightByLeft/-1` 与确有消费方的 `unmatchedRight`。
- Body 的 sanitize/lifecycle finalize 必须先于 legacy publish 和 hand 消费；具体 finalized snapshot 表示不得强制为 header-level `FrameBodyView`。Hand 没有 tracker 内部下游，不得为形式统一新增 `FrameHandView`、publish payload 或 eligibility。
- Hand assignment 的 unmatched 解释只针对本帧候选 rows；lifecycle 必须另行 sweep 所有 initialized slots，确保未进入候选 rows 的 owner/slot 也按明确策略推进或清理。
- owner 不再可发布、body 消失或 face 短时消失时，initialized hand slot 的 bounded lifecycle 必须有明确规则；不得因不再进入 assignment row 而永久停止 miss/cleanup。assignment rows 只定义本帧候选匹配，不能替代全量 initialized slot lifecycle sweep。
- publish helper 不得调用 `PrepareTrackForOutput`、`AdvanceMiss` 或 cleanup。
- `body` 和 `face` 使用恒速度运动模型。
- `hand` 使用恒加速度运动模型。
- 关联流程必须遵循预测、构造损失矩阵、匈牙利匹配、命中更新、未命中衰减的顺序。
- invalid track id、unmatched collection index、forbidden assignment edge 和 absent diagnostic loss 必须保持不同语义，不得重新复用同一裸值表达多个概念。
- `body` 命中后允许检测主导融合，但不能破坏稳定输出与生命周期计数语义。
- `face` 命中后输出使用检测框，预测状态只作为关联输入。
- `hand` 命中后输出使用检测框，miss 时不向下游输出预测框。

## 0.7 Type And Filter Contracts

- 当前代码中 driver identity source 来自 head/face；body/hand 的人员类型是 evidence 向 legacy map 的投影。
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
- 下一阶段必须引入可日志化的 profile 选择边界，至少区分 2m head/face only 与 5m handoff/handpose 需要 body/hand 的模式。
- 阈值、Kf 参数和区域配置必须通过结构化配置项读取，不能依赖手工散落常量。
- `track_params.json` 的 `presets.driver_face_anchor` 配置 driver face preferred anchor 与尺寸方向性权重；车型节点可覆盖坐标并继承 DEFAULT 权重。
- 配置变化若影响阈值、运动模型或区域约束，必须同步更新 current 文档。

## 0.9 Verification Contracts

- 若实现触及 `track.cpp` 的 body/face/hand 输出逻辑，至少重新检查 body 稳定输出门槛、driver 唯一化、face/hand 解耦与 handoff 清理、左右手真相源保持，以及 Body 四态 edge 是否只在标定后打开 Reacquire。
- head-first 后续验证必须覆盖 2m body/hand disabled、5m driver head-bound body/torso、hand owner source、driver identity source 日志和四类 map ABI 兼容。
- head-first 后续优化必须同时读取 [[head-first跟踪方案]] 与 [[02_Projects/DMS/04_Tracking/tracking_implementation_current]]，不得只从本 spec 摘要推断完整实现。
- 若实现宣称修复 face/hand 区域级唯一输出，必须在 `tracking_validation_current` 中更新证据状态。
- 若实现改变接口事实源或导出兼容边界，必须同步更新 `tracking_implementation_current` 与本文件。
- 若实现仍需要 baseline、两篇及以上 delta 或长段代码阅读才能恢复当前规范，则默认实现输入链判定不成立。

## 0.10 Non-goals

- 本规范不把“较好的 ID 连续性”直接定义为已验收效果，只约束当前机制与验证缺口的表达方式。
- 本规范不要求 baseline 继续作为实现输入。
- 本规范不要求本次文档覆盖所有仓外消费者契约。
- 本规范不把验证结果伪装成设计约束。
- 本规范不声称 head-first 运行效果已验收；仅记录第一轮实现已本地编译通过。
- 本规范不把 Occupant/PersonTrack + PartTrack 作为当前第一阶段实现目标。
- 本规范不把 Occupant/PersonTrack + PartTrack 作为后续默认路线。

## 0.11 Historical Mapping

- baseline 的目标与初始思路来自 [[座舱乘员多目标跟踪方案]]。
- 早期实现说明来自已归档的 [[90_Archive/02_Projects/DMS/04_Tracking/座舱多目标跟踪实现]]。
- 当前有效规范来自 design/implementation/validation current 与 2026-03-25、2026-03-31、2026-04-05 的 delta 收敛，不再要求实现时回读 baseline。
- 2026-05-09 decision record 将 body-first 归档为 legacy 主线，并把 head-first 作为下一阶段推荐实现规范来源之一。
