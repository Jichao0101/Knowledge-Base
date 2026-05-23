# 1 EyeStatus crop VP 与疲劳兜底修复记录

- 状态：implemented
- 日期：2026-05-23
- 代码仓：`/home/jichao/dms`
- 训练侧参考：`eyestatus_gpu:/workspace/src/stage_d_export_rois.py`、`eyestatus_gpu:/workspace/src/train_rois.py`
- 验证：`bash scripts/compile_j6b.sh` 编译通过

## 1.1 背景

本次修复针对 `eye_status_model` 三个问题：

1. `cropEye128` 先构造完整 padded square，再 `copyTo`，最后走 VP resize，存在额外 CPU/内存拷贝。
2. VP ROI resize 有最小输入尺寸限制，需要在调用 VP 前补足到至少 32。
3. 眼状态模型失败时提前插入默认 `EyeStatusResult`，形成 `eyeOpen + score=0`，疲劳后处理按 `1 - score` 得到闭眼置信度 1。

## 1.2 训练侧语义

训练 ROI 生成流程为：

- 以眼部 bbox 中心构造正方形 ROI。
- 越界区域使用常量 padding，默认 `pad_value=114`。
- Stage D 输出原尺度 ROI，训练加载时再 `Resize((128, 128))`。

因此推理侧修复保持“正方形 ROI + 常量 114 padding + resize 到 128”的协议，不改为边界 clamp。

## 1.3 代码改动

### 1.3.1 `source/models/eye_status_model.cpp`

- 移除 `Run` 中推理成功前的默认 map 插入：
  - 删除 `(void)m_atomicResult->m_eyeStatusResultMap[trackId];`
  - 只在 `PostProcess` 成功后通过 `m_eyeStatusResultMap[m_trackId]` 写入结果。
- `cropEye128` 不再创建完整 `side_i x side_i` 方图，也不再 `copyTo`。
- 新增 `kVpMinInputSize = 32`，在 VP ROI resize 前将正方形边长补足到至少 32。
- 直接调用 `VpRoiResize_Y(srcY, res, ..., roi, roi_resize_param)`。
- `roi_resize_param` 使用 `HB_VP_INTER_LINEAR` 和 padding 值 `{114, 114, 114, 0}`。
- `EyeCrop` 记录实际送入 VP 的正方形 ROI 与 padding。

### 1.3.2 `source/fuse_algos/fatigue_algorithm.cpp`

- 检查 `computeClosedConfidenceFromStatus` 返回值。
- 若 eye status 无效，闭眼置信度置 0，避免无效结果进入疲劳滤波。

## 1.4 验证结果

- 初始按用户给定命令 `bash script/compile_j6b.sh` 执行失败，原因是仓库实际脚本目录为 `scripts/`。
- 实际执行 `bash scripts/compile_j6b.sh`。
- 编译通过，最终输出：
  - `[100%] Linking CXX executable sdk`
  - `[100%] Built target sdk`

## 1.5 边界

- 未修改 VP 算子实现。
- 未做板端验证。
- 未改写 current 文档组。
- 当前仓库中 `scripts/compile_j6b.sh` 已有非本次修改的工作区差异，本次未处理。

## 1.6 风险与后续

- VP ROI 坐标按现有 `J6bVpProcessor::VpRoiResize_Y` 的 inclusive ROI 语义传入，即 `right = square_x2 - 1`、`bottom = square_y2 - 1`。
- 本次只验证编译，不覆盖板端实际 ROI 越界 padding 行为。
- 若后续需要验证视觉一致性，应补充训练侧 Python crop 与推理侧 VP ROI resize 的样例对齐测试。
