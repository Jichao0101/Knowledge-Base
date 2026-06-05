---
type: project_current
status: created_but_not_fully_verified
project: DMS
module: Model Training
current_kind: implementation
sources:
  - 02_Projects/DMS/03_Model_Training/睁闭眼增量更新策略实现同步记录.md
  - 02_Projects/DMS/03_Model_Training/T1训练测试联动脚本调整记录.md
updated_at: 2026-06-05
---

# Model Training Implementation Current

## 1 代码与脚本入口

| 目的 | 路径 |
|---|---|
| Stage A 扫描 | `/home/jichao/EyeStatusModel/src/stage_a_scan_blink.py` |
| Stage B 复制 | `/home/jichao/EyeStatusModel/src/stage_b_copy_data.py` |
| Stage C manifest | `/home/jichao/EyeStatusModel/src/stage_c_build_final_manifest.py` |
| Stage D ROI 导出 | `/home/jichao/EyeStatusModel/src/stage_d_export_rois.py` |
| 训练入口 | `/home/jichao/EyeStatusModel/src/train_rois.py` |
| Stage A 脚本 | `/home/jichao/EyeStatusModel/scripts/stage_a_scan_blink.sh` |
| Stage B 脚本 | `/home/jichao/EyeStatusModel/scripts/stage_b_copy_data.sh` |
| Stage C 脚本 | `/home/jichao/EyeStatusModel/scripts/stage_c_build_final_manifest.sh` |
| Stage D 容器脚本 | `/workspace/scripts/stage_d_export_rois.sh` |
| 训练容器脚本 | `/workspace/scripts/train_rois.sh` |
| T1 训练 grid | `/workspace/scripts/t1_train_grid.sh` |
| T1 test best | `/workspace/scripts/t1_test_best.sh` |

## 2 关键产物

- `stage_a_scan_state.json`
- `stage_a_source_manifest.json`
- `stage_c_group_registry.json`
- `stage_d_roi_manifest.json`
- `train/val/test` ROI 目录
- 训练 run 目录
- `test_fp32/`
- `test_summary.json`
- 全量 trace 文件

## 3 当前实现语义

- Stage A 增量扫描后应产出“全量当前视图”，不只输出本轮新增目录。
- Stage A 对被复用目录从历史 manifest 回填旧 items。
- Stage A 若发现可复用目录在历史 manifest 中缺失旧 items，应补偿重扫。
- Stage D 不只维护 manifest，还必须清理输出目录中的失效 ROI。
- 训练入口已对齐读取 `stage_d_roi_manifest.json`。
- T1 训练脚本在每个 run 完成后立即检查 `best.pth` 并执行 test-only。
- T1 测试结果写入 `${run_dir}/test_fp32/`，避免覆盖训练阶段 `hparams.json`。

## 4 已知实现风险

- `N_min` 仍未固定为具体数值。
- Stage C 仍保留对历史 `pending_eval` 记录的兼容读取。
- 当前记录确认脚本级和合成增量用例验证，但真实业务数据全链路回归仍未完成。
