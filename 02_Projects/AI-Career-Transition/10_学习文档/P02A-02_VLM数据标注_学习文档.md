---
type: project_learning_document
status: active
project: AI-Career-Transition
created_at: 2026-11-07
scope: 面向模型训练人员的标注规范设计学习材料，以九类任务说明如何选择监督信号和评估方法。
sources:
  - 04_Sources/模型工程/2026-11-07_VLM数据集标注方案来源对照.md
  - 正文各节附数据集发布入口、样本标识及评分或文件说明。
---

# 1 从公开样本学习设计 VLM 标注规范

拿到一个新任务，先找一条与目标接近的公开样本，试着回答三个问题：**模型得到什么输入？参考答案从哪里来？如果少采一项信息，哪种错误就无法发现？** 例如，同一张图可以拿来训练描述，也可以训练定位。描述任务把区域交给模型，请它写一句话；定位任务把那句话交给模型，请它返回区域。两者甚至可以复用同一批事实，输入和答案的位置却恰好相反。

读每个案例时，把数据集制作者和模型看作两个不同的参与者。**制作者可以看人工标注、完整录像或源表来确定答案；模型在训练和部署时能看什么，取决于你设计的任务。** 下文的发布记录展示标签从哪里来；含 `input` 与 `target` 的 JSON 展示一种可选的训练导出方式。图像或视频 ID 表示加载对应媒体。训练时用 target 计算损失，部署时只提供 input 中约定的信息。以下导出示例说明设计方法；实际训练、调参与最终评测应使用各自的数据划分。

| 要训练的输出 | 主例 | 该例最值得研究的决定 |
|---|---|---|
| 1.1 实体类别、位置与轮廓 | Visual Genome | 如何让标签对应图中一个具体实例 |
| 1.2 图像或区域描述 | COCO Captions | 同一幅图为什么允许多种描述 |
| 1.3 从语言定位对象 | Flickr30K Entities | 一条表达何时对应多个框 |
| 1.4 图文检索 | Flickr30K | 哪些图文算匹配，负例从哪里来 |
| 1.5 视觉问答与推理 | GQA，辅以 VQA v2 | 答案是按标注求出来，还是由多人提供 |
| 1.6 OCR、文档与图表理解 | ChartQA | 正确读数与正确计算如何分开验证 |
| 1.7 视频动作、时间定位与预测 | Drive&Act | 同一帧应采用哪一层时间标签 |
| 1.8 多轮对话与消歧 | SIMMC 2.1 | 当前轮不知道的事怎样记录 |
| 1.9 工具调用 | BFCL | 应保存一段回答、一次调用，还是执行结果 |

## 1.1 实体识别与检测：一个标牌需要几种标注？

![Visual Genome 图像 1：街边两人、时钟、建筑和车辆](assets/vlm-annotation/vg-1.jpg)

在街景左侧可以找到一块固定在建筑外墙上的标牌。Visual Genome 图 1 的关系记录 15930 同时引用标牌和建筑。先只读其中的标牌对象，以下是原字段节选。[Visual Genome 标注文件与字段](https://visualgenome.org/api/v0/api_readme)

```json
{"object_id":1058507,"name":"sign","x":118,"y":13,"w":88,"h":182}
```

对象类别和框来自底层对象标注。制样程序可以用同一行生成两种监督。假设本题只要求定位这块标牌，下例用源框作目标；`bbox_xywh_px` 按原图像素保存左上角、宽、高。

```json
{
  "input": {"image":"vg/1","question":"图中建筑外墙上的标牌在哪里？"},
  "target": {"bbox_xywh_px":[118,13,88,182]}
}
```

如果训练坐标输出，损失要覆盖模型预测的框，部署时返回框。若改为给定区域识别类别，就在制样时按这组坐标裁图，用裁剪图作输入，只对类别 sign 计算损失。后一种模型上线时需要有人或上游检测器给出区域。两种任务都能复用对象 ID 来连接记录。

图 1 的原始尺寸为 800 × 600。object_id 让描述、属性和关系都能引用同一个实例。若要训练整图中**全部**标牌的检测，单独这一条正例还不够，训练团队得确定覆盖范围并检查是否漏标。

要不要采掩码，取决于边界是否影响交付。如果下游只需高亮一个大致区域，框可以承担这个用途；若要按可见轮廓抠出物体，就需像素级标注。实例分割还要把相邻的同类物体分开。用这条 Visual Genome 记录可以派生分类和框定位样本，无法从四个框坐标恢复标牌的真实轮廓。需要学习多边形或掩码的发布格式时，再对照 [COCO 实例标注](https://cocodataset.org/#format-data)。

## 1.2 描述生成：同一张图可以有几个正确答案？

![广场上拿风筝的人](assets/vlm-annotation/coco-442786.jpg)

COCO 训练图 442786 中，一名男子拿着风筝，背后有人走过广场。五条人工描述关注点不同：有的写风筝和广场，有的写人群，还有的写男子双腿交叉。下面是同图的一条人工描述，节选两个发布字段。[COCO Captions 数据集](https://cocodataset.org/#captions-2015) · [COCO 2014 标注下载](https://s3.amazonaws.com/images.cocodataset.org/annotations/annotations_trainval2014.zip)

```json
{"image_id":442786,"caption":"A man flying a kite in a plaza area."}
```

这里没有生成问答的中间程序。人工已经写出了参考句，制样时只需按 image_id 取照片，把 caption 放进助手的目标文本。以生成式微调为例，模型看到照片和“描述这张图”的指令，损失算在参考句的输出 token 上。上线时生成一条描述即可；选择哪一句人工描述用于本次更新，是训练团队的数据采样决定。

**标注重点是描述的范围和允许省略的内容。** 如果目标是生成一句自然的整图描述，写到男子和风筝就可以成为参考答案。若产品要求“列出所有告警图标”，遗漏一个告警都影响使用；这时应定义必答事实，评测它们的覆盖率。让人随意写五句流畅描述，也不能保证某个稀有图标一定被提到。

当目标是“描述指定区域”，还要保存文字指的是哪块区域。例如上一节街景中的区域 1432 有独立短句。区域框与对象框服务于不同问题，两组坐标可以不同。[Visual Genome 区域记录说明](https://visualgenome.org/api/v0/api_readme)

```json
{"region_id":1432,"image_id":1,"x":122,"y":14,"width":84,"height":178,"phrase":"A sign on the facade of the building"}
```

## 1.3 语言定位：“两个人”这句话应当连到哪个框？

![Flickr30K 原图 1000092795，院子里两个人站在一起](assets/vlm-annotation/flickr30k-1000092795.jpg)

先看原图：两个人靠得很近，右侧穿浅色上衣的人站得稍靠前。下面把同一张照片并排展示，黄框按发布的 XML 坐标绘制。左图读短语 **Two men**，要找出两个人；右图读 **A man**，这条描述选中右侧的人。[图像来源：Flickr30K 数据集，文件 1000092795.jpg](https://huggingface.co/datasets/nlphuji/flickr30k)

![同图短语对照：编号 1 对应两个独立人物框，编号 6 只对应右侧人物框](assets/vlm-annotation/flickr30k-1000092795-chains.svg)

Flickr30K Entities 的图 1000092795 在不同描述中出现“两个人”“两位朋友”等说法。发布文件 `Sentences/1000092795.txt` 给这些短语相同的指代编号 1；同图 XML 中有两个矩形带有这个编号。下面把两份文件联结成一小段 JSON，便于阅读。坐标沿用 XML 的 xmin、ymin、xmax、ymax。[作者标注包](https://github.com/BryanPlummer/flickr30k_entities/blob/master/annotations.zip) · [短语与区域的对应规则](https://github.com/BryanPlummer/flickr30k_entities)

```json
{
  "image":"1000092795.jpg", "phrase":"Two men", "chain_id":1,
  "boxes_xyxy":[[159,125,219,335],[197,110,261,373]]
}
```

这两个框怎样进入训练？制样程序先用 chain_id 把人工短语标注和 XML 中的框连接起来，再移除仅用于连接的编号。采用直接定位方案时，一条导出样本如下。

```json
{
  "input": {"image":"1000092795.jpg","phrase":"Two men"},
  "target": {"boxes_xyxy":[[159,125,219,335],[197,110,261,373]]}
}
```

这种方案训练并评价两个预测框与真值区域的匹配，部署时输入原图和短语，输出框集合。也可以让上游检测器先提候选框，再训练模型选中候选；后一方案的损失针对候选选择，部署时还依赖检测器。人工短语编号本身不规定使用哪条路线。

如果模型输入图像和这个短语，目标就应覆盖两个人。训练时强行取第一个框会丢掉一人；取两个框的外接矩形，又改变了要模型交付的区域形状。因此应先决定产品允许一个目标、多个实例，还是一个整体区域，再决定如何从原标注导出答案。相反，同图的单数短语“A man”关联编号 6，只对应第二个矩形。这对样本可以检验模型是否利用了数量和指代差异。

**迁移到座舱。** “前面第二辆车是什么车型”先选车，再查属性。构造一例：本车道从近到远为 v1、v2，左车道为 v3、v4。若上一轮已明确本车道，可以保存 `候选=[v1,v2]，次序=由近到远，目标=v2，属性=车身类别，值=SUV`。如果部署只需回答车型，框和次序可用于生成和复核；若还需高亮目标，则要把定位加入模型输出。两辆车恰好同型时，单评“SUV”无法检出选错车。

## 1.4 图文检索：同一条描述在这里对应什么答案？

继续使用 Flickr30K 图 1000092795。上一节要从短语找到人物框；换成“按文字搜照片”，该图五条描述里的任意一条都可以作为查询，目标变成整张照片。以原描述的中文释义为例，下面是**据图文对应关系派生的训练样本**。[Flickr30K 图文数据](https://shannon.cs.illinois.edu/DenotationGraph/) · [该图的五条描述所在标注包](https://github.com/BryanPlummer/flickr30k_entities/blob/master/annotations.zip)

```json
{"query":"两个穿绿衬衫的男人站在院子里","positive_image_ids":["1000092795"]}
```

这些正例 ID 是从人工描述与原图的配对派生的。训练双编码器时，图像侧收到实际照片，文本侧收到查询，正例 ID 用来指定哪些相似度应提高。例如把图 1000092795 与经核实不匹配的照片放在同一批次，用对比损失提高真匹配相对负例的分数。部署时可预先编码图库，收到一句新查询后按相似度返回图像列表。模型从头到尾都可以不用生成图片文件名。

一条原始配对能证明这张图是正例，却无法证明图库中别的照片都不符合。构建负例时，可以挑一张同样是“两个人在院子里”但衣服条件明显不符的图，人工核实后加入候选。这样即使模型会认“人”和“院子”，也必须用到“绿衬衫”才能排对。若候选中另有完全符合描述的图，应允许多正例。用前 K 个结果是否命中正例来衡量检索质量时，还要说明正例核查覆盖了哪些候选。

## 1.5 视觉问答：一道题需要哪几项人工事实？

![GQA 图 1339：米饭左方的叉子压在白色餐巾上](assets/vlm-annotation/gqa-1339.jpg)

GQA 验证题 14778715 问“米饭左侧的餐具下面有没有餐巾”。在图 1339 的标注中，先找到米饭 1066932，再找到左侧餐具 1066923，最后查到餐巾 1066926 指向该餐具的 under 关系。因此参考答案为 yes。下面是餐巾关系表中的原始出边；这一行必须连同它所属的餐巾对象一起读。[GQA 官方场景图与问题格式](https://cs.stanford.edu/people/dorarad/gqa/download.html) · [验证题记录](https://huggingface.co/datasets/pppop7/GQA/viewer/val_balanced_instructions/val)

```json
{"object":"1066923","name":"under"}
```

**先看这道题怎样被制出来。** GQA 整理 Visual Genome 中基于人工观察的对象、属性和关系，再由程序基于场景图生成题目和答案。上面这条 under 关系只是原料之一。这道题还要用到米饭左边是哪件餐具。发布问答中的 `semantic` 保存操作、参数和步骤依赖；下面列出该题的操作顺序（中文释义），便于对照场景图。

选取米饭 1066932 → 找它左边的餐具 1066923 → 找在该餐具下面的餐巾 1066926 → 查结果是否非空 → yes。这里描述的是**制作者如何得到参考答案**。只抄下三个对象编号会丢掉“左侧”和“下方”及其方向，无法据此重算答案。[GQA 官方构造说明](https://cs.stanford.edu/people/dorarad/gqa/about.html)

**再看用于训练时，哪些字段真正进模型。** 以直接回答的 VLM 为例，下方用这道验证题演示同类训练样本的形状，问题译成中文。制样程序根据 imageId 加载原图，从问答记录读取问题和已算好的答案。

```json
{
  "input": {"image":"gqa/1339","question":"米饭左边的餐具下面有餐巾吗？"},
  "target": {"answer":"yes"}
}
```

训练时对答案计算分类或生成损失。部署时给图和问题，模型直接答题。它是否利用了物体关系，要用对照题或定位实验来检验；即使答对 yes，也不能据此认定它在内部执行了上面的程序。

| 训练团队的选择 | 训练时对什么计算损失 | 部署时怎样回答同一道题 |
|---|---|---|
| 直接问答 | 只监督最终答案 | 图像＋问题 → 答案 |
| 关系辅助监督 | 答案损失之外，用已有关系标签训练一个辅助目标 | 可以只保留问答输出，辅助标签无需作为输入 |
| 显式两阶段推理 | 先用对象和关系真值训练场景图预测器；自然语言若需转程序，还要实现或训练解析器 | 从图像预测场景图，从问题得到查询，再在预测图上求答案。直接使用人工真值图只能检验后半段 |

**这里值得采集的是能反复出题的底层事实。** 问颜色只需一个对象和属性；比较两个集合的数量要先确定成员、去重并计数；上面的关系题还要查两条方向正确的边。若用规则扩量，验收时既要执行一次程序，也要回看图核对其依赖的事实。漏掉餐巾关系时，程序可能稳定地产出错误的否定答案。[CLEVR 的场景与程序](https://cs.stanford.edu/people/jcjohns/clevr/)

**什么时候值得改采多人答案？** VQA v2 对左图问“他位于什么上方”，十人分别给出 picnic table 六票、table 三票、skateboard 一票。问题 ID 为 262148002。差异有两种来源：“桌子”和“野餐桌”描述粒度不同，滑板与桌子则是两个空间参照。若希望评估自然回答，这组分歧本身就值得保留。[VQA v2 数据](https://visualqa.org/download.html) · [官方评分规则](https://visualqa.org/evaluation.html)

| 图 262148 | 配对图 209757 |
|---|---|
| ![滑板者位于桌面上方，背景有人观看](assets/vlm-annotation/coco-262148.jpg) | ![另一滑板场景，背景人物及活动随图像改变](assets/vlm-annotation/coco-209757.jpg) |

官方评分每次排除一人，剩余九人中有三人或更多同答就给满分。答 table 时，三次余两票、七次余三票，因此得 (3 × 2/3 + 7 × 1)/10 = 0.9。同一对图片还可检查模型是否看图：问背景中的人在做什么，左图为 watching 九票、spectating 一票；右图变为 skateboarding 七票、skating 三票。固定回答 watching 只会答对前图。

## 1.6 文字与图表理解：参考答案是抄出来的，还是算出来的？

![ChartQA 图 41699051005347，羊肉和玉米的指数分别为 103.7 与 103.13](assets/vlm-annotation/chartqa-41699051005347.png)

ChartQA 的人工测试题问图中羊肉与玉米的数值之差。柱端分别写着 103.7 和 103.13，源表也有这两个值，二者相减为 **0.57**。同图另有一道计数题，答案是图中展示了 14 种食品。下面是差值题发布记录的字段与原值。[人工问题文件](https://raw.githubusercontent.com/vis-nlp/ChartQA/main/ChartQA%20Dataset/test/test_human.json) · [该图源表](https://raw.githubusercontent.com/vis-nlp/ChartQA/main/ChartQA%20Dataset/test/tables/41699051005347.csv) · [ChartQA 数据集](https://github.com/vis-nlp/ChartQA)

```json
{"imgname":"41699051005347.png","query":"What is the difference in value between Lamb and Corn?","label":"0.57"}
```

这条记录属于人工测试题。把它作为格式示范：对同类训练样本，生成式 VLM 的输入是原图和 query，目标是文本“0.57”，训练损失算在答案上。部署时模型根据新图和新题输出数值。模型是否内部学会了相减，不能从命中一次答案推出。若产品要给出可检查的算式，训练团队可另外采集或派生“羊肉读数、玉米读数、相减”的监督，并把算式列为输出要求。

模型答错时，源表能帮助区分三种错误：读错小数、取错食品行、算错差值。**发布的问答记录只给最终标签；保存操作数与运算是自建诊断集可以选择的做法。** 若部署只有图像，把源表同时喂给模型会改变题目难度。

相邻任务所需的标签更少或不同。如果问“第一行末尾印着什么”，OCR 监督可以是原文 `103.7`；若要求高亮它，还要文字框。若在文档中问“到期日”，要把答案关联到正确字段，即使纸上还有另一个同格式日期。可分别参照 [TextOCR 的文字区域与转写](https://textvqa.org/textocr/dataset/)、[TextVQA 的场景文字问答](https://textvqa.org/download/) 和 [DocVQA 的单页抽取式问答](https://www.docvqa.org/datasets/docvqa)。

## 1.7 视频理解：先决定要识别哪一段行为

| Drive&Act 深度录像，第 400 帧 | 同一录像，第 480 帧 |
|---|---|
| ![第 400 帧，对照从安全带处收回区间](assets/vlm-annotation/da-2.png) | ![第 480 帧，中层标签已切换到操作屏幕](assets/vlm-annotation/da-4.png) |

Drive&Act 中同一个人系安全带，第 400 帧既属于“系安全带”的任务，也属于“手从安全带处收回”的短时交互；到第 480 帧，长期任务标签仍是系安全带，中层动作已变成操作多媒体屏。下面是第 400 帧所属交互区间的发布行。按录像和帧区间跨表关联，就能看到为什么同一帧会有多个正确标签。[Drive&Act 数据与使用条件](https://www.driveandact.com/) · [活动标注 CSV](https://www.driveandact.com/dataset/iccv_activities_3s.zip)

```csv
participant_id,file_id,annotation_id,frame_start,frame_end,activity,object,location,chunk_id
1,vp1/run1b_2018-05-29-14-02-47.kinect_depth,1,380,417,retracting_from,seatbelt,left_backseat,0
```

发布行记录的是人工界定的动作区间及其动作、物体和位置。下面演示一个制样程序怎样使用它：在 380–417 内截取 390–410 帧，实际像素作为输入，复制动作与物体作为分类目标。选这个子窗口是本文的设计选择。

```json
{
  "input": {"video":"vp1/run1b_2018-05-29-14-02-47.kinect_depth","frames":[390,410]},
  "target": {"action":"retracting_from","object":"seatbelt"}
}
```

**这是要在指定片段内分类，还是要模型自己找出片段？** 片段分类可分别对动作和物体计算损失，部署时输入已经切好的片段。若要自动找出动作何时发生，就改为输入长视频与查询，监督开始和结束位置，部署输出区间。这时把人工切好的短片直接交给模型会跳过定位任务。若任务是预测下一动作，必须再定一个预测时刻，未来观察仅用作标签。边界评分也随之变化：类别答对不足以证明找准了开始时刻，切片长度更不能自动当成事件的最短观察时长。[ActivityNet Captions 的事件区间与描述](https://cs.stanford.edu/people/ranjaykrishna/densevid/)

驾驶场景还有视角约束。DriveLM 演示帧 4a0798f849ca477ab18009c3a20b7df2 的对象 c1 绑定后向相机。对“它是路障吗”可以查 Vehicle 类别；对“它是否在动”可以核对发布状态，但要独立验证速度还需连续时间证据；对“自车该不该保持速度”则需策略评价依据。任务名称本身不足以决定评价方式。[DriveLM 演示帧与问答](https://raw.githubusercontent.com/OpenDriveLab/DriveLM/main/challenge/data/train_sample.json)

| 同一关键帧，前向 | 同一关键帧，后向 |
|---|---|
| ![前向原图：湿路面及上方信号灯](assets/vlm-annotation/dl-CAM_FRONT.jpg) | ![后向原图：后方道路和车辆](assets/vlm-annotation/dl-CAM_BACK.jpg) |

## 1.8 多轮对话：怎样保存“当前还不知道”？

SIMMC 2.1 官方数据说明给了一个消歧例：用户问一件衬衫的价格，场景中有多件衬衫。文档用 1、3、4、5 等对象编号示意可能的指代；歧义轮的已确定对象列表为空。下面是**按官方示意缩写的 JSON**，候选只展示其中几个，未当作某条训练集记录的完整名单。[SIMMC 2.1 原字段与示例](https://github.com/facebookresearch/simmc2/blob/main/data/README.md)

```json
{"disambiguation_label":1,"disambiguation_candidates":[1,3,4,5]}
```

这些候选属于人工记录的对话状态。若训练目标是回复用户，还要明确谁提供助手回复：可以由人写，也可以用缺失参数按模板生成，再由人复核。下例是借鉴 SIMMC 思想构造的座舱对话，分别列出两次前向计算真正可见的输入和该轮要学的回复。

```json
[
  {
    "input": {"scene":"demo/front01","history":[],"user":"前面第二辆是什么车型？"},
    "annotation": {"possible_targets":["v2","v4"],"target_id":null},
    "target": {"reply":"您指本车道还是左车道？"}
  },
  {
    "input": {"scene":"demo/front01","history":[["user","前面第二辆是什么车型？"],["assistant","您指本车道还是左车道？"]],"user":"左车道。"},
    "annotation": {"target_id":"v4"},
    "target": {"reply":"左车道前方第二辆是货车。"}
  }
]
```

训练生成回复时，只对本轮助手文本计算损失。`possible_targets` 和 `target_id` 可以留给离线质检。若需要模型显式列出候选，再增加指代消歧目标。部署时模型得到现场图像、历史和当前用户话语，决定追问或回答。第一轮评分看它是否问到缺失的车道，第二轮评分看它是否用上用户补充的信息。目标清楚但车标模糊时，应另记为证据不足。[多轮视觉对话](https://visualdialog.org/) · [不可回答的视觉问题](https://vizwiz.org/tasks-and-datasets/vqa/)

## 1.9 工具调用：要标调用参数，还是工具执行后的答案？

BFCL 的 simple_python_0 询问底为 10、高为 5 的三角形面积，将 calculate_triangle_area 的接口提供给模型。对普通问答，回答 25 已能表达数值；这道工具题却要检验是否选对函数，并把 10 和 5 放进对应参数。发布答案节选如下。[BFCL 题目与函数定义](https://raw.githubusercontent.com/ShishirPatil/gorilla/main/berkeley-function-call-leaderboard/bfcl_eval/data/BFCL_v4_simple_python.json) · [该题参考调用](https://raw.githubusercontent.com/ShishirPatil/gorilla/main/berkeley-function-call-leaderboard/bfcl_eval/data/possible_answer/BFCL_v4_simple_python.json)

```json
{"id":"simple_python_0","ground_truth":[{"calculate_triangle_area":{"base":[10],"height":[5],"unit":["units",""]}}]}
```

这里的列表记录评测可接受的参数值。实际发起调用时，base 和 height 各取一个整数。若直接拿评测 JSON 当作助手的训练文本，可能教出“传列表”的错误行为。设计时先用函数签名生成合法调用，再用评测参考核验参数。

从题目文件读取请求与工具签名，再从参考文件选择一个合法调用，可构成如下教学样本（签名压缩展示，省略可选参数 unit）。

```json
{
  "input": {"user":"求底为 10、高为 5 的三角形面积。","tool_signature":"calculate_triangle_area(base:int, height:int, unit?:string)"},
  "target": {"name":"calculate_triangle_area","arguments":{"base":10,"height":5}}
}
```

若用生成式模型，训练目标是可解析的函数名与参数；部署时由运行时执行调用，得到数值 25。助手若要向用户报告结果，再将真实工具返回加入下一轮输入。若业务只需模型回答数值，可以另外训练数字答案，但仅凭答对 25 无法验收函数调用。

**迁移到车控时再增加状态监督。** 例如“打开副驾阅读灯”，首轮目标可为 `{"tool":"set_reading_light","arguments":{"seat":"front_passenger","on":true}}`。先验收有无误操作主驾灯，等工具返回后再评价助手能否如实说明成功或失败。BFCL 是语言工具调用参照；若用户通过手势指灯，还要补第 1.3 节的视觉对象标注。[BFCL 多轮执行评测](https://gorilla.cs.berkeley.edu/blogs/13_bfcl_v3_multi_turn.html)

## 1.10 怎样把读到的做法写成自己的第一版规范

先拿一条真实输入，写出你愿意接受的答案，然后反推生成这个答案必须采集什么。若框、属性和规则已经足够，保存原始事实即可派生训练问答。若需要自然语言扩写，可以使用教师模型，但要检验扩写是否把不确定的证据变成确定陈述。

![公交车尾部与路侧车辆](assets/vlm-annotation/coco-33471.jpg)

LLaVA 的公交车样本 033471 正好说明这种风险。颜色和尾部广告可从画面核实；至于车辆正在行驶还是靠边停着，COCO 的五条人工描述本身有分歧，而生成对话给了一个确定答案。可以保留有证据的两轮，将运动判断另行复核。以下是发布样本的首轮消息。[LLaVA 发布数据](https://huggingface.co/datasets/liuhaotian/LLaVA-Instruct-150K/tree/main) · [生成方法与文件说明](https://github.com/haotian-liu/LLaVA/blob/main/docs/Data.md)

```json
{"id":"000000033471","image":"000000033471.jpg","conversations":[
  {"from":"human","value":"What are the colors of the bus in the image?\n<image>"},
  {"from":"gpt","value":"The bus in the image is white and red."}
]}
```

这里同样有两次不同的“看见”：教师基于已有描述与框写出对话，学生训练时接收原图、指令和此前轮次，对助手消息计算生成损失。部署学生只需要产品提供的图像和用户输入，教师描述没有因此成为在线依赖。

**九类任务中较可迁移的是三个检查问题。** 第一，只给部署时可见的信息，模型有没有依据完成任务？第二，从人工记录导出训练目标时，哪些条件和歧义被保留，哪些在转换中丢失？第三，把正确答案换成一个接近但有关键错误的答案，评分能否发现？这三问并不指定要几份答案、是否画掩码或是否输出中间步骤；那些决定应由本任务的失败代价、采集成本和下游用途来定。

用一小批样本试一次完整流程：独立填写原始标注，生成训练输入与目标，对照留出的同类样本复算评分。两人若选错了同一问题所指的目标，就修指代规则；若看见同一事实却使用不同标签，就修类别定义；若两种错误答案得分一样，就修评价协议。到这一步，才有依据判断是否值得扩量。
