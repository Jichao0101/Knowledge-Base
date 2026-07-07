---
type: candidate
status: pending_review
summary: Skill frontmatter description 应负责召回入口，正文负责后置判定与执行策略。
sources:
  - 2026-07-07 当前对话：conversation-to-knowledge-candidate skill 的 frontmatter description 设计讨论
target_path: 01_Knowledge/Agent Workflow/
scope: Codex skill / agent capability 的触发描述、隐式触发与执行门禁设计
updated_at: 2026-07-07
---

# 1 Skill frontmatter 触发职责候选经验

## 1.1 摘要

Skill 的 `frontmatter.description` 应回答“什么情况下值得尝试加载这个 skill”，而不是回答“什么情况下最终应该输出结果”。需要在 skill 加载后才能判断的候选价值、证据完整度、scope consistency 和低打扰输出策略，应放在正文执行门禁中。

## 1.2 候选经验

1. `frontmatter.description` 是 skill 的召回入口，应覆盖显式请求和合理的隐式触发场景。
2. skill body 是执行策略位置，适合放置候选价值评分、证据完整度、scope consistency、输出等级和低打扰规则。
3. 不要把依赖 skill 内部分析后才能得到的判断条件写入 `description`，否则会产生循环依赖：是否加载 skill 取决于加载后才能完成的分析。
4. 对隐式触发型 skill，frontmatter 应明确“用户没有要求，但讨论已经产生潜在知识资产”这一入口，否则主动捕获能力会被削弱。

## 1.3 适用范围

- Codex skill、agent capability、plugin skill 的触发描述设计。
- 需要支持隐式触发、主动识别或低打扰输出的技能。
- 需要区分“召回条件”和“执行后门禁”的能力设计。

## 1.4 风险与边界

- 该经验不等于要求扩大所有 skill 的触发范围；普通工具型 skill 仍应保持精确触发。
- `description` 可以描述值得加载的上下文，但不应包含复杂评分阈值或后置输出策略。
- 需要结合更多 skill 案例验证后，才能提升为正式 Agent Workflow 知识。

## 1.5 推荐后续处理

- 对比其他隐式触发型 skill 的 frontmatter，验证是否存在类似循环依赖。
- 若验证稳定，可整理为 Agent Workflow 中的 skill metadata 设计原则。
