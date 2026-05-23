
# 1 文档目的

本文档基于 FaceID 功能时序流程图，整理 A核侧需求流程。
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

# 3 A核通用输入输出定义

## 3.1 A核输入信号

| 信号                                          | 来源     | 含义                                     |
| ------------------------------------------- | ------ | -------------------------------------- |
| `ADASFaceIDSysSta`                          | R核     | FaceID 系统状态                            |
| `ADASFaceIDAtvSta`                          | R核     | FaceID 当前动作状态                          |
| `VCU2FaceId`                                | R核     | R核转发给 A核的目标 Face ID                    |


---

## 3.2 A核输出信号

| 信号                           | 目标  | 含义                    |
| ---------------------------- | --- | --------------------- |
| `FaceId2DSCaptureStatus`     | R核  | 录入结果状态                |
| `FaceId2DSRecognitionStatus` | R核  | 登录识别结果状态              |
| `FaceId2DSDeleteStatus`      | R核  | 删除 / 恢复出厂设置结果状态       |
| `FaceId2DScheckStatus`       | R核  | check 查询结果状态          |
| `FaceId2DSUnbinedStatus`     | R核  | 解绑结果状态                |
| `FaceId2VCU`                 | R核  | A核返回给 R核的 Face ID 标识符 |
| `statusCode`                 | R核  | 失败原因或状态码              |

---

# 4 状态值定义

## 4.1 FaceID 系统状态

| 信号                 |  取值 | 含义  |
| ------------------ | --: | --- |
| `ADASFaceIDSysSta` | `2` | 激活  |
| `ADASFaceIDSysSta` | `1` | 待机  |

---

## 4.2 FaceID 动作状态

| 信号                 |  取值 | 功能含义         |
| ------------------ | --: | ------------ |
| `ADASFaceIDAtvSta` | `1` | 录入 capture   |
| `ADASFaceIDAtvSta` | `2` | 登录 recognize |
| `ADASFaceIDAtvSta` | `3` | 解绑 unbine    |
| `ADASFaceIDAtvSta` | `4` | 删除账号 delete  |
| `ADASFaceIDAtvSta` | `5` | 查询 check     |
| `ADASFaceIDAtvSta` |   6 | 录入取消         |
| `ADASFaceIDAtvSta` | `7` | 登录取消         |
| `ADASFaceIDAtvSta` | `8` | 解绑取消         |
| `ADASFaceIDAtvSta` | `9` | 恢复出厂设置       |

---

# 5 A核通用处理原则

## 5.1 数据一致性原则

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
ADASFaceIDAtvSta == 1
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

逻辑建议为：

``````text
当前人脸与本地已有 Face ID 比对
    ├─ 匹配已有用户：复用已有 Face ID
    └─ 未匹配已有用户：创建新的 Face ID
``````

### 6.1.6 绑定不成功

在绑定失败时，R核会返回 ADASFaceIDAtvSta = 4 和 VCU2FaceId，A核应该在收到后删除该id对应的人脸数据

## 6.2 录入取消流程

### 6.2.1 触发条件

在录入过程中，如果 R核向 A核下发取消状态：

``````text
ADASFaceIDSysSta == 2
ADASFaceIDAtvSta == 6
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
ADASFaceIDAtvSta == 2
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
FaceId2DSRecognitionStatus = success
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

## 6.4 取消登录流程

### 6.4.1 触发条件

在登录识别过程中，如果 R核向 A核下发：

``````text
ADASFaceIDSysSta == 2
ADASFaceIDAtvSta == 7
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
ADASFaceIDAtvSta == 4
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
ADASFaceIDAtvSta == 9
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
ADASFaceIDAtvSta == 5
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
FaceId2DSCheckStatus = success
FaceId2VCU = queried_face_id
``````

查询失败时，A核向 R核输出：

``````text
FaceId2DSCheckStatus = fail
statusCode = 失败原因
``````


---

## 6.8 一般解绑流程

### 6.8.1 触发条件

当 R核根据 User / VCU 的解绑请求向 A核下发：

``````text
ADASFaceIDSysSta == 2
ADASFaceIDAtvSta == 3
``````

A核应进入解绑流程。

### 6.8.2 A核执行流程

A核应执行：

1. 提取当前人脸特征；
2. 读取本地已保存 Face ID 特征库；
3. 将当前人脸特征与本地 Face ID 特征库逐一比对；
4. 若匹配到已保存 Face ID，则以匹配到的 Face ID 作为解绑结果；
5. 若未匹配到已保存 Face ID，则返回解绑失败；
6. 返回解绑结果。

当前实现不使用 `VCU2FaceId` 作为本地特征查询条件；解绑结果中的 Face ID 来自当前人脸识别/比对命中的本地库记录。

### 6.8.3 A核输出

解绑成功时，A核向 R核输出：

``````text
FaceId2DSUnbinedStatus = success
FaceId2VCU = face_id
``````

解绑失败时，A核向 R核输出：

``````text
FaceId2DSUnbinedStatus = fail
statusCode = 失败原因
``````

### 6.8.4 关键约束

解绑与删除账号需要区分。

| 操作   | 语义                                     |
| ---- | -------------------------------------- |
| 删除账号 | 删除 A核本地指定 Face ID 及对应人脸特征              |
| 解绑   | 根据当前人脸匹配本地库并返回命中的 Face ID，A核只负责查询，不删除 |

---

## 6.9 取消解绑流程

### 6.9.1 触发条件

在解绑过程中，如果 R核向 A核下发：

``````text
ADASFaceIDSysSta == 2
ADASFaceIDAtvSta == 8
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

| 功能       | R核下发给 A核的条件                          | A核执行动作                       |
| -------- | ------------------------------------ | ---------------------------- |
| 正常录入     | `SysSta=2`, `AtvSta=1`               | 采集人脸，提取特征，生成或复用 Face ID，保存数据 |
| 录入取消     | `SysSta=2`, `AtvSta=6`，且当前处于录入流程     | 终止录入，清理临时数据，不保存 Face ID      |
| 正常登录     | `SysSta=2`, `AtvSta=2`               | 采集人脸，与本地 Face ID 特征库比对       |
| 取消登录     | `SysSta=2`, `AtvSta=7`，且当前处于登录流程     | 终止登录识别，清理临时缓存                |
| 请求删除     | `SysSta=2`, `AtvSta=4`, `VCU2FaceId` | 删除指定 Face ID 数据              |
| 恢复出厂设置   | `AtySta=9`                           | 删除全部 FaceID 用户数据             |
| check 查询 | `SysSta=2`, `AtvSta=5`, `VCU2FaceId` | 查询指定 Face ID 是否存在            |
| 一般解绑     | `SysSta=2`, `AtvSta=3`               | 识别当前人脸，与本地 Face ID 特征库比对并返回命中的 Face ID |
| 取消解绑     | `SysSta=2`, `AtvSta=8`，且当前处于解绑流程     | 终止解绑，不修改绑定状态                 |

---

# 8 失败原因

A核通过 `statusCode` 向 R核返回失败原因。

A核只保留少量通用错误码。具体失败细节可以通过内部日志记录，不一定全部透传到 R核。

```
enum class ErrorCode {

    ERROR_UNKNOWN = 0,

    ERROR_NO_FACE = 2,              

    ERROR_HEAD_UP = 3,            

    ERROR_HEAD_DOWN = 4,            

    ERROR_HEAD_LEFT = 5,            

    ERROR_HEAD_RIGHT = 6,          

    ERROR_FACE_OCCLUDED  = 8,      

    ERROR_INVALID_INPUT = 9,

    ERROR_BUSY = 10,

    ERROR_NOT_MATCHED = 11,

    ERROR_FACE_ID_NOT_FOUND = 12,

    ERROR_STORAGE_FAIL = 13,

    ERROR_INTERNAL = 14,

};
```

--- 
# 9 状态机

A核内部维护 FaceID 状态机，用于控制录入、登录、解绑、删除、check、恢复出厂设置和取消流程。

A核侧 R核信号接收、FaceID 算法处理存在异步更新关系，因此不能只在流程开始时判断一次 R核状态。A核应在 FaceID 处理链路的关键步骤之间重复执行状态判断，防止取消信号到达后继续执行保存、登录成功返回或解绑成功返回。

核心原则为：

```
A核根据 R核最新信号更新内部状态。每个关键子步骤执行前后都调用 JudgeState()。如果收到取消信号，则切换到对应取消状态，清理当前流程缓存，并回到待机。取消后不得继续提交当前流程的成功结果。
```

---

## 9.1 内部状态定义

|状态|含义|
|---|---|
|`STANDBY`|待机，当前无 FaceID 流程执行|
|`CAPTURE`|正在录入|
|`RECOGNIZE`|正在登录识别|
|`UNBIND`|正在解绑|
|`DELETE_ID`|正在删除指定 Face ID|
|`CHECK_ID`|正在查询 Face ID|
|`FACTORY_RESET`|正在恢复出厂设置|
|`CANCEL_CAPTURE`|正在取消录入|
|`CANCEL_RECOGNIZE`|正在取消登录|
|`CANCEL_UNBIND`|正在取消解绑|
|`ERROR`|内部异常状态|

---

## 9.2 R核信号到内部状态映射

A核根据 R核下发的 `ADASFaceIDAtvSta` 更新内部状态。

|R核输入|功能|A核目标状态|
|---|---|---|
|`AtvSta=1`|录入|`CAPTURE`|
|`AtvSta=2`|登录|`RECOGNIZE`|
|`AtvSta=3`|解绑|`UNBIND`|
|`AtvSta=4`|删除账号|`DELETE_ID`|
|`AtvSta=5`|check 查询|`CHECK_ID`|
|`AtvSta=6`|录入取消|`CANCEL_CAPTURE`|
|`AtvSta=7`|登录取消|`CANCEL_RECOGNIZE`|
|`AtvSta=8`|解绑取消|`CANCEL_UNBIND`|
|`AtvSta=9`|恢复出厂设置|`FACTORY_RESET`|

---

## 9.3 JudgeState 机制

A核提供`JudgeState()` 方法，用于根据 R核最新信号和当前内部状态决定是否继续执行当前流程。

核心逻辑：

```
读取 R核最新 SysSta / AtvSta / VCU2FaceId
判断当前 R核请求是否与当前 A核状态一致    
如果是正常业务请求：    - 待机状态下进入对应业务状态    - 当前已在相同业务状态下则继续执行    - 当前正在其他业务中则返回 busy 或忽略新请求    
如果是取消请求：    - 若取消请求与当前业务匹配，则进入对应取消状态    - 执行取消清理    - 回到 STANDBY    
如果是恢复出厂设置：    - 优先进入 FACTORY_RESET
```

---

## 9.4 状态切换表

| 当前状态               | R核输入       | 下一状态                | A核动作                  |
| ------------------ | ---------- | ------------------- | --------------------- |
| `STANDBY`          | `AtvSta=1` | `CAPTURE`           | 开始录入                  |
| `STANDBY`          | `AtvSta=2` | `RECOGNIZE`         | 开始登录识别                |
| `STANDBY`          | `AtvSta=3` | `UNBIND`            | 开始解绑                  |
| `STANDBY`          | `AtvSta=4` | `DELETE_ID`         | 删除指定 Face ID          |
| `STANDBY`          | `AtvSta=5` | `CHECK_ID`          | 查询指定 Face ID          |
| `STANDBY`          | `AtvSta=9` | `FACTORY_RESET`     | 恢复出厂设置                |
| `CAPTURE`          | `AtvSta=6` | `CANCEL_CAPTURE`    | 停止录入，清理录入缓存           |
| `RECOGNIZE`        | `AtvSta=7` | `CANCEL_RECOGNIZE`  | 停止登录，清理识别缓存           |
| `UNBIND`           | `AtvSta=8` | `CANCEL_UNBIND`     | 停止解绑，清理解绑缓存           |
| `CAPTURE`          | `AtvSta=1` | `CAPTURE`           | 继续当前录入流程              |
| `RECOGNIZE`        | `AtvSta=2` | `RECOGNIZE`         | 继续当前登录流程              |
| `UNBIND`           | `AtvSta=3` | `UNBIND`            | 继续当前解绑流程              |
| 非 `STANDBY`        | 新普通任务      | 原状态                 | 返回 `ERR_BUSY`，避免中途抢占  |
| 任意状态               | `AtvSta=9` | `FACTORY_RESET`     | 进入恢复出厂设置流程，必要时先清理当前流程 |
| `CANCEL_CAPTURE`   |            | `STANDBY`           |                       |
| `CANCEL_RECOGNIZE` |            | `STANDBY`           |                       |
| `CANCEL_UNBIND`    |            | `STANDBY`           |                       |
| `CAPTURE`          | 录入成功 / 失败  | `STANDBY`           | 返回录入结果                |
| `RECOGNIZE`        | 登录成功 / 失败  | `STANDBY`           | 返回登录结果                |
| `UNBIND`           | 解绑成功 / 失败  | `STANDBY`           | 返回解绑结果                |
| `DELETE_ID`        | 删除成功 / 失败  | `STANDBY`           | 返回删除结果                |
| `CHECK_ID`         | 查询成功 / 失败  | `STANDBY`           | 返回查询结果                |
| `FACTORY_RESET`    | 恢复成功 / 失败  | `STANDBY` 或 `ERROR` | 返回恢复结果                |

---

## 9.5 取消流程处理

取消不是新的业务流程，而是当前业务流程的中止状态。

由于 A核运行频率较高，例如 30Hz，取消清理通常会在一个或少数几个处理周期内完成，因此不需要额外引入复杂会话管理。

---

## 9.6 新请求处理规则

当前状态不是 `STANDBY` 时，如果 R核下发新的普通业务请求，

A核不应直接抢占当前流程。

|情况|A核处理|
|---|---|
|当前状态与 R核请求一致|继续当前流程|
|当前状态与 R核请求不一致|返回 `ERR_BUSY` 或忽略该请求|
|当前为取消请求且与当前流程匹配|切换到对应取消状态|
|当前为恢复出厂设置|作为高优先级请求处理|
