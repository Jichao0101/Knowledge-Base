---
type: project_module_index
status: active
project: DMS
module: Issue Analysis Skill
scope: DMS 问题分析 Skill 的方案、实现、验证和维护记录入口。
updated_at: 2026-07-30
---

# 1 DMS 问题分析 Skill 模块索引

## 1.1 当前入口

- [[02_Projects/DMS/10_Issue_Analysis_Skill/DMS问题分析Skill项目方案]]：当前架构、输入模式、阶段契约、降级策略、Jira 回写边界和实施状态。
- [[02_Projects/DMS/10_Issue_Analysis_Skill/DMS R核问题分析流程]]：R 核疲劳、分心、抽烟和接打电话排查规则的项目来源文档。
- [[02_Projects/DMS/10_Issue_Analysis_Skill/Current Maintenance Records/2026-07-13-ADASL2-1565真实端到端验证与Jira中文写回修复]]：首个真实端到端 case、证据不足结论、Jira 中文化和 Wiki Markup 修复记录。
- [[02_Projects/DMS/10_Issue_Analysis_Skill/Current Maintenance Records/2026-07-27-R核Reference分层与Skill瘦身状态同步]]：R 核 reference/strategy 分层、Skill 瘦身、验证结果和未解除的 analyser 缺口。
- [[02_Projects/DMS/10_Issue_Analysis_Skill/Current Maintenance Records/2026-07-29-R核远程规则更新审查与本地同步]]：远程规则更新审查、用户确认的修正、本地来源同步及 reference/strategy 待同步缺口。
- [[02_Projects/DMS/10_Issue_Analysis_Skill/Current Maintenance Records/2026-07-30-Skill当前实现全量差异同步]]：当前 Skill 相对原方案的全量差异，包括 R→A 反向分析、内置映射、Jira 评论数据路径解析、Evidence Package v2、验证结果与未解除边界。

## 1.2 当前状态

- 项目状态：阶段三验证中；已用 `ADASL2-1565` 完成首个在线飞书 → Jira/Data → Evidence Package → A 核准备 → Agent review → Conclusion → 真实 Jira 新增评论闭环，但结论为 `partial/INSUFFICIENT_EVIDENCE/low`，仍未形成真实根因闭环。
- 当前采集主链路：飞书表格只读 Jira ID 与业务上下文 → Jira Parser 采集全部评论 → 路径片段提取 → Agent/LLM 在 `\\192.168.1.111\Global_VIP\J6B_DMSRain` 下受限容错检索 → 确定性路径校验 → Data Loader → Evidence Package v2 → R-core 自动阶段 `skipped` → A-core Analyser → 结论回写 Jira。
- 直接日志模式只读取用户明确授权的日志路径，跳过飞书、Jira、Evidence Package 和自动写回；Agent 可执行带原始位置的 `manual_r_core_review`，再继续 A 核分析。
- 飞书表格仅作为只读问题入口，不承担分析结果回写。
- 表格不再读取或要求数据路径；没有数据路径字段不阻塞候选。Jira 评论路径由确定性脚本提取字符和检索词，LLM 只负责候选召回/排序，不具有绕过路径校验的权限。
- 无评论提示、零候选、多候选、共享根不可访问、候选不存在、不可读或越界时固定为 `blocked_user_confirmation/continue_allowed=false`，必须让用户确认地址并停止后续分析。
- Jira Parser 使用本地 Bearer token 做只读采集，已通过真实 Issue 验证；凭据不进入版本控制或知识库。
- Data Loader 已完成只读清单、hash 和候选分类验证，`calmcar_camera_service` 作为 A 核日志候选。
- Evidence Package Builder 已升级为 v2，强制消费 `path_resolution.json` 并校验 Jira ID、`resolved/continue_allowed`、实际 `access_path` 与 Data Loader 源路径一致；package 同时保存规范 UNC 路径、实际访问路径及四个输入 hash。待用户确认的路径不能降级构建 partial package。
- R 核 reference/strategy 已同步到项目来源 SHA-256 `70745baf9fe48903b9fdc57dc0da196fa5500e306ed8a54f81935a053466486f`，schema/revision 为 4，当前状态为 `reference_ready/analyser_not_implemented`。它已包含六类行为间歇容忍、抽烟完整规则、正式报警反向分析、四类独立时长口径和 `conforming/nonconforming/unknown` 三态合同；确定性 analyser 仍未实现，自动阶段继续固定为 `skipped/r_core_analyser_not_available`。
- R 核三态结果无论为何都必须继续 A 核。`r-a-core-alignment.md` 已固化 J6B A→R 版本化映射、同一物理 A/R 日志 marker 分流、禁止未来样本回配，以及延迟、丢失、重复、乱序和陈旧数据检查；运行 profile 不可确认时标记 `mapping_version_unverified`，普通 case 不访问源码或协议。
- A 核分析已实现全部候选日志的物理行索引、签名 census、错误/初始化/低频签名召回、问题时间 seed、跨线程 correlation 扩展、字符预算和原始位置追溯；输出初始状态为 `partial/pending_agent_review`。
- A 核查询规则固定在 Skill reference 中并通过修改 Skill 手工更新；普通问题分析不读取 DMS 源码、不自动生成 reference、不把单次 case 临时关键词静默固化。
- Conclusion Synthesizer 已实现 Evidence Package/A-core/selection hash 与 evidence ID 一致性门禁、pending review 降级、R/跨核归属禁用、置信度封顶、独立原子输出和 Jira 回写隔离；结论策略同样只能通过显式修改 Skill 手工更新。
- Jira 写回默认自动新增评论，不要求提交确认；目标锁定在 conclusion，提交前按稳定 analysis marker 查询既有评论，命中后跳过 POST。该去重覆盖普通重试，但并发查询—提交仍可能重复，不是服务端强幂等。
- 自动写回只允许新增评论，保存 comment ID/响应/本地工件，不修改 Jira 字段或既有评论；mock 自动提交、dry-run、partial 披露、重复 marker、远端失败和输出边界已验证。
- Jira 用户可见摘要和分析条目现在必须包含中文；评论按 Jira Wiki Markup 使用 `h2.` / `h3.`、`*` 和 `bq.`，并禁止 Markdown 行首 `#`，避免被 renderer 解释为重复的 `1. 1. 1.`。
- 首次英文评论 `8654391` 作为历史事实保留；中文纠正版评论 `8654396` 已成功新增。当前 Skill commit 为 `88a4170`，仓库全量 83 项单元测试和 `git diff --check` 通过。
- 当前真实验证仍只覆盖 1 个证据不足的旧链路 case；Jira 评论路径解析尚未连接真实共享盘完成端到端验证。R 核 analyser、真实 DMS 状态链、多 case 诊断有效性、内置映射的运行 profile 兼容性、并发去重和 recoverability verification 仍未闭环。

## 1.3 维护规则

- 实现、验证或接口发生变化时，先更新项目方案或新增对应记录，再同步本索引。
- 在完成独立 recoverability verification 前，不建立 `single_pass_recoverable: true` 的 current 状态。
- Jira、日志格式、Jira 评论路径提示和飞书表格检索策略确定后，记录具体字段与版本，避免将临时约定写成稳定事实。
- 路径解析规则升级必须保持“LLM 只召回候选、脚本执行硬校验”的边界；不得把近似匹配、用户确认或历史 case 路径直接当作可访问性证明。
- A 核规则升级必须显式修改 strategy/reference、提升规则版本并运行回归测试；不得在单次问题分析中自动学习或写回固定规则。
- R 核规则升级必须显式修改 strategy/reference、提升规则版本并校验项目来源快照；普通灵敏度哈欠和 `isMonitoringEnabled` 门禁关系等未定义项不得被自动补全。
- 结论规则升级必须显式修改 conclusion policy/reference、提升策略版本并运行回归测试；不得在单次问题分析中读取源码、自动学习或写回固定规则。
- Jira 写回规则升级必须显式修改 writeback policy/reference、提升策略版本并运行回归测试；不得在运行时自动扩大为 Jira 字段修改、评论更新或删除。
- Jira Server v2 评论模板必须使用 Jira Wiki Markup，不得使用 Markdown 行首 `#` 标题；中文正文门禁必须在网络访问前执行。
