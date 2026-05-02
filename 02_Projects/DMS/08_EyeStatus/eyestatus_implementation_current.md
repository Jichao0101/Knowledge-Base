---
title: EyeStatus Implementation Current
summary: EyeStatus 当前实现事实文档，记录代码入口、关键函数、数据流、VP memory 策略和输出落点。
status: draft_verified_project
doc_role: current
truth_role: current
current_kind: implementation
lifecycle_state: active
default_entry: false
retrieval_priority: current
related_code:
  - /home/jichao/dms/include/models/eye_status_model.h
  - /home/jichao/dms/source/models/eye_status_model.cpp
  - /home/jichao/dms/source/utils/visualizer.cpp
sources:
  - /home/jichao/dms/include/models/eye_status_model.h
  - /home/jichao/dms/source/models/eye_status_model.cpp
  - /home/jichao/dms/source/utils/visualizer.cpp
  - 02_Projects/DMS/08_EyeStatus/EyeStatus_VpResize_Y_Adapt_板端验证记录.md
scope: 适用于恢复 EyeStatus 当前代码实现事实，不替代代码审查。
risks:
  - 本文档基于当前代码静态读取和最近一次板端验证记录。
updated_at: 2026-05-02
---

## 0.1 Code Entry

主类：

- `ModelsDomain::EyeStatusModel`

关键文件：

- `/home/jichao/dms/include/models/eye_status_model.h`
- `/home/jichao/dms/source/models/eye_status_model.cpp`

主要函数：

- `Init`
- `Run`
- `PreProcess(shared_ptr<ImageData>&, const std::vector<Point2D>&)`
- `cropEye128`
- `Inference`
- `PostProcess`
- `reset`
- `loadConfigFromJson`

## 0.2 Run Flow

当前 `Run` 流程：

1. 清空 `m_eyeStatusResultMap`。
2. 从 `m_faceTrackResultMap` 中找到 driver face track id。
3. 用 track id 查找 landmark。
4. landmark 数不足 68 时跳过。
5. 执行 `PreProcess`。
6. 执行 `Inference`。
7. 执行 `PostProcess`。
8. 写回 `AtomicResult` 并 reset 临时状态。

## 0.3 Preprocess Implementation

当前 `PreProcess` 为左右眼分别调用 `cropEye128`：

- left indices：`{37, 38, 39, 40, 41, 42}`
- right indices：`{43, 44, 45, 46, 47, 48}`

`cropEye128` 关键实现事实：

- 检查输入图像和 index。
- 检查目标尺寸必须是正方形。
- 计算 6 点 tight bbox。
- `side = max(w, h)`。
- 将输入转为 Y：
  - `CV_8UC1` 直接使用。
  - `CV_8UC3` 使用 `cv::COLOR_RGB2GRAY`。
- 使用 floor/ceil 计算整数 ROI。
- 构造完整方形 `CV_8UC1` 画布。
- 用 `114` 初始化画布。
- 将图像内有效区域 copy 到对应 padding 偏移位置。
- 调用 `VpResize_Y_Adapt` 输出 `128x128`。
- 保存 `EyeCrop` 元数据。

## 0.4 VP Memory Implementation

`EyeStatusModel` 当前持有：

- `std::shared_ptr<VpMemBase> m_eyeResizeVpMem`

当前实现参考 face landmark 的固定 max size 策略复用 VP memory：

- `VpResize_Y_Adapt` 的 `max_size` 固定传 `cv::Size(2160, 2160)`。
- `m_eyeResizeVpMem` 由 `J6bVpProcessor::VpResize_Y_Adapt` 在首次调用时初始化。
- 左右眼复用同一个 `m_eyeResizeVpMem`。
- 模型层不再按动态 `max_vp_side` reset VP memory。

## 0.5 Output Implementation

`PostProcess` 当前：

- 要求 `m_modelOutput.size() == 2`。
- 对每只眼前 4 维输出做 softmax。
- 使用 `argmaxVec` 得到 label。
- 写入 `EyeStatusResult`。
- 日志打印左右眼 logits、label 和 score。

## 0.6 Visualization Implementation

`Visualizer::drawEyeStatus` 当前按 EyeStatus `cropEye128` 的 crop 几何绘制眼框：

- 使用 `EyeCrop.x1/y1/side` 表示原图坐标系下的方形 crop。
- 使用与 `cropEye128` 一致的 `floor/ceil` 计算整数边界。
- 使用 `side_i = max(raw_w, raw_h)` 保持整数 ROI 为正方形。
- 使用 `extra_x/extra_y` 对齐奇偶补齐逻辑。
- 越界时按 crop 流程 clamp 到原图内有效区域绘制，不画不可见 padding 区。
- 颜色仍按 EyeStatus 分类结果区分。

## 0.7 Current Implementation Boundaries

- `m_params.expand_percent` 和 `m_params.vertical_boost` 当前仍读取配置，但当前 crop 路径没有使用它们扩张 ROI。
- 代码注释中保留了 NV12 转换调试片段，但当前正式路径不启用。
- `m_eyeStatusResultMap.clear()` 当前在 `Run` 开始执行，因此本模型每次运行只保留当前帧结果。
