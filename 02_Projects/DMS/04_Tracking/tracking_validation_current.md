---
title: Tracking Validation Current
summary: Tracking 当前验证状态文档，记录当前已具备的证据、未闭合项、审核结论与“哪些结论只是文档推断、哪些已被代码或历史记录支撑”。
status: verified
doc_role: current
truth_role: current
current_kind: validation
lifecycle_state: active
default_entry: false
sync_required_when:
  - 证据状态变化
  - blocker 或 review 结论变化
  - 所需下一步验证变化
  - single_pass_recoverable 判定依据变化
retrieval_priority: current
supersedes:
  - 02_Projects/DMS/04_Tracking/多目标跟踪功能审核记录-2026-03-27.md
  - 02_Projects/DMS/04_Tracking/多目标跟踪设计失配修复未闭环记录-2026-03-27.md
merged_into: []
current_replacement: []
related_code:
  - /home/jichao/dms/source/utils/track.cpp
  - /home/jichao/dms/include/utils/track.h
  - /home/jichao/dms/source/fuse_algos/fuse_algorithm.cpp
sources:
  - 02_Projects/DMS/04_Tracking/多目标跟踪功能审核记录-2026-03-27.md
  - 02_Projects/DMS/04_Tracking/多目标跟踪设计失配修复未闭环记录-2026-03-27.md
  - 02_Projects/DMS/04_Tracking/多目标跟踪手部连续性优化闭环记录-2026-03-31.md
  - /home/jichao/dms/source/utils/track.cpp
scope: 适用于判断 Tracking 当前有哪些证据已经成立、哪些结论仍需更高等级验证；为默认实现输入链提供验证边界，不承接设计或规范正文。
risks:
  - 本文档没有新增运行验证，只整合现有记录并用代码静态读取校准其当前有效性。
updated_at: 2026-04-03
---

## 0.1 Evidence Status

### 0.1.1 已由代码静态证据支撑

- body 使用预测 + 匈牙利 + 生命周期管理
- face 使用恒速度模型并支持启动后解耦
- hand 使用恒加速度模型，并支持短 miss 预测输出
- body 结果作为乘员级主锚点
- 上游结果事实源是 body / face / leftHand / rightHand 四类 map
- driver body 最终唯一化已在代码中显式实现

### 0.1.2 由历史记录支撑但本轮未重新执行

- 03-24、03-25、03-31 各轮编译级验证曾通过
- 03-25、03-31 曾有独立审查通过或 pass_with_risks 记录

### 0.1.3 当前仍未被充分证据支撑

- face 区域级最终唯一输出
- left_hand / right_hand 区域级最终唯一输出
- “较好的 ID 连续性”效果性结论
- 运行时 replay / 视频流级验证

## 0.2 Current Review Conclusion

- 当前系统主框架不是“未实现”，而是“主框架已形成，但仍有输出唯一性与运行级证据缺口”
- 以本轮允许范围内的静态读取判断，`多目标跟踪功能审核记录-2026-03-27` 中关于唯一性未闭合和 ID 连续性证据不足的结论仍然有效
- `多目标跟踪设计失配修复未闭环记录-2026-03-27` 记录的是一次中间阻塞状态，已经不再代表当前整体状态

## 0.3 Required Next Verification

- 如果要把 Tracking 从“当前实现已形成”推进到“功能验收接近闭合”，优先补：
  1. face 区域级唯一输出验证
  2. left/right hand 区域级唯一输出验证
  3. 代表性视频或日志回放，验证 ID 连续性和 hand continuity 优化

## 0.4 Current Boundary

本文档只回答当前证据状态，不等价于重新执行完整审核。若后续代码变更 touching `track.cpp`、`AtomicResult` 或导出链路，应重新做 `knowledge_sync_check` 并更新本文件。

## 0.5 Single-Pass Recoverability Verdict

- single_pass_recoverable: `true`
- 判定依据：
  - 读取 `tracking_overview_current + tracking_design_current + tracking_spec_current + tracking_implementation_current + tracking_validation_current` 已能恢复当前 Tracking 的主要设计、默认实现约束、实现事实与验证边界。
  - 只需少量代码路径辅助核对事实源：`track.h`、`track.cpp`、`atomic_result.h`、`fuse_algorithm.cpp`。
  - baseline 与历史 delta 已全部降级为 `default_entry: false`，不再承担默认恢复职责。
  - 默认情况下不再要求拼接 baseline 或两篇及以上 delta 才能理解当前态。
- 保留限制：
  - 该判定只说明“当前态可单次恢复”，不等价于“运行效果已验证闭环”。
  - 若默认恢复 bundle、事实源代码路径或历史文档入口关系变化，必须重新判定本节。

## 0.6 Historical Mapping

- 03-27 审核记录中的有效 blocker 已收敛到本文件
- 03-31 手部连续性优化的收益与风险判断也已收敛到本文件

## Current Sync Rule

- must_update_when:
  - 已有证据等级变化
  - 功能审核 blocker 被关闭或新增
  - hand continuity 的收益/风险评估变化
  - 默认恢复所需的验证边界变化
- absorbs_history_from:
  - `多目标跟踪功能审核记录-2026-03-27.md`
  - `多目标跟踪设计失配修复未闭环记录-2026-03-27.md`
  - `多目标跟踪手部连续性优化闭环记录-2026-03-31.md`
- evidence_only_docs:
  - `多目标跟踪功能审核记录-2026-03-27.md`
  - `多目标跟踪设计失配修复未闭环记录-2026-03-27.md`
- not_a_default_entry_anymore:
  - `多目标跟踪功能审核记录-2026-03-27.md`
  - `多目标跟踪设计失配修复未闭环记录-2026-03-27.md`
