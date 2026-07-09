---
type: project_record
status: implemented_but_not_fully_verified
project: agent-trajectory
module: phase0-hook-feasibility
summary: "完成 agent-trajectory P0 最小实现和全局 passive Codex hook 注册：hook 同步路径只做 allowlist + fail-open enqueue，collector service 将 queue 转为 append-only raw events，并生成 Phase 0 feasibility report；真实新 Codex 会话中的 hook payload/correlation/ordering 验证仍未完成。"
sources:
  - "2026-07-09 当前对话：基于 agent 轨迹蒸馏方案，在 /home/jichao/agent-trajectory 完成 P0 实现"
  - "2026-07-09 当前对话：确认 repo-local hook 不能覆盖业务仓库后，改为全局 passive hook + allowlist 方案"
  - "02_Projects/agent-trajectory/agent_trajectory_initial_design.md"
scope: "agent-trajectory Phase 0 hook feasibility spike 的实现与注册记录；覆盖 collector 最小实现、Codex hook 包装器、全局 hooks.json 注册、allowlist、测试与残余验证缺口。"
risks:
  - "本记录只证明本地模拟 payload 到 collector/report 的链路可运行，尚未证明真实新 Codex 会话会按预期触发所有 lifecycle hooks。"
  - "当前 hook 包装器为 passive/fail-open，不提供阻断式治理，也不保证事件完整性。"
  - "当前 report 中的 correlation 成功来自手动模拟 payload，不能代表真实 Codex tool pre/post payload 已具备稳定 correlation key。"
  - "Raw event、snapshot 和 artifact 落盘仍是 P0 骨架，尚未经过多任务、高并发、丢失率或 overhead 统计验证。"
updated_at: 2026-07-09
---

# 1 Agent Trajectory P0 实现与 Hook 注册记录

## 1.1 背景

初始设计要求 Phase 0 先验证 Codex hook 是否足以支撑 trajectory collector service，而不是直接进入异步蒸馏或完整 trajectory 资产建设。本轮实现目标是做出最小可运行链路：hook adapter 轻量触发、collector service 负责 raw collection、raw collection 同步路径不调用 LLM，并用 report 回答 Phase 0 feasibility 问题。

实现过程中发现 repo-local hook 只会观测运行 Codex 的当前仓库。由于 `/home/jichao/agent-trajectory` 是 collector/trajectory 系统仓库，不是主要业务任务仓库，repo-local hook 只能自测 collector，不能采集 DMS、Knowledge-Base 等业务任务轨迹。因此本轮改为全局 passive hook + allowlist：全局 hook 负责跨仓库观察，allowlist 控制允许采集的 workspace，collector root 固定为 `/home/jichao/agent-trajectory`。

## 1.2 已完成实现

代码仓库：`/home/jichao/agent-trajectory`。

已完成的 P0 组件：

- `collector/hook_adapter.py`：读取 hook payload 并写入本地 JSONL queue。
- `collector/service.py`：将 queue 转为 append-only raw events，生成 `trajectory_schema_version`、`collector_version`、collector instance、单调 `sequence_no`、hook phase、correlation metadata、artifact refs 和 baseline snapshot refs。
- `collector/report.py`：生成 Phase 0 feasibility report，记录 raw collection LLM call count、event type 统计、hook profile、workspace/session 可观测性、ordering 单调性和 tool pre/post correlation blocker。
- `collector/codex_hook_entry.py`：Codex lifecycle hook 包装器，负责读取 stdin payload、识别 workspace、检查 allowlist、调用 hook adapter enqueue，并始终输出合法 JSON `{}`。
- `collector/allowed_workspaces.json`：当前 allowlist 包含 `/home/jichao/dms`、`/mnt/d/Knowledge-Base`、`/home/jichao/agent-trajectory`。
- `schemas/raw_event_schema.json`：Raw Event v1 JSON schema。
- `tests/test_phase0.py` 与 `tests/test_codex_hook_entry.py`：覆盖 enqueue/collect/report、correlation blocker、allowlist 采集和非 allowlist 忽略。

本轮没有实现异步 Semantic Distillation；`distiller/README.md` 明确 Phase 0 不在 raw collection 同步路径调用 LLM。

## 1.3 Hook 注册方式

全局 hook 注册文件：`/home/jichao/.codex/hooks.json`。

已注册事件：

- `UserPromptSubmit`
- `PreToolUse`
- `PostToolUse`
- `Stop`

所有事件都调用：

```bash
python3 /home/jichao/agent-trajectory/collector/codex_hook_entry.py --hook-name <HookName>
```

设计约束：

- Hook 同步路径只做 payload 读取、allowlist 判断和 enqueue。
- Hook 不运行 collector service、不排序、不做 snapshot/report、不调用 LLM。
- Hook stdout 始终为单一 JSON 对象 `{}`。
- Hook 内部异常写入 `storage/hook_errors.log`，同时 fail-open，不阻断 Codex 正常任务。
- 非 allowlist workspace 直接忽略，不采集 payload。

## 1.4 验证结果

已执行的验证：

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`
- 结果：5 个测试全部通过。
- 手动模拟 allowed workspace hook：stdout 为 `{}`，成功写入 queue。
- 手动模拟 non-allowlist workspace hook：stdout 为 `{}`，未写入 queue。
- 运行 collector service 后，成功将 1 条模拟 hook payload 转为 raw event。
- 运行 report 后生成 `phase0_feasibility_report.json`，其中 `raw_collection_llm_call_count = 0`。

本轮验证中的重要边界：

- Report 中 `tool_pre_post_has_stable_correlation_key = true` 来自手动模拟 payload 的 `tool_call_id`，不能证明真实 Codex payload 已稳定提供 correlation key。
- 当前会话不一定热加载新写入的全局 hooks；真实验证需要新开 Codex 会话后观察 queue/raw events。
- 当前 collector 是本地文件队列方案，未测 hook p95 overhead、并发写入、丢失率或长期运行稳定性。

## 1.5 当前结论

P0 已从纯设计推进到最小可运行实现，并完成全局 passive hook 注册。该实现满足以下阶段性约束：

- Raw collection 同步路径 LLM call count 为 0。
- Hook adapter 保持轻量 enqueue。
- Collector service 独立处理 ordering、artifact refs、snapshot refs 和 raw event 落盘。
- Raw event stream 采用 append-only JSONL，不被蒸馏结果覆盖。
- 全局 hook 通过 allowlist 限制采集范围，避免只在 collector 仓库自测。

但 Phase 0 仍未完成。继续推进前必须用真实新 Codex 会话验证：

- lifecycle hook 是否真实触发 `UserPromptSubmit`、`PreToolUse`、`PostToolUse` 和 `Stop`。
- 真实 hook payload 是否包含 cwd、tool name、input/output、session/thread、approval、error 和稳定 correlation key。
- tool pre/post 是否可可靠关联；若不能，应记录为 Phase 0 blocker。
- hook enqueue 的同步开销、失败率和 raw event 丢失率。
- sandbox/权限边界下，全局 hook 是否能稳定写入 collector queue。

## 1.6 后续动作

建议下一步：

1. 新开 Codex 会话，在 allowlist 内业务仓库执行一个小型真实任务。
2. 运行 `python3 -m collector.service --root /home/jichao/agent-trajectory` 消费 queue。
3. 运行 `python3 -m collector.report --root /home/jichao/agent-trajectory --write` 生成新的 report。
4. 检查 raw events 中真实 payload 的字段覆盖、pre/post correlation、sequence ordering、error/approval 可见性和 workspace/session 可见性。
5. 若真实 payload 不足，记录 Phase 0 blocker 并评估 wrapper CLI、shell history + artifact scanner 或人工 task boundary marker 降级路线。

本记录不提升正式知识，不声明 `single_pass_recoverable: true`。
