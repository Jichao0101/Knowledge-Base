---
title: Head-first 跟踪代码重构闭环记录
summary: 记录 2026-05-23 DMS tracking 从 body-first 残留向 head-first identity ownership 收敛的代码改动、编译验证、审查结论与剩余风险。
status: verified
doc_role: maintenance_record
truth_role: project_record
scope: DMS Tracking head-first code refactor on /home/jichao/dms/include/utils/track.h and /home/jichao/dms/source/utils/track.cpp
sources:
  - /home/jichao/dms/include/utils/track.h
  - /home/jichao/dms/source/utils/track.cpp
  - 02_Projects/DMS/04_Tracking/head-first渐进跟踪方案.md
  - 02_Projects/DMS/04_Tracking/head-first渐进跟踪实现.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/head-first双阶段body-torso匹配静态分析记录-2026-05-23.md
updated_at: 2026-05-23
---

# 0 本次补充 2026-05-23

本轮评估后又补了一处代码收敛：

- 旧 hand 输出阶段会在所有 `m_bodyHandTracks` 中选择几何最优的 hand slot，并可能用旧 owner id 写入 left/right hand map；
- 该路径已改为只按当前 driver head-owned body evidence 的同一 `headId` 发布 hand；
- `left_hand_output_anchor / right_hand_output_anchor / *_orphan` 输出标签已收敛为 `*_head_bound` 和 `*_head_bound_fallback`；
- 重新执行 `bash scripts/compile_j6b.sh`，最终 `[100%] Built target sdk`。

当前结论：head-first 第一轮代码主线已完成本地编译验证；运行效果仍需回放或板端证据。

# 1 目标

本轮目标是把 tracking 代码从 body-first 残留继续收敛到 head-first：

- head/face trackId 是 identity 的唯一来源；
- body/torso 不再独立分配 identity id；
- body/torso evidence 按 head trackId 挂载，并投影回 legacy body map；
- hand evidence 只挂在已发布的 driver head-bound body evidence 下；
- driver head 选择中 size continuity 高于位置 loss，用于优先过滤 driver ROI 内的后排/副驾探头干扰。

# 2 代码改动

代码范围：

- `/home/jichao/dms/include/utils/track.h`
- `/home/jichao/dms/source/utils/track.cpp`

核心变化：

- `DmsTrack::Update` 调整为 `face -> selectDriverHead -> body evidence -> hand`。
- 删除 body track 独立 id 分配入口，不再使用 `allocateBodyTrackId` 或 `m_nextBodyTrackId`。
- 新增 face/head id 分配与 driver head 选择状态：
  - `m_nextFaceTrackId`
  - `m_driverHeadId`
  - `allocateFaceTrackId`
  - `selectDriverHead`
- `m_bodyTracks` 的 key 改为 head trackId。body 只作为 head-owned evidence 状态，不再作为 identity owner。
- `updateBodyTracks` 改为按 head 遍历：
  1. driver head 优先；
  2. 已有 body evidence 的 head 先按 body 运动模型做常规 tracking match；
  3. 常规 tracking match 失败或未绑定 body 时，按当前 head 几何做 body/torso acquisition；
  4. matched body evidence 写回 `m_bodyTracks[headId]`；
  5. 对外 `m_bodyTrackResultMap` 仍用同一 `headId` 发布兼容 body 结果。
- `updateHandTracks` 保持 legacy map 形态，但注释明确：历史变量 `bodyId` 在 head-first 下实际是 head trackId；hand 不能自建身份，只能挂在已发布 driver body evidence 下。
- 非 driver face 若历史稳定类型为 DRIVER，会降级为前排/后排并清空 `driverCount`，避免旧投票把身份弹回 DRIVER。

# 3 Driver Head 选择

driver head 选择在稳定 face/head 中进行：

- 必须在 driver ROI 内；
- 明确排除 front passenger ROI；
- small face 直接拒绝；
- 若有上一帧 driver head reference，使用 `FaceSizeContinuityLoss` 作为硬门控，`sizeLoss > 0.70` 直接拒绝；
- 综合分数使用 `3.0 * sizeLoss + positionLoss + continuityBonus`。

该策略体现本轮实车现象判断：driver ROI 内可能出现后排或副驾探头干扰，size continuity 的权重应高于位置 loss；明显小脸或尺寸突变候选应先被过滤。

# 4 验证

本地编译：

```text
cd /home/jichao/dms
bash scripts/compile_j6b.sh
```

结果：

```text
[100%] Linking CXX shared library libsdk.so
[100%] Built target sdk
```

未执行：

- 未做板端部署；
- 未做视频回放；
- 未生成运行日志。

# 5 审查结论

静态审查结论：

- head/face 已成为 trackId 的唯一分配入口；
- body/torso evidence 不再独立创建 identity id；
- 已有 body evidence 的 head 和新建/未绑定 body evidence 的 head 共用同一套 head-to-body acquisition 逻辑；
- legacy body/hand map 仍保留，但 key 已按 head trackId 投影；
- driver head 选择已把 size continuity 作为更高优先级的过滤条件。

# 6 剩余风险

- 当前证据为静态分析加本地编译，不代表实车或回放效果已验收。
- `selectDriverHead` 当前使用 face/head bbox 的尺寸连续性，尚未结合真实 head pose 或 landmark 后验。
- hand 当前只挂 driver head-bound body evidence；多人 hand 输出能力不是本轮目标。
- legacy 下游仍通过四类 map 消费结果，运行中需确认 `body / face / left_hand / right_hand` 同 key 行为符合 callback 与 fusion 预期。
- 需要补代表性 2m/5m 回放，特别关注 driver ROI 内小脸、后排探头、副驾探头和 hand owner 稳定性。
