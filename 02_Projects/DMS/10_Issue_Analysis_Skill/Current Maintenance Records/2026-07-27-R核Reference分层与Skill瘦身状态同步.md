---
type: project_maintenance_record
status: completed_with_gaps
project: DMS
module: Issue Analysis Skill
scope: 将 R 核项目排查流程分层为 Skill reference/strategy，瘦身 SKILL.md，并同步尚未解除的 analyser 与运行验证缺口。
sources:
  - 02_Projects/DMS/10_Issue_Analysis_Skill/DMS R核问题分析流程.md
  - /mnt/d/analyze-dms-issue/references/r-core-analysis.md
  - /mnt/d/analyze-dms-issue/references/r-core-analysis-strategy.json
  - /mnt/d/analyze-dms-issue/SKILL.md
created_at: 2026-07-27
updated_at: 2026-07-27
---

# R 核 Reference 分层与 Skill 瘦身状态同步

## 1. 本轮结论

- R 核疲劳、分心、抽烟和接打电话排查流程已从项目来源文档转换为 Skill 内的解释性 `r-core-analysis.md` 与机器可消费 `r-core-analysis-strategy.json`。
- `SKILL.md` 已从阶段细节说明收敛为主流程、运行门禁和 reference 路由，避免 A/R 核规则在主文件中重复维护。
- 当前能力状态为 `reference_ready/analyser_not_implemented`。R 核 analyser、输入适配、证据 ID 和原子输出合同尚未实现，因此运行阶段继续为 `skipped/r_core_analyser_not_available`。

## 2. 规则分层

- `r-core-analysis.md` 保存输入边界、统一排查顺序、功能规则、证据等级和不能得出的结论。
- `r-core-analysis-strategy.json` 保存工作状态、速度、灵敏度、冷却期、inhibit、报警枚举、优先级、持续时间和候选分类规则。
- strategy 记录项目来源文档 SHA-256 `228a09cea3cdfa44cef06083dc2e18e2b9773d7d1500eb9df9e57b9c56b567f3`，用于确认本轮转换对应的输入快照；Skill 运行时不依赖知识库路径。
- 普通灵敏度哈欠、`isMonitoringEnabled` 门禁关系、抽烟持续时间和灵敏度条件在来源中没有完整规则，分别保留为 `not_documented`、`decision_relation_not_documented` 或 `rule_incomplete`，未使用相邻功能规则补写。

## 3. Skill 瘦身

- `SKILL.md` 保留责任人/Jira ID 筛选、Evidence Package、一致性 fail-closed、R 核跳过、A 核 review、结论合成和 Jira 新增评论的主链路。
- 具体字段、阈值、证据契约和写回策略均通过一层 `references/` 路由按需加载。
- 飞书只读、源数据只读、Jira 仅新增评论、普通 case 不自动学习固定规则等既有行为边界保持不变。

## 4. 验证

- Skill quick validation：通过。
- `r-core-analysis-strategy.json` JSON 解析：通过。
- 12 个 `SKILL.md` reference 路径存在性检查：通过。
- 项目来源文档 SHA-256 与 strategy 中 `source_snapshot.sha256` 一致。
- `git diff --check`：通过。
- `python3 -m unittest discover -s scripts -p 'test_*.py'`：55 项通过。
- 知识库授权范围 lint 未命中本轮新增或修改文件；全库入口检查仍报告一个既有问题：结构审计声明的 `02_Projects/Knowledge-Base/知识库结构审计-2026-06-05.md` supersession 目标不存在，本轮未扩大范围修复。

## 5. 当前边界与下一步

- reference 完成不等于 R 核分析已执行，不生成或暗示存在 `r_core_result.json`。
- 解除 `skipped` 前需实现确定性 analyser、MF4/信号输入适配、持续时间证据、输出 schema、证据 ID、原子输出和回归测试。
- 结论策略仍禁止仅凭 A 核证据确认 `R_CORE` 或 `CROSS_CORE_INTERFACE`；R 核缺失期间的置信度边界保持不变。
- 模块仍以项目方案和模块索引作为当前入口，未建立 current 五文件组，未完成独立 recoverability verification，也未声明 `single_pass_recoverable: true`。

## Retrieval Summary

R 核规则已完成 Skill reference/strategy 分层并通过 55 项仓库测试，但 analyser 和结果合同尚未实现；因此当前改动改善了规则可维护性与可发现性，没有解除 `skipped/r_core_analyser_not_available` 或扩大可确认的根因范围。

## Retrieval Anchors

- `r-core-analysis.md`
- `r-core-analysis-strategy.json`
- `reference_ready`
- `analyser_not_implemented`
- `r_core_analyser_not_available`
- `rule_incomplete`
- `55 tests`
