---
type: structure_audit
status: active
scope: 记录知识库结构化、current 标准化、总览内容化的当前迁移状态；不作为具体主题事实源。
updated_at: 2026-07-13
supersedes:
  - 02_Projects/Knowledge-Base/知识库结构审计-2026-06-05.md
---

# 1 知识库结构审计 Current

## 1.1 当前决策

知识库入口采用“内容简介 + 入口分流”。结构状态不放在读者主入口中心，而集中记录在本审计文件中。知识库自身维护已作为独立项目纳入项目区，默认入口为 [[02_Projects/Knowledge-Base/知识库维护治理项目总览]]。仓库 `AGENTS.md` 当前同时承担知识写入前门禁与自动化禁区的硬政策权威，工作流、机器规则和工具实现仍归 knowledge-base skill 所有。

## 1.2 分区结构状态

| 分区 | 当前状态 |
|---|---|
| `01_Knowledge` | 已新增正式知识总览和主要一级主题总览 |
| `02_Projects` | 已新增项目总览、DMS 总览、DMS 模块索引、Model Training current 组、Knowledge-Base 维护治理项目入口、CVAT 云端部署 current 文档组和 agent-trajectory 项目 current 入口 |
| `03_Inbox` | 已新增候选内容索引 |
| `04_Sources` | 已新增来源索引和知识库工程来源证据卡 |
| `90_Archive` | 暂不处理为当前入口 |

## 1.3 DMS current 标准化状态

| 模块 | 状态 | 下一步 |
|---|---|---|
| Tracking | current 组较完整；仍是 partial recoverability | 后续补运行验证或 recoverability review |
| SDK Integration | current 组已创建；created_but_not_fully_verified | 后续补运行态验证或 recoverability review |
| EyeStatus | current 组已创建；single_pass_recoverable=false | 后续补独立可恢复性验证 |
| FaceID | current 组已有默认入口；partial recoverability | 后续补 recoverability verification |
| Model Training | current 组已创建；created_but_not_fully_verified | 后续补 recoverability verification |
| Postprocess | 已补模块索引；无 current 组 | 若持续迭代，再创建 current 组 |
| State Machine | 已补模块索引；无 current 组 | 若进入实现或长期维护，再创建 current 组 |
| Issue Analysis Skill | 已补模块索引和项目方案；完成首个真实 case，但无 current 组 | 补多 case、完整状态链和独立 recoverability verification 后再评估 current 化 |

## 1.4 正式知识结构化状态

| 主题 | 状态 | 下一步 |
|---|---|---|
| Agent Workflow | 已有主题总览；部分条目有完整元数据 | 核验新增条目互相引用和重复边界 |
| 模型 | 已有主题总览；J6 工具链结构较完整 | 对高频旧条目补 `summary/sources/scope/risks` |
| C++ | 已有主题总览；多数为历史笔记 | 分批补最小元数据，不批量改写正文 |
| 多模态大模型 | 已有主题总览 | 补高频条目最小元数据 |
| 通信技术 | 已有主题总览 | 补条目来源、适用范围和风险 |
| Apollo | 已有主题总览 | 补版本边界和条目元数据 |
| 库 | 已有主题总览 | 补 OpenCV/PyTorch 条目元数据 |
| 操作系统 | 已有主题总览 | 补版本和环境边界 |
| 芯片架构与底软 | 已有主题总览 | 补来源和具体芯片适用边界 |
| 计算机原理 | 已有主题总览 | 补基础概念来源和适用边界 |
| Docker | 单条目已补最小元数据 | 后续按需补 Docker 主题总览 |

## 1.5 入口呈现状态

读者入口已切换为“内容简介 + 入口分流”。结构状态集中记录在本审计文件、模块 current 文档或维护记录中。

## 1.6 未解决项

- `01_Knowledge` 旧条目的最小元数据覆盖仍未完成，但一级主题入口已基本收口。
- Model Training current 组已创建，但尚未完成独立 recoverability verification。
- FaceID、EyeStatus、SDK Integration 的 recoverability verification 尚未完成。
- Postprocess、State Machine 是否 current 化尚未决策。
- Knowledge-Base 防静默覆盖治理方案已完成阶段 0 至 3B 首版实现：skill-owned Schema rules、只读 lint、Traceability Index、pre-write gate 和 hash check 已通过单元与真实知识库只读集成验证；中文检索基准、current 去历史化和事件驱动维护尚未执行。
- 本审计文件仍混有较多 Tracking 历史维护流水，等待治理方案阶段 4 去历史化；在迁移前不将这些流水作为新的 current 表达范式。
- Knowledge-Base 维护治理相关的 `knowledge-base-structure-builder` 与 `knowledge-base-retriever` 文档已归位到 codex-capability 项目；Knowledge-Base 项目只保留知识库侧结构审计、治理边界和历史实现记录。
- 现有 Traceability CLI 的目录枚举、索引、匹配和原文读取尚未全链路接受 authorized paths，后续实现前必须先消除越权扫描风险。
- CVAT 云端部署 current 文档组已创建，状态为 `created_but_not_fully_verified`；当前方案已从 turbo/API 回写主路径调整为 NAS 持续挂载、训练平台模型结果落盘、CVAT 读取并人工复核；尚未完成真实云桌面 Docker/Compose、NAS share、模型结果导入、导出和备份恢复验证。
- agent-trajectory 项目 current 入口已创建，状态为 `created_but_not_fully_verified`；当前方案已收敛为 hook feasibility 前置、hook adapter 轻量触发、collector service 采集 raw events、分层 Snapshot、异步 Semantic Distillation、decision point、state graph 和五类资产模型；P0 已完成最小 collector、raw event schema、global passive hook + allowlist 注册、5 个单元测试和一次模拟 hook 到 report 链路验证；尚未完成真实新 Codex 会话下的 trajectory 采集、真实 hook payload/correlation/ordering 验证、hook overhead/丢失率统计、100 条人工重建 review、Counterfactual Stability rubric、Failure Taxonomy 样本校准和 holdout 验证，未声明 `single_pass_recoverable: true`。
- agent-trajectory 后续已补充 hook / collector / distiller 三层解析边界和 hook 外 scheduler 调度实现：新增 `collector.scheduler`、`collector.cli schedule`、`storage/collector.lock`、limit、loop 和 write-report 支持，8 个单元测试通过，并已消费真实本地 queue 中 90 条 payload 生成 91 条 raw events；仍未完成长期 timer/daemon 稳定性、overhead、丢失率、重复 envelope 幂等加固和异步 distiller 验证。
- DMS Issue Analysis Skill 已完成 `ADASL2-1565` 首个在线飞书到真实 Jira 评论的端到端运行，并修复中文正文与 Jira Wiki Markup；但该 case 结论为证据不足，R 核、多 case、完整 DMS 状态链、并发去重和 recoverability verification 仍未闭合。

## 1.7 2026-06-09 Tracking current 增量维护记录

- 因 DmsTrack 首轮内部可读性重构改变了当前实现事实和验证状态，已局部更新：
  - `tracking_overview_current.md`
  - `tracking_implementation_current.md`
  - `tracking_validation_current.md`
  - `DMS项目总览.md`
  - 对应 Current Maintenance Record
- 未整组重写 current 文档；`tracking_design_current.md` 与 `tracking_spec_current.md` 未修改，因为设计目标、算法契约和 public API 没有变化。
- Tracking 默认入口、默认恢复顺序和 default recovery bundle 未变化。
- `recoverability_status` 仍为 `partial`；未新增或保留 `single_pass_recoverable: true` 声明。
- 新增证据为 patch check、J6B 编译和独立 repo review；runtime replay 与单元测试未执行，板端验证按本次任务边界为 not required。
- 同日继续局部同步 Hand Phase 4A：仅更新 Tracking overview/implementation/validation、维护记录和 DMS 总览；design/spec、默认入口、恢复顺序与 `recoverability_status: partial` 均未变化。

## 1.8 2026-06-11 Tracking current 增量维护记录

- 因 sentinel、ID 生命周期语义和 Body/Hand 阶段组织成为新的当前实现事实，已同步更新 Tracking 五份 current 文档、DMS 项目总览和本结构审计。
- 本轮未整组重写正文；design/spec 仅补充 `bodyId / handId` 初始继承 face key、但 body/hand 生命周期独立的边界，以及 hand 发布仍依赖当前 DRIVER body evidence 的约束。
- Tracking 默认入口、默认恢复顺序、default recovery bundle 和 `recoverability_status: partial` 均未变化。
- 证据为 `git diff --check`、J6B 编译、独立 repo review `approved` 和 verification-manager `conditional_pass`；runtime replay 与单元测试未执行，板端验证为 not required。
- 未新增或保留 `single_pass_recoverable: true` 声明。

## 1.9 2026-06-12 Tracking 后排误跟踪主驾修复写回

- 因 2m 回灌样本新增已验证运行事实，已同步更新 Tracking current 五份文档、DMS 项目总览和本结构审计，并新增项目级维护记录。
- 本次新增板端证据：二次回灌完成后 `face-first driver face select face=1` 为 0 次，`reject back passenger` 与 `reject smaller` 共同过滤后排候选。
- 本轮未整组重写 current 文档；仅补充 driver face 防后排误绑定的设计、规范、实现和验证事实。
- Tracking 默认入口、默认恢复顺序、default recovery bundle 和 `recoverability_status: partial` 均未变化。

## 1.10 2026-06-15 Tracking assignment helper 与职责分层写回

- 因 assignment helper 形态、Body finalize/projection 边界和 Hand solve/apply/finalize/publish 边界成为新的当前实现事实，已同步更新 Tracking 五份 current 文档、DMS 项目总览和目标维护记录。
- 本轮未整组重写 current 文档；只追加 helper 删减、非对称分层、编译证据和残余验证边界。
- Tracking 默认入口、默认恢复顺序、default recovery bundle 和 `recoverability_status: partial` 均未变化。
- 未新增或保留 `single_pass_recoverable: true`；独立 review、runtime replay 和板端验证仍未完成。
- 未新增或保留 `single_pass_recoverable: true` 声明。

## 1.11 2026-06-15 Tracking 深模块重新评审写回

- 新增项目级评审记录 `DmsTrack深模块重新评审与CleanRefactor规划-2026-06-15.md`。
- 因推荐重构路线、抽象结论和验证状态变化，已局部同步 Tracking 五份 current 文档与 DMS 项目总览。
- 未整组重写 current 文档；代码事实继续保留，但 header-level `FrameBodyView`、assignment 中间类型和 step-level helper 不再作为推荐结构。
- Tracking 默认入口、默认恢复顺序、default recovery bundle 不变。
- `recoverability_status` 仍为 `partial`；未新增或保留 `single_pass_recoverable: true`。
- 本轮未修改 DMS 业务代码，未执行 runtime replay、单元测试或板端验证。

## 1.12 2026-06-16 Tracking 4A 生命周期闭环代码写回

- 因 `feat/ljc/track_0615` 已在 `source/utils/track.cpp` 补齐 Owner/body/hand 4A 生命周期候选域和 hand initialized slot sweep，已局部同步 Tracking overview/spec/implementation/validation、DMS 项目总览和目标维护记录。
- 本轮未整组重写 current 文档；`tracking_design_current.md` 未修改，因为 public API、身份主线和分阶段设计目标未变化。
- Tracking 默认入口、默认恢复顺序、default recovery bundle 和 `recoverability_status: partial` 均未变化。
- 新增证据为 subpower explorer/worker 结果、`git diff --check`、`track.cpp.o` 对象级编译，以及临时打开 build 清理后的 `compile_j6b.sh` 完整构建通过；验证后 `compile_j6b.sh` 已恢复注释状态且未保留脚本改动。
- Runtime replay、单元测试和板端验证未执行；Body Reacquire、loss instrumentation 与 Hand Reacquire 评估仍待后续阶段。
- 未新增或保留 `single_pass_recoverable: true` 声明。

## 1.13 2026-06-16 Tracking 基线对比与路线收缩写回

- 因重新对比 `1401fc338107f05b9cf` 与 `feat/ljc/track_0615` 后，Tracking 当前推荐路线发生变化，已局部同步：
  - `02_Projects/DMS/04_Tracking/head-first跟踪方案.md`
  - `tracking_overview_current.md`
  - `tracking_design_current.md`
  - `tracking_spec_current.md`
  - `tracking_implementation_current.md`
  - `tracking_validation_current.md`
  - `02_Projects/DMS/DMS项目总览.md`
- 新增项目级维护记录：`02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack基线对比与HeadFirst路线收缩设计记录-2026-06-16.md`。
- 将两篇已过时的扩张路线记录移动到归档区，保留历史可追溯但不再作为默认推荐入口：
  - `90_Archive/02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack深模块重新评审与CleanRefactor规划-2026-06-15.md`
  - `90_Archive/02_Projects/DMS/04_Tracking/Current Maintenance Records/Tracking方案优化与历史实现归档记录-2026-06-16.md`
- 当前推荐路线收缩为 face/head identity、2m face/head-only、5m driver-bound body/hand evidence、face missing 优先 face occlusion、body/hand bounded evidence cache；Body/Hand global assignment、independent lifecycle、四态 edge 和 Reacquire 降级为历史实验或未来重启项。
- Tracking 默认入口、默认恢复顺序、default recovery bundle 和 `recoverability_status: partial` 均未变化。
- 未新增或保留 `single_pass_recoverable: true` 声明。

## 1.14 2026-06-17 Tracking 2m/5m 配置分流写回

- 因 `DmsTrack` 已基于 `track_params.json` 的 `camera_type` 落地 2m/5m 第一层分流，已局部同步 Tracking 五份 current 文档、DMS 项目总览和本结构审计。
- 新增项目级维护记录：`02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack 2m5m配置分流单步重构闭环记录-2026-06-17.md`。
- 本轮未整组重写 current 文档；只更新 profile 分流实现事实、验证证据和残余运行验证缺口。
- Tracking 默认入口、默认恢复顺序、default recovery bundle 和 `recoverability_status: partial` 均未变化。
- 新增证据为 subpower planner/implementer/reviewer 结果、`git diff --check` 和 `bash scripts/compile_j6b.sh` 完整构建通过；runtime replay、单元测试和板端验证未执行。
- 未新增或保留 `single_pass_recoverable: true` 声明。

## 1.15 2026-06-17 Tracking 5m driver-bound body evidence 写回

- 因 `DmsTrack` 已将 body evidence 收缩为只服务 selected driver face，已局部同步 Tracking 五份 current 文档、DMS 项目总览和本结构审计。
- 新增项目级维护记录：`02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack 5m DriverBound Body Evidence收缩闭环记录-2026-06-17.md`。
- 本轮未整组重写 current 文档；只更新 body owner acquisition/publish 当前事实、验证证据和残余运行验证缺口。
- Tracking 默认入口、默认恢复顺序、default recovery bundle 和 `recoverability_status: partial` 均未变化。
- 新增证据为 subpower planner/reviewer 结果、`git diff --check` 和 `bash scripts/compile_j6b.sh` 完整构建通过；runtime replay、单元测试和板端验证未执行。
- 未新增或保留 `single_pass_recoverable: true` 声明。

## 1.16 2026-06-17 Tracking body-to-hand finalized snapshot 写回

- 因 `DmsTrack` 已将 hand 内部 body 输入从 legacy body output map 隔离为 body phase 返回的局部 finalized driver body evidence snapshot，已局部同步 Tracking 五份 current 文档、DMS 项目总览和本结构审计。
- 新增项目级维护记录：`02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack BodyToHand Finalized Snapshot隔离闭环记录-2026-06-17.md`。
- 本轮触及 private phase-level 方法签名，已按 `interface-abstraction-implementation-guard` 执行守门和 diff 审计；未新增 Row/View/Payload/Result 类型，未改变 public API。
- 本轮未整组重写 current 文档；只更新 body-to-hand 输入边界、验证证据和残余运行验证缺口。
- Tracking 默认入口、默认恢复顺序、default recovery bundle 和 `recoverability_status: partial` 均未变化。
- 新增证据为 subpower planner/reviewer 结果、interface guard 工件、`git diff --check` 和 `bash scripts/compile_j6b.sh` 完整构建通过；runtime replay、单元测试和板端验证未执行。
- 未新增或保留 `single_pass_recoverable: true` 声明。

## 1.17 2026-06-17 Tracking updateHandTracks 第二阶段可读性优化方案写回

- 新增项目级方案记录：`02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack updateHandTracks第二阶段可读性优化方案-2026-06-17.md`。
- 已局部同步 DMS 项目总览、Tracking implementation current 和 validation current。
- 本方案不改变 current 默认入口、默认恢复顺序、default recovery bundle 或 `recoverability_status: partial`。
- 本方案只规划行为不变的可读性优化，不声明运行效果闭合，不新增 `single_pass_recoverable: true`。
- 后续每个实现小步仍需单独记录验证、review 和写回。

## 1.18 2026-06-17 Tracking updateHandTracks publish 段可读性整理写回

- 因 `DmsTrack` 已完成 updateHandTracks 第二阶段 Step 1 publish 段整理，已局部同步 Tracking implementation current、validation current、DMS 项目总览和本结构审计。
- 新增项目级维护记录：`02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack updateHandTracks publish段可读性整理闭环记录-2026-06-17.md`。
- 本轮未整组重写 current 文档；只更新 publish 段局部抽象、验证证据和后续小步边界。
- Tracking 默认入口、默认恢复顺序、default recovery bundle 和 `recoverability_status: partial` 均未变化。
- 新增证据为 subpower reviewer 结果、interface guard 工件、`git diff --check` 和 `bash scripts/compile_j6b.sh` 完整构建通过；runtime replay、单元测试和板端验证未执行。
- 未新增或保留 `single_pass_recoverable: true` 声明。

## 1.19 2026-06-17 Tracking updateHandTracks unmatched miss 可读性整理写回

- 因 `DmsTrack` 已完成 updateHandTracks 第二阶段 Step 2 unmatched miss 段整理，已局部同步 Tracking implementation current、validation current、DMS 项目总览和本结构审计。
- 新增项目级维护记录：`02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack updateHandTracks unmatched miss可读性整理闭环记录-2026-06-17.md`。
- 本轮未整组重写 current 文档；只更新 unmatched miss 局部抽象、验证证据和后续小步边界。
- Tracking 默认入口、默认恢复顺序、default recovery bundle 和 `recoverability_status: partial` 均未变化。
- 新增证据为 subpower reviewer 结果、interface guard 工件、`git diff --check` 和 `bash scripts/compile_j6b.sh` 完整构建通过；runtime replay、单元测试和板端验证未执行。
- 未新增或保留 `single_pass_recoverable: true` 声明。

## 1.20 2026-06-17 Tracking updateHandTracks owner/candidate 准备区可读性整理写回

- 因 `DmsTrack` 已完成 updateHandTracks 第二阶段 Step 3 owner/candidate 准备区整理，已局部同步 Tracking implementation current、validation current、DMS 项目总览和本结构审计。
- 新增项目级维护记录：`02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack updateHandTracks owner候选可读性整理闭环记录-2026-06-17.md`。
- 本轮未整组重写 current 文档；只更新 owner/candidate 准备区局部抽象、验证证据和后续小步边界。
- Tracking 默认入口、默认恢复顺序、default recovery bundle 和 `recoverability_status: partial` 均未变化。
- 新增证据为 subpower reviewer 结果、interface guard 工件、`git diff --check` 和 `bash scripts/compile_j6b.sh` 完整构建通过；runtime replay、单元测试和板端验证未执行。
- 未新增或保留 `single_pass_recoverable: true` 声明。

## 1.21 2026-06-17 Tracking DmsTrack 整体内部架构可读性评审写回

- 因用户指出 handtrack 只是例子，优化范围应覆盖 Face/Body/Hand 整体架构，本轮新增项目级设计评审记录：`02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack整体内部架构可读性优化评审与方案-2026-06-17.md`。
- 已将 `DmsTrack updateHandTracks第二阶段可读性优化方案-2026-06-17.md` 标记为 `superseded`。
- 已将三条 updateHandTracks 局部 lambda 小步记录标记为 `superseded`，保留对应代码提交和验证证据，但不再作为 active plan。
- 已局部同步 Tracking implementation current、validation current、DMS 项目总览和本结构审计。
- 本轮未修改 DMS 业务代码，未执行编译、runtime replay、单元测试或板端验证。
- Tracking 默认入口、默认恢复顺序、default recovery bundle 和 `recoverability_status: partial` 均未变化。
- 未新增或保留 `single_pass_recoverable: true` 声明。

## 1.22 2026-06-17 Tracking current 文档组去历史化治理

- 因用户指出 current 文档组被写成预期方案和历史提交枚举，本轮按 current lifecycle 的 `hardening_refactor` 模式清理 Tracking current 表达。
- 已将 `tracking_overview_current.md` 的 Current Truth 从长段历史变化压缩为当前 Tracking 代码事实、profile gate、driver-bound evidence 和验证边界摘要。
- 已将 `tracking_design_current.md` 中的基线对比/路线收缩段压缩为当前内部架构边界，不再把对比过程作为 current 主内容。
- 已将 `tracking_implementation_current.md` 从按日期/提交枚举改为当前代码事实的主题式说明：入口、状态容器、profile gate、motion model、spec-to-code mapping、Face/Body/Hand 当前 lifecycle、实现约束、验证缺口和历史追溯入口。
- 已将 `tracking_validation_current.md` 从逐小步验证日志改为当前证据等级、未闭合验证项、review conclusion、required next verification 和 recoverability 判定。
- 已将 `DMS项目总览.md` 恢复为项目入口职责，只保留 Tracking 当前摘要和追溯入口，不再列出 Tracking 每条维护记录。
- 历史提交、superseded 方案、review 细节和命令证据继续保留在 `Current Maintenance Records/` 与 `subpower_runs/`，不作为 current 正文主内容。
- 本轮未改变 Tracking 默认入口、默认恢复顺序、default recovery bundle 或 `recoverability_status: partial`。
- 未新增或保留 `single_pass_recoverable: true` 声明。

## 1.23 2026-06-17 Tracking Face phase assignment loss 可读性整理写回

- 因 `DmsTrack` 整体内部架构可读性优化方案进入 Face phase 局部组织，本轮新增项目级维护记录：`02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack FacePhase assignment loss可读性整理闭环记录-2026-06-17.md`。
- 本步代码只将 `updateFaceTracks` 内 face assignment loss 矩阵构造移动到 `.cpp` anonymous namespace helper `BuildFaceAssignmentLoss`，未修改 public/private header API，未新增 Row/View/Payload/Result/Context 类型。
- 本轮不更新 Tracking current 文档组和 DMS 项目总览：当前行为事实、默认入口、默认恢复顺序、default recovery bundle 和 `recoverability_status: partial` 均未变化；若把 helper 名称写入 current 正文，会重新把 current 文档变成实现小步枚举。
- 新增证据为 interface guard 记录、`git diff --check` 和 `bash scripts/compile_j6b.sh` 完整构建通过；subpower 本轮为 host-only fallback，独立 subagent reviewer 因 agent thread limit 未执行。
- 未执行 runtime replay、单元测试或板端验证；未新增或保留 `single_pass_recoverable: true` 声明。

## 1.24 2026-06-17 Tracking Body phase match selection 可读性整理写回

- 因 `DmsTrack` 整体内部架构可读性优化方案进入 Body phase 局部组织，本轮新增项目级维护记录：`02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack BodyPhase match selection可读性整理闭环记录-2026-06-17.md`。
- 本步代码只将 `updateBodyTracks` 内 tracked body match 与 face-anchored acquisition 两段 detection 选择机制移动到 `.cpp` anonymous namespace helper，未修改 public/private header API，未新增 Row/View/Payload/Result/Context 类型。
- 本轮不更新 Tracking current 文档组和 DMS 项目总览：当前行为事实、默认入口、默认恢复顺序、default recovery bundle 和 `recoverability_status: partial` 均未变化；helper 名称和逐步验证留在维护记录与 subpower artifacts。
- 新增证据为 interface guard 记录、独立 repo-reviewer `approve`、`git diff --check` 和 `bash scripts/compile_j6b.sh` 完整构建通过；runtime replay、单元测试和板端验证未执行。
- 未新增或保留 `single_pass_recoverable: true` 声明。

## 1.25 2026-06-17 Tracking Hand phase internal helper 可读性整理写回

- 因 `DmsTrack` 整体内部架构可读性优化方案进入 Hand phase 局部组织，本轮新增项目级维护记录：`02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack HandPhase internal helper可读性整理闭环记录-2026-06-17.md`。
- 本步代码将 `updateHandTracks` 内 owner 收集、slot 预测、candidate 收集、unmatched miss、expired reset 和 publish gate 等局部机制从函数局部 lambda 移到 `.cpp` anonymous namespace helper，未修改 public/private header API，未新增 Row/View/Payload/Result/Context 类型。
- 本轮不更新 Tracking current 文档组和 DMS 项目总览：当前行为事实、默认入口、默认恢复顺序、default recovery bundle 和 `recoverability_status: partial` 均未变化；helper 名称和逐步验证留在维护记录与 subpower artifacts。
- 新增证据为 interface guard 记录、独立 repo-reviewer `approve`、`git diff --check` 和 `bash scripts/compile_j6b.sh` 完整构建通过；runtime replay、单元测试和板端验证未执行。
- 未新增或保留 `single_pass_recoverable: true` 声明。

## 1.26 2026-06-17 Tracking Face/Body/Hand 主流程叙述化重构修订方案写回

- 因用户指出当前主要问题不是 public API 或短时匹配算法，而是 Face/Body/Hand phase 主流程不够高层叙述化，本轮新增项目级修订方案：`02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack FaceBodyHand主流程叙述化重构修订方案-2026-06-17.md`。
- 本修订方案将优先级调整为“可读性高于 private interface 最小化”，允许用少量 `DmsTrack` private helper 表达稳定 phase 子流程，同时禁止新增搬运型 `Row/View/Payload/Result/Context` 类型。
- 本轮只写回方案，不修改 DMS 业务代码；后续 Face、Body 与 Hand 主流程叙述化需分步执行、分别编译和 review。
- 本轮不更新 Tracking current 文档组和 DMS 项目总览：当前行为事实、默认入口、默认恢复顺序、default recovery bundle 和 `recoverability_status: partial` 均未变化。
- 未新增或保留 `single_pass_recoverable: true` 声明。

## 1.27 2026-06-17 Tracking Face phase 主流程叙述化写回

- 因 `DmsTrack` Face/Body/Hand 主流程叙述化修订方案进入阶段 1，本轮新增项目级维护记录：`02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack FacePhase主流程叙述化闭环记录-2026-06-17.md`。
- 本步代码将 `updateFaceTracks` 主体收敛为 collect、predict、solve/apply、bootstrap、advance/erase 的 phase 摘要；新增 4 个 `DmsTrack` private helper，未修改 public `Init/Update`，未新增 Row/View/Payload/Result/Context 类型。
- 本轮不更新 Tracking current 文档组和 DMS 项目总览：当前行为事实、默认入口、默认恢复顺序、default recovery bundle 和 `recoverability_status: partial` 均未变化。
- 新增证据为 interface guard 记录、独立 repo-reviewer `approve`、`git diff --check` 和 `bash scripts/compile_j6b.sh` 完整构建通过；runtime replay、单元测试和板端验证未执行。
- 未新增或保留 `single_pass_recoverable: true` 声明。

## 1.28 2026-06-17 Tracking Body phase 主流程叙述化写回

- 因 `DmsTrack` Face/Body/Hand 主流程叙述化修订方案进入阶段 2，本轮新增项目级维护记录：`02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack BodyPhase主流程叙述化闭环记录-2026-06-17.md`。
- 本步代码将 `updateBodyTracks` 主体收敛为 collect detections、collect owner、match/acquire、advance/retire、publish snapshot 的 phase 摘要；新增 4 个 `DmsTrack` private helper，未修改 public `Init/Update`，未新增 Row/View/Payload/Result/Context 类型。
- 本轮不更新 Tracking current 文档组和 DMS 项目总览：当前行为事实、默认入口、默认恢复顺序、default recovery bundle 和 `recoverability_status: partial` 均未变化。
- 新增证据为 interface guard 记录、独立 repo-reviewer `approve`、`git diff --check` 和 `bash scripts/compile_j6b.sh` 完整构建通过；runtime replay、单元测试和板端验证未执行。
- 未新增或保留 `single_pass_recoverable: true` 声明。

## 1.29 2026-06-17 Tracking Hand phase 主流程叙述化写回

- 因 `DmsTrack` Face/Body/Hand 主流程叙述化修订方案进入阶段 3，本轮新增项目级维护记录：`02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack HandPhase主流程叙述化闭环记录-2026-06-17.md`。
- 本步代码将 `updateHandTracks` 主体收敛为 collect detections、collect allowed owners、predict、first pass、second pass、cleanup、publish 的 phase 摘要；新增 5 个 `DmsTrack` private helper 和 1 个 `.cpp` slot helper，未修改 public `Init/Update`，未新增 Row/View/Payload/Result/Context 类型。
- 本轮不更新 Tracking current 文档组和 DMS 项目总览：当前行为事实、默认入口、默认恢复顺序、default recovery bundle 和 `recoverability_status: partial` 均未变化。
- 新增证据为 interface guard 记录、独立 repo-reviewer `approve`、`git diff --check` 和 `bash scripts/compile_j6b.sh` 完整构建通过；runtime replay、单元测试和板端验证未执行。
- 未新增或保留 `single_pass_recoverable: true` 声明。

## 1.30 2026-06-15 Tracking 统一 Assignment 目标澄清

- 用户明确 Face 全局匹配、Body 全局 Hungarian 和 Hand 全局 slot assignment 均属于本次行为重构目标。
- 已局部同步 Tracking review、overview、design、spec、implementation、validation 与 DMS 项目总览；未整组重写 current 文档。
- 推荐分支路线仍为从 `br_develop_forJ6b` 新开 clean branch；`feat/ljc/track_0609` 仅作为 solver/cost/row 算法参考和结构反例。
- `recoverability_status` 仍为 `partial`；未新增 `single_pass_recoverable: true`，未修改 DMS 业务代码。

## 1.31 2026-06-15 Tracking clean branch Body 全局 assignment 写回

- 因 `feat/ljc/track_0615` 已完成 clean refactor 阶段 2 Body 全局 owner-to-detection assignment，已局部同步 Tracking review、overview、design、spec、implementation、validation 与 DMS 项目总览。
- 本轮未整组重写 current 文档；只更新 Body matching 当前事实、验证证据和后续风险。
- Tracking 默认入口、默认恢复顺序、default recovery bundle 和 `recoverability_status: partial` 均未变化。
- 未新增或保留 `single_pass_recoverable: true`。
- 本轮代码验证为 QNX `Utils` 与 `sdk` 构建通过；runtime replay、单元测试和板端验证未执行。当前保守实现关闭已有 body / initialized hand 的 acquisition fallback；tracking loss、acquisition loss、driver/non-driver bias 与 `dummyLoss` 的标定仍待后续冲突样例与 diff 白名单验证。

## 1.32 2026-06-16 Tracking 方案优化与历史实现归档

- `02_Projects/DMS/04_Tracking/座舱多目标跟踪实现.md` 已移动到 `90_Archive/02_Projects/DMS/04_Tracking/座舱多目标跟踪实现.md`，角色收敛为历史 body-first baseline。
- 已局部同步 `head-first跟踪方案.md`、Tracking 五份 current 文档、DMS 项目总览和 `DmsTrack深模块重新评审与CleanRefactor规划-2026-06-15.md`。
- 本轮当时将 body/hand 生命周期独立原则、Body Track/Reacquire/Bootstrap/Forbidden 四态 edge、deep-module phase-level 约束吸收到方案；该推荐路线已在 1.16 基线对比后被收缩路线取代。
- 当时的后续阶段顺序为先完成 Owner/body/hand 独立生命周期闭环，再做 loss instrumentation + replay 标定，最后打开 Body Reacquire 并评估 Hand 是否需要类似 Reacquire；该顺序现已归档为历史实验路线，不再作为当前默认路线。
- Tracking 默认入口、默认恢复顺序和 default recovery bundle 未变化。
- `recoverability_status` 仍为 `partial`；未新增或保留 `single_pass_recoverable: true`。
- 本轮未修改 DMS 业务代码，未执行 runtime replay、单元测试或板端验证。

## 1.33 2026-06-22 Knowledge-Base 双 Skill 子项目调整

- 新增 [[02_Projects/codex-capability-registry/knowledge-base-structure-builder/项目总览]]，负责 authoring、indexing-prep、生命周期、retrieval header、lint 和风险分级写入门禁。
- 新增 [[02_Projects/codex-capability-registry/knowledge-base-retriever/项目总览]]，负责只读 Query Planning、多轮历史检索、原文读取和 `retrieval_package`。
- 两个 skill 共享概念和交换格式，但不共享实现权威：Builder 不拥有相关性排序，Retriever 不执行事实写入和 gate decision。
- 父级 `知识库防静默覆盖治理实施方案.md` 已删除，避免形成第三个 active 方案权威；有效设计已分别进入两个子项目总览。
- `AGENTS.md` 是目标仓库本地政策，不作为 skill 资产，不与 skill 版本绑定。
- 阶段 0 至 3B 实现记录继续保存拆分前实现与验证事实，并已改为引用两个子项目入口。
- 本轮没有创建五份 current 文档组；两个子项目均先以单一项目总览作为入口，后续形成长期独立设计、实现和验证事实后再评估 current 化。

## 1.34 2026-07-03 Inbox 与 skill 项目文档归位

- `03_Inbox` 中 J6 工具链候选文档和配套 assets 已集中到 `03_Inbox/J6工具链/`，候选索引和正式知识来源引用同步到新路径。
- `knowledge-base-structure-builder` 与 `knowledge-base-retriever` 项目文档已从 `02_Projects/Knowledge-Base/` 归位到 `02_Projects/codex-capability-registry/`。
- Knowledge-Base 项目总览已改为记录知识库侧治理边界和相关 skill 项目入口；codex-capability 入口已补充两个 skill 项目文档入口。
- 本轮只做结构归位和引用路径同步，不提升正式知识，不改写历史结论，不新增 `single_pass_recoverable: true`。

## 1.35 2026-07-02 SDK Integration DMS 回灌方案记录写回

- 新增项目级方案记录：[[02_Projects/DMS/06_SDK_Integration/DMS回灌方案]]。
- 已局部同步 SDK Integration overview current 和 DMS 项目总览，使回灌方案可从模块入口召回。
- 本记录将回灌方案命名为 DMS 回灌方案，而非原始图像回灌方案，以保留 README 中 `start_stage=model` 与 `start_stage=postprocess` 的同一配置语义。
- 当前事实边界：`start_stage=model` 的模型阶段回灌路径已有源码静态证据；`start_stage=postprocess` 为 README 预留但目前不支持，未看到 atomic 结果注入 Fuse/后处理的运行时链路。
- 本轮未执行编译、x86 回灌或板端回灌验证；未新增或保留 `single_pass_recoverable: true` 声明。

## 1.36 2026-07-09 agent-trajectory P0 实现与 Hook 注册写回

- 新增项目级阶段记录：`02_Projects/agent-trajectory/agent_trajectory_p0_implementation_and_hook_registration-2026-07-09.md`。
- 已同步 agent-trajectory overview current、项目总览和本结构审计。
- 本轮不提升正式知识，不改变 `created_but_not_fully_verified` 状态，不新增或保留 `single_pass_recoverable: true`。
- 当前事实变化为：P0 最小 collector、raw event schema、global passive hook wrapper、allowlist 和模拟链路验证已完成；真实 Codex 会话 hook payload/correlation/ordering 仍是后续验证缺口。

## 1.37 2026-07-09 agent-trajectory Scheduler 与分层解析写回

- 新增项目级阶段记录：`02_Projects/agent-trajectory/agent_trajectory_scheduler_and_layered_parse_update-2026-07-09.md`。
- 已同步 agent-trajectory overview current、项目总览和本结构审计。
- 本轮不提升正式知识，不改变 `created_but_not_fully_verified` 状态，不新增或保留 `single_pass_recoverable: true`。
- 当前事实变化为：hook / collector / distiller 三层边界已明确，每次 hook 抓取后不做同步解析；collector 解析改由 hook 外 timer、loop 或后续 daemon 执行；distiller 仍保持 trajectory/session 级异步批处理。
- 当前实现变化为：`/home/jichao/agent-trajectory` 新增 `collector.scheduler` 和 CLI `schedule` 子命令，支持 lock、limit、loop 和 write-report；8 个单元测试通过，真实本地 scheduler 已消费 90 条 queued payload 并刷新 Phase 0 report。
- 残余风险为：当前增量处理依赖 `collector_state.json:last_queue_line`，正常重复运行只处理新增 queue 行，但 raw event append 后、state 保存前仍有 crash 重复窗口；长期 timer/daemon 稳定性、overhead、丢失率和异步 distiller 尚未验证。

## 1.38 2026-07-09 agent-trajectory P1 Raw Trace 分段设计写回

- 已直接修订 `02_Projects/agent-trajectory/agent_trajectory_initial_design.md` 的 Phase 1 设计，避免另建补丁文档影响后续检索准确率。
- 已同步 agent-trajectory overview current 和本结构审计。
- 本轮不提升正式知识，不改变 `created_but_not_fully_verified` 状态，不新增或保留 `single_pass_recoverable: true`。
- 当前设计变化为：P1 不应继续把不同会话长期集中写入单一 `trajectories/raw_events.jsonl`；应按 `trajectories/raw/<trajectory_id>/` 建立 per-trajectory raw bundle，并用 `trajectory_meta.json` 记录 session、workspace、UserPrompt/Stop、空闲超时、quality tier 和 segmentation reason。
- 全局 ingest/raw audit stream 可保留用于排错和重放，但 distiller 默认输入应切换到分段后的 trajectory bundle；若从 legacy/global raw stream 重建分段，必须生成 migration proposal 或 recovery record，不得静默覆盖。
- 残余风险为：该设计尚未在 `/home/jichao/agent-trajectory` 实现，真实 session/thread 字段、Stop 边界、空闲超时和人工 marker 策略仍需验证。

## 1.39 2026-07-09 agent-trajectory P1 Raw Bundle 实现写回

- `/home/jichao/agent-trajectory` 已提交 `243585f feat: store raw events per trajectory`，本地未推送远程。
- 已同步 agent-trajectory overview current、P1 initial design、项目总览和本结构审计。
- 本轮不提升正式知识，不改变 `created_but_not_fully_verified` 状态，不新增或保留 `single_pass_recoverable: true`。
- 当前实现变化为：取消 P0 集中 `trajectories/raw_events.jsonl` 和 `phase0_feasibility_report.json` 兼容输出；collector 只写 `trajectories/raw/<trajectory_id>/raw_events.jsonl`、`trajectory_meta.json`、`artifact_index.json`、`snapshot_refs.json`，report 聚合 per-trajectory bundle 并写入 `trajectories/collection_report.json`。
- 分段规则已实现基础版：`session_id + workspace` 归属同一 active trajectory，session 变化、workspace 变化会创建新 trajectory，`Stop` 后新的 `UserPromptSubmit` 会创建新 trajectory；空闲超时、人工 marker、capture policy 和 distiller 输入切换仍未实现。
- 验证结果：`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v` 11 个测试通过。

## 1.40 2026-07-09 agent-trajectory 异步 Semantic Distillation Skill 实现写回

- 已直接修订 `02_Projects/agent-trajectory/agent_trajectory_initial_design.md` 的 1.7.3 异步 Semantic Distillation 设计，避免新增补丁文档影响后续检索准确率。
- 已同步 agent-trajectory overview current、项目总览和本结构审计。
- 本轮不提升正式知识，不改变 `created_but_not_fully_verified` 状态，不新增或保留 `single_pass_recoverable: true`。
- 当前设计变化为：异步 Semantic Distillation 作为 `/home/jichao/agent-trajectory` repo-local 中文 skill 维护，并通过 `~/.codex/skills/semantic-distillation` 软链接暴露给 Codex runtime；skill 不进入 hook、collector、scheduler 或 daemon 的同步路径，只处理明确指定的 `trajectory_id` 或 raw bundle。
- 当前实现变化为：新增 `skills/semantic-distillation/SKILL.md`、`distiller/scripts/prepare_distillation.py` 和 distiller 单元测试；确定性脚本读取 `trajectories/raw/<trajectory_id>/`，写入 `trajectories/distilled/<trajectory_id>/<distillation_run_id>/` 下的 `run_meta.json`、`evidence_index.json`、`distilled_experience.json` 和 `distilled_experience.md` 脚手架。
- 验证结果：`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v` 14 个测试通过；软链接 `/home/jichao/.codex/skills/semantic-distillation -> /home/jichao/agent-trajectory/skills/semantic-distillation` 已验证。
- 残余风险为：尚未用真实 trajectory 完成人工或 LLM 语义蒸馏、reviewer 复核、批量候选选择、daemon 调度或 distillation run 版本对比验证；`reviewer_status` 默认仍应保持 `unreviewed`。

## 1.41 2026-07-13 DMS Issue Analysis Skill 首个真实闭环写回

- 新增项目级维护记录：[[02_Projects/DMS/10_Issue_Analysis_Skill/Current Maintenance Records/2026-07-13-ADASL2-1565真实端到端验证与Jira中文写回修复]]。
- 已同步 Issue Analysis Skill 模块索引、项目方案、DMS 项目总览、项目总览和本结构审计；未整组创建或重写 current 文档组。
- 当前事实变化为：`ADASL2-1565` 已完成在线飞书读取、真实 Jira/Data 采集、Evidence Package、A 核 308/308 行确定性准备、Agent review、受约束结论和真实 Jira 新增评论；结论为 `partial/INSUFFICIENT_EVIDENCE/low`，不代表根因确认。
- Jira 写回已强制用户可见正文包含中文，模板从 Markdown 标题改为 Jira Wiki Markup 的 `h2.` / `h3.`、`*` 和 `bq.`，消除 `1. 1. 1.` 重复编号；中文纠正版评论 ID 为 `8654396`。
- R 核仍为 `skipped/r_core_analyser_not_available`；多 case、完整 DMS 状态链、并发去重和独立 recoverability verification 仍待完成。
- 本轮不提升正式知识，不新增 `single_pass_recoverable: true`。
