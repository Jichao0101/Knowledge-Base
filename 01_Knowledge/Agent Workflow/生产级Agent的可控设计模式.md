---
type: knowledge
status: verified
unit_type: design_pattern
domain: 工程工作流
topic: 生产级Agent的可控设计模式
sources:
  - 03_Inbox/2026-06-03_12-Factor-Agents_agent设计模式候选评估.md
  - 04_Sources/Agent工程化/2026-06-03_12-Factor-Agents_来源证据卡.md
  - 01_Knowledge/Agent Workflow/运行时门禁与独立审查边界模式.md
  - 01_Knowledge/Agent Workflow/Plugin-first与Contracts-first治理插件设计模式.md
  - 01_Knowledge/Agent Workflow/Codex Skill开发与脚本化边界规范.md
scope: 适用于需要把 LLM 工具调用、多步任务、暂停恢复、人类审批、状态管理和可审计执行结合起来的生产级 agent 或 agentic workflow。
risks:
  - 把 agent 设计误解为一个 prompt 加一组工具的黑箱循环
  - 把框架或 SDK 封装误认为可以替代控制流、权限、状态和副作用治理
  - 将外部演讲中的 12-Factor Agents 原样搬入内部知识，忽略本地 plugin、contract、review 和 writeback 边界
  - 将所有任务都 agent 化，导致固定流程成本升高、可预测性下降
evidence:
  - 外部 12-Factor Agents 方法论、Anthropic agent 工程建议与 OpenAI Agents SDK 文档均强调应用侧需要拥有 orchestration、tool execution、state、approval 或工具接口边界
  - 本地已验证知识表明，高风险协作系统需要 runtime gate、review 独立性、contracts-first truth source 和窄边界 skill
  - 候选评估已将过时风险改写为现代 SDK/MCP/guardrail/eval 可兼容的内部设计模式
updated_at: 2026-06-03
summary: "生产级Agent的可控设计模式 相关的历史知识笔记，归入 Agent Workflow 主题，用于学习、查阅和工程参考。"
---

## 0.1 摘要

生产级 agent 不应被设计成“一个 prompt + 一袋工具 + 自主循环直到成功”的黑箱。

更稳定的形态是：确定性软件拥有控制流、权限、状态、副作用和恢复语义；LLM 在受控上下文中生成候选意图、结构化工具调用、局部判断或自然语言交互。

这不是反对 agent SDK 或 MCP。框架可以用于模型调用、工具协议、tracing、sandbox、guardrail、handoff 和 eval，但不能替代业务系统对控制流、状态、权限和审查边界的 ownership。

## 0.2 适用范围

适合以下场景：

- 多步工具调用任务
- 需要暂停、恢复、审批或异步等待的任务
- 需要审计、重放、失败注入和 trace review 的任务
- 需要在 workflow、agent、human reviewer 和外部系统之间保持边界的任务
- 步骤不完全可预知，但每一步执行都需要受权限和状态约束的任务

不适合以下场景：

- 单次问答或简单生成
- 固定确定性流程已经能稳定解决的问题
- 没有可验证反馈、却要求高风险自动执行的问题
- 责任边界不清的多 agent 自由协作

## 0.3 核心设计模式

### 0.3.1 LLM 生成意图，应用代码执行动作

LLM 的职责是把用户请求、上下文和历史转成结构化候选意图，例如：

- 调用哪个工具
- 需要哪些参数
- 是否需要澄清
- 是否需要人工审批
- 是否完成

应用代码的职责是：

- 校验 schema
- 校验权限
- 执行工具
- 处理重试和失败
- 写入状态
- 提交或拒绝副作用

不能把“模型输出了合法 JSON”视为“动作可以执行”。

### 0.3.2 显式拥有 context window

上下文不是聊天记录的自然累积，而是每一步运行时的输入构造结果。

系统应显式决定：

- 当前任务目标
- 可用工具和边界
- 已完成步骤
- 关键业务状态
- 最近错误和恢复提示
- 必要的检索结果
- 需要排除的噪声历史

长上下文模型降低了裁剪压力，但没有消除上下文污染、优先级冲突和无关历史干扰。

### 0.3.3 工具接口按 ACI 设计

工具不是普通函数暴露给模型那么简单。它是 agent-computer interface。

工具定义应包含：

- 单一清晰职责
- 明确参数和类型
- 可执行前置条件
- 禁止事项
- 错误语义
- 示例或边界说明
- 幂等或副作用约束

当多个工具相似时，参数名和描述必须帮助模型区分使用场景。工具接口越模糊，后续 guardrail 和 review 成本越高。

### 0.3.4 应用拥有控制流

核心循环、分支、暂停、恢复、审批、最大轮次、失败退出条件，应由应用或 workflow runtime 控制。

LLM 可以决定下一步候选动作，但不应独占：

- 是否允许执行
- 是否继续循环
- 是否越过审批
- 是否升级权限
- 是否写回最终结论

在高风险协作系统中，这些边界应进入 runtime gate 或 contracts，而不是停留在 prompt 描述。

### 0.3.5 状态必须可恢复、可审计、可幂等

agent 状态至少应区分：

- execution state：当前步骤、工具调用、等待项、错误
- business state：业务对象、需求、审批、决策
- external side-effect state：已经提交到外部系统的不可逆动作

将 agent step 建模为类似 reducer 的状态转换有利于重放和调试，但不能忽略长期记忆、用户偏好和外部副作用。恢复逻辑必须避免重复提交、越权继续或丢失人工审批结果。

### 0.3.6 人类审批是工具路径，不是异常路径

需要人工判断时，不应把人工介入当作失败或额外聊天，而应作为正常工具路径建模：

- 请求审批
- 请求澄清
- 请求 reviewer 裁决
- 等待外部确认
- 收到结果后恢复

审批结果进入状态后，后续步骤必须可追溯到该结果。

### 0.3.7 小而聚焦的 agent 需要 ownership 边界

小 agent 有利于 prompt 聚焦、工具收敛和验证。但多 agent 系统必须补充：

- 每个 agent 的职责
- handoff 输入输出
- 谁拥有最终回复
- 谁拥有写回权限
- reviewer 是否独立
- 证据不足时如何 blocked

没有 ownership 的多 agent 拆分会把复杂度从单 agent 推理转移到协调和责任漂移上。

## 0.4 与 workflow / SDK / plugin 的关系

固定流程优先使用 workflow。  
步骤不可预知、需要模型动态选择路径时，再引入更自主的 agent。

SDK、MCP 和托管 workflow 适合承担：

- 模型调用
- 工具协议
- tracing
- sandbox
- guardrail
- handoff
- eval
- hosted UI 或 ChatKit 类集成

但以下内容仍应由业务系统或治理插件拥有：

- route
- role
- state transition
- approval gate
- reviewer independence
- writeback level
- external side-effect policy

## 0.5 验证方式

生产级 agent 设计至少应验证：

- 工具调用 schema 校验是否稳定拒绝非法参数
- 无权限动作是否被 runtime gate 拒绝
- 人工审批缺失时是否暂停而不是继续
- 错误结果是否被压缩进下一步上下文
- pause/resume 是否能恢复必要状态
- 已提交副作用是否不会重复执行
- 多 agent handoff 后最终 ownership 是否明确
- reviewer 是否只读取最小证据包
- trace 是否能解释关键决策和工具调用

只验证 happy path 不足以证明 agent 可上线。负向测试必须覆盖越权、误路由、重复提交、审批缺失、工具误用和状态恢复失败。

## 0.6 提升判断

12-Factor Agents 的价值不在于原样复述 12 条原则，而在于抽象出一组稳定工程判断：

- agent 是软件系统，不是纯 prompt
- LLM 适合生成候选意图，不适合独占执行权
- context、state、control flow 和 tools 都必须被工程化管理
- 人类审批、review 和恢复应是一等路径
- 框架可以降低接入成本，但不能替代治理边界

因此该候选内容可以升级为正式知识，但升级后的知识应绑定内部已验证的 runtime gate、contracts-first、skill 边界和 review 独立性规则，而不是作为外部视频摘要保存。
