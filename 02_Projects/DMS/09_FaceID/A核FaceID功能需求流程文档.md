
# 1 文档目的

本文档基于 FaceID 功能时序流程图，整理 A核侧需求流程。

- A核不直接接收 `VCU FaceID Function Request`；
- A核只根据 R核下发的信号执行对应功能；
- A核执行完成后，将执行结果返回给 R核。


---

# 2 系统交互关系

## 2.1 交互对象

| 对象 | 职责 |
|---|---|
| User / VCU | 发起 FaceID 功能请求，例如录入、登录、取消、删除、恢复出厂设置、check、解绑等 |
| R核 | 接收 User / VCU 请求，控制 FaceID 功能状态，并向 A核下发执行状态 |
| A核 | FaceID 算法执行端，负责采集、识别、比对、保存、删除、查询、解绑等实际处理 |
| VCU仪表 | 展示 FaceID 功能状态、语音提示、失败原因等 |

---

## 2.2 信号链路说明

### 2.2.1 User / VCU 与 R核链路

信号包括：

``````text
VCU FaceID Function Request
Restore User Data Request
VCU FaceID Identifier Number Signal Group
``````

这些信号不经过 A核，A核不应直接依赖这些请求作为功能触发源。

---

### 2.2.2 R核与 A核链路

R核向 A核下发：

``````text
ADASFaceIDSysSta
ADASFaceIDAtySta
VCU2FaceId
``````

A核向 R核返回：

``````text
FaceId2DSCaptureStatus
FaceIdDSRecognitionStatus
FaceId2DSDeleteStatus
FaceId2DScheckStatus
FaceId2DSUnbinedStatus
FaceId2VCU
ADASFaceIDFuncRes
statusCode
``````

---

# 3 A核通用输入输出定义

## 3.1 A核输入信号

| 信号 | 来源 | 含义 |
|---|---|---|
| `ADASFaceIDSysSta` | R核 | FaceID 系统状态 |
| `ADASFaceIDAtySta` | R核 | FaceID 当前动作状态 |
| `VCU2FaceId` | R核 | R核转发给 A核的目标 Face ID |
| `VCU FaceID Identifier Number Signal Group` | R核间接转发 | 目标 Face ID 编号信号组，A核侧通常体现为 `VCU2FaceId` |

---

## 3.2 A核输出信号

| 信号 | 目标 | 含义 |
|---|---|---|
| `FaceId2DSCaptureStatus` | R核 | 录入结果状态 |
| `FaceIdDSRecognitionStatus` | R核 | 登录识别结果状态 |
| `FaceId2DSDeleteStatus` | R核 | 删除 / 恢复出厂设置结果状态 |
| `FaceId2DScheckStatus` | R核 | check 查询结果状态 |
| `FaceId2DSUnbinedStatus` | R核 | 解绑结果状态 |
| `FaceId2VCU` | R核 | A核返回给 R核的 Face ID 标识符 |
| `ADASFaceIDFuncRes` | R核 | FaceID 功能执行结果 |
| `statusCode` | R核 | 失败原因或状态码 |

---

# 4 状态值定义

## 4.1 FaceID 系统状态

| 信号                 |  取值 | 含义               |
| ------------------ | --: | ---------------- |
| `ADASFaceIDSysSta` | `2` | FaceID active 状态 |
| `ADASFaceIDSysSta` | `1` | 恢复出厂设置           |

---

## 4.2 FaceID 动作状态

| 信号 | 取值 | 功能含义 |
|---|---:|---|
| `ADASFaceIDAtySta` | `1` | 录入 capture |
| `ADASFaceIDAtySta` | `2` | 登录 recognition |
| `ADASFaceIDAtySta` | `3` | 解绑 / 数据同步相关识别比对 |
| `ADASFaceIDAtySta` | `4` | 删除账号 delete |
| `ADASFaceIDAtySta` | `5` | check 查询 |
| `ADASFaceIDAtySta` | `7` | 登录取消 / 录入取消，图中标注为 `RecognitionCancel` |
| `ADASFaceIDAtySta` | `8` | 解绑取消 |
| `ADASFaceIDAtySta` | `9` | 恢复出厂设置 |

---

# 5 A核通用处理原则

## 5.1 功能触发原则

A核不直接接收 User / VCU 的功能请求。

A核应根据 R核下发的状态组合触发功能：

``````text
ADASFaceIDSysSta == 2
ADASFaceIDAtySta == 对应功能值
``````


---

## 5.2 结果返回原则

A核执行完成后，应将结果返回给 R核。

结果至少包括：

``````text
成功 / 失败状态
Face ID 标识符
失败原因 statusCode
``````

具体输出信号根据功能不同而不同。

---

## 5.3 数据一致性原则

A核涉及本地 FaceID 数据操作，包括：

- 新增 Face ID；
- 复用已有 Face ID；
- 删除指定 Face ID；
- 删除全部 Face ID；
- 查询 Face ID；
- 解绑 Face ID；
- 清理临时数据。

因此需要保证：

1. 保存成功后，本地特征库与 Face ID 映射一致；
2. 删除成功后，本地不应残留对应 Face ID 特征；
3. 取消流程不应误保存或误删除正式数据；
4. 失败流程应清理临时数据；
5. 解绑流程需要明确是否删除本地特征数据。

---

# 6 功能流程需求

---

## 6.1 正常录入流程

### 6.1.1 触发条件

当 R核根据 User / VCU 的录入请求进入 FaceID active 状态后，向 A核下发：

``````text
ADASFaceIDSysSta == 2
ADASFaceIDAtySta == 1
``````

### 6.1.2 A核执行流程

A核检测到上述状态后，应进入录入流程。

A核应执行以下步骤：

1. 提取当前人脸特征；
2. 判断当前人脸是否与本地已保存 Face ID 属于同一人；
3. 若当前人脸与已保存 Face ID 属于同一人，则复用已有 Face ID；
4. 若当前人脸为新用户，则生成新的 Face ID；
5. 保存人脸特征与 Face ID 映射关系；
6. 返回录入结果。

### 6.1.3 A核输出

录入成功时，A核向 R核输出：

``````text
FaceId2DSCaptureStatus = success
FaceId2VCU = face_id
``````

录入失败时，A核向 R核输出：

``````text
FaceId2DSCaptureStatus = fail
statusCode = 失败原因
``````

### 6.1.4 失败处理

录入失败时，A核应清理本次录入过程中产生的临时数据，包括但不限于：

- 临时人脸图像；
- 临时特征；
- 尚未确认保存的 Face ID；
- 临时缓存状态。

### 6.1.5 关键约束

A核在录入时需要避免同一人重复生成多个 Face ID。

判断逻辑建议为：

``````text
当前人脸与本地已有 Face ID 比对
    ├─ 匹配已有用户：复用已有 Face ID
    └─ 未匹配已有用户：创建新的 Face ID
``````

### 6.1.6 绑定不成功

在绑定失败时，R核会返回 ADASFaceIDAtySta == 6，A核应该在收到后删除临时数据

## 6.2 录入取消流程

### 6.2.1 触发条件

在录入过程中，如果 R核向 A核下发取消状态：

``````text
ADASFaceIDSysSta == 2
ADASFaceIDAtySta == 7
``````

则 A核应终止当前录入流程。

### 6.2.2 A核执行流程

A核当前处于录入流程时，收到取消状态后，应执行：
1. 停止特征提取；
2. 终止当前录入流程；
3. 删除本次录入过程中产生的临时数据；
4. 不保存新的 Face ID；
5. 不更新正式 FaceID 特征库。

### 6.2.3 关键约束

录入取消只影响当前录入过程，不应影响已保存的 Face ID 数据。

---

## 6.3 正常登录流程

### 6.3.1 触发条件

当 R核根据 User / VCU 的登录请求进入 FaceID active 状态后，向 A核下发：

``````text
ADASFaceIDSysSta == 2
ADASFaceIDAtySta == 2
``````

### 6.3.2 A核执行流程

A核检测到上述状态后，应进入登录识别流程。

A核应执行：
1. 提取当前人脸特征；
2. 读取本地已保存 Face ID 特征库；
3. 将当前人脸特征与本地 Face ID 特征库进行比对；
4. 判断是否存在匹配 Face ID；
5. 返回识别结果。

### 6.3.3 A核输出

登录成功时，A核向 R核输出：

``````text
FaceIdDSRecognitionStatus = success
FaceId2VCU = matched_face_id
``````

登录失败时，A核向 R核输出：

``````text
FaceIdDSRecognitionStatus = fail
statusCode = 失败原因
``````

### 6.3.4 失败处理

登录失败时，A核不应删除本地已保存 Face ID 数据。

A核只应清理当前识别过程中的临时数据，例如：

- 当前帧缓存；
- 当前识别特征；
- 当前比对结果缓存。

---
### 6.3.5 绑定不成功

在绑定失败时==R核会返回== ，A核应该在收到后删除临时数据

---

## 6.4 取消登录流程

### 6.4.1 触发条件

在登录识别过程中，如果 R核向 A核下发：

``````text
ADASFaceIDSysSta == 2
ADASFaceIDAtySta == 7
``````

则 A核应终止当前登录流程。

### 6.4.2 A核执行流程

A核当前处于登录识别流程时，收到取消状态后，应执行：

1. 停止特征提取；
2. 停止人脸比对；
3. 终止当前登录流程；
4. 清理当前识别临时缓存；
5. 不返回登录成功。

### 6.4.3 关键约束

取消登录不应删除本地 Face ID 数据，也不应改变已有绑定关系。

---

## 6.5 请求删除账号流程

### 6.5.1 触发条件

当 R核根据 User / VCU 的删除请求向 A核下发：

``````text
ADASFaceIDSysSta == 2
ADASFaceIDAtySta == 4
VCU2FaceId = 待删除 Face ID
``````

A核应进入删除账号流程。

### 6.5.2 A核执行流程

A核应执行：

1. 接收 R核下发的 `VCU2FaceId`；
2. 根据 `VCU2FaceId` 查询本地 Face ID 数据；
3. 若 Face ID 存在，则删除对应人脸特征和映射关系；
4. 若 Face ID 不存在，则返回删除失败；
5. 删除完成后，建议再次查询确认该 Face ID 已不存在；
6. 返回删除结果。

### 6.5.3 A核输出

删除成功时，A核向 R核输出：

``````text
FaceId2DSDeleteStatus = success
FaceId2VCU = deleted_face_id
``````

删除失败时，A核向 R核输出：

``````text
FaceId2DSDeleteStatus = fail
statusCode = 失败原因
``````

### 6.5.4 关键约束

删除账号属于破坏性操作，A核需要保证：

1. 只删除 `VCU2FaceId` 指定的 Face ID；
2. 不误删其他 Face ID；
3. 删除成功后本地存储状态与返回状态一致；
4. 删除失败时保留原始数据，避免半删除状态。

---

## 6.6 恢复出厂设置流程

### 6.6.1 触发条件

当 R核根据恢复出厂设置请求向 A核下发：

``````text
ADASFaceIDAtySta == 9
ADASFaceIDSysSta == 2 或 1
``````

### 6.6.2 A核执行流程

A核进入恢复出厂设置流程后，应执行：

1. 停止当前 FaceID 相关流程；
2. 删除本地全部 Face ID；
3. 删除全部人脸特征数据；
4. 删除 Face ID 与用户账号的映射关系；
5. 清理 FaceID 临时缓存；
6. 清理未完成流程状态；
7. 返回恢复出厂设置结果。

### 6.6.3 A核输出

恢复成功时，A核向 R核输出：

``````text
FaceId2DSDeleteStatus = success
``````

恢复失败时，A核向 R核输出：

``````text
FaceId2DSDeleteStatus = fail
statusCode = 失败原因
``````

### 6.6.4 关键约束

恢复出厂设置与删除账号不同。

| 功能 | 操作范围 |
|---|---|
| 删除账号 | 删除指定 Face ID |
| 恢复出厂设置 | 删除全部 FaceID 用户数据 |

恢复出厂设置应清除全部用户相关 FaceID 数据，包括：

- Face ID 编号；
- 人脸特征库；
- Face ID 与用户的映射关系；
- 本地缓存数据；
- 未完成任务状态。

---

## 6.7 check / 数据同步流程

### 6.7.1 触发条件

当 R核根据 User / VCU 的 check 请求向 A核下发：

``````text
ADASFaceIDSysSta == 2
ADASFaceIDAtySta == 5
VCU2FaceId = 待查询 Face ID
``````

A核应进入 check 查询流程。

### 6.7.2 A核执行流程

A核应执行：

1. 接收 R核下发的 `VCU2FaceId`；
2. 查询本地是否存在该 Face ID；
3. 若存在，则返回成功和对应 Face ID；
4. 若不存在，则返回失败；
5. 不修改本地 FaceID 数据。

### 6.7.3 A核输出

查询成功时，A核向 R核输出：

``````text
FaceId2DScheckStatus = success
FaceId2VCU = queried_face_id
``````

查询失败时，A核向 R核输出：

``````text
FaceId2DScheckStatus = fail
``````


---

## 6.8 一般解绑流程

### 6.8.1 触发条件

当 R核根据 User / VCU 的解绑请求向 A核下发：

``````text
ADASFaceIDSysSta == 2
ADASFaceIDAtySta == 3
VCU2FaceId = 待解绑 Face ID
``````

A核应进入解绑流程。

### 6.8.2 A核执行流程

A核应执行：

1. 接收 R核下发的 `VCU2FaceId`；
2. 提取当前人脸特征；
3. 根据 `VCU2FaceId` 查询本地对应人脸特征；
4. 将当前人脸特征与目标 Face ID 对应特征进行比对；
5. 若比对通过，则执行解绑；
6. 若比对失败，则返回解绑失败；
7. 返回解绑结果。

### 6.8.3 ==6.8.3 A核输出==

==解绑成功时，A核向 R核输出：==

``````text
FaceId2DSUnbinedStatus = success
ADASFaceIDFuncRes = 1
FaceId2VCU = unbind_face_id
``````

==解绑失败时，A核向 R核输出：==

``````text
FaceId2DSUnbinedStatus = fail
statusCode = 失败原因
``````

### 6.8.4 关键约束

解绑与删除账号需要区分。

| 操作 | 语义 |
|---|---|
| 删除账号 | 删除 A核本地指定 Face ID 及对应人脸特征 |
| 解绑 | 解除 Face ID 与用户账号 / VCU 侧关系，是否删除本地特征需进一步定义 |

当前图中未明确解绑成功后是否删除本地 Face ID 数据。

因此需要确认：

``````text
解绑成功后，A核是否删除本地 Face ID 特征？
``````

若解绑仅解除关系，则 A核应保留特征数据，只更新绑定状态。

若解绑等价于删除，则 A核应删除对应 Face ID 特征和映射关系。

---

## 6.9 取消解绑流程

### 6.9.1 触发条件

在解绑过程中，如果 R核向 A核下发：

``````text
ADASFaceIDSysSta == 2
ADASFaceIDAtySta == 8
``````

A核应终止当前解绑流程。

### 6.9.2 A核执行流程

A核当前处于解绑流程时，收到取消解绑状态后，应执行：

1. 停止特征提取；
2. 停止人脸比对；
3. 终止当前解绑流程；
4. 不解除绑定关系；
5. 不删除本地 Face ID 数据；
6. 清理当前流程临时缓存。

### 6.9.3 关键约束

取消解绑只终止当前解绑流程，不应改变已有绑定状态，也不应删除本地 FaceID 数据。

---

# 7 A核功能流程汇总表

| 功能       | R核下发给 A核的条件                          | A核执行动作                       | A核返回给 R核                                               |
| -------- | ------------------------------------ | ---------------------------- | ------------------------------------------------------ |
| 正常录入     | `SysSta=2`, `AtySta=1`               | 采集人脸，提取特征，生成或复用 Face ID，保存数据 | `FaceId2DSCaptureStatus`, `FaceId2VCU`/`statusCode`    |
| 录入取消     | `SysSta=2`, `AtySta=7`，且当前处于录入流程     | 终止录入，清理临时数据，不保存 Face ID      |                                                        |
| 正常登录     | `SysSta=2`, `AtySta=2`               | 采集人脸，与本地 Face ID 特征库比对       | `FaceIdDSRecognitionStatus`, `FaceId2VCU`/`statusCode` |
| 取消登录     | `SysSta=2`, `AtySta=7`，且当前处于登录流程     | 终止登录识别，清理临时缓存                |                                                        |
| 请求删除     | `SysSta=2`, `AtySta=4`, `VCU2FaceId` | 删除指定 Face ID 数据              | `FaceId2DSDeleteStatus`, `FaceId2VCU`/`statusCode`     |
| 恢复出厂设置   | `AtySta=9`                           | 删除全部 FaceID 用户数据             | `FaceId2DSDeleteStatus`, `FaceId2VCU`/`statusCode`     |
| check 查询 | `SysSta=2`, `AtySta=5`, `VCU2FaceId` | 查询指定 Face ID 是否存在            | `FaceId2DScheckStatus`, `FaceId2VCU`                   |
| 一般解绑     | `SysSta=2`, `AtySta=3`, `VCU2FaceId` | 识别当前人脸，与目标 Face ID 比对，执行解绑   | `FaceId2DSUnbinedStatus`, `FaceId2VCU`/`statusCode`    |
| 取消解绑     | `SysSta=2`, `AtySta=8`，且当前处于解绑流程     | 终止解绑，不修改绑定状态                 |                                                        |

---

# 8 A核内部状态机建议

## 8.1 状态定义

A核内部建议抽象以下状态：

``````text
IDLE
CAPTURING
RECOGNIZING
DELETING
FACTORY_RESETTING
CHECKING
UNBINDING
CANCELING
ERROR
``````

---

## 8.2 状态转移

### 8.2.1 正常功能转移

``````text
IDLE
 ├─ SysSta=2, AtySta=1             -> CAPTURING
 ├─ SysSta=2, AtySta=2             -> RECOGNIZING
 ├─ SysSta=2, AtySta=3, VCU2FaceId -> UNBINDING
 ├─ SysSta=2, AtySta=4, VCU2FaceId -> DELETING
 ├─ SysSta=2, AtySta=5, VCU2FaceId -> CHECKING
 └─ AtySta=9                       -> FACTORY_RESETTING
``````

---

### 8.2.2 取消类转移

``````text
CAPTURING
 └─ AtySta=7 -> CANCELING -> IDLE

RECOGNIZING
 └─ AtySta=7 -> CANCELING -> IDLE

UNBINDING
 └─ AtySta=8 -> CANCELING -> IDLE
``````

---

### 8.2.3 删除类状态建议

删除账号与恢复出厂设置属于破坏性操作。

建议删除落盘阶段不允许取消：

``````text
DELETING
 └─ 执行完成后 -> IDLE

FACTORY_RESETTING
 └─ 执行完成后 -> IDLE
``````

原因是删除过程中若允许取消，容易产生：

- 特征已删除但映射未删除；
- 映射已删除但特征残留；
- 返回失败但本地已部分删除；
- R核与 A核状态不一致。

---

# 9 失败原因建议

A核可通过 `statusCode` 返回失败原因。

建议至少区分以下失败类型：

| 场景 | 建议失败原因 |
|---|---|
| 未检测到人脸 | `NO_FACE_DETECTED` |
| 多人脸 | `MULTI_FACE_DETECTED` |
| 人脸质量不满足 | `LOW_FACE_QUALITY` |
| 特征提取失败 | `FEATURE_EXTRACT_FAILED` |
| 活体检测失败 | `LIVENESS_FAILED` |
| 与已有 Face ID 比对失败 | `FACE_NOT_MATCHED` |
| Face ID 不存在 | `FACE_ID_NOT_FOUND` |
| 本地保存失败 | `SAVE_FAILED` |
| 本地删除失败 | `DELETE_FAILED` |
| 本地查询失败 | `QUERY_FAILED` |
| 流程被取消 | `CANCELLED` |
| 状态非法 | `INVALID_STATE` |
| 输入 Face ID 非法 | `INVALID_FACE_ID` |
| 存储异常 | `STORAGE_ERROR` |

---
# 10 删除和恢复出厂设置的并发保护

删除和恢复出厂设置期间，需要阻止其他流程并发执行。

例如：

- 删除过程中不应同时录入；
- 恢复出厂设置过程中不应同时登录；
- 解绑过程中不应同时删除同一 Face ID；
- check 查询过程中如果发生删除，需要保证结果一致性。

建议 A核内部增加 FaceID 数据锁或任务互斥机制。

---


