---
title: Tracking Spec Current
summary: Tracking 当前可执行规范文档，提供按规范实现代码所需的默认实现约束，包括必须满足的行为、接口契约、状态规则、非目标项与验证挂钩。
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
updated_at: 2026-04-03
---

## 0.1 Spec Scope

本文件回答“现在按什么规范实现 Tracking 代码”。默认实现输入链为：

1. [[02_Projects/DMS/04_Tracking/tracking_design_current]]
2. [[02_Projects/DMS/04_Tracking/tracking_spec_current]]
3. [[02_Projects/DMS/04_Tracking/tracking_implementation_current]]
4. [[02_Projects/DMS/04_Tracking/tracking_validation_current]]

baseline 和历史 delta 默认不进入实现输入链。

## 0.2 Required Behaviors

### 0.2.1 body

- 必须以 body 作为乘员级主锚点。
- 必须执行“预测 -> 关联 -> 更新/新建 -> 生命周期衰减 -> 稳定输出”主流程。
- body 输出必须只在达到稳定阈值后对外暴露。
- driver body 最终输出必须唯一。

### 0.2.2 face

- face 只能在稳定 body 存在后初始化，并继承 `bodyId`。
- face 初始化后允许与 body 短时解耦，不得在 body 暂失时被无条件同步清理。
- 新 stable body 在同一区域接管时，应基于 retired body anchor 清理 orphan face。

### 0.2.3 hand

- hand 必须按每个 body 的 `left/right` 两个槽位建模，不得退回统一 hand truth source。
- hand 初始化后允许按槽位独立存活。
- hand miss 时允许短时使用预测框维持连续性，但该策略只能在已知风险已记录的前提下保留。
- 新 stable body 在同一区域接管时，应基于 retired body anchor 清理 orphan hand 槽位。

## 0.3 Interface Contracts

- 上游 tracking 事实源必须维持为：
  - `m_bodyTrackResultMap`
  - `m_faceTrackResultMap`
  - `m_leftHandTrackResultMap`
  - `m_rightHandTrackResultMap`
- `m_humanTrackResultMap` 只可视为导出兼容层，不得再次反向塑造 tracking 上游设计。
- 下游 hand 消费必须以 left/right hand 分离结果为基础，不得把“单一 hand map”重新定义为当前真相源。

## 0.4 State / Transition Rules

- 生命周期规则必须保持 `hit` 增长/封顶、`miss` 衰减/删除的统一语义。
- child handoff 清理必须依赖 retired body anchor，而不是只依赖 child 当前几何命中。
- 若代码变更会影响以下任一对象，必须同步更新 current 文档：
  - 生命周期规则
  - 输出唯一性规则
  - 上游事实源
  - 下游兼容边界
  - hand continuity 策略

## 0.5 Non-goals

- 本规范不把“较好的 ID 连续性”直接定义为已验收效果，只约束当前机制与验证缺口的表达方式。
- 本规范不要求 baseline 继续作为实现输入。
- 本规范不要求本次文档去覆盖所有仓外消费者契约。

## 0.6 Verification Hooks

- 若实现触及 `track.cpp` 的 body/face/hand 输出逻辑，至少重新检查：
  - body 稳定输出门槛
  - driver 唯一化
  - face/hand 解耦与 handoff 清理
  - left/right hand truth source 是否被保持
- 若实现宣称修复 face/hand 区域级唯一输出，必须在 `tracking_validation_current` 中更新证据状态。
- 若实现改变接口事实源或导出兼容边界，必须同步更新 `tracking_implementation_current` 与本文件。

## 0.7 Historical Mapping

- baseline 的目标与初始思路来自 [[02_Projects/DMS/04_Tracking/座舱乘员多目标跟踪方案]]。
- 早期实现说明来自 [[02_Projects/DMS/04_Tracking/座舱多目标跟踪实现]]。
- 当前有效规范来自 design/implementation/validation current 与 2026-03-25、2026-03-31 的 delta 收敛，不再要求实现时回读 baseline。

## 0.8 Current Sync Rule

- must_update_when:
  - body/face/hand 的 required behaviors 改变
  - 上游事实源或下游兼容边界改变
  - 允许或禁止的 continuity 策略改变
  - 验证 hook 和默认实现输入链改变
- absorbs_history_from:
  - `座舱乘员多目标跟踪方案.md`
  - `座舱多目标跟踪实现.md`
  - `多目标跟踪设计失配修复闭环记录-2026-03-25.md`
  - `多目标跟踪生命周期与手部关联设计失配修复闭环记录-2026-03-25.md`
  - `多目标跟踪功能审核记录-2026-03-27.md`
  - `多目标跟踪手部连续性优化闭环记录-2026-03-31.md`
- evidence_only_docs:
  - `tracking_interfaces_current.md`
  - `多目标跟踪功能审核记录-2026-03-27.md`
- not_a_default_entry_anymore:
  - `座舱乘员多目标跟踪方案.md`
  - `座舱多目标跟踪实现.md`
