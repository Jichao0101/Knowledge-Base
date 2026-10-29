---
type: knowledge
status: legacy_structured
domain: Docker
summary: Dockerfile、镜像、容器和归档的关系，以及通用构建与交付边界；按 SDK 开发与模型训练场景分流。
sources:
  - 从原 Docker 条目迁移的已整理内容
  - "[[04_Sources/模型工程/2026-10-29_Docker与训练环境固化_来源及修订记录]]"
scope: Docker 通用概念、构建说明与镜像交付；具体环境组成和验收由场景文档负责。
risks:
  - 镜像可加载不等于目标应用已验证；Dockerfile 也不单独保证重建一致。
updated_at: 2026-10-29
---

# 1 Docker 镜像基础与构建交付

Docker 的构建和运行机制可以用于多种任务，但不同任务需要固化的内容不同。先在本文理解通用对象，再按目标进入对应场景：

| 读者目标 | 阅读位置 |
|---|---|
| 在供应商 SDK 上增加编译、调试和开发工具 | [[01_Knowledge/Docker/基于基础镜像构建开发镜像]] |
| 把已验证的模型训练环境固化为可交付镜像 | [[01_Knowledge/模型/方法与流程/模型训练与环境固化流程]] |

## 1.1 从 Dockerfile 到镜像，再到容器

Docker 是构建和运行容器的工具体系。Dockerfile 是文本形式的构建说明；image（镜像）是按说明构建出的文件系统层与运行配置；container（容器）是从镜像创建的运行实例。同一个镜像可以创建多个容器。

| 对象 | 保存的内容 | 在流程中的用途 |
|---|---|---|
| Dockerfile | 基础镜像、安装步骤、复制文件、工作目录和默认命令等指令 | 说明如何构建 |
| 镜像 image | 应用、依赖、文件系统层及运行配置 | 作为创建容器的输入 |
| 容器 container | 基于镜像的可写层、进程状态及挂载配置等 | 实际执行开发、训练或服务 |
| 镜像归档 `.tar` | 按镜像归档格式保存的镜像内容 | 在机器之间传递或备份镜像 |

```text
Dockerfile + 构建上下文 ── docker build ──> 镜像 ── docker run ──> 容器
                                             │
                                        docker save
                                             ↓
                                         镜像归档
                                             │
                                        docker load
                                             ↓
                                      另一台机器上的镜像
```

“构建上下文”是构建时可供 Dockerfile 使用的文件集合，通常由 `docker build` 最后的路径指定。镜像已经是产物，使用已有镜像不要求同时拥有其原始 Dockerfile；但要解释或重建环境，就需要保留构建说明和相应输入。

`.tar` 只是归档格式，普通文件备份也能使用这个后缀。是否是可加载的镜像归档，要看导出方式和内部内容，不能仅凭文件名判断。

## 1.2 Dockerfile 如何表达环境变更

开发环境有系统包、Python 依赖和项目代码等不同内容，Dockerfile 可以把它们的安装过程编排在一起。`environment.yml` 或 `requirements.txt` 负责声明依赖，Dockerfile 负责在选定的基础环境中安装这些依赖，两者并不互斥。[Dockerfile reference](https://docs.docker.com/reference/dockerfile/)

先理解最常用的几条指令：

| 指令 | 在示例中的作用 |
|---|---|
| `FROM` | 选择作为起点的基础镜像 |
| `RUN` | 在构建时执行命令，例如安装开发工具 |
| `COPY` | 把构建上下文中的文件复制进镜像 |
| `WORKDIR` | 设置后续相关指令及容器默认工作目录 |
| `USER` | 指定后续指令及容器默认使用的用户 |
| `CMD` | 提供默认启动命令或参数，并与 `ENTRYPOINT` 配合 |

构建时通常通过 `docker build -f Dockerfile -t my-app:1.0 .` 指定 Dockerfile、产物名称和当前目录的构建上下文。使用 `docker image inspect my-app:1.0` 检查运行配置，再通过 `docker run` 创建容器。容器内临时安装的工具不会自动写回原镜像；需要保留的环境变更应进入构建说明和依赖文件。

具体要安装哪些内容，由场景决定：SDK 开发篇演示增加工具，训练篇说明如何保留框架环境、安装项目依赖并固定训练入口。

## 1.3 镜像交付与重建依据

镜像验证后，可以推送到镜像仓库，也可以保存成归档供另一台机器加载。下列镜像名是命令示意：

```bash
docker image save -o my-app-1.0.tar my-app:1.0
docker image load -i my-app-1.0.tar
docker image inspect my-app:1.0
```

`save/load` 用于镜像交付。`export/import` 对应容器文件系统导出与从文件系统归档创建镜像，不能作为等价替换；尤其是 `export` 不包含关联卷里的内容。[save](https://docs.docker.com/reference/cli/docker/image/save/) / [load](https://docs.docker.com/reference/cli/docker/image/load/) / [export](https://docs.docker.com/reference/cli/docker/container/export/) / [import](https://docs.docker.com/reference/cli/docker/image/import/)

镜像能加载，并不代表项目代码、数据集、训练输出和宿主机环境都已交付。挂载的目录需要另行管理，目标机器还需满足架构及运行前提；加载后应重新执行对应场景的基本检查和项目验证。

要保留重建能力，还应把 Dockerfile、依赖文件、项目代码版本与基础镜像身份一起记录。标签可能指向新的镜像，需要严格锁定输入时可使用基础镜像摘要；软件包源和未固定依赖同样会影响重建结果。如果基础镜像和软件包依赖未固定，就不应声称每次构建得到相同产物。[固定基础镜像版本的边界](https://docs.docker.com/build/building/best-practices/#pin-base-image-versions)

## 1.4 来源与迁移说明

本文由原 SDK 开发镜像条目中的通用说明迁出，保持原验证边界，不提升知识状态。迁移关系及官方依据见 [[04_Sources/模型工程/2026-10-29_Docker与训练环境固化_来源及修订记录#2026-10-29 结构重整与 NVIDIA 实例依据]]。
