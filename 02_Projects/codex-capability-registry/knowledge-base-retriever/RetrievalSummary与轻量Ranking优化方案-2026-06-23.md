---
type: design_record
status: active
project: Knowledge-Base
module: knowledge-base-retriever
summary: 基于 DMS Tracking A/B 评测修订下一步优化方向：移除 Builder Fix Registry 实现，优先增强原始历史记录的 Retrieval summary，并为 retriever 增加可解释 priority-tier ranking。
sources:
  - 02_Projects/codex-capability-registry/knowledge-base-retriever/DMS-Tracking检索与FixRegistry联动评测-2026-06-23.md
  - 02_Projects/codex-capability-registry/knowledge-base-retriever/项目总览.md
  - 02_Projects/codex-capability-registry/knowledge-base-structure-builder/项目总览.md
scope: Retriever v0.1 下一轮检索质量优化；Builder retrieval summary lint 与 patch proposal；不改变 DMS Tracking 事实。
risks:
  - Retrieval summary 只能作为召回锚点，不得替代正文事实、验证证据或 supersession 记录。
  - proposal 阶段不得触发完整 trace-index/preflight/hash-check；实际 apply 到 Markdown 前才执行最小校验，current、guarded、critical、结论替代等高风险变更需升级完整 preflight。
updated_at: 2026-06-23
---

# 1 Retrieval Summary 与可解释 Ranking 优化方案

## 1.1 结论

基于 DMS Tracking A/B 评测，下一轮不把 Fix Registry 作为 retriever 质量优化主线，并从 Builder 实现中移除 Fix Registry。

原因：

1. 默认 Builder Fix Registry 是 JSON 派生物，当前 retriever 不消费它；实际检索结果没有改善。
2. Markdown 探针显示 registry 作为聚合摘要会抢占 rank 1，但不能直接替代原始 fix 文档。
3. Registry 命中仍必须追读 `source_fix_doc`，否则只是另一个非事实源候选。
4. 本轮真正暴露的问题是 current/overview 聚合引用压过原始 fix 文档，以及部分历史记录缺少稳定、短小、可正文支撑的检索锚点。

因此优化顺序改为：

1. 先增强原始 fix / decision / validation 记录自身的可检索性。
2. 再调整 retriever 的可解释 ranking，使原始历史记录优先于 current/overview 的来源列表命中。
3. 移除 Builder Fix Registry 实现，不把 registry 消费作为下一步默认实现目标。

## 1.2 Retrieval Summary 规范

每条历史 fix / decision / validation 记录可以增加一个短小 section：

```markdown
## Retrieval Summary

- topic:
- component:
- symptoms:
- affected_paths:
- symbols:
- constraints:
- validation:
- aliases:
```

要求：

- 每个字段必须能在正文、frontmatter、验证记录或 source/evidence 引用中找到支撑。
- 用短语或短句，避免段落化复述。
- `symptoms` 应包含用户可能描述的问题表现、错误文本或失败模式。
- `aliases` 只放确有历史用法或合理中英文/新旧名称映射的别名。
- `constraints` 只放后续修改必须保持或禁止发生的约束。
- 不得把无正文支撑的关键词、同义词堆砌进 summary。
- Retrieval Summary 与正文冲突时，以正文及其证据为准。

## 1.3 Builder 侧职责变更

Builder 移除 Fix Registry 实现，新增三类 authoring 支持：

1. lint 检查 fix / decision / validation 记录是否存在 `Retrieval Summary` 或 `Retrieval Anchors` section。
2. 对缺少 summary 的历史记录生成 patch proposal，不自动改写原文，proposal 阶段不跑 trace-index/preflight/hash-check。
3. lint 检查 summary 质量：
   - section 不应过长；
   - 关键词数量应有上限；
   - summary 中的 code/path/symbol 锚点必须能在正文或 frontmatter 中找到支撑；
   - 实际 apply 时，Retrieval Summary append 先跑 `minimal-apply-check`；current、guarded、critical、结论替代、supersession 等高风险目标升级完整 preflight。

Builder 输出的 proposal 应至少包含：

- target path
- gate reason
- recommended apply check
- proposed section
- supporting source lines or text snippets
- unsupported anchors requiring manual review

## 1.4 Retriever 侧职责变更

Retriever 不读取 Fix Registry JSON 作为下一步默认实现。

下一轮只做可解释 priority-tier ranking，不引入复杂搜索引擎，也不使用隐式复杂评分：

1. 显式优先级：
   - `P1 original_record_retrieval_summary`：原始 fix / decision / validation / incident / maintenance 记录命中 Retrieval Summary。
   - `P2 original_record_body_or_title`：原始记录命中正文或标题。
   - `P3 current_or_overview_body`：current / overview 命中正文。
   - `P4 ordinary_body_or_title`：其他文档命中正文或标题。
   - `P5 metadata_source_or_aggregate_only`：只命中 frontmatter、sources/evidence_refs 列表，或 current/overview 聚合来源而无正文命中。
2. 同级 tie-break：
   - exact/title batch 优先；
   - symptom batch 优先；
   - 多 query term、多 query batch 优先；
   - 再按 hit_count 和 path 做确定性排序。
3. 输出可解释性：
   - `candidate_documents` 应包含 `rank_priority`、`rank_tier`、`rank_rules`、`rank_tie_breakers`。
   - 不输出或依赖 `rank_score`，避免把检索排序理解成不可解释的综合相关性分数。

## 1.5 实施切片

### 1.5.1 Step 1：写回方案

- 新增本方案记录。
- 同步 retriever/builder 子项目总览。
- 不修改 DMS Tracking current 文档。

### 1.5.2 Step 2：Retriever 可解释 priority-tier ranking

- 在 `kb_retrieve.py` 中替换单纯 `hit_count` 排序。
- 保持 `retrieval_package` schema 兼容，只给 `candidate_documents` 增加可选排名解释字段。
- 不读取 registry JSON。
- 不改变 query plan schema。

### 1.5.3 Step 3：Builder Retrieval Summary lint/proposal

- 在 `kb.py lint` 中增加 retrieval summary 相关 finding。
- 新增 proposal 命令或等价子命令，生成 patch proposal 到 reports，而不是直接改 Markdown。
- proposal 阶段不跑 trace-index、preflight 或 hash-check；只有实际 apply 到 Markdown 时才执行最小校验。
- 对 current、guarded、critical、结论替代和 supersession 等高风险变更升级完整 preflight。
- 默认 timestamped reports 每类最多保留最新 3 条，包括 lint、preflight、minimal-apply-check 和 retrieval-summary-proposals。

### 1.5.4 Step 4：回归评测

- 复跑 DMS Tracking 三个场景。
- 重点比较原始 fix 文档 rank，而不是只看 Recall@10。
- 若 hand continuity 原始修复仍在 rank 10 之后，优先生成该记录的 Retrieval Summary proposal，不直接改 verified/current。

## 1.6 非目标

- 不把 Fix Registry 作为 retriever 当前事实源或默认优化路径；Builder 不保留 Fix Registry CLI 或生成逻辑。
- 不自动修改 DMS Tracking verified/current 文档。
- 不自动提升正式知识。
- 不引入 BM25、embedding、FTS5 或外部分词。
- 不让 Builder 生成自然语言 query plan。

## 1.7 验收标准

- Retriever 在 DMS Tracking 三个基准中不降低 Recall@10。
- 原始 fix 文档 rank 不被 current/overview 的 `sources` 列表系统性压低。
- 排序输出必须能用 `rank_priority` / `rank_rules` 解释，不使用隐式复杂 `rank_score`。
- Builder 能找出缺少 Retrieval Summary 的 fix/decision/validation 记录。
- Builder 对缺少 summary 的记录只生成 patch proposal；approved Retrieval Summary append 走 `minimal-apply-check`，不默认触发完整 preflight。
- Summary lint 能识别明显关键词堆砌和无正文支撑的锚点。
