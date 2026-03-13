# 1 OpenClaw 是什么

OpenClaw 是一个**自托管、local-first 的 AI assistant gateway**。  
官方文档将它描述为一个本地优先的 Gateway，作为 sessions、channels、tools 和 events 的统一控制平面；它支持多消息渠道接入、内置 Pi agent runtime、per-sender session 管理、多平台节点和控制界面。

从系统角度看，OpenClaw 不是一个单纯的“聊天模型壳”，更接近：

> 一个以 Gateway 为中心、把渠道、Agent、工具、会话和节点设备组织到一起的运行时平台。

---

# 2 为什么它值得单独写成案例笔记

OpenClaw 值得单独成章，不是因为它“功能很多”，而是因为它把很多 Agent 理论里的抽象对象，做成了具体系统部件：

- Gateway
    
- Channels
    
- Agents
    
- Sessions
    
- Tools
    
- Nodes
    
- Platform Apps
    

官方文档直接把这些列为架构组成部分，并说明 Gateway 作为 WebSocket 控制平面负责路由消息、承载会话和工具体系。

所以它非常适合拿来说明一件事：

> Agent 不是 prompt，而是长期运行的软件系统。

---

# 3 OpenClaw 的系统定位

如果用统一抽象来映射，OpenClaw 大致位于这条链路中：

`LLM -> Tool-Augmented LLM -> Agent Runtime Platform`

它的重点不是重新发明基础模型，而是组织这些能力：

- 多渠道输入
    
- 会话与状态管理
    
- Agent runtime 承载
    
- 工具与节点接入
    
- 自动化调度
    
- 平台控制面
    

因此，OpenClaw 更适合作为“**Agent 平台层**”来理解，而不是作为某个单一 Agent 策略来理解。官方介绍中明确写到它提供 local-first Gateway、multi-channel inbox、multi-agent routing、会话管理、工具系统和平台应用。

---

# 4 架构总览

根据官方文档，OpenClaw 的架构包含六个关键部分：

1. Gateway
    
2. Channels
    
3. Agents
    
4. Sessions
    
5. Tools
    
6. Platform Apps
    

如果进一步展开，可以写成：

channels / platform apps / nodes  
            ↓  
         Gateway  
            ↓  
     sessions + routing  
            ↓  
        agent runtime  
            ↓  
           tools  
            ↓  
   external software / devices

其中最关键的是 Gateway。  
官方文档明确说明 Gateway 运行在本机或 VPS 上，作为 WebSocket server，对接消息渠道，并把消息按配置路由到对应的 AI agent。默认端口为 18789。

---

# 5 Gateway：控制平面

Gateway 是 OpenClaw 的核心。

官方介绍给出的定义非常明确：它是一个 local-first Gateway，用作 sessions、channels、tools、events 的单一控制平面。

## 5.1 它解决什么问题

在一般 Agent 原型里，消息入口、工具调用、状态管理、权限处理经常散落在不同脚本里。  
OpenClaw 把这些统一进 Gateway，有几个直接效果：

- 所有渠道都接入同一个控制面
    
- 消息路由与会话管理统一
    
- 工具调用不再散落在各自实现里
    
- 节点和平台应用都通过同一个网关协作
    

## 5.2 工程意义

这意味着 OpenClaw 的设计重心不是“让模型多想一步”，而是：

> 让一个 Agent 能以稳定的软件系统形态长期运行。

---

# 6 Channels：多渠道接入

OpenClaw 的一个突出特征是多消息渠道接入。  
GitHub 仓库首页和官方文档都列出了多渠道支持，包括 WhatsApp、Telegram、Slack、Discord、Google Chat、Signal、iMessage、Microsoft Teams、Matrix 等。

## 6.1 这件事为什么重要

在抽象的 Agent 理论里，输入只是 observation。  
但在真实系统里，observation 来自很多入口：

- 私聊
    
- 群聊
    
- 机器人 webhook
    
- 语音入口
    
- 移动设备
    
- 桌面端 app
    

OpenClaw 通过多渠道统一接入，把“输入源异构”这个工程问题做成了平台能力，而不是让每个 Agent 自己重新造轮子。

## 6.2 对系统设计的启发

这说明一个重要事实：

> Agent 平台的复杂度，往往首先来自 I/O 入口，而不是推理策略本身。

---

# 7 Sessions：会话与状态

官方文档指出，OpenClaw 支持 per-sender sessions，并提供 group isolation 和 activation modes。

## 7.1 为什么 Session 很关键

Session 是 Agent 连续性的基础。  
没有 session，系统只能做单轮调用；有了 session，系统才可能：

- 跨 step 持续执行
    
- 在群聊和私聊中隔离状态
    
- 为不同用户维护不同上下文
    
- 支持恢复与继续
    

## 7.2 系统映射

在统一符号里：

- $h_t$ 对应历史轨迹
    
- $m_t$ 对应内部记忆
    

而 session 就是这些状态的宿主之一。

所以 OpenClaw 的 session 设计值得关注，不是因为它“看起来像聊天记录”，而是因为：

> 它承载的是 Agent 的持续状态，而不只是对话文本。

---

# 8 Agents 与 Runtime

官方文档明确写到 OpenClaw 内置 **Pi agent runtime**，并支持 RPC mode、tool streaming、workspace isolation、multi-agent routing。GitHub 仓库首页和介绍页都有相应描述。

## 8.1 这意味着什么

这表明 OpenClaw 不是“写死一个 bot 逻辑”，而是：

- 有独立的 agent runtime
    
- 有多 agent 路由
    
- 有 per-agent 隔离边界
    

它已经具备平台层对 runtime 的抽象。

## 8.2 当前 runtime 的现实情况

 OpenClaw 的演化方向不是“继续往现有 runtime 里硬塞功能”，而是：

> 平台层与 runtime 层逐步解耦。

这对系统笔记很重要，因为它对应一个更一般的设计趋势：

- 平台层负责 session、routing、permissions、channels、control plane
    
- runtime 层负责策略执行与工具使用
    

---

# 9 Pi：OpenClaw 下面那层“极简 runtime”

Armin Ronacher 的文章直接指出：OpenClaw 底下跑的是一个叫 Pi 的 coding agent。文章还给出 Pi 的两个核心特点：

- 核心非常小，工具极少
    
- 通过扩展系统弥补能力，并允许扩展把状态写入 session
    

文章中提到 Pi 的核心工具只有四个：Read、Write、Edit、Bash。

## 9.1 这和常见 Agent 的差异

很多 Agent 走的是“预置很多工具 + 很长系统 prompt”的路线。  
Pi 更像反过来：

- 核心尽量小
    
- runtime 和扩展机制来承担复杂性
    
- 状态写入 session 文件
    
- 强调 agent 能自我扩展
    

## 9.2 对 OpenClaw 的启发

这解释了为什么 OpenClaw 很强调：

- Gateway
    
- Session
    
- Tool streaming
    
- Nodes
    
- Workspace isolation
    

因为如果 runtime 核心刻意保持极简，那么平台层就必须承担更多环境接入和状态组织能力。

---

# 10 Tools：工具系统

官方文档在架构总览里明确列出 Tools，并举例说明包括 browser control、canvas、nodes、cron jobs 和 automation。

## 10.1 为什么这里的工具系统重要

OpenClaw 的工具不是只给模型“多几个函数”。

它们更像是平台能力的外露接口，覆盖：

- 软件环境控制
    
- 可视化工作区
    
- 节点设备调用
    
- 自动化调度
    
- 长时任务触发
    

因此它体现的不是单轮 function calling，而是：

> Agent 平台如何把执行能力组织成一个统一工具面。

## 10.2 工具系统的工程含义

一旦工具不再只是“查天气”这类轻操作，而开始覆盖 browser、system、automation、nodes，系统风险就会陡增。  
这也是 OpenClaw 这类平台比普通聊天助手更需要安全边界的原因。

---

# 11 Nodes：设备与外围执行面

官方 nodes 文档把 node 定义为 companion device，可以是 macOS、iOS、Android 或 headless 设备；它连接 Gateway 的 WebSocket，并暴露如 `canvas.*`、`camera.*`、`device.*`、`notifications.*`、`system.*` 这样的命令面。

## 11.1 结构上怎么理解

Node 不是 gateway。  
OpenClaw 把执行面拆成了两层：

- Gateway：控制面
    
- Node：设备侧能力暴露面
    

## 11.2 一个非常有用的抽象

文档还说明，当 gateway 跑在一台机器、而命令需要在另一台机器执行时，可以用 node host；模型仍和 gateway 对话，gateway 再把 `exec` 类调用转发给 node host。

这件事很有系统味道。  
它说明 OpenClaw 不是简单地“本机调命令”，而是在向**分布式 agent execution** 走。

---

# 12 Multi-Agent Routing：从单 agent 到平台调度

GitHub 仓库首页把 multi-agent routing 作为一等能力来展示，并说明可以把不同 inbound channels、accounts、peers 路由到隔离的 agents。

## 12.1 这件事意味着什么

这意味着 OpenClaw 至少在平台设计上已经承认：

- 不同场景需要不同 agent
    
- 不同工作空间需要隔离
    
- session 不应混在一起
    
- routing 需要平台层处理
    

这和很多“所有任务塞给一个超级 agent”的想法不同。  
它更接近一种现实工程取向：

> 不追求一个万能 agent，而是追求可管理的多 agent 编排。

---

## 12.2 OpenClaw 与通用 Agent 抽象的映射

如果把 OpenClaw 映射到 `Agent = Policy Core + Memory + Tools + Planner/Controller + Runtime` 这个抽象里，可以大致对应为：

- Policy Core：Pi runtime 或其他未来 runtime
    
- Memory：sessions + workspace state
    
- Tools：browser / canvas / nodes / cron / automation
    
- Planner/Controller：runtime + gateway routing + execution orchestration
    
- Runtime：gateway + agent runtime + platform apps + node execution surface
    

这个映射说明：

> OpenClaw 更像一个承载 Agent 的系统框架，而不是某个特定推理方法。

---

## 12.3 它和普通 Tool-Calling Assistant 的差异

普通 tool-calling assistant 一般是：

- 单入口
    
- 单会话
    
- 工具轻量
    
- 多为单轮或短链
    
- 缺少长期运行能力
    

而 OpenClaw 更强调：

- 多渠道
    
- 持久会话
    
- 设备节点
    
- 长期运行
    
- 自动化触发
    
- 多 agent 路由
    
- 平台控制面
    

所以二者差别不只是“功能多少”，而是系统级别差异：

- 一个更像函数调用增强的助手
    
- 一个更像本地优先的 agent 平台
    

---
# 13 对 Agent 设计的启发

OpenClaw 这个案例最有价值的，不是平台本身多热，而是它揭示了几件相当稳定的系统规律。

## 13.1 Agent 需要控制面

没有控制面，渠道、会话、工具、节点、自动化会散成一地零件。  
OpenClaw 用 Gateway 把这些东西收拢到一起。

## 13.2 Agent 需要长期状态

单轮 prompt 无法支撑长期任务。  
session、workspace 和持久状态是 Agent 连续性的基础。
### 13.2.1 Agent 平台层与 runtime 层会逐渐解耦

社区已经在讨论把 AgentRuntime 抽象出来、接入其他 runtime。  
这说明“平台承载什么”和“策略核心是谁”正在分离。

## 13.3 高权限 Agent 的主风险不在回答，而在执行

当系统能跑命令、调设备、操作渠道时，核心问题不再只是模型精度，而是：

- 谁能触发
    
- 触发后能做什么
    
- 结果如何审计
    
- 出错如何隔离
    

---

# 14 小结

OpenClaw 可以被看成一个典型的 **local-first Agent 平台案例**：

- Gateway 是控制面
    
- Sessions 承载状态
    
- Runtime 承载策略执行
    
- Tools 和 Nodes 提供执行能力
    
- Channels 和 Platform Apps 提供多入口
    
- Multi-agent routing 负责工作空间隔离和分发
    

因此，它最适合用来支撑这样一个观点：

> Agent 的关键不只是模型会不会思考，而是系统是否能稳定地管理状态、能力、入口、权限与执行面