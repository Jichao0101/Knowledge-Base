---
type: project_entry
status: active
project: DMS
scope: DMS 项目区模块入口索引；只负责导航和内容简介，不替代各模块 current 文档。
updated_at: 2026-07-13
---

# 1 DMS 项目总览

本文件是 `02_Projects/DMS` 的项目级入口。模块当前事实以各模块 `overview_current` 或对应主题文档为准。

## 1.1 模块入口

| 模块 | 默认入口 | 内容简介 | 读取提示 |
|---|---|---|---|
| Tracking | [[02_Projects/DMS/04_Tracking/tracking_overview_current]] | 多目标跟踪、head-first 身份主线、body/face/hand 关联和验证边界 | 按 current 恢复顺序读取 |
| SDK Integration | [[02_Projects/DMS/06_SDK_Integration/sdk_overview_current]] | SDK 两条使用路径、动态库接口、回灌入口、DMS 回灌方案、Pipeline/Fuse 和硬件加速落点 | 按 current 恢复顺序读取 |
| EyeStatus | [[02_Projects/DMS/08_EyeStatus/eyestatus_overview_current]] | 睁闭眼模型部署态、眼部 crop、VP resize、推理输出和验证证据 | 按 current 恢复顺序读取 |
| FaceID | [[02_Projects/DMS/09_FaceID/overview_current]] | A 核 FaceID 录入、登录、解绑、删除、check、恢复出厂设置和本地特征库 | 按 current 恢复顺序读取 |
| Issue Analysis Skill | [[02_Projects/DMS/10_Issue_Analysis_Skill/DMS问题分析Skill模块索引]] | 从飞书/Jira/现场数据构建证据包；当前跳过 R 核，A 核已实现全量日志索引和预算化证据选择，后续 Agent review 与受控 Jira 回写尚待完成 | 先读模块索引 |
| Model Training | [[02_Projects/DMS/03_Model_Training/model_training_overview_current]] | 睁闭眼数据构建、输入生成、训练配置、对照实验和增量更新链路 | 按 current 恢复顺序读取 |
| Postprocess | [[02_Projects/DMS/05_Postprocess/后处理模块索引]] | 疲劳驾驶监测后处理、闭眼/哈欠规则、报警条件和头姿兜底修复 | 先读模块索引 |
| State Machine | [[02_Projects/DMS/07_State_Machine/状态机模块索引]] | 事件状态机、报警条件、测试方案和测试 TP | 先读模块索引 |
| Vehicle Config | [[02_Projects/DMS/2026-06-02-车型配置增量读取与双路径车型来源]] | 车型配置增量读取、双路径车型来源和配置兼容记录 | 单记录入口 |

## 1.2 推荐读取顺序

理解 DMS 当前项目结构时：

1. 先读本文件。
2. 再进入目标模块默认入口。
3. 若模块存在 current 文档组，按模块 `overview_current` 内的默认恢复顺序读取。
4. 若模块没有 current 文档组，只读取与任务直接相关的方案、实验或记录文件。
5. `Current Maintenance Records` 仅用于追溯具体修复、验证、review 和 writeback 决策。

## 1.3 结构维护

DMS current 覆盖情况、模块索引状态和待修复项记录在 [[02_Projects/Knowledge-Base/知识库结构审计_current]]。

## 1.4 当前维护摘要

- Tracking 当前事实源为 [[02_Projects/DMS/04_Tracking/tracking_overview_current]] 及其 current 文档组；项目总览不再枚举 Tracking 的历史提交和逐步 writeback。
- 当前 Tracking 代码事实：`DmsTrack::Init/Update` public API 保持不变；`Update` 以 face/head identity 为主线，按 profile gate 执行 driver-bound body evidence 和 hand evidence；2m profile 关闭并清理 body/hand tracking cache；hand 内部 body 输入来自 body phase 返回的 finalized driver body evidence snapshot。
- 当前验证边界：profile split、driver-bound body evidence、body-to-hand snapshot 和三笔 hand lambda 可读性整理已有本地编译与独立 review 记录；runtime replay、单元测试、代表性视频集和区域级唯一性验证仍未闭合。
- 历史方案、superseded lambda 路线、整体架构评审和每步验证命令详见 `02_Projects/DMS/04_Tracking/Current Maintenance Records/` 与 `02_Projects/DMS/04_Tracking/subpower_runs/`。
- SDK Integration 当前补充记录：[[02_Projects/DMS/06_SDK_Integration/DMS回灌方案]] 记录 `start_stage=model` 已实现的模型阶段回灌路径，以及 README 中 `start_stage=postprocess` 预留但暂不支持的边界；该记录仅为源码静态整理，未完成 x86 或板端运行验证。
- Issue Analysis Skill 当前进入阶段二：A 核确定性分析准备层已实现全量物理行索引、签名 census、多锚点与跨线程 correlation 选择、字符预算、hash/输出隔离和手工规则版本提示；36 项仓库测试通过。查询规则只能通过修改 Skill 手工更新，普通 case 不读取源码；真实日志端到端、Agent review、结论合成和 Jira 回写仍未闭环。
