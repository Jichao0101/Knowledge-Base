---
type: project_implementation_record
status: active
project: investment-advisor
source: user task and local implementation in /mnt/d/investment-advisor
scope: Skill launcher wrapper and host-callable orchestration for the personal US equities investment research MVP.
updated_at: 2026-06-05
promoted_to_knowledge: false
---

# Skill 启动器封装与 host 调用记录

## 1 目标

将 `/mnt/d/investment-advisor` 仓库封装为一个 host-callable Skill 启动器，使 host 不需要手动运行：

```bash
python -m investment_agents.main run-demo
```

即可通过程序化入口启动个人美股投资研究 MVP。

目标接口：

```python
import investment_advisor_skill

result = investment_advisor_skill.run(
    demo=True,
    shadow_mode=True,
    report_date="2026-06-05",
    ticker="MSFT",
)
```

## 2 本次实现

新增或修改的关键文件：

- `/mnt/d/investment-advisor/investment_advisor_skill.py`
- `/mnt/d/investment-advisor/investment_agents/skill_runner.py`
- `/mnt/d/investment-advisor/skills/investment_advisor_skill/SKILL.md`
- `/mnt/d/investment-advisor/tests/test_skill_runner.py`
- `/mnt/d/investment-advisor/pyproject.toml`
- `/mnt/d/investment-advisor/README.md`
- `/mnt/d/investment-advisor/.gitignore`
- `/mnt/d/investment-advisor/investment_agents/main.py`

启动器返回 `SkillRunResult`，包含：

- `mode`
- `ticker`
- `report_date`
- `shadow_mode`
- `report`
- `feedback_memo`
- `markdown_report`
- `report_path`
- `feedback_memo_path`
- `agent_trace`
- `warnings`

## 3 内部调度链

`investment_agents.skill_runner.InvestmentAdvisorOrchestrator` 串联以下 MVP 角色：

1. OpenBB-style data layer：读取 mock market snapshot。
2. SEC/EDGAR evidence layer：读取本地 mock SEC filings。
3. TradingAgents-style research agents：生成 deterministic mock votes。
4. AttributionEngine：计算 raw、market-adjusted、sector-adjusted、residual、direction、calibration、risk、evidence scores。
5. FeedbackController：生成 prompt focus、confidence calibration、agent weight proposal、risk penalty proposal、thesis status proposal。
6. ThesisMemory：更新 thesis lifecycle proposal。
7. ReportGenerator：生成 markdown research draft 和 JSON feedback memo。

MVP 内部 agent 是 Python orchestration roles，不代表真实 LLM subagent 已接入。

## 4 Shadow mode 与 policy 边界

本次 review 后明确：

- Skill launcher 在当前 MVP 中所有模式均为 proposal-only。
- `shadow_mode=True` 额外标记为 shadow review。
- 即使底层 `FeedbackController` 在样本充足时可能返回 `policy_update_applied=True`，Skill launcher 也会强制改为 `False`。
- 真正的 policy apply 需要未来引入持久化 state 和人工 review gate 后再开放。

负反馈仍只输出研究流程调整建议：

- prompt focus
- confidence calibration proposal
- agent weight proposal
- risk penalty proposal
- thesis status proposal

不会输出：

- 自动下单
- broker/order API
- 自动调仓
- “确定买入/卖出”式指令

## 5 Host 可调用性修复

subpower reviewer 发现：仅在仓库 cwd 下放置 `investment_advisor_skill.py` 不足以让外部 host import。

修复：

- `pyproject.toml` 增加 setuptools build metadata。
- 包含 root module `investment_advisor_skill` 和 package `investment_agents`。
- 已执行 editable install：

```bash
python -m pip install -e . --no-deps
```

验证：

```bash
cd /mnt/d/Knowledge-Base
python -c "import investment_advisor_skill; r=investment_advisor_skill.run(demo=True, shadow_mode=True, write_outputs=False); print(r.mode, r.shadow_mode, r.report.ticker, r.feedback_memo.policy_update_applied, r.report.label)"
```

结果：

```text
demo True MSFT False research draft / 投资研究草案
```

## 6 验证结果

单元测试：

```bash
cd /mnt/d/investment-advisor
python -m unittest discover -s tests
```

结果：

```text
Ran 18 tests ... OK
```

CLI 兼容性：

```bash
python -m investment_agents.main run-demo
```

结果：

- `data/output/msft_2026-06-05_research_report.md`
- `data/output/msft_2026-06-05_feedback_memo.json`

Host import 验证：

- 从 `/mnt/d/Knowledge-Base` 可直接 `import investment_advisor_skill`。
- `shadow_mode=True` 返回 `policy_update_applied=False`。
- report label 保持 `research draft / 投资研究草案`。

## 7 测试覆盖新增

新增 `tests/test_skill_runner.py`，覆盖：

- host-callable `investment_advisor_skill.run(...)` 返回 `SkillRunResult`。
- shadow mode 写出 report 和 feedback memo。
- report 包含昨日反馈、Feedback Memo、SEC Evidence、agent votes、invalidation conditions、disclaimer、attribution audit inputs。
- `report_date` 可用于 report labeling，并在 demo data date 不一致时给出 warning。
- 无 aggressive trading / broker / order instruction。
- agent weight proposal 保持 5%、10%-45% 边界。
- 即使底层 controller 返回 applied，Skill launcher 也强制 proposal-only。

## 8 当前边界

- OpenBB 仍为 mock provider。
- SEC/EDGAR 仍为 local JSON mock。
- TradingAgents-style agents 仍为 deterministic mock votes。
- Skill launcher 是 Python API，不是独立长期 daemon。
- editable install 是当前 host import 的启用方式。
- 尚未实现持久化 policy state、human review gate 或真实 LLM agents。

## 9 后续建议

1. 增加真实 Codex/user-level skill 安装流程，避免依赖单仓 repo-local skill 文件。
2. 增加 provider contract tests 后再接入 OpenBB 与 SEC/EDGAR。
3. 增加 LLM agent adapter，并保持 `AgentVote` 结构化输出。
4. 增加 policy state persistence 和人工 review gate，再考虑 `policy_update_applied=True`。
5. 增加 report audit id、input snapshot hash 和 evidence source validation。

## 10 当前状态

状态：Skill launcher MVP complete，host-callable via editable install。

未提升到正式知识区的原因：

- 当前记录强绑定 `/mnt/d/investment-advisor` 项目。
- 启动器仍为 MVP 阶段。
- 真实 provider、LLM agent、policy persistence 和 review gate 尚未接入。

