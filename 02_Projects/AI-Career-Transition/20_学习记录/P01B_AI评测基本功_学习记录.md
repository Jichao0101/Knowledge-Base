---
type: project_learning_record
status: closed_by_scope
project: AI-Career-Transition
learning_stage: Phase 1-B - evaluation basics and seed cases
record_role: durable_stage_learning_record
summary: 保存 Phase 1-B 的主动学习结论、seed case 形成状态、范围豁免和切换到 Phase 1-C 的决定。
sources:
  - 2026-08-09 Phase 1-B 主动学习对话、费曼复述与范围调整决定
  - 02_Projects/AI-Career-Transition/10_学习文档/P01B-01_AI评测基本功_学习文档.md
  - 02_Projects/AI-Career-Transition/20_学习记录/当前阶段学习检查点.md
scope: Phase 1-B 的个人掌握状态、范围决定和未执行实践。
risks:
  - working 只表示对话诊断中的可用理解，不代表已建立或运行 benchmark。
  - waived_by_scope 不等于实践已完成，不得改写为运行证据。
  - 四类 seed case 是概念草案，未持久化为数据集。
single_pass_recoverable: false
updated_at: 2026-08-11
---

# 1 Phase 1-B AI 评测基本功学习记录

## 1.1 阶段关闭结论

2026-08-09 的主动学习覆盖了任务类型、评分方法、评测合同、可靠性风险和 seed case 边界设计。概念主干达到对话诊断意义上的 `working`。

用户根据目标岗位与学习投入产出，决定将规则脚本、逐 case 运行和重复评分移出当前阶段门禁，证据状态记为 `waived_by_scope`。该决定关闭当前学习主线，但不表示这些实践已经执行，也不表示练习集已经成为 benchmark。

## 1.2 已形成的概念能力

- 能按输出空间、证据依赖和外部副作用区分确定性、开放生成、检索/证据和工具执行任务。
- 能为混合 Agent 任务拆分子任务并分别定义合同，而不是按 Regex、LLM 或脚本等实现方式分类。
- 能区分 exact match、规则评分、语义/模型评分和人工评分的适用范围。
- 能定义输入、可接受结果、证据、abstain、失败标签与权限预算组成的评测合同。
- 能说明评分一致性不等于正确性，留出集参与调参后会成为开发集。

## 1.3 Seed case 与基线状态

对话中形成四种概念案例：

1. 正常合规与明确不合规航班。
2. 必要字段缺失，返回 `insufficient_evidence`。
3. 信息完整但没有合规航班，任务仍为 `completed`，合法结果为空集合。
4. 政策无法读取，按原因返回 `needs_authorization`、`input_error` 或 `failed`，不能伪装成空合规结果。

证据状态：

```text
任务类型、评分方法、评测合同、可靠性边界：working
四类 seed case 持久化：waived_by_scope
隔天重复评分：waived_by_scope
确定性规则基线：waived_by_scope
逐 case 运行：waived_by_scope
真实 benchmark：not_verified
```

## 1.4 阶段切换

滚动检查点已切换到 Phase 1-C：VLM 基线与 benchmark 草案。Phase 1-B 的概念骨架继续作为 VLM 任务定义、证据边界和评分合同的前置知识；只有 Phase 1-C 暴露真实评测缺口时才按需回补，不恢复已豁免的传统规则脚本练习。
