---
title: DmsTrack updateHandTracks unmatched miss 可读性整理闭环记录
summary: 第二阶段可读性优化 Step 2，仅将 unmatched hand slot 的 miss 推进定位逻辑收束为函数局部 lambda。
status: reviewed
doc_role: implementation_record
truth_role: project_record
scope: DMS Tracking updateHandTracks unmatched slot miss 推进行为不变整理、编译验证、interface guard 审计、独立 review 与知识库写回；不包含 runtime replay、单元测试或板端验证。
sources:
  - /home/jichao/dms/AGENTS.md
  - /home/jichao/dms/source/utils/track.cpp
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack updateHandTracks第二阶段可读性优化方案-2026-06-17.md
  - 02_Projects/DMS/04_Tracking/tracking_implementation_current.md
  - 02_Projects/DMS/04_Tracking/tracking_validation_current.md
  - 02_Projects/DMS/04_Tracking/subpower_runs/2026-06-17_hand_unmatched_miss_readability/
risks:
  - 本轮只完成静态 review、diff check 与本地 J6B 编译；未执行 runtime replay、单元测试或板端验证。
  - 本轮不处理 second pass Hungarian 矩阵构造、owner candidate collection、cleanup 或 publish 段。
updated_at: 2026-06-17
---

# 1 变更摘要

本轮执行 `updateHandTracks` 第二阶段可读性优化 Step 2：只整理 unmatched hand slot 的 miss 推进定位逻辑。

代码变更：

- 在 `unmatchedSlots` 构造之后新增函数局部 lambda `advanceUnmatchedSlotMiss`。
- 该 lambda 统一执行：
  - 按 `slotKey.ownerFaceId` 查找 `m_handTracks`。
  - owner 不存在时直接返回。
  - 根据 `slotKey.isRight` 选择 left/right slot。
  - 对选中的 `slot.track` 执行 `AdvanceMiss`。
- second pass Hungarian 未匹配分支和无 hand detection 分支改为调用该 lambda。

# 2 接口与抽象守门结论

保持不变：

- `DmsTrack::Init` / `DmsTrack::Update` public API。
- `track.h` private phase 方法签名。
- `unmatchedSlots` 构造条件。
- `matchedSlots`、`usedDetections`、second pass Hungarian 输入和 match acceptance 条件。
- cleanup/reset/publish 顺序。

允许且已执行：

- 在函数局部使用 lambda 收束重复的 slot 定位与 `AdvanceMiss` 调用。

未引入：

- 新 Row/View/Payload/Result 类型。
- Header-level helper。
- 跨 phase wrapper 或稳定类型。

# 3 Review 结论

独立 repo-reviewer 结论：`approved`，无 findings。

审查确认：

- `advanceUnmatchedSlotMiss` 提取的是原有 `m_handTracks.find`、owner 缺失保护、left/right 选择和 `AdvanceMiss(slot.track)` 逻辑。
- 两个调用点保留原触发条件和每 slot miss 次数。
- 未修改 `unmatchedSlots` 构造、`matchedSlots`、`usedDetections`、second pass Hungarian 输入、match acceptance、cleanup/reset/publish、header/API surface 或无关逻辑。

# 4 验证

- `git -C /home/jichao/dms diff --check -- source/utils/track.cpp`：通过。
- `bash scripts/compile_j6b.sh`：通过，最终输出 `[100%] Built target sdk`。
- 独立 repo-reviewer：`approved`。

未执行：

- runtime replay。
- 单元测试。
- 板端验证；本次任务边界声明不涉及板端验证。

# 5 残余风险与后续步骤

- Step 3 可继续整理 driver owner candidate collection，但不得改变 allowed owner 只来自 driver body evidence 且 stable `DRIVER` 的候选域。
- 若后续步骤需要修改 private signature、helper 可见性或新增类型，必须重新执行 `interface-abstraction-implementation-guard`。

# 6 写回决策

本记录写入项目区 `02_Projects/DMS/04_Tracking/Current Maintenance Records/`。本轮内容仍是 DMS Tracking 项目绑定实现事实，不提升到 `01_Knowledge/`。
