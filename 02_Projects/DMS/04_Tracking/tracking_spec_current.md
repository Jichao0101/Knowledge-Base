---
title: Tracking Spec Current
summary: Tracking 当前可执行规范文档，区分当前代码事实与下一阶段 head-first 实现约束；第一阶段保持四类 map ABI，不推进完整 OccupantTrack 分层。
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
  - 02_Projects/DMS/04_Tracking/座舱多目标跟踪实现.md
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
  - 02_Projects/DMS/04_Tracking/座舱多目标跟踪实现.md
  - 02_Projects/DMS/04_Tracking/多目标跟踪设计失配修复闭环记录-2026-03-25.md
  - 02_Projects/DMS/04_Tracking/多目标跟踪生命周期与手部关联设计失配修复闭环记录-2026-03-25.md
  - 02_Projects/DMS/04_Tracking/多目标跟踪功能审核记录-2026-03-27.md
  - 02_Projects/DMS/04_Tracking/多目标跟踪手部连续性优化闭环记录-2026-03-31.md
  - 02_Projects/DMS/04_Tracking/多目标跟踪快速运动恢复阶段预测更新一致性修复闭环记录-2026-04-05.md
  - 02_Projects/DMS/04_Tracking/head-first优先于body-first跟踪主线决策记录-2026-05-09.md
  - 02_Projects/DMS/04_Tracking/head-first渐进跟踪方案.md
  - 02_Projects/DMS/04_Tracking/head-first渐进跟踪实现.md
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
updated_at: 2026-05-09
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
- `HeadFirstDriver`：下一阶段 driver identity 的主入口，来自 head/face track 与业务配置约束；不是新增 ABI 类型。
- `BodyTorsoEvidence`：5m profile 中由 driver head 约束后的 body/torso evidence；不单独决定 driver identity。
- `PersonType`：稳定人员类型，至少包含 `PERSON_UNKNOWN`、`DRIVER`、`FRONT_PASSENGER`、`BACK_PASSENGER`。
- `InstanceType`：跟踪实例类型，至少包含 `BODY`、`FACE`、`LEFT_HAND`、`RIGHT_HAND`。
- `TrackInfo`：单条轨迹核心载体，承载 `box`、`predBox`、即时/稳定人员类型、实例类型、生命周期计数、投票计数与 motion state。
- `AtomicResult`：帧级原子结果容器，承载 tracking 真相源 map 与下游兼容导出字段。

## 0.3 Required Behaviors

- 当前代码事实中，`body` 仍作为乘员级主锚点；下一阶段修改不得继续扩大该 body-first 语义。
- 第一阶段推荐实现必须采用 head-first driver identity：driver 优先由 head/face track 与业务配置约束决定。
- 2m profile 默认应关闭 body/hand tracking 链路，避免无业务必要的 body/hand 状态污染输出。
- 5m profile 中，`body` 必须降级为 driver head-bound body/torso evidence，不得由 raw body center 单独决定 driver identity。
- `body` 当前仍执行“预测 -> 关联 -> 更新/新建 -> 生命周期衰减 -> 稳定输出”主流程；后续若保留 body 输出，必须保持 legacy map 兼容。
- `body` 输出只能在达到稳定阈值后对外暴露。
- `driver body` 最终输出必须唯一。
- `face/head` 不应再被异常 raw body box 扩大 owner；driver face/head reject 不能被同帧 second-pass 绕回。
- 当前代码中 `face` 在稳定 `body` 存在后初始化，并继承 `bodyId`；下一阶段可保持 legacy key 投影，但 identity 决策优先级应迁移到 head-first。
- `face` 初始化后允许与 `body` 短时解耦，不得在 `body` 暂失时被无条件同步清理。
- `hand` 必须按每个 `body` 的 `left/right` 两个槽位建模，不得退回统一 hand truth source。
- 下一阶段 hand owner 必须受 driver head-bound body/torso 或业务搜索区域约束；raw body box 不得单独扩大 hand owner。
- `hand` 初始化后允许按槽位独立存活。
- 当前代码中 `hand` miss 只推进内部生命周期，不再向下游发布预测框；若后续重新引入短时预测输出，必须先更新 validation 风险并验证 handoff/handpose 消费影响。
- 新 stable `body` 在同一区域接管时，应基于 retired body anchor 清理 orphan `face` 与 orphan `hand` 槽位。

## 0.4 Core State Variables

- `TrackThresholds.hitThreshold`：稳定输出门槛。
- `TrackThresholds.missThreshold`：删除门槛。
- `TrackThresholds.typeMinVotes`：稳定类型最小投票数。
- `TrackThresholds.typeRatioThreshold`：稳定类型占比阈值。
- `TrackThresholds.dummyLoss`：关联中的不匹配门槛。
- `TrackParameters.body / face / hand`：三类轨迹各自阈值。
- `TrackParameters.bodyKalman / faceKalman / handKalman`：三类运动模型配置。
- `TrackParameters.smallFaceAreaRatio`：driver 场景的小脸过滤阈值。
- `AtomicResult.m_bodyTrackResultMap`：body 真相源。
- `AtomicResult.m_faceTrackResultMap`：face 真相源。
- `AtomicResult.m_leftHandTrackResultMap`：left hand 真相源。
- `AtomicResult.m_rightHandTrackResultMap`：right hand 真相源。
- `TrackProfile`：下一阶段必须显式区分 2m/5m 或业务模式启用链路；当前代码尚未实现该状态。

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

- `body` 和 `face` 使用恒速度运动模型。
- `hand` 使用恒加速度运动模型。
- 关联流程必须遵循预测、构造损失矩阵、匈牙利匹配、命中更新、未命中衰减的顺序。
- `body` 命中后允许检测主导融合，但不能破坏稳定输出与生命周期计数语义。
- `face` 命中后输出使用检测框，预测状态只作为关联输入。
- `hand` 命中后输出使用检测框，miss 时不向下游输出预测框。

## 0.7 Type And Filter Contracts

- 当前代码中 `body` 类型判定依赖 driver/front/back 投票，而不是单帧类别。
- 下一阶段 driver identity source 应优先来自 head/face；body center ROI 投票只能作为 fallback/evidence，不应作为主来源。
- `driver` 过滤可依据空间区域和稳定投票收敛，不可由单帧外观直接锁死。
- `smallFaceAreaRatio` 是 driver 场景的人脸过滤契约，用于抑制明显过小的人脸候选。
- `hand` 侧的左右槽位必须维持方向区分和历史连续性约束。

## 0.8 Config Contracts

- 当前配置来源固定为 `/home/jichao/dms/etc/track_params.json`。
- 配置必须先加载 `DEFAULT`，再按车型节点覆盖。
- 下一阶段必须引入可日志化的 profile 选择边界，至少区分 2m head/face only 与 5m handoff/handpose 需要 body/hand 的模式。
- 阈值、Kf 参数和区域配置必须通过结构化配置项读取，不能依赖手工散落常量。
- 配置变化若影响阈值、运动模型或区域约束，必须同步更新 current 文档。

## 0.9 Verification Contracts

- 若实现触及 `track.cpp` 的 body/face/hand 输出逻辑，至少重新检查 body 稳定输出门槛、driver 唯一化、face/hand 解耦与 handoff 清理、左右手真相源保持。
- 若实现 head-first，必须验证 2m body/hand disabled、5m driver head-bound body/torso、hand owner source、driver identity source 日志和四类 map ABI 兼容。
- 若实现 head-first，必须同时读取 [[02_Projects/DMS/04_Tracking/head-first渐进跟踪方案]] 与 [[02_Projects/DMS/04_Tracking/head-first渐进跟踪实现]]，不得只从本 spec 摘要推断完整实现。
- 若实现宣称修复 face/hand 区域级唯一输出，必须在 `tracking_validation_current` 中更新证据状态。
- 若实现改变接口事实源或导出兼容边界，必须同步更新 `tracking_implementation_current` 与本文件。
- 若实现仍需要 baseline、两篇及以上 delta 或长段代码阅读才能恢复当前规范，则默认实现输入链判定不成立。

## 0.10 Non-goals

- 本规范不把“较好的 ID 连续性”直接定义为已验收效果，只约束当前机制与验证缺口的表达方式。
- 本规范不要求 baseline 继续作为实现输入。
- 本规范不要求本次文档覆盖所有仓外消费者契约。
- 本规范不把验证结果伪装成设计约束。
- 本规范不声称 head-first 已实现。
- 本规范不把 Occupant/PersonTrack + PartTrack 作为当前第一阶段实现目标。
- 本规范不把 Occupant/PersonTrack + PartTrack 作为后续默认路线。

## 0.11 Historical Mapping

- baseline 的目标与初始思路来自 [[02_Projects/DMS/04_Tracking/座舱乘员多目标跟踪方案]]。
- 早期实现说明来自 [[02_Projects/DMS/04_Tracking/座舱多目标跟踪实现]]。
- 当前有效规范来自 design/implementation/validation current 与 2026-03-25、2026-03-31、2026-04-05 的 delta 收敛，不再要求实现时回读 baseline。
- 2026-05-09 decision record 将 body-first 归档为 legacy 主线，并把 head-first 作为下一阶段推荐实现规范来源之一。
