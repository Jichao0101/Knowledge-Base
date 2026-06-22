# 1 Codex plugin skill 集中注册与迁移方案

状态：已落地  
日期：2026-06-16  
适用范围：本地 Codex plugin/skill 的集中注册、能力摘要、portable source、安装策略、runtime link、版本锁定与验证。

## 1.1 结论

采用“集中注册 + 分散源码”的方案。

`/mnt/d/codex-capability-registry` 是集中注册仓，不是所有能力源码的唯一仓。它负责：

- 记录 first-party / third-party ownership
- 记录能力摘要和描述来源
- 记录 portable source 事实、安装策略和验证规则
- 锁定自研 plugin submodule commit
- 保存小型自研 skill 源码
- 生成 runtime symlink
- 保存 marketplace 模板
- 提供迁移和验证脚本

大型自研 plugin 继续保留独立仓库历史，以 Git submodule 方式接入 registry。

## 1.2 ownership 分层

- `first_party_submodule`：自研 plugin，保留独立 Git 仓库和历史，通过 submodule 锁定版本。
- `first_party_embedded`：小型自研 skill，直接纳入 registry 的 `skills/`。
- `third_party_external`：第三方 skill/plugin，不纳入源码树，只在 manifest 中记录能力摘要、provider/source hint、安装策略和可信恢复来源。

## 1.3 Manifest 字段策略

`manifests/*.yaml` 是能力注册表，不是本机 runtime 快照。

保留字段：

- `name` / `ownership`：能力标识与归属分层。
- `summary`：面向检索和人工判断的简短简介。
- `description_source`：一方能力指向仓库内权威描述；三方能力标记为外部 runtime frontmatter 快照来源。
- `source.distribution`：区分 `bundled`、`git_submodule`、`external`。
- `source.path`：仅用于随仓库迁移的一方源码相对路径。
- `source.commit`：仅用于 submodule plugin 版本锁定。
- `source.restore_from`：仅作为三方能力在已知机器上的可信恢复线索。
- `install.strategy`：表达安装方式，例如从 registry 建 symlink、从 provider 安装或从备份恢复。
- `verification`：表达验证约束，例如需要 `SKILL.md`、需要 plugin manifest、禁止三方能力 symlink 回 registry。

删除或避免字段：

- 一方 skill 的绝对 `runtime.skill_path` 和 `runtime.link_target`。
- plugin 的绝对 `runtime.codex_plugin_path` 和 marketplace symlink 目标路径。
- 三方 skill 的本机 `source.path`。
- 重复的 `install_hint` 文本。

原因：

- 一方自研 skill 固定在 registry `skills/<name>`，拷贝仓库即可获得源码，runtime/link 路径可由脚本推导。
- 三方 skill 不随 registry 迁移，本机 runtime 路径和 symlink 目标没有跨机器语义。
- 能力简介比路径更影响发现、判断和维护，应作为 manifest 的一等字段。

## 1.4 当前落地结构

Registry 仓库：

```text
/mnt/d/codex-capability-registry
  .gitmodules
  README.md
  docs/
    migration-plan.md
    sync-procedure.md
  manifests/
    plugins.yaml
    skills.yaml
  marketplaces/
    personal-local.marketplace.json
  scripts/
    install-runtime-links.sh
    verify-runtime.sh
  skills/
    deep-module-design-review/
    interface-abstraction-implementation-guard/
    karpathy-guidelines/
    knowledge-base-structure-builder/
    lark-doc-to-obsidian/
    module-comment-and-naming-governance/
  sources/submodules/
    cutepower/
    subpower/
```

自研 plugin：

- `cutepower`：submodule，remote `git@github.com:Jichao0101/cutepower.git`
- `subpower`：submodule，remote `git@github.com:Jichao0101/subpower.git`

自研 embedded skill：

- `deep-module-design-review`
- `interface-abstraction-implementation-guard`
- `karpathy-guidelines`
- `knowledge-base-structure-builder`
- `lark-doc-to-obsidian`
- `module-comment-and-naming-governance`

第三方 skill：

- 不进入 registry `skills/`
- 保持在 `/home/jichao/.agents/skills/<name>` 的普通目录
- 在 `manifests/skills.yaml` 中标记为 `third_party_external`
- manifest 不记录三方本机 runtime path；只保留 provider/source hint、安装策略和必要的可信备份路径

## 1.5 Runtime 链接策略

Plugin runtime 使用软链接：

```text
/home/jichao/.codex/plugins/cutepower -> /mnt/d/codex-capability-registry/sources/submodules/cutepower
/home/jichao/.codex/plugins/subpower -> /mnt/d/codex-capability-registry/sources/submodules/subpower
```

自研 embedded skill 使用软链接：

```text
/home/jichao/.agents/skills/<first_party_skill> -> /mnt/d/codex-capability-registry/skills/<first_party_skill>
```

第三方 skill 不链接到 registry。

`scripts/install-runtime-links.sh` 和 `scripts/verify-runtime.sh` 从 manifest 的 `ownership` 读取能力列表；plugin 名单不再在脚本中硬编码。

## 1.6 验证方式

在 registry 根目录运行：

```bash
scripts/verify-runtime.sh
```

当前验证结果：`runtime verification passed`

验证覆盖：

- submodule commit 与 `manifests/plugins.yaml` 一致
- plugin runtime link 指向 `sources/submodules/*`
- 自研 skill runtime link 指向 `skills/*`
- 第三方 skill 是普通 runtime 目录
- 第三方 skill 未污染 registry `skills/`

## 1.7 迁移到新设备

推荐流程：

```bash
git clone --recurse-submodules <registry-remote> codex-capability-registry
cd codex-capability-registry
scripts/install-runtime-links.sh
scripts/verify-runtime.sh
```

第三方 skill 需要通过其原始安装方式安装；若有可信备份，可按 `manifests/skills.yaml` 中记录的路径恢复。

当前三方恢复语义：

- 默认 `scripts/install-runtime-links.sh` 不恢复三方 skill，只报告缺失项。
- 显式执行 `scripts/install-runtime-links.sh --restore-third-party` 时，才会按 `source.restore_from` 恢复三方 runtime 目录。
- 恢复后的三方 skill 必须是普通 runtime 目录，不能是指向 registry 的 symlink。

## 1.8 风险与边界

- registry 不负责发布到官方 marketplace。
- registry 不修改 plugin/skill 内部逻辑。
- 第三方 skill 不能直接导入 registry 源码树。
- 推送 registry 到远程前，需要先创建或指定 registry 远程仓库。

## 1.9 本次写回说明

- allowed_paths：`/mnt/d/codex-capability-registry`，`/home/jichao/.agents/skills`，`/mnt/d/Knowledge-Base/README.md`，`/mnt/d/Knowledge-Base/02_Projects/项目总览.md`，`/mnt/d/Knowledge-Base/02_Projects/codex-capability-registry`
- files_read：registry README/docs、manifest、runtime scripts、plugin manifest、skill frontmatter、知识库入口与项目记录
- files_written：registry manifest/scripts/docs，知识库总入口，项目总览，本方案文档
- candidate_created：否
- source_notes_created：否
- promoted_to_knowledge：否
- missing_authorization：无
- promotion_blockers：本内容是项目方案，保留在项目区，未提升到正式知识区
- unresolved_items：registry 远程仓库状态未在本次任务中处理
