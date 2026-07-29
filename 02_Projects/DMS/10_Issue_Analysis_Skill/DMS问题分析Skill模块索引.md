---
type: project_module_index
status: active
project: DMS
module: Issue Analysis Skill
scope: DMS 问题分析 Skill 的方案、实现、验证和维护记录入口。
updated_at: 2026-07-29
---

# 1 DMS 问题分析 Skill 模块索引

## 1.1 当前入口

- [[02_Projects/DMS/10_Issue_Analysis_Skill/DMS问题分析Skill项目方案]]：当前初版架构、阶段契约、降级策略、Jira 回写边界和实施建议。
- [[02_Projects/DMS/10_Issue_Analysis_Skill/DMS R核问题分析流程]]：R 核疲劳、分心、抽烟和接打电话排查规则的项目来源文档。
- [[02_Projects/DMS/10_Issue_Analysis_Skill/Current Maintenance Records/2026-07-13-ADASL2-1565真实端到端验证与Jira中文写回修复]]：首个真实端到端 case、证据不足结论、Jira 中文化和 Wiki Markup 修复记录。
- [[02_Projects/DMS/10_Issue_Analysis_Skill/Current Maintenance Records/2026-07-27-R核Reference分层与Skill瘦身状态同步]]：R 核 reference/strategy 分层、Skill 瘦身、验证结果和未解除的 analyser 缺口。
- [[02_Projects/DMS/10_Issue_Analysis_Skill/Current Maintenance Records/2026-07-29-R核远程规则更新审查与本地同步]]：远程规则更新审查、用户确认的修正、本地来源同步及 reference/strategy 待同步缺口。

## 1.2 当前状态

- 项目状态：阶段三验证中；已用 `ADASL2-1565` 完成首个在线飞书 → Jira/Data → Evidence Package → A 核准备 → Agent review → Conclusion → 真实 Jira 新增评论闭环，但结论为 `partial/INSUFFICIENT_EVIDENCE/low`，仍未形成真实根因闭环。
- 已确认主链路：飞书表格读取 Jira ID 和数据路径 → Jira Parser 与 Data Loader → Evidence Package → R-core Analyser → A-core Analyser → 结论回写 Jira。
- 飞书表格仅作为只读问题入口，不承担分析结果回写。
- Jira Parser 使用本地 Bearer token 做只读采集，已通过真实 Issue 验证；凭据不进入版本控制或知识库。
- Data Loader 已完成只读清单、hash 和候选分类验证，`calmcar_camera_service` 作为 A 核日志候选。
- Evidence Package Builder 已完成输入一致性校验、原子构建、阶段状态、缺失证据和 artifact hash；已使用真实 Jira/Data 输入与 synthetic 飞书候选完成集成验证，在线飞书端到端验证仍待完成。
- R 核项目来源文档已于 2026-07-29 同步新规则，新增六类检测的间歇 `false` 容忍窗口，补齐抽烟规则，并修正危险报警信号名、灵敏度措辞、误报笔误和遮挡/无人脸优先级。既有 Skill reference/strategy 仍锁定旧 SHA-256 快照，当前为 `source_updated/reference_sync_pending/analyser_not_implemented`；在完成转换和回归验证前不得视为与最新来源一致。R 核运行阶段继续固定为 `skipped/r_core_analyser_not_available`，最终结论不得确认 R 核或跨核根因。
- A 核分析已实现全部候选日志的物理行索引、签名 census、错误/初始化/低频签名召回、问题时间 seed、跨线程 correlation 扩展、字符预算和原始位置追溯；输出初始状态为 `partial/pending_agent_review`。
- A 核查询规则固定在 Skill reference 中并通过修改 Skill 手工更新；普通问题分析不读取 DMS 源码、不自动生成 reference、不把单次 case 临时关键词静默固化。
- Conclusion Synthesizer 已实现 Evidence Package/A-core/selection hash 与 evidence ID 一致性门禁、pending review 降级、R/跨核归属禁用、置信度封顶、独立原子输出和 Jira 回写隔离；结论策略同样只能通过显式修改 Skill 手工更新。
- Jira 写回默认自动新增评论，不要求提交确认；目标锁定在 conclusion，提交前按稳定 analysis marker 查询既有评论，命中后跳过 POST。该去重覆盖普通重试，但并发查询—提交仍可能重复，不是服务端强幂等。
- 自动写回只允许新增评论，保存 comment ID/响应/本地工件，不修改 Jira 字段或既有评论；mock 自动提交、dry-run、partial 披露、重复 marker、远端失败和输出边界已验证。
- Jira 用户可见摘要和分析条目现在必须包含中文；评论按 Jira Wiki Markup 使用 `h2.` / `h3.`、`*` 和 `bq.`，并禁止 Markdown 行首 `#`，避免被 renderer 解释为重复的 `1. 1. 1.`。
- 首次英文评论 `8654391` 作为历史事实保留；中文纠正版评论 `8654396` 已成功新增。R 核 reference 分层与 Skill 瘦身后，Skill 校验、来源 hash/引用一致性检查、`git diff --check` 和仓库全量 55 项测试通过。
- 当前验证只覆盖 1 个证据不足的真实 case；R 核规则虽已进入 Skill reference，analyser 仍未实现且运行时继续跳过，真实 DMS 状态链、多 case 诊断有效性、并发去重和 recoverability verification 仍未闭环。

## 1.3 维护规则

- 实现、验证或接口发生变化时，先更新项目方案或新增对应记录，再同步本索引。
- 在完成独立 recoverability verification 前，不建立 `single_pass_recoverable: true` 的 current 状态。
- Jira、日志格式和飞书表格检索策略确定后，记录具体字段与版本，避免将临时约定写成稳定事实。
- A 核规则升级必须显式修改 strategy/reference、提升规则版本并运行回归测试；不得在单次问题分析中自动学习或写回固定规则。
- R 核规则升级必须显式修改 strategy/reference、提升规则版本并校验项目来源快照；普通灵敏度哈欠和 `isMonitoringEnabled` 门禁关系等未定义项不得被自动补全。
- 结论规则升级必须显式修改 conclusion policy/reference、提升策略版本并运行回归测试；不得在单次问题分析中读取源码、自动学习或写回固定规则。
- Jira 写回规则升级必须显式修改 writeback policy/reference、提升策略版本并运行回归测试；不得在运行时自动扩大为 Jira 字段修改、评论更新或删除。
- Jira Server v2 评论模板必须使用 Jira Wiki Markup，不得使用 Markdown 行首 `#` 标题；中文正文门禁必须在网络访问前执行。
