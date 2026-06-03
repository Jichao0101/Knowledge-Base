# Codex plugin skill 集中注册与迁移方案

状态：已落地  
日期：2026-05-28  
适用范围：本地自研 Codex plugin/skill 的集中注册、迁移、runtime link、版本锁定与验证。

## 结论

采用“集中注册 + 分散源码”的方案。

`/mnt/d/codex-capability-registry` 是集中注册仓，不是所有能力源码的唯一仓。它负责：

- 记录 first-party / third-party ownership
- 锁定自研 plugin submodule commit
- 保存小型自研 skill 源码
- 生成 runtime symlink
- 保存 marketplace 模板
- 提供迁移和验证脚本

大型自研 plugin 继续保留独立仓库历史，以 Git submodule 方式接入 registry。

## ownership 分层

- `first_party_submodule`：自研 plugin，保留独立 Git 仓库和历史，通过 submodule 锁定版本。
- `first_party_embedded`：小型自研 skill，直接纳入 registry 的 `skills/`。
- `third_party_external`：第三方 skill/plugin，不纳入源码树，只在 manifest 中记录 runtime 路径、恢复来源或安装说明。

## 当前落地结构

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
    karpathy-guidelines/
    lark-doc-to-obsidian/
  sources/submodules/
    cutepower/
    subpower/
```

自研 plugin：

- `cutepower`：submodule，remote `git@github.com:Jichao0101/cutepower.git`
- `subpower`：submodule，remote `git@github.com:Jichao0101/subpower.git`

自研 embedded skill：

- `karpathy-guidelines`
- `lark-doc-to-obsidian`

第三方 skill：

- 不进入 registry `skills/`
- 保持在 `/home/jichao/.agents/skills/<name>` 的普通目录
- 在 `manifests/skills.yaml` 中标记为 `third_party_external`

## Runtime 链接策略

Plugin runtime 使用软链接：

```text
/home/jichao/.codex/plugins/cutepower -> /mnt/d/codex-capability-registry/sources/submodules/cutepower
/home/jichao/.codex/plugins/subpower -> /mnt/d/codex-capability-registry/sources/submodules/subpower
```

自研 embedded skill 使用软链接：

```text
/home/jichao/.agents/skills/karpathy-guidelines -> /mnt/d/codex-capability-registry/skills/karpathy-guidelines
/home/jichao/.agents/skills/lark-doc-to-obsidian -> /mnt/d/codex-capability-registry/skills/lark-doc-to-obsidian
```

第三方 skill 不链接到 registry。

## 验证方式

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

## 迁移到新设备

推荐流程：

```bash
git clone --recurse-submodules <registry-remote> codex-capability-registry
cd codex-capability-registry
scripts/install-runtime-links.sh
scripts/verify-runtime.sh
```

第三方 skill 需要通过其原始安装方式安装；若有可信备份，可按 `manifests/skills.yaml` 中记录的路径恢复。

## 风险与边界

- registry 不负责发布到官方 marketplace。
- registry 不修改 plugin/skill 内部逻辑。
- 第三方 skill 不能直接导入 registry 源码树。
- 推送 registry 到远程前，需要先创建或指定 registry 远程仓库。

## 本次写回说明

- allowed_paths：`/mnt/d/codex-capability-registry`，`/mnt/d/cutepower`，`/mnt/d/subpower`，`/home/jichao/.codex`，`/home/jichao/.agents/skills`，`/mnt/d/Knowledge-Base/02_Projects/codex-capability-registry`
- files_read：plugin/skill runtime 路径、registry Git 状态、manifest、runtime scripts
- files_written：本方案文档
- candidate_created：否
- source_notes_created：否
- promoted_to_knowledge：否
- missing_authorization：无
- promotion_blockers：本内容是项目方案，保留在项目区，未提升到正式知识区
- unresolved_items：registry 远程仓库尚未配置
