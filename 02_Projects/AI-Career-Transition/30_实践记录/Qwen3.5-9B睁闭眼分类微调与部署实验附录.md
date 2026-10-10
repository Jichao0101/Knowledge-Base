---
type: project_experiment_evidence_appendix
status: active
project: AI-Career-Transition
summary: 按实验主题保存运行条件、原始测量、可见输出及工件入口；分析结论见实验记录，文档修订过程独立归档。
scope: Qwen3.5-9B实验的可核对数据与来源，不承载操作方案或历史接替叙述。
single_pass_recoverable: false
updated_at: 2026-10-10
---

# 1 Qwen3.5-9B睁闭眼分类微调与部署实验附录

本附录按实验主题保存原始测量、可见输出、运行条件和工件入口；结果分析与配置决定见[[02_Projects/AI-Career-Transition/30_实践记录/Qwen3.5-9B睁闭眼分类微调与部署实验记录]]，方法与验收见[[02_Projects/AI-Career-Transition/00_规划/Qwen3.5-9B睁闭眼分类微调与部署实验方案]]。实测日期用于识别实验轮次，不按文档修订顺序组织阅读。

来源为截图时，以下内容仅是当时可见字段的转录，不等于完整JSON或原始日志。临时截图未长期归档，不以文件名声称附件现可访问，也不补造缺失数据。

## 1.1 运行环境与来源

报告时间：2026-09-15～17；来源为用户运行输出，未在本次整理中重新测量。

| 项目      | 报告时配置与快照                                                                       |
| ------- | ------------------------------------------------------------------------------- |
| GPU     | 4张RTX PRO 5000 72GB Blackwell，每卡73415MiB；driver 580.126.20                      |
| 占用      | GPU 0已释放，当时显示0MiB/73415MiB；GPU 1～3仍有进程占用，本步骤仅使用GPU 0                            |
| PyTorch | 2.10.0+cu128，runtime CUDA12.8、CUDA available=True                               |
| Python  | python3.11                                                                      |
| 训练依赖    | transformers5.2.0、huggingface-hub1.8.0、accelerate1.13.0、pillow11.3.0、peft0.18.1 |
| 扩展      | causal-conv1d1.6.1、flash-linear-attention0.4.2；包存在不代表kernel已执行                  |
| 图文接口    | Qwen3.5图文生成已有报告；格式归一化后40图均可解析，非原生裸JSON通过声明 |
| 推理引擎    | vLLM0.17.1导入exit0、CLI可用；SGLang未安装，无需同时安装                                        |
| 离线约束    | 云桌面无网络；Turbo约6809.5GiB空闲                                                        |
| 模型      | /workspace/dms-eye-status-turbo/qwen_models/Qwen3.5-9B                          |

资源快照截图标识：`codex-clipboard-489234ea-43f9-4fad-bc92-e067e409d9c3.png`、`codex-clipboard-86473abc-fd2d-4eb9-9fa7-e56744378470.png`、`codex-clipboard-e53f9a0e-089f-4ddf-95f8-98d2a1b5a326.png`、`codex-clipboard-cf588378-87c0-4311-ba13-4170bb47174b.png`。GPU空闲、进程占用、磁盘空间都是当时快照，不表示当前资源。

## 1.2 Processor输入规模

### 1.2.1 分类prompt测量（2026-09-17）

来源：用户截图`codex-clipboard-b15e2939-4b4f-4762-a8d4-62e2411bc9fd.png`，样本来自67批次。完整输出JSON及云端脚本未归档核验；截图脚本hash与已保存探测脚本不同。

| 字段 | 可见值 |
|---|---|
| 原图宽高 | [1808,2592] |
| 处理后宽高 | [1792,2592] |
| image_grid_thw | [[1,162,112]] |
| pixel_values.shape | [18144,1536] |
| grid.shape | [1,3] |
| 视觉token | 4536 |
| 总输入token | 4614 |
| 其他输入token | 78 |
| 生成预留 | 128 |
| 所需context | 4742 |
| 4096是否满足 | false |

归档的[processor探测脚本](assets/Qwen3.5-9B/s01_processor_probe.py)只作来源材料，不等同该云端运行版本；已有SHA-256为`36e5ced53d019e87092b85bc63397040e0c56f54e04dd739007c8930029e32e4`。

### 1.2.2 检测prompt测量（2026-09-18）

来源：用户截图`codex-clipboard-220b4088-aa37-4cba-ad3e-2b83c025c19f.png`；未读取云端完整JSON。与上一轮分开记录。

| 字段 | 报告值 |
|---|---:|
| 视觉token | 4536 |
| 文本及模板token | 196 |
| 总输入token | 4732 |
| processor阶段生成预留 | 128 |
| 所需context | 4860 |
| 5600预算余量 | 740 |

2026-09-21实际generate采用256上限，输入与输出字段另见1.4，不混入本轮processor预留。

## 1.3 权重与模型加载

### 1.3.1 本地checkpoint头部统计（2026-09-16）

来源：代理读取config、processor及四个safetensors header，未读完整payload或加载GPU。

| dtype | tensor数 |           元素数 |                  tensor字节数 |
| ----- | ------: | ------------: | -------------------------: |
| BF16  |     727 | 9,653,100,528 |             19,306,201,056 |
| FP32  |      48 |         3,840 |                     15,360 |
| 合计    |     775 | 9,653,104,368 | 19,306,216,416，约17.9803GiB |

按名称分组的存储量约为语言/其他16.68GiB、视觉0.85GiB、MTP0.45GiB。

[权重头部核验工件](assets/Qwen3.5-9B/2026-09-16_model_header_evidence.json)，已有SHA-256为`5250321a90f71860643e69bd8d28b09250d12ff8d25f0b8931ef35e0acee34d8`；包含分片长度、header hash、config/processor内容及dtype/shape统计。header hash不覆盖payload。

### 1.3.2 云端模型加载（2026-09-17）

来源：用户截图`codex-clipboard-d07f7d89-6ab6-4f32-a6f7-e1195759f41b.png`中的load_metrics.json。stage=`model_loaded_no_forward`；加载耗时17.924108689650893s，开启memory history；未归档完整加载日志或snapshot。

| 指标 | 加载前 | 加载后 |
|---|---:|---:|
| allocated（GiB） | 0 | 17.5272193 |
| reserved（GiB） | 0 | 17.5410156 |
| peak allocated（GiB） | 0 | 17.5272293 |
| peak reserved（GiB） | 0 | 17.5410156 |
| 设备总占用（GiB） | 0.3341675 | 17.9279175 |
| 设备空闲（GiB） | 70.7895508 | 53.1958008 |

| 字段 | 报告值 |
|---|---|
| parameter_layout | cuda:0 / torch.bfloat16 |
| 参数numel | 9409813744 |
| 参数bytes | 18819627488 |
| 加载后allocated精确值（GiB） | 17.52721929550171 |
| 加载后reserved精确值（GiB） | 17.541015625 |
| peak allocated精确值（GiB） | 17.52722930908203 |

该运行未执行forward或优化器更新。

## 1.4 单图推理测量与输出

轮次：2026-09-21，用户报告。运行目录：`vlm_eye_experiment/runs/s01/infer_20260921_155244_025105`。可见文件包括first_metrics.json、repeat_03_metrics.json、summary.json、load_metrics.json、prompt.txt；未读取repeat_01/02完整记录。

| 指标 | 首次 | 第3次重复/汇总 |
|---|---:|---:|
| 输入token | 4732 | 4732 |
| 生成token（含特殊标记） | 95 | 95 |
| max_new_tokens | 256 | 256 |
| generate耗时（秒） | 43.29743397794664 | 第3次2.643217164091766 |
| 后续3次耗时（秒） | — | 均值2.7742946908498802；中位数2.643217164091766 |
| 推理前allocated（GiB） | 17.58002471923828 | 17.58893632888794 |
| 峰值allocated（GiB） | 18.549700260162354 | 18.511788845062256 |
| 相对起点峰值增量（GiB） | 0.9696755409240723 | 0.9228525161743164 |
| 推理后allocated（GiB） | 17.588972568511963 | 17.588972568511963 |
| 推理后/峰值reserved（GiB） | 19.021484375 | 19.021484375 |
| 推理后设备空闲（GiB） | 51.44384765625 | 51.44384765625 |

计时范围仅为CUDA同步后的model.generate，不含加载、读图、processor、H2D、解码或写盘；未启用memory history。summary报告首次和三次重复输出一致，均EOS结束、未触顶，strict格式失败、quality_evaluated=false。

可见原始回答带json代码围栏，内部为数组；字段为bbox_2d、label、state。可见值如下（仅重排已转录字段，不冒充完整输出文件）：

```json
[
  {"bbox_2d":[290,415,323,433],"label":"image_left_eye","state":"open"},
  {"bbox_2d":[355,392,390,409],"label":"image_right_eye","state":"open"}
]
```

解析器报告`Expecting value: line 1 column 1 (char 0)`。本轮未读取原图/GT完成几何评分，框的实际尺度与定位正确性未验证。

截图路径前缀C:/Users/Jichao/AppData/Local/Temp/：
- codex-clipboard-e3112015-dffc-4eea-b9b6-50f582875287.png：repeat_03。
- codex-clipboard-55b078c1-9758-4b50-81a4-cfdbb393e5ce.png：summary。
- codex-clipboard-03dd33db-b089-461e-a3c0-9d63bddbfdf6.png：first_metrics。
- codex-clipboard-12ffd358-9281-4b65-870c-9a769b04f3d8.png：load_metrics局部，仅见generation_config及transformers_version=5.2.0，非完整环境核验。
- codex-clipboard-19191582-4ab7-427d-a2f6-967591bf8738.png：prompt局部，1808×2592、单个image_pad和空think块，长指令未完全显示。


## 1.5 开发集40图诊断

轮次：2026-09-30，用户截图报告。直接从原始数据抽样；完整分组清单、代码版本及预测工件未归档核验。此轮与1.4不是同一次运行，与后续独立9B/2B对照也不混算。

| 字段 | 报告值 |
|---|---|
| 图片 / 眼睛 | 40 / 80 |
| 有效预测图片 | 40 |
| GT读取错误 | 0 |
| 同侧平均IoU | 0.35211651622369833 |
| valid平均IoU | 0.35211651622369816 |
| IoU≥0.5时TP / FP / FN | 15 / 65 / 65 |
| precision / recall | 0.1875 / 0.1875 |
| 匹配后左右 / 状态准确率 | 1.0 / 1.0，仅15个open眼睛 |
| 匹配混淆矩阵 | 15个open→open，其他类别F1为null |
| 单眼端到端成功率 | 0.1875 |
| 双眼成功率 | 0.125 |

可见示例：双眼open预测框大于GT，IoU约0.328/0.424；另一图GT为左closed/右narrow，预测均closed，左框偏大、右框偏移且IoU=0。截图未展示IoU≥0.75结果，不补造。

来源截图位于C:/Users/Jichao/AppData/Local/Temp/：
- codex-clipboard-a24aa12e-f9bd-4794-b586-a114ca57e1a3.png：双眼open示例，预测框大于GT，IoU约0.328/0.424。
- codex-clipboard-8f09308f-40da-41e7-a671-e626c1bd9c96.png：GT左closed/右narrow，预测均closed；左框偏大，右框偏移、IoU=0。不能将全部错误概括为框偏大。
- codex-clipboard-6fa3c5cd-d898-4ba0-8b60-9bbeaba94c4f.png：40图/80眼、有效预测40图、GT读取错误0；平均同侧IoU=0.35211651622369833（valid均值0.35211651622369816）；IoU≥0.5时TP=15、FP=65、FN=65、precision/recall=0.1875，匹配后左右及状态准确率均1.0。
- codex-clipboard-74939fdc-7558-4305-8c82-c3b7f65d3c45.png：匹配混淆矩阵只有15个open→open；其余类别F1为null；单眼端到端=0.1875、双眼成功率=0.125。
- codex-clipboard-fba32067-d73c-482f-992f-9a20deba4d05.png：与上一张内容相同，不计为独立证据或第二次运行。截图未展示0.75阈值结果，不补造。


## 1.6 数据与性能代码验证材料

### 1.6.1 本地数据/代码验证（2026-10-03）

来源：当次代理工具输出；验证目录`/home/jichao/test/vlm_experiment`，数据目录`/home/jichao/test/data`。以下是当次实现的结果，不用旧schema或校验策略描述当前代码。

| 观察项 | 当次结果 |
|---|---|
| 原始图片 | 4189 |
| hard排除 | 66 |
| 保留图片 | 4123 |
| 本地train（71/75） | 2633 |
| 本地test（79） | 1490 |
| 77验证批次 | 本地无此批次 |
| 契约测试 | 11项通过 |
| 保留图片解码/尺寸/内容核验 | 4123图，无读取错误 |
| Norm1000转换及反算 | 4123条通过，误差不超过半个量化步长，状态不变 |

当次临时清单、测试脚本、报告和探测结果已按用户要求清理；没有持久验证工件可重新打开。测试覆盖范围与当时schema均属于该次本地检查，不表示当前版本重测通过，也不表示云端模型推理完成。

### 1.6.2 云端数据构建确认（2026-10-08）

来源：用户人工确认“数据集已成功构建”，并明确无需截图、人工确认即可视为通过。这里只保存确认事实；未获得正式清单数量或完整构建报告，不补造统计值。

### 1.6.3 性能脚本本地检查（2026-10-10）

代码：`/home/jichao/test/vlm_experiment/src/s02_sample_eval.py`；参数：同仓库sample_eval.json。此前本轮实现让benchmark/profile共用batch_sizes，profile保存五阶段显存边界及峰值，普通benchmark仍保存整轮峰值。

| 检查方式 | 实际结果 |
|---|---|
| Python AST语法 / JSON结构 / diff格式 | 通过 |
| CUDA allocator模拟 | 阶段峰值与入口增量记录通过；失败阶段证据保留 |
| benchmark隔离检查 | 不被profile阶段峰值重置逻辑影响 |
| 扫描及OOM模拟 | 共用batch档位，OOM后停止更大档位 |
| worker结果模拟 | 完整批阶段汇总与包含尾批的整体峰值分别记录 |
| 云端GPU、真实模型、实际trace | 尚未实测 |

临时测试仅在/tmp执行，不留在代码仓；本地检查不是性能结果，不给出images/s、最优batch或训练容量。

## 1.7 资料维护

新实验按主题增加独立轮次，保存运行条件、来源、原始字段和工件路径；分析及决定写入实验记录。实验日期用于区分工作负载，旧测量只要仍有比较价值即可保留，不以“旧”自动判为无效。文档创建过程、过时操作说明和版本接替不再追加到本附录。

整理前两份文档的完整快照保存在[[90_Archive/02_Projects/AI-Career-Transition/Qwen3.5-9B实验文档整理前快照_2026-10-10]]，仅供追溯文档修订，不作为当前方法或状态入口。
