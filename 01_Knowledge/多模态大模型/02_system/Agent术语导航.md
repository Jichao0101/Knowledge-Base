---
type: knowledge
status: verified
unit_type: knowledge_map
domain: 多模态大模型系统
topic: Agent相关术语导航
sources:
  - 01_Knowledge/多模态大模型/02_system/Agent.md
  - 01_Knowledge/多模态大模型/02_system/OpenClaw.md
  - 01_Knowledge/多模态大模型/多模态大模型系统.md
scope: 适用于在本知识库中快速区分 Agent、Harness、Runtime、Framework、Skill、Workflow / Orchestration 的概念边界，并跳转到对应正文文档。
risks:
  - 本页是导航页，不替代各术语正文定义
  - 个别术语在外部社区可能有不同口径，应以本库当前定义为准
source_task: 根据 Agent 文档局部重构结果补充术语导航页，收敛相邻文档中的概念边界
evidence:
  - Agent 主文档已采用 Agent = Model + Harness 的最上层分法
  - OpenClaw 案例已按 Model / Harness / Platform-Framework 重新映射
updated_at: 2026-04-11
---

# 1 Agent 术语导航

## 1.1 这页解决什么问题

这页不是重新定义所有术语，而是回答一个更实际的问题：

> 在本知识库里，看到 Agent、Harness、Runtime、Framework、Skill、Workflow / Orchestration 时，应该先跳去哪里看，边界怎么快速区分？

---

## 1.2 最短关系图

可以先按下面这条链理解：

`Agent -> Harness -> Runtime`

以及：

`Agent = Model + Harness`

`Framework / Platform = 用来搭和承载系统的抽象与控制面`

`Skill = 在既定 Framework / Harness 下可路由调用的窄能力包`

`Workflow / Orchestration = Harness 内的全局编排控制层`

---

## 1.3 术语入口

### 1.3.1 Agent

- 关注点：一个完整可运行系统由哪些部分组成，以及如何形成闭环
- 在本库中的角色：完整可运行系统，即 `Model + Harness`
- 首读文档：[[Agent]]

### 1.3.2 Model

- 关注点：在给定目标、状态和反馈时，下一步系统动作是什么
- 在本库中的角色：策略与动作选择核心，不等于完整 Agent
- 首读文档：[[Agent]]

### 1.3.3 Harness

- 关注点：如何把 Agent 接到真实执行环境中，并实施状态承载、工具执行、权限门禁、恢复与审计
- 在本库中的角色：宽口径上指 Model 之外的模型外承载与控制系统总称
- 内部分层：局部执行承载层 + 全局编排控制层
- 首读文档：[[Agent]]

### 1.3.4 Runtime

- 关注点：执行循环、生命周期推进、调度、取消、恢复
- 在本库中的角色：Harness 的局部执行承载层内部的动态运行机制
- 首读文档：[[Agent]]

### 1.3.5 Framework / Platform

- 关注点：如何搭系统、怎么组织节点、状态图、控制面、集成接口
- 在本库中的角色：构建或承载 Agent 系统的抽象与平台层，不等于单个 Agent
- 首读文档：[[OpenClaw]]

### 1.3.6 Skill

- 关注点：一个可复用、可路由、边界清楚的窄能力包
- 在本库中的角色：能力单元，不等于 Agent 本体，也不等于 Runtime
- 首读文档：[[Codex Skill开发与脚本化边界规范]]

### 1.3.7 Workflow / Orchestration

- 关注点：多步流程、角色顺序、审批、返工、多 agent 协同
- 在本库中的角色：Harness 内的全局编排控制层
- 它不是什么：不是单个 Agent 内部的局部 planning，也不是某个 Skill 的执行脚本
- 首读文档：[[01_Knowledge/Agent Workflow/Agent驱动知识库、代码库与板端侧协同闭环规范|Agent驱动知识库、代码库与板端侧协同闭环规范]]
- 配套运行文档：[[01_Knowledge/Agent Workflow/Agent三侧运行规范与调度模板|Agent三侧运行规范与调度模板]]

一个直接可用的例子是三侧闭环里的 `workflow-orchestrator`：

- 主代理默认承担 `workflow-orchestrator` 职责
- 它决定先调用 `knowledge-planner`
- 再决定是否进入 `repo-coder`
- 之后把结果裁剪后交给 `repo-reviewer`
- 最后再由 `knowledge-closer` 完成知识回写
- 若本地知识不足，可插入 `source-ingestor`
- 若问题复杂，可插入 `failure-analyst`

这里真正发生的是：

- 角色调用顺序控制
- 审批与门禁控制
- reviewer 独立性控制
- 返工轮次控制
- `stop / retry / replan / escalate / close` 决策

这就是 workflow / orchestration，而不是单个 agent 在内部“想下一步做什么”。

---

## 1.4 快速判别法

- 如果你在讨论“一个完整系统由模型和执行壳层怎么组成”，优先落到 Agent。
- 如果你在讨论“给定目标、状态和反馈时下一步系统动作是什么”，优先落到 Model。
- 如果你在讨论“这一步如何被安全执行、记录、恢复和约束”，优先落到 Harness 的局部执行承载层。
- 如果你在讨论“执行循环怎么跑、怎么中断、怎么恢复”，优先落到 Runtime。
- 如果你在讨论“系统怎么搭、控制面怎么组织、平台如何承载多入口和多节点”，优先落到 Framework / Platform。
- 如果你在讨论“一个能力包如何被触发、输入输出是什么、边界怎么收紧”，优先落到 Skill。
- 如果你在讨论“多个步骤、多个角色或多个 agent 如何排顺序和过门禁”，优先落到 Harness 的全局编排控制层，也就是 Workflow / Orchestration。

---

## 1.5 当前知识库中的推荐阅读顺序

1. [[多模态大模型系统]]
2. [[Agent]]
3. [[OpenClaw]]
4. [[Codex Skill开发与脚本化边界规范]]
5. [[01_Knowledge/Agent Workflow/Agent驱动知识库、代码库与板端侧协同闭环规范|Agent驱动知识库、代码库与板端侧协同闭环规范]]
6. [[01_Knowledge/Agent Workflow/Agent三侧运行规范与调度模板|Agent三侧运行规范与调度模板]]

---

## 1.6 使用边界

- 这页适合做术语入口，不适合承载完整机制推导。
- 若正文定义与本页摘要发生冲突，以正文为准，并应回到本页更新导航摘要。
