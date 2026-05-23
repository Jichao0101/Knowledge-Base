---
title: Head-first 优先于 Body-first 的 DMS Tracking 主线决策记录 2026-05-09
summary: 记录 DMS Tracking 推荐实现主线从 body-first 收敛为 head-first 渐进方案；body-first 保留为历史实现与 legacy evidence，Occupant/PersonTrack + PartTrack 已评估但当前不采用，归档为非目标方案。2026-05-23 第一轮 head-first 已代码落地并本地编译通过。
status: verified
doc_role: decision_record
truth_role: decision
lifecycle_state: active
default_entry: false
retrieval_priority: evidence_only
record_type: architecture_decision
decision_scope: DMS Tracking head/body/hand association architecture
decision: head_first_over_body_first
implementation_state: implemented_compile_verified_no_board
related_current_docs:
  - 02_Projects/DMS/04_Tracking/tracking_overview_current.md
  - 02_Projects/DMS/04_Tracking/tracking_design_current.md
  - 02_Projects/DMS/04_Tracking/tracking_spec_current.md
  - 02_Projects/DMS/04_Tracking/tracking_implementation_current.md
  - 02_Projects/DMS/04_Tracking/tracking_validation_current.md
sources:
  - 02_Projects/DMS/04_Tracking/tracking_design_current.md
  - 02_Projects/DMS/04_Tracking/tracking_implementation_current.md
  - 02_Projects/DMS/04_Tracking/tracking_validation_current.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/2m摄像头后排head误绑定主驾修复闭环记录-2026-05-08.md
  - 02_Projects/DMS/04_Tracking/座舱乘员多目标跟踪方案.md
  - /home/jichao/dms/source/utils/track.cpp
  - /home/jichao/dms/include/utils/track.h
  - /home/jichao/dms/etc/track_params.json
  - /home/jichao/dms/etc/track_params_2m.json
scope: 适用于追溯 DMS Tracking 第一阶段 head-first 架构决策约束；第一轮实现已由 2026-05-23 闭环记录承接，不替代后续回放或板端验证。
risks:
  - 本记录是设计决策与知识库回写；代码实现和编译证据以 2026-05-23 闭环记录为准。
  - head-first 第一阶段仍需通过 2m/5m 回放和板端验证闭环。
  - Occupant/PersonTrack + PartTrack 已评估但当前不采用，不能被本记录解释为当前或默认后续实现目标。
updated_at: 2026-05-23
---

> 文档状态：本文件是项目级 architecture decision record，同时归档 body-first 历史主线的失配原因。当前态入口仍是 `tracking_overview_current`，本文件不进入默认恢复顺序。

## 0.1 Decision

当前 DMS Tracking 第一阶段推荐主线为 `head-first 渐进方案`：

- driver identity 优先由 head/face track 和 profile 约束决定；
- 2m profile 默认只保留 head/face 相关链路，关闭无业务必要的 body/hand 链路；
- 5m profile 中 body 降级为 driver head-bound body/torso evidence；
- hand 只能在 driver head-bound body/torso 或业务搜索区域范围内关联；
- 对外 `m_bodyTrackResultMap / m_faceTrackResultMap / m_leftHandTrackResultMap / m_rightHandTrackResultMap` ABI 第一阶段保持不变；
- 完整 `Occupant/PersonTrack + PartTrack` 分层当前不采用，不作为第一阶段或默认后续实现目标。

本决策在 2026-05-09 形成时不表示 head-first 已经实现；2026-05-23 后第一轮代码事实已更新为 `face/head -> selectDriverHead -> body evidence -> hand evidence`。

## 0.2 Code Facts

- 2026-05-09 当时，`DmsTrack::Update` 每帧先清空四类输出 map，再按 `updateBodyTracks -> updateFaceTracks -> updateHandTracks` 重建。
- 2026-05-23 后，`DmsTrack::Update` 已改为 `updateFaceTracks -> selectDriverHead -> updateBodyTracks -> updateHandTracks`。
- 2026-05-23 后，`face/head` 持有 identity trackId，`body/hand` 作为 head-owned evidence 继承 headId。
- `loadConfigFromJson` 当前固定读取 `track_params.json`；仓内存在 `track_params_2m.json`，但尚未形成显式运行时模式选择层。

## 0.3 Verified Problem

body-first 历史方案把 body detection box 当成稳定 driver/person anchor。实际检测模型输出的 body 更接近包含头、躯干、手臂和手部的 person 外接矩形。

当驾驶员手部伸出或摆动时，raw body box 的宽高、中心和边界可能跳变，进而污染 driver 身份 ROI 投票、face/head 候选集合、hand owner 与 left/right 槽位、orphan face/hand 接管，以及下游按 track id 消费的 driver/head/hand 语义。

2026-05-08 的 2m 记录已证明异常宽 driver body 会扩大 face 候选集合；continuity gate 和 second-pass 限制能缓解该样本，但不能修复 body anchor 语义失配。

## 0.4 Body-first Legacy Archive

body-first 曾作为 Tracking 主线：body 是乘员级 root；face/head 依附稳定 body 并复用 bodyId；hand 以 bodyId 下的 left/right 槽位维护；driver/front/back 来自 body center ROI 投票；retired body 参与 orphan child 清理和接管。

历史防护包括 small face filter、passenger region filter、initialized face continuity gate、driver second-pass strict gate、first-pass reject 不允许同帧 second-pass 绕回、driver body unique、orphan face/hand 清理、sanitize/clamp、hand hit/miss 生命周期与 left/right 槽位。

仍可复用的部分包括 body detection 作为 5m driver body/torso evidence、legacy 四类 map ABI、hand left/right 槽位、hit/miss 生命周期、Kalman、Hungarian、sanitize/clamp 等工具链。

不应继续扩大的部分包括 raw body center 决定 driver identity、异常 raw body box 扩大 face/head owner、异常 raw body box 扩大 hand owner、2m profile 在无业务必要时继续运行 body/hand 链路，以及用局部阈值补丁替代 anchor 语义修正。

## 0.5 Current Recommended Head-first Boundary

第一阶段 head-first 不引入完整 Person/Part 分层，只改变决策优先级和 profile 边界：

1. head/face track 是 driver identity 的主入口。
2. 2m profile 默认关闭 body/hand，清空或不发布 stale body/hand。
3. 5m profile 中，先由 driver head 选择，再匹配 driver body/torso evidence。
4. hand association 必须受 driver head-bound body/torso 或业务搜索区域约束。
5. body miss 不应立即破坏稳定 driver head；head miss 时才允许短期 body/torso fallback。
6. 对外 ABI 第一阶段不变，内部新增状态应保持最小化。

## 0.6 OccupantTrack Non-target

完整 `Occupant/PersonTrack + PartTrack` 已评估为非目标方案，当前不采用，也不作为后续默认路线。只有在未来出现明确新需求、ABI 重构计划、代表性 2m/5m 回放基准和 ID/owner 指标后，才可作为新的独立方案重新评估，而不是从当前 head-first 路线自然演进。

在这些条件不满足前，后续 Codex 不应把 OccupantTrack 写成第一阶段目标或后续默认路线。

## 0.7 HumanPose-assisted Hand Direction

未来若 hand association 仍不足，优先方向是 HumanPose-assisted hand tracking：`head-first driver selection -> head-bound body/torso crop -> HumanPose -> wrist/elbow/shoulder evidence -> pose-guided hand association -> HandPose / Handoff`。HumanPose 是 hand owner、left/right 和 miss recovery 的辅助 evidence，不是引入 OccupantTrack 的理由。

## 0.8 Next Implementation Guardrails

- 不恢复 body-first 作为当前主线。
- 不声称 head-first 运行效果已验收，除非回放或板端验证证据已补齐。
- 不把本决策简化成 Kalman 或阈值调参。
- 不破坏 legacy 四类 map ABI。
- profile 选择、driver identity source、head/body binding、hand owner source 必须可日志化和可回放复现。
