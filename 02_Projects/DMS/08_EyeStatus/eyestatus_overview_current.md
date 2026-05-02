---
title: EyeStatus Overview Current
summary: EyeStatus 当前态入口，定义文档组恢复顺序、模块边界、当前事实源和部署验证状态。
status: draft_verified_project
doc_role: current
truth_role: current
current_kind: overview
lifecycle_state: active
default_entry: true
default_entry_verified: false
sync_mode: current_creation
current_files_must_update:
  - 02_Projects/DMS/08_EyeStatus/eyestatus_overview_current.md
  - 02_Projects/DMS/08_EyeStatus/eyestatus_design_current.md
  - 02_Projects/DMS/08_EyeStatus/eyestatus_spec_current.md
  - 02_Projects/DMS/08_EyeStatus/eyestatus_implementation_current.md
  - 02_Projects/DMS/08_EyeStatus/eyestatus_validation_current.md
history_files_to_mark:
  - 02_Projects/DMS/08_EyeStatus/eyestatus推理前处理对齐训练流程记录.md
  - 02_Projects/DMS/08_EyeStatus/EyeStatus_VpResize_Y_Adapt_板端验证记录.md
single_pass_recoverable: false
single_pass_recoverable_reason: 初次创建 current 文档组，尚未完成独立 recoverability verification。
retrieval_priority: current
related_code:
  - /home/jichao/dms/include/models/eye_status_model.h
  - /home/jichao/dms/source/models/eye_status_model.cpp
  - /home/jichao/dms/etc/eye_status_model.json
  - /home/jichao/dms/source/models/face_landmark_model.cpp
sources:
  - 02_Projects/DMS/08_EyeStatus/eyestatus推理前处理对齐训练流程记录.md
  - 02_Projects/DMS/08_EyeStatus/EyeStatus_VpResize_Y_Adapt_板端验证记录.md
  - /home/jichao/dms/include/models/eye_status_model.h
  - /home/jichao/dms/source/models/eye_status_model.cpp
  - /home/jichao/dms/etc/eye_status_model.json
scope: 适用于恢复 EyeStatus 当前部署态、推理前处理、实现边界与验证证据。
risks:
  - 本组 current 是 creation 场景，不是已完成可恢复性审核的 hardening_refactor。
  - 板端验证覆盖了 EyeStatus 预处理、推理、后处理不报错，不等价于分类精度或全量场景验收。
updated_at: 2026-05-02
---

## 0.1 Current Scope

本目录是 DMS EyeStatus 的独立部署知识区，不再把 EyeStatus 当前态放在 `06_SDK_Integration` 子目录下维护。

默认恢复顺序：

1. [[02_Projects/DMS/08_EyeStatus/eyestatus_overview_current]]
2. [[02_Projects/DMS/08_EyeStatus/eyestatus_design_current]]
3. [[02_Projects/DMS/08_EyeStatus/eyestatus_spec_current]]
4. [[02_Projects/DMS/08_EyeStatus/eyestatus_implementation_current]]
5. [[02_Projects/DMS/08_EyeStatus/eyestatus_validation_current]]

默认实现输入链：

1. [[02_Projects/DMS/08_EyeStatus/eyestatus_design_current]]
2. [[02_Projects/DMS/08_EyeStatus/eyestatus_spec_current]]
3. [[02_Projects/DMS/08_EyeStatus/eyestatus_implementation_current]]
4. [[02_Projects/DMS/08_EyeStatus/eyestatus_validation_current]]

## 0.2 Current Truth

- 当前模型类：`ModelsDomain::EyeStatusModel`
- 当前配置：`/home/jichao/dms/etc/eye_status_model.json`
- 当前模型权重配置：`/model_weight/eye_status_model/J6B/eyestatus_mbv2_128_nv12.hbm`
- 当前输入来源：driver face track 对应的 68 点 landmarks
- 当前输出位置：`AtomicResult::m_eyeStatusResultMap[trackId]`
- 当前预处理核心：左右眼 6 点 tight bbox -> 方形 Y crop -> OOB constant padding 114 -> `VpResize_Y_Adapt` 到 `128x128`

## 0.3 Module Boundary

EyeStatus 负责：

- 从 driver face track 和 landmark 结果中定位左右眼。
- 为左右眼分别构造模型输入。
- 执行模型推理与 4 类 softmax 后处理。
- 写出左右眼状态、分数和 eye crop 元数据。

EyeStatus 不负责：

- face track 的生成与稳定性。
- landmark 模型本身。
- 疲劳融合业务规则。
- 通用 VP resize 算子实现。
- 分类精度训练结论。

## 0.4 Current Document Roles

- current：
  - [[02_Projects/DMS/08_EyeStatus/eyestatus_overview_current]]
  - [[02_Projects/DMS/08_EyeStatus/eyestatus_design_current]]
  - [[02_Projects/DMS/08_EyeStatus/eyestatus_spec_current]]
  - [[02_Projects/DMS/08_EyeStatus/eyestatus_implementation_current]]
  - [[02_Projects/DMS/08_EyeStatus/eyestatus_validation_current]]
- history / evidence：
  - [[02_Projects/DMS/08_EyeStatus/eyestatus推理前处理对齐训练流程记录]]
  - [[02_Projects/DMS/08_EyeStatus/EyeStatus_VpResize_Y_Adapt_板端验证记录]]

## 0.5 Known Gaps

- `single_pass_recoverable` 暂为 false，原因是本次只完成 current 文档组创建与内容收敛，未做独立可恢复性验证。
- 板端验证证明 EyeStatus 当前链路不再因预处理 VP resize 报错，但没有覆盖模型精度、长时稳定性或全量输入源。
- 仍需后续确认 `input_channels=3` 配置与当前 Y-only 输入在部署契约上的命名一致性。
