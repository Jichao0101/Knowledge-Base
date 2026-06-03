---
type: project_current
status: draft
topic: DMS SDK Integration Validation
recoverability: created_but_not_fully_verified
single_pass_recoverable: false
updated_at: 2026-06-02
---

# DMS SDK 集成验证状态

## 1. 本轮验证边界

本轮仅执行源码静态调查和文档 recoverability 检查。按任务边界，未运行：

- 代码仓编译。
- 单元测试或集成测试。
- `sdk` 可执行程序。
- `libsdk.so` 外部调用。
- 板端验证。

## 2. 已确认的静态事实

| 事实 | 证据 |
|---|---|
| 常规 J6B QNX 默认脚本生成 `libsdk.so` | `/home/jichao/dms/scripts/compile_j6b.sh:22` |
| QNX 非 PIC 分支创建共享库 | `/home/jichao/dms/main/CMakeLists.txt:198` |
| QNX 8 + J6M PIC 回灌分支创建可执行程序 | `/home/jichao/dms/main/CMakeLists.txt:198` |
| 动态库接口包含初始化、输入、状态、回调和销毁 | `/home/jichao/dms/main/dms_process_interface.cpp:275` |
| 动态库初始化创建 buffer、Fuse、Pipeline 和任务 | `/home/jichao/dms/main/dms_process_interface.cpp:83` |
| Pipeline 根据配置创建模型 | `/home/jichao/dms/source/pipeline/dms_pipeline.cpp:24` |
| HBM 推理任务提交至 BPU | `/home/jichao/dms/source/ai_engine/ddk_manager_hbm.cpp:274` |
| VP 处理任务提交至 DSP | `/home/jichao/dms/source/utils/j6b_vp_processor.cpp:945` |

## 3. 静态可见风险

| 风险 | 证据 | 状态 |
|---|---|---|
| 动态库接口不是纯 C ABI | `/home/jichao/dms/main/dms_process_interface.hpp:59` | 待集成确认 |
| 初始化忽略 Fuse init 返回值 | `/home/jichao/dms/main/dms_process_interface.cpp:97` | 待运行态验证 |
| destroy 未等待工作任务退出 | `/home/jichao/dms/main/dms_process_interface.cpp:307` | 待运行态验证 |
| `detection=false` 时 Pipeline 仍固定使用 `DetModel` | `/home/jichao/dms/source/pipeline/dms_pipeline.cpp:177` | 配置约束 |
| QNN 加载失败可能退出进程 | `/home/jichao/dms/source/ai_engine/ddk_manager_qnn.cpp:635` | 待平台确认 |
| QNN 析构释放逻辑不可达 | `/home/jichao/dms/source/ai_engine/ddk_manager_qnn.cpp:807` | 待运行态验证 |
| HBM 错误路径资源释放不完整 | `/home/jichao/dms/source/ai_engine/ddk_manager_hbm.cpp:287` | 待运行态验证 |

## 4. 待确认项

- 实际交付目标使用的 CMake 宏组合。
- 部署环境是否始终设置 `VISION_ROOT_PATH`。
- 输出 callback 的线程上下文、耗时约束与重入约束。
- destroy 是否存在任务访问已释放对象的风险。
- QNN 资源释放路径是否导致持续泄漏。
- 固定创建 `J6bVpProcessor` 是否覆盖所有目标平台。
- `HandKeypointsModel` 与 `PoseEstimationModel` 的后端差异是否为设计意图。

## 5. 后续验证路径

以下命令和操作仅作为后续候选，本轮未执行：

1. 使用 `bash scripts/compile_j6b.sh` 验证常规 J6B 动态库构建。
2. 使用回灌宏组合构建 `sdk`，确认可执行入口与依赖。
3. 用最小外部调用方依次执行 initialize、callback register、image input、state switch 和 destroy。
4. 在目标平台确认 BPU 与 DSP 任务实际提交。
5. 重复 initialize/destroy，检查线程退出和资源释放。

## 6. Recoverability

```yaml
recoverability: created_but_not_fully_verified
single_pass_recoverable: false
```

五文件 current 组已经创建，但运行态验证未执行。当前不得升级为 `recoverable` 或 `single_pass_recoverable: true`。

