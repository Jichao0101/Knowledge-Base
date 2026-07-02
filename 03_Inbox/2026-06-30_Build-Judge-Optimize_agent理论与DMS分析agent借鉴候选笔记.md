---
type: candidate
status: pending_review
summary: 基于 Build, Judge, Optimize 论文和相关视频主题整理 agent 评估、可信 LLM-as-a-Judge、GEPA 优化 judge rubric，以及对座舱 DMS 问题分析解决 agent 的借鉴。
sources:
  - 04_Sources/Agent工程化/2026-06-30_Build-Judge-Optimize_agent理论来源证据卡.md
  - https://www.youtube.com/watch?v=X4dEHRzBLmc&t=575s
  - https://arxiv.org/abs/2603.03565
  - https://arxiv.org/abs/2507.19457
target_path: 01_Knowledge/Agent Workflow/待定
scope: Agent Workflow、LLM-as-a-Judge、GEPA、DMS 问题分析 agent
updated_at: 2026-06-30
---

# 1 Judge the Judge、GEPA judge rubric 与 DMS 分析 agent 借鉴候选笔记

## 1.1 摘要

这次 workshop 的主线不是“如何让业务 agent 更聪明”，而是先回答一个更基础的问题：如果评估器本身不可靠，agent 优化闭环会被错误信号带偏。因此需要先构建、校准和评估 judge，也就是先 `Judge the Judge`。

朴素 LLM judge 看起来能打分，但常见问题是 rubber-stamp：因为 agent 语气礼貌、流程完整、调用了工具，judge 就倾向判定合规。航空客服案例表明，这种 judge 会严重漏掉业务政策违规。根据用户补充的公开 notebook 记录，seed rubric 的 accuracy 为 65.2%，但 non-compliant recall 只有 14.0%，并且 112 个样本中 104 个被判为 compliant，约 93% 偏向合规。

对座舱 DMS 故障分析 agent 的核心启发是：不能只评估报告是否流畅，而要评估真实故障是否被召回、根因是否被正确归类、证据是否有效、是否能区分模型问题/策略问题/输入质量问题/时间同步问题，以及是否避免无证据的工程结论。

## 1.2 为什么要 Judge the Judge

业务 agent 需要评估，但评估器如果不可靠，后续优化会朝错误方向收敛。Judge the Judge 是一个二阶评估问题：

1. 一阶：judge 评估业务 agent 的 trace。
2. 二阶：人类标注或 ground truth 评估 judge。
3. 三阶：优化器根据 judge 错误样本修正 judge rubric。

航空客服 workshop 的输入是一段客服对话 trace，包括：

- 用户消息。
- agent 回复。
- 工具调用。
- 工具结果。
- ground-truth assertions。

目标不是让 LLM 泛泛判断“回答是否正确”，而是构建一个读取 trace 后判断 `compliant / non-compliant` 的窄域 LLM judge，再用 GEPA 优化 judge rubric，使其更接近 ground truth。

## 1.3 朴素 LLM Judge 为什么失败

Naive judge 容易把大多数轨迹判成合规。失败机制不是模型完全不会推理，而是缺少业务判据：

- agent 语气礼貌。
- 流程看起来完整。
- 调用了工具。
- 没有明显异常文本。

但真实违规藏在业务政策里，例如：

- Basic Economy 票是否允许取消。
- 是否满足 24 小时规则。
- 是否有保险。
- 是否允许补偿。
- 是否允许基于未验证信息执行操作。

因此 accuracy 不足以证明 judge 可靠。类别分布不均时，judge 可以靠偏向多数类得到看似还行的 accuracy。必须看：

- non-compliant recall。
- false positive / false negative。
- confusion matrix。
- judge bias，例如是否过度判 compliant。
- 关键违规类型的漏报率。

DMS 领域同理。不能只看“分析报告像不像专家写的”，而要看：

- 真实故障是否被召回。
- 误报根因是否过多。
- 是否引用有效证据。
- 是否能区分模型问题、策略问题、输入质量问题、时间同步问题。
- 是否能识别状态机、配置、版本和数据分布问题。

## 1.4 好的 Judge 是窄域判据，不是通用裁判

不要构建一个万能 judge。`hallucination`、`correctness`、`policy violation`、`safety`、`tone` 这些词太宽泛，会导致：

- 判据不稳定。
- 不同样本之间标准漂移。
- LLM 根据表面语气判断。
- 无法定位可修复问题。

更好的方式是把业务失败拆成具体 failure mode。航空客服可拆成：

- `policy_non_compliance`
- `unsupported_action`
- `wrong_tool_call`
- `missing_verification`
- `incorrect_refund`
- `premature_compensation`

DMS 故障分析可拆成：

- `input_quality_issue`
- `face_track_loss`
- `landmark_quality_drop`
- `gaze_invalid_but_warning_triggered`
- `state_machine_debounce_error`
- `enable_condition_mismatch`
- `false_distraction_warning`
- `fatigue_missed_detection`
- `camera_exposure_ir_issue`
- `timestamp_alignment_error`

这种拆分决定 GEPA 是否能收敛。GEPA 优化 prompt/rubric 时，需要从失败样本里学到具体规则，而不是抽象口号。

## 1.5 Ground Truth 和 Annotation 是优化燃料

GEPA 不是凭空优化 judge。它依赖：

- trace。
- judge verdict。
- ground truth label。
- 失败原因 annotation。

如果只有 label，judge 只知道自己错了。如果有 annotation，judge 才知道错在哪里，GEPA 才能把错误模式转写成 rubric 规则。

航空客服示例：

```json
{
  "label": "non-compliant",
  "annotation": "agent 给了不符合政策的补偿。政策要求只有 silver/gold 或有保险用户才可补偿。该用户不满足条件，因此 agent 应拒绝补偿。"
}
```

GEPA 可以把这类 annotation 转成 rubric：

```text
若用户不具备会员等级或保险条件，agent 不应承诺补偿；
若 agent 在未满足条件时提供补偿，判定 non-compliant。
```

DMS 故障分析需要积累的也不只是最终根因标签，而是工程师写的故障解释：

```json
{
  "case_id": "DMS_xxx",
  "label": "false_distraction_warning",
  "root_cause": "gaze_valid_jitter",
  "annotation": "报警前 1.2s 内 gaze_valid 在 true/false 之间抖动 6 次，head_pose 和 face_confidence 稳定，warning_state 在 debounce 未满足稳定条件时进入 pending，因此优先判定为 gaze valid 后处理门控问题。",
  "evidence": [
    "face_confidence stable > 0.9",
    "head_pose_yaw stable < 5 deg",
    "gaze_valid toggled",
    "warning_state entered pending"
  ]
}
```

没有这类 annotation，优化器只能学到表面相关性。

## 1.6 GEPA 是什么

GEPA 指 Genetic-Pareto。它不是把轨迹压缩成稀疏 scalar reward，而是利用语言 trace 的可解释性：

1. 采样 trajectories，包括 reasoning、tool calls、tool outputs。
2. 用自然语言 reflection 诊断失败原因。
3. 提出并测试 prompt/rubric 更新。
4. 从 Pareto frontier 中组合互补经验。

简化工程流程：

```text
seed prompt / seed rubric
  -> 训练样本运行
  -> trace + prediction + score + annotation
  -> reflection LLM 分析失败原因
  -> 生成新 rubric / prompt
  -> 重新评估
  -> 保留更优候选
  -> merge 多个互补候选
  -> 验证集评估泛化
```

GEPA 适合优化文本化控制面：

- prompt。
- judge rubric。
- agent policy。
- tool description。
- 输出 schema 和报告模板。
- 多模块 agent 的局部提示词。

它不直接替代模型训练；优化对象主要是文本参数，而不是模型权重。

## 1.7 GEPA 和 RL 的关键差异

RL/GRPO 类方法通常是：

```text
trajectory -> scalar reward -> policy update
```

问题是中间的大量诊断信息被丢掉了。

GEPA 更接近：

```text
trajectory + textual feedback -> reflection -> prompt mutation -> evaluation
```

Agent 失败通常不只是 answer wrong，而可能是：

- 调用了错误工具。
- 工具参数错。
- 没有等待工具结果。
- 循环提前退出。
- 记忆恢复错。
- 系统提示词约束缺失。
- 输出格式不符合 schema。
- 中间步骤忽略了证据。

这些信息都能在 trace 里看到。如果只压成 0/1 或 0.63，就丢掉了最有价值的诊断信号。

## 1.8 Workshop 中的 GEPA 用法：优化 Judge Rubric

这次 workshop 中，GEPA 不是直接优化航空客服 agent，而是优化 judge rubric。

流程是：

1. 用当前 rubric 评估训练样本。
2. 把失败样本和 annotations 展示给 reflection LLM。
3. reflection LLM 提出改进后的 rubric。
4. 在同一批样本上测试新 rubric。
5. 如果提升则保留，否则丢弃。
6. 重复多轮。

关键点是 annotations 提供了当前 judge 缺失的具体政策规则。GEPA 的作用是把这些规则编码进 rubric。

根据用户补充的公开 notebook 记录，优化后的 rubric 从 727 字符扩展到 3606 字符，并包含更具体的政策规则，例如先识别 Ticket Class 和 User Request，再根据 mandatory rules 判断；同时保留关键 directive：除非有明确记录化的政策违规，否则默认 presume compliant。

这不是“提示词越长越好”，而是 rubric 从抽象原则变成了可执行判据。

## 1.9 优化结果说明什么

根据用户补充的 workshop 结果：

| Metric | Seed rubric | GEPA optimized rubric |
|---|---:|---:|
| Accuracy | 65.2% | 69.6% |
| Non-compliant recall | 14.0% | 55.8% |
| Bias says compliant | 93% | 65% |

同时 compliant recall 从 97.1% 降到 78.3%。这说明优化不是简单“全部判违规”，而是在漏报和误报之间重新权衡。

理论意义：

- 评估器优化目标不一定是单一 accuracy 最大化。
- 更重要的是错误类型分布符合业务风险。
- 高风险违规召回可能比总体 accuracy 更关键。

DMS 类比：

- 严重故障漏诊率。
- 安全相关误判率。
- 根因归因准确率。
- 证据引用完整性。
- 是否发现配置回归。
- 是否避免无证据归因模型。

例如把状态机 debounce 问题误判成模型问题，会让研发方向完全错误。DMS judge 应特别惩罚这种错误归因。

## 1.10 Presume Compliant 的理论含义

Workshop 中的一个重要实践是：judge 默认应假设 agent 合规，除非有明确证据证明违规。

这不是放松标准，而是抑制 LLM judge 的过度指控倾向。如果要求 judge 主动寻找违规，它可能把模糊、不完整、不确定的现象解释为违规。

因此 rubric 应要求：

- 必须引用具体证据。
- 不能用 vague concerns。
- 不能因为“感觉不对”判违规。
- 只有能指出具体错误消息或动作时才判 non-compliant。

DMS 故障 agent 应采用类似规则：

- 默认不下根因结论。
- 除非有明确时间点、信号、阈值、状态转换证据。
- 不允许用“可能是模型不稳定”“应该是光照问题”“看起来像策略问题”作为结论。

可采纳结论必须说明：

- 哪个时间点。
- 哪个信号。
- 如何变化。
- 是否跨过阈值。
- 与报警/故障事件的时间关系。

## 1.11 GEPA 的 Pareto 思想

GEPA 名字中的 Pareto 很关键。一个候选 prompt 可能擅长捕获补偿违规，另一个擅长捕获取消规则违规。单一全局最优候选可能过早丢掉局部能力。

Pareto frontier 的意义是保留多个互补候选：

- 候选 A：错误类型 1 上好。
- 候选 B：错误类型 2 上好。
- 候选 C：总体一般，但在罕见场景上好。

然后通过 merge 组合这些候选中的有效规则。

DMS 中也应保留互补候选：

- prompt A 擅长判断 `gaze_valid` 抖动。
- prompt B 擅长判断 IR/exposure 问题。
- prompt C 擅长判断状态机未复位。
- prompt D 擅长判断版本配置回归。

如果只看总体准确率，罕见但高风险故障模式可能被优化过程丢掉。Pareto/merge 可以降低这种风险。

## 1.12 映射到 DMS 故障分析 Agent

最大启发是：不要只构建分析 agent，还要构建评估分析 agent 的 judge，并用 GEPA 持续优化 judge/rubric/诊断提示词。

建议形成三层系统：

```text
DMS Analysis Agent
  读取日志、构建时间线、提出根因假设

DMS Judge
  判断分析结果是否有证据、是否符合诊断规范、是否错误归因

GEPA Optimization Loop
  用工程师标注过的 case 优化 judge rubric 或 analysis prompt
```

闭环：

```text
历史 DMS case
  -> 人工标注根因 + 证据 + 错误分析
  -> analysis agent 生成诊断报告
  -> judge 判断报告是否正确
  -> 对比 ground truth
  -> 收集 judge 漏判/误判
  -> GEPA 优化 judge rubric
  -> 再用优化后的 judge 约束 analysis agent
```

## 1.13 DMS 场景可以优化哪些文本组件

GEPA 可以优化任何文本化控制参数。DMS agent 中可优化：

1. 故障分类 prompt。
2. 日志摘要 prompt。
3. 时间线构建 prompt。
4. 根因分析 prompt。
5. 工具选择 prompt。
6. 证据引用规范。
7. judge rubric。
8. 报告模板。
9. 不确定性表达规则。
10. 下一步验证建议规则。

建议先从 judge rubric 开始：

输入：

- case 描述。
- 日志摘要。
- 关键时间线。
- agent 诊断报告。
- 人工 ground truth。

输出：

- pass/fail。
- root cause correctness。
- evidence completeness。
- unsupported inference。
- missed signals。
- recommended fix。

## 1.14 DMS Judge 初版 Rubric 草案

### 1.14.1 顶层 domain

| Domain | 判断目的 |
|---|---|
| Problem Framing | 是否清楚定义现象、影响范围、复现条件和严重度 |
| Evidence Grounding | 是否引用日志、视频、配置、代码、实验等一手证据 |
| Root Cause Isolation | 是否正确区分模型、输入、配置、状态机、时间同步、部署集成等根因 |
| Unsupported Inference Control | 是否避免无证据推断和过早定论 |
| Fix and Validation | 修复建议是否最小、可执行、可回归验证 |
| Safety and Governance | 是否识别安全风险、量产影响和人工 review 边界 |

### 1.14.2 二值检查示例

Problem Framing：

- 是否记录 case_id、数据来源、时间段和版本。
- 是否明确误检、漏检、延迟、抖动、误报警或未报警类型。
- 是否区分单例问题和分布性问题。

Evidence Grounding：

- 是否引用原始日志或视频帧段。
- 是否列出关键中间输出。
- 是否标明缺失证据。
- 是否把 agent 推测和事实证据分开。

Root Cause Isolation：

- 是否至少比较两个候选根因。
- 是否排除配置/阈值/状态机因素后再归因模型。
- 是否解释错误传播路径。
- 是否能区分输入质量、跟踪丢失、landmark 质量下降、状态机 debounce、enable condition mismatch、时间戳对齐问题。

Unsupported Inference Control：

- 是否避免“可能是模型不稳定”这类无证据结论。
- 是否在证据不足时输出 Unknown / Need Evidence。
- 是否给出下一步验证数据，而不是直接下结论。

Fix and Validation：

- 是否给出最小改动方案。
- 是否给出离线、板端、回归三类验证中适用的验证项。
- 是否定义通过/失败标准。

Safety and Governance：

- 是否避免未经验证直接修改量产阈值。
- 是否标记法规或报警策略影响。
- 是否要求 critical change 进入人工 review。

## 1.15 正式知识提升条件

本候选仍不应直接提升到正式知识。提升条件：

1. 找到并保存 workshop notebook 的可复核链接或本地副本。
2. 明确航空客服实验指标来自可核验 notebook，而不是仅来自转述。
3. 完成 DMS 专用 trace schema。
4. 至少完成一轮 DMS 专家标注与 judge-human agreement 统计。
5. GEPA 优化 judge prompt 后有 held-out 提升记录。
6. 有至少一个 DMS 历史 case 的端到端分析 trace。
7. 明确哪些输出只能 proposal-only，哪些可进入自动化执行。
