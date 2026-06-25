---
type: current_maintenance_record
status: active
scope: 记录 CVAT 云端部署 current 文档组的创建、入口同步、门禁结果和未验证项。
updated_at: 2026-06-24
---

# 1 CVAT 云端部署 current 文档组创建记录

## 1.1 来源清单

- 用户提供的云端模型部署流程、CVAT 部署目标、turbo 目录建议、任务机制、网络通信和部署产物要求。
- 既有本地部署记录：[[02_Projects/cvat/cvat_local_deployment]]
- CVAT 官方安装、share path、SDK 文档。
- Docker 官方架构文档。
- 知识库入口：[[README]]
- 项目区入口：[[02_Projects/项目总览]]
- 结构审计入口：[[02_Projects/Knowledge-Base/知识库结构审计_current]]

## 1.2 创建文件

- [[02_Projects/cvat/CVAT云端部署项目总览_current]]
- [[02_Projects/cvat/CVAT云端部署原理讨论与方案权衡]]
- [[02_Projects/cvat/CVAT云端部署最终架构与扩展规划_current]]
- [[02_Projects/cvat/CVAT云端部署实施手册]]

## 1.3 同步文件

- [[README]]
- [[02_Projects/项目总览]]
- [[02_Projects/Knowledge-Base/知识库结构审计_current]]

## 1.4 门禁结果

本次写入前执行 full preflight 和 hash-check。

| 目标 | preflight | 说明 |
|---|---|---|
| `CVAT云端部署项目总览_current.md` | manual_review | current/guarded 路径保护；用户已明确要求执行写入 |
| `CVAT云端部署原理讨论与方案权衡.md` | allow | 新增项目方案讨论 |
| `CVAT云端部署最终架构与扩展规划_current.md` | manual_review | current/guarded 路径保护；用户已明确要求执行写入 |
| `CVAT云端部署实施手册.md` | allow | 新增项目实施手册 |
| 本维护记录 | allow | current 创建记录 |
| `README.md` | allow | 项目入口同步 |
| `02_Projects/项目总览.md` | allow | 项目入口同步 |
| `02_Projects/Knowledge-Base/知识库结构审计_current.md` | manual_review | 结构审计 guarded current；只追加必要状态记录 |

hash-check 均通过，未发现门禁后输入 hash 变化。

## 1.5 Recoverability 决策

本次不声明 `single_pass_recoverable: true`。

- 当前状态：`created_but_not_fully_verified`
- 原因：文档组已覆盖目标架构、边界、实施步骤和验证路径，但尚未在真实云桌面完成端到端部署验证。
- 下一步：用实施手册完成一次 CVAT 启动、share 导入、模型 API 回写、人工审核和导出闭环，再补验证记录。

## 1.6 未解决项

- 云桌面 Docker daemon 权限未现场确认。
- 端口暴露、安全组和域名/TLS 未现场确认。
- turbo 的实际挂载类型和跨节点访问方式未确认。
- CVAT 版本号仍需在实际部署时固定。
- 模型预标注回写 schema 需要按具体任务类型验证。

