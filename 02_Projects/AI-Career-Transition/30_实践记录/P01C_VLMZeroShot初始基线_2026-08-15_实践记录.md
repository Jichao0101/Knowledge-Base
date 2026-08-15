---
type: project_practice_record
status: user_reported
project: AI-Career-Transition
learning_stage: Phase 1-C - VLM baseline and benchmark draft
practice_kind: zero_shot_initial_baseline
summary: 记录 Qwen2.5-VL-3B-Instruct 在 5 个内部授权双眼状态 case 上的 zero-shot 初始基线、输入身份审计和固定人脸 ROI 诊断；链路与结构化输出稳定，但精确匹配仅 20%，出现 closed 类预测坍缩。
sources:
  - 2026-08-15 用户提供的 Google Colab 代码、环境快照、逐 case 输出、输入 hash 与固定 ROI 诊断
  - 02_Projects/AI-Career-Transition/20_学习记录/P01C_VLM基线与Benchmark_学习记录.md
  - 02_Projects/AI-Career-Transition/30_实践记录/P01C_VLM单图SmokeTest_2026-08-14_实践记录.md
scope: Qwen2.5-VL-3B-Instruct 双眼 open、closed、narrow、abstain 任务的 5-case zero-shot 初始诊断基线。
risks:
  - 结果由用户在 Colab 运行并提供，代理未访问 Google Drive、原图、标注或模型文件进行独立复跑。
  - 模型目录固定但尚未保存模型文件 hash、精确 revision 或许可证快照。
  - 仅有 5 个样本且每组 1 个；输出已被查看，因此这些 case 只能作为开发/诊断集，不能充当最终留出集或稳定 benchmark。
  - 固定 ROI 只在一个失败 case 上诊断，不能证明全部错误的唯一原因，也不能把错误归因确定为模型参数量不足。
updated_at: 2026-08-15
---

# 1 Phase 1-C VLM zero-shot 初始基线

## 1.1 实验目的与证据边界

本次实验承接 [[02_Projects/AI-Career-Transition/30_实践记录/P01C_VLM单图SmokeTest_2026-08-14_实践记录]]，在已经证明单图多模态链路可执行的基础上，检查同一冻结配置能否对一个小型多类别 case 集进行 zero-shot 推理，并暴露首个稳定失败模式。

它回答的是“当前模型、prompt、预处理和输入合同组合形成什么初始基线”，不是模型规模对比，也不是正式 benchmark 验收。5 个 case 的输出已经参与错误分析，后续只能作为开发/诊断样本。

## 1.2 冻结输入与推理合同

- 模型路径：`/content/drive/MyDrive/models/Qwen2.5-VL-3B-Instruct`
- 输入：单张完整图片和统一文字 prompt。
- 方向：`left_eye`、`right_eye` 均按最终输入画面左右定义。
- 标签：`open | closed | narrow | abstain`。
- `abstain`：眼睛因遮挡、眩光、模糊或画质问题而无法辨认时的拒答状态，不作为视觉类别。
- 输出：必须归一化为仅含 `left_eye` 与 `right_eye` 的 JSON 对象；允许外层存在一个 `json` Markdown 代码围栏，不允许解释、置信度或额外字段。
- 解码：`do_sample=false`、`num_beams=1`、`max_new_tokens=64`、seed `47`。
- 预处理：没有手工 resize；实际仍经过 `process_vision_info(messages)` 和 `processor(...)`，因此不能记为“无预处理”。
- 评分：先去除可选的单个 Markdown 代码围栏，再执行 JSON 解析、字段集合与枚举校验，最后对双眼做精确匹配。

运行 prompt：

```text
判断驾驶员双眼状态。

方向定义：
- left_eye：最终输入画面的左侧眼睛
- right_eye：最终输入画面的右侧眼睛

每只眼睛只能使用以下标签：
open、closed、narrow、abstain

判断规则：
- 根据图片中的眼部视觉证据判断。
- 如果遮挡、眩光、模糊或画质问题导致状态不可辨认，使用 abstain。
- 不要根据文件名、上下文暗示或输出示例猜测答案。

输出规则：
- 只输出一个 JSON 对象。
- JSON 必须且只能包含 left_eye 和 right_eye 两个字段。
- 可以使用单个 json Markdown 代码围栏。
- 不要输出解释、置信度或其他字段。
```

与首次 smoke test 相比，正确答案不再出现在 prompt 示例中，`expected` 也改为 `infer_qwen_vl` 的显式参数，避免答案泄露和全局变量耦合。模型仍为确定性贪心生成；seed 被保存为实验身份的一部分，但 `do_sample=false` 时不会通过随机采样决定 token。

## 1.3 软件与硬件快照

| 项目 | 值 |
|---|---|
| Python | `3.12.13` |
| PyTorch | `2.11.0+cu128` |
| PyTorch CUDA runtime | `12.8` |
| Transformers | `5.15.0` |
| Accelerate | `1.14.0` |
| qwen-vl-utils | `0.0.14` |
| Pillow | `11.3.0` |
| CUDA available | `true` |
| GPU | `Tesla T4` |
| GPU memory | `14.563 GiB`，`nvidia-smi` 显示 `15360 MiB` |
| Compute capability | `7.5` |
| NVIDIA driver | `580.82.07` |
| `nvidia-smi` CUDA | `13.0`，表示驱动支持上限，不是 PyTorch 实际 runtime |
| 快照时进程显存 | `9554 MiB` |

## 1.4 Case 清单与输入身份

全部样本的 `source_boundary` 均为“内部授权”，原图均为 `1920 x 1200`、RGB。

| case | group | expected | 文件 MD5 | 图片路径 |
|---|---|---|---|---|
| 1 | clear_closed | `closed / closed` | `818287ac778f8905c6afa0c192f924d6` | `/content/drive/MyDrive/datasets/2026011430_20260114-175455_BlnkHO/APillar_C1UL_seat1_2026011430_m_175_18_Black_BlnkHO_Glasses_c1lR1_StaticOutdoor_DawnDusk_700_NormalScene_000036.jpg` |
| 2 | fuzzy_open | `abstain / open` | `b59e3b023d24dfef0f8fa321012a8f3d` | `/content/drive/MyDrive/datasets/2026011427_20260114-125242_GlsAdj/APillar_C1UL_seat1_2026011427_m_180_46_Black_GlsAdj_Glasses_c1lR1_StaticOutdoor_SunnyNormal_1390_NormalScene_000002.jpg` |
| 3 | clear_open | `open / open` | `a01d104ad204bf27f4678ce508985c4a` | `/content/drive/MyDrive/datasets/2026011427_20260114-125242_GlsAdj/APillar_C1UL_seat1_2026011427_m_180_46_Black_GlsAdj_Glasses_c1lR1_StaticOutdoor_SunnyNormal_1390_NormalScene_000003.jpg` |
| 4 | clear_abstain | `abstain / abstain` | `e2afc6171a40695b19f5e30e1b6f5be2` | `/content/drive/MyDrive/datasets/2026011427_20260114-125242_GlsAdj/APillar_C1UL_seat1_2026011427_m_180_46_Black_GlsAdj_Glasses_c1lR1_StaticOutdoor_SunnyNormal_1390_NormalScene_000007.jpg` |
| 5 | clear_narrow | `narrow / narrow` | `567844c8bb4d84643531a0e341cd61ef` | `/content/drive/MyDrive/datasets/2026011429_20260114-170829_BlnkHO/APillar_C1UL_seat1_2026011429_m_182_23_Black_BlnkHO_Glasses_c1lR1_StaticOutdoor_SunnyNormal_1200_NormalScene_000011.jpg` |

处理后的五个输入都具有 `pixel_shape=(11868, 1176)`、`image_grid_thw=[[1, 86, 138]]`，但 tensor 内容 MD5 各不相同：

| case | processed MD5 |
|---|---|
| 1 | `f7dfed2ea82e8e524b7326e09d2eed12` |
| 2 | `a783899d8cc97d9dfbe86d7fedfec20f` |
| 3 | `e4a2b0218379ff71e05f7202dfdf1d8c` |
| 4 | `4c58df45a9b0b5e95f1ddbd6272ee4a7` |
| 5 | `86606316cb77df949d35ee9d9c7d23f0` |

因此可以排除“循环中意外重复送入同一图片或同一处理后 tensor”这一直接实现错误。相同 shape 和 image grid 只表示统一的处理预算，不表示内容相同。

## 1.5 逐 case 结果

五次原始输出都带一个合法的 `json` Markdown 代码围栏，归一化后均成功解析；模型对每张图都输出 `closed / closed`。

| case | parsed output | expected | case pass | failure label | elapsed | peak allocated | peak reserved |
|---|---|---|---:|---|---:|---:|---:|
| 1 | `closed / closed` | `closed / closed` | true | `None` | `9.768s` | `8.696 GiB` | `9.195 GiB` |
| 2 | `closed / closed` | `abstain / open` | false | `incorrect_classification` | `6.722s` | `8.694 GiB` | `9.195 GiB` |
| 3 | `closed / closed` | `open / open` | false | `incorrect_classification` | `6.094s` | `8.694 GiB` | `9.197 GiB` |
| 4 | `closed / closed` | `abstain / abstain` | false | `incorrect_classification` | `5.840s` | `8.694 GiB` | `9.197 GiB` |
| 5 | `closed / closed` | `narrow / narrow` | false | `incorrect_classification` | `5.783s` | `8.694 GiB` | `9.197 GiB` |

聚合结果：

- execution success：`5/5 = 100%`。
- 归一化后 JSON parse success：`5/5 = 100%`。
- case exact-match accuracy：`1/5 = 20%`。
- per-eye accuracy：`2/10 = 20%`。
- 平均推理时间：`6.841s/case`。
- 预测分布：`10/10` 只眼均预测为 `closed`。
- 每组只有 1 个 case；除 `clear_closed` 外其余组准确率均为 0%，不能据此估计稳定的组性能。
- 初始 baseline：`failed`。语义正确性未通过，且 5-case 开发集不足以宣布正式 benchmark gate 通过。

## 1.6 固定人脸 ROI 诊断

为检查全图图像 token 与目标区域尺度是否是主要原因，用户在 `clear_open` case 3 上采用固定 ROI `(950, 350, 1400, 650)`。该 ROI 根据已知相机视角设置，并用开发样本标注确认能覆盖眼睛；标注没有传入模型，也没有按当前图片真实类别动态选择裁剪框。

诊断结果：

- parsed output：`closed / closed`。
- expected：`open / open`。
- case pass：`false`。
- failure：`incorrect_classification`。
- elapsed：`1.723s`。
- peak allocated：`7.054 GiB`。
- peak reserved：`9.201 GiB`。

固定人脸 ROI 降低了耗时和 allocated 峰值，但没有修复该 case 的语义错误。这削弱了“仅因全图缩放或目标区域过小而失败”的解释；仍不能据单个 ROI case 证明参数规模是唯一原因。

## 1.7 错误分析与阶段结论

当前最强证据是：

1. 多模态加载、预处理、生成、归一化、解析、计时和显存记录链路可运行。
2. 不同文件和不同处理后 tensor 确实进入模型。
3. 当前模型与任务合同组合出现稳定的 `closed` 类预测坍缩，不能可靠区分 open、narrow 与 abstain。
4. 固定人脸 ROI 没有修复已知 clear-open 失败，因此继续围绕同一 5-case 微调裁剪或 prompt 容易把开发集错误当成能力提升。
5. 可以描述为“Qwen2.5-VL-3B-Instruct 在当前 zero-shot DMS 细粒度眼态任务上能力不足或模型-任务/域不匹配”；不能直接断言根因就是 3B 参数量限制。

当前没有必要把 3B/7B 对比作为 Phase 1-C 阻塞实验。它回答模型选择与容量归因问题，而本轮已经完成初始基线和主失败模式识别；若未来确有选型需求，可另建独立实验。

## 1.8 下一步

1. 冻结这 5 个 case 为开发/诊断集，不再把它们作为最终泛化证据。
2. 若需要提高结论强度，只新增一个小型、未查看的内部授权留出集，并在运行前冻结 ROI、prompt、归一化与门禁。
3. 在课程范围内决定：做一次最小 few-shot 对比，或把 few-shot/模型规模对比标为 `waived_by_scope`；不把 7B 对比设为默认必做项。
4. 模型 hash、精确 checkpoint 身份和许可证快照仍需在形成可移交 benchmark 前补齐。

