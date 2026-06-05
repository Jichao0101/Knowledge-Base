---
type: project_entry
status: active
project: DMS
scope: DMS 项目区模块入口索引；只负责导航和当前结构状态说明，不替代各模块 current 文档。
updated_at: 2026-06-05
---

# 1 DMS 项目总览

本文件是 `02_Projects/DMS` 的项目级入口。模块当前事实以各模块 `overview_current` 或对应主题文档为准。

## 1.1 模块入口

| 模块 | 默认入口 | current 状态 | 说明 |
|---|---|---|---|
| Tracking | [[02_Projects/DMS/04_Tracking/tracking_overview_current]] | verified / partial recoverability | 已建立完整 current 文档组和默认恢复顺序 |
| SDK Integration | [[02_Projects/DMS/06_SDK_Integration/sdk_overview_current]] | draft / created_but_not_fully_verified | 已建立 current 文档组，尚未完成运行态验证 |
| EyeStatus | [[02_Projects/DMS/08_EyeStatus/eyestatus_overview_current]] | draft_verified_project / single_pass_recoverable=false | 已建立 current 文档组，尚未完成独立可恢复性验证 |
| FaceID | [[02_Projects/DMS/09_FaceID/overview_current]] | verified / partial recoverability | 已有 current 文件组、默认读取顺序和 recoverability 缺口说明 |
| Model Training | [[02_Projects/DMS/03_Model_Training/模型训练模块索引]] | module index / no current group | 已补模块索引，尚未形成标准 current 文档组 |
| Postprocess | [[02_Projects/DMS/05_Postprocess/后处理模块索引]] | module index / no current group | 已补模块索引，尚未形成标准 current 文档组 |
| State Machine | [[02_Projects/DMS/07_State_Machine/状态机模块索引]] | module index / no current group | 已补模块索引，尚未形成标准 current 文档组 |
| Vehicle Config | [[02_Projects/DMS/2026-06-02-车型配置增量读取与双路径车型来源]] | single record | 单次增量记录 |

## 1.2 推荐读取顺序

理解 DMS 当前项目结构时：

1. 先读本文件。
2. 再进入目标模块默认入口。
3. 若模块存在 current 文档组，按模块 `overview_current` 内的默认恢复顺序读取。
4. 若模块没有 current 文档组，只读取与任务直接相关的方案、实验或记录文件。
5. `Current Maintenance Records` 仅用于追溯具体修复、验证、review 和 writeback 决策。

## 1.3 current 文档组覆盖情况

| 状态 | 模块 |
|---|---|
| current 组较完整 | Tracking |
| current 组已创建但未完全验证 | SDK Integration, EyeStatus |
| current 组已有默认入口但仍是 partial recoverability | FaceID |
| 已补模块索引但尚未标准化为 current 组 | Model Training, Postprocess, State Machine |

## 1.4 待修复项

1. 判断 Model Training 是否需要 current creation；该目录内容量大且包含增量更新规则、实验记录和训练方案。
2. 判断 Postprocess、State Machine 是否只需保留项目记录，还是需要模块级 current 文档组。
3. 把后续新增记录写入对应模块入口或 `Current Maintenance Records`，避免继续在模块根目录堆叠无入口记录。
