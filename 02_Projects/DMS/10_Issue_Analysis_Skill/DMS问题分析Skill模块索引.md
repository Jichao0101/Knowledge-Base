---
type: project_module_index
status: active
project: DMS
module: Issue Analysis Skill
scope: DMS 问题分析 Skill 的方案、实现、验证和维护记录入口。
updated_at: 2026-07-13
---

# DMS 问题分析 Skill 模块索引

## 当前入口

- [[02_Projects/DMS/10_Issue_Analysis_Skill/DMS问题分析Skill项目方案]]：当前初版架构、阶段契约、降级策略、Jira 回写边界和实施建议。

## 当前状态

- 项目状态：阶段一实施中；飞书入口、Jira Parser、Data Loader 与 Evidence Package Builder 已实现，Jira 评论草稿和后续分析/回写阶段尚未实现。
- 已确认主链路：飞书表格读取 Jira ID 和数据路径 → Jira Parser 与 Data Loader → Evidence Package → R-core Analyser → A-core Analyser → 结论回写 Jira。
- 飞书表格仅作为只读问题入口，不承担分析结果回写。
- Jira Parser 使用本地 Bearer token 做只读采集，已通过真实 Issue 验证；凭据不进入版本控制或知识库。
- Data Loader 已完成只读清单、hash 和候选分类验证，`calmcar_camera_service` 作为 A 核日志候选。
- Evidence Package Builder 已完成输入一致性校验、原子构建、阶段状态、缺失证据和 artifact hash；已使用真实 Jira/Data 输入与 synthetic 飞书候选完成集成验证，在线飞书端到端验证仍待完成。
- 当前没有 R 核分析方案，R 核阶段固定标记为 `skipped` 后直接进入 A 核；最终结论必须披露 R 核未执行及覆盖缺口，不得确认 R 核或跨核根因。
- A 核参考资料计划从指定版本代码中总结，当前 A 核结论只覆盖 A 核可观察范围。

## 维护规则

- 实现、验证或接口发生变化时，先更新项目方案或新增对应记录，再同步本索引。
- 在完成独立 recoverability verification 前，不建立 `single_pass_recoverable: true` 的 current 状态。
- Jira、日志格式和飞书表格检索策略确定后，记录具体字段与版本，避免将临时约定写成稳定事实。
