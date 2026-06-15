---
type: project_record
status: implemented_pending_review
project: DMS
module: Tracking
created_at: 2026-06-13
scope: DmsTrack 匹配、状态、finalize、projection、publish 分层修正
source_code:
  - /home/jichao/dms/include/utils/track.h
  - /home/jichao/dms/source/utils/track.cpp
---

# 1 DmsTrack 匹配、状态、finalize、projection、publish 职责边界修正实施前方案

## 1.1 背景

当前 `AssignmentPolicyMatrix` 已取消，solver 通过 edge evaluator 直接构造 Hungarian 输入矩阵。这一方向保留。

对 assignment helper 的进一步评估结论：

- 当前检测已较稳定、误检较少，face/body/hand 的业务 gate 和 `dummyLoss` 已承担主要正确性约束。
- `AssignmentCandidate`、`AssignmentEdge`、`AssignmentRejection`、`AssignmentPolicyMatrix` 的主要收益是给 forbidden edge 命名和输出 rejection 聚合日志，不参与最终 Hungarian 结果表达。
- 当前 rejection 分类需要在 evaluator、solver、枚举和日志格式之间来回追踪，阅读成本高于诊断收益；删除后允许边仍由有限 cost 且严格 `< rejectCost` 判定，禁止边统一返回有限 `kForbiddenAssignmentCost = 1e6f`，避免 Hungarian 内部参与 infinity 或接近浮点上限的运算。
- `AssignmentResult` 仍有独立价值：统一表达一对一匹配结果、未匹配 left/right 和实际 match cost，并为 solve/apply 边界提供稳定契约，因此保留。

helper 删减先于分层实施，作为后续接口修复的基线：

```text
业务 evaluator -> float cost
forbidden / invalid edge -> kForbiddenAssignmentCost (1e6f)
SolveAssignment -> AssignmentResult
```

删除分类 rejection 聚合日志是有意接受的可观测性变化；现有 face/body/hand 命中日志和关键业务 reject 日志继续保留。

当前仍存在的问题不是 stage 数量，而是短期匹配层、长期状态层、cleanup/finalize 层、projection 层和 publish 层的职责边界没有完全收敛：

- `AssignmentResult` 不能进入 cleanup、finalize、projection、publish。
- 不能为了隐藏 `AssignmentResult` 把 solve/apply 混在一个叫 `apply*` 或 `matchAndApply*` 的函数里。
- `publishAllowedHandSlots` 若包含 `PrepareTrackForOutput` 和 sanitize fail 后的 `AdvanceMiss`，它不是 pure output。
- hand miss 必须以本帧实际构造的 assignment row 为候选域，不能从 matched slot 反推候选域，也不能扫描全量 `m_handTracks`。
- 使用 `std::pair<track_id, bool>` 作为 hand slot key 会造成 `.first/.second` 语义不清；本次采用显式 `HandSlotKey { ownerFaceId, side }`。
- 分层是职责约束，不要求 face/body/hand 机械拥有相同数量、相同形态的 stage。`FrameBodyView` 有真实的 body -> hand 下游；hand 在 tracker 内没有后续消费者，不新增 `FrameHandView`、publish payload 或 eligibility 中间层。

## 1.2 目标

在不改变 Hungarian 算法、不改变 tracking 行为正确性、不改变 public API 和 legacy output map ABI 的前提下：

1. short-term matching：solve only，输出短期 `AssignmentResult`。
2. state apply：消费 `AssignmentResult`，修改长期 track state，输出领域事实。
3. state finalize：cleanup、sanitize、lifecycle boundary，可修改长期 state。
4. projection：只在存在真实下游契约时生成 frame view，不修改长期 state。
5. publish：只写 `curResult` output map，不读 solver result，不推进 lifecycle。
6. `FrameBodyView` 是 body 到 hand 的单帧只读投影，不是 authoritative state。

## 1.3 Body 方案

body 不使用“solve + apply”但命名为 `apply*` 的函数。职责拆为：

```text
bodyDetections = collectBodyDetections(curResult)
bodyIds = collectBodyOwnerFaceIds(driverFaceId)
predictBodyTracks(bodyIds)
assignment = solveBodyAssignments(bodyIds, bodyDetections, driverFaceId)
matchedOwnerFaces = applyBodyMatches(bodyIds, bodyDetections, assignment, driverFaceId)
advanceAndRetireBodyTracks(matchedOwnerFaces)
finalizedOwnerFaces = finalizeBodyTracksForOutput(matchedOwnerFaces, driverFaceId, frameSize)
bodyOutputView = projectBodyTracks(finalizedOwnerFaces, driverFaceId)
publishBodyTracks(curResult, bodyOutputView)
```

约束：

- `solveBodyAssignments` 只调用 solver，不修改长期 state。
- `applyBodyMatches` 消费 `AssignmentResult` 并修改 `m_bodyTracks`。
- `finalizeBodyTracksForOutput` 可调用 `PrepareTrackForOutput`，sanitize fail 时可对本帧 matched owner `AdvanceMiss`，并返回完成 finalize 的 owner id。
- `projectBodyTracks` 只按 finalized owner 生成 `FrameBodyView`，不修改 `m_bodyTracks`。
- `publishBodyTracks` 只写 `curResult->m_bodyTrackResultMap`。

## 1.4 Hand 方案

hand 保留短期匹配和长期状态应用的独立边界：

```text
handDetections = collectHandDetections(curResult)
allowedOwners = collectAllowedHandOwners(bodyOutputView)
predictInitializedHandSlots()
rows = buildHandAssignmentRows(bodyOutputView, allowedOwners)
assignment = solveHandAssignments(rows, handDetections)
matchedSlots = applyHandMatches(rows, handDetections, assignment)
advanceUnmatchedHandSlots(rows, assignment)
cleanupRetiredOwnerHandSlots(bodyOutputView)
resetExpiredHandSlots()
eraseEmptyHandOwnerStates()
finalizeHandTracksForOutput(bodyOutputView, allowedOwners, matchedSlots, frameSize)
publishHandTracks(curResult, bodyOutputView, allowedOwners, frameSize)
cleanupRetiredBodyAnchors()
```

`HandAssignmentRow` 是短期匹配层的真实行描述：

- 显式包含 `HandSlotKey`、对应 slot 引用和 owner body 引用。
- row 顺序固定为 `bodyOutputView` 顺序、每个 owner left-before-right。
- row 同时覆盖 initialized slot 和允许 acquisition 的未初始化 slot；只有 initialized 且 unmatched 的 row 推进 miss。

`AssignmentResult` 只允许存在于 `solveHandAssignments -> applyHandMatches / advanceUnmatchedHandSlots` 的短期匹配与长期状态应用边界。`applyHandMatches` 返回显式 `matchedSlots`，只供 finalize 判断“sanitize fail 是否来自本帧命中”。

`advanceUnmatchedHandSlots` 只遍历 `rows` 并推进其中 initialized 且 unmatched 的 slot，不扫描全量 `m_handTracks`，也不额外维护 `candidateSlots` 集合。

hand 不增加 projection stage：

- `FrameBodyView` 保留，因为 hand 是它的真实下游。
- hand 在 tracker 内没有下游消费者，增加 `FrameHandView`、publish payload 或 eligibility 只会形成新的搬运层。
- `finalizeHandTracksForOutput` 负责 cleanup 之后的 sanitize 和条件性 lifecycle 推进。
- `publishHandTracks` 只读 finalized state、`bodyOutputView` 和 `allowedOwners`，执行无副作用的输出有效性判断后写 legacy hand map；不得调用 `PrepareTrackForOutput`、`AdvanceMiss` 或 cleanup。

## 1.5 Output Layer 约束

- `finalize*TracksForOutput`：lifecycle boundary，可调用 `PrepareTrackForOutput` 和条件性 `AdvanceMiss`。
- `projectBodyTracks`：只生成存在真实下游用途的 `FrameBodyView`，不调用 `PrepareTrackForOutput`、`AdvanceMiss` 或 cleanup。
- hand 无独立 projection；不得为了形式统一引入 `FrameHandView`、publish payload 或 eligibility。
- `publish*Tracks`：只写 legacy output map，不调用 `PrepareTrackForOutput`、`AdvanceMiss` 或 cleanup，不读 `AssignmentResult`。

## 1.6 cleanupRetiredBodyAnchors 位置

若 `cleanupRetiredBodyAnchors()` 只删除 `m_retiredBodyTracks` 中不再被 body/face/hand 引用的历史 anchor，不影响当前 `m_handTracks` 或本帧 output，则放在 publish 后可以接受，作为尾部 GC。

若未来它清理 hand/body state、allowed owner 或影响本帧 hand publish，则必须移到 `finalizeHandTracksForOutput()` 前。

## 1.7 非目标

- 不修改 Hungarian 算法。
- 不恢复 `AssignmentPolicyMatrix`。
- 不恢复 `AssignmentCandidate / AssignmentEdge / AssignmentRejection`；若未来确有诊断需求，应在具体业务 gate 附近增加低噪声日志，而不是重新引入跨 solver 的分类对象层。
- 不引入新解释层或 debug layer。
- 不改变 face/body/hand 的 detection 顺序、left-before-right 顺序、hit/miss 阈值和 reject semantics。
- 不改变团队既有 `body` 命名。

## 1.8 验证计划

- 静态检查：
  - `AssignmentCandidate / AssignmentEdge / AssignmentRejection / AssignmentPolicyMatrix` 不存在。
  - `AssignmentResult` 保留，`SolveAssignment` 仍按有限 cost 且严格 `< rejectCost` 接受真实边。
  - forbidden edge 使用有限 `1e6f`，且所有配置化 `dummyLoss` 必须显著小于该值。
  - `AssignmentResult` 不出现在 cleanup、finalize、projection、publish 函数签名。
  - `publish*Tracks` 只执行 map 写入，不调用 `PrepareTrackForOutput`、`AdvanceMiss` 或 cleanup。
  - `projectBodyTracks` 不调用 `PrepareTrackForOutput`、`AdvanceMiss` 或 cleanup。
  - 不存在 `FrameHandView`、hand publish payload 或 eligibility 类型。
  - `advanceUnmatchedHandSlots` 只消费本帧 `HandAssignmentRow`，不扫描全量 `m_handTracks`。
  - `m_bodyTrackResultMap` 仍只清空和写入，不作为 hand input。
- `git diff --check`。
- J6B build：`bash scripts/compile_j6b.sh` 或直接 `cmake --build build --target sdk -j8`，按实际可用路径记录结果。
- 不做板端验证，不声称 runtime replay 等价。

## 1.9 实施结果（2026-06-15）

实际实施遵循“先删减 helper、再先接口后实现非对称分层”的顺序：

- 删除 `AssignmentEdge / AssignmentRejection` 及 rejection 聚合日志；未恢复 `AssignmentPolicyMatrix`。
- forbidden edge 使用有限 `kForbiddenAssignmentCost = 1e6f`；`SolveAssignment` 仍以有限 cost 且严格 `< rejectCost` 接受真实边。
- 保留 `AssignmentResult`，作为 solve/apply 边界的统一短期结果。
- Body 拆为 `solveBodyAssignments -> applyBodyMatches -> advanceAndRetireBodyTracks -> finalizeBodyTracksForOutput -> projectBodyTracks -> publishBodyTracks`。
- Hand 新增显式 `HandSlotKey` 和单帧 `HandAssignmentRow`；row 是 solve/apply/unmatched miss 的共同候选域。
- `AssignmentResult` 不再进入 hand cleanup、finalize 或 publish。
- `finalizeHandTracksForOutput` 承担 sanitize 和 matched sanitize failure 的 lifecycle 推进。
- `publishHandTracks` 只读 finalized state 和 `FrameBodyView`，不调用 `PrepareTrackForOutput`、`AdvanceMiss` 或 cleanup。
- 未新增 `FrameHandView`、hand publish payload 或 eligibility 中间层。

实际修改文件：

- `/home/jichao/dms/include/utils/track.h`
- `/home/jichao/dms/source/utils/track.cpp`

验证结果：

- `git diff --check -- include/utils/track.h source/utils/track.cpp`：通过。
- `cmake --build build --target Utils -j8`：在加载 QNX 环境后通过。
- `cmake --build build --target sdk -j8`：在加载 QNX 环境后通过，最终 `[100%] Built target sdk`。
- 未执行 runtime replay、单元测试或板端验证。

当前状态为 `implemented_pending_review`：编译和静态职责检查已通过，仍需独立 review 判断多帧行为等价与职责边界是否完整闭合。
