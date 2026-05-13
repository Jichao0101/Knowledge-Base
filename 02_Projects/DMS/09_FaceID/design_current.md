---
type: current_design
status: verified
topic: DMS FaceID A核设计当前态
sources:
  - 02_Projects/DMS/09_FaceID/A核FaceID功能需求流程文档.md
  - 02_Projects/DMS/09_FaceID/Current Maintenance Records/FaceID代码评估与修复记录_2026-05-13.md
updated_at: 2026-05-13
---

# 1 Design Goal

A核只根据 R核下发的 FaceID 状态和目标 ID 执行本地算法与数据操作，完成后把执行结果回传给 R核。

# 2 Non-goals

- A核不负责 User / VCU 请求编排。
- A核不负责 R核业务状态机。
- A核不负责 VCU 仪表显示和 TTS 完整提示链。
- 解绑不删除 A核本地 Face ID 特征数据。

# 3 Module Boundary

核心对象：

- R核输入：`ADASFaceIDSysSta`、`ADASFaceIDAtvSta`、`VCU2FaceId`。
- A核算法入口：`FaceIdAlgorithm::Process()`。
- 本地数据载体：`FaceIdStorage`。
- 输出载体：`FaceIdResult`，经 callback 映射到 DS 输出结构。

# 4 Key Decisions

- 录入时先查本地特征库，匹配已有用户则复用 Face ID，避免同一人重复生成多个 ID。
- 登录必须与 A核本地特征库比对，不能只用模型输出的 `faceName` 判定成功。
- 删除账号与恢复出厂设置分离：删除账号只删除指定 `VCU2FaceId`，恢复出厂设置删除全部。
- 解绑按 `VCU2FaceId` 指定目标特征做身份校验；A核不删除本地 Face ID。
- delete/check/factory reset 属于命令型流程，不依赖当前帧原子结果。

# 5 Known Design Risks

- 当前实现未在每个内部子步骤之间重新读取 R核最新状态；如果同一次 `Process()` 内存在异步取消信号，需要后续补充机制。
- 本地特征库使用简单二进制文件和 temp rename；未覆盖断电一致性或 fsync 级别保证。
- 相对路径 `feature_file` 依赖运行目录，部署时需明确。
