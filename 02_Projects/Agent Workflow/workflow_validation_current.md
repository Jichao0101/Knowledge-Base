---
title: Agent Workflow Validation Current
summary: Agent Workflow 项目化管理当前已验证与未验证边界，记录规范侧规则和 Chaospower P0 插件化落地是否已在项目实例中验证。
status: verified
doc_role: current
truth_role: current
current_kind: validation
lifecycle_state: active
default_entry: false
sync_required_when:
  - modification-record 规则落地情况变化
  - DMS Tracking 诊断结果变化
retrieval_priority: current
supersedes: []
merged_into: []
current_replacement: []
related_code: []
related_plugins:
  - plugins/chaospower
sources:
  - 02_Projects/Agent Workflow/Agent Workflow-current与修改记录分工收敛记录-2026-04-13.md
  - 02_Projects/Agent Workflow/Agent Workflow-DMS Tracking 文档体系诊断记录-2026-04-13.md
  - 02_Projects/DMS/04_Tracking/tracking_overview_current.md
  - 02_Projects/DMS/04_Tracking/tracking_validation_current.md
  - 02_Projects/Agent Workflow/Chaospower P0 skill-first 第一阶段落地收敛记录-2026-04-15.md
scope: 适用于判断 Agent Workflow 的 current + modification-record 规则是否已被当前项目实例吸收。
risks:
  - Chaospower P0 当前只完成静态结构校验，尚未在真实代码变更任务中完整跑通。
updated_at: 2026-04-15
---

## 0.1 Validated

- 现有规范已足够支撑 current 组与 single-pass recoverability
- DMS Tracking 已成功建立 overview/design/spec/implementation/validation current 组
- 本轮已补充 modification-record 规则与模板
- 主代理越权执行规范硬化记录已完成独立 review，复审结论为 `pass`
- 默认 deny、核心门禁状态、writeback 分层和违规冻结机制已写入正式规范
- `plugins/chaospower` 已建立 P0 最小 skill-first 结构
- `plugin.json` 已通过 JSON 解析
- P0 skill frontmatter 已完成轻量静态检查
- `skills/` 下未误建 P1/P2 skill 目录

## 0.2 Not Yet Closed

- modification-record 模板尚未批量推广到旧项目
- 仍需进一步清理 DMS Tracking 中 active delta、伪 current 命名与 metadata 漏项
- 工具层 runtime enforcement 尚未验证，目前仍依赖角色自检、audit_log 与 writeback 冻结机制
- 小任务 review 降级例外尚未形成 verified 规则
- `plugins/chaospower` 尚未加入 `.agents/plugins/marketplace.json`
- `skill-creator` 的 `quick_validate.py` 因本地缺少 `yaml` 模块未能运行，只完成替代静态校验
- P1/P2 能力尚未落地：source ingest、board run、incident triage、functional review、knowledge promotion review

## 0.3 Next Verification

- 对至少一个非 Tracking 主题再执行一次 current + modification-record 收敛
- 检查旧 delta 是否都能映射到新的 record_type
- 用后续代码修改类任务验证 `workflow-orchestrator` 是否能被高风险动作默认 deny 约束阻断
- 用一次真实 scoped repo change 验证 Chaospower P0 链路：`using-chaospower -> scope-plan -> repo-change -> code-review -> writeback`
- 校验 marketplace 注册后插件发现和 skill 触发是否符合预期
