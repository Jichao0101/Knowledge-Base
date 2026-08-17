---
title: Tracking Overview Current
summary: Tracking 当前态唯一入口，定义默认恢复顺序、默认实现输入链、default_recovery_bundle 与真相源集合；当前事实基线为 feat/ljc/track_0812 提交 13efd826，Hand 已分离已有轨迹匹配与空侧获取，并在发布边界把图像左右映射为驾驶员实际左右。
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
  - 90_Archive/02_Projects/DMS/04_Tracking/座舱多目标跟踪实现.md
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
  - 90_Archive/02_Projects/DMS/04_Tracking/座舱多目标跟踪实现.md
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
  - 90_Archive/02_Projects/DMS/04_Tracking/座舱多目标跟踪实现.md
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
  - 02_Projects/DMS/04_Tracking/head-first跟踪方案.md
  - 02_Projects/DMS/04_Tracking/tracking_implementation_current.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack内部结构与可读性重构分析-2026-06-08.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack基线对比与HeadFirst路线收缩设计记录-2026-06-16.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack 当前分支跟踪架构可读性重构闭环记录-2026-08-12.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/Face遮挡期间Body续跟与Hand级联生命周期修复闭环记录-2026-08-12.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/Hand跟踪与空侧获取分离及实际左右发布映射记录-2026-08-17.md
  - 90_Archive/02_Projects/DMS/04_Tracking/Current Maintenance Records/Tracking方案优化与历史实现归档记录-2026-06-16.md
scope: 适用于恢复当前 Tracking 模块的整体目标、边界、入口文档与当前真相源，不展开全部历史过程。
risks:
  - 当前态判断基于代码静态读取、既有本地编译和用户报告的单次运行验收；没有完成代表性视频集回放。
  - 对“效果性目标”如 ID 连续性，只能记录当前机制与证据边界，不能把静态机制等同于最终效果验收。
updated_at: 2026-08-17
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

Tracking 当前代码事实以 `AtomicResult` 四类 map 和 `DmsTrack::Update -> updateFaceTracks -> selectDriverFace -> updateBodyTracks -> updateHandTracks` 为核心，对外仍提供 `body / face / left_hand / right_hand` 跟踪结果。当前代码基线为 `feat/ljc/track_0812@13efd826`。

当前实现状态：
- driver identity 由 Face track 决定；Face 跟踪的量产行为保持不变，本轮只抽取检测分类与 assignment loss 等纯计算 helper 并补充必要注释。
- 完整 face-first 帧流程、Face loss 公式、人员类型投票、DRIVER Face 过滤评分、Body/Hand 两阶段关联见 `tracking_design_current`；逐函数和状态字段映射见 `tracking_implementation_current`。
- 当前没有按 `camera_type` 跳过 body/hand 的 profile gate；每帧在 Face/driver 选择后继续执行 Body 和 Hand phase。
- Body 仍以 Face track 为 owner，但已有 Body 在 Face 短时 miss、尚未删除期间继续按自身预测匹配；只有当帧有效 Face 才允许首次 acquisition 或 tracking 失败后的 Face-anchor reacquisition。Face 真正删除或 Body miss 达阈值时删除 Body。
- Hand 读取本帧 `curResult->m_bodyTrackResultMap` 作为 body evidence；稳定 DRIVER Body 只提供同一继承 `trackId` 下的候选域。已有 Hand track 先用预测连续性匹配，匹配后剩余 detection 才能进入空侧 acquisition。
- Hand 主流程拆为 `trackExistingHands`、`acquireEmptyHandSlots`、`cleanupExpiredHandSlots`、`publishHands` 四个 private 子阶段；Body 删除时同步删除同 id Hand，不再保留 retired-body/orphan Hand 独立生命周期。
- Hand 内部 left/right 表示图像坐标侧；发布时 image-left 写入实际右手 map、image-right 写入实际左手 map，并同步修正输出 `TrackInfo::instanceType`。四类 legacy map ABI 和继承的 key 不变。
- driver face selection 当前拒绝稳定 `BACK_PASSENGER` 候选，并使用配置化 preferred anchor、变小惩罚和变大增益抑制后排误绑定。
- `DmsTrack::Init/Update` public API 和四类 legacy map ABI 保持不变；current 组记录当前事实、实现边界和验证缺口，历史记录只作为追溯证据。

## 0.4 Current Boundaries

- 本模块负责：检测结果关联、轨迹生命周期、人员类型稳定判定、face/hand 与 body 的关联和输出。
- 本模块不负责：新增检测器能力、运行时效果验收、下游业务判决逻辑。
- 当前架构口径为 face-first：Face 先建立 identity/key 和唯一 DRIVER，Body 绑定 Face，Hand 再绑定 DRIVER Body。开放问题集中在运行验证、Body 重绑定和左右 Hand 槽稳定性。
- 当前主框架已落地并通过本地编译/静态审查记录，但不是运行效果已验收。
- `3a2ed302` 与 `04da47b8` 已有全量编译通过记录；`13efd826` 已由用户报告单次运行验收通过，但没有保存为可重放的日志证据或代表性视频集统计。
- 当前优先缺口是 Face 短时 miss 下 Body 续跟的系统性验证、Body id 交接、双手交叉/跨中线序列和不同图像翻转配置下的实际左右映射验证。
- `tracking_interfaces_evidence` 不再承担默认输入职责，只作为接口边界的辅助证据。

## 0.5 Current Document Roles

- baseline / archived baseline：
  - [[座舱乘员多目标跟踪方案]]
  - [[90_Archive/02_Projects/DMS/04_Tracking/座舱多目标跟踪实现]]
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
  - [[head-first跟踪方案]]
  - [[02_Projects/DMS/04_Tracking/tracking_implementation_current]]
- superseded delta：
  - 2026-03-27 设计失配修复未闭环记录

## 0.6 Current Recovery Rule

若只为理解当前 Tracking 状态，默认不再需要按时间顺序重放全部历史文档。只有在以下情况才回读 delta：

- 需要看某个设计修复的证据链
- 需要追溯某个开放问题何时暴露
- 需要核对 current 文档中的历史映射

若只为按规范实施代码，默认也不再需要回读 baseline；只有在需要追溯原始设计动机时才回读 [[座舱乘员多目标跟踪方案]]。
若仍需要依赖 baseline、两篇及以上 delta 或长段代码阅读才能恢复关键机制、实现落点或验证边界，则本组 current 不能声明单次恢复完全闭环。

## 0.7 Known Gaps

- 2026-06-12 已新增一次 2m 问题样本板端回灌验证，关闭“后排误跟踪为主驾”本样本；这不等价于全部代表性视频集验收。
- 2026-06-09 可读性重构未执行 runtime replay 或新增单元测试；本次板端验证按任务边界为 not required。
- face / left_hand / right_hand 的区域级最终唯一输出，仍不能被当前代码静态证据完全证明为已闭合。
- ID 连续性仍缺少运行时证据。
- face-first 主线、`3a2ed302` 生命周期修复和 `04da47b8` Hand 两阶段修复已实现并完成 J6B 编译；`13efd826` 有用户报告的单次运行验收。代表性视频回放、callback/fusion 同 key 消费、Hand 继承 id 运行日志和水平翻转输入仍需后续验证。6 月分支中的 profile gate、driver-only Body 和 body-to-hand snapshot 只作为历史方案追溯，不是当前代码事实。
- OccupantTrack 不作为后续默认路线；未来 hand 增强优先验证 HumanPose-assisted hand association。

## 0.8 Historical Mapping

- 初始设计目标与分层来自 [[座舱乘员多目标跟踪方案]]。
- 早期实现说明来自已归档的 [[90_Archive/02_Projects/DMS/04_Tracking/座舱多目标跟踪实现]]。
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
