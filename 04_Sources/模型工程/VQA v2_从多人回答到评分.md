---
type: source_note
status: source_note
created_at: 2026-11-07
scope: 公开样本标注拆解与学习用对照，来源和核对范围见正文。
---

# VQA v2：同一问题为什么需要十个回答

在 COCO 验证图 262148 中，一名滑板者位于桌面上方，后方有观众。对同一张图提出三个问题，十位回答者的分歧有三种不同含义。本次用 question_id 联结官方验证问题、十份人工答案和互补题清单，并查看两张原图。[数据与配对下载](https://visualqa.org/download.html) · [原图 262148](https://s3.amazonaws.com/images.cocodataset.org/val2014/COCO_val2014_000000262148.jpg)

| 验证题 ID | 问题含义 | 十份发布答案的计数 |
|---|---|---|
| 262148000 | 他在看哪里？ | down ×7，at table ×1，skateboard ×1，table ×1。有人答朝向，有人答注视目标。 |
| 262148001 | 背景里的人在做什么？ | watching ×9，spectating ×1。两种说法在这个场景下含义接近。 |
| 262148002 | 他位于什么上方？ | picnic table ×6，table ×3，skateboard ×1。桌子的类别粒度不同，滑板则是另一个空间参照物。 |

**把边界答案代进评分。** 以第三题预测 `table` 为例，官方算法依次留出一名回答者，用剩余九份计算匹配数除以 3，上限为 1，再对十次取平均。留下的那个人若答了 table，余下两份匹配，出现 3 次；其余 7 次均有三份匹配。最终为 (3 × 2/3 + 7 × 1)/10 = **0.9**。同题答 picnic table 得 1，答 skateboard 得 0.3。第二题的 spectating 同样只有 0.3。官方归一化处理大小写等写法，近义表达仍可能因人群用词频率而得分不同。[官方评分](https://visualqa.org/evaluation.html)

**为什么还要换图。** 262148001 与 209757007 是官方互补对，问题逐字相同。第二张图背景可见滑板场地及其他人物，参考答案改为 skateboarding ×7、skating ×3。若模型只记住“背景的人通常在观看”，在第一题可得满分，在配对题得 0。图像和问题构成作答输入，十份答案用于监督与评测，配对 ID 用于检查模型是否随视觉证据改变回答。互补题还揭示了另一条边界：两张图上各自到底看得多清，是图像证据问题，十人意见一致度度量的是回答共识。[配对文件](https://cvmlp.s3.amazonaws.com/vqa/mscoco/vqa/v2_Complementary_Pairs_Val_mscoco.zip) · [原图 209757](https://s3.amazonaws.com/images.cocodataset.org/val2014/COCO_val2014_000000209757.jpg)
