---
type: project_implementation_record
status: active
project: investment-advisor
source: local implementation and shadow validation in /mnt/d/investment-advisor
scope: SEC/EDGAR and OpenBB provider adapter integration for the personal US equities investment research MVP.
updated_at: 2026-06-05
promoted_to_knowledge: false
---

# 真实 Provider 接入与 Shadow 验证记录

## 1 目标

在不破坏默认 mock demo、不改变 feedback 防线、不引入交易动作的前提下，将 `/mnt/d/investment-advisor` 推进到真实数据接口可 shadow 使用的阶段。

目标包括：

- 增加 provider protocol/factory，避免 orchestrator 直接硬编码 mock provider。
- 增加 SEC/EDGAR 只读 evidence adapter。
- 增加 OpenBB market data adapter。
- 允许 host 通过 `config_overrides` 临时切换 provider。
- 保持所有投资输出为 `research draft / 投资研究草案`。
- 保持 Skill launcher 全模式 proposal-only。

## 2 本次代码改动

关键文件：

- `/mnt/d/investment-advisor/investment_agents/providers.py`
- `/mnt/d/investment-advisor/investment_agents/skill_runner.py`
- `/mnt/d/investment-advisor/investment_advisor_skill.py`
- `/mnt/d/investment-advisor/configs/demo_config.json`
- `/mnt/d/investment-advisor/pyproject.toml`
- `/mnt/d/investment-advisor/tests/test_providers.py`
- `/mnt/d/investment-advisor/tests/test_skill_runner.py`
- `/mnt/d/investment-advisor/README.md`
- `/mnt/d/investment-advisor/docs/architecture.md`
- `/mnt/d/investment-advisor/skills/investment_advisor_skill/SKILL.md`

## 3 Provider seam

新增：

- `MarketDataProvider`
- `SecEvidenceProvider`
- `ProviderBundle`
- `build_provider_bundle(...)`

默认配置仍保持：

- `market_provider = "mock"`
- `sec_provider = "mock"`

真实 provider 只能通过显式配置或 `config_overrides` 启用。

## 4 SEC/EDGAR adapter

新增 `SecEdgarEvidenceStore`：

- 读取 SEC submissions metadata。
- 需要配置 CIK map。
- 需要合规 `sec_user_agent`，且 user-agent 必须包含 contact email。
- 输出 `SecEvidence`。
- 保留 filing type、filing date、accession number、SEC archive URL。

真实 SEC shadow smoke：

```python
investment_advisor_skill.run(
    demo=True,
    shadow_mode=True,
    write_outputs=False,
    config_overrides={
        "sec_provider": "sec_edgar",
        "sec_user_agent": "investment-advisor-mvp jichao@example.com",
    },
)
```

结果：

- trace 显示 `sec_edgar_submissions`。
- 返回 MSFT accession numbers：
  - `0001193125-26-224155`
  - `0001193125-26-191507`
  - `0001193125-26-191457`
- `policy_update_applied=False`。
- report label 保持 `research draft / 投资研究草案`。

## 5 OpenBB adapter

新增 `OpenBBMarketDataProvider`：

- 使用官方 OpenBB Python 入口：`from openbb import obb`。
- 调用形态：`obb.equity.price.historical(symbol=..., start_date=..., end_date=..., provider=...).to_df()`。
- 从 close price 序列计算 ticker、market benchmark、sector benchmark return。
- 输出 `MarketSnapshot`。

安装：

```bash
cd /mnt/d/investment-advisor
python -m pip install -e ".[openbb]"
```

安装结果：

- `openbb==4.7.2`
- `openbb-yfinance==1.6.3`

真实 OpenBB shadow smoke：

```python
investment_advisor_skill.run(
    demo=True,
    shadow_mode=True,
    write_outputs=False,
    config_overrides={
        "market_provider": "openbb",
        "openbb_provider": "yfinance",
        "market_start_date": "2026-06-01",
        "market_end_date": "2026-06-05",
    },
)
```

结果：

- trace 显示 `openbb_market_data`。
- 仍使用 mock SEC evidence。
- attribution audit inputs：
  - `raw_return`: `-0.07050725700364585`
  - `market_adjusted_return`: `-0.06859575436189223`
  - `sector_adjusted_return`: `-0.0572767890297607`
  - `residual_return`: `-0.0572767890297607`
- `policy_update_applied=False`。
- report label 保持 `research draft / 投资研究草案`。
- 未写报告文件。

## 6 `config_overrides`

`investment_advisor_skill.run(...)` 与 `run_skill(...)` 新增 `config_overrides` 参数。

用途：

- 一次性启用真实 provider。
- 避免为 shadow smoke 修改 `configs/demo_config.json`。
- 保持默认 demo 仍可重复、稳定、离线运行。

示例：

```python
result = investment_advisor_skill.run(
    demo=True,
    shadow_mode=True,
    write_outputs=False,
    config_overrides={
        "market_provider": "openbb",
        "openbb_provider": "yfinance",
        "sec_provider": "sec_edgar",
        "sec_user_agent": "investment-advisor-mvp your_email@example.com",
    },
)
```

## 7 测试与验证

测试命令：

```bash
cd /mnt/d/investment-advisor
python -m unittest discover -s tests
```

结果：

```text
Ran 25 tests ... OK
```

覆盖新增：

- provider factory 默认 mock。
- SEC user-agent 防线。
- SEC submissions JSON 到 `SecEvidence` 的映射。
- mock fixture loading。
- OpenBB historical price contract test。
- `config_overrides` 切换 SEC provider。
- `config_overrides` 切换 OpenBB market provider。
- provider source 写入 `agent_trace`。

默认 demo 回归：

```bash
python -m investment_agents.main run-demo
```

结果：

- 成功生成 report 和 feedback memo。
- 默认 trace 仍为 `mock_market_data` + `mock_sec_evidence`。

## 8 当前状态

状态：真实 SEC/EDGAR metadata 与 OpenBB/yfinance market data 已可 shadow 使用。

默认运行状态：

- 仍为 mock provider。
- 仍为 proposal-only。
- 仍为 research draft。
- 不生成交易指令。

## 9 当前边界

- SEC adapter 当前只读取 submissions metadata，不下载/解析完整 filing 文本。
- OpenBB adapter 当前只取 historical close 并计算简单区间收益。
- market benchmark 和 sector benchmark 当前由配置指定，默认 `SPY` 与 `XLK`。
- 尚未建立真实 provider replay fixture 文件落库流程。
- 尚未建立 provider failure fallback policy。
- 尚未接入真实 LLM research agents。
- 尚未持久化 policy state 或 thesis memory。

## 10 后续建议

1. 增加真实 provider replay fixture 写入流程，测试只依赖 replay fixture。
2. 将 OpenBB smoke 输出保存为 `04_Sources` 或项目区 evidence run record，再决定是否沉淀。
3. 增加 provider timeout、retry、fallback-to-mock 策略。
4. 增加 SEC filing document retrieval 与摘要来源标记。
5. 明确 market return 口径：交易日窗口、调整后价格、分红拆股处理、benchmark 选择。
6. 增加 live provider run 的人工审批 gate，避免自动长期运行消耗或误用。

## 11 未提升正式知识原因

- 当前内容绑定 `investment-advisor` 项目。
- 真实 provider 接入仍处于 shadow 验证阶段。
- OpenBB/SEC 使用方式尚未形成跨项目复用规范。
- 仍缺少长期稳定性、失败回退和 replay fixture 体系。

