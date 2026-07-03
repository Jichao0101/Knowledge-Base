---
type: evaluation_record
status: completed
project: Knowledge-Base
module: knowledge-base-retriever
summary: 记录 knowledge-base-retriever v0.1 在 DMS Tracking 历史问题上的无索引基线、Builder Fix Registry 构建结果和 registry 消费集成缺口。
sources:
  - 02_Projects/codex-capability-registry/knowledge-base-retriever/项目总览.md
  - 02_Projects/codex-capability-registry/knowledge-base-structure-builder/项目总览.md
  - 02_Projects/DMS/04_Tracking/tracking_overview_current.md
  - 02_Projects/DMS/04_Tracking/tracking_validation_current.md
  - reports/kb/retrieval-eval/2026-06-23-dms-tracking/metrics_summary.json
scope: DMS Tracking 项目测试；Retriever v0.1 query plan、authorized-path 检索、source section 读取和 Fix Registry 联动评估。
risks:
  - 本记录只评估检索召回与工具集成，不评价 DMS Tracking 业务修复本身。
  - reports/kb 与 .kb_cache 产物均为派生证据，不替代 Markdown 原文和 current 文档。
updated_at: 2026-06-23
---

# 1 DMS Tracking 检索与 Fix Registry 联动评测

## 1.1 评测目标

本轮评测用于回答两个问题：

1. `knowledge-base-retriever` v0.1 在没有 Fix Registry 参与时，是否能依靠 agent-authored query plan、`rg` 和 Markdown section extraction 召回 DMS Tracking 历史修复。
2. `knowledge-base-structure-builder` 生成的 DMS Tracking Fix Registry 是否能被当前 retriever 实际消费，并改善历史修复入口。

本轮不修改 DMS Tracking 业务 current 文档，不改变 Tracking 事实源或验证状态。

## 1.2 授权范围与输入

- 知识库根目录：`/mnt/d/Knowledge-Base`
- 主检索授权范围：`02_Projects/DMS/04_Tracking`
- 写回授权范围：`02_Projects/Knowledge-Base`
- Fix Registry 生成范围：`02_Projects/DMS/04_Tracking`
- 派生评测包：`reports/kb/retrieval-eval/2026-06-23-dms-tracking/`
- metrics summary hash：`83596c7b9772374e1bb48013805b285ce3b24fe232c45109b53e9b288f61a846`
- Fix Registry report hash：`ed56d07bb4344ae947050cef4c8c9d1ceb76aef1ce6d867b36aad4995236429b`

测试集包含三个 DMS Tracking 历史问题：

| 场景 | 期望目标文档 |
|---|---|
| 2m 后排 head/face 误绑定主驾 | `2m摄像头后排head误绑定主驾修复闭环记录-2026-05-08.md`；`后排误跟踪为主驾修复闭环记录-2026-06-12.md` |
| 跟踪框越界 coredump | `跟踪框越界导致板端coredump调查与修复闭环记录-2026-04-07.md` |
| 手部连续性与快速运动恢复 | `多目标跟踪手部连续性优化闭环记录-2026-03-31.md`；`多目标跟踪快速运动恢复阶段预测更新一致性修复闭环记录-2026-04-05.md` |

## 1.3 Round A：无 Fix Registry 基线

Round A 只授权 `02_Projects/DMS/04_Tracking`，不授权 `.kb_cache`。

| 场景 | 目标文档排名 | Recall@5 | Recall@10 | 观察 |
|---|---:|---:|---:|---|
| 2m 后排误绑定主驾 | 5, 3 | 1.0 | 1.0 | 能召回两条目标修复；current/spec/implementation 因引用密集排在前列。 |
| coredump | 1 | 1.0 | 1.0 | 目标 incident/fix 文档 rank 1，精确标题和症状词有效。 |
| hand/快速运动 | 11, 5 | 0.5 | 0.5 | 快速运动修复 rank 5；手部连续性修复被 current/功能审核等文档挤到 rank 11。 |

三组均出现：

- `hit_limit_reached:120`
- `section_read_limit:30`
- `query_understanding_done_by_agent_not_script`
- `hashes_not_computed_by_retriever`

结论：无 registry 基线已经具备最低召回能力；主要问题不是完全漏召回，而是噪声较高、current 和聚合引用容易压过原始 fix 文档。

## 1.4 Builder Fix Registry 构建

执行 Builder Fix Registry 构建后生成：

- `.kb_cache/fix-registry/02_Projects__DMS__04_Tracking.json`
- entries: 10
- scope: `02_Projects/DMS/04_Tracking`

Registry 包含 2m 后排 head 误绑定、DMS 主驾打哈欠误报、后排乘客头部误跟踪、后排误跟踪主驾、快速运动恢复、生命周期/设计失配、coredump 等历史修复条目。

边界：

- registry 是 `.kb_cache` 下的派生 JSON，不是事实源。
- factual authority 仍是每个 `source_fix_doc` 的 Markdown 原文。
- Retriever 命中 registry 后仍必须读取 `source_fix_doc` 原文 section。

## 1.5 Round B：授权 JSON Registry 后再检索

Round B 授权：

- `02_Projects/DMS/04_Tracking`
- `.kb_cache/fix-registry`

但 retriever v0.1 的执行脚本只遍历 `*.md`，不会搜索 JSON registry。因此默认 JSON registry 未进入候选集。

| 场景 | registry 是否进入候选 | Recall@5 | Recall@10 | 结论 |
|---|---|---:|---:|---|
| 2m 后排误绑定主驾 | 否 | 1.0 | 1.0 | 与 Round A 相同。 |
| coredump | 否 | 1.0 | 1.0 | 与 Round A 相同。 |
| hand/快速运动 | 否 | 0.5 | 0.5 | 与 Round A 基本相同，排名小幅波动来自同分候选顺序。 |

结论：当前“构建 registry 后再检索”没有产生真实集成增益，因为 retriever 没有消费 JSON registry。

## 1.6 Markdown 兼容性探针

为确认问题是否来自文件类型过滤，本轮创建了 `.kb_cache/fix-registry/02_Projects__DMS__04_Tracking.probe.md` 临时派生副本并重新检索。该文件只用于测试，不作为事实源。

结果：

| 场景 | registry probe rank | 目标文档排名变化 | 观察 |
|---|---:|---|---|
| 2m 后排误绑定主驾 | 1 | 5/3 -> 8/7 | Registry 可被 Markdown 遍历命中，但整份 JSON/Markdown 作为单一候选抢占 rank 1，未自动追读 `source_fix_doc`。 |
| coredump | 1 | 1 -> 2 | Registry 可作为入口，但目标原文仍需自动展开。 |
| hand/快速运动 | 1 | 11/5 -> 11/5 | Registry 进入候选但未改善手部连续性原文排名。 |

结论：只让 registry 被 `rg` 搜到不够。Retriever 需要识别 registry 条目结构，把它作为路由入口，然后把对应 `source_fix_doc` 原文 section 插入候选和 source reads。

## 1.7 评测结论

- v0.1 无索引检索对 DMS Tracking 历史修复具备可用基线：三个场景 Recall@10 分别为 1.0、1.0、0.5。
- 当前最大召回弱点是“原始 fix 文档排名被 current、overview、聚合引用和宽泛代码词压低”，不是没有命中。
- Builder Fix Registry 已能从 DMS Tracking 生成 10 条派生 fix 条目。
- 当前 retriever 不能直接消费 Builder 默认 JSON registry；授权 `.kb_cache/fix-registry` 不会带来候选变化。
- Markdown 探针证明 registry 内容可帮助路由，但必须由 retriever 原生支持 JSON registry 或 Builder 额外提供 Markdown projection，并自动追读 `source_fix_doc`。

## 1.8 原始下一轮优化建议（已被取代）

后续修订：本节最初建议实现 registry JSON reader。经用户复盘，该方向已由 [[02_Projects/codex-capability-registry/knowledge-base-retriever/RetrievalSummary与轻量Ranking优化方案-2026-06-23]] 取代；当前决策是移除 Builder Fix Registry 实现，先增强原始记录 Retrieval Summary，再做 retriever 轻量 ranking。

以下为本评测记录最初给出的优先级，仅保留为决策演变证据：

1. 在 retriever 中增加授权范围内的 Fix Registry JSON reader，仅读取显式授权的 registry 文件或目录，不扫描全库 cache。
2. Registry 命中后不要把 registry 摘要当事实；应把 `source_fix_doc`、`source_section` 对应 Markdown 原文 section 加入 `source_sections_read`。
3. candidate ranking 应区分 original fix、current 聚合引用和 registry routing hit；registry 可提升原始 fix 文档，而不是作为最终事实候选占据 rank 1。
4. 对 current/overview 的“sources 列表命中”降低排序权重，避免聚合入口压过原始修复记录。
5. 修复 `hit_limit_reached` 与 `section_read_limit` 的噪声问题后，再扩大到 Knowledge-Base 治理、cutepower/runtime 项目和无命中场景。

## 1.9 写回边界

本记录是项目测试证据，不提升为正式知识。

未同步 DMS Tracking current 文档，原因是本轮没有改变 Tracking 的设计、实现、验证或事实源；只读取 DMS Tracking 作为 retriever 评测样本。

本轮同步 `knowledge-base-retriever/项目总览.md`，原因是 retriever 子项目的当前状态和下一步优化焦点已经从“尚未进入项目测试”推进为“已完成首个 DMS Tracking 基线测试，发现 Fix Registry JSON 消费缺口”。
