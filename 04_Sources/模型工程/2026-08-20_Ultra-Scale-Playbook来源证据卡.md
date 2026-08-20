---
type: source_card
status: active
source_type: web
source: https://nanotron-ultrascale-playbook.static.hf.space/index.html
summary: Hugging Face Ultra-Scale Playbook 以显存、计算效率和通信开销为主线，解释从单卡训练到多维并行的大模型训练工程。
scope: Phase 2-A 的训练显存、gradient accumulation、profiling、DDP、ZeRO/FSDP、TP、PP 与 CP 认知。
risks:
  - 材料主要面向大规模 LLM 集群，不能把全部实现深度直接设为 OMS VLM 学习门禁。
  - 并行布局和性能结论依赖硬件、互联、模型、shape 与软件版本，实际项目必须重新 profile。
  - 本卡只保存来源边界，不代表内容已掌握或实现。
updated_at: 2026-08-20
---

# 1 Ultra-Scale Playbook 来源证据卡

## 1.1 来源与关联

- 原文：https://nanotron-ultrascale-playbook.static.hf.space/index.html
- 关联：[[02_Projects/AI-Career-Transition/10_学习文档/P02A-01_VLM模型工程认知_学习文档]]

## 1.2 本阶段阅读路由

第一轮优先阅读 High-Level Overview、单 GPU 显存、activation recomputation、gradient accumulation、profiler、data parallelism、ZeRO/FSDP 与 tensor parallelism 概览。

pipeline schedule、3D/context/expert parallelism、集群拓扑和大规模 benchmark 细节留作按需阅读，不作为当前完成门禁。

## 1.3 可支持的认知结论

- 分布式训练主要在显存容量、计算利用率和通信开销之间取舍。
- 参数、梯度、optimizer state 和 activation 是训练显存核心组成；序列长度和 batch 会显著影响 activation。
- gradient accumulation、recomputation 与多 GPU 并行解决的问题不同。
- 扩展策略依赖实际硬件与互联，必须用 profiler 和吞吐测量验证。

这些结论用于组织学习问题，不直接作为具体 OMS 配置建议。
