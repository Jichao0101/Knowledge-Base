---
type: project_current
status: draft
topic: DMS SDK Integration
lifecycle: creation
recoverability: created_but_not_fully_verified
single_pass_recoverable: false
source_repo: /home/jichao/dms
source_branch: feat/ljc/fatigue_params_0601
source_commit: dabc4ec2ec7e61b7172d89b48fe08b898bdcf096
updated_at: 2026-07-02
---

# 1 DMS SDK 集成概览

## 1.1 默认入口

本文档组是 DMS SDK 集成主题的默认恢复入口。建议按以下顺序读取：

1. `sdk_overview_current.md`
2. `sdk_design_current.md`
3. `sdk_spec_current.md`
4. `sdk_implementation_current.md`
5. `sdk_validation_current.md`

`DMS_SDK.md` 保留为补充来源，不再承担默认恢复入口职责。

## 1.2 范围

本文档组覆盖：

- SDK 的两条使用路径。
- 动态库集成接口的生命周期。
- 初始化、配置、Pipeline、Fuse 和输出链路。
- SDK 回灌入口、数据集格式和 start_stage 扩展边界。
- HBM/BPU 与 VP/DSP 硬件加速落点。
- 静态源码调查能够确认的事实、风险和待验证项。

本文档组不覆盖：

- 单个模型的算法原理和训练方案。
- 疲劳、分心等业务算法的完整规则。
- 板端部署操作手册。
- 尚未执行的运行态验证结论。

## 1.3 两条 SDK 使用路径

### 1.3.1 动态库外部集成路径

常规 J6B QNX 构建通过 `scripts/compile_j6b.sh` 生成 `build/main/libsdk.so`。外部调用方通过 `main/dms_process_interface.hpp` 中声明的接口初始化 SDK、输入图像和状态、注册回调并销毁实例。

### 1.3.2 可执行程序回灌路径

启用 `QNX_8_0_0_VERSION` 与 `J6M_PIC_VERSION` 时，构建目标为可执行文件 `build/main/sdk`。入口位于 `main/main.cpp`，内部通过 `PatacVisionSdk` 拉取图像并执行处理循环。

## 1.4 主真相源

| 类型 | 路径 | 用途 |
|---|---|---|
| 构建入口 | `/home/jichao/dms/CMakeLists.txt` | 平台宏和子目录组织 |
| SDK 构建规则 | `/home/jichao/dms/main/CMakeLists.txt` | 可执行程序与动态库产物分支 |
| J6B 构建脚本 | `/home/jichao/dms/scripts/compile_j6b.sh` | 默认 J6B 动态库构建命令和回灌分支 |
| 动态库接口 | `/home/jichao/dms/main/dms_process_interface.hpp` | 对外接口声明 |
| 动态库实现 | `/home/jichao/dms/main/dms_process_interface.cpp` | 初始化、入队、线程、状态和销毁 |
| 回灌入口 | `/home/jichao/dms/main/main.cpp` | 可执行程序入口 |
| 回灌方案记录 | [[02_Projects/DMS/06_SDK_Integration/DMS回灌方案]] | 统一记录模型阶段回灌已实现链路，以及 postprocess 阶段回灌预留边界 |
| Pipeline | `/home/jichao/dms/source/pipeline/dms_pipeline.cpp` | 模型初始化与逐帧调度 |
| Fuse | `/home/jichao/dms/source/fuse_algos/fuse_algorithm.cpp` | 融合算法初始化、消费和输出 |
| 补充来源 | `DMS_SDK.md` | 目录背景、buffer manager 和 protobuf 说明 |

## 1.5 当前状态

- 本轮从源码静态证据创建 current 文档组。
- 2026-07-02 新增 [[02_Projects/DMS/06_SDK_Integration/DMS回灌方案]]，记录 `start_stage=model` 已实现路径和 `start_stage=postprocess` 未支持边界。
- 未执行编译、测试、可执行程序或板端验证。
- 本轮只能声明 `created_but_not_fully_verified`。
- 在完成整组文档复核和运行态验证前，不得设置 `single_pass_recoverable: true`。
