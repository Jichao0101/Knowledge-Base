---
title: DmsTrack FacePhase assignment loss 可读性整理闭环记录
summary: 记录按照 DmsTrack 整体内部架构可读性优化方案执行的第一笔代码小步：将 updateFaceTracks 中 face assignment loss 矩阵构造收敛为 .cpp internal helper，保持 Face phase 行为和接口不变。
status: closed
doc_role: implementation_record
truth_role: project_record
scope: /home/jichao/dms/source/utils/track.cpp 中 Face phase 局部组织；不覆盖 Body/Hand 后续阶段。
sources:
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack整体内部架构可读性优化评审与方案-2026-06-17.md
  - /home/jichao/dms/source/utils/track.cpp
updated_at: 2026-06-17
---

# 1 本步范围

- 方案阶段：阶段 2 Face phase 局部组织的第一小步。
- 代码范围：`/home/jichao/dms/source/utils/track.cpp`。
- 本步只整理 `updateFaceTracks` 内 face assignment loss 矩阵构造。
- 未修改：
  - `/home/jichao/dms/include/utils/track.h`
  - public `DmsTrack::Init/Update`
  - private phase 方法签名
  - Face bootstrap、miss lifecycle、driver selection、profile gate、Body/Hand phase

# 2 实现内容

- 新增 `.cpp` anonymous namespace helper：
  - `BuildFaceAssignmentLoss(...)`
- `updateFaceTracks` 中原有 face assignment loss 矩阵构造改为调用该 helper。
- helper 内保留原有逻辑：
  - matrix size 仍为 `detectionCount + trackCount`
  - real edge 初值仍为 `1e6f`
  - driver stable face 对 small face candidate 仍跳过
  - face score 仍由 `BuildFaceTrackMatchScore` 生成
  - driver distance gate 仍为 `0.45f`，非 driver 仍为 `0.65f`
  - `breakdown.total >= face.dummyLoss` 仍拒绝
  - dummy edge 仍使用 `face.dummyLoss`
  - bottom-right dummy block 仍为 `0.0f`
- 实现中将 helper 对 `faceTracks` 的访问写成 `find` + `continue`，避免用 `map::at` 引入新的异常失败模型。

# 3 Interface Guard 结论

- public API 变化：无。
- private header API 变化：无。
- 新增稳定类型：无。
- 新增 Row/View/Payload/Result/Context：无。
- 新增 helper 可见性：仅 `.cpp` anonymous namespace。
- 行为意图变化：无。
- 抽象判断：`BuildFaceAssignmentLoss` 只隐藏 Face phase 内稳定且纯局部的 matrix 构造细节，不把固定执行脚本暴露到 header，也不承载跨 phase 状态。

# 4 验证

- `git -C /home/jichao/dms diff --check -- source/utils/track.cpp`：通过。
- `bash scripts/compile_j6b.sh`：通过，最终 `[100%] Built target sdk`。

# 5 审查与限制

- host 已完成 diff 审计：实际 diff 只涉及 Face assignment loss 构造位置移动，不触及 matching 结果应用、bootstrap、miss cleanup 或输出 map。
- 新一轮 subagent reviewer 未执行：当前会话子代理额度已满，无法 spawn 新 repo-reviewer。本记录不声明 complete subagent-first review。
- 未执行：
  - runtime replay
  - 单元测试
  - 板端验证

# 6 后续

- 下一步可继续按照整体方案评估 Body phase 局部组织，或先补本步独立 review。
- 若后续需要新增 private helper 或改变 matching/acquisition/lifecycle 行为，必须重新执行 `interface-abstraction-implementation-guard`。
