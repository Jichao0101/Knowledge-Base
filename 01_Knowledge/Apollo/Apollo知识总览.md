---
type: knowledge_topic_index
status: active
domain: Apollo
scope: Apollo 正式知识入口；用于 Apollo、CyberRT、Bazel 和日志机制分流。
updated_at: 2026-06-05
---

# Apollo 知识总览

本主题组织 Apollo 相关知识，重点是 Bazel 构建、CyberRT 通信与启动机制，以及日志功能。

## 1 主入口

| 分组 | 入口 | 内容简介 |
|---|---|---|
| Apollo 总览 | [[01_Knowledge/Apollo/Apollo]] | Apollo 使用 Bazel + CyberRT 的基本架构入口 |
| Bazel | [[01_Knowledge/Apollo/Bazel语法]] | Bazel 语法和构建相关笔记 |
| CyberRT 通信 | [[01_Knowledge/Apollo/CyberRT通信机制]] | Reader/Writer、Topic、消息类型和序列化机制 |
| CyberRT 启动 | [[01_Knowledge/Apollo/CyberRT启动机制]] | CyberRT 启动流程相关笔记 |
| 日志 | [[01_Knowledge/Apollo/日志功能]] | Glog、日志级别、条件输出和配置 |

## 2 读取规则

1. 理解 Apollo 主题入口先读 [[01_Knowledge/Apollo/Apollo]]。
2. 构建问题读 Bazel。
3. 通信问题读 CyberRT 通信机制。
4. 启动和日志问题分别读启动机制和日志功能。

## 3 结构风险

- 本主题仍是轻量笔记索引，尚未完成完整元数据标准化。
- 具体 Apollo 版本差异未在本索引中展开。
