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
  - 2026-07-13 当前版本跳过 R 核并在结论中披露分析覆盖缺口的用户决策
  - 2026-07-13 A-core 日志索引与证据选择实现、36 项仓库测试验证及用户确认的手工规则更新边界
  - 2026-07-13 Conclusion Synthesizer、手工结论策略、证据链门禁与44项仓库测试验证
  - 2026-07-13 Jira 自动评论写回、marker 去重、失败边界与54项仓库测试验证
  - 2026-07-13 ADASL2-1565 首个真实端到端分析、Jira 评论 8654391/8654396 与中文 Wiki Markup 修复记录
  - 2026-07-27 R 核项目流程文档、Skill reference/strategy 分层、Skill 瘦身与55项仓库测试验证
  - 2026-07-29 用户提供并确认的 R 核远程规则更新、问题修正与本地来源同步
  - 2026-07-29 Skill 提交 d259741 与 eda7018：R 核规则同步、正式报警反向分析、R/A 对齐与内置映射合同
  - 2026-07-30 Skill 提交 88a4170：Jira 评论数据路径解析、人工确认门禁与 Evidence Package Builder v2
  - 2026-07-30 当前 Skill 仓库 83 项单元测试验证
scope: DMS 问题的只读采集、证据打包、R/A 核分析和 Jira 结论回写。
risks:
  - R 核规则 reference/strategy 已补齐，但确定性 analyser、输入适配和结果合同尚未实现，仍不能形成 R 核或跨核根因结论。
  - 飞书多维表格字段名可能变化，需要通过可配置别名维持兼容并对 Jira ID 等必需字段 fail-closed；表格不再承担数据路径来源。
  - Jira 评论由人类填写，路径提示可能缺少中间层级、存在少量错字或只能形成多个近似候选；LLM 只能用于候选召回和排序，不能替代目录存在性、可读性、根目录边界与唯一性校验。
  - 数据共享根目录 `\\192.168.1.111\Global_VIP\J6B_DMSRain` 仍依赖运行环境提供可访问映射；根目录或候选目录不可访问时必须停止并请求用户确认，当前尚未完成真实共享盘端到端验证。
  - Jira 写回属于外部变更；当前按用户决策默认自动新增评论，不再要求提交确认，因此必须通过 conclusion 锁定目标、固定接口范围、marker 去重和结果凭据约束风险。
  - Jira 访问依赖本地 Bearer token；凭据不得进入版本控制或知识库正文。
  - A 核查询规则由 Skill reference 手工维护；运行版本变化后规则可能过期，单次问题分析不得临时读取源码或自动改规则。
  - 初始问题时间只能作为检索 seed；异步多线程、时钟偏差和字段缺失仍可能限制跨阶段因果关联。
  - 当前 R 核固定跳过，因此结论不能确认 R 核或跨核归属，其他归属的最高可信度也受策略限制。
  - R 核 reference/strategy 已同步到来源 SHA-256 `70745baf9fe48903b9fdc57dc0da196fa5500e306ed8a54f81935a053466486f`，但运行 profile 与内置信号映射的兼容性仍需逐 case 验证；不匹配时必须标记 `mapping_version_unverified`。
  - Jira marker 去重是提交前查询实现的 best-effort 机制；并发执行仍可能在查询与 POST 之间产生重复评论。
  - Jira Server v2 使用 Jira Wiki Markup；Markdown 行首 `#` 会被解释为多级有序列表。评论正文必须使用中文和 Jira Wiki 模板，既有错误评论因禁止更新/删除只能追加纠正版。
updated_at: 2026-07-30
---

# 1 DMS 问题分析 Skill 项目方案

## 1.1 目标与边界

目标是建立一个可复用的 DMS 问题分析 Skill：采集模式从飞书表格按责任人姓名或指定 Jira ID 定位问题，只把 Jira ID 和业务上下文作为入口；数据地址改为从 Jira 评论提取人类路径提示，在固定共享根目录下由 Agent/LLM 容错检索候选，再经确定性校验后读取现场数据。直接日志模式则只读取用户明确授权的日志路径，跳过飞书、Jira 采集和自动写回。两种模式最终都按正式 R 核报警反向追踪 R 核输入、计时与门禁，再继续分析 A 核和跨核链路。

当前 R 核规则 reference/strategy 与 R/A 对齐合同已就绪，但确定性 analyser 尚未实现；自动 Evidence Package 流水线仍将 R 核标记为 `skipped/r_core_analyser_not_available`。直接日志任务允许 Agent 输出带原始位置的 `manual_r_core_review`，但不得生成或冒充 `r_core_result.json`。

本项目当前边界：
- 首版只自动新增 Jira 评论，不自动修改状态、负责人、优先级或其他字段，也不更新或删除既有评论。
- 结论必须区分事实、推断、假设与未知，不以证据不足的局部发现替代完整根因。
- 本文同时记录当前实施状态；飞书入口、Jira Parser、Jira 评论路径解析、Data Loader、Evidence Package Builder、A 核分析准备、结论合成与 Jira 写回均有实现和自动化验证，但 Jira 评论路径链路尚未完成真实共享盘端到端验证。

## 1.2 总体架构

```text
Lark CLI Base Reader
        ↓
Jira Parser（含全部评论）
        ↓
Path Hint Extractor
        ↓
Agent/LLM 受限容错检索
        ↓
Path Validator ── 不存在/不可访问/不唯一 → 用户确认并停止
        ↓
Data Loader
        ↓
Evidence Package Builder v2
        ↓
R-core Analyser（当前 skipped）
        ↓
A-core Analyser
        ↓
Conclusion Synthesizer
        ↓
Jira Writeback
```

直接日志模式从用户授权路径进入手工 R→A review，不经过飞书、Jira、Evidence Package 和自动 Jira 写回。采集模式各阶段通过结构化输入输出解耦；下游只依赖已通过门禁的公开产物，不直接依赖上一阶段内部实现。

## 1.3 飞书表格入口

### 1.3.1 定位方式

采集模式只在以下两类请求中触发：

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
- 对 Jira ID 和 Jira URL 进行格式校验与标准化；不再读取或标准化表格数据路径。
- 输出源信息、筛选条件、字段映射、候选记录、跳过记录、统计和警告。

策略 reference 负责：

- Jira ID、概要、描述、产品版本、车型、项目区域、责任人和分析标记的字段别名。
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

标准化记录至少保留 `record_id`、`jira_id`、`jira_url`、概要、描述、产品版本、车型、项目区域、责任人、分析标记、候选状态、判定原因和原始字段。缺少 Jira ID 时显式标记为阻塞；没有表格数据路径不再构成阻塞条件。

## 1.4 Jira Parser、路径解析与 Data Loader

### 1.4.1 Jira Parser

Jira Parser 负责只读采集并保留原始响应。当前策略是支持配置化的 required/optional 字段集合。

Jira 认证统一使用 Bearer token。Token 仅允许保存在被 Git 忽略的本地 credential reference。采集失败时保留明确认证错误，不自动轮询其他认证方式。

候选信息包括：

- Issue 基本字段、描述、状态、优先级和类型。
- Reporter、assignee、创建时间、更新时间和解决时间。
- 评论、changelog、子任务和关联 Issue。
- 附件元数据；附件下载默认关闭，按类型、大小和数量白名单启用。
- Jira 原文链接和采集时间。

### 1.4.2 Jira 评论数据路径解析

路径解析采用“确定性提取 + LLM 容错检索 + 确定性校验”的分层设计：

1. `scripts/resolve_jira_data_path.py prepare` 只从 `jira_evidence.json` 的评论原文提取路径片段和检索词，不直接选择目录。
2. Agent/LLM 只允许在 `\\192.168.1.111\Global_VIP\J6B_DMSRain` 对应的已授权可访问根目录内检索，可利用评论原文、片段和目录结构处理漏写中间层级、别名和少量错字。
3. LLM 只能提出候选。只有候选数为 1 时，才允许进入 `validate`；来源 comment ID 和候选数必须写入解析产物。
4. `validate` 校验根目录与候选目录存在、候选为可读目录、解析后未逃逸根目录，并同时记录规范 UNC 路径 `canonical_path` 与 Data Loader 实际使用的 `access_path`。
5. 无提示、零候选、多候选、根目录不可访问、候选不存在、不可读或越界时输出 `blocked_user_confirmation`、`continue_allowed=false`，退出码为 3；不得进入 Data Loader、Evidence Package 或后续分析。
6. 用户确认地址后可用 `user_confirmed` 方式重新校验，但用户确认不能绕过存在性、可读性和根目录边界检查。

`references/data-path-resolution-strategy.json` 保存规范共享根、路径关键词、唯一候选要求和阻塞状态。当前实现已通过缺少提示、HTTP URL 排除、漏层级候选、路径不存在、多候选、目录越界和用户确认恢复等单元测试；真实共享盘访问仍待验证。

### 1.4.3 Data Loader

Data Loader 负责：

- 校验解析产物中的 `access_path` 是否仍然存在且可读。
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
├── data/
│   ├── path_resolution.json
│   └── files_manifest.json
├── analysis/
└── reports/
```

Builder v2 只接受 `ready` 飞书候选，并强制消费 `path_resolution.json`。构建前校验飞书候选与 Jira ID 一致、路径解析 Jira ID 与 Jira 证据一致、解析状态为 `resolved`、`continue_allowed=true`，以及解析 `access_path` 与 Data Loader 清单源路径一致。任何未解析或待用户确认状态都不能降级构建 partial package。

输出目录必须不存在且不得位于源数据目录内；构建使用同级临时目录和原子切换，失败时不保留半成品，也不覆盖已有 package。`manifest.json` 记录 package ID、Jira ID、实际 `data_path`、规范 `canonical_data_path`、builder 版本、四个输入路径与 hash、缺失证据、各阶段状态，以及每个交付文件的相对路径、大小和 SHA-256。Jira 和 Data Loader 任一为 `partial` 时允许生成 `partial` package；`blocked`、`failed`、路径未解析、输入冲突或 Jira 原始响应缺失时 fail-closed。

统一阶段状态：

- `ready`
- `complete`
- `partial`
- `blocked`
- `failed`
- `skipped`

Evidence Package 是本工作流的输入快照和阶段交接契约；它本身不是未经核验结论的可信性证明。Builder 不复制源日志，`analysis/` 与 `reports/` 在本阶段保持为空，不伪造尚未执行的分析或回写结果。

## 1.6 R-core Analyser

R 核规则已按渐进披露分层：`references/r-core-analysis.md` 保存排查顺序、证据边界和维护规则，`references/r-core-analysis-strategy.json` schema/revision 4 保存信号、阈值、灵敏度、优先级、事件分段、三态逻辑结果和跨核规则。当前 strategy 已锁定并验证项目来源 SHA-256 `70745baf9fe48903b9fdc57dc0da196fa5500e306ed8a54f81935a053466486f`，状态从旧方案的 `source_updated/reference_sync_pending` 更新为 `reference_ready/analyser_not_implemented`。

同步后的 reference 已包含闭眼、哈欠、视线分心、头部姿态、电话和抽烟检测中的间歇 `false` 容忍窗口，明确抽烟持续时间、High 灵敏度边界、危险报警信号名和遮挡/无人脸优先级。普通灵敏度哈欠与 `isMonitoringEnabled` 门禁关系仍保留为 `not_documented` 或 `decision_relation_not_documented`，未从相邻功能规则推断补齐。

R 核 review 改为正式报警反向分析：

1. 从对应 `WrngIndReq` 的 UTC 跳变和原始位置开始。
2. 反查 R 核内部状态、内部计时峰值、工作状态、冷却、车速、灵敏度、功能开关与更高优先级报警。
3. 反查 R 核收到的感知枚举与派生标签。
4. 分开记录每个正标签段、每次中间间歇、间歇次数与合计、`wall_clock_span`、`positive_duration_sum`、`intermediate_gap_duration_sum` 和 `r_core_internal_duration_peak`，不得互相替代。
5. 输出 `conforming`、`nonconforming` 或 `unknown`，并分别列出依据、矛盾和缺失证据。
6. 无论 R 核结果为何，都继续执行 A 核与跨核分析，不允许因 R 核符合、异常或未知而提前结束。

`references/r-a-core-alignment.md` 定义 A→R 的反向对齐合同：区分 R 核收到的输入与 A 核发出的输出，检查延迟、丢失、重复、乱序和陈旧数据；运行时只使用 Skill 内置的版本化 J6B 映射，不访问源码或协议。无法确认运行 profile 兼容性时标记 `mapping_version_unverified`。同一物理日志同时含 `[ALGORITHM_RESULT_Q1]` 与 `[SwcMsg_DMS_RSM_Viewer]` 时保留统一源路径和物理行号，按 marker 逻辑分流，且禁止用未来 A 核样本解释此前 R 核输入。

跳过 R 核时必须保留以下边界：

1. Data Loader 仍可登记 R 核候选日志，但候选分类不等同于已执行 R 核分析。
2. 不生成虚假的 R 核事实、时间线、假设或 `r_core_result.json`。
3. 不把 R 核缺失标记为数据本身的 `failed`；这是当前分析能力缺失，阶段状态使用 `skipped`。
4. Agent 可在直接日志模式形成带原始位置的 `manual_r_core_review`；自动流水线仍不得把它冒充确定性 analyser 产物。
5. 最终结论必须显式披露 R 核未执行及其对结论覆盖范围和可信度的影响。

未来实现 R 核 analyser 后，应重新评审输入适配、阶段顺序、输出契约、结论策略和既有结论适用范围，不得仅凭 reference 已存在就把 `skipped` 改写为已完成。

## 1.7 A-core Analyser

分析范围包括：

- 输入数据与预处理。
- 模型推理输出。
- 后处理。
- 配置是否命中。
- 输出给 R 核的消息内容、时序、漏发、重复和乱序。
- 错误码与异常恢复流程。

当前 A 核输出只代表 A 核可观察范围内的事实和推断。涉及 R 核消费结果、R/A 交互或最终系统行为的判断必须降级为待验证假设或未知。

在反向分析模式中，A 核阶段还需按 `r-a-core-alignment.md` 对齐 fuse/atomic/model 输出、映射前枚举和 R 核接收值；只有 UTC、消息时间戳或序号，以及内置映射兼容性均有证据时，才能提升跨核一致性判断。普通问题分析不得为解释单个 case 临时读取源码、推断枚举或静默修改固定映射。

当前已实现确定性日志索引与证据选择层，入口为 `scripts/analyze_a_core.py`。脚本把 Evidence Package 作为只读输入，扫描 Data Loader 标记的全部 `a_core_log_candidate`，但不把全部原文放入 Agent context。输出目录必须位于源数据和 Evidence Package 之外，采用临时目录加原子切换，避免污染输入快照。

确定性输出包括：

```text
a-core-analysis/
├── a_core_log_index.jsonl
├── a_core_signature_summary.json
├── a_core_selection_manifest.json
└── a_core_result.json
```

- `a_core_log_index.jsonl`：为每个物理日志行保存文件、行号、byte offset、解析状态、时间、级别、线程、源码位置、模块、签名、关联键和原文。
- `a_core_signature_summary.json`：保存输入文件 hash、行覆盖不变量、级别/模块计数、签名计数及首次/末次样本。
- `a_core_selection_manifest.json`：记录 Jira/显式关键词、问题时间、错误级别、初始化、通用异常、低频签名、邻接上下文以及 frame ID、timestamp、tracking ID、sequence 跨线程扩展的选择原因和字符预算。
- `a_core_result.json`：保存确定性事实、覆盖声明、手工规则版本状态和工件 hash；初始状态固定为 `partial`、`reasoning_status=pending_agent_review`，不得冒充完整诊断。

全量处理的硬约束是 `total_lines = parsed_lines + unparsed_lines`；无法按已知格式解析的行仍保留原文和位置。若 Data Loader 已记录日志 hash，分析前必须一致；分析过程中再次校验文件未变化。

A 核模块、初始化、异常和 correlation 查询规则的运行时事实源是 `references/a-core-analysis-strategy.json`。这些规则只能通过显式修改 Skill 并重新验证来更新。日常问题分析不读取 DMS 源码，不自动生成 reference，也不根据单个 case 静默修改固定规则。`compatible_runtime_revisions` 只用于提示已验证版本：为空时为 `generic_unversioned`，版本未知时为 `runtime_version_unknown`，不在兼容列表时为 `review_recommended`。

Agent review 仍是后续步骤：Agent 只消费 selection manifest 和按原始位置定向回读的少量证据，再形成 `fact`、`inference`、`hypothesis` 与 `unknown`。若 selection 不足，应增加显式 anchor 重跑或定向回读，不得把完整日志直接放入 context。

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

Evidence Package 自动流水线的结论必须增加分析覆盖声明：

- `R_CORE`：`skipped`，原因是 R 核 analyser 尚未实现。
- `A_CORE`：按实际执行结果记录 `complete`、`partial`、`blocked` 或 `failed`。
- 明确说明结论仅覆盖 A 核与现有输入证据，未验证 R 核行为和跨核链路。
- 在 R 核未执行时，不得把问题确认为 `R_CORE` 或 `CROSS_CORE_INTERFACE`；相关判断只能列为假设、未知或补证方向。

直接日志模式的 `manual_r_core_review` 与分层手工结论必须引用源路径、行号、marker 和 UTC；它不属于 Evidence Package 自动流水线输入，不能直接进入自动 Jira 写回。

当前已实现确定性 Conclusion Synthesizer，入口为 `scripts/synthesize_conclusion.py`。脚本只消费 Evidence Package、A-core result 及同目录 selection manifest，不读取 DMS 源码、不修改任一输入、不自动学习规则，也不写 Jira。可执行策略位于 `references/conclusion-policy.json`，解释性契约位于 `references/conclusion-policy.md`；两者只能通过显式 Skill 变更手工更新。

Agent review 尚未完成时，综合器只输出 `partial/INSUFFICIENT_EVIDENCE/low`。完成 review 时，A-core result 必须同时声明 `status=complete` 和 `reasoning_status=complete`，提供摘要、拟议归属、置信度、事实、推断、假设、未知项、反证与下一步，并至少用一个 `evidence_ids` 引用 selection manifest 中的现有证据。综合器校验 package ID、Jira ID、Evidence Package manifest hash、selection manifest hash 和全部 evidence ID；任一不一致即 fail-closed。

输出为独立目录中的 `conclusion.json`，保存分析覆盖、归属、置信度、事实/推断/假设/未知项、反证、下一步、证据链、策略调整和 Jira 回写限制。当前 `R_CORE` 与 `CROSS_CORE_INTERFACE` 拟议归属会降级为 `INSUFFICIENT_EVIDENCE`；其他归属在 R 核跳过期间最高为 `medium`。输出目录必须不存在，且不能与源数据、Evidence Package 或 A-core analysis 目录重叠。

## 1.9 Jira 回写

Jira 自动写回已实现，入口为 `scripts/writeback_jira.py`，可执行规则位于 `references/jira-writeback-policy.json`，边界说明位于 `references/jira-writeback.md`，评论格式位于 `assets/jira-comment-template.md`。默认 `automatic_comment` 模式不要求提交前确认；`--dry-run` 只用于测试或排查，不是自动化链路前置条件。

写回脚本只接受 `conclusion.json`，Jira ID 只能来自结论输入元数据，命令行不能替换目标。脚本只调用 Jira v2 新增评论接口，不开放状态、负责人、优先级、标签、既有评论更新或删除。`complete` 和 `partial` 结论都可写回，但评论必须原样披露结论状态、归属、置信度、R/A 核覆盖、事实、推断、竞争假设、未知项、反证与下一步；完整日志不进入评论。

analysis key 由 Jira ID、Evidence Package manifest hash、A-core result hash 与结论策略版本生成，不包含 `generated_at`。评论尾部写入 `[dms-ai-analysis:<key>]`；提交前分页读取既有评论，命中 marker 时记录 `already_exists` 并跳过 POST。该设计覆盖普通重试，以及远端已成功但本地结果未落盘后的再次运行；Jira 未提供本流程使用的服务端 idempotency key，两个并发执行者仍可能在查询与 POST 之间竞态，因此不得声明绝对幂等。

本地输出目录必须不存在且不能与 conclusion 输入重叠。`submitted` 和 `already_exists` 生成 `comment.md`、`writeback_result.json` 与 `jira_response.json`；`dry_run` 不生成远端响应。远端失败时不生成成功工件。POST 成功但响应缺少 comment ID 时仍记录 `submitted`、完整响应和 warning，避免把已发生的外部变更误报为失败。

Jira 用户可见的摘要、事实、推断、竞争假设、未知项、反证和下一步必须包含中文；允许保留必要的英文日志原文、枚举值和技术名词。写回策略固定 `comment_language=zh-CN` 和 `comment_markup=jira_wiki`，模板使用 `h2.` / `h3.`、`*` 与 `bq.`，并在提交前拒绝行首 `#`，避免 Jira renderer 产生重复编号。

`ADASL2-1565` 已完成首个真实写回：英文评论 `8654391` 暴露了英文可读性和 Markdown/Jira Wiki 语法不兼容问题；修复后中文纠正版评论 `8654396` 提交成功。现行边界禁止更新或删除既有评论，因此纠错采用新增评论并生成新 analysis marker。详细证据见 [[02_Projects/DMS/10_Issue_Analysis_Skill/Current Maintenance Records/2026-07-13-ADASL2-1565真实端到端验证与Jira中文写回修复]]。

## 1.10 Skill 资源规划

```text
analyze-dms-issue/
├── SKILL.md
├── agents/openai.yaml
├── scripts/
│   ├── fetch_lark_issue_context.py
│   ├── fetch_jira_evidence.py
│   ├── resolve_jira_data_path.py
│   ├── test_resolve_jira_data_path.py
│   ├── load_case_data.py
│   ├── build_evidence_package.py
│   ├── analyze_r_core.py（待实现，当前不得生成 r_core_result.json）
│   ├── analyze_a_core.py
│   ├── test_analyze_a_core.py
│   ├── test_r_core_reference_contract.py
│   ├── synthesize_conclusion.py
│   ├── test_synthesize_conclusion.py
│   ├── writeback_jira.py
│   └── test_writeback_jira.py
├── references/
│   ├── lark-base-strategy.json
│   ├── jira-fetch-strategy.json
│   ├── jira-credentials.local.json
│   ├── data-path-resolution-strategy.json
│   ├── data-loader-strategy.json
│   ├── evidence-schema.md
│   ├── r-core-analysis.md
│   ├── r-core-analysis-strategy.json
│   ├── r-a-core-alignment.md
│   ├── a-core-analysis.md
│   ├── a-core-analysis-strategy.json
│   ├── conclusion-policy.json
│   ├── conclusion-policy.md
│   ├── jira-writeback-policy.json
│   └── jira-writeback.md
└── assets/jira-comment-template.md
```

确定性采集、路径硬校验、打包和写回使用脚本；人类路径备注的容错召回与事实解释、竞争假设、根因判断由 Agent/LLM 完成。可变业务规则、信号映射和领域知识放入 references。R 核已完成解释性流程、机器可消费 strategy 和 R/A 对齐合同的分层，但 analyser 仍待实现；A 核已将全量行索引、签名 census、规则版本提示、多锚点选择、跨线程 correlation 扩展和预算控制固化为可测试脚本。当前仓库全量 83 项单元测试通过。

`jira-credentials.local.json` 是本地运行时输入，必须由 `.gitignore` 排除，不属于可提交的 Skill 资源或知识事实源。
