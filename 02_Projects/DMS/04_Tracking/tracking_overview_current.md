---
title: Tracking Overview Current
summary: Tracking 当前态唯一入口，定义默认恢复顺序、默认实现输入链、default_recovery_bundle 与真相源集合；当前推荐实现主线已从 body-first 收敛为 head-first 渐进方案，但代码事实仍需由 implementation_current 区分。
status: verified
doc_role: current
truth_role: current
current_kind: overview
lifecycle_state: active
default_entry: true
default_entry_verified: true
sync_mode: current_rewrite
current_files_must_update:
  - 02_Projects/DMS/04_Tracking/tracking_overview_current.md
  - 02_Projects/DMS/04_Tracking/tracking_design_current.md
  - 02_Projects/DMS/04_Tracking/tracking_spec_current.md
  - 02_Projects/DMS/04_Tracking/tracking_implementation_current.md
  - 02_Projects/DMS/04_Tracking/tracking_validation_current.md
history_files_to_mark:
  - 02_Projects/DMS/04_Tracking/座舱乘员多目标跟踪方案.md
  - 02_Projects/DMS/04_Tracking/座舱多目标跟踪实现.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/tracking_interfaces_evidence.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪实现闭环记录-2026-03-24.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪设计失配修复闭环记录-2026-03-25.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪生命周期与手部关联设计失配修复闭环记录-2026-03-25.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪功能审核记录-2026-03-27.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪设计失配修复未闭环记录-2026-03-27.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪手部连续性优化闭环记录-2026-03-31.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/后排乘客头部误跟踪为副驾驶修复闭环记录-2026-04-05.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪快速运动恢复阶段预测更新一致性修复闭环记录-2026-04-05.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/跟踪框越界导致板端coredump调查与修复闭环记录-2026-04-07.md
recoverability_status: partial
sync_required_when:
  - 默认恢复顺序变化
  - 默认实现输入链变化
  - current 文档角色分层变化
  - default_recovery_bundle 变化
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
  - /home/jichao/dms/source/fuse_algos/fuse_algorithm.cpp
  - /home/jichao/dms/source/models/handpose_model.cpp
  - /home/jichao/dms/source/models/humanpose_model.cpp
sources:
  - 02_Projects/DMS/04_Tracking/座舱乘员多目标跟踪方案.md
  - 02_Projects/DMS/04_Tracking/座舱多目标跟踪实现.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪实现闭环记录-2026-03-24.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪设计失配修复闭环记录-2026-03-25.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪生命周期与手部关联设计失配修复闭环记录-2026-03-25.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪功能审核记录-2026-03-27.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪设计失配修复未闭环记录-2026-03-27.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪手部连续性优化闭环记录-2026-03-31.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/后排乘客头部误跟踪为副驾驶修复闭环记录-2026-04-05.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪快速运动恢复阶段预测更新一致性修复闭环记录-2026-04-05.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/跟踪框越界导致板端coredump调查与修复闭环记录-2026-04-07.md
  - /home/jichao/dms/include/utils/track.h
  - /home/jichao/dms/source/utils/track.cpp
  - /home/jichao/dms/include/models/atomic_result.h
  - /home/jichao/dms/source/models/handpose_model.cpp
  - /home/jichao/dms/source/models/humanpose_model.cpp
  - /home/jichao/dms/source/fuse_algos/fuse_algorithm.cpp
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/head-first优先于body-first跟踪主线决策记录-2026-05-09.md
  - 02_Projects/DMS/04_Tracking/head-first渐进跟踪方案.md
  - 02_Projects/DMS/04_Tracking/head-first渐进跟踪实现.md
scope: 适用于恢复当前 Tracking 模块的整体目标、边界、入口文档与当前真相源，不展开全部历史过程。
risks:
  - 当前态判断基于本次允许范围内的代码静态读取与既有项目记录，没有补做新的编译或运行回放。
  - 对“效果性目标”如 ID 连续性，只能记录当前机制与证据边界，不能把静态机制等同于最终效果验收。
updated_at: 2026-05-13
---

## 0.1 Current Scope

本组 current 文档回答“现在的 Tracking 系统是什么”，并且只允许一个默认入口：`tracking_overview_current`。

默认恢复顺序固定为：

1. [[02_Projects/DMS/04_Tracking/tracking_overview_current]]
2. [[02_Projects/DMS/04_Tracking/tracking_design_current]]
3. [[02_Projects/DMS/04_Tracking/tracking_spec_current]]
4. [[02_Projects/DMS/04_Tracking/tracking_implementation_current]]
5. [[02_Projects/DMS/04_Tracking/tracking_validation_current]]

若任务目标是“按规范实现代码”，默认实现输入链固定为：

1. [[02_Projects/DMS/04_Tracking/tracking_design_current]]
2. [[02_Projects/DMS/04_Tracking/tracking_spec_current]]
3. [[02_Projects/DMS/04_Tracking/tracking_implementation_current]]
4. [[02_Projects/DMS/04_Tracking/tracking_validation_current]]

[[02_Projects/DMS/04_Tracking/Current Maintenance Records/tracking_interfaces_evidence]] 只保留为接口补充证据，不进入默认恢复顺序，也不进入默认实现输入链。

## 0.2 Default Recovery Bundle

默认恢复 bundle 为最小可恢复集合，不要求先读 baseline 或两篇及以上 delta：

default_recovery_bundle:
1. [[02_Projects/DMS/04_Tracking/tracking_overview_current]]
2. [[02_Projects/DMS/04_Tracking/tracking_design_current]]
3. [[02_Projects/DMS/04_Tracking/tracking_spec_current]]
4. [[02_Projects/DMS/04_Tracking/tracking_implementation_current]]
5. [[02_Projects/DMS/04_Tracking/tracking_validation_current]]
6. 关键代码路径：
   - `/home/jichao/dms/include/utils/track.h`
   - `/home/jichao/dms/source/utils/track.cpp`
   - `/home/jichao/dms/include/models/atomic_result.h`
   - `/home/jichao/dms/source/fuse_algos/fuse_algorithm.cpp`
   - `/home/jichao/dms/source/models/handpose_model.cpp`
   - `/home/jichao/dms/source/models/humanpose_model.cpp`

## 0.3 Current Truth

- primary_truth_source_set:
  - `tracking_overview_current`
  - `tracking_design_current`
  - `tracking_spec_current`
  - `tracking_implementation_current`
  - `tracking_validation_current`
- auxiliary_evidence_set:
  - `tracking_interfaces_evidence`
  - merged `fix_record / investigation_record` 仅承担追溯与证据补充
  - `/home/jichao/dms/include/utils/track.h`
  - `/home/jichao/dms/source/utils/track.cpp`
  - `/home/jichao/dms/include/models/atomic_result.h`
  - `/home/jichao/dms/source/fuse_algos/fuse_algorithm.cpp`
  - `/home/jichao/dms/source/models/handpose_model.cpp`
  - `/home/jichao/dms/source/models/humanpose_model.cpp`

Tracking 当前代码事实仍以 `AtomicResult` 四类 map 和 `DmsTrack::Update -> updateBodyTracks -> updateFaceTracks -> updateHandTracks` 为核心，对外仍提供 `body / face / left_hand / right_hand` 跟踪结果。
Tracking 当前推荐下一阶段实现主线为 head-first 渐进方案：driver identity 优先由 head/face track 决定；body 降级为 5m 场景下的 driver body/torso evidence；hand 只在 driver head-bound body/torso 或业务搜索区域内关联；2m 或 face/head only 模式默认关闭 body/hand 链路。
下一阶段若实现 head-first，必须读取 [[02_Projects/DMS/04_Tracking/head-first渐进跟踪方案]] 与 [[02_Projects/DMS/04_Tracking/head-first渐进跟踪实现]]；current 组只保留当前事实、推荐主线和实现边界，不替代完整设计与实现文档。
当前文档入口已经从 baseline + 多篇 delta 切换为本组 current 文档；历史记录只保留为证据和决策来源，不再承担默认当前态入口职责。
当前实现输入链也已从历史补丁式恢复切换为 `design_current + spec_current + implementation_current + validation_current`。

## 0.4 Current Boundaries

- 本模块负责：检测结果关联、轨迹生命周期、人员类型稳定判定、face/hand 与 body 的关联和输出。
- 本模块不负责：新增检测器能力、运行时效果验收、下游业务判决逻辑。
- 当前仍存在的开放问题集中在验证与输出唯一性边界，而不是主框架缺失。
- 当前推荐主线与当前代码事实必须分开表达：head-first 是下一阶段实现依据，不是已经落地的代码事实。
- `tracking_interfaces_evidence` 不再承担默认输入职责，只作为接口边界的辅助证据。

## 0.5 Current Document Roles

- baseline：
  - [[02_Projects/DMS/04_Tracking/座舱乘员多目标跟踪方案]]
  - [[02_Projects/DMS/04_Tracking/座舱多目标跟踪实现]]
- current：
  - [[02_Projects/DMS/04_Tracking/tracking_overview_current]]
  - [[02_Projects/DMS/04_Tracking/tracking_design_current]]
  - [[02_Projects/DMS/04_Tracking/tracking_spec_current]]
  - [[02_Projects/DMS/04_Tracking/tracking_implementation_current]]
  - [[02_Projects/DMS/04_Tracking/tracking_validation_current]]
- evidence/reference only：
  - [[02_Projects/DMS/04_Tracking/Current Maintenance Records/tracking_interfaces_evidence]]
- merged delta：
  - 2026-03-24 实现闭环
  - 2026-03-25 两篇设计失配修复闭环
  - 2026-03-27 功能审核
  - 2026-03-31 手部连续性优化闭环
  - 2026-04-05 快速运动恢复阶段预测更新一致性修复闭环
- decision/archive：
  - 2026-05-09 head-first 优先于 body-first 跟踪主线决策记录
- implementation reference：
  - [[02_Projects/DMS/04_Tracking/head-first渐进跟踪方案]]
  - [[02_Projects/DMS/04_Tracking/head-first渐进跟踪实现]]
- superseded delta：
  - 2026-03-27 设计失配修复未闭环记录

## 0.6 Current Recovery Rule

若只为理解当前 Tracking 状态，默认不再需要按时间顺序重放全部历史文档。只有在以下情况才回读 delta：

- 需要看某个设计修复的证据链
- 需要追溯某个开放问题何时暴露
- 需要核对 current 文档中的历史映射

若只为按规范实施代码，默认也不再需要回读 baseline；只有在需要追溯原始设计动机时才回读 [[02_Projects/DMS/04_Tracking/座舱乘员多目标跟踪方案]]。
若仍需要依赖 baseline、两篇及以上 delta 或长段代码阅读才能恢复关键机制、实现落点或验证边界，则本组 current 不能声明单次恢复完全闭环。

## 0.7 Known Gaps

- 当前未新增本轮编译或运行时回放验证，验证结论以既有记录和代码静态读取为主。
- face / left_hand / right_hand 的区域级最终唯一输出，仍不能被当前代码静态证据完全证明为已闭合。
- ID 连续性仍缺少运行时证据。
- head-first 方案尚未实现；2m/5m profile 分流、driver head-first selection、head-bound body/torso 与 hand owner 仍需后续代码和回放验证。
- OccupantTrack 不作为后续默认路线；未来 hand 增强优先验证 HumanPose-assisted hand association。

## 0.8 Historical Mapping

- 初始设计目标与分层来自 [[02_Projects/DMS/04_Tracking/座舱乘员多目标跟踪方案]]。
- 早期实现说明来自 [[02_Projects/DMS/04_Tracking/座舱多目标跟踪实现]]。
- 当前设计、实现规范、代码事实与验证状态已拆分到 design/spec/implementation/validation 四份 current 文档。

## 0.9 Sync Contract

- sync_mode: `current_rewrite`
- current_files_must_update:
  - `tracking_overview_current.md`
  - `tracking_design_current.md`
  - `tracking_spec_current.md`
  - `tracking_implementation_current.md`
  - `tracking_validation_current.md`
- history_files_to_mark:
  - `座舱乘员多目标跟踪方案.md`
  - `座舱多目标跟踪实现.md`
  - `多目标跟踪实现闭环记录-2026-03-24.md`
  - `多目标跟踪设计失配修复闭环记录-2026-03-25.md`
  - `多目标跟踪生命周期与手部关联设计失配修复闭环记录-2026-03-25.md`
  - `多目标跟踪功能审核记录-2026-03-27.md`
  - `多目标跟踪设计失配修复未闭环记录-2026-03-27.md`
  - `多目标跟踪手部连续性优化闭环记录-2026-03-31.md`
  - `多目标跟踪快速运动恢复阶段预测更新一致性修复闭环记录-2026-04-05.md`
- default_entry_verified: `true`
- recoverability_status: `partial`
