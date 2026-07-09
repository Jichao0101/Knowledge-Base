---
type: project_record
status: implemented_but_not_fully_verified
project: agent-trajectory
module: collector-scheduler
summary: "确认 agent-trajectory 采用 hook / collector / distiller 三层职责边界：hook 同步路径只做 allowlist + enqueue，collector 在 hook 外近实时或定时消费 payload 并生成 raw events，distiller 后续按 trajectory/session 批处理语义蒸馏；已在 /home/jichao/agent-trajectory 增加受锁保护的 scheduler 入口并完成单元测试与一次真实 queue 消费。"
sources:
  - "2026-07-09 当前对话：评估每次抓取后自动解析还是定时解析更优，并决定 hook 外异步近实时解析 + 定时批处理兜底"
  - "2026-07-09 当前对话：在 /home/jichao/agent-trajectory 增加 collector.scheduler、CLI schedule 子命令、lock、limit、write-report 和测试"
  - "02_Projects/agent-trajectory/agent_trajectory_initial_design.md"
  - "02_Projects/agent-trajectory/agent_trajectory_p0_implementation_and_hook_registration-2026-07-09.md"
scope: "agent-trajectory P0 后的解析调度设计与当前实现同步；覆盖 hook/collector/distiller 分层、定时解析与 daemon/loop 取舍、scheduler 实现、真实运行结果和幂等边界。"
risks:
  - "当前 scheduler 只完成 collector 层 raw event 消费与 report 刷新，不包含异步 Semantic Distillation。"
  - "真实运行结果来自当前本地 queue，尚未完成长期 daemon、systemd timer、overhead、丢失率或多任务稳定性验证。"
  - "当前重复处理主要依赖 collector_state.json 的 last_queue_line；若进程在 raw event append 后、state 保存前崩溃，仍存在重复 raw event 窗口。"
  - "本记录不提升正式知识，不声明 single_pass_recoverable: true。"
updated_at: 2026-07-09
---

# 1 Agent Trajectory Scheduler 与分层解析更新记录

## 1.1 背景

P0 实现完成后，hook 只抓取 payload 以避免每次 Codex lifecycle hook 调用耗时过久。这带来新的调度问题：payload 已进入本地 queue 后，是每次抓取后立即解析，还是定时解析、后台 daemon 解析更合适。

本轮结论是保持 P0 原有同步边界：hook 同步路径不直接解析，不启动 collector service，不运行 snapshot/report，不调用 LLM。payload 解析放到 hook 外的 collector 调度层执行；语义蒸馏继续放到更后的异步 distiller 层。

## 1.2 三层职责边界

当前方案明确为三层：

| 层级 | 职责 | 触发建议 | 同步成本边界 |
|---|---|---|---|
| Hook 层 | 读取 payload、识别 workspace、allowlist 判断、fail-open enqueue | Codex `UserPromptSubmit`、`PreToolUse`、`PostToolUse`、`Stop` | 只做本地 JSONL append；不得运行 collector、snapshot、report 或 LLM |
| Collector 层 | 消费 queue，把 payload 转为 append-only raw events，生成 ordering、artifact refs、baseline snapshot refs 和 Phase 0 report | hook 外定时任务、轻量 loop 或后续 daemon | 允许 stdlib 确定性解析；不做语义蒸馏 |
| Distiller 层 | 基于 raw events、snapshot、artifact index 生成 interpreted intent、decision point、causal link、failure tags 和 evidence chain | trajectory close、session close、空闲超时或批处理 | 可调用 LLM，但必须异步、可重跑，并保留 evidence chain |

该分层保留 raw collection 的低延迟和低侵入性，同时让语义解释与后验推断保持可审计、可重跑。

## 1.3 定时解析与 daemon/loop 取舍

评估结论：

- 不推荐在每次 hook 抓取后同步解析。它会把 collector 成本叠加到每个 Codex hook 调用上，放大 overhead，并使 hook fail-open 路径更复杂。
- 纯低频定时解析成本可控，但反馈延迟较高，真实 hook payload 字段、pre/post correlation 和 queue backlog 问题可能晚发现。
- 当前推荐混合方案：collector 层在 hook 外做近实时或短间隔定时消费；distiller 层按 session/trajectory 或低频批处理执行。

可选运行形态：

1. **Timer 模式**：例如每 30 到 60 秒执行一次 `collector.scheduler --limit N --write-report`。实现简单，适合 P0/P1 初期。
2. **Loop 模式**：`collector.scheduler --loop --interval 30` 保持轻量轮询，适合手动观察和短期试运行。
3. **Daemon 模式**：后续可封装为 systemd user service 或长期 daemon。进入 daemon 前需要补充长期运行、锁、日志、退出和错误恢复验证。

## 1.4 当前实现

代码仓库：`/home/jichao/agent-trajectory`。

本轮新增或更新：

- `collector/scheduler.py`：新增 hook 外调度入口，支持 `run_once`、`--loop`、`--interval`、`--limit` 和 `--write-report`。
- `collector/paths.py`：新增 `storage/collector.lock` 路径。
- `collector/cli.py`：新增 `schedule` 子命令。
- `tests/test_phase0.py`：新增 scheduler 测试，覆盖写 report、limit 分批消费和锁占用时跳过。
- `README.md`：补充低开销连续采集的推荐运行方式。

推荐命令：

```bash
python3 -m collector.scheduler --root /home/jichao/agent-trajectory --limit 100 --write-report
python3 -m collector.scheduler --root /home/jichao/agent-trajectory --loop --interval 30 --limit 100 --write-report
```

也可通过统一 CLI 调用：

```bash
python3 -m collector.cli schedule --root /home/jichao/agent-trajectory --limit 100 --write-report
```

## 1.5 验证结果

已执行：

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`
- 结果：8 个测试全部通过。
- `python3 -m collector.scheduler --root /home/jichao/agent-trajectory --limit 100 --write-report`

真实 scheduler 运行结果：

- `processed = 90`
- `last_queue_line = 91`
- `next_sequence_no = 92`
- `raw_events_file = /home/jichao/agent-trajectory/trajectories/raw_events.jsonl`
- `report_file = /home/jichao/agent-trajectory/trajectories/phase0_feasibility_report.json`
- Phase 0 report 显示 `total_events = 91`
- `raw_collection_llm_call_count = 0`
- `tool_correlation.missing_correlation_events = 0`
- `tool_correlation.phase0_blocker = false`
- `ordering.monotonic_sequence_valid = true`

边界说明：

- 该结果证明当前本地 queue 到 raw events/report 的 scheduler 路径可运行。
- 该结果不等价于长期 daemon 稳定性、真实任务完整采集率、hook overhead 或丢失率验证。
- report 是派生产物；本项目 current 只记录其关键指标，不把 report 默认作为项目事实源入口。

## 1.6 重复处理与幂等边界

当前 collector 不会因为 `storage/` 持续增量更新而从 `trajectories/raw_events.jsonl` 重新提取。默认增量边界是：

- 输入源：`storage/queue/hook_events.jsonl`
- 输出源：`trajectories/raw_events.jsonl`
- 游标状态：`storage/collector_state.json`
- 关键字段：`last_queue_line`

`collector.service.collect()` 读取 queue 时会跳过 `line_no <= last_queue_line` 的记录，因此正常多次运行 scheduler 时只处理新增 queue 行。

当前残余风险是 crash 窗口：若进程已 append raw event，但尚未保存更新后的 `collector_state.json` 就崩溃，下次可能重复处理同一个 `queued_envelope_id`。后续加固建议：

- 每条 event append 成功后立即原子保存 state，缩小批处理 crash 窗口。
- 启动时读取 raw events 中已有的 `queued_envelope_id` 集合，遇到已处理 envelope 直接跳过。
- 在 report 中增加重复 `queued_envelope_id` 统计。

## 1.7 后续动作

建议下一步：

1. 在真实新 Codex 会话中持续运行 timer 或 loop 模式，记录 hook overhead、queue backlog、丢失率和 tool pre/post correlation。
2. 补充 scheduler 幂等加固：按 event 保存 state、raw event envelope 去重和重复统计。
3. 若短期稳定，再封装 systemd user timer 或 daemon，并记录重启恢复行为。
4. Distiller 仍保持异步批处理，不进入 hook 同步路径；待 raw event 样本稳定后再设计 distillation run version、evidence chain 和 reviewer 流程。

本记录不提升正式知识，不声明 `single_pass_recoverable: true`。
