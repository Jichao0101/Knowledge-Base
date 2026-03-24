
Bazel是google的开源构建工具，使用BUILD文件和WORKSPACE文件来定义构建规则和依赖关系
# 1 基本概念
- BUILD文件：指定如何构建目标（Target）
- Package：BUILD文件所在的目录及其所有子目录（不包含BUILD文件）
- LABEL：唯一标识Bazel构建的目标，@repository//package:target
- WORKSPACE文件：定义项目的根目录，并引入外部依赖，类似CmakeLists.txt
# 2 BUILD文件语法
BUILD文件由目标、规则、依赖构成
```
cc_library(
    name = "exam_lib",
    srcs = ["lib.cpp"],
    hdrs = ["lib.h"],
    deps = ["//third_party:some_dep"]
)    

```
## 2.1 目标
exam_lib为目标名称
## 2.2 规则
规则定义如何构建不同类型的目标
### 2.2.1 c++规则
- cc_binary：编译c/c++可执行文件
- cc_library：编译c/c++静态或动态库
- cc_test:编译c/c++测试
### 2.2.2 python规则
- py_binary, 
- py_library
- py_test
### 2.2.3 通用规则
- filegroup:聚合多个文件，供其他目标依赖，只定义文件集合，不编译
```
file_group(
    name = "cyber_conf",
    srcs = glob(["conf/*.conf"])
)

pkg_tar(
    name = "config_tar",
    srcs = [":cyber_conf"],
    package_dir = "conf",
)
```

- genrule:运行自定义命令生成文件
- sh_binary:运行shell脚本
- sh_test:运行shell测试
## 2.3 依赖
Bazel的依赖关系可以是本地目标、其他package、WORKSPACE中定义的外部依赖
### 2.3.1 本地目标
```
deps = [":some_lib"]
```

### 2.3.2 其他package
```
deps = ["//path/to/package:target"]
```

### 2.3.3 外部依赖
WORKSPACE中定义
```
http_archive(
    name = "rules_python",
    url = 
["https://github.com/bazelbuild/rules_python/release/rules_python-1.10.1.tar.gz"],
    sha256 = "xxxxxx"
)

```
BUILD文件中引用
```
deps = ["@rules_python//:py_deps"]
```

## 2.4 其他语法
### 2.4.1 visibility用法
```
cc_library(
    name = "internal_lib",
    srcs = ["internal.cpp"],
    hdrs = ["internal.h"],
    visibility  = ["//project:__subpackages__"],
)

```
控制其他Bazel包是否可以访问当前目标，避免未授权的依赖

| 值                         | 说明                               |
| ------------------------- | -------------------------------- |
| //visibility:public       | 任何包都可以访问                         |
| //visibility:private      | 仅BUILD文件所在的package可访问            |
| //project:__subpackages__ | 仅project/及其子package可访问           |
| //project:some_lib        | 仅project/some_lib package可访问<br> |

### 2.4.2 glob用法
glob()运行在BUILD文件中使用通配符指定文件列表
```
srcs = glob(["src/*.cpp"]) #匹配src目录下的所有cpp文件
srcs = glob(["src/**/*.cpp"]) #递归匹配所有子目录下的cpp文件
srcs = glob(["src/**/*.cpp"], exclude = ["src/legacy/*.cpp"]) #排除某些文件
```

### 2.4.3 config_setting+select()
config_setting用于定义构建条件，以便select()选择不同的依赖项、编译选项或目标。它不会直接构建任何目标，当bazel build指定的配置符合config_setting的values，该config_setting被激活，例如bazel build --cpu=aarch64  //my_package:my_target
```
confing_setting(
    name = "x86_mode",
    values = {"cpu":"k8"}  #当cpu为x86(k8)时，匹配x86_mode
)
config_setting(
    name = "arm_mode",
    values = {"cpu":"aarch64"} #当cpu为ARM时，匹配arm_mode
)
```

select()基于config_setting动态选择依赖、编译参数，同样不会创建新目标
```
cc_library(
    name = "cyber_core_dev_lib",
    deps = select({
        ":x86_mode":["cyber_core_dev_lib_x86"],
        ":arm_mode":["cyber_core_dev_lib_arm"]
    })
)
```

# 3 WORKSPACE文件语法
定义Bazel项目的根目录，并指定外部依赖
1. workspace(name) 设置工作区名称
2. load()导入Starlark规则
```
load("@rules_python//python:pip.bzl", _pip_install = "pip_install")
```

_pip_install是导入的别名
3. http_archive加载外部库,用于Bazel官方库，已包含BUILD文件
```
http_archive(
    name = "rules_python",
    url = 
["https://github.com/bazelbuild/rules_python/release/rules_python-1.10.1.tar.gz"],
    sha256 = "xxxxxx"，
    strip_prefix = "rules_python-1.10.1",
)

```
4. new_http_archive用于下载第三方库，没有Bazel的BUILD文件
```
new_http_archive(
    name = "boost",
    url = "https://boost.org/boost_1_75_0.tar.gz",
    strip_prefix = "boost_1_75_0",
    build_file = "@//third_party:boost.BUILD",
    sha256 = "xxxxx",
)
```

在third_party/boost.BUILD中定义
```
cc_library(
    name = "boost",
    srcs = glob(["boost/**/*.cpp"]),
    hdrs = glob(["boost/**/*.h"]),
    includes = ["boost"],
    visibility = ["//visibility:public"],
)
```

使用时在BUILD文件中引用
```
cc_library(
    name = "my_project",
    srcs = ["my_project.cpp"],
    deps = ["@boost//:boost"],
)

```
5. git_repository从git仓库拉取依赖
```
git_repository(
    name = "some_library",
    remote = "https://github.com/example/some_library.git",
    branch = "main",
)

```
6. local_repository使用本地目录作为依赖
```
local_repository(
    name = "my_local_repo",
    path = "/path/to/repo",
)
```

7. new_local_repository
WORKSPACE
```
new_local_repository(
    name = "protobuf",
    path = "/home/user/protobuf",
    build_file = "@//third_party:protobuf.BUILD"
)

```
third_party/protobuf.BUILD
```
cc_library(
    name = "protobuf",
    srcs = glob(["src/**/*.cpp"]),
    hdrs = glob(["include/**/*.h"]),
    includes = ["include"],
    linkopts = ["-Llib", "-lprotobuf"],
    visibility = ["//visibility:public"]
)
```
my_project/BUILD使用protobuf
```
proto_library(
    name = "my_proto",
    srcs = ["proto/my_message.proto"],
)


cc_proto_library(
    name = "my_cc_proto",
    deps = [":my_proto", "@protobuf//:protobuf"],
)

cc_binary(
    name = "my_app",
    srcs = ["src/main.cpp"],
    deps = [":my_cc_proto", "@protobuf//:protobuf"]
)
```
Bazel提供了rules_proto作为protoc生成.pb.cc的工具链，无需protobuf依赖。但是如果使用本地protobuf库或手动调用了protobuf相关API，则需要手动添加protobuf依赖