---
type: project_implementation_record
status: active
project: investment-advisor
source: local implementation in /mnt/d/investment-advisor
scope: Package investment-advisor repository as a Codex plugin containing skill, Python helpers, configs, data fixtures, scripts, and tests.
updated_at: 2026-06-05
promoted_to_knowledge: false
---

# Codex Plugin 封装记录

## 1 目标

将 `/mnt/d/investment-advisor` 从“普通项目仓库 + repo-local Skill”整理为完整 Codex plugin。

原因：

- 单独安装 `skills/` 不可用，会丢失 Python helper、provider adapter、配置、样例数据和测试。
- Skill 只是入口和工作流说明。
- 完整能力需要 plugin 承载 Skill、scripts、Python package、configs、fixtures 和 tests。

## 2 本次实现

新增：

- `/mnt/d/investment-advisor/.codex-plugin/plugin.json`
- `/mnt/d/investment-advisor/scripts/collect_evidence.py`
- `/mnt/d/investment-advisor/scripts/run_shadow_snapshot.py`
- `/mnt/d/investment-advisor/tests/test_plugin_manifest.py`

调整：

- Skill 目录从 `skills/investment_advisor_skill/` 规范化为 `skills/investment-advisor/`。
- Skill frontmatter 修复为合法 YAML。
- `tests/test_skill_definition.py` 路径同步到新 Skill 目录。

## 3 Plugin manifest

插件名：

```text
investment-advisor
```

Manifest：

```text
/mnt/d/investment-advisor/.codex-plugin/plugin.json
```

Manifest 声明：

- `skills: "./skills/"`
- display name: `Investment Advisor`
- default prompts:
  - `重点分析美股科技股`
  - `分析 MSFT 和 NVDA 的投资 thesis`
  - `复盘昨天的美股研究建议`

## 4 Plugin 内部组成

```text
.codex-plugin/plugin.json
skills/investment-advisor/SKILL.md
skills/investment-advisor/references/tradingagents-style-workflow.md
scripts/collect_evidence.py
scripts/run_shadow_snapshot.py
investment_agents/
configs/demo_config.json
data/sample_market_data/
data/sample_sec_filings/
data/sample_previous_reports/
tests/
pyproject.toml
```

## 5 Scripts

### 5.1 `scripts/collect_evidence.py`

用途：

- 收集 market snapshot 与 SEC evidence。
- 输出 JSON evidence packet。
- 供 Codex 多角色投研流程读取。
- 不输出 LLM 结论，不构成投资建议。

### 5.2 `scripts/run_shadow_snapshot.py`

用途：

- 运行 proposal-only shadow snapshot。
- 输出 feedback memo、agent trace 和 markdown draft。
- 用于 Codex synthesis 的辅助输入。
- 不应用 policy，不交易。

## 6 验证

Plugin validator：

```bash
python3 /home/jichao/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py /mnt/d/investment-advisor
```

结果：

```text
Plugin validation passed: /mnt/d/investment-advisor
```

Unit tests：

```bash
cd /mnt/d/investment-advisor
python -m unittest discover -s tests
```

结果：

```text
Ran 29 tests ... OK
```

Script smoke：

```bash
python scripts/collect_evidence.py --ticker MSFT
python scripts/run_shadow_snapshot.py --ticker MSFT
```

结果：

- 两个脚本均可输出 JSON。
- 默认 provider 仍为 mock。
- `policy_update_applied=false`。
- 输出声明不构成投资建议。

## 7 当前状态

状态：当前仓库已具备 Codex plugin 基础结构。

尚未完成：

- 尚未创建/更新 personal marketplace entry。
- 尚未执行 plugin reinstall/cachebuster 流程。
- 尚未在新 Codex 会话中验证 marketplace 发现。

## 8 后续建议

1. 如果要在 Codex app 中安装使用，下一步应按 personal marketplace 流程创建或更新 marketplace entry。
2. 使用 plugin update/cachebuster 流程，而不是手动复制 skill。
3. 增加 `references/roles.md` 和 `references/report-template.md`，进一步产品化多角色投研流程。
4. 增加 end-to-end 示例任务：`重点分析美股科技股`。

## 9 未提升正式知识原因

- 当前记录是项目封装过程事实。
- plugin 仍处于本地开发状态。
- marketplace 安装和新会话发现尚未验证。

