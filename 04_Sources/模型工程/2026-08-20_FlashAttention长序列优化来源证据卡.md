---
type: source_card
status: active
source_type: web
source: https://hazyresearch.stanford.edu/blog/2023-01-12-flashattention-long-sequences
summary: Hazy Research 以长序列 FlashAttention 说明 attention 的 HBM/SRAM 数据搬运、tiling、重计算与并行度如何影响速度和显存。
scope: Phase 2-A 的算子 IO、VLM 视觉 token 长度、FlashAttention 边界与性能证据判断。
risks:
  - 页面发布于 2023 年，具体速度对应当时实现、A100 和给定 shape，不能直接外推到 T4 或其他版本。
  - FlashAttention 是 attention 子系统优化，端到端瓶颈也可能在预处理、vision encoder、数据加载、通信或解码。
  - 理解 IO-aware 原理不等于具备 CUDA/Triton kernel 实现能力。
updated_at: 2026-08-20
---

# 1 FlashAttention 长序列优化来源证据卡

## 1.1 来源与关联

- 原文：https://hazyresearch.stanford.edu/blog/2023-01-12-flashattention-long-sequences
- 关联：[[02_Projects/AI-Career-Transition/10_学习文档/P02A-01_VLM模型工程认知_学习文档]]

## 1.2 本阶段阅读重点

1. 标准 attention 为什么产生大量中间数据和 HBM 读写。
2. tiling 如何把 Q/K/V 分块搬入更快的片上存储。
3. 为什么重排计算和 recomputation 可以降低显存与 IO，而不近似 attention。
4. 长序列、小 batch、较少 heads 时为什么可能缺少并行度。
5. 为什么算子 benchmark 不自动代表 VLM 端到端收益。

## 1.3 可支持的认知结论

- FlashAttention 的关键是减少高成本内存读写并避免完整 attention 中间矩阵落入 HBM。
- 它保持精确 attention；核心计算量仍随序列长度二次增长，不能写成“计算复杂度线性”。
- VLM 的分辨率、patch/token 数和视频帧数会放大序列长度问题。

当前阶段不要求手写 CUDA/Triton kernel。
