
> 内容包括：基础用法、第三方库管理、动态库搜索路径（RPATH）、ARM/QNX 交叉编译、GoogleTest 单测组织。

---

# 1 CMake

CMake 本身不编译代码，它做的事情是：

```
CMakeLists.txt → 生成 Makefile / Ninja / VS 工程 → 调用编译器 + 链接器
```

它负责：

- 管理源文件、头文件、库依赖
    
- 区分 Debug / Release 等构建配置
    
- 多平台适配（Linux / Windows / 嵌入式）
    
- （可选）安装、打包、测试集成
    

---

# 2 最小工程骨架

```
cmake_minimum_required(VERSION 3.10) project(MyProject CXX)  set(CMAKE_CXX_STANDARD 17) set(CMAKE_CXX_STANDARD_REQUIRED ON) set(CMAKE_CXX_EXTENSIONS OFF)  add_executable(demo main.cpp)
```

构建与运行：

```
mkdir build
cd build
cmake ..        # 生成 Makefile
make -j         # 编译
./demo          # 运行
```

---

# 3 构建类型（Build Type）

常用构建类型：

|类型|优化|调试信息|场景|
|---|---|---|---|
|Debug|关|开|开发调试|
|Release|开|关|投产、上线|
|RelWithDebInfo|开|开|调优分析|

指定方式：

`cmake -DCMAKE_BUILD_TYPE=Release ..`


---

# 4 编译选项

## 4.1 C++ 标准与基础 flags

```
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(CMAKE_CXX_FLAGS_DEBUG   "-O0 -g3 -Wall -Wno-unused-variable -Wno-deprecated-declarations -fPIC")
set(CMAKE_CXX_FLAGS_RELEASE "-O2 -DNDEBUG -Wall -Wno-unused-variable -Wno-deprecated-declarations -fPIC")

# 视三方库 ABI 而定
add_definitions(-D_GLIBCXX_USE_CXX11_ABI=1)
```
[[编译与调试]]
## 4.2 覆盖率（可选）
[[测试流程]]
覆盖率衡量**测试用例到底运行了多少行代码 / 分支 / 路径**

```
option(ENABLE_COVERAGE "Enable coverage flags" OFF)
if(ENABLE_COVERAGE)
    add_compile_options(-fprofile-arcs -ftest-coverage)
    link_libraries(gcov)
endif()

```

---

# 5 include / lib 搜索路径

## 5.1 头文件路径

推荐用 `target_include_directories`：

```
add_library(Utils src/utils.cpp)
target_include_directories(Utils
    PUBLIC
        ${PROJECT_SOURCE_DIR}/include
        ${PROJECT_SOURCE_DIR}/src
)

```

多 target 时，每个 target 自己声明依赖，便于复用和隔离。

## 5.2 库文件搜索路径（链接阶段）

`link_directories(${PROJECT_SOURCE_DIR}/thirdparty/lib)`

⚠ **注意**：  
`link_directories()` **只影响编译/链接阶段**，不会影响“运行时找不找得到 `.so`”这个问题。

---

# 6 链接库：target_link_libraries

基本用法：

```
add_executable(App src/main.cpp)
target_link_libraries(App
    PRIVATE
        CoreLib
        Utils
        pthread
        opencv_core
)

```

可见性：

|关键字|对当前 target|对依赖它的其它 target|
|---|---|---|
|PRIVATE|有效|不传播|
|PUBLIC|有效|也传播（包含头+库）|
|INTERFACE|无源码依赖，仅传播接口|仅对下游有效|

例子：Core 依赖 Utils，下游只需要写 Core：

```
add_library(Utils src/utils.cpp)
add_library(Core src/core.cpp)
target_link_libraries(Core PUBLIC Utils)

add_executable(App src/main.cpp)
target_link_libraries(App PRIVATE Core)  # 自动带上 Utils

```

---

# 7 运行时动态库搜索：RPATH / LD_LIBRARY_PATH

## 7.1 运行搜索顺序
Linux 下 loader 的搜索顺序：

1. ELF 内嵌的 `RPATH` / `RUNPATH`
    
2. `LD_LIBRARY_PATH` 环境变量
    
3. `/etc/ld.so.conf` + `ldconfig` 缓存
    
4. 系统默认路径 `/lib`, `/usr/lib`, `/usr/lib/x86_64-linux-gnu` 等
    

## 7.2 用 CMake 写 RPATH（推荐做法）

假设你有第三方库在：

`${PROJECT_SOURCE_DIR}/thirdparty/opencv/lib ${PROJECT_SOURCE_DIR}/thirdparty/protobuf/lib`

可以在 CMake 里写：

```
set(THIRDPARTY_LIB_DIRS
    ${PROJECT_SOURCE_DIR}/thirdparty/opencv/lib
    ${PROJECT_SOURCE_DIR}/thirdparty/protobuf/lib
)

set(CMAKE_SKIP_BUILD_RPATH FALSE)
set(CMAKE_BUILD_RPATH "${THIRDPARTY_LIB_DIRS}")
set(CMAKE_BUILD_RPATH_USE_ORIGIN TRUE)
```

生成后检查：

`readelf -d app | grep RPATH ldd app`

---

# 8 `--as-needed`

现代工具链几乎都默认启用链接器选项 `-Wl,--as-needed`：

- 若 `target_link_libraries(App somelib)`， 但 App 内没有任何符号来自 `somelib`， 链接器会认为“这个库没用”，直接丢弃，不会写入 ELF 的 NEEDED 列表。

- 因此把一个库写进 `target_link_libraries`，但代码没用它，**一般不会导致运行时依赖这个库**

---

# 9 ARM 交叉编译（Linux on ARM）

场景：在 x86_64 Ubuntu 上，为 ARM Linux（例如 Cortex-A 系列）编译程序。

## 9.1 准备交叉编译工具链

一般会有类似：

`/opt/toolchains/gcc-arm-9.2.1/bin/arm-linux-gnueabihf-gcc /opt/toolchains/gcc-arm-9.2.1/bin/arm-linux-gnueabihf-g++`

## 9.2 写一个 toolchain 文件（推荐）

新建 `cmake/toolchain-arm-linux.cmake`：

```
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR arm)

# 工具链前缀，例如 arm-linux-gnueabihf- / aarch64-linux-gnu-
set(TOOLCHAIN_PREFIX arm-linux-gnueabihf)

set(CMAKE_C_COMPILER   /opt/toolchains/gcc-arm-9.2.1/bin/${TOOLCHAIN_PREFIX}-gcc)
set(CMAKE_CXX_COMPILER /opt/toolchains/gcc-arm-9.2.1/bin/${TOOLCHAIN_PREFIX}-g++)

# 指定 sysroot（若有）
set(CMAKE_SYSROOT /opt/sysroots/arm-linux-sysroot)

# 让 CMake 使用 sysroot 查找 include/lib
set(CMAKE_FIND_ROOT_PATH ${CMAKE_SYSROOT})

# 只在 sysroot 里找库/头，避免误用主机库
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)

```

## 9.3 配置 & 构建

```
mkdir build-arm
cd build-arm
cmake .. -DCMAKE_TOOLCHAIN_FILE=../cmake/toolchain-arm-linux.cmake -DCMAKE_BUILD_TYPE=Release
make -j
```

编出来的是 ARM 架构的 ELF，可通过 `file` 命令确认：

```
file app 
# ELF 32-bit LSB executable, ARM, EABI5
``` 

> 第三方库（例如 OpenCV for ARM）需要在 sysroot 或指定路径下有对应的 ARM 版本，链接时路径要对齐。

---

# 10 QNX 交叉编译（例如 QNX 7.x）

QNX 通常自带工具链与 qcc 封装器。

## 10.1 准备 QNX 工具链

例如 QNX 7.1 安装后，会有类似：

```
$QNX_HOST/usr/bin/qcc
$QNX_HOST/usr/bin/q++

```
QNX 通过环境变量控制目标架构：

- `-Vgcc_ntoarmv7le` 等等
    

### 10.1.1 编写 QNX toolchain 文件

`cmake/toolchain-qnx.cmake`：

```
set(CMAKE_SYSTEM_NAME QNX)
set(CMAKE_SYSTEM_PROCESSOR arm)       # 或 aarch64 / x86 depending on target

# QNX 的 qcc / q++ 封装器
set(CMAKE_C_COMPILER   "$ENV{QNX_HOST}/usr/bin/qcc")
set(CMAKE_CXX_COMPILER "$ENV{QNX_HOST}/usr/bin/q++")

# 指定 QNX 目标平台 variant，例如 gcc_ntoarmv7le
set(QNX_TARGET_VARIANT "gcc_ntoarmv7le")

# 给编译器和链接器增加平台参数
set(CMAKE_C_FLAGS   "${CMAKE_C_FLAGS}   -V${QNX_TARGET_VARIANT}")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -V${QNX_TARGET_VARIANT}")

# QNX sysroot
set(CMAKE_SYSROOT "$ENV{QNX_TARGET}")

set(CMAKE_FIND_ROOT_PATH ${CMAKE_SYSROOT})
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)

```


### 10.1.2 配置 & 构建

```
mkdir build-qnx
cd build-qnx
cmake .. -DCMAKE_TOOLCHAIN_FILE=../cmake/toolchain-qnx.cmake -DCMAKE_BUILD_TYPE=Release
make -j
```

QNX 的第三方库（OpenCV、protobuf 等）也需要对应的 QNX 版本，放在 QNX 的 sysroot 或你指定的 qnx-lib 目录下。

---

## 10.2 单元测试组织（以 GoogleTest 为例）

### 10.2.1 引入 gtest

方式一：自己下载预编译 gtest，放在 `thirdparty/googletest`：

```
set(GTEST_INCLUDE_DIR ${PROJECT_SOURCE_DIR}/thirdparty/googletest/include)
set(GTEST_LIB_DIR     ${PROJECT_SOURCE_DIR}/thirdparty/googletest/lib)

include_directories(${GTEST_INCLUDE_DIR})
link_directories(${GTEST_LIB_DIR})

```

方式二：通过 `FetchContent` 自动拉取（现代用法）：

```
include(FetchContent)
FetchContent_Declare(
    googletest
    URL https://github.com/google/googletest/archive/refs/tags/v1.15.0.zip
)
FetchContent_MakeAvailable(googletest)

```
### 10.2.2 定义测试可执行文件

例如测试一个 Fatigue 算法模块：

```
# test/CMakeLists.txt

add_executable(test_fatigue
    test_fatigue.cpp
)

target_link_libraries(test_fatigue
    PRIVATE
        sdk              # 被测模块（你的主库）
        gtest
        gtest_main
        pthread
)

```
`test_fatigue.cpp`示例：
```
#include <gtest/gtest.h>
#include "fatigue_algorithm.h"

TEST(FatigueAlgorithm, BasicThreshold)
{
    FatigueAlgorithm algo;
    // 准备输入...
    // EXPECT_xxx / ASSERT_xxx 断言业务逻辑
}

int main(int argc, char** argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

```

### 10.2.3 集成 CTest

在顶层 CMakeLists 打开测试支持：

`enable_testing()`

给每个测试注册为 CTest 用例：

```
add_executable(test_fatigue test_fatigue.cpp)
target_link_libraries(test_fatigue PRIVATE sdk gtest gtest_main pthread)

add_test(NAME FatigueTests COMMAND test_fatigue)
```
然后在 build 目录执行：

```
ctest          # 运行所有测试
ctest -R Fatigue  # 只跑名称匹配的测试
ctest -V      # 输出详细 log

```

### 10.2.4 批量组织单测（建议结构）

推荐目录结构：

```
project_root/
  src/                 # 源码
  include/             # 头文件
  test/
    CMakeLists.txt     # 测试工程 CMake
    test_fatigue.cpp
    test_distraction.cpp
    test_pipeline.cpp
```

`test/CMakeLists.txt` 示例：

```
add_executable(test_fatigue test_fatigue.cpp)
target_link_libraries(test_fatigue PRIVATE sdk gtest gtest_main pthread)
add_test(NAME FatigueTests COMMAND test_fatigue)

add_executable(test_distraction test_distraction.cpp)
target_link_libraries(test_distraction PRIVATE sdk gtest gtest_main pthread)
add_test(NAME DistractionTests COMMAND test_distraction)

```

这样 CTest 能统一管理，CI 管道也方便集成。

---

## 10.3 常用命令速查表

|命令|作用|
|---|---|
|`cmake ..`|生成构建系统|
|`cmake -DCMAKE_BUILD_TYPE=Debug ..`|设置构建类型|
|`cmake --build . --target all -j`|通用构建方式|
|`make -j$(nproc)`|使用 Makefile 并行编译|
|`ctest`|运行所有 CTest 单元测试|
|`ctest -R pattern`|按名字匹配运行部分测试|
|`ldd app`|查看 app 需要哪些动态库以及加载路径|
|`readelf -d app|grep RPATH`|
|`file app`|看 ELF 架构（x86_64 / arm / aarch64）|

---

## 10.4 推荐项目结构总结

```
project_root/
  CMakeLists.txt
  cmake/
    toolchain-arm-linux.cmake
    toolchain-qnx.cmake
  src/
    ...
  include/
    ...
  thirdparty/
    opencv/
    protobuf/
    zmq/
    googletest/
  test/
    CMakeLists.txt
    test_xxx.cpp
  build/           # 本地构建目录（建议 gitignore）
  build-arm/       # ARM 交叉编译目录
  build-qnx/       # QNX 交叉编译目录

```