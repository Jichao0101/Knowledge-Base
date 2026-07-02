---
type: project_record
status: draft
project: DMS
module: SDK Integration
summary: 记录 DMS SDK 回灌方案的统一结构，当前已实现从模型阶段开始回灌，后处理阶段回灌为预留方向但尚未支持。
sources:
  - /home/jichao/dms/README.md
  - /home/jichao/dms/python_zmq/fillback_preprocess.py
  - /home/jichao/dms/etc/fillback.json
  - /home/jichao/dms/main/patac_vision_sdk.cpp
  - /home/jichao/dms/main/CameraInputJpgTest.h
  - /home/jichao/dms/source/utils/camera_inst.cpp
  - /home/jichao/dms/main/DmsProcessEngine.cpp
  - /home/jichao/dms/source/pipeline/dms_pipeline.cpp
scope: DMS SDK 离线/板端回灌入口、数据集格式、模型阶段回灌调用链，以及后处理阶段回灌的预留边界。
risks:
  - 当前仅基于源码与 README 静态阅读，未执行编译、x86 回灌或板端回灌验证。
  - README 明确提到 postprocess start_stage 目前不支持；不得把后处理阶段回灌写成已实现功能。
updated_at: 2026-07-02
---

# 1 DMS 回灌方案

## 1.1 当前结论

DMS 回灌方案使用统一 dump 数据集作为输入，通过 `fillback.json` 和 `manifest.csv` 把离线数据接入 SDK 的 camera callback 层。当前代码链路支持 `start_stage=model`，即从模型阶段开始回灌：SDK 读取离线图片，构造 `ImageData`，再进入原有 `DmsProcessEngine`、`DmsPipeline` 和 Fuse 链路。

README 中同时保留 `start_stage=postprocess` 的配置语义，但标注“目前不支持”。因此本文档把方案命名为“DMS 回灌方案”，不限定为原始图像回灌；后续从后处理开始回灌应作为同一方案下的扩展，而不是另起一个只面向图片输入的方案。

## 1.2 数据集结构

预处理脚本 `python_zmq/fillback_preprocess.py` 将 `video`、`bin` 或 `image_seq` 转换为统一 dump 目录：

| 路径 | 作用 |
|---|---|
| `images/<timestamp>.*` | 回灌图像，供 SDK camera callback 读取 |
| `atomic/<timestamp>.json` | 从 bin 解析出的历史 SDK 输出结果，当前主要作为后续 postprocess 回灌扩展的候选输入 |
| `manifest.csv` | 统一帧索引，字段为 `timestamp_us,frame_id,image_path,atomic_path` |

`manifest.csv` 是运行时索引入口。SDK 加载时要求表头固定，并要求 timestamp 严格递增；否则 `loadManifest()` 返回失败。

## 1.3 模型阶段回灌链路

当前已实现链路如下：

1. 预处理阶段生成 dump 目录和 `manifest.csv`。
2. `etc/fillback.json` 打开 `fillback`，设置 `car_type`、`source_type`、`start_stage`、`dumps_folder` 和 `camera_intrinsic_path`。
3. `PatacVisionSdk::Init()` 在 `J6M_PIC_VERSION` 或 `J6M_X86_VERSION` 分支读取 `fillback.json`，加载 manifest，并把 `FillbackContext` 注册给 `CameraInst`。
4. `ConfigureFillbackImageSize()` 读取第一张回灌图，设置 DMS 输入图像尺寸。
5. 回灌时 `GetImageRgbBuff()` 按 `picNum` 从 `FillbackContext::frames` 取帧，读取灰度图，校验分辨率，写入 `CameraData.buff` 和 timestamp。
6. `CameraInst::GetImage()` 调用已注册的取图函数，把 buffer 复制到 `ImageData::m_img`，并传递 timestamp。
7. `PatacVisionSdk::FetchImage()` 将 `ImageData` 推入 `DmsProcessEngine`。
8. `DmsProcessEngine` 复用原有队列、5M ROI/旋转处理和 `DmsPipeline` 调度。
9. `DmsPipeline` 继续执行检测、跟踪、landmark、其他模型与 Fuse 订阅，不区分数据来自真实相机还是回灌图片。

该设计的关键点是：回灌入口位于 camera callback 层，模型和 Fuse 主链路基本复用生产路径。

## 1.4 配置约束

`fillback.json` 当前关键字段：

| 字段 | 语义 |
|---|---|
| `fillback` | 是否启用回灌 |
| `car_type` | 必须显式设置为 1-7，用于车型和相机类型选择 |
| `source_type` | README 中使用 `bin`、`image_seq`、`video` 作为预处理来源类型 |
| `start_stage` | 当前可用值为 `model`；`postprocess` 是预留语义，README 标注暂不支持 |
| `dumps_folder` | dump 目录根路径 |
| `camera_intrinsic_path` | 回灌时使用的相机内参 JSON |

代码对 `car_type` 做合法性检查，避免静默继承默认车型。回灌开启时还会从 `camera_intrinsic_path` 初始化相机内参，避免离线图像与车型/内参不一致时无提示跑偏。

## 1.5 后处理阶段回灌预留边界

`fillback_preprocess.py` 已经能从 bin 中解析出 `atomic/<timestamp>.json`，并在 manifest 中记录 `atomic_path`。这为 `start_stage=postprocess` 提供了数据形态基础：后续可以按 timestamp/frame_id 读取模型原子结果，跳过模型推理，直接注入 Fuse 或后处理消费链。

但当前源码阅读中未看到 `start_stage` 分支实际改变 pipeline 起点，也未看到 runtime 使用 `atomic_path` 注入后处理。因此现阶段只能记录为预留扩展方向：

- 已有：dump/manifest 结构中保留 atomic 结果路径。
- 已有：配置项 `start_stage` 保留 `postprocess` 语义。
- 未有：从 atomic JSON 还原 `AtomicResult` 的运行时注入链路。
- 未有：跳过模型推理并直接驱动 Fuse/后处理的 SDK 分支。
- 未有：postprocess 回灌的验证标准和兼容性约束。

## 1.6 后续扩展建议

从后处理开始回灌时，建议优先明确以下边界：

1. `atomic/*.json` 到 C++ `AtomicResult` 的字段映射和缺省值策略。
2. `start_stage=postprocess` 是否完全跳过 `DmsPipeline`，还是复用部分 pipeline 包装后再投递 Fuse。
3. timestamp、frame_id、picName、原图可视化和 drawAtomicResult 的对齐规则。
4. 缺失 atomic、缺失 image、字段版本不兼容时的 fail-fast 行为。
5. x86 本地回灌与板端回灌是否共享同一 manifest 和 atomic schema。

## 1.7 验证状态

本记录只完成源码与 README 静态整理，未执行以下验证：

- `python_zmq/fillback_preprocess.py` 实际生成 dump。
- x86 回灌脚本运行。
- `J6M_PIC_VERSION` 板端构建与运行。
- `start_stage=postprocess` 运行态验证。

因此本文档状态保持 `draft`。
