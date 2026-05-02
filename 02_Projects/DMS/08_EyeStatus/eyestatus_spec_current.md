---
title: EyeStatus Spec Current
summary: EyeStatus 当前可执行规范，定义输入契约、预处理契约、推理后处理契约、配置契约和验证契约。
status: draft_verified_project
doc_role: current
truth_role: current
current_kind: spec
lifecycle_state: active
default_entry: false
retrieval_priority: current
related_code:
  - /home/jichao/dms/include/models/eye_status_model.h
  - /home/jichao/dms/source/models/eye_status_model.cpp
  - /home/jichao/dms/etc/eye_status_model.json
sources:
  - 02_Projects/DMS/08_EyeStatus/eyestatus_design_current.md
  - 02_Projects/DMS/08_EyeStatus/eyestatus_implementation_current.md
  - 02_Projects/DMS/08_EyeStatus/eyestatus_validation_current.md
scope: 适用于后续修改 EyeStatus 代码时作为默认规范输入。
risks:
  - 本规范记录当前部署态，不替代训练数据协议文档。
updated_at: 2026-05-02
---

## 0.1 Input Contracts

- 必须只处理 driver face track。
- driver face track 取自 `m_faceTrackResultMap` 中 `stablePersonType == DRIVER` 的 track id。
- 必须用相同 track id 从 `m_landmarkResultMap` 获取 68 点 landmark。
- landmark 少于 68 点时必须跳过 EyeStatus，不应继续构造 crop。
- 输入图像必须是 `CV_8UC1` 或 `CV_8UC3`。

## 0.2 Preprocess Contracts

- 左右眼分别处理，每只眼产生一个 `128x128` 模型输入。
- 左右眼索引固定为：
  - left：37-42
  - right：43-48
- 每只眼使用 6 点 tight bbox。
- ROI 必须是以 eye bbox 中心为中心的正方形。
- padding 只允许用于图像越界区域。
- padding 值固定为 `114`。
- RGB 输入必须先转 Y 后再进入 VP resize。
- EyeStatus 当前 resize 路径必须是 `vp_processor->VpResize_Y_Adapt(...)`。
- 不得在 EyeStatus 模型代码中修改 VP 算子。
- 不得恢复为 EyeStatus 内的 `VpRoiResize_Y` 预处理路径，除非同步更新本组 current 文档和板端验证记录。

## 0.3 Inference Contracts

- 当前推理引擎初始化使用 `DdkManagerHbm` 或 `DdkManagerQnn`，取决于编译宏。
- 每帧 EyeStatus 应对 left/right 两个输入分别推理。
- `m_modelInput.size()` 必须为 2。
- `m_modelOutput` 在推理前必须为空。
- 单眼输出至少包含 `m_params.output_size` 个 float，当前 `output_size=4`。

## 0.4 Postprocess Contracts

- 当前后处理只取前 4 维 logits。
- 对 4 维 logits 做 softmax。
- `argmax` 得到预测标签。
- 输出 `leftEyeScore/rightEyeScore` 为 top1 probability。
- 标签映射固定：
  - 0: close
  - 1: narrow
  - 2: shelter
  - 3: open
- 必须把左右眼 crop 元数据写回 `EyeStatusResult`。

## 0.5 Config Contracts

配置来源固定为：

- `/home/jichao/dms/etc/eye_status_model.json`

当前关键配置：

- `input_width: 128`
- `input_height: 128`
- `output_size: 4`
- `model_path: /model_weight/eye_status_model/J6B/eyestatus_mbv2_128_nv12.hbm`

若后续修改 input size、output class 数或模型路径，必须同步更新本规范、实现文档和验证文档。

## 0.6 Verification Contracts

触及 EyeStatus 预处理时，至少需要：

- `git diff --check`
- `bash scripts/compile_j6b.sh`
- 板端运行覆盖到 EyeStatus：
  - 出现 `EyeStatus:J6bVpProcessor::VpResize_Y_Adapt`
  - 出现 `EyeStatus::PreProcess`
  - 出现 `EyeStatus::Inference`
  - 出现 `EyeStatus::PostProcess`
  - 不出现 `cropEye128: VpResize_Y_Adapt failed`

如果只完成编译而没有板端运行，则验证状态不得标记为 board passed。
