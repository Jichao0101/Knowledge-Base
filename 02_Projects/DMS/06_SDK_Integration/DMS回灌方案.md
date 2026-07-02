---
type: project_record
status: draft
project: DMS
module: SDK Integration
summary: 记录 DMS SDK 回灌方案的统一结构，当前已实现从模型阶段开始回灌；后处理阶段回灌方案收敛为 log-only 数据来源、vector 消费契约和现有代码最小改造骨干。
sources:
  - /home/jichao/dms/README.md
  - /home/jichao/dms/python_zmq/fillback_preprocess.py
  - /home/jichao/dms/etc/fillback.json
  - /home/jichao/dms/main/patac_vision_sdk.cpp
  - /home/jichao/dms/main/patac_vision_sdk.h
  - /home/jichao/dms/main/postprocess_fillback.cpp
  - /home/jichao/dms/main/postprocess_fillback.h
  - /home/jichao/dms/main/CameraInputJpgTest.h
  - /home/jichao/dms/source/utils/camera_inst.cpp
  - /home/jichao/dms/include/utils/camera_inst.h
  - /home/jichao/dms/main/DmsProcessEngine.cpp
  - /home/jichao/dms/main/DmsProcessEngine.h
  - /home/jichao/dms/source/pipeline/dms_pipeline.cpp
  - /home/jichao/dms/include/models/atomic_result.h
  - /home/jichao/dms/include/fuse_algos/base_algorithm.h
  - /home/jichao/dms/include/fuse_algos/fuse_algorithm.h
  - /home/jichao/dms/source/fuse_algos/fuse_algorithm.cpp
  - /home/jichao/dms/include/fuse_algos/algorithm_result.h
  - /home/jichao/dms/include/fuse_algos/serialize_result.h
  - /home/jichao/dms/main/dms_data_types.hpp
  - /home/jichao/dms/python_zmq/sdk_output.proto
scope: DMS SDK 离线/板端回灌入口、数据集格式、模型阶段回灌调用链，以及后处理阶段回灌的 vector 消费契约、log-only 数据来源约束和代码骨干。
risks:
  - 2026-07-02 已完成 postprocess 回灌代码骨干并通过 J6B 编译；但未执行板端 runtime 回灌。
  - `LoadPostprocessFillbackData(log_path)` 的具体日志解析格式仍未由当前源码事实确认；当前实现保留 log-only helper 入口并 fail-fast，不能把 postprocess 回灌写成端到端已可运行。
  - 现有 `FuseAlgorithm::Run(std::shared_ptr<AtomicResult>)` 同时承担后处理、可视化、protobuf/ZMQ/UDP 输出，并会在空图像时返回失败；postprocess 回灌需要新增窄入口，不能直接复用该函数作为最终方案。
updated_at: 2026-07-02
---

# 1 DMS 回灌方案

## 1.1 当前结论

DMS 回灌方案分为两个入口：`start_stage=model` 使用 dump/manifest 图片数据集接入 SDK camera callback 层；`start_stage=postprocess` 按优化方案只接受 log 日志经 helper 还原出的 `std::vector<FuseAlgosDomain::DmsProcessOutputData>`。当前代码链路已支持模型阶段回灌：SDK 读取离线图片，构造 `ImageData`，再进入原有 `DmsProcessEngine`、`DmsPipeline` 和 Fuse 链路。

README 中同时保留 `start_stage=postprocess` 的配置语义，但标注“目前不支持”。因此本文档把方案命名为“DMS 回灌方案”，不限定为原始图像回灌；后续从后处理开始回灌应作为同一方案下的扩展，而不是另起一个只面向图片输入的方案。

## 1.2 模型阶段数据集结构

模型阶段回灌使用 dump/manifest 图片数据集。预处理脚本 `python_zmq/fillback_preprocess.py` 将 `video`、`bin` 或 `image_seq` 转换为统一 dump 目录：

| 路径 | 作用 |
|---|---|
| `images/<timestamp>.*` | 回灌图像，供 SDK camera callback 读取 |
| `manifest.csv` | 模型阶段回灌帧索引，运行时使用 timestamp、frame_id 和 image_path 定位图像 |

`manifest.csv` 是模型阶段运行时索引入口。SDK 加载时要求表头固定，并要求 timestamp 严格递增；否则 `loadManifest()` 返回失败。postprocess 阶段不以 dump、manifest 或 atomic JSON 作为主输入，统一走 log 日志到 `std::vector<FuseAlgosDomain::DmsProcessOutputData>` 的 helper 契约。

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

`fillback.json` 当前按 `start_stage` 分流理解：

| 字段 | model 阶段语义 | postprocess 阶段语义 |
|---|---|---|
| `fillback` | 是否启用回灌 | 是否启用回灌 |
| `car_type` | 必须显式设置为 1-7，用于车型和相机类型选择 | 若后处理依赖车型语义，仍应显式设置 |
| `source_type` | `bin`、`image_seq`、`video` 等预处理来源类型 | 只能为 `log` |
| `start_stage` | `model` | `postprocess` |
| `dumps_folder` | dump 目录根路径 | 不作为 postprocess 主输入 |
| `log_path` | 不使用 | 指向法规允许的数据来源日志 |
| `camera_intrinsic_path` | 回灌时使用的相机内参 JSON | 通常不作为 postprocess 主输入，除非后处理显式依赖 |

代码对 `car_type` 做合法性检查，避免静默继承默认车型。回灌开启时还会从 `camera_intrinsic_path` 初始化相机内参，避免离线图像与车型/内参不一致时无提示跑偏。

## 1.5 后处理阶段回灌优化方案

后处理阶段回灌应与模型阶段图片回灌分流。优化后的边界是：日志生成与日志解析细节不进入 SDK 回灌主流程，SDK 只依赖 helper 返回的结构化帧序列。当前代码里存在多个同名输出结构：`FuseAlgosDomain::DmsProcessOutputData` 是 `include/fuse_algos/serialize_result.h` 中的内部 SDK 输出结构，`::dms::DmsProcessOutputData` 是 `main/dms_data_types.hpp` 中的外部 callback 结构，protobuf 也有生成类型。postprocess 回灌骨干优先使用内部 `FuseAlgosDomain::DmsProcessOutputData`，因为 `FuseAlgorithm::buildSdkOutput()` 已以该结构承载模型原子结果和融合后处理输出。

该 helper 的内部实现不在本文展开，本文只约束其返回值语义：

```cpp
std::vector<FuseAlgosDomain::DmsProcessOutputData>
LoadPostprocessFillbackData(const std::string& logPath);
```

该 vector 是 postprocess 回灌的唯一输入集合。SDK 不关心 log 行格式、字段映射或 protobuf JSON 细节，只要求 vector 已按回灌顺序排列，且每帧能够提供后处理所需的模型原子结果和原始后处理输出。

## 1.6 postprocess 模式运行分流

建议 `fillback.json` 对 postprocess 模式采用独立语义：

| 字段 | 约束 |
|---|---|
| `fillback` | `true` |
| `start_stage` | `postprocess` |
| `source_type` | 只能为 `log` |
| `log_path` | 指向法规允许的数据来源日志 |

运行时分流：

1. `start_stage=model`：继续走现有图片/manifest/camera callback 回灌路径。
2. `start_stage=postprocess && source_type=log`：调用 helper 读取 `log_path`，得到 `std::vector<FuseAlgosDomain::DmsProcessOutputData>`。
3. SDK 按顺序消费 vector 中的帧数据。
4. 每帧提取模型原子结果作为后处理输入。
5. 每帧提取原始后处理输出作为 expected baseline。
6. 运行当前后处理/Fuse 链路得到 actual output。
7. 对比 expected 与 actual，并输出差异。

法规约束必须作为硬边界：postprocess 模式的数据来源只能是 log 日志，不接受 bin、protobuf 序列化文件、图片目录或 manifest 作为主输入。`protobuf` 类型只作为内存结构承载，不作为文件来源。

## 1.7 模块边界建议

建议将 postprocess 回灌拆成三个内部职责，而不是把逻辑混入现有图片回灌路径：

| 职责 | 边界 |
|---|---|
| Fillback loader | 调用 helper 并返回 vector；不解析日志格式细节 |
| Postprocess fillback runner | 顺序消费 vector，将模型原子结果灌入后处理 |
| Result comparator | 比较原始后处理输出和新输出，生成 diff |

该边界能保证模型阶段回灌路径继续复用 camera callback，postprocess 回灌路径只面对 `FuseAlgosDomain::DmsProcessOutputData` vector，不把日志解析、图片回灌和 Fuse 对比混成一个浅接口。

## 1.8 SDK 侧最小校验

由于日志生成和解析由 helper 封装，SDK 侧只做消费前的最小契约校验：

- vector 非空。
- 帧顺序可直接作为回灌顺序使用。
- timestamp 或 frame id 满足顺序消费要求。
- 每帧不依赖 `imageData`。
- 每帧包含 postprocess 所需模型原子结果。
- 每帧包含用于对比的原始后处理输出。

若任一条件不满足，应 fail-fast，不应静默跳帧继续。若后处理依赖历史状态，runner 必须顺序执行，不应并发打乱帧序。

## 1.9 待确认实现点

后续实现前仍需确认：

1. helper 是否能完整还原 `FuseAlgosDomain::DmsProcessOutputData` 中后处理所需的原子结果字段和 expected 输出字段。
2. `FuseAlgosDomain::DmsProcessOutputData` 是否完整包含重跑后处理所需的车辆状态、DP/CAN 状态、dmsMode、时间状态和历史状态初始化条件。
3. 对比输出的字段范围：全量输出对比，还是只对法规/业务关注字段对比。
4. 结果对比是否需要容忍浮点误差、时间戳重写和 rollingCount 重算。

## 1.10 基于现有代码的落地骨干

### 1.10.1 现有代码可复用点

| 代码位置 | 当前职责 | postprocess 回灌用法 |
|---|---|---|
| `PatacVisionSdk::Init()` | 读取 `fillback.json`，创建 `FillbackContext`，初始化 engine | 增加 `start_stage=postprocess` 分支，解析 `log_path`，不加载 manifest 和图片尺寸 |
| `UtilsDomain::FillbackContext` | 保存 `sourceType`、`startStage`、`dumpsFoler`、manifest 帧列表 | 增加 `logPath`，postprocess 模式只依赖 `sourceType/startStage/logPath` |
| `DmsProcessEngine` | 拥有 `m_fuseAlgo`、callback manager、pipeline 和 image queue | 增加同步 `RunPostprocessFillback()`，绕过 image queue 和 `DmsPipeline` |
| `FuseAlgorithm` | 拥有 `m_dmsAlgos`，按顺序执行各后处理算法，并用 `buildSdkOutput()` 生成 SDK 输出 | 增加只执行后处理和构造 actual output 的窄入口 |
| `buildSdkOutput()` | 将 `AtomicResult + AlgorithmResult` 组装成 `FuseAlgosDomain::DmsProcessOutputData` | 作为 actual output 的统一出口，避免重新写一套输出映射 |

### 1.10.2 配置与上下文骨干

`FillbackContext` 应补充 `logPath`，并在读取配置时对 postprocess 模式做硬校验：

```cpp
struct FillbackContext {
  bool fillback;
  uint8_t carType = 0;
  std::string sourceType;
  std::string startStage;
  std::string dumpsFoler;
  std::string cameraIntrinsicPath;
  std::string logPath;
  std::vector<FillbackFrame> frames;
};

int16_t getFillbackConfig(std::shared_ptr<FillbackContext> ctx) {
  // existing fields...
  ctx->logPath = conf->GetSTDStringValue("log_path", "");

  if (ctx->fillback && ctx->startStage == "postprocess") {
    if (ctx->sourceType != "log" || ctx->logPath.empty()) {
      LOGE("postprocess fillback only supports source_type=log and non-empty log_path");
      return FAIL;
    }
  }
  return SUCCESS;
}
```

`PatacVisionSdk::Init()` 当前在 `fillback=true` 时无条件 `loadManifest()` 并 `ConfigureFillbackImageSize()`。postprocess 分支必须先分流，避免把 log-only 回灌误判为图片 dump：

```cpp
if (m_fillbackCtx->fillback) {
  if (m_fillbackCtx->startStage == "postprocess") {
    // log-only 模式：不加载 manifest，不配置图片尺寸，不要求 camera_intrinsic_path。
  } else if (m_fillbackCtx->startStage == "model") {
    if (loadManifest(m_fillbackCtx->dumpsFoler + "/manifest.csv",
                     m_fillbackCtx->frames) != SUCCESS) {
      return FAIL;
    }
    if (ConfigureFillbackImageSize(m_fillbackCtx) != SUCCESS) {
      return FAIL;
    }
    // existing intrinsic init...
  } else {
    LOGE("unsupported fillback start_stage {}", m_fillbackCtx->startStage);
    return FAIL;
  }
}
```

### 1.10.3 SDK/Engine 入口骨干

postprocess 回灌不应启动 `RunGetCameraPic()`，也不应调用 `PushImage()`。建议由 `PatacVisionSdk` 增加同步入口，或在 `RunDms()` 里按 `startStage` 分流：

```cpp
int16_t PatacVisionSdk::RunPostprocessFillback() {
  if (!m_fillbackCtx || !m_fillbackCtx->fillback ||
      m_fillbackCtx->startStage != "postprocess") {
    return FAIL;
  }

  auto frames = LoadPostprocessFillbackData(m_fillbackCtx->logPath);
  if (frames.empty()) {
    LOGE("postprocess fillback: empty frames");
    return FAIL;
  }
  return m_engine.RunPostprocessFillback(frames);
}
```

`DmsProcessEngine` 作为 `m_fuseAlgo` 的持有者，应提供窄入口，不暴露内部指针，也不复用 image queue：

```cpp
class DmsProcessEngine {
 public:
  int16_t RunPostprocessFillback(
      const std::vector<FuseAlgosDomain::DmsProcessOutputData>& frames);
};

int16_t DmsProcessEngine::RunPostprocessFillback(
    const std::vector<FuseAlgosDomain::DmsProcessOutputData>& frames) {
  if (!m_fuseAlgo || frames.empty()) {
    return FAIL;
  }

  for (const auto& frame : frames) {
    auto atomic = BuildAtomicResultFromSdkOutput(frame);
    FuseAlgosDomain::DmsProcessOutputData actual{};
    if (m_fuseAlgo->RunPostprocessFillback(atomic, &actual) != SUCCESS) {
      return FAIL;
    }
    auto diff = ComparePostprocessOutput(frame, actual);
    EmitPostprocessFillbackDiff(diff);
  }
  return SUCCESS;
}
```

### 1.10.4 FuseAlgorithm 窄入口骨干

现有 `FuseAlgorithm::Run(shared_ptr<AtomicResult>)` 会先执行 `m_dmsAlgos`，随后要求 `res->m_img` 非空，再做可视化、protobuf 序列化、ZMQ 发送和 RT UDP 发送。postprocess 回灌的数据来源不能依赖图像，因此应新增只做后处理和输出构造的入口：

```cpp
class FuseAlgorithm {
 public:
  int8_t RunPostprocessFillback(
      const std::shared_ptr<ModelsDomain::AtomicResult>& atomicRes,
      DmsProcessOutputData* actualOutput);
};

int8_t FuseAlgorithm::RunPostprocessFillback(
    const std::shared_ptr<ModelsDomain::AtomicResult>& atomicRes,
    DmsProcessOutputData* actualOutput) {
  if (!atomicRes || !actualOutput) {
    return FAIL;
  }

  m_algoResult->Clear();
  m_algoResult->m_canData = m_canData;
  {
    std::lock_guard<std::mutex> lock(m_dpDataMutex);
    m_algoResult->m_dpData = m_dpData;
    m_algoResult->m_dpDataMutex = &m_dpDataMutex;
  }

  for (auto& algo : m_dmsAlgos) {
    if (algo->Process(atomicRes, m_algoResult) != SUCCESS) {
      return FAIL;
    }
  }

  return buildSdkOutput(*actualOutput, atomicRes, m_algoResult);
}
```

该入口必须不做以下事情：

- 不检查 `atomicRes->m_img.empty()`。
- 不调用 visualizer。
- 不调用 `DmsResultsToProto()`。
- 不执行 ZMQ/UDP 发送。
- 不发布生产 callback，除非后续明确需要把回灌结果走外部 callback 展示。

### 1.10.5 数据适配与对比骨干

建议把 `DmsProcessOutputData -> AtomicResult` 的逆向适配和结果对比放在独立 adapter 中，避免污染 `FuseAlgorithm`：

```cpp
std::shared_ptr<ModelsDomain::AtomicResult>
BuildAtomicResultFromSdkOutput(
    const FuseAlgosDomain::DmsProcessOutputData& frame);

PostprocessDiff ComparePostprocessOutput(
    const FuseAlgosDomain::DmsProcessOutputData& expected,
    const FuseAlgosDomain::DmsProcessOutputData& actual);
```

最小字段映射应与 `buildSdkOutput()` 保持反向一致：

| `DmsProcessOutputData` 字段 | `AtomicResult` 或 expected 用法 |
|---|---|
| `m_detResultMap` | 还原 `AtomicResult::m_detResultMap`，注意 `Rect` 到 `DetectBox` 的字段转换 |
| `m_landmarkResultMap` | 还原 `m_landmarkResultMap` |
| `m_faceTrackResultMap` | 还原 `m_faceTrackResultMap` |
| `m_leftHandTrackResultMap` / `m_rightHandTrackResultMap` | 还原左右手 track map |
| `m_humanTrackResultMap` | 还原 `m_bodyTrackResultMap` |
| `m_gazeResultMap` / `m_eyeStatusResultMap` | 还原 gaze 和 eye status 原子结果 |
| `m_handPoseResultMap` | 还原 `m_handPoseResultMap`，需要把整数 key 转回 `ModelsDomain::InstanceType` |
| `m_humanPoseResult` | 还原 human pose 原子结果 |
| `faceQualityResult` / `m_smkCallClsResult` | 还原 face quality 与 smoking/calling 分类原子结果 |
| `cameraOcclusion` | 作为 camera shelter 相关输入或 expected 字段，取决于后处理实现 |
| `fatigueFuseRes` / `distractionFuseRes` / `smokingFuseRes` / `phoneCallFuseRes` | expected 后处理输出 |
| `faceRecognitionResult` | expected FaceID/人脸识别输出；当前 `buildSdkOutput()` 由 `PopulateFusedFaceRecognitionResult()` 填充 |

比较逻辑不应直接比较 `header.timestamp_us` 和 `rollingCount`。当前 `buildSdkOutput()` 会用系统时间重写 `header.timestamp_us`，`rollingCount` 也由静态计数递增；postprocess 回灌应按 vector 顺序、日志帧号或 helper 提供的源标识对齐帧，再比较法规/业务关注字段。

### 1.10.6 最小文件改造面

按当前代码组织，最小改造面建议如下：

| 文件 | 改造内容 |
|---|---|
| `include/utils/camera_inst.h` | `FillbackContext` 增加 `logPath` |
| `main/patac_vision_sdk.cpp` | `getFillbackConfig()` 读取 `log_path`；`Init()` 按 `start_stage` 分流；新增或调用 `RunPostprocessFillback()` |
| `main/patac_vision_sdk.h` | 声明 SDK 内部 postprocess 回灌入口 |
| `main/DmsProcessEngine.h/.cpp` | 增加 `RunPostprocessFillback(vector<...>)` |
| `include/fuse_algos/fuse_algorithm.h` | 声明 `RunPostprocessFillback(AtomicResult, DmsProcessOutputData*)` |
| `source/fuse_algos/fuse_algorithm.cpp` | 复用 `m_dmsAlgos` 和 `buildSdkOutput()` 实现无图、无发送的后处理执行 |
| 新增 adapter 源文件 | 放置 `BuildAtomicResultFromSdkOutput()`、`ComparePostprocessOutput()` 和 diff 输出 |

该骨干把修改集中在 SDK fillback 分流、engine 窄入口、Fuse 窄入口和数据 adapter 四处，不改动 `DmsPipeline`、模型推理队列和 camera callback 路径。

## 1.11 2026-07-02 实现回写

本轮已按上述骨干完成代码接入，分支与版本为：

| 项 | 值 |
|---|---|
| repo | `/home/jichao/dms` |
| branch | `feat/ljc/fillback_0702` |
| commit | `59a164d6-dirty` |
| 验证命令 | `bash scripts/compile_j6b.sh` |
| 验证结果 | 通过，`build/main/sdk` 链接成功 |

实际改造点：

| 文件 | 实现内容 |
|---|---|
| `include/utils/camera_inst.h` | `FillbackContext` 增加 `logPath` |
| `main/patac_vision_sdk.cpp/.h` | 读取 `log_path`；`fillback && start_stage=postprocess` 时跳过 manifest、图片尺寸和相机内参加载；`Start()`/`RunDms()` 分流到同步 `RunPostprocessFillback()` |
| `main/DmsProcessEngine.cpp/.h` | 增加 `RunPostprocessFillback(vector<...>)`，顺序消费 helper 返回帧，构造 atomic，调用 Fuse 窄入口并输出 diff |
| `include/fuse_algos/fuse_algorithm.h` | 声明 `RunPostprocessFillback(const shared_ptr<AtomicResult>&, DmsProcessOutputData*)` |
| `source/fuse_algos/fuse_algorithm.cpp` | 新增无图、无 visualizer、无 protobuf/ZMQ/UDP 发送的后处理窄入口，复用 `m_dmsAlgos` 和 `buildSdkOutput()` 生成 actual output |
| `main/postprocess_fillback.cpp/.h` | 新增 log-only helper 入口、`DmsProcessOutputData -> AtomicResult` adapter 和 selected-field diff 输出 |

当前代码闭合了 SDK 侧的 postprocess 回灌执行骨干：配置分流、runner、Fuse 窄入口、adapter 和 diff 输出均已接入并参与 J6B 编译。仍未闭合的是日志解析本身：当前 `LoadPostprocessFillbackData()` 会打开 `log_path` 并 fail-fast 返回空 vector，等待日志格式和字段映射实现接入；因此运行态上若选择 `start_stage=postprocess`，在 parser 接入前会因空 frames 返回失败。

## 1.12 验证状态

本记录已完成以下验证：

- `bash scripts/compile_j6b.sh`：通过，`build/main/sdk` 链接成功。

仍未执行以下验证：

- `python_zmq/fillback_preprocess.py` 实际生成 dump。
- x86 回灌脚本运行。
- `J6M_PIC_VERSION` 板端运行。
- `start_stage=postprocess` runtime 回灌验证。
- 真实 `log.txt -> std::vector<FuseAlgosDomain::DmsProcessOutputData>` 解析验证。

因此本文档状态保持 `draft`。
