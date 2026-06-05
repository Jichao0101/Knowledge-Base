# 1 12-Factor Agents 来源证据卡

- 标题：12-Factor Agents: Patterns of reliable LLM applications
- 视频：Dex Horthy, HumanLayer, AI Engineer World's Fair
- 原始链接：https://www.youtube.com/watch?v=8kMaTybvDUw
- 公开项目：https://github.com/humanlayer/12-factor-agents
- 状态：source_note
- 记录日期：2026-06-03

## 1.1 摘要

该视频主张：生产级 agent 不应主要依赖“一个 prompt + 一袋工具 + 自主循环直到成功”的黑箱模式，而应把 LLM 作为可控软件系统中的若干步骤。核心倾向是：显式拥有 prompt、上下文、控制流、状态、工具执行、人类审批、错误恢复和观测边界。

公开仓库给出的 12 个 factor：

1. Natural Language to Tool Calls
2. Own your prompts
3. Own your context window
4. Tools are just structured outputs
5. Unify execution state and business state
6. Launch/Pause/Resume with simple APIs
7. Contact humans with tool calls
8. Own your control flow
9. Compact Errors into Context Window
10. Small, Focused Agents
11. Trigger from anywhere, meet users where they are
12. Make your agent a stateless reducer

## 1.2 交叉参考

- Anthropic 的 “Building effective agents” 同样建议从简单方案开始，在确有收益时再增加 agentic complexity；区分 workflow 与 agent；强调工具接口、透明规划、人类检查点、测试和沙箱。
- OpenAI Agents SDK 文档将 agent 描述为会规划、调用工具、跨 specialist 协作并保留足够状态的应用；其 code-first 路径要求应用侧拥有 orchestration、tool execution、approvals 和 state。

## 1.3 初步判断

该资料不是“过时框架教程”，而是 agent 工程化原则。随着 2026 年 SDK、MCP、托管 workflow、reasoning model 能力增强，部分实现细节已变化，但核心设计约束仍可用。

不应原样提升为正式知识。更适合整理为内部工程模式：可控 agent = deterministic control flow + typed intent/tool output + explicit context/state + recoverable pause/resume + eval/observability + human approval boundary。

## 1.4 风险与边界

- 资料来自演讲和开源方法论，仍需结合本地 agent workflow 经验验证。
- 不能把“少用框架”绝对化；现代 SDK 在 tracing、guardrail、handoff、sandbox 和 hosted tools 上已有价值。
- “stateless reducer”适合恢复、重放、调试，但对长期记忆、用户偏好、异步外部副作用需要额外建模。
- “small focused agents”不能替代明确的跨 agent ownership、handoff contract 和最终责任边界。
