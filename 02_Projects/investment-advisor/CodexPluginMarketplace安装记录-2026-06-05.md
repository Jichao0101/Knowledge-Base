---
type: project_implementation_record
status: active
project: investment-advisor
source: local personal marketplace installation for /mnt/d/investment-advisor
scope: Install investment-advisor plugin into personal-local marketplace and Codex plugin cache.
updated_at: 2026-06-05
promoted_to_knowledge: false
---

# Codex Plugin Marketplace 安装记录

## 1 目标

将 `/mnt/d/investment-advisor` 整理后的 Codex plugin 安装到本地 Codex personal marketplace，使 Codex 能从 `personal-local` marketplace 发现并加载该 plugin。

## 2 Marketplace

Marketplace 文件：

```text
/home/jichao/.agents/plugins/marketplace.json
```

Marketplace name：

```text
personal-local
```

新增 entry：

```json
{
  "name": "investment-advisor",
  "source": {
    "source": "local",
    "path": "./.codex/plugins/investment-advisor"
  },
  "policy": {
    "installation": "AVAILABLE",
    "authentication": "ON_INSTALL"
  },
  "category": "Productivity"
}
```

## 3 Plugin source

最终 source：

```text
/home/jichao/.codex/plugins/investment-advisor
```

处理过程：

- 初始尝试使用 symlink 指向 `/mnt/d/investment-advisor`。
- 安装后发现 cache 中包含源仓库 `.git`，不够干净。
- 已改为干净 source 目录，只复制 plugin 需要的文件：
  - `.codex-plugin`
  - `skills`
  - `scripts`
  - `investment_agents`
  - `configs`
  - `data`
  - `docs`
  - `tests`
  - `pyproject.toml`
  - `README.md`
  - `AGENTS.md`

干净 source 不包含：

- `.git`
- `__pycache__`
- `*.egg-info`

## 4 Cachebuster

已通过 plugin-creator update helper 更新 manifest：

```bash
python3 /home/jichao/.codex/skills/.system/plugin-creator/scripts/update_plugin_cachebuster.py /mnt/d/investment-advisor
```

版本从：

```text
0.1.0
```

更新为：

```text
0.1.0+codex.20260605095746
```

## 5 安装命令

```bash
codex plugin add investment-advisor@personal-local
```

结果：

```text
Added plugin `investment-advisor` from marketplace `personal-local`.
Installed plugin root: /home/jichao/.codex/plugins/cache/personal-local/investment-advisor/0.1.0+codex.20260605095746
```

## 6 验证

Source validator：

```bash
python3 /home/jichao/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py /home/jichao/.codex/plugins/investment-advisor
```

结果：

```text
Plugin validation passed: /home/jichao/.codex/plugins/investment-advisor
```

Cache validator：

```bash
python3 /home/jichao/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py /home/jichao/.codex/plugins/cache/personal-local/investment-advisor/0.1.0+codex.20260605095746
```

结果：

```text
Plugin validation passed: /home/jichao/.codex/plugins/cache/personal-local/investment-advisor/0.1.0+codex.20260605095746
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

## 7 当前状态

状态：`investment-advisor` 已安装到 `personal-local` marketplace 的 Codex plugin cache。

安装路径：

```text
/home/jichao/.codex/plugins/cache/personal-local/investment-advisor/0.1.0+codex.20260605095746
```

后续验证建议：

- 开启新 Codex 会话，测试自然语言触发：
  - “重点分析美股科技股”
  - “分析 MSFT 和 NVDA 的投资 thesis”
  - “复盘昨天的美股研究建议”

## 8 未解决项

- 尚未在新会话中验证 skill 自动触发。
- 后续开发时需要再次运行 cachebuster + `codex plugin add investment-advisor@personal-local`。

