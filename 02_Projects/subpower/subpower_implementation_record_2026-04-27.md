---
type: project_record
status: current
domain: 工程工作流
topic: subpower 初版实现记录
project: subpower
created_at: 2026-04-27
updated_at: 2026-04-28
source_repo: /mnt/d/subpower
related_blueprint: /mnt/d/knowledgeBase/02_Projects/subpower/subpower_architecture_blueprint_current.md
---

# 1 subpower 初版实现记录 2026-04-27

## 1.1 本轮目标

基于 contracts-first / runtime-gate / role boundary 的抽象原则，以及 Knowledge-Base 中旧三侧同步子代理设计，创建独立项目 `subpower` 的 MVP 实现。

本轮同时修正两个方向：

1. Knowledge-Base 项目文档使用中文 current 蓝图，并新增实现记录。
2. subpower 仓库既作为本地开发源，也按未来 Codex plugin 分发源设计，不把插件元数据或安装说明误 ignore。

## 1.2 已完成实现

仓库：`/mnt/d/subpower`

已新增：

- `README.md`
- `README.codex.md`
- `AGENTS.md`
- `.codex-plugin/plugin.json`
- `agents/*.toml`
- `contracts/*.yaml`
- `schemas/run-artifacts/*.schema.json`
- `scripts/run-artifacts.js`
- `scripts/runtime-gates.js`
- `scripts/validate-contracts.js`
- `scripts/test-*.js`
- `skills/using-subpower/SKILL.md`
- `docs/*.md`
- `.gitignore`

## 1.3 已实现的 contracts

- `role-contracts.yaml`
- `workflow-patterns.yaml`
- `decision-points.yaml`
- `gate-matrix.yaml`
- `artifact-requirements.yaml`
- `side-state-machine.yaml`
- `route-policy.yaml`
- `closure-policy.yaml`

这些文件是 subpower 当前 active truth source。

## 1.4 已实现的 runtime 能力

`scripts/runtime-gates.js` 当前覆盖：

- role / phase action gate；
- required artifact gate；
- schema required-field gate；
- reviewer independence gate；
- board target gate；
- evidence gate；
- board failure route gate；
- closure gate；
- writeback gate。

实现边界：runtime gate 只判断结构合法性，不判断业务语义、根因正确性或实现质量。

## 1.5 已实现的负向测试

已新增测试：

- `scripts/test-runtime-gates.js`
- `scripts/test-decision-points.js`
- `scripts/test-agent-boundaries.js`
- `scripts/test-run-artifacts.js`

覆盖场景包括：

- coder 试图自审；
- reviewer 试图执行 repo_write；
- board-runner 缺少 board target；
- board failed 后缺少 board failure review；
- illegal route；
- 缺少 evidence close；
- 缺少 closure writeback；
- implementer 与 reviewer 使用同一 agent identity。

## 1.6 已验证命令

```bash
node scripts/validate-contracts.js
node scripts/test-runtime-gates.js
node scripts/test-decision-points.js
node scripts/test-agent-boundaries.js
node scripts/test-run-artifacts.js
```

以上命令已通过。

## 1.7 插件化调整记录

已新增 `.codex-plugin/plugin.json`，使仓库具备未来作为 Codex plugin 分发的基础元数据。

已新增 `README.codex.md`，明确：

- 当前仓库是 development source；
- runtime 应使用安装后的插件源；
- `.subpower/run/<session_id>/` 是运行态，不进入版本库；
- 插件 metadata 与 runtime state 分离。

已调整 `.gitignore`：

- 不再版本化忽略 `.codex/`，避免将来插件安装说明或 Codex 配置被误排除；
- 只忽略 `.subpower/run/`、依赖、coverage、日志和临时文件。

## 1.8 后续建议与状态

以下建议已在 2026-04-28 第二阶段完成：

1. 增加 `scripts/install-plugin.js` 与安装测试，实现 personal / repo scoped staging。
2. 为 contracts 增加更严格 JSON schema，而不是仅做 required-field 检查。
3. 增加 `failure-analyst`、`knowledge-closer`、`verification-manager` 的 post-MVP contracts。
4. 增加真实 `.subpower/run/<session_id>/` fixture，演示 bug_fix + board_validation 的完整失败返工路径。

第二阶段同时取消了外部 runtime adapter 方向：subpower 不读取外部 run-state，不生成上游 context artifact，仓库 README 与 docs 保持自包含。
