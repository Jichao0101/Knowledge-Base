---
title: EyeStatus Design Current
summary: EyeStatus 当前设计文档，说明输入依赖、预处理设计、VP resize 选择、输出语义与非目标。
status: draft_verified_project
doc_role: current
truth_role: current
current_kind: design
lifecycle_state: active
default_entry: false
retrieval_priority: current
related_code:
  - /home/jichao/dms/source/models/eye_status_model.cpp
  - /home/jichao/dms/include/models/eye_status_model.h
sources:
  - 02_Projects/DMS/08_EyeStatus/eyestatus推理前处理对齐训练流程记录.md
  - 02_Projects/DMS/08_EyeStatus/EyeStatus_VpResize_Y_Adapt_板端验证记录.md
  - /home/jichao/dms/source/models/eye_status_model.cpp
scope: 适用于理解 EyeStatus 当前部署设计，不覆盖训练侧完整数据生产流程。
risks:
  - 训练仓未定义 68 点 landmarks 到 eye bbox 的转换规则，当前沿用 DMS 侧 6 点 eye bbox。
updated_at: 2026-05-02
---

## 0.1 Design Goal

EyeStatus 当前设计目标是让部署侧推理前处理与训练侧 Stage D 的关键 ROI 语义对齐，并规避旧 `VpRoiResize_Y` 在 EyeStatus 预处理中的 VP padding/roi 约束问题。

当前设计接受以下事实：

- EyeStatus 的 crop 本身是正方形。
- 只有 eye crop 越出图像边界时才先 padding 再 resize。
- 正方形 crop 直接 resize 到模型输入尺寸不会引入长宽比形变问题。
- 不由模型侧额外保证 padding 奇偶，也不新增奇偶兜底。

## 0.2 Input Dependencies

EyeStatus 当前依赖：

- `m_faceTrackResultMap` 中稳定人员类型为 `DRIVER` 的 face track。
- `m_landmarkResultMap[trackId]` 中至少 68 个 landmark。
- 原始图像 `ImageData::m_img`，支持 `CV_8UC1` 或 `CV_8UC3`。

若没有 driver face track、没有对应 landmark 或 landmark 数不足，当前实现返回 `SUCCESS` 并跳过 EyeStatus 输出，不把该情况视为模型失败。

## 0.3 Preprocess Design

左右眼索引：

- left eye：37, 38, 39, 40, 41, 42
- right eye：43, 44, 45, 46, 47, 48

每只眼的设计流程：

1. 用 6 个 landmark 计算 tight bbox。
2. `side = max(width, height)`，以 bbox 中心构造正方形 ROI。
3. RGB 输入先转 Y；Y 输入直接使用。
4. 若 ROI 越出图像边界，在方形 `CV_8UC1` 画布中按对应边填充常量 `114`。
5. 使用 `VpResize_Y_Adapt` resize 到 `input_width x input_height`。
6. 保存 crop 元数据到 `EyeCrop`。

## 0.4 VP Resize Design

EyeStatus 参考 face landmark 的 processor 形式使用：

- `UtilsDomain::CreateVpImgProcessor()`
- `vp_processor->VpResize_Y_Adapt(...)`
- `HB_VP_INTER_LINEAR`

模型侧只切换调用路径，不修改 VP 算子实现。

VP memory 设计：

- `EyeStatusModel` 持有 `m_eyeResizeVpMem`。
- `VpResize_Y_Adapt` 的 `max_size` 固定传 `cv::Size(2160, 2160)`，对齐 face landmark 的固定上限策略。
- `m_eyeResizeVpMem` 首次调用时由 processor 初始化，左右眼复用同一块 VP memory。
- 模型层不再根据 eye crop 动态 max side reset VP memory。

## 0.5 Output Design

当前输出写入：

- `eyeResult.leftEye`
- `eyeResult.rightEye`
- `eyeResult.leftEyeScore`
- `eyeResult.rightEyeScore`
- `eyeResult.leftEyeCrop`
- `eyeResult.rightEyeCrop`

标签映射：

- 0 -> `eyeClose`
- 1 -> `eyeNarrow`
- 2 -> `eyeShelter`
- 3 -> `eyeOpen`

## 0.6 Non-goals

- 不修改 `VpResize_Y_Adapt` 或 `VpRoiResize_Y` 算子。
- 不在 EyeStatus 内新增 padding 奇偶兜底。
- 不调整 face track / landmark 模型。
- 不在本设计中声明分类精度改善。
- 不把 SDK Integration 的通用部署事项放入 EyeStatus current 组。
