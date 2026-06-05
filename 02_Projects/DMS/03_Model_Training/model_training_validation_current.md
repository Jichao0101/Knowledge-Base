---
type: project_current
status: created_but_not_fully_verified
project: DMS
module: Model Training
current_kind: validation
sources:
  - 02_Projects/DMS/03_Model_Training/睁闭眼分类模型对照实验设计.md
  - 02_Projects/DMS/03_Model_Training/睁闭眼增量更新策略实现同步记录.md
  - 02_Projects/DMS/03_Model_Training/T1训练测试联动脚本调整记录.md
updated_at: 2026-06-05
---

# Model Training Validation Current

## 1 已验证事实

- Stage A 合成增量用例验证已完成。
- Python 语法、shell 语法和脚本 diff 已检查。
- Stage A 已补历史 manifest 缺失时的自愈重扫逻辑。
- Stage D 已补清理失效 ROI 的逻辑。
- T1 训练脚本已调整为训练完成后立即执行 test-only。

## 2 实验结果摘要

T1：

- 当前 T1 CE baseline 可作为 T2/T3 的对照锚点。
- T1 对比锚点 `t1_mbv2_lr1e-3_wd0_emaoff` 的 `test_fp32` Macro-F1 为 `0.8324`，Acc@1 为 `0.9115`。

T2：

- Weighted CE 对 `eye_occluded` 有轻微信号，但整体没有稳定超过 T1。
- Focal Loss 暂不进入 T3 主线。
- Label Smoothing 不支持“过置信是主因”的判断。
- T3 主线继续使用 T1 CE baseline。

T3：

- `SquareCrop(k=1.0) + OOB Const Padding` 仍是正式输入主线。
- `k=1.4 / 1.8 / 2.2` 均未超过 T3 `k=1.0` 的整体 Macro-F1 与 Acc@1。
- `k=1.8` 对 narrow 有局部改善，但会污染 closed 边界，不作为默认部署输入。

## 3 未验证项

- `N_min` 的正式数值未固定。
- 未用真实历史 `stage_c_group_registry.json` 完成 Stage C 增量更新验证。
- 未用同一批增量数据分别验证更新 benchmark 与冻结 benchmark。
- 未完成真实 extract_data 目录下 A->B->C->D->Train 端到端回归。
- 未完成量化链路下的最终 baseline 选择。

## 4 Recoverability 结论

本组 current 能恢复当前训练主线、设计取舍、stage 契约、实现入口和验证边界，但尚未完成独立 recoverability verification。当前状态保持 `created_but_not_fully_verified`，不得声明 `single_pass_recoverable: true`。
