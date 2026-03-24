# 1 CMake的核心:Target Graph

## 1.1 Target

CMake的编译基本单位不是文件，而是target
- `add_library()` 生成库目标
- `add_executable()` 生成可执行目标
- `add_library(xxx INTERFACE)` 只描述接口(头文件/编译选项/依赖)，自己不编译

“对象依赖对应的源文件或其他对象”，在 CMake 里等价于：
- **源文件属于哪个 target**
- **target 依赖哪些库 target**
- **target 需要哪些 include/compile options/definitions**
- **target 需要哪些生成步骤（custom command / generated sources）**

## 1.2 依赖的传递性：PUBLIC/PRIVATE/INTERFACE

这是现代 CMake 的关键机制，决定依赖如何沿图传播：

- `PRIVATE`：只影响当前 target 的编译，不传播给依赖者
- `PUBLIC`：既影响当前 target，也传播给依赖者
- `INTERFACE`：只传播给依赖者（自己不需要/自己不编译）

示例：
```cmake
add_library(core core.cpp)
target_include_directories(core PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)

add_library(utils utils.cpp)
target_link_libraries(utils PUBLIC core)     # utils 依赖 core，并把 core 的接口继续传下去

add_executable(app main.cpp)
target_link_libraries(app PRIVATE utils)     # app 得到 utils 的接口，也会传递得到 core 的接口
```
**类比 Bazel：**

- CMake 的 `target_link_libraries(... PUBLIC ...)` ≈ Bazel `deps = [...]`（依赖传播）
    
- CMake 的 `PRIVATE` ≈ Bazel `implementation_deps`（只本目标可见，不传播）
    
- CMake 的 `INTERFACE` ≈ Bazel 的纯接口库/工具库（自己不产出编译对象，只提供编译信息）

# 2 CMake操作清单

## 2.1 指定源文件 `target_sources`

比 `add_library(xxx a.cpp b.cpp)` 更可维护，支持按条件/按平台追加：

```
add_library(mylib)
target_sources(mylib
  PRIVATE
    src/a.cpp
    src/b.cpp
  PUBLIC
    include/mylib/api.h
)

```
**要点**：源文件属于 target，这就是“对象依赖哪些源文件”的入口。

**Bazel 类比：**

- `target_sources(mylib ...)` ≈ `cc_library(name="mylib", srcs=[...], hdrs=[...])`

## 2.2 include 路径：`target_include_directories`

```
target_include_directories(mylib
  PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
  PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)

```
**Bazel 类比：**

- Bazel 推荐通过 `hdrs` + `includes`/`strip_include_prefix`/`include_prefix` 来控制可见头路径
    
- CMake 通过 PUBLIC/PRIVATE 控制 include 是否传播

## 2.3 编译选项与宏：`target_compile_options` / `target_compile_definitions`

```
target_compile_options(mylib PRIVATE -Wall -Wextra)
target_compile_definitions(mylib PUBLIC MYLIB_ENABLE_FOO=1)

```
**Bazel 类比：**

- `copts = [...]`，`defines = [...]`

## 2.4 链接依赖：`target_link_libraries`

```
target_link_libraries(app
  PRIVATE
    mylib
    Threads::Threads
)
```
注意：现代 CMake 不建议直接写 `-lxxx`，而是**尽量链接 target**，因为 target 携带了依赖信息（include/defs/options/link flags）。

**Bazel 类比：**

- `deps = [...]` 或 `linkopts = [...]`（CMake 的 target 化更像 deps）

## 2.5 查找第三方：`find_package` / imported targets

 `find_package`，本质是在引入**预定义的“外部 target”**（Imported Target）。

例如 OpenCV：

```
find_package(OpenCV REQUIRED)
target_link_libraries(app PRIVATE opencv_core opencv_imgproc)
```

更现代的包会提供 `OpenCV::opencv_core` 这种命名空间 target：

`target_link_libraries(app PRIVATE OpenCV::opencv_core OpenCV::opencv_imgproc)`

**Bazel 类比：**

- Bazel 用 `@repo//:target` 的外部仓库依赖
    
- CMake 用 `find_package` + `FooConfig.cmake` 或 `FindFoo.cmake`，通常依赖系统安装/自定义前缀路径

## 2.6 生成代码/文件依赖: ### `add_custom_command` + `add_custom_target`

当某个源文件不是静态存在，而是“生成出来”的，CMake 可以显式建模

```
add_custom_command(
  OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/gen/foo.pb.cc ${CMAKE_CURRENT_BINARY_DIR}/gen/foo.pb.h
  COMMAND protoc --cpp_out=${CMAKE_CURRENT_BINARY_DIR}/gen ${CMAKE_CURRENT_SOURCE_DIR}/proto/foo.proto
  DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/proto/foo.proto
  VERBATIM
)

add_library(proto_lib)
target_sources(proto_lib PRIVATE ${CMAKE_CURRENT_BINARY_DIR}/gen/foo.pb.cc)
target_include_directories(proto_lib PUBLIC ${CMAKE_CURRENT_BINARY_DIR}/gen)

```
这样 **proto_lib 明确依赖 foo.proto**，并且生成物成为编译输入。

**Bazel 类比：**

- Bazel 的 rule 天然就是这种“声明式生成”（`genrule` / `proto_library`）
    
- CMake 需要你手写 command/target，但同样能形成依赖图

# 3 “依赖图”到底谁更强：CMake vs Bazel

### 3.1.1 Bazel 的强项

- **依赖必须显式声明**：不允许“偷偷 include 但没 deps”
    
- **可复现构建（reproducible）更强**：更少依赖系统环境
    
- **缓存与远程构建**：增量速度和 CI 扩展性很强
    
- **沙盒化**：依赖缺失会更早暴露
    

## 3.2 CMake 的强项

- **生态/集成广**：与系统包管理、IDE、各类工具链适配成熟
    
- **迁移成本低**：传统项目更容易渐进式改造
    
- **生成器模式**：可以输出 Ninja/Makefile/VS 工程，方便本地调试
    
- **target 传递属性**：现代写法下依赖图也可以很清晰
    

## 3.3 关键差异：依赖“约束力度”

|维度|CMake（默认）|Bazel（默认）|
|---|---|---|
|依赖声明|可以显式，也可以“偷懒”靠全局 include/link|强制显式（规则驱动）|
|可复现性|受系统环境影响较大（除非你做 toolchain/包管理）|更强（外部依赖受控）|
|生成规则|手写 custom command/target|rule 天生支持生成链|
|增量/缓存|Ninja 增量很好，但跨机器缓存不如 Bazel|远程缓存是核心能力|
|IDE 体验|非常好（VS/CLion 等）|依赖插件/集成，逐步改善|

一句话：**Bazel 更像“严格的构建编译器”，CMake 更像“跨平台构建生成器”**

## 3.4 对照示例

**Bazel**
```
cc_library(
  name = "core",
  srcs = ["core.cpp"],
  hdrs = ["core.h"],
  deps = ["@opencv//:core"],
)

cc_binary(
  name = "app",
  srcs = ["main.cpp"],
  deps = [":core"],
)

```
**CMake**
```
add_library(core)
target_sources(core PRIVATE core.cpp PUBLIC core.h)

find_package(OpenCV REQUIRED)
target_link_libraries(core PUBLIC opencv_core)

add_executable(app main.cpp)
target_link_libraries(app PRIVATE core)

```