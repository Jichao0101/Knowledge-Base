---
type: knowledge
status: verified
domain: 工程工作流
topic: Agent驱动知识库、代码库与板端侧协同闭环规范
sources: ["内部方法论整理"]
scope: 适用于使用 Agent 连接知识库、代码库与智驾芯片板端侧，在受控知识检索、方案设计、代码实现、上板执行、日志采集、效果评估、状态回写和知识沉淀之间形成三侧闭环的通用工程协作流程
risks: ["项目特例误沉淀为正式知识", "代码优化越过需求边界", "知识库与代码库规则不一致导致越权修改", "板端执行环境与仓库实现脱节", "板端日志和效果评估未回流仓库审查", "外部信息未经审核直接进入正式知识区", "主代理 orchestration 职责不清导致角色漂移"]
updated_at: 2026-04-07
---

## 0.1 摘要

本文档定义 Agent 三侧闭环的上位规则，目标是让**知识依据、实施方案、代码改动、板端执行结果、效果评估、状态回写与知识沉淀**保持一致。
它只定义制度边界，不承载运行模板细节。

---

## 0.2 规范定位

本文档回答四个问题：

1. 闭环系统由哪些区域、规则、角色和能力组成
2. 稳定角色如何固化，而不是在单次 prompt 中临时扮演
3. 关键状态何时允许推进、何时必须阻断
4. 运行规范与文件结构规范分别承接什么内容

配套文档分层如下：

- 上位规范：`01_Knowledge/Agent Workflow/Agent驱动知识库、代码库与板端侧协同闭环规范.md`
- 运行规范：`01_Knowledge/Agent Workflow/Agent三侧运行规范与调度模板.md`
- 角色契约：`01_Knowledge/Agent Workflow/Agent三侧角色契约规范.md`
- 文件规范：`01_Knowledge/Agent Workflow/Agent三侧模板与文件结构规范.md`

---

## 0.3 系统目标

三侧闭环至少要覆盖六步：

1. 受控检索
2. 受约束规划
3. 边界内实施
4. 板端执行与产物采集
5. 分级验证与 repo review
6. 分区回写、板端结果同步与候选沉淀

它主要防止六类断裂：

- 只改代码不上板，无法进入软硬件效果闭环
- 只改代码，不回写知识
- 板端已运行，但日志与效果评估未进入 repo review
- 只写方案，不真正落地
- 板端状态已变化，但知识 current 与验证事实未同步
- 外部信息直接污染正式知识
- 主代理、实施者、reviewer、closer 职责漂移

---

# 1 结构规范

本章只回答“系统由什么组成、每部分负责什么”，不描述一次任务的执行顺序。

## 1.1 知识库分层结构

知识库不是笔记堆放区，而是分层治理系统。

### 1.1.1 `01_Knowledge`

用于存放已审核、可复用、边界清晰、可引用的正式知识，例如：

- 已验证机制
- 稳定设计模式
- 通用流程规范
- 高复用经验总结
- 结构化背景知识

### 1.1.2 `02_Projects`

用于存放与当前项目强绑定的内容，例如：

- 需求拆解
- 设计方案
- 实验记录
- 实现计划
- 调试日志
- 决策记录
- 项目专用经验

### 1.1.3 `03_Inbox`

用于存放待整理、待分类、待审核的内容，例如：

- 网络采集候选
- 临时想法
- 中间总结
- 待确认结论

### 1.1.4 `04_Sources`

用于存放原始外部材料和证据，例如：

- 网页摘录
- 论文摘要
- PDF 阅读卡片
- 厂商文档片段
- 外部证据记录

### 1.1.5 `05_Templates`

用于存放模板、frontmatter 骨架和固定工作流模板，不用于存放正式知识结论。

### 1.1.6 `90_Archive`

用于存放失效内容、子 Vault 碎片、旧索引、历史缓存和不再参与主流程的结构。

### 1.1.7 分层原则

- 正式知识、项目内容、候选内容、原始来源必须严格分离
- 未审核来源不得直接进入 `01_Knowledge/`
- 项目临时记录不得直接提升为正式知识
- 插件缓存、索引和子 Vault 元数据不得混入正文知识

---

## 1.2 三侧职责划分

### 1.2.1 知识库侧职责

知识库侧负责“**知道什么、读取什么、写回哪里**”，本质上是知识治理规则。

知识库侧应回答：

- 当前任务属于什么类型
- 允许读取哪些目录
- 什么内容应写入 `01_Knowledge/`
- 什么内容必须写入 `02_Projects/`
- 什么内容只能先进入 `03_Inbox/` 或 `04_Sources/`
- 哪些结论必须等待审核后才能转正

知识库侧不负责代码实现细节，不负责工程测试指令。

### 1.2.2 代码库侧职责

代码库侧负责“**怎么改、改到哪、如何验证**”，本质上是工程实施规则。

代码库侧应回答：

- Agent 可以改哪些模块
- 哪些目录禁止修改
- 哪些改动必须先有方案依据
- 哪些改动属于高风险，需要停止并确认
- 哪些测试、编译、静态检查必须执行
- 什么情况下只能修 bug，不能顺带重构

代码库侧不负责知识分区和沉淀门槛。

### 1.2.3 board 侧职责

board 侧负责“**代码在哪块板上运行、如何采集执行产物、板端状态如何推进与回流**”，本质上是板端执行与效果验证规则。

board 侧应回答：

- 目标板端是什么，例如哪块智驾芯片板、哪套固件或运行环境
- 通过什么 SSH 入口、部署路径和执行命令完成上板运行
- 运行时需要采集哪些日志、指标、trace、录像或效果产物
- 何时可从 `board_ready / package_deployed / running / artifacts_collected / analyzed` 推进到完成态
- 板端失败、超时、环境异常或效果不达标时如何回流到 repo 侧返工
- 哪些板端日志摘要、效果评估和回写结果必须进入项目区与知识区

board 侧不直接做代码质量裁决，不替代知识分区与知识转正审查。

### 1.2.4 三侧协同关系

知识库侧、代码库侧与 board 侧共同构成三侧约束：

- 知识库侧负责“知道什么、写回哪里”
- 代码库侧负责“怎么改、改到哪、如何验证”
- board 侧负责“在哪里运行、产出什么执行证据、板端状态如何流转”

三者缺一不可。
如果只有 knowledge + repo，而没有 board，Agent 可以形成工程内闭环，但无法形成“上板执行、日志采集、效果验证”的软硬件闭环。
如果只有 board + repo，而没有知识治理规则，Agent 可能完成上板测试，但无法沉淀可复用知识。
如果只有 board + knowledge，而没有工程规则，Agent 可能知道为什么做，也知道写回哪里，但无法安全落地。

### 1.2.5 三侧核心属性

#### 1.2.5.1 knowledge side

- 核心目标：提供受控知识依据，决定写回分区与沉淀门槛
- 主要输入：`allowed_paths`、项目 current、来源材料、板端关联知识范围
- 主要输出：知识依据、实施约束、writeback targets、候选与转正建议
- 权限边界：不直接实施代码，不直接替代 repo review 做板端效果裁决，不直接提升未审内容
- 状态责任：维护 knowledge sync、current 收敛、single-pass recoverability
- 同步关系：接收板端执行约束，为 repo 实施提供依据，并在完成后接收 repo/board 结果写回

#### 1.2.5.2 repo side

- 核心目标：在授权范围内完成实现、修复、验证与独立代码审查
- 主要输入：板端目标、knowledge 计划、repo_scope、verification plan
- 主要输出：diff、验证结果、板端运行命令、repo review 结论、回归风险
- 权限边界：不替代知识沉淀，但负责汇总板端日志与效果评估结论
- 状态责任：推进 `implementation_done`、`board_executed`、`repo_review_done`
- 同步关系：从 knowledge side 获取约束，把构建产物部署到 board side，并把实现事实和板端证据回流给两侧

#### 1.2.5.3 board side

- 核心目标：作为智驾芯片板端执行侧，承接部署、运行、日志产出与效果观察
- 主要输入：构建产物、SSH 目标、部署路径、运行命令、采集路径、超时与安全约束
- 主要输出：板端日志、trace、效果指标、运行状态与失败信号
- 权限边界：不直接修改仓库代码，不独立给出最终质量裁决，不替代知识分区
- 状态责任：维护 `board_ready / package_deployed / running / artifacts_collected / analyzed / failed / completed`
- 同步关系：接收 repo 产物与命令，在板端生成执行证据，再由 repo review 汇总为质量结论

---

## 1.3 规则外置原则

稳定规则不应依赖单次任务 prompt 重复注入，而应外置为长期约束。

### 1.3.1 应外置到知识库/代码库/board 侧 `AGENTS.md` 或等价制度文件的内容

- 知识分区语义
- 可访问范围
- 板端执行合同
- 板端状态映射与回写协议
- 高风险修改边界
- 测试与验证要求
- 禁止事项
- 回写规则
- 正式沉淀门槛

### 1.3.2 不应由单次 prompt 重复定义的内容

- 长期角色职责
- 知识分区规则
- 仓库级风险边界
- 默认验证要求
- 审查优先级体系

单次 prompt 只负责**任务实例化与调度**，不负责重复定义长期制度。

---

# 2 角色规范

本章定义稳定角色如何固化，以及角色之间如何分工。

## 2.1 角色固化原则

稳定角色必须固化为可复用的 agent，而不是在单次任务 prompt 中临时要求模型“扮演某个角色”。

原因包括：

- 角色边界更稳定
- 权限与职责更可审计
- 跨任务复用成本更低
- 降低 prompt 过重导致的职责混叠
- 提高 reviewer 等角色的独立性

控制层与执行层应区分建模：

- 控制层：`workflow-orchestrator`
- 执行层：`knowledge-planner`、`source-ingestor`、`repo-coder`、`repo-reviewer`、`knowledge-closer` 与按需扩展角色

其中 `workflow-orchestrator` 默认表示**主代理在三侧闭环任务中的 orchestration 职责模式**，默认由 Codex 主代理承担，而不是默认显式启动的普通子代理。

至少建议固化以下执行层角色：

- `knowledge-planner`
- `repo-coder`
- `repo-reviewer`
- `knowledge-closer`
- `source-ingestor`（按需）

### 2.1.1 角色解析优先级

角色来源出现并存时，默认优先级必须为：

1. 系统 / 开发者硬约束
2. `.codex/agents/*.toml` 中的稳定角色骨架
3. 角色契约规范与运行规范中的长期制度
4. 单次任务 prompt 中的本轮 overlay

补充约束：

- 单次任务 prompt 只能实例化任务，不应重写长期角色职责
- 若本轮 overlay 与稳定角色骨架冲突，默认以稳定角色骨架与规范为准
- 只有在本轮存在明确特例时，才允许覆盖任务级输入、路径、验证等级与调用顺序
- 若确需偏离稳定角色基线，必须显式记录 `role_override_reason`，并进入 `run_log / audit_log`

---

## 2.2 角色定义

### 2.2.1 `workflow-orchestrator`

定位：

- 默认由 Codex 主代理承担的控制层职责模式
- 不应默认列入普通子代理调用链
- 只有在特殊复杂任务且系统明确支持多层调度代理时，才允许显式启动独立 orchestrator 子代理

职责：

- 维护状态机
- 决定角色调用顺序
- 裁剪交接包
- 控制 reviewer 独立性
- 控制返工轮次
- 决定 `stop / retry / replan / escalate / confirm`
- 汇总最终输出
- 维护 `run_log / audit_log`

约束：

- 不直接修改代码
- 不直接做质量裁决
- 不绕过 review 进入 writeback
- 不把未审内容直接提升为正式知识

### 2.2.2 `knowledge-planner`

职责：

- 读取知识库侧规则
- 解析板端执行目标或显式判断本轮是否为“无板端执行”
- 识别 `primary_type` 与 `task_modifiers`
- 确定允许访问范围
- 检索项目区与相关正式知识
- 对 `incident_investigation` 先形成调查计划、证据缺口分析、分类候选与路由前提；对 plan-first 任务再形成实施计划、验证计划与建议回写路径
- 输出验证等级与非目标项

约束：

- 不直接修改代码
- 不直接创建正式知识条目
- 不直接写入未审核外部信息到 `01_Knowledge/`

其主要产出是：

- 任务判断
- 板端执行判断
- 知识依据
- 约束与风险
- 调查计划或实施计划
- 板端执行与验证建议
- 板端映射建议
- 建议回写路径
- `verification_tier`

### 2.2.3 `repo-coder`

职责：

- 读取代码库侧规则
- 按计划在允许范围内实施修改
- 执行最小必要验证
- 在需要时通过 SSH 或等价通道完成上板部署与运行
- 记录修改文件、修改原因和方案外优化

约束：

- 不扩大任务边界
- 不为了减少改动而破坏既有设计契约、模块职责或接口边界
- 不进行无依据的跨模块重构
- 不负责知识沉淀归类

补充原则：

- `repo-coder` 应优先满足设计规范、职责边界和兼容性要求
- “最小修改”是次级原则，只能在满足上述约束后再优化改动规模
- 若下游变动导致问题，应优先在下游适配层、转换层或调用侧修复，而不是反向污染上游接口
- 若要改变上游公共接口语义，不应被视为“最小修复”，而应升级为设计变更确认

其主要产出是：

- 实际改动文件
- 改动原因
- 验证结果
- 板端执行记录
- 方案外优化记录
- 未覆盖风险
- 对 reviewer 发现的返工实现

### 2.2.4 `repo-reviewer`

职责：

- 基于任务目标、计划、diff、测试输出进行独立审查
- 判断改动是否满足目标与约束
- 识别 blocker / major / minor 风险
- 判断是否可以进入闭环回写阶段
- 基于板端日志、指标和效果产物做最终质量判断

约束：

- 不直接修改代码
- 不把“建议改进”与“必须修复”混为一谈
- 不负责知识库分区写入

其主要产出是：

- 分层审查结论
- 风险分级
- 未覆盖边界
- 回归缺口
- 板端效果评估结论
- 是否需要返工以及返工建议

### 2.2.5 `knowledge-closer`

职责：

- 根据任务结果进行分区回写
- 更新 `02_Projects/`
- 输出 board 回写摘要与状态同步结果
- 将可复用结论标记为 `01_Knowledge/` 候选
- 将未审核内容放入 `03_Inbox/` 或 `04_Sources/`

约束：

- 不负责代码实现
- 不负责代码审查裁决
- 不将未经验证的内容直接提升为正式知识

其主要产出是：

- 项目区更新
- board 回写摘要
- 正式知识候选
- 候选/来源归档
- 闭环完成记录

### 2.2.6 `source-ingestor`

职责：

- 在任务允许联网且本地知识不足时采集外部材料
- 对外部内容做来源级收集与初步整理
- 将结果写入候选区或来源区

约束：

- 不直接写入 `01_Knowledge/`
- 不替代正式知识审核
- 不自行完成项目结论沉淀

其主要产出是：

- 外部来源记录
- 待审核候选
- 来源摘要与链接关系

---

## 2.3 扩展角色与启用条件

扩展角色用于补齐默认链路中的高风险、高复杂度或高审计需求场景，不默认进入所有任务的调度链。

### 2.3.1 `verification-manager`

何时启用：

- 验证矩阵复杂
- 存在多层验证依赖
- 高风险任务需要统一编排验证等级与证据

不启用时由谁兜底：

- 默认由 `knowledge-planner` 输出验证计划
- `workflow-orchestrator` 负责检查是否满足门禁

边界：

- 负责验证设计与覆盖判断
- 不负责修改代码
- 不替代 `repo-reviewer` 做最终质量裁决

输入输出契约：

- 输入：任务目标、实施计划、风险边界、已执行验证结果
- 输出：验证矩阵、required / optional / unavailable 分类、验证缺口、是否构成 blocker

是否进入默认调度链：

- 否

### 2.3.2 `functional-reviewer`

何时启用：

- 任务核心是功能符合度审核
- 需要对规范与行为证据做逐项比对
- 需要对规范要求与板端效果证据做逐项比对

不启用时由谁兜底：

- 默认由 `repo-reviewer` 承担轻量功能符合度检查

边界：

- 负责规范符合度与行为证据审查
- 不直接修改代码
- 不替代 `knowledge-closer` 做知识回写
- 不替代 `repo-reviewer` 做最终质量裁决

输入输出契约：

- 输入：规范文本、验收条目、代码或运行证据、必要上下文
- 输出：`acceptance_items`、`compliance_matrix`、`evidence_used`、`evidence_gaps`、`norm_conflicts`、`review_conclusion`

是否进入默认调度链：

- 否

### 2.3.3 `failure-analyst`

何时启用：

- `primary_type = incident_investigation`
- 复杂 `primary_type = bug_fix`
- 根因假设存在多分支竞争
- 多轮返工后仍不能稳定收敛

不启用时由谁兜底：

- 默认由 `knowledge-planner` 做根因假设整理

边界：

- 负责故障模式拆解、根因路径收敛与最小验证路径设计
- 在 board-first 模式下负责区分根因、表象、伴随噪声与环境问题
- 不直接改代码
- 不做最终审查裁决

输入输出契约：

- 输入：预期行为或设计预期状态、实际行为或观测现象、日志、trace、指标、复现路径或触发条件、相关代码线索
- 输出：故障树、根因假设、证据优先级、最小验证路径、分类建议、probe 优先级、是否需要 replan

是否进入默认调度链：

- 否

### 2.3.4 `knowledge-auditor`

何时启用：

- 任务涉及正式知识提升审查
- 候选内容需要判断是否具备跨项目复用价值
- 需要补充知识边界、证据与风险说明

不启用时由谁兜底：

- 默认由 `knowledge-closer` 只生成候选与转正建议
- 人工审核负责最终入库

边界：

- 负责正式知识提升审查
- 不负责采集原始来源
- 不直接替代人工审核授权

输入输出契约：

- 输入：候选条目、来源、适用边界、风险、来源任务、证据
- 输出：提升建议、复用价值判断、边界补全建议、是否仍应停留在候选区

是否进入默认调度链：

- 否

## 2.4 角色独立性原则

角色之间的独立性不是绝对隔离，而是输入与职责的受控分离。

### 2.4.1 planner 与 coder

两者共享任务目标和计划是有益的，因为 planner 的职责就是为 coder 提供受约束实施路径。

### 2.4.2 coder 与 reviewer

为降低认知污染，reviewer 的输入应尽量裁剪为：

- 用户目标
- 计划中的验收标准
- diff
- 测试结果
- 必要代码上下文

不应默认让 reviewer 继承 coder 的完整自然语言叙述。

若 reviewer 发现的问题需要代码改动，默认应回到原 `repo-coder` 执行返工，而不是让主调度 agent 直接接管实现。

原因包括：

- 原 coder 保留了实现期的局部代码上下文与验证经验
- 板端执行失败或效果不达标后的返工也应默认回到原 `repo-coder`，而不是由主代理直接接管实现
- 主调度 agent 应维持编排职责，避免角色漂移
- reviewer 的独立性并不要求切换修复责任人，而是要求独立给出审查结论
- 返工责任回到原 coder，更容易形成“实现 -> 审查 -> 返工 -> 重审”的稳定闭环

只有在以下情况，才应由非原 coder 接手修复：

- 原 coder 会话不可恢复
- 原 coder 连续返工仍未收敛
- 返工内容已超出原授权范围并需要重新规划
- 问题本质上属于调度、知识回写或范围控制错误，而不是代码实现错误

### 2.4.3 reviewer 与 closer

reviewer 负责质量判定，closer 负责知识归档，两者不应混为同一职责，否则容易出现“未通过审查却提前沉淀”的状态错位。

### 2.4.4 主代理与 `workflow-orchestrator`

主代理默认承担 `workflow-orchestrator` 职责，但这不意味着主代理可吸收执行层角色的工作。

控制层职责与执行层职责应保持以下边界：

- 主代理负责编排，不负责实现
- 主代理负责状态推进，不负责质量裁决
- 主代理负责记录与阻断，不负责绕过门禁
- 主代理负责是否调用扩展角色，不负责把扩展角色永固为默认链

---

# 3 能力规范

Skill 是执行闭环时的能力承载，不等同于流程本身。  
流程决定先后，角色决定谁负责，Skill 决定 Agent 是否具备执行能力。

为了稳定执行闭环流程，建议至少具备以下能力模块。

## 3.1 `knowledge-retrieval`

在允许范围内检索知识库，优先读取：

1. 当前项目区
2. 相关正式知识区
3. 被允许访问的来源区

## 3.2 `solution-planning`

将已检索到的知识整理为可执行方案，明确：

- 目标
- 约束
- 假设
- 风险
- 拟修改模块
- 验证路径
- 回写建议

## 3.3 `repo-implementation`

在代码库中按方案实施，执行：

- 新增实现
- 缺陷修复
- 小范围重构
- 低风险优化

## 3.4 `validation-and-regression`

对修改执行验证，例如：

- 单元测试
- 集成测试
- 编译验证
- 静态检查
- 回归检查

## 3.5 `knowledge-close-loop`

将结果回写知识库，包括：

- 项目区更新
- 决策记录
- 可复用结论候选
- 风险与未决项记录

## 3.6 `source-ingestion`

当本地知识不足且任务允许联网时：

- 外部信息先进入 `03_Inbox/` 或 `04_Sources/`
- 审核后再决定是否提升为正式知识

## 3.7 `verification-tiering`

为不同风险等级任务提供显式验证等级，至少应支持：

- `V0`：只要求基本可读性或知识整理核对
- `V1`：要求最小功能验证
- `V2`：要求受影响范围回归验证
- `V3`：要求高风险、多维验证与证据闭环

验证等级必须在计划阶段进入系统，而不是在 review 阶段事后补写。

## 3.8 `audit-logging`

闭环系统应维护可审计运行记录，至少覆盖：

- 谁承担了控制层职责
- 调用了哪些执行角色
- 经过了哪些状态跃迁
- 每轮返工由谁负责
- 哪些 blocker 导致停止、重试或重规划
- 哪些候选进入了待审核区、哪些建议提升为正式知识

---

# 4 状态规范

为避免流程只停留在描述层，闭环执行过程中应显式维护状态对象，并把关键状态从“记录容器”升级为“状态门禁对象”。

## 4.1 `task_state`

记录：

- 任务类型
- 用户目标
- 允许访问范围
- 可修改范围
- 风险边界
- `verification_tier`

## 4.2 `plan_state`

记录：

- 知识依据
- 目标拆解
- 实施步骤
- 验收标准
- 验证计划
- 回写建议
- 非目标项
- 未解决不确定项

### 4.2.1 `plan_ready` 门禁

进入条件：

- 已识别 `primary_type`
- 已识别 `task_modifiers`
- 已明确 `allowed_paths`
- 若涉及代码，已明确 `repo_scope`
- 已给出 `implementation_plan`
- 已给出 `verification_plan`
- 已给出 `non_goals`
- 已给出 `open_uncertainties`

阻断条件：

- 主类型与修饰属性语义混杂
- 允许范围不清
- 涉及代码但未定义代码作用域
- 未定义验证等级或验证集合
- 非目标项缺失导致 scope 无法约束

## 4.3 `implementation_state`

记录：

- 实际改动文件
- 改动说明
- 方案外优化
- 验证结果
- 未覆盖项
- 决策偏差

### 4.3.1 `implementation_done` 门禁

进入条件：

- 已记录 `files_changed` 或明确无代码改动
- 已记录 `commands_run`
- 已记录 `verification_results`
- 已记录 `decision_deltas`
- 已记录 `open_risks`
- 如存在，已记录 `optional_optimizations`

阻断条件：

- 改动文件不清
- 验证结果缺失或无法解释
- 实际实现偏离计划但未记录
- 风险未展开
- 方案外扩张未说明

## 4.4 `review_state`

记录：

- 审查结论
- blocker / major / minor
- 未覆盖风险
- 是否允许进入回写
- 返工建议

### 4.4.1 `review_done` 门禁

进入条件：

- 已记录 `findings`
- 已记录 `finding_severity`
- 已记录 `scope_assessment`
- 已记录 `regression_risks`
- 已记录 `review_conclusion`
- 已记录 `next_action`
- 已记录 `fix_owner`

阻断条件：

- 缺少验证覆盖判断
- 缺少范围合规判断
- 只有结论没有发现依据
- reviewer 独立性被破坏
- 返工责任不清

## 4.5 `closure_state`

记录：

- 写回分区
- 正式知识候选
- 待审核候选
- 原始来源记录
- 未决问题

### 4.5.1 `writeback_done` 门禁

进入条件：

- 已记录 `files_written`
- 已记录 `target_zone`
- 已记录 `candidate_created / promoted_to_knowledge / source_notes_created`
- 已记录 `pending_items`
- 已记录 `residual_risks`

阻断条件：

- 回写分区不清
- 候选与正式知识混淆
- 未审核内容拟进入正式知识区
- 缺少来源、边界或残余风险

---

# 5 执行规范

本章只回答“一次任务如何推进”，执行顺序必须服从前述结构规范、角色规范与状态规范。

## 5.1 标准闭环流程

一次任务建议按以下顺序推进：

1. 读取知识库侧 `AGENTS.md`
2. 识别 `primary_type`、`task_modifiers` 与允许访问范围
3. 检索当前项目区和相关正式知识
4. 生成 `task_state` 与 `plan_state`
5. 读取代码库侧 `AGENTS.md`
6. 在代码库实施方案
7. 对方案外优化做受控判断
8. 执行测试、验证和回归检查
9. 生成 `implementation_state`
10. 对结果执行独立审查，生成 `review_state`
11. 若审查发现需要代码改动，按裁剪后的审查结论将任务返还原 `repo-coder` 进行返工
12. 对返工结果重新执行必要验证，并再次进入独立审查
13. 审查通过后，将项目结果写回 `02_Projects/`
14. 将可复用结论标记为 `01_Knowledge/` 候选
15. 将外部材料或未审核内容写入 `03_Inbox/` 或 `04_Sources/`
16. 生成 `closure_state` 并输出闭环摘要

### 5.1.1 审查返工闭环原则

审查之后若需要继续修改代码，`workflow-orchestrator` 默认只负责：

- 保留状态对象
- 裁剪 reviewer 输出
- 把返工要求交还给原 `repo-coder`
- 控制是否进入下一轮独立审查

`workflow-orchestrator` 默认不应直接吸收 reviewer 发现并自己修改代码，否则会同时破坏以下边界：

- 调度者与实施者边界
- coder 与 reviewer 的职责边界
- 审查发现与返工责任的可追踪性

推荐的返工交接包应包含：

- `review_conclusion`
- `findings`
- `finding_severity`
- `next_action`
- `affected_files`
- `verification_gaps`

若返工轮次超过预设上限，或多轮后仍无法收敛，应升级为重新规划或人工确认，而不是无限循环。

## 5.2 方案外优化规则

Agent 可以实现方案中未明确列出的优化项，但必须满足以下条件。

### 5.2.1 允许的优化

- 不改变核心业务目标
- 不扩大修改边界
- 不引入新的架构依赖
- 能清楚说明优化动机
- 能通过测试或验证证明无回归

典型例子：

- 局部重复代码消除
- 明显的边界检查补全
- 小范围错误处理完善
- 与当前变更强相关的命名、注释、结构整理

### 5.2.2 不允许的优化

- 无需求依据的跨模块重构
- 为“更优雅”而重写稳定逻辑
- 未经确认的大规模性能改造
- 影响接口语义的顺手修改
- 无验证支撑的行为调整

### 5.2.3 记录要求

凡是实际实施的方案外优化，都应记录：

- 为什么做
- 改了什么
- 影响范围
- 如何验证
- 是否应沉淀为通用知识候选

## 5.3 回写与沉淀规则

任务完成后，必须根据内容性质分区回写。

### 5.3.1 写入 `02_Projects`

适用于：

- 当前项目方案更新
- 实现记录
- 调试结论
- 决策说明
- 当前项目专用经验
- 回归与验证结果

### 5.3.2 标记为 `01_Knowledge` 候选

适用于：

- 已验证、可复用的机制
- 稳定设计模式
- 通用闭环工作流
- 跨项目经验总结

注意：  
这里首先应是“候选”而不是默认直接转正，除非已有明确审核流程保证其满足正式知识门槛。

### 5.3.3 知识沉淀单元类型

仅允许以下类型进入正式知识候选：

- `failure_mode`
- `design_pattern`
- `workflow_pattern`
- `verification_pattern`
- `integration_constraint`
- `decision_heuristic`

每个候选必须明确：

- 类型
- 复用场景
- 不适用场景
- 来源任务
- 证据
- 为什么不只是项目特例

### 5.3.4 写入 `03_Inbox`

适用于：

- 尚未审核的总结
- 尚未分类的中间结果
- 待确认的外部信息候选
- 未完成验证的经验结论

### 5.3.5 写入 `04_Sources`

适用于：

- 原始网页摘录
- 文献卡片
- 厂商文档片段
- 外部证据材料

### 5.3.6 正式沉淀门槛

只有满足以下条件，内容才可进入 `01_Knowledge`：

- 已验证
- 有复用价值
- 边界清晰
- 风险明确
- 不是纯项目特例
- 来源可追溯

---

# 6 调度规范

本章定义任务 prompt 在系统中的职责边界。

## 6.1 prompt 的职责

任务 prompt 只负责：

- 指定 `primary_type`
- 指定 `task_modifiers`
- 提供本轮任务输入
- 指定调用顺序
- 指定本轮是否需要确认
- 指定输出要求与停止条件

## 6.2 prompt 不负责的内容

任务 prompt 不应重复承担以下职责：

- 长期角色定义
- 知识分区规则定义
- 仓库级测试规范定义
- 高风险边界长期定义
- 正式知识门槛定义

这些内容应外置到：

- `AGENTS.md`
- agent 配置
- skills
- 上位规范文档

## 6.3 轻量调度原则

任务 prompt 应尽量轻量，只描述：

- 本轮任务目标
- 本轮输入
- 本轮允许范围
- 是否允许联网
- 是否需要确认
- 本轮输出要求

不应用单次 prompt 重写闭环制度。

---

# 7 模板落位原则

上位规范不直接承载运行型模板文本。

推荐落位如下：

- 原则、职责、门禁与沉淀规则：留在本文档
- 状态机、调用矩阵、返工升级规则、运行型 prompt 模板：写入运行规范
- 文件树、toml 骨架、frontmatter 字段、日志模板骨架：写入文件结构规范

这样可以避免：

- 上位规范被运行细节淹没
- 运行规范失去制度依据
- 文件结构规范混入调度逻辑

---

# 8 风险与失败模式

## 8.1 项目内容误入正式知识

若未判断复用价值、边界和风险，项目经验可能被误提升为正式知识。

## 8.2 未审核外部信息直接入库

若 `source-ingestor` 或主代理绕过候选区，外部信息会污染正式知识层。

## 8.3 Agent 越权读取或修改

若允许范围未显式限定，任何“默认可读可写”的假设都可能导致越权。

## 8.4 代码实现与知识方案脱节

若 planner 输出无法约束 coder，或 coder 未记录偏差，方案与实现会分裂。

## 8.5 方案外优化未记录

若未记录方案外优化，后续 review 与知识回写会缺失上下文。

## 8.6 只改代码不回写知识库

若没有 closure 阶段，闭环会退化成一次性执行。

## 8.7 用复杂 prompt 代替角色固化

若长期依赖一次性 prompt 临时指定职责，系统将失去稳定边界和可审计性。

## 8.8 状态跃迁前提缺失

若未满足关键状态的进入条件就继续推进，闭环可能出现“没有计划就实施”“没有审查就回写”的状态错位。

## 8.9 验证等级不足

若任务风险高但验证等级仍停留在低层，review 结论会建立在不充分证据上。

## 8.10 `primary_type / task_modifiers` 语义混杂

若同一任务同时包含实现、审计、知识整理和网络研究而没有拆分主类型与修饰属性，planner 很难形成可执行计划。

## 8.11 `run_log` 缺失导致无法审计

若无法回溯角色调用、返工轮次和 blocker，系统将无法总结失败模式或优化运行策略。

## 8.12 主代理与 orchestration 职责不清导致角色漂移

若主代理一边调度、一边实现、一边审查，系统会同时失去独立性、可追踪性和门禁能力。

---

# 9 最小执行原则

若任务规模较小，系统仍应尽量保留以下最小闭环：

1. 明确 `primary_type`、`task_modifiers` 与允许范围
2. 至少形成轻量计划
3. 执行最小必要验证
4. 经独立审查或等价独立检查后再回写
5. 把项目记录与知识候选分区处理

即使是轻量任务，也不应跳过：

- 允许范围确认
- 验证等级确认
- reviewer 独立性判断
- 候选与正式知识的分离

---

# 10 文档收敛与当前态治理

三侧闭环不仅要记录“发生过什么”，还要维护“现在系统是什么”以及“board 当前状态与验收事实是什么”。

## 10.1 文档角色分层

项目区与知识区中的设计/实现文档必须按以下角色分层：

- `baseline`：历史起点文档，记录最初方案或初始设计，只保留历史起点职责
- `current`：当前有效状态文档的总称，必须通过 `current_kind` 区分 `overview / design / spec / implementation / validation / interface`
- `delta`：增量问题、修复、优化、审核与验证记录，只负责记录变化与证据
- `adr` / `decision_ledger`：关键设计决策、接口取舍、边界变化的决策文档
- `archive`：明确退出主检索路径的历史文档

默认回写策略必须为“更新 `current` 并压缩历史”，而不是“新增 `delta` 记录变化”。
除非满足本章定义的 `delta_only` 例外条件，否则不得只写 `delta` 而不更新相关 `current`。

### 10.1.1 current 与 modification-record 分工

项目演化中，`current` 与 `delta` 的真正分工不是“一个写现在、一个写变化”这么宽泛，而应进一步收紧为：

- `current` 只承载当前态与稳定语义
- `modification record` 只承载事件闭环、决策动机、验证边界、追溯索引与未闭环风险

其中 `modification record` 仍可使用 `doc_role: delta`，但语义上必须满足以下约束：

- 它记录的是某次修复、优化、审核、调查或验证事件
- 它必须说明为什么会发生这次修改或审查，而不仅是“改了什么”
- 它必须说明该事件影响哪些 current owner，而不是自己长期承担 current 职责
- 它必须说明验证边界、review 结论和残余风险，而不是只给 patch 结果

工程上应优先保留四类信息：

1. 当前态语义
2. 机制规则与约束
3. 决策动机与修复闭环
4. 引用与追溯索引

工程上应避免五类信息：

1. 代码镜像
2. 配置镜像
3. 版本流水账
4. patch 过程细节
5. 临时噪声

解释：

- `current` 可以保留最小必要的代码入口、配置契约和实现映射，但不得复制代码或配置正文
- `modification record` 可以保留关键变更点与受影响路径，但不得退化成 patch 回放
- 代码难以低成本恢复、但会持续影响实现、审查、排障、文档恢复与追溯的信息，才应进入 `current` 或 `modification record`

### 10.1.2 modification-record 类型

`delta` 不应再被当作单一“增量文档”桶使用。项目侧至少应区分以下 modification-record 类型：

- `fix_record`：缺陷修复与闭环
- `optimization_record`：受控优化与收益/风险评估
- `audit_record`：功能符合度或独立审查
- `investigation_record`：调查、分流、证据裁剪与 route 决策
- `validation_record`：独立验证、复核与样本级结论

若主题持续演化，应允许这些记录并存；但它们共同的硬约束不变：

- 不能替代 current 解释“系统现在是什么”
- 必须指向被影响的 current 文档 owner
- 必须可被后续 `tracking_validation_current` 或同类验证 current 吸收

## 10.2 状态标记与结构化字段

文档除原有 `status` 外，必须增加或等价表达以下结构化字段：

- `doc_role`：`baseline / current / delta / adr / archive`
- `truth_role`：`current / history / evidence`
- `lifecycle_state`
- `default_entry`
- `sync_required_when`
- `retrieval_priority`
- `supersedes`
- `merged_into`
- `current_replacement`
- `related_code`
- `scope`

其中 `lifecycle_state` 的允许值为：

- `active`
- `partially_active`
- `superseded`
- `pending_merge`
- `merged`
- `archived`

并应满足以下硬约束：

- `current` 默认使用 `active`，退出默认入口时改为 `partially_active` 或 `superseded`
- `delta` 只允许使用 `pending_merge` 或 `merged`，禁止长期 `active delta`
- `baseline` 只允许使用 `partially_active / superseded / archived`
- `archive` 只允许使用 `archived`
- `default_entry = true` 的文档必须同时具备 `retrieval_priority = current`
- `baseline / delta / archive` 默认 `default_entry = false`

## 10.3 current 真相源原则

`current` 文档组的目标不是“给出几个当前文档入口”，而是以**最小 current 文档组单次恢复当前系统的设计、规范、实现事实、验证边界与已知缺口**。

它必须共同回答以下六个问题：

1. 现在系统目标和边界是什么
2. 现在系统按什么设计组织
3. 现在系统按什么规范实现
4. 现在代码事实是什么
5. 现在已证明和未证明什么
6. 当前已知缺口与风险是什么

若 coder / reviewer / verifier 仍需默认依赖 baseline、两篇及以上 delta、或大段代码阅读才能恢复关键当前态，则视为 `current` 文档组粒度不足，`single_pass_recoverable = false`。

### 10.3.1 current_kind 强职责与排他边界

- `overview_current`
  - 必须承担：唯一默认入口声明、默认恢复顺序、默认实现输入链、`default_recovery_bundle`、历史文档角色映射、当前真相源集合声明、当前入口排他声明
  - 不得承担：机制级规范细节主体、代码逐层实现映射主体、具体验证结论主体
- `design_current`
  - 必须承担：当前设计目标与边界、当前模块分层与数据流、当前关键状态/生命周期/对象耦合的设计组织、当前设计约束、非目标项、当前仍开放的设计级问题
  - 不得承担：代码路径级事实主体、完整验证证据主体、逐项配置语义主体
- `spec_current`
  - 必须承担：当前版本必须遵守的机制级规范事实，以及在相应机制存在时的 `object model / required behaviors / core state variables / interface contracts / calculation rules / type or attribute computation / motion or filter model / state or transition rules / config contract / verification contract`
  - 不得承担：逐行代码细节、完整数学推导全集、纯实验记录、纯历史叙事
- `implementation_current`
  - 必须承担：当前代码入口路径、关键容器/结构体/类/函数映射、design/spec 到代码的映射关系、当前实现中的关键约束、实际分支、兼容层，以及当前代码事实与规范间的已知不完全闭合点
  - 不得承担：规范性行为定义主体、验证结论主体
- `validation_current`
  - 必须承担：当前已持有证据、当前证据缺口、当前能证明什么、当前不能证明什么、当前 review / verification 结论、下一轮必须补的验证
  - 不得承担：用猜测替代证据、用“待验证”替代规范定义、承接设计或实现主体职责

### 10.3.2 current 组互补关系

- `overview / design / spec / implementation / validation` 不是并列可选说明文档，而是恢复当前态的互补组
- 若某项关键当前事实既不在 `design/spec`，也不在 `implementation/validation` 中，则视为 current 组缺口
- 若某项事实被写入错误 `current_kind`，导致默认恢复链不能稳定裁剪，也视为收敛失败
- 设计目标、结构边界、机制约束、代码落点、证据边界必须各归其位，不能通过“混写一篇 current”规避职责分层
- evidence 应优先下沉到 `validation_current`、`delta` 或来源文档；历史叙事应留在 `delta / adr / archive`；只有当前稳定真相才上收为 current 主体

### 10.3.3 overview_current 额外门禁

- 若同一持续演化主题存在 2 份及以上 `current` 文档，则必须存在 `overview_current`
- `overview_current` 必须声明：
  - `Current Scope`
  - `Current Truth`
  - `Current Boundaries`
  - `Default Recovery Order`
  - `Default Implementation Input Chain`
  - `Default Recovery Bundle`
  - `Current Document Roles`
  - `Current Recovery Rule`
  - `Known Gaps`
  - `Historical Mapping`
  - `Current Sync Rule`
- 若多份 current 并存，但 `overview_current` 未能排除 baseline / interfaces / delta 的默认入口地位，则 `default_entry` 校验失败
- 若 `default_recovery_bundle` 不能支撑单次恢复当前态，则 `overview_current` 粒度不足

### 10.3.4 样例提醒

Tracking 类主题暴露的典型问题不是“只缺一篇更细的 `spec_current`”，而是 current 组整体仍可能无法唯一恢复 body / face / hand 的设计边界、规范事实、代码映射和证据边界。
因此规范必须整体收紧 `overview / design / spec / implementation / validation`，而不是只补单篇规范。

## 10.4 默认实现输入链

若任务目标是“按照规范实现代码”，默认实现输入链必须为：

1. `design_current`
2. `spec_current`
3. `implementation_current`
4. `validation_current`

其中：

- `design_current` 提供设计边界、对象/模块组织、关键状态与非目标项
- `spec_current` 提供必须满足的机制级规范事实；若存在状态、计算、类型、滤波、配置或验证机制，对应约束不得缺位
- `implementation_current` 提供当前代码事实、关键实现载体以及 design/spec 到代码的映射，帮助识别应改哪里
- `validation_current` 提供当前证据边界、已证实/未证实结论与下一轮验证要求，帮助确定验证计划

`baseline` 与 `delta` 不得作为 `implementation / bug_fix / optimization` 类任务的默认实现入口，只能在追溯来源、证据或历史决策时按需回读。
若主题已存在 `spec_current`，coder 不得绕过 `spec_current` 直接基于 baseline 或 delta 实施。
若 coder 仍需依赖 baseline、两篇及以上 delta、或大段代码阅读才能恢复行为约束、状态语义、关键计算链、滤波模型、类型计算或配置语义，则 `spec_current` 粒度不足。

## 10.5 强制收敛规则与 `delta_only` 例外

默认情况下，以下变化必须同步更新 `current`：

- 当前设计事实发生变化
- 当前规范事实发生变化
- 当前实现事实发生变化
- 当前验证边界发生变化
- 默认恢复顺序发生变化
- 默认实现入口发生变化
- 当前推荐做法、当前有效限制或当前风险表达发生变化

`delta_only` 只在同时满足以下条件时允许：

- 变更仅提供纯审计证据、纯运行记录或纯历史链路补充
- 不改变设计事实、规范事实、实现事实、验证边界
- 不改变默认恢复顺序、默认实现入口和 `default_recovery_bundle`
- 现有 current 已能单次恢复当前态
- 已显式记录 `why_delta_only_allowed`

若不满足上述任一条件，则 `delta_only` 不成立，必须改为 `current_patch`、`current_rewrite` 或 `adr_only`。

## 10.6 delta 生命周期与数量门禁

`delta` 的生命周期必须遵守以下规则：

- 新增 delta 时，`lifecycle_state` 必须为 `pending_merge`
- delta 内容被吸收到 current 或 adr 后，必须改为 `merged`
- 不允许长期保留 `active delta`

数量门禁：

- 同一主题新增第 2 篇 `pending_merge` delta 时，下一轮 writeback 必须优先执行压缩，不得继续只追加记录
- 同一主题已有 3 篇 delta 时，禁止新增第 4 篇 delta，必须先重写或重整 current
- 若 reviewer 或 knowledge-auditor 判定 delta 已污染当前态检索，则即使数量未到阈值，也必须优先压缩

## 10.7 baseline / adr / archive 规则

- `baseline` 只保留原始设计 / 实现起点，不接受滚动式正文续写
- `baseline` 只能更新 frontmatter、替代关系、状态说明和引用入口说明
- `baseline` 不得继续承载 implementation / bug_fix / optimization 类任务的默认入口
- `adr / decision_ledger` 用于承接仍需独立保留的决策，而不是替代 current 承担当前态说明
- `archive` 只承担审计价值，不参与默认检索和默认实现输入链

## 10.8 knowledge_sync_check 强制决议

当以下对象发生变化时，闭环必须显式执行 `knowledge_sync_check`：

- 代码实现策略
- 状态机或生命周期
- 对外接口或导出契约
- 行为约束、容错规则、模块边界
- 关键设计决策
- 默认恢复顺序
- 默认实现输入链

`knowledge_sync_check` 不得只写“已检查”，必须显式产出：

- `sync_mode: current_rewrite | current_patch | delta_only | adr_only`
- `why_delta_only_allowed`
- `current_files_must_update`
- `history_files_to_mark`

检查问题至少包括：

1. 是否必须同步更新 `current`
2. 是否必须新增或更新 `adr / decision_ledger`
3. 既有 `delta` 是否应转为 `merged`
4. baseline 或旧 current 是否应改为 `superseded`
5. `default_entry` 与 `retrieval_priority` 是否需要调整
6. `overview / design / spec / implementation / validation` 是否仍承担正确职责
7. 是否存在关键事实只留在 baseline、delta 或代码中
8. `default_recovery_bundle` 是否仍足以支撑单次恢复
9. 哪些信息应上收、下沉或只保留为 evidence

若答案不明确，不得默认跳过知识同步。

## 10.9 检索优先级、single-pass recoverability 与回写门禁

默认检索优先级从高到低必须为：

1. `overview_current / design_current / spec_current`
2. `implementation_current / validation_current`
3. `pending_merge delta`
4. `adr / decision_ledger`
5. `merged delta`
6. `superseded baseline / archive`

若检索系统或人工入口不能表达上述优先级，必须至少通过文件命名、目录组织和状态头提示降低历史文档误命中概率。

`single_pass_recoverable = true` 仅在同时满足以下条件时成立：

1. `overview_current` 可单次确定默认入口、默认恢复顺序、默认实现输入链和 current 真相源集合
2. `design_current` 可单次恢复当前设计目标、边界、主流程和关键机制组织
3. `spec_current` 可单次恢复当前版本必须遵守的机制级规范事实
4. `implementation_current` 可单次恢复主要代码入口、关键实现载体与规范映射
5. `validation_current` 可单次恢复当前已证实/未证实边界
6. baseline 和 delta 仅用于追溯来源，而不是补 current 主体缺口
7. 关键状态变量、关键计算口径、关键接口事实、关键验证缺口不得只存在于代码或 delta 中

补充硬规则：

- 若 `design_current` 只写高层图景，不能支撑 `spec_current` 的机制落点，则视为粒度不足
- 若 `implementation_current` 只列文件路径和函数名，不能解释 design/spec 落在哪些代码载体上，则视为粒度不足
- 若 `validation_current` 只能写“待验证”，却不能明确哪些结论已证明、哪些未证明、缺什么证据，则视为粒度不足
- 若某个当前风险在 `validation_current` 中不可判定，则视为验证边界未收敛
- 若 `overview_current` 未排除 baseline、interfaces 或 delta 的默认入口地位，则 `default_entry` 校验失败
- 若 `spec_current` 只能写“应该怎么做”，不能写清“按什么机制和什么约束去做”，则视为粒度不足
- 若 coder / reviewer / verifier 仍需默认回读 baseline、两篇及以上 delta 或大段代码才能补齐关键当前态，则必须判定 `single_pass_recoverable = false`

对项目区和知识区的 writeback，除原有来源/审查门槛外，还必须同时满足：

- 默认回写策略已执行为“更新 current 并压缩历史”，或已给出合法 `delta_only` 举证
- `single_pass_recoverable = true`
- 默认实现输入链已经从 baseline/delta 切换到 `design_current + spec_current`
- 需要更新的 current 已更新
- 历史文档已补齐 `merged_into / supersedes / lifecycle_state`
- `default_entry` 已校验

未通过上述检查时，writeback 只算记录完成，不算闭环完成。

---

# 11 结论

Agent 三侧闭环规范的关键，不是增加多少角色，而是把控制层与执行层分开，把 board 入口、repo 实施、board 验收、知识回写和审计放入同一套受控系统。

在该体系下：

- `workflow-orchestrator` 默认是主代理的职责模式，而不是默认显式子代理
- 执行层角色负责规划、实现、审查、采集与回写
- 扩展角色只在复杂场景按条件启用
- 正式知识只能来自可验证、可复用、边界清晰且可审计的候选内容
