---
type: knowledge
status: verified
unit_type: workflow_pattern
domain: 工程工作流
topic: Codex Skill开发与脚本化边界规范
sources:
  - 用户提供的《Codex Skill 开发指导文档》整理
  - /home/jichao/.codex/skills/.system/skill-creator/SKILL.md
scope: 适用于为 Codex 设计和实现可复用 Skill，尤其适用于需要明确触发边界、脚本化主通道、路径约束和验证要求的第一版 Skill。
risks:
  - 将探索性需求过早固化为 Skill
  - 把多项职责混入单一 Skill 导致边界失控
  - 把认证、批量处理或全库扫描塞进第一版主流程
  - description 触发边界不清导致误触发
  - 未做失败路径和端到端验证就共享 Skill
source_task: 根据用户提供材料，优化整理并写入知识库合适位置
evidence:
  - 仓库级 Skill 适合项目专用复用，用户级 Skill 适合跨项目复用
  - 第一版 Skill 必须压缩为单一 job，并显式列出 non-goals
  - 飞书文档导入类 Skill 应优先消费已登录 lark-cli，而不是自管认证
  - 脚本类 Skill 需覆盖语法层、合同层、端到端层三层验证
updated_at: 2026-03-30
summary: "Codex Skill开发与脚本化边界规范 相关的历史知识笔记，归入 Agent Workflow 主题，用于学习、查阅和工程参考。"
---

## 0.1 摘要

Skill 不是“大提示词”，而是可被路由、可被验证、可逐步扩展的工作流包。  
第一版 Skill 应优先做成“单一主任务、触发边界清楚、失败显式、结果可验证”的窄工具，而不是把导入、分类、递归抓取、链接修复、同步等职责揉成一个大而全系统。

---

## 0.2 适用定位

本文档回答五个问题：

1. Skill 应放在仓库级还是用户级
2. 新 Skill 应如何先做抽象，而不是直接写最终版 `SKILL.md`
3. `SKILL.md` 应写什么，哪些内容不该写
4. 何时应保持 instruction-only，何时必须脚本化
5. Skill 落地后应如何做验证与共享

---

## 0.3 放置策略

### 0.3.1 仓库级与用户级

- 仓库级路径：`<repo>/.agents/skills/<skill-name>/`
- 用户级路径：`~/.agents/skills/<skill-name>/`

选择规则：

- 仓库级：适合项目专用 Skill、强依赖当前仓库环境或团队约束的 Skill
- 用户级：适合跨项目复用、可作为个人长期工具箱的 Skill

判断原则不是“放哪里方便”，而是“能力边界是否跨项目稳定”。

---

## 0.4 第一轮先做抽象

### 0.4.1 使用 `skill-creator` 的目标

在第一轮不要直接手写最终 `SKILL.md`，而应先产出抽象骨架：

- Job statement
- Name candidates
- Description candidate
- Use / do-not-use
- Inputs / outputs
- Script judgment
- Open questions

这样做的目的，是先压缩主任务与触发边界，避免模型把上游方案直接复制成一份冗长、失焦的 Skill 文档。

### 0.4.2 单一 job 原则

一个 Skill 第一版只服务一个主任务。  
如果一个 Skill 同时承担导入器、分类器、链接修复器或同步器，它几乎一定会失控。

正确做法是把 Skill 压缩成一句话 job，例如：

> 将单篇飞书富文本文档导入为本地 Obsidian Markdown 笔记；对无法稳定转换的对象执行附件化降级，并输出导入摘要。

### 0.4.3 先定义 non-goals

第一版比“能做什么”更重要的是“不做什么”。  
至少要显式列出非目标，例如：

- 不做批量导入
- 不做双向同步
- 不做 OCR
- 不做评论同步
- 不扫描整个 vault
- 不修改既有笔记
- 不做跨文档链接映射

这些 non-goals 的作用是防止 Skill 从窄工具膨胀成不可控平台。

---

## 0.5 `SKILL.md` 编写合同

### 0.5.1 元信息要求

最小 frontmatter 只保留：

```yaml
---
name: lark-doc-to-obsidian
description: Import one Feishu/Lark rich-text document into a local Obsidian vault as a Markdown note. Use when Codex needs to fetch a single document, convert basic supported content to Markdown, downgrade unsupported objects into local attachments or placeholders, and verify only links created for that import. Do not use for batch import, bidirectional sync, OCR, comment sync, whole-vault scans, modifying existing notes, or cross-document link mapping.
---
```

约束如下：

- `name` 要短、单义，并尽量同时包含源端与目标端
- `description` 必须同时包含 use 与 do-not-use
- `description` 负责触发路由，不应写成宣传文案
- 不要把实现细节、长背景或讨论过程塞进 `description`

### 0.5.2 正文只写执行合同

正文建议只保留执行所需的稳定结构，例如：

- Goal
- Inputs
- Core job / Workflow
- Conversion rules
- Path rules
- Link verification rules
- Summary output
- Non-goals
- Execution guidance

不建议写入：

- 冗长背景介绍
- 需求来源回放
- 与当前 Skill 无关的通用原则
- 上游讨论纪要全文复制

Skill 正文应该像操作合同，而不是设计复盘。

---

## 0.6 Instruction-only 与 Script-backed 的分界

### 0.6.1 适合 instruction-only 的场景

当任务主要依赖分析步骤、外部系统弱、结果以文本判断为主、失败成本低时，可以只写说明。

### 0.6.2 必须脚本化的场景

当任务同时具备以下一项或多项时，应优先脚本化：

- 需要远程读取数据
- 需要调用 CLI 或 API
- 需要严格路径规则
- 需要稳定落盘逻辑
- 需要结构化校验

例如“飞书文档 -> Obsidian Markdown”就应视为 script-backed Skill，因为它涉及 token 解析、远程读取、JSON 校验、Markdown 写入、附件路径约束与本地链接验证。

---

## 0.7 外部系统接入原则

### 0.7.1 优先消费已验证主通道

接入带权限的外部系统时，应先判断：

- 权限是否依赖用户身份
- 是否已有可登录 CLI
- 是否存在对象类型分流
- 是否有异步导出任务

若权限由用户身份决定，应优先让 Skill 脚本消费已认证 CLI，而不是自己管理 token、会话和 OAuth。

### 0.7.2 飞书到 Obsidian 的第一版约束

对于飞书文档导入类 Skill，推荐主通道固定为已登录的 `lark-cli`，并采用最小状态机：

```text
input
-> parse wiki token
-> lark-cli wiki spaces get_node
-> read obj_type + obj_token
-> if obj_type == docx
-> lark-cli docs +fetch --doc <obj_token>
-> convert current document only
-> write markdown + assets
-> verify local links in this note only
-> print summary
```

第一版建议固定为：

- 输入：wiki URL 或 wiki token
- 路由：`wiki spaces get_node -> obj_type / obj_token -> docs +fetch`
- 支持对象：仅 `docx`
- mention-doc：原样保留，不递归展开
- 只转换当前文档
- 只校验当前 note 中指向当前 assets 目录的链接

### 0.7.3 不把认证写进 Skill 主流程

第一版脚本不要负责：

- 交互式登录
- token 生命周期管理
- 多账号切换
- 浏览器 OAuth 回调
- 会话缓存治理

这些属于外部 CLI 的职责，不应与 Skill 主 job 混合。

---

## 0.8 错误与路径规则

### 0.8.1 错误分层

脚本类 Skill 不应只抛出一个泛化异常，而应把错误定位到具体阶段。  
推荐显式区分：

- `CliNotFoundError`
- `CliCommandError`
- `InvalidJsonError`
- `MissingFieldError`
- `UnsupportedObjTypeError`
- `TargetFileExistsError`

判断标准：

- 错误必须定位到阶段，例如 `get_node` 失败或 `docs +fetch` 失败
- 错误必须指出缺失字段或无效数据
- 第一版不支持的对象类型应直接报错，而不是静默降级

### 0.8.2 路径与落盘约束

第一版应尽量使用硬约束：

- 默认要求调用方显式提供 `--note-path`
- 若只给 `--note-dir`，固定命名为 `<document-title>.md`
- 默认附件目录为 `<note_stem>.assets/`
- 仅检查当前 Markdown 中指向当前附件目录的本地链接
- 不扫描整个 vault
- 不修改既有笔记
- 目标 note 已存在时默认拒绝覆盖

导入器的职责是“单次可验证落盘”，不是“自动知识库整理器”。

---

## 0.9 验证与发布

### 0.9.1 三层验证

每个 Skill 至少通过三层验证：

1. 语法层：例如 `python3 -m py_compile`
2. 合同层：验证 CLI 缺失、非 JSON、缺字段、不支持对象、目标文件已存在等失败路径
3. 端到端层：至少选择一个真实对象，验证读取、写入、mention-doc 保留、路径规则和链接检查边界

### 0.9.2 共享路径

共享优先级应为：

1. 先共享整个 Skill 目录
2. 在小范围验证稳定后，再考虑升级为 Plugin

Plugin 更适合长期团队分发、版本化安装和多能力打包；不要在第一版就过早插件化。

---

## 0.10 开发禁忌

以下做法应避免：

- 直接把需求方案整段复制进 `SKILL.md`
- 第一版同时做导入、分类、递归抓取、链接重写
- 让脚本自管复杂认证
- 为了“更智能”扩大扫描范围
- 默认覆盖已有文件
- 对不支持对象静默丢弃
- 用脆弱字符串截取替代 JSON 解析

---
## 0.11 推荐的最小目录模板

```
<repo>/.agents/skills/lark-doc-to-obsidian/
├── SKILL.md
├── scripts/
│   └── import_lark_doc.py
├── references/
│   └── cli-usage.md
└── README.md
```
### 0.11.1 `README.md` 建议包含

- Skill 作用
- 依赖安装说明
- `lark-cli` 登录要求
- 调用示例
- 已知限制
- 版本记录

---
## 0.12 一句话原则

第一版 Skill 应优先做成“边界窄、路径硬、失败显式、结果可验证”的工具；  
只有在该核心链路稳定后，才逐步扩展分类、批处理、同步或更强自动化能力。
