---
title: Head-first 双阶段 body/torso 匹配静态分析记录
summary: 重构前静态分析 DMS tracking 代码与 head-first 方案之间的差异；该记录已被 2026-05-23 head-first 跟踪代码重构闭环记录取代，仅作为 pre-refactor evidence 保留。
status: static_analysis
doc_role: investigation_record
truth_role: project_evidence
lifecycle_state: superseded
superseded_by:
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/head-first跟踪代码重构闭环记录-2026-05-23.md
analysis_date: 2026-05-23
scope: 仅适用于追溯 head-first 重构前的静态差异分析；不代表 2026-05-23 重构后的当前代码事实。
sources:
  - /home/jichao/dms/source/utils/track.cpp
  - /home/jichao/dms/include/utils/track.h
  - /home/jichao/dms/include/models/atomic_result.h
  - /home/jichao/dms/source/utils/dms_head_pos_2_face.cpp
  - /home/jichao/dms/source/models/face_landmark_model.cpp
  - /home/jichao/dms/source/models/face_recognition_model.cpp
  - 02_Projects/DMS/04_Tracking/head-first渐进跟踪方案.md
  - 02_Projects/DMS/04_Tracking/head-first渐进跟踪实现.md
  - 02_Projects/DMS/04_Tracking/tracking_implementation_current.md
  - 02_Projects/DMS/04_Tracking/tracking_spec_current.md
risks:
  - 本轮未修改代码、未编译、未运行回放、未做板端验证。
  - 当前判断基于静态代码与项目文档；运行时 ID 连续性仍需日志或回放验证。
  - 当前代码中的 orphan face/head 自维持路径可能让下游继续消费旧 DRIVER face/head。
updated_at: 2026-05-23
---

> 文档状态：本文件是 pre-refactor 静态分析记录，已被 `head-first跟踪代码重构闭环记录-2026-05-23.md` 取代。当前代码事实请读取 current 文档组和重构闭环记录。

# 1 结论

以下结论只适用于重构前代码状态。

重构前仓库代码没有实现 head-first identity。`DmsTrack::Update` 仍按 `updateBodyTracks -> updateFaceTracks -> updateHandTracks` 执行，identity/key 的主锚点仍是 body track 分配出的 `bodyId`。

现有代码中的“双阶段”不是 head-first 意义上的 body/torso acquisition：

1. 第一阶段：body track 先由 body detection 与已有 body 预测框匹配，并通过 body ROI 投票得到 `stablePersonType`。
2. face 绑定阶段：`updateFaceTracks` 遍历当前稳定输出的 body track，用 `bodyId` 绑定或更新 face track；新建 face track 时 key 直接复用 `bodyId`。
3. second pass：未匹配 face track 会对剩余 face detection 做 rematch，用于 face 自维持或 orphan face 延续；这不是由 head track 发起的 torso acquisition。

因此，当前代码主体仍是 body-first。head-first 方案中的合理双阶段应表达为：

1. head/face track 先建立并持有 driver identity。
2. 在 5m 或需要 body/hand 的业务模式下，由 driver head 主动绑定 body/torso evidence。
3. body/torso evidence 只能投影到 legacy body map 或约束 hand owner，不能反向创建、覆盖或抢占 driver identity。

# 2 关键代码事实

- `/home/jichao/dms/source/utils/track.cpp:397`：`DmsTrack::Update` 每帧清空四类输出 map 后依次执行 `updateBodyTracks`、`updateFaceTracks`、`updateHandTracks`。
- `/home/jichao/dms/source/utils/track.cpp:686`：`allocateBodyTrackId` 只分配 body id，并避开仍存活的 face/hand 子轨迹 id。
- `/home/jichao/dms/source/utils/track.cpp:735`：`computePersonType` 基于 body 框中心所在 ROI 判定 DRIVER / FRONT_PASSENGER / BACK_PASSENGER。
- `/home/jichao/dms/source/utils/track.cpp:812`：body 匹配旧轨迹或创建新轨迹时更新人员类型投票与稳定身份。
- `/home/jichao/dms/source/utils/track.cpp:896`：注释明确 face 启动依附稳定 body，但初始化后可按自身运动状态继续存在。
- `/home/jichao/dms/source/utils/track.cpp:918`：face 第一阶段遍历 `curResult->m_bodyTrackResultMap`，用 body track 发起 face 绑定。
- `/home/jichao/dms/source/utils/track.cpp:1033`：新建 face track 时 key 直接复用 `bodyId`。
- `/home/jichao/dms/source/utils/track.cpp:1054`：face 命中后从 body track 复制 `instantPersonType` 与 `stablePersonType`。
- `/home/jichao/dms/source/utils/track.cpp:1079`：unmatched face tracks 对剩余 face detections 做 second pass rematch。
- `/home/jichao/dms/source/utils/track.cpp:1268`：未被当前 body 占用的 face 仍可能经 `face_output_orphan` 输出。
- `/home/jichao/dms/source/utils/dms_head_pos_2_face.cpp:75`：head posture 按 face track id 和 landmark id 生成，写入 `m_headPostureResultMap[trackId]`。
- `/home/jichao/dms/source/models/face_landmark_model.cpp:304`：landmark 遍历 driver face track，并用 face track id 写入 `m_landmarkResultMap`。
- `/home/jichao/dms/source/models/face_recognition_model.cpp:419`：FaceID 从 driver face track 取 ROI，`trackingId_` 来自 face box id。

# 3 风险点

## 3.1 body -> head identity fallback

当前 face/head 不拥有独立 identity。face 初始化和 role 均来自 body track，orphan face 又允许短时自维持并输出。当 body track 已失效或重新分配 id 时，下游若只消费 `m_faceTrackResultMap` 中的 DRIVER face，就可能继续使用旧 driver face/head id。

## 3.2 second pass 语义混淆

当前 second pass 是 unmatched face/hand slot 的补救匹配。若后续把它解释为“尚未匹配到 head 的 body track 去剩余 head detection 中寻找匹配”，会重新引入 body 主体，把 head-first 方案退化为 body-first fallback。

## 3.3 torso 概念未落到代码

当前代码中没有独立 torso track 或 torso detection 路径；业务上说的 torso 在现实现中基本等同 body evidence。head-first 文档应继续使用 `body/torso evidence` 表达设计语义，但实现时必须明确它不是新的 identity source。

# 4 head-first 收敛约束

- head/face track 是 driver identity 主体。
- body/torso 只作为 head-bound evidence，不能单独产生 driver identity。
- body/torso 匹配可以保留预测、Hungarian、hit/miss 和 legacy map 投影，但其输出必须受 driver head 约束。
- second pass 若保留，必须说明发起者与权限：
  - face/head second pass 只能维护 head continuity。
  - body/torso second pass 只能由已选 driver head 获取 evidence。
  - unmatched body track 不得向剩余 head detection 申请 identity。
- body miss 不清空 driver head；body reappear 只能重新绑定 evidence。
- `face_output_orphan` 这类旧 driver face/head 输出路径必须在 head-first 实现中显式收敛：要么作为 head-owned continuity，要么受 current driver head 状态约束，不能作为 body-first identity fallback。

# 5 验证建议

后续若进入代码实现或验证，至少需要补充：

- `driver_identity_source=head` 的日志；
- `driver_head_id`、`bound_body_id`、`body_evidence_source` 的日志；
- body miss / body reappear 场景下 driver head 不切换的回放；
- orphan face/head 输出是否仍会被下游当作 DRIVER 的检查；
- 5m 主驾手伸中控导致 body 扩大时，driver identity 不被 body center 改写的回放；
- 2m profile 下 body/hand disabled 的输出 map 检查。

# 6 Subpower 执行记录

- execution_mode: subagent_assisted_static_analysis
- subagents:
  - repo explorer: 静态分析双阶段匹配主流程
  - repo explorer: 静态分析 identity 所有权与 fallback 风险
- code_modified: false
- build_run: false
- board_validation_run: false
- knowledge_writeback: project_record_created
