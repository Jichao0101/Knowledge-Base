---
title: DmsTrack updateHandTracks publish 段可读性整理闭环记录
summary: 第二阶段可读性优化 Step 1，仅将 hand publish 条件与写 map 的重复逻辑收束为函数局部 lambda。
status: reviewed
doc_role: implementation_record
truth_role: project_record
scope: DMS Tracking updateHandTracks publish 段行为不变整理、编译验证、interface guard 审计、独立 review 与知识库写回；不包含 runtime replay、单元测试或板端验证。
sources:
  - /home/jichao/dms/source/utils/track.cpp
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack updateHandTracks第二阶段可读性优化方案-2026-06-17.md
  - 02_Projects/DMS/04_Tracking/tracking_implementation_current.md
  - 02_Projects/DMS/04_Tracking/tracking_validation_current.md
  - 02_Projects/DMS/04_Tracking/subpower_runs/2026-06-17_hand_publish_readability/
risks:
  - 本轮只完成静态 review、diff check 与本地 J6B 编译；未执行 runtime replay、单元测试或板端验证。
  - 本轮目标是降低 publish 段阅读复杂度，不处理 updateHandTracks 中候选构造、Hungarian assignment、slot lifecycle 或 retired-owner cleanup 的层级混杂问题。
updated_at: 2026-06-17
---

# 1 变更摘要

本轮执行 `updateHandTracks` 第二阶段可读性优化 Step 1：只整理 hand publish 段。

代码变更：

- 在 `updateHandTracks` 函数内部新增局部 lambda `publishHandSlot`。
- `publishHandSlot` 统一保留 hand slot 发布前的四个条件：
  - slot 已初始化。
  - 同 owner 未被对应 left/right occupied set 占用。
  - `ShouldOutputTrackByHitCount(slot.track, m_parameters.hand)` 通过。
  - `HandBelongsToBody(bodyBox, slot.track.box)` 通过。
- left/right 正常发布路径与 fallback 发布路径改为调用该 lambda。
- stage tag、legacy output map、owner key 和 body evidence 来源保持原语义。

# 2 接口与抽象守门结论

保持不变：

- `DmsTrack::Init` / `DmsTrack::Update` public API。
- `track.h` private phase 方法签名。
- 四类 legacy map ABI。
- hand matching、miss 推进、cleanup、retired-owner 清理和 2m/5m profile 分流。

允许且已执行：

- 在函数局部使用 lambda 收束重复 publish 条件和 `PublishSanitizedTrack` 调用。

未引入：

- 新 Row/View/Payload/Result 类型。
- Header-level helper。
- 跨 phase wrapper 或稳定类型。

# 3 Review 结论

独立 repo-reviewer 结论：`approved`，无 findings。

审查确认：

- 正常 left/right publish 的条件、output map、output key 和 stage tag 等价。
- fallback 仍只处理存在 allowed owner 与 driver body evidence 的同 owner hand state。
- lambda 在 fallback 中插入 occupied set 不改变行为；`m_handTracks` 以 owner 唯一存储，fallback loop 每个 owner 只访问一次。
- 未发现 API/header surface、lifecycle cleanup 或无关逻辑变化。

# 4 验证

- `git -C /home/jichao/dms diff --check -- source/utils/track.cpp`：通过。
- `bash scripts/compile_j6b.sh`：通过，最终输出 `[100%] Built target sdk`。
- 独立 repo-reviewer：`approved`。

未执行：

- runtime replay。
- 单元测试。
- 板端验证；本次任务边界声明不涉及板端验证。

# 5 残余风险与后续步骤

- Step 2 可继续整理 unmatched slot advance，但不得改变 miss 推进次数或 cleanup 时机。
- Step 3 可继续整理 driver owner candidate collection，但不得新增 Row/View/Payload/Result 或改变 owner 候选域。
- 若后续步骤需要修改 private signature、helper 可见性或新增类型，必须重新执行 `interface-abstraction-implementation-guard`。

# 6 写回决策

本记录写入项目区 `02_Projects/DMS/04_Tracking/Current Maintenance Records/`。本轮内容仍是 DMS Tracking 项目绑定实现事实，不提升到 `01_Knowledge/`。
