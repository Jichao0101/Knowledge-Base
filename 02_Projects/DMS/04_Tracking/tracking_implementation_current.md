---
title: Tracking Implementation Current
summary: Tracking 当前实现文档，记录 head-first 功能代码事实、历史 body-first 实现归档、1401fc 基线对比后的路线收缩、driver face 防后排误绑定实现和 clean refactor 边界。
status: verified
doc_role: current
truth_role: current
current_kind: implementation
lifecycle_state: active
default_entry: false
sync_required_when:
  - 关键状态容器变化
  - 更新顺序变化
  - 上游结果 map 或下游兼容映射变化
  - hand continuity 的实现路径变化
retrieval_priority: current
supersedes:
  - 90_Archive/02_Projects/DMS/04_Tracking/座舱多目标跟踪实现.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪实现闭环记录-2026-03-24.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/tracking_interfaces_evidence.md
merged_into: []
current_replacement: []
related_code:
  - /home/jichao/dms/include/utils/track.h
  - /home/jichao/dms/source/utils/track.cpp
  - /home/jichao/dms/etc/track_params.json
  - /home/jichao/dms/etc/track_params_2m.json
sources:
  - 90_Archive/02_Projects/DMS/04_Tracking/座舱多目标跟踪实现.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪实现闭环记录-2026-03-24.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪设计失配修复闭环记录-2026-03-25.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪生命周期与手部关联设计失配修复闭环记录-2026-03-25.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪手部连续性优化闭环记录-2026-03-31.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪快速运动恢复阶段预测更新一致性修复闭环记录-2026-04-05.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/跟踪框越界导致板端coredump调查与修复闭环记录-2026-04-07.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/2m摄像头后排head误绑定主驾修复闭环记录-2026-05-08.md
  - /home/jichao/dms/include/utils/track.h
  - /home/jichao/dms/source/utils/track.cpp
  - /home/jichao/dms/etc/track_params.json
  - /home/jichao/dms/etc/track_params_2m.json
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/head-first优先于body-first跟踪主线决策记录-2026-05-09.md
  - 02_Projects/DMS/04_Tracking/head-first跟踪方案.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/head-first跟踪代码重构闭环记录-2026-05-23.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack内部结构与可读性重构分析-2026-06-08.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack基线对比与HeadFirst路线收缩设计记录-2026-06-16.md
  - 90_Archive/02_Projects/DMS/04_Tracking/Current Maintenance Records/Tracking方案优化与历史实现归档记录-2026-06-16.md
scope: 适用于恢复当前 Tracking 在代码中的主要实现结构、接口事实与行为，不覆盖全部调试历史。
risks:
  - 本文档基于代码静态读取与 2026-05-23 本地编译证据恢复当前实现；仍不等价于完整代表性样本集验收。
  - 2026-05-23 head-first 重构未做板端验证或视频回放。
updated_at: 2026-06-16
---

## 0.0.9 2026-06-16 基线对比后的路线收缩

- 对比 `1401fc338107f05b9cf` 与当前 `feat/ljc/track_0615` 后确认：`include/utils/track.h` 未变化，public `DmsTrack::Init/Update` 未变化，架构漂移集中在 `source/utils/track.cpp`。
- 当前分支已有代码事实包括 `.cpp` internal `SolveAssignment`、Body global owner-to-detection assignment、Hand global slot assignment、tracking-first/acquisition fallback 和 Body/Hand 4A independent lifecycle 小步。
- 这些代码事实不再作为默认推荐路线；当前推荐实现主线收缩为：保留 face/head identity，2m face/head-only，5m driver-bound body evidence 和 driver-bound hand evidence，face missing 时优先 face occlusion，body/hand 只做 bounded evidence cache。
- `SolveAssignment` 可作为 `.cpp` internal 薄工具保留，职责限定为 expanded matrix、dummy edge、forbidden edge、strict `< dummyLoss` 和结果解析；不作为统一 assignment 架构目标。
- Body global assignment、Hand global slot assignment、Body/Hand full independent lifecycle、Body 四态 edge、Reacquire cost band 和 Hand Reacquire 降级为历史实验或未来重启项；重启前必须具备 replay、loss 分布、冲突样例和 diff 白名单。
- 2026-06-15/2026-06-16 两篇扩张路线记录已移动到 `90_Archive/02_Projects/DMS/04_Tracking/Current Maintenance Records/`，当前推荐记录为 `DmsTrack基线对比与HeadFirst路线收缩设计记录-2026-06-16.md`。

## 0.0.8 2026-06-16 Head-first 方案优化与历史实现归档（已归档为历史实验路线）

- `座舱多目标跟踪实现.md` 已移动到 `90_Archive/02_Projects/DMS/04_Tracking/`，只作为历史 body-first baseline 和参数推导参考，不再位于 Tracking 当前工作区。
- `head-first跟踪方案.md` 当时吸收了 body/face/hand 生命周期独立原则、Body 四态 edge 和 deep-module clean refactor 约束；该路线现已由 0.0.9 收缩，不再作为当前默认推荐。
- 2026-06-16 已在 `feat/ljc/track_0615` 小步实现 4A 生命周期闭环：已有 body track owner 会被纳入 tracking-only assignment 候选域，face miss/暂不存在时仍可按 body prediction 延续；body 未匹配时推进 miss，并只在 `body.missThreshold` 后 retire，不因 face absence 立即删除。
- Hand 4A 同步补齐：published DRIVER body 仍是 hand 对外发布依据；内部 initialized hand slot 可基于已有 DRIVER body track 进入 tracking-only row，internal-only owner 不 bootstrap 未初始化 slot；未进入 row 的 initialized left/right slot 会在全量 sweep 中推进 miss，避免 owner/body 不可发布时 lifecycle 停滞。
- Hand publish 阶段不再因 output sanitize 失败推进 miss，避免 matched initialized slot 在同帧先 hit 后 miss；hand lifecycle 统一收敛到 assignment/sweep 阶段推进。
- Body 全局 assignment 的目标 edge 解释扩展为 Track / Reacquire / Bootstrap / Forbidden。当前代码在 loss 未标定前仍关闭 Reacquire；标定后打开时必须保持 ownerFaceId、稳定 hitCount 和输出连续性，只允许重置或强校正 motion state。
- 本次未修改 `include/utils/track.h` 或 public `Init/Update`；仍沿用 2026-06-15 deep-module 结论：private header 保持 phase-level，solver/row/key/result/snapshot 和 edge classifier 默认留在 `.cpp` 或函数局部。
- 本次仍未打开 Body Reacquire、loss instrumentation 或 Hand Reacquire；运行 replay、冲突样例 diff 和板端验证未执行。

## 0.0.7 2026-06-15 Clean Branch Body Global Assignment

- 代码范围：`/home/jichao/dms/source/utils/track.cpp`。
- 未修改 `include/utils/track.h`、public `DmsTrack::Init/Update`、Face 行为或 Hand 行为。
- 当前 clean branch `feat/ljc/track_0615` 已在既有 Face cpp-internal `SolveAssignment` 基础上，把 `updateBodyTracks` 的逐 owner greedy body matching 改为全局 owner-to-body-detection assignment。
- Body owner row 仍按 driver face 优先构造，用于确定性 row 顺序和 tie-break 输入；不再用 driver-first 遍历抢占 detection。
- 每条 Body assignment 边由 body phase evaluator 决定：已有 body track 提供 `computeMatchLoss(predBox, detection)`，head geometry acquisition 提供 `FaceBelongsToBody + FaceAnchorLoss`。
- 新增 `.cpp` internal 常量 `kBodyAcquireBias = 0.5f` 与 `kDriverBodyAssignmentBonus = -0.25f`；driver acquisition cost 可低于非 driver acquisition cost，但 solver 仍通过 strict `< body.dummyLoss` 接受真实边。
- 对已初始化 body，evaluator 保留 tracking-first 层级：tracking loss 低于 `body.dummyLoss` 时优先延续旧 body track；否则本帧 miss，不使用 acquisition 重新绑定。acquisition 只用于尚无 body track 的新 owner。
- 该保守层级依赖 loss 标定：tracking loss、acquisition loss、driver/non-driver bias 与 `dummyLoss` 未经场景标定前，不能声明运行效果闭环；标定完成前不打开 initialized acquisition fallback。
- Hand 已同步收敛为全局 slot assignment：eligible owner 的 left/right rows 一次性进入 solver；initialized slot 只接受 prediction tracking，tracking 不可靠则 miss；uninitialized slot 只走 acquisition。
- Body/Hand 输出改为 `PrepareTrackForOutput` 后纯写 output map；sanitize failure 只在 finalize 中对本帧 matched body/slot 推进 miss。

## 0.0.5 2026-06-15 Assignment Helper 删减与非对称分层

- 删除 `AssignmentEdge / AssignmentRejection` 和 rejection 聚合日志；不恢复 `AssignmentPolicyMatrix`。业务 evaluator 直接返回 cost，forbidden edge 使用有限 `kForbiddenAssignmentCost = 1e6f`。
- `AssignmentResult` 保留，继续统一表达 matches、unmatched left/right 和 match cost。
- Body 主流程现为 `solve -> apply -> advance/retire -> finalize -> project FrameBodyView -> publish`；sanitize 与 view 构造不再混在同一 helper。
- Hand 使用单帧 `HandAssignmentRow` 绑定 `HandSlotKey`、slot 和 owner body；solve、apply、unmatched miss 共享同一 row 候选域。
- Hand finalize 负责 sanitize 和 matched sanitize failure 的 lifecycle 推进；`publishHandTracks` 不读取 `AssignmentResult`，不调用 `PrepareTrackForOutput`、`AdvanceMiss` 或 cleanup。
- Hand 没有 tracker 内部下游，因此未新增 `FrameHandView`、publish payload 或 eligibility。
- public `Init/Update`、Hungarian、strict `< dummyLoss`、四类 legacy map ABI、owner/key 和 left-before-right 顺序未变。

## 0.0.6 2026-06-15 Deep Module Re-review

- `feat/ljc/track_0609` 当前实现继续作为实验样本保留，但不再作为推荐 clean refactor 基底。
- public `Init/Update` 已足够深；private header 的完整 step helper 树被判定为过宽。
- `1237f6c6` 将稳定基线 driver-first greedy body ownership 改为 global Hungarian，属于本次明确目标的高风险算法参考；其 solver/cost 语义可重做，但 step-level helper 和 header 中间类型不作为推荐结构。
- `FrameBodyView` 解决 output-as-input 问题的目标可保留，但具体类型应降级为局部 finalized body snapshot；`HandSlotKey`、`HandAssignmentRow`、`AssignmentResult` 建议移出 header。
- 当前 hand owner 消失后 lifecycle 如何继续推进尚未闭合；实验实现可能保留 initialized slot、retired anchor 并阻止 id 复用。
- 推荐从 `br_develop_forJ6b` 新开 clean branch：先以 Face 验证通用 solver 等价，再分阶段重做 Body 全局 assignment、Hand 全局 slot assignment、sanitize matched-only miss、finalize-before-publish 和 body-to-hand 内部状态隔离。

## 0.0.4 2026-06-13 State Normalization And Body Output View

- 代码范围仍只涉及 `/home/jichao/dms/include/utils/track.h` 和 `/home/jichao/dms/source/utils/track.cpp`。
- 新增 private `FrameBodyView`，由 body 阶段在单帧内生成，字段为 owner face id 与 body `TrackInfo` 拷贝；该 view 不作为 member、不跨帧保存，hand 阶段只读消费。
- `updateBodyTracks` 返回 `std::vector<FrameBodyView>`；2026-06-15 起由 `finalizeBodyTracksForOutput` 完成 body sanitize、matched-only sanitize failure miss 和人员类型投影，再由 `projectBodyTracks` 单独生成该 view。
- `publishBodyTracks` 不再读取 `m_bodyTracks` 或重新判断 publishable set，只从 `FrameBodyView` 投影写入 `curResult->m_bodyTrackResultMap`。
- hand 阶段的 `collectAllowedHandOwners`、`buildHandAssignmentRows`、`cleanupRetiredOwnerHandSlots`、`finalizeHandTracksForOutput` 和 `publishHandTracks` 均消费 `FrameBodyView`，不再读取 `curResult->m_bodyTrackResultMap`。
- `curResult->m_bodyTrackResultMap` 在 `track.cpp` 中仅保留每帧 clear 与 body output 写入角色。
- 清理废弃 `m_hasPreviousFrame` declaration/init；静态搜索未发现剩余引用。
- public API、`hungarian()`、统一 assignment helper、strict `< dummyLoss`、legacy output key、left-before-right hand slot 顺序不变。

## 0.0.3 2026-06-12 Driver Face 防后排误绑定

- 代码范围：
  - `/home/jichao/dms/include/utils/track.h`
  - `/home/jichao/dms/source/utils/track.cpp`
  - `/home/jichao/dms/etc/track_params.json`
- `TrackParameters` 新增 `driverFaceAnchor`、`driverFaceAnchorWeight`、`driverFaceSmallerPenaltyWeight`、`driverFaceLargerBonusWeight`。
- `loadConfigFromJson` 读取 `presets.driver_face_anchor`，DEFAULT 提供默认权重，2m 车型可覆盖 anchor 坐标。
- `selectDriverFace` 中稳定 `BACK_PASSENGER` face 不再进入 driver 候选，即使当前帧 `instantPersonType == DRIVER`。
- 原 `FaceSizeContinuityLoss` 的对称 driver selection 用法被替换为：
  - `FaceSmallerThanReferenceLoss`：候选比当前 driver reference 更小时增加 penalty，并超过阈值直接拒绝。
  - `FaceLargerThanReferenceGain`：候选比 reference 更大时降低 score，支持真实主驾遮挡后恢复。
- score 由 smaller penalty、anchor loss、larger gain 和 continuity bonus 组成；未改 face match `distanceLoss` 或 driver distance gate。

## 0.0.2 2026-06-11 Sentinel、ID 与阶段语义收敛

- 代码变更仍只涉及 `/home/jichao/dms/include/utils/track.h` 和 `/home/jichao/dms/source/utils/track.cpp`。
- `DmsTrack::Init()`、`DmsTrack::Update()`、`SolveAssignment()`、`hungarian()` 和四类 legacy map 接口未变化；public header 中既有 `INF` 保留，避免仓外源码兼容风险。
- sentinel 已按概念拆分：invalid track id、unmatched index、forbidden assignment cost、absent diagnostic loss 不再依赖含混的裸 `-1` 或 max-float 语义。
- Body 主流程显式为 `collect -> predict -> assign -> apply -> advance/retire -> publish`。
- Hand 主流程显式为 `collect/allowed -> predict -> build slots -> assign -> apply hits -> advance misses -> cleanup/reset/erase -> publish -> retired-anchor cleanup`。
- `bodyId / handId` 初始继承 `faceId` 数值与 map key，但 body、hand 各自维护生命周期；face 消失后 body retired state 或 hand state 可保留原始继承 id。hand 发布条件未放宽，仍要求当前已发布的 DRIVER body evidence。
- 本轮保持 assignment cost、遍历顺序、left-before-right、hit/miss 推进、日志 stage tag、sanitize 和发布语义不变。

## 0.0.1 2026-06-09 Internal Readability Refactor Delta

- 本轮代码变更仅限 `/home/jichao/dms/include/utils/track.h` 和 `/home/jichao/dms/source/utils/track.cpp`。
- `DmsTrack::Init()`、`DmsTrack::Update()` 和 public-facing tracker 接口未变化。
- 帧级 `face update -> driver selection -> face publish -> body update -> hand update` 顺序未变化。
- `Update` 的 face 角色修正/发布、`updateFaceTracks` 的检测/预测/匹配/bootstrap/lifecycle、`updateBodyTracks` 的 owner/body assignment/apply/retire/publish 已拆为 private helper，使主流程只保留阶段编排。
- Face / Body / Hand 的统一 assignment helper 只负责矩阵扩展、dummy 边和结果解析，Body 不再维持顺序 greedy。
- Hand 已从 first/second pass 收敛为单次 slot assignment；left/right slot、owner bodyId、prediction、cleanup、empty-owner erase、publish 和 retired-anchor cleanup 仍由 private helper 维护。
- 独立 review 结论为 `approved`；`git diff --check` 和 QNX 编译通过。未执行 runtime replay、单元测试或板端验证。
- 后续注释治理补充轮为新增统一 assignment helper 与 Body/Hand 相关 private helper 增加了中文契约注释，明确 owner/bodyId/key、哨兵值、顺序不变量和状态副作用；未做重命名，剥离注释后代码 token 不变。

## 0.0 2026-05-23 Head-first Current Delta

- 当前 `DmsTrack::Update` 顺序已变更为：
  1. 清空 `m_bodyTrackResultMap / m_faceTrackResultMap / m_leftHandTrackResultMap / m_rightHandTrackResultMap`
  2. `updateFaceTracks`
  3. `selectDriverHead`
  4. publish face/head map
  5. `updateBodyTracks`
  6. `updateHandTracks`
- `trackId` ownership 已收敛到 head/face：`allocateBodyTrackId` 和 `m_nextBodyTrackId` 已删除，新增 `allocateFaceTrackId` 与 `m_nextFaceTrackId`。
- `m_bodyTracks` 当前以 head trackId 为 key；body/torso 是 head-owned evidence，不再独立创建 identity id。2026-06-13 起，hand 阶段不再从 body legacy output map 读取 body evidence，而是消费 body 阶段生成的单帧 `FrameBodyView`。
- `updateBodyTracks` 当前由 head 发起 body evidence matching：2026-06-15 clean branch 起，所有有效 owner face 与本帧 body detections 进入一次全局 assignment；已有 evidence 的 body motion tracking cost 与 head geometry acquisition cost 取最小可用值，不再按逐 owner greedy 方式先抢占 detection。
- `m_bodyTrackResultMap` 仍作为 legacy body map 输出，但 key 使用 head trackId。
- `m_bodyHandTracks` 的 legacy 变量名仍包含 bodyId；当前语义应理解为 head-owned body evidence id，即 head trackId。
- driver head 选择由 `selectDriverHead` 完成：small face、front passenger ROI、尺寸突变优先过滤，size continuity 权重大于 position loss。
- 2026-06-12 起 driver head/face 选择增加 stable BACK_PASSENGER 拒绝、尺寸方向性 scoring 和配置化 preferred anchor；不再把真实主驾恢复时的“脸变大”作为 size continuity 损失。
- 本地编译 `bash scripts/compile_j6b.sh` 已通过，最终 `[100%] Built target sdk`。
- 未完成板端验证、视频回放和 callback/fusion 同 key 行为运行确认。

## 0.1 Core Entry

- 入口类：`UtilsDomain::DmsTrack`
- 主要入口函数：`Init`、`Update`
- 每帧更新顺序固定为 `head/face -> driver head selection -> body evidence -> hand evidence`。
- 配置入口固定从 `/home/jichao/dms/etc/track_params.json` 读取，并先应用 `DEFAULT`，再按车型节点覆盖。
- 代码已实现 head-first driver selection 与 head-bound body/torso evidence；尚未实现 2m/5m 运行时模式选择，也未完成 hand owner source 的运行日志验证。
- head-first 设计细节见 [[head-first跟踪方案]]；本文记录当前实现事实。

## 0.2 Current State Containers

- 长期内部状态：
  - `m_bodyTracks`
  - `m_retiredBodyTracks`
  - `m_faceTracks`
  - `m_bodyHandTracks`
- 对外结果：
  - `AtomicResult::m_bodyTrackResultMap`（legacy output projection；不再作为 hand 内部输入）
  - `AtomicResult::m_faceTrackResultMap`
  - `AtomicResult::m_leftHandTrackResultMap`
  - `AtomicResult::m_rightHandTrackResultMap`
- 下游兼容与消费：
  - `humanpose_model.cpp` 直接消费 `m_bodyTrackResultMap`
  - `handpose_model.cpp` 分别消费 `m_leftHandTrackResultMap` 与 `m_rightHandTrackResultMap`
  - `fuse_algorithm.cpp` 将 body 兼容映射到 `m_humanTrackResultMap`
- 关键状态语义：
  - `m_bodyTracks` 承载当前 active body 轨迹
  - `m_retiredBodyTracks` 承载旧 body 的清理锚点
  - `m_faceTracks` 承载 face 子轨迹
  - `m_bodyHandTracks` 承载每个 body 的 left/right hand 槽位

## 0.3 Motion Models

- body：恒速度 KF
- face：恒速度 KF
- hand：恒加速度 KF，状态包含位置、尺寸、速度、加速度和尺寸变化速度
- body / face / hand 仍先做预测用于匹配，但 2026-04-05 起对“快速运动后恢复正常位姿”的更新路径增加了预测残留抑制：
  - face：命中检测后最终输出框直接使用检测框，不再把 `CorrectMotion` 结果写回输出框
  - hand：命中检测后最终输出框直接使用检测框；2026-04-07 起 miss 时不再沿 `predBox` 向下游输出
  - body：命中检测后改为检测主导融合；当预测与检测出现反向/过冲时，直接回到检测框并重建运动状态
- 2026-04-07 起 body / face / hand 在写入 `AtomicResult::*TrackResultMap` 前统一经过 track 内部 sanitize/clamp；非法框直接丢弃，不再透传给下游
- 2026-05-08 起，已有 face track 在 first pass 被当前稳定 body 重新关联时，会先通过 face 自身预测连续性门控；driver 相关 face 绑定使用更严格的 `distanceLoss <= 0.45`，非 driver 使用 `0.65`。

配置来自 `/home/jichao/dms/etc/track_params.json`，按 `DEFAULT` 或车型节点加载 body / face / hand 的 threshold 与 kalman 参数。

## 0.4 Spec-to-Code Mapping

- 人员类型投票与稳定解析 -> `AccumulatePersonVote` / `ResolveStablePersonType`
- 配置读取与 `DEFAULT` / 车型覆盖 -> `loadConfigFromJson`
- head/face id 分配 -> `allocateFaceTrackId`
- driver head 选择 -> `selectDriverHead`
- head-owned body evidence 主流程与全局 owner-to-detection assignment -> `updateBodyTracks`
- face/head 常规匹配、driver small-face filtering、face continuity gate -> `updateFaceTracks`
- driver face 防后排误绑定 -> `selectDriverFace`、`FaceSmallerThanReferenceLoss`、`FaceLargerThanReferenceGain`、`TrackParameters::driverFaceAnchor*`
- hand 左右槽位、second pass、miss 不输出策略 -> `updateHandTracks`
- 统一输出 sanitize/clamp 与非法框过滤 -> `SanitizeDetectBoxToImage` / `PublishSanitizedTrack`
- 导出兼容层 -> `fuse_algorithm.cpp`、`handpose_model.cpp`、`humanpose_model.cpp`
- 预测残留抑制 -> body / face / hand 命中更新路径中的 detection-dominant update 与 motion-state 重建点；实现上落在各自命中更新分支，而不是独立的统一导出层
- 2m 宽 body 下 head 误绑定抑制 -> face match 中的 size continuity、distance gate、driver head small-face/front-passenger reject
- head-first 主线 -> 已完成第一轮实现；当前证据为静态分析和本地编译。

## 0.5 Matching And Lifecycle

### 0.5.1 body

- body/torso 不再独立分配 id；`m_bodyTracks` 以 head trackId 为 key。
- `updateBodyTracks` 先构造当前有效 head owner rows，driver head 优先作为确定性 row 顺序。
- clean branch 已把 Body 改为全局 owner-to-body-detection assignment；已有 body evidence 的 tracking cost 与 head geometry acquisition cost 同时参与单条边评估，但 evaluator 在未标定前只允许已有 track 走 tracking edge，不允许 acquisition fallback 重新绑定。
- acquisition 候选必须满足 `FaceBelongsToBody`，并使用 `FaceAnchorLoss` 加 driver/non-driver bias；真实边仍必须 strict `< body.dummyLoss`。
- 命中的 body detection 写回 `m_bodyTracks[headId]`，并以同一 headId 发布到 `m_bodyTrackResultMap`。

### 0.5.2 face

- face/head 不再依附 body 邻域启动，而是先于 body evidence 更新。
- 已有 face 轨迹按预测框与 face detection 做匈牙利匹配。
- face 匹配损失综合 IoU、距离和 size continuity；driver 相关使用更严格的 `distanceLoss <= 0.45`，其他为 `0.65`，且总分必须小于 face `dummyLoss`。
- 未匹配 face detection 通过 `allocateFaceTrackId` 创建新的 head/face track。
- face 命中后更新 CV state、hit/miss 和 person type vote；driver identity 的最终发布由 `selectDriverHead` 覆盖。

### 0.5.3 hand

- hand 先按 driver head-owned body evidence 局部候选与左右槽位做一次分配。
- 之后对未匹配槽位做 second pass，但仍必须受当前 owner body evidence 几何约束。
- hand miss 时只推进内部 miss 生命周期，不再把 `predBox` 推进到对外输出框。
- hand / face / body 现在统一按命中门限决定是否允许对外输出；hand 不再保留短 miss window 输出。
- hand 命中检测后，输出框完全使用检测框；miss 路径不再向下游输出预测框。
- 命中检测且出现明显反向/过冲时，会重建 CA state，降低旧加速度对下一帧预测的延续。

## 0.6 Current Implementation Constraints

- face / body / hand 对外仍使用 legacy 四类 map，但同一 occupant 的 key 现在来源于 head trackId。
- hand 代码中的 legacy 变量名仍包含 `bodyId`；当前语义应理解为 head-owned body evidence id，不代表 body identity owner。
- retired body 只作为 handoff 和 orphan child 清理的历史锚点，不直接对外输出。
- 当前实现保留 head/hand 的内部连续性；hand 对外输出 key 已收敛为当前 driver head-owned body evidence id，但区域级唯一性仍需运行验证。
- `m_humanTrackResultMap` 只在导出层作为 body 兼容映射，不是 tracking 上游事实源。
- 当前实现并未把 `tracking_interfaces_evidence` 提升为默认实现输入；其接口事实已经并入本文件和 spec。
- 仓内存在 `track_params_2m.json`，但当前 `loadConfigFromJson` 固定读取 `track_params.json`，尚未实现显式 2m/5m profile 选择。

## 0.7 Known Gaps

- 2026-06-09 内部可读性重构已有编译、patch check 和独立 review 证据，但未用 replay 或单元测试执行多帧运行等价验证。
- 2026-06-15 重新评审已否定“继续沿当前 helper tree 优化”的路线；此前编译和静态 review 只能证明代码可构建和局部审查通过，不能证明该结构或算法变化应继续保留。
- 代码里仍存在 hand slot 内部 fallback 输出路径，但输出 key 已要求回到当前 driver head-owned body evidence id。
- 运行级验证仍待补。
- 仅靠本文件和 code facts 可以恢复当前实现框架，但不能把运行级区域唯一性当成已闭合结论。
- head-first 第一轮已实现并本地编译通过；任何后续优化仍必须保持“代码事实”和“运行效果验证”分离。
- HumanPose 当前由 driver body map 触发并产出 `m_humanPoseResult`；这不是 OccupantTrack，也不是 person/part 状态层。

## 0.8 Historical Mapping

- 03-24 delta 落地了 body/face/hand 主框架。
- 03-25 delta 收敛了上游事实源、左右手槽位、retired body handoff 清理与输出契约。
- 03-31 delta 收敛了 hand continuity 优化与短 miss 输出。
- 04-05 delta 收敛了快速运动恢复阶段的预测残留抑制。
- 04-07 delta 收敛了 tracking 输出框统一 sanitize/clamp，并把 hand miss 输出语义对齐到 face/body。
- 05-08 delta 在不重构 tracker 的前提下，为 2m 摄像头宽 body 场景增加 initialized-face continuity gate 和 driver second-pass strict gate，避免后排 head 借异常 body ROI 误绑定到主驾 track。
- 05-09 decision record 将 body-first 归档为 legacy 主线，并要求下一阶段不再把 raw body detection box 作为 driver/person identity 主锚点。
- 原 `tracking_interfaces_evidence` 的当前有效接口事实已并入本文件。

## 0.9 Current Sync Rule

- must_update_when:
  - `DmsTrack::Update` 的主顺序变化
  - `m_bodyTracks / m_retiredBodyTracks / m_faceTracks / m_bodyHandTracks` 结构变化
  - `AtomicResult` 四类 tracking map 或 body 兼容映射变化
  - hand miss 输出策略、统一 sanitize/clamp 或 orphan fallback / hand second pass 逻辑变化
  - `track_params.json` 的 DEFAULT 读取或车型覆盖规则变化
  - head-first driver selection、profile 选择、head-bound body/torso、hand owner source 任一实现落地
- absorbs_history_from:
  - `座舱多目标跟踪实现.md`
  - `多目标跟踪实现闭环记录-2026-03-24.md`
  - `多目标跟踪设计失配修复闭环记录-2026-03-25.md`
  - `多目标跟踪生命周期与手部关联设计失配修复闭环记录-2026-03-25.md`
  - `多目标跟踪手部连续性优化闭环记录-2026-03-31.md`
  - `多目标跟踪快速运动恢复阶段预测更新一致性修复闭环记录-2026-04-05.md`
  - `tracking_interfaces_evidence.md`
- evidence_only_docs:
  - `tracking_interfaces_evidence.md`
- not_a_default_entry_anymore:
  - `座舱多目标跟踪实现.md`
  - `多目标跟踪实现闭环记录-2026-03-24.md`
