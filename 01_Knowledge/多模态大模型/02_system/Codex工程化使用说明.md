---
type: knowledge
status: verified
unit_type: workflow_pattern
domain: 工程工作流
topic: Codex工程化使用说明
sources:
  - https://developers.openai.com/codex/cli
  - https://developers.openai.com/codex/config
  - https://developers.openai.com/codex/advanced
  - https://developers.openai.com/codex/cli/sandbox
  - https://developers.openai.com/codex/cli/slash-commands
  - https://developers.openai.com/codex/guides/agents-md
  - https://developers.openai.com/codex/skills
  - https://developers.openai.com/codex/subagents
scope: 适用于已具备基本开发背景、希望在真实工程仓库中稳定使用 Codex 的场景，重点覆盖配置分层、职责边界、仓库组织和常见误区。
risks:
  - 将仓库长期规则错误地塞进单次 prompt
  - 依赖 undocumented 行为、隐藏 prompt 或非官方稳定接口
  - 过早把一次性流程固化为 skill 或 subagent
  - 将 slash commands、skills、subagents、AGENTS.md 的职责混写
source_task: 基于当前官方 Codex 文档重写工程化使用说明，弱化对 Agent Workflow 专用体系的耦合
evidence:
  - 官方文档已提供 AGENTS.md、config.toml、skills、subagents、slash commands 的稳定入口
  - 项目层与用户层配置在官方文档中已有明确落点
  - slash commands 适合会话控制，不适合替代仓库长期规则
updated_at: 2026-04-11
summary: "Codex工程化使用说明 相关的历史知识笔记，归入 多模态大模型 主题，用于学习、查阅和工程参考。"
---

# 1 Codex 工程化使用说明

## 1.1 这篇文档解决什么问题

这篇文档不介绍 Codex 的抽象概念，而是回答更实际的问题：

> 在真实工程仓库里，Codex 应该怎么配、怎么用、哪些规则放在哪一层。

重点不是“功能罗列”，而是三件事：

- 如何把会话层、项目层、用户层分开
- 如何把 prompt、默认行为、长期规则、skills、subagents、slash commands 分工写清
- 如何避免把所有约束塞进 prompt，或者依赖不稳定接口

---

## 1.2 Codex 的工程化定位

从工程使用角度看，Codex 更接近一个**面向仓库工作的交互式代理入口**，而不是单次问答模型。

它的稳定价值主要在于：

- 读取当前仓库上下文并执行受控修改
- 在会话中进行计划、实现、检查和迭代
- 读取仓库级规则文件，如 `AGENTS.md`
- 使用项目级和用户级配置
- 调用 skills、slash commands、subagents 等机制扩展行为

因此，Codex 在工程流程中的位置通常是：

- 会话入口
- 代码与文档工作台
- 仓库规则执行器
- 可扩展的任务分发面

它不应该被理解成：

- 只靠一个长 prompt 驱动的一次性执行器
- 默认负责所有长期制度和所有流程门禁的唯一载体
- 可以安全依赖 undocumented 内部行为的黑箱接口

---

## 1.3 配置分层

### 1.3.1 会话层

会话层只解决“这一次要做什么”。

会话层通常包括：

- 用户当前 prompt
- 当前会话中的上下文选择
- slash commands 触发的临时控制
- 会话内临时追加的边界或目标

这一层适合放：

- 当前问题描述
- 当前目标
- 当前成功标准
- 本轮只对这次任务有效的限制

这一层不适合放：

- 仓库长期规则
- 组织级流程制度
- 多轮复用的代码风格或目录语义
- 需要长期稳定生效的 reviewer / writeback / board 类门禁

一句话说，会话层负责**实例化当前任务**，不负责**持久化工程制度**。

### 1.3.2 项目层

项目层解决“在这个仓库里默认怎么工作”。

这一层是 Codex 工程化使用的主战场，通常包括：

- `AGENTS.md`
- `.codex/config.toml`
- `.codex/agents/*.toml`
- 仓库内 skills

这一层适合承载：

- 仓库目录语义
- 默认读写边界
- 默认验证方式
- 团队约定的工程规则
- 项目级自定义 agents
- 项目级可复用 skills

如果某个约束希望跨多轮任务、跨多位使用者稳定生效，就应优先放在项目层，而不是反复写进 prompt。

### 1.3.3 用户层

用户层解决“这个用户跨项目复用哪些能力和偏好”。

官方文档里，用户层最常见的落点包括：

- `~/.codex/config.toml`
- `~/.codex/AGENTS.md`
- `CODEX_HOME`
- 用户级 `AGENTS.md`
- 用户级 skills
- 用户级自定义 agents

这层适合承载：

- 与某个仓库无关的默认模型、审批、工具行为
- 跨项目都成立的工作偏好
- 通用技能库
- 个人常用 agent 角色

用户层的原则不是“越多越好”，而是“跨仓库仍然成立”。  
只对单个仓库有效的规则，不应上提到用户层。

---

## 1.4 会话层的实际使用方式

### 1.4.1 prompt 应该承担什么

prompt 只应表达本轮任务实例。  
一个好的工程 prompt 通常只包含：

- 当前问题
- 当前目标
- 必要边界
- 成功标准
- 允许访问范围或修改范围

如果一个约束在下次任务还成立，它通常就不应该继续停留在 prompt。

### 1.4.2 slash commands 的位置

官方文档里的 slash commands 更适合做**会话控制**，而不是做**仓库制度承载**。

它们适合解决的事情包括：

- `/plan`：进入 plan mode
- `/status`：查看当前模型、审批策略、可写根路径和 token 使用
- `/permissions`：调整会话级审批策略
- `/model`：切换当前会话模型
- `/mention`：把文件显式拉入当前上下文
- `/compact`：压缩上下文
- `/resume`：恢复历史会话
- `/review`：对当前工作树做审查
- `/init`：生成 `AGENTS.md` 脚手架

它们不适合承载：

- 仓库长期目录规则
- 长期 reviewer 边界
- 项目默认验证合同
- 团队制度

换句话说，slash commands 主要回答：

> 这次会话现在怎么操作。

而不是：

> 这个仓库以后长期应该怎么治理。

### 1.4.3 会话层的推荐做法

- 用 prompt 定义当前任务，不在 prompt 里重抄长期制度
- 用 slash commands 做会话控制，不把它当配置文件替代物
- 把会复用的规则下沉到 `AGENTS.md` 或 `.codex/config.toml`
- 把会复用的窄流程下沉到 skill
- 把需要角色独立性的职责下沉到 subagent

---

## 1.5 项目层配置

### 1.5.1 `AGENTS.md`

`AGENTS.md` 是项目层最重要的长期规则入口之一。  
官方文档的核心思想很明确：把稳定规则写进 `AGENTS.md`，而不是每次重新拼 prompt。

它适合承载：

- 仓库目录语义
- 默认工作方式
- 默认禁止事项
- 哪些路径可读、哪些路径可写
- 测试、评审、提交等流程要求
- 团队对输出格式和行为边界的要求

它不适合承载：

- 本轮一次性任务细节
- 临时成功标准
- 本轮特有例外

按官方文档，Codex 会在开始工作前读取 `AGENTS.md` 指令链。  
常见落点包括：

- `~/.codex/AGENTS.md`：用户级默认规则
- 仓库根目录 `AGENTS.md`：项目级规则
- 更靠近当前工作目录的 `AGENTS.md` 或 `AGENTS.override.md`：局部覆盖规则

如果仓库已有其他文件名，也可以通过 `project_doc_fallback_filenames` 配置额外的候选文件名。  
这意味着：

- 长期规则优先放进 `AGENTS.md`
- 局部覆盖优先用更近层级的 `AGENTS.md` 或 `AGENTS.override.md`
- 不要把这套长期层级再复制回 prompt

### 1.5.2 `.codex/config.toml`

项目级 `.codex/config.toml` 适合放**可配置行为**，而不是自然语言制度。

例如：

- 项目默认模型相关设置
- 审批与权限相关设置
- 沙箱和执行策略
- 其他官方支持的 Codex 配置项

从官方文档看，配置优先级大致是：

1. CLI flags 和 `--config`
2. profile
3. 项目级 `.codex/config.toml`
4. 用户级 `~/.codex/config.toml`
5. 系统级配置
6. 内建默认值

另外，项目级 `.codex/` 配置只会在项目被标记为 trusted 时生效。  
如果项目是不可信的，Codex 会跳过项目级 `.codex/config.toml` 并回退到用户级和系统级配置。

工程上应注意两点：

- 只使用官方文档明确支持的配置项
- 不要把本应写在 `AGENTS.md` 的制度性说明硬塞进 `config.toml`

一个简单判断方法是：

- 如果它是“机器可解析配置”，优先考虑 `config.toml`
- 如果它是“团队长期行为规则”，优先考虑 `AGENTS.md`

### 1.5.3 `.codex/agents/*.toml`

这一层适合定义**项目级自定义 agents / subagents**。

适合放进这里的内容：

- 明确的角色定位
- 工具权限范围
- 角色专用说明
- 明确的使用场景

适合做成项目级 agent 的情况：

- 该角色反复出现
- 职责边界稳定
- 与项目结构强相关
- 需要独立视角或独立输入裁剪

不适合做成项目级 agent 的情况：

- 只是一次性临时拆分
- 职责还不稳定
- 和仓库结构并无固定耦合

### 1.5.4 skills

skills 适合沉淀**重复出现、边界清楚、输入输出稳定的窄任务能力**。

更适合做成 skill 的典型例子：

- 固定格式的文档转换
- 固定入口的 API 调用流程
- 有明确结果合同的脚本化操作
- 可反复验证的单一 job

不适合做成 skill 的情况：

- 一个 skill 同时覆盖检索、设计、编码、评审、回写整条链
- 还没有稳定合同
- 只是一次性试探流程

---

## 1.6 用户级全局配置

### 1.6.1 `~/.codex/config.toml`

这层适合放**跨项目都成立**的默认配置，例如：

- 默认模型偏好
- 通用审批偏好
- 通用沙箱偏好
- 与具体仓库无关的常用设置

如果某个配置只适用于某一仓库，不要写到用户级配置里。

### 1.6.2 `CODEX_HOME`

`CODEX_HOME` 用于改变 Codex 的用户级工作目录。  
工程上更重要的意义不是“知道有这个变量”，而是知道它影响的是**用户层落点**，不是项目层落点。

因此：

- 想改个人级目录位置，可以考虑 `CODEX_HOME`
- 想定义某个仓库自己的规则，不应依赖 `CODEX_HOME`

### 1.6.3 `~/.codex/AGENTS.md`

如果你希望某些工作习惯在所有仓库默认生效，官方推荐的稳定入口是 `~/.codex/AGENTS.md`。  
它适合承载：

- 通用工作协议
- 通用测试或验证习惯
- 通用依赖管理偏好
- 与单仓库无关的默认行为

若只是临时全局覆盖，可使用 `~/.codex/AGENTS.override.md`，撤掉后恢复基线。

### 1.6.4 用户级 skills 与 agents

用户级能力适合放那些：

- 跨多个仓库都成立
- 不依赖单一项目结构
- 长期稳定复用

如果某个能力明显依赖某个仓库的目录、构建系统或验证合同，更适合沉淀到项目层，而不是用户层。

---

## 1.7 prompt、长期规则、默认行为、subagents、skills、slash commands 的职责边界

### 1.7.1 prompt

负责本轮任务实例化。  
关键词是：当前问题、当前目标、当前边界。

### 1.7.2 长期规则

负责跨多轮任务稳定成立的规则。  
落点通常是：

- `AGENTS.md`
- 项目长期规范
- 团队长期约定

### 1.7.3 默认行为

默认行为主要由配置和系统默认机制决定。  
它应尽量来自：

- 官方支持的配置项
- 明确写入的长期规则

而不是依赖某次 prompt 里顺手补的一段话。

### 1.7.4 subagents

subagents 适合承担**角色分工**和**独立视角**，例如：

- reviewer
- planner
- verifier
- 某个项目专用分析角色

是否需要 subagent，关键不在“任务大不大”，而在：

- 是否需要独立输入
- 是否需要独立判断
- 是否需要与主代理职责隔离

### 1.7.5 skills

skills 适合承担**窄而重复的能力单元**。  
一个稳定的 skill，通常能用一句话说清楚它做什么和不做什么。

### 1.7.6 slash commands

slash commands 适合做**会话内操作控制**。  
它们是操作入口，不是仓库治理载体。

---

## 1.8 推荐的仓库组织方式

一个更稳的工程落点通常是：

```text
repo/
├── AGENTS.md
├── .codex/
│   ├── config.toml
│   └── agents/
│       ├── reviewer.toml
│       └── planner.toml
├── .agents/
│   └── skills/
│       ├── skill_a/
│       │   └── SKILL.md
│       └── skill_b/
│           └── SKILL.md
└── ...
```

这个组织方式的好处是：

- 长期规则有固定入口
- 可配置行为和自然语言规则分层清楚
- 项目级角色和项目级 skills 都有稳定落点
- 新成员更容易判断“该改 prompt、规则、agent 还是 skill”

---

## 1.9 常见误区

### 1.9.1 把所有约束都塞进 prompt

这是最常见的问题。  
结果通常是 prompt 越来越长，但规则反而越来越不稳定。

### 1.9.2 把 `AGENTS.md` 当成任务单

`AGENTS.md` 适合长期规则，不适合写一次性任务说明。

### 1.9.3 用 skill 承载整条复杂流程

skill 应该窄。  
需要复杂角色分工、独立判断和多阶段门禁时，优先考虑 subagents 或项目流程，而不是继续放大一个 skill。

### 1.9.4 过度依赖用户级配置

项目规则写在用户级配置里，最终会造成：

- 仓库不可迁移
- 团队不可共享
- 行为难以审计

### 1.9.5 把 undocumented 行为当接口

如果某个行为没有在当前官方文档中明确出现，就不要把它当作长期稳定接口依赖。  
尤其不要依赖：

- 猜测出的内部 prompt 结构
- 未文档化的隐藏文件约定
- 非官方声明稳定的内部行为

---

## 1.10 非官方稳定接口的边界

在工程里，真正适合长期依赖的，应优先限于当前官方文档明确给出的机制，例如：

- `AGENTS.md`
- 官方支持的 `config.toml`
- 官方文档描述的 skills 机制
- 官方文档描述的 subagents 机制
- 官方文档描述的 slash commands

而对以下内容，应保持保守：

- 逆向猜测出来的内部约束
- 某次版本偶然可用的 undocumented 参数
- 依赖系统内部提示词细节的流程设计

工程上最稳的原则是：

> 能放到官方明示接口，就不要依赖隐式行为。

---

## 1.11 使用建议

如果要把 Codex 用稳，推荐顺序是：

1. 先把仓库级长期规则收敛到 `AGENTS.md`
2. 再把机器可解析配置收敛到 `.codex/config.toml`
3. 再把稳定角色下沉到 `.codex/agents/*.toml`
4. 再把窄而重复的任务下沉到 skills
5. 最后只把当前任务实例留在 prompt

这套顺序的核心不是“把东西分散存放”，而是让每一层只承载它该承载的东西。
