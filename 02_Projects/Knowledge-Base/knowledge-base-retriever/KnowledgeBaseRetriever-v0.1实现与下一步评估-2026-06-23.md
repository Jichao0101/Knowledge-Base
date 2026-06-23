---
type: implementation_record
status: completed
project: Knowledge-Base
module: knowledge-base-retriever
summary: 记录 knowledge-base-retriever v0.1 skill 的实现边界、验证证据，以及下一步应进入项目测试而不是继续堆叠 v1 功能。
sources:
  - /mnt/d/codex-capability-registry/skills/knowledge-base-retriever/SKILL.md
  - /mnt/d/codex-capability-registry/skills/knowledge-base-retriever/scripts/kb_retrieve.py
  - /mnt/d/codex-capability-registry/skills/knowledge-base-retriever/agents/openai.yaml
scope: Retriever v0.1 implementation, validation evidence, next-step decision.
risks:
  - v0.1 只完成 skill 结构、脚本边界和局部夹具验证，尚未在真实历史问题基准上评估 recall。
  - query_plan 质量仍取决于 agent 对问题语义、旧名称、症状和授权入口的拆解能力。
updated_at: 2026-06-23
---

# 1 KnowledgeBaseRetriever v0.1 实现与下一步评估

## 1.1 实现摘要

`knowledge-base-retriever` 已在 capability registry 中新建为独立 skill：

- skill 路径：`/mnt/d/codex-capability-registry/skills/knowledge-base-retriever`
- 入口说明：`SKILL.md`
- 执行脚本：`scripts/kb_retrieve.py`
- agent 配置：`agents/openai.yaml`

v0.1 的架构边界为：

- agent 负责语义 Query Planning，包括 query facets、旧名称推断、症状归类和多批 `rg` 查询设计。
- script 只负责 deterministic `rg` execution、Markdown section extraction 和 `retrieval_package` formatting。
- script 不接收 `--question`，只接收结构化 query plan 与必填 `authorized_paths`。
- script 不自行理解问题，不做中文分词、同义词扩展、旧名称推断或症状分类。
- script 不计算文档 hash；已有索引或调用方提供 hash 时，后续可作为可选字段透传。

## 1.2 已实现约束

query plan 验证已覆盖：

- `batches` 和 `terms` 类型校验。
- 空 term 拒绝。
- `candidate_field` 只允许 `candidate_decisions`、`candidate_constraints`、`candidate_fixes`、`candidate_supersessions`。
- `max_batches`、`max_terms_per_batch`、`max_term_length`、`max_total_terms` 上限。
- term 中换行和控制字符拒绝。
- batch 内 term 去重。

section extraction 已覆盖：

- heading 边界只识别 `^#{1,6}\s+`。
- fenced code block 内 heading-like 行不作为 section 边界。
- `rg` 命中代码块可以保留，但不会让代码块内的 `#include`、shell prompt 或注释干扰 section 切分。

section 读取顺序已加入简单多样性：

- 每个 candidate document 优先读取 1 个 section。
- 每个 document 默认最多读取 2 个 section。
- 剩余 quota 再按 hit count 补充。

## 1.3 验证证据

已执行的验证：

- skill quick validation 通过。
- 正常 query plan 样例可生成 `retrieval_package`。
- 旧接口 `--question` 被拒绝。
- 非法 `candidate_field` 被拒绝。
- 超过单批 term 上限的 query plan 被拒绝。
- term 含换行或控制字符时被拒绝。
- 本地夹具验证了 term 去重、fenced code block heading 忽略和跨文档 section 多样性。

这些验证只证明 v0.1 的实现边界、输入约束和 section extraction 行为成立，不证明真实知识库问题的召回率已经达标。

## 1.4 下一步判断

当前不应继续做下一轮 v1 功能优化，应先进入项目测试。

理由：

- v0.1 的核心风险已经不在脚本能力，而在 agent 生成 query_plan 的语义质量。
- 继续把中文分词、同义词扩展、旧名称推断或症状分类写进脚本，会把 deterministic executor 推向低质量 NLP 系统。
- 是否需要 FTS5、BM25、embedding 或 Fix Registry 联动，必须先通过真实历史问题基准暴露 recall 缺口。
- Builder 侧真正需要的是 package 覆盖范围、source sections 和 recall limitations；这些字段已经具备测试入口。

## 1.5 项目测试建议

下一步建立小型项目测试集，至少覆盖：

- DMS Tracking 历史修复：旧名称、症状描述、代码符号和 validation/current 入口混合召回。
- Knowledge-Base 治理历史：lint、preflight、Traceability Index、Fix Registry 和 supersession 相关记录召回。
- cutepower 或 runtime 项目记录：项目级与子项目级授权路径差异。
- 无命中场景：确认输出为 `no_match_within_authorized_scope` 或明确 recall limitation，而不是“历史不存在”。

建议指标：

- Recall@5 / Recall@10。
- 首个相关 source section 出现位置。
- candidate document 覆盖多样性。
- 授权路径泄露次数，目标为 0。
- recall_limitations 是否准确描述 query_plan 覆盖不足、未读路径或无命中边界。

项目测试完成前，不建议扩大 v1 功能面。
