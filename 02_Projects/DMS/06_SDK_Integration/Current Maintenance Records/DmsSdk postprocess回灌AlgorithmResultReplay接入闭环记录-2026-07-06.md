---
type: current_maintenance_record
status: pending_review
topic: DMS SDK Integration
lifecycle: patch
action: postprocess_fillback_algorithm_result_replay_writeback
recoverability: created_but_not_fully_verified
single_pass_recoverable: false
source_repo: /home/jichao/dms
source_branch: feat/ljc/fillback_0702
source_commit: 7df460b44f981eb7c71e8a7755069f9279922370
updated_at: 2026-07-06
---

# 1 DMS SDK postprocess 回灌 AlgorithmResultReplay 接入闭环记录

## 1.1 目标

将 `start_stage=postprocess` 回灌从 2026-07-02 的 `DmsProcessOutputData` vector 骨干收敛到当前实现：J6M_PIC 回灌模式下读取 `AlgorithmResultReplay` 日志，直接消费 `AlgorithmResult::m_atomicRes` 作为后处理输入，并用 `AlgorithmResult` 中已有后处理结果做 selected-field 对比。

## 1.2 授权边界

- 允许读取代码仓：`/home/jichao/dms/**`
- 允许读取和写入项目区：`02_Projects/DMS/06_SDK_Integration/**`
- 本轮只同步知识库维护记录，不修改 DMS 业务代码。
- 本轮不声明板端 runtime 回灌已验证。

## 1.3 Source Inventory

### 1.3.1 代码仓状态

```yaml
branch: feat/ljc/fillback_0702
commit: 7df460b44f981eb7c71e8a7755069f9279922370
head_subject: add fillback in postprocess
dirty_files:
  - main/CMakeLists.txt
  - main/DmsProcessEngine.cpp
  - main/DmsProcessEngine.h
  - main/patac_vision_sdk.cpp
  - main/postprocess_fillback.cpp
  - main/postprocess_fillback.h
  - source/CMakeLists.txt
```

### 1.3.2 项目区来源

- `02_Projects/DMS/06_SDK_Integration/DMS回灌方案.md`

该方案文档已更新为 2026-07-06 结论：postprocess 回灌不再逆向适配 `DmsProcessOutputData`，而是通过 `AlgorithmResultReplayLoader` 读取 `AlgorithmResult` 序列。

## 1.4 实现同步内容

| 文件 | 当前实现事实 |
|---|---|
| `main/postprocess_fillback.cpp/.h` | `LoadPostprocessFillbackData()` 改为读取 `etc/fillback.json` 并返回 `std::vector<std::shared_ptr<FuseAlgosDomain::AlgorithmResult>>`；非 `QNX_8_0_0_VERSION && J6M_PIC_VERSION` 分支 fail-fast；删除 `DmsProcessOutputData -> AtomicResult` 逆向 adapter |
| `main/DmsProcessEngine.cpp/.h` | `RunPostprocessFillback()` 改为消费 `AlgorithmResult` 序列，逐帧校验 `m_atomicRes`，调用 Fuse 后处理窄入口，并在 selected-field diff 非零时返回失败 |
| `main/patac_vision_sdk.cpp` | postprocess 回灌读取 `VISION_ROOT_PATH + "/etc/fillback.json"`；配置校验字段改为 `log_fillback_path` |
| `source/CMakeLists.txt` | `algorithm_result_replay` 子目录仅在 `QNX_8_0_0_VERSION && J6M_PIC_VERSION` 下加入构建 |
| `main/CMakeLists.txt` | `AlgorithmResultReplay` 仅链接到 `QNX_8_0_0_VERSION && J6M_PIC_VERSION` 的 `sdk` 分支 |

## 1.5 Superseded 结论

本轮替代 `DMS回灌方案.md` 中 2026-07-02 骨干的以下内容：

- `LoadPostprocessFillbackData(log_path)` 返回 `std::vector<FuseAlgosDomain::DmsProcessOutputData>`。
- SDK 侧构造 `DmsProcessOutputData -> AtomicResult` 逆向 adapter。
- postprocess 回灌记录 expected/actual 全量结果。
- 通过 `log_path` 直接指向单个日志文件。

新的当前边界为：

- 通过 `fillback.json` 和 `log_fillback_path` 进入 `AlgorithmResultReplayLoader`。
- replay 输入必须提供有效 `AlgorithmResult` 与 `m_atomicRes`。
- 对比范围限制在 fatigue、smoking、phone call、distraction gaze field 和 camera occlusion 等 selected fields。
- 不比较 timestamp、rolling count、图像字段、face recognition 或 face id。

## 1.6 验证证据

已记录的验证：

- `bash scripts/compile_j6b.sh`：通过，`build/main/sdk` 链接成功。
- `cmake -S /home/jichao/dms -B /tmp/dms-nopic-config-check2`：通过，非 PIC 配置阶段未强制构建或链接 `AlgorithmResultReplay`。

本轮知识库写回验证：

- 写入前门禁：`minimal-apply-check` 返回 `allow`。

## 1.7 未闭合项

- 尚未执行 `J6M_PIC_VERSION` 板端 runtime 回灌。
- 尚未执行真实 postprocess log runtime 回灌验证。
- `AlgorithmResultReplay` 中既有 face recognition / face id 解析属于历史实现；本轮 SDK 适配层不新增、不比较、不专门屏蔽 face recognition / face id。
- 当前记录只同步项目维护事实，不改变 SDK current 文档组 recoverability。

## 1.8 Writeback Decision

```yaml
candidate_created: false
source_notes_created: false
promoted_to_knowledge: false
current_group_updated: false
project_record_created: true
single_pass_recoverable: false
```

本轮只新增 `02_Projects/` 项目维护记录，不写入 `01_Knowledge/` 正式知识区，不提升 evidence level，不声明 `single_pass_recoverable: true`。
