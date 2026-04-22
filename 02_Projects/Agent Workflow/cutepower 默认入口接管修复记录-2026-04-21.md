---
title: cutepower 默认入口接管修复记录
summary: 记录 cutepower 默认入口未稳定接管工程任务的问题定义、根因判断、cutepower 仓库内的主修复、以及对项目区 current 的同步边界。
status: pending_review
doc_role: modification_record
record_type: implementation_record
truth_role: evidence
lifecycle_state: pending_merge
default_entry: false
retrieval_priority: evidence_only
target_current_docs:
  - 02_Projects/Agent Workflow/workflow_overview_current.md
  - 02_Projects/Agent Workflow/workflow_interface_current.md
  - 02_Projects/Agent Workflow/workflow_design_current.md
  - 02_Projects/Agent Workflow/workflow_spec_current.md
  - 02_Projects/Agent Workflow/workflow_implementation_current.md
  - 02_Projects/Agent Workflow/workflow_validation_current.md
related_plugins:
  - cutepower
sources:
  - /mnt/d/cutepower/contracts/task-normalization.yaml
  - /mnt/d/cutepower/contracts/routing-table.yaml
  - /mnt/d/cutepower/.codex-plugin/plugin.json
  - /mnt/d/cutepower/agents/openai.yaml
  - /mnt/d/cutepower/scripts/task-profile.js
  - /mnt/d/cutepower/scripts/task-intake.js
  - /mnt/d/cutepower/scripts/validate-contracts.js
  - /mnt/d/cutepower/scripts/test-task-profile.js
  - /mnt/d/cutepower/scripts/test-task-intake.js
  - /mnt/d/cutepower/scripts/test-runtime-gates.js
  - /mnt/d/cutepower/scripts/test-install-plugin.js
scope: 适用于追溯 cutepower 默认入口接管修复，不适合作为 contracts 替代品，也不作为正式知识区的稳定规则文档。
risks:
  - 当前修复已把默认入口接到 intake，但仍未完成一次真实 Codex 会话里的完整发现链路验收。
  - 当前 runtime classifier 仍主要依赖 manifest/agent metadata 与 task-normalization 规则，后续仍可继续提高召回率。
updated_at: 2026-04-21
---

# 1 cutepower 默认入口接管修复记录

## 1.1 问题定义

- 现象：
  - cutepower 已有自然语言 `task normalization` 与 route/gate 能力，但真实工程任务进来后，主代理仍常直接读 current、定位 repo、排查并修改代码。
  - 运行链里经常缺失 `intake`、`preflight`、`route_resolution`、`context_requirements`、`blocking_gaps`、`skill_handoff`、`runtime_gate`。
- 根因判断：
  - 主问题更像默认入口没有稳定接入 cutepower，而不是 cutepower 完全没有语义层。
  - 现有仓库在修复前已经有 `task-profile.js`、`routing-table.yaml`、`runtime-gates.js`，说明 route/gate 基础能力存在。
  - 但 cutepower 缺少一个默认入口前置层，也缺少足够强的 runtime metadata，让工程任务先落到 cutepower intake。
- 为什么不是单纯“知识库限制过紧”：
  - `/mnt/d/Knowledge-Base/AGENTS.md` 已明确不负责 plugin 启动与路由规则，只负责知识边界、目录授权、写入分层与 runtime discovery 例外。
  - runtime discovery 相关路径也已被知识库 AGENTS 明确排除在普通知识上下文之外。
  - 因此主修复场必须回到 `/mnt/d/cutepower`，而不是继续在知识库里放宽或重写治理。

## 1.2 修复思路

- 先在 cutepower 仓库内补一层显式 `task-intake`：
  - 先跑 `task_profile`
  - 再输出 `route_resolution`
  - 再给出 `context_requirements`
  - 再给出 `blocking_gaps`
  - 最后给出 `skill_handoff` 与 `runtime_gate`
- 默认入口调整为：
  - 工程类自然语言请求先尝试 cutepower intake
  - cutepower 只有在明确 `declined` 时才允许普通直接执行回退
  - `clarification_required` 与 `blocked` 不能静默绕过
- runtime discovery 单独建模：
  - `~/.codex`、`~/.agents` 与 plugin/marketplace/hook 检查属于 runtime discovery
  - 不能因此被当作知识库上下文读取
- runtime 接入方式采用最小可回退方案：
  - 在 contracts 中声明 `autostart_primary_types` 与 `fallback_behavior`
  - 在 manifest 与 `agents/openai.yaml` 中补默认入口元数据
  - 不做复杂 hooks，不恢复 project current 作为主规则源

## 1.3 实际修改

- contracts：
  - `contracts/task-normalization.yaml`
    - 新增 `autostart_primary_types`
    - 新增 `fallback_behavior`
    - 新增 `runtime_entry`
    - 新增 `runtime_discovery`
- runtime scripts：
  - 新增 `scripts/task-intake.js`
    - 统一产出 `task_profile`
    - `route_resolution`
    - `context_requirements`
    - `blocking_gaps`
    - `runtime_discovery`
    - `skill_handoff`
    - `runtime_gate`
  - 修改 `scripts/task-profile.js`
    - 同分命中时改为按 contract `priority` 进行 tie-break，不再把典型 `bug_fix`/`implementation` 请求过度判成歧义
  - 修改 `scripts/validate-contracts.js`
    - 校验新的 activation/runtime 字段
    - 校验 intake script 落点存在
- runtime metadata：
  - 修改 `.codex-plugin/plugin.json`
    - 增加 `keywords`
    - 增加 `agents`
    - 增加 `interface.defaultPrompt`
  - 新增 `agents/openai.yaml`
    - 把工程任务默认先过 cutepower intake 的入口意图暴露给 runtime discovery
- tests：
  - 新增 `scripts/test-task-intake.js`
    - 覆盖 bug_fix 先走 intake
    - 覆盖 incident 先 route 再决定 repo change
    - 覆盖 audit/read_only 不误进 repo_write
    - 覆盖 knowledge/repo/board 授权缺口返回 `blocking_gaps`
    - 覆盖 runtime discovery 不被当成知识上下文
    - 覆盖自动触发层不绕过 runtime gate
  - 修改 `scripts/test-install-plugin.js`
    - 额外校验 runtime agent metadata 会被安装复制

## 1.4 影响范围

- `implementation` / `bug_fix`
  - 默认不应再直接跳进 repo 排查与改码
  - 先进入 intake/preflight，再 handoff 到 `cute-scope-plan`
- `incident_investigation`
  - 默认先 route 到 incident skill 链
  - 是否进入 repo-change 改为后续条件性交接，不在默认入口阶段直接越级
- `audit` / `read_only`
  - 保持读路径，不误进 `repo_write`
- 知识库使用方式
  - 知识库 AGENTS 继续只负责知识边界、授权与写入分层
  - 不再承担主代理运行治理与 plugin 启动判定
- 用户级 runtime discovery
  - `.codex`、`.agents`、plugin/marketplace/hook 检查从 knowledge context 中分离
  - 只作为 runtime 配置发现与启用状态判断

## 1.5 验证

- 已通过：
  - `cd /mnt/d/cutepower && node scripts/validate-contracts.js`
  - `cd /mnt/d/cutepower && node scripts/test-task-profile.js`
  - `cd /mnt/d/cutepower && node scripts/test-runtime-gates.js`
  - `cd /mnt/d/cutepower && node scripts/test-task-intake.js`
  - `cd /mnt/d/cutepower && node scripts/test-install-plugin.js`
- 当前仍未闭环：
  - 真实 Codex 会话中的完整插件发现与接管验收
  - 不同宿主环境下 classifier 命中率的真实统计

## 1.6 后续建议

- P1：
  - 增加真实会话级别的默认入口验收
  - 为 intake 增加更细的 evidence / clarification 分类
- P2：
  - 若 runtime 后续支持更强钩子，再评估更主动的入口拦截
  - 为 conditional handoff 增加更结构化的触发证据
