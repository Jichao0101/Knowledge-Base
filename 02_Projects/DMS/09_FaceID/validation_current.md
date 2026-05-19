---
type: current_validation
status: verified
topic: DMS FaceID A核验证当前态
sources:
  - 02_Projects/DMS/09_FaceID/Current Maintenance Records/FaceID代码评估与修复记录_2026-05-13.md
  - 02_Projects/DMS/09_FaceID/Current Maintenance Records/FaceID_J6M_X86单测入口修正记录_2026-05-13.md
updated_at: 2026-05-13
---

# 1 Verified Facts

已通过单元测试验证：

- capture 新增 Face ID 并复用同一人已有 ID。
- recognize 使用本地特征库匹配。
- check 和 delete 使用 `VCU2FaceId`。
- unbind 比对指定 Face ID 且不删除本地特征。
- factory reset 删除全部已保存 Face ID。
- delete/check/factory reset 不需要当前帧 `AtomicResult`。
- `Init()` 可从已有存储恢复下一生成 ID。
- no-face 返回失败状态和错误码。

# 2 Validation Commands

```bash
cd /home/jichao/dms
cmake -S . -B build -DJ6M_X86_VERSION=ON
cmake --build build --target gTestsdk -j4
VISION_ROOT_PATH=/home/jichao/dms ./build/test/gTestsdk --gtest_filter='FaceIdAlgorithmTest.*'
```

# 3 Evidence

最近验证结果：

- `cmake -S . -B build -DJ6M_X86_VERSION=ON` passed。
- `gTestsdk` 尚未完成通过验证；当前阻塞为全 SDK 非 FaceID 编译问题。
- 旧专项 `face_id_algorithm_test` 路线不再作为最终验证入口。

# 4 Unverified Items

- 板端集成行为未验证。
- J6M_X86 下 `gTestsdk --gtest_filter='FaceIdAlgorithmTest.*'` 未完成通过验证。
- protobuf 头版本混用导致全 SDK 构建失败。
- `camera_shelter.cpp` 中 `rgbImg/croppedImg` 未声明导致全 SDK 构建失败。
- `det_model.cpp` 中 `m_VpMemRoiResizeY` 未声明导致全 SDK 构建失败。
- R核真实信号节奏未验证。
- 同一次 `Process()` 内异步取消信号未验证。
- 断电或文件系统异常下的存储一致性未验证。
- fail 状态值 `2` 仍需与 R核协议最终确认。

# 5 Next Check Path

后续若进入板端或集成验证，优先检查：

1. `face_id_params.json` 的 `feature_file` 实际落盘路径。
2. R核下发 delete/check/factory reset 时是否可能没有图像帧。
3. 取消流程是否可能在单次 A核处理链路中异步到达。
4. callback 输出字段是否满足 R核和 VCU 仪表需求。
