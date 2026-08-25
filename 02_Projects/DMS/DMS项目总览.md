---
type: project_entry
status: active
project: DMS
scope: DMS 项目区模块入口索引；只负责导航和内容简介，不替代各模块 current 文档。
updated_at: 2026-08-25
---

# 1 DMS 项目总览

本文件是 `02_Projects/DMS` 的项目级入口。模块当前事实以各模块 `overview_current` 或对应主题文档为准。

## 1.1 模块入口

| 模块 | 默认入口 | 内容简介 | 读取提示 |
|---|---|---|---|
| Tracking | [[02_Projects/DMS/04_Tracking/tracking_overview_current]] | 多目标跟踪、face-first 身份主线、Face/Body/Hand 关联和验证边界 | 按 current 恢复顺序读取 |
| SDK Integration | [[02_Projects/DMS/06_SDK_Integration/sdk_overview_current]] | SDK 两条使用路径、动态库接口、回灌入口、DMS 回灌方案、Pipeline/Fuse 和硬件加速落点 | 按 current 恢复顺序读取 |
| EyeStatus | [[02_Projects/DMS/08_EyeStatus/eyestatus_overview_current]] | 睁闭眼模型部署态、眼部 crop、VP resize、推理输出和验证证据 | 按 current 恢复顺序读取 |
| FaceID | [[02_Projects/DMS/09_FaceID/overview_current]] | A 核 FaceID 录入、登录、解绑、删除、check、恢复出厂设置和本地特征库 | 按 current 恢复顺序读取 |
| Issue Analysis Skill | [[02_Projects/DMS/10_Issue_Analysis_Skill/DMS问题分析Skill模块索引]] | 从飞书/Jira/现场数据构建证据包；R 核规则 reference 已就绪但 analyser 尚未实现且运行时仍跳过，已完成首个真实 case 的 A 核准备、Agent review、受约束结论和中文 Jira 评论闭环 | 先读模块索引 |
| Model Training | [[02_Projects/DMS/03_Model_Training/model_training_overview_current]] | 睁闭眼数据构建、输入生成、训练配置、对照实验和增量更新链路 | 按 current 恢复顺序读取 |
| Postprocess | [[02_Projects/DMS/05_Postprocess/后处理模块索引]] | 疲劳驾驶监测后处理、闭眼/哈欠规则、报警条件和头姿兜底修复 | 先读模块索引 |
| State Machine | [[02_Projects/DMS/07_State_Machine/状态机模块索引]] | 事件状态机、报警条件、测试方案和测试 TP | 先读模块索引 |
| Law Test | [[02_Projects/DMS/11_Law_Test/法规测试模块索引]] | DMS 法规测试问题、日志时序、报警等级、测试口径与证据边界 | 先读模块索引 |
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
- 当前 Tracking 主线更新事实以 `feat/ljc/track_0825@b0a8da10` 为准：架构为 face-first；Hand tracking、空侧 acquisition 和 publish 已统一增加面积比、Body 中心/交叠及非主驾竞争归属门禁，四类 legacy map ABI 不变。
- 当前验证边界：提交前同内容构建产物已完成 J6B 全量编译、SDK 校验部署和 `/ota/dump` 999 帧板端回灌；可比窗口保留 241 个 driver-only 输出，并将 non-driver-only/both/none 从 127/7/7 降为 0/0/0。`/ota/TC001`、`/ota/TC004` 不存在，代表性视频集、Body 边界召回、多人重叠、双手交叉/长漏检和水平翻转输入仍未系统性闭合。
- 本轮修复与证据边界见 [[02_Projects/DMS/04_Tracking/Current Maintenance Records/副驾手误关联主驾Hand归属门禁修复与板端回灌验证记录-2026-08-25]]；前置 Hand 两阶段与实际左右发布见 [[02_Projects/DMS/04_Tracking/Current Maintenance Records/Hand跟踪与空侧获取分离及实际左右发布映射记录-2026-08-17]]。
- 历史方案、superseded lambda 路线、整体架构评审和每步验证命令详见 `02_Projects/DMS/04_Tracking/Current Maintenance Records/` 与 `02_Projects/DMS/04_Tracking/subpower_runs/`。
- SDK Integration 当前补充记录：[[02_Projects/DMS/06_SDK_Integration/DMS回灌方案]] 记录 `start_stage=model` 已实现的模型阶段回灌路径，以及 README 中 `start_stage=postprocess` 预留但暂不支持的边界；该记录仅为源码静态整理，未完成 x86 或板端运行验证。
- Issue Analysis Skill 当前处于阶段三验证：`ADASL2-1565` 已完成在线飞书、真实 Jira/Data、Evidence Package、308/308 行 A 核准备、Agent review、证据不足结论和真实 Jira 评论闭环；R 核规则已拆分为解释性 reference 与机器可消费 strategy，但 analyser、输入适配和结果合同仍未实现，运行时继续 `skipped/r_core_analyser_not_available`。Skill 瘦身与 R 核 reference 分层后全量 55 项测试通过；多 case、完整 DMS 状态链、并发去重和 recoverability verification 仍未闭环。
