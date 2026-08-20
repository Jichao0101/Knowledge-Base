---
type: project_learning_document
status: active
project: AI-Career-Transition
learning_stage: Phase 2-A - VLM model engineering cognition and OMS adaptation preparation
summary: 以未来 OMS 开源 VLM 数据适配为迁移场景，建立从单卡 SFT/PEFT、训练显存到分布式并行、算子 IO 和 profiler 的模型工程决策地图。
sources:
  - 04_Sources/模型工程/2026-08-20_Ultra-Scale-Playbook来源证据卡.md
  - 04_Sources/模型工程/2026-08-20_FlashAttention长序列优化来源证据卡.md
  - 02_Projects/AI-Career-Transition/10_学习文档/P01A-02_LLM训练机制_学习文档.md
  - 02_Projects/AI-Career-Transition/10_学习文档/P01C-01_VLM基线与Benchmark_学习文档.md
  - 2026-08-20 用户确认 Phase 1-C 范围关闭，并要求补全可阅读原文、可主动考核的下一阶段骨架
scope: VLM 单卡训练、SFT/PEFT、显存/计算/通信、分布式概念、算子 IO、profiling 与 OMS 适配边界。
risks:
  - 本阶段建立认知，不代表已经运行 SFT、掌握集群调优或具备 kernel 开发能力。
  - 外部材料面向特定 LLM/硬件；迁移到 VLM、T4 或 OMS 前必须重新核对架构、shape、版本和 profile。
  - 是否执行 SFT 仍取决于任务合同、合法数据、基线、错误分类和资源预算。
updated_at: 2026-08-20
---

# 1 Phase 2-A VLM 模型工程认知学习文档

## 1.1 学习目标与边界

目标：面对可能需要开源 VLM 数据适配的 OMS demo，能够解释训练是否可行、资源花在哪里、何时需要某种优化，以及应该采集什么证据。

前置知识：Transformer/VLM 推理主链、next-token loss、SFT masking、反向传播、AdamW、混合精度、checkpoint 和评测合同。

本文覆盖单卡 SFT/PEFT、训练显存、分布式并行、算子 IO、profiling 和 OMS 决策；当前不要求实现完整 SFT、多机训练、复杂 pipeline schedule 或 CUDA/Triton kernel。

对应学习记录：[[02_Projects/AI-Career-Transition/20_学习记录/P02A_VLM模型工程认知_学习记录]]。

## 1.2 依赖顺序

```text
单卡训练主链
→ 显存与 step 时间分解
→ PEFT / checkpointing / precision 取舍
→ 多 GPU 并行解决什么问题
→ 算子 IO 为什么影响性能
→ profiler 如何验证瓶颈
→ 迁移到 OMS VLM 适配决策
```

# 2 单卡 VLM SFT 主链

```text
授权数据与任务合同
→ 图像/视频预处理 + chat template
→ visual tokens + text tokens
→ labels 与 loss mask
→ forward 得到 logits/loss
→ backward 生成梯度
→ optimizer/scheduler 更新可训练参数
→ checkpoint + 固定评测合同
→ 与 zero-shot/few-shot 基线比较
```

训练能运行只证明执行链成立。还要回答：数据是否覆盖目标错误、loss 是否监督预期输出、可训练模块是否合适、结果是否在未参与调参的数据上稳定提升。

## 2.1 VLM 可训练边界

| 模块 | 常见选择 | 主要取舍 |
|---|---|---|
| vision encoder | 冻结或局部解冻 | 冻结省资源并降低小数据破坏风险；解冻可能适配视觉域，但成本与过拟合风险更高。 |
| projector | 训练或 adapter | 影响视觉特征进入语言空间的适配。 |
| language model | 冻结、LoRA 或全量训练 | LoRA 更适合资源受限小规模适配；全量训练成本和遗忘风险更高。 |

必须能解释“冻结了什么、训练了什么、optimizer 实际包含什么参数”。

## 2.2 SFT label masking

常见 SFT 只让 assistant answer token 贡献 loss；prompt、padding 和无效位置使用 ignore index。错误 masking 可能导致模型学习复述问题、预测 padding，或有效 token 统计错误。考核时要能在最小样本上指出 input、监督目标、忽略位置及 shift 由谁完成。

# 3 训练资源预算

训练峰值至少包含：

```text
模型参数 + 参数梯度 + optimizer states + activations
+ CUDA kernel / 临时 buffer / 通信 buffer / allocator reserve
```

参数规模主要决定前三项；batch、序列长度、层数和 hidden size 显著影响 activation。VLM 还要考虑分辨率、patch/token 数、视频帧数和 vision encoder 中间特征。不能只用权重文件大小估算训练显存。

| 杠杆 | 直接改变 | 代价或边界 |
|---|---|---|
| micro-batch | 单次 activation | 吞吐可能下降。 |
| gradient accumulation | 用多次 micro-batch 模拟 global batch | 不消除参数和 optimizer 显存。 |
| checkpointing | 少存 activation、反向重算 | 以计算换显存。 |
| BF16/FP16 | 计算与部分 tensor 字节数 | 受稳定性和硬件支持约束。 |
| LoRA | 可训练参数、梯度和 optimizer state | 不消除 base weights 与 activation。 |
| QLoRA | base weights 存储精度 | 有量化误差和 kernel/框架约束。 |
| FlashAttention | attention 中间 IO 与保存方式 | 收益依赖 shape、硬件、版本和框架。 |

统一追问：是否能放入显存？GPU 是否在有效计算？多卡时间是否被通信吞噬？

# 4 分布式训练地图

| 策略 | 基本做法 | 首要问题 | 当前掌握深度 |
|---|---|---|---|
| gradient accumulation | 单卡顺序处理 micro-batches | activation 容量/global batch | 能计算 batch 关系并说明它不是并行。 |
| DDP | 每卡完整模型，不同数据，all-reduce 梯度 | 模型能放下时提高吞吐 | 能解释同步点、global batch 和通信。 |
| ZeRO/FSDP | 分片 optimizer、梯度或参数 | 单卡放不下训练状态 | 能解释分片对象和 gather 代价。 |
| TP | 层内切矩阵或 heads | 单层/模型无法单卡容纳 | 能指出高频 collective 和互联要求。 |
| PP | 按层切 stage、micro-batch 流水 | 模型纵向切分 | 能解释 pipeline bubble。 |
| CP/SP | 沿序列维切计算或 activation | 超长上下文 | 能关联 VLM 高分辨率/视频 tokens。 |

最小决策顺序：先判断容量还是吞吐；activation 超限先看 batch/sequence/checkpointing/attention IO，训练状态超限再看 PEFT 或 FSDP/ZeRO，单层仍过大才考虑 TP/PP 或更小模型。

# 5 算子级 IO 心智模型

GPU 要在主机内存、PCIe/NVLink、HBM、片上 cache/shared memory/register 间搬运数据。若算术单元等待数据，理论 FLOPs 不会自动变成吞吐。

FlashAttention 用 tiling 分块处理 Q/K/V，在片上存储完成局部计算，并按需重算部分量，减少 HBM 流量和中间 activation 保存。必须保留：它是精确 attention；核心计算量仍二次增长；算子加速不等于端到端同比加速。

VLM 的 ROI、抽帧、视觉 token 压缩会改变输入或 token 数；FlashAttention 优化给定 attention 的执行方式，二者不是同一层杠杆。

# 6 Profiling 与证据链

最小观测包括：模型/数据/input shape/precision/可训练参数/版本，warmup 后 step time 与吞吐，peak allocated/reserved，forward/backward/optimizer/data/eval 时间，kernel/memcpy/sync/collective/idle，以及 loss、有效监督 token、gradient norm、学习率和 checkpoint。

```text
确认任务与输入合同
→ 确认 shape、dtype、可训练参数和 loss mask
→ 测单 step 显存与时间
→ 区分数据、计算、IO、同步或通信瓶颈
→ 只改变一个主要杠杆
→ 用同一合同复测质量、吞吐和显存
```

“GPU 利用率低”不是根因；“启用了 FlashAttention/FSDP”也不是优化完成证据。

# 7 OMS VLM 适配决策

只有任务输出与非目标、数据授权、zero/few-shot 或其他基线、错误分类、独立验证数据和资源/部署目标明确后，才打开最小 LoRA/QLoRA 分支。

当前阶段交付是：训练主链图、显存与杠杆表、并行选择树、profiler 计划，以及“何时不该微调或上分布式”的反例，不要求完成 SFT。

# 8 主动考核骨架

每单元按闭卷重建、边界辨析、迁移决策三层检查：

| 单元 | 闭卷主问题 | 边界题 | OMS 迁移题 |
|---|---|---|---|
| A 单卡 SFT | 从样本到 optimizer step 发生什么？ | loss mask 与 attention mask 有何不同？ | 哪些 VLM 模块冻结、LoRA 或解冻？ |
| B 显存 | 训练显存各项何时存在？ | accumulation 为什么不省掉全部显存？ | T4 OOM 先检查哪些量和 shape？ |
| C PEFT | LoRA/QLoRA 改变哪些状态？ | 权重量化与 activation 量化是否同义？ | 小数据为何不默认全参微调？ |
| D 分布式 | DDP/FSDP/TP/PP 各切分什么？ | DDP 与 accumulation 本质区别？ | 单卡能放下但慢，是否直接 FSDP？ |
| E 算子 IO | FlashAttention 为何更快更省？ | IO、显存与 FLOPs 复杂度如何区分？ | 高分辨率 VLM 变慢怎样定位？ |
| F Profiling | step 时间和显存如何分解？ | utilization 为何不能单独证明高效？ | 如何做只变一个杠杆的 A/B profile？ |

## 8.1 完成门禁

- [ ] 闭卷画出单卡 VLM SFT 主链并解释 label masking。
- [ ] 分解训练显存并针对 OOM 给出有顺序的检查计划。
- [ ] 区分 LoRA、QLoRA、checkpointing、precision 与 FlashAttention 的直接作用。
- [ ] 用容量、吞吐、通信解释 DDP、FSDP/ZeRO、TP、PP、CP。
- [ ] 用 HBM/SRAM、tiling、recomputation 解释 FlashAttention并保留复杂度边界。
- [ ] 为 OMS VLM 适配写 profiler/评测计划，并说明何时不执行 SFT 或分布式。
- [ ] 完成至少两道新情境迁移题，不依赖背诵框架名。

完成代表认知可用，不代表 SFT、集群训练或 kernel 实现已验证。

# 9 原文阅读路线

Ultra-Scale Playbook 第一轮只读来源卡指定章节，每段回答“解决容量、利用率还是通信；交换什么；用什么 profile 证明”。FlashAttention 原文重点重建 HBM→SRAM tiling、长序列并行度和端到端边界。通读不是门禁。

- [[04_Sources/模型工程/2026-08-20_Ultra-Scale-Playbook来源证据卡]]
- [[04_Sources/模型工程/2026-08-20_FlashAttention长序列优化来源证据卡]]
