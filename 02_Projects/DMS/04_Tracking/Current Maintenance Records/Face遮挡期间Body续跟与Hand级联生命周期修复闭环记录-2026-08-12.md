---
title: Face 遮挡期间 Body 续跟与 Hand 级联生命周期修复闭环记录
summary: 将已有 Body tracking 与 Face 当帧可见性解耦，并将 Hand 生命周期严格从属于 Body；记录代码实现、编译证据和待完成的板端验证。
status: implemented
doc_role: delta
truth_role: evidence
lifecycle_state: active
default_entry: false
record_type: fix_record
project: DMS
module: 04_Tracking
scope: DmsTrack 中 Face、Body、Hand 的 owner、tracking eligibility 与删除级联。
sources:
  - /home/jichao/dms/include/utils/track.h
  - /home/jichao/dms/source/utils/track.cpp
  - /alglog/active_logs/Acore/percep/dms
  - 02_Projects/DMS/04_Tracking/tracking_design_current.md
  - 02_Projects/DMS/04_Tracking/tracking_spec_current.md
  - 02_Projects/DMS/04_Tracking/tracking_implementation_current.md
risks:
  - 已通过静态审计和 J6B 全量编译，但尚未用目标序列完成板端 runtime replay。
  - Face 真正删除后仍采用严格级联，不允许无 Face owner 的 Body 独立维持；长遮挡超过 Face 生命周期会建立新身份。
related_code:
  - /home/jichao/dms/include/utils/track.h
  - /home/jichao/dms/source/utils/track.cpp
target_current_docs:
  - 02_Projects/DMS/04_Tracking/tracking_overview_current.md
  - 02_Projects/DMS/04_Tracking/tracking_design_current.md
  - 02_Projects/DMS/04_Tracking/tracking_spec_current.md
  - 02_Projects/DMS/04_Tracking/tracking_implementation_current.md
  - 02_Projects/DMS/04_Tracking/tracking_validation_current.md
updated_at: 2026-08-12
---

## Retrieval Summary

- topic: Face 短时遮挡期间 Body 续跟，以及 Body 删除时 Hand 级联清理。
- anchors: `updateBodyTracks`, `PredictAndSelectTrackedBodyDetection`, `SelectFaceAnchoredBodyDetection`, `m_handTracks.erase`。
- fix: Body tracking 与 Face 当帧可见性解耦；Face 仅控制 acquisition；移除 retired-body/orphan Hand 生命周期。
- validation: `git diff --check` 与 J6B 全量编译通过，板端 runtime replay 待完成。
- boundary: Face track 真正删除后仍严格删除同 owner Body/Hand，不维持无 owner Body。

## 0.1 Problem And Decision

- 旧实现只遍历当帧 `missCount==0` 的 Face owner。Face 短时 miss 时，即使 Body detection 持续存在，已有 Body 也不执行 tracking，只会增加 miss。
- 旧实现把删除后的 Body 写入 `m_retiredBodyTracks`，Hand 可以继续保留，直到同区域新 Body 出现后再按 retired anchor 清理，形成独立于 Body 的残留生命周期。
- 当前决策：已有 Body 在 Face track 尚未删除期间继续使用自身运动模型匹配；Face 当帧有效才允许首次 acquisition 或 tracking 失败后的 Face-anchor reacquisition；Face 真正删除或 Body miss 达阈值时删除 Body，并同步删除同 owner Hand。

## 0.2 Implementation

- `updateBodyTracks` 分为三段：已有 Body tracking、有效 Face acquisition、命中应用与生命周期收尾。
- Face 短时 miss 但 Body tracking 命中时，Body 执行 `AdvanceHit`；只有 Body 未命中时才执行 `AdvanceMiss`。
- Face track 已删除时，Body 不再占用 detection，并在收尾阶段级联删除 Body 与同 id Hand。
- 删除 `m_retiredBodyTracks`、`SameOccupantRegionByBodyAnchor` 和 retired-body orphan Hand 清理路径。
- Hand 单侧 slot 仍按自身 `hand.missThreshold` reset；两侧均未初始化时删除空 owner state。
- public `DmsTrack::Init/Update` 和四类 legacy output map 未变化；未新增中间领域类型。

## 0.3 Verification

- 代码提交：`/home/jichao/dms` 的 `3a2ed302 Fix Body and Hand lifecycle coupling`，本地提交，未推送。
- `git diff --check`：通过。
- stale-code audit：`m_retiredBodyTracks`、`cleanupOrphanAndExpiredHandSlots`、`SameOccupantRegionByBodyAnchor` 在 `track.h/track.cpp` 中均无残留引用。
- `bash scripts/compile_j6b.sh`：通过，输出 `[100%] Built target sdk`。
- runtime replay / 板端目标序列：未执行；不能据此声明 Face 遮挡恢复和 Hand 左右稳定性已经效果闭环。

## 0.4 Supersession Boundary

本记录不改写历史记录。历史 retired-body/orphan cleanup 方案仍作为当时实现证据保留；其当前有效结论由 Tracking current 文档组替代。默认入口、恢复顺序和 `recoverability_status: partial` 不变，不声明 `single_pass_recoverable: true`。
