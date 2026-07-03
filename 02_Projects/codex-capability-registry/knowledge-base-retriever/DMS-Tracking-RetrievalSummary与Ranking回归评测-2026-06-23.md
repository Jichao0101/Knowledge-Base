---
type: evaluation_record
status: completed
project: Knowledge-Base
module: knowledge-base-retriever
summary: 复跑 DMS Tracking 三个既有检索基准，并新增三条 Tracking 记录作为防过拟合样本，验证 Retrieval Summary 与可解释 priority-tier ranking 的效果。
sources:
  - 02_Projects/codex-capability-registry/knowledge-base-retriever/DMS-Tracking检索与FixRegistry联动评测-2026-06-23.md
  - 02_Projects/codex-capability-registry/knowledge-base-retriever/RetrievalSummary与轻量Ranking优化方案-2026-06-23.md
  - reports/kb/retrieval-eval/2026-06-23-dms-tracking-summary-ranking/metrics_summary.json
  - reports/kb/retrieval-summary-proposals/retrieval-summary-proposals-20260623T170916414913.json
scope: DMS Tracking 授权路径内的 retriever 回归评测；不评价 DMS Tracking 业务修复本身。
risks:
  - reports/kb 与 .kb_cache 均为派生产物，不替代 Markdown 原文、current 文档或项目记录。
  - 本轮仍使用 agent-authored query plan；query planning 质量仍会影响召回结果。
  - 仍存在 `hit_limit_reached` 与 `section_read_limit`，说明噪声和 section quota 压力未完全消除。
updated_at: 2026-06-23
---

# 1 DMS Tracking Retrieval Summary 与 Ranking 回归评测

## 1.1 评测目标

本轮用于验证 `knowledge-base-retriever` 优化后的两个效果：

1. 原始 DMS Tracking 三个基准在加入 Retrieval Summary 和可解释 priority-tier ranking 后，Recall@10 不下降，并观察原始 fix 文档排名是否改善。
2. 额外选取三条 Tracking 记录做防过拟合测试，确认优化不只适配原三例。

本轮不修改 DMS Tracking current 文档，不改变 Tracking 事实源或验证状态。

## 1.2 授权范围与输入

- 知识库根目录：`/mnt/d/Knowledge-Base`
- 检索授权范围：`02_Projects/DMS/04_Tracking`
- 写回记录路径：`02_Projects/codex-capability-registry/knowledge-base-retriever`
- 派生评测包：`reports/kb/retrieval-eval/2026-06-23-dms-tracking-summary-ranking/`
- metrics summary hash：`6e46fd6b4beb78603fe05ea5ce94f03254765a3a04b1b9b04eaf10cd2f9935f0`
- Builder Retrieval Summary proposal report：`reports/kb/retrieval-summary-proposals/retrieval-summary-proposals-20260623T170916414913.json`
- Builder proposal count：0
- 手工最小写入校验：`reports/kb/minimal-apply-check/minimal-apply-check-20260623T171509927741.json`

Builder proposal count 为 0，表示当前规则下本轮授权范围内未自动生成 Retrieval Summary proposal。回归初跑发现 hand continuity 目标仍为 rank 11 后，已对 `多目标跟踪手部连续性优化闭环记录-2026-03-31.md` 执行 `minimal-apply-check`，并只追加由原文支撑的 Retrieval Summary。

## 1.3 原三例对比结果

| 场景 | 旧 rank | 新 rank | Recall@5 | Recall@10 | 观察 |
|---|---:|---:|---:|---:|---|
| 2m 后排 head/face 误绑定主驾 | 5, 3 | 2, 1 | 1.0 | 1.0 | 两条目标均命中 P1 `original_record_retrieval_summary`，current/overview 不再压过原始修复记录。 |
| 跟踪框越界 coredump | 1 | 1 | 1.0 | 1.0 | 目标仍为 rank 1，排序解释从原始记录 Retrieval Summary 给出。 |
| 手部连续性与快速运动恢复 | 11, 5 | 2, 1 | 1.0 | 1.0 | 补 hand continuity Retrieval Summary 后，两条目标均进入 top2。 |

结论：原三例 Recall@10 未下降；2m、hand continuity 与快速运动场景的原始修复文档排名均明显改善。

## 1.4 防过拟合三例

| 场景 | 目标文档 rank | Recall@5 | Recall@10 | 观察 |
|---|---:|---:|---:|---|
| 主驾打哈欠误报 | 1 | 1.0 | 1.0 | 目标命中 P1 Retrieval Summary。 |
| 后排乘客头部误跟踪为副驾驶 | 1 | 1.0 | 1.0 | 目标命中 P1 Retrieval Summary，同时能容忍后排误跟踪相关相邻记录进入 top5。 |
| head-first 优先于 body-first 主线决策 | 1 | 1.0 | 1.0 | decision 记录也能通过 P1 排到 current 文档之前。 |

结论：新增三例均 rank 1，说明 priority-tier ranking 对 fix 与 decision 记录均有效，不只服务原三例。

## 1.5 仍未闭合的问题

- 初跑时 `多目标跟踪手部连续性优化闭环记录-2026-03-31.md` 在 hand/快速运动混合查询中为 rank 11，且优先级为 P5 `metadata_source_or_aggregate_only`；补 Retrieval Summary 后已提升到 rank 2。
- 所有场景仍有 `hit_limit_reached:120` 和 `section_read_limit:30` limitation，说明噪声和 section quota 压力仍存在。

## 1.6 结论

Retrieval Summary 与可解释 priority-tier ranking 已验证能改善 DMS Tracking 多数历史修复/决策记录的入口排名，并保持原基准 Recall@10 不下降。当前不需要回到 Fix Registry 方案。

下一步应继续处理噪声与 quota 压力：优先收紧 query plan 的宽泛 structure/code terms，并观察是否能降低 `hit_limit_reached` 与 `section_read_limit`，而不是扩大为 registry 或向量检索方案。
