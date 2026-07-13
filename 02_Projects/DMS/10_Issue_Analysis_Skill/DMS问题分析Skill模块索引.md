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

- 项目状态：阶段二实施中；飞书入口、Jira Parser、Data Loader、Evidence Package Builder 与 A 核确定性日志索引/证据选择层已实现，Agent review、结论合成和 Jira 评论草稿/回写尚未实现。
- 已确认主链路：飞书表格读取 Jira ID 和数据路径 → Jira Parser 与 Data Loader → Evidence Package → R-core Analyser → A-core Analyser → 结论回写 Jira。
- 飞书表格仅作为只读问题入口，不承担分析结果回写。
- Jira Parser 使用本地 Bearer token 做只读采集，已通过真实 Issue 验证；凭据不进入版本控制或知识库。
- Data Loader 已完成只读清单、hash 和候选分类验证，`calmcar_camera_service` 作为 A 核日志候选。
- Evidence Package Builder 已完成输入一致性校验、原子构建、阶段状态、缺失证据和 artifact hash；已使用真实 Jira/Data 输入与 synthetic 飞书候选完成集成验证，在线飞书端到端验证仍待完成。
- 当前没有 R 核分析方案，R 核阶段固定标记为 `skipped` 后直接进入 A 核；最终结论必须披露 R 核未执行及覆盖缺口，不得确认 R 核或跨核根因。
- A 核分析已实现全部候选日志的物理行索引、签名 census、错误/初始化/低频签名召回、问题时间 seed、跨线程 correlation 扩展、字符预算和原始位置追溯；输出初始状态为 `partial/pending_agent_review`。
- A 核查询规则固定在 Skill reference 中并通过修改 Skill 手工更新；普通问题分析不读取 DMS 源码、不自动生成 reference、不把单次 case 临时关键词静默固化。
- 新增 A 核测试与既有仓库测试共 36 项通过；尚未使用真实现场日志完成端到端运行和独立 Agent review，因此当前 A 核结论仍只覆盖确定性准备层和 A 核可观察范围。

## 维护规则

- 实现、验证或接口发生变化时，先更新项目方案或新增对应记录，再同步本索引。
- 在完成独立 recoverability verification 前，不建立 `single_pass_recoverable: true` 的 current 状态。
- Jira、日志格式和飞书表格检索策略确定后，记录具体字段与版本，避免将临时约定写成稳定事实。
- A 核规则升级必须显式修改 strategy/reference、提升规则版本并运行回归测试；不得在单次问题分析中自动学习或写回固定规则。
