---
type: project_record
status: current
domain: 工程工作流
topic: subpower 第二阶段实现记录
project: subpower
created_at: 2026-04-28
updated_at: 2026-04-28
source_repo: /mnt/d/subpower
related_blueprint: /mnt/d/Knowledge-Base/02_Projects/subpower/subpower_architecture_blueprint_current.md
---

# 1 subpower 第二阶段实现记录 2026-04-28

## 1.1 本轮目标

继续推进 `/mnt/d/subpower` 第二阶段，实现插件 staging、schema validation、post-MVP agent contracts、真实 board failure rework fixture、全量回归入口，并收紧 subpower 独立性边界。

核心边界：

- subpower 是独立 development source；
- `.codex-plugin/plugin.json` 是未来插件分发 metadata；
- `scripts/install-plugin.js` 只是 staging utility，不代表正式发布；
- `.subpower/run/<session_id>/` 是运行态，不版本化；
- workflow 是 pattern，不是固定脚本；
- board failed 后必须先 assessment 再 route；
- runtime gate 只做结构合法性，不做业务判断；
- subpower 不保留外部 runtime adapter，不读取外部 run-state，不生成上游 context artifact。

## 1.2 已完成变更

仓库：`/mnt/d/subpower`

已完成：

- 删除外部 runtime adapter 脚本与旧兼容文档；
- README、README.codex、docs、AGENTS、using-subpower skill 改为自包含边界说明；
- 新增 `scripts/install-plugin.js`，支持 `--scope personal|repo`、`--target`、`--dry-run`、`--force`；
- 新增 `scripts/test-install-plugin.js`，覆盖缺少 target、dry-run、repo staging、force、排除 runtime 目录、复制 plugin metadata；
- 新增 `scripts/schema-validator.js`，支持轻量 JSON schema subset；
- `scripts/runtime-gates.js` 已调用 schema validator；
- `scripts/validate-contracts.js` 已校验 contracts 可解析、必要字段、contract schema 与 run-artifact schema 合法；
- 增强 run artifact schemas，包括 `board_failure_review`、`main_route_decision`、`closure_matrix`、`board_session`；
- 新增 `failure-analyst`、`verification-manager`、`knowledge-closer` agent skeleton；
- `contracts/role-contracts.yaml`、`gate-matrix.yaml`、`workflow-patterns.yaml` 已加入对应 role 与 optional participant / assessor 边界；
- 新增 `fixtures/bugfix-board-failure-rework/`；
- 新增 `scripts/test-fixtures.js`；
- 新增外部 runtime dependency 负向扫描测试；
- 新增 `scripts/test-all.js`。

## 1.3 Fixture 场景

fixture：`fixtures/bugfix-board-failure-rework/`

场景：

- 板端融合目标跳变问题；
- 第一次 bug_fix 修复 timestamp alignment；
- 本地 review 通过；
- 板端验证失败：高 yaw-rate 场景仍有目标跳变；
- reviewer 可以评估为 `implementation_defect` 并 route 到 `coder_rework`；
- reviewer 可以评估为 `plan_mismatch` 并 route 到 `planner_rework`；
- `closure_matrix.blocked.json` 表示不能 close。

测试覆盖：

- 所有 fixture artifact 通过 schema；
- board failed 后没有 `board_failure_review` 会被拒绝；
- `implementation_defect` + `coder_rework` route gate 通过；
- `plan_mismatch` + `planner_rework` route gate 通过；
- blocked closure matrix 不允许 close；
- board failed 但 route=`proceed_to_closure` 必须失败。

## 1.4 已验证命令

```bash
node scripts/validate-contracts.js
node scripts/test-runtime-gates.js
node scripts/test-decision-points.js
node scripts/test-agent-boundaries.js
node scripts/test-run-artifacts.js
node scripts/test-schema-validator.js
node scripts/test-install-plugin.js
node scripts/test-fixtures.js
node scripts/test-all.js
```

以上命令在第二阶段收尾时已通过。

## 1.5 当前限制

- schema validator 是刻意保守的最小 subset，不实现完整 JSON Schema draft；
- runtime gate 只做结构合法性、角色边界、route 合法性，不判断业务语义；
- plugin installer 是 staging 工具，不处理 marketplace 发布、版本升级或远端安装；
- knowledge writeback 仍依赖 closure gate 后的人控或后续 workflow，不自动提升未经 review 的结论。
