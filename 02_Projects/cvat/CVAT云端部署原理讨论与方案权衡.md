---
type: project_design_discussion
status: active
scope: CVAT 云端部署的原理讨论、方案取舍和未选方案风险；不作为最终部署命令手册。
updated_at: 2026-06-24
source:
  - 用户提供的云端模型部署流程和 CVAT 部署目标
  - 02_Projects/cvat/cvat_local_deployment.md
  - CVAT 官方安装、share path、SDK 文档
  - Docker 官方架构文档
---

# 1 CVAT 云端部署原理讨论与方案权衡

## 1.1 结论摘要

推荐方案是：CVAT 在 CPU 云桌面宿主机上通过 Docker Compose 独立部署，标注平台持续挂载 NAS 作为数据和结果共享层；模型由训练平台 task 按需启动，处理完成后把标注结果写入 NAS，CVAT 再读取数据和结果并由人工复核。

明确不推荐：

- 不使用 Docker in Docker 部署 CVAT。
- 不把 CVAT 镜像群塞进模型镜像。
- 不把 Docker 镜像群当作普通目录挂载到大容器中。
- 初期不把 Nuclio 作为复杂模型自动标注的主路径。
- 不把 turbo 作为 CVAT 在线平台的持续挂载依赖。
- 不把模型 API 回写或 CVAT 主动调用模型作为当前主路径。

## 1.2 Docker daemon、CLI 与 Compose 的边界

Docker daemon 是宿主机上的 `dockerd` 服务，负责管理镜像、容器、网络、volume、端口映射、cgroup、namespace 和 overlayfs 等运行态资源。

`docker` CLI 与 `docker compose` 是客户端：

```text
docker / docker compose
        |
        v
Docker API
        |
        v
dockerd
        |
        v
images / containers / networks / volumes / ports
```

因此，CVAT Compose project 应由云桌面宿主机 Docker daemon 直接管理。这样 `docker compose ps`、`docker compose logs`、端口映射、volume 挂载、备份和升级都落在宿主机可见的运维边界内。

## 1.3 方案对比

| 方案 | 优点 | 主要问题 | 结论 |
|---|---|---|---|
| 宿主机 Docker Compose 部署 CVAT | 架构清晰，符合 CVAT 官方部署方式，端口和 volume 可控 | 依赖云桌面宿主机 Docker 权限 | 推荐 |
| Docker in Docker 部署 CVAT | 表面上便于把环境封装进一个容器 | daemon 嵌套、volume/网络/GPU/安全复杂 | 不推荐 |
| CVAT 与模型合并成大镜像 | 初看像“一键启动” | CVAT 平台生命周期和模型生命周期强耦合，升级困难 | 不推荐 |
| turbo 挂载 Docker 镜像群 | 文件层面可见 | 不能获得运行中的 daemon、network、volume、service | 不成立 |
| CVAT 直接挂载 turbo 作为在线数据层 | 可复用训练侧数据 | 当前必须通过训练平台新建容器访问，会让标注平台持续运行依赖算力容器 | 不推荐 |
| CVAT 挂载 NAS 作为在线数据层 | 平台可持续运行，不占用算力卡容器，适合 share、导出和备份 | 需要确认 NAS 权限、性能和目录规范 | 推荐 |
| CVAT + Nuclio 初期接入模型 | UI 内可点击自动标注 | 输入输出接口、超时、GPU、复杂传感器数据处理门槛高 | 后续扩展 |
| 模型容器主动调用 CVAT API | 模型运行独立，网络方向简单，适合异步批处理 | 需要 token、网络、回写脚本和 schema 稳定 | 后续可选 |
| 训练平台 task 输出结果到 NAS，CVAT 导入后人工复核 | 不占用算力卡维持平台服务，边界清晰，符合当前训练平台访问 turbo 的限制 | 需要结果格式转换和人工复核流程 | 当前推荐 |

## 1.4 为什么不推荐 Docker in Docker

Docker in Docker 会把 CVAT Compose project 放进内层 Docker daemon，带来多层运行边界：

| 维度 | 风险 |
|---|---|
| daemon | 内外两层 daemon 状态分裂，宿主机无法直接看到完整 CVAT Compose project |
| cgroup | 资源限制、OOM、GPU 资源分配和进程回收行为更难预测 |
| namespace | 网络、PID、mount namespace 嵌套后故障定位困难 |
| overlayfs | overlay 嵌套 overlay，性能、兼容性和磁盘清理风险高 |
| volume | 内层 volume 的真实落点不直观，备份和迁移容易漏数据 |
| network | 双层 NAT 和端口映射使 CVAT UI/API/模型互访复杂 |
| 安全权限 | DinD 常要求 privileged，扩大宿主机攻击面 |
| GPU runtime | NVIDIA runtime、驱动、device 暴露和容器内调度复杂 |
| 运维 | `docker compose ps/logs/down` 的观察对象不再是实际宿主边界 |

云端部署 CVAT 的目标是稳定运行标注平台，不是把平台藏进模型容器。只要宿主机允许 Docker daemon，就应直接在宿主机运行 CVAT Compose project。

## 1.5 NAS 与 turbo 的职责边界

NAS 是当前 CVAT 在线平台的数据层，turbo 只在训练平台 task 需要访问训练侧资源时使用。二者都不是平台运行时：

```text
NAS 当前提供：
- 原始数据
- 模型输出结果
- CVAT share 导入目录
- manifest
- 导出结果
- 备份文件

turbo 当前限制：
- 必须通过训练平台新建容器访问
- 不适合作为 CVAT 长期在线服务的直接挂载依赖
- 不应为了标注平台持续运行而占用算力卡容器

NAS / turbo 都不能提供：
- Docker daemon
- CVAT 正在运行的服务组
- CVAT 容器网络
- CVAT 端口映射
- CVAT 任务分配状态权威
```

挂载 `/nas/cvat-share` 到 CVAT 只表示 CVAT server/worker 能从该目录导入数据。它不等于挂载 Docker daemon，也不等于拥有 CVAT 镜像群或运行中的 CVAT 服务。

## 1.6 CVAT 与模型职责边界

| 系统 | 管什么 | 不管什么 |
|---|---|---|
| CVAT | project、task、job、assignee、annotation、review、export | 模型训练环境、GPU 调度、复杂模型依赖 |
| 训练平台 task / 模型容器 | 加载权重、读取训练侧数据、执行推理、生成模型标注结果并写入 NAS | 标注员分配、审核状态、平台数据库、CVAT 长期服务 |
| dispatcher / 导入脚本 | 读 manifest、建任务、分 job、导入模型结果、推进人工复核、导出 | 直接修改 CVAT DB、长期占用算力卡 |
| NAS | 数据、模型输出、manifest、导入导出、备份 | 任务系统、权限系统、运行时编排 |
| turbo | 训练平台 task 可访问的训练侧数据或资源 | CVAT 在线平台的持续挂载存储 |

## 1.7 模型结果导入、Nuclio 与 API 回写的取舍

Nuclio 适合输入输出简单、模型服务接口稳定、确实需要在 CVAT UI 中点击自动标注的场景。对于 BEV3D、点云、多相机、多传感器、DMS/OMS 等复杂输入，初期直接接 Nuclio 会提前承担以下复杂度：

- 多源数据同步。
- calibration、ego pose、timestamp 对齐。
- 3D box schema 和坐标系转换。
- GPU 显存、超时、并发和批处理。
- CVAT UI 调用模型服务时的错误反馈和重试策略。

因此当前推荐三阶段：

1. 训练平台 task 离线推理并把模型结果写入 NAS。
2. CVAT 读取或导入模型结果，标注员和审核员人工复核。
3. 输入输出、网络和鉴权稳定后，再评估 API 回写、Nuclio 或 CVAT 主动调用模型服务。

## 1.8 网络方案权衡

### 1.8.1 同一云桌面宿主机

当前不要求模型容器和 CVAT 位于同一宿主机，也不要求模型容器访问 CVAT API。CVAT 只需要能访问 NAS：

```text
browser         -> http://<host-ip>:8080
CVAT containers -> compose internal network
CVAT workers    -> /home/django/share -> /nas/cvat-share
```

优点是部署简单，缺点是 GPU 资源可能不足。

### 1.8.2 CVAT 在 CPU 云桌面，模型在 GPU 节点

跨节点时推荐通过 NAS 交接模型结果：

```text
training task / model container -> NAS model-results
CVAT UI/API                    -> CPU desktop host
NAS                            -> shared storage for CVAT
turbo                          -> training platform task only
```

需要确认：

- 训练平台 task 能把模型结果写入约定 NAS 路径。
- CVAT server/worker 能读取 NAS share 和结果目录。
- label schema、annotation schema、坐标系和结果转换脚本明确。
- 若后续改为 API 回写，再补 CVAT URL、防火墙、token、TLS、超时和重试策略。

### 1.8.3 CVAT 主动调用模型容器

CVAT 主动调用模型容器适合后续扩展，但需要稳定解决：

- 模型容器 IP/端口稳定性。
- 服务发现或网关。
- 鉴权和访问控制。
- 超时、并发、重试和队列。
- GPU 节点动态调度。
- 模型接口版本和错误返回格式。

## 1.9 当前取舍

当前选择“CVAT Compose 平台 + NAS 数据层 + 训练平台模型任务 + 模型结果导入 + 人工复核”的原因：

- 平台边界清晰。
- 可从最小路径验证，不被 Nuclio 和 DinD 提前放大复杂度。
- 适合复杂传感器输入。
- 模型镜像和 turbo 访问沿用现有训练平台 task 流程。
- CVAT 持续运行不需要占用算力卡或训练容器。
- CVAT 保持标注平台角色，专注任务分配、人工修正、审核、状态和导出。
