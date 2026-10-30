---
type: project_analysis
status: draft
created_at: 2026-10-30
updated_at: 2026-10-30
scope: Qwen3.5_VLM_Basic仓库的首轮静态分析；不代表运行复现或性能验收。
---

# 1 Qwen3.5_VLM_Basic仓库分析

本记录保存2026-10-30同一对话中的仓库读取结果。分析对象为 `/home/jichao/Qwen3.5_VLM_Basic`；当时未发现 `.git`，未保存完整文件快照，因此不能把本文视为可精确恢复的代码版本。以下路径均相对此仓库，后续修改后需要重新核对。

## 1.1 仓库解决什么问题

仓库将Qwen3.5视觉语言模型经过权重优化、静态图导出和QAIRT编译，交由Genie在Qualcomm HTP上运行。Stage 1～3提供0.8B、2B、4B、9B配置，Stage 4只提供0.8B与4B现成配置。源码还包含其他模型和音频相关工具，但本次分析的主入口是无音频的VL流程。

| 阶段 | 主要入口 | 输入与输出 |
|---|---|---|
| Stage 1 | `stage1_ptq/main.py`、对应LLaVA YAML | 基础checkpoint与校准数据 → AdaScale优化后的checkpoint |
| Stage 2 decoder | `stage2_export/pipeline_ar128_ar1.sh`、`hf_qwen3_5_vl.py` | checkpoint → prefill/decode ONNX及encodings |
| Stage 2 vision | `stage2_export/run_vision_vl.sh`、`hf_qwen3_5_vl_vision.py` | checkpoint及图像校准数据 → ViT ONNX及encodings |
| Stage 3 | `compile_arn_ar1_vl.sh`、`compile_arn_vl.sh`、`compile_vision_vl.sh` | 图及量化参数 → HTP context binaries等产物 |
| Stage 4 | `stage4_run/genie_app_pipeline_llm`、`genie_app_pipeline_vl` | 模型产物与运行配置 → 文本或视觉语言推理 |

Stage 2的0.8B配置默认W8，其他三种规模默认W4，激活默认16 bit。实际各层可能有混合精度例外，不能只凭整体标签判断所有张量精度。Stage 3默认目标为 `dsp_arch:v81;soc_model:72`，默认上下文长度2048；这不是任意高通设备的通用配置。

## 1.2 核心适配为什么复杂

`stage2_export/genai_lib/llm/dev/model_adaptation/qwen3_5/adaptation.py` 实现attention、GatedDeltaNet、缓存及静态图相关适配。该模型不只有普通KV cache，还涉及卷积状态和recurrent state，所以跨调用状态的形状与数值解释需要共同维护。

prefill与decode的图不同。`llm_utils/prepared_graph_encoding_utils.py` 从prepared Python图的数据流发现状态反馈关系，支持AR128与AR1之间的encoding映射；AR256分支仍保留 `Add_48`、`Mul_18` 等编号映射。这些编号依赖具体图，不能泛化为稳定语义标识。

`hf_qwen3_5_vl.py` 中的 `perform_calibration_ar1` 先用保留的动态适配模型完成prefill，再通过AR1 QuantSim逐token解码。这为decode校准提供实际生成状态，但不能代替量化prefill与decode在设备上的联合验证。

## 1.3 已观察问题与待验证影响

| 静态观察 | 依据位置 | 影响或后续核验 |
|---|---|---|
| README仍列出已被统一入口替换的按规模编译脚本 | 根README；Stage 3实际脚本目录 | 按旧命令执行会找不到文件，运行前以现有入口核对 |
| decoder Python不读取OUTPUT_DIR决定模型产物目录 | `hf_qwen3_5_vl.py` 的 `_output_base`/`output_dir`；`run_arn_vl.sh` | 覆盖Shell输出目录可能只改变日志位置 |
| encodings未精确同名匹配时回退到首个候选 | `qwen3_5_builder.py:get_related_encodings_path` | 多个文件混放时有误配风险，建议失败退出或明确指定 |
| 跨图参数加载使用strict=False且未检查返回键列表 | `hf_qwen3_5_vl.py` 第7.8节 | 映射变化时可能漏加载；本文未复现精度异常 |
| prefill脚本注释要求PPL评估承担buffer预热 | `run_arn_vl.sh` 的RUN_PPL_EVAL说明 | 评估和初始化耦合；关闭评估可能影响prepare，未在本项目复测 |
| 导出、编译及设备配置分散维护 | Stage 2环境变量、Stage 3默认值、Stage 4 JSON | 上下文长度、图拆分及视觉patch grid需要跨阶段核对 |

Stage 3 README对 `--finalize-p 15` 的描述与当前脚本默认不传该参数存在差异；仅凭静态代码不能推断底层SDK一定跳过finalize或确定性能损失。该项应保留为SDK行为核验问题。

## 1.4 已完成哪些验证

本次对话前序执行的语法检查结果为：137个Python文件AST解析通过、33个JSON文件解析通过、15个Shell文件通过 `bash -n`。这些是当时的检查结果，本记录没有归档原始工具输出或完整代码快照。本次未发现常规自动化测试套件；名为test_vectors的文件主要用于生成测试向量。

没有安装依赖、下载模型或数据、运行AdaScale、导出ONNX、执行QAIRT编译或连接目标设备。因此本记录不提供精度、延迟、内存、SDK兼容性或端到端可用性结论。

## 1.5 下一步如何使用这个案例

先阅读 [[02_Projects/VLM部署/量化部署流程与验证框架]] 理解四组对比，再按 [[02_Projects/VLM部署/Qwen3.5量化部署实操规划]] 核对环境、产物交接和首轮验证动作。仓库固定依赖中包括torch 2.6.0、aimet-torch 2.29.0、transformers 4.57.1，并附有qairt_dev wheel；SDK、模型及数据的实际可用性仍需确认。部分脚本还保留原环境 `/prj/qct/...` 默认路径。

实验开始时应保存代码身份和配置；在此之前，本文用于导航和提出核验问题，不作为已验证部署方案。官方方法入口见 [[04_Sources/VLM部署/2026-10-30_量化部署官方资料学习导航]]。
