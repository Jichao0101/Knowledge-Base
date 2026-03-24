# 1 QNX系统
## 1.1 微内核（Microkernel）架构

QNX Neutrino 采用微内核设计，其内核仅实现最基础且可靠的核心能力，例如：

- **线程调度（Thread Scheduling）**
    
- **进程间通信 IPC（Inter-Process Communication, QNX Message-Passing）**
    
- **中断处理（Interrupt Handling）**
    
- **基本内存管理（Minimal Memory Management）**
    

内核极小化带来两个重要特性：

1. **高可靠性（Reliability）**  
    用户态驱动、文件系统、网络协议栈等全部运行在 User Space。  
    当某个用户态服务崩溃时，不会导致系统整体崩溃。
    
2. **高可恢复性（Fault Isolation）**  
    单个用户态进程的错误不会影响内核，也不会影响其他用户态进程。  
    QNX 的 Watchdog + Restart 机制可在毫秒级恢复系统服务。
    

## 1.2 QNX 的适用场景

- 自动驾驶域控制器（DCU）
    
- 功能安全要求较高的系统（ASIL-D）
    
- 工业控制、轨交、机器人系统
    
- 多核调度、实时性要求严格的嵌入式环境
    

实时性来自其消息传递架构（Message-passing IPC），使任务调度确定性更强。

# 2 交叉编译
## 2.1 定义

在**编译设备 A** 上编译代码，生成可在 **另一种架构设备 B** 上运行的二进制程序，这一过程即交叉编译。

例如：  
在 x86_64 Ubuntu 主机上编译运行于 ARMv8 QNX 的程序。

## 2.2 交叉编译的难点与限制

### 2.2.1 资源能力不同

目标嵌入式平台通常：

- CPU 性能较弱
    
- 内存小
    
- 文件系统限制多
    
- 工具链可用性低
    

因此必须在 Host 侧提前完成编译和优化。

### 2.2.2 可用库与 ABI 差异

不同架构的库 ABI（Application Binary Interface）不兼容。  
交叉编译工具链需包含：

- 目标平台的 C 库（libc）
    
- 编译器（gcc/clang）
    
- 链接器（ld）
    
- 运行时支持库
    

否则目标系统无法运行二进制

## 2.3 交叉编译链命名规则

典型命名格式：

`<arch>-<core>-<kernel>-<system>`

或更通用的 GNU 风格：

`<target>-<vendor>-<os>-<abi>`

示例（QNX ARM64）：

`aarch64-unknown-nto-qnx`

解释：

- **aarch64**：CPU 指令集
    
- **unknown/vendor**：工具链供应商（可有可无）
    
- **nto**：QNX Neutrino OS 缩写
    
- **qnx**：目标系统 ABI 规范
    

QNX SDP（Software Development Platform）中的工具链通常为：

`qcc, q++, gcc, nto*-gcc, nto*-ld`

编译命令常用形式：

`qcc -Vgcc_ntoaarch64le ...`

## 2.4 常见目标平台工具链示例

|目标架构|工具链前缀|OS|示例|
|---|---|---|---|
|ARMv7|arm-unknown-nto-qnx6|QNX|多用于车规 SOC（如 TI TDA）|
|ARMv8|aarch64-unknown-nto-qnx7|QNX|主流自动驾驶 ADC 芯片（如 8155/8295）|
|x86 QNX|i486-pc-nto-qnx6|QNX|工控场景|

# 3 Linux 环境下交叉编译 QNX 程序

使用 QNX SDP 提供的构建工具链，通常包含 `qcc`、`q++`、`nto*-gcc` 等。

---

## 3.1 CMake 方式

CMake 推荐使用 toolchain 文件：

toolchain-qnx-aarch64.cmake:

```
set(CMAKE_SYSTEM_NAME QNX)
set(CMAKE_SYSTEM_PROCESSOR aarch64)

set(QNX_HOST /opt/qnx/sdp)
set(QNX_TARGET /opt/qnx/target/qnx7)

set(CMAKE_C_COMPILER   ${QNX_HOST}/host/linux/x86_64/usr/bin/aarch64-unknown-nto-qnx7-gcc)
set(CMAKE_CXX_COMPILER ${QNX_HOST}/host/linux/x86_64/usr/bin/aarch64-unknown-nto-qnx7-g++)

```

构建：

```
cmake -DCMAKE_TOOLCHAIN_FILE=toolchain-qnx-aarch64.cmake ..
make -j8
```

# 4 QNX 交叉编译典型工作流示例

假设要编译一个融合算法模块（如IOU匹配、点云聚类）到 QNX ARM64：

1. 安装 QNX SDP
    
2. 链接环境变量
    
    `source /opt/qnx/sdp/qnxsdp-env.sh`
    
3. 编译
    
    `qcc -Vgcc_ntoaarch64le -O2 my_algo.cpp -o my_algo`
    
4. 上传到目标板：
    
    `scp my_algo root@192.168.1.x:/usr/bin`
    
5. 运行：
    
    `./my_algo`