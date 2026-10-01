---
type: project_experiment_plan
status: planned
project: AI-Career-Transition
summary: 以Qwen3.5-9B为部署目标及学生，整图输出驾驶员眼睛位置与四类状态；按图片坐标定义左右，以评测闭环推进训练与部署。
sources:
  - 2026-10-01 用户附件授权双轨优化、坐标合同补全及条件分支收紧；替代记录见实验附录O
  - 2026-09-16 用户授权连续实验记录及逐步更新规则
  - 2026-09-15 本会话用户对工业微调部署目标、模型角色、整图分类、双卡DP和独立文档的连续确认及回写授权
  - 04_Sources/模型工程/2026-09-15_Qwen3.5与DDP微调部署来源证据卡.md
supersedes:
  - 02_Projects/AI-Career-Transition/00_规划/AI职业转型整体学习方案.md 第1.6与1.12节2026-09-14前瞻安排，原文存该文第1.15节
  - 02_Projects/AI-Career-Transition/20_学习记录/P02A_VLM模型工程认知_学习记录.md 第1.12.3节恢复任务
scope: AI Career跨阶段实验工作包；从Phase 2-A接入，不等于P2A全部内容或正式生产项目立项。
risks:
  - 数据目录、完整标签、人员/session划分、预算和精确运行版本尚待确认。
  - 方案和环境截图不构成模型训练、部署或性能验证。
single_pass_recoverable: false
updated_at: 2026-10-01
---

# 1 Qwen3.5-9B驾驶员眼睛检测与状态分类实验方案

## 1.1 目标、决定与文档边界

实际路径、已有结果与当前步骤见[[02_Projects/AI-Career-Transition/30_实践记录/Qwen3.5-9B睁闭眼分类微调与部署实验记录]]；按维护规范1.7维护。已完成的推理与开发基线继续复用；后续按质量主线与工程学习线分别推进。

目标是形成可评测、可微调、可恢复、可部署和可回滚的模型服务。训练机制服务于工业微调与部署；不以完成大模型训练全课程作为服务部署的前置条件。

- 最终部署目标和蒸馏学生均为Qwen3.5-9B。
- 质量训练优先使用GT监督与困难样本/类别平衡的针对性SFT；稳定能力缺口仍存在时，评估更大教师。学生与部署模型始终保持9B。
- 主任务为整图驾驶员眼睛检测＋状态分类：生成框、画面左右字段及四类状态。检测直接作为基线和后续优化目标，不强制纯分类A/B；仅有具体归因需要时增加分类对照。条件性GT-crop诊断不改变整图部署输入。
- 双卡LoRA DDP保留为工程学习与扩展实验，完成情况独立记录；质量候选按自身评测结果进入部署验证。资源不可用时记录延期。
- 全参数训练、ZeRO/FSDP、TP/PP实作、在线logits蒸馏不作为当前门禁；蒸馏为条件分支。
- 本方案承载跨阶段全貌。P2A正文保存机制，阶段学习记录保存个人诊断，全局学习检查点保存整个学习方案的当前阶段与任务指向，连续主实验记录保存本实验内部路径、事件与证据。不创建五份current文档组。

### 1.1.1 Track A：模型质量主线

本轨回答：Qwen3.5-9B在驾驶舱真实整图输入下，能否满足双眼检测＋四类状态的业务要求，以及最小需要什么干预。起点是已有Qwen3.5-9B checkpoint，固定整图、任务指令与输出合同后建立zero-shot / limited few-shot基线。

```text
Qwen3.5-9B + 固定整图输入/输出合同
                    ↓
          zero-shot / limited few-shot baseline
                    ↓
                 错误归因
      ┌──────────┬───────────┬───────────┐
 prompt/schema  resolution   grounding   state/类别分布
      ↓             ↓            ↓             ↓
 模板/解码修正  整图像素预算调整  定位监督     GT/类别平衡SFT
      └──────────┴───────────┴───────────┘
                    ↓
                validation
          ┌─────────┴─────────┐
        达标                 未达标
          ↓                    ↓
     冻结最终候选        困难样本 / 扩大适配范围
          ↓             教师评估（有依据时）
       冻结测试                 ↓
          ↓                返回validation
       部署回归
```

模型容量问题需结合输入、标注、训练曲线及干预结果判断；每轮围绕一个主要错误组，选择能检验假设的最小干预。监督来源、训练目标和更新范围分别决定；LoRA是更新方式，SFT/KD是训练目标，QLoRA另涉及底座量化。

E0～E6与S01～S07保留为工作包编号，可采用E1→E5、E1→targeted E2→E5，或在SFT后仍有能力缺口时采用E1→E2→条件性E4→E5。达到质量要求的候选可进入E5；工程学习进度独立记录。候选在validation上冻结后才进入测试；测试反馈用于最终验收，后续改动返回开发/验证侧，并记录原测试集已被观察。

每轮记录错误组、干预假设、监督、目标、更新范围、预算、接受条件与复评决定。困难样本从训练/开发侧挖掘，先处理错标、不可判定输入和重复帧，并保留普通样本回归。冻结测试集隔离于训练、prompt搜索、hard-example mining、teacher筛选、threshold调整和量化校准。DPO按可靠偏好信号与比较收益另行论证；RL当前缺少任务证据，保留教学边界，暂不安排主实验。

### 1.1.2 Track B：模型工程学习线

本轨解释模型更新、资源消耗、扩展效率与服务行为。沿用原生PyTorch＋Transformers＋PEFT＋Accelerate训练栈，使用同一9B底座和可追溯产物。

```text
LoRA forward/backward生命周期 + label masking + optimizer state
    → gradient accumulation与checkpoint save/resume
    → 单卡 / 双卡DDP：归一化、no_sync、rank一致性与扩展成本
    → profiler归因
    → vLLM服务 / 量化对照 / multi-replica serving
    → failure / recovery / rollback
```

这条线用于组织学习内容，按需要选择实验。工程学习完成与否独立于质量候选的部署资格；例如，达标候选可先验证部署，DDP学习随后继续。真正用于该候选的训练正确性、引擎质量回归和服务安全恢复检查，仍需在对应工作包完成。

两轨共享底座、adapter/checkpoint、输入合同和评测工具，各自维护验收证据。工程练习产物成为部署候选时，同样接受Track A质量评测。历史范围与本次替代关系见1.16及实验附录O。

## 1.2 当前证据与待确认项

最新数据、环境和本地权重证据由[[02_Projects/AI-Career-Transition/30_实践记录/Qwen3.5-9B睁闭眼分类微调与部署实验记录]]第1.3～1.4节承载：用户确认整图同名JSON、四类、左右id及按批次隔离，要求跳过重复审计；用户报告smoke样本生成与Transformers/vLLM导入成功；本地权重header已检查为BF16为主，约17.98GiB。

模型已完成BF16加载和推理资源观测；4536视觉token的早期分类输入4614，检测prompt输入4732、单图生成上限256。格式归一化和坐标适配后已有40图开发基线，当前决定为GT监督SFT＋单卡LoRA准备，详见主实验记录1.4.5与附录M。训练完整更新/峰值、独立四类质量、正式split及质量/SLO门槛仍待验证或固定。

## 1.3 任务、数据与评测合同

### 1.3.1 输入输出

输入为方向已统一的整图与固定指令；目标为VLM生成式定位＋眼睛状态，不预设专用检测头或框回归损失。文件名保持现有稳定路径，正文标题与任务合同以本次定义为准。

**左右以最终输入图片坐标为准，不推断人物解剖学左右。** 图片原点位于左上角，x向右、y向下；在驾驶员双眼均有可靠位置时，框中心x较小者为image_left_eye，较大者为image_right_eye。不能按图像左/右半幅直接判定，也不能把原标注id=1/2固定绑定到画面左右。

输出字段结构：

```text
image_left_eye:  {bbox: [x_min, y_min, x_max, y_max], state: 四类之一}
image_right_eye: {bbox: [x_min, y_min, x_max, y_max], state: 四类之一}
```

bbox与state属于同一只眼。原始annotation保留pixel xyxy；model adapter将其转换为0～1000整数xyxy训练目标，模型生成采用同一尺度。该约定与[ms-swift Qwen3.5 grounding文档](https://swift.readthedocs.io/en/v4.1/BestPractices/Qwen3_5-Best-Practice.html)一致，本项目原生adapter显式执行转换。来源区补充见2026-10-01核对记录，既有坐标适配运行证据仍见实验附录M。

设W、H为进入任务合同的整图实际宽高：

```text
x_norm = round(x_pixel / W * 1000)
y_norm = round(y_pixel / H * 1000)
x_pixel = x_norm / 1000 * W
y_pixel = y_norm / 1000 * H
```

normalization仅存在于model adapter / model I/O，原始标注文件保持原值。读取时标记pixel或norm1000，adapter只转换一次。训练目标按统一round规则生成；评测反变换保留浮点精度，在原图pixel空间计算IoU。越界、退化或非法框按合同计失败，评测保留原始预测。

当前输入沿用原图和对应像素GT，方向处理保持既有数据约定。若改变orientation、整体resize或引入padding，记录原图→最终输入的几何变换，同步处理bbox，并以最终输入坐标定义左右；预测先还原到该输入pixel空间，再通过逆变换回到原图评分。processor内部整体缩放需要核对其geometry语义，防止输入坐标系偏移。评测记录原图/最终输入尺寸、变换、坐标尺度、round规则、原始预测及反变换后的框。

接受裸JSON或完整单个JSON围栏，剥离围栏后严格解析；保持既有不补框、不换左右的规则。原标注两点转xyxy后按中心x排序，同步保持状态对应；镜像增强须变换框并重新排序。

四类保持eye_open→open、eye_closed→closed、eye_occluded→occluded、eye_narrow→narrow。occluded表示因光线、头发等因素无法判定open/closed/narrow，可理解为这三类之外的other语义；字段仍保留occluded，不新增或重命名类别。它描述状态不可判定，不要求必须存在物体遮挡，也不自动表示眼睛不存在或无法定位。不能将其等同缺框、漏检或拒答。只有一眼、位置不可确定、中心x相同及完全遮挡时的输出/评分规则需结合现有标注约定明确；不能机械将单个框视为左眼，也不能把缺失强行改为closed或occluded。遮挡框表示推定眼睛区域还是可见部分，须在数据适配时明确。

不把待测样本文件名、GT框、标注或答案放入检测prompt；GT框用于监督和评分，oracle分支另行标识。主链保留整图，必要时整体缩放。单帧检测与状态判断不代表眨眼、疲劳或报警系统验证。

### 1.3.2 复用预处理与批次划分

用户说明原始整图/JSON已预处理，要求不重复全量审计；原ROI dataset不能直接复用。按批次划分训练/验证/测试，用户保证同一人员id不跨集合，本基准接受该范围，代理未独立审计。完整映射与样本清单在正式基准前固定；67/68/70/71/75训练、77验证、79测试目前为助手提案而非已执行清单。

直接读取同名同目录JSON的dataList[].coordinates与properties.eye_status；图片使用实际像素尺寸，忽略标注info宽高，不新增GT尺寸/框/ID检查，不自动旋转图片或修正GT。读取异常作为运行错误报告，不另设重复审计门禁。开发/验证/测试用途分离；已展示或用于调参的样例仅作开发证据，旧5-case和已观察的40图同样按其既有用途保留。冻结测试集不得用于prompt搜索、困难样本挖掘、教师筛选、阈值调整、训练或量化校准。

### 1.3.3 评测

评测直接针对检测＋状态任务，分别报告：

- 定位：按预先固定IoU阈值和一对一匹配规则统计precision/recall、漏检、多余框、越界/无效框及IoU分布。位置匹配不先依赖预测状态，避免状态错掩盖定位能力。
- 画面左右关联：空间匹配后统计字段是否对应正确眼睛；不能在评分时自动交换字段掩盖模型错误。
- 状态：报告成功匹配眼睛的四类macro-F1/balanced accuracy、各类precision/recall及混淆矩阵，同时给出匹配覆盖率。
- 微调复评补充：记录不以定位匹配为前提的对应侧四类混淆矩阵，解析失败单独计入总体失败；匹配后macro-F1需注明哪些类有样本，不能把仅open类的高分当作四类通过。定位同时记录框面积比和中心偏差，以区分框偏大与位置偏移。
- 端到端：位置、画面左右、状态同时正确的单眼比例及双眼完全正确率；全部GT眼睛进入分母，漏检不能被移除。解析失败、非法标签、重复预测单独报告并计入整体失败。

若没有可靠且一致的置信分数，不强行以mAP作为主指标；有对应分数合同后再补充。阈值、框尺度、缺失/遮挡规则和匹配协议在正式基准前冻结。按人员/session聚合分析，避免把相邻帧当独立证据；无需另建纯分类A/B任务即可分别诊断定位与状态错误。

正式调参前冻结质量下限、允许退化和延迟目标。没有业务SLO时只报告能力边界，不声称生产达标。性能以整图端到端p50/p95、图像请求吞吐、失败率和显存为主，TTFT为辅助；输出很短时不能只用输出token/s代表业务价值。

## 1.4 工作包E0：环境与兼容性（两轨共用）

复用已完成的加载、图文推理与依赖导入结果。下面是连续实验记录1.3.2已有环境报告的摘要，表示记录时配置；本次文档修订没有连接机器或新增运行验证。

| 项目 | 已记录配置/事实 |
|---|---|
| GPU | 4 × RTX PRO 5000 72GB Blackwell，每卡73415MiB；driver 580.126.20 |
| 当前使用范围 | 本实验只使用GPU0；GPU1～3可用性由实际运行前确认 |
| Python / PyTorch | Python 3.11；PyTorch 2.10.0＋cu128，CUDA runtime 12.8 |
| 训练依赖 | Transformers 5.2.0、PEFT 0.18.1、Accelerate 1.13.0 |
| 数据与Hub依赖 | Pillow 11.3.0、huggingface-hub 1.8.0 |
| 扩展 | causal-conv1d 1.6.1、flash-linear-attention 0.4.2；kernel实际执行按运行证据确认 |
| Serving | vLLM 0.17.1已可导入、CLI可用；模型服务、adapter及量化能力分别待验证 |
| SGLang | 未安装；当前沿用vLLM |
| 模型路径 | `/workspace/dms-eye-status-turbo/qwen_models/Qwen3.5-9B` |

实现角色分别为：

| 角色 | 选用方式 |
|---|---|
| 训练实现 | 原生PyTorch＋Transformers＋PEFT＋Accelerate |
| 正确性参考推理 | Transformers，使用固定processor与任务合同 |
| Reference implementation | ms-swift Qwen3.5 multimodal / grounding / LoRA，仅用于实现核对 |
| Serving benchmark | vLLM，完成同请求质量回归后测量服务表现 |

冻结镜像digest、模型/processor revision、依赖、代码hash、GPU UUID/驱动、随机种子和处理配置。确认Turbo空间与GPU拓扑；已有步骤直接复用，训练前补齐LoRA完整更新与资源测量。模型权重可加载仅覆盖加载容量，完整训练配置由实际更新峰值决定。

### 1.4.1 Reference implementation的使用范围

[ms-swift Qwen3.5文档](https://swift.readthedocs.io/en/v4.1/BestPractices/Qwen3_5-Best-Practice.html)及其官方仓库用于核对dataset representation、bbox normalization、chat template、multimodal processor、LoRA target scope和训练参数。文档示例属于参考配置，本项目按9B实际模块与既有合同检查差异。

运行依赖保持上述原生栈；ms-swift安装状态未声明，LLaMA-Factory不加入主实验依赖。若原生实现与reference behavior有差异，记录输入、模板、处理器、mask或目标模块的差异并定位。现有环境按已固定版本核查兼容性；版本变更作为独立配置记录。

参考入口及适用版本见[[04_Sources/模型工程/2026-09-15_Qwen3.5与DDP微调部署来源证据卡]]。当前backward、完整更新和服务能力仍为pending / not_verified。

## 1.5 工作包E1：整图基线与错误归因（Track A）

基线采用BF16、单卡TP=1、非思考模式、并发1，Transformers承担正确性参考推理。既有40图开发基线及坐标处理见1.2和实验记录1.4.5，后续补齐正式split与独立四类validation。当前已记录单样本检测输入4732、生成上限256；5600总预算及早期128预留保留为历史资源起点。扩展prompt、图文示例或像素预算时重新计算输入/输出规模。vLLM生产近似服务与并发对照归入E5；引擎约80%显存预算仍是待测候选。

先建立zero-shot与固定few-shot基线，比较简单指令、类别规则及少量文字示例；图文few-shot按需要另测并记录额外视觉token成本。示例来自训练/开发侧，不包含待测样本答案。限定调试预算，不持续搜索prompt。普通解码与schema约束解码分别记账，不把约束解码收益当微调收益。

固定整图处理合同后，补齐所需质量基线及参考推理的单请求成本，保持图像集合、像素预算、输出规则和版本一致。记录输入/输出token数、延迟测量范围及失败率；超预算样本显式记录和处理。多并发服务技术内容移入E5，质量归因优先保持单卡、单请求配置。

验收：取得质量、主要错误组及输入成本依据，明确最小干预。候选达标可直接进入E5；需要训练则进入targeted E2，独立执行所用训练配置的correctness gate。

### 1.5.1 错误归因与优先策略

| 类型 | 优先排查/非训练干预 | 证据支持后的训练候选 |
|---|---|---|
| instruction / format following | 模板、停止条件、输出长度、schema | SFT |
| domain adaptation | 类别定义、标注一致性、few-shot | 领域SFT |
| 基础感知/识别不足 | 输入细节、视觉编码、教师差异 | 视觉适配、targeted SFT/KD |
| grounding / localization | 对象位置、左右语义、目标尺度 | 定位相关监督或架构适配 |
| 候选排序/偏好错误 | 正确候选是否存在、评分与解码 | 难负例/ranking loss，必要时DPO |
| reasoning / decision | 核对任务规则与视觉证据 | targeted SFT；教师优势经验证后考虑KD |
| input information bottleneck | 分辨率、缩放、token预算、采集信息 | 优先修输入路径 |
| model capacity bottleneck | 排除数据、优化失败、监督不足 | 扩大适配范围或架构/容量调整 |

策略是优先候选而非自动映射。普通样本饱和、长尾差时考虑hard-example mining与targeted SFT，保留普通样本回归。loss高或验证差不能独立证明容量不足。四分类出现错类不自动支持DPO，应先与监督损失、重采样及KD比较。

RL教学边界保留：采用奖励优化需具备可靠reward、值得探索的行为空间与可承担成本。当前单帧任务缺少引入证据，RL不安排进入主实验。

### 1.5.2 视觉瓶颈归因与conditional oracle diagnostic

优先使用真实整图完成归因：固定其他条件，比较max_pixels / visual-token预算或整体resize策略；结合bbox IoU、框面积比、中心偏差、grounding error distribution及matched-eye state metrics分析。输入预算变化同时记录视觉token和延迟，判断质量收益是否可部署。

GT-crop降级为conditional oracle diagnostic。只有以上可部署变量和指标仍无法区分目标尺度/resolution、localization与state recognition问题时，才在训练集或验证集侧选少量困难样本执行。GT只提供裁剪位置，类别答案保持隐藏。

Oracle诊断独立记录样本、裁剪方式、问题和结果，仅用于提出下一轮实验假设。它不进入测试集、正式benchmark或部署候选，也不与整图指标混合报告；正式服务输入始终是驾驶舱原始整图。裁剪会同时改变尺度、上下文和背景，结果应由后续整图单变量实验检验。

原图失败而oracle成功，可以提出空间细节、背景或定位相关假设；高质量输入仍失败时继续检查任务定义、标注与识别能力。保留这一诊断解释，不建立“GT crop→classifier”的部署路线。

## 1.6 工作包E2：targeted SFT与单卡正确性（Track A / B）

### 1.6.1 第一轮训练问题与更新范围

第一轮回答：在已确定的baseline错误组上，最小语言侧LoRA能否改善整图定位与四类状态指标？质量主实验优先使用单卡，依据GT开展targeted SFT，保留普通样本回归；困难样本与类别平衡采样按训练/开发侧分布安排。

首轮冻结vision encoder与连接模块，只更新经过检查的language-side LoRA。候选r=16、alpha=32、lr≈1e-4用于smoke与初始比较，最优配置由validation决定。

语言侧候选不足时，先复查整图resolution、视觉token与localization证据，再决定是否扩大范围：跨模态映射问题评估projector / connector，视觉域问题评估vision-side adaptation，语言侧适配不足评估rank或target scope。每轮选择有证据的模块，无需逐项走完；Full FT保留为最后候选。QLoRA按容量和成本另行比较。

正式训练须有E1错误组、干预假设、独立validation与可接受预算。label masking、更新正确性、可运行容量及保存重载属于所用训练配置的correctness gate；生命周期完整对照和DDP学习的验收单独归Track B。

### 1.6.2 初始配置与正确性

| 项目 | 试运行起点 |
|---|---|
| 底座 | Qwen3.5-9B BF16，冻结 |
| 视觉编码器 | 首轮冻结，仍处理整图 |
| LoRA | r=16、alpha=32、dropout=0 |
| 目标模块 | 检查语言主干线性投影后冻结显式白名单；不复制其他架构列表 |
| optimizer | AdamW，仅adapter，lr=1e-4、betas=(0.9,0.999)、weight_decay=0.01，固定实现路径 |
| batch | 每卡micro batch=1、单卡累积8 |
| 输入 | 固定整图视觉预算与norm1000答案；总序列上限依据既有processor测量和代表性输入检查冻结 |
| 更新预算 | smoke 20 optimizer updates；首轮200 updates保留为默认工程上限，正式质量预算同时按样本/token暴露量记录，详见1.6.2.1 |
| 其他 | 训练use_cache=False；先不量化底座，不开compile；checkpointing容量需要时启用并记录 |

打印可训练参数名/数/dtype、optimizer实际持有参数；检查loss/梯度有限、adapter变化和冻结参数一致。LoRA初始化可能使个别矩阵首步梯度为零，应结合初始化与后续更新解释。

#### 1.6.2.1 训练预算与checkpoint选择

每次训练同时记录number of samples、optimizer updates、effective global batch size、计划/实际epochs、seen samples及effective supervised target tokens。samples指训练清单样本数；seen samples包含重采样和重复读取，另记其分布。有效target tokens按实际参与监督的token累计。

smoke预算为20次optimizer更新。正式short run可先以0.25 / 0.5 epoch作候选，根据validation curve决定是否继续到1 / 2 epoch；这些是预算提案，实际次数按数据规模、有效batch与采样策略换算。首轮200 updates工程上限仍保留，先记录它实际覆盖的epoch和暴露量。达到上限时复评并决定是否给下一轮预算；validation饱和、退化或明显过拟合时可提前停止。

class-balanced或重复采样时，另记sampler长度与epoch定义；以实际seen samples/token说明训练暴露量。所有续训预算与停止条件在validation侧决定，checkpoint只按validation选择。

#### 1.6.2.2 Label masking：正式训练correctness gate

用真实batch显式检查input_ids、labels、attention-related multimodal inputs、image tokens/placeholders、assistant target及shift后的effective supervised token count。

| 位置 | labels合同 |
|---|---|
| System / user prompt及非目标模板 | -100 |
| Image placeholder / 非目标图像位置 | -100，视觉输入仍通过对应attention/多模态字段参与前向 |
| Padding | -100 |
| Assistant bbox/state JSON | 保留目标token ID，参与监督 |
| EOS / end marker | 依固定模板合同监督；记录实际ID与mask边界 |

至少打印一个真实batch的decoded input、decoded supervised target和effective target token number，并核对image位置数量、pixel_values / grid及实际attention相关字段与模型输入一致。assistant监督只覆盖规定答案与结束标记；causal shift按当前模型/训练实现核对，防止重复shift、答案截断或空监督。该检查直接在原生collator/训练链路完成，具体字段和LoRA白名单以安装版本及实际模型核对结果为准。

训练配置通过此gate后才开展质量short run。当前检查与完整更新继续保持pending / not_verified。

### 1.6.3 生命周期与性能

独立诊断运行：加载→forward→backward→首次optimizer.step→zero_grad。阶段边界同步，记录allocated/reserved与阶段峰值、实际梯度和optimizer state字节数。冻结底座不消除activation与反向链；backward不保证显存单调下降。

单卡对照S1=1×8、S2=2×4，固定8个样本/更新、样本集合、初始化、图像形状/预算与优化器。变长回答按有效目标token总数归一化。先检查更新一致性，再比较首次峰值和稳定窗口。

性能窗口默认预热10次、连续50次完整更新，过短或未稳定时统一调整两组窗口。边界同步，预热结束/梯度清除后重置峰值；窗口内不.item打印、不存checkpoint、不empty_cache、不启profiler。三次独立重复，记录完整step、图像样本及有效目标token吞吐、峰值、波动。GPU驻留预处理输入与包含解码/处理/搬运的端到端测量分别命名。

Profiler独立抓取少量更新，标注forward/backward/optimizer和数据路径，解释一项具体瓶颈；一次只改一个因素。

### 1.6.4 恢复与验收

完整更新边界保存adapter、optimizer/scheduler、RNG、步数、数据位置及版本。恢复后与不中断分支继续相同三次更新，比较loss、梯度或adapter更新误差。首轮质量无提升也可形成工程证据，但不能将该产物自动设为上线版本。

Track A验收：训练correctness gate通过，验证集目标指标改善且普通样本回归可接受，随后可进入E5。Track B另验收更新/恢复、生命周期与累积对照、一次独立故障定位；其学习任务继续按证据推进。扩大视觉侧适配范围作为新的单变量候选记录。

## 1.7 工作包E3：双卡LoRA DDP（Track B：engineering learning / scaling experiment）

本工作包回答：相同训练目标下，双卡是否保持更新语义一致，获得的加速是否值得GPU成本？它独立于model-quality gate。质量主实验先用单卡减少变量，72GB单卡LoRA可行性仍由首次完整更新测量确认。

DDP进入正式训练的触发条件是单卡吞吐过低、总训练时间不可接受，或目标global batch确需扩大；真实多GPU scaling验证可单独作为工程学习理由。普通DDP每卡复制完整底座与本地训练状态，单卡OOM应先定位activation/状态并采用降显存或分片方案，容量满足后再评估DDP。四张可见GPU不构成使用四卡的理由。


每GPU一个进程，torchrun+NCCL；先注入LoRA再包装DDP。每卡完整冻结底座与adapter，分配不同样本，两个rank更新轮数一致。明确sampler补齐/丢弃行为；正确性实验使用固定全局样本清单，避免重复样本混入。

| 配置 | GPU数 | 每卡micro batch | 累积 | 全局样本/更新 |
|---|---:|---:|---:|---:|
| 单卡 | 1 | 1 | 8 | 8 |
| 双卡 | 2 | 1 | 4 | 8 |

设W为rank数，N为本次更新所有rank/累积轮的有效目标token总数，S(r,k)为本地该轮token loss总和。在默认DDP梯度平均且无额外框架缩放时，各轮backward使用W×S(r,k)/N；不能再除累积次数。N先由本次样本标签计数并跨rank求和，具体实现与框架自动缩放核对。非最后轮no_sync覆盖forward/backward。

先比较前几次全局loss、同步后梯度、adapter更新及rank间一致性，记录绝对/相对误差；BF16不要求逐位一致。排查样本、mask、归一化、padding、随机性和数值路径；容差必须在检查参考误差后明确，不用宽松阈值掩盖错误。

性能窗口rank对齐、GPU同步，采用最慢rank完成时间；报告单卡/双卡耗时、加速比T1/T2、效率(T1/T2)/2、GPU·秒T1与2T2、通信和等待。增加一组no_sync开关对照，其他条件不变。结果不要求两倍加速；四卡为可选扩展。

保存共同更新边界与各rank RNG/数据位置；演练一个rank中断，确认失败退出、超时与恢复，无样本跳过或重复更新。资源临时不可用时延期并记录，不能用单GPU多进程冒充跨GPU性能。

## 1.8 工作包E4：条件性教师监督与KD（Track A条件分支）

正式质量优化优先GT supervised SFT，再按错误组考虑hard-example / class-balanced targeted SFT。若9B仍存在稳定能力缺口，在相同整图输入合同、相同训练/开发/验证侧困难样本上评估larger teacher；教师在关键指标上明显优于当前9B，且监督可获取、许可与预算明确时，才打开KD分支。优势标准在验证前固定，并结合普通样本回归判断。

优先评估response / pseudo-label KD；有可验证软信号与对齐方案时再考虑probability / ranking KD；feature / logit KD只在明确迁移假设下采用。下节保留各粒度教学内容，这一优先级服务于当前任务，不构成固定SFT→KD流水线。候选已达标或教师缺少优势时记录有依据的跳过决定，直接继续E5。9B保持学生和部署目标。

### 1.8.1 蒸馏信号粒度

| 类型 | 适用条件与限制 |
|---|---|
| Response / sequence-level | 教师完整回答用于SFT；跨架构容易，短JSON的额外结构有限 |
| Pseudo-label | 教师补充训练侧未标注样本；区分数据增量、重标与教师信号收益 |
| Logit / probability | 可获得可靠软分布并对齐输出空间；异tokenizer不能直接逐token比较，可优先四类概率 |
| Candidate score / ranking | 存在共同候选集合，教师排序明显更好 |
| Hidden-state / feature / attention / relational | 有明确表征迁移假设，可处理层、维度、空间位置或关系对齐 |

这些类别可重叠，不是执行阶梯。架构差异大时优先response、可对齐概率或ranking，再考虑feature alignment；不默认hidden-state最优。离线答案/伪标签是低成本候选而非唯一允许路径，在线/feature KD不设首轮门禁。

### 1.8.2 GT与教师监督

```text
L_total = λ_gt L_gt + λ_kd L_kd + λ_aux L_aux
```

GT提供correctness anchor，Teacher提供软结构或行为示范；权重需考虑损失尺度与有效样本mask。硬伪标签不等于完整dark knowledge。教师不默认覆盖GT，冲突需判断教师错误、标注噪声和定义差异。

confidence filtering需在验证侧校准，不能把教师自报置信度当正确率；agreement checking可结合GT、规则、多教师或重复预测，仍需注意共同偏差。用GT校准/审核教师信号，按类别与困难组抽检，避免过滤掉全部长尾；冻结测试答案不参与筛选。

### 1.8.3 KD与偏好优化

KD逼近教师输出分布、行为或表征；DPO调整chosen与rejected的相对偏好。可以组合Teacher→response→SFT、Teacher→logits→KD、Teacher→preference pairs→DPO；后者是偏好信号迁移，不等于logit KD。是否引入取决于候选质量、偏好可靠性及与简单监督方案相比的增益。

### 1.8.4 复评与成本

固定输入集合与更新预算比较无教师/有教师候选，额外数据与教师计算独立记账。教师生成可按预算多卡独立分流，学生训练优先复用已验证单卡配置，需扩展时采用已验证DDP；离线logits也需评估存储和对齐成本。复评整体、困难组、普通样本回归及服务成本，接受/拒绝均记录；未达标回到错误归因，线上不依赖教师。

## 1.9 工作包E5：9B部署回归（Track A）与量化对照（Track B / 按需候选）

验证集选checkpoint，最终候选才进入冻结测试集。兼容时加载adapter，否则验证合并产物；保存底座/adapter身份、合并精度与脚本，检查合并前后任务指标和输出差异。底座、adapter和合并产物均可追溯。

Transformers提供correctness reference inference，vLLM提供production-like serving benchmark。使用相同请求清单和模型产物，核对processor、resize、orientation、chat template、bbox合同、non-thinking mode、stop token、max output tokens、schema、LoRA loading及merged model behavior。直接adapter与合并产物分别确认支持与身份；本机vLLM导入成功仅是已有环境事实，其9B adapter/量化能力仍待验证。

跨引擎比较bbox validity、IoU、matched-eye state metrics、end-to-end metric和JSON parse success，并记录允许差异。生成结果可以不同，明显任务回归须得到可复核解释或修复。先在开发/验证请求上完成部署配置选择，最终冻结配置再做测试与部署回归；阈值、prompt和产物选择持续隔离于冻结测试。

服务性能依次评估并发1/4/8，保持图像集合、像素预算、输出规则、模型和processor版本一致。冷启动与预热后的稳定服务分别记录；先短测筛选，候选窗口延长并重复3次，报告请求数、波动及实际输入/输出token数。

先验证BF16质量和服务链路，再选择当前架构/GPU/引擎明确支持的量化路径。FP8是优先核验的候选，支持性及收益按固定版本与运行证据确认；不适用时记录原因，再选择受支持路径。官方recipe的latest信息只作参考，不视为vLLM 0.17.1本机支持证明。

```text
BF16质量基线 → supported quantization
    → same-request质量回归 → latency / throughput / VRAM比较
```

量化对照保持processor、输入几何、model adapter与decode合同固定，仅改变量化主变量。校准数据来自训练侧，量化方式与阈值选择使用validation。QLoRA和部署量化分别立项；同一对照不同时改变底座量化、processor与adapter。BF16候选可按自身结果部署，量化学习仍可继续。

比较同请求负载的质量、图像端到端p50/p95、吞吐、失败率、显存；再比较相同显存预算的容量。量化不达质量门槛则拒绝，保留BF16。

## 1.10 工作包E6：多副本服务与故障演练（Track B / 按业务扩容需求）

每卡一个完整服务副本TP=1，前置请求路由；与训练DDP区分，不同步梯度。单/双副本先保持相同总负载，再提高到达速率，检查排队和SLO内吞吐；混合图像处理成本不同的请求观察负载不均。

测试健康检查、超时、取消、异常输入、限流、单副本中断/摘除、重启加入及回滚。记录整体与每副本吞吐、尾延迟、排队、错误、显存和恢复耗时；确认客户端不是瓶颈。不承诺中断流式响应无缝续接。

候选配置做持续负载测试，冻结运行时长与请求分布并观察漂移。交付启动配置、模型版本、日志指标、长度/并发限制、回归集和回滚至原始9B BF16的方法。称为生产流程演练；正式生产SLO仍需真实业务验证。

## 1.11 工件、停止条件与双轨验收

Turbo下拟设manifests/configs/data/scripts/runs/adapters/checkpoints/profiles/reports目录；实际根路径待确认。每次记录实验问题、所属轨道、改变变量、预测、实际结果、固定条件和结论边界。每个benchmark注明输入合同、数据split/清单、模型版本、processor及decode参数。

遇到NaN、空监督、冻结参数误更新、DDP不一致、数据泄漏、版本身份变化时停止后续比较，先修复。OOM保存原配置与日志；不得改参数后沿用旧实验名。预算先由smoke test测得的step成本估算再启动正式运行；不默认四张卡同时常驻任务。

Track A按候选实际使用的路径验收；Track B按独立实验记录学习完成度。待执行内容继续标记pending / not_verified；以下摘要复用已有记录，不新增运行结论。

| 工作包 | 轨道与验收问题 | 已有事实 / 待验证范围 |
|---|---|---|
| E0 | 共用：环境、模型、输入与训练实现是否兼容？ | 加载、processor、图文生成和依赖导入已有报告；正式split、完整更新兼容仍pending |
| E1 | A：整图定位/左右/四类状态及端到端指标是否达标？ | 40图开发基线已有报告；独立四类质量与业务门槛not_verified |
| E2 | A：targeted SFT是否改善错误组？B：更新/恢复/资源机制是否正确？ | GT监督语言LoRA准备；masking、完整更新、收益、恢复及对照not_verified |
| E3 | B：单双卡一致性、效率/GPU·秒、故障恢复 | not_verified；不作为A的部署前置 |
| E4 | A条件分支：教师有优势且KD有收益吗？ | conditional_pending；满足触发条件再评估 |
| E5 | A：服务产物质量回归；B/按需候选：量化收益 | not_verified；BF16、adapter/合并、引擎、量化分别确认 |
| E6 | B/业务扩容：多副本吞吐、故障与回滚 | not_verified；扩容需求决定候选是否采用 |

## 1.12 当前恢复入口与来源

全局学习检查点负责恢复任务指向；本实验的实际步骤与结果继续由[[02_Projects/AI-Career-Transition/30_实践记录/Qwen3.5-9B睁闭眼分类微调与部署实验记录]]承载。当前复用记录1.4.5的40图开发基线与S03准备决定：固定split清单与缺失/遮挡细则，按1.3保持pixel GT→norm1000监督，按1.6完成label masking、实际LoRA白名单、完整更新及保存重载检查，再开展单卡质量short run。

S01未完成的训练资源验证与S02独立四类validation继续补齐；已完成推理、坐标适配和数据处理结果直接复用。当前训练尚未执行，DDP、KD、量化及多副本服务仍按所属轨道或触发条件推进。技术方案变化与旧恢复文字的接替见1.16及附录O，不新增重复全量审计。

机制阅读：[[02_Projects/AI-Career-Transition/10_学习文档/P02A-01_VLM模型工程认知_学习文档]]第2、3、11章；蒸馏、量化和服务主题按需要补教学骨架。个人诊断见[[02_Projects/AI-Career-Transition/20_学习记录/P02A_VLM模型工程认知_学习记录]]第1.13节。滚动位置见[[02_Projects/AI-Career-Transition/20_学习记录/当前阶段学习检查点]]；实现参考见[[04_Sources/模型工程/2026-09-15_Qwen3.5与DDP微调部署来源证据卡]]。方案配置与本机已验证事实按1.2、E0和连续记录分开查阅。

## 1.13 修订与历史追溯

2026-10-01明确质量主线与工程学习双轨，补全坐标、训练预算、masking及部署对照；依据见实验附录O。此前旧方案与条款统一移至[[90_Archive/02_Projects/AI-Career-Transition/Qwen3.5-9B实验旧方案与条款归档]]，当前正文只承载有效设计。已有实验结果与未验证状态继续由连续实验记录及证据附录承载。
