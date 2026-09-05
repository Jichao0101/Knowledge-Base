---
type: project_learning_record
status: active
project: AI-Career-Transition
learning_stage: Phase 2-A - VLM model engineering cognition and OMS adaptation preparation
record_role: durable_stage_learning_record
summary: 保存 Phase 2-A GPU 基础桥接的自述起点、学习安排与证据状态；个人笔记已整理，硬件基础和模型工程能力仍待诊断。
sources:
  - 2026-09-05 用户说明有模型训练经验但缺少硬件基础，Part4 阅读抽象；确认 P02A-01 为经 AI 整理优化的个人学习笔记，并要求更新阶段、目标与检查点
  - 2026-08-20 用户确认 Phase 1-C 范围关闭，并同意先建立模型工程认知、暂不要求完整 SFT
  - 2026-08-20 用户要求补全下一阶段学习骨架，以支持原文阅读和考核
  - 02_Projects/AI-Career-Transition/10_学习文档/P02A-01_VLM模型工程认知_学习文档.md
  - 02_Projects/AI-Career-Transition/20_学习记录/当前阶段学习检查点.md
scope: Phase 2-A 的个人掌握状态、诊断、缺口、阅读进度、迁移能力和恢复任务。
risks:
  - 当前缺口依据用户自述，尚未形成正式诊断；各能力状态保持 not_verified。
  - 阅读或复述术语不等于能独立做资源判断和故障定位。
  - 本阶段不要求完成 SFT、集群训练或 kernel 实现，不得把范围豁免写成实现完成。
single_pass_recoverable: false
updated_at: 2026-09-05
---

# 1 Phase 2-A VLM 模型工程认知学习记录

## 1.1 当前状态

- 对应笔记：[[02_Projects/AI-Career-Transition/10_学习文档/P02A-01_VLM模型工程认知_学习文档]]；用户确认其为经 AI 整理优化的个人学习笔记。
- 主阶段：Phase 2-A；当前子阶段：GPU 基础桥接，安排已明确，课程完成状态未报告。
- 已有基础：用户自述有模型训练经验；此前训练实践证据边界仍以项目总览和原记录为准。
- 当前缺口：用户自述无硬件基础，阅读 Playbook Part4 感到抽象；这是自述证据，不是闭卷评测结论。
- 笔记整理不代表阅读全部完成或能力已验证；GPU 基础、模型工程迁移与 profiling 仍为 `not_verified`。

## 1.2 范围决定

“完整”指问题空间和决策关系完整，不指每项技术都独立实现。未来 OMS 任务以月推进；任务合同、数据、基线、错误分类和资源目标明确后，才决定是否打开 LoRA/QLoRA 实践。

## 1.3 诊断队列

先完成相应教学和例子，再逐项检查；不以连续考试代替基础补课。

| 顺序 | 主题 | 状态 | 合格证据 |
|---|---|---|---|
| 1 | 计算与访存、吞吐/延迟/带宽 | not_verified | 能以具体过程解释 GPU 等待数据 |
| 2 | GPU 执行与存储模型 | not_verified | 画出向量加法执行、线程组织和数据位置 |
| 3 | 向量加法与矩阵乘法例子 | not_verified | 解释线程索引、数据搬运、同步和 tiling 动机 |
| 4 | Part4 与算子 IO | not_verified | 理解合并访存、tiling、fusion 与 FlashAttention 的目标和边界 |
| 5 | 单卡 SFT、显存与 PEFT | not_verified | 复述训练主链，分解 OOM，区分资源杠杆 |
| 6 | 单卡 profiling | not_verified | 固定配置与测量口径，形成资源变化的预测及观测 |
| 7 | 分布式地图与 OMS 迁移 | not_verified | 解释容量/吞吐/通信取舍；具备单卡基线后再评估两节点 DDP |

## 1.4 缺口与证据状态

```text
GPU 执行与存储基础：not_verified
单卡 SFT 主链：not_verified
训练显存与资源杠杆：not_verified
分布式训练决策：not_verified
算子 IO / FlashAttention：not_verified
profiling 迁移能力：not_verified
SFT 实践：not_required_in_current_scope
分布式训练实践：not_required_in_current_scope
kernel 实现：not_required_in_current_scope
```

## 1.5 原文阅读状态

- P02A-01：用户确认是经 AI 整理优化的个人学习笔记；整理存在，不推断所有章节已掌握。
- Ultra-Scale Playbook：用户已接触中文 Part4 并报告抽象；具体读到的位置、其他部分完成度尚未报告。2026-08-20 的 `not_started` 是当时记录，见第 1.7 节。
- CS149 第 7 讲：已选定为主教材，是否开始观看及完成进度未报告。
- CS149 第 1～3 讲相关部分、第 6 讲：按缺口选读，未报告完成。
- FlashAttention 长序列文章：本轮未报告新增阅读进展，保留待学习状态。

阅读、笔记整理、解释能力与运行证据分别记录；课程完成需用户报告，能力验证需作答或实践证据。材料链接统一由当前检查点第 1.5 节维护。

## 1.6 下一步恢复任务

1. 从计算与访存、吞吐与延迟、带宽和缓存开始教学；结合现有训练经验解释术语。
2. 进入 CS149 第 7 讲，配合向量加法例子理解执行与数据移动。
3. 教学后回答：GPU 的计算单元很多，为什么仍可能在等数据？
4. 回答与缺口写入本记录；稳定机制补充写入 P02A-01，视频观看位置可追加到阅读状态。
5. GPU 基础子阶段通过后返回 Part4，随后用现有小模型建立单卡基线；两节点 DDP 尚未启动。

## 1.7 2026-09-05 学习顺序调整记录

- 原安排（2026-08-20）：先读阶段文档第 2～3 章，以“全量微调 VLM 为何比推理占显存”作为首个闭卷问题；当时学习覆盖和原文阅读均记为 `not_started`，尚无诊断证据。
- 新安排（本次对话）：用户说明有模型训练经验但没有硬件基础，Part4 阅读抽象，并确认笔记由 AI 整理优化；据此前置 GPU 基础桥接，当前安排见第 1.3、1.6 节和滚动检查点。
- 调整关系：新安排接替上述旧恢复顺序，旧安排作为历史保留；原训练主链、显存、并行和 profiling 目标后移，未删除或判定失效。
- 依据与验证边界：依据为本次用户自述及更新请求；没有新增闭卷答案、课程完成、单卡 profile 或两节点运行证据。不提高能力 evidence level，不宣布阶段完成。
- 深度边界：先理解例子与机制；不以 CUDA/Triton 高性能 kernel、完整 SFT 或集群训练作为当前完成条件。
