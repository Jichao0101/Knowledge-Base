---
type: project_entry
status: active
project: DMS
scope: DMS 项目区模块入口索引；只负责导航和内容简介，不替代各模块 current 文档。
updated_at: 2026-06-15
---

# 1 DMS 项目总览

本文件是 `02_Projects/DMS` 的项目级入口。模块当前事实以各模块 `overview_current` 或对应主题文档为准。

## 1.1 模块入口

| 模块 | 默认入口 | 内容简介 | 读取提示 |
|---|---|---|---|
| Tracking | [[02_Projects/DMS/04_Tracking/tracking_overview_current]] | 多目标跟踪、head-first 身份主线、body/face/hand 关联和验证边界 | 按 current 恢复顺序读取 |
| SDK Integration | [[02_Projects/DMS/06_SDK_Integration/sdk_overview_current]] | SDK 两条使用路径、动态库接口、回灌入口、Pipeline/Fuse 和硬件加速落点 | 按 current 恢复顺序读取 |
| EyeStatus | [[02_Projects/DMS/08_EyeStatus/eyestatus_overview_current]] | 睁闭眼模型部署态、眼部 crop、VP resize、推理输出和验证证据 | 按 current 恢复顺序读取 |
| FaceID | [[02_Projects/DMS/09_FaceID/overview_current]] | A 核 FaceID 录入、登录、解绑、删除、check、恢复出厂设置和本地特征库 | 按 current 恢复顺序读取 |
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

## 1.4 近期维护状态

- Tracking 2026-06-15 深模块重新评审：public `Init/Update` 判定为深接口，主要问题是 private header 和内部组织过浅；global body Hungarian 属于未隔离行为变化，hand owner 消失后的 lifecycle 存在高风险缺口。停止继续 `feat/ljc/track_0609`，建议从 `br_develop_forJ6b` 新开 clean branch，不整提交 cherry-pick，仅选择性重做已确认行为。详见 [[02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack深模块重新评审与CleanRefactor规划-2026-06-15]]。
- Tracking 2026-06-15：删除低收益 assignment edge/rejection helper，forbidden edge 改为有限 `1e6f` 并保留 `AssignmentResult`；Body 完成 finalize/projection 拆分，Hand 以单帧 row 收敛 solve/apply/miss 候选域且不引入无下游用途的 view/payload，publish 不再推进 lifecycle。`git diff --check`、`Utils` 和完整 `sdk` 构建通过；独立 review、runtime replay 和板端验证待补。详见 [[02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrackHand短期匹配结果隐藏与miss候选域修复实施前方案-2026-06-13]]。
- Tracking 2026-06-13：完成 DmsTrack 状态源收敛一期，新增单帧只读 `FrameBodyView`，消除 hand 阶段对 `curResult->m_bodyTrackResultMap` 的内部输入依赖，并清理废弃 `m_hasPreviousFrame`。`git diff --check`、直接 `sdk` 目标构建和独立 review 通过；`compile_j6b.sh` 在构建完成后因 strip 不存在的 `main/libsdk.so` 返回 1，未执行 runtime replay 或板端验证。详见 [[02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack状态收敛与输出投影隔离闭环记录-2026-06-13]]。
- Tracking 2026-06-13：完成禁止匹配语义、assignment solver 副作用、Face/Body/Hand gating 和 publish lifecycle 职责收敛；移除 `OptionalCost` 与业务 forbidden-cost sentinel，solver 改为消费预计算 policy matrix，并增加低噪声 rejection 汇总。独立 review、`git diff --check` 和 J6B 编译通过；未新增专项测试，未执行 runtime replay 或板端验证。详见 [[02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack约束语义与Assignment职责收敛闭环记录-2026-06-13]]。
- Tracking：2026-06-09 完成 DmsTrack 首轮内部可读性重构，保持 public API 和既有算法契约；`git diff --check`、J6B 编译和独立 repo review 通过。未执行 runtime replay，板端验证不属于本次范围。
- Tracking Hand Phase 4A：已完成 owner、prediction、cleanup、publish 外围阶段拆分并通过独立 review 与 J6B 编译；first/second pass 和 Hungarian 未改，未执行 runtime replay。
- Tracking 2026-06-11：完成 sentinel 语义分离、`bodyId / handId` 数值继承与独立生命周期边界澄清，以及 Body/Hand 阶段顺序显式化；public API、统一 assignment、四类 map 和算法契约不变。J6B 编译与独立 review 通过，verification 为 conditional pass，未执行 runtime replay 或单元测试。
- Tracking 2026-06-12：修复 2m 回灌中主驾遮挡后后排 face/head 被误跟踪为主驾的问题；driver face 选择拒绝稳定 BACK_PASSENGER，size scoring 改为变小强惩罚、变大增益，preferred anchor 配置化。J6B 编译通过，板端二次回灌 `face=1` driver select 为 0 次，本问题样本闭环；代表性视频集仍未全量验收。
