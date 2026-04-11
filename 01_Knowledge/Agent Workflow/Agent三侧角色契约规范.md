---
type: knowledge
status: verified
domain: 工程工作流
topic: Agent三侧角色契约规范
sources: ["内部方法论整理", "01_Knowledge/Agent Workflow/Agent驱动知识库、代码库与板端侧协同闭环规范.md", "01_Knowledge/Agent Workflow/Agent三侧运行规范与调度模板.md", "01_Knowledge/Agent Workflow/Agent三侧模板与文件结构规范.md"]
scope: 适用于定义三侧闭环任务中的稳定角色边界、最小输入输出契约、停止条件与 reviewer 独立性要求。本文档承接角色契约，不承接状态机与实例 prompt 模板。
risks: ["角色契约与实际工具链不一致", "主代理吸收执行层职责", "reviewer 输入未裁剪导致独立性失效", "角色契约散落在运行模板中重复维护"]
updated_at: 2026-04-11
---

## 0.1 摘要

本文档定义三侧闭环中的**角色契约层**。  
它回答“每个角色负责什么、拿什么输入、产出什么输出、何时应停止”，但不重复状态机、不承载实例 prompt。

---

## 0.2 文档定位

四层分工如下：

- 上位规范：制度边界、长期门禁、三侧职责
- 运行规范：任务入口、状态机、角色集合派生、返工升级
- 角色契约：角色边界、最小输入输出、停止条件、独立性要求
- 文件结构规范：AGENTS、toml、日志模板和骨架放置方式

---

## 0.3 与 toml 的关系

- 本文档是**角色契约的可读规范**
- `.codex/agents/*.toml` 是**角色骨架与可执行配置载体**
- 若两者发生冲突，应先更新规范，再同步 `toml`

换句话说：

- `toml` 负责让角色可被实例化
- 本文档负责让角色边界可被审查和维护

---

## 0.4 控制层角色

### 0.4.1 `workflow-orchestrator`

定位：

- 默认由主代理承担的控制层职责模式
- 不应默认列入普通子代理调用链
- 只负责调度、门禁、裁剪与审计，不吸收执行层实现

最小输入：

- `task_goal`
- `primary_type`
- `task_modifiers`
- `allowed_paths`
- `repo_scope`
- `board_target` 或 `no_board_execution`
- `verification_tier`

最小输出：

- `roles_invoked`
- `state_transitions`
- `overall_decision`
- `rework_rounds`
- `run_log`
- `audit_log`

必须做：

- 维护状态机
- 决定角色调用顺序
- 裁剪交接包
- 控制 reviewer 独立性
- 控制返工轮次
- 决定 `stop / confirm / replan / escalate / close`

不得做：

- 直接修改代码
- 直接替代 reviewer 做质量裁决
- 绕过 review 进入 knowledge writeback
- 把未审内容直接写入正式知识区
- 在 `board_execution_required` 场景下绕过上板闭环

---

## 0.5 规划与知识侧角色

### 0.5.1 `knowledge-planner`

定位：

- 负责识别任务类型、裁剪允许范围、形成计划与建议回写路径

最小输入：

- 任务目标
- 允许范围
- 项目上下文
- 可选的 `board_target`
- 联网策略

最小输出：

- `primary_type`
- `task_modifiers`
- `allowed_paths`
- `files_read`
- `implementation_plan` 或 `investigation_plan`
- `verification_plan`
- `verification_tier`
- `writeback_targets`
- `open_uncertainties`

停止条件：

- 未获得允许范围
- `board_execution_required` 但板端入口不完整
- 无法确定 `primary_type`
- 需要联网但未授权

不得做：

- 直接修改代码
- 直接创建正式知识条目

### 0.5.2 `knowledge-closer`

定位：

- 负责按分区规则回写项目结果、候选条目、来源记录和闭环摘要

最小输入：

- 任务目标
- 实际修改或调查结果
- 验证结果
- 审查结论

最小输出：

- `files_written`
- `writeback_targets`
- `candidate_created`
- `source_notes_created`
- `run_log`
- `audit_log`

停止条件：

- 无法确定分区位置
- 结论缺少来源或边界
- review 未通过却试图直接 writeback

不得做：

- 越过 reviewer 独立裁决
- 把未审来源直接提升为正式知识

### 0.5.3 `source-ingestor`

定位：

- 在允许联网时负责抓取外部信息并落入候选区或来源区

最小输入：

- 检索目标
- 联网授权
- 候选落区

最小输出：

- `files_written`
- `evidence`
- `source_notes_created`
- `candidate_created`

停止条件：

- 未授权联网
- 无法落入候选区或来源区

不得做：

- 直接写入正式知识区

### 0.5.4 `knowledge-auditor`

定位：

- 对候选知识是否具备转正条件做独立审查

最小输入：

- 候选条目
- 来源与证据
- 适用边界
- 风险说明

最小输出：

- `promotion_recommendation`
- `reusability_assessment`
- `boundary_gap_assessment`

停止条件：

- 候选缺少来源
- 边界与风险缺失

不得做：

- 直接代替 `knowledge-closer` 完成写回

---

## 0.6 代码与验证侧角色

### 0.6.1 `repo-coder`

定位：

- 在授权范围内实施修改、执行最小验证，并在需要时完成上板运行和产物采集

最小输入：

- 任务目标
- 实施计划
- 代码库允许修改范围
- 验证计划
- `verification_tier`

最小输出：

- `files_changed`
- `verification_results`
- `commands_run`
- `open_risks`
- 若涉及板端：`board_execution_artifacts`

停止条件：

- 需修改禁止目录
- 需做接口级高风险变更
- 无法完成最小验证
- 返工已超出授权范围

不得做：

- 自行给出最终质量裁决
- 跳过独立 reviewer 直接宣告完成

### 0.6.2 `repo-reviewer`

定位：

- 对实现、验证、板端证据和回归风险做独立质量裁决

最小输入：

- `task_goal`
- `acceptance_criteria`
- `implementation_plan`
- `diff_summary`
- `verification_results`
- `necessary_code_context`
- `verification_tier`
- 若涉及板端：`board_execution_artifacts`

最小输出：

- `review_conclusion`
- `findings`
- `finding_severity`
- `next_action`
- `regression_risk_assessment`
- `scope_compliance_assessment`

停止条件：

- 关键验证缺失
- 板端证据要求存在但缺失
- 输入未裁剪且无法保证独立性

独立性要求：

- 使用独立 reviewer 实例或独立会话阶段
- 不默认继承 coder 的完整自然语言推理
- 只基于裁剪后的计划、diff、验证结果和必要上下文做判断

不得做：

- 直接修改代码
- 提前执行 knowledge writeback

### 0.6.3 `functional-reviewer`

定位：

- 对功能符合度、规范符合度与验收条目做只读审查

最小输入：

- 规范输入
- 验收条目
- 代码或运行证据

最小输出：

- `acceptance_items`
- `compliance_matrix`
- `evidence_used`
- `evidence_gaps`
- `review_conclusion`

停止条件：

- 规范输入不足
- 证据不足以支持判定

### 0.6.4 `verification-manager`

定位：

- 对验证矩阵、tier 对应验证要求和 blocker 规则做补充约束

最小输入：

- 任务目标
- 风险边界
- 实施计划
- 已执行验证

最小输出：

- `verification_matrix`
- `required_optional_unavailable`
- `blocker_assessment`

停止条件：

- 无法定义验证目标
- 验证证据无法映射到风险边界

### 0.6.5 `failure-analyst`

定位：

- 在根因复杂、调查优先或多轮返工不收敛时，输出可检验假设和最小验证路径

最小输入：

- 预期行为或设计预期
- 实际行为或观测现象
- 日志、trace、指标、视频、dump、错误码等证据

最小输出：

- `hypothesis_set`
- `hypothesis_confidence`
- `evidence_priority`
- `minimal_verifiable_path`
- `next_probe_actions`

停止条件：

- 无法形成可检验假设
- 证据不足以支持分流判断

---

## 0.7 角色协作硬门禁

- 主代理不得吞并 `repo-coder + repo-reviewer + knowledge-closer` 全链路职责
- reviewer 不得继承 coder 全量上下文
- review 未通过不得 writeback
- `board_execution_required` 场景下不得绕过上板闭环
- 调查型任务中，不得在问题未定性时强推业务修复

---

## 0.8 维护建议

- 角色职责变化时，优先更新本文档，再同步 `.codex/agents/*.toml`
- 运行规范只保留“何时调用谁、何时阻断、何时返工”
- 实例 prompt 只描述本轮问题，不重复角色契约
