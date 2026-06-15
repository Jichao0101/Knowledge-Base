---
type: project_record
status: planned
project: DMS
module: Tracking
scope: DmsTrack assignment result shape 统一、helper 生命周期约束、hand eligibility 中间表示消除
created_at: 2026-06-13
source:
  - /home/jichao/dms/include/utils/track.h
  - /home/jichao/dms/source/utils/track.cpp
  - subpower discussion: helper lifecycle and AssignmentResult-only phase output
validation_status: not_started
---

# 1 DmsTrack Assignment 结果形态统一与中间身份消除实施前方案

## 1.1 目标

本轮目标不是减少 stage 数量，也不是机械合并 helper，而是在不改变 tracking 行为正确性的前提下，降低必须顺序追踪的 transformation layer：

- 每个 assignment phase 的最终决策结果只使用 `AssignmentResult`。
- 消除跨 step 搬运身份的 helper：`BodyMatchDecision`、`HandSlotCandidate`、`HandPublishEligibility`。
- 保留 `FrameBodyView` 作为唯一跨 body -> hand phase 的单帧只读投影。
- hand pipeline 的核心优化点是消除 intermediate eligibility representation，而不是合并主流程 stage。

## 1.2 Helper 生命周期策略

- 跨 phase helper：只允许真实 phase contract。当前仅保留 `FrameBodyView`。
- phase 内 helper：只能在单个 phase 内局部存在，不进入 header，不跨 assign/apply/publish 多段传播。
- 禁止型 helper：如果 struct 只是把前一步解释搬到后一步，并形成新的 result identity，应删除。
- solver helper：assignment 的输出形态统一为 `AssignmentResult`，apply 阶段只解释 `match.left / match.right`。

## 1.3 设计约束

- 不修改 `hungarian()`。
- 不修改 `AssignmentResult` / `SolveAssignment` 语义。
- 不修改 public API：`DmsTrack::Init/Update` 保持不变。
- 不修改 `AtomicResult` 四类 legacy map ABI。
- 不修改 body/hand output key。
- 不修改 body/hand assignment 行列方向。
- 不修改 strict `< dummyLoss` 拒绝语义。
- 不修改 `FrameBodyView` 单帧只读、非 member、不可跨帧保存约束。
- 不修改 left-before-right hand slot 顺序。

## 1.4 计划改动

### 1.4.1 Body

当前：

```text
assignBodyDetections -> vector<BodyMatchDecision>
applyBodyAssignments -> BodyMatchDecision
applyBodyDetection -> BodyMatchDecision
```

目标：

```text
assignBodyDetections -> AssignmentResult
applyBodyAssignments -> AssignmentResult
applyBodyDetection -> detection index
```

`trackLoss/acquireLoss` 不再作为跨 step helper 字段传递；如需日志，使用 `AssignmentMatch.cost` 或 assignment 局部信息，不能让 apply contract 依赖第二套 decision identity。

### 1.4.2 Hand

当前：

```text
buildHandSlots -> vector<HandSlotCandidate>
assignHandDetections -> vector<int>
apply/miss/prepare/publish -> slots + matched indices + HandPublishEligibility
```

目标：

```text
build local hand rows
assignHandDetections -> AssignmentResult
apply/miss/publish -> row resolver + AssignmentResult
```

`HandSlotCandidate` 降级为 `.cpp` 局部 row view，仅服务本 phase，不进入 header。`HandPublishEligibility` 删除，publish 阶段 inline predicate：

```text
slot initialized
hit threshold
body containment
PrepareTrackForOutput success
matched sanitize failure only advances miss
```

## 1.5 验证要求

最低门禁：

- `git diff --check`
- `cmake --build build --target sdk -j8`
- 尝试执行 `bash scripts/compile_j6b.sh`，若仍因脚本尾部 strip 目标不匹配失败，需明确区分 C++ 编译结果与脚本尾部失败。

静态验证重点：

- `BodyMatchDecision` 不再存在。
- `HandPublishEligibility` 不再存在。
- `HandSlotCandidate` 不再出现在 header；若保留，只能为 `.cpp` 局部 row view。
- `assignBodyDetections` 与 `assignHandDetections` 返回 `AssignmentResult`。
- `curResult->m_bodyTrackResultMap` 仍只能 clear 和 body projection 写入，不得重新成为 hand 输入。

## 1.6 风险边界

- 本轮是结构优化，不声称 runtime replay 等价。
- 不执行板端验证。
- 高风险边界包括 sanitize 失败时的 miss 推进、hand left/right 顺序、retired body cleanup、output key 和 dummyLoss 拒绝语义。
