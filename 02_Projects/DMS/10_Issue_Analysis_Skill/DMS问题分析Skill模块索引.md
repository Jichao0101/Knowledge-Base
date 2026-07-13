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

- 项目状态：阶段一实施中；飞书入口、Jira Parser 与 Data Loader 已实现，Evidence Package 和后续分析/回写阶段尚未实现。
- 已确认主链路：飞书表格读取 Jira ID 和数据路径 → Jira Parser 与 Data Loader → Evidence Package → R-core Analyser → A-core Analyser → 结论回写 Jira。
- 飞书表格仅作为只读问题入口，不承担分析结果回写。
- Jira Parser 使用本地 Bearer token 做只读采集，已通过真实 Issue 验证；凭据不进入版本控制或知识库。
- Data Loader 已完成只读清单、hash 和候选分类验证，`calmcar_camera_service` 作为 A 核日志候选。
- R 核分析资料尚未补齐；A 核参考资料计划从指定版本代码中总结。

## 维护规则

- 实现、验证或接口发生变化时，先更新项目方案或新增对应记录，再同步本索引。
- 在完成独立 recoverability verification 前，不建立 `single_pass_recoverable: true` 的 current 状态。
- Jira、日志格式和飞书表格检索策略确定后，记录具体字段与版本，避免将临时约定写成稳定事实。
