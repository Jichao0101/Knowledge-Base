---
title: Tracking Design Current
summary: Tracking 当前设计文档，描述当前模块目标、层级关系、生命周期、body/face/hand 关联策略、唯一性边界与已知限制。
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
  - 02_Projects/DMS/04_Tracking/多目标跟踪设计失配修复闭环记录-2026-03-25.md
  - 02_Projects/DMS/04_Tracking/多目标跟踪生命周期与手部关联设计失配修复闭环记录-2026-03-25.md
  - 02_Projects/DMS/04_Tracking/多目标跟踪功能审核记录-2026-03-27.md
  - 02_Projects/DMS/04_Tracking/多目标跟踪手部连续性优化闭环记录-2026-03-31.md
  - /home/jichao/dms/source/utils/track.cpp
scope: 适用于恢复当前 Tracking 的设计真相，重点描述目标、边界、层级、生命周期和设计原则；不单独承担完整实现规范职责。
risks:
  - 文档明确区分“当前设计目标”和“当前代码已证实行为”；对未被代码静态证据完全支撑的项保持保守表述。
updated_at: 2026-04-03
---

## 0.1 Current Goal

当前 Tracking 仍采用 body 作为乘员级主锚点，向下派生 face、left_hand、right_hand 子轨迹，并向下游输出稳定的 body / face / left_hand / right_hand 结果。

本文件回答“当前设计是什么”，不回答全部“按什么精确规则实现代码”；实现级硬约束已收敛到 [[02_Projects/DMS/04_Tracking/tracking_spec_current]]。

## 0.2 Current Layering

- body：主轨迹，负责 `track_id` 分配、短期生命周期、稳定人员类型判定与 driver 唯一化。
- face：在稳定 body 出现后创建，key 复用 `bodyId`，启动后允许与 body 短时解耦。
- hand：每个 body 维护 `left/right` 两个槽位，key 复用 `bodyId`，启动后允许按各自槽位独立存活。

## 0.3 Current Lifecycle

### 0.3.1 body

- 以 body 检测为输入。
- 对已有轨迹先做预测，再与当前检测通过扩展损失矩阵 + 匈牙利匹配。
- 命中时 `hitCount` 增长并清零 `missCount`，丢失时 `hitCount` 衰减、`missCount` 增长。
- `missCount` 达阈值后转入 `m_retiredBodyTracks`，供 child handoff 清理使用。
- 达到 `hitThreshold` 的 body 才对外输出。

### 0.3.2 face

- 只在当前稳定 body 输出存在时为对应 `bodyId` 初始化 face。
- 已初始化 face 先按自身预测匹配，可在 body 暂时不输出时继续维持。
- 新 stable body 若与 retired body 属于同一区域，会清理旧 orphan face。
- 当前代码会先为当前 body 选择最佳 face，再将未占用且稳定的 face 作为兜底输出，因此“区域级 face 唯一”仍未被完全闭合。

### 0.3.3 hand

- 每个 body 维护 `left/right` 两个槽位，而不是统一 hand 池。
- 槽位初始化依赖 body anchor；初始化后优先按各自预测状态继续匹配。
- 未命中时手部会沿预测框短时输出，并允许短 miss window 维持连续性。
- 新 stable body 若与 retired body 属于同一区域，会清理旧 orphan hand 槽位。
- 当前代码会先为当前 body 选择最佳 left/right hand，再把未占用但满足输出条件的手槽做兜底输出，因此“区域级左右手唯一”仍未被完全闭合。

## 0.4 Current Identity And Region Rules

- `stablePersonType` 由 driver/front/back 投票累计后再解析，不按单帧直接锁定。
- driver 最终只保留一个稳定 body 输出，其余 DRIVER 候选会被降级。
- face / hand 当前只达到了“对当前稳定 body 优先选最合适 child”的程度，尚不能把区域级最终唯一完全视为已闭合。

## 0.5 Current Constraints

- body 是当前系统的主锚点；face / hand 启动与 handoff 清理都依赖 body 或 retired body anchor。
- hand 连续性已做特化优化，但仍存在 stale predicted hand 和错误关联风险。
- 对“较好的 ID 连续性”只能确认机制已存在，不能确认效果已验收。
- 若要按规范直接实施代码，必须同时读取 [[02_Projects/DMS/04_Tracking/tracking_spec_current]]。

## 0.6 Known Gaps

- face 区域级唯一输出：未闭合
- left_hand / right_hand 区域级唯一输出：未闭合
- 运行时 replay / 视频证据：未闭合

## 0.7 Historical Mapping

- baseline 设计由 [[02_Projects/DMS/04_Tracking/座舱乘员多目标跟踪方案]] 提供。
- body/face/hand 解耦、retired body handoff 清理、左右手槽位和连续性优化来自 2026-03-25 与 2026-03-31 的 delta 收敛。

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
- evidence_only_docs:
  - `多目标跟踪功能审核记录-2026-03-27.md`
  - `tracking_interfaces_current.md`
- not_a_default_entry_anymore:
  - `座舱乘员多目标跟踪方案.md`
  - `座舱多目标跟踪实现.md`
