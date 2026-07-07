---
type: vault_entry
status: active
scope: 知识库顶层导航；只负责入口分流，不作为具体主题真相源。
updated_at: 2026-06-22
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
| 多模态大模型 | [[01_Knowledge/多模态大模型/多模态大模型知识总览]] |
| 通信技术 | [[01_Knowledge/通信技术/通信技术知识总览]] |
| C++ | [[01_Knowledge/C++/C++知识总览]] |
| Apollo | [[01_Knowledge/Apollo/Apollo知识总览]] |

## 1.3 项目导航

| 项目 | 入口 | 内容简介 |
|---|---|---|
| DMS | [[02_Projects/DMS/DMS项目总览]] | DMS 算法、SDK、训练、后处理、状态机、FaceID 与 EyeStatus 项目资料 |
| cutepower | [[02_Projects/cutepower/cutepower_overview_current]] | Agent workflow 治理插件、contracts-first 路由、runtime gate 与 writeback 规则 |
| subpower | [[02_Projects/subpower/subpower_architecture_blueprint_current]] | subagent-first 三侧协作流程、架构蓝图和实现记录 |
| codex capability registry | [[02_Projects/codex-capability-registry/Codex plugin skill 集中注册与迁移方案]] | Codex plugin/skill 集中注册、能力摘要、portable source、安装策略和版本锁定 |
| investment-advisor | [[02_Projects/investment-advisor/investment-advisor项目总览]] | 个人美股投资研究 Agent 系统 MVP，含 mock 数据层、SEC 证据层、反馈调节和 thesis memory |
| agent-trajectory | [[02_Projects/agent-trajectory/agent_trajectory_overview_current]] | 工业 agent 任务轨迹库、Agent Execution Event Sourcing、状态重建、Failure Taxonomy 和轨迹蒸馏实现指导 |
| Knowledge-Base | [[02_Projects/Knowledge-Base/知识库维护治理项目总览]] | 知识库结构维护、写前追溯门禁、生命周期元数据和防静默覆盖治理 |
| CVAT | [[02_Projects/cvat/CVAT云端部署项目总览_current]] | CVAT 云端标注平台部署、Docker Compose 架构、NAS 数据层、训练平台模型任务输出和人工复核流程 |

## 1.4 入口说明

本文件只提供入口分流。目录访问、写入分层、正式知识提升和外部信息入库约束以 [[AGENTS]] 为准。

## 1.5 结构维护

结构状态和待修复项记录在 [[02_Projects/Knowledge-Base/知识库结构审计_current]]。
