---
type: current_overview
status: verified
topic: DMS FaceID A核当前状态
source_inventory:
  - 02_Projects/DMS/09_FaceID/A核FaceID功能需求流程文档.md
  - 02_Projects/DMS/09_FaceID/Current Maintenance Records/FaceID代码评估与修复记录_2026-05-13.md
  - /home/jichao/dms FaceID working tree
recoverability_status: partial
updated_at: 2026-05-13
---

# 1 Current State

FaceID A核侧当前以 R核下发的 `ADASFaceIDSysSta`、`ADASFaceIDAtvSta`、`VCU2FaceId` 为输入，执行录入、登录、解绑、删除、check、恢复出厂设置和取消流程。

当前代码已完成一次对照需求文档的修复：

- 录入：提取当前人脸特征，与本地库比对；同一人复用已有 Face ID，新用户生成新 Face ID 并保存。
- 登录：使用当前特征与本地 Face ID 特征库比对，不直接信任模型 `faceName`。
- 删除：按 `VCU2FaceId` 删除指定 Face ID。
- check：按 `VCU2FaceId` 查询指定 Face ID 是否存在。
- 解绑：按 `VCU2FaceId` 读取目标特征，比对通过后返回解绑成功，不删除本地特征。
- 恢复出厂设置：删除全部本地 FaceID 特征数据并重置生成 ID。
- 命令型流程：delete/check/factory reset 不要求当前帧 `AtomicResult` 存在。

# 2 Default Entry

默认读取顺序：

1. `overview_current.md`
2. `spec_current.md`
3. `design_current.md`
4. `implementation_current.md`
5. `validation_current.md`
6. `A核FaceID功能需求流程文档.md`
7. `Current Maintenance Records/FaceID代码评估与修复记录_2026-05-13.md`

# 3 Scope

范围内：

- A核 FaceID 状态映射。
- A核 FaceID 本地特征库读写。
- A核 FaceID 功能流程输出。
- FaceID 专项单元测试入口。

范围外：

- R核状态机实现。
- VCU 仪表展示逻辑。
- 板端验证。
- TTS 字段完整映射。
- FaceID 模型推理精度。

# 4 Current File Roles

- `design_current.md`：记录设计边界、模块关系和主要取舍。
- `spec_current.md`：记录状态、输入输出、行为契约和验证契约。
- `implementation_current.md`：记录代码入口、配置入口、spec-to-code 映射。
- `validation_current.md`：记录已验证事实、测试命令和剩余风险。

# 5 Recoverability

当前 current 组可恢复 FaceID A核侧的主要需求、实现入口和验证路径，但仍保留以下缺口：

- 文档第 9 节要求关键步骤之间重复 `JudgeState()`；当前实现仍以每次 `Process()` 入口判断为主。
- fail 状态值当前按代码和测试使用 `2`，需与 R核协议持续对齐。
- `face_id_params.json` 中 `feature_file` 是相对路径，部署工作目录需要明确。
