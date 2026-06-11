---
type: project_decision_record
status: active
project: investment-advisor
source: user correction and local skill update in /mnt/d/investment-advisor
scope: Correct investment-advisor from Python launcher centric design to Codex-native multi-agent research skill.
updated_at: 2026-06-05
promoted_to_knowledge: false
---

# Codex 投研 Skill 方向修正记录

## 1 背景

用户指出当前骨架偏离原设计：此前实现偏向 `investment_advisor_skill.run(...)` 这类 Python 启动器，而目标应是一个 Codex Skill，能够响应自然语言任务，例如：

- “重点分析美股科技股”
- “分析 MSFT/NVDA 的投资 thesis”
- “复盘昨天的研究建议”

Skill 的核心不应是内置 LLM API 的 Python 脚本，而应是由 Codex/子代理执行的 TradingAgents-style 多角色投研工作流。

## 2 参考项目

参考：`https://github.com/hsliuping/TradingAgents-CN`

公开资料要点：

- TradingAgents-CN 是面向学习和研究的多智能体股票分析框架。
- 其公开说明强调多角色协作、数据源管理、报告导出、风险提示和研究/教育用途。
- 多角色协作形态包括分析师、研究员/多空辩论、风险管理、管理层综合等。
- 项目自身也明确不构成投资建议。

本项目仅借鉴高层 workflow pattern，不复制 TradingAgents-CN 代码，也不引入其实现。

## 3 本次修正

更新：

- `/mnt/d/investment-advisor/skills/investment_advisor_skill/SKILL.md`
- `/mnt/d/investment-advisor/skills/investment_advisor_skill/references/tradingagents-style-workflow.md`
- `/mnt/d/investment-advisor/tests/test_skill_definition.py`

修正后的 Skill 定位：

- 触发自然语言个人美股投研任务。
- Codex/subagents 执行多角色投研推理。
- Python 模块只作为 deterministic data/evidence/report helper。
- 不允许在 Python 中新增或调用 LLM API。
- 不提供交易执行。

## 4 新 Skill 工作流

触发后默认执行：

1. 解析用户目标：ticker、sector/theme、horizon、日期、是否允许 live data。
2. 如任务较宽泛，例如“美股科技股”，显式选择小 universe，如 `MSFT`、`NVDA`、`AAPL`、`GOOGL`、`AMD`。
3. 使用 Python helper 获取确定性数据或证据：
   - OpenBB/yfinance market snapshot。
   - SEC/EDGAR evidence。
   - mock 或 shadow snapshot。
4. 由 Codex/子代理执行角色：
   - Market/sector analyst
   - Fundamental analyst
   - SEC evidence analyst
   - Bull researcher
   - Bear researcher
   - Risk manager
   - Feedback/process controller
   - Report editor
5. 输出 markdown research draft。

## 5 Guardrails

- 所有结论必须标记 `research draft / 投资研究草案`。
- 不生成自动交易、broker API、order placement、仓位执行。
- 不使用“一日 raw return”直接改变 confidence、thesis status 或 agent weights。
- feedback 只输出研究流程建议：
  - prompt focus
  - confidence calibration proposal
  - agent weight proposal
  - risk penalty proposal
  - thesis status proposal

## 6 输出合同

最终报告必须包含：

- Scope and universe
- Data/evidence sources used
- Market and sector context
- Company/fundamental notes
- SEC/EDGAR evidence
- Bull case
- Bear case
- Risk factors and missing evidence
- Agent vote table
- Thesis status and invalidation conditions
- Feedback memo / process adjustment
- Disclaimer: `research draft / 投资研究草案`

## 7 验证

新增测试：

- `tests/test_skill_definition.py`

测试覆盖：

- Skill 能触发 “重点分析美股科技股”。
- Skill 明确是 Codex/subagents 工作流。
- Skill 包含 Market/sector analyst、Bull researcher、Bear researcher、Risk manager 等角色。
- Skill 明确禁止 Python LLM API。
- TradingAgents-style reference 存在，并包含研究辩论和 research draft guardrail。

验证结果：

```bash
cd /mnt/d/investment-advisor
python -m unittest discover -s tests
```

结果：

```text
Ran 27 tests ... OK
```

## 8 当前状态

状态：方向已纠正为 Codex-native multi-agent research Skill。

保留 Python 启动器和 provider adapter 的理由：

- 它们作为数据/证据/报告辅助工具存在。
- 不是 Skill 的 LLM 推理核心。
- 不应继续扩展为内置 LLM API 系统。

## 9 后续建议

1. 若要正式安装 Skill，应把 `skills/investment_advisor_skill/` 安装到 Codex 可发现的 user-level skills 目录，或通过 plugin packaging 管理。
2. 为真实任务增加 subagent delegation 模板。
3. 增加示例任务 fixture，例如“重点分析美股科技股”的完整输出样例。
4. 将 Python provider 输出改为 evidence packet，供 Codex roles 使用，而不是直接生成最终投研判断。

