---
title: Tracking Validation Current
summary: Tracking 当前验证状态文档，记录当前代码仓已具备的证据等级、仍未闭合的运行验证缺口和 recoverability 判定；不枚举历史提交过程。
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
  - recoverability 判定依据变化
retrieval_priority: current
supersedes:
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪功能审核记录-2026-03-27.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪设计失配修复未闭环记录-2026-03-27.md
merged_into: []
current_replacement: []
related_code:
  - /home/jichao/dms/source/utils/track.cpp
  - /home/jichao/dms/include/utils/track.h
  - /home/jichao/dms/source/fuse_algos/fuse_algorithm.cpp
sources:
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪功能审核记录-2026-03-27.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪设计失配修复未闭环记录-2026-03-27.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪手部连续性优化闭环记录-2026-03-31.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/DMS主驾打哈欠误报修复闭环记录-2026-04-05.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/后排乘客头部误跟踪为副驾驶修复闭环记录-2026-04-05.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪快速运动恢复阶段预测更新一致性修复闭环记录-2026-04-05.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/跟踪框越界导致板端coredump调查与修复闭环记录-2026-04-07.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/2m摄像头后排head误绑定主驾修复闭环记录-2026-05-08.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/head-first优先于body-first跟踪主线决策记录-2026-05-09.md
  - 02_Projects/DMS/04_Tracking/head-first跟踪方案.md
  - 02_Projects/DMS/04_Tracking/tracking_implementation_current.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack基线对比与HeadFirst路线收缩设计记录-2026-06-16.md
  - 90_Archive/02_Projects/DMS/04_Tracking/Current Maintenance Records/Tracking方案优化与历史实现归档记录-2026-06-16.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/head-first跟踪代码重构闭环记录-2026-05-23.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack内部结构与可读性重构分析-2026-06-08.md
  - /home/jichao/dms/source/utils/track.cpp
scope: 适用于判断 Tracking 当前有哪些证据已经成立、哪些结论仍需更高等级验证；为默认实现输入链提供验证边界，不承接设计或规范正文。
risks:
  - 本文档只记录当前验证状态和证据边界；每个历史小步的详细验证记录保留在 Current Maintenance Records 与 subpower_runs。
  - 当前已有编译/静态审查证据不能替代 runtime replay、单元测试或代表性视频集验收。
updated_at: 2026-06-17
---

## 0.1 Evidence Status

### 0.1.1 已由当前代码静态证据支撑

- head/face 使用恒速度模型并作为 identity 主锚点
- body/torso evidence 以 head trackId 为 key，使用预测、匹配、acquisition 与生命周期管理
- hand 使用恒加速度模型，但 2026-04-07 起不再向下游输出 miss 预测框
- body 结果作为 head-owned evidence legacy 输出，不再作为乘员级主锚点
- 上游结果事实源是 body / face / leftHand / rightHand 四类 map
- driver head 最终唯一化已在代码中显式实现
- 更新顺序为 `face/head -> selectDriverHead -> body evidence -> hand evidence`
- 配置从 `track_params.json` 读取，并以 `DEFAULT` 加车型覆盖
- `camera_type == "2m"` 时 body/hand phase 被跳过，旧 body/retired body/hand cache 会被清理
- 5m/default profile 下 body evidence 只对 selected driver face 获取和发布，非 driver body cache 不发布
- hand 内部 body 输入来自 `updateBodyTracks` 返回的 `driverBodyEvidence` snapshot，不再反读 `curResult->m_bodyTrackResultMap`
- `m_humanTrackResultMap` 只是导出兼容层，不是上游事实源
- track 输出在写入四类 track map 前已有统一 sanitize/clamp 与非法框过滤
- initialized face first pass 已有连续性门控；driver 相关 face 绑定使用更严格的 `distanceLoss <= 0.45`
- first pass 被连续性门控明确拒绝的 face track，同帧不会再通过 second pass 绕回匹配
- 2026-06-12 后，driver face selection 已验证在目标 2m 回灌样本中不会选择 stable BACK_PASSENGER 后排候选，且不依赖收紧 `distanceLoss`。
- 当前代码已完成 head-first 第一轮实现：driver identity 来自 head/face track，body/hand 作为 head-bound evidence 组织

### 0.1.2 已有验证证据等级

- `bash scripts/compile_j6b.sh`：head-first 第一轮、2026-06-17 profile split、driver-bound body evidence、body-to-hand snapshot 和三笔 hand lambda 可读性整理均已有通过记录，最终目标为 `[100%] Built target sdk`。
- `git diff --check`：上述 2026-06-17 代码小步均已有通过记录。
- 独立 review：profile split、driver-bound body evidence、body-to-hand snapshot 和三笔 hand lambda 可读性整理均已有 `approved` 记录。
- `interface-abstraction-implementation-guard`：body-to-hand snapshot 涉及 private phase-level 方法签名变化，已有守门和 diff 审计记录；三笔 hand lambda 整理未改变 header/private phase 方法签名。
- 板端/日志样本：2026-06-12 后排误跟踪主驾样本二次回灌中 `face-first driver face select face=1` 为 0 次，`face=0` 为 189 次，`reject back passenger` 为 126 次，`reject smaller face=1` 为 61 次。
- 历史 coredump 修复已有目标帧覆盖且未再出现 `abort` / `core dumped` 的板端记录，但该记录不代表 hand 功能指标重新验收。

### 0.1.3 当前仍未被充分证据支撑

- face 区域级最终唯一输出
- left_hand / right_hand 区域级最终唯一输出
- “较好的 ID 连续性”效果性结论
- 运行时 replay / 视频流级验证
- face / hand fallback 路径是否在更广泛运行样本中完全满足唯一性约束
- 对快速运动恢复的效果改善是否能推广到代表性样本集
- 2m profile 下 body/hand output 长序列持续为空且无 stale cache 复活
- 5m profile 下 driver-bound body/hand evidence 不跨 owner
- body-to-hand finalized snapshot 下 hand owner source、left/right slot 和 orphan cleanup 的序列级行为
- 三笔 hand lambda 可读性整理只具备行为等价的静态/编译/review 证据，不证明运行效果改善

## 0.2 Current Review Conclusion

- 当前系统主框架不是“未实现”，而是“当前代码事实已形成，但仍有输出唯一性与运行级证据缺口”。
- 编译、静态检查和独立 review 足以支撑当前实现边界写入 current；不足以证明运行效果闭合。
- 2m 摄像头后排 head 误绑定主驾样本已有板端日志验证，可作为该问题样本级闭环；但不关闭整体 face 区域级唯一输出缺口。
- DMS 主驾打哈欠误报修复属于 accepted with risks 的项目闭环，不应被提升为正式知识，也不应表述为已完成根因级彻底消除。
- 跟踪框越界 coredump incident 已有 track-only 修复证据，但不构成所有 hand 相关功能指标已重新验收通过。
- 当前 current 组已能在不依赖 baseline 或多篇历史 delta 作为默认入口的前提下恢复 Tracking 主态；但运行效果仍未闭合。
- 具体历史小步的 review、命令输出、失败轮次和 superseded route 以维护记录与 subpower artifacts 为准，不在 current validation 中逐项展开。

## 0.3 Required Next Verification

- 如果要把 Tracking 从“当前实现已形成”推进到“功能验收接近闭合”，优先补：
  1. face 区域级唯一输出验证
  2. left/right hand 区域级唯一输出验证
  3. 代表性视频或日志回放，验证 ID 连续性和 hand miss 不输出后的功能影响
  4. 快速运动恢复样本，验证 body/face/hand 的 `predBox / detection / updated box` 三者关系是否按预期收敛
- 若后续要重新评估 DMS driver false-yawn 的根因消除，建议补更长窗口 replay，专门量化 identity-swap 风险
- 若后续继续优化 2m 场景，建议补更长 2m 视频集，对 `driver face reject`、`driver face match`、`driver second-pass face match orphan=` 做计数型统计，而不是只依赖抽样日志。
- 若后续进入 head-first 运行验收，必须补：
  1. `track_params.json` 车型 profile 下 body/hand disabled 且不发布 stale body/hand 的回放验证；
  2. 5m profile 下只发布 selected driver face-bound body/torso 的 owner 稳定性验证；
  3. hand owner source、left/right slot、orphan takeover 在 finalized body snapshot 边界下的手部大幅运动和多人干扰序列统计；
  4. driver identity source 日志，区分 `head_first`、`body_fallback` 与 reject reason。
- 若后续使用 HumanPose-assisted hand association，需要单独验证 wrist 已有证据链，以及 elbow/shoulder/arm direction 对 hand owner、left/right、miss recovery 的增益。
- 若后续继续沿用本轮 sanitize/clamp 方案，建议补一次日志降噪，避免 `track sanitize clamp` 在板端形成噪声洪泛
- 若后续代码再次触及 `track.cpp`、`AtomicResult` 或导出链路，应重新跑 `knowledge_sync_check`，并再次判断 recoverability 状态。

## 0.4 Current Boundary

本文档只回答当前证据状态，不等价于重新执行完整审核。若后续代码变更 touching `track.cpp`、`AtomicResult` 或导出链路，应重新做 `knowledge_sync_check` 并更新本文件。

## 0.5 Recoverability Verdict

- recoverability_status: `partial`
- 判定依据：
  - 读取 `tracking_overview_current + tracking_design_current + tracking_spec_current + tracking_implementation_current + tracking_validation_current` 已能恢复当前 Tracking 的主要设计、默认实现约束、实现事实与验证边界。
  - 只需少量代码路径辅助核对事实源：`track.h`、`track.cpp`、`atomic_result.h`、`fuse_algorithm.cpp`、`humanpose_model.cpp`、`handpose_model.cpp`。
  - baseline 与历史 delta 已全部降级为 `default_entry: false`，不再承担默认恢复职责。
  - 默认情况下不再要求拼接 baseline 或两篇及以上 delta 才能理解当前态。
  - 代码里仍存在 fallback 输出路径，但 current 文档已经明确把该风险归入验证边界，而不是恢复入口缺口。
- 保留限制：
  - 该判定只说明 current 组可恢复当前主态，不等价于运行效果已验证闭环。
  - 由于仍存在 replay、区域级唯一性、ID 连续性和 head-first 落地验证缺口，本组不声明单次恢复完全闭环。
  - 若默认恢复 bundle、事实源代码路径或历史文档入口关系变化，必须重新判定本节。

## 0.6 Historical Mapping

- 03-27 审核记录中的有效 blocker 已收敛到本文件
- 03-31 手部连续性优化的收益与风险判断也已收敛到本文件
- 2026-04-05 DMS 主驾打哈欠误报修复的 accepted-with-risks 结论已收敛到本文件，但仍保留残余风险描述
- 2026-04-05 后排乘客头部误跟踪修复的 pass-with-risks 结论已收敛到本文件
- 2026-05-08 2m 摄像头后排 head 误绑定主驾修复的板端日志证据已收敛到本文件
- 2026-05-09 head-first over body-first 决策已收敛到本文件，但不提升为已验证运行事实
- 当前 validation 仅负责证据与边界判定，不承担设计职责或实现职责

## 0.7 Current Sync Rule

- must_update_when:
  - 已有证据等级变化
  - 功能审核 blocker 被关闭或新增
  - hand continuity 的收益/风险评估变化
  - 默认恢复所需的验证边界变化
  - DMS driver false-yawn 的 acceptance standard 或风险边界变化
  - 2m 摄像头 head/body association 的 gate、日志证据或风险边界变化
  - head-first 实现、回放或板端验证证据状态变化
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
