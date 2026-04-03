---
type: knowledge
status: verified
domain: 工程工作流
topic: Agent双侧运行规范与调度模板
sources: ["内部方法论整理", "01_Knowledge/Agent Workflow/Agent驱动知识库与代码库协同闭环规范.md", "01_Knowledge/Agent Workflow/Agent双侧模板与文件结构规范.md"]
scope: 适用于需要将双侧闭环规则包装成可运行流程，包括任务入口、状态推进、调度 prompt、角色输入输出契约与回写要求的场景。
risks: ["运行规范过重导致单次任务负担过大", "项目特例被误提升为通用步骤", "角色契约与实际执行工具不一致", "扩展角色加入后模板不同步导致制度与运行脱节"]
updated_at: 2026-04-02
---

## 0.1 摘要

本文档定义双侧闭环的运行层，回答“系统怎么跑起来”。  
它承接任务入口、状态门禁、角色调度、返工升级、日志记录和 prompt 模板。

---

## 0.2 方案评价

三层文档的分工如下：

- 上位规范：制度、边界、门槛
- 运行规范：状态机、调度、返工、模板
- 文件结构规范：文件树、骨架、字段

---

## 0.3 任务入口

每个任务在进入系统时，至少要明确以下输入对象：

- `task_goal`：本轮目标
- `primary_type`：主类型
- `task_modifiers`：修饰属性集合
- `allowed_paths`：允许读取与写入的目录
- `repo_scope`：代码库允许修改范围
- `confirmation_policy`：哪些步骤需要确认
- `output_contract`：需要交付哪些结果
- `verification_tier`：本轮要求的验证等级

### 0.3.1 标准任务表达

正式入口统一使用“主类型 + 修饰属性”：

- `primary_type`: `implementation / bug_fix / audit / optimization / knowledge_task`
- `task_modifiers`: `requires_web / read_only / code_change_allowed / writeback_required / review_required / promotion_review / functional_scope / failure_investigation`

常见组合：

- 背景检索：`knowledge_task` + `read_only`
- 联网研究：`knowledge_task` + `requires_web` + `read_only`
- 项目实现：`implementation` + `code_change_allowed` + `review_required`
- 缺陷修复：`bug_fix` + `code_change_allowed` + `review_required`
- 受控优化：`optimization` + `code_change_allowed` + `review_required`
- 功能审核：`audit` + `functional_scope` + `read_only`
- 知识提升：`knowledge_task` + `promotion_review` + `writeback_required`

### 0.3.2 进入条件

任务启动前必须满足：

- 已给出目标
- 已给出知识库允许访问范围
- 若涉及代码修改，已给出代码库修改范围
- 若允许联网，已明确联网权限
- 已给出或可推导 `verification_tier`

若上述条件缺失，应先补全条件，而不是直接执行。

---

## 0.4 运行状态机

标准状态推进如下：

1. `task_received`
2. `scope_confirmed`
3. `context_retrieved`
4. `plan_ready`
5. `execution_approved`
6. `implementation_done`
7. `knowledge_sync_checked`
8. `review_done`
9. `convergence_ready`
10. `rework_needed`（条件态）
11. `writeback_done`
12. `closed`

### 0.4.1 状态说明

#### 0.4.1.1 `task_received`

接收任务目标，判断是否信息不足。

#### 0.4.1.2 `scope_confirmed`

确认知识侧与代码侧允许范围。

#### 0.4.1.3 `context_retrieved`

完成项目区、正式知识区、来源区的受控检索。

#### 0.4.1.4 `plan_ready`

输出实施计划、验证计划、回写路径和不确定项。

进入条件：

- 已有 `primary_type`
- 已有 `task_modifiers`
- 已有 `allowed_paths`
- 若涉及代码，已有 `repo_scope`
- 已有 `implementation_plan`
- 已有 `verification_plan`
- 已有 `non_goals`
- 已有 `open_uncertainties`
- 已有 `verification_tier`

阻断条件：

- 允许范围不清
- 任务语义混杂
- 非目标项缺失
- 验证集合未区分 `required / optional / unavailable`

#### 0.4.1.5 `execution_approved`

若任务要求确认，则在此节点停下；若无需确认，可继续执行。

#### 0.4.1.6 `implementation_done`

代码修改、知识整理或外部信息采集已完成。

进入条件：

- 已记录 `files_changed` 或明确无代码改动
- 已记录 `commands_run`
- 已记录 `verification_results`
- 已记录 `decision_deltas`
- 已记录 `open_risks`
- 如存在，已记录 `optional_optimizations`

阻断条件：

- 验证结果缺失
- 实施偏差未记录
- 风险未展开
- 变更已触发 `scope_creep_trigger`

#### 0.4.1.7 `knowledge_sync_checked`

完成 `knowledge_sync_check`，并输出强制同步决议，确认本轮变化是否要求同步更新 `current / delta / adr / 状态头 / default_entry`。

进入条件：

- 已评估设计、实现、接口、约束或状态机是否发生变化
- 已输出 `sync_mode: current_rewrite | current_patch | delta_only | adr_only`
- 已输出 `current_files_must_update`
- 已输出 `history_files_to_mark`
- 若 `sync_mode = delta_only`，已输出 `why_delta_only_allowed`

阻断条件：

- 变化已触发文档失配但未给出同步决策
- 明显只追加 delta 而未判断 current 是否过期
- 使用 `delta_only` 但未给出举证
- 需要更新的 current 未列入同步决议

#### 0.4.1.8 `review_done`

完成独立审查，确认是否存在越界、缺少验证或风险未闭环。

进入条件：

- 已记录 `findings`
- 已记录 `finding_severity`
- 已记录 `scope_assessment`
- 已记录 `regression_risks`
- 已记录 `review_conclusion`
- 已记录 `next_action`
- 已记录 `fix_owner`

阻断条件：

- 关键验证缺失
- 审查输入未裁剪
- reviewer 独立性破坏
- 只有结论没有证据

#### 0.4.1.9 `convergence_ready`

确认 writeback 后当前态可被单次恢复，历史文档不会继续与 current 竞争主入口。

进入条件：

- 已确认 current 是否足以恢复当前主要设计
- 已确认历史文档完成最小状态标记
- 已确认默认检索顺序不会优先命中 superseded baseline
- 已确认 `default_entry` 与 `retrieval_priority` 已校验
- 已确认 `single_pass_recoverable = true`

阻断条件：

- 仍需依赖 baseline + 多篇 delta 才能恢复当前态
- 历史文档未做最小状态映射
- current 缺少关键主题
- 仍存在应降级但未降级的 baseline / delta
- default entry 仍指向 baseline 或 delta

#### 0.4.1.10 `rework_needed`

reviewer 已给出需要代码修改的发现，任务返回实施环节，等待原 `repo-coder` 返工并重新验证。

#### 0.4.1.11 `writeback_done`

结果已按分区规则写回项目区、候选区或来源区。

进入条件：

- 已记录 `files_written`
- 已记录 `target_zone`
- 已记录 `candidate_created / promoted_to_knowledge / source_notes_created`
- 已记录 `pending_items`
- 已记录 `residual_risks`
- 已记录 `sync_mode`
- 已记录 `current_updated`
- 已记录 `delta_created`
- 已记录 `delta_merged`
- 已记录 `baseline_status_checked`
- 已记录 `default_entry_verified`
- 已记录 `single_pass_recoverable`

阻断条件：

- 未通过 review
- 写回分区不明
- 未审内容拟写入正式知识区
- 缺少来源与边界
- 需要更新的 current 未更新
- 新增 delta 但未说明为何允许 `delta_only`
- 历史文档未标记 `merged_into / supersedes / lifecycle_state`
- `default_entry` 未校验
- `single_pass_recoverable = false`

#### 0.4.1.12 `closed`

形成最终摘要与残留风险列表。

---

## 0.5 主代理调度契约与子代理调用顺序

### 0.5.1 主代理调度契约

在双侧闭环任务中，Codex 主代理默认承担 `workflow-orchestrator` 职责。

主代理负责：

- 接收任务
- 识别 `primary_type`
- 识别 `task_modifiers`
- 检查进入条件
- 维护状态对象
- 决定是否调用子代理
- 裁剪子代理输入
- 控制 reviewer 独立性
- 控制返工轮次
- 决定 `stop / confirm / replan / escalate / close`
- 汇总最终输出
- 维护 `run_log / audit_log`

主代理默认不得：

- 直接修改代码
- 直接替代 reviewer 做质量裁决
- 绕过 review 直接进入 knowledge writeback
- 把未审内容直接写入正式知识区

### 0.5.2 主代理对子代理的默认调用顺序

以下顺序描述的是主代理在 orchestration 模式下对子代理的默认调用顺序。  
`workflow-orchestrator` 默认由主代理承担，不作为普通子代理列入调用链。

默认子代理顺序：

1. `knowledge-planner`
2. `repo-coder`
3. `repo-reviewer`
4. `knowledge-closer`

条件分支：

- 若本地知识不足且允许联网：插入 `source-ingestor`，并在其后重新经过 `knowledge-planner` 收敛计划
- 若 `primary_type = bug_fix` 且根因复杂：可插入 `failure-analyst`
- 若为高风险任务或验证矩阵复杂：可插入 `verification-manager`
- 若为功能符合度审核：可使用 `functional-reviewer` 替代或补充 `repo-reviewer`
- 若任务涉及正式知识提升审查：可插入 `knowledge-auditor`

### 0.5.3 reviewer 独立性要求

为降低上下文污染，`repo-reviewer` 或 `functional-reviewer` 的调度应满足：

1. 使用独立的 reviewer 实例或独立会话阶段。
2. 输入尽量裁剪为任务目标、验收标准、实施计划、diff、验证结果和必要代码上下文。
3. 不默认传入 `repo-coder` 的完整自然语言推理、排查草稿或无界历史对话。
4. reviewer 只负责质量判定，不负责直接修改代码或提前执行知识回写。

### 0.5.4 coder 到 reviewer 的最小交接包

推荐交给 reviewer 的最小材料为：

- `task_goal`
- `acceptance_criteria`
- `implementation_plan`
- `diff_summary`
- `verification_results`
- `necessary_code_context`
- `verification_tier`

若无法构造上述最小交接包，应视为审查前置条件不足，而不是让 reviewer 继承全量执行上下文。

### 0.5.5 review 后返工责任

默认规则：

1. reviewer 负责判定，不负责修改。
2. 若审查结论要求代码变更，返工责任默认归原 `repo-coder`。
3. 主代理负责调度、裁剪审查结论、维持状态机，不直接吸收返工实现。
4. 只有当原 coder 不可恢复、连续返工不收敛或返工已超出授权范围时，才切换修复责任人或回到 planner。

推荐返工交接包：

- `review_conclusion`
- `findings`
- `finding_severity`
- `next_action`
- `affected_files`
- `verification_gaps`

循环控制要求：

- 默认保留原 coder 会话直到审查通过或明确终止
- 每轮返工后必须重新执行受影响验证
- 每轮返工后必须再次使用独立 reviewer
- 连续返工超过 2 轮时，默认升级为重新规划或人工确认

---

## 0.6 子代理调用矩阵

### 0.6.1 `knowledge_task + read_only`

- 主代理职责：确认允许范围、裁剪检索目标、维护轻量状态与输出
- 必须显式调用的子代理：`knowledge-planner`
- 条件启用的子代理：`source-ingestor`
- 可被主代理轻量吸收的职责：最终汇总、轻量 writeback 建议

### 0.6.2 `knowledge_task + requires_web + read_only`

- 主代理职责：确认联网授权、限定候选落区、控制不进入正式知识
- 必须显式调用的子代理：`knowledge-planner`、`source-ingestor`
- 条件启用的子代理：`knowledge-auditor`
- 可被主代理轻量吸收的职责：候选整理摘要

### 0.6.3 `implementation + code_change_allowed + review_required`

- 主代理职责：维护状态机、控制默认链路与返工轮次
- 必须显式调用的子代理：`knowledge-planner`、`repo-coder`、`repo-reviewer`、`knowledge-closer`
- 条件启用的子代理：`source-ingestor`、`verification-manager`
- 可被主代理轻量吸收的职责：轻量确认点判断

### 0.6.4 `bug_fix + code_change_allowed + review_required`

- 主代理职责：确认预期行为、实际行为与根因路径是否充分
- 必须显式调用的子代理：`knowledge-planner`、`repo-coder`、`repo-reviewer`、`knowledge-closer`
- 条件启用的子代理：`failure-analyst`、`source-ingestor`、`verification-manager`
- 可被主代理轻量吸收的职责：返工轮次控制

### 0.6.5 `optimization + code_change_allowed + review_required`

- 主代理职责：控制不演化为结构性重构，维护收益验证门禁
- 必须显式调用的子代理：`knowledge-planner`、`repo-coder`、`repo-reviewer`、`knowledge-closer`
- 条件启用的子代理：`verification-manager`、`source-ingestor`
- 可被主代理轻量吸收的职责：收益对比摘要

### 0.6.6 `audit + functional_scope + read_only`

- 主代理职责：确认规范来源、证据优先级与只读边界
- 必须显式调用的子代理：`knowledge-planner`、`functional-reviewer`
- 条件启用的子代理：`source-ingestor`、`knowledge-closer`
- 可被主代理轻量吸收的职责：验收条目整理

### 0.6.7 `knowledge_task + promotion_review + writeback_required`

- 主代理职责：确认候选来源、边界、风险与证据链
- 必须显式调用的子代理：`knowledge-closer`
- 条件启用的子代理：`knowledge-auditor`、`source-ingestor`
- 可被主代理轻量吸收的职责：候选汇总、转正建议编排

---

## 0.7 verification_tier

### 0.7.1 分级定义

- `V0`：仅要求文档核对、结构检查或知识整理一致性校验
- `V1`：要求最小功能验证或最小复现验证
- `V2`：要求受影响范围回归验证，包含相关测试、静态检查或集成验证
- `V3`：要求高风险多维验证，包含核心行为、回归、兼容性、边界条件或性能证据闭环

### 0.7.2 角色责任

- planner 必须输出 `verification_tier`
- planner 必须输出 `required / optional / unavailable` 验证集合
- coder 必须按 tier 执行可执行验证并记录不可执行原因
- reviewer 必须检查是否按 tier 执行

### 0.7.3 blocker 规则

- `required` 验证缺失：默认构成 blocker
- `optional` 验证缺失：不自动构成 blocker，但必须记录风险
- `unavailable` 验证：必须说明原因、影响范围和替代证据

---

## 0.8 scope creep trigger

若满足以下任一条件，主代理必须 `stop / confirm / replan`：

- 修改文件数超过预设上限
- 新增模块超过预设上限
- 涉及公共接口签名变更
- 涉及 schema / ABI / serialization format
- 涉及跨层调用链变化
- 新增外部依赖
- 原定 `primary_type = bug_fix` 演化为 `refactor / redesign`
- 原定 `primary_type = optimization` 演化为结构性重构

推荐策略：

- 轻微超出且仍在授权边界内：`allow_minor_expansion_with_record`
- 影响计划与验证门禁：`replan_required`
- 影响任务语义或授权边界：`stop_and_confirm`

---

## 0.9 角色输入输出契约

### 0.9.1 knowledge-planner

输入：

- 任务目标
- 知识侧允许范围
- 项目侧允许范围
- 可选的来源范围与联网策略

输出：

- 主类型与修饰属性
- 已读取文件
- 实施计划
- 验证计划
- `verification_tier`
- `required / optional / unavailable` 验证集合
- 回写建议
- 未解决不确定项

停止条件：

- 未获得允许范围
- 无法确定 `primary_type` 或 `task_modifiers`
- 需要联网但未授权

### 0.9.2 repo-coder

输入：

- 任务目标
- 计划
- 代码库允许修改范围
- 验证命令
- 不做事项
- `verification_tier`

输出：

- 修改文件
- 实施结果
- 执行过的验证
- 未解决技术风险
- 对审查发现的返工结果
- `scope_creep_triggered`

停止条件：

- 需修改禁止目录
- 需做接口级变更
- 无法完成最小验证
- reviewer 发现需要返工但返工内容已超出当前授权范围

### 0.9.3 repo-reviewer

输入：

- 任务目标
- 计划与验收标准
- diff 摘要
- 验证结果
- 必要代码上下文
- `verification_tier`

输出：

- `goal_alignment_assessment`
- `scope_compliance_assessment`
- `validation_coverage_assessment`
- `regression_risk_assessment`
- `behavioral_correctness_assessment`
- `overall_decision`
- `findings`
- `finding_severity`
- `next_action`
- `fix_owner`

停止条件：

- 关键验证缺失
- 修改目标与计划不一致
- 审查输入未裁剪且无法保证独立性

### 0.9.4 functional-reviewer

输入：

- 任务目标
- 规范输入
- 验收条目
- 代码或运行证据
- 必要上下文

输出：

- `acceptance_items`
- `compliance_matrix`
- `evidence_used`
- `evidence_gaps`
- `norm_conflicts`
- `review_conclusion`
- `suggested_followup`

停止条件：

- 规范输入不足
- 证据不足以支撑判定
- 规范冲突未被显式标注

### 0.9.5 verification-manager

输入：

- 任务目标
- 风险边界
- 实施计划
- 已执行验证

输出：

- 验证矩阵
- tier 对应验证要求
- 缺失验证分类
- blocker 判断

停止条件：

- 无法定义验证目标
- 验证证据无法映射到风险边界

### 0.9.6 failure-analyst

输入：

- 预期行为
- 实际行为
- 复现路径
- 日志与错误证据
- 相关代码线索

输出：

- 根因假设
- 证据优先级
- 最小验证路径
- 是否需要 replan

停止条件：

- 预期行为未定义
- 证据不足以形成可检验假设

### 0.9.7 knowledge-auditor

输入：

- 候选条目
- 来源与证据
- 适用边界
- 风险
- 来源任务

输出：

- 提升建议
- 复用价值判断
- 边界补全建议
- 是否仍应停留在候选区

停止条件：

- 候选缺少来源
- 边界与风险缺失
- 无法判断其是否只是项目特例

### 0.9.8 knowledge-closer

输入：

- 任务目标
- 实际修改
- 验证结果
- 审查结论

输出：

- 项目回写内容
- 知识候选
- 来源记录
- 未闭环事项
- `run_log`
- `audit_log`

停止条件：

- 无法确定分区位置
- 结论缺少来源或边界

---

## 0.10 确认点、停止条件与返工升级

### 0.10.1 以下场景建议强制确认

- 首次定义允许访问范围
- 涉及公共接口变化
- 涉及 schema / ABI / 数据结构兼容性变化
- 涉及批量重构或删除逻辑
- 计划与原始需求明显偏离
- 需要将内容提升为 `01_Knowledge/`
- reviewer 独立性被破坏但仍试图直接给出审查裁决

### 0.10.2 以下场景必须停止

- 未明确允许范围
- 无法验证核心改动
- 外部信息未经审核却拟入正式知识区
- 发现任务目标本身矛盾
- `scope_creep_trigger` 已命中且未确认处理策略

### 0.10.3 返工升级规则

- review 不通过后默认由原 `repo-coder` 返工
- 可影响返工路径的角色：`repo-reviewer`、`functional-reviewer`、`verification-manager`
- 连续返工超过 2 轮时，默认升级为 `replan` 或人工确认
- 当根因假设失效、`scope_creep_trigger` 命中、返工超出授权范围时，应回 `knowledge-planner`，而不是继续原地循环

---

## 0.11 run_log / audit_log

运行记录至少应包含以下字段：

- `task_id`
- `primary_type`
- `task_modifiers`
- `verification_tier`
- `roles_invoked`
- `rework_rounds`
- `files_changed_count`
- `review_findings_count`
- `blocker_count`
- `candidate_count`
- `promotion_count`
- `sync_mode`
- `current_updated`
- `delta_created`
- `delta_merged`
- `baseline_status_checked`
- `default_entry_verified`
- `single_pass_recoverable`
- `final_status`
- `stop_reason`

建议补充：

- `state_transitions`
- `entry_conditions_satisfied`
- `blocking_conditions_hit`
- `scope_creep_triggered`

---

## 0.12 调度 prompt 设计原则

调度 prompt 只负责实例化本轮任务，不负责重写长期制度。

一个合格的调度 prompt 应包含：

- 本轮任务目标
- 输入材料
- 允许范围
- 是否允许联网
- 是否需要确认
- 输出要求
- reviewer 是否独立调度以及 reviewer 的输入边界
- review 未通过时由谁返工以及返工轮次上限
- `verification_tier`
- `scope_creep_policy`
- `extended_roles`

一个不合格的调度 prompt 往往会：

- 临时定义长期角色
- 重复知识分区规则
- 重复仓库级验证制度
- 同时塞入过多特例和例外
- 让 reviewer 直接继承 coder 的完整上下文叙述

---

## 0.13 调度 prompt 模板

### 0.13.1 通用型

```text
按 Agent 双侧运行规范执行本次任务。

技术基准：
- [[01_Knowledge/Agent Workflow/Agent驱动知识库与代码库协同闭环规范]]
- [[01_Knowledge/Agent Workflow/Agent双侧运行规范与调度模板]]

任务目标：
[填写目标]

主类型：
[填写 primary_type]

任务修饰属性：
[填写 task_modifiers]

允许范围：
- 知识库读取：[填写路径]
- 项目区读写：[填写路径]
- 代码库修改：[填写路径]

联网策略：
[允许 / 禁止 / 条件允许]

main_agent_mode:
- orchestration

planner_mode:
- explicit / lightweight_absorbed

writeback_mode:
- explicit / recommendation_only

verification_tier:
- V0 / V1 / V2 / V3

scope_creep_policy:
- stop_and_confirm / replan_required / allow_minor_expansion_with_record

extended_roles:
- failure-analyst: enabled / disabled
- verification-manager: enabled / disabled
- functional-reviewer: enabled / disabled
- knowledge-auditor: enabled / disabled

确认策略：
[填写确认点与停止条件]

主代理职责：
- 维护状态机与状态门禁
- 决定角色调用顺序
- 裁剪交接包
- 控制 reviewer 独立性
- 控制返工轮次
- 汇总最终输出

主代理不得：
- 直接修改代码
- 替代 reviewer 做质量裁决
- 绕过 review 进入 knowledge writeback
- 把未审内容直接写入正式知识区

说明：
以下顺序描述的是主代理在 orchestration 模式下对子代理的默认调用顺序。
workflow-orchestrator 默认由主代理承担，不作为普通子代理列入调用链。

子代理调用顺序：
1. 先调用 knowledge-planner，输出主类型、修饰属性、已读取范围、实施计划、验证计划、verification_tier、验证集合、建议回写路径。
2. 如本地知识不足且允许联网，再调用 source-ingestor，结果只写候选区或来源区；之后重新经过 knowledge-planner 收敛计划。
3. 如验证矩阵复杂，再调用 verification-manager 补充 required / optional / unavailable 验证集合。
4. 再调用 repo-coder，仅在授权范围内实施修改并执行最小验证。
5. 再调用 repo-reviewer，使用独立 reviewer 实例，仅接收任务目标、验收标准、计划、diff、验证结果和必要代码上下文，独立检查越界风险、验证覆盖和行为变化。
6. 若 review 不通过，则将裁剪后的审查结论返回原 repo-coder 返工；超过 2 轮、根因失效或 scope creep 触发时，回 planner 或 stop / confirm / escalate。
7. 仅在 review 通过后调用 knowledge-closer，按分区规则回写结果。

输出要求：
- roles_invoked
- state_transitions
- rework_rounds
- overall_decision
- verification_tier
- files_read
- files_written
- implementation_plan
- verification_results
- review_conclusion
- writeback_targets
- risks_or_uncertainties
- rule_changes_summary
- run_log / audit_log（如适用）
```

### 0.13.2 功能审核型

```text
按 Agent 双侧运行规范执行本次功能审核任务。

技术基准：
- [[01_Knowledge/Agent Workflow/Agent驱动知识库与代码库协同闭环规范]]
- [[01_Knowledge/Agent Workflow/Agent双侧运行规范与调度模板]]

任务目标：
[填写要审核的功能或能力]

审核对象：
[功能模块 / 接口 / 状态机 / 页面行为 / 算法行为]

规范输入：
[填写技术规范、设计要求、验收标准、接口契约、时序约束、边界条件]

实现输入：
[填写代码路径 / diff / 可执行产物 / 测试结果 / 日志 / trace / 截图]

主类型：
audit

任务修饰属性：
[functional_scope, read_only]

允许范围：
- 知识库读取：[填写路径]
- 项目区读写：[填写路径]
- 代码库读取：[填写路径]
- 代码库修改：默认禁止

联网策略：
[允许 / 禁止 / 条件允许]

main_agent_mode:
- orchestration

planner_mode:
- explicit / lightweight_absorbed

writeback_mode:
- explicit / recommendation_only

verification_tier:
- V0 / V1 / V2 / V3

scope_creep_policy:
- stop_and_confirm / replan_required / allow_minor_expansion_with_record

extended_roles:
- failure-analyst: disabled
- verification-manager: disabled
- functional-reviewer: enabled
- knowledge-auditor: enabled / disabled

主代理职责：
- 确认规范来源与允许范围
- 维护状态对象
- 控制 reviewer 独立性
- 汇总审核结论与后续动作

主代理不得：
- 直接修改代码
- 用 coder/planner 解释替代证据
- 绕过 review 直接写入正式知识区

说明：
以下顺序描述的是主代理在 orchestration 模式下对子代理的默认调用顺序。
workflow-orchestrator 默认由主代理承担，不作为普通子代理列入调用链。

证据优先级：
- 行为证据 > 规范文本 > 代码证据 > coder/planner 解释

子代理调用顺序：
1. 先调用 knowledge-planner 的轻量模式，仅完成规范来源确认、允许范围确认、验收条目整理与 verification_tier 输出。
2. 如本地规范不足且允许联网，再调用 source-ingestor，结果只写候选区或来源区。
3. 调用 functional-reviewer；如无需独立功能审查，可由 repo-reviewer 轻量兜底。
4. reviewer 必须输出 acceptance_items、compliance_matrix、evidence_used、evidence_gaps、norm_conflicts、review_conclusion、suggested_followup。
5. 若审核不通过，不直接修代码；建议转入 `primary_type = bug_fix / optimization` 或 redesign 时，由主代理 stop / confirm / replan。
6. 若审核通过且需要沉淀，再调用 knowledge-closer；若涉及正式知识提升审查，可插入 knowledge-auditor。

输出要求：
- roles_invoked
- state_transitions
- rework_rounds
- overall_decision
- verification_tier
- files_read
- audit_scope
- acceptance_items
- compliance_matrix
- evidence_used
- evidence_gaps
- review_conclusion
- suggested_followup
- writeback_targets
- risks_or_uncertainties
- run_log / audit_log（如适用）
```

### 0.13.3 缺陷修复型

```text
按 Agent 双侧运行规范执行本次缺陷修复任务。

技术基准：
- [[01_Knowledge/Agent Workflow/Agent驱动知识库与代码库协同闭环规范]]
- [[01_Knowledge/Agent Workflow/Agent双侧运行规范与调度模板]]

任务目标：
[填写缺陷目标]

缺陷类型：
[runtime_bug / functional_bug / design_mismatch]

预期行为：
[填写设计要求、验收标准或方案约束]

实际行为：
[填写当前表现、错误输出、偏差现象]

已知证据：
[日志 / 截图 / 复现输入 / 指标异常 / 相关代码线索]

主类型：
bug_fix

任务修饰属性：
[code_change_allowed, review_required]

允许范围：
- 知识库读取：[填写路径]
- 项目区读写：[填写路径]
- 代码库修改：[填写路径]

联网策略：
[允许 / 禁止 / 条件允许]

main_agent_mode:
- orchestration

planner_mode:
- explicit

writeback_mode:
- explicit / recommendation_only

verification_tier:
- V1 / V2 / V3

scope_creep_policy:
- stop_and_confirm / replan_required / allow_minor_expansion_with_record

extended_roles:
- failure-analyst: enabled / disabled
- verification-manager: enabled / disabled
- functional-reviewer: disabled
- knowledge-auditor: enabled / disabled

主代理职责：
- 检查预期行为、实际行为、根因假设与最小验证路径
- 维护返工轮次
- 决定是否 replan 或 escalate

主代理不得：
- 直接修改代码
- 替代 reviewer 做质量裁决
- 在 review 前进入 writeback

说明：
以下顺序描述的是主代理在 orchestration 模式下对子代理的默认调用顺序。
workflow-orchestrator 默认由主代理承担，不作为普通子代理列入调用链。

子代理调用顺序：
1. knowledge-planner 输出主类型、修饰属性、已读取范围、根因假设、最小验证路径、修复计划、verification_tier、建议回写路径。
2. 若根因复杂或多轮返工不收敛，可插入 failure-analyst，补充根因假设、证据优先级和最小验证路径。
3. 如本地知识不足且允许联网，再调用 source-ingestor，结果只写候选区或来源区；之后重新经过 knowledge-planner 收敛计划。
4. 如验证矩阵复杂，再调用 verification-manager。
5. 调用 repo-coder，仅在授权范围内实施符合设计边界的修复，并执行最小必要验证与相关回归验证。
6. 调用 repo-reviewer，仅接收任务目标、预期行为、实际行为、验收标准、实施计划、diff、验证结果和必要代码上下文，独立检查根因是否闭环、改动是否越界、验证是否覆盖行为失配、是否仍存在回归风险。
7. 若 review 不通过，默认返回原 repo-coder 返工；根因假设失效、scope creep 触发或返工超出授权范围时，回 planner。
8. 仅在 review 通过后，knowledge-closer 回写调试记录、修复结论、failure_mode 候选和未闭环事项；如涉及正式知识提升审查，可插入 knowledge-auditor。

输出要求：
- roles_invoked
- state_transitions
- rework_rounds
- overall_decision
- verification_tier
- files_read
- files_written
- root_cause_hypotheses
- implementation_plan
- verification_results
- review_conclusion
- writeback_targets
- risks_or_uncertainties
- run_log / audit_log（如适用）
```

### 0.13.4 受控优化型

```text
按 Agent 双侧运行规范执行本次受控优化任务。

技术基准：
- [[01_Knowledge/Agent Workflow/Agent驱动知识库与代码库协同闭环规范]]
- [[01_Knowledge/Agent Workflow/Agent双侧运行规范与调度模板]]

任务目标：
[填写优化目标]

优化类型：
[performance / memory / latency / maintainability / build / test]

优化依据：
[填写瓶颈证据、基线数据、重复问题或明确设计依据]

基线现状：
[填写当前耗时、资源占用、复杂度或维护问题]

目标指标：
[填写希望改善的指标或约束]

非目标项：
[填写明确不做事项]

主类型：
optimization

任务修饰属性：
[code_change_allowed, review_required]

允许范围：
- 知识库读取：[填写路径]
- 项目区读写：[填写路径]
- 代码库修改：[填写路径]

联网策略：
[允许 / 禁止 / 条件允许]

main_agent_mode:
- orchestration

planner_mode:
- explicit

writeback_mode:
- explicit / recommendation_only

verification_tier:
- V1 / V2 / V3

scope_creep_policy:
- stop_and_confirm / replan_required / allow_minor_expansion_with_record

extended_roles:
- failure-analyst: disabled
- verification-manager: enabled
- functional-reviewer: disabled
- knowledge-auditor: enabled / disabled

主代理职责：
- 控制 scope creep
- 检查优化依据、收益验证和语义回归验证
- 决定是否需要 replan 或 stop_and_confirm

主代理不得：
- 直接修改代码
- 替代 reviewer 给出质量裁决
- 绕过 review 直接沉淀优化结论

说明：
以下顺序描述的是主代理在 orchestration 模式下对子代理的默认调用顺序。
workflow-orchestrator 默认由主代理承担，不作为普通子代理列入调用链。

子代理调用顺序：
1. knowledge-planner 输出优化依据、风险边界、非目标项、验证计划、verification_tier 和回写建议。
2. 如本地知识不足且允许联网，再调用 source-ingestor，结果只写候选区或来源区；之后重新经过 knowledge-planner 收敛计划。
3. 调用 verification-manager，补充收益验证、语义回归验证和 tier 对应验证集合。
4. 调用 repo-coder，仅在授权范围内实施边界内优化，并完成收益验证与语义回归验证。
5. 调用 repo-reviewer，仅接收任务目标、目标指标、非目标项、实施计划、diff、验证结果和必要代码上下文，独立检查是否越界、是否改变核心语义、优化收益是否有证据、是否引入新的回归风险。
6. 若 review 不通过，默认返回原 repo-coder；若优化演化为结构性重构或验证不足构成 blocker，则 stop / confirm / replan。
7. 仅在 review 通过后，knowledge-closer 回写项目优化记录、可复用候选和未闭环事项；如涉及正式知识提升审查，可插入 knowledge-auditor。

输出要求：
- roles_invoked
- state_transitions
- rework_rounds
- overall_decision
- verification_tier
- files_read
- files_written
- optimization_basis
- implementation_plan
- verification_results
- review_conclusion
- writeback_targets
- risks_or_uncertainties
- run_log / audit_log（如适用）
```

---

## 0.14 回写输出格式

任务结束时，统一输出：

### 0.14.1 Summary

- primary_type:
- task_modifiers:
- allowed_paths:
- files_read:
- files_written:
- sync_mode:
- current_files_must_update:
- history_files_to_mark:
- default_entry_verified:
- single_pass_recoverable:

### 0.14.2 Review status

- candidate_created:
- promoted_to_knowledge:
- source_notes_created:
- current_updated:
- delta_created:
- delta_merged:
- baseline_status_checked:

### 0.14.3 Risks / uncertainties

- ...

---

## 0.15 使用建议

建议按以下顺序使用三篇文档：

1. 先读 [[01_Knowledge/Agent Workflow/Agent驱动知识库与代码库协同闭环规范]]，明确原则和边界。
2. 读本文档，按运行状态机和调度模板组织任务。
3. 读 [[01_Knowledge/Agent Workflow/Agent双侧模板与文件结构规范]]，在根目录生成所需文件骨架。

---

## 0.16 文档收敛运行补充

### 0.16.1 适用前提

当任务涉及设计演化、实现状态更新、审核结论收敛、文档体系整理或历史记录压缩时，主代理必须把“文档收敛与状态更新”视为闭环的一部分，而不是可选附加项。

### 0.16.2 计划阶段新增输出

`knowledge-planner` 在 `plan_ready` 前必须补充：

- `document_role_strategy`
- `current_docs_expected`
- `spec_source_required`
- `implementation_input_chain`
- `default_recovery_bundle`
- `delta_docs_to_merge`
- `baseline_docs_to_downgrade`
- `adr_needed`
- `retrieval_priority_plan`
- `current_recoverability_goal`
- `sync_mode`
- `why_delta_only_allowed`
- `current_files_must_update`
- `history_files_to_mark`

其中 `document_role_strategy` 至少要回答：

- 哪些文档是 `baseline`
- 哪些文档是 `overview_current / design_current / spec_current / implementation_current / validation_current`
- 哪些文档是 `delta`
- 哪些文档应转为 `archive` 或 `superseded`
- 哪些文档应保持 `default_entry = true`

### 0.16.3 状态机新增检查点

标准状态机在 `implementation_done` 与 `writeback_done` 之间增加显式门禁：

1. `knowledge_sync_checked`
2. `convergence_ready`

进入 `knowledge_sync_checked` 的前提：

- 已评估代码、设计、接口、约束或状态机是否变化
- 已判断 `current / adr / delta` 是否需要同步更新
- 已输出 `sync_mode / current_files_must_update / history_files_to_mark`
- 若为 `delta_only`，已给出合法举证

进入 `convergence_ready` 的前提：

- 已确认当前态是否可被单次恢复
- 已确认默认实现输入链是否可由 current 文档独立成立
- 已确认历史文档是否完成最小状态标记
- 已确认 default retrieval 不再以历史 baseline 作为主入口
- 已确认 `default_entry_verified = true`
- 已确认 `single_pass_recoverable = true`

若这两个门禁未通过，不得进入 `writeback_done`。

### 0.16.4 角色补充职责放置规则

与文档收敛相关的角色补充职责，应写入 [[01_Knowledge/Agent Workflow/Agent双侧模板与文件结构规范]] 中对应角色的 `toml` 模板，而不是写在运行模板里重复定义。
本文档只保留状态机、门禁、输入输出与调度要求。

### 0.16.5 默认检索顺序

在 orchestration 模式下，主代理组织上下文时默认按以下顺序读取：

1. `overview_current / design_current / spec_current`
2. `implementation_current / validation_current`
3. pending delta
4. adr / decision ledger
5. merged delta
6. superseded baseline / archive

若当前目录未形成该顺序，planner 应把“建立 current 入口”列入实施计划。

若同一主题存在 2 份及以上 current 文档而缺少 `overview_current`，planner 不得把该主题判定为已收敛，必须把建立 `overview_current` 列入实施计划。

### 0.16.6 current 可恢复性最低标准

若任务要求文档收敛，则 writeback 前至少满足以下问题可由单次 current 检索回答：

1. 当前模块目标与边界是什么
2. 当前主流程、状态机或生命周期是什么
3. 当前对外接口或结果事实源是什么
4. 当前已知限制与未闭环项是什么
5. 哪些历史文档只保留为证据，不再代表当前真相

### 0.16.7 默认实现输入链最低标准

若任务要求“按规范实现代码”，则 writeback 或执行前至少满足：

1. `design_current` 能说明目标、边界与设计原则
2. `spec_current` 能说明必须满足的行为、接口、状态规则与非目标项
3. `implementation_current` 能说明当前代码事实与修改落点
4. `validation_current` 能说明当前证据边界与所需验证
5. coder 不再需要读取 baseline 才能补齐关键实现约束

若主题已存在 `spec_current`，则 `implementation / bug_fix / optimization` 类任务中 coder 不得绕过 `spec_current` 直接基于 baseline 或 delta 实施。
历史补丁驱动开发应被视为 blocker，而不是可接受捷径。

### 0.16.8 orchestration 任务模板补充

涉及文档收敛的任务，在“实施计划”和“验证计划”中至少增加两段：

- 规范更新阶段：更新角色分层、状态头、收敛规则、knowledge sync 与检索优先级
- 文档收敛阶段：建立/更新 current，标记 baseline 与 delta 状态，验证 current 可恢复性

输出要求还应补充：

- `document_role_strategy`
- `implementation_input_chain`
- `default_recovery_bundle`
- `spec_source_required`
- `current_recoverability_assessment`
- `knowledge_sync_decision`
- `convergence_decision`
- `sync_mode`
- `current_files_must_update`
- `history_files_to_mark`
- `default_entry_verified`
- `single_pass_recoverable`
