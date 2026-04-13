---
title: Tracking Design Current
summary: Tracking 当前设计文档，只描述目标、边界、状态组织、模块耦合与非目标项，不承载实现级契约或验证结论。
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
  - 02_Projects/DMS/04_Tracking/多目标跟踪快速运动恢复阶段预测更新一致性修复闭环记录-2026-04-05.md
  - /home/jichao/dms/source/utils/track.cpp
scope: 适用于恢复当前 Tracking 的设计真相，重点描述目标、边界、层级、生命周期和设计原则；不单独承担完整实现规范职责。
risks:
  - 文档明确区分“当前设计目标”和“当前代码已证实行为”；对未被代码静态证据完全支撑的项保持保守表述。
updated_at: 2026-04-07
---

## 0.1 Current Goal

当前 Tracking 仍采用 `body` 作为乘员级主锚点，向下派生 `face`、`left_hand`、`right_hand` 子轨迹，并向下游输出稳定的 `body / face / left_hand / right_hand` 结果。

本文件只回答“当前设计是什么”，不回答全部“按什么精确规则实现代码”；实现级硬约束收敛到 [[02_Projects/DMS/04_Tracking/tracking_spec_current]]。

## 0.2 Current Layering

- `body`：主轨迹，负责乘员级身份建立、稳定人员类型判定、短期生命周期与对外唯一主锚点。
- `face`：在稳定 `body` 出现后创建，key 复用 `bodyId`，启动后允许与 `body` 短时解耦。
- `hand`：每个 `body` 维护 `left/right` 两个槽位，key 复用 `bodyId`，启动后允许按各自槽位独立存活。
- `retired body`：仅作为旧子轨迹清理和接管判断的历史锚点，不是新的主入口。

## 0.3 Current Lifecycle

### 0.3.1 body

- 以 `body` 检测为输入。
- 对已有轨迹先做预测，再与当前检测做最优关联。
- 命中时 `hitCount` 增长并清零 `missCount`，丢失时 `hitCount` 衰减、`missCount` 增长。
- `missCount` 达阈值后转入 `m_retiredBodyTracks`，供 child handoff 清理使用。
- 达到稳定阈值的 `body` 才对外输出。

### 0.3.2 face

- 只在当前稳定 `body` 输出存在时为对应 `bodyId` 初始化 `face`。
- 已初始化 `face` 先按自身预测匹配，可在 `body` 暂时不输出时继续维持。
- 新 stable `body` 若与 retired `body` 属于同一区域，会清理旧 orphan `face`。
- 当前设计保留“当前 body 优先选择最佳 face”与“未占用且稳定 face 兜底输出”的双路径，这一设计意图用于提高召回，但也意味着区域级唯一性必须放到 validation 里判定，不在 design 中假装闭合。

### 0.3.3 hand

- 每个 `body` 维护 `left/right` 两个槽位，而不是统一 hand 池。
- 槽位初始化依赖 `body` anchor；初始化后优先按各自预测状态继续匹配。
- 未命中时手部会沿预测框短时输出，并允许短 miss window 维持连续性。
- 新 stable `body` 若与 retired `body` 属于同一区域，会清理旧 orphan hand 槽位。
- 当前设计保留左右槽位的独立存活和兜底输出能力；是否已经形成区域级唯一闭合，属于 validation 负责的证据结论，不在 design 里提前写死。

## 0.4 Current Identity And Region Rules

- `stablePersonType` 由 driver/front/back 投票累计后再解析，不按单帧直接锁定。
- `driver` 目标的最终输出唯一，是 `body` 层的设计约束。
- `face / hand` 当前只达到“对当前稳定 `body` 优先选最合适 child”的设计目标，是否已经形成区域级最终唯一，需要 validation 依据代码和证据单独判定。
- 当前设计不把运行时效果验收等同于静态结构设计。

## 0.5 Current Constraints

- `body` 是当前系统的主锚点；`face / hand` 启动与 handoff 清理都依赖 `body` 或 retired `body` anchor。
- `hand` 连续性已做特化优化，但仍存在 stale predicted hand 和错误关联风险。
- 对“较好的 ID 连续性”只能确认机制已存在，不能确认效果已验收。
- 若要按规范直接实施代码，必须同时读取 [[02_Projects/DMS/04_Tracking/tracking_spec_current]]。
- 设计文件不承载 `sync_mode`、`default_entry_verified` 这类回写决策字段；这类字段只在 overview/validation 中收口。

## 0.6 Known Gaps

- face 区域级唯一输出：未闭合
- left_hand / right_hand 区域级唯一输出：未闭合
- 运行时 replay / 视频证据：未闭合

## 0.7 Historical Mapping

- baseline 设计由 [[02_Projects/DMS/04_Tracking/座舱乘员多目标跟踪方案]] 提供。
- body/face/hand 解耦、retired body handoff 清理、左右手槽位和连续性优化来自 2026-03-25 与 2026-03-31 的 delta 收敛。
- 2026-04-05 的快速运动恢复修复只影响实现与验证边界，不改变本文件的设计职责。

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
