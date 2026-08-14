---
type: project_practice_record
status: user_reported
project: AI-Career-Transition
learning_stage: Phase 1-C - VLM baseline and benchmark draft
practice_kind: single_image_smoke_test
summary: 记录用户在 Google Colab T4 环境使用 Qwen2.5-VL-3B-Instruct 完成单图多模态推理和双眼状态结构化输出 smoke test 的代码、结果与证据边界。
sources:
  - 2026-08-14 用户提供的 Google Colab 推理代码、标注片段与运行输出
  - 02_Projects/AI-Career-Transition/10_学习文档/P01C-01_VLM基线与Benchmark_学习文档.md
  - 02_Projects/AI-Career-Transition/20_学习记录/P01C_VLM基线与Benchmark_学习记录.md
scope: 单张座舱图片的 Qwen2.5-VL 加载、视觉预处理、确定性生成、JSON 解析、耗时和峰值显存 smoke test。
risks:
  - 本次结果由用户在 Colab 运行并粘贴，代理未独立复跑，也未读取 Google Drive 中的模型、图片或完整标注文件。
  - 未保存 Python、PyTorch、Transformers、qwen-vl-utils、驱动、CUDA runtime、模型文件 hash、图片 hash 和完整许可证快照。
  - 原始输出带 Markdown 代码围栏，不满足 prompt 中的严格裸 JSON 要求；只有去除围栏后的语义结果与标注一致。
  - 单个 case 只能证明 smoke test 链路和该样本的归一化后结果，不能支持 zero-shot baseline、聚合 accuracy 或 benchmark 结论。
updated_at: 2026-08-14
---

# 1 Phase 1-C VLM 单图 Smoke Test 实践记录

## 1.1 实践合同

- 目标：验证 Google Drive 模型加载、单图视觉输入、Qwen2.5-VL 推理、结构化输出、JSON 解析、耗时与峰值显存记录链路。
- 非目标：不评估聚合 accuracy，不声明 zero-shot baseline 通过，不建立 benchmark，不执行 few-shot 或微调。
- 输入与来源边界：用户提供 Google Drive 图片路径和对应标注片段；图片、完整标注文件与使用授权未由代理独立读取或验证。
- 方向定义：`left_eye` 和 `right_eye` 分别指最终输入画面的左侧和右侧眼睛。
- 允许标签：`open | closed | narrow | abstain`。
- 期望行为：本 case 的左右眼标注均为 `closed`。
- 严格格式要求：只输出合法裸 JSON，不输出 Markdown、解释或额外字段。

## 1.2 冻结配置

| 项目 | 本次配置 | 证据边界 |
|---|---|---|
| 运行环境 | 用户报告的 Google Colab T4 16 GB | `nvidia-smi`、驱动和包版本未保存 |
| 模型路径 | `/content/drive/MyDrive/models/Qwen2.5-VL-3B-Instruct` | 精确 revision 和文件 hash 未保存 |
| 模型 dtype | `torch.float16` | 来自用户粘贴代码 |
| device map | `auto` | 来自用户粘贴代码 |
| processor | `AutoProcessor.from_pretrained(model_path)` | processor 版本和像素预算未保存 |
| 图片路径 | `/content/drive/MyDrive/datasets/2026011430_20260114-175455_BlnkHO/APillar_C1UL_seat1_2026011430_m_175_18_Black_BlnkHO_Glasses_c1lR1_StaticOutdoor_DawnDusk_700_NormalScene_000036.jpg` | 图片 hash 未保存 |
| 标注 | 画面左眼 `closed`，画面右眼 `closed` | 来自用户提供的两个眼部框和 `eye_closed` 属性 |
| 随机种子 | `47` | CPU 与 CUDA seed 均设置 |
| 解码 | `do_sample=false`、`num_beams=1`、`max_new_tokens=64` | 确定性生成配置 |
| 运行次数 | `1` | 未做重复运行一致性检查 |

prompt 要求模型分别输出画面左右眼状态；证据不可辨认时输出 `abstain`；目标 schema 为：

```json
{"left_eye":"closed","right_eye":"closed"}
```

## 1.3 执行与原始结果

模型加载和首次开放描述推理成功。用户随后运行任务特定推理，核心生成调用为：

```python
with torch.inference_mode():
    generated_ids = model.generate(
        **inputs,
        do_sample=False,
        num_beams=1,
        max_new_tokens=64,
    )
```

原始输出为：

````text
```json
{
  "left_eye": "closed",
  "right_eye": "closed"
}
```
````

用户代码中的 `extract_json()` 去除 Markdown 代码围栏后，得到：

```json
{
  "left_eye": "closed",
  "right_eye": "closed"
}
```

运行观测：

| 指标 | 结果 |
|---|---:|
| execution success | `true` |
| elapsed seconds | `13.581` |
| peak memory allocated | `8.631 GiB` |
| peak memory reserved | `9.137 GiB` |
| normalized semantic match | `true` |
| strict raw JSON compliance | `false` |

## 1.4 评分与失败分析

本次必须拆分两个结果：

- `raw_format_success = false`：原始输出包含 Markdown 代码围栏，不符合严格裸 JSON 合同。
- `semantic_pass_after_normalization = true`：去除围栏后，左右眼结果与用户提供的标注一致。

当前代码把 `expected` 作为 `infer_qwen_vl()` 的外部全局变量。单 case 可以运行，但扩展到多 case 时可能误用上一条标注；后续应把 `expected` 作为显式参数传入评分函数。

最终 `case_pass` 应采用严格原始格式还是“允许预先冻结的代码围栏归一化后再评分”，尚未确认。该规则必须在 zero-shot baseline 前冻结，不能根据后续输出临时改变。

## 1.5 结论与边界

- 已获得用户报告的真实单图多模态推理证据，模型加载、图片处理、GPU 推理、生成、解码、JSON 归一化和资源记录链路可运行。
- 本 case 在归一化后语义上正确，但严格原始输出格式未通过。
- 本次不支持任何总体、macro、worst-group 或安全关键组指标，也不证明 zero-shot/few-shot baseline 完成。
- 由于环境版本、模型 hash、图片 hash 和完整标注路径未冻结，本记录不是完全可复现的 baseline 证据。

## 1.6 下一步

1. 冻结严格 JSON 与允许代码围栏归一化之间的评分规则，并分别保留格式合规率和归一化后语义正确率。
2. 把 `expected` 改为推理或评分函数的显式参数，避免多 case 污染。
3. 保存 `nvidia-smi`、`torch.version.cuda`、Python 和关键包版本，以及模型与图片 hash。
4. 冻结小型 case 集和门禁后运行 zero-shot baseline；本 smoke case 不直接充当最终留出集结论。
