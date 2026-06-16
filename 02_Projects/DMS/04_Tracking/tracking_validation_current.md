---
title: Tracking Validation Current
summary: Tracking 当前验证状态文档，记录 head-first、driver 修复、实验重构证据、2026-06-16 基线对比后的路线收缩结论，以及 2m/5m 分流、driver-bound evidence 和 face occlusion 的未验证项；实验分支不再视为推荐结构基底。
status: verified
doc_role: current
truth_role: current
current_kind: validation
lifecycle_state: active
default_entry: false
sync_required_when:
  - 证据状态变化
  - blocker 或 review 结论变化
  - 所需下一步验证变化
  - recoverability 判定依据变化
retrieval_priority: current
supersedes:
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪功能审核记录-2026-03-27.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪设计失配修复未闭环记录-2026-03-27.md
merged_into: []
current_replacement: []
related_code:
  - /home/jichao/dms/source/utils/track.cpp
  - /home/jichao/dms/include/utils/track.h
  - /home/jichao/dms/source/fuse_algos/fuse_algorithm.cpp
sources:
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪功能审核记录-2026-03-27.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪设计失配修复未闭环记录-2026-03-27.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪手部连续性优化闭环记录-2026-03-31.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/DMS主驾打哈欠误报修复闭环记录-2026-04-05.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/后排乘客头部误跟踪为副驾驶修复闭环记录-2026-04-05.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪快速运动恢复阶段预测更新一致性修复闭环记录-2026-04-05.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/跟踪框越界导致板端coredump调查与修复闭环记录-2026-04-07.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/2m摄像头后排head误绑定主驾修复闭环记录-2026-05-08.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/head-first优先于body-first跟踪主线决策记录-2026-05-09.md
  - 02_Projects/DMS/04_Tracking/head-first跟踪方案.md
  - 02_Projects/DMS/04_Tracking/tracking_implementation_current.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack基线对比与HeadFirst路线收缩设计记录-2026-06-16.md
  - 90_Archive/02_Projects/DMS/04_Tracking/Current Maintenance Records/Tracking方案优化与历史实现归档记录-2026-06-16.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/head-first跟踪代码重构闭环记录-2026-05-23.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack内部结构与可读性重构分析-2026-06-08.md
  - /home/jichao/dms/source/utils/track.cpp
scope: 适用于判断 Tracking 当前有哪些证据已经成立、哪些结论仍需更高等级验证；为默认实现输入链提供验证边界，不承接设计或规范正文。
risks:
  - 本文档已整合 2026-05-23 head-first 和 2026-06-09 内部可读性重构的编译/审查证据，但仍不等价于完整代表性视频集验收。
  - 2026-06-09 未执行 runtime replay 或新增单元测试；按任务边界不要求板端验证。
updated_at: 2026-06-16
---

## 0.1 Evidence Status

### 0.1.0J 2026-06-16 基线对比后的路线收缩审查

- 对比对象：
  - `1401fc338107f05b9cf`
  - `feat/ljc/track_0615`
  - `/home/jichao/dms/include/utils/track.h`
  - `/home/jichao/dms/source/utils/track.cpp`
- 静态结论：
  - `track.h` 未变化，public `DmsTrack::Init/Update` 仍是深接口。
  - 架构漂移集中在 `track.cpp`：Face solver helper、Body global assignment、Hand global slot assignment、tracking/acquisition fallback 和 Body/Hand 4A lifecycle 小步。
  - 当前分支已进入行为扩张链，不应继续作为默认推荐架构基底。
  - 当前推荐路线收缩为：face/head identity、2m face/head-only、5m driver-bound body/hand evidence、face missing 优先 face occlusion、body/hand bounded evidence cache。
- 归档：
  - 2026-06-15 深模块重新评审与 2026-06-16 方案优化记录已移动到 `90_Archive/02_Projects/DMS/04_Tracking/Current Maintenance Records/`，保留为历史实验路线。
- 未执行：
  - `runtime_replay: not_executed`
  - `unit_tests: not_added`
  - `board_validation: not_executed`
- 新验证重点：
  - 2m face/head-only 不输出陈旧 body/hand。
  - 5m driver-bound body/hand evidence 不跨 owner。
  - face missing 时输出 face occlusion 语义，而不是 body/hand identity continuation。
  - bounded cache 在 face 恢复、owner retire、id reuse 时正确清理。

### 0.1.0I 2026-06-16 Owner/body/hand 4A 生命周期闭环实现（历史实验代码事实）

- 代码范围：
  - `/home/jichao/dms/source/utils/track.cpp`
- 未修改：
  - `/home/jichao/dms/include/utils/track.h`
  - public `DmsTrack::Init/Update`
  - Body Reacquire / loss instrumentation / Hand Reacquire
- 静态结论：
  - 2A Conservative Body global assignment 与 3A Conservative Hand global slot assignment 已作为当前分支代码事实保留，但不再作为当前推荐路线。
  - 4A 已补齐 body/hand 生命周期候选域：已有 body owner 可在 face miss/暂不存在时以 tracking-only 方式参与 assignment；initialized hand slot 可基于内部 DRIVER body track 继续 tracking；未进入 hand row 的 initialized slot 会被 sweep 推进 miss。该行为降级为历史实验事实，后续推荐改为 bounded evidence cache。
  - 输出语义仍保守：body 输出仍要求当前 face evidence；hand 输出仍基于当前发布的 DRIVER body evidence。
- 验证：
  - `git -C /home/jichao/dms diff --check -- source/utils/track.cpp`: pass
  - `make -C build source/utils/CMakeFiles/Utils.dir/track.cpp.o`: pass
  - 临时打开 `scripts/compile_j6b.sh` 中 `rm -r build` / `mkdir build` 后执行 `bash scripts/compile_j6b.sh`: pass，`sdk` 目标构建到 100%，随后已把脚本恢复为注释状态且未保留脚本 diff。
- 独立 review：
  - 首轮发现 hand matched slot 在 output sanitize 失败路径可能同帧 `AdvanceHit` 后再 `AdvanceMiss`。
  - 已修复：hand publish 路径不再推进 lifecycle，hand hit/miss 只由 assignment/sweep 阶段负责。
- 证据限制：
  - `runtime_replay: not_executed`
  - `unit_tests: not_added`
  - `board_validation: not_required`
  - Body/Hand loss 标定、Reacquire 打开和 Hand 是否需要 Reacquire 仍未开始；这些不再是默认下一步。

### 0.1.0H 2026-06-16 Head-first 方案优化状态（已被 0.1.0J 收缩路线取代）

- 文档变更：
  - `座舱多目标跟踪实现.md` 已归档到 `90_Archive/02_Projects/DMS/04_Tracking/`。
  - `head-first跟踪方案.md` 当时吸收 body/hand 独立生命周期、Body 四态 edge 和 deep-module clean refactor 约束；该路线已被 0.1.0J 收缩路线取代。
- 证据性质：
  - 本节记录方案整理和 current 同步；随后 0.1.0I 已补充 `/home/jichao/dms` 4A 代码小步实现。
  - loss instrumentation + replay 标定、Body Reacquire、Hand 是否需要类似 Reacquire 均未获得新的运行证据。
- 必补验证：
  - 基于 replay 验证 face 短时消失时 body/hand 内部 tracking 可连续，hand slot 未进入 assignment row 时仍推进 miss/reset/cleanup，且每帧最多推进一次 lifecycle。
  - 继续检查 owner 确认退休、新 stable owner 接管、face id 复用时的 body/hand cleanup。
  - 在生命周期候选域闭合后，再做 Body Track / Reacquire / Bootstrap / Forbidden 四态 edge 的 loss instrumentation + replay 标定。
  - Reacquire 打开后再验证 ownerFaceId、hitCount、output continuity 和 motion reset/strong correction 的逐帧对比。
  - 基于 hand slot replay 数据评估 Hand 是否需要类似 Reacquire，而不是默认复制 Body 策略。
- `runtime_replay: not_executed`
- `unit_tests: not_added`
- `board_validation: not_executed`

### 0.1.0G 2026-06-15 Clean Branch Body Global Assignment 证据

- 代码范围：
  - `/home/jichao/dms/source/utils/track.cpp`
- 未修改：
  - `/home/jichao/dms/include/utils/track.h`
  - public `DmsTrack::Init/Update`
  - Face assignment 行为
  - Hand assignment/lifecycle
- `git diff --check`：通过。
- 直接 `cmake --build build --target Utils` 首次失败，原因是当前 shell 未定义 `QNX_HOST` 与 `QNX_TARGET`；加载 QNX SDK 环境后不再复现。
- QNX 环境加载后 `cmake --build build --target Utils`：通过，最终 `[100%] Built target Utils`。
- QNX 环境加载后 `cmake --build build --target sdk`：通过，最终 `[100%] Built target sdk`。
- 独立 explorer：确认阶段 1 Face cpp-internal solver 已落地，Body/Hand 原先尚未迁移，阶段 2 最小落点为 `updateBodyTracks`。
- 独立 reviewer：未发现编译、API/header 抽象漂移或 Face 非目标修改；确认 Body evaluator 已改为 tracking-first，Hand 已按同类原则做全局 slot assignment，未发现 double-miss publish 路径。当前保守实现关闭已有 body / initialized hand 的 acquisition fallback；剩余风险为 Body/Hand tracking/acquisition loss、driver/non-driver bias 与 `dummyLoss` 尚未用 sequence replay 标定，仍需 body owner 竞争、driver 竞争、hand 左右交叉和 crowded multi-person diff 白名单。
- `runtime_replay: not_executed`
- `unit_tests: not_added`
- `board_validation: not_required`

### 0.1.0E 2026-06-15 Assignment Helper 删减与非对称分层证据

- 代码范围：
  - `/home/jichao/dms/include/utils/track.h`
  - `/home/jichao/dms/source/utils/track.cpp`
- `git diff --check -- include/utils/track.h source/utils/track.cpp`：通过。
- 静态检查：`AssignmentEdge / AssignmentRejection / AssignmentPolicyMatrix / FrameHandView / HandPublishEligibility` 不存在；`AssignmentResult` 不进入 hand cleanup/finalize/publish。
- QNX 环境加载后 `cmake --build build --target Utils -j8`：通过。
- QNX 环境加载后 `cmake --build build --target sdk -j8`：通过，最终 `[100%] Built target sdk`。
- `runtime_replay: not_executed`
- `unit_tests: not_added`
- `board_validation: not_executed`
- `independent_review: pending`

### 0.1.0F 2026-06-15 Deep Module Re-review

- 独立 repo-reviewer：`changes_requested`。
- 结论：public API 已足够深；private header surface 过宽，实验分支已进入补救式重构。
- 高风险 finding：body 从 driver-first greedy ownership 改为 global Hungarian，不能作为等价可读性重构。
- 高风险 finding：owner 消失后的 initialized hand slot 可能停止 miss/cleanup，长期保留 hand owner 与 retired anchor，并影响 face id 复用。
- 抽象审计：`FrameBodyView` 降级为局部 snapshot；`HandSlotKey / HandAssignmentRow / AssignmentResult` 移出 header；已删除 matrix/candidate/rejection 不恢复。
- route：停止继续 `feat/ljc/track_0609`，从 `br_develop_forJ6b` 新开 clean branch。
- 历史需求澄清：当时统一 assignment solver、Body 全局 Hungarian 和 Hand 全局 slot assignment 被确认为目标行为；2026-06-16 基线对比后，该目标已降级为历史实验或未来重启项。
- `runtime_replay: not_executed`
- `unit_tests: not_executed`
- `board_validation: not_required`

### 0.1.0D 2026-06-13 State Normalization 与 FrameBodyView 证据

- 代码范围：
  - `/home/jichao/dms/include/utils/track.h`
  - `/home/jichao/dms/source/utils/track.cpp`
- `git diff --check`：通过。
- 静态搜索：`curResult->m_bodyTrackResultMap` 不再作为 hand 阶段输入；仅保留每帧 clear 与 body output 写入。
- 直接构建：`cmake --build build --target sdk -j8` 通过，最终 `[100%] Built target sdk`。
- `bash scripts/compile_j6b.sh`：CMake 和 make 阶段完成，日志包含 `[100%] Built target sdk`；脚本最后执行 `strip main/libsdk.so`，但当前构建实际产物为 `build/main/sdk`，`main/libsdk.so` 不存在，因此脚本返回 1。该失败发生在脚本末尾 strip 目标不匹配，不是 `track.cpp` 编译失败。
- 独立 repo review：`approved`；确认 body publish 等价、hand owner gating 仍来自本帧可输出 DRIVER body evidence、left/right 与 owner 顺序保持、`FrameBodyView` 指针生命周期安全、output map key 不变。
- `runtime_replay: not_executed`
- `unit_tests: not_added`
- `board_validation: not_required`

### 0.1.0C 2026-06-12 后排误跟踪主驾修复证据

- 代码范围：
  - `/home/jichao/dms/include/utils/track.h`
  - `/home/jichao/dms/source/utils/track.cpp`
  - `/home/jichao/dms/etc/track_params.json`
- 本地检查：
  - `git diff --check -- include/utils/track.h source/utils/track.cpp etc/track_params.json`：通过。
  - `python3 -m json.tool etc/track_params.json`：通过。
- J6B 编译：
  - `bash scripts/compile_j6b.sh` 产出 `/home/jichao/dms/build/main/sdk`，构建日志包含 `[100%] Built target sdk`。
- 独立 review：
  - 第一轮 review 判定 `fail`，因为板端日志仍有 2 次 `face=1` 被选为 driver，其中一次为 `stable=BACK_PASSENGER` 后被选中。
  - 第二轮修正后，review/functional conclusion 为 `pass`。
- 板端验证：
  - 部署目标：`root@192.168.2.10:/userdata/dms/sdk` 与 `/userdata/dms/etc/track_params.json`
  - 运行命令：`cd /userdata/dms && sh run.sh`
  - 结束信号：`Can not get image from J6M PIC` 连续出现，表示图片已回灌完成。
  - 二次回灌日志：`/tmp/dms-driver-misbinding-logs-after2/dms*.log`
- 二次回灌统计：
  - `face-first driver face select face=1`：0 次。
  - `face-first driver face select face=0`：189 次。
  - `face-first driver face reject back passenger`：126 次。
  - `face-first driver face reject smaller face=1`：61 次。
- 验证结论：
  - 本次 2m 回灌样本中，后排 face/head 不再被选为主驾，driver 选择稳定落在 `face=0`。
  - 该结论关闭本次“后排误跟踪为主驾”样本级任务；不关闭全部代表性视频集、全部车型 anchor 参数和 face 区域级唯一输出的长期验证缺口。

### 0.1.0B 2026-06-11 Sentinel、ID 与阶段拆分证据

- 代码范围：
  - `/home/jichao/dms/include/utils/track.h`
  - `/home/jichao/dms/source/utils/track.cpp`
- `git diff --check -- include/utils/track.h source/utils/track.cpp`：通过。
- `bash scripts/compile_j6b.sh`：通过，`track.cpp` 参与构建并完成 `libsdk.so`。
- 独立 repo review：`approved`，无 findings；确认 Body/Hand 阶段顺序、assignment、left-before-right、hit/miss、key、日志、sanitize/publish 和 slot 引用生命周期保持等价。
- verification-manager：`conditional_pass`；确认 public API、helper 声明/定义、sentinel 使用和编译产物，但由于没有行为单测或 before/after result-map 对比，不把编译和静态审查提升为运行等价证明。
- 语义核对：`bodyId / handId` 初始继承 `faceId` 数值，但 body/hand 生命周期独立；face 消失后内部状态可保留原 id，hand 发布仍受当前 DRIVER body evidence 约束。
- `runtime_replay: not_executed`
- `unit_tests: not_added`
- `board_validation: not_required`

### 0.1.0A 2026-06-09 DmsTrack 内部重构证据

- 代码范围：
  - `/home/jichao/dms/include/utils/track.h`
  - `/home/jichao/dms/source/utils/track.cpp`
- Patch integrity：
  - `git diff --check -- include/utils/track.h source/utils/track.cpp`
  - 结果：退出码 `0`
- J6B 编译：
  - `bash scripts/compile_j6b.sh`
  - 结果：退出码 `0`，最终 `[100%] Built target sdk`
  - `track.cpp` 已参与构建，变更文件无编译 error 或 warning
- 独立 repo review：
  - 结论：`approved`
  - 未发现 Update 顺序、Face Hungarian、Body driver-first ownership、生命周期推进、ID/key、sanitize、日志或 Hand 语义回归
- 静态检查边界：
  - 仓库未发现原生独立 `clang-tidy`、`cppcheck` 或同类入口
  - 本轮覆盖为 `git diff --check`、J6B `-Wall` 编译诊断和独立静态语义审查
- 未执行项：
  - `runtime_replay: not_executed`
  - `unit_tests: not_added`
  - `board_validation: not_required`
- 注释治理补充：
  - 独立 review：`approved`
  - pre/post snapshot 剥离注释与空白后代码 token 一致
  - `git diff --check` 再次通过
  - J6B 编译再次通过，最终 `[100%] Built target sdk`
  - 独立 verifier 因 forked build 目录只读未能执行编译；host 在授权可写环境补跑并披露参与范围
- Hand Phase 4A：
  - 外围 owner、prediction、cleanup、publish 阶段完成 private helper 拆分
  - independent repo review：`approved`，无 findings
  - `git diff --check`：passed
  - `bash scripts/compile_j6b.sh`：exit `0`，最终 `[100%] Built target sdk`
  - first/second pass、Hungarian、miss 推进和四个 publish stage tag 经静态审查保持不变
  - `runtime_replay: not_executed`，`unit_tests: not_added`，`board_validation: not_required`

### 0.1.0 2026-05-23 head-first 编译证据

- 代码范围：
  - `/home/jichao/dms/include/utils/track.h`
  - `/home/jichao/dms/source/utils/track.cpp`
- 本地编译：
  - `bash scripts/compile_j6b.sh`
  - 结果：`[100%] Built target sdk`
- 静态结论：
  - head/face trackId 已成为 identity id 的唯一分配入口；
  - body/torso evidence 以 head trackId 为 key 维护；
  - body/torso 不再独立生成 trackId；
  - driver head 选择中 small face 与尺寸突变被优先过滤，size continuity 权重大于 position loss；
  - hand evidence 只挂在 driver head-bound body evidence 下。
- 证据限制：
  - 未执行板端验证；
  - 未执行视频回放；
  - 未采集 callback/fusion 同 key 消费日志。

### 0.1.1 已由代码静态证据支撑

- head/face 使用恒速度模型并作为 identity 主锚点
- body/torso evidence 以 head trackId 为 key，使用预测、匹配、acquisition 与生命周期管理
- hand 使用恒加速度模型，但 2026-04-07 起不再向下游输出 miss 预测框
- body 结果作为 head-owned evidence legacy 输出，不再作为乘员级主锚点
- 上游结果事实源是 body / face / leftHand / rightHand 四类 map
- driver head 最终唯一化已在代码中显式实现
- 更新顺序为 `face/head -> selectDriverHead -> body evidence -> hand evidence`
- 配置从 `track_params.json` 读取，并以 `DEFAULT` 加车型覆盖
- `m_humanTrackResultMap` 只是导出兼容层，不是上游事实源
- track 输出在写入四类 track map 前已有统一 sanitize/clamp 与非法框过滤
- initialized face first pass 已有连续性门控；driver 相关 face 绑定使用更严格的 `distanceLoss <= 0.45`
- first pass 被连续性门控明确拒绝的 face track，同帧不会再通过 second pass 绕回匹配
- 2026-06-12 后，driver face selection 已验证在目标 2m 回灌样本中不会选择 stable BACK_PASSENGER 后排候选，且不依赖收紧 `distanceLoss`。
- 当前代码已完成 head-first 第一轮实现：driver identity 来自 head/face track，body/hand 作为 head-bound evidence 组织。
- head-first 当前已有本地编译证据，但没有回放或板端证据证明其运行效果。
- head-first 设计方案已落点到 `head-first跟踪方案.md`，实现事实已落点到 `tracking_implementation_current.md` 和 2026-05-23 闭环记录。

### 0.1.2 由历史记录支撑但本轮未重新执行

- 03-24、03-25、03-31 各轮编译级验证曾通过
- 03-25、03-31 曾有独立审查通过或 pass_with_risks 记录
- 2026-04-05 DMS 主驾打哈欠误报修复已按 revised acceptance sign-off：
  - 最终接受的实现仅保留在 `/home/jichao/dms/source/utils/track.cpp`
  - acceptance standard: whole-process driver tracking remains normal；在 `3429360843..3441459880` 内最多允许 `4` 帧 yawn-positive
  - board/log facts: driver track id unique value `0`，yawn-positive frame count `4`，driver face logs 具备 `candidates=1` 且频繁出现 `small_filtered=1`
  - review outcome: `pass_with_risks`
- 2026-04-05 快速运动恢复阶段预测-更新一致性修复已完成：
  - `/home/jichao/dms/source/utils/track.cpp` 对 body/face/hand 的命中检测更新路径做了收敛
  - compile result: `bash scripts/compile_j6b.sh` passed，最终 `[100%] Built target sdk`
  - review outcome: `pass_with_risks`
  - current evidence level 仍为 compile/review 级，不是运行样本级
- 2026-04-05 的修复仍未补运行回放证据，因此它只能支撑实现边界，不支撑效果验收
- 2026-04-05 后排乘客头部误跟踪为副驾驶修复已完成：
  - 当前代码已移除 body small-face 判定污染并收敛 unique-driver 回退逻辑
  - repo review 结论为 `pass_with_risks`
  - 仍缺最终问题样本日志级验收，因此只能作为实现/验证边界补充，不能视为功能完全闭环
- 2026-04-07 跟踪框越界导致板端 coredump 调查与修复已完成：
  - 代码改动仅落在 `/home/jichao/dms/source/utils/track.cpp`
  - compile result: `bash scripts/compile_j6b.sh` passed，最终 `[100%] Built target sdk`
  - board result: 新 `sdk` 已部署到 `192.168.2.10:/userdata/dms/sdk`，`bash run.sh` 覆盖到目标帧 `3425547100` 且未再出现 `abort` / `core dumped`
  - review outcome: `pass_with_risks`
  - 残余风险：sanitize clamp 日志可能过多；hand miss 不输出后，HandOff 等下游会更频繁看到空 hand map，需要单独做功能侧确认

### 0.1.3 2026-05-08 2m 摄像头后排 head 误绑定主驾修复证据

- 代码范围：
  - `/home/jichao/dms/source/utils/track.cpp`
- 本地编译：
  - `bash scripts/compile_j6b.sh` passed，最终 `[100%] Built target sdk`
- 独立 repo review：
  - 最终结论 `pass`
  - 确认 first-pass reject 不再被 second-pass 绕回，driver second-pass face 使用 strict gate
- 板端验证：
  - 新 `sdk` 已部署到 `root@192.168.2.10:/userdata/dms/sdk`
  - 运行命令：`cd /userdata/dms && sh run.sh`
  - 回灌样本：`/userdata/dms/dumps_2m/dumps_20260507_02/images`
  - run 结束方式：收集到证据后手动 kill `sdk` 进程，退出码 137 属于预期清理
- 关键日志事实：
  - 异常宽 driver body 场景下，非主驾候选被拒绝：
    - `driver face reject body=1 det=1 score=3.38 iou=1.00 dist=0.57 size=1.81`
    - `driver face reject body=1 det=2 score=2.58 iou=1.00 dist=0.77 size=0.81`
  - 主驾 face 仍稳定匹配：
    - `driver face match body=1 det=0 candidates=3 small_filtered=0 score=0.25 iou=0.18 dist=0.05 size=0.02`
    - `track det-hit body=1 det=0 instance=face stable=DRIVER`
  - 下游继续消费同一 driver/head track：
    - `Headface found: TrackID=1`
    - `Driver Gazeface found: TrackID=1`
    - `driver track id: 1`
- 验证结论：
  - 后排/非主驾 head 在异常宽 driver body ROI 下未绑定到主驾 track，driver head 绑定保持稳定。
  - 本次证据可关闭该 2m dump 场景的临时修复任务，结论为 `passed_with_risks`。

### 0.1.4 当前仍未被充分证据支撑

- face 区域级最终唯一输出
- left_hand / right_hand 区域级最终唯一输出
- “较好的 ID 连续性”效果性结论
- 运行时 replay / 视频流级验证
- face / hand fallback 路径是否在更广泛运行样本中完全满足唯一性约束
- 对快速运动恢复的效果改善是否能推广到代表性样本集

## 0.2 Current Review Conclusion

- 2026-06-09 的证据足以关闭“保持 public API 和既有算法契约完成 DmsTrack 首轮内部可读性重构，并通过编译、仓库可用静态检查和独立审查”的任务。
- 2026-06-11 的证据足以关闭 sentinel 语义、ID 命名/生命周期边界和 Body/Hand 阶段顺序显式化任务；closure 仍只到编译与独立静态审查级。
- 2026-06-13 的证据足以关闭 output-as-input 消除和 `FrameBodyView` 单帧投影落地任务；closure 仍只到静态审查与本地构建级，不证明多帧运行等价。
- 2026-06-15 的证据足以确认 helper 已删减、接口已按非对称职责分层且代码可编译；在独立 review 和 runtime replay 缺失时，状态保持 `implemented_pending_review`。
- 2026-06-15 深模块重新评审已经完成独立 review，并将该状态更新为 `changes_requested_for_refactor_route`：不要求在实验分支继续 rework，而是要求从稳定基线重新规划 clean refactor。
- 该 closure 不证明运行时行为等价，不关闭 ID 连续性、face/hand 区域级唯一性或代表性视频验收缺口。
- 当前系统主框架不是“未实现”，而是“主框架已形成，但仍有输出唯一性与运行级证据缺口”
- 以本轮允许范围内的静态读取判断，`多目标跟踪功能审核记录-2026-03-27` 中关于唯一性未闭合和 ID 连续性证据不足的结论仍然有效
- `多目标跟踪设计失配修复未闭环记录-2026-03-27` 记录的是一次中间阻塞状态，已经不再代表当前整体状态
- DMS 主驾打哈欠误报修复属于 accepted with risks 的项目闭环，不应被提升为正式知识，也不应表述为已完成根因级彻底消除
- 跟踪框越界 coredump 的当前 route 已收敛为 `bug_fix(track-only)`，本轮证据足以关闭 incident，但还不构成“所有 hand 相关功能指标已重新验收通过”
- 2m 摄像头后排 head 误绑定主驾的临时修复已完成板端日志验证，可作为该问题的项目级闭环；但它不关闭整体 face 区域级唯一输出缺口。
- 2026-05-09 架构决策将 head-first 定为下一阶段推荐主线；该结论是项目决策，不是运行验证结果。
- 当前 current 组已能在不依赖 baseline 作为默认入口、也不依赖两篇及以上 delta 作为当前态补洞的前提下恢复 Tracking 主态；但运行效果仍未闭合

## 0.3 Required Next Verification

- 如果要把 Tracking 从“当前实现已形成”推进到“功能验收接近闭合”，优先补：
  1. face 区域级唯一输出验证
  2. left/right hand 区域级唯一输出验证
  3. 代表性视频或日志回放，验证 ID 连续性和 hand miss 不输出后的功能影响
  4. 快速运动恢复样本，验证 body/face/hand 的 `predBox / detection / updated box` 三者关系是否按预期收敛
- 若后续要重新评估 DMS driver false-yawn 的根因消除，建议补更长窗口 replay，专门量化 identity-swap 风险
- 若后续继续优化 2m 场景，建议补更长 2m 视频集，对 `driver face reject`、`driver face match`、`driver second-pass face match orphan=` 做计数型统计，而不是只依赖抽样日志。
- 若后续进入 head-first 运行验收，必须补：
  1. 2m profile 下 body/hand disabled 且不发布 stale body/hand 的回放验证；
  2. 5m profile 下 driver head-bound body/torso 的 owner 稳定性验证；
  3. hand owner source、left/right slot、orphan takeover 在手部大幅运动和多人干扰下的序列统计；
  4. driver identity source 日志，区分 `head_first`、`body_fallback` 与 reject reason。
- 若后续使用 HumanPose-assisted hand association，需要单独验证 wrist 已有证据链，以及 elbow/shoulder/arm direction 对 hand owner、left/right、miss recovery 的增益。
- 若后续继续沿用本轮 sanitize/clamp 方案，建议补一次日志降噪，避免 `track sanitize clamp` 在板端形成噪声洪泛
- 若后续代码再次触及 `track.cpp`、`AtomicResult` 或导出链路，应重新跑 `knowledge_sync_check`，并再次判断 recoverability 状态。

## 0.4 Current Boundary

本文档只回答当前证据状态，不等价于重新执行完整审核。若后续代码变更 touching `track.cpp`、`AtomicResult` 或导出链路，应重新做 `knowledge_sync_check` 并更新本文件。

## 0.5 Recoverability Verdict

- recoverability_status: `partial`
- 判定依据：
  - 读取 `tracking_overview_current + tracking_design_current + tracking_spec_current + tracking_implementation_current + tracking_validation_current` 已能恢复当前 Tracking 的主要设计、默认实现约束、实现事实与验证边界。
  - 只需少量代码路径辅助核对事实源：`track.h`、`track.cpp`、`atomic_result.h`、`fuse_algorithm.cpp`、`humanpose_model.cpp`、`handpose_model.cpp`。
  - baseline 与历史 delta 已全部降级为 `default_entry: false`，不再承担默认恢复职责。
  - 默认情况下不再要求拼接 baseline 或两篇及以上 delta 才能理解当前态。
  - 代码里仍存在 fallback 输出路径，但 current 文档已经明确把该风险归入验证边界，而不是恢复入口缺口。
- 保留限制：
  - 该判定只说明 current 组可恢复当前主态，不等价于运行效果已验证闭环。
  - 由于仍存在 replay、区域级唯一性、ID 连续性和 head-first 落地验证缺口，本组不声明单次恢复完全闭环。
  - 若默认恢复 bundle、事实源代码路径或历史文档入口关系变化，必须重新判定本节。

## 0.6 Historical Mapping

- 03-27 审核记录中的有效 blocker 已收敛到本文件
- 03-31 手部连续性优化的收益与风险判断也已收敛到本文件
- 2026-04-05 DMS 主驾打哈欠误报修复的 accepted-with-risks 结论已收敛到本文件，但仍保留残余风险描述
- 2026-04-05 后排乘客头部误跟踪修复的 pass-with-risks 结论已收敛到本文件
- 2026-05-08 2m 摄像头后排 head 误绑定主驾修复的板端日志证据已收敛到本文件
- 2026-05-09 head-first over body-first 决策已收敛到本文件，但不提升为已验证运行事实
- 当前 validation 仅负责证据与边界判定，不承担设计职责或实现职责

## 0.7 Current Sync Rule

- must_update_when:
  - 已有证据等级变化
  - 功能审核 blocker 被关闭或新增
  - hand continuity 的收益/风险评估变化
  - 默认恢复所需的验证边界变化
  - DMS driver false-yawn 的 acceptance standard 或风险边界变化
  - 2m 摄像头 head/body association 的 gate、日志证据或风险边界变化
  - head-first 实现、回放或板端验证证据状态变化
- absorbs_history_from:
  - `多目标跟踪功能审核记录-2026-03-27.md`
  - `多目标跟踪设计失配修复未闭环记录-2026-03-27.md`
  - `多目标跟踪手部连续性优化闭环记录-2026-03-31.md`
- evidence_only_docs:
  - `多目标跟踪功能审核记录-2026-03-27.md`
  - `多目标跟踪设计失配修复未闭环记录-2026-03-27.md`
- not_a_default_entry_anymore:
  - `多目标跟踪功能审核记录-2026-03-27.md`
  - `多目标跟踪设计失配修复未闭环记录-2026-03-27.md`
