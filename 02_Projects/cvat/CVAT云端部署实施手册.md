---
type: project_runbook
status: active
scope: CVAT 云端部署的实际操作手册，包括云端准备、Docker/Compose 安装、CVAT clone 或离线拷贝、启动、验证、备份和故障处理。
updated_at: 2026-06-24
---

# 1 CVAT 云端部署实施手册

## 1.1 目标目录

```text
# 云端标注平台
/opt/cvat                 # CVAT 源码和 Compose 配置

# 数据存储
/nas
  /datasets
  /model-results
  /annotations
  /cvat-share
  /cvat-backups
  /manifests
  
# 模型
由训练平台 task 启动
```

## 1.2 安装 Docker  Compose

云桌面已经安装 Docker，本地安装docker compose
```
sudo apt-get update
sudo apt-get install -y docker-compose-plugin
```

查看compose所在位置
```
dpkg -L docker-compose-plugin | grep docker-compose$
```

通过coscli拷贝到云端后授予运行权限
```
mkdir -p ~/.docker/cli-plugins
mv /tmp/docker-compose ~/.docker/cli-plugins/docker-compose
chmod +x ~/.docker/cli-plugins/docker-compose
```
查看版本
```bash
docker --version
docker compose version
docker info
```

## 1.3 推送CVAT源码与镜像

在本地准备源码包，拷贝到云端

```bash
git clone https://github.com/cvat-ai/cvat.git
```

拉取镜像文件
```
docker compose -f docker-compose.yml build
docker compose -f docker-compose.yml pull
```

生成镜像清单文件，并将镜像打包
目前使用基础镜像配置，如果将来新增服务，需要将相关配置文件涉及的镜像一并推送
```
cd /mnt/d/cvat
docker compose -f docker-compose.yml config --images | sort -u > cvat-images.txt
docker save -o cvat-images.tar $(cat cvat-images.txt)
```
云端导入镜像
```
docker load -i cvat-images.tar
```
## 1.4 配置 CVAT_HOST

本机浏览器访问可用：

```bash
export CVAT_HOST=localhost
```

其他机器或 GPU 节点需要访问时，使用云桌面 IP 或域名：

```bash
export CVAT_HOST=<cpu-desktop-ip-or-domain>
```

建议写入 `/opt/cvat/.env` 或部署脚本，但不要把 token 写入公开文件。


## 1.5 更新 cvat_opa镜像

合规云桌面不支持x86-v2指令集，需要手动下载opa:1.12.2-static 镜像推送到云端后替换

```
docker pull openpolicyagent/opa:1.12.2-static
docker save -o opa-1.12.2-static.tar openpolicyagent/opa:1.12.2-static
```

在合规云：

```
docker load -i opa-1.12.2-static.tar
cd ~/cvat/cvat
sed -i 's#openpolicyagent/opa:1.12.2#openpolicyagent/opa:1.12.2-static#g' docker-compose.yml
```
## 1.6 配置 NAS share 挂载

### 1.6.1 创建 NAS 本地挂载目录

```
sudo mkdir -p /mnt/nas-1/cvat-share
sudo chown $USER:$USER /mnt/nas-1/cvat-share
```
### 1.6.2 挂载NAS

在 `~/cvat/cvat/docker-compose.override.yml` 写入：

```yaml
services:
  cvat_server:
    volumes:
      - cvat_share:/home/django/share:ro
    networks:
      cvat:
        aliases:
          - cvat-server

  cvat_worker_import:
    volumes:
      - cvat_share:/home/django/share:ro

  cvat_worker_export:
    volumes:
      - cvat_share:/home/django/share:ro

  cvat_worker_annotation:
    volumes:
      - cvat_share:/home/django/share:ro

  cvat_worker_chunks:
    volumes:
      - cvat_share:/home/django/share:ro

volumes:
  cvat_share:
    driver_opts:
      type: none
      device: /mnt/nas-1/cvat-share
      o: bind
```


## 1.7 启动 CVAT

```bash
cd ~/cvat/cvat
export CVAT_HOST=192.168.10.200
docker compose up -d
docker compose ps
```

健康检查：

```bash
docker exec -t cvat_server python manage.py health_check
curl -fsS "http://${CVAT_HOST}:8080/api/server/about"
```

创建管理员：

```bash
docker exec -it cvat_server bash -ic 'python3 ~/manage.py createsuperuser'
```

浏览器访问：

```text
http://192.168.10.200:18080 #8080端口已被占用，映射到18080
```

## 1.8 创建 MVP 数据任务

准备测试数据：

```bash
mkdir -p /nas/cvat-share/mvp/images
cp /path/to/test_images/*.jpg /nas/cvat-share/mvp/images/
```

在 CVAT UI 中：

1. 创建 project。
2. 创建 task。
3. 数据源选择 `share` 下的 `mvp/images`。
4. 创建 job 并分配给测试标注员。

## 1.9 模型任务输出

模型由训练平台 task 启动，不由 CVAT 平台主动拉起，也不要求模型容器直接访问 CVAT API。

## 1.10 dispatcher / 导入脚本最小流程

dispatcher MVP 可以先做成脚本，不需要长期占用 GPU 或训练平台容器：

```text
读取 /nas/manifests/<project>/<batch>.json
  -> 校验数据路径和 label schema
  -> 调用 CVAT API 创建 project/task
  -> 写入 task_id/job_id 映射
  -> 等待训练平台 task 将模型结果写入 /nas/model-results
  -> 校验模型结果文件和格式
  -> 将模型结果转换或导入为 CVAT annotation
  -> 标记 ready_for_review
  -> 人工修正和审核
  -> 导出到 /nas/annotations/export
```

dispatcher 不直接连接或修改 CVAT PostgreSQL。

## 1.11 停止、重启和升级

停止但保留数据：

```bash
cd /opt/cvat
docker compose down
```

重启：

```bash
cd /opt/cvat
docker compose up -d
```

查看日志：

```bash
docker compose logs --tail=200 cvat_server
docker compose logs --tail=200 cvat_worker_import
docker compose logs --tail=200 cvat_worker_export
```

升级前：

1. 备份数据库。
2. 备份 `/opt/cvat/.env` 和 `docker-compose.override.yml`。
3. 记录当前 Git tag 和镜像版本。
4. 在测试环境验证 share 导入、模型结果导入、人工复核和导出。

## 1.12 备份与恢复

数据库备份示例：

```bash
mkdir -p /nas/cvat-backups/postgres
docker exec -t cvat_db pg_dumpall -U root > /nas/cvat-backups/postgres/cvat-$(date +%Y%m%d-%H%M%S).sql
```

标注结果应定期通过 CVAT 导出 API 或 UI 导出到：

```text
/nas/annotations/export/<project_key>/<batch_id>
```

恢复必须在测试环境演练后再用于生产环境。

## 1.13 常见故障

| 现象 | 检查 |
|---|---|
| `docker compose` 不存在 | 安装 `docker-compose-plugin` |
| 浏览器打不开 CVAT | 检查 `CVAT_HOST`、端口、安全组、防火墙、`docker compose ps` |
| CVAT 不能看到 share 数据 | 检查 `/nas/cvat-share`、override volume、worker 挂载 |
| 模型结果未出现 | 检查训练平台 task、NAS 输出路径、权限和 manifest |
| 模型结果导入失败 | 检查 label schema、annotation schema、坐标系和转换脚本 |
| 导出失败 | 查看 `cvat_worker_export` 日志和磁盘空间 |
| CVAT 读不到 NAS | 确认宿主机挂载、容器 bind mount、SELinux/AppArmor 和目录权限 |

