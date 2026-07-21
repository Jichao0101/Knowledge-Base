---
type: project_learning_checkpoint
status: in_progress
project: AI-Career-Transition
learning_stage: Phase 1 - LLM training mechanism
summary: 记录第二阶段 LLM 训练机制主动学习的已验证理解、薄弱项、未完成评测计划与跨设备恢复入口。
sources:
  - 2026-07-21 第二阶段主动学习对话
  - 02_Projects/AI-Career-Transition/AI职业转型项目总览.md
  - 02_Projects/AI-Career-Transition/LLM最小推理机制系统学习文档.md
  - 02_Projects/AI-Career-Transition/多模态AI职业转型学习方案.md
scope: next-token 训练目标、loss、梯度、训练循环、optimizer、mask 与 SFT 监督边界的理解诊断。
risks:
  - 本文是跨设备恢复检查点，不是完整学习文档，也不证明已完成代码实现或独立工程验证。
  - 部分结论是在引导和纠正后形成，必须通过后续闭卷复述或最小实验再次验证。
  - 未完成独立 recoverability verification，不声明 single-pass recoverable。
updated_at: 2026-07-21
---

# 1 LLM 训练机制主动学习检查点

## 1.1 检查点用途

本文件用于在切换设备后恢复第二阶段主动学习，不把对话顺序当作知识结构，也不把“听过纠正”写成“已经掌握”。

状态解释：

```text
已验证：能够主动解释主要机制或完成检查题。
部分闭合：理解主干，但在边界题中仍需提示或纠正。
待学习：当前回答表明心智模型尚未建立。
未评测：尚未进入该覆盖区。
```

## 1.2 当前阶段结论

第二阶段评测仍在进行中。当前可以确认 loss 与基础反向传播主干已经形成，训练循环边界达到可用理解；optimizer 自适应机制和 SFT prompt/label masking 尚未闭合，不能把“LLM 训练机制”标记为完成。

## 1.3 已验证内容

### 1.3.1 Cross-entropy 与正确 token 概率

- 能说明 one-hot next-token 监督下，正确 token 概率越高，cross-entropy 越低。
- 能说明正确 token 概率趋近 1 时 loss 趋近 0，概率趋近 0 时 loss 趋向无界增大。
- 已纠正一次“高正确概率对应更大 loss”的反向判断，后续检查回答正确。

### 1.3.2 Softmax 与 logits 梯度

- 能解释 softmax 分母耦合整个词表，因此一个正确标签仍会让全部 vocabulary logits 收到梯度。
- 能解释正确 token 的 logit 应增大、错误 token 的 logit 应减小；错误概率越高，受到的压制越强。

### 1.3.3 反向传播主干

- 能说明 LM Head 反向传播需要同时形成参数梯度和返回 hidden state 的梯度。
- 能按高层顺序描述误差信号穿过 MLP、residual 与 attention 返回更早层。
- 能解释 residual 恒等路径保留直接梯度通道；鉴于已有 CNN 背景，本阶段不继续深挖通用反向传播细节。

### 1.3.4 Train / eval / autograd 边界

- 已确认 `model.eval()` 只切换 dropout、BatchNorm 等模块行为，不会自动关闭梯度。
- 已确认 `torch.no_grad()` 关闭求导记录，但不会自动切换 dropout 行为。
- 已确认 `loss.backward()` 计算梯度，真正修改参数的是 `optimizer.step()`。
- 能说明常规推理需要组合 `model.eval()` 与 `torch.no_grad()`。

### 1.3.5 Mask 的基础分工

- 能区分 causal mask 屏蔽未来 token，attention mask 屏蔽无效 PAD 输入。
- 能说明某位置不能读取右侧 EOS 是因为未来信息边界，不能读取 PAD 是因为 PAD 不是有效输入。
- 理解 label mask / `ignore_index=-100` 用于排除不参与 loss 的位置。

## 1.4 部分闭合内容

### 1.4.1 梯度累积

已理解：

- 不调用 `zero_grad()` 会累积 `.grad`。
- 梯度累积可用多个 micro-batch 模拟更大 batch，而不是用“大梯度逃离局部最优”。
- 累积 4 次但不做相应缩放，会使梯度尺度约放大 4 倍。

仍需复核：

- 不等长序列必须按有效 token 数加权，不能简单平均每个 micro-batch 已经归一化的 loss。
- 梯度累积与单个大 batch 的等价条件，以及 dropout、BatchNorm、梯度裁剪时机造成的差异。

### 1.4.2 LM Head 的矩阵梯度

已理解需要分别计算 LM Head 参数梯度与返回 hidden state 的梯度，但未独立写出完整矩阵关系和 shape。该局部不是当前主阻塞项，后续以计算图和 ASCII shape 复核，不在 CLI 中要求依赖 LaTeX 渲染的矩阵推导。

## 1.5 明确薄弱项

### 1.5.1 Adam / AdamW 自适应更新

当前误区：

- 曾把梯度一阶移动平均理解为“平均速度”，把梯度平方移动平均理解为“平均加速度”。
- 曾推断“统计阶数越高，拟合程度越高”，这不适用于 Adam 的设计目的。

待建立的机制：

- 一阶矩如何平滑梯度方向并形成 momentum。
- 二阶矩如何估计每个参数的典型梯度尺度，而不是表示加速度。
- `m / sqrt(v)` 如何产生逐参数自适应步长。
- Adam 与 AdamW 的 weight decay 为什么不是同一实现。
- bias correction、epsilon 和 optimizer state 的基本作用。

### 1.5.2 SFT prompt 与 label masking

当前未闭合：

- 曾把用户 prompt 的 `attention_mask` 设为 0，同时保留其 label token ID，实际方向相反。
- 已获得详细解释，但尚未完成新的独立检查题，因此不能标记为已验证。

目标判断规则：

```text
System/User prompt：attention_mask = 1，label = -100
Assistant answer：attention_mask = 1，label 保留 token ID
PAD：attention_mask = 0，label = -100
```

需要进一步理解：prompt 虽然不直接计算监督 loss，answer loss 仍可通过 attention 路径影响如何利用 prompt。

## 1.6 本阶段明确排除项

- CNN 大 batch 与学习率线性缩放只是临时插问，用户已要求跳过，不纳入第二阶段完成门禁。
- 通用反向传播的逐算子矩阵推导与 CNN 差异不大，当前不作为主线深挖项。
- 不在本检查点扩展到 RLHF、DPO、分布式训练或完整预训练数据工程。

## 1.7 未完成评测计划

### 1.7.1 优先级 1：完成 mask 与 SFT 监督边界

恢复后的第一道题：

```text
一个样本包含 System 指令、User 问题、Assistant 回答和 PAD。
若只监督 Assistant 回答，四个区域的 attention_mask 与 labels 应怎样设置？为什么？
```

通过标准：

- 不再混淆“可以作为上下文读取”和“需要计算监督 loss”。
- 能解释 causal mask、attention mask、label mask 各自控制的计算阶段。
- 能说明 EOS、PAD 和 `ignore_index=-100` 的角色差异。

### 1.7.2 优先级 2：补齐 Adam / AdamW

学习和检查顺序：

```text
SGD 当前梯度更新
→ momentum / 一阶矩
→ 梯度平方移动平均 / 二阶矩
→ 逐参数尺度归一化
→ bias correction 与 epsilon
→ Adam 和 AdamW weight decay 对比
```

通过标准：能用纯语言和简单数值例子解释两类移动平均，不再使用“平均加速度”或“阶数越高拟合越好”描述二阶矩。

### 1.7.3 优先级 3：训练循环可靠性

待评测：

- 学习率 schedule 与 warmup 在训练循环中的位置。
- gradient clipping 应发生在 backward 之后、optimizer step 之前的原因。
- 混合精度下 loss scaling 要解决什么数值问题。
- checkpoint 恢复为什么除模型参数外还需要 optimizer、scheduler 与 step 状态。

### 1.7.4 优先级 4：最小实践验证

完成概念评测后，用极小 decoder-only 模型或最小训练脚本验证：

1. 构造一条可过拟合的小样本，观察 loss 是否下降。
2. 打印有效 token 数、被忽略 label 数和梯度范数。
3. 对比正确与错误 label mask，观察监督信号差异。
4. 验证 `train/eval`、`no_grad`、`zero_grad/backward/step` 的行为边界。

## 1.8 跨设备恢复顺序

切换设备后按以下顺序恢复：

1. 阅读 [[02_Projects/AI-Career-Transition/AI职业转型项目总览]] 的“当前状态”。
2. 阅读本文的“当前阶段结论”“明确薄弱项”和“未完成评测计划”。
3. 需要回顾推理前置时，再读 [[02_Projects/AI-Career-Transition/LLM最小推理机制系统学习文档]] 的训练目标与第一阶段进度。
4. 从 `1.7.1` 的 SFT mask 检查题继续，不重复第一阶段已经通过的 causal mask、KV cache 和 decoding 诊断。

本恢复顺序只提高人工恢复清晰度；由于没有在新设备上进行独立恢复验证，不声明 `single_pass_recoverable: true`。

## 1.9 阶段完成门禁

只有同时满足以下条件，才结束第二阶段评测并生成完整训练机制学习文档：

- 已验证 cross-entropy、softmax 梯度、训练循环和三类 mask 的作用边界。
- 已补齐 Adam/AdamW 一阶矩、二阶矩、自适应步长与 weight decay。
- 已覆盖 schedule/warmup、gradient clipping、混合精度和 checkpoint 状态的基本机制。
- 至少完成一次不依赖对话提示的训练主链复述。
- 已运行一个最小训练实验，或明确记录尚未具备实验环境并保持阶段未完成。

最终学习文档应按机制组织，重点展开薄弱项，不按聊天时间线堆叠问答记录。
