---
name: agent-workflow-migration
description: Bootstrap or sync the Agent Workflow three-side knowledge-base setup into another Obsidian knowledge base. Use when Codex needs to migrate AGENTS.md, 01_Knowledge/Agent Workflow docs, .codex/agents configs, logs templates, and 02_Projects/Agent Workflow current docs into a target root with one command. The plugin carries a bundled payload so it can migrate across hosts without depending on the source vault still being present. Do not use for partial manual edits, codebase-only migrations, or arbitrary repository restructuring.
---

# 1 Goal

Provide a one-command migration path for reusing this repository's Agent Workflow setup in another knowledge base, including cross-host migration from the plugin's bundled payload.

# 2 When To Use

- A new knowledge base needs the same three-side workflow scaffolding.
- An existing knowledge base needs to sync its Agent Workflow specs from this repo.
- The plugin has been copied to another machine and must bootstrap a new vault without reading the original source repo.
- The user wants repeatable migration instead of manually copying AGENTS, docs, and agent configs.

# 3 Do Not Use

- For one-off manual edits in the current repo.
- For code repository migrations without a knowledge-base root.
- For copying unrelated notes or archives.

# 4 Workflow

1. Confirm the target root path.
2. Run:

```bash
python3 plugins/agent-workflow-migrator/scripts/migrate_agent_workflow.py --target <target-root>
```

3. By default the command reads from the plugin's bundled `payload/`.
4. Use `--source <source-root>` only when you intentionally want to migrate from a live repo instead of the bundle.
5. Use `--dry-run` first when the target already contains content.
6. Use `--force` only when overwriting target files is intended.

# 5 What It Migrates

- `AGENTS.md`
- `01_Knowledge/Agent Workflow/`
- `.codex/agents/`
- `logs/`
- `02_Projects/Agent Workflow/`

# 6 Cross-Host Note

- The plugin is self-contained only when `payload/` is shipped with it.
- If you distribute just the script without `payload/`, cross-host migration will fail.

# 7 Validation

- Check the summary printed by the script.
- Verify the target contains the expected files and directories.
- If the target already has customized content, compare before using `--force`.
