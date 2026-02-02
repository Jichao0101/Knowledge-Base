## 1. 模块概览

### 1.1 模块功能

`FuseAlgorithm` 模块用于对多源输入（如眼睛开闭、眼睛纵横比等）的结果进行融合后处理。  
它采用 **Builder 模式** 构建算法实例，通过回调管理、配置注入和 CAN 数据驱动实现灵敏度自适应。

### 1.2 模块结构图

`CAN → VehicleStateProvider → FuseAlgorithm -> AlgorithmResult (fused)`

### 1.3 依赖关系

|模块|功能|
|---|---|
|`BaseAlgorithm`|定义算法接口规范|
|`AtomicResult` / `AlgorithmResult`|各子算法输入输出数据结构|
|`VehicleState`|来自 CAN 的车辆状态输入|
|`CallBackManager`|回调注册与事件发布|
|`SerializeResult`|序列化及外部通信支持|

---

## 2. 快速上手

```
#include "fuse_algorithm.h"
#include "fatigue_algorithm.h"

int main() {
    using namespace FuseAlgosDomain;

    // 1. 创建回调管理器
    auto cbManager = std::make_shared<CallBackManager>();

    // 2. 构建融合算法实例
    auto fuseAlgo = FuseAlgorithm::build
        .SetCallBackManager(cbManager)
        ->SetProtoFlag(true)
        ->SetProtoPath("config/fuse_output.pb")
        ->SetIP("192.168.1.10")
        ->Build();

    // 3. 启动算法
    fuseAlgo->Run();
    return 0;
}

```

---

## 3. 核心接口定义

### 3.1 BaseAlgorithm 抽象类

```
class BaseAlgorithm {
 public:
    virtual ~BaseAlgorithm() {}
    virtual int32_t Init() = 0;
    virtual int32_t Process(std::shared_ptr<AtomicResult>& res,
                            std::shared_ptr<VehicleState>& state,
                            std::shared_ptr<AlgorithmResult>& out) = 0;
    virtual void Action(uint8_t ret) {}
};

```

#### 参数说明

|参数|类型|描述|
|---|---|---|
|`res`|`shared_ptr<AtomicResult>`|子算法输入结果（图像分析结果、关键点、置信度等）|
|`state`|`shared_ptr<VehicleState>`|来自 CAN 的车辆状态（车速、档位、方向盘角度、灵敏度系数等）|
|`out`|`shared_ptr<AlgorithmResult>`|算法输出结果（融合后的状态、警报等级等）|

#### 返回值

|值|含义|
|---|---|
|0|成功|
|非 0|错误码（初始化失败、输入无效、计算异常）|

---

### 3.2 FuseAlgorithm 类
```
class FuseAlgorithm {
public:
    class Builder {
        Builder* SetCallBackManager(std::shared_ptr<CallBackManager> cb);
        Builder* SetProtoFlag(bool use);
        Builder* SetProtoPath(std::string path);
        Builder* SetIP(std::string ip);
        std::shared_ptr<FuseAlgorithm> Build();
    };

    int8_t Run();
    void Stop();
    int8_t SubscribePipelineResults(std::shared_ptr<AtomicResult>& res);
    void UpdateVehicleState(const VehicleState& vs);
};
```

#### 功能描述

|方法|功能|
|---|---|
|`Run()`|启动算法主循环|
|`Stop()`|停止融合与发布|
|`SubscribePipelineResults()`|接收子算法原子结果|
|`UpdateVehicleState()`|更新 CAN 状态（支持实时灵敏度切换）|

---

### 3.3 FatigueAlgorithm 类

```
lass FatigueAlgorithm : public BaseAlgorithm {
public:
    int32_t Init() override;
    int32_t Process(std::shared_ptr<AtomicResult>& res,
                    std::shared_ptr<VehicleState>& state,
                    std::shared_ptr<AlgorithmResult>& out) override;
    void Action(uint8_t ret) override;
    void SetParams(DMS_MODE mode);
};
```

#### FatigueParams 结构体

|字段|类型|默认值|说明|
|---|---|---|---|
|`FATIGUE_ENABLE`|bool|true|是否启用疲劳检测|
|`FATIGUE_YAWN_DETECT`|bool|true|是否启用哈欠检测|
|`DMS_SPEED_ENABLE`|float|0.0|DMS 功能启用车速阈值|
|`DMS_WARNING_SPEED`|float|30.0|报警启用车速阈值|
|`FATIGUE_COOL_TIME_1`|float|60.0|轻度疲劳冷却时间（秒）|
|`FATIGUE_COOL_TIME_2`|float|0.0|重度疲劳冷却时间（秒）|
|`FATIGUE_YAWN_TIME`|float|3.0|哈欠检测时间（秒）|
|`NO_FACE_TIME`|float|10.0|无人脸检测持续时间（秒）|

#### 示例：灵敏度预设表

|模式|冷却时间1|冷却时间2|无人脸时间|
|---|---|---|---|
|高灵敏度|60|0|10|
|中灵敏度|60|0|10|
|低灵敏度|60|0|15|

---

## 4. 返回值与错误码

|错误码|含义|解决建议|
|---|---|---|
|-1|参数为空|检查输入指针是否为空|
|-2|状态不合法|检查 VehicleState 内容|
|-3|内部异常|查看日志输出|
|-4|未初始化|确保已调用 Init()|

---

## 5. 线程安全说明

|接口|线程安全性|备注|
|---|---|---|
|`Init()`|否|应在主线程调用一次|
|`Process()`|是|内部复制局部快照，安全多线程调用|
|`SetParams()`|是|使用互斥锁保护|
|`UpdateVehicleState()`|是|内部自锁更新 VehicleState|

---

## 6. 日志与调试

- 默认日志路径：`logs/fuse_algorithm.log`
    
- 日志等级：`INFO / WARN / ERROR / DEBUG`
    
- 可通过配置文件 `config/logger.yaml` 控制输出等级。
    

---

## 7. 性能指标

|项目|指标|备注|
|---|---|---|
|运行帧率|30 FPS|处理 1080p 图像流|
|单帧延迟|< 20 ms|包含融合与结果发布|
|内存占用|< 200 MB|典型 DMS 模式下|

---

## 8. 版本与兼容性

|版本|时间|变更说明|
|---|---|---|
|v1.0|2025.03|初版发布|
|v1.1|2025.06|增加灵敏度动态缩放|
|v1.2|2025.09|支持 CAN 状态订阅与 VehicleStateProvider 模式|

---

## 9. 附录

- **术语表**
    
    - DMS: Driver Monitoring System
        