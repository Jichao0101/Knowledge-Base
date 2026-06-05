# HumanLayer human layer 与 subagent workflow 原则候选条目

- 状态: partially_promoted
- 类型: candidate_knowledge
- 来源:
  - YouTube: No Vibes Allowed: Solving Hard Problems in Complex Codebases - Dex Horthy, HumanLayer, https://www.youtube.com/watch?v=rmvDxxNubIg&t=33s
  - Transcript mirror: https://www.youtubetranscript.dev/zh/transcript/rmvDxxNubIg/no-vibes-allowed-solving-hard-problems-in-complex-codebases-dex-horthy-humanlaye
  - Summary mirror: https://summarizeyoutubevideo.com/video/no-vibes-allowed-solving-hard-problems-in-complex-codebases-dex-horthy-humanlayer-rmvDxxNubIg
- 可能目标路径: 01_Knowledge/Agent Workflow/
- 已升格路径: `01_Knowledge/Agent Workflow/Human layer 的合理性与边界.md`
- 升格说明: 仅升格窄化版本，即“外部资源启发下的 human layer 合理性与边界建议”。该升格结果属于 reviewed advisory / external inspired pattern，不等同于项目泛化后的 verified knowledge；subagent-first workflow 和 subpower 只作为 human layer 适用场景的参照，不是升格知识主体。
- 适用主题: agentic coding workflow, context engineering, human-in-the-loop, subagent workflow

## 摘要

HumanLayer 的这场分享把 AI coding agent 在复杂 brownfield codebase 中失败的主要原因归结为上下文管理失控，而不是单纯模型不够强。核心方法是通过 intentional compaction、Research-Plan-Implement workflow、人工高杠杆审查和受控 subagent 使用，让 agent 保持在更小、更正确、更完整、更低噪声的上下文中工作。

其中 human layer 的重点不是让人类逐行补救 agent 生成的代码，而是在研究结果、计划和关键决策点上保持 mental alignment。subagent 的重点也不是模拟组织架构中的前端、后端、QA 等角色，而是把高消耗的搜索和研究隔离到独立上下文里，只把压缩后的结论交还给主 agent。

## Human layer 原则

### 1. 人类负责判断，不外包思考

视频明确强调不要把思考外包给 AI。agent 可以放大已有思路，也会放大缺失的思路；如果研究或计划本身是错的，后续实现会把错误扩展成大量错误代码。

实践含义:
- 人类应审查研究结论是否基于真实代码路径。
- 人类应审查计划是否符合系统意图、架构边界和风险约束。
- 人类不应只在最终 PR 阶段做被动补救。

### 2. 人类审查应放在最高杠杆点

传统代码审查在 AI 大量生成代码后成本很高。HumanLayer 提出的思路是把人类介入前移到 research 和 plan 阶段，先确认方向，再让 agent 执行。

高杠杆审查点:
- research doc: 文件、行号、系统行为是否正确。
- plan doc: 改动步骤、测试策略、受影响文件是否具体可执行。
- implementation gate: 是否允许按计划进入实现。

### 3. Mental alignment 比逐行监督更重要

mental alignment 指团队和 agent 对问题、约束、计划和预期结果保持同一理解。计划文件是压缩意图的载体，比仅看最终 diff 更利于对齐。

适用方式:
- 用计划描述“为什么改、改哪里、怎么验证”。
- 让审查者在实现前识别错误假设。
- 对复杂任务，优先审查意图和路径，而不是等到大量代码生成后再审查结果。

### 4. 根据任务复杂度调整 human layer 强度

human layer 不应成为所有任务的固定重流程。简单 UI 或小修可以直接交互；跨模块、中大型、brownfield 任务需要 research、plan 和明确 review gate。

建议分层:
- 简单任务: 直接交互即可。
- 小功能: 简短计划即可。
- 中等跨模块任务: research + plan。
- 复杂 brownfield 任务: 完整 RPI workflow + 人工审查 research/plan。

## Subagent workflow 优势

### 1. 隔离上下文污染

subagent 的主要价值是上下文管理。主 agent 不必携带大量搜索过程、无关文件、工具输出和中间推理，只接收 subagent 压缩后的结论。

收益:
- 主上下文更小。
- 无关搜索轨迹不污染主 agent 的后续决策。
- 减少因为上下文过大进入性能下降区间的概率。

### 2. 让 research 成为可压缩产物

subagent 适合承担“查找真实代码路径、定位相关文件、归纳系统行为”的 research 工作。它的交付物应是精简结论，而不是完整搜索日志。

好的 subagent 输出应包含:
- 关键文件和行号。
- 与任务有关的系统行为。
- 已排除的错误路径。
- 仍不确定的问题。

### 3. 支持 Research-Plan-Implement 的阶段化工作

RPI workflow 本质是频繁 intentional compaction:
- Research: 从代码中压缩事实。
- Plan: 从事实和需求中压缩执行意图。
- Implement: 从计划中执行改动。

subagent 在 Research 阶段尤其有价值，因为它可以消耗大量探索上下文，而不把这些上下文全部带入 Plan 和 Implement。

### 4. 避免把 subagent 当组织角色拟人化

视频中特别提醒，不应因为听起来完整就创建 front-end、backend、QA、data scientist 等拟人化 subagent。subagent 的判断标准应是是否能降低上下文复杂度，而不是是否像团队分工。

适用判断:
- 需要大范围搜索但主 agent 只需要摘要: 适合 subagent。
- 需要并行探索多个独立假设: 适合 subagent。
- 只是为了“看起来多智能体”: 不适合。

## 可复用模式

```text
Human request
  -> Main agent clarifies objective and boundaries
  -> Research subagent(s) gather code facts in isolated contexts
  -> Main agent compacts findings into research doc
  -> Human reviews research for correctness
  -> Main agent writes implementation plan
  -> Human reviews plan for intent and risk
  -> Main agent implements
  -> Tests and final review
```

## 适用范围

适合:
- 复杂 brownfield codebase。
- 多模块、多文件、多约束的软件变更。
- 需要保留架构判断和团队对齐的 agentic coding workflow。
- agent 容易被长上下文、工具输出、历史错误轨迹带偏的任务。

不适合:
- 极小的机械修改。
- 无法提供可靠代码事实来源的任务。
- 缺少人类 review 能力或 review gate 无法执行的团队。
- 只追求多 agent 形式而没有上下文隔离收益的流程。

## 风险与边界

- research doc 可能压缩错误事实；必须保留来源文件、行号和不确定项。
- plan 越长通常越可靠，但可读性下降，需要控制粒度。
- subagent 输出若未经主 agent 或人类校验，可能把错误结论伪装成压缩事实。
- markdown 文件不是自动可信的记忆系统，维护不当会随时间引入过期信息。
- human layer 不能流于形式；若只签字不审查，错误仍会放大。

## 提升到正式知识区的条件

当前条目来自外部视频和第三方转录/摘要，尚未经过内部验证，不应直接进入 `01_Knowledge/`。

提升前至少需要:
- 用本地 agent workflow 实例验证 RPI + subagent 隔离是否有效。
- 补充一个内部案例，说明 review gate 放在 research/plan 阶段的收益。
- 明确与现有 workflow plugin 或 current 文档组规则的关系。
- 记录失败案例或不适用范围。
