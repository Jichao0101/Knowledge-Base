---
type: structure_audit
status: active
scope: 记录知识库结构化、current 标准化、总览内容化的当前迁移状态；不作为具体主题事实源。
updated_at: 2026-06-05
supersedes:
  - 02_Projects/Knowledge-Base/知识库结构审计-2026-06-05.md
---

# 知识库结构审计 Current

## 1 当前决策

知识库入口采用“内容简介 + 入口分流”。结构状态不放在读者主入口中心，而集中记录在本审计文件中。

## 2 分区结构化策略

| 分区 | 目标结构 | 当前处理 |
|---|---|---|
| `01_Knowledge` | 正式知识条目元数据 + 主题总览 | 已新增正式知识总览和主要一级主题总览 |
| `02_Projects` | 项目入口 + 长期模块 current 文档组 + 记录区 | 已新增项目总览、DMS 总览、DMS 模块索引和 Model Training current 组 |
| `03_Inbox` | 候选队列索引 | 已新增候选内容索引 |
| `04_Sources` | 来源证据卡索引 | 已新增来源索引 |
| `90_Archive` | 归档区 | 暂不处理为当前入口 |

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

## 5 总览内容化规则

1. 总览主表使用“内容简介”，不使用“结构状态”作为主列。
2. 结构状态只保留在 frontmatter、模块 current 文档、维护记录或本审计文件中。
3. 新增正式知识应登记到对应主题总览。
4. 新增项目模块应先登记到项目总览或模块索引。
5. 长期维护模块才创建 current 五件套；临时记录只需要模块索引和 records。

## 6 未解决项

- `01_Knowledge` 旧条目的最小元数据覆盖仍未完成，但一级主题入口已基本收口。
- Model Training current 组已创建，但尚未完成独立 recoverability verification。
- FaceID、EyeStatus、SDK Integration 的 recoverability verification 尚未完成。
- Postprocess、State Machine 是否 current 化尚未决策。
