---
type: knowledge
status: verified
domain: 工程工作流
topic: Agent双侧运行规范与调度模板
sources: ["内部方法论整理", "01_Knowledge/Agent Workflow/Agent驱动知识库与代码库协同闭环规范.md", "01_Knowledge/Agent Workflow/Agent双侧模板与文件结构规范.md"]
scope: 适用于需要将双侧闭环规则包装成可运行流程，包括任务入口、状态推进、调度 prompt、角色输入输出契约与回写要求的场景。
risks: ["运行规范过重导致单次任务负担过大", "项目特例被误提升为通用步骤", "角色契约与实际执行工具不一致"]
updated_at: 2026-03-24
---

## 0.1 摘要

本文档定义 Agent 双侧闭环的运行规范，用于指导任务如何进入系统、按什么状态推进、何时确认、如何调度角色、如何回写结果。

技术基准：

- [[01_Knowledge/Agent Workflow/Agent驱动知识库与代码库协同闭环规范]]
- [[01_Knowledge/Agent Workflow/Agent双侧模板与文件结构规范]]

本文档回答的是“系统怎么跑起来”，而不是“文件怎么放置”。

---

## 0.2 方案评价

在现有“上位规范 + 文件结构规范”之外，再补一层运行规范是必要的，原因如下：

1. 仅有原则，缺少任务入口、状态机和确认点，执行时仍会依赖临场发挥。
2. 仅有文件模板，无法说明角色应该按什么顺序协作、何时停止、何时回写。
3. 调度 prompt 模板本质上属于运行层，不属于文件结构层，也不应塞回上位规范。

因此推荐的三层文档体系是：

- 上位规范：定义原则、边界、职责
- 运行规范：定义状态推进、调度方式、角色契约、输出格式
- 文件结构规范：定义根目录文件树与模板骨架

---

## 0.3 任务入口

每个任务在进入系统时，至少要明确以下输入对象：

- `task_goal`：本轮目标
- `task_type`：任务类型
- `allowed_paths`：允许读取与写入的目录
- `repo_scope`：代码库允许修改范围
- `confirmation_policy`：哪些步骤需要确认
- `output_contract`：需要交付哪些结果

### 0.3.1 标准任务类型

- `project_implementation`
- `background_retrieval`
- `web_research`
- `knowledge_refactor`
- `knowledge_promotion`
- `bug_fix`
	- runtime_bug  
	- functional_bug  
	- design_mismatch
- `controlled_optimization`

### 0.3.2 进入条件

任务启动前必须满足：

- 已给出目标
- 已给出知识库允许访问范围
- 若涉及代码修改，已给出代码库修改范围
- 若允许联网，已明确联网权限

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
7. `review_done`
8. `writeback_done`
9. `closed`

### 0.4.1 状态说明

#### 0.4.1.1 `task_received`

接收任务目标，判断是否信息不足。

#### 0.4.1.2 `scope_confirmed`

确认知识侧与代码侧允许范围。

#### 0.4.1.3 `context_retrieved`

完成项目区、正式知识区、来源区的受控检索。

#### 0.4.1.4 `plan_ready`

输出实施计划、验证计划、回写路径和不确定项。

#### 0.4.1.5 `execution_approved`

若任务要求确认，则在此节点停下；若无需确认，可继续执行。

#### 0.4.1.6 `implementation_done`

代码修改、知识整理或外部信息采集已完成。

#### 0.4.1.7 `review_done`

完成独立审查，确认是否存在越界、缺少验证或风险未闭环。

#### 0.4.1.8 `writeback_done`

结果已按分区规则写回项目区、候选区或来源区。

#### 0.4.1.9 `closed`

形成最终摘要与残留风险列表。

---

## 0.5 标准调度顺序

### 0.5.1 默认顺序

1. `knowledge-planner`
2. `repo-coder` 或其他执行角色
3. `repo-reviewer`
4. `knowledge-closer`

其中 `repo-reviewer` 应作为独立审查阶段单独存在，不应默认继承 `repo-coder` 的完整上下文。

### 0.5.2 可选分支

若本地知识不足且任务允许联网，可在 planner 之后插入：

- `source-ingestor`

插入顺序为：

1. `knowledge-planner`
2. `source-ingestor`
3. `knowledge-planner` 重新收敛计划
4. `repo-coder`
5. `repo-reviewer`
6. `knowledge-closer`

### 0.5.3 reviewer 独立性要求

为降低上下文污染，`repo-reviewer` 的调度应满足：

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

若无法构造上述最小交接包，应视为审查前置条件不足，而不是让 reviewer 继承全量执行上下文。

---

## 0.6 角色输入输出契约

### 0.6.1 knowledge-planner

输入：

- 任务目标
- 知识侧允许范围
- 项目侧允许范围
- 可选的来源范围与联网策略

输出：

- 任务类型
- 已读取文件
- 实施计划
- 验证计划
- 回写建议
- 未解决不确定项

停止条件：

- 未获得允许范围
- 无法确定任务类型
- 需要联网但未授权

### 0.6.2 repo-coder

输入：

- 任务目标
- 计划
- 代码库允许修改范围
- 验证命令
- 不做事项

输出：

- 修改文件
- 实施结果
- 执行过的验证
- 未解决技术风险

停止条件：

- 需修改禁止目录
- 需做接口级变更
- 无法完成最小验证

### 0.6.3 repo-reviewer

输入：

- 任务目标
- 计划与验收标准
- diff 摘要
- 验证结果
- 必要代码上下文

输出：

- 审查发现
- 严重级别分类
- 越界判断
- 回归风险
- 审查结论

停止条件：

- 关键验证缺失
- 修改目标与计划不一致
- 审查输入未裁剪且无法保证独立性

### 0.6.4 knowledge-closer

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

停止条件：

- 无法确定分区位置
- 结论缺少来源或边界

---

## 0.7 确认点与停止条件

以下场景建议强制确认：

- 首次定义允许访问范围
- 涉及公共接口变化
- 涉及 schema / ABI / 数据结构兼容性变化
- 涉及批量重构或删除逻辑
- 计划与原始需求明显偏离
- 需要将内容提升为 `01_Knowledge/`
- reviewer 独立性被破坏但仍试图直接给出审查裁决

以下场景必须停止：

- 未明确允许范围
- 无法验证核心改动
- 外部信息未经审核却拟入正式知识区
- 发现任务目标本身矛盾

---

## 0.8 调度 prompt 设计原则

调度 prompt 只负责实例化本轮任务，不负责重写长期制度。

一个合格的调度 prompt 应包含：

- 本轮任务目标
- 输入材料
- 允许范围
- 是否允许联网
- 是否需要确认
- 输出要求
- reviewer 是否独立调度以及 reviewer 的输入边界

一个不合格的调度 prompt 往往会：

- 临时定义长期角色
- 重复知识分区规则
- 重复仓库级验证制度
- 同时塞入过多特例和例外
- 让 reviewer 直接继承 coder 的完整上下文叙述

---

## 0.9 调度 prompt 模板

### 0.9.1 通用型

```text
按 Agent 双侧运行规范执行本次任务。

技术基准：
- [[01_Knowledge/Agent Workflow/Agent驱动知识库与代码库协同闭环规范]]
- [[01_Knowledge/Agent Workflow/Agent双侧运行规范与调度模板]]

任务目标：
[填写目标]

任务类型：
[填写 task_type]

允许范围：
- 知识库读取：[填写路径]
- 项目区读写：[填写路径]
- 代码库修改：[填写路径]

联网策略：
[允许 / 禁止 / 条件允许]

确认策略：
[以下场景强制确认：

- 首次定义允许访问范围
- 涉及公共接口变化
- 涉及 schema / ABI / 数据结构兼容性变化
- 涉及批量重构或删除逻辑
- 计划与原始需求明显偏离
- 需要将内容提升为 `01_Knowledge/`
- reviewer 独立性被破坏但仍试图直接给出审查裁决

以下场景必须停止：

- 未明确允许范围
- 无法验证核心改动
- 外部信息未经审核却拟入正式知识区
- 发现任务目标本身矛盾]

调度顺序：
1. 先调用 knowledge-planner，输出任务类型、已读取范围、实施计划、验证计划、建议回写路径。
2. 如本地知识不足且允许联网，再调用 source-ingestor，结果只写候选区或来源区。
3. 再调用 repo-coder，仅在授权范围内实施修改并执行最小验证。
4. 再调用 repo-reviewer，使用独立 reviewer 实例，仅接收任务目标、验收标准、计划、diff、验证结果和必要代码上下文，独立检查越界风险、验证覆盖和行为变化。
5. 最后调用 knowledge-closer，按分区规则回写结果。

输出要求：
- files_read
- files_written
- implementation_plan
- verification_results
- review_conclusion
- writeback_targets
- risks_or_uncertainties
```

### 0.9.2 缺陷修复型

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
  
任务类型：  
bug_fix  
  
允许范围：  
- 知识库读取：[填写路径]  
- 项目区读写：[填写路径]  
- 代码库修改：[填写路径]  
  
联网策略：  
[允许 / 禁止 / 条件允许]  
  
确认策略：  
以下场景强制确认：  
- 首次定义允许访问范围  
- 涉及公共接口变化  
- 涉及 schema / ABI / 数据结构兼容性变化  
- 涉及批量重构或删除逻辑  
- 修复方案明显偏离“最小修复”  
- 需要将 failure mode 提升为 `01_Knowledge/`  
  
以下场景必须停止：  
- 未明确允许范围  
- 无法定义预期行为  
- 无法验证核心改动  
- 发现问题根因需要越界修改  
- 外部信息未经审核却拟入正式知识区  
  
要求：  
- 优先根因闭环  
- 优先最小修复  
- 不做方案外重构  
- 必须区分“预期行为”和“实际行为”  
- 必须说明修复是否真正闭合设计失配  
  
调度顺序：  
1. knowledge-planner 输出任务类型、已读取范围、根因假设、最小验证路径、修复计划、建议回写路径。  
2. 如本地知识不足且允许联网，再调用 source-ingestor，结果只写候选区或来源区。  
3. repo-coder 仅在授权范围内实施最小修复，并执行最小必要验证与相关回归验证。  
4. repo-reviewer 使用独立 reviewer 实例，仅接收任务目标、预期行为、实际行为、验收标准、实施计划、diff、验证结果和必要代码上下文，独立检查：  
- 根因是否闭环  
- 改动是否越界  
- 验证是否覆盖行为失配  
- 是否仍存在回归风险  
5. knowledge-closer 回写调试记录、修复结论、failure mode 候选和未闭环事项。  
  
输出要求：  
- files_read  
- files_written  
- root_cause_hypotheses  
- implementation_plan  
- verification_results  
- review_conclusion  
- writeback_targets  
- risks_or_uncertainties
```

### 0.9.3 受控优化型

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

任务类型：
controlled_optimization

允许范围：
- 知识库读取：[填写路径]
- 项目区读写：[填写路径]
- 代码库修改：[填写路径]

联网策略：
[允许 / 禁止 / 条件允许]

确认策略：
以下场景强制确认：
- 首次定义允许访问范围
- 涉及公共接口变化
- 涉及 schema / ABI / 数据结构兼容性变化
- 涉及批量重构或删除逻辑
- 优化方案演化为结构性重构
- 可能改变核心行为语义
- 需要将内容提升为 `01_Knowledge/`

以下场景必须停止：
- 未明确允许范围
- 无法给出优化依据或基线
- 无法验证优化收益
- 优化已影响核心语义但未获确认
- 外部信息未经审核却拟入正式知识区

要求：
- 明确优化依据
- 明确不做事项
- 禁止演化为大规模重构
- 必须验证优化收益
- 必须验证核心语义未改变

调度顺序：
1. knowledge-planner 输出优化依据、风险边界、非目标项、验证计划和回写建议。
2. 如本地知识不足且允许联网，再调用 source-ingestor，结果只写候选区或来源区。
3. repo-coder 仅在授权范围内实施边界内优化，并完成收益验证与语义回归验证。
4. repo-reviewer 使用独立 reviewer 实例，仅接收任务目标、目标指标、非目标项、实施计划、diff、验证结果和必要代码上下文，独立检查：
   - 是否越界
   - 是否改变核心语义
   - 优化收益是否有证据
   - 是否引入新的回归风险
5. knowledge-closer 回写项目优化记录、可复用候选和未闭环事项。

输出要求：
- files_read
- files_written
- optimization_basis
- implementation_plan
- verification_results
- review_conclusion
- writeback_targets
- risks_or_uncertainties
```

---

## 0.10 回写输出格式

任务结束时，统一输出：

### 0.10.1 Summary

- task_type:
- allowed_paths:
- files_read:
- files_written:

### 0.10.2 Review status

- candidate_created:
- promoted_to_knowledge:
- source_notes_created:

### 0.10.3 Risks / uncertainties

- ...

---

## 0.11 使用建议

建议按以下顺序使用三篇文档：

1. 先读 [[01_Knowledge/Agent Workflow/Agent驱动知识库与代码库协同闭环规范]]，明确原则和边界。
2. 读本文档，按运行状态机和调度模板组织任务。
3. 读 [[01_Knowledge/Agent Workflow/Agent双侧模板与文件结构规范]]，在根目录生成所需文件骨架。
