---
title: cutepower Design Current
summary: cutepower 当前设计中心是 contracts-first + artifact-driven governance，而不是旧的 hook-front lifecycle 设计；知识库项目层也已从 Agent Workflow 收口为 cutepower 专项目录。
status: pending_review
doc_role: current
truth_role: current
current_kind: design
lifecycle_state: active
default_entry: false
sync_required_when:
  - contracts-first 边界变化
  - artifact-driven gating 变化
  - 项目层命名与分层变化
retrieval_priority: current
supersedes: []
merged_into: []
current_replacement: []
related_code: []
related_plugins:
  - cutepower
sources:
  - 02_Projects/cutepower/cutepower_overview_current.md
  - /mnt/d/cutepower/README.md
  - /mnt/d/cutepower/docs/runtime-hardening.md
  - /mnt/d/cutepower/contracts/
  - /mnt/d/cutepower/agents/openai.yaml
  - /mnt/d/cutepower/scripts/task-intake.js
  - /mnt/d/cutepower/scripts/host-runtime.js
  - /mnt/d/cutepower/scripts/runtime-gates.js
  - /mnt/d/cutepower/scripts/governance-response.js
  - /mnt/d/cutepower/scripts/run-artifacts.js
scope: 适用于恢复当前 cutepower 的项目设计分层、角色边界与当前非目标。
risks:
  - 若把 current 写成 contracts 替代品，会削弱 contracts-first 主轴。
  - 若把 future cuteagents 预先混入 cutepower current，会污染项目边界。
updated_at: 2026-04-23
---

## 0.1 Design Goal

当前目标是维护一个 skill-first 的 cutepower 项目，而不是继续维护泛化的 Agent Workflow 总设计。

## 0.2 Layering

- `contracts/`：治理真相源
- `skills/`：消费 contracts 的运行资产
- `agents/openai.yaml`：宿主 surface metadata
- `scripts/task-intake.js`：默认入口与 preflight
- `scripts/host-runtime.js`：显式模式下的 session capability 注入
- `scripts/runtime-gates.js`：执行期 action gate
- `scripts/governance-response.js`：统一治理裁决对象
- `scripts/run-artifacts.js` + `schemas/run-artifacts/`：repo-local runtime state
- `README*` / `AGENTS.md` / `agents/*.toml`：薄桥接

## 0.3 Explicit Non-goals

- 恢复 hook 文件链作为主线
- 把 install/uninstall 重新做成 hook 配置管理器
- 把 knowledge-base 目录结构塞回 plugin
- 把 cuteagents 与 cutepower 混写在同一个 current 集合里
