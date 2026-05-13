---
type: current_implementation
status: verified
topic: DMS FaceID A核实现当前态
sources:
  - /home/jichao/dms working tree
  - 02_Projects/DMS/09_FaceID/Current Maintenance Records/FaceID代码评估与修复记录_2026-05-13.md
updated_at: 2026-05-13
---

# 1 Code Entry Points

| Purpose | Path |
|---|---|
| FaceID 算法入口 | `/home/jichao/dms/source/fuse_algos/face_id_algorithm.cpp` |
| FaceID 算法头文件 | `/home/jichao/dms/include/fuse_algos/face_id_algorithm.h` |
| FaceID 存储实现 | `/home/jichao/dms/source/fuse_algos/face_id_storage.cpp` |
| FaceID 存储头文件 | `/home/jichao/dms/include/fuse_algos/face_id_storage.h` |
| 输出结果结构 | `/home/jichao/dms/include/fuse_algos/algorithm_result.h` |
| DS 输出映射 | `/home/jichao/dms/source/utils/callback_manager.cpp` |
| 单元测试 | `/home/jichao/dms/test/unit_test_face_id_algorithm.cpp` |
| 测试目标入口 | `/home/jichao/dms/CMakeLists.txt` |

# 2 Config Entry

配置文件：

- `/home/jichao/dms/etc/face_id_params.json`

当前字段：

- `feature_file`: 本地特征库文件路径。
- `match_loss`: 特征比对阈值。

# 3 Spec-to-Code Mapping

| Spec behavior | Implementation |
|---|---|
| 状态判断 | `FaceIdAlgorithm::JudgeState()` |
| 动作分发 | `FaceIdAlgorithm::ExecuteAction()` |
| 录入 | `FaceIdAlgorithm::CaptureFace()` |
| 登录 | `FaceIdAlgorithm::RecognizeFace()` |
| 删除 | `FaceIdAlgorithm::DeleteFace()` |
| check | `FaceIdAlgorithm::CheckFace()` |
| 恢复出厂设置 | `FaceIdAlgorithm::ResetFace()` |
| 解绑 | `FaceIdAlgorithm::UnbindFace()` |
| 本地存储读写 | `FaceIdStorage::*` |
| ID 恢复 | `FaceIdAlgorithm::RecoverNextGeneratedFaceId()` |

# 4 Current Implementation Notes

- `FaceIdStorage` 使用二进制文件保存 `id -> feature vector` 映射。
- 写入采用临时文件加 rename。
- `Process()` 允许 `AtomicResult` 为空；无当前帧时，依赖人脸特征的 capture/recognize/unbind 会失败，但 delete/check/factory reset 可以执行。
- 专项测试目标为 `face_id_algorithm_test`，由 `BUILD_DMS_TESTS=ON` 启用，不启用历史 `gTestsdk`。

# 5 Known Gaps

- `FaceIdStorage::Unbind()` 仍保留旧接口，但当前 FaceID 算法解绑路径不再调用它。
- 取消流程当前以状态机入口判定为主，未实现同一次处理链路中每个关键步骤后的二次判定。
