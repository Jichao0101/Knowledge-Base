---
title: Agent Workflow Design Current
summary: 当前 Agent Workflow 主题只围绕 cutepower 维护；本文件定义 plugin、project current、baseline、record 与通用知识之间的分层和边界。
status: pending_review
doc_role: current
truth_role: current
current_kind: design
lifecycle_state: active
default_entry: false
sync_required_when:
  - cutepower 分层变化
  - current / baseline / record 的职责边界变化
  - P0/P1 active 能力集合变化
retrieval_priority: current
supersedes: []
merged_into: []
current_replacement: []
related_code: []
related_plugins:
  - cutepower
sources:
  - 02_Projects/Agent Workflow/workflow_overview_current.md
  - /mnt/d/cutepower/README.md
  - /mnt/d/cutepower/contracts/role-contracts.yaml
  - /mnt/d/cutepower/contracts/routing-table.yaml
  - 01_Knowledge/Agent Workflow/Plugin-first与Contracts-first治理插件设计模式.md
scope: 适用于恢复当前 cutepower 的项目分层、角色边界与项目区资产职责分工。
risks:
  - 若把 project current 扩写成 contracts 替代品，会削弱 contracts-first 主轴。
  - 若把 cutepower record 写成旧式制度说明，会重新膨胀项目区。
updated_at: 2026-04-17
---

## 0.1 Current Goal

当前目标不是继续维护 Agent Workflow 的旧三侧体系，而是维护一个已经落到 plugin 内部的 cutepower 治理系统。
项目区只负责：

- 当前组织方式说明
- 基线追溯
- 实施与验证状态同步

## 0.2 Current Layering

- `/mnt/d/cutepower/contracts/`
  - 当前治理真相源
  - 承接 role / gate / review / writeback / routing
- `/mnt/d/cutepower/skills/` 与 `scripts/`
  - 当前运行与校验资产
  - 消费 contracts，不复制治理正文
- `02_Projects/Agent Workflow/workflow_*_current.md`
  - 当前项目态说明与恢复入口
- `02_Projects/Agent Workflow/cutepower_*_baseline.md`
  - 历史实施基线
- `02_Projects/Agent Workflow/cutepower P1插件落地与运行时门禁收敛记录-2026-04-17.md`
  - cutepower 事件记录
- `01_Knowledge/Agent Workflow/*.md`
  - 只保留通用模式知识，不承接 active truth

## 0.3 Current 与 Baseline / Record 分工

- `current`
  - 当前真相源集合
  - 当前分层
  - 当前实现落点
  - 当前验证结论
- `baseline`
  - 某一轮实施前冻结的边界
  - 不作为默认实现入口
- `record`
  - 某次 cutepower 收敛、实现、验证或硬化事件
  - 只做事件追溯，不承担当前规则正文

## 0.4 Non-goals

- 不恢复原三侧项目记录
- 不再维护 Chaospower current 或 record
- 不把宿主知识库目录语义写回 cutepower plugin
- 不把 current 组写成 changelog
- 不把 AGENTS / toml 扩回治理正文
- 不把入口提示词写成固定执行链

## 0.5 Owner Rules

- overview owner：默认入口、真相源集合、保留资产边界
- interface owner：最小启动提示词模板与入口边界
- design owner：分层、职责边界、非目标项
- spec owner：项目级强规则与优先级
- implementation owner：当前落点与保留载体
- validation owner：验证状态、缺口与下一轮重点

## 0.6 Current Cutepower Design

P0 active skills：

1. `using-cutepower`
2. `cute-scope-plan`
3. `cute-repo-change`
4. `cute-code-review`
5. `cute-writeback`

P1 active skills：

1. `cute-board-run`
2. `cute-functional-review`
3. `cute-incident-investigation`

当前设计原则固定为：

- plugin-first
- contracts-first
- thin bridge
- repo review / functional review / writeback 独立
- runtime gate 优先阻断越权路径

## 0.7 Record Policy

本目录只保留 cutepower-specific record。
若未来新增记录，不得再写回原三侧泛化制度、Chaospower 过渡阶段或与 cutepower 无直接关系的主题记录。
