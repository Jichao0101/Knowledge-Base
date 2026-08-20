---
type: project_learning_record
status: draft
project: AI-Career-Transition
learning_stage: Phase 3 - Agent Systems
record_role: future_stage_learning_record
summary: 保存 Agent Systems 主动学习的恢复题、诊断结果和实践状态；当前仅建立恢复骨架，尚未进入该主阶段。
sources:
  - 02_Projects/AI-Career-Transition/10_学习文档/P03-01_Agent系统_学习文档.md
  - 02_Projects/AI-Career-Transition/20_学习记录/当前阶段学习检查点.md
scope: Agent Systems 的个人诊断与实践进度。
risks:
  - 当前问题仅是未来诊断骨架，尚无作答结果，不得标记为 working 或完成。
  - DMS evidence case 只允许使用合成或明确授权材料。
single_pass_recoverable: false
updated_at: 2026-08-20
---

# 1 Agent 系统学习记录

## 1.1 当前状态

Agent Systems 学习文档已形成 `draft` 骨架，但当前主阶段是 Phase 2-A 模型工程认知。本记录不包含已完成诊断；后续正式进入 Agent Systems 阶段时，应先以 [[02_Projects/AI-Career-Transition/10_学习文档/P03-01_Agent系统_学习文档]] 为教学骨架，再逐题记录回答、缺口和实践证据。

## 1.2 主动学习恢复题

建议按下面顺序继续，每次只诊断一个问题：

1. 解释为什么模型输出是动作提议，不是执行事实。
2. 画出一次 tool call 从提议到 observation 的状态转换。
3. 判断 timeout 后是否可以重试，并指出缺少的环境状态。
4. 区分 RunState、模型上下文、持久记忆和外部知识。
5. 给一个环境 outcome 成功但过程不安全的反例。
6. 为一个 DMS evidence case 写出 success、evidence 和 abstain 条件。

每个覆盖区采用同一学习闭环：

```text
主动回忆 → 暴露最小缺口 → 阅读相关主干
→ 故障注入或迁移题 → 解释观察 → 记录未验证边界
```

## 1.3 证据状态

```text
学习骨架：draft
诊断作答：not_verified
最小实现：not_verified
故障注入：not_verified
```
