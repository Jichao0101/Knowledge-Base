---
type: project_learning_record
status: closed_by_scope
project: AI-Career-Transition
learning_stage: Phase 1-A - LLM mechanism and training
record_role: durable_stage_learning_record
summary: 保存 LLM 推理与训练阶段的闭卷题、主动学习诊断、TinyCausalLM 实践证据、范围豁免和阶段关闭决定。
sources:
  - 2026-07-21 第一阶段与第二阶段主动学习对话
  - 2026-07-25 Adam/AdamW 闭卷检查与最小训练实践
  - 2026-08-01 TinyCausalLM 单步训练运行、AMP 与 checkpoint 续测
  - 2026-08-04 TinyCausalLM 单 batch 过拟合、确定性评估与 checkpoint 轨迹恢复
  - 2026-08-06 Phase 1-A closure 诊断与范围决定
  - 02_Projects/AI-Career-Transition/10_学习文档/P01A-01_LLM推理机制_学习文档.md
  - 02_Projects/AI-Career-Transition/10_学习文档/P01A-02_LLM训练机制_学习文档.md
  - 02_Projects/AI-Career-Transition/20_学习记录/当前阶段学习检查点.md
scope: Phase 1-A 的个人诊断、实践结果、完成边界和未验证项。
risks:
  - working 只表示主动诊断中的可用理解，不能替代独立实现或运行证据。
  - TinyCausalLM 结果来自用户运行与静态审查，本轮未由代理独立复跑。
  - checkpoint 实验使用 CPU 内存快照，不代表磁盘、跨设备或生产 recoverability 已验证。
single_pass_recoverable: false
updated_at: 2026-08-11
---

# 1 Phase 1-A LLM 机制与训练学习记录

## 1.1 文档职责

本文保存个人诊断、实践证据和阶段决定。稳定教学内容分别见：

- [[02_Projects/AI-Career-Transition/10_学习文档/P01A-01_LLM推理机制_学习文档]]
- [[02_Projects/AI-Career-Transition/10_学习文档/P01A-02_LLM训练机制_学习文档]]

## 1.2 LLM 推理闭卷题

1. 闭卷画出 `text → token IDs → embeddings → blocks → last hidden → LM Head → logits → decoding`，说明每一步输入、输出和 shape。
2. 解释为什么第 2 层不能继续直接使用原始 token embeddings 计算 Q/K/V。
3. 手写四个 token 的 causal mask，并解释为什么训练能并行、生成必须逐 token 进行。
4. 给定一组 logits，解释降低 temperature、设置 top-k 和 top-p 分别改变什么，并明确每一步只生成一个 token。
5. 画出 prefill 与第二个 decode step，说明旧 K/V、新 Q/K/V 和 cache 更新的位置。

可用理解的诊断边界包括：不跳过 tokenizer、embedding、LM Head 或 decoding；能解释逐层 Q/K/V、causal mask 的信息泄漏边界、logits 到 token 选择，以及 KV cache 节省和未节省的计算。

## 1.3 2026-07-21 第一阶段诊断

本轮使用主动回忆、苏格拉底追问、费曼复述和迁移题完成口头机制诊断，状态记录为 `working`。该状态只说明在对话提示范围内能解释主干并完成相邻迁移，不代表已完成闭卷独立重画、代码实现、测试、性能测量或故障定位。

已通过的诊断点：

- 能解释 causal mask 阻断未来 token 防止答案泄漏，并区分训练并行与生成逐 token。
- 能说明训练输入与监督标签错开一位；当前位置可读取自身输入，但监督目标是下一个 token。
- 能闭环说明 token IDs、embeddings、Transformer blocks、最后位置 hidden state、LM Head、logits、decoding 与新 token。
- 能说明 Q/K/V 在每层由该层输入 hidden states 重新计算。
- 能区分 attention 输出、完整 block 输出、最终 hidden state、vocabulary logits 和 softmax 概率。
- 能区分 temperature、top-k、top-p 与最终 greedy/sampling。
- 能区分 prefill 与 decode，并说明 KV cache 保存历史 K/V 而不保存历史 Q。
- 能用位置敏感性解释无位置信息时 attention 无法区分前缀排列顺序。
- 能迁移到 VLM：视觉 encoder 与 projector 改变输入 embedding 来源，后续 causal LLM 主干基本不变。

仍需在实践复核：完整序列训练通常不用增量解码意义上的 KV cache；logits 是未归一化分数；norm、residual 与 attention/MLP 顺序依架构而异。

## 1.4 2026-08-06 Phase 1-A closure 诊断

达到 `working` 的主题：

- 能区分双向 encoder、因果 decoder 和 encoder-decoder，并解释翻译中的 self-attention 与 cross-attention 边界。
- 能说明 multi-head attention、`W_Q/W_K/W_V`、`W_O`、residual、LayerNorm 和 FFN 的职责。
- 能区分 `unsupported_claim`、`fabricated_evidence` 和 `contradicted_by_evidence`；证据不可得时应 abstain 并报告限制。
- 能闭卷说明 scaled dot-product attention 的 shape、mask 维度和 `sqrt(D)` 缩放对 softmax 饱和的影响。

最终证据状态：

```text
encoder/decoder、Transformer block 主干、证据边界：working
scaled dot-product attention 数学机制与 shape：working
temperature、top-p、停止条件与上下文影响机制：working
位置编码作用、causal mask 隐式顺序与 RoPE 相对位置：working
自回归生成、teacher forcing 与文本生成伪代码：working
有证据/无证据回答边界：working

独立实现 scaled dot-product attention：waived_by_scope
真实采样参数抽样实验：waived_by_scope
手写完整 GPT、tokenizer 与 generation：waived_by_scope
真实 tokenizer → generation → decode 文本闭环：not_verified
真实模型有/无证据对照运行：not_verified
```

用户根据 Agent 开发与 AI Infra 的职业目标，确认 Phase 1-A 在调整后的课程范围内完成并转入 Phase 1-B。`waived_by_scope` 不等于已实现；若未来需要排查 attention、tokenizer 或 generation 故障，必须补充新的运行证据。

关闭决定前曾计划用固定 logits 和固定随机种子观察 temperature、top-p、最大输出长度和上下文变化，并补做有/无证据对照、真实文本生成链与位置编码复核；最终这些运行项按上述状态分别记为 `waived_by_scope` 或 `not_verified`，不再作为阶段阻塞项。

## 1.5 LLM 训练诊断题与完成边界

Adam/AdamW 闭卷题：

1. 不用公式解释一阶矩与二阶矩各记录什么。
2. 解释为什么大而振荡的梯度可能被抑制。
3. 解释 AdamW 为什么把 weight decay 从自适应梯度中解耦。

训练主链闭卷复述：

```text
tokens / labels / masks
→ forward / logits / loss
→ scale / backward / unscale / clip
→ AdamW / scheduler / zero_grad
→ checkpoint / eval
```

实践完成边界要求在最小训练实验中观察 loss 下降、有效梯度、参数真实更新，并完成一次 checkpoint 恢复验证。

## 1.6 TinyCausalLM 实践记录

截至 2026-08-04，实践文件为 `/home/jichao/test/llm_practice.py`。静态审查覆盖 tensor shape、next-token shift、有效监督 token、忽略位置、PAD 与 `label=-100` 一致性。

用户能解释：原始位置 3 的 ASSISTANT hidden state 产生位置 3 的 logits，而 shift 后它与原始位置 4 的 label `A` 配对；ASSISTANT 自身 label 为 `-100`，只表示不要求前一位置直接预测该模板 token。

2026-08-01 用户使用 `/home/jichao/miniconda3/envs/openmmlab/bin/python` 运行单步训练，报告：

```text
loss: 2.095466136932373
grad_norm: 6.997917486628188
lm_head_delta: 0.00010000145994126797
```

这证明当次 shifted cross-entropy、backward 与 AdamW 更新链路产生 finite nonzero gradient 和参数变化，但单步证据本身不等于过拟合。

2026-08-04 用户运行单 batch 过拟合路径，报告：

```text
overfit:(loss:0.0916125476360321),(accuray:1.0)
```

shift 后有 3 个有效监督 token，因此 accuracy 对应 `3/3`；eval loss 低于预设阈值 `0.1`。评估函数在 `model.eval()` 与 `torch.no_grad()` 下使用更新后参数重新 forward，并在 loss 前检查有效 token 数。

同日用户运行 `recover_trajectory()`，报告：

```text
max_loss_diff = 0
max_grad_norm_diff = 0
max_lm_head_delta_diff = 0
max_param_abs_diff = 0
```

静态审查确认 checkpoint 对 model、optimizer 和 CPU RNG 做了独立快照；恢复时先加载 model/optimizer，再在下一次带 dropout 的 forward 前恢复 RNG；两个分支在相同 M 步后比较。

## 1.7 实践证据边界

- 结果来自用户运行与静态代码审查，本轮未由代理独立复跑。
- 未保留逐 step loss 曲线。
- 恢复实验使用内存 checkpoint，且当时代码未把 `global_step` 写入 checkpoint。
- scheduler、GradScaler、CUDA RNG、DataLoader/Sampler 状态、磁盘序列化、错误 label mask 对照和变长 micro-batch 等价性仍未验证。
- 因此只可标记“最小训练实践已完成（用户运行 + 静态审查）”，不得外推为生产训练闭环或独立 recoverability verification。

## 1.8 阶段关闭

Adam/AdamW、训练主链、有效 token 加权、AMP 缩放顺序、global step、RNG 与 checkpoint 主干通过主动学习检查；TinyCausalLM 取得单步梯度/参数变化、单 batch 确定性 eval 门禁和 CPU 内存 checkpoint 轨迹恢复证据。当前主线转入评测基本功，不以局部训练加固继续阻塞。
