---
title: Tracking Overview Current
summary: Tracking 当前态唯一入口，定义默认恢复顺序、默认实现输入链、default_recovery_bundle 与真相源集合；head-first 功能主线已形成，但 2026-06-15 深模块重新评审已判定 feat/ljc/track_0609 不宜继续作为结构重构基底。
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
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack内部结构与可读性重构分析-2026-06-08.md
scope: 适用于恢复当前 Tracking 模块的整体目标、边界、入口文档与当前真相源，不展开全部历史过程。
risks:
  - 当前态判断基于代码静态读取、subpower 审查和本地编译；没有补做板端或视频回放。
  - 对“效果性目标”如 ID 连续性，只能记录当前机制与证据边界，不能把静态机制等同于最终效果验收。
updated_at: 2026-06-15
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

Tracking 当前代码事实以 `AtomicResult` 四类 map 和 `DmsTrack::Update -> updateFaceTracks -> selectDriverHead/selectDriverFace -> updateBodyTracks -> updateHandTracks` 为核心，对外仍提供 `body / face / left_hand / right_hand` 跟踪结果。2026-06-13 起，body legacy output map 不再作为 hand 阶段内部输入；body 阶段生成单帧只读 `FrameBodyView` 供 hand 阶段消费，再由同一投影写入 legacy body output。
Tracking 当前已完成 head-first 第一轮实现：driver identity 由 head/face track 决定；body 降级为 head-owned body/torso evidence；hand 只在 driver head-bound body evidence 下输出；四类 legacy map ABI 保持不变。
2026-06-12 修复 2m 回灌中后排 face/head 被误跟踪为主驾的问题：driver face 选择拒绝稳定类型为 BACK_PASSENGER 的候选；主驾 face 尺寸连续性改为“变小强惩罚、变大增益”；driver face preferred anchor 和权重从 `track_params.json` 配置读取。板端二次回灌显示 `face-first driver face select face=1` 为 0 次，后排候选通过 `reject back passenger` 或 `reject smaller` 被过滤。
2026-06-09 已完成 DmsTrack 首轮内部阶段拆分，并进一步把 Face / Body / Hand 收敛到统一 assignment helper：`Update`、Face、Body 以及 Hand 的 owner/prediction/cleanup/publish 通过 private helper 显式表达；public API、匹配核心、owner/bodyId/ID/key 和生命周期契约不变。证据级别为 patch check、QNX 编译和独立静态审查。
2026-06-11 继续完成内部语义收敛：invalid track id、unmatched index、forbidden assignment cost 和 absent diagnostic loss 已分离为明确 sentinel；Body 与 Hand 主流程显式拆为预测、分配、应用、生命周期推进和发布阶段。`bodyId / handId` 初始继承 `faceId` 数值与 map key。当前代码在 face owner 消失时会立即退休并删除 body；hand 对外发布仍要求当前已发布的 DRIVER body evidence，而 owner 消失后的 hand 内部 lifecycle 尚未闭合。2026-06-13 进一步把 hand 阶段对 body 输出的依赖从 `curResult->m_bodyTrackResultMap` 收敛为单帧 `FrameBodyView`。
2026-06-15 完成 assignment helper 删减与非对称职责分层：删除仅服务 rejection 分类日志的 edge/rejection 包装，forbidden edge 使用有限 `1e6f`，保留 `AssignmentResult`；Body 显式拆分 finalize 与 `FrameBodyView` projection，Hand 以单帧 assignment row 作为 solve/apply/miss 的共同候选域，不新增无下游用途的 hand view/payload，publish 不再推进 lifecycle。
2026-06-15 深模块重新评审进一步区分“实验分支代码事实”和“推荐结构”：public `Init/Update` 已是深接口，但 private header 已暴露完整 step-level 执行脚本；global body Hungarian 属于未隔离的算法变化，`FrameBodyView / HandSlotKey / HandAssignmentRow / AssignmentResult` 不应默认作为稳定 header 抽象。当前推荐路线为停止在 `feat/ljc/track_0609` 上继续结构叠加，从 `br_develop_forJ6b` 新开 clean branch，并只选择性重做已确认行为语义。详见 [[02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack深模块重新评审与CleanRefactor规划-2026-06-15]]。
后续若继续优化 head-first，必须读取 [[02_Projects/DMS/04_Tracking/head-first渐进跟踪方案]] 与 [[02_Projects/DMS/04_Tracking/head-first渐进跟踪实现]]；current 组记录当前事实、推荐主线和实现边界，不替代完整设计与实现文档。
当前文档入口已经从 baseline + 多篇 delta 切换为本组 current 文档；历史记录只保留为证据和决策来源，不再承担默认当前态入口职责。
当前实现输入链也已从历史补丁式恢复切换为 `design_current + spec_current + implementation_current + validation_current`。

## 0.4 Current Boundaries

- 本模块负责：检测结果关联、轨迹生命周期、人员类型稳定判定、face/hand 与 body 的关联和输出。
- 本模块不负责：新增检测器能力、运行时效果验收、下游业务判决逻辑。
- 当前仍存在的开放问题集中在代表性样本运行验证、2m/5m runtime profile、callback/fusion 同 key 消费确认和输出唯一性边界，而不是 head-first 主框架缺失。
- 当前推荐主线与当前代码事实必须分开表达：head-first 第一轮已落地并通过本地编译，但不是运行效果已验收。
- DmsTrack 内部可读性重构已通过编译和独立审查，但没有 runtime replay 或单元测试证明多帧运行等价。
- 2026-06-11 sentinel、ID 生命周期语义和 Body/Hand 阶段拆分已通过 patch check、J6B 编译和独立 review；仍未新增 runtime replay 或单元测试。
- Body 与 Hand 的统一 assignment 已改变局部匹配实现路径；2026-06-13 的 `FrameBodyView` 又改变了 hand 阶段内部 body 输入来源。后续继续扩展时仍需要更强的回归保护。
- 2026-06-15 分层修复已通过 `Utils` 和 `sdk` 构建，但尚未执行 runtime replay、单元测试、板端验证或独立 review；运行等价性仍未闭合。
- 2026-06-15 独立深模块 review 已完成并要求改变重构路线：实验分支不再作为推荐结构基底；发现 global body assignment 行为混入结构重构，以及 owner 消失后 hand slot 可能不再推进 lifecycle 的高风险缺口。
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

- 2026-06-12 已新增一次 2m 问题样本板端回灌验证，关闭“后排误跟踪为主驾”本样本；这不等价于全部代表性视频集验收。
- 2026-06-09 可读性重构未执行 runtime replay 或新增单元测试；本次板端验证按任务边界为 not required。
- face / left_hand / right_hand 的区域级最终唯一输出，仍不能被当前代码静态证据完全证明为已闭合。
- ID 连续性仍缺少运行时证据。
- head-first 第一轮已实现并通过本地编译；2m/5m profile 分流、板端/视频回放、callback/fusion 同 key 消费和 hand owner 运行日志仍需后续验证或实现。
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
