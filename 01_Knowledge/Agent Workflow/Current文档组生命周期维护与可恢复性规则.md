---
type: knowledge
status: verified
domain: 工程工作流
topic: Current文档组生命周期维护与可恢复性规则
sources:
  - "Knowledge-Base current 文档组维护实践"
  - "commit 01acb13b94861331c4af0e2c6f9ff2ff773bf14e 后的三侧同步规范删除结果"
scope: 适用于项目区 current 文档组的 creation、hardening/refactor、patch 和 rewrite 全生命周期维护，并在 writeback 前验证 recoverability。
risks:
  - 若没有先识别生命周期场景，agent 容易把 creation、hardening 或 patch 都误执行为整组 full rewrite。
  - 若把历史三侧同步规范当作 active dependency，会重新引入已删除的运行治理真相源。
  - 若证据不足时伪造完整 current 或标记 single_pass_recoverable: true，会制造虚假的恢复闭环。
updated_at: 2026-04-29
---

## 0.1 摘要

current 文档组维护是 lifecycle maintenance，不只是已有 current 的增量 patch。  
默认先识别场景，再选择最小足够动作：

1. current creation：没有 current 文档时，新建可恢复的 current 组合。
2. current hardening/refactor：已有零散文档、旧 current、baseline/delta 混杂时，重构为 hardened current 组合。
3. current patch：已有合格 current 时，做最小增量更新。
4. current rewrite：仅在 `structural_unrecoverable` 证据触发时升级。

任何场景都不得恢复或依赖已删除的三侧同步规范。运行治理、route、review 独立性和 writeback 分层由当前 workflow plugin 或 contracts 承担，不由本 Knowledge 文档重新定义。

## 0.2 职责边界

### 0.2.1 AGENTS.md

`AGENTS.md` 只承担 thin bridge：

- 声明 current 维护入口指向本生命周期规则。
- 声明 hard stop。
- 不复制完整生命周期流程、review 规则或 writeback 规则。

### 0.2.2 Knowledge 文档

`01_Knowledge/*/` 只存正式可复用规则，例如本 lifecycle 规则。  
具体执行记录、迁移记录、审查记录不得继续堆在该目录根下。

### 0.2.3 Records 目录

current 维护的具体记录应放在：

- `02_Projects/*/Current Maintenance Records/`

适合放入 records 的内容包括：

- 某个主题 current creation 的执行记录。
- 某组旧 current hardening/refactor 的迁移记录。
- recoverability review 记录。
- rewrite escalation 证据包。
- writeback decision 记录。

正式可复用规则沉淀前，应先从 records 中抽象，满足来源明确、适用范围明确、风险明确后，再进入 `01_Knowledge/Agent Workflow/`。

## 0.3 Current 组合默认恢复职责

### 0.3.1 overview_current

负责恢复：

- 当前状态。
- 默认入口。
- 主题范围和非范围。
- 默认读取顺序。
- 主真相源集合。
- 其他 current 文件的角色索引。
- 当前 recoverability 状态。

### 0.3.2 design_current

负责恢复：

- 设计目标。
- 非目标。
- 系统边界。
- 关键取舍。
- 模块关系和状态组织。
- 已知设计风险。

### 0.3.3 spec_current

负责恢复：

- 对象模型。
- 状态变量。
- required behaviors。
- 接口契约。
- 配置、类型、过滤或计算约束。
- verification contract。

### 0.3.4 implementation_current

负责恢复：

- 文件路径。
- 代码入口。
- 配置入口。
- 关键载体。
- spec-to-code mapping。
- 兼容层和已知不闭合点。

### 0.3.5 validation_current

负责恢复：

- 已验证事实。
- 验证命令。
- 证据路径。
- 未验证项。
- 风险。
- 下一步检查路径。

## 0.4 通用入口流程

任何 current 生命周期维护都先执行：

1. source inventory
2. lifecycle classification
3. evidence assessment
4. action selection
5. recoverability verification
6. review/writeback decision

### 0.4.1 source inventory

列出本轮允许范围内的材料：

- 现有 current 文件。
- baseline / delta / 修改记录。
- 相关设计、实现、验证记录。
- 必要时的代码或配置证据路径。
- 已知 `sync_mode`、`single_pass_recoverable` 或等价状态。

不得在未完成 inventory 前开始 full rewrite。

### 0.4.2 lifecycle classification

将任务归入一个主场景：

- `creation`
- `hardening_refactor`
- `patch`
- `rewrite`

若证据不足以分类，应先补证据或记录 `blocked_by_evidence_gap`，不得伪造完整 current。

## 0.5 Current Creation

适用条件：

- 主题没有 current 文档组。
- 允许范围内已有足够来源材料，可支撑当前状态、设计、规格、实现和验证边界。
- 新建 current 的目的，是建立默认恢复入口，而不是复制 baseline 或 delta 全文。

创建时应优先形成最小完整组合：

- `overview_current`
- `design_current`
- `spec_current`
- `implementation_current`
- `validation_current`

若某一类证据不足，可以创建对应 current，但必须明确：

- `status: draft` 或等价未完成状态。
- 缺失证据。
- 不可验证断言。
- 下一步补证路径。

证据不足时禁止：

- 伪造完整 current。
- 把推测写成事实。
- 写入 `single_pass_recoverable: true`。
- 声称 current 已可替代 baseline / delta。

creation 后的最低输出：

- `created_current_files`
- `source_inventory`
- `evidence_gaps`
- `recoverability_result`
- `records_target`

## 0.6 Current Hardening / Refactor

适用条件：

- 已有零散文档、旧 current、baseline/delta 混杂。
- 当前入口、恢复顺序或职责分工不清。
- 大部分事实仍可从现有材料中归并，不需要直接 full rewrite 全部内容。

hardening/refactor 的目标是把材料收敛为 hardened current 组合：

- 把当前状态和读取顺序收敛到 `overview_current`。
- 把设计取舍收敛到 `design_current`。
- 把行为和接口约束收敛到 `spec_current`。
- 把代码路径和 mapping 收敛到 `implementation_current`。
- 把证据和风险收敛到 `validation_current`。

处理旧文档时：

- baseline / delta 可作为来源，不作为默认入口。
- 旧 current 可 patch、拆分、降级或标记 superseded。
- 迁移过程写入 records 目录，不写入正式 Knowledge 根目录。
- 不借 hardening 恢复三侧同步规范。

hardening/refactor 后必须输出：

- `refactored_current_files`
- `superseded_or_retained_sources`
- `mapping_from_old_docs`
- `evidence_gaps`
- `recoverability_result`
- `records_target`

## 0.7 Current Patch

适用条件：

- current 文档组已经存在。
- 默认入口和主要职责分工仍清楚。
- 缺口可以定位到有限文件、有限章节或有限字段。
- 现有 current 组织仍足以表达主题事实。

patch 默认流程：

1. current inventory
2. gap classification
3. minimal patch
4. recoverability verification
5. review/writeback decision

gap classification 至少区分：

- `local_gap`：单个 current 文件缺少局部事实、引用、边界或证据。
- `cross_file_gap`：多个 current 文件之间存在事实冲突、职责错位或恢复顺序断裂。
- `evidence_gap`：current 文件声称的事实缺少项目记录、验证结果或代码证据支撑。
- `structural_unrecoverable`：现有 current 组织无法恢复当前系统状态，且局部补丁会继续制造冲突或误导。

patch 要求：

- `local_gap` 优先 patch 单文件。
- `cross_file_gap` 优先 patch 直接冲突的文件和索引/入口声明。
- `evidence_gap` 优先补证据引用、降低断言强度或标记 unresolved。
- 不为统一风格、章节重排或“看起来更完整”执行整组重写。
- patch 后仍必须保留各 current 文件的恢复职责边界。

## 0.8 Current Rewrite

full rewrite 不是默认维护路径。  
只有出现 `structural_unrecoverable` 证据时，才允许把 rewrite 作为升级路径。

可接受证据包括：

- 默认入口缺失或错误，导致 reader 无法判断应从哪个 current 文件恢复当前态。
- 多数 current 文件的职责边界失效，局部 patch 会继续造成跨文件矛盾。
- current 组合无法表达当前主题事实，且需要重新设计文档组结构。
- 关键机制、实现落点和验证边界分散在 baseline、多篇 delta 或代码中，无法通过 creation/hardening/patch 收敛。
- 现有 current 大量承载已失效事实，且无法可靠区分可保留内容与应删除内容。

rewrite 前必须输出：

- `rewrite_escalation_reason`
- `structural_unrecoverable_evidence`
- `why_creation_hardening_or_patch_is_insufficient`
- `expected_rewrite_scope`
- `review_required_before_writeback`
- `records_target`

没有上述证据时，不得把 “hardened current” 解释为整组重写。

## 0.9 single_pass_recoverable 判定

只有同时满足以下条件，才允许写入或保留 `single_pass_recoverable: true`：

- `overview_current` 明确默认入口、范围、默认读取顺序和主真相源集合。
- `design_current` 能恢复设计目标、非目标、边界和关键取舍。
- `spec_current` 能恢复对象模型、状态变量、行为约束和接口契约。
- `implementation_current` 能恢复文件路径、代码入口、配置入口和 spec-to-code mapping。
- `validation_current` 能恢复已验证事实、验证命令、未验证项、风险和下一步检查路径。
- 不需要默认读取 baseline 才能理解当前目标、设计或实现。
- 不需要读取两篇及以上 delta / 修改记录才能补齐当前态。
- 不需要大段代码阅读才能定位关键机制、实现落点或验证边界。
- 本轮已完成整组 recoverability verification，且没有未解决的 cross-file contradiction。

出现任一情况时，禁止写入或保留 `single_pass_recoverable: true`：

- 证据不足，只能创建 draft current。
- 本轮只是局部 patch，尚未验证整组 recoverability。
- validation_current 没有列明已验证、未验证和证据缺口。
- spec/design/implementation 之间存在未解决的行为、接口、状态或证据冲突。
- 仍需依赖 baseline、delta 或代码阅读作为默认恢复路径。

若只能证明“局部缺口已修复”，应写：

- `single_pass_recoverable: false`
- 或保留原状态并增加 `recoverability_unverified`
- 或在 review/writeback decision 中明确暂不更新该字段

## 0.10 Recoverability Verification

验证结论必须区分：

- `recoverable`
- `created_but_not_fully_verified`
- `hardened_but_evidence_gap_remains`
- `locally_patched_but_not_fully_verified`
- `blocked_by_evidence_gap`
- `structural_unrecoverable`

最低检查项：

- 是否能从 `overview_current` 找到默认入口、范围、默认读取顺序和主真相源集合。
- 是否能从 `design_current` 恢复设计目标、非目标、边界和关键取舍。
- 是否能从 `spec_current` 恢复对象模型、状态变量、行为约束和接口契约。
- 是否能从 `implementation_current` 恢复文件路径、代码入口、配置入口和 spec-to-code mapping。
- 是否能从 `validation_current` 恢复已验证事实、验证命令、未验证项、风险和下一步检查路径。
- 是否仍需要 baseline、多篇 delta 或大段代码阅读补洞。
- 是否误把历史三侧同步规范当作 active dependency。

## 0.11 避免恢复三侧同步规范

以下做法禁止：

- 引用已删除的三侧同步规范作为 active dependency。
- 使用“按 Agent 三侧/双侧运行规范执行”作为任务入口。
- 把知识库、代码库、板端侧的旧协同闭环规则复制回 AGENTS、Knowledge 或项目 current 文档。
- 用旧规范中的角色链、调度链或 writeback 语义替代当前 workflow plugin / contracts。

允许保留的只有历史说明：

- 在历史记录或来源说明中提到这些规范曾存在。
- 在 migration note 中说明相关规范已删除且不再作为 active dependency。
- 在风险项中提醒不得恢复旧规范。

## 0.12 任务模板

```text
# 任务名称
维护 <主题名> current 文档组，并验证 recoverability

# 技术基准
- [[01_Knowledge/Agent Workflow/Current文档组生命周期维护与可恢复性规则]]

# 默认策略
- lifecycle_classification_first
- creation_when_no_current_exists
- hardening_refactor_when_sources_are_mixed
- patch_first_when_current_is_already_qualified
- full_rewrite_requires_structural_unrecoverable_evidence
- no_legacy_three_side_sync_dependency
- records_to_02_projects_agent_workflow_current_maintenance_records

# 允许范围
- 知识库读取：
  - 01_Knowledge/Agent Workflow/Current文档组生命周期维护与可恢复性规则.md
  - 02_Projects/<Project>/<Topic>/**
- 项目区读写：
  - 02_Projects/<Project>/<Topic>/**
  - 02_Projects/Agent Workflow/Current Maintenance Records/**
- 代码库修改：
  - 禁止，除非任务另行授权
- 联网策略：
  - 禁止，除非任务另行授权

# 本轮目标
1. 完成 source inventory。
2. 判定 lifecycle scenario：creation / hardening_refactor / patch / rewrite。
3. 评估证据是否足以支撑 current 内容。
4. 执行最小足够维护动作。
5. 验证 recoverability。
6. 输出 review/writeback decision。

# 必须输出
- files_read
- files_written
- lifecycle_classification
- source_inventory
- evidence_assessment
- action_summary
- recoverability_verification
- single_pass_recoverable_decision
- rewrite_escalation_reason（仅 rewrite 适用）
- records_target
- review_writeback_decision
- risks_or_uncertainties
```
