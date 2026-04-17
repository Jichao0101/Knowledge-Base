---
type: knowledge
status: verified
unit_type: design_pattern
domain: 工程工作流
topic: Plugin-first与Contracts-first治理插件设计模式
sources:
  - 02_Projects/Agent Workflow/cutepower_p0_implementation_baseline.md
  - 02_Projects/Agent Workflow/cutepower_p1_board_functional_incident_baseline.md
  - /mnt/d/cutepower/contracts/contract-index.yaml
  - /mnt/d/cutepower/contracts/role-contracts.yaml
  - /mnt/d/cutepower/contracts/gate-matrix.yaml
  - /mnt/d/cutepower/contracts/routing-table.yaml
scope: 适用于需要把运行治理从长篇文档压缩为插件 contracts、技能边界与薄桥接层的工程协作系统，不绑定具体知识库或仓库目录语义。
risks:
  - 把 host workspace 的目录结构误写进 plugin contracts
  - 把治理正文复制到 skill、AGENTS 或 toml，导致 truth source 分裂
  - 新增能力时绕开既有 contract 家族，重新膨胀为规则散文
source_task: 根据 cutepower 设计与实现收敛出可复用治理插件模式
evidence:
  - active truth 收敛到 plugin contracts 后，skills 与 bridge 只需消费 contract id，不再复制治理正文
  - 将 role、gate、review、writeback、routing 固定为少量 contract 家族，可在扩展 P1 时保持边界稳定
  - host-specific 的项目目录、知识分区和历史文档不应进入 plugin 自身 contracts
updated_at: 2026-04-17
---

## 0.1 摘要

可复用治理插件的稳定形态不是“长篇说明文档 + 厚 prompt”，而是：

- plugin-first：运行时资产放在插件内
- contracts-first：治理真相先落到结构化 contracts
- thin bridge：`AGENTS.md`、`agents/*.toml`、skills 只做最小桥接

这个模式的目标，是让治理边界可验证、可扩展、可审查，而不是继续依赖散落文档解释。

## 0.2 适用边界

适合以下场景：

- 需要把角色边界、状态门禁、review 约束和 writeback 规则固化为可校验结构
- 需要在多个 skills 之间共享统一治理真相
- 需要让插件脱离宿主项目或知识库目录语义仍可自洽运行

不适合以下场景：

- 只需要一次性 prompt 约束、没有长期复用目标
- 治理边界还在高频探索，尚未形成稳定 contract 结构

## 0.3 核心结构

推荐把治理拆成少量稳定 contract 家族：

- `role-contracts`：角色允许动作、最小输入输出、停止条件
- `gate-matrix`：状态与动作门禁
- `review-boundaries`：review 类型、独立性与最小证据包
- `writeback-levels`：写回层级与前置条件
- `routing-table`：route、skill chain、role chain 与条件 handoff

扩展新能力时，优先扩现有 contract 家族，而不是新开类别。

## 0.4 薄桥接原则

skills、`AGENTS.md` 和 `agents/*.toml` 只应承担以下职责：

- skill：消费 contract，执行单一职责工作流
- `AGENTS.md`：声明极薄入口和 hard stop
- `agents/*.toml`：只保留确有直接实例化价值的桥接描述

它们不应复制：

- 角色契约正文
- review 规则正文
- writeback 分层正文
- host workspace 的目录结构语义

## 0.5 设计判断

若一个规则满足以下任一条件，应优先进入 contracts：

- 需要被多个 skills 共享
- 需要被 validator 或 runtime gate 直接消费
- 一旦模糊就会造成权限漂移或 review 失效

若一个说明只用于背景理解、迁移记录或历史决策追溯，应留在项目文档，而不是回流为 plugin truth。
