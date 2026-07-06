---
type: current_maintenance_record
status: pending_review
topic: DMS SDK Integration
lifecycle: creation
action: creation_with_source_extraction
recoverability: created_but_not_fully_verified
single_pass_recoverable: false
updated_at: 2026-06-02
---

# 1 DMS SDK current 文档组创建记录

## 1.1 目标

根据 `/home/jichao/dms` 代码仓静态证据，为 SDK 集成主题建立可恢复的 current 文档组，补充 SDK 双调用路径、初始化、配置、Pipeline/Fuse、硬件加速和风险边界。

## 1.2 授权边界

- 允许读取代码仓：`/home/jichao/dms/**`
- 允许读取知识库 lifecycle 规则：`01_Knowledge/Agent Workflow/Current文档组生命周期维护与可恢复性规则.md`
- 允许读取和写入项目区：`02_Projects/DMS/06_SDK_Integration/**`
- 禁止修改代码。
- 禁止运行测试、编译、可执行程序和板端验证。

## 1.3 Source Inventory

### 1.3.1 项目区来源

- `DMS_SDK.md`

处理结论：保留为 `retained_source`。该文档包含目录背景、buffer manager 和 protobuf 说明，但不承担默认恢复入口职责。

### 1.3.2 代码仓静态证据

- `/home/jichao/dms/CMakeLists.txt`
- `/home/jichao/dms/main/CMakeLists.txt`
- `/home/jichao/dms/scripts/compile_j6b.sh`
- `/home/jichao/dms/main/main.cpp`
- `/home/jichao/dms/main/patac_vision_sdk.cpp`
- `/home/jichao/dms/main/dms_process_interface.hpp`
- `/home/jichao/dms/main/dms_process_interface.cpp`
- `/home/jichao/dms/source/pipeline/dms_pipeline.cpp`
- `/home/jichao/dms/source/fuse_algos/fuse_algorithm.cpp`
- `/home/jichao/dms/source/utils/callback_manager.cpp`
- `/home/jichao/dms/source/ai_engine/ddk_manager_hbm.cpp`
- `/home/jichao/dms/source/ai_engine/ddk_manager_qnn.cpp`
- `/home/jichao/dms/source/utils/img_proc_interface.cpp`
- `/home/jichao/dms/source/utils/j6b_vp_processor.cpp`

代码仓调查基线：

```yaml
branch: feat/ljc/fatigue_params_0601
commit: dabc4ec2ec7e61b7172d89b48fe08b898bdcf096
pre_existing_dirty_file:
  - source/fuse_algos/fatigue_algorithm.cpp
```

本轮没有修改代码仓，也没有读取已有未提交修改的内容。

## 1.4 Lifecycle Classification

```yaml
lifecycle_classification: creation
detail: creation_with_source_extraction
```

依据：

- SDK 集成主题原先只有 `DMS_SDK.md`。
- 原先不存在 `overview_current`、`design_current`、`spec_current`、`implementation_current`、`validation_current`。
- 没有 `structural_unrecoverable` 证据，不升级为 rewrite。

## 1.5 创建文件

- `sdk_overview_current.md`
- `sdk_design_current.md`
- `sdk_spec_current.md`
- `sdk_implementation_current.md`
- `sdk_validation_current.md`

## 1.6 Evidence Assessment

静态源码证据足以支撑：

- 常规 J6B QNX `libsdk.so + dms_process_interface` 外部调用路径。
- `J6M_PIC_VERSION` 回灌 `sdk` 可执行路径。
- 初始化、buffer、Pipeline、Fuse 和 callback 主链路。
- `VISION_ROOT_PATH`、Pipeline 配置和 Fuse 配置入口。
- HBM/BPU 与 VP/DSP 硬件加速落点。
- 若干静态可见风险。

静态源码证据不足以支撑：

- 实际交付环境宏组合。
- 部署环境变量完整性。
- destroy 线程退出安全性。
- 资源泄漏的运行态影响。
- BPU 与 DSP 在目标平台上的实际运行结果。

## 1.7 Recoverability Verification

当前结论：

```yaml
recoverability: created_but_not_fully_verified
single_pass_recoverable: false
```

原因：

- 已创建五文件 current 组合，并分离 overview、design、spec、implementation 和 validation 职责。
- 已补充精确源码路径、接口契约、静态证据和风险。
- 本轮按任务边界未执行运行态验证。
- 当前不得声明 `recoverable`，也不得设置 `single_pass_recoverable: true`。

## 1.8 Writeback Decision

```yaml
candidate_created: true
source_notes_created: false
promoted_to_knowledge: false
legacy_three_side_sync_dependency: false
```

本轮只写入 `02_Projects/` 项目区，不写入 `01_Knowledge/` 正式知识区。

