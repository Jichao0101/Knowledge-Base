---
type: source_note
status: source_note
created_at: 2026-11-07
scope: 公开样本标注拆解与学习用对照，来源和核对范围见正文。
---

# LLaVA-Instruct：教师生成的回答能追溯到什么证据

初代 LLaVA 用 COCO 图像的人工描述和对象框作为语言教师的文本输入，由教师生成指令数据。学生训练时收到原图和问题，对助手回答进行监督。两者接收的证据不同。下面从三个发布文件各取一条，按 COCO ID 回查五条人工描述及原图。人工描述是可复核的原料，本次没有取得逐次教师请求日志。[作者数据说明](https://github.com/haotian-liu/LLaVA/blob/main/docs/Data.md) · [论文 §§3–4](https://arxiv.org/abs/2304.08485) · [COCO 原始标注](https://s3.amazonaws.com/images.cocodataset.org/annotations/annotations_trainval2014.zip)

| 文件、COCO ID | 教师给出的监督 | 对照人工描述与原图 |
|---|---|---|
| conversation_58k，033471 | 三轮依次回答公交车颜色、车尾特征、车辆在行驶还是靠边。 | 白红车身和车尾广告有文字和画面支持。五条描述中既有沿街行驶，也有靠边停靠。教师最后选了行驶。单帧可以看见道路位置，很难据此裁定速度。[原图](https://s3.amazonaws.com/images.cocodataset.org/train2014/COCO_train2014_000000033471.jpg) |
| detail_23k，442786 | 长描述包含广场、拿风筝的男子、其他行人及对气氛的概括。 | 人工描述明确提到广场、行人、拿风筝与双腿交叉。原图可见相应人物姿态。“人们玩得开心”需要推测感受，训练长描述时应区别可复核细节与文风扩写。[原图](https://s3.amazonaws.com/images.cocodataset.org/train2014/COCO_train2014_000000442786.jpg) |
| complex_reasoning_77k，215677 | 询问完成胯下飞盘动作需要哪些技能，回答列出协调、平衡等。 | 多条人工描述提到飞盘从腿下或两腿间经过，原图能检查相对位置。练习形成肌肉记忆属于一般建议，图像并未提供此人训练经历的证据。[原图](https://s3.amazonaws.com/images.cocodataset.org/train2014/COCO_train2014_000000215677.jpg) |

**一次人工评分对照。** 若检查公交车记录中的三个事实，前两项可直接核验，第三项应标记“来源间有分歧，单帧无法定案”。按整段文本相似度评分，复述教师原话很容易掩盖这个问题。对于飞盘题，可分别评价“是否读对腿与飞盘的位置”及“建议是否合理”。这是针对样例的审核办法。该指令集主要提供训练目标，以上复核没有运行模型或官方基准。[三个原始 JSON 发布文件](https://huggingface.co/datasets/liuhaotian/LLaVA-Instruct-150K/tree/main)

这里值得借鉴的是保留图像 ID，以及从生成回答回到其原料的能力。遇到教师自行消解了原始分歧的样本，可以保留争议、改问静态可见特征或补充时间证据。仅凭回答完整流畅，无法决定哪种处置合适。
