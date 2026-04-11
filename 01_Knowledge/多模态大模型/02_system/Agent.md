
# 1 Agent 的定义

大语言模型的任务是：**根据上下文生成下一个最可能的符号**。

但 Agent 的任务不同。  Agent 不只是生成文本，而是要在目标约束下持续选择“系统下一步该做什么”。

$P(u_t \mid o_t, m_t, g, h_t)$

其中：

- $u_t$：系统动作（system action）
    
- $o_t$：当前观测（observation）
    
- $m_t$：内部记忆（memory）
    
- $g$：任务目标（goal）
    
- $h_t$：历史轨迹（history）
    

这里最关键的区别是：

- LLM 输出的是 **符号**
    
- Agent 输出的是 **系统动作**
    

所谓系统动作，不一定是物理控制，也不一定直接作用于真实环境。  
它可以是：

- 回复用户
    
- 调用工具
    
- 发起检索
    
- 更新记忆
    
- 修改计划
    
- 调度下一步任务
    
- 终止执行
    

因此，Agent 的本质不是“更会聊天的 LLM”，而是：

> 由 Model 与 Harness 共同构成的闭环系统：前者负责策略与动作选择，后者负责模型外承载与控制。

---

# 2 Agent 与 LLM 的本质差异

LLM 的主问题是：

> 在给定上下文时，下一个 token 是什么？

Agent 的主问题是：

> 在给定目标、状态和反馈时，下一步系统动作是什么？

这意味着二者研究对象不同。

## 2.1 LLM 关注的是分布拟合

LLM 的核心仍然是语言分布建模：

- token 预测
    
- 表示学习
    
- 模式拟合
    
- 条件生成
    

它的失败通常表现为：

- 幻觉
    
- 格式错误
    
- 推理不稳
    
- 上下文利用不足
    

## 2.2 Agent 关注的是闭环执行

Agent 关注的是：

- 状态如何维持
    
- 动作如何选择
    
- 工具如何执行
    
- 反馈如何写回
    
- 错误如何恢复
    
- 权限如何约束
    

它的失败不再只是“回答错了”，而是：

- 调错工具
    
- 写错状态
    
- 走错流程
    
- 重复执行
    
- 越权操作
    
- 在错误前提上持续推进
    

因此，LLM 和 Agent 的区别，不只是“会不会调工具”，而是：

> Agent 把生成模型嵌入到了一个可执行、可反馈、可持久的系统中。

---

# 3 Agent 的最小工程分层


`Agent = Model + Harness`

其中：

- Model：负责基于目标、状态和反馈选择下一步系统动作
    
- Harness：负责让这个模型能够稳定、受控、可恢复、可审计地运行
    

`Agent` 指向**完整可运行系统**

## 3.1 Model

这里的 Model 不只是“一个裸 LLM 参数文件”，而是系统里承担策略与动作选择的模型侧核心。

它关注的问题是：

> 在给定目标、状态和反馈时，下一步系统动作是什么？

因此，Model 侧通常至少包含：

1. Policy Core
    
2. 面向动作选择的状态抽象
    
3. 面向工具与执行的动作抽象
    
4. 局部 planner / controller
    

这些东西共同构成“模型如何决定下一步”的那一侧。

## 3.2 Harness

如果从工程闭环运行的角度看，Harness 最好按宽口径理解：

> Harness 是 Model 之外，为了让 Agent 稳定、受控、可恢复、可审计地运行所需的模型外系统总称。

它之所以重要，是因为真实系统里很多问题都不在模型本身，而在 Harness：

- 状态如何承载
    
- 工具如何真正执行
    
- 权限和审批如何生效
    
- 失败后如何恢复
    
- 多角色任务链如何编排
    
- 审查、返工和回写如何过门禁
    

先用 Harness 把“模型外运行系统”整体框住，再在内部分层，通常更利于工程改造、排障和知识维护。

## 3.3 Harness 的内部两层

### 3.3.1 局部执行承载层

这一层负责把某个模型侧决策真正落到执行环境中。  
典型内容包括：

- 会话与任务生命周期绑定
    
- Memory 后端接入
    
- Tool dispatcher 与执行器接入
    
- sandbox / timeout / checkpoint / resume
    
- 权限、审批与审计
    
- workspace / session / tenant 隔离
    
- 异常处理、恢复与取消
    
- 与外部 I/O、平台入口和运行环境对接
    

### 3.3.2 全局编排控制层

这一层负责跨角色、跨 agent、跨阶段的任务链控制。  
典型内容包括：

- workflow / orchestration
    
- 角色调用顺序
    
- reviewer 独立性控制
    
- handoff 与交接包裁剪
    
- stop / retry / replan / escalate / close 门禁
    
- 返工轮次控制
    
- 多 agent 协同与条件分支插入
    

这层不直接回答“当前模型下一步输出什么”，而是回答：

> 整个任务链由谁先执行、谁后执行、何时暂停、何时返工、何时关闭。

## 3.4 边界结论

在本文里，后续术语默认按以下边界使用：

- Agent：完整可运行系统，即 `Model + Harness`
    
- Model：策略与动作选择核心
    
- Harness：Model 之外的模型外承载与控制系统总称
    
- Runtime：Harness 的局部执行承载层内部，用于驱动执行循环、调度和生命周期的动态机制
    
- Workflow / Orchestration：Harness 的全局编排控制层
    
- Framework：用于构建 Model 或 Harness 的抽象与平台
    
- Skill：在既定 Framework / Harness 下可复用、可路由的窄能力包
    

这样处理后，后文的 Memory、Tools、Planner / Controller 和 Runtime 才有稳定归属。

---

# 4 Model：策略与动作选择核心

本章讨论的是 Agent 中负责“决定下一步系统动作”的模型侧部分。  
为避免与完整系统层混淆，后文不再使用 `Agent Core` 作为顶层主术语，而统一使用 `Model` 指代这一侧。

## 4.1 Policy Core

Policy Core 通常由 LLM 承担。

它的作用不是亲自完成所有任务，而是：

- 解析目标
    
- 读取状态
    
- 解释工具描述
    
- 选择下一步动作
    
- 在反馈后更新策略
    

从系统角度看，它更像一个**高层策略选择器**。

## 4.2 它做什么

常见职责包括：

- 将用户请求转成可执行目标
    
- 判断是否需要外部工具
    
- 决定先规划还是先执行
    
- 根据 observation 调整下一步
    
- 在局部失败后选择重试、回退或终止
    

## 4.3 它不做什么

Policy Core 本身并不天然具备：

- 持久状态
    
- 真实 I/O
    
- 并发调度
    
- 权限隔离
    
- 恢复能力
    

这些能力都来自系统外壳，而不是模型本身。

所以从工程上讲：

> LLM 决定策略方向，系统负责让策略真正落地。

---

# 5 Memory：记忆与状态

Memory 的作用不是“让模型记住更多东西”，而是：

> 让系统在多步执行中维持状态连续性。

可以按生命周期分成三层。

## 5.1 Context Memory

这是直接放在 prompt 里的上下文。

特点：

- 访问最简单
    
- 延迟最低
    
- 容量受窗口限制
    
- 容易被噪声污染
    

它适合放：

- 当前目标
    
- 最近几步 observation
    
- 关键中间变量
    
- 必要约束条件
    

## 5.2 Session Memory

这是一次任务执行过程中的工作状态。

常见内容：

- 当前计划
    
- 已完成步骤
    
- 待执行步骤
    
- 工具结果
    
- 失败原因
    
- 重试记录
    
- 产出物引用
    

它的核心作用是：

- 避免模型每步从零开始
    
- 让控制器可恢复
    
- 让系统具备中断续跑能力
    

## 5.3 Persistent Memory

这是跨会话长期存在的状态。

例如：

- 用户偏好
    
- 环境配置
    
- 账户和权限信息
    
- 常用工作流
    
- 历史任务摘要
    
- 固化知识条目
    

Persistent Memory 不等于“无限记忆”。  
真正难的不是存下来，而是：

- 何时写入
    
- 写入什么
    
- 如何检索
    
- 如何防止脏数据污染后续行为
    

## 5.4 关键结论

Agent 的连续性主要不来自模型参数，而来自**外部状态管理**。  
这件事非常重要。很多“Agent 看起来会持续工作”的能力，本质上都是状态外置，而不是模型突然长了记性。

补一句边界：Memory 作为“Model 可利用的状态抽象”属于模型侧视角；  
而 session store、数据库、文件状态、向量库、checkpoint 文件等具体存储与检索机制，属于 Harness 视角。

也就是说：

- Model 关心“当前可读到什么状态”
    
- Harness 关心“这些状态如何被持久化、检索、版本化、恢复与隔离”

---

# 6 Tool Interface：工具接口

Tool 是 Agent 和外部世界之间的执行端口。

抽象形式可以写为：

`tool(input)→output`
工具的本质不是“让模型更强”，而是：

> 把语言模型从纯符号生成器，变成可以触发真实执行的决策器。

## 6.1 常见工具类别

- 文件读写
    
- 检索与搜索
    
- 浏览器控制
    
- Shell / 代码执行
    
- 数据库访问
    
- API 调用
    
- 邮件、日历、IM
    
- UI 操作
    
- 设备控制
    

## 6.2 工具调用的本质变化

在普通对话里，模型输出的是文本。  
在 Agent 系统里，模型输出的文本或结构化对象会被解释为**动作意图**，然后进入 dispatcher 执行。

因此，中间多了一层关键变换：

`symbol -> action intent -> real execution`

## 6.3 工具接口设计原则

工具如果要适合 Agent，不只是“能调通”就行。  
更重要的是：

- 输入输出清晰
    
- 参数 schema 稳定
    
- 错误码明确
    
- 行为幂等
    
- 可审计
    
- 可超时
    
- 可回滚或补偿
    

否则系统很容易出现“模型理解得差不多，但接口地狱把它拖死”的经典烂活。

这里也要区分两层：

- Tool Interface 作为 action schema，属于 Model 面向外部能力的决策接口
    
- dispatcher、executor、sandbox、timeout、retry、权限检查等，属于 Harness 的执行承载
    

Model 决定“调用哪个工具、带什么参数”；  
Harness 决定“这个调用是否允许、如何执行、如何超时、如何审计、失败后如何反馈”。

---

# 7 Planner / Controller：规划与控制

Planner 解决的是：

> 任务应该如何拆解？

Controller 解决的是：

> 当前该继续、终止、重试还是回退？

二者可以由同一模块承担，也可以分开。

## 7.1 Planner 的作用

Planner 负责：

- 把大目标拆成子目标
    
- 确定执行顺序
    
- 建立依赖关系
    
- 识别可并行步骤
    
- 约束预算和边界条件
    

## 7.2 Controller 的作用

Controller 负责：

- 判断当前 step 是否成功
    
- 决定是否继续
    
- 处理异常和超时
    
- 做重试与降级
    
- 维护 checkpoint
    
- 管理终止条件
    

## 7.3 为什么二者不能省

如果没有 Planner，系统容易变成“想到哪做到哪”的局部贪心。  
如果没有 Controller，系统容易：

- 无限循环
    
- 重复执行
    
- 错误升级
    
- 在错误前提上继续推进
    

因此，Agent 的可用性很大程度上取决于：

> 它有没有可靠的控制流，而不是它会不会说漂亮话。

还要再收紧一个边界：

- 模型侧局部决策链内部的任务拆解、步进控制、重试和终止判断，属于 Planner / Controller
    
- 跨角色、跨 agent、跨系统的顺序编排、审批门禁、交接包裁剪和返工控制，更接近 Workflow / Orchestration
    

前者偏 Model，后者偏 Harness 或更上层的运行系统。

可以结合本知识库里的 `Agent Workflow` 文档看一个更具体的例子：

- 若 `knowledge-planner` 在项目上下文中形成实施计划，这仍属于某个执行角色内部的 planning
    
- 若主代理以 `workflow-orchestrator` 身份决定先调 `knowledge-planner`，再调 `repo-coder`，之后交给 `repo-reviewer`，最后再由 `knowledge-closer` 做回写，这已经不是单个 Agent 的局部 planning，而是 orchestration
    
- 若系统还要控制 reviewer 独立性、决定是否插入 `source-ingestor` 或 `failure-analyst`、以及在 `stop / retry / replan / escalate / close` 之间做门禁决策，这更明确属于 workflow 层控制
    

所以在工程实践里可以用一句话区分：

> planner/controller 解决“当前模型侧决策链下一步怎么走”，workflow/orchestration 解决“整个任务链由谁先上、谁后上、何时停、何时返工”。

---

# 8 Harness：Model 之外的工程承载与控制系统

前文已经把 Agent 收敛为：

`Agent = Model + Harness`

如果从工程闭环运行的角度看，Harness 不应只按狭义 runtime 去理解，而应理解为：

> Model 之外，为了让 Agent 稳定、受控、可恢复运行所需的模型外承载与控制系统。

这个定义之所以重要，不是因为术语更漂亮，而是因为它更符合真实工程里的问题分布。  
很多“Agent 不稳定”的问题，根因并不在策略本身，而在 Harness：

- 状态承载失真
    
- tool dispatch 失败
    
- timeout / retry 策略不稳
    
- 权限和审批边界失效
    
- handoff 污染
    
- orchestration 路由错误
    
- reviewer 不独立
    
- 返工和回写门禁缺失
    

## 8.1 为什么宽口径 Harness 更贴近工程

如果只有 Policy Core、Memory 抽象、Tool 接口和 Planner / Controller 抽象，系统仍可能只是一个逻辑上成立的 Agent 设计。  
它未必已经是一个可长期运行、可恢复、可审计、可约束的工程系统。

宽口径 Harness 的价值主要在三点：

- 更贴近改造对象  
  工程里很多升级都发生在模型外系统，而不是 Model。
    
- 更适合排障  
  出问题时先判断“是不是 Harness 侧问题”，通常比先在 runtime / workflow / tooling 之间机械分类更有效。
    
- 更适合知识沉淀  
  长期可复用的往往是承载模式、门禁模式、交接模式和恢复模式，而不只是某个具体 runtime 接口。
    

但它也有风险：  
如果只讲“宽口径 Harness”，不继续细分，Runtime、Workflow / Orchestration、Framework 很快又会混成一层。  
所以 Harness 必须继续做内部层次划分。

## 8.2 Harness 内的局部执行承载层

这一层负责把某个 Agent 的局部决策真正绑定到执行环境中。  
它偏“执行承载”，典型职责包括：

- 会话与任务生命周期管理
    
- 状态后端接入与读写约束
    
- 工具 dispatcher 与真实执行
    
- 异常处理与超时控制
    
- 并发管理
    
- 取消与中断
    
- 日志与审计
    
- checkpoint / resume
    
- 权限边界执行
    
- workspace / session / tenant 隔离
    

这一层最接近很多人平时口中的 runtime 外壳。

## 8.3 Runtime 在局部执行承载层中的位置

Runtime 是 Harness 的一部分，但不是 Harness 的全称。  
更准确地说，它是**局部执行承载层内部的动态运行机制**。

可以把它理解为负责以下事情的部分：

- event loop 或 step loop
    
- 调度与派发
    
- 生命周期推进
    
- 中断、取消与恢复
    
- 执行结果回流
    
- 并发与资源占用控制
    

所以：

- Harness 是总括层
    
- 局部执行承载层是 Harness 的一部分
    
- Runtime 又是局部执行承载层中的运转机构
    

## 8.4 Harness 内的全局编排控制层

Harness 不仅包含局部执行承载，也包含全局流程编排控制。  
这是因为真实系统里，“能不能稳定运行”不只取决于某一步是否执行成功，还取决于：

- 角色调用顺序是否正确
    
- 审查是否独立
    
- 返工是否受控
    
- 交接包是否被裁剪
    
- 哪些条件下允许 stop / retry / replan / escalate / close
    
- 是否在恰当阶段插入 source-ingestor、failure-analyst、verification-manager 等角色
    

这些问题不属于单个 Agent 内部 planner/controller，  
它们属于更上位的 workflow / orchestration 控制，但从工程闭环角度看，仍然属于 Harness，因为它们同样是 Model 之外、保证系统受控运行的模型外控制机制。

结合本知识库的 `Agent Workflow` 文档，可以把这一层理解为 `workflow-orchestrator` 所承担的职责模式：

- 主代理维护状态机
    
- 决定角色调用顺序
    
- 控制 reviewer 独立性
    
- 控制返工轮次
    
- 决定 `stop / retry / replan / escalate / confirm / close`
    
- 维护 `run_log / audit_log`
    

以及默认调用链：

`knowledge-planner -> repo-coder -> repo-reviewer -> knowledge-closer`

必要时按条件插入：

- `source-ingestor`
    
- `failure-analyst`
    
- `verification-manager`
    
- `functional-reviewer`
    
- `knowledge-auditor`
    

因此，Workflow / Orchestration 不应被看成 Harness 外的一块漂浮概念。  
在工程视角下，它更适合作为 Harness 内的**全局编排控制层**。

## 8.5 Framework、Skill 与 Harness 的关系

### 8.5.1 Framework

Framework 是构建 Agent 或 Harness 的抽象与平台。  
它解决的是“怎么搭系统”，不等于当前任务里已经运行的 Harness。

### 8.5.2 Skill

Skill 不是 Agent 本体，也不是 Runtime。  
它更像在既定 Framework / Harness 下可复用、可路由的窄能力包。

它可以被 Harness 调用、约束和编排，但它本身不等于 Harness。

## 8.6 一个更稳的判断准则

当你在系统里看到某个能力时，可以用下面的问题判断它属于哪层：

- 它是在决定“下一步做什么”吗？  
  如果是，更接近 Model。
    
- 它是在决定“这一步如何被安全执行、记录、恢复和约束”吗？  
  如果是，更接近 Harness 的局部执行承载层。
    
- 它是在决定“整个任务链如何编排、交接、审批、返工和关闭”吗？  
  如果是，更接近 Harness 的全局编排控制层。
    
- 它是在驱动执行循环、调度和生命周期吗？  
  如果是，更接近 Runtime。
    
- 它是在提供搭建这些系统的通用抽象吗？  
  如果是，更接近 Framework。
    
- 它是在封装一个可复用窄能力吗？  
  如果是，更接近 Skill。
    
- 它是在编排多个步骤、角色或 agent 吗？  
  如果是，更接近 Harness 内的 Workflow / Orchestration 子层。
    

这样区分后，`Agent` 的定义会更稳定，`Harness` 也不会继续被 `Runtime` 或 `Framework` 吞掉。

---

# 9 Agent 的统一执行闭环

把前面的模块拼起来，Agent 的运行过程可以写成：

$$
\begin{aligned}
s_t &= \{o_t, m_t, g, h_t\} \\
u_t &= \pi(s_t) \\
e_t &= \operatorname{execute}(u_t) \\
m_{t+1} &= \operatorname{update}(m_t, e_t)
\end{aligned}
$$

其中：

- $s_t$：当前系统状态
    
- $u_t$：系统动作
    
- $e_t$：执行结果 / 外部反馈
    
- $m_{t+1}$：更新后的内部状态
    

这说明 Agent 不只是一次生成，而是一个状态转移过程：

`observe -> decide -> execute -> feedback -> update -> next step`

因此，Agent 的能力不是单点函数能力，而是**闭环稳定性**。

---

# 10 常见执行范式

## 10.1 Single-Step Tool Calling

形式：

用户请求  
→ LLM 选工具  
→ 调工具  
→ LLM 总结

优点：

- 简单
    
- 延迟低
    
- 易上线
    

缺点：

- 多步能力弱
    
- 状态保持差
    
- 错误恢复弱
    

适合：

- FAQ
    
- 轻量助手
    
- 单跳查询任务
    

## 10.2 ReAct

形式：

Thought  
→ Action  
→ Observation  
→ Thought  
→ Action

优点：

- 中间轨迹清晰
    
- 易调试
    
- 适合探索型任务
    

缺点：

- token 开销大
    
- 长链容易漂移
    
- observation 噪声会累积
    

适合：

- 原型系统
    
- 研究型实现
    
- 工具探索任务
    

## 10.3 Plan-and-Execute

形式：

先规划  
再执行子任务  
执行中按反馈修正

优点：

- 全局结构清晰
    
- 长任务更稳
    
- 易插入预算约束
    

缺点：

- 初始计划错了会级联
    
- 环境变化时需要重规划
    

适合：

- 长流程任务
    
- 工作流自动化
    
- 较强结构化任务
    

## 10.4 Reflect / Critic Loop

形式：

执行  
→ 评估  
→ 修正  
→ 再执行

优点：

- 有显式纠错能力
    
- 适合代码、写作、复杂规划
    

缺点：

- 延迟高
    
- 成本高
    
- 可能陷入自我循环
    

## 10.5 Multi-Agent

形式：

把不同职能拆给不同 agent：

- planner
    
- executor
    
- reviewer
    
- retrieval agent
    
- domain specialist
    

优点：

- 分工清晰
    
- 可扩展性好
    

缺点：

- 协同复杂
    
- 状态同步难
    
- 通信开销大
    

---

# 11 主导约束

工程里真正决定 Agent 上限的，通常不是“模型是否更聪明”，而是主导约束是什么。

### 11.1.1 上下文窗口约束

问题：

- 历史过长
    
- 工具结果太大
    
- 多轮执行后 prompt 膨胀
    

后果：

- 成本高
    
- 延迟高
    
- 重要信息被淹没
    
- 状态污染
    

解决方向：

- 摘要压缩
    
- 状态结构化
    
- 中间结果外存
    
- 证据按需加载
    

## 11.2 工具延迟约束

问题：

- 网络 API 慢
    
- 浏览器慢
    
- I/O 阻塞
    
- 代码执行慢
    

后果：

- 总延迟被慢工具主导
    
- 长任务不稳定
    
- 用户体验崩掉
    

解决方向：

- 异步化
    
- 并行化
    
- timeout
    
- 缓存
    
- 优先级调度
    

## 11.3 状态一致性约束

问题：

- 重试时重复写状态
    
- 并发步骤相互覆盖
    
- 错误 observation 被固化进 memory
    

后果：

- 后续 step 建立在错误前提上
    
- 重复操作
    
- 错误持续放大
    

解决方向：

- 显式 state schema
    
- version / revision id
    
- 幂等设计
    
- checkpoint / rollback
    

## 11.4 权限与安全约束

问题：

- prompt injection
    
- tool poisoning
    
- 越权执行
    
- 本地命令破坏
    
- 敏感信息泄露
    

后果：

- 不只是“答错”
    
- 而是“做错并且造成损害”
    

解决方向：

- capability sandbox
    
- allowlist / denylist
    
- human approval
    
- secret isolation
    
- execution audit
    

---

# 12 常见失败模式

### 12.1.1 目标漂移

系统在长链执行中偏离原始任务目标。  
常见原因是：

- 历史太长
    
- 中间 observation 噪声大
    
- 缺少显式 goal anchor
    

## 12.2 工具幻觉

模型错误地假设某个工具具备某能力。  
常见原因是：

- 工具描述模糊
    
- schema 变动
    
- 名称误导
    

## 12.3 状态污染

错误结果被写入 memory，后续 step 持续基于错误前提推进。  
这比一次性答错更危险，因为错误被系统化了。

## 12.4 无限循环

表现为：

- 重复调用同一工具
    
- 重复生成近似计划
    
- 不满足终止条件却持续执行
    

应对方式：

- max steps
    
- loop detector
    
- repeated-action penalty
    
- termination classifier
    

## 12.5 高权限误操作

例如：

- 误删文件
    
- 误发消息
    
- 错误修改配置
    
- 执行危险 shell
    

这是 Agent 相比普通 LLM 最本质的风险升级。

---

# 13 工程设计原则

## 13.1 把“思考”和“执行”分离

不要让模型自由文本直接驱动真实工具。  
更可靠的方法是：

- 结构化 action schema
    
- 参数验证
    
- 执行前检查
    
- 高风险操作审批
    

## 13.2 把状态显式化

不要寄希望于模型“自己记住”。  
应明确记录：

- task id
    
- 当前计划
    
- 已完成步骤
    
- 待执行步骤
    
- 工具结果引用
    
- 失败原因
    
- 产出物位置
    

## 13.3 工具必须可验证

工具接口最好做到：

- 输入输出稳定
    
- 失败可检测
    
- 执行可审计
    
- 结果可复用
    

 13.2.2 默认最小权限

高能力加高不确定性，最后常常等于高事故率。  
Agent 默认应只拿到当前任务所需的最小能力。

 13.2.3 长任务必须支持恢复

因为现实世界里：

- 网络会抖
    
- 进程会挂
    
- 上下文会爆
    
- 工具会超时
    

所以长任务至少要支持：

- checkpoint
    
- replay
    
- partial commit
    
- resume
    

---

# 14 Agent 与 RAG、World Model、VLA 的边界

## 14.1 Agent vs RAG

RAG 解决的是：

> 缺知识时如何补证据？

Agent 解决的是：

> 有目标时如何分步执行？

所以：

- RAG 是条件扩展模块
    
- Agent 是控制与执行模块
    

## 14.2 Agent vs World Model

Agent 关注：

> 当前状态下应该做什么？

World Model 关注：

> 做了动作之后世界会怎样变化？

前者偏控制与任务执行，后者偏环境动态预测。
### 14.2.1 Agent vs VLA

VLA 主要学习：

- 视觉输入
    
- 语言条件
    
- 动作输出
    

它更像策略模型。  
而 Agent 更强调：

- 任务编排
    
- 状态管理
    
- 工具调用
    
- 长链闭环
    

在具身系统里，二者可以组合：

- Agent 负责高层任务控制
    
- VLA 负责低层动作策略
    

---

# 15 常用Agent

[[Codex工程化使用说明]]

[[OpenClaw]]

# 16 小结

Agent 的核心不是“把 LLM 包成一个聊天机器人”，而是：

> 让语言模型从符号生成器升级为系统动作选择器。

因此，Agent 的关键研究对象不再只是模型本身，而是：

- 状态如何表示
    
- 动作如何执行
    
- 反馈如何闭环
    
- 错误如何隔离
    
- 权限如何约束
    

从这个角度看，Agent 是一个系统问题，而不是一个提示词技巧问题。
