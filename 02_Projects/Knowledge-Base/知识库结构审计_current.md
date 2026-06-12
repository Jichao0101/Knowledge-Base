---
type: structure_audit
status: active
scope: 记录知识库结构化、current 标准化、总览内容化的当前迁移状态；不作为具体主题事实源。
updated_at: 2026-06-12
supersedes:
  - 02_Projects/Knowledge-Base/知识库结构审计-2026-06-05.md
---

# 知识库结构审计 Current

## 1 当前决策

知识库入口采用“内容简介 + 入口分流”。结构状态不放在读者主入口中心，而集中记录在本审计文件中。

## 2 分区结构状态

| 分区 | 当前状态 |
|---|---|
| `01_Knowledge` | 已新增正式知识总览和主要一级主题总览 |
| `02_Projects` | 已新增项目总览、DMS 总览、DMS 模块索引和 Model Training current 组 |
| `03_Inbox` | 已新增候选内容索引 |
| `04_Sources` | 已新增来源索引 |
| `90_Archive` | 暂不处理为当前入口 |

## 3 DMS current 标准化状态

| 模块 | 状态 | 下一步 |
|---|---|---|
| Tracking | current 组较完整；仍是 partial recoverability | 后续补运行验证或 recoverability review |
| SDK Integration | current 组已创建；created_but_not_fully_verified | 后续补运行态验证或 recoverability review |
| EyeStatus | current 组已创建；single_pass_recoverable=false | 后续补独立可恢复性验证 |
| FaceID | current 组已有默认入口；partial recoverability | 后续补 recoverability verification |
| Model Training | current 组已创建；created_but_not_fully_verified | 后续补 recoverability verification |
| Postprocess | 已补模块索引；无 current 组 | 若持续迭代，再创建 current 组 |
| State Machine | 已补模块索引；无 current 组 | 若进入实现或长期维护，再创建 current 组 |

## 4 正式知识结构化状态

| 主题 | 状态 | 下一步 |
|---|---|---|
| Agent Workflow | 已有主题总览；部分条目有完整元数据 | 核验新增条目互相引用和重复边界 |
| 模型 | 已有主题总览；J6 工具链结构较完整 | 对高频旧条目补 `summary/sources/scope/risks` |
| C++ | 已有主题总览；多数为历史笔记 | 分批补最小元数据，不批量改写正文 |
| 多模态大模型 | 已有主题总览 | 补高频条目最小元数据 |
| 通信技术 | 已有主题总览 | 补条目来源、适用范围和风险 |
| Apollo | 已有主题总览 | 补版本边界和条目元数据 |
| 库 | 已有主题总览 | 补 OpenCV/PyTorch 条目元数据 |
| 操作系统 | 已有主题总览 | 补版本和环境边界 |
| 芯片架构与底软 | 已有主题总览 | 补来源和具体芯片适用边界 |
| 计算机原理 | 已有主题总览 | 补基础概念来源和适用边界 |
| Docker | 单条目已补最小元数据 | 后续按需补 Docker 主题总览 |

## 5 入口呈现状态

读者入口已切换为“内容简介 + 入口分流”。结构状态集中记录在本审计文件、模块 current 文档或维护记录中。

## 6 未解决项

- `01_Knowledge` 旧条目的最小元数据覆盖仍未完成，但一级主题入口已基本收口。
- Model Training current 组已创建，但尚未完成独立 recoverability verification。
- FaceID、EyeStatus、SDK Integration 的 recoverability verification 尚未完成。
- Postprocess、State Machine 是否 current 化尚未决策。

## 7 2026-06-09 Tracking current 增量维护记录

- 因 DmsTrack 首轮内部可读性重构改变了当前实现事实和验证状态，已局部更新：
  - `tracking_overview_current.md`
  - `tracking_implementation_current.md`
  - `tracking_validation_current.md`
  - `DMS项目总览.md`
  - 对应 Current Maintenance Record
- 未整组重写 current 文档；`tracking_design_current.md` 与 `tracking_spec_current.md` 未修改，因为设计目标、算法契约和 public API 没有变化。
- Tracking 默认入口、默认恢复顺序和 default recovery bundle 未变化。
- `recoverability_status` 仍为 `partial`；未新增或保留 `single_pass_recoverable: true` 声明。
- 新增证据为 patch check、J6B 编译和独立 repo review；runtime replay 与单元测试未执行，板端验证按本次任务边界为 not required。
- 同日继续局部同步 Hand Phase 4A：仅更新 Tracking overview/implementation/validation、维护记录和 DMS 总览；design/spec、默认入口、恢复顺序与 `recoverability_status: partial` 均未变化。

## 8 2026-06-11 Tracking current 增量维护记录

- 因 sentinel、ID 生命周期语义和 Body/Hand 阶段组织成为新的当前实现事实，已同步更新 Tracking 五份 current 文档、DMS 项目总览和本结构审计。
- 本轮未整组重写正文；design/spec 仅补充 `bodyId / handId` 初始继承 face key、但 body/hand 生命周期独立的边界，以及 hand 发布仍依赖当前 DRIVER body evidence 的约束。
- Tracking 默认入口、默认恢复顺序、default recovery bundle 和 `recoverability_status: partial` 均未变化。
- 证据为 `git diff --check`、J6B 编译、独立 repo review `approved` 和 verification-manager `conditional_pass`；runtime replay 与单元测试未执行，板端验证为 not required。
- 未新增或保留 `single_pass_recoverable: true` 声明。

## 9 2026-06-12 Tracking 后排误跟踪主驾修复写回

- 因 2m 回灌样本新增已验证运行事实，已同步更新 Tracking current 五份文档、DMS 项目总览和本结构审计，并新增项目级维护记录。
- 本次新增板端证据：二次回灌完成后 `face-first driver face select face=1` 为 0 次，`reject back passenger` 与 `reject smaller` 共同过滤后排候选。
- 本轮未整组重写 current 文档；仅补充 driver face 防后排误绑定的设计、规范、实现和验证事实。
- Tracking 默认入口、默认恢复顺序、default recovery bundle 和 `recoverability_status: partial` 均未变化。
- 未新增或保留 `single_pass_recoverable: true` 声明。
