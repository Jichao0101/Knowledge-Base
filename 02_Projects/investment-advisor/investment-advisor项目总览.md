---
type: project_entry
status: active
scope: personal US equities investment research agent MVP project; project-specific source of current navigation, not reusable formal knowledge.
updated_at: 2026-06-05
---

# 1 investment-advisor 项目总览

## 1.1 项目定位

`/mnt/d/investment-advisor` 是个人美股投资研究 Agent 系统 MVP 仓库。系统定位为个人投资研究辅助，不做自动下单、不接入券商 API、不承诺收益，也不声称提供正式金融投顾服务。

所有报告和建议必须标记为 `research draft / 投资研究草案`。

## 1.2 当前事实源

| 类型 | 文件 |
|---|---|
| MVP 方案与实现记录 | [[02_Projects/investment-advisor/美股投资研究Agent系统MVP方案与实现记录-2026-06-05]] |
| Skill 启动器封装记录 | [[02_Projects/investment-advisor/Skill启动器封装与host调用记录-2026-06-05]] |
| 真实 provider 接入记录 | [[02_Projects/investment-advisor/真实Provider接入与shadow验证记录-2026-06-05]] |
| Codex Skill 方向修正记录 | [[02_Projects/investment-advisor/Codex投研Skill方向修正记录-2026-06-05]] |
| Codex Plugin 封装记录 | [[02_Projects/investment-advisor/CodexPlugin封装记录-2026-06-05]] |
| Codex Plugin marketplace 安装记录 | [[02_Projects/investment-advisor/CodexPluginMarketplace安装记录-2026-06-05]] |

## 1.3 当前仓库能力概览

- Python MVP 骨架已创建。
- 支持 mock market data provider、mock SEC evidence store、mock 多 agent votes。
- 支持 performance attribution、feedback memo、thesis memory、markdown report generation。
- 支持 demo 命令：`python -m investment_agents.main run-demo`。
- 支持 host-callable Skill 启动入口：`investment_advisor_skill.run(...)`。
- 支持 demo 与 shadow mode；当前 MVP 中所有 Skill launcher 运行均为 proposal-only。
- 支持 provider factory 与 `config_overrides`。
- SEC/EDGAR submissions metadata 已可 shadow 使用。
- OpenBB/yfinance market data 已可 shadow 使用。
- repo-local Skill 已修正为 Codex-native 多角色投研工作流，而不是 Python LLM 启动脚本。
- 仓库已整理为 Codex plugin 基础结构，包含 `.codex-plugin/plugin.json`、Skill、scripts、Python helper、configs、fixtures 和 tests。
- 已安装到 `personal-local` marketplace，cache 版本为 `0.1.0+codex.20260605095746`。
- 支持单元测试：`python -m unittest discover -s tests`。

## 1.4 当前边界

- OpenBB 与 SEC/EDGAR 已有 shadow adapter；默认运行仍使用 mock provider。
- LLM provider 未真实接入。
- Skill 的 LLM 推理由 Codex/子代理承担；Python 模块仅作为数据/证据/报告辅助工具。
- Plugin marketplace 已安装；新会话自然语言触发尚未验证。
- 不包含交易执行、券商账户、组合调仓或自动下单模块。
- feedback 输出为研究流程调整建议，不是交易指令。
- 本项目记录仍是项目区内容，未提升为正式知识。
