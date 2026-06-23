---
type: design_record
status: active
project: Knowledge-Base
module: knowledge-base-retriever
summary: 基于 DMS Tracking A/B 评测修订下一步优化方向：移除 Builder Fix Registry 实现，优先增强原始历史记录的 Retrieval summary，并为 retriever 增加轻量 ranking。
sources:
  - 02_Projects/Knowledge-Base/knowledge-base-retriever/DMS-Tracking检索与FixRegistry联动评测-2026-06-23.md
  - 02_Projects/Knowledge-Base/knowledge-base-retriever/项目总览.md
  - 02_Projects/Knowledge-Base/knowledge-base-structure-builder/项目总览.md
scope: Retriever v0.1 下一轮检索质量优化；Builder retrieval summary lint 与 patch proposal；不改变 DMS Tracking 事实。
risks:
  - Retrieval summary 只能作为召回锚点，不得替代正文事实、验证证据或 supersession 记录。
  - 自动化不得直接改写 verified、guarded、critical 或 current 文档；只能生成候选 patch proposal。
updated_at: 2026-06-23
---

# 1 Retrieval Summary 与轻量 Ranking 优化方案

## 1.1 结论

基于 DMS Tracking A/B 评测，下一轮不把 Fix Registry 作为 retriever 质量优化主线，并从 Builder 实现中移除 Fix Registry。

原因：

1. 默认 Builder Fix Registry 是 JSON 派生物，当前 retriever 不消费它；实际检索结果没有改善。
2. Markdown 探针显示 registry 作为聚合摘要会抢占 rank 1，但不能直接替代原始 fix 文档。
3. Registry 命中仍必须追读 `source_fix_doc`，否则只是另一个非事实源候选。
4. 本轮真正暴露的问题是 current/overview 聚合引用压过原始 fix 文档，以及部分历史记录缺少稳定、短小、可正文支撑的检索锚点。

因此优化顺序改为：

1. 先增强原始 fix / decision / validation 记录自身的可检索性。
2. 再调整 retriever 的轻量 ranking，使原始历史记录优先于 current/overview 的来源列表命中。
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
2. 对缺少 summary 的历史记录生成 patch proposal，不自动改写原文。
3. lint 检查 summary 质量：
   - section 不应过长；
   - 关键词数量应有上限；
   - summary 中的 code/path/symbol 锚点必须能在正文或 frontmatter 中找到支撑；
   - current / verified / guarded / critical 文档只能 proposal，不自动写入。

Builder 输出的 proposal 应至少包含：

- target path
- gate reason
- proposed section
- supporting source lines or text snippets
- unsupported anchors requiring manual review

## 1.4 Retriever 侧职责变更

Retriever 不读取 Fix Registry JSON 作为下一步默认实现。

下一轮只做轻量 ranking，不引入复杂搜索引擎：

1. 文档类型权重：
   - original fix / decision / validation / incident 记录优先；
   - current 文档保留高可信入口价值，但当命中只发生在 frontmatter `sources` 列表时降权；
   - overview / project entry / hardening inventory 等聚合入口不应压过原始 fix。
2. 命中位置权重：
   - `Retrieval Summary`、标题和正文问题段优先；
   - frontmatter `sources` / `evidence_refs` 列表命中降权；
   - 单个宽泛词命中如 `driver face`、`sanitize` 不应压过精确症状或标题命中。
3. 查询批次权重：
   - `exact_history_titles` 和 symptom batch 高于 broad code anchors；
   - structure/current batch 主要用于发现入口，不直接压过 fix 原文。
4. 输出可解释性：
   - `candidate_documents` 应包含 `rank_score`、`rank_reason` 或等价字段，方便后续评测定位排序原因。

## 1.5 实施切片

### Step 1：写回方案

- 新增本方案记录。
- 同步 retriever/builder 子项目总览。
- 不修改 DMS Tracking current 文档。

### Step 2：Retriever 轻量 ranking

- 在 `kb_retrieve.py` 中替换单纯 `hit_count` 排序。
- 保持 `retrieval_package` schema 兼容，只给 `candidate_documents` 增加可选排名字段。
- 不读取 registry JSON。
- 不改变 query plan schema。

### Step 3：Builder Retrieval Summary lint/proposal

- 在 `kb.py lint` 中增加 retrieval summary 相关 finding。
- 新增 proposal 命令或等价子命令，生成 patch proposal 到 reports，而不是直接改 Markdown。
- 对 guarded/current/verified/critical 文档只输出 proposal。
- 默认 timestamped reports 每类最多保留最新 3 条，包括 lint、preflight 和 retrieval-summary-proposals。

### Step 4：回归评测

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
- Builder 能找出缺少 Retrieval Summary 的 fix/decision/validation 记录。
- Builder 对缺少 summary 的记录只生成 patch proposal，不直接改写 guarded/current/verified 文档。
- Summary lint 能识别明显关键词堆砌和无正文支撑的锚点。
