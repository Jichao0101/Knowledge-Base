# 1 CVAT 本地部署说明

> 适用场景：在本机、内网服务器或开发机上部署 CVAT Community，用于图像、视频、点云/3D 标注，以及后续接入预标注模型。


---

## 1.1 部署目标

本说明覆盖三种部署层级：

| 层级 | 目标 | 适用情况 |
|---|---|---|
| 基础版 | 启动 CVAT Web 服务 | 手工标注、数据查看、任务管理 |
| 自动标注版 | 启动 CVAT + Nuclio serverless | 使用内置/自定义预标注模型 |
| GPU 自动标注版 | Nuclio 函数可访问 NVIDIA GPU | 部署 YOLO、SAM、BEV/3D 模型等较重模型 |

---

## 1.2 前置依赖

### 1.2.1 必须安装

| 依赖 | 说明 |
|---|---|
| Git | 拉取 CVAT 源码 |
| Docker Engine / Docker Desktop | 运行 CVAT 容器 |
| Docker Compose v2 | 使用 `docker compose` 命令编排容器 |
| Chromium 系浏览器 | 推荐 Chrome 或 Edge |

检查命令：

```bash
git --version
docker --version
docker compose version
```

如果没有安装`docker impose`
```
sudo apt install docker-compose-pluginl 
```

如果是在 Windows 上部署，建议使用：

```text
Windows 11 + WSL2 + Docker Desktop
```

注意：CVAT 服务跑在 Docker 里，但数据卷、端口映射和 GPU 访问仍然依赖宿主机配置。

---

## 1.3 基础版 CVAT 部署

### 1.3.1 拉取源码

```bash
git clone https://github.com/cvat-ai/cvat.git
```

建议固定一个稳定 release，而不是一直使用 develop/main：

```bash
git tag --sort=-creatordate | head
git checkout v2.xx.x
```

如果不确定版本，可以先用默认分支验证流程。

---

### 1.3.2 可选：设置访问 Host

本机访问可以不设置：

```bash
# 本机访问时通常不需要
# export CVAT_HOST=localhost
```

如果要从局域网其他机器访问，建议设置为服务器 IP 或域名：

```bash
export CVAT_HOST=192.168.1.100
```


---

### 1.3.3 安装 CVAT

读取 docker-compose.yml，检查镜像，创建容器并启动服务
```bash
cd cvat
docker compose up -d
```

查看Compose 启动的服务容器状态，包括容器名、状态、端口映射等

```bash
docker compose ps
```


---

### 1.3.4 启动CVAT

- 如果是第一次使用，需要创建账号

```bash
docker exec -it cvat_server bash -ic 'python3 ~/manage.py createsuperuser'
```

按提示输入用户名、邮箱和密码。

- 启动CVAT

```
docker exec -it cvat_server bash
```

默认访问地址：

```text
http://localhost:8080
```

如果部署在服务器上：

```text
http://<服务器IP>:8080
```

---

## 1.4 停止、重启与清理

### 1.4.1 停止服务但保留数据

```bash
docker compose down
```

### 1.4.2 重新启动

```bash
docker compose up -d
```


### 1.4.3 清理容器但保留 volume

```bash
docker compose down
```

### 1.4.4 危险操作：删除所有 CVAT 数据

只有在明确要重装时执行：

```bash
docker compose down -v
```

这会删除 PostgreSQL、Redis、CVAT 数据卷等持久化数据。

---

## 1.5 BEV3D / 自定义预标注模型推荐接入方式

对于 BEV3D、点云、多相机融合、DMS/OMS 等车载数据，不建议一开始就强行嵌入 CVAT serverless。推荐三阶段：

### 1.5.1 第一阶段：离线推理 + 标注导入

```text
原始数据
  ├── image / video / point cloud
  ├── calibration
  ├── timestamp
  └── ego pose
        ↓
自定义推理脚本
        ↓
detections.json
        ↓
格式转换
        ↓
CVAT annotation import
```

优点：

- 最容易 debug；
- 不受 CVAT 函数接口限制；
- 方便检查坐标系、yaw、尺寸、frame index；
- 适合 BEV3D 这类输入复杂的模型。

建议中间格式：

```json
{
  "frame": 123,
  "objects": [
    {
      "label": "car",
      "score": 0.91,
      "center": [12.3, -1.8, 0.7],
      "size": [4.5, 1.8, 1.6],
      "yaw": 1.57,
      "track_id": 42,
      "attributes": {
        "source": "bev3d_model",
        "quality": "auto"
      }
    }
  ]
}
```

### 1.5.2 第二阶段：CVAT SDK / REST API 回写

当离线转换稳定后，再写脚本：

```bash
python auto_annotate.py --task-id 123 --model bev3d
```

典型流程：

```text
读取 CVAT task frame 列表
  ↓
运行模型推理
  ↓
转换为 CVAT shape / track / tag
  ↓
通过 CVAT SDK 或 REST API 写回
```

### 1.5.3 第三阶段：封装成 Nuclio 函数

只有当模型输入输出已经稳定，并且你希望在 CVAT UI 中直接点击自动标注时，再封装 Nuclio。

对于 BEV3D，Nuclio 函数要额外处理：

- 多传感器输入；
- 标定文件读取；
- 坐标系转换；
- 点云/图像同步；
- 3D box schema 转换；
- GPU 显存管理；
- 超时与批处理。

---

## 1.6 参考链接

- CVAT GitHub: https://github.com/cvat-ai/cvat
- CVAT 官方安装文档: https://docs.cvat.ai/docs/administration/community/basics/installation/
- CVAT 自动标注文档: https://docs.cvat.ai/docs/administration/community/advanced/installation_automatic_annotation/
- CVAT Serverless Tutorial: https://docs.cvat.ai/docs/guides/serverless-tutorial/
- Nuclio Releases: https://github.com/nuclio/nuclio/releases
