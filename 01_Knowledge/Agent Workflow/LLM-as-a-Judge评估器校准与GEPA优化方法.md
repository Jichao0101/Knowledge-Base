---
type: knowledge
status: draft
unit_type: external_inspired_pattern
domain: Agent Workflow
topic: LLM-as-a-Judge评估器校准与GEPA优化方法
summary: 将 LLM-as-a-Judge 作为可校准组件管理，先评估 judge 与人工或 ground truth 的一致性，再用 GEPA 等反思式 prompt 优化方法改进 judge rubric。
sources:
  - 03_Inbox/2026-06-30_Build-Judge-Optimize_agent理论与DMS分析agent借鉴候选笔记.md
  - 04_Sources/Agent工程化/2026-06-30_Build-Judge-Optimize_agent理论来源证据卡.md
  - https://arxiv.org/abs/2603.03565
  - https://arxiv.org/abs/2507.19457
scope: 适用于需要用 LLM judge 评估 agent trace、政策合规、工具调用质量、诊断报告或多步骤工作流输出的场景。
risks:
  - 本条目是外部启发型方法论，不声明已在本地 DMS 或生产 workflow 中验证。
  - workshop notebook 中的具体航空客服实验指标尚未保存为可复核来源，不在本文作为已核验事实使用。
  - GEPA 优化 judge rubric 可能过拟合少量样本，必须保留 held-out 验证和高风险检查项。
  - judge 一致性提升不等同于业务正确，安全或量产相关结论仍需人工 review 与工程验证。
updated_at: 2026-06-30
---

# 1 LLM-as-a-Judge 评估器校准与 GEPA 优化方法

## 1.1 摘要

当 agent 的输出需要被自动评估时，LLM-as-a-Judge 不能被当成天然可靠的裁判。更稳健的做法是先 `Judge the Judge`：把 judge 本身作为一个可评估、可校准、可回归验证的组件。

核心模式是：

1. 用业务 trace、ground truth 和人工 annotation 构造 judge 训练/验证样本。
2. 让 judge 基于具体 trace artifact 做窄域判断，而不是泛泛评价“是否正确”。
3. 用混淆矩阵、关键失败类型召回率、误报率和 bias 分析 judge。
4. 用 GEPA 这类反思式 prompt optimizer，把 judge 的错误样本和 annotation 转成更明确的 rubric 规则。
5. 在 held-out 样本上确认 judge 改进，并检查高风险项没有回退。

本条目属于外部启发型方法论，不能替代本地工程验证。

## 1.2 为什么要 Judge the Judge

业务 agent 需要评估，但评估器不可靠时，优化闭环会被错误信号带偏。

常见错误路径是：

```text
agent 输出
  -> naive LLM judge 给出看似合理的分数
  -> prompt optimizer 或研发流程按错误分数优化
  -> agent 更擅长迎合 judge，而不是更符合业务要求
```

因此应建立二阶评估：

- 一阶：judge 评估 agent trace。
- 二阶：人工标注或 ground truth 评估 judge。
- 三阶：优化器基于 judge 错误样本改进 judge rubric。

## 1.3 Naive Judge 的典型失败

通用 judge 容易 rubber-stamp。它可能因为输出语气自然、流程看似完整、调用了工具，就倾向判定合规或正确。

但真正重要的失败往往隐藏在业务规则中：

- 工具调用虽然发生，但调用条件不满足。
- 流程看似完整，但缺少必要验证。
- 回复礼貌，但承诺了政策不允许的动作。
- 结论流畅，但没有引用可确认的 trace evidence。

因此不能只看 overall accuracy。需要至少检查：

- 高风险失败类型 recall。
- false positive / false negative。
- confusion matrix。
- judge 是否偏向多数类。
- judge 是否能指出具体证据和违规规则。

## 1.4 Judge 应是窄域判据

不要构建一个万能 judge 来同时判断 correctness、hallucination、policy、safety、tone 和 user satisfaction。

更可控的方式是把业务失败拆成具体 failure mode，并为每类失败定义可观测判断规则。

例如客服合规场景可以拆成：

- policy non-compliance。
- unsupported action。
- wrong tool call。
- missing verification。
- incorrect refund。
- premature compensation。

工程诊断场景可以拆成：

- 证据不足。
- 根因归类错误。
- 工具或日志字段误读。
- 未排除关键候选原因。
- 无验证计划。
- 安全或量产风险未标记。

窄域 rubric 的价值是让 GEPA 能从失败样本中学习具体规则，而不是学习抽象口号。

## 1.5 Ground Truth 和 Annotation

GEPA 优化 judge rubric 需要的不只是 label，而是带解释的 annotation。

只有 label 时，系统只知道 judge 错了。  
有 annotation 时，系统才能知道错在哪里，并把失败模式改写成 rubric 规则。

一个可用样本至少应包含：

```yaml
trace:
judge_verdict:
ground_truth_label:
annotation:
  failure_reason:
  evidence_refs:
  violated_rule:
  expected_judgment:
```

annotation 应引用具体 trace 位置或业务规则，避免只写“判断错误”。

## 1.6 GEPA 优化 Judge Rubric 的流程

GEPA 可以用于优化 judge prompt/rubric，而不是直接优化业务 agent。

基本流程：

1. 准备 seed rubric。
2. 在训练样本上运行 judge。
3. 收集 judge prediction、score、ground truth 和 annotation。
4. 让 reflection LLM 读取失败样本并诊断 rubric 缺口。
5. 生成新的 rubric 候选。
6. 重新评估候选 rubric。
7. 保留改进候选，丢弃退化候选。
8. 合并互补候选中的有效规则。
9. 在 held-out 样本上验证泛化。

优化后的 rubric 不一定只是更长。关键是从抽象原则变成可执行判据：

- 明确输入字段含义。
- 明确只依据实际发生的 trace artifact。
- 明确必要条件和禁止条件。
- 明确 edge cases。
- 明确何时输出 unknown 或 insufficient evidence。
- 明确输出 schema。

## 1.7 Presume Compliant / Presume Unknown

在合规类任务中，judge 可采用 `presume compliant unless clear documented violation`。它的意义不是放松标准，而是防止 LLM judge 把模糊、不完整、不可确认的现象解释成违规。

迁移到工程诊断时，更合适的形式通常是：

```text
presume unknown unless there is concrete trace evidence
```

也就是默认不下根因结论，除非有明确证据说明：

- 哪个时间点。
- 哪个信号或日志字段。
- 如何变化。
- 是否跨过阈值。
- 与故障事件的时间关系。
- 哪些候选原因已被排除。

这能抑制“看起来像模型问题”“可能是光照问题”这类无证据结论。

## 1.8 Pareto 保留互补能力

GEPA 中的 Pareto 思想适合多失败类型评估。一个 rubric 候选可能擅长捕获某类高频错误，另一个候选可能擅长捕获罕见但高风险错误。只按总体 accuracy 选择单一候选，可能丢掉罕见风险能力。

应保留并合并互补候选：

- 候选 A 擅长识别工具调用错误。
- 候选 B 擅长识别缺少验证。
- 候选 C 擅长识别政策边界。
- 候选 D 擅长识别输出 schema 问题。

最终 rubric 应在 held-out 集合上验证整体表现，同时单独检查高风险 failure mode 的 recall。

## 1.9 适用边界

适合使用本方法的场景：

- agent trace 可记录且可回放。
- 有人工标注或 ground truth。
- 失败类型可被拆成业务规则。
- judge 输出会影响后续优化或自动化决策。
- 高风险失败不应被平均分掩盖。

不适合或需谨慎的场景：

- 没有 ground truth 或 annotation。
- 只有少量、同质、不可泛化样本。
- judge 输出会直接触发高风险动作。
- 业务规则本身仍不稳定。
- 评估目标无法落到可观察 trace evidence。

## 1.10 后续验证条件

若要从 external inspired pattern 升级为 verified pattern，需要补充：

1. 一个本地 agent workflow 或 DMS case 集合。
2. 专家标注协议和 ground truth 样本。
3. seed judge 与优化后 judge 的 confusion matrix。
4. 高风险 failure mode 的 recall / precision 对比。
5. GEPA 优化前后的 rubric diff。
6. held-out 验证结果。
7. 人工 review 证明优化后的 judge 没有引入不可接受的误判。
