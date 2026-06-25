---
type: project_current_overview
status: active
scope: CVAT 云端部署项目的当前入口、事实源顺序和未决前提；不替代具体方案、架构和实施手册正文。
updated_at: 2026-06-24
recoverability_status: created_but_not_fully_verified
single_pass_recoverable: false
---

# 1 CVAT 云端部署项目总览 Current

## 1.1 当前结论

CVAT 云端部署按项目内容维护，当前推荐路线是：

- CVAT 作为标注平台部署在 CPU 云桌面宿主机上，由宿主机 Docker daemon 直接管理 Docker Compose project。
- CVAT 不进入模型镜像，不使用 Docker in Docker，不把 CVAT 镜像群当普通目录挂进大容器。
- 数据、模型输出、CVAT share、备份和 manifest 当前放在 NAS 盘；不使用 turbo 作为标注平台持续运行依赖。
- turbo 目前必须通过训练平台新建容器才能访问，不适合作为 CVAT 长期在线平台的直接挂载存储。
- 模型由训练平台 task 启动和管理；当前不是由 CVAT 主动调用模型，也不是模型主动把预标注 API 回写到 CVAT。
- 当前流程是模型完成数据标注后，将结果落到 NAS；CVAT 访问 NAS 中的数据和标注结果，由标注员或审核员人工复核。

## 1.2 当前事实源

默认读取顺序：

1. [[02_Projects/cvat/CVAT云端部署项目总览_current]]
2. [[02_Projects/cvat/CVAT云端部署原理讨论与方案权衡]]
3. [[02_Projects/cvat/CVAT云端部署最终架构与扩展规划_current]]
4. [[02_Projects/cvat/CVAT云端部署实施手册]]
5. [[02_Projects/cvat/cvat_local_deployment]]

本项目组与本地部署旧文档的关系：

- `cvat_local_deployment.md` 是本地部署和早期接入方式参考。
- 云端部署以本 current 文档组为当前入口。
- 若云端方案与本地文档不一致，以云端架构 current 和实施手册为准。

## 1.3 文档职责边界

| 文档 | 职责 | 不负责 |
|---|---|---|
| [[CVAT云端部署原理讨论与方案权衡]] | 解释 Docker、CVAT、NAS/turbo 存储边界、模型任务、Nuclio、网络方案的取舍 | 记录最终生产配置和逐步执行命令 |
| [[CVAT云端部署最终架构与扩展规划_current]] | 记录当前选定架构、系统边界、状态机、manifest 映射和扩展占位 | 展开全部未选方案的历史讨论 |
| [[CVAT云端部署实施手册]] | 记录云端机器准备、Docker/Compose 安装、CVAT clone 或离线拷贝、启动、验证、备份与故障处理 | 重新论证架构取舍 |

## 1.4 适用范围

- CPU 云桌面部署 CVAT Community。
- 训练平台 task 执行模型训练、推理或预标注。
- NAS 作为 CVAT 可持续挂载的数据、模型输出、CVAT share、导出和备份目录。
- CVAT 用于 project、task、job、assignee、annotation、review、export 管理。
- BEV3D、点云、多相机、多传感器、DMS/OMS 等复杂输入优先采用训练平台离线处理、NAS 落盘、CVAT 访问结果并人工复核。

## 1.5 当前未决前提

- 云桌面是否允许宿主机安装并运行 Docker daemon。
- 云桌面是否允许暴露 8080、80 或 443 端口。
- 云端是否能联网拉取 GitHub 和容器镜像；若不能，需要离线包和内网 registry。
- NAS 在云桌面宿主机和 CVAT worker 容器中的挂载权限、性能和容量。
- 训练平台 task 输出到 NAS 的路径规范、结果格式和权限归属。
- CVAT 导入或读取模型结果的具体格式转换方式。
- CVAT 版本、镜像 registry、备份周期和服务账号 token 管理策略。

## 1.6 Recoverability 状态

本 current 文档组已按云端部署项目创建，但尚未完成独立 recoverability verification。

- `recoverability_status: created_but_not_fully_verified`
- `single_pass_recoverable: false`
- 下一步验证：用实施手册在目标云桌面完成一次最小路径部署，并记录命令、版本、端口、NAS share 导入、模型结果读取、人工复核和导出证据。

## 1.7 维护记录

- [[02_Projects/cvat/Current Maintenance Records/CVAT云端部署current文档组创建记录-2026-06-24]]
- [[02_Projects/cvat/Current Maintenance Records/CVAT云端部署NAS与模型结果复核方案更新记录-2026-06-24]]
