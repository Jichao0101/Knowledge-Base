---
type: project_current
status: created_but_not_fully_verified
project: DMS
module: Model Training
current_kind: overview
lifecycle: creation
default_entry: true
single_pass_recoverable: false
source_inventory:
  - 02_Projects/DMS/03_Model_Training/睁闭眼模型训练方案.md
  - 02_Projects/DMS/03_Model_Training/睁闭眼分类模型对照实验设计.md
  - 02_Projects/DMS/03_Model_Training/睁闭眼增量更新策略实现同步记录.md
  - 02_Projects/DMS/03_Model_Training/T1训练测试联动脚本调整记录.md
updated_at: 2026-06-05
---

# Model Training Overview Current

本组 current 文档恢复 DMS 睁闭眼模型训练当前方案，包括数据构建、输入生成、训练配置、实验阶段、增量更新和验证边界。

## 1 默认恢复顺序

1. [[02_Projects/DMS/03_Model_Training/model_training_overview_current]]
2. [[02_Projects/DMS/03_Model_Training/model_training_design_current]]
3. [[02_Projects/DMS/03_Model_Training/model_training_spec_current]]
4. [[02_Projects/DMS/03_Model_Training/model_training_implementation_current]]
5. [[02_Projects/DMS/03_Model_Training/model_training_validation_current]]

补充来源：

- [[02_Projects/DMS/03_Model_Training/睁闭眼模型训练方案]]
- [[02_Projects/DMS/03_Model_Training/睁闭眼分类模型对照实验设计]]
- [[02_Projects/DMS/03_Model_Training/睁闭眼增量更新策略实现同步记录]]
- [[02_Projects/DMS/03_Model_Training/T1训练测试联动脚本调整记录]]

## 2 当前主题

当前训练主线是睁闭眼分类模型，目标是统一数据构建、输入生成、训练配置、评测协议和误分类分析机制，保证增量数据加入后 benchmark 不漂移，训练输入与部署输入尽可能一致。

## 3 当前结论

- split 主键仅使用 `group_id = f(person_id)`。
- `val/test` 候选仅使用 `total_samples >= N_min` 作为门槛；`N_min` 仍未固定。
- 正式训练输入主线为 `SquareCrop(k=1.0) + OOB Const Padding`。
- 正式评测仅使用 GT 口径。
- MobileNetV2 必须先完成基线重建，再做 loss、输入构造和联合验证。
- baseline 选择应以 `Quant Macro-F1` 为主导指标，而不是只看 FP32。
- Stage A/B/C/D 必须支持增量更新和幂等恢复。
- 冻结 benchmark 后，增量数据不得导致历史测试集样本回流训练集。

## 4 当前文档角色

| 文件 | 角色 |
|---|---|
| `model_training_overview_current.md` | 当前入口、恢复顺序、当前结论 |
| `model_training_design_current.md` | 设计目标、非目标、关键取舍 |
| `model_training_spec_current.md` | 数据、输入、训练、实验和验证契约 |
| `model_training_implementation_current.md` | stage、脚本、路径和产物映射 |
| `model_training_validation_current.md` | 已验证事实、实验结果、未验证项 |

## 5 当前边界

范围内：

- 睁闭眼数据构建。
- ROI 输入生成。
- MobileNetV2 训练与对照实验。
- 增量扫描、复制、manifest、ROI 导出和训练入口对齐。
- 误分类分析与 trace 输出要求。

范围外：

- EyeStatus 板端部署实现。
- 模型量化链路的完整通过结论。
- 其他模型任务的数据构建规范。
- 未完成的真实业务数据 A->B->C->D->Train 端到端回归。

## 6 Recoverability

本组 current 是 creation 场景，尚未完成独立 recoverability verification，因此不得设置 `single_pass_recoverable: true`。
