---
type: project_learning_record
status: active
project: AI-Career-Transition
learning_stage: Phase 2-A - VLM model engineering cognition and OMS adaptation preparation
record_role: durable_stage_learning_record
summary: 保存 Phase 2-A 的主动诊断、缺口映射、原文阅读状态、证据等级与恢复任务，不把阅读或对话理解记为实现证据。
sources:
  - 2026-08-20 用户确认 Phase 1-C 范围关闭，并同意先建立模型工程认知、暂不要求完整 SFT
  - 2026-08-20 用户要求补全下一阶段学习骨架，以支持原文阅读和考核
  - 02_Projects/AI-Career-Transition/10_学习文档/P02A-01_VLM模型工程认知_学习文档.md
  - 02_Projects/AI-Career-Transition/20_学习记录/当前阶段学习检查点.md
scope: Phase 2-A 的个人掌握状态、诊断、缺口、阅读进度、迁移能力和恢复任务。
risks:
  - 当前尚未开始正式诊断，能力状态保持 not_verified。
  - 阅读或复述术语不等于能独立做资源判断和故障定位。
  - 本阶段不要求完成 SFT、集群训练或 kernel 实现，不得把范围豁免写成实现完成。
single_pass_recoverable: false
updated_at: 2026-08-20
---

# 1 Phase 2-A VLM 模型工程认知学习记录

## 1.1 当前状态

- 对应文档：[[02_Projects/AI-Career-Transition/10_学习文档/P02A-01_VLM模型工程认知_学习文档]]
- 当前覆盖：`not_started`
- 证据：骨架已建立；尚无闭卷诊断、迁移题或运行证据。

## 1.2 范围决定

“完整”指问题空间和决策关系完整，不指每项技术都独立实现。未来 OMS 任务以月推进；任务合同、数据、基线、错误分类和资源目标明确后，才决定是否打开 LoRA/QLoRA 实践。

## 2 诊断队列

| 顺序 | 主题 | 状态 | 合格证据 |
|---|---|---|---|
| 1 | 单卡 VLM SFT 主链 | not_verified | 闭卷画出样本、mask、forward/backward、optimizer、checkpoint。 |
| 2 | 训练显存 | not_verified | 分解主要占用并诊断 OOM。 |
| 3 | PEFT 与资源杠杆 | not_verified | 区分 LoRA/QLoRA/checkpointing/precision/FlashAttention。 |
| 4 | 分布式地图 | not_verified | 用容量、吞吐、通信解释 DDP/FSDP/TP/PP/CP。 |
| 5 | 算子 IO | not_verified | 用 HBM/SRAM、tiling、recomputation 解释 FlashAttention。 |
| 6 | Profiling 与 OMS 迁移 | not_verified | 给出可复核资源与性能计划。 |

## 3 缺口与证据状态

```text
单卡 SFT 主链：not_verified
训练显存与资源杠杆：not_verified
分布式训练决策：not_verified
算子 IO / FlashAttention：not_verified
profiling 迁移能力：not_verified
SFT 实践：not_required_in_current_scope
分布式训练实践：not_required_in_current_scope
kernel 实现：not_required_in_current_scope
```

## 4 原文阅读状态

- Ultra-Scale Playbook：`not_started`，按来源卡选择性阅读。
- FlashAttention 长序列文章：`not_started`，重点重建 IO-aware 原理。

阅读只记录为 source_read，不自动提升诊断状态。

## 5 下一步恢复任务

1. 学习阶段文档第 2～3 章。
2. 回答第一个闭卷问题：全量微调 VLM 时，为什么训练显存显著高于同一模型推理？
3. 按回答缺口决定先补 SFT 主链还是显存分解，再进入原文选择性阅读。
