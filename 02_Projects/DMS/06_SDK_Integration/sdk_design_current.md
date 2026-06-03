---
type: project_current
status: draft
topic: DMS SDK Integration Design
recoverability: created_but_not_fully_verified
single_pass_recoverable: false
updated_at: 2026-06-02
---

# 1 DMS SDK 集成设计

## 1.1 设计目标

- 允许外部进程通过共享库集成 DMS 能力。
- 保留可执行程序回灌入口，用于图像拉取和处理循环场景。
- 将图像输入、模型 Pipeline、业务融合与回调输出分层。
- 在 J6 系列目标上使用 BPU 与 DSP 完成异构加速。

## 1.2 系统边界

```text
外部调用方或回灌主程序
  -> SDK 入口
  -> 图像 BufferManager
  -> DmsPipeline
  -> FuseAlgorithm
  -> CallBackManager
  -> 外部回调或主程序输出
```

动态库路径由外部调用方主动推送图像。回灌路径由 `main()` 通过回调主动拉取图像。两条路径最终都进入 Pipeline 和 Fuse，但入口模型、线程组织和生命周期控制不同。

## 1.3 动态库集成设计

动态库路径的入口是 `dms_process_initialize()`。初始化过程创建图像 buffer、融合算法、Pipeline，并启动 Pipeline 和 Fuse 工作任务。调用方通过 `dms_process_input_ir_image_data()` 推送图像，通过注册回调获取结果。

BufferManager 维护空闲池与已填充池。输入速度高于消费速度且无空闲 buffer 时，代码会从已填充队列取出旧帧并复用，以优先接收新帧。

## 1.4 回灌可执行程序设计

带 `J6M_PIC_VERSION` 的 QNX 8 构建生成 `sdk` 可执行程序。`main()` 初始化日志和车辆配置，将图像获取函数与输出函数传入 `PatacVisionSdk::Init()`。

- `Multi_Thread`：启动取图、Pipeline 和 Fuse 任务。
- 非 `Multi_Thread`：主循环重复调用 `RunDms()`，按顺序完成取图、Pipeline、Fuse 和结果清理。

## 1.5 配置边界

- 运行资源路径以环境变量 `VISION_ROOT_PATH` 为根目录。
- Pipeline 根据 `etc/pipeline.json` 的模型开关创建模型。
- Fuse 根据 `etc/fuse_algorithm.json` 创建业务融合算法。
- JSON 配置由 `ReadJsonConfig` 读取；缺少字段时 getter 使用调用方提供的默认值。

## 1.6 硬件加速设计

### 1.6.1 模型推理

多数模型在 J6M、J6M PIC、J6M x86 或 QNX 8 条件下使用 `DdkManagerHbm`。HBM 初始化加载模型包、获取模型句柄并申请 tensor buffer，推理任务提交至 `HB_UCP_BPU_CORE_ANY`。

其他平台通常使用 `DdkManagerQnn`。例外项见 `sdk_validation_current.md`。

### 1.6.2 图像处理

图像处理通过统一接口创建 VP processor。当前工厂固定创建 `J6bVpProcessor`，并将 VP 任务提交至 `HB_UCP_DSP_CORE_0`。VP 内存对象通过 RAII 调用 `hbUCPFree()`。

## 1.7 已知设计风险

- 动态库导出函数使用 C linkage，但参数包含 C++ 引用、命名空间类型和 `std::vector`，不是纯 C ABI。
- 动态库销毁路径设置停止标志后立即删除对象，线程退出时序需要运行态确认。
- Pipeline 固定使用 `DetModel`，因此 `detection=false` 不是受支持配置。
- VP processor 固定为 `J6bVpProcessor` 是否适用于所有目标平台，仍需确认。

