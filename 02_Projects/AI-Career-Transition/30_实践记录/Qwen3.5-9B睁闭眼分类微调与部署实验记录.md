---
type: project_continuous_experiment_record
status: active
project: AI-Career-Transition
record_role: primary_experiment_history
current_step: S01 - 模型与资源方案选型验证
step_status: in_progress
summary: 以9B整图四分类串起资源选择、微调与部署；已建立理论预算，当前等待GPU显存实测。
sources:
  - 02_Projects/AI-Career-Transition/30_实践记录/Qwen3.5-9B睁闭眼分类微调与部署实验附录.md
  - 02_Projects/AI-Career-Transition/00_规划/Qwen3.5-9B睁闭眼分类微调与部署实验方案.md
  - 02_Projects/AI-Career-Transition/30_实践记录/assets/Qwen3.5-9B/2026-09-16_model_header_evidence.json
scope: 从模型资源选择到质量基线、LoRA、DDP、条件性更大教师、量化及多副本服务的连续工程路径与结果分析。
risks:
  - 依赖导入和权重文件检查不能替代GPU推理、训练或服务验证。
  - 权重头部检查不校验全部payload，也不能代替模型revision和完整文件hash。
single_pass_recoverable: false
updated_at: 2026-09-16
---

# 1 Qwen3.5-9B睁闭眼分类微调与部署实验记录

## 1.1 实验目标与阅读方式

本实验以Qwen3.5-9B为学生和部署目标，围绕整图睁闭眼四分类，逐步完成资源选型、质量基线、微调、分布式训练和部署验证。每一步先明确问题和理论预期，再用实测决定是否采用或调整方案。

恢复整体学习时，先读全局《当前阶段学习检查点》，确认当前阶段与任务；指向本实验时，从当前步骤继续。本记录说明如何推进实验及如何理解结果。

## 1.2 当前进度

| 步骤 | 工程决策 | 状态 |
|---|---|---|
| S01 | 9B BF16整图推理/LoRA是否适合现有GPU及输入预算 | in_progress；理论已建，远端实测pending |
| S02 | 原始四分类质量、错误分组与是否值得适配 | not_started |
| S03 | 单卡LoRA是否正确且有收益，能否恢复 | not_started |
| S04 | 双卡DDP是否保持目标一致，加速是否值得成本 | not_started |
| S05 | 9B不足时，更大教师是否能改善学生 | conditional_pending |
| S06 | 9B产物/精度组合是否满足质量、延迟和容量 | not_started |
| S07 | 双卡多副本的扩容、故障及回滚路径 | not_started |

学生和最终部署目标为Qwen3.5-9B。仅当其质量不足时引入更大教师。当前尚未完成模型GPU推理、反向传播、质量评分或显存峰值测量。

## 1.3 数据与环境约定

### 1.3.1 数据

- 云端根目录：`/workspace/dms-eye-status-turbo/extract_data`。数据已预处理，一图一个同名JSON；原ROI dataset不能直接复用，必须读取整图。
- `id=1`为人物真实左眼，即画面右眼；`id=2`对应画面左眼，按id读取而非数组顺序。
- 映射：`eye_open→open`、`eye_closed→closed`、`eye_occluded→occluded`、`eye_narrow→narrow`。四类均保留；`occluded`不是拒答，不默认添加unknown。
- 输出：`{"image_left_eye":"open","image_right_eye":"open"}`。图像和固定指令进入模型，expected、文件名和原标注只供数据组织/评分，不进入prompt；不裁剪、不输出框。
- 本基准按批次划分train/val/test，采用同一人员ID不跨集合的数据约定。直接使用已有预处理结果，读取时对缺文件、未知标签报错。
- 拟采用的批次划分为：67/68/70/71/75训练，77验证，79测试；具体划分待确认并生成全量split清单。下一次生成清单时固定该映射或记录修改。

### 1.3.2 环境

| 项目 | 当前配置与待确认项 |
|---|---|
| GPU | 4张RTX PRO 5000 72GB Blackwell，每卡73415MiB；driver 580.126.20 |
| 占用 | 上次检查每卡空闲22543MiB；占位脚本可关闭，释放后需重新测量 |
| PyTorch | 2.10.0+cu128，runtime CUDA12.8、CUDA available=True |
| Python | python3.11 |
| 训练依赖 | transformers5.2.0、huggingface-hub1.8.0、accelerate1.13.0、pillow11.3.0、peft0.18.1 |
| 扩展 | causal-conv1d1.6.1、flash-linear-attention0.4.2；包存在不代表kernel已执行 |
| 图文接口 | Qwen3.5多模态接口导入通过；GPU执行待验证 |
| 推理引擎 | vLLM0.17.1导入exit0、CLI可用；SGLang未安装，无需同时安装 |
| 离线约束 | 云桌面无网络；Turbo约6809.5GiB空闲 |
| 模型 | /workspace/dms-eye-status-turbo/qwen_models/Qwen3.5-9B |


## 1.4 S01：模型与资源方案选型验证

### 1.4.1 目标与决定

判断单张约71.7GiB GPU是否能以有余量的配置完成9B BF16整图推理和LoRA，并保留眼部有效细节。通过条件不是仅“不OOM”：还需实际输入预算、推理/训练完整窗口峰值、稳定开销与方案边界。

### 1.4.2 理论预测及前提

#### 1.4.2.1 权重存储量

BF16为主、少量FP32的非量化checkpoint，权重header统计结果如下：

| dtype | tensor数 | 元素数 | tensor字节数 |
|---|---:|---:|---:|
| BF16 | 727 | 9,653,100,528 | 19,306,201,056 |
| FP32 | 48 | 3,840 | 15,360 |
| 合计 | 775 | 9,653,104,368 | 19,306,216,416，约17.9803GiB |

称分组约语言/其他16.68GiB、视觉0.85GiB、MTP0.45GiB；不是GPU常驻分配实测。框架是否加载MTP、dtype转换和权重重排仍需实测。

#### 1.4.2.2 推理与LoRA显存预算框架

```text
推理峰值 = 实际加载权重 + 视觉/prefill中间结果
         + full-attention KV与线性attention状态 + logits/workspace + runtime
LoRA峰值 = 冻结底座 + adapter参数/梯度/Adam状态
         + backward保存的activation + 视觉计算与logits/loss临时空间 + runtime
```

不要把reserved与allocated相加。

#### 1.4.2.3 单图视觉token数

单张静态图像先按patch划分，再在空间上合并：

```text
N_patch ≈ (H / p) × (W / p)
N_visual ≈ N_patch / m² = H × W / (p² × m²)
```

H、W是processor处理后的图像高和宽，p是patch边长，m是每个空间方向的合并数。真实token数由processor输出的grid及合并规则确定。

本地配置p=16、m=2，相当于每个合并后的视觉token覆盖约32×32像素。不同尺寸的估算结果如下：

| 处理后尺寸（宽×高） | 视觉token近似值 |
|---|---:|
| 1024×768 | 768 |
| 1536×1152 | 1728 |
| 1920×1200 | 2250 |
| 2592×1944（假设不缩放） | 约4921，仍需尺寸对齐 |

上下文还需容纳文本、特殊token和生成内容，因此4096上下文不能直接覆盖所有原图。原始整图可整体缩放，但不裁剪；像素预算还需保留眼部可判别性。

#### 1.4.2.4 Full-attention KV缓存

传统KV缓存按层数、序列长度及每个KV头的大小计算：

```text
M_KV = L_full × 2 × B × S × n_kv × d_head × b_kv
```

L_full是full-attention层数；系数2代表K和V；B是batch size；S是已缓存序列长度；n_kv是KV头数；d_head是每头维度；b_kv是每个缓存元素的字节数。

本模型32层中有8层full attention、24层linear attention。采用BF16缓存（每元素2 bytes），B=1、S=4096、n_kv=4、d_head=256时，传统KV缓存约为**128 MiB**。

该值仅覆盖full-attention的传统KV，不含线性attention状态、视觉计算开销或推理引擎预分配缓存池。

#### 1.4.2.5 LoRA参数与训练状态

对于一个输入维度为d_in、输出维度为d_out的线性层，秩为r的LoRA使用两个低秩矩阵。对所有目标层求和：

```text
N_LoRA = Σ[r × (d_in + d_out)]
M_LoRA_states = N_LoRA × (b_param + b_grad + b_Adam_m + b_Adam_v)
```

b_param、b_grad、b_Adam_m、b_Adam_v分别是adapter参数、梯度及Adam一阶、二阶状态每个元素的字节数。此式只统计这四项，不包含activation或额外副本。

假设r=16，覆盖主语言层二维投影，排除视觉、MTP、embedding与输出头，候选adapter参数量约为**43,278,336**。若参数、梯度及两份Adam状态均为FP32，每个可训练参数共需16 bytes，合计约**0.6449 GiB**。

冻结视觉/底座不意味着全部训练activation消失；LoRA减少可训练状态，单个micro-batch的activation仍可能主导显存。

#### 1.4.2.6 完整logits张量

若模型为每个序列位置输出整个词表的logits，其张量大小为：

```text
M_logits = B × S × V × b_logits
```

B是batch size，S是参与输出的序列长度，V是词表大小，b_logits是每个logit的字节数。

B=1、S=4096、V=248320时，完整logits使用BF16约占**1.8945 GiB**，使用FP32约占**3.7891 GiB**。

这里计算的是完整logits张量；loss可能产生额外临时副本，也可能采用节省空间的实现。短JSON监督不保证只计算回答位置的logits。各项能否同时驻留、何时达到峰值仍需实测；vLLM的预分配量不能当作单请求必要内存。

### 1.4.3 预测与实测对照

| 项目 | 理论/静态证据 | GPU实测 | 决定 |
|---|---|---|---|
| 权重存储 | 17.9803GiB，BF16为主 | 未测实际加载常驻量 | 保留BF16候选，不默认转FP32/QLoRA |
| 输入规模 | 原图可能产生超过4096的视觉token | processor未运行 | 先固定整图预算，不静默截断 |
| 推理容量 | 权重以外仍有状态/activation/workspace | pending | 不声明可用峰值或服务容量 |
| LoRA容量 | 假设adapter训练状态约0.645GiB，activation未知 | pending | micro batch1起步，checkpointing由测量决定 |
| 云端余量 | 上次检查仅22543MiB空闲 | 释放后未测 | 先关闭目标卡占位脚本，再进行容量验证 |

### 1.4.4 当前决定与操作步骤

9B BF16整图推理与LoRA仍是待验证方案。接下来按以下顺序确认容量：

1. 将模型上传到Turbo，固定容器内模型路径；关闭目标GPU的占位脚本并记录释放后的可用显存。
2. 对smoke样本运行processor，记录处理后尺寸、grid、视觉token和总长度，据此固定整图输入预算，避免静默截断。
3. 测量单图推理的加载常驻显存和完整推理峰值，记录对应输入和生成长度。
4. 从micro-batch=1开始，测量LoRA首次完整更新（forward、backward、optimizer.step、清梯度）的峰值；再测预热后的稳定窗口，分别记录allocated、reserved及设备占用。
5. 如余量不足，每次只改变checkpointing或像素预算中的一个变量。调整像素预算时同时检查眼部信息是否仍可辨认。
6. 填写预测与实测对照，解释差异，决定采用、调整或拒绝该配置；确认资源方案后进入S02原始质量基线。

正式基准前冻结全量数据划分清单。当前尚未产生GPU实测结果，因此不预填峰值、吞吐或可用容量。

## 1.5 参考与附录

完整路线见[[02_Projects/AI-Career-Transition/00_规划/Qwen3.5-9B睁闭眼分类微调与部署实验方案]]。执行来源、工件和原正文修订历史已迁至[[02_Projects/AI-Career-Transition/30_实践记录/Qwen3.5-9B睁闭眼分类微调与部署实验附录]]，需要追溯时查阅。
