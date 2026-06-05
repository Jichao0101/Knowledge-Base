---
type: project_current
status: created_but_not_fully_verified
project: DMS
module: Model Training
current_kind: design
sources:
  - 02_Projects/DMS/03_Model_Training/睁闭眼模型训练方案.md
  - 02_Projects/DMS/03_Model_Training/睁闭眼分类模型对照实验设计.md
updated_at: 2026-06-05
---

# Model Training Design Current

## 1 设计目标

当前睁闭眼训练方案要同时满足：

- 训练输入与部署输入尽可能一致。
- 数据版本、split 版本、输入版本、训练版本和评测版本严格绑定。
- 增量数据加入后，历史 benchmark 不漂移。
- 输入实验、loss 实验与 backbone 实验可归因。
- 误分类可追溯至原始数据与输入生成链路。
- 正式 baseline 以量化表现优先，而不是仅以 FP32 最优为准。

## 2 非目标

- 不在当前方案中引入时序约束、覆盖度约束或受约束分配。
- 不把 `Deploy Eval` 作为正式输出口径。
- 不把 `RectROI + ConstPad` 作为当前正式主线输入。
- 不将本训练方案直接泛化为其他模型任务的通用规范。

## 3 关键取舍

- split 使用 `group_id = f(person_id)`，其他信息只保留为 meta，不参与 split。
- 评测 group 候选只使用 `total_samples >= N_min`，但 `N_min` 尚未固定。
- 正式输入主线切换为 `const padding`，避免 reflect/replicate padding shortcut。
- 当前部署对齐基线为 `SquareCrop(k=1.0) + OOB Const Padding`。
- `SquareCrop(k=1.8)` 只作为 narrow 召回复核分支，不作为默认部署输入。
- `eye_narrow` 与 `eye_occluded` 的瓶颈机制不同，必须分治分析。

## 4 实验设计

实验按阶段推进：

1. T1：MobileNetV2 基线重建。
2. T2：Loss 单变量对照。
3. T3：输入构造单变量对照。
4. T4：联合验证。

只有通过阶段 gate 的方案才允许进入下一阶段。

## 5 设计风险

- 若 `N_min` 不固定，评测候选集行为仍依赖外部参数。
- 若只看 FP32 指标，可能选到量化后不可用的 baseline。
- 若输入策略变更不绑定版本，后续实验无法归因。
- 若增量更新不保证当前全量视图，历史 benchmark 会被污染。
