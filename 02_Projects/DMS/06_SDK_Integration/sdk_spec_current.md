---
type: project_current
status: draft
topic: DMS SDK Integration Specification
recoverability: created_but_not_fully_verified
single_pass_recoverable: false
updated_at: 2026-06-02
---

# DMS SDK 集成规格

## 1. 动态库接口生命周期

推荐外部调用顺序：

```text
dms_process_initialize(camera_info)
  -> 注册 output callback
  -> 可选注册 DS callback
  -> 可选输入 CAN 与 DS 状态
  -> 重复输入 IR 图像
  -> 可选切换 IDLE / ON
  -> dms_process_destroy(handle)
```

| 阶段 | API | 说明 |
|---|---|---|
| 初始化 | `dms_process_initialize()` | 创建实例并调用 `DmsProcessInterface::Init()` |
| 销毁 | `dms_process_destroy()` | 设置停止标志并删除实例 |
| 图像输入 | `dms_process_input_ir_image_data()` | 将图像写入有界 buffer 队列 |
| CAN 输入 | `dms_process_input_dp_can_data()` | 输入车辆 CAN 数据 |
| DS 状态输入 | `dms_process_input_ds_state_data()` | 输入 DS 状态 |
| 状态切换 | `dms_state_switch()` | 切换 SDK 状态 |
| 完整结果回调 | `dms_process_output_register_output_data()` | 注册完整输出回调 |
| DS 结果回调 | `dms_process_output_register_ds_data()` | 注册 DS 输出回调 |

## 2. 初始化契约

动态库初始化应满足：

1. 部署环境提供有效的 `VISION_ROOT_PATH`。
2. 根目录下存在所需 `etc/` 配置与模型资源。
3. `camera_info` 提供图像尺寸。
4. 外部调用方保存并使用初始化返回的 handle。
5. 外部调用方使用与 SDK ABI 兼容的 C++ 工具链。

`DmsProcessInterface::Init()` 的静态执行顺序：

```text
BufferManager(camera dimensions)
  -> FuseAlgosFactory::CreateFuseAlgos()
  -> FuseAlgorithm::Init()
  -> DmsPipeline::Init()
  -> Start()
```

## 3. 图像处理契约

动态库路径：

```text
dms_process_input_ir_image_data()
  -> PushImage()
  -> filled buffer queue
  -> RunDmsThread()
  -> DmsPipeline::Run()
  -> SubscribePipelineResults()
  -> FuseAlgorithm::Run()
  -> CallBackManager::PublishResult()
  -> 外部 callback
```

Pipeline 的静态执行顺序：

```text
复制原图
  -> 可选遮挡检测
  -> DetModel
  -> tracking
  -> head-position-to-face
  -> 其他模型
  -> 投递 Fuse 队列
```

普通模式运行全部非检测模型。face-id 模式仅运行 face quality、face recognition 和 landmark。

## 4. 回调契约

- 输出 callback 和对应 opaque 均非空时才触发回调。
- 调用方应在持续输入图像前注册所需回调。
- 当前文档未确认 callback 线程上下文、调用耗时约束和重入约束，集成方需要补充验证。

## 5. 构建契约

| 场景 | 关键宏 | 产物 |
|---|---|---|
| 常规 J6B QNX 动态库 | `QNX_VERSION=ON`, `QNX_8_0_0_VERSION=ON` | `build/main/libsdk.so` |
| J6B 回灌 | 额外启用 `J6M_PIC_VERSION=ON` | `build/main/sdk` |

实际交付使用的完整宏组合必须由具体集成环境确认。

## 6. 验证契约

当前文档组只基于静态源码证据。发布或集成前至少需要确认：

- `libsdk.so` 的实际构建命令与依赖。
- `sdk` 回灌可执行程序的实际构建和启动方式。
- `VISION_ROOT_PATH` 与配置资源完整性。
- 初始化失败传播。
- 回调触发与线程行为。
- destroy 后线程退出与资源释放。
- BPU 和 DSP 加速路径在目标平台上的实际生效情况。

