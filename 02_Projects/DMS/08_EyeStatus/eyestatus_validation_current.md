---
title: EyeStatus Validation Current
summary: EyeStatus 当前验证状态文档，记录编译、板端运行、已证明事实、环境问题和未覆盖项。
status: draft_verified_project
doc_role: current
truth_role: current
current_kind: validation
lifecycle_state: active
default_entry: false
retrieval_priority: current
related_code:
  - /home/jichao/dms/source/models/eye_status_model.cpp
sources:
  - 02_Projects/DMS/08_EyeStatus/eyestatus推理前处理对齐训练流程记录.md
  - 02_Projects/DMS/08_EyeStatus/EyeStatus_VpResize_Y_Adapt_板端验证记录.md
scope: 适用于判断 EyeStatus 当前有哪些验证证据成立，哪些仍需补充。
risks:
  - 板端验证后段出现输入源耗尽，不能作为长时稳定性验证。
updated_at: 2026-05-02
---

## 0.1 Evidence Status

### 0.1.1 已验证

- `git diff --check` 通过。
- `bash scripts/compile_j6b.sh` 通过。
- 编译产物为 `/home/jichao/dms/build/main/sdk`。
- 编译脚本已将 `sdk` 部署到 `root@192.168.2.10:/userdata/dms/sdk`。
- 板端使用 `sh run.sh` 覆盖到 EyeStatus。
- 板端日志出现：
  - `EyeStatus:J6bVpProcessor::VpResize_Y_Adapt cost run time`
  - `EyeStatus::PreProcess cost run time`
  - `EyeStatus::Inference cost run time`
  - `EyeStatus::PostProcess cost run time`
  - `EyeStatus logits ... pred=open`
- 捕获日志中未观察到：
  - `cropEye128: VpResize_Y_Adapt failed`
- 延迟复查已覆盖 EyeStatus 与 face_landmark 的同窗口 resize 分位数对比。
- EyeStatus 固定 `cv::Size(2160, 2160)` 后仍存在 resize 尾延迟，排除动态 max side 过小导致反复分配为主因。
- face_landmark 同窗口也存在 resize 尾延迟，说明该现象不是 EyeStatus 个例。

### 0.1.2 环境事实

- 用户给定的 `bash run.sh` 在板端不可用，原因是板端无可执行 `bash`。
- 实际验证命令为 `cd /userdata/dms && sh run.sh`。
- 板端后段出现重复 `Can not get image from J6M PIC`，运行被中断。
- 板端还存在 ZMQ bind、其他模型 ROI resize 等与本次 EyeStatus 改动无关的日志。

## 0.2 Current Review Conclusion

当前结论：

- EyeStatus 预处理已从旧 `VpRoiResize_Y` 路径切换到 `VpResize_Y_Adapt`。
- 板端已证明 EyeStatus 当前预处理、推理、后处理链路可以跑通。
- 本次成功标准“板端日志 eye status 模型不报错”已满足。
- 偶发 resize 高耗时更可能来自 VP 调度或整体 pipeline 压力；不是 EyeStatus 误用算子，也不是模型层动态 max size 过小导致的反复分配。

不能声明：

- EyeStatus 分类精度已改善。
- 全量视频或长时运行已验收。
- 板端其他模块报错已修复。
- 输入源耗尽问题已修复。

## 0.3 Required Next Verification

后续若继续推进 EyeStatus 部署质量，建议补：

1. 连续视频或固定 replay 的长时运行。
2. 含越界 eye crop 的样本，确认 `pad_left/top/right/bottom` 只在越界时非零。
3. 与训练侧 ROI dump 的像素级抽样对照。
4. 对 `input_channels=3` 与当前 Y-only 输入路径的模型契约确认。
5. 如果恢复使用 `bash run.sh`，需先确认板端 shell 环境或改运行脚本入口。

## 0.4 Current Boundary

本验证文档只记录 EyeStatus 当前部署链路验证状态。它不承接 SDK Integration 的通用部署验证，也不承接 fatigue fuse 或 camera source 的长期稳定性验收。
