---
type: project_current
status: draft
topic: DMS SDK Integration Implementation
recoverability: created_but_not_fully_verified
single_pass_recoverable: false
updated_at: 2026-06-02
---

# 1 DMS SDK 集成实现映射

## 1.1 构建产物映射

| 机制 | 代码位置 | 说明 |
|---|---|---|
| 平台宏定义 | `/home/jichao/dms/CMakeLists.txt:3` | QNX、J6M、J6M PIC、J6M x86、J6B 2M、5M 与 IR camera |
| 动态库与可执行分支 | `/home/jichao/dms/main/CMakeLists.txt:198` | QNX 常规路径为 `libsdk.so`；PIC 或非 QNX 组合通常为 `sdk` |
| J6B 默认构建 | `/home/jichao/dms/scripts/compile_j6b.sh:22` | 默认生成并 strip `main/libsdk.so` |
| J6B 回灌构建 | `/home/jichao/dms/scripts/compile_j6b.sh:11` | 注释示例生成并 strip `main/sdk` |

## 1.2 动态库接口映射

| API | 代码位置 |
|---|---|
| 导出宏与声明 | `/home/jichao/dms/main/dms_process_interface.hpp:8` |
| `dms_process_initialize()` | `/home/jichao/dms/main/dms_process_interface.cpp:275` |
| `dms_process_destroy()` | `/home/jichao/dms/main/dms_process_interface.cpp:307` |
| `dms_process_input_ir_image_data()` | `/home/jichao/dms/main/dms_process_interface.cpp:316` |
| `dms_process_input_dp_can_data()` | `/home/jichao/dms/main/dms_process_interface.cpp:327` |
| `dms_process_input_ds_state_data()` | `/home/jichao/dms/main/dms_process_interface.cpp:336` |
| `dms_state_switch()` | `/home/jichao/dms/main/dms_process_interface.cpp:343` |
| `dms_process_output_register_output_data()` | `/home/jichao/dms/main/dms_process_interface.cpp:361` |
| `dms_process_output_register_ds_data()` | `/home/jichao/dms/main/dms_process_interface.cpp:371` |

## 1.3 初始化与处理链映射

| 机制 | 代码位置 | 说明 |
|---|---|---|
| 动态库初始化 | `/home/jichao/dms/main/dms_process_interface.cpp:83` | 创建 buffer、Fuse、Pipeline，并启动任务 |
| 图像入队 | `/home/jichao/dms/main/dms_process_interface.cpp:113` | 无空闲 buffer 时复用已填充旧帧 |
| Pipeline 消费 | `/home/jichao/dms/main/dms_process_interface.cpp:209` | 从队列取图并执行 Pipeline |
| Pipeline 初始化 | `/home/jichao/dms/source/pipeline/dms_pipeline.cpp:24` | 根据配置创建模型 |
| Pipeline 执行 | `/home/jichao/dms/source/pipeline/dms_pipeline.cpp:161` | 检测、跟踪、其他模型与结果投递 |
| Fuse 消费 | `/home/jichao/dms/source/fuse_algos/fuse_algorithm.cpp:194` | 消费原子结果并执行融合 |
| Fuse 初始化 | `/home/jichao/dms/source/fuse_algos/fuse_algorithm.cpp:545` | 根据配置创建融合算法 |
| 输出回调 | `/home/jichao/dms/source/utils/callback_manager.cpp:199` | 发布 SDK 输出 |

## 1.4 回灌路径映射

| 机制 | 代码位置 | 说明 |
|---|---|---|
| 可执行入口 | `/home/jichao/dms/main/main.cpp:33` | 仅在 QNX 8 与 J6M PIC 条件下定义 |
| SDK 初始化 | `/home/jichao/dms/main/main.cpp:100` | 注册取图函数与输出函数 |
| 多线程启动 | `/home/jichao/dms/main/main.cpp:114` | 调用 `sdk.Start()` |
| 单线程循环 | `/home/jichao/dms/main/main.cpp:127` | 重复调用 `sdk.RunDms()` |
| `PatacVisionSdk::Init()` | `/home/jichao/dms/main/patac_vision_sdk.cpp:288` | 包装旧式拉取路径初始化 |
| `SdkInterface::Init()` | `/home/jichao/dms/main/patac_vision_sdk.cpp:74` | 初始化旧式路径组件 |
| `SdkInterface::RunDms()` | `/home/jichao/dms/main/patac_vision_sdk.cpp:144` | 单线程执行链 |
| `SdkInterface::Start()` | `/home/jichao/dms/main/patac_vision_sdk.cpp:200` | 多线程任务启动 |

## 1.5 配置映射

| 机制 | 代码位置 |
|---|---|
| 资源根路径 | `/home/jichao/dms/include/utils/const_variable.h:15` |
| JSON 读取与解析 | `/home/jichao/dms/source/utils/read_json_config.cpp:28` |
| JSON getter 默认值 | `/home/jichao/dms/source/utils/read_json_config.cpp:156` |
| Pipeline 配置 | `/home/jichao/dms/etc/pipeline.json:1` |
| Fuse 配置 | `/home/jichao/dms/etc/fuse_algorithm.json` |

## 1.6 硬件加速映射

| 机制 | 代码位置 | 说明 |
|---|---|---|
| 模型后端选择示例 | `/home/jichao/dms/source/models/det_model.cpp:109` | J6 系列与 QNX 8 通常选择 HBM |
| HBM 初始化 | `/home/jichao/dms/source/ai_engine/ddk_manager_hbm.cpp:159` | 加载模型并申请 tensor buffer |
| BPU 任务提交 | `/home/jichao/dms/source/ai_engine/ddk_manager_hbm.cpp:274` | 提交至 `HB_UCP_BPU_CORE_ANY` |
| VP 工厂 | `/home/jichao/dms/source/utils/img_proc_interface.cpp:7` | 当前固定创建 `J6bVpProcessor` |
| DSP 任务提交 | `/home/jichao/dms/source/utils/j6b_vp_processor.cpp:945` | 提交至 `HB_UCP_DSP_CORE_0` |
| VP 内存释放 | `/home/jichao/dms/include/utils/vp_mem_base.h:22` | RAII 调用 `hbUCPFree()` |

## 1.7 已知未闭合点

- `DmsProcessInterface::Init()` 忽略 `m_fuseAlgo->Init()` 返回值：`main/dms_process_interface.cpp:97`。
- `dms_process_destroy()` 未等待工作任务退出：`main/dms_process_interface.cpp:307`。
- QNN 动态库加载失败可能调用 `std::exit()`：`source/ai_engine/ddk_manager_qnn.cpp:635`。
- `DdkManagerQnn` 析构函数开头直接返回：`source/ai_engine/ddk_manager_qnn.cpp:807`。
- HBM tensor 申请与 task handle 清理存在待验证路径：`source/ai_engine/ddk_manager_hbm.cpp:110`、`:287`。
- `HandKeypointsModel` 固定使用 QNN：`source/models/hand_keypoints_model.cpp:62`。
- `PoseEstimationModel` 的 HBM 条件未包含 `J6M_PIC_VERSION`：`source/models/pose_estimation_model.cpp:57`。

