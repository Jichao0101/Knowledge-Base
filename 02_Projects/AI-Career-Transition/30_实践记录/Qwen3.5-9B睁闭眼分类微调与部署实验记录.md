---
type: project_continuous_experiment_record
status: active
project: AI-Career-Transition
record_role: primary_experiment_history
current_step: S02-B - batch size与DP推理实验准备（S02-C正式baseline待执行）
step_status: preparing
summary: 汇总资源验证与开发集抽样诊断的分析结果和决定；数据集构建已人工确认，batch/DP云端实验及正式baseline尚未完成。
sources:
  - 02_Projects/AI-Career-Transition/30_实践记录/Qwen3.5-9B睁闭眼分类微调与部署实验附录.md
  - 02_Projects/AI-Career-Transition/00_规划/Qwen3.5-9B睁闭眼分类微调与部署实验方案.md
  - 02_Projects/AI-Career-Transition/30_实践记录/assets/Qwen3.5-9B/2026-09-16_model_header_evidence.json
scope: 本实验的分析结论、实际进度、配置选择和验证边界；原始测量及输出由实验附录承载。
risks:
  - 依赖导入和权重文件检查不能替代GPU推理、训练或服务验证。
  - 权重头部检查不校验全部payload，也不能代替模型revision和完整文件hash。
single_pass_recoverable: false
updated_at: 2026-10-10
---

# 1 Qwen3.5-9B驾驶员眼睛检测与状态分类实验记录

## 1.1 实验目标与阅读方式

目标是评估Qwen3.5-9B整图双眼定位与四类状态判断，并按证据决定是否开展SFT/LoRA及后续部署。本记录保留分析后的关键结果、支撑资源判断的预算计算、配置决定和未解决问题；原始测量、输出和工件入口见[[02_Projects/AI-Career-Transition/30_实践记录/Qwen3.5-9B睁闭眼分类微调与部署实验附录]]。长篇原理说明、操作流程及验收条件以[[02_Projects/AI-Career-Transition/00_规划/Qwen3.5-9B睁闭眼分类微调与部署实验方案]]为准，不在记录中重复展开。

方案指导实验，实验产生记录。方案用E工作包定义方法，记录用S编号跟踪执行：S02-A为开发集抽样诊断，S02-B为推理效率实验，S02-C为正式baseline。新结果按实际运行条件解释；用户报告、代理本地验证和云端GPU实测分别注明，不互相替代。

## 1.2 当前进度

| 步骤  | 工程决策                           | 状态                                    |
| --- | ------------------------------ | ------------------------------------- |
| S01 | 9B BF16整图推理/LoRA是否适合现有GPU及输入预算 | partial；推理链路和解析可用，LoRA完整更新/资源待测       |
| S02-A | 开发集抽样诊断：链路可用性和错误线索 | user_reported；原始数据抽样40图，非正式baseline |
| S02-B | batch size与DP推理实验：确定全量推理执行方式 | preparing；单卡扫描、profiler与DP选择待执行 |
| S02-C | 正式baseline：完整验证集推理与错误归因 | pending_S02-B；数据集已构建，全量结果待执行 |
| S03 | 针对性训练是否有效；单卡更新与恢复是否正确 | pending_baseline；GT SFT＋语言LoRA保留为候选，质量训练尚未执行 |
| S04 | 双卡DDP是否保持目标一致，加速是否值得成本         | not_started                           |
| S05 | 教师优势与KD收益是否成立，按设计E4条件触发        | conditional_pending                   |
| S06 | 9B产物/精度组合是否满足质量、延迟和容量          | not_started                           |
| S07 | 双卡多副本的扩容、故障及回滚路径               | not_started                           |

当前先完成S02-B，确定全量推理执行方式，再建立S02-C正式baseline。S01训练资源验证可独立推进，S03质量训练依赖正式比较基准。已有40图仅提供局部诊断证据；数据集构建完成不等于baseline推理完成。

## 1.3 执行采用的数据与环境

### 1.3.1 数据

- 云端原始数据根目录：`/workspace/dms-eye-status-turbo/extract_data`；使用整图及同名JSON。
- 正式批次：67/68/70/71/75训练、77验证、79测试。完整会话目录是不可拆分的场景group；同一人员不同会话允许跨集合，人员交叠只统计，同场景或同内容图片跨集合拒绝。
- 按用户后续明确约定，`id=2`映射为`image_left_eye`，`id=1`映射为`image_right_eye`；不重新排序GT。四类为open/closed/narrow/occluded；hard、缺失或非法标注/框整图排除并记录原因，hard不归入occluded。
- 模型输出Norm1000整数xyxy；manifest保留像素GT及Norm1000监督目标，预测按实际宽高还原一次后对像素GT评分。不修框、不交换左右，不把GT或文件名送入prompt。
- 云端正式数据集构建完成，数据前置条件通过；正式split数量、类别覆盖及旧40图关系仍需由正式运行材料报告。本地71/75/79样例仅用于代码验证。

### 1.3.2 环境

4张RTX PRO 5000 72GB Blackwell（每卡73415MiB）、Python3.11、PyTorch2.10.0+cu128与Transformers5.2.0；
模型目录为`/workspace/dms-eye-status-turbo/qwen_models/Qwen3.5-9B`。
完整依赖版本和设备快照见[[02_Projects/AI-Career-Transition/30_实践记录/Qwen3.5-9B睁闭眼分类微调与部署实验附录#1.1 运行环境与来源]]。

## 1.4 实验结果与决定

### 1.4.1 结果总览

| 实验环节 | 分析后的结果 | 决定与验证边界 |
|---|---|---|
| 输入规模 | 单样本检测输入4732 tokens，视觉部分4536 | 5600预算可容纳该样本和256生成上限，不代表全数据最大输入 |
| BF16加载 | 常驻allocated约17.53GiB，加载峰值与结束值接近 | 保留BF16；未证明推理或训练容量 |
| 单图推理 | 生成链路可用，输出结构违约；首次约43.30s，热运行均值约2.77s | 先归因开销及处理输出协议；不以单图推断最大batch |
| 开发集诊断 | 定位不足，四类能力证据不完整 | SFT/LoRA为候选；先建立正式baseline |
| batch/DP | 实现已保存，尚无云端吞吐或扩展结果 | 待实测选执行配置，不承诺四倍加速 |
| LoRA更新 | 尚无实际完整更新与训练峰值 | 推理余量不能证明训练可行 |

### 1.4.2 步骤1：确定输入规模

#### 1.4.2.1 理论预算

H、W取processor处理后的高宽，p为patch边长，m为空间每个方向的合并数：

```text
N_visual ≈ H × W / (p² × m²)
所需context预算 ≥ 视觉token + 文本及模板token + 生成预留
```

按p=16、m=2估算不同处理后尺寸的视觉序列规模，先判断候选context能否覆盖整图输入：

| 处理后尺寸（宽×高） |             视觉token估算 |
| ---------- | --------------------: |
| 1024×768   |                   768 |
| 1920×1200  |                  2250 |
| 2592×1944  | 约4921，仍需processor尺寸对齐 |

较大整图仅视觉部分就可能超过4096，因此以5600作为起始context预算，并预留生成空间；是否足够，需测量processor实际输入长度。文本及模板开销取决于prompt，不能用视觉token单独判断容量。

#### 1.4.2.2 实验统计

检测prompt样本处理后宽高为1792×2592，视觉token=4536，文本及模板token=196，总输入4732。processor阶段生成预留128；后续generate采用256上限。旧分类prompt总输入4614，与本轮检测prompt分属不同配置。测量字段见[[02_Projects/AI-Career-Transition/30_实践记录/Qwen3.5-9B睁闭眼分类微调与部署实验附录#1.2 Processor输入规模]]。

#### 1.4.2.3 差异分析与决定

processor给出的1792×2592输入对应4536个视觉token，说明原图尺寸估算还需要处理后尺寸对齐。按实际输入4732计算，预留128时共4860、5600余740；生成上限256时共4988、余612。两轮预留不能混用。

**决定：保留5600作为起点，实际样本预算逐批检查。** 该样本有余量，不代表全数据或更大batch均可容纳；processor统计不涉及视觉编码或模型前向，尚未冻结全数据容量上限。

### 1.4.3 步骤2：加载模型并建立显存基线

#### 1.4.3.1 理论预算

按checkpoint header的元素数与dtype计算权重存储量：

```text
M_weights = Σ(元素数 × dtype字节数)
          = 9,653,100,528 × 2 + 3,840 × 4
          = 19,306,216,416 bytes ≈ 17.9803 GiB
```

这是BF16/FP32混合checkpoint的tensor存储预算。GPU加载后的常驻量还取决于实际加载的参数集合、dtype转换和框架分配；需要分别观察加载结束值与加载峰值，不能直接把17.9803GiB当作GPU实测。

#### 1.4.3.2 实验统计

BF16模型已报告加载成功。实际参数为18,819,627,488 bytes，allocated为17.52721929550171GiB；加载峰值约17.5272293GiB，与结束值接近。此时尚未执行forward或优化器更新。精确测量及header统计见[[02_Projects/AI-Career-Transition/30_实践记录/Qwen3.5-9B睁闭眼分类微调与部署实验附录#1.3 权重与模型加载]]。

#### 1.4.3.3 差异分析与决定

实测allocated比实际参数字节数多80,928 bytes，本次未见明显额外GPU加载峰值。checkpoint存储量比实际参数多486,588,928 bytes；MTP分组为486,581,248 bytes，3,840个FP32元素转BF16可节省7,680 bytes。这一差额提供MTP分组未加载、少量FP32转BF16的解释线索，但缺少逐参数及完整加载日志核验，仍保留为推断。

**决定：继续采用BF16开展推理。** 设备总占用与PyTorch allocator不是同一口径，不能相加；本结果不涉及activation、KV缓存或优化器状态，不能据此判定推理或训练峰值。

### 1.4.4 步骤3：跑通单图推理并测量开销

#### 1.4.4.1 理论预算

推理预算由常驻权重、视觉/prefill中间结果、缓存状态、logits/workspace及runtime共同组成；各项同时驻留情况决定峰值，不能累加各自峰值。先单列可估算的full-attention KV缓存：

```text
M_KV = L_full × 2 × B × S × n_kv × d_head × b_kv
     = 8 × 2 × 1 × 4096 × 4 × 256 × 2
     = 134,217,728 bytes = 128 MiB
```

预算假设为8层full attention、batch=1、缓存序列长4096、4个KV头、每头维度256、BF16每元素2 bytes；系数2对应K和V。128MiB不包含24层linear-attention状态、视觉中间结果或workspace，只用于说明该配置下传统KV的量级，不是完整推理显存。

#### 1.4.4.2 实验统计

单样本首次及三次重复均完成generate，输入4732 tokens，生成95 tokens，正常EOS结束且未触及256上限；四次输出一致，严格结构约定未通过。输出带代码围栏、顶层为数组，采用bbox_2d/label字段。

首次generate约43.30s，后续三次均值约2.77s；峰值allocated约18.55GiB，相对入口增加约0.97GiB。计时只覆盖同步后的generate；早期该样本未对照GT。精确值及可见输出见[[02_Projects/AI-Career-Transition/30_实践记录/Qwen3.5-9B睁闭眼分类微调与部署实验附录#1.4 单图推理测量与输出]]。

#### 1.4.4.3 差异分析与决定

实测输入长于KV预算示例的4096，且推理峰值增量包含多类中间状态，不能直接与128MiB比较后把差额全部归为activation或KV。该样本推理有余量，但首次额外开销尚无profiler归因，三次重复不能代表稳定p95。

正常EOS且未触顶表明本次格式失败不是截断造成的；仅剥离围栏仍不能修复数组及字段违约。**决定：分开检查输出协议和视觉质量，再用batch/profile测量提升效率。** 框数值及左右顺序不能证明定位正确，四次相同输出也不是四个质量样本。

### 1.4.5 步骤4：抽样诊断、batch/DP实验与正式baseline

#### 1.4.5.1 S02-A：开发集抽样诊断

40图/80眼均有可解析结果，同侧平均IoU约0.352，IoU≥0.5定位precision/recall为18.75%，双眼成功率12.5%。预测框偏大和中心偏移均有示例，不能固定一个收缩比例修复全部问题。接受代码围栏后的可解析率不等于原生裸JSON遵守率。

匹配后的左右及状态准确率100%仅覆盖15个open眼睛，不能证明四类能力。**决定：形成GT SFT＋语言LoRA候选；先建立正式baseline再评价训练收益。** 该40图直接从原始数据抽样，仅属已观察开发诊断，不充当正式验证或未见测试。原始指标与来源见[[02_Projects/AI-Career-Transition/30_实践记录/Qwen3.5-9B睁闭眼分类微调与部署实验附录#1.5 开发集40图诊断]]。

#### 1.4.5.2 S02-B：batch size与DP推理实验

数据集构建前置条件已人工确认通过。`/home/jichao/test/vlm_experiment/src/s02_sample_eval.py`已保存配置化benchmark与profile实现；2026-10-10完成profile与benchmark共用batch档位及分阶段显存测量的本地模拟验证。**实现可供云端运行，尚无实测最优batch、吞吐、显存峰值或DP收益。** 本地检查的具体范围见[[02_Projects/AI-Career-Transition/30_实践记录/Qwen3.5-9B睁闭眼分类微调与部署实验附录#1.6 数据与性能代码验证材料]]。

沿用本会话后续约定：效率实验随机采样，不要求场景覆盖、不计算GT精度；benchmark测稳定吞吐，profile解释阶段耗时和显存增长。推理profile只筛选微调候选batch，训练仍需独立测forward/backward/optimizer step。测试集不用于选参，正式精度评估保持独立。实际执行参数来自JSON，方法及验收仍由方案指导；这里不把尚未运行的扫描计划写成结果。

#### 1.4.5.3 S02-C：正式baseline阶段

**当前无云端全量baseline结果。** 数据构建与本地读取通过，均不代表模型推理完成。待S02-B确定执行配置后，按方案在冻结验证清单全量评估，并说明四类支持数及旧40图关系；推理/解析失败保留分母，测试集留给最终候选验收。

本阶段须建立LoRA前后的固定比较基准，不能将开发抽样报告改名充当baseline。zero-shot与按方案选择的few-shot结果分别报告。

#### 1.4.5.4 正式baseline之后的训练决定

GT监督定位＋四类状态SFT、首轮语言LoRA仍是候选。依据正式baseline错误组决定是否训练及更新范围；基准达标时可以进入部署验证，工程学习任务独立保留。loss下降、资源探测或代码生成均不等于质量收益。

### 1.4.6 步骤5：验证LoRA完整更新

#### 1.4.6.1 理论预算

训练显存包括冻结底座、adapter参数/梯度/优化器状态、反向保存的activation、视觉计算及logits/loss临时空间。先估算可训练状态；对输入维度d_in、输出维度d_out的目标线性层求和：

```text
N_LoRA = Σ[r × (d_in + d_out)]
M_states = N_LoRA × (b_param + b_grad + b_Adam_m + b_Adam_v)
```

候选r=16、覆盖语言主干二维投影，排除视觉、MTP、embedding及输出头时，adapter参数估算为43,278,336。若参数、梯度及Adam一阶/二阶状态均为FP32，共16 bytes/参数：`43,278,336×16=692,453,376 bytes≈0.6449GiB`。该预算不含activation、额外参数副本或loss空间；实际注入名单和dtype仍需核对。

另估算每个序列位置均保留完整词表输出时的logits：

```text
M_logits = B × S × V × b_logits
```

B=1、S=4096、V=248320时，BF16为`1×4096×248320×2=2,034,237,440 bytes≈1.8945GiB`；FP32约3.7891GiB。loss可能另有临时副本，也可能采用节省空间的实现；短JSON监督不保证只计算回答位置的logits。以上为训练预算示例，不可直接加到generate显存中。

#### 1.4.6.2 实验统计

**尚无实际LoRA完整更新或训练显存结果。** 真实模块、参数量、dtype、有效labels、首次/稳定更新及保存重载均待验证，不以0.6449GiB状态预算充当实测。

#### 1.4.6.3 差异分析与决定

目前没有训练实测可与预算比较。冻结底座不意味着无需保存训练activation，推理KV和adapter状态估算不能代替完整训练步峰值。

**决定：完整测量forward、backward及optimizer step后，再选择梯度检查点和输入预算。** 执行方法与验收查阅方案，不把估算列作通过结果。

### 1.4.7 步骤6：评估并固定资源方案

资源结论目前只支持BF16单图链路可运行；batch效率、训练容量和多卡收益尚未确定。**下一项待解决问题是S02-B执行配置选择，随后完成S02-C；S01剩余训练资源验证可独立推进。** 不将早期设备空闲快照当作当前资源保证，也不依据最大batch自动选择配置。

## 1.5 参考与附录

方法与验收：[[02_Projects/AI-Career-Transition/00_规划/Qwen3.5-9B睁闭眼分类微调与部署实验方案]]。原始测量、输出及工件：[[02_Projects/AI-Career-Transition/30_实践记录/Qwen3.5-9B睁闭眼分类微调与部署实验附录]]。每轮结果应能对应运行条件、来源与适用范围；原始材料不可取得时明确注明，不补造完整日志。
