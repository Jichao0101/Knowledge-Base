---
type: current_spec
status: verified
topic: DMS FaceID A核规格当前态
sources:
  - 02_Projects/DMS/09_FaceID/A核FaceID功能需求流程文档.md
updated_at: 2026-05-13
---

# 1 Inputs

| Signal | Meaning |
|---|---|
| `ADASFaceIDSysSta` | FaceID 系统状态，`2` 为激活，`1` 为待机 |
| `ADASFaceIDAtvSta` | FaceID 当前动作状态 |
| `VCU2FaceId` | R核下发给 A核的目标 Face ID |

# 2 Action Mapping

| `ADASFaceIDAtvSta` | Required behavior |
|---:|---|
| 1 | capture，录入当前人脸，生成或复用 Face ID |
| 2 | recognize，登录识别，与本地库比对 |
| 3 | unbind，按 `VCU2FaceId` 校验当前人脸与目标 Face ID |
| 4 | delete，删除 `VCU2FaceId` 指定数据；也覆盖绑定失败后的删除回滚 |
| 5 | check，查询 `VCU2FaceId` 是否存在 |
| 6 | cancel capture |
| 7 | cancel recognize |
| 8 | cancel unbind |
| 9 | factory reset，删除全部 FaceID 数据 |

# 3 Outputs

| Field | Meaning |
|---|---|
| `FaceId2DSCaptureStatus` | 录入结果 |
| `FaceId2DSRecognitionStatus` | 登录结果 |
| `FaceId2DSDeleteStatus` | 删除 / 恢复出厂设置结果 |
| `FaceId2DSCheckStatus` | check 查询结果 |
| `FaceId2DSUnbinedStatus` | 解绑结果 |
| `FaceId2VCU` | A核返回给 R核的 Face ID |
| `faultcode` / `statusCode` | 失败原因 |

# 4 Required Behaviors

- capture 成功后，本地特征库必须保存 Face ID 与特征映射。
- capture 遇到同一人已有特征时必须复用已有 Face ID。
- recognize 必须读取本地特征库并执行特征比对。
- delete 必须只删除 `VCU2FaceId` 指定 Face ID，失败时不得误删其他数据。
- factory reset 必须删除全部 FaceID 数据。
- check 不修改本地数据。
- unbind 只做目标 Face ID 的人脸比对，不删除本地特征。
- no-face / 姿态异常 / 遮挡等失败应写入对应 `faultcode`。

# 5 Verification Contract

最低单元测试覆盖：

- capture 新增并复用同一人 Face ID。
- recognize 匹配本地特征库。
- check/delete 使用指定 `VCU2FaceId`。
- unbind 成功后不删除本地特征。
- factory reset 删除全部本地特征。
- delete/check/factory reset 可在无当前帧 `AtomicResult` 时执行。
- `Init()` 能从已有本地存储恢复下一个生成 ID。
- no-face 返回失败状态和错误码。
