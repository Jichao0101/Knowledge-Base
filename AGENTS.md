
## 0.1 Scope
本文件只定义知识库使用边界，不定义主代理运行治理，不定义多角色调度规则，不定义 plugin 路由顺序。

本文件负责：
- 知识目录语义
- 目录访问授权
- 文件写入分层
- 外部信息入库约束
- 正式知识提升条件
- 知识写入前门禁与自动化写入边界

本文件不负责：
- 主代理角色约束
- workflow-orchestrator 行为规范
- reviewer 独立性控制
- rework 轮次控制
- plugin 启动与路由规则
- 代码执行链调度
- lint、索引、gate 的工具实现、规则表和报告格式

这些运行治理要求不由本文件规定。

---

## 0.2 Core principles
1. **只在授权范围内读取**
   未授权目录不得读取，不因文件系统可见而视为可读。

2. **先分层，再写入**
   内容写入前，先判断属于正式知识、项目内容、候选内容还是原始来源。

3. **外部信息不得直接入正式知识区**
   网络信息、网页摘录、外部摘要、未审整理结果，必须先进入候选区或来源区。

4. **正式知识必须可复用且边界清晰**
   若内容没有明确来源、适用范围、风险或不适用范围，则不得进入正式知识区。

5. **项目内容优先留在项目区**
   与当前项目强绑定、尚未抽象为通用知识的内容，应优先写入项目区。

6. **写入门禁发生在修改前**
   知识库事实文件的创建、修改、移动、删除或替代，必须在首次文件变更前完成 preflight；写后 lint 不得替代写前门禁。

7. **派生产物不是事实源**
   索引、缓存、lint 报告和 preflight 报告均为可重建派生物，不得替代 Markdown 原文、current 入口或正式证据记录。

---

## 0.3 Directory semantics
- `01_Knowledge/`：正式知识区。仅存已审核、可复用、边界清晰的知识。
- `02_Projects/`：项目工作区。存需求、设计、实验、实现、调试、决策、阶段性审查结果。
- `03_Inbox/`：候选区。存待分类、待审核、待整理内容。
- `04_Sources/`：来源区。存外部原始摘录、网页信息、论文摘要、PDF阅读记录、证据卡片。
- `90_Archive/`：归档区。存历史、冻结、失效或不再维护内容。

---

## 0.4 Access rules

### 0.4.1 Read scope
读取本地内容时，只能读取已授权目录。

默认读取顺序建议为：
1. 若存在对应总览、项目入口、模块入口或 `overview_current`，先读取入口文件确认默认读取顺序和当前事实源。
2. 当前任务直接相关的 `02_Projects/...`
3. 已授权的 `01_Knowledge/...`
4. 已授权的 `04_Sources/...`
5. 必要时读取已授权的 `03_Inbox/...`

常用入口：
- 全库入口：`README.md`
- 正式知识入口：`01_Knowledge/知识总览.md`
- 项目区入口：`02_Projects/项目总览.md`
- DMS 项目入口：`02_Projects/DMS/DMS项目总览.md`
- 候选区入口：`03_Inbox/候选内容索引.md`
- 来源区入口：`04_Sources/来源索引.md`
- 结构审计入口：`02_Projects/Knowledge-Base/知识库结构审计_current.md`

若任务命中某个项目模块，且该模块存在 `*_overview_current.md` 或 `overview_current.md`：
- 默认先读 overview/current 入口
- 再按入口文件列出的恢复顺序读取 design/spec/implementation/validation 或补充来源
- 不从历史记录、运行工件、baseline 或 delta 文件直接开始，除非任务明确要求追溯历史

若某目录未被授权：
- 不得读取
- 不得基于其内容做事实性判断
- 不得声称“按该目录中的内容执行过”

### 0.4.2 Missing authorization
若当前任务缺少目录授权信息：
- 可以说明缺少哪些授权
- 可以请求补充授权范围
- 不得擅自扩大读取范围

是否允许在无授权下进行任务画像、route_resolution 或 intake，不由本文件规定。

---
## 0.5 Runtime discovery exception
本文件仅约束知识内容读取、写入分层与正式入库，不限制用户级 Codex / agent 运行时配置与能力发现。

以下路径若用于 runtime discovery、plugin/skill/config 读取、能力启用状态判断，可访问：
- `~/.codex/`
- `~/.codex/config.toml`
- 用户级 Codex skills / plugins / agents 相关目录
- 当前项目及上级目录中的 `.codex/`
- 当前项目及上级目录中的 `AGENTS.md`
- 本地工作流约定的用户级 agent runtime 目录（如 `~/.agents/`、`~/.agents/plugins/`、`~/.agents/skills/`，若本地环境实际采用）

限制：
- 这些路径仅用于 runtime 配置发现、能力判断、plugin/skill/agent 启用状态确认
- 不得将其中内容默认视为项目知识背景
- 若要把其中内容作为知识上下文引用，仍需满足知识访问授权规则
- 不得因此扩大为对整个用户目录的自由读取

### 0.5.1 Current 文档组硬约束
维护项目区 current 文档组时：

- 不得默认整组重写 current 文档组。
- 不得把历史记录、运行工件、baseline 或 delta 文件直接当作当前事实源。
- 不得把已删除或失效的同步规范作为 active dependency。
- 未完成独立 recoverability verification 时，不得新增或保留 `single_pass_recoverable: true`。
- 涉及 current 入口、事实源、状态或 recoverability 变化时，必须同步更新对应 `overview_current`、项目总览和结构审计记录。

### 0.5.2 知识写入门禁硬约束

以下约束适用于知识库事实文件的创建、修改、移动、删除和结论替代；可重建 cache/report 的生成不因此获得事实源地位。

1. 写入前必须基于已授权范围执行 preflight，并明确目标路径和本次 change intent。
2. 门禁结果为 `blocked` 时不得写入；结果为 `manual_review` 时，必须获得用户或授权 reviewer 的显式确认；结果为 `allow` 时，只允许执行本次目标、意图和输入快照对应的变更。
3. verified、guarded、critical 或内容扫描命中 active constraints 的文档不得被自动化直接改写；自动化只能生成 proposal、patch draft、候选摘要或验证计划。
4. 对 append-only 内容，不得改写或删除既有历史事实；更正只能追加说明或建立新的替代记录。
5. 替代旧结论时，必须显式记录双向 supersession、替代原因和验证证据，不得静默覆盖。
6. Traceability Index 只用于召回候选。命中 strong 记录或 guarded/critical 来源时，必须读取对应 Markdown 原文后才能继续，索引摘要不得作为事实依据。
7. 授权不足、目标或命中原文不可读、规则/索引缺失或过期、输入 hash 变化、supersession 冲突未解决时，高风险写入必须 fail-closed。
8. 自动化不得自动提升正式知识、修改受保护文档、关闭 supersession 冲突、删除历史记录、提高 evidence level 或声明 `single_pass_recoverable: true`。
9. `.kb_cache/`、`reports/kb/` 及同类索引/报告目录默认不进入事实读取顺序；若报告需要成为验证依据，必须由正式项目记录显式引用其路径与 hash。

---

## 0.6 File placement rules

### 0.6.1 Write to `01_Knowledge/`
只有满足以下条件时，才允许写入正式知识区：
- 内容已审核
- 来源明确
- 具有复用价值
- 适用范围明确
- 风险或不适用范围明确

适合写入正式知识区的内容包括：
- 已验证机制
- 稳定设计模式
- 常见失败模式
- 可复用验证模式
- 稳定集成约束
- 高复用经验总结
- 决策启发式总结

### 0.6.2 Write to `02_Projects/`
以下内容优先写入项目区：
- 需求拆解
- 设计方案
- 实验记录
- 实现计划
- 调试记录
- 阶段性分析
- 决策记录
- 与当前项目强绑定、尚未抽象为通用知识的内容

### 0.6.3 Write to `03_Inbox/`
以下内容优先写入候选区：
- 网络信息候选
- 临时摘录
- 待分类内容
- 待审核摘要
- 尚未确认是否值得沉淀的外部信息

### 0.6.4 Write to `04_Sources/`
以下内容优先写入来源区：
- 原始网页摘录
- 文献摘要
- PDF阅读笔记
- 外部来源证据卡片
- 需要保留原始出处的信息整理

### 0.6.5 Entry and overview sync
涉及新增、移动、重命名、删除或改变当前事实源的写入，必须同步维护相应入口：

- 新增正式知识：更新 `01_Knowledge/知识总览.md` 或对应主题总览。
- 新增项目或项目模块：更新 `02_Projects/项目总览.md`、项目总览或模块索引。
- 新增/维护 current 文档组：更新模块 `overview_current`、项目总览和必要的结构审计记录。
- 新增候选内容：更新 `03_Inbox/候选内容索引.md`。
- 新增来源证据卡：更新 `04_Sources/来源索引.md`。
- 改变 current 标准化状态、recoverability 状态或总览结构策略：更新 `02_Projects/Knowledge-Base/知识库结构审计_current.md` 或后续结构审计记录。

若只做正文内的小修订，且不改变入口、状态、范围或事实源，可不更新总览；但结束时应说明未同步总览的理由。

---

## 0.7 External information rules
当任务允许联网且本地上下文不足时，外部信息处理遵循以下规则：

1. 外部信息先进入 `03_Inbox/` 或 `04_Sources/`
2. 不得直接写入 `01_Knowledge/`
3. 若后续需要正式沉淀，必须经过审核与结构化整理
4. 对外部信息的整理结果应保留来源信息

---

## 0.8 Promotion rules
只有满足以下条件时，才允许将内容提升到 `01_Knowledge/`：

1. 已完成审核
2. 至少有可信来源或明确内部依据
3. 内容不是原文堆叠，而是经过结构化总结
4. 具有明确复用价值
5. 已写明适用范围
6. 已写明风险、不适用范围或边界条件

若不满足上述条件，则内容应保留在：
- `02_Projects/`
- `03_Inbox/`
- `04_Sources/`

---

## 0.9 Minimal metadata expectations

### 0.9.1 Candidate content
候选内容建议至少包含：
- 标题
- 摘要
- 来源
- 状态（如 `draft` / `pending_review`）
- 可能的目标路径
- 适用范围或主题说明

### 0.9.2 Knowledge content
正式知识建议至少包含：
- 标题
- 摘要
- 来源
- 适用范围
- 风险或不适用范围
- 状态（如 `verified`）

---

## 0.10 Output expectations
涉及知识库读写的任务结束时，建议至少说明：

### 0.10.1 Summary
- allowed_paths:
- files_read:
- files_written:

### 0.10.2 Placement
- candidate_created:
- source_notes_created:
- promoted_to_knowledge:

### 0.10.3 Risks / uncertainties
- missing_authorization:
- promotion_blockers:
- unresolved_items:
