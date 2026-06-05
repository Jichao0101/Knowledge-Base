---
type: vault_entry
status: active
scope: 知识库顶层导航；只负责入口分流，不作为具体主题真相源。
updated_at: 2026-06-05
---

# 1 知识库总入口

本入口用于快速定位知识库内容。具体事实判断应进入对应正式知识、项目 current 文档组、候选记录或来源证据卡。

## 1.1 分区入口

| 分区 | 用途 | 默认处理方式 |
|---|---|---|
| [[01_Knowledge/知识总览]] | 已审核、可复用、边界清晰的正式知识 | 作为稳定知识入口使用，仍需阅读条目内的适用范围与风险 |
| [[02_Projects/项目总览]] | 项目工作区、current 文档组、实验和决策记录 | 优先读取项目或模块总览，再进入 current 文档组 |
| [[03_Inbox]] | 待分类、待审核、待提升候选内容 | 不直接视为正式知识，先看 [[03_Inbox/候选内容索引]] |
| [[04_Sources/来源索引]] | 外部来源证据卡、原始摘录、阅读记录 | 作为候选或正式知识的来源依据 |
| [[90_Archive]] | 历史、冻结、失效或不再维护内容 | 默认不作为当前事实源 |

## 1.2 正式知识导航

| 主题 | 入口 |
|---|---|
| Agent Workflow | [[01_Knowledge/Agent Workflow/Agent Workflow总览]] |
| 模型工程总览 | [[01_Knowledge/模型/模型知识总览]] |
| J6 工具链 | [[01_Knowledge/模型/工具与平台/J6工具链/总览]] |
| 多模态大模型 | [[01_Knowledge/多模态大模型/多模态大模型系统]] |
| 通信技术 | [[01_Knowledge/通信技术/车载系统通信]] |
| C++ | [[01_Knowledge/C++/C++知识总览]] |
| Apollo | [[01_Knowledge/Apollo/Apollo]] |

## 1.3 项目导航

| 项目 | 入口 | 状态说明 |
|---|---|---|
| DMS | [[02_Projects/DMS/DMS项目总览]] | 已建立模块级入口索引；部分模块 current 未完成 recoverability verification |
| cutepower | [[02_Projects/cutepower/cutepower_overview_current]] | current 文档组已存在 |
| subpower | [[02_Projects/subpower/subpower_architecture_blueprint_current]] | current/implementation records 已存在 |
| codex capability registry | [[02_Projects/codex-capability-registry/Codex plugin skill 集中注册与迁移方案]] | 单主题项目记录 |

## 1.4 读取规则

1. 找正式知识时，先进入 `01_Knowledge` 对应主题入口。
2. 找项目当前状态时，先进入项目总览，再进入模块 `overview_current`。
3. 找外部资料或待整理内容时，先进入 [[03_Inbox/候选内容索引]] 和 `04_Sources`。
4. `Current Maintenance Records`、历史方案、运行工件只作为证据或追溯材料，不默认承担当前入口职责。

## 1.5 当前结构风险

- 正式知识中仍有部分旧笔记缺少统一 frontmatter。
- 项目区 current 文档组成熟度不一致，不能把所有 `*_current.md` 都等同为已完成可恢复性验证。
- 候选区部分外部资料已提升到正式知识，但候选原文仍保留，需要依赖候选索引判断状态。
