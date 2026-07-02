---
type: project_current
status: created_but_not_fully_verified
project: DMS
module: Model Training
current_kind: spec
sources:
  - 02_Projects/DMS/03_Model_Training/睁闭眼模型训练方案.md
  - 02_Projects/DMS/03_Model_Training/睁闭眼分类模型对照实验设计.md
updated_at: 2026-06-05
---

# 1 Model Training Spec Current

## 1.1 数据与 Split 契约

- split 主键：`group_id = f(person_id)`。
- `val/test` 候选门槛：`total_samples >= N_min`。
- 冻结 benchmark 后，历史 `val/test` group 不得因增量数据回流训练集。
- 数据、split、输入、训练和评测版本必须绑定。

## 1.2 Stage 契约

| Stage | 目标 | 关键要求 |
|---|---|---|
| A | 扫描源目录，生成 source manifest | 目录级增量扫描；复用目录必须从历史 manifest 回填旧 items；历史 items 缺失时触发补偿重扫 |
| B | 复制数据到私人目录 | 目录粒度增量复制；源目录未变化时跳过；内容变化时只复制新增或变化文件 |
| C | 生成 final manifest 与 split | 继承冻结 benchmark；输出当前全量 source_manifest 对应视图 |
| D | 导出 ROI 数据集 | 输出目录必须与 `stage_d_roi_manifest.json` 表示同一份当前视图；清理失效 ROI |
| Train | 训练与评测 | 使用绑定版本的 ROI manifest 和输入协议 |

## 1.3 输入契约

- 当前正式输入：`SquareCrop(k=1.0) + OOB Const Padding`。
- padding 常量：OOB constant padding。
- 正式评测仅使用 GT 口径。
- ROI 导出必须记录 shortcut 观测字段。
- 训练、量化、部署预处理协议必须版本化并写死。

## 1.4 实验 Gate

T1 进入 T2/T3 的条件：

- MobileNetV2 FP32 基线稳定。
- 后续若量化链路接通，baseline 选择优先看 `Quant Macro-F1`。

T2 结束条件：

- Loss 对照完成后，不建议直接替换 T1 CE baseline。
- `weighted_ce t0.75 clip[0.6,1.8]` 仅作为辅助复核分支。
- Focal Loss 暂不进入 T3 主线。

T3 结束条件：

- `k=1.0` 保持当前正式输入主线。
- `k=1.4 / 1.8 / 2.2` 不替代默认部署输入。

## 1.5 验证契约

最低验证应覆盖：

- Stage A 增量复用与历史 items 回填。
- Stage A 历史 manifest 缺失时自愈重扫。
- Stage D 输出目录与 manifest 当前视图一致。
- T1 训练后立即执行 test-only，结果写入对应 run 的 `test_fp32`。
- T2/T3 对照实验使用统一测试口径。
- 真实业务数据 A->B->C->D->Train 端到端回归。
