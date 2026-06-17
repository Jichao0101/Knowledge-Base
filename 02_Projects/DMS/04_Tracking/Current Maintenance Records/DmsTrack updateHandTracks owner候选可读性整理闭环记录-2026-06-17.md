---
title: DmsTrack updateHandTracks owner 候选可读性整理闭环记录
summary: 第二阶段可读性优化 Step 3，仅将 allowed owner 收集、slot prediction 与 body-constrained hand candidate 收集拆成函数局部 lambda。
status: reviewed
doc_role: implementation_record
truth_role: project_record
scope: DMS Tracking updateHandTracks owner/candidate 准备区行为不变整理、编译验证、interface guard 审计、独立 review 与知识库写回；不包含 runtime replay、单元测试或板端验证。
sources:
  - /home/jichao/dms/source/utils/track.cpp
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack updateHandTracks第二阶段可读性优化方案-2026-06-17.md
  - 02_Projects/DMS/04_Tracking/tracking_implementation_current.md
  - 02_Projects/DMS/04_Tracking/tracking_validation_current.md
  - 02_Projects/DMS/04_Tracking/subpower_runs/2026-06-17_hand_owner_candidate_readability/
risks:
  - 本轮只完成静态 review、diff check 与本地 J6B 编译；未执行 runtime replay、单元测试或板端验证。
  - 本轮不处理 matching matrix、slot lifecycle、cleanup/reset 或 publish 段。
updated_at: 2026-06-17
---

# 1 变更摘要

本轮执行 `updateHandTracks` 第二阶段可读性优化 Step 3：只整理 owner/candidate 准备区。

代码变更：

- 新增函数局部 lambda `collectAllowedHandOwners`，仍只从 `driverBodyEvidence` 中 `stablePersonType == PersonType::DRIVER` 的 body track 收集 owner。
- 新增函数局部 lambda `predictHandSlot`，统一 initialized guard、`PredictMotion` 和 `predBox` 写入。
- 将已有 `buildCandidates` 重命名并收敛为 `collectBodyConstrainedHandCandidates`，仍清空候选数组、按原顺序遍历 `handDetections`、排除 `usedDetections`、要求 `HandBelongsToBody(bodyBox, handDetections[i])`。
- `updateHandTrackState` 仍传入 `bodyTrack.box` 作为 body 几何约束。

# 2 接口与抽象守门结论

保持不变：

- `DmsTrack::Init` / `DmsTrack::Update` public API。
- `track.h` private phase 方法签名。
- allowed owner 候选域。
- hand prediction 遍历范围和 left/right 顺序。
- body-constrained hand candidate 条件。
- matching matrix、`matchedSlots`、`usedDetections`、lifecycle、cleanup/reset/publish。

允许且已执行：

- 在函数局部使用 lambda 分别表达 owner 收集、slot prediction 和 body-constrained candidate 收集。

未引入：

- 新 Row/View/Payload/Result 类型。
- Header-level helper。
- 跨 phase wrapper 或稳定类型。

# 3 Review 结论

独立 repo-reviewer 结论：`approved`，无 findings。

审查确认：

- `collectAllowedHandOwners` 仍只从 `driverBodyEvidence` 中 stable `DRIVER` body track 派生 owner。
- `predictHandSlot` 保留 initialized guard，并仍对每个现有 `m_handTracks` owner 按 left 后 right 调用。
- `collectBodyConstrainedHandCandidates` 仍清空 vector、按原 `handDetections` 顺序遍历、排除 `usedDetections`，并用相同输入调用 `HandBelongsToBody`。
- 未修改 matching matrix、`matchedSlots` / `usedDetections` 语义、lifecycle、cleanup/reset/publish、API/header surface 或无关逻辑。

# 4 验证

- `git -C /home/jichao/dms diff --check -- source/utils/track.cpp`：通过。
- `bash scripts/compile_j6b.sh`：通过，最终输出 `[100%] Built target sdk`。
- 独立 repo-reviewer：`approved`。

未执行：

- runtime replay。
- 单元测试。
- 板端验证；本次任务边界声明不涉及板端验证。

# 5 残余风险与后续步骤

- Step 4 可选继续整理 retired-owner cleanup，但不得改变 orphan hand cleanup、expired slot reset、`m_retiredBodyTracks` 删除条件或执行顺序。
- 若 Step 4 需要新增稳定 cleanup context、payload 或跨 phase 类型，应停止并重新做 deep-module review。

# 6 写回决策

本记录写入项目区 `02_Projects/DMS/04_Tracking/Current Maintenance Records/`。本轮内容仍是 DMS Tracking 项目绑定实现事实，不提升到 `01_Knowledge/`。
