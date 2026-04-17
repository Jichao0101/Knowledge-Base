---
type: knowledge
status: verified
domain: 工程工作流
topic: Current文档组重写任务模板
sources:
  - "01_Knowledge/Agent Workflow/Plugin-first与Contracts-first治理插件设计模式.md"
  - "01_Knowledge/Agent Workflow/运行时门禁与独立审查边界模式.md"
scope: 适用于下一轮按 hardened current 规则重写某个项目主题的 overview/design/spec/implementation/validation 文档组，并在 writeback 前验证 single-pass recoverability。
risks:
  - 若允许范围未明确，模板中的读取与写回动作可能越权。
  - 若主题本身缺少 design/spec/implementation/validation 事实基础，重写前仍需先补证据。
updated_at: 2026-04-07
---

## 0.1 摘要

本模板用于下一轮项目级 current 文档组重写。执行顺序固定为：先查 current 组缺口，再按新模板重写，再验证 single-pass recoverability，最后独立审查并写回。

## 0.2 任务模板

```text
按 Agent 双侧运行规范执行本次任务。

# 任务名称
重写 <主题名> current 文档组，使其满足 hardened current recoverability 要求

# 技术基准
- [[01_Knowledge/Agent Workflow/Plugin-first与Contracts-first治理插件设计模式]]
- [[01_Knowledge/Agent Workflow/运行时门禁与独立审查边界模式]]
- [[01_Knowledge/Agent Workflow/Current文档组重写任务模板]]

# 主类型
knowledge_task

# 任务修饰属性
- writeback_required
- review_required
- verification_required
- current_series_rewrite_required
- single_pass_recoverability_required

# 允许范围
- 知识库读取：
  - 01_Knowledge/Agent Workflow/**
  - 02_Projects/<Project>/<Topic>/**
- 项目区读写：
  - 02_Projects/<Project>/<Topic>/**
- 代码库修改：
  - 禁止

# 联网策略
禁止

# main_agent_mode
- orchestration

# verification_tier
- V1

# 本轮目标
1. 检查 overview/design/spec/implementation/validation 的粒度缺口。
2. 按 hardened 模板重写 current 文档组。
3. 验证新的 current 组是否 single-pass recoverable。
4. 完成独立审查后正式写回。

# 必查问题
1. overview_current 是否能唯一声明默认入口、恢复顺序、实现输入链、default_recovery_bundle 和真相源集合？
2. design_current 是否能恢复当前设计目标、边界、状态组织、模块耦合、非目标项？
3. spec_current 是否能恢复 object model、required behaviors、core state variables、interface contracts、calculation/type/filter/config/verification contract？
4. implementation_current 是否能恢复代码入口、关键载体、spec-to-code mapping、兼容层和已知不闭合点？
5. validation_current 是否能恢复已有证据、缺失证据、已证明/未证明边界、当前审查结论和下一轮验证？
6. 是否仍有关键事实只存在于 baseline、delta 或代码中？

# 执行阶段
## 第 1 阶段：current 组缺口审计
输出：
- current_role_gap_assessment
- current_complementarity_checks
- single_pass_blockers

## 第 2 阶段：按新模板重写
要求：
- 先重写 overview_current
- 再重写 design_current / spec_current
- 再重写 implementation_current / validation_current
- 不得把 design/spec/implementation/validation 的主体职责混写

## 第 3 阶段：recoverability 验证
至少验证：
- 不依赖 baseline 作为默认入口
- 不依赖两篇及以上 delta 作为当前态补洞
- 不依赖大段代码阅读来恢复关键机制、实现落点和验证边界

## 第 4 阶段：独立审查
检查：
- 是否真正收紧了 current 粒度
- 是否保住了 current_kind 边界
- 是否把关键事实从 baseline/delta/代码上收到了 current
- 是否让 single_pass_recoverable 的判定更严格而不是更松

## 第 5 阶段：正式写回
仅在 review 通过后写回，并更新：
- sync_mode
- current_files_must_update
- history_files_to_mark
- default_entry_verified
- single_pass_recoverable

# 输出要求
必须输出：
- roles_invoked
- state_transitions
- rework_rounds
- overall_decision
- files_read
- files_written
- current_role_gap_assessment
- current_complementarity_checks
- single_pass_blockers
- verification_results
- review_conclusion
- writeback_targets
- risks_or_uncertainties
```

## 0.3 使用说明

- 本模板默认只重写项目 current 文档组，不默认改 baseline、delta 正文。
- 若现有 current_kind 体系无法容纳主题事实，应停止并确认，而不是擅自新增新的 current_kind。
- 若验证后仍需依赖 baseline、两篇及以上 delta 或大段代码阅读，则不得写 `single_pass_recoverable: true`。
