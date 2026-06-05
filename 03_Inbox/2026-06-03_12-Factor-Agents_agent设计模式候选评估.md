# 1 12-Factor Agents agent 设计模式候选评估

- 状态：promoted
- 来源：YouTube 视频与 HumanLayer 公开仓库
- 原始视频：https://www.youtube.com/watch?v=8kMaTybvDUw
- 公开仓库：https://github.com/humanlayer/12-factor-agents
- 来源证据卡：`04_Sources/Agent工程化/2026-06-03_12-Factor-Agents_来源证据卡.md`
- 可能目标路径：`01_Knowledge/Agent Workflow/Agent工程化设计模式.md`
- 实际提升路径：`01_Knowledge/Agent Workflow/生产级Agent的可控设计模式.md`
- 提升日期：2026-06-03

## 1.1 结论

值得写入知识库，但不建议直接把“12-Factor Agents”原样作为正式知识条目。更合适的方式是将其改写成内部可复用的 agent 工程化模式，并补充本地 workflow/plugin 的运行治理边界。

已提升为正式知识，但提升内容采用内部工程化改写，不原样复制 12-Factor Agents。

## 1.2 仍然可用的模式

### 1.2.1 LLM 负责意图生成，业务代码负责执行

可用。LLM 将自然语言、上下文和历史转为结构化 intent/tool call；应用代码负责权限、执行、重试、错误处理和副作用提交。

适用场景：工具调用、工作流路由、代码助手、客服工单、数据处理编排。

风险：不能把结构化输出等同于可靠执行；schema 校验、权限校验和执行结果回写仍必须在代码侧完成。

### 1.2.2 拥有 prompt 与 context window

可用，而且仍是核心。prompt、上下文构造、RAG、历史压缩、错误摘要、工具结果裁剪都应由系统显式管理。

适用场景：长任务、多轮工具执行、需要可恢复和可审计的 agent。

风险：现代长上下文降低了部分压缩压力，但没有消除上下文污染、优先级冲突和无关历史干扰。

### 1.2.3 工具是结构化输出，不是魔法动作

可用。工具定义应被视为 agent-computer interface，需要像 API 文档一样设计参数、边界、示例和错误语义。

适用场景：MCP tools、function calling、shell/file/browser/database 操作。

风险：现代 SDK 会封装工具协议，但不会替代工具语义设计。

### 1.2.4 应用拥有控制流

可用。核心 loop、分支、暂停、恢复、审批、最大轮次、失败退出条件应由应用控制。

适用场景：生产工作流、代码修改、财务/医疗/权限敏感任务。

风险：对开放式探索任务，过度固定控制流会降低 agent 的发现能力；需要保留有限自主窗口。

### 1.2.5 启动、暂停、恢复与人类审批

可用。agent 应能在外部事件、人工审批、异步结果、失败恢复后继续执行，而不是依赖一次长会话。

适用场景：审批流、异步任务、长时间运行任务、需要人工确认的副作用操作。

风险：必须区分执行状态、业务状态、外部副作用状态，避免重复提交或恢复后越权执行。

### 1.2.6 小而聚焦的 agent

可用，但要补充 ownership 规则。小 agent 有利于 prompt 聚焦、测试和责任清晰；多 agent 场景还需要 handoff contract、最终决策者和独立 review 边界。

适用场景：review agent、planner agent、executor agent、retriever agent、specialist 工具代理。

风险：拆得过细会引入协调成本、上下文丢失和责任漂移。

### 1.2.7 Stateless reducer

部分可用。将 agent step 建模为 `new_state = reducer(previous_state, event)` 有利于重放、审计、恢复和测试。

适用场景：事件驱动 agent、可恢复工作流、需要审计的自动化任务。

风险：长期记忆、用户偏好、外部系统状态、不可逆副作用不能被简单看作 stateless；需要额外持久化和幂等机制。

## 1.3 需要更新或避免误用的部分

- 不应把“不要用框架”理解为禁用 SDK。2026 年的 agent SDK、MCP、tracing、sandbox、guardrail、eval 工具已经更成熟，合理使用可以降低工程成本。
- 不应把“structured JSON”限定为手写 JSON。现代 structured outputs、tool calling、schema parser、typed SDK 都可承担这部分能力。
- 不应只关注 agent loop，还要补充安全、观测、评测、成本、权限、沙箱和数据边界。
- 不应把所有任务都 agent 化。固定流程优先用 workflow，开放式且步骤不可预知时才使用更自主的 agent。

## 1.4 建议沉淀为正式知识的主题

建议正式知识标题：`生产级 Agent 的可控设计模式`

建议核心命题：

生产级 agent 不是“全自动黑箱循环”，而是由确定性软件拥有控制流、状态、权限和副作用，由 LLM 在受约束的上下文中生成候选意图、结构化调用或局部判断。

建议正式知识结构：

1. 适用范围：长任务、多步工具调用、需要恢复/审计/审批的 LLM 应用。
2. 核心模式：typed intent、explicit context、owned control flow、recoverable state、human approval、tool interface design、small specialists、eval and tracing。
3. 不适用范围：一次性问答、固定确定性流程、无可验证反馈的高风险自动执行。
4. 风险：上下文污染、工具误用、权限越界、恢复重复执行、多 agent 责任不清、框架黑箱。
5. 验证方式：trace review、tool-call eval、恢复重放测试、人工审批路径测试、失败注入测试。

## 1.5 提升阻塞项

- 需要补充至少一个本地 agent workflow 案例，验证这些模式与本地 cutepower/subpower/知识库工作流的边界一致。
- 需要审核是否与现有 `01_Knowledge/Agent Workflow/` 文档重复或冲突。
- 需要在正式条目中明确现代 SDK/MCP/托管 agent builder 的适用位置，避免形成“框架一律不可用”的过时结论。
