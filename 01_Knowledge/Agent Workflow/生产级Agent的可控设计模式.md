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
  - 2026-07-02 用户提供的生产级 Agent 评测驱动工程化讨论
scope: 适用于需要把 LLM 工具调用、多步任务、暂停恢复、人类审批、状态管理和可审计执行结合起来的生产级 agent 或 agentic workflow。
risks:
  - 把 agent 设计误解为一个 prompt 加一组工具的黑箱循环
  - 把框架或 SDK 封装误认为可以替代控制流、权限、状态和副作用治理
  - 将外部演讲中的 12-Factor Agents 原样搬入内部知识，忽略本地 plugin、contract、review 和 writeback 边界
  - 将所有任务都 agent 化，导致固定流程成本升高、可预测性下降
  - 只看总通过率或平均分数，掩盖高风险工具误调用、权限越界、关键业务场景退化和不可逆副作用
  - 只建设复杂 agent 架构，不建设评测、Verifier、降级、灰度、bad case 回流和回滚机制
evidence:
  - 外部 12-Factor Agents 方法论、Anthropic agent 工程建议与 OpenAI Agents SDK 文档均强调应用侧需要拥有 orchestration、tool execution、state、approval 或工具接口边界
  - 本地已验证知识表明，高风险协作系统需要 runtime gate、review 独立性、contracts-first truth source 和窄边界 skill
  - 候选评估已将过时风险改写为现代 SDK/MCP/guardrail/eval 可兼容的内部设计模式
updated_at: 2026-07-02
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

## 0.5 评测驱动的生产生命周期

生产级 agent 的可靠性不能只靠更复杂的 ReAct、Plan-and-Execute 或多 agent 架构获得。更稳的主线是：

1. 先定义任务边界和可观测目标。
2. 构建分层评测集。
3. 对 Direct、Single Tool、ReAct、Plan-and-Execute 等候选架构跑基线。
4. 选择满足目标的最小可行架构。
5. 用 Verifier、工具治理和降级机制约束运行。
6. 通过灰度日志和线上 bad case 反哺评测集。
7. 用发布门禁和回滚标准控制迭代。

这套机制的合理性在于：agent 失败通常不是单点错误，而是意图识别、任务拆解、工具选择、参数构造、中间结果解释、最终输出合成和约束遵守共同构成的状态机失败。没有评测和 trace，优化会退化成主观调 prompt。

### 0.5.1 分层评测集

50 到 100 条黄金用例适合作为 MVP 基线，但不应被视为稳定覆盖。生产级评测集应分层维护：

| 层级 | 覆盖内容 | 目的 |
|---|---|---|
| L0 基础能力 | 单轮问答、明确工具调用、简单抽取、格式遵守 | 建立最低能力基线 |
| L1 任务型 | 多步骤推理、多工具组合、参数约束、中间状态依赖 | 验证主流程是否可完成 |
| L2 异常与边界 | 输入缺失、工具空结果、工具超时、工具冲突、上下文矛盾、违规请求 | 验证失败路径和恢复 |
| L3 线上 bad case | 灰度期间采集、人工标注、固化回归 | 防止已知失败复发 |

每条样本至少应包含：用户输入、必要上下文、期望行为、约束、评分标准、风险等级和是否进入发布门禁。

### 0.5.2 可解释指标

单一通过率不足以衡量 agent。应拆成可归因指标：

| 指标 | 判断问题 |
|---|---|
| Task Success | 是否解决用户任务 |
| Constraint Following | 是否满足格式、安全、权限和业务边界 |
| Tool Accuracy | 是否选择正确工具、构造正确参数、避免不必要调用 |
| Process Stability | 是否避免循环、重复调用、过度规划和上下文漂移 |
| Output Quality | 是否清晰、完整、符合用户期望 |
| Risk Severity | 失败是否触及危险动作、业务关键错误或普通质量问题 |

更适合作为发布判断的形式是：

```text
总分 = 任务完成分 × 约束门禁 × 风险惩罚
```

其中约束门禁必须优先于平均分。例如触发 P0 风险时，即使总通过率提升，也不得发布。

## 0.6 架构、工具、验证与降级

### 0.6.1 按任务路由选择最小架构

ReAct 与 Plan-and-Execute 不是二选一。架构应由任务动态性、顺序约束、风险等级和恢复要求决定：

| 任务形态 | 推荐架构 |
|---|---|
| 简单确定任务 | Direct Answer 或 Single Tool |
| 中等动态任务 | ReAct |
| 复杂确定任务 | Plan-and-Execute |
| 复杂且动态任务 | Plan + ReAct substeps + Verifier |
| 高风险任务 | Planner + Executor + Policy Guard + Human Approval |

选择规则不是“越复杂越 agent”，而是“满足目标的最小可行架构”。固定流程能稳定解决的问题优先使用 workflow；步骤不可预知、工具返回会改变后续路径时，再引入更自主的 agent。

### 0.6.2 工具按任务路径最小暴露

“工具少”是正确方向，但不应机械限制整个系统只能有 2 到 3 个工具。更稳的规则是：

- 全局工具可以多。
- 当前任务路径只暴露 2 到 3 个核心工具。
- 通过 router 或 capability scope 控制可见工具集。
- 工具增删必须跑回归。

工具注册至少应记录：工具名称、功能边界、输入 schema、输出 schema、副作用等级、权限等级、幂等性、超时策略和错误码规范。

只读工具与写入工具必须分开治理：

| 工具类型 | 例子 | 默认策略 |
|---|---|---|
| 只读工具 | search、retrieve、query | 可自动调用，但要处理空结果和冲突结果 |
| 低风险写工具 | 创建草稿、保存临时记录 | 可自动执行并记录 trace |
| 中风险写工具 | 发送通知、提交表单 | 执行前摘要确认 |
| 高风险写工具 | 删除、支付、生产写回、权限变更 | 必须人工确认 |
| 不可逆动作 | 永久删除、资金划转等 | 默认禁止自动执行 |

### 0.6.3 Verifier 是核心路径

生产级 agent 不应只依赖生成侧。关键链路应增加 Verifier：

```text
Agent output -> Verifier -> pass -> return
                         -> fail -> repair / degrade / ask human
```

Verifier 可以分层实现：

| 验证层 | 适用内容 |
|---|---|
| 规则校验 | JSON schema、字段完整性、数值范围、权限检查 |
| 程序校验 | 单元测试、API dry-run、SQL explain、静态检查 |
| 模型校验 | 语义一致性、答案完整性、多约束判断 |

高风险场景中，Verifier 是必要组件，不是可选优化。

### 0.6.4 降级策略必须显式建模

agent 不可能完全避免失败，因此失败后的状态转移必须被设计出来：

| 失败类型 | 推荐降级 |
|---|---|
| 工具失败 | 重试一次、换备用工具、返回可解释失败或请求补充信息 |
| 置信度低 | 缩小回答范围、声明不确定性、提供可验证路径或转人工 |
| 上下文冲突 | 优先最新用户指令，标记冲突字段，请求确认关键参数 |
| 高风险动作 | 不自动执行，生成草稿，等待确认 |
| 权限不足 | 停止执行，说明需要的权限或审批 |

没有降级策略的 agent 容易在异常路径上幻觉补全，或反复调用工具。

## 0.7 验证、灰度与发布门禁

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
- Verifier 是否能捕获格式、权限、约束和工具结果一致性问题

只验证 happy path 不足以证明 agent 可上线。负向测试必须覆盖越权、误路由、重复提交、审批缺失、工具误用、状态恢复失败、工具超时、空结果和上下文矛盾。

### 0.7.1 bad case 回流

线上 bad case 不能只靠人工翻日志，应形成标准闭环：

```text
线上日志采集
-> 自动聚类
-> 人工标注
-> 归因分类
-> 加入评测集
-> 修复 prompt / router / tool schema / data / policy
-> 离线回归
-> 小流量灰度
-> 指标对比
-> 放量或回滚
```

bad case 至少应标注：用户输入、上下文、模型输出、工具调用轨迹、工具返回、失败类型、严重等级、预期行为、修复策略和是否加入回归集。

失败类型建议固定化：

| 类型 | 含义 |
|---|---|
| IntentError | 意图理解错误 |
| PlanError | 任务拆解错误 |
| ToolSelectionError | 工具选择错误 |
| ToolParamError | 参数构造错误 |
| ToolRuntimeError | 工具失败处理错误 |
| ContextError | 上下文引用错误 |
| ConstraintError | 约束未遵守 |
| Hallucination | 幻觉 |
| SafetyError | 安全或权限问题 |
| FormatError | 输出格式错误 |
| LatencyError | 耗时过长 |

### 0.7.2 发布与回滚门禁

发布标准不应是“平均分上涨”。更稳的判断是：

- 关键安全指标不退化。
- 核心业务指标提升或至少不低于基线。
- 成本和延迟在预算内。
- 灰度 bad case 可控。
- 可快速回滚到上一版本。

硬门禁：

- P0 case = 0。
- 高风险工具误调用 = 0。
- 权限越界 = 0。
- 关键业务场景不低于基线。

软指标：

- 总任务完成率提升。
- 平均工具调用次数不显著增加。
- 平均延迟不显著增加。
- token 成本不显著增加。
- 用户满意度不下降。

回滚条件：

- 线上触发 P0。
- P1 错误率超过阈值。
- 延迟超过 SLA。
- 成本超过预算。
- 投诉率异常上升。

## 0.8 提升判断

12-Factor Agents 的价值不在于原样复述 12 条原则，而在于抽象出一组稳定工程判断：

- agent 是软件系统，不是纯 prompt
- LLM 适合生成候选意图，不适合独占执行权
- context、state、control flow 和 tools 都必须被工程化管理
- 人类审批、review 和恢复应是一等路径
- 框架可以降低接入成本，但不能替代治理边界
- 生产级 agent 的核心竞争力不只是复杂架构，而是评测驱动、工具治理、验证闭环、发布门禁和可回滚迭代

因此该候选内容可以升级为正式知识，但升级后的知识应绑定内部已验证的 runtime gate、contracts-first、skill 边界和 review 独立性规则，而不是作为外部视频摘要保存。
