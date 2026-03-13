# 1 算法架构

## 1.1 架构总览（逻辑分层）

```
输入/数据源
 ├─ 摄像头/图像序列/视频/回灌数据
 │
核心流水线（Pipeline）
 ├─ DmsPipeline 组织多模型推理与调度
 │   ├─ 模型推理（Det/Face/Hand/Gaze/Pose 等）
 │   └─ 中间结果（AtomicResult）
 │
融合与业务算法（Fuse/Algorithms）
 ├─ 疲劳/分心/抽烟打电话等判别与融合
 └─ 结果序列化/输出
 │
输出与工具链
 ├─ SDK接口/主程序
 └─ Python ZMQ 观看/录制/回放/离线解析

```

## 1.2 关键模块划分（目录级）

- **入口与SDK**
    - main/  
        提供 SDK/接口与可执行入口。
- **核心源码**
    - source/pipeline/  
        负责按配置加载模型并串行/并行执行。
    - source/models/  
        各类模型封装（检测、关键点、姿态、视线、识别等）。
    - source/fuse_algos/  
        融合算法与结果序列化（疲劳、分心、吸烟/打电话等）。
    - source/utils/  
        相机/图像处理、后处理、跟踪、配置读取、回调等通用能力。
    - source/ai_engine/  
        推理引擎与动态加载封装（QNN/DDK 等适配）。
    - source/config/  
        配置解析与管理。
- **对外配置与模型**
    - etc/  
        各模型与流水线 JSON 配置。
    - model_weight/  
        模型权重与资源文件。
- **工具链与脚本**
    - scripts/  
        多平台编译与运行脚本（J6M/QNX/x86 等）。
    - python_zmq/  
        在线显示、录制、回放、离线解析等工具。
- **测试与第三方**
    - test/  
        模型与组件级测试。
    - thirdparty/  
        外部依赖。

## 1.3 运行流程（简化）

1. **入口**：main/ 启动 SDK 或可执行程序。
2. **配置加载**：读取 json中的模型与流水线配置。
3. **流水线初始化**：DmsPipeline 根据配置加载所需模型。
4. **推理执行**：按顺序运行检测/关键点/姿态/眼部/手部等模型。
5. **融合输出**：fuse_algos 对模型结果进行业务融合并序列化。
6. **输出**：SDK 接口返回或通过 ZMQ 工具显示/录制/回放。


# 2 多线程

## 2.1 buffter manager

### 2.1.1 双队列

bufftermanager中有两个数据池：
- m_availableBuff: 空闲池(可写、可复用的空白对象)
- m_filledBuff:已填充池（已经装有最新一帧数据，等待下游消费）
#### 2.1.1.1 作用
1. 解决读写互斥的问题，避免一个buffer同时被读写
2. 相机（生产者）可能很快，下游pipeline（消费者）可能慢
	- filled太多：丢帧/覆盖旧帧
	- available太少
		- 阻塞生产者
		- 从filled弹出一个（意味着丢掉一帧还未被消费的图）并使用新数据覆盖后重新push到filled

### 2.1.2 条件等待

wait的机制：
```
1 获取锁  
2 检查条件  
3 如果条件不满足：  
释放锁  
线程睡眠  
4 被唤醒  
5 重新获取锁  
6 再次检查条件
```

|函数|行为|
|---|---|
|wait|无限等待直到条件成立|
|wait_for|等待指定时间，超时返回|
### 2.1.3 buffer recycling

启动时预创建buffer，放入空闲池

available（空壳可写） -> producer GetImage 填充 -> filled（可读） -> consumer 处理完 -> 归还到 available

# 3 睁闭眼模型

[[睁闭眼模型训练方案]]

# 4 后处理

[[疲劳驾驶监测后处理]]

[[座舱乘员多目标跟踪方案]]
# 5 交叉编译

[[QNX与Linux交叉编译]]

## 5.1 protobuf编译

核心原则：

> 同一份 `.proto` 文件必须在所有平台上保持一致，并且代码生成工具（protoc）与运行时库（protobuf runtime）应来自同一版本。

---

### 5.1.1 protobuf 构建组成

protobuf 在工程中包含三个不同角色：

|组件|作用|平台|
|---|---|---|
|proto 文件|数据结构定义|通用|
|protoc|代码生成工具|x86|
|libprotobuf.so|序列化运行时库|x86 / QNX|

因此构建流程可以分为三部分：

```
.proto  
   │  
   ├── protoc (x86)  
   │      ├── 生成 pb.cc / pb.h （C++）  
   │      └── 生成 pb2.py （Python）  
   │  
   ├── x86 libprotobuf.so  
   │      └── protoc 运行依赖  
   │  
   └── QNX libprotobuf.so  
          └── sdk.so 运行依赖
```


---

### 5.1.2 Host 侧（x86）protobuf

Host 侧主要用于：

- 运行 `protoc`
    
- 生成 C++ 与 Python protobuf代码
    
- Python 工具解析算法输出
    


要求：
```
protoc_x86   
libprotoc.so
```

必须来自 **同一版本构建**。

---

### 5.1.3 Target 侧（QNX）protobuf

板端运行需要 protobuf 运行库，因此需要交叉编译：libprotobuf.so (QNX)

该库用于：sdk.so  ->  libprotobuf.so

sdk.so使用的protobuf版本 = 生成 pb.cc 时使用的 protobuf 版本

否则可能出现 ABI 不兼容

---

### 5.1.4 Python 侧 protobuf

Python 工具链用于：

- ZMQ 接收算法结果
    
- protobuf 解析
    
- 图像显示 / 离线分析
    

Python 运行时需要安装 protobuf runtime，与 `protoc` 保持同版本，

---

### 5.1.5 版本一致性要求

工程中 protobuf 需要满足以下一致性规则：

| 组件              | 要求           |
| --------------- | ------------ |
| proto文件         | 所有平台统一       |
| protoc          | 固定版本         |
| x86 protobuf.so | 与 protoc 同版本 |
| QNX protobuf.so | 与 protoc 同版本 |
| Python protobuf | 与 protoc 同版本 |
