---
title: Tracking Interfaces Evidence
summary: Tracking 接口补充证据文档，保留接口事实的独立展开说明；默认实现输入链已切换到 design/spec/implementation/validation，本文件不再作为 current 命名文档或必读入口。
status: verified
doc_role: delta
truth_role: evidence
lifecycle_state: merged
default_entry: false
sync_required_when: []
retrieval_priority: evidence_only
supersedes: []
merged_into:
  - 02_Projects/DMS/04_Tracking/tracking_implementation_current.md
  - 02_Projects/DMS/04_Tracking/tracking_spec_current.md
current_replacement:
  - 02_Projects/DMS/04_Tracking/tracking_implementation_current.md
  - 02_Projects/DMS/04_Tracking/tracking_spec_current.md
related_code:
  - /home/jichao/dms/include/models/atomic_result.h
  - /home/jichao/dms/source/models/handpose_model.cpp
  - /home/jichao/dms/source/models/humanpose_model.cpp
  - /home/jichao/dms/source/fuse_algos/fuse_algorithm.cpp
  - /home/jichao/dms/include/fuse_algos/serialize_result.h
  - /home/jichao/dms/source/fuse_algos/serialize_result.cpp
record_type: audit_record
target_current_docs:
  - 02_Projects/DMS/04_Tracking/tracking_implementation_current.md
  - 02_Projects/DMS/04_Tracking/tracking_spec_current.md
decision_scope: DMS Tracking interface evidence consolidation
sources:
  - 02_Projects/DMS/04_Tracking/多目标跟踪设计失配修复闭环记录-2026-03-25.md
  - 02_Projects/DMS/04_Tracking/多目标跟踪生命周期与手部关联设计失配修复闭环记录-2026-03-25.md
  - /home/jichao/dms/include/models/atomic_result.h
  - /home/jichao/dms/source/models/handpose_model.cpp
  - /home/jichao/dms/source/models/humanpose_model.cpp
  - /home/jichao/dms/source/fuse_algos/fuse_algorithm.cpp
  - /home/jichao/dms/include/fuse_algos/serialize_result.h
  - /home/jichao/dms/source/fuse_algos/serialize_result.cpp
scope: 适用于补充查看 Tracking 的接口事实源与兼容边界，不再作为默认实现输入链入口。
risks:
  - 当前接口说明以已读取实现文件为准，未补读所有仓外消费者。
updated_at: 2026-04-03
---

> 文档状态：本文件保留为接口补充证据，其当前有效接口事实已并入 `tracking_implementation_current` 与 `tracking_spec_current`。

## 0.1 Upstream Facts

当前 Tracking 上游事实源是四类结果 map，而不是统一 human/hand 抽象：

- `m_bodyTrackResultMap`
- `m_faceTrackResultMap`
- `m_leftHandTrackResultMap`
- `m_rightHandTrackResultMap`

## 0.2 Downstream Consumption

- `humanpose_model.cpp` 直接消费 `m_bodyTrackResultMap`
- `handpose_model.cpp` 分别消费 `m_leftHandTrackResultMap` 与 `m_rightHandTrackResultMap`
- `fuse_algorithm.cpp` 会把：
  - `m_faceTrackResultMap`
  - `m_leftHandTrackResultMap`
  - `m_rightHandTrackResultMap`
  - `m_bodyTrackResultMap`
  转存到导出结果中，并把 body 兼容映射到 `m_humanTrackResultMap`

## 0.3 Interface Boundary

- 上游当前真相源是 `body/face/leftHand/rightHand`
- `m_humanTrackResultMap` 当前属于导出兼容层，而不是 tracking 内部设计事实源
- 左右手当前不应再被重新收敛成单一 hand 真相源

## 0.4 Current Consistency

- 代码静态读取显示：序列化输出侧已存在 `m_faceTrackResultMap`、`m_leftHandTrackResultMap`、`m_rightHandTrackResultMap`
- 当前接口语义已经从“上游被下游反向塑形”收回到“上游定义事实源、下游按需兼容”

## 0.5 Known Interface Risks

- 仓外消费者若仍把旧 hand 聚合语义视为稳定契约，仍需联调确认
- 本次任务没有扩展到所有 proto / SDK 外部消费者验证

## 0.6 Historical Mapping

- 03-25 两篇 delta 记录了接口从下游反向污染恢复到上游事实源的过程
- 当前有效接口事实已并入 `tracking_spec_current` 与 `tracking_implementation_current`
- 本文件只保留补充证据和接口边界展开说明，不再承担当前真相源职责
