---
title: Tracking Design Current
summary: Tracking 当前设计文档，记录 head-first 功能边界、2m/5m 第一层分流、driver face 防后排误绑定设计、body/hand driver-bound evidence 与 clean refactor 收缩路线；统一 assignment 和 independent lifecycle 降级为历史实验路线。
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
  - 90_Archive/02_Projects/DMS/04_Tracking/Current Maintenance Records/Tracking方案优化与历史实现归档记录-2026-06-16.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack基线对比与HeadFirst路线收缩设计记录-2026-06-16.md
  - /home/jichao/dms/source/utils/track.cpp
scope: 适用于恢复当前 Tracking 的设计真相，重点描述目标、边界、层级、生命周期和设计原则；不单独承担完整实现规范职责。
risks:
  - 文档明确区分“当前设计目标”和“当前代码已证实行为”；对未被代码静态证据完全支撑的项保持保守表述。
updated_at: 2026-06-16
---

## 0.1 Current Goal

当前代码事实已采用 `head/face` 作为 identity 主锚点，向下挂载 `body/torso evidence`、`left_hand`、`right_hand` evidence，并向下游输出 `body / face / left_hand / right_hand` legacy 结果。

当前设计主线为 `head-first 跟踪方案`：driver identity 由 head/face track 决定；body 不再作为 driver/person identity 的主来源，而是 driver head-bound body/torso evidence；hand association 必须受 driver head-bound body evidence 约束。2m 默认 face/head-only，不启动或不输出陈旧 body/hand；5m 在 driver face/head 选定后只做 driver-bound body/hand evidence。body/hand 继承 face owner key，但只允许 bounded evidence cache，不默认维持完整 independent identity-like lifecycle。完整设计见 [[head-first跟踪方案]]，实现记录见 [[02_Projects/DMS/04_Tracking/tracking_implementation_current]]。

本文件声称 head-first 第一轮已实现并通过本地编译；运行效果、2m/5m profile 和板端/视频回放仍以 [[02_Projects/DMS/04_Tracking/tracking_validation_current]] 的证据边界为准。

本文件只回答“当前设计是什么”，不回答全部“按什么精确规则实现代码”；实现级硬约束收敛到 [[02_Projects/DMS/04_Tracking/tracking_spec_current]]。

## 0.1.1 2026-06-16 基线对比后的路线收缩与组织架构基线

- public `DmsTrack::Init/Update` 已经形成深接口，不建议改变。
- `track.h` 从 `1401fc338107f05b9cf` 到 `feat/ljc/track_0615` 未变化；架构漂移集中在 `track.cpp`。
- `feat/ljc/track_0615` 已从 clean refactor 进入行为扩张链：Body global assignment、Hand global slot assignment、tracking/acquisition 修补和 independent lifecycle 小步连续叠加。
- 后续推荐不再把 Face/Body/Hand 统一 assignment 作为默认架构目标；`SolveAssignment` 不作为必须保留项。若 clean branch 中只有 Face 使用该 helper，且直接调用 Hungarian 更清晰，则允许删除 helper。
- Body global assignment、Hand global slot assignment、Body/Hand independent lifecycle、Body 四态 edge、Reacquire cost band 降级为历史实验或未来重启项。
- 当前推荐从 `1401fc338107f05b9cf` 稳定骨架收缩：Face 等价 solver 可选保留或删除，优先实现基于 `track_params.json` 车型配置的 2m/5m 分流、5m driver-only body evidence 和 5m driver-only hand evidence。face occlusion 下游已有接口和判断逻辑，track 内部无需新增 face occlusion 业务判断。
- 组织架构基线同样回到 `1401fc338107f05b9cf` 的 `track.h` private surface：header 只保留长期状态、配置/ID 基础能力和 `updateFaceTracks/selectDriverFace/updateBodyTracks/updateHandTracks` phase-level 方法。
- 不把 `solve/apply/advance/finalize/project/publish` 全套执行脚本展开为 header-level private helper；只在确有独立契约、复用、测试或失败边界时才提升为 private method。
- `FrameBodyView`、`HandAssignmentRow`、`AssignmentResult`、`BodyEdgeMode`、`LifecycleContext/Payload/Eligibility` 不作为默认稳定抽象；优先降级到 `.cpp` anonymous namespace、函数局部 struct、局部 lambda、局部 map/vector 或直接复用 `TrackInfo`。

## 0.2 Current Layering

- phase 内部按三段式组织：frame-local computation、persistent state transition、output projection；分层不要求 face/body/hand 机械拥有同形 stage。
- frame-local computation 只处理当前帧输入、候选集、loss、assignment、profile 判断和输出资格判断；结果不得跨帧保存，不得提升为 header 类型。
- persistent state transition 是唯一允许修改 `m_faceTracks`、`m_bodyTracks`、`m_handTracks`、`m_retiredBodyTracks`、`motionState`、`hitCount`、`missCount` 和 cleanup 的阶段。
- output projection 只读取已完成状态并写 legacy maps；除 sanitize 明确归属于 finalize 外，publish 不得推进 hit/miss、retire、reset 或 owner migration。
- body -> hand 确实需要同帧 finalized body 契约，但不预设必须使用 header-level `FrameBodyView`；优先复用局部 `const map/vector` 或 `.cpp` internal snapshot。
- 通用 solver 只统一 expanded matrix、dummy、forbidden 和结果解析，不统一各 phase 的 row 方向、领域 gating、cost 或 lifecycle；最小 `AssignmentResult`、solver row 和 slot key 降级到 `.cpp` 或函数局部。
- `head/face`：当前 driver identity 的主入口，负责稳定 driver/head 选择和后续 face/head 模型输入。
- `body`：当前代码中的 head-owned body/torso evidence，不再单独决定 driver identity。
- `hand`：当前代码中按 head-owned body evidence id 维护 `left/right` 两个槽位，输出 key 与 driver headId 对齐；推荐路线只在 driver-bound body evidence 下运行 hand，不做跨 owner global slot assignment。
- `retired body`：仅作为旧 evidence/hand 槽位清理的历史锚点，不是新的主入口。
- finalized body snapshot：body 阶段产生的单帧只读事实，只用于 hand 阶段和 legacy body publish；具体表示不进入稳定 header 契约，`FrameBodyView` 仅是实验分支当前实现。
- ID 数值来源与生命周期所有权分离：`bodyId / handId` 初始继承 `faceId` 数值和 map key，但 body/hand 不应成为独立 identity lifecycle owner。body/hand 只允许 bounded evidence cache，并在 owner 确认退休、id 复用或 handoff 完成前收敛 cleanup。

## 0.3 Current Lifecycle

### 0.3.1 body/torso evidence

- 以 `body` 检测作为 evidence 输入。
- 推荐路线中，只有 selected driver face/head 主动维护 body/torso evidence；2m profile 默认不启用 body 链路。
- Body association 优先表达为 driver-bound evidence selection，不追求多 owner global assignment。已有 body evidence 的 tracking 不可信时先进入 miss/cache 路径，不使用 acquisition fallback 重新绑定到几何更合理但 identity 风险更高的检测。
- Body global assignment、Track/Reacquire/Bootstrap/Forbidden 四态 edge、Reacquire cost band 和 initialized acquisition fallback 均降级为历史实验或未来重启项；只有在多 owner body evidence 成为明确业务目标且具备 replay、loss 分布、冲突样例和 diff 白名单后才重新评估。
- driver head 尚未绑定 body 时，acquisition 只服务 driver-bound body evidence 的首次绑定。
- 命中时 `hitCount` 增长并清零 `missCount`，丢失时 `hitCount` 衰减、`missCount` 增长。
- bounded cache 只允许短期保留 box、motion state、hit/miss，用于 face 恢复后的平滑；不得发布为有效 body，不得 acquisition/bootstrap，不得 owner migration，不得反向影响 driver identity。
- `missCount` 达阈值后清理或转入 bounded cleanup anchor；该 anchor 只服务 hand slot 清理，不是独立 identity lifecycle。
- 达到稳定阈值的 `body` evidence 才对外输出，legacy map key 使用 head trackId。
- body 的稳定输出不能单独成为 driver identity 的主来源。

### 0.3.2 face

- face/head 先于 body evidence 更新，使用自身预测、size continuity 和 distance gate 匹配当前 face detection。
- 未匹配 face detection 通过 head/face id 分配入口创建新 identity。
- driver head 由 `selectDriverHead` 基于 driver ROI、小脸过滤、front passenger 排除、size continuity 和位置 loss 选择。
- 区域级唯一性和运行中 id 连续性仍必须放到 validation 中判定，不在 design 中假装闭合。

### 0.3.3 hand

- driver-bound body evidence 维护 `left/right` 两个槽位，而不是统一 hand 池或跨 owner global slot assignment。
- 槽位初始化依赖 driver head-bound body evidence；初始化后只作为 driver-bound evidence 的 bounded cache，不反向创建、扩大或迁移 owner。
- 未命中时 hand 内部可短期保留状态以支持遮挡恢复；对外输出仍要求当前允许发布的 DRIVER body evidence 或等价 owner 证据。
- bounded hand cache 只允许短期保留 box、motion state、hit/miss，用于 face 恢复后的平滑；不得发布为有效 hand，不得 acquisition/bootstrap，不得 owner migration，不得反向影响 driver identity。
- 新 stable driver body evidence 若接管同一区域，应清理旧 orphan hand 槽位。
- 当前设计保留左右槽位的短期状态连续性，但不保留完整 independent identity lifecycle；body/hand 不继续承担 identity-like continuation。

## 0.4 Current Identity And Region Rules

- 当前代码中的 driver identity source 来自 head/face track；body/hand 的 `stablePersonType` 是向 legacy map 投影的 evidence 标签。
- body center ROI 只能作为非最终先验/evidence，不能继续作为主来源。
- `driver` 目标的最终输出唯一仍是设计约束，但唯一性应迁移到 head-first driver selection 上表达。
- driver face selection 对后排探头的防护以稳定人员类型、尺寸方向性和 driver face anchor 共同表达：稳定 BACK_PASSENGER 不进入 driver 候选；比当前 driver reference 变小是强惩罚，变大是恢复增益；preferred anchor 作为配置项表达主驾头枕/主驾脸偏好位置。
- driver face selection 不通过收紧 `distanceLoss` 解决本类问题，避免主驾转头或遮挡恢复时因 KF 预测和观测距离偏大而误拒真实主驾。
- `face / body / hand` 当前达到同 key legacy map 投影；是否已经形成运行级区域最终唯一，需要 validation 依据代码和运行证据单独判定。
- 当前设计不把运行时效果验收等同于静态结构设计。

## 0.5 Current Constraints

- `body` 是历史实现主锚点；当前代码已把它降级为 head-owned evidence。
- `hand` 连续性已做特化优化，但仍存在需要运行样本验证的 owner 稳定性风险。
- 2m profile 默认不应继续运行无业务必要的 body/hand 链路。
- Occupant/PersonTrack + PartTrack 已评估为非目标方案；当前不采用，不作为第一阶段或后续默认路线。
- 未来 hand tracking 增强优先考虑 HumanPose-assisted hand association，而不是引入完整 OccupantTrack。
- 对“较好的 ID 连续性”只能确认机制已存在，不能确认效果已验收。
- 若要按规范直接实施代码，必须同时读取 [[02_Projects/DMS/04_Tracking/tracking_spec_current]]。
- 设计文件不承载 `sync_mode`、`default_entry_verified` 这类回写决策字段；这类字段只在 overview/validation 中收口。

## 0.6 Known Gaps

- 2m/5m 第一层 profile 分流已在 2026-06-17 单步实现并通过本地编译和独立 review；设计层仍不把它提升为运行验收闭合，2m stale body/hand 输出和 5m driver-bound evidence 仍需 runtime replay。
- 5m body evidence 已在 2026-06-17 收缩为 selected driver face-bound acquisition/publish；设计层仍不把它提升为运行验收闭合，driver-bound hand evidence 和 bounded cache 仍需后续实现或验证。
- hand 内部 body 输入已在 2026-06-17 从 legacy body output map 隔离为局部 finalized driver body evidence snapshot；设计层仍不把它提升为运行验收闭合，hand owner source 与 left/right slot 仍需序列验证。
- face 区域级唯一输出运行验证：未闭合
- left_hand / right_hand 区域级唯一输出运行验证：未闭合
- 运行时 replay / 视频证据：未闭合
- head-first 第一阶段实现：已本地编译通过；2026-06-12 后排误跟踪主驾问题样本已完成板端回灌验证，更广泛代表性样本仍未闭合

## 0.7 Historical Mapping

- baseline 设计由 [[座舱乘员多目标跟踪方案]] 提供。
- body/face/hand 解耦、retired body handoff 清理、左右手槽位和连续性优化来自 2026-03-25 与 2026-03-31 的 delta 收敛；2026-06-16 方案整理明确继承其“身份 owner 与部件生命周期分离”原则，但不继承 body-first identity 主线。
- 2026-04-05 的快速运动恢复修复只影响实现与验证边界，不改变本文件的设计职责。
- 2026-05-09 决策记录将 body-first 归档为历史主线，head-first 定为下一阶段推荐主线，OccupantTrack 归档为当前不采用的非目标方案。

## 0.8 Current Sync Rule

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
