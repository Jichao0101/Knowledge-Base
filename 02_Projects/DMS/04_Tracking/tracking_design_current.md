---
title: Tracking Design Current
summary: Tracking 当前设计文档，记录 head-first 功能边界、driver face 防后排误绑定设计与 clean refactor 路线；实验分支的 step-level helper 和中间类型不再视为推荐设计。
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
  - 02_Projects/DMS/04_Tracking/座舱多目标跟踪实现.md
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
  - 02_Projects/DMS/04_Tracking/head-first渐进跟踪方案.md
  - 02_Projects/DMS/04_Tracking/head-first渐进跟踪实现.md
  - /home/jichao/dms/source/utils/track.cpp
scope: 适用于恢复当前 Tracking 的设计真相，重点描述目标、边界、层级、生命周期和设计原则；不单独承担完整实现规范职责。
risks:
  - 文档明确区分“当前设计目标”和“当前代码已证实行为”；对未被代码静态证据完全支撑的项保持保守表述。
updated_at: 2026-06-15
---

## 0.1 Current Goal

当前代码事实已采用 `head/face` 作为 identity 主锚点，向下挂载 `body/torso evidence`、`left_hand`、`right_hand` evidence，并向下游输出 `body / face / left_hand / right_hand` legacy 结果。

当前设计主线为 `head-first 渐进方案`：driver identity 由 head/face track 决定；body 不再作为 driver/person identity 的主来源，而是 head-bound body/torso evidence；hand association 必须受 driver head-bound body evidence 约束。完整设计见 [[02_Projects/DMS/04_Tracking/head-first渐进跟踪方案]]，实现记录见 [[02_Projects/DMS/04_Tracking/head-first渐进跟踪实现]]。

本文件声称 head-first 第一轮已实现并通过本地编译；运行效果、2m/5m profile 和板端/视频回放仍以 [[02_Projects/DMS/04_Tracking/tracking_validation_current]] 的证据边界为准。

本文件只回答“当前设计是什么”，不回答全部“按什么精确规则实现代码”；实现级硬约束收敛到 [[02_Projects/DMS/04_Tracking/tracking_spec_current]]。

## 0.1.1 2026-06-15 Deep Module Re-review

- public `DmsTrack::Init/Update` 已经形成深接口，不建议改变。
- 当前主要设计问题是 private header 和内部组织过浅，不是调用方边界过浅。
- `feat/ljc/track_0609` 的 solve/apply/advance/finalize/project/publish helper 树只作为实验分支代码事实，不再作为推荐层级设计。
- 推荐从 `br_develop_forJ6b` 新开 clean branch，以 face/body/hand phase-level helper 为主，单帧 row/key/result/snapshot 使用最低必要可见性。
- Face/Body/Hand 统一 assignment solver 是明确目标：Face 已在 clean branch 完成等价迁移，Body 已从逐 owner greedy 改为全局 Hungarian，Hand 仍待从 owner 内 two-pass 改为全局 slot assignment；三者仍必须分别按等价迁移、算法变化和生命周期契约管理，不能统一归入可读性重构。

## 0.2 Current Layering

- 内部职责按短期 matching、长期 state apply、cleanup/finalize、必要的 projection、pure publish 分层；分层不要求 face/body/hand 机械拥有同形 stage。
- body -> hand 确实需要同帧 finalized body 契约，但不预设必须使用 header-level `FrameBodyView`；优先复用局部 `const map/vector` 或 `.cpp` internal snapshot。
- 通用 solver 只统一 expanded matrix、dummy、forbidden 和结果解析，不统一各 phase 的 row 方向、领域 gating、cost 或 lifecycle；最小 `AssignmentResult`、solver row 和 slot key 降级到 `.cpp` 或函数局部。
- `head/face`：当前 driver identity 的主入口，负责稳定 driver/head 选择和后续 face/head 模型输入。
- `body`：当前代码中的 head-owned body/torso evidence，不再单独决定 driver identity。
- `hand`：当前代码中按 head-owned body evidence id 维护 `left/right` 两个槽位，输出 key 与 driver headId 对齐；hand 阶段只消费 body 阶段给出的单帧 `FrameBodyView`，不再读取 body legacy output map 作为内部输入。
- `retired body`：仅作为旧 evidence/hand 槽位清理的历史锚点，不是新的主入口。
- finalized body snapshot：body 阶段产生的单帧只读事实，只用于 hand 阶段和 legacy body publish；具体表示不进入稳定 header 契约，`FrameBodyView` 仅是实验分支当前实现。
- ID 数值来源与生命周期所有权分离：`bodyId / handId` 初始继承 `faceId` 数值和 map key。当前实现中 body 在 face owner 消失时立即退休；hand 的 owner-disappearance lifecycle 尚未形成明确、已验证契约。

## 0.3 Current Lifecycle

### 0.3.1 body/torso evidence

- 以 `body` 检测作为 evidence 输入。
- 每个有效 head 主动维护自己的 body/torso evidence。
- Body 全局 assignment 中，已有 evidence 的 head 同时提供 body 运动预测 tracking cost 与 head geometry acquisition cost，但 evaluator 保留 tracking-first 层级：在 loss 完成场景标定前，已有 body track 只接受可靠 tracking edge，tracking 不可靠则 miss，不使用 acquisition 重新绑定；acquisition 只用于新 owner 首次绑定。tracking loss、acquisition loss、driver/non-driver bias 与 `dummyLoss` 必须用冲突样例标定，否则未来打开 initialized fallback 时仍可能误绑定到其他人的 body。
- 新 head 或未绑定 body 的 head 也使用同一套 acquisition 逻辑首次获取 body evidence。
- 命中时 `hitCount` 增长并清零 `missCount`，丢失时 `hitCount` 衰减、`missCount` 增长。
- `missCount` 达阈值后转入 `m_retiredBodyTracks`，供 child handoff 清理使用。
- 达到稳定阈值的 `body` evidence 才对外输出，legacy map key 使用 head trackId。
- body 的稳定输出不能单独成为 driver identity 的主来源。

### 0.3.2 face

- face/head 先于 body evidence 更新，使用自身预测、size continuity 和 distance gate 匹配当前 face detection。
- 未匹配 face detection 通过 head/face id 分配入口创建新 identity。
- driver head 由 `selectDriverHead` 基于 driver ROI、小脸过滤、front passenger 排除、size continuity 和位置 loss 选择。
- 区域级唯一性和运行中 id 连续性仍必须放到 validation 中判定，不在 design 中假装闭合。

### 0.3.3 hand

- 每个 head-owned body evidence 维护 `left/right` 两个槽位，而不是统一 hand 池。
- 槽位初始化依赖 driver head-bound body evidence；初始化后优先按各自预测状态继续匹配。
- 未命中时手部会沿预测框短时输出，并允许短 miss window 维持连续性。
- 新 stable head-owned body evidence 若与 retired evidence 属于同一区域，会清理旧 orphan hand 槽位。
- 当前设计保留左右槽位的独立存活，但对外输出 key 必须回到当前 driver headId；是否已经形成运行级唯一闭合，属于 validation 负责的证据结论，不在 design 里提前写死。
- face 消失后，内部 body retired anchor 或 hand slot 可在各自清理阈值内保留原始继承 id；这不放宽 hand 发布条件，hand 对外输出仍依赖当前允许发布的 DRIVER body evidence。

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

- face 区域级唯一输出运行验证：未闭合
- left_hand / right_hand 区域级唯一输出运行验证：未闭合
- 运行时 replay / 视频证据：未闭合
- head-first 第一阶段实现：已本地编译通过；2026-06-12 后排误跟踪主驾问题样本已完成板端回灌验证，更广泛代表性样本仍未闭合

## 0.7 Historical Mapping

- baseline 设计由 [[02_Projects/DMS/04_Tracking/座舱乘员多目标跟踪方案]] 提供。
- body/face/hand 解耦、retired body handoff 清理、左右手槽位和连续性优化来自 2026-03-25 与 2026-03-31 的 delta 收敛。
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
