---
type: source_card
status: active
source_type: paper
source: https://arxiv.org/abs/2603.03565
summary: Build, Judge, Optimize 论文与视频主题相关，提供多智能体消费助手的评估、LLM-as-a-Judge 校准和 GEPA 优化框架。
scope: Agent 工程化、LLM-as-a-Judge、GEPA、multi-agent optimization
risks:
  - YouTube 视频字幕未能直接获取，本卡以论文 HTML/PDF 和 arXiv 摘要为可核验依据。
  - 论文场景是购物助手，迁移到 DMS 问题分析 agent 时需要重新定义领域 trace、rubric 和安全约束。
updated_at: 2026-06-30
---

# 1 Build, Judge, Optimize agent 理论来源证据卡

## 1.1 来源

- 视频触发来源：https://www.youtube.com/watch?v=X4dEHRzBLmc&t=575s
- 主要可核验来源：https://arxiv.org/abs/2603.03565
- HTML 阅读缓存来源：https://arxiv.org/html/2603.03565v2
- 方法补充来源：https://arxiv.org/abs/2507.19457

## 1.2 核心事实摘记

`Build, Judge, Optimize: A Blueprint for Continuous Improvement of Multi-Agent Consumer Assistants` 讨论生产级多智能体购物助手从原型到上线后的两个工程难点：

1. 多轮、工具密集、偏好敏感的交互不能只用检索或排序指标评价，需要轨迹级 rubric。
2. 单独优化子 agent 不一定改善端到端质量，因为错误会延迟显现，并且存在跨 agent 耦合。

论文提出的主线是：

1. Build：把单体 agent 拆为 Orchestrator 和多个面向工具或模型的 sub-agent。
2. Judge：用结构化 rubric 和 LLM-as-a-Judge 评价完整 interaction trace。
3. Optimize：先用 GEPA 校准 judge rubric，再用校准后的 judge 作为优化信号，对子 agent 或整个多 agent 系统做 prompt-level 优化。

## 1.3 LLM-as-a-Judge 设计要点

- rubric 被拆成多个正交 domain：Shopping Execution、Personalization and Context、Conversation Quality、Safety and Compliance。
- 每个 criterion 不是模糊打分，而是基于 trace 的二值 Pass/Fail 检查。
- judge 先判断 criterion 是否适用，只评价被激活的项。
- judge 只能依据确认过的 trace artifact，例如工具调用、最终购物车、已选商品、store selection history。
- critical check 可以导致整条 trace 失败，不应被平均分掩盖。
- GEPA 优化 judge prompt 后，论文报告 human agreement 从 84.1% 提升到 91.4%；表格中的 weighted agreement 从 88.47% 提升到 93.45%。

## 1.4 GEPA 相关事实

GEPA 原论文将 GEPA 定义为 Genetic-Pareto prompt optimizer：

- 输入是包含一个或多个 LLM prompt 的系统。
- 采样 reasoning、tool calls、tool outputs 等 trajectory。
- 通过自然语言 reflection 诊断失败、提出 prompt 更新、测试更新。
- 从 Pareto frontier 合并互补经验。
- 论文摘要报告 GEPA 相比 GRPO 平均高 6%，最高高 20%，并最多减少 35x rollout。

在 Build, Judge, Optimize 中，GEPA 有两层用途：

1. Judge calibration：优化 judge prompt/rubric 的判定边界，使其更接近人工标注。
2. Agent optimization：优化 sub-agent prompt 或多 agent prompt bundle。

## 1.5 Sub-agent GEPA

Sub-agent GEPA 把每个节点当成独立优化对象：

- 从日志 trace 中抽取单个 sub-agent invocation。
- 为每个 sub-agent 建立 micro-rubric。
- micro-rubric 来自反复出现的失败模式，并映射回全局 domain。
- 在 held-out split 上选择 rubric 分数最好的 prompt variant。

适合修复：

- 局部工具使用错误。
- 单个节点输入输出契约不清。
- 结构化上下文已足够、credit assignment 明确的问题。

不适合单独解决：

- Orchestrator 没把上下文传给下游。
- 某个 sub-agent 输出过长污染共享上下文。
- 多轮后才显现的协调失败。

## 1.6 MAMuT GEPA

MAMuT GEPA 是系统级优化：

- 优化对象不是单个 prompt，而是 prompt bundle，例如 orchestrator、cart、search 等一组 prompt。
- 目标函数是完整 trajectory 的 aggregate rubric score。
- 用 simulator 重新 roll out 历史意图。
- 若新动作与日志动作语义等价，则复用真实用户下一轮响应；若偏离，则由 User Persona Agent 生成符合原始约束的合成响应。
- 接受新 prompt bundle 的条件包括 held-out 提升和无 Safety regression。

论文在 238 条 held-out trajectories 上报告：

- overall rubric pass rate 从 77.1% 到 84.7%。
- Safety and Compliance 提升 12.0%。
- Conversational Quality 提升 8.0%。
- Personalization and Context 提升 6.8%，原因之一是 MAMuT 能优化 Orchestrator 正确传递偏好给下游 agent。

## 1.7 附录 prompt 对 judge 设计的启发

baseline judge prompt 只列出检查项和 Pass/Fail/N/A 规则；GEPA 优化后的 prompt 增加了：

- 输入字段解释。
- grounding rules。
- 只评价实际发生动作的证据规则。
- 后续澄清覆盖早期要求的规则。
- 替代方案必须用户批准才算满足。
- 领域 edge cases。
- 输出 schema 约束。

这说明 GEPA 对 judge rubric 的主要优化不是让 judge 更“聪明”，而是把隐含领域判断写成可执行边界。

## 1.8 可迁移边界

可迁移：

- trace-first evaluation。
- binary rubric。
- conditional activation。
- human-calibrated LLM-as-a-Judge。
- judge prompt 的 GEPA 迭代。
- sub-agent 局部优化与系统级 bundle 优化分层。

需重新验证：

- DMS 问题分析 agent 的 trace 结构。
- DMS 的 critical safety/factuality checks。
- 是否能构造稳定 replay/simulation。
- judge 与专家标注的一致性基线。
