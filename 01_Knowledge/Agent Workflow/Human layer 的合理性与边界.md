# 1 Human layer 的合理性与边界

- 状态: reviewed_advisory
- 类型: external_inspired_pattern
- 来源:
  - 外部启发: No Vibes Allowed: Solving Hard Problems in Complex Codebases - Dex Horthy, HumanLayer, https://www.youtube.com/watch?v=rmvDxxNubIg&t=33s
  - 候选条目: `03_Inbox/HumanLayer human layer 与 subagent workflow 原则候选条目.md`
- 相关内部依据:
  - subpower runtime 规范: `/home/jichao/.codex/plugins/cache/personal-local/subpower/0.1.0/skills/using-subpower/SKILL.md`
- 适用范围: agentic coding workflow、复杂任务治理、需要 research/plan/review/closure 判断的流程
- 不适用范围: 简单机械任务、无明确审查对象的口头确认、把人类介入当作形式化签字的流程

## 1.1 摘要

human layer 的合理性不在于让人类逐行替 agent 修补输出，而在于把人类判断放到高杠杆决策点：研究结论是否可信、计划是否符合目标、证据是否足够、review 是否独立、closure 是否成立、知识写回是否越界。

当 agent workflow 变复杂时，错误更容易被上下文压缩、自动执行和多阶段交接放大。human layer 的作用是阻断错误假设继续扩散，并把主观判断落到可审查的 artifact 上。

本条目属于外部启发型建议，不声明其效果已由真实本地 workflow 实证。subagent-first workflow 和 subpower 只作为 human layer 适用场景的内部参照，不是本文的知识主体。

## 1.2 合理性

### 1.2.1 Agent 会放大已有思路，也会放大错误思路

agent 的执行能力越强，错误前提造成的损失越大。若 research 误读代码、plan 误判边界、review 缺失独立性，后续实现会把这些问题扩展成更多代码、更多 artifact 和更难回滚的状态。

human layer 因此应优先审查“前提”和“方向”，而不是只在最终输出阶段做补救。

### 1.2.2 高杠杆审查优于末端补救

人类审查放在 research、plan、review、closure、writeback 等阶段，比只看最终 diff 更有效。

适合人类判断的问题包括:
- research 是否基于真实代码、日志或来源。
- plan 是否覆盖关键风险和验证路径。
- review 是否独立，是否遗漏行为回归。
- evidence 是否足够支撑 closure。
- knowledge writeback 是否把临时观察误升格为长期知识。

### 1.2.3 Human layer 需要具体承载物

没有 artifact 的 human layer 容易退化为口头确认。可审查对象可以是 research note、implementation plan、review decision、evidence manifest、closure matrix、writeback candidate 等。

artifact 的价值不是增加流程负担，而是让人类判断有对象、有边界、有证据引用。

### 1.2.4 Subagent workflow 增强了 human layer 的必要性

subagent 能隔离上下文和职责，但也会带来新的风险：每个 subagent 都可能压缩错事实、遗漏不确定项或把局部结论包装成确定结论。

因此在 subagent-first workflow 中，human layer 更适合出现在:
- research 汇总进入 plan 前。
- plan 进入 implementation 前。
- implementation 进入 validation 前。
- validation failed 进入 rework 前。
- closure 进入 knowledge writeback 前。

## 1.3 使用边界

human layer 适合:
- 任务存在高代价错误前提。
- 需要跨模块或跨侧状态判断。
- 有明确 artifact 可供审查。
- 需要独立 review、证据判断或 closure 判断。
- 存在知识写回或长期记忆污染风险。

human layer 不适合:
- 低风险、可快速回滚的机械修改。
- 没有实际审查者参与的流程。
- 只要求人类形式化批准而不提供证据对象。
- 把人类介入放到所有小任务上，导致流程成本高于风险收益。

## 1.4 判断准则

可以引入 human layer 时，应满足至少一个条件:
- 错误会跨阶段放大。
- 任务结果会进入长期状态，例如代码、board 配置、知识库或发布物。
- agent 需要把大量上下文压缩成结论。
- 后续执行依赖 research 或 plan 的正确性。
- 存在独立性要求，例如实现者和 reviewer 分离。

不应引入或应弱化 human layer 时:
- 任务目标和改动路径非常明确。
- 验证成本低且失败影响小。
- artifact 不能帮助判断，只会制造流程噪声。
- 人类没有足够上下文做有效判断。

## 1.5 反模式

- 把 human layer 理解为人类逐行修代码。
- 在最终结果阶段才发现 research 或 plan 已经错了。
- 把“用户同意继续”当作已完成审查。
- 没有 evidence refs，却要求人类批准 closure。
- 把外部建议直接当作本地 verified practice。
- 在 subagent workflow 中把多个角色输出直接串起来，中间没有 research/plan/review gate。

## 1.6 后续验证条件

若要把本条目从 reviewed advisory 升级为 verified pattern，需要至少补充:
- 一个真实本地 workflow 案例，说明 human layer 放在早期 gate 后减少了返工或阻断了错误。
- 对比没有 human layer 或只做末端 review 的失败案例。
- 明确哪些 artifact 对审查最有用，哪些只是流程噪声。
- 记录 human layer 过重导致效率下降的边界案例。
