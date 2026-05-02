# 1 EyeStatus 预处理切换 VpResize_Y_Adapt 板端验证记录

- 状态：verified_project_record
- 日期：2026-05-02
- 项目：DMS EyeStatus Deployment
- 代码仓：`/home/jichao/dms`
- 来源：subpower 本次任务工件 `/tmp/subpower-eyestatus-vpresize/`

## 1.1 摘要

本次将 EyeStatus 预处理中的旧 `VpRoiResize_Y` 路径替换为 `vpImgProcessor->VpResize_Y_Adapt`。实现参考 `face_landmark_model` 的 VP resize 调用方式，但未修改 VP 算子本身。

EyeStatus crop 逻辑保持为方形 eye crop：先构造 `CV_8UC1` 方形输入，只有 ROI 越出图像边界时才使用常量 padding，然后 resize 到模型输入尺寸。未新增奇偶 padding 兜底。

## 1.2 代码变更

- `/home/jichao/dms/include/models/eye_status_model.h`
  - 增加 EyeStatus resize 用的 `std::shared_ptr<VpMemBase>` 缓存。
- `/home/jichao/dms/source/models/eye_status_model.cpp`
  - `cropEye128` 构造方形 Y crop。
  - 删除 EyeStatus 内的 `VpRoiResize_Y` resize 路径。
  - 改为调用 `CreateVpImgProcessor()->VpResize_Y_Adapt(...)`。
  - `max_size` 固定传 `cv::Size(2160, 2160)`，参考 face landmark 的固定上限策略。
  - VP resize memory 首次初始化后复用，模型层不再根据 eye crop 动态 max side reset。

## 1.3 验证

本地编译：

- 命令：`bash scripts/compile_j6b.sh`
- 结果：通过
- 产物：`/home/jichao/dms/build/main/sdk`
- 备注：脚本已执行 `scp main/sdk root@192.168.2.10:/userdata/dms/sdk`

板端验证：

- 请求命令：`cd /userdata/dms && bash run.sh`
- 实际执行：`cd /userdata/dms && sh run.sh`
- 原因：板端无可执行 `bash`
- 结果：EyeStatus 路径通过；后续因输入源耗尽出现重复 `Can not get image from J6M PIC`，已中断运行

关键日志证据：

- `EyeStatus:J6bVpProcessor::VpResize_Y_Adapt cost run time`
- `EyeStatus::PreProcess cost run time`
- `EyeStatus::Inference cost run time`
- `EyeStatus::PostProcess cost run time`
- `EyeStatus logits ... pred=open`

未观察到：

- `cropEye128: VpResize_Y_Adapt failed`

## 1.4 结论

本次成功标准“板端日志 eye status 模型不报错”已满足。当前记录属于 DMS EyeStatus 部署实现与验证记录，尚未抽象为通用知识，因此保留在项目区，不提升到正式知识区。

## 1.4.1 延迟复查：固定 max size 与 face landmark 对比

复查背景：

- 观察到 EyeStatus 左眼 resize 偶发高耗时。
- 为排除动态 max side 过小导致重新分配内存的可能，EyeStatus 已改为固定 `cv::Size(2160, 2160)`。
- 重新编译 `bash scripts/compile_j6b.sh` 并部署 `/home/jichao/dms/build/main/sdk` 到 `root@192.168.2.10:/userdata/dms/sdk`。
- 板端运行日志：`/tmp/eyestatus_latency_maxsize2160.log`。

同一日志窗口统计，单位为 us：

| 指标 | count | min | p50 | p90 | p95 | p99 | max | mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| EyeStatus resize, 含首帧 | 120 | 521 | 754 | 2386 | 3873 | 6373 | 8619 | 1251.95 |
| EyeStatus resize, 去首个调用 | 119 | 521 | 754 | 2297 | 3808 | 5967 | 8619 | 1208.92 |
| face_landmark resize, 含首帧 | 60 | 721 | 996 | 2567 | 4077 | 10321 | 35593 | 2076.08 |
| face_landmark resize, 去首个调用 | 59 | 721 | 996 | 2546 | 3450 | 4255 | 10321 | 1508.00 |

结论：

- EyeStatus 固定 `2160x2160` 后仍存在运行期左眼 resize 尾延迟，说明不是动态 max side 过小导致的反复分配。
- face_landmark 在同一日志窗口也存在 VP resize 尾延迟，且首次调用受 `VpMem_Y init success` 和首个 resize op 影响更明显。
- EyeStatus 的最高运行期样本主要由单次 `resize_op` 变慢带动，例如 line 13281 附近 `resize_op` 7880us、EyeStatus resize 8619us。
- 部分高耗时附近出现 `Wait for model result`、`fill 4, available 0`、`Drop one image since Pipeline is too slow!`，更符合 VP 调度或整体 pipeline 压力下的尾延迟，而不是 EyeStatus 个例。

## 1.5 风险与边界

- 板端 `bash run.sh` 不可用，验证使用 `sh run.sh`。
- 板端存在与本次 EyeStatus 改动无关的日志，如 ZMQ bind 失败、部分其他模型 ROI resize 报错、后续 J6M PIC 图像源耗尽。
- 本记录不声明这些无关日志已修复。
- 未修改 VP 算子实现。
