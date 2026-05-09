---
title: Tracking Validation Current
summary: Tracking 当前验证状态文档，记录 body-first 代码事实证据、2m 局部修复证据、head-first 决策边界、缺失证据和下一轮验证路径。
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
  - 02_Projects/DMS/04_Tracking/DMS主驾打哈欠误报修复闭环记录-2026-04-05.md
  - 02_Projects/DMS/04_Tracking/后排乘客头部误跟踪为副驾驶修复闭环记录-2026-04-05.md
  - 02_Projects/DMS/04_Tracking/多目标跟踪快速运动恢复阶段预测更新一致性修复闭环记录-2026-04-05.md
  - 02_Projects/DMS/04_Tracking/跟踪框越界导致板端coredump调查与修复闭环记录-2026-04-07.md
  - 02_Projects/DMS/04_Tracking/2m摄像头后排head误绑定主驾修复闭环记录-2026-05-08.md
  - 02_Projects/DMS/04_Tracking/head-first优先于body-first跟踪主线决策记录-2026-05-09.md
  - 02_Projects/DMS/04_Tracking/head-first渐进跟踪方案.md
  - 02_Projects/DMS/04_Tracking/head-first渐进跟踪实现.md
  - /home/jichao/dms/source/utils/track.cpp
scope: 适用于判断 Tracking 当前有哪些证据已经成立、哪些结论仍需更高等级验证；为默认实现输入链提供验证边界，不承接设计或规范正文。
risks:
  - 本文档已整合 2026-05-08 的 2m dump 板端日志验证，但仍不等价于完整代表性视频集验收。
updated_at: 2026-05-09
---

## 0.1 Evidence Status

### 0.1.1 已由代码静态证据支撑

- body 使用预测 + 匈牙利 + 生命周期管理
- face 使用恒速度模型并支持启动后解耦
- hand 使用恒加速度模型，但 2026-04-07 起不再向下游输出 miss 预测框
- body 结果作为乘员级主锚点
- 上游结果事实源是 body / face / leftHand / rightHand 四类 map
- driver body 最终唯一化已在代码中显式实现
- 更新顺序为 `body -> face -> hand`
- 配置从 `track_params.json` 读取，并以 `DEFAULT` 加车型覆盖
- `m_humanTrackResultMap` 只是导出兼容层，不是上游事实源
- track 输出在写入四类 track map 前已有统一 sanitize/clamp 与非法框过滤
- initialized face first pass 已有连续性门控；driver 相关 face 绑定使用更严格的 `distanceLoss <= 0.45`
- first pass 被连续性门控明确拒绝的 face track，同帧不会再通过 second pass 绕回匹配
- 当前代码仍是 body-first：driver identity 来自 body center ROI 投票，face/hand 仍围绕 bodyId 组织。
- head-first 尚未实现，当前没有编译、回放或板端证据证明其运行效果。
- head-first 设计方案已落点到 `head-first渐进跟踪方案.md`，实现方案已落点到 `head-first渐进跟踪实现.md`，但两者均无代码实现、回放或板端证据。

### 0.1.2 由历史记录支撑但本轮未重新执行

- 03-24、03-25、03-31 各轮编译级验证曾通过
- 03-25、03-31 曾有独立审查通过或 pass_with_risks 记录
- 2026-04-05 DMS 主驾打哈欠误报修复已按 revised acceptance sign-off：
  - 最终接受的实现仅保留在 `/home/jichao/dms/source/utils/track.cpp`
  - acceptance standard: whole-process driver tracking remains normal；在 `3429360843..3441459880` 内最多允许 `4` 帧 yawn-positive
  - board/log facts: driver track id unique value `0`，yawn-positive frame count `4`，driver face logs 具备 `candidates=1` 且频繁出现 `small_filtered=1`
  - review outcome: `pass_with_risks`
- 2026-04-05 快速运动恢复阶段预测-更新一致性修复已完成：
  - `/home/jichao/dms/source/utils/track.cpp` 对 body/face/hand 的命中检测更新路径做了收敛
  - compile result: `bash scripts/compile_j6b.sh` passed，最终 `[100%] Built target sdk`
  - review outcome: `pass_with_risks`
  - current evidence level 仍为 compile/review 级，不是运行样本级
- 2026-04-05 的修复仍未补运行回放证据，因此它只能支撑实现边界，不支撑效果验收
- 2026-04-05 后排乘客头部误跟踪为副驾驶修复已完成：
  - 当前代码已移除 body small-face 判定污染并收敛 unique-driver 回退逻辑
  - repo review 结论为 `pass_with_risks`
  - 仍缺最终问题样本日志级验收，因此只能作为实现/验证边界补充，不能视为功能完全闭环
- 2026-04-07 跟踪框越界导致板端 coredump 调查与修复已完成：
  - 代码改动仅落在 `/home/jichao/dms/source/utils/track.cpp`
  - compile result: `bash scripts/compile_j6b.sh` passed，最终 `[100%] Built target sdk`
  - board result: 新 `sdk` 已部署到 `192.168.2.10:/userdata/dms/sdk`，`bash run.sh` 覆盖到目标帧 `3425547100` 且未再出现 `abort` / `core dumped`
  - review outcome: `pass_with_risks`
  - 残余风险：sanitize clamp 日志可能过多；hand miss 不输出后，HandOff 等下游会更频繁看到空 hand map，需要单独做功能侧确认

### 0.1.3 2026-05-08 2m 摄像头后排 head 误绑定主驾修复证据

- 代码范围：
  - `/home/jichao/dms/source/utils/track.cpp`
- 本地编译：
  - `bash scripts/compile_j6b.sh` passed，最终 `[100%] Built target sdk`
- 独立 repo review：
  - 最终结论 `pass`
  - 确认 first-pass reject 不再被 second-pass 绕回，driver second-pass face 使用 strict gate
- 板端验证：
  - 新 `sdk` 已部署到 `root@192.168.2.10:/userdata/dms/sdk`
  - 运行命令：`cd /userdata/dms && sh run.sh`
  - 回灌样本：`/userdata/dms/dumps_2m/dumps_20260507_02/images`
  - run 结束方式：收集到证据后手动 kill `sdk` 进程，退出码 137 属于预期清理
- 关键日志事实：
  - 异常宽 driver body 场景下，非主驾候选被拒绝：
    - `driver face reject body=1 det=1 score=3.38 iou=1.00 dist=0.57 size=1.81`
    - `driver face reject body=1 det=2 score=2.58 iou=1.00 dist=0.77 size=0.81`
  - 主驾 face 仍稳定匹配：
    - `driver face match body=1 det=0 candidates=3 small_filtered=0 score=0.25 iou=0.18 dist=0.05 size=0.02`
    - `track det-hit body=1 det=0 instance=face stable=DRIVER`
  - 下游继续消费同一 driver/head track：
    - `Headface found: TrackID=1`
    - `Driver Gazeface found: TrackID=1`
    - `driver track id: 1`
- 验证结论：
  - 后排/非主驾 head 在异常宽 driver body ROI 下未绑定到主驾 track，driver head 绑定保持稳定。
  - 本次证据可关闭该 2m dump 场景的临时修复任务，结论为 `passed_with_risks`。

### 0.1.4 当前仍未被充分证据支撑

- face 区域级最终唯一输出
- left_hand / right_hand 区域级最终唯一输出
- “较好的 ID 连续性”效果性结论
- 运行时 replay / 视频流级验证
- face / hand fallback 路径是否在更广泛运行样本中完全满足唯一性约束
- 对快速运动恢复的效果改善是否能推广到代表性样本集

## 0.2 Current Review Conclusion

- 当前系统主框架不是“未实现”，而是“主框架已形成，但仍有输出唯一性与运行级证据缺口”
- 以本轮允许范围内的静态读取判断，`多目标跟踪功能审核记录-2026-03-27` 中关于唯一性未闭合和 ID 连续性证据不足的结论仍然有效
- `多目标跟踪设计失配修复未闭环记录-2026-03-27` 记录的是一次中间阻塞状态，已经不再代表当前整体状态
- DMS 主驾打哈欠误报修复属于 accepted with risks 的项目闭环，不应被提升为正式知识，也不应表述为已完成根因级彻底消除
- 跟踪框越界 coredump 的当前 route 已收敛为 `bug_fix(track-only)`，本轮证据足以关闭 incident，但还不构成“所有 hand 相关功能指标已重新验收通过”
- 2m 摄像头后排 head 误绑定主驾的临时修复已完成板端日志验证，可作为该问题的项目级闭环；但它不关闭整体 face 区域级唯一输出缺口。
- 2026-05-09 架构决策将 head-first 定为下一阶段推荐主线；该结论是项目决策，不是运行验证结果。
- 当前 current 组已能在不依赖 baseline 作为默认入口、也不依赖两篇及以上 delta 作为当前态补洞的前提下恢复 Tracking 主态；但运行效果仍未闭合

## 0.3 Required Next Verification

- 如果要把 Tracking 从“当前实现已形成”推进到“功能验收接近闭合”，优先补：
  1. face 区域级唯一输出验证
  2. left/right hand 区域级唯一输出验证
  3. 代表性视频或日志回放，验证 ID 连续性和 hand miss 不输出后的功能影响
  4. 快速运动恢复样本，验证 body/face/hand 的 `predBox / detection / updated box` 三者关系是否按预期收敛
- 若后续要重新评估 DMS driver false-yawn 的根因消除，建议补更长窗口 replay，专门量化 identity-swap 风险
- 若后续继续优化 2m 场景，建议补更长 2m 视频集，对 `driver face reject`、`driver face match`、`driver second-pass face match orphan=` 做计数型统计，而不是只依赖抽样日志。
- 若后续进入 head-first 实现，必须补：
  1. 2m profile 下 body/hand disabled 且不发布 stale body/hand 的回放验证；
  2. 5m profile 下 driver head-bound body/torso 的 owner 稳定性验证；
  3. hand owner source、left/right slot、orphan takeover 在手部大幅运动和多人干扰下的序列统计；
  4. driver identity source 日志，区分 `head_first`、`body_fallback` 与 reject reason。
- 若后续使用 HumanPose-assisted hand association，需要单独验证 wrist 已有证据链，以及 elbow/shoulder/arm direction 对 hand owner、left/right、miss recovery 的增益。
- 若后续继续沿用本轮 sanitize/clamp 方案，建议补一次日志降噪，避免 `track sanitize clamp` 在板端形成噪声洪泛
- 若后续代码再次触及 `track.cpp`、`AtomicResult` 或导出链路，应重新跑 `knowledge_sync_check`，并再次判断 `single_pass_recoverable`

## 0.4 Current Boundary

本文档只回答当前证据状态，不等价于重新执行完整审核。若后续代码变更 touching `track.cpp`、`AtomicResult` 或导出链路，应重新做 `knowledge_sync_check` 并更新本文件。

## 0.5 Single-Pass Recoverability Verdict

- single_pass_recoverable: `true`
- 判定依据：
  - 读取 `tracking_overview_current + tracking_design_current + tracking_spec_current + tracking_implementation_current + tracking_validation_current` 已能恢复当前 Tracking 的主要设计、默认实现约束、实现事实与验证边界。
  - 只需少量代码路径辅助核对事实源：`track.h`、`track.cpp`、`atomic_result.h`、`fuse_algorithm.cpp`、`humanpose_model.cpp`、`handpose_model.cpp`。
  - baseline 与历史 delta 已全部降级为 `default_entry: false`，不再承担默认恢复职责。
  - 默认情况下不再要求拼接 baseline 或两篇及以上 delta 才能理解当前态。
  - 代码里仍存在 fallback 输出路径，但 current 文档已经明确把该风险归入验证边界，而不是恢复入口缺口。
- 保留限制：
  - 该判定只说明“当前态可单次恢复”，不等价于“运行效果已验证闭环”。
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
