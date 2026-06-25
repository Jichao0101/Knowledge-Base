---
type: project_architecture_current
status: active
scope: CVAT 云端部署当前选定架构、系统边界、目录结构、任务状态机、manifest 映射和扩展占位。
updated_at: 2026-06-24
recoverability_status: created_but_not_fully_verified
single_pass_recoverable: false
---

# 1 CVAT 云端部署最终架构与扩展规划 Current

## 1.1 当前架构结论

CVAT 云端部署采用以下架构：

- CPU 云桌面宿主机运行 Docker daemon。
- Docker daemon 直接管理 CVAT Docker Compose project。
- CVAT Compose project 包含 `cvat_server`、`cvat_ui`、PostgreSQL、Redis、Traefik/Gateway、worker，以及可选 Nuclio。
- NAS 作为标注平台持续运行可挂载的数据层，提供数据、模型输出、manifest、CVAT share、导入导出和备份。
- 模型完成处理后将标注结果落到 NAS，CVAT 访问数据和结果并由人工复核。
- dispatcher 或脚本只负责 manifest、CVAT project/task/job、结果导入和导出闭环，不负责占用算力卡维持平台服务。

## 1.2 总体架构图

```text
                    标注员 / 审核员
                         |
                         v
              http://<cpu-desktop>:8080
                         |
+--------------------------------------------------+
| CPU 云桌面宿主机                                 |
|                                                  |
|  Docker daemon / dockerd                         |
|    |                                             |
|    +-- CVAT Compose project                      |
|        |-- traefik / gateway                     |
|        |-- cvat_ui                               |
|        |-- cvat_server                           |
|        |-- cvat_worker_import/export/...         |
|        |-- postgres                              |
|        |-- redis                                 |
|        `-- optional nuclio                       |
|                                                  |
|  /nas/cvat-share -> /home/django/share:ro        |
+--------------------------------------------------+
          |
          | 读写数据 / manifest / 模型结果
          v
+-------------------+       +-----------------------------+
| NAS 数据层         | <---- | 训练平台 task / 模型容器      |
| /datasets          |       | 由训练平台按需新建和回收       |
| /model-results     |       | 可访问训练数据环境    |
| /annotations       |       | 输出标注结果到 NAS             |
| /cvat-share        |       +-----------------------------+
| /cvat-backups      |
| /manifests         |
+-------------------+
          ^
          |
+-------------------+
| dispatcher / script|
| 读 manifest         |
| 建 project/task/job |
| 分配 assignee       |
| 导入模型结果        |
| 导出复核结果        |
+-------------------+
```

## 1.3 部署分层

| 层 | 组件 | 责任 |
|---|---|---|
| CVAT 平台层 | CVAT Compose project、PostgreSQL、Redis、Gateway、worker | 标注平台、任务、人工修正、审核、导入导出 |
| NAS 数据层 | `/nas/datasets`、`/nas/model-results`、`/nas/annotations`、`/nas/cvat-share`、`/nas/cvat-backups`、`/nas/manifests` | 数据、模型输出、CVAT share、备份和 manifest |
| 模型处理层 | 训练平台 task、按需创建的模型容器、推理脚本、结果转换脚本 | 加载模型、访问训练/推理数据环境、生成标注结果并落盘到 NAS |
| 任务调度层 | dispatcher 或脚本、manifest reader、CVAT API client、导入导出脚本 | 创建任务、拆 job、分配、导入模型结果、推进人工复核、导出 |

## 1.4 推荐 NAS 目录结构

```text
/nas
  /datasets
    /<project_key>
      /<batch_id>
        /images
        /videos
        /pointcloud
        /calibration
        /ego_pose
  /model-results
    /<project_key>/<batch_id>
      /raw
      /cvat-import
  /annotations
    /model/<project_key>/<batch_id>
    /intermediate/<project_key>/<batch_id>
    /export/<project_key>/<batch_id>
  /cvat-share
    /<project_key>/<batch_id>
  /cvat-backups
    /postgres
    /exports
  /manifests
    /<project_key>/<batch_id>.json
```

## 1.5 系统职责边界

| 系统 | 权威事实 | 不应承担 |
|---|---|---|
| CVAT | project、task、job、assignee、stage、state、annotation、review、export | 模型运行环境、GPU 调度、NAS/turbo 数据生命周期 |
| NAS | 数据路径、模型输出路径、manifest、导入导出文件、备份文件 | 标注任务状态权威、权限分配、运行中的服务组 |
| 训练平台 task / 模型容器 | 推理结果、预标注中间文件、可导入 CVAT 的结果文件 | 标注平台状态机、审核、人工分配、CVAT 长期服务 |
| dispatcher / script | 编排记录、manifest 到 CVAT 的映射、结果导入、导出闭环 | 直接改 CVAT 数据库、长期占用算力卡运行平台 |

## 1.6 任务状态机

```text
created
  -> pre_annotating
  -> pre_annotated
  -> assigned
  -> annotating
  -> reviewing
  -> accepted
  -> exported
```

失败和返工分支：

```text
pre_annotating -> prelabel_failed -> pre_annotating
annotating     -> rework_required  -> annotating
reviewing      -> rejected         -> annotating
exported       -> archived
```

状态权威建议：

| 状态域 | 权威系统 |
|---|---|
| CVAT task/job/assignee/stage/state/annotation | CVAT |
| batch 原始数据和路径 | NAS manifest |
| 模型预标注运行状态 | 训练平台 task 日志与模型输出目录 |
| 最终导出路径 | dispatcher 或脚本与 `/nas/annotations/export` |

## 1.7 CVAT 与 manifest 映射

manifest 建议记录 batch、frame、timestamp、calibration、原始路径和 CVAT task/job 映射：

```json
{
  "project_key": "project_x",
  "batch_id": "batch_0001",
  "data_root": "/nas/datasets/project_x/batch_0001",
  "cvat_share_path": "/home/django/share/project_x/batch_0001/images",
  "labels": ["car", "pedestrian", "cyclist"],
  "frames": [
    {
      "frame_index": 0,
      "timestamp": 1710000000.123,
      "image": "images/front/000000.jpg",
      "pointcloud": "pointcloud/000000.pcd",
      "calibration": "calibration/000000.json",
      "ego_pose": "ego_pose/000000.json"
    }
  ],
  "cvat": {
    "project_id": 10,
    "task_id": 123,
    "jobs": [
      {
        "job_id": 456,
        "frame_start": 0,
        "frame_stop": 499,
        "assignee": "annotator_a",
        "state": "pre_annotated"
      }
    ]
  },
  "prelabel": {
    "model": "bev3d",
    "version": "v1",
    "output": "/nas/model-results/project_x/batch_0001/cvat-import/task_123.json",
    "import_status": "ready_for_manual_review"
  }
}
```

## 1.8 dispatcher 职责

dispatcher 或脚本是云端标注流程的编排层，至少承担：

1. 读取 `/nas/manifests`。
2. 校验数据、标定、timestamp、路径和 label schema。
3. 调用 CVAT API 创建 project/task。
4. 将 CVAT task/job id 写回 manifest 或编排数据库。
5. 按规则拆分 job 并分配给标注员。
6. 读取训练平台 task 已落盘的模型结果。
7. 将模型结果转换为 CVAT 可导入格式，或记录为人工复核输入。
8. 导入结果后推进人工复核状态。
9. 触发导出并写入 `/nas/annotations/export`。
10. 记录审计日志。

dispatcher 不直接修改 CVAT PostgreSQL。

## 1.9 模型结果读取与人工复核流程

```text
dispatcher 读取 manifest
  -> 创建 CVAT project/task/job
  -> 写回 task_id/job_id 映射
  -> 训练平台 task 启动模型容器
  -> 模型访问训练平台可见的数据和权重
  -> 模型输出 detections.json / tracks.json / cvat-import 文件到 /nas/model-results
  -> 转换为 CVAT shapes/tracks/tags
  -> CVAT 通过 share、导入脚本或 API 读取模型结果
  -> dispatcher 标记 ready_for_review
  -> 标注员人工修正
  -> 审核员 validation / acceptance
  -> 导出最终标注到 /nas/annotations/export
```

## 1.10 网络设计

### 1.10.1 同一云桌面宿主机

```text
browser         -> http://<host-ip>:8080
CVAT containers -> compose internal network
CVAT workers    -> /home/django/share -> /nas/cvat-share
```

### 1.10.2 CVAT 在 CPU 云桌面，模型在 GPU 节点

```text
training task / model container -> 写出模型结果到 NAS
CVAT                         -> CPU 云桌面宿主机
NAS                          -> CVAT 持续挂载的数据层
```

## 1.11 扩展规划占位

### 1.11.1 CVAT 主动调用模型服务

保留为后续扩展，不作为当前主路径。前置条件：

- 模型服务 IP/端口稳定，或有服务发现。
- 有统一网关、鉴权、超时、重试和并发控制。
- 模型输入输出 schema 稳定。
- GPU 节点调度和资源隔离明确。

### 1.11.2 Nuclio 自动标注

保留为 UI 内点击自动标注的后续方案，不作为当前主路径。适用前提：

- 模型输入输出稳定。
- 数据可以通过 CVAT job context 或外部服务可靠定位。
- 超时和批处理策略明确。
- GPU runtime 接入完成验证。

### 1.11.3 K8s 或云原生部署

当单台云桌面无法满足并发、可用性或运维要求时再评估。当前 Compose 方案优先满足 MVP 和小规模生产验证。

## 1.12 当前验证缺口

- 尚未在目标云桌面完成 Docker daemon 权限验证。
- 尚未确认端口暴露和跨节点网络策略。
- 尚未完成 NAS 在 CVAT server/worker 容器内的只读/读写挂载验证。
- 尚未确认训练平台 task 写出模型结果到 NAS 的权限、目录规范和结果格式。
- 尚未完成一次模型结果导入 CVAT 后人工复核的端到端验证。
- 尚未完成 CVAT DB 备份恢复演练。
