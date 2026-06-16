---
title: DMS Head-first 渐进跟踪方案
summary: DMS Tracking head-first 当前推荐设计方案。身份 owner 来自 head/face track；body/hand 继承 owner key 但保持独立生命周期；后续实现应吸收 deep-module clean refactor 约束、Body 四态 edge 和运行标定要求。
status: verified
doc_role: solution_design
truth_role: plan
lifecycle_state: active
default_entry: false
retrieval_priority: implementation_when_head_first
implementation_state: implemented_compile_verified_no_board_and_pending_refactor
decision_scope: DMS Tracking head-first design plan
sources:
  - 02_Projects/DMS/04_Tracking/tracking_overview_current.md
  - 02_Projects/DMS/04_Tracking/tracking_design_current.md
  - 02_Projects/DMS/04_Tracking/tracking_spec_current.md
  - 02_Projects/DMS/04_Tracking/tracking_implementation_current.md
  - 02_Projects/DMS/04_Tracking/tracking_validation_current.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/head-first优先于body-first跟踪主线决策记录-2026-05-09.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/head-first双阶段body-torso匹配静态分析记录-2026-05-23.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/head-first跟踪代码重构闭环记录-2026-05-23.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/DmsTrack深模块重新评审与CleanRefactor规划-2026-06-15.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/Tracking方案优化与历史实现归档记录-2026-06-16.md
  - 02_Projects/DMS/04_Tracking/座舱乘员多目标跟踪方案.md
  - 90_Archive/02_Projects/DMS/04_Tracking/座舱多目标跟踪实现.md
  - /home/jichao/dms/source/utils/track.cpp
  - /home/jichao/dms/include/utils/track.h
  - /home/jichao/dms/include/models/atomic_result.h
scope: 适用于 DMS Tracking head-first 设计评审、clean refactor 实现复核和后续运行验证准备；第一轮代码已落地并完成本地编译，后续 body/hand lifecycle 和四态 edge 仍需标定与验证。
risks:
  - 本文档是项目设计方案，不替代代码 diff、回放报告或板端验收。
  - 第一轮实现只有本地编译证据，没有实车、板端或代表性视频回放证据。
  - 具体代码落地应读取 tracking_implementation_current.md、tracking_spec_current.md 和 DmsTrack 深模块重新评审记录。
updated_at: 2026-06-16
---

> 文档状态：本文件是 head-first 当前推荐设计方案。2026-05-23 第一轮实现已落地；2026-06-15 深模块重新评审后，后续实现应以 phase-level 接口、局部 solver 表示、Body 四态 edge 和独立 lifecycle sweep 为目标。代码事实与验证边界应同时读取 `tracking_implementation_current.md`、`tracking_validation_current.md` 和闭环记录。

# 1 目标

实现对驾驶员/乘员的**头部/人脸、人体/躯干证据、双手**进行稳定跟踪，满足以下要求：

- driver identity 优先由 head/face track 稳定决定；
- raw body detection box 不再作为稳定 driver/person 主锚点；
- 在短时漏检、局部遮挡、检测抖动、手部大幅运动场景下保持 driver 身份连续；
- 2m 场景默认只保留 head/face 相关链路，不输出陈旧 body/hand；
- 5m 场景在 driver head 选定后再绑定 body/torso evidence，并基于该证据进行 hand association；
- 对双手保持左手/右手连续性，避免异常 body 框扩大 hand owner；
- 保持现有四类 map ABI：`body / face / left_hand / right_hand`；
- 为后续 HumanPose 辅助 hand association 预留边界；
- 不引入 `Occupant/PersonTrack + PartTrack` 作为当前或默认后续路线。

---

# 2 总体思路

系统仍采用“**检测 + 卡尔曼滤波预测 + 匈牙利匹配 + 生命周期管理**”的多目标跟踪框架，但调整层级主次关系。

历史 body-first 流程为：

`body -> face -> hand`

head-first 设计主线为：

`head/face -> driver identity -> head-bound body/torso evidence -> hand association`

## 2.1 层级设计

整体分为四个层级：

1. **头部/人脸跟踪**  
   负责建立 driver identity 的主入口。head/face track 先于 body/hand 参与 driver 选择，提供后续 body/torso evidence 与 hand association 的上游约束。

2. **人体/躯干证据跟踪**  
   body detection 仍可跟踪和输出，但不再建立 driver identity。5m 场景中，body 作为 driver head 约束后的 body/torso evidence，用于兼容 body map、约束手部搜索和服务后续 HumanPose 输入。body 的 owner key 来自 face，生命周期仍由 body 自身连续性决定。

3. **手部跟踪**  
   手部不再直接依附 raw body box 扩大的范围。手部 owner 需要由 driver head-bound body/torso 或业务搜索区域约束，并结合自身时序连续性与 left/right 历史状态。hand 的发布受 owner 证据约束，但内部 slot 生命周期不应只由本帧是否可发布决定。

4. **姿态辅助证据**  
   HumanPose 不是第一阶段必须项。未来若 hand association 仍不足，优先使用 wrist / elbow / shoulder / arm direction evidence 辅助手部 owner、left/right 和丢失恢复。

各类轨迹仍采用统一的短期状态与长期状态管理机制：

- **短期状态**：解决逐帧匹配、命中、丢失、轨迹延续问题；
- **长期状态**：解决轨迹是否稳定输出、driver identity 是否可信、手部左右槽位是否可发布的问题。

## 2.2 Owner 与生命周期分离原则

head-first 只改变身份来源，不应把 body/hand 的生命周期重新收缩为 face 生命周期的附属物。

- `face/head` 负责分配和选择 owner identity，是 driver identity 的主来源。
- `body/torso evidence` 继承 owner face id 作为 legacy key，但自身仍按 body detection、motion state、hit/miss 和 retire 阈值独立推进。
- `left/right hand` 继承 owner face id 作为 legacy key，但左右槽位按自身 prediction、match、hit/miss、reset/cleanup 独立推进。
- face 短时消失时，body/hand 可以在 bounded grace period 内保留原 owner key 和 motion state；是否对外发布仍受当前业务 owner 证据和稳定输出条件约束。
- face 已确认退休或 id 复用前，body/hand 必须通过明确的 handoff、miss sweep 或 cleanup 规则收敛，不能永久悬挂。
- 这继承了历史方案中 body/face/hand 生命周期解耦的正确部分，但不继承 body-first identity 主线。

## 2.3 基本流程

每一帧的设计流程如下：

1. 读取当前帧检测结果，得到 head/face、body、hand 候选框；
2. 对 head/face 历史轨迹执行预测和匹配；
3. 基于稳定 head/face、业务 ROI、历史连续性和迟滞机制选择 driver head；
4. 根据车型/摄像头业务配置决定是否继续处理 body/hand；
5. 2m 或无 body/hand 业务时，清理 body/hand 陈旧状态并只输出 head/face 相关结果；
6. 5m 且需要 handoff/handpose 时，在 driver head 约束下匹配 body/torso evidence；
7. 在 driver head-bound body/torso 或业务搜索区域内匹配 left/right hand；
8. 根据 hit/miss、owner 证据和左右手迟滞规则输出稳定结果；
9. 将内部 head-first 绑定关系投影回现有四类 map。

可概括为：

`稳定 head/face -> 选择 driver -> 绑定 body/torso evidence -> 约束 hand owner -> 输出 legacy map`

---

# 3 轨迹层级设计

## 3.1 头部/人脸跟踪

头部/人脸跟踪是 driver identity 的主入口，负责：

- 建立并维护 driver head 连续性；
- 作为 face/head 下游模型的稳定输入；
- 作为 5m body/torso evidence 的绑定起点；
- 为 hand association 提供 owner 上游约束。

### 3.1.1 初始化

在首帧或无稳定 head/face 轨迹时，将检测到的 head/face 框初始化为轨迹。轨迹可继续使用现有 `TrackInfo` 和卡尔曼状态，不要求新增对外 ID 类型。

### 3.1.2 状态建模

head/face 采用匀速模型，状态可表示为：

$\mathbf{x}_t^{head} = [c_x, c_y, w, h, v_x, v_y]^T$

其中：

- $c_x, c_y$ 表示框中心位置；
- $w, h$ 表示框宽高；
- $v_x, v_y$ 表示中心点速度。

观测向量为：

$\mathbf{z}_t^{head} = [c_x, c_y, w, h]^T$

### 3.1.3 状态预测

对上一时刻更新后的 head/face 轨迹执行卡尔曼滤波预测，得到预测状态和预测框。

### 3.1.4 数据关联

head/face 检测与 head/face 预测轨迹采用匈牙利匹配。匹配损失应综合空间重叠、位置距离、历史连续性和业务区域约束。dummy loss 继续承担拒绝劣质匹配的作用。

### 3.1.5 Driver Head 选择

driver head 选择优先级为：

1. 历史 driver head 的连续命中；
2. 业务配置中 driver 区域内的稳定 head/face；
3. 短时 head miss 时的最近可信 driver head 记忆；
4. body/torso evidence 只能作为 fallback evidence，不能作为主来源。

driver 切换需要迟滞。单帧 head/face 抖动不能立即切换 driver。

### 3.1.6 头部唯一原则

同一 driver 区域内如存在多个 head/face 候选，应仅发布一个 driver head/face。其余候选可作为内部竞争轨迹保留，但不能因异常 body 框扩大而被吸入 driver。


---

## 3.2 人体/躯干证据跟踪

body 在 head-first 方案中不是 driver/person 主锚点，而是证据层。

body/torso evidence 负责：

- 在 5m 场景中为 driver head 提供 body/torso 区域证据；
- 兼容现有 `m_bodyTrackResultMap`；
- 为 hand association 提供搜索约束；
- 为未来 HumanPose 输入提供候选裁剪区域。

### 3.2.1 启动条件

body/torso evidence 仅在业务配置要求处理 body/hand 或下游需要 body evidence 时启动。2m 或只需要 face/head 的链路默认不启动 body/hand。

### 3.2.2 状态建模

body detection 可继续使用匀速模型：

$\mathbf{x}_t^{body} = [c_x, c_y, w, h, v_x, v_y]^T$

但 raw body detection box 只表示检测证据，不表示稳定躯干锚点。

### 3.2.3 Head-to-body 绑定

body candidate 必须由 driver head 约束后才能成为 driver body/torso evidence。约束包括：

- 与 driver head 的空间关系合理；
- 不吸入副驾/后排 head；
- 不因手部伸出导致异常大 body 而扩大 owner；
- body miss 不清空稳定 driver head。

### 3.2.4 Body 全局 assignment 与四态 edge

后续 body/torso evidence 应采用 owner-to-body-detection 全局 assignment。solver 只负责一对一最小代价分配；Track、Reacquire、Bootstrap、Forbidden 是 body phase 对 edge 的业务解释，不进入通用 solver。

四态 edge 规则：

| 模式 | 条件 | 处理 |
|---|---|---|
| Track | owner 有 body track；tracking loss 可信；face consistency 不明显冲突 | `CorrectMotion`、`AdvanceHit`，保持 body 生命周期连续 |
| Reacquire | owner 有 body track；tracking loss 不可信；acquisition loss 高可信 | 保持 owner face id；重置或强校正 motion state；不把 `hitCount` 重置为 1；若之前已可输出，保持输出连续 |
| Bootstrap | owner 没有 body track；acquisition loss 可信 | 新建 body evidence；`hitCount` 从 1 开始；按 `hitThreshold` 决定是否输出 |
| Forbidden | tracking 与 acquisition 都不可信，或 face consistency 冲突 | owner unmatched；已有 body 执行 `AdvanceMiss`；必要时 retire |

标定前的保守实现可以只打开 Track 与 Bootstrap：已有 body track 的 tracking 不可信时直接 miss，不启用 Reacquire。标定后打开 Reacquire 必须满足：

- tracking loss、acquisition loss、driver/non-driver bias 与 `dummyLoss` 已有场景分布依据；
- acquisition gate 不会把 owner 绑定到几何更合理但身份错误的其他 body；
- face consistency gate 能拒绝后排/副驾探头、异常大 body 或跨 owner 竞争；
- runtime replay 明确允许 Reacquire 带来的输出 delta。

### 3.2.5 双阶段匹配边界

head-first 可以保留“双阶段”补救结构，但阶段主体必须清晰：

1. 第一阶段由 head/face track 建立和维护 driver identity；
2. 第二阶段只允许由已选 driver head 发起 body/torso evidence acquisition；
3. 未匹配 body track 不得在剩余 head/face detection 中申请、创建或抢占 identity；
4. body/torso second pass 只能产出 evidence 或 legacy map 投影，不能改写 driver head；
5. face/head second pass 只能维护 head continuity，不能重新退化为 body-first 绑定。

如果后续实现仍保留 body track 自身的预测、Hungarian、hit/miss 和 legacy body map 输出，它们只能服务 body/torso evidence 稳定性，不再承担 driver identity 决策。

### 3.2.6 输出原则

body map 只在业务配置允许时输出：

- 5m 场景输出 driver head-bound body/torso evidence 或兼容 body；
- 2m 默认不输出 body；
- body evidence 不足时可以不发布 body，而不是发布不可信 body。

---

## 3.3 手部跟踪

手部跟踪用于为 handpose、handoff、smoking-call 等依赖手部区域的业务提供稳定输入。

### 3.3.1 启动条件

hand tracking 仅在业务配置要求 handoff、handpose 或其他手部业务时启动。只需要 face/head 的 2m 链路默认不启动 hand。

### 3.3.2 左右手先验

左右手身份区分基于：

- 与历史 left/right slot 的连续性；
- 与 driver head-bound body/torso 或业务搜索区域的 owner 关系；
- 与上一帧左手/右手轨迹的一致性；
- 未来可用的 wrist / elbow / shoulder evidence。

左右手不能仅靠当前帧 x 位置瞬时翻转。

### 3.3.3 状态建模

手部仍采用匀加速模型，并显式维护尺度状态：

$\mathbf{x}_t^{hand} = [c_x, c_y, w, h, v_x, v_y, a_x, a_y, v_w, v_h]^T$

观测向量为：

$\mathbf{z}_t^{hand} = [c_x, c_y, w, h]^T$

### 3.3.4 数据关联

手部检测与 left/right hand 预测轨迹采用匈牙利匹配，但匹配前必须先通过 owner 约束。owner 约束来自 driver head-bound body/torso 或业务搜索区域。

### 3.3.5 状态更新

匹配成功的手部轨迹执行卡尔曼更新，并同步更新位置和尺度。匹配失败时增加丢失计数，内部可短时保留状态，但默认不发布预测框。

### 3.3.6 左手唯一原则与右手唯一原则

同一 driver owner 下，每侧手部只能发布一个稳定结果。若存在多个候选，以历史连续性、owner 证据、匹配损失和左右手迟滞共同决定发布对象。

### 3.3.7 orphan hand 约束

orphan hand 接管必须具备 owner 证据。异常大的 body detection box 不能单独扩大 orphan hand 接管范围。

### 3.3.8 Owner 消失后的 hand lifecycle

hand assignment 候选域和 lifecycle sweep 必须分离。只有当前可发布 owner 进入 hand assignment row 时，仍不足以定义所有 hand slot 的生命周期。

- initialized slot 即使本帧没有进入 assignment row，也必须按明确策略推进 miss、reset 或 cleanup。
- owner face 短时消失但 body/hand motion 连续时，可在 bounded grace period 内保留内部 slot，等待 owner 恢复或新 stable owner handoff。
- 对外发布仍要求当前业务允许的 driver body evidence 或等价 owner 证据；内部保留不等于发布放宽。
- 新 stable body evidence 接管同一区域时，应清理旧 owner 下的 orphan hand slot，避免 face id 复用污染。

---

## 3.4 HumanPose 辅助证据

HumanPose 不是第一阶段必须项。若未来 hand association 仍不足，优先增强路线为：

`head-first driver selection -> head-bound body/torso crop -> HumanPose -> wrist/elbow/shoulder evidence -> pose-guided hand association -> HandPose / Handoff`

设计约束：

- HumanPose 只作为 hand association 的辅助证据；
- wrist 可用于 hand-to-wrist 连续性；
- elbow/shoulder 和手臂方向可用于 owner、left/right 和丢失恢复；
- pose 不反向推翻 head-first driver identity；
- pose 丢失或不可靠时回退到 head-bound body/torso 与业务搜索区域；
- pose 不是引入 OccupantTrack 的理由。

---

# 4 匈牙利匹配方案

## 4.1 设计目标

匈牙利匹配继续用于解决以下问题：

- 当前检测应匹配到哪个已有轨迹；
- 哪些检测不应匹配任何历史轨迹，而应创建新轨迹；
- 哪些历史轨迹当前没有对应检测，应进入丢失状态。

系统继续采用**扩展损失矩阵 + dummy node** 的方式统一建模。

## 4.2 输入集合定义

设当前时刻的检测集合为：

$\mathcal{D}_t = \{d_1, d_2, \dots, d_m\}$

历史轨迹预测集合为：

$\mathcal{T}_{pred,t} = \{t_1, t_2, \dots, t_n\}$

不同部件使用不同候选集合：

- head/face：head/face detections 与 head/face tracks；
- body/torso evidence：body detections 与 body evidence tracks；
- hand：通过 owner 约束后的 hand detections 与 left/right hand tracks。

## 4.3 匹配损失定义

基础匹配损失仍由 IoU 损失和归一化距离损失组成：

$L(i,j) = \lambda_{iou} \cdot L_{iou}(i,j) + \lambda_{dist} \cdot L_{dist}(i,j)$

head-first 方案新增的是**匹配前后的约束语义**：

- driver head selection 使用 head/face 连续性和业务区域约束；
- body 只有在 driver head 约束下才可成为 driver body/torso evidence；
- hand 只有在 owner 证据成立时才可匹配和发布；
- rejected face/hand 不允许通过同帧 second-pass 绕过约束。

## 4.4 dummy loss 机制

dummy loss 继续表示“拒绝劣质匹配优于强行绑定”。当真实匹配损失高于 dummy loss 时，检测应新建或轨迹应进入丢失状态。

dummy loss 不应被用于强制把异常 body、face 或 hand 绑定到 driver。

## 4.5 扩展损失矩阵构造

扩展损失矩阵仍沿用 baseline：

- 左上区域：真实检测与真实轨迹；
- 左下区域：真实检测与伪轨迹；
- 右上区域：伪检测与真实轨迹；
- 右下区域：伪检测与伪轨迹。

head-first 的差异在于：进入矩阵前，候选集合已按 driver head、body/torso evidence 或 hand owner 约束进行过滤。

## 4.6 匈牙利最优分配

在扩展矩阵上使用匈牙利算法求最小总代价分配。输出仍用于：

- 检测与轨迹的一对一匹配；
- 未匹配检测的新建决策；
- 未匹配轨迹的丢失决策。

## 4.7 Deep-module clean refactor 约束

后续代码结构应遵循 2026-06-15 深模块评审结论：

- public `DmsTrack::Init/Update` 保持深接口，不暴露 face/body/hand 内部步骤；
- private header 只保留长期状态、稳定配置/ID 职责和 phase-level 方法；
- solver、edge classifier、row、key、snapshot 和临时 result 默认留在 `.cpp` anonymous namespace、函数局部 struct 或局部 lambda；
- `FrameBodyView`、`HandSlotKey`、`HandAssignmentRow`、`AssignmentResult` 不作为稳定 header 抽象；
- finalize 负责 sanitize 和 lifecycle 副作用，publish 只写 legacy output map；
- Body 四态 edge、Hand lifecycle sweep、global assignment 都属于行为变更或边界重组，必须用 replay、冲突样例和 diff 白名单验证。

---

# 5 短期状态更新

## 5.1 检测匹配到真实轨迹

匹配成功时：

1. 根据检测生成观测向量；
2. 执行卡尔曼更新；
3. 更新轨迹框、命中计数和丢失计数；
4. 对 hand 同步更新尺度状态；
5. 记录 owner source 和 reject reason。

## 5.2 检测匹配到伪轨迹

检测未匹配到已有轨迹时：

- head/face 可按业务区域和置信度新建；
- body 只能作为 body evidence 新建，不能直接新建 driver identity；
- hand 只有 owner 证据成立时才允许初始化 left/right slot。

## 5.3 轨迹匹配到伪检测

轨迹未匹配到检测时：

- 增加丢失计数；
- 保留短时状态用于后续恢复；
- head miss 可触发短时 driver fallback；
- body miss 不清空 driver head；
- hand miss 默认不发布预测框。

---

# 6 长期状态更新

## 6.1 生命周期独立与发布约束

内部生命周期与对外发布是两层判断：

- `face/head` 生命周期决定 owner identity 是否仍可信；
- `body/hand` 生命周期决定 evidence 是否仍连续；
- 发布层必须同时满足业务 owner 证据、稳定门槛、sanitize 和唯一性约束；
- 因 owner 暂失而禁止发布，不等于必须立即删除 body/hand 内部状态；
- 因 owner 已确认退休、id 即将复用或 handoff 已完成，必须推进 cleanup，不能让内部状态永久保留。

## 6.2 删除失活轨迹

达到 miss 删除门限后删除对应轨迹。禁用 body/hand 的业务模式下，应清理或冻结 body/hand 状态，避免陈旧结果发布。

## 6.3 输出稳定轨迹

只有达到稳定条件且满足 owner 约束的轨迹才允许输出：

- face/head：输出稳定 driver head/face；
- body：仅在业务允许时输出 driver head-bound body/torso evidence；
- hand：仅输出通过 owner 证据、稳定门限和左右手迟滞的 left/right hand。

## 6.4 稳定属性更新

driver identity 稳定属性由 head/face 主导。body center ROI 只能作为 fallback evidence，不再作为主来源。

## 6.5 兼容输出

第一阶段保持四类 map ABI：

- `m_bodyTrackResultMap`
- `m_faceTrackResultMap`
- `m_leftHandTrackResultMap`
- `m_rightHandTrackResultMap`

内部 head-first 绑定关系需要投影回 legacy map。该投影是兼容层，不应反向定义 driver identity。

---

# 7 业务模式约束

业务模式由车型/摄像头配置或 pipeline 上游决定。tracking 设计不定义具体字段名，也不假设配置文件路径。

设计只要求上游能够明确提供以下语义：

- 是否为只需要 face/head 的链路；
- 是否需要 body evidence；
- 是否需要 hand tracking；
- 是否需要 handpose、handoff 或其他手部业务；
- 是否允许 body fallback；
- 是否需要发布兼容 body map。

2m 默认只需要 face/head 时，应关闭 body/hand 链路。5m 需要 handoff/handpose 时，应启用 body evidence 和 hand association。

---

# 8 与下游模型的关系

- `DmsHeadPos2Face`：依赖 driver head/face track，不应依赖 raw body box。
- landmark/headpose/gaze/eye：依赖 driver face/head track。
- HumanPose：未来应优先使用 head-bound body/torso crop 或业务配置裁剪区域；当前不是第一阶段必做项。
- HandPose：依赖经过 owner 约束后的 driver left/right hand map。
- Handoff：继续消费 face/body/hand/handpose/humanpose，但 body 在新设计中是 evidence，不是 identity root。
- smoking-call 或其他手部业务：依赖 hand map 时，应消费 head-first hand owner 后的手部输出。

---

# 9 非目标

- 不实现 `Occupant/PersonTrack + PartTrack`。
- 不把 OccupantTrack 写成当前目标或后续默认路线。
- 不把 head-first 写成已完成运行效果验收；第一轮代码实现和本地编译证据已由 current 文档与闭环记录承接。
- 不删除 body 相关逻辑。
- 不破坏四类 map ABI。
- 不在 tracking 方案中发明车型配置字段名或配置路径。
- 不引入新的 public `Occupant/PersonTrack + PartTrack` ID 层。必要的 body/hand 独立生命周期应留在 `DmsTrack` 内部 phase，不扩散成新的上游 ABI。

---
