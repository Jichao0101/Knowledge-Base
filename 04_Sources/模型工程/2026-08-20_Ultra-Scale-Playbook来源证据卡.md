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

## 1.4 2026-09-02 补充来源与口径边界

本节为 append-only 补充，不改写前述来源判断。

- 中文翻译页：https://github.com/pprp/ultrascale-playbook-zh/blob/main/docs/The%20UltraScale%20Playbook-Part1.md
- 显存 profile 原图：https://raw.githubusercontent.com/pprp/blogimagebed/main/image%2012.png
- 本地项目资产：`02_Projects/AI-Career-Transition/10_学习文档/assets/P02A-01/ultrascale-llama1b-memory-profile.png`
- 原图下载后 SHA-256：`e49dd5b22126b662eda4354e0e3c79b5551a6075dcea3a657efcd2db3848d82d`

写入学习文档时保留以下边界：参数量和 activation 公式来自特定简单 Transformer 假设，不直接代表完整 VLM；混合精度下 master weights、梯度 dtype 和 optimizer states 依赖训练栈；activation 对序列长度不能一概称为线性；recomputation、gradient accumulation、DDP 和状态分片解决的问题不同，性能结论必须以目标硬件、shape、软件版本和 profiler 结果复核。

## 1.5 框架实现校验来源

- PyTorch Automatic Mixed Precision examples：https://docs.pytorch.org/docs/stable/notes/amp_examples.html

该文档用于校验 `autocast`、gradient scaling 和 accumulation 的框架语义；它不替代 Ultra-Scale Playbook 的训练扩展主线，也不意味着其他训练栈采用相同的参数、梯度或 master-weight 存储布局。

## 1.6 2026-09-03 ZeRO 与 TP 图片来源补充

本节为 append-only 补充，用于记录 Phase 2-A 学习文档新增图片的原始来源与内容边界。

| 内容 | 原始图片 | 本地项目资产 | SHA-256 |
|---|---|---|---|
| Baseline DP 与 ZeRO-1/2/3 模型状态分片 | https://raw.githubusercontent.com/pprp/blogimagebed/main/image%2025.png | `02_Projects/AI-Career-Transition/10_学习文档/assets/P02A-01/ultrascale-zero-stages-memory.png` | `8bf26ba404491363cce449ac2d7cea2076de384de0903cc5cafe6b5bb40396d1` |
| ZeRO-1 reduce-scatter、局部更新与 all-gather | https://raw.githubusercontent.com/pprp/blogimagebed/main/image%2026.png | `02_Projects/AI-Career-Transition/10_学习文档/assets/P02A-01/ultrascale-zero1-step.png` | `3c5ba8309716d2b3f84984db36239d3f0fc001304f2b44b562b9c6e97a6ef912` |
| Column + Row parallel MLP | https://raw.githubusercontent.com/pprp/blogimagebed/main/image%2036.png | `02_Projects/AI-Career-Transition/10_学习文档/assets/P02A-01/ultrascale-tp-mlp-column-row.png` | `79b4178619e6781e092c48ddc9c591772c7cfff83aa8bfb31172a86e04686566` |
| Attention 的 QKV column split 与输出 row split | https://raw.githubusercontent.com/pprp/blogimagebed/main/image%2037.png | `02_Projects/AI-Career-Transition/10_学习文档/assets/P02A-01/ultrascale-tp-attention.png` | `ef5ef9f34bc99f76872aaad27fe38f146e274f1cc4aa8e6a2503222838f25eba` |

ZeRO 显存公式是忽略 activation、临时 buffer 和峰值参数物化的简化模型；stage 名称描述长期分片对象，collective 与生命周期由实现决定。TP 图片展示一种经典 column/row layout；实际是否执行 broadcast、scatter、all-gather 或 reduce-scatter 取决于相邻算子已经建立的张量布局。原材料中的固定通信量、collective 次数和 TP degree 性能拐点只作为对应配置下的分析示例。

## 1.7 2026-09-05 SP、CP、PP、EP 与多维并行来源补充

本节为 append-only 补充，用于记录 Phase 2-A 学习文档继续扩展时使用的原始页面、图片和口径边界。

- 中文翻译 Part 2：https://github.com/pprp/ultrascale-playbook-zh/blob/main/docs/The%20UltraScale%20Playbook-Part2.md
- 中文翻译 Part 3：https://github.com/pprp/ultrascale-playbook-zh/blob/main/docs/The%20UltraScale%20Playbook-Part3.md

| 内容 | 原始图片 | 本地项目资产 | SHA-256 |
|---|---|---|---|
| TP 区与 SP 区的 activation 布局转换 | https://raw.githubusercontent.com/pprp/blogimagebed/main/part_2_image%202.png | `02_Projects/AI-Career-Transition/10_学习文档/assets/P02A-01/ultrascale-sp-layout.png` | `25b98fbf13ebfc92c90271d84ceb03106fa59acdbd1e562fd5d8ca8d36269225` |
| Ring Attention 的 K/V 环形轮转 | https://raw.githubusercontent.com/pprp/blogimagebed/main/part_2_image%2010.png | `02_Projects/AI-Career-Transition/10_学习文档/assets/P02A-01/ultrascale-cp-ring-attention.png` | `da8bc790b8413a33cc8f66e631ab312da1755070eb8f2cae93d5dc6976688a42` |
| Zig-zag Ring Attention 的 causal mask 负载均衡 | https://raw.githubusercontent.com/pprp/blogimagebed/main/part_2_image%2012.png | `02_Projects/AI-Career-Transition/10_学习文档/assets/P02A-01/ultrascale-cp-zigzag.png` | `1137cf8b6135527382a7f1f5ce97a7d37287eee38231f5feb62cdae654e7087f` |
| AFAB pipeline schedule | https://raw.githubusercontent.com/pprp/blogimagebed/main/part_2_image%2017.png | `02_Projects/AI-Career-Transition/10_学习文档/assets/P02A-01/ultrascale-pp-afab.png` | `8fb15ca3f9a2adcab642b00ad6d675f7f841c223848a5280cd8e3dc70aef00c8` |
| 1F1B pipeline schedule | https://raw.githubusercontent.com/pprp/blogimagebed/main/part_2_image%2018.png | `02_Projects/AI-Career-Transition/10_学习文档/assets/P02A-01/ultrascale-pp-1f1b.png` | `5c26ea7a05630c87f88d74e2870e7f4bead77f6964409b8a997270826cf1161a` |
| Expert Parallelism 与 Data Parallelism 组合 | https://raw.githubusercontent.com/pprp/blogimagebed/main/part_2_image%2027.png | `02_Projects/AI-Career-Transition/10_学习文档/assets/P02A-01/ultrascale-ep-dp.png` | `dee1c6ff9d9658604865d231d2495d9bf62987e91ae91c89d8546eb83c9e219e` |
| DP、TP/SP、CP、PP 与 EP 的分片方向 | https://raw.githubusercontent.com/pprp/blogimagebed/main/part_2_image%2031.png | `02_Projects/AI-Career-Transition/10_学习文档/assets/P02A-01/ultrascale-5d-parallelism.png` | `a0194ceffc34bf10c954c423400f1957b48367131bcd2fa3e2cc807062312888` |

写入学习文档时保留以下边界：SP 是与 TP 配套的 activation 布局优化，不等于让 Attention 始终保持 sequence shard 的 CP；LayerNorm 在保留完整 hidden dimension 的 sequence shard 上可本地计算，复制参数梯度同步与 activation all-reduce 不应混为一谈；ring K/V exchange 不是 All-to-All；PP 的 $(p-1)/m$ 气泡比例依赖等 stage 耗时等简化假设；1F1B 主要降低在途 activation，不自动消除 bubble；EP 的 token dispatch/combine、All-to-All、capacity 与负载均衡不能被“比 TP 更轻量”掩盖。

Part 3 中按模型参数量、GPU 数量给出的组合是特定 H100 集群、固定 sequence length、global batch 和实现版本下的经验案例。可复用的是先满足容量、再校准 global batch、最后 profile 吞吐的搜索顺序，而不是固定的 10B、512 GPU 或 1024 GPU 阈值。

## 1.8 2026-09-05 Interleaving Stage 图片来源补充

本节为 append-only 补充，不改写 1.7 节既有记录。

- 内容：每个物理 pipeline rank 持有多个 model chunks 的 Interleaved Pipeline schedule
- 原始图片：https://raw.githubusercontent.com/pprp/blogimagebed/main/part_2_image%2020.png
- 本地项目资产：`02_Projects/AI-Career-Transition/10_学习文档/assets/P02A-01/ultrascale-pp-interleaved-stages.png`
- SHA-256：`c0d75c8ab4bfa02d684e23f4445ccf6bf397c9aacd36acf08e27daff5093741d`
