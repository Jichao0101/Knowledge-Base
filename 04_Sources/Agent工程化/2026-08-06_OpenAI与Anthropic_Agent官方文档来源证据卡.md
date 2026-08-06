---
type: source_card
status: active
source_type: web
source: OpenAI 官方开发文档、OpenAI Agents SDK 官方文档、Anthropic 官方开发文档与官方工程/研究文章
summary: 为 AI-Career-Transition 的 Agent Systems 系统学习提供 Agent loop、工具、状态、编排、安全、可观测性、评测和长期运行的官方依据。
scope: Agent 开发概念框架、最小运行时、工具契约、上下文与记忆、单/多 Agent 编排、安全审批、轨迹评测及 DMS 证据任务实践。
risks:
  - OpenAI 与 Anthropic 的 SDK、API 字段、模型名和产品入口可能继续变化，编码前必须重新核对对应官方页面。
  - 两家文档使用的抽象层级不同；概念可对照，但 SDK 类型名和生命周期接口不可直接互换。
  - 官方案例说明可行模式，不自动证明其适合 DMS 高风险证据任务或满足生产可靠性要求。
updated_at: 2026-08-06
---

# 1 OpenAI 与 Anthropic Agent 官方文档来源证据卡

## 1.1 采集说明

- 访问日期：2026-08-06。
- OpenAI 获取方式：新注册的 `openaiDeveloperDocs` MCP，先搜索、再抓取官方 Markdown；本次 MCP 可用，未触发网页检索回退。
- Anthropic 获取方式：仅检索并读取 `platform.claude.com` 与 `anthropic.com` 官方开发、工程和研究页面。
- 未使用第三方来源。
- 本卡是外部来源证据整理，不是正式知识，也不代表内容已被学习者掌握或经过本地生产验证。

## 1.2 OpenAI 官方来源

| ID | 官方页面 | 本次采用的证据 | 适用版本 / 时效性风险 |
|---|---|---|---|
| OAI-01 | [Agents SDK](https://developers.openai.com/api/docs/guides/agents) | Agent 是会规划、调用工具、跨 specialist 协作并保持多步状态的应用；Responses API 由应用自管 loop，Agents SDK 由 SDK 管理 loop 和生命周期。 | 页面反映 2026-08-06 的 Python/TypeScript SDK 概念；API 与 SDK 能力可能更新。 |
| OAI-02 | [Agent definitions](https://developers.openai.com/api/docs/guides/agents/define-agents) | Agent 封装 model、instructions、tools、guardrails、handoffs 与 structured outputs；conversation history 与只供代码使用的 local run context 必须区分。 | 类型名在 Python/TypeScript 中不同；动态 instructions 与 output type 的具体接口需按当前 SDK 核对。 |
| OAI-03 | [Running agents](https://developers.openai.com/api/docs/guides/agents/running-agents) | Runner 执行 model → tool/handoff → next model 的循环；可用 history、session、conversation ID 或 previous response ID 延续状态；审批是 paused run，应从 state 恢复。 | 会话与恢复接口可能演化；选择一种 conversation strategy，避免重复注入上下文。 |
| OAI-04 | [Using tools](https://developers.openai.com/api/docs/guides/tools) | 工具扩展模型能力；应用仍需拥有自定义执行器、网络/权限边界和工具结果处理。 | 内置工具、tool search 和支持模型会变化；不得把示例模型名当作长期固定建议。 |
| OAI-05 | [Function calling](https://developers.openai.com/api/docs/guides/function-calling) | 函数调用是模型提出结构化调用、应用执行、返回结果、模型继续决策的往返协议。 | 请求/响应字段及 strict schema 支持范围需按当前 API 复核。 |
| OAI-06 | [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs) | Structured Outputs 约束输出匹配 JSON Schema；JSON mode 只保证合法 JSON，不保证符合业务 schema；仍需处理 refusal、截断和内容过滤。 | 支持的 JSON Schema 子集、嵌套和大小限制可能变化。 |
| OAI-07 | [Orchestration and handoffs](https://developers.openai.com/api/docs/guides/agents/orchestration) | handoff 让 specialist 接管对话；agents-as-tools 让 manager 保持最终答复所有权；仅在工具、策略、模型或责任边界实质不同后拆分。 | 具体 handoff filter、metadata 与 nested run 接口依语言版本而异。 |
| OAI-08 | [Guardrails and human review](https://developers.openai.com/api/docs/guides/agents/guardrails-approvals) | input/output/tool guardrails 做自动检查；有副作用或敏感动作应暂停并由人审批，再从同一 state 继续。 | guardrail 执行顺序、异常类型和 approval API 可能变化。 |
| OAI-09 | [Integrations and observability](https://developers.openai.com/api/docs/guides/agents/integrations-observability) | Agents SDK trace 可记录 model calls、tool calls、handoffs、guardrails 与 custom spans；先用 trace 调试，再形成系统评测。 | tracing 默认值、隐私设置和 dashboard 入口可能变化；敏感 payload 不应默认记录。 |
| OAI-10 | [Evaluate agent workflows](https://developers.openai.com/api/docs/guides/agent-evals) | 单条 trace 用于定位行为，稳定标准后再进入 dataset/eval run；可评估工具选择、handoff、指令/安全违规和端到端行为。 | 平台 eval 产品界面与 API 会变化；指标定义仍由任务合同负责。 |
| OAI-11 | [Trace grading](https://developers.openai.com/api/docs/guides/trace-grading) | trace grading 对决策、工具调用和步骤打结构化标签，能定位编排错误，不只看最终文本。 | grader 本身有误差，需与确定性检查和人工校准结合。 |
| OAI-12 | [Safety in building agents](https://developers.openai.com/api/docs/guides/agent-builder-safety) | 不可信内容不应进入高优先级指令；结构化输出、最小权限、工具审批、guardrails、trace graders 与 evals 需组合使用。 | 页面含 Agent Builder 退役信息；本卡只采用通用安全原则，不依赖该产品继续可用。 |

## 1.3 Anthropic 官方来源

| ID | 官方页面 | 本次采用的证据 | 适用版本 / 时效性风险 |
|---|---|---|---|
| ANT-01 | [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) | workflow 由预定义代码路径编排；agent 由模型动态决定过程和工具使用；优先选择能满足任务的最简单形态。 | 发布于 2024-12-19，是稳定架构原则，不是当前 Claude API 字段参考。 |
| ANT-02 | [How tool use works](https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works) | 工具是应用与模型之间的契约；client tool 的 canonical loop 是 `tool_use → execute → tool_result → continue`，并按 stop reason 退出。 | 适用于当前 Claude Platform 工具语义；server/client tool 清单和 stop reason 细节可能更新。 |
| ANT-03 | [Strict tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use) | `strict: true` 用 grammar-constrained sampling 保证工具名与输入符合支持的 JSON Schema 子集。 | 支持 schema 子集、数据保留和合规说明具有时效性，使用前需复核。 |
| ANT-04 | [Handle tool calls](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls) | `tool_use.id` 与 `tool_result` 必须正确关联；工具错误应以结构化错误返回，让模型或执行器决定后续。 | Tool Runner 处于 beta 的信息可能变化；需要自定义审批和日志时仍应理解手动 loop。 |
| ANT-05 | [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | 上下文是有限 attention budget；instructions、tools、外部数据、message history 都会竞争窗口，应检索、压缩、清理旧 tool results 并用外部 note 保持长期状态。 | 发布于 2025-09-29；具体模型窗口与 memory/tool 产品状态会变化。 |
| ANT-06 | [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) | orchestrator-worker 适合可并行、开放式、超单上下文的信息检索；协调成本和 token 成本显著，不适合高依赖共享上下文任务。 | 发布于 2025-06-13；文中性能数字只适用于其内部 research eval，不可外推到 DMS。 |
| ANT-07 | [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) | task、trial、grader、transcript/trace、outcome、eval harness 和 agent harness 必须区分；最终声称与环境最终状态可能不一致。 | 发布于 2026-01-09；案例和产品接口会变化，定义与评测原则相对稳定。 |
| ANT-08 | [Trustworthy agents in practice](https://www.anthropic.com/research/trustworthy-agents) | Agent 在自导 loop 中计划、行动、观察和调整；安全应同时约束 model、harness、tools 与 environment，并保留有意义的人类控制。 | 发布于 2026-04-09；产品权限界面不是通用 API 合同。 |

## 1.4 跨来源一致结论

1. 普通 LLM 调用只产生一次模型输出；workflow 的控制流主要由代码预定义；agent 的关键特征是模型能在受约束 loop 中根据中间结果选择下一动作。
2. 模型只提出工具调用，执行器才真正产生外部读取或副作用；schema 合法不等于业务允许。
3. 多 Agent 是责任、上下文或并行边界的工程选择，不是能力成熟度标签；单 Agent 能闭合时不应先拆分。
4. 上下文窗口、会话状态、持久记忆和外部知识是不同层；把全部历史塞回 prompt 会造成成本、注意力和污染问题。
5. 可靠性来自状态机、错误模型、权限、审批、幂等、恢复、trace 和 eval 的组合，不来自某一个 SDK 自动保证。
6. Agent 评测必须同时观察最终 outcome 和过程 trace；只看最终文本会漏掉错误工具、无依据结论和危险副作用。

## 1.5 概念差异与不可直接映射项

| 共同概念 | OpenAI 表达 | Anthropic 表达 | 不可直接映射处 |
|---|---|---|---|
| 自主循环 | Agents SDK runner / Responses 自管 loop | client tool loop / agent harness | stop reason、result block、run state 类型不同。 |
| 结构化工具 | function tool、JSON Schema、strict outputs | `tool_use`、`tool_result`、`input_schema`、strict tool use | wire format、schema 子集和 server tool 分类不同。 |
| 状态延续 | history、session、conversation、previous response、resumable state | messages、context editing、memory/note、SDK/tool runner 状态 | 存储责任、服务端状态和恢复 token 不可互换。 |
| 多 Agent | handoff、agents-as-tools | orchestrator-worker、subagents | handoff 的“答复所有权”是 OpenAI SDK 具体抽象；Anthropic 文章更偏架构模式。 |
| 安全 | guardrails、approvals、sandbox/MCP trust boundary | harness、permissions、human control、tool/environment boundary | guardrail hook 与权限产品界面不同。 |
| 可观测与评测 | traces、trace grading、datasets/eval runs | transcript/trajectory、grader、outcome、eval harness | 平台采集格式和 grader 产品接口不同。 |

## 1.6 使用边界

- 本卡允许支撑 `02_Projects/AI-Career-Transition/Agent开发系统学习文档.md`，不直接进入 `01_Knowledge/`。
- DMS 实践章节只能把现有任务当作设计场景，不得在未读 DMS 原始材料时写出新的 DMS 根因事实。
- 实现具体 SDK 示例前，应重新读取相应官方页面并固定依赖版本；本卡不替代依赖锁文件或 API contract test。
- 对 retry、timeout、幂等、durable execution 的工程细节，官方 SDK 提供部分机制，但最终策略必须由应用根据副作用和业务风险定义。
