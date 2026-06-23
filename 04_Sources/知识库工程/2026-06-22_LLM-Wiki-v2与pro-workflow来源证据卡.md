---
type: source_card
status: active
source_type: web
source:
  - https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2
  - https://github.com/rohitg00/pro-workflow
summary: 汇总 LLM Wiki v2 的生命周期与自动维护建议，以及 pro-workflow 的 Markdown、SQLite FTS5、lint、reindex 和自动检索实现参考。
scope: 知识库维护治理、派生索引、生命周期、检索和自动化设计参考。
risks:
  - 两份材料面向通用或英文知识库，不能证明默认 FTS5 tokenizer 适合中文内容。
  - pro-workflow 的 SQLite schema 和自动化策略不得直接替代本库 Markdown 事实源及人工提升门禁。
  - LLM Wiki v2 的浮点 confidence、遗忘曲线、知识图谱和自动冲突处理不适合作为本项目早期默认能力。
updated_at: 2026-06-22
---

# 1 LLM Wiki v2 与 pro-workflow 来源证据卡

## 1.1 来源

- LLM Wiki v2：https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2
- pro-workflow：https://github.com/rohitg00/pro-workflow

## 1.2 可借鉴内容

- Markdown 保持为可读、可版本控制的主存储。
- 用 SQLite FTS5 等方式建立可重建的影子索引。
- 分离页面、来源、索引和派生工件。
- 提供 reindex、lint、research seed 和查询注入能力。
- 将生命周期、supersession、陈旧度、审计和隐私纳入维护设计。

## 1.3 不直接采用内容

- 不把 claim-level 浮点 confidence 作为 P0 能力。
- 不在未评测 tokenizer 前假设 BM25 对中文有效。
- 不让 SQLite、索引摘要或 preflight 报告成为事实源。
- 不允许外部内容自动提升到正式知识。
- 不自动改写 verified/current 内容、解决冲突或删除历史。
- 不在查询评测证明必要前建设向量检索或知识图谱。

## 1.4 对当前项目的作用

方案的强制边界以本库 [[AGENTS]] 为准。
