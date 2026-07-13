---
type: project_plan
status: draft
project: DMS
module: Issue Analysis Skill
summary: 建立从飞书表格定位问题输入、汇聚 Jira 与日志证据、依次分析 R 核和 A 核并将结论回写 Jira 的 DMS 问题分析 Skill。
sources:
  - 2026-07-13 用户确认的工作流与方案讨论
  - 2026-07-13 Jira Parser 与 Data Loader 实现及真实只读验证
  - 2026-07-13 Evidence Package Builder 实现与集成验证
scope: DMS 问题的只读采集、证据打包、R/A 核分析和 Jira 结论回写。
risks:
  - R 核文档和日志规则尚未补齐，首版不能保证形成跨核根因结论。
  - 飞书多维表格字段名可能变化，需要通过可配置别名维持兼容并对缺失字段 fail-closed。
  - Jira 写回属于外部变更，必须预览并确认目标与内容。
  - Jira 访问依赖本地 Bearer token；凭据不得进入版本控制或知识库正文。
updated_at: 2026-07-13
---

# 1 DMS 问题分析 Skill 项目方案

## 1.1 目标与边界

目标是建立一个可复用的 DMS 问题分析 Skill，从飞书表格中按责任人姓名或指定 Jira ID 定位问题，读取对应 Jira ID、数据路径和分析上下文，采集 Jira 信息与现场数据，构建可追溯证据包，按照 R 核到 A 核的顺序分析问题，并将最终结论回写 Jira。

本项目当前边界：
- 首版只新增 Jira 评论，不自动修改状态、负责人、优先级或其他字段。
- 结论必须区分事实、推断、假设与未知，不以证据不足的局部发现替代完整根因。
- 本文同时记录当前实施状态；飞书入口、Jira Parser、Data Loader 与 Evidence Package Builder 已实现并完成对应验证，后续分析与回写阶段仍以实际验证结果为准。

## 1.2 总体架构

```text
Lark CLI Base Reader
        ↓
Jira Parser + Data Loader
        ↓
Evidence Package Builder
        ↓
R-core Analyser
        ↓
A-core Analyser
        ↓
Conclusion Synthesizer
        ↓
Jira Writeback
```

各阶段通过结构化输入输出解耦。下游只依赖上一阶段的公开产物，不直接依赖其内部实现。

## 1.3 飞书表格入口

### 1.3.1 定位方式

Skill 只在以下两类请求中触发：

- 用户要求分析飞书中某个责任人名下的 DMS 问题。
- 用户要求分析某个 Jira ID 的 DMS 问题。

输入为带 `table` 和 `view` 参数的飞书 Wiki/Base URL，入口按实际字段名及配置别名读取记录。

按责任人筛选时使用去除首尾空白后的精确姓名匹配；按 Jira ID 筛选时同时接受纯 ID 和完整 Jira URL。两个条件同时存在时取交集。未提供任一条件时拒绝执行，避免无范围扫描。

### 1.3.2 固定执行器与策略配置

采用“固定读取脚本 + reference 策略配置”。固定脚本负责 URL 解析、Base 读取、记录筛选、字段标准化和候选判定；reference 保存字段别名、Jira browse 前缀、重复分析标记值和分页大小。

固定执行器负责：

- 解析 Wiki/Base URL、table ID 和 view ID。
- 获取表结构并按字段名读取记录，不依赖字段顺序。
- 按责任人或 Jira ID 筛选；两者同时存在时执行交集筛选。
- 读取 `已经过AI分析` 字段
- 默认排除已分析记录，但在 `skipped_records` 中保留记录和原因。
- 对 Jira ID、Jira URL 和数据路径进行格式校验与标准化。
- 输出源信息、筛选条件、字段映射、候选记录、跳过记录、统计和警告。

策略 reference 负责：

- Jira ID、数据路径、概要、描述、产品版本、车型、项目区域、责任人和分析标记的字段别名。
- `https://jira-patac.apps.saic-gm.com/browse/` Jira 地址前缀。
- 已分析、未分析标记值及未知非空标记的 fail-safe 行为。
- 必需字段和分页大小。

表中缺少责任人/Jira 筛选字段时必须 fail-closed。没有记录命中筛选条件时返回空候选和警告，不扩大范围或模糊匹配。

### 1.3.3 Jira 地址与重复分析门禁

Jira 地址按以下规则生成：

1. Jira 单元格包含以 `https://jira-patac.apps.saic-gm.com/browse/` 开头的超链接时，直接保留该地址。
2. 其他超链接或纯文本能够提取 Jira ID 时，在 ID 前拼接上述 browse 前缀。
3. 不静默修正 Jira 项目前缀的拼写差异；无法提取 ID 时将记录标记为阻塞。

重复分析按以下规则处理：

1. 优先读取 `已经过AI分析`，兼容 `AI分析`。
2. 肯定值、布尔值 `true` 或未知但非空的标记均视为已分析。
3. 已分析记录默认标记为 `already_analyzed` 并排除出 `analysis_candidates`。
4. 只有用户明确要求重新分析时，才允许通过显式参数重新纳入候选。
5. 表中没有分析标记字段时输出警告，不自行推断分析状态。

### 1.3.4 输出契约

```json
{
  "source": {
    "object_type": "bitable",
    "table_id": "tbl...",
    "view_id": "vew...",
    "collected_at": "..."
  },
  "selection": {
    "owner": "张三",
    "jira_id": "ADASL2-1565",
    "mode": "intersection"
  },
  "field_mapping": {},
  "records": [],
  "analysis_candidates": [],
  "skipped_records": [],
  "summary": {},
  "warnings": []
}
```

标准化记录至少保留 `record_id`、`jira_id`、`jira_url`、`data_path`、概要、描述、产品版本、车型、项目区域、责任人、分析标记、候选状态、判定原因和原始字段。缺少 Jira ID 或数据路径时显式标记为阻塞，不猜测值。

## 1.4 Jira Parser 与 Data Loader

### 1.4.1 Jira Parser

Jira Parser 负责只读采集并保留原始响应。当前策略是支持配置化的 required/optional 字段集合。

Jira 认证统一使用 Bearer token。Token 仅允许保存在被 Git 忽略的本地 credential reference。采集失败时保留明确认证错误，不自动轮询其他认证方式。

候选信息包括：

- Issue 基本字段、描述、状态、优先级和类型。
- Reporter、assignee、创建时间、更新时间和解决时间。
- 评论、changelog、子任务和关联 Issue。
- 附件元数据；附件下载默认关闭，按类型、大小和数量白名单启用。
- Jira 原文链接和采集时间。

### 1.4.2 Data Loader

Data Loader 负责：

- 校验数据路径是否合法、存在且可读。
- 生成文件清单，记录相对路径、类型、大小、修改时间和必要的 hash。
- 识别 R 核日志、A 核日志、配置、版本信息和其他辅助文件。
- 将无法分类的文件显式列入 `unclassified`。

Data Loader 不修改、移动或删除原始数据。分析产物写入独立工作目录。

文件分类使用可配置规则；包含 `calmcar_camera_service` 关键字的日志作为 A 核日志候选，尚未命中规则的文件继续显式进入 `unclassified`，候选分类不等同于已完成日志协议解析。

## 1.5 Evidence Package

产物结构：

```text
evidence-package/
├── manifest.json
├── lark/context.json
├── jira/
│   ├── issue.json
│   ├── comments.json
│   ├── changelog.json
│   ├── attachments_manifest.json
│   └── raw/
├── data/files_manifest.json
├── analysis/
└── reports/
```

Builder 只接受 `ready` 飞书候选，并在构建前校验飞书、Jira 与 Data Loader 输入中的 Jira ID 和数据路径一致。输出目录必须不存在且不得位于源数据目录内；构建使用同级临时目录和原子切换，失败时不保留半成品，也不覆盖已有 package。

`manifest.json` 记录 package ID、Jira ID、数据路径、构建时间、builder 版本、输入路径与 hash、缺失证据、各阶段状态，以及每个交付文件的相对路径、大小和 SHA-256。Jira 和 Data Loader 任一为 `partial` 时允许生成 `partial` package；`blocked`、`failed`、输入冲突或 Jira 原始响应缺失时 fail-closed。

统一阶段状态：

- `ready`
- `complete`
- `partial`
- `blocked`
- `failed`
- `skipped`

Evidence Package 是本工作流的输入快照和阶段交接契约；它本身不是未经核验结论的可信性证明。Builder 不复制源日志，`analysis/` 与 `reports/` 在本阶段保持为空，不伪造尚未执行的分析或回写结果。

## 1.6 R-core Analyser

R 核固定先于 A 核分析。目标是从最终可观察结果开始，检查 R 核判定、状态机、输出事件及其消费的 A 核输入。

R 核资料暂缺时：

1. 识别并登记 R 核候选日志。
2. 输出缺失的日志格式、接口、消息 ID 或时钟说明。
3. 能可靠解析时间戳时生成原始时间线。
4. 将阶段标记为 `partial` 或 `blocked`。
5. 允许 A 核继续做局部事实分析，但禁止据此声明跨核根因。

R 核输出至少包括状态、事实、时间线、假设、缺失证据，以及移交 A 核时允许和禁止的推断范围。

## 1.7 A-core Analyser

分析范围包括：

- 输入数据与预处理。
- 模型推理输出。
- 后处理。
- 配置是否命中。
- 输出给 R 核的消息内容、时序、漏发、重复和乱序。
- 错误码与异常恢复流程。

## 1.8 结论合成

所有结论按以下证据等级标记：

- `fact`：由日志、配置或接口直接观察到。
- `inference`：由多个已列明事实推导。
- `hypothesis`：仍需要实验或补充证据验证。
- `unknown`：当前证据不能判断。

问题归属使用标准枚举：

- `R_CORE`
- `A_CORE`
- `CROSS_CORE_INTERFACE`
- `DATA`
- `CONFIGURATION`
- `ENVIRONMENT`
- `INSUFFICIENT_EVIDENCE`
- `NOT_REPRODUCED`

结论应同时列出支持证据、反证、竞争假设、可信度和下一步补证计划。

## 1.9 Jira 回写

Jira 回写分为草稿和提交两个阶段：

1. 生成 Jira 评论草稿。
2. 展示目标 Jira ID 和完整评论内容。
3. 新增评论。
4. 保存 comment ID、提交时间和响应结果。
5. 使用分析运行 ID 避免重复评论。

评论建议包含分析状态、关键事实、R 核分析、A 核分析、初步结论、缺失证据和下一步建议。完整日志不直接粘贴进 Jira。

## 1.10 Skill 资源规划

```text
analyze-dms-issue/
├── SKILL.md
├── agents/openai.yaml
├── scripts/
│   ├── fetch_lark_issue_context.py
│   ├── fetch_jira_evidence.py
│   ├── load_case_data.py
│   ├── build_evidence_package.py
│   ├── analyze_r_core.py
│   ├── analyze_a_core.py
│   ├── synthesize_conclusion.py
│   └── writeback_jira.py
├── references/
│   ├── lark-base-strategy.json
│   ├── jira-fetch-strategy.json
│   ├── jira-credentials.local.json
│   ├── data-loader-strategy.json
│   ├── evidence-schema.md
│   ├── r-core-analysis.md
│   ├── a-core-analysis.md
│   └── conclusion-policy.md
└── assets/jira-comment-template.md
```

确定性采集、校验、打包和写回使用脚本；可变业务规则和领域知识放入 references。日志格式稳定后，再逐步将 R/A 核日志解析从 Agent 推理固化为可测试脚本。

`jira-credentials.local.json` 是本地运行时输入，必须由 `.gitignore` 排除，不属于可提交的 Skill 资源或知识事实源。

## 1.11 分阶段实施建议

### 1.11.1 阶段一：输入与证据框架

- 建立 Skill 骨架和阶段契约。
- 实现飞书 Base URL 解析、按责任人/Jira ID 筛选、重复分析门禁、Jira URL 规范化、Jira 只读采集和 Data Loader。
- 实现 Evidence Package 与 Jira 评论草稿生成。

当前进展：飞书入口、Jira Parser、Data Loader 和 Evidence Package Builder 已实现；Jira Parser 已通过真实 Issue 的 Bearer 只读采集验证，Data Loader 已通过本地日志目录验证，Evidence Package 已使用真实 Jira/Data 输入与明确标注的 synthetic 飞书候选完成集成构建。在线飞书到 package 的端到端验证和 Jira 评论草稿尚未完成。

### 1.11.2 阶段二：分析器

- 补齐 R 核资料、日志规则和接口映射。
- 建立 A 核 reference。
- 实现跨核时间线和结论合成规则。

### 1.11.3 阶段三：验证与受控写回

- 用真实但脱敏的故障样例验证检索和证据包。
- 覆盖缺字段、多路径、版本不一致和 R 核阻塞等降级场景。
- 验证 Jira 草稿预览、确认提交、幂等和失败恢复。

## 1.12 待确认事项

- 飞书 Base 默认入口 URL、table/view 是否固定，以及字段别名变更治理方式。
- Jira 必采字段、关联 Issue 规则和附件策略。
- 数据路径协议、目录布局、日志命名、压缩格式和数据规模上限。
- R 核文档、日志格式、R/A 接口、消息 ID 和时间同步规则。
- A 核代码仓库、默认 branch/commit 获取方式和模块覆盖范围。
- Jira 评论目标、模板、审批方式和是否允许更新已有评论。
