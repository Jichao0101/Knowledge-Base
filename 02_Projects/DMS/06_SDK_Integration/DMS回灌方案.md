--- 
type: project_record
status: draft
project: DMS
module: SDK Integration
summary: 记录 DMS SDK 回灌方案的统一结构；模型阶段回灌已接入 SDK camera callback 层，后处理阶段回灌应基于 main/main.cpp 可执行入口和 PIC 回灌模式扩展，复用 AlgorithmResultReplay 日志解析基础，但不直接进入相机输入或外部动态库框架路径。
sources:
  - /home/jichao/dms/README.md
  - /home/jichao/dms/python_zmq/fillback_preprocess.py
  - /home/jichao/dms/etc/fillback.json
  - /home/jichao/dms/main/main.cpp
  - /home/jichao/dms/main/patac_vision_sdk.cpp
  - /home/jichao/dms/main/CameraInputJpgTest.h
  - /home/jichao/dms/source/utils/camera_inst.cpp
  - /home/jichao/dms/main/DmsProcessEngine.cpp
  - /home/jichao/dms/source/pipeline/dms_pipeline.cpp
  - /home/jichao/dms/source/fuse_algos/fuse_algorithm.cpp
  - /home/jichao/dms/source/algorithm_result_replay/
  - /home/jichao/dms commit fcadf6f2a946d440d264a2d27340097ad1a2fcac
  - /home/jichao/dms commit 2e1f8c27ad6a681d08969310ccc72f54dd123a49
scope: DMS SDK 离线/板端回灌入口、数据集格式、模型阶段回灌调用链，以及后处理阶段回灌的可执行入口、PIC 构建隔离、日志 replay 输入、visualizer 验收和不可解析边界。
risks:
  - 本记录是后处理回灌的方案优化，不声明 postprocess runtime 已闭合。
  - `source/algorithm_result_replay` 为同事构建的日志 replay 模块，非必要不应修改；SDK 侧应以调用和构建隔离为主。
  - Face recognition / FaceID 依赖 R 核消息和模型结果，因隐私约束无法加载；方案不解析这些输入，后处理直接因缺少输入返回错误即可。
  - postprocess replay 缺少原始图像，不做原始输出与现输出对比，仅用同尺寸黑图承载 visualizer 显示。
updated_at: 2026-07-06
---

# 1 DMS 回灌方案

## 1.1 当前结论

DMS 回灌分为两条入口语义：

1. `start_stage=model`：已实现的模型阶段回灌。离线图片经 SDK camera callback 层进入 `DmsProcessEngine`、`DmsPipeline` 和 Fuse 主链路。
2. `start_stage=postprocess`：后处理阶段回灌方案。入口仍应在 `main/main.cpp` 的可执行程序回灌路径中分流，不走外部动态库框架路径；运行时通过 `FillbackContext::startStage` 区分 model / postprocess，非必要不新增宏。

`AlgorithmResultReplay` 的作用是读取后处理 replay 日志并恢复 `AlgorithmResult` / `AtomicResult` 相关输入。它单独构建静态库的目的不是成为通用依赖，而是只在 `J6M_PIC_VERSION` 这类图片/回灌构建中使用，避免普通相机输入路径引入日志解析、文件扫描或额外 CPU 占用。

## 1.2 模型阶段数据集结构

预处理脚本 `python_zmq/fillback_preprocess.py` 将 `video`、`bin` 或 `image_seq` 转换为统一 dump 目录：

| 路径 | 作用 |
|---|---|
| `images/<timestamp>.*` | 回灌图像，供 SDK camera callback 读取 |
| `atomic/<timestamp>.json` | 从 bin 解析出的历史 SDK 输出结果，主要作为后续 postprocess 扩展候选输入 |
| `manifest.csv` | 统一帧索引，字段为 `timestamp_us,frame_id,image_path,atomic_path` |

`manifest.csv` 是 model 阶段运行时索引入口。SDK 加载时要求表头固定，并要求 timestamp 严格递增；否则 `loadManifest()` 返回失败。

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

该设计的关键点是：model 阶段回灌入口位于 camera callback 层，模型和 Fuse 主链路基本复用生产路径。

## 1.4 配置约束

`fillback.json` 当前关键字段：

| 字段 | model 阶段语义 | postprocess 阶段语义 |
|---|---|---|
| `fillback` | 是否启用回灌 | 是否启用回灌 |
| `car_type` | 必须显式设置为 1-7，用于车型和相机类型选择 | 若后处理依赖车型语义，仍应显式设置 |
| `source_type` | README 中使用 `bin`、`image_seq`、`video` 作为预处理来源类型 | 只接受 log replay 来源 |
| `start_stage` | `model` | `postprocess` |
| `dumps_folder` | dump 目录根路径 | 不作为主输入 |
| `camera_intrinsic_path` | 回灌时使用的相机内参 JSON | 通常不作为主输入 |
| `log_fillback_path` | 不使用 | replay 日志目录 |
| `log_fillback_name` | 不使用 | 可选；为空时按目录发现日志 |

运行时分流应由 `FillbackContext` 携带配置结果后在 SDK 内判断，不应为了 model/postprocess 再扩展一组编译宏。编译宏只用于隔离构建产物，例如 `AlgorithmResultReplay` 只在 PIC 回灌构建中加入和链接。

## 1.5 后处理阶段回灌方案

后处理回灌应作为 `main/main.cpp` 可执行程序回灌入口下的一次性 replay 模式：

1. `main/main.cpp` 创建 `PatacVisionSdk` 并调用 `Init()`。
2. `PatacVisionSdk::Init()` 读取 `fillback.json`，若 `fillback=true && start_stage=postprocess`，则不加载 manifest、不初始化图片 camera callback 数据集、不进入相机取帧循环。
3. `main/main.cpp` 或 `PatacVisionSdk::RunDms()` 根据 `FillbackContext::startStage` 分流到 postprocess replay runner。
4. runner 调用 `AlgorithmResultReplayLoader` 读取 `log_fillback_path/name` 指定的日志，得到按顺序排列的 replay 帧。
5. 每帧取日志中可恢复的 `atomicResult` / `algorithmResult` 输入，直接驱动 Fuse/后处理链路。
6. 因 replay 缺少原始图像，runner 创建一张与 DMS 输入尺寸一致的黑色图像，填入 `AtomicResult::m_img` 或 visualizer 所需图像位置，仅用于显示承载，不作为模型输入。
7. 后处理结果不与原始输出做字段级 expected/actual 对比，只通过 visualizer 输出观察效果。
8. replay 结束后可执行程序退出，不应像 model 阶段一样无限循环取图。

该方案的核心边界是：postprocess replay 使用日志恢复的后处理输入，不走模型推理，不走相机输入，不占用普通相机路径 CPU；可视化用黑图只是显示载体，不改变算法输入来源。

## 1.6 AlgorithmResultReplay 边界

`fcadf6f2` 引入过 `AtomicResultReplay`，`2e1f8c27` 将 replay 方向收敛到 `source/algorithm_result_replay`，并通过 `[ALGORITHM_RESULT_Q1]` 日志记录 `AlgorithmResult::ToJsonWithoutImage()` 作为后处理 replay 来源。该方向更符合后处理回灌：日志中同时携带后处理结果对象和其关联的 atomic 输入，SDK 不需要从 `DmsProcessOutputData` 逆向拼装输入。

`AlgorithmResultReplay` 的设计边界：

- 作为独立静态库构建，便于在 PIC 回灌构建中按需链接。
- 不应默认加入普通相机输入构建路径；否则日志扫描、JSON 解析和 replay 依赖会污染生产相机路径。
- `source/algorithm_result_replay` 已由同事构建，后续 SDK 方案优先通过调用、配置、构建条件和 runner 适配来接入，非必要不修改该目录内部解析逻辑。
- 日志目录与文件名使用 `log_fillback_path` / `log_fillback_name`；`log_fillback_name` 为空时可由 replay 模块按目录规则发现日志。

## 1.7 Face Recognition / FaceID 边界

Face recognition 与 FaceID 不作为本轮 postprocess 回灌解析目标：

- face recognition 需要 R 核消息与模型结果共同参与。
- FaceID 同样依赖隐私敏感数据、模型输出和运行态状态。
- 这些输入因隐私因素无法加载，replay 方案不应伪造或补齐。
- 后处理链路运行到相关算法时，因输入缺失返回错误是可接受行为；runner 不应吞掉该错误，也不应把缺失输入伪装成通过。

因此方案不新增 face recognition / FaceID 的日志解析、字段补齐、结果对比或特殊绕过。若后续需要验证这部分，必须另行获得合法输入来源和隐私合规说明。

## 1.8 可视化与验收方式

后处理回灌的目标是辅助观察后处理行为，不是做原始输出与现输出的自动差分：

- 不需要对比原始输出和现有输出。
- 不需要记录 expected/actual 全量结果。
- 不需要比较 `header.timestamp_us`、`rollingCount` 或 replay 中的历史输出字段。
- visualizer 是主要观察出口。
- 因缺少原始图像，使用同尺寸黑色图像承载 visualizer 绘制结果。

黑图的尺寸来源优先级：

1. `fillback.json` 或已有 DMS 图像尺寸配置。
2. model 阶段可复用的输入尺寸设置逻辑。
3. 若尺寸不可确定，postprocess runner 应 fail-fast，不应使用隐式默认尺寸静默运行。

## 1.9 最小改造面

后续实现应控制在以下边界内：

| 文件/模块 | 改造意图 |
|---|---|
| `main/main.cpp` | 作为回灌可执行入口，根据 SDK 状态执行 postprocess replay 一次并退出 |
| `main/patac_vision_sdk.cpp/.h` | 读取 `fillback.json`，在 `FillbackContext` 中保留 `startStage`、`log_fillback_path/name`，按 ctx 分流 model/postprocess |
| `main/DmsProcessEngine.cpp/.h` | 增加同步 postprocess replay runner，直接调用 Fuse/后处理，不复用 image queue |
| `source/fuse_algos/fuse_algorithm.cpp` | 复用已有后处理算法执行和 visualizer；必要时提供无模型推理、可接受黑图显示载体的窄入口 |
| `source/CMakeLists.txt` / `main/CMakeLists.txt` | 只在 PIC 回灌构建中加入并链接 `AlgorithmResultReplay` 静态库 |
| `source/algorithm_result_replay` | 原则上不改；仅当 replay 模块自身 bug 阻断接入时再提出独立修改 |

不建议的改造：

- 不把 postprocess replay 接到外部动态库接口主路径。
- 不让普通相机输入构建默认依赖 `AlgorithmResultReplay`。
- 不为 model/postprocess 增加新的编译宏分叉。
- 不为了对比输出而引入一套 expected/actual diff 框架。
- 不伪造 face recognition / FaceID 输入。

## 1.10 验证状态

本记录完成以下静态方案整理：

- 读取 `fcadf6f2a946d440d264a2d27340097ad1a2fcac` 和 `2e1f8c27ad6a681d08969310ccc72f54dd123a49` 的相关 diff。
- 确认 replay 日志方向已从 `[ATOMIC_RESULT_Q1]` 收敛到 `[ALGORITHM_RESULT_Q1]`。
- 确认 `etc/fillback.json` 已出现 `log_fillback_path` / `log_fillback_name` 字段。
- 确认方案约束应以 `main/main.cpp` 回灌入口、PIC 构建隔离和 ctx 运行时分流为主。

仍未完成：

- 新分支上的 postprocess replay 代码实现。
- `J6M_PIC_VERSION` 构建验证。
- 板端 postprocess replay 运行验证。
- visualizer 黑图输出检查。
- Face recognition / FaceID 缺输入错误路径验证。

因此本文档状态保持 `draft`。
