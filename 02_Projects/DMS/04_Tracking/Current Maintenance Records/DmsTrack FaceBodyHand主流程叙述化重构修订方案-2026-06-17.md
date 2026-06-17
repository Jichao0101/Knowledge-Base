---
title: DmsTrack Face/Body/Hand 主流程叙述化重构修订方案
summary: 修订 DmsTrack 整体内部架构可读性优化路线：当前优先级从局部 helper/lambda 整理切换为 Face/Body/Hand phase 主流程高层叙述化，允许用少量 private helper 换取更清晰的 phase 边界。
status: planned
doc_role: design_review
truth_role: project_plan
scope: /home/jichao/dms 中 DmsTrack 的 Face/Body/Hand phase 内部组织；不改变 public API、legacy output ABI、Face-owned identity、matching/miss/retire/publish/cleanup 行为语义。
sources:
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack整体内部架构可读性优化评审与方案-2026-06-17.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack BodyPhase match selection可读性整理闭环记录-2026-06-17.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack HandPhase internal helper可读性整理闭环记录-2026-06-17.md
  - /home/jichao/dms/include/utils/track.h
  - /home/jichao/dms/source/utils/track.cpp
updated_at: 2026-06-17
supersedes:
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack整体内部架构可读性优化评审与方案-2026-06-17.md
---

# 1 修订原因

前一版整体方案正确识别了局部 lambda 不是更好抽象，但后续代码小步仍偏向“把局部机制移到 `.cpp` helper”。这能减少闭包捕获和局部噪音，但没有充分解决当前主要问题：

- `updateFaceTracks` 已有 assignment loss helper，但主函数仍直接承载 solve/apply、bootstrap 和 miss/erase 细节，读者需要在同一层级理解 Hungarian 结果应用、new face 创建和生命周期推进。
- `updateBodyTracks` 后半段的长期状态更新、miss 推进、retire、publish driver body evidence snapshot 仍散落在一个函数内。
- `updateHandTracks` 主流程仍没有以高层状态机摘要呈现，`updateHandTrackState` / `processSlot` 这类复杂局部闭包仍让读者在主函数中同时加载 solver、slot update、miss、cleanup 和 publish。

因此本修订方案将第一优先级调整为：

```text
Face/Body/Hand phase 主流程高层叙述化 > private interface 最小化
```

private interface 是成本项，不是禁止项。若 private helper 能让主流程更清晰、依赖更显式、phase 边界更稳定，应允许新增；但必须证明收益大于新增认知入口成本。

# 2 必须保持的行为边界

- public `DmsTrack::Init()` / `DmsTrack::Update(...)` 签名不变。
- legacy `body/face/left_hand/right_hand` output map ABI 与 key 语义不变。
- Face-owned identity 主线不变。
- Body / Hand 仍只能作为 selected driver face 下的 evidence/cache。
- `left/right hand map key == owner face id` 不变。
- 非 driver owner 不发布 body/hand。
- Hand 只消费本帧 `driverBodyEvidence`，不反读 legacy body output map。
- 2m profile 不输出陈旧 body/hand。
- 不改变 matching、bootstrap、miss、retire、publish、cleanup 行为语义。
- 不引入 `Row/View/Payload/Result/Context` 等只搬运局部字段的新类型。
- 不新增序列化、协议、持久化、并发或生命周期模型。
- 不做无关格式化、风格化命名清理或注释大改。

# 3 Helper / private interface 策略

## 3.1 `.cpp` anonymous namespace helper

适合：

- 纯计算。
- detection/candidate 收集。
- loss 构造。
- slot reset。
- publish gate。
- 不依赖 `DmsTrack` 长期状态的局部机制。

## 3.2 `DmsTrack` private helper

适合：

- 需要操作 `m_bodyTracks`、`m_handTracks`、`m_retiredBodyTracks`、`m_faceTracks` 或 `m_parameters`。
- 表达稳定 phase 子流程，而不是机械 step。
- 能让 `updateFaceTracks` / `updateBodyTracks` / `updateHandTracks` 主体读起来像状态机摘要。

允许新增 private helper，但必须满足：

- 名字表达领域动作，不使用 `step1` / `process` / `fill` 这类执行脚本名。
- 调用点能读出 phase 状态推进。
- 副作用清楚。
- 参数数量可控。
- 不把固定执行脚本暴露成大量 private method 清单。

禁止新增：

- 搬运型 `Context/Payload/View/Result/Row`。
- 同时混合 solver index、状态指针、领域对象和输出约束的中间结构。
- 只为避免参数传递而引入的长期类型。

# 4 Face phase 修订目标

`updateFaceTracks` 主体应收敛为类似状态机摘要：

```cpp
void DmsTrack::updateFaceTracks(...) {
    const auto faceDetections = CollectDetectionsByClass(...);
    predictExistingFaceTracks(faceIds);
    solveAndApplyFaceAssignments(faceDetections, faceIds, imgSize, usedDetections, matchedFaceTracks);
    bootstrapUnmatchedFaceDetections(faceDetections, imgSize, usedDetections, matchedFaceTracks);
    advanceAndEraseUnmatchedFaceTracks(matchedFaceTracks);
}
```

不要求逐字使用上述函数名，但主流程必须体现：

1. 收集 face detections。
2. 预测 existing face tracks，并得到稳定迭代顺序的 face ids。
3. solve/apply detection-to-face assignment。
4. bootstrap unmatched detections 为新 face track。
5. 推进 unmatched face 的 miss，并 erase expired face tracks。

当前 `BuildFaceAssignmentLoss` 抽象程度可以保留。本轮 Face 重点不是 matching loss 公式，而是把 Hungarian 结果应用、bootstrap、miss/erase 分成可读的 phase 子流程。

# 5 Body phase 修订目标

`updateBodyTracks` 主体应收敛为类似状态机摘要：

```cpp
std::map<track_id, TrackInfo> DmsTrack::updateBodyTracks(...) {
    const auto bodyDetections = CollectDetectionsByClass(...);
    const auto ownerFaceIds = collectEligibleBodyOwners(driverFaceId);

    std::set<int> usedDetections;
    std::set<track_id> matchedOwnerFaces;
    matchOrAcquireDriverBodyEvidence(bodyDetections, ownerFaceIds, driverFaceId, usedDetections, matchedOwnerFaces);
    advanceAndRetireBodyEvidence(driverFaceId, matchedOwnerFaces);
    return publishDriverBodyEvidenceSnapshot(curResult, frameSize, driverFaceId);
}
```

不要求逐字使用上述函数名，但主流程必须体现：

1. 收集 body detections。
2. 收集 eligible driver owner face。
3. 对 driver owner 执行 tracked body matching 或 face-anchored acquisition。
4. 应用 matched body evidence 到 `m_bodyTracks`。
5. 推进 unmatched / non-current / dead owner 的 miss。
6. retire expired body evidence 到 `m_retiredBodyTracks`。
7. 发布本帧 driver body evidence snapshot，并返回给 hand phase。

当前 `SelectTrackedBodyDetection`、`SelectFaceAnchoredBodyDetection` 抽象程度可以保留。本轮 Body 重点不是短时匹配算法，而是长期状态推进、retire、publish snapshot 的分层。

# 6 Hand phase 修订目标

`updateHandTracks` 主体应收敛为类似状态机摘要：

```cpp
void DmsTrack::updateHandTracks(...) {
    const auto handDetections = CollectDetectionsByClass(...);
    const auto allowedOwners = CollectAllowedHandOwners(driverBodyEvidence);

    predictExistingHandSlots();
    updateOwnedHandSlotsFromBodyConstrainedDetections(handDetections, driverBodyEvidence, allowedOwners, usedDetections, matchedSlots);
    recoverUnmatchedHandSlots(handDetections, driverBodyEvidence, allowedOwners, usedDetections, matchedSlots);
    cleanupOrphanAndExpiredHandSlots(driverBodyEvidence);
    publishDriverBoundHandSlots(curResult, frameSize, driverBodyEvidence, allowedOwners);
}
```

不要求逐字使用上述函数名，但主流程必须体现：

1. 收集 hand detections。
2. 收集 allowed driver hand owners。
3. predict existing hand slots。
4. first pass：基于 driver body constrained candidates 更新 owner-local left/right slots。
5. second pass：对未在 first pass 命中的 initialized slots 做受 body 约束的 recovery matching。
6. cleanup：清理 orphan hand、expired slot、retired body cache。
7. publish：发布 driver-bound left/right hand outputs。

`updateHandTrackState` / `processSlot` 不应长期作为主函数局部闭包存在。若下沉到 `.cpp` helper 后参数膨胀或明显依赖 `m_handTracks/m_parameters`，应改为少量 `DmsTrack` private helper。

# 7 Hand first/second pass 与 publish 边界

first pass 与 second pass 语义不同，必须在主流程中显式分开：

- first pass：每个 allowed owner 内部，left/right slot 对 body-constrained candidates 做 assignment。
- second pass：对 first pass 未命中的 initialized slots 做 recovery matching，仍必须受 owner body track 几何约束。

publish 阶段要读得出：

- primary publish：直接发布当前 owner 的 left/right slot。
- fallback publish：只补同 owner 未发布的轨迹。
- 保持 occupied left/right id 防重语义。
- 保持输出 key 等于 owner face id。
- 不允许旧 owner 用自己的 id 重新输出。
- 不允许从其他 owner 迁移 best hand id。

若发现 fallback 与 primary 行为完全重复，默认先不删除；只有行为等价可证明时才合并。

# 8 分步执行计划

| 阶段 | 范围 | 允许 | 禁止 | 验证 |
|---|---|---|---|---|
| 0 修订方案写回 | 知识库 | 新增本修订方案与结构审计记录 | 改 current 为计划枚举 | KB diff check |
| 1 Face 主流程叙述化 | `track.h` / `track.cpp` | 少量 DmsTrack private helper；复用现有 `.cpp` matching helper | 改行为、改 public API、新增搬运类型 | diff check + J6B 编译 + review |
| 2 Body 主流程叙述化 | `track.h` / `track.cpp` | 少量 DmsTrack private helper；复用现有 `.cpp` matching helper | 改行为、改 public API、新增搬运类型 | diff check + J6B 编译 + review |
| 3 Hand 主流程叙述化 | `track.h` / `track.cpp` | 少量 DmsTrack private helper；下沉复杂闭包 | 改 solver/miss/publish/cleanup 语义、新增搬运类型 | diff check + J6B 编译 + review |
| 4 Hand first/second pass 与 publish 边界微调 | `track.cpp` 为主 | 只在 review 后做命名/边界小修 | 删除 fallback 或合并语义不明逻辑 | diff check + 编译 |

每个实现阶段必须使用 `interface-abstraction-implementation-guard`。若新增 private helper，记录其“可读性收益是否大于 private interface 成本”。

# 9 Current 文档组写回策略

本修订方案和后续每步实现记录放入 `Current Maintenance Records/` 与 `subpower_runs/`。

除非当前行为事实、默认入口、恢复顺序或 recoverability 状态变化，否则不更新 Tracking current 文档组，不把 helper 名称和小步提交写入 current 正文。
