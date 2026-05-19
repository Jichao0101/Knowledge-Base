---
title: DMS Head-first 渐进跟踪实现
summary: DMS Tracking head-first 设计的下一阶段实现方案。文档参考历史 baseline 实现文档结构，说明输入输出、状态复用、卡尔曼模型复用、函数落点、阶段性改造顺序与验证入口；不修改现有 ABI，不引入 OccupantTrack。
status: verified
doc_role: implementation_plan
truth_role: plan
lifecycle_state: active
default_entry: false
retrieval_priority: implementation_when_head_first
implementation_state: not_implemented
decision_scope: DMS Tracking head-first implementation plan
sources:
  - 02_Projects/DMS/04_Tracking/head-first渐进跟踪方案.md
  - 02_Projects/DMS/04_Tracking/Current Maintenance Records/head-first优先于body-first跟踪主线决策记录-2026-05-09.md
  - 02_Projects/DMS/04_Tracking/座舱多目标跟踪实现.md
  - 02_Projects/DMS/04_Tracking/tracking_implementation_current.md
  - /home/jichao/dms/source/utils/track.cpp
  - /home/jichao/dms/include/utils/track.h
  - /home/jichao/dms/include/models/atomic_result.h
  - /home/jichao/dms/source/models/humanpose_model.cpp
  - /home/jichao/dms/source/models/handpose_model.cpp
  - /home/jichao/dms/source/fuse_algos/handoff_algorithm.cpp
scope: 适用于下一阶段 head-first 代码实现拆解、review 和验证准备；不声称代码已实现。
risks:
  - 本文档为实现计划，不包含代码 patch、测试结果或板端验证。
  - 当前代码仍为 body-first，任何实现前必须重新检查最新代码。
updated_at: 2026-05-09
---

> 文档状态：本文件是 head-first 的实现方案。设计依据见 `head-first渐进跟踪方案.md`；当前代码事实见 `tracking_implementation_current.md`。

# 1 基本框架

## 1.1 目标

在不破坏现有四类 map ABI 的前提下，将当前 `DmsTrack` 从 body-first 执行顺序逐步改造为 head-first 决策主线：

`head/face -> driver identity -> head-bound body/torso evidence -> hand association`

第一阶段实现目标：

- driver identity 优先来自 head/face；
- body 只作为 5m 或手部业务下的 body/torso evidence；
- 2m 或只需要 face/head 的链路不发布陈旧 body/hand；
- hand owner 受 driver head-bound body/torso 或业务搜索区域约束；
- 输出仍写入现有四类 map；
- 不引入 OccupantTrack、PersonTrack、PartTrack 或新的对外 ID 体系。

## 1.2 输入变量

输入仍来自检测模型写入的：

```cpp
std::map<id, DetectBox> m_detResultMap;
```

`DetectBox` 结构继续沿用当前代码定义，至少包含：

- `left / top / right / bottom`
- `width / height`
- `score`
- `className`
- `index`
- `classId`

实现不修改检测模型输出格式。

## 1.3 输出变量

输出继续使用现有 `AtomicResult` 四类 map：

```cpp
std::map<track_id, TrackInfo> m_bodyTrackResultMap;
std::map<track_id, TrackInfo> m_faceTrackResultMap;
std::map<track_id, TrackInfo> m_leftHandTrackResultMap;
std::map<track_id, TrackInfo> m_rightHandTrackResultMap;
```

`TrackInfo` 继续承载：

- 当前框 `box`；
- 预测框 `predBox`；
- 瞬时与稳定 `PersonType`；
- `InstanceType`；
- `hitCount / missCount`；
- driver/front/back 计数；
- `MotionState`。

head-first 只改变 owner 决策、执行顺序和发布条件，不改变下游读取四类 map 的 ABI。

## 1.4 业务模式输入

tracking 实现不新增车型配置字段名，不假设配置路径。

实现只需要从现有车型/摄像头配置或 pipeline 上游获得以下语义：

- 当前链路是否只需要 face/head；
- 是否需要 body evidence；
- 是否需要 hand tracking；
- 是否需要 handpose / handoff；
- 是否允许 body fallback；
- 是否需要发布兼容 body map。

当前代码固定读取 `track_params.json` 是代码事实。若下一阶段要支持 2m/5m 分流，应在现有配置体系中接入上述语义，而不是在 tracking 内部发明独立字段。

---

# 2 卡尔曼滤波参数设置

## 2.1 匀速模型

head/face 与 body/torso evidence 继续使用匀速模型。

状态向量：

$$\mathbf{x}_k^{cv} = [c_x,\ c_y,\ w,\ h,\ v_x,\ v_y]^T$$

观测向量：

$$\mathbf{z}_k = [c_x,\ c_y,\ w,\ h]^T$$

实现可继续复用当前 baseline 中的状态转移矩阵、观测矩阵、初始协方差、过程噪声和观测噪声配置。

head-first 的区别是：

- head/face 的稳定性用于 driver identity；
- body 的匀速状态只用于 body/torso evidence；
- body 预测框不能单独扩大 face/head 或 hand owner。

## 2.2 匀加速模型

hand 继续使用匀加速模型。

状态向量：

$$\mathbf{x}_k^{ca} = [c_x,\ c_y,\ w,\ h,\ v_x,\ v_y,\ a_x,\ a_y,\ v_w,\ v_h]^T$$

观测向量：

$$\mathbf{z}_k = [c_x,\ c_y,\ w,\ h]^T$$

实现可继续复用 baseline 的匀加速状态转移、观测、协方差与噪声设置。

head-first 的区别是：

- hand 初始化前必须有 owner 证据；
- left/right 更新必须保留侧别迟滞；
- hand miss 可短时保留内部状态，但默认不发布预测框。

---

# 3 代码

## 3.1 当前函数事实

当前 `DmsTrack::Update` 顺序为：

```text
clear output maps
updateBodyTracks
updateFaceTracks
updateHandTracks
```

关键函数事实：

- `computePersonType` 当前使用 body center ROI 投票；
- `FaceBelongsToBody` / `FaceAnchorLoss` 当前使用 body 几何约束 face；
- `HandBelongsToBody` / `HandAnchorLoss` 当前使用 body 几何约束 hand；
- `updateFaceTracks` 当前 face key 复用 bodyId；
- `updateHandTracks` 当前 hand 按 bodyId 下 left/right slot 维护；
- orphan face/hand 清理已有局部防护，但仍围绕 body anchor。

## 3.2 目标函数组织

建议下一阶段逐步调整为：

```text
clear output maps
resolve business mode
updateHeadFaceTracks
selectDriverHead
if body/hand disabled:
    clear or suppress body/hand state and output
else:
    updateBodyEvidenceTracks
    bindDriverHeadToBodyEvidence
    updateHandTracksWithOwnerGate
publishLegacyMaps
```

其中 `resolve business mode` 只消费上游配置语义，不在 track 内部发明车型配置字段。

---

# 4 状态与 ID 策略

## 4.1 复用现有状态

第一阶段继续复用：

- `TrackInfo`
- `MotionState`
- `hitCount / missCount`
- stable/instant person type
- left/right hand slot
- Hungarian + dummy loss
- 输出框裁剪和合法性保护

## 4.2 ID 投影

实现期保持：

- 外部 bodyId 仍用于 `m_bodyTrackResultMap`；
- face map key 可继续兼容现有 key 语义；
- hand 仍输出 left/right map；
- 不新增 handTrackId；
- 不新增 occupantId。

head id 到 legacy key 的投影必须集中处理，避免散落在 face/body/hand 多处。

---

# 5 分阶段实现

## 5.1 P1 业务模式接入与日志

目标：让 track 能知道当前是否需要 body/hand 链路。

改动：

- 增加从现有车型/摄像头配置或 pipeline 上游读取业务模式语义的入口；
- 记录当前是否启用 body evidence、hand tracking、body fallback、兼容 body 发布；
- 不新增 tracking 自定义配置字段名；
- 保持默认行为可回退到当前 body-first。

验证：

- 2m 配置能进入 face/head only 分支；
- 5m handoff/handpose 配置能进入 body/hand 分支；
- 日志能复现本帧采用的业务模式。

## 5.2 P2 Head/Face Track First

目标：让 head/face 先于 body 决定 driver identity。

改动：

- 从 `updateFaceTracks` 中抽出可独立运行的 head/face 更新逻辑；
- 建立 driver head 选择逻辑；
- body center ROI 降级为 fallback evidence；
- driver face reject 后不能同帧绕回。

验证：

- body 中心跳变时 driver head 不切换；
- 副驾/后排 head 不被异常 driver body 吸入。

## 5.3 P3 2m 关闭 body/hand 链路

目标：2m 或 face/head only 模式不发布陈旧 body/hand。

改动：

- body/hand 禁用时不执行发布；
- 清理或冻结 body/hand 内部状态；
- 输出 map 保持为空或仅按明确兼容要求发布。

验证：

- 2m 回放中 body/hand 默认不输出；
- face/head 下游不受影响。

## 5.4 P4 5m Body/Torso Evidence

目标：body 在 5m 中作为 driver head 约束后的证据。

改动：

- `updateBodyTracks` 可保留预测、匹配、hit/miss；
- 新增 driver head 到 body evidence 的绑定；
- `computePersonType` 不再单独决定 driver identity；
- body miss 不清空 driver head。

验证：

- 主驾手伸中控导致 body 扩大时 driver 不切换；
- body evidence 失败时不发布不可信 driver body。

## 5.5 P5 Hand Owner Gate

目标：hand owner 由 driver head-bound body/torso 或业务搜索区域约束。

改动：

- 在 `updateHandTracks` 匹配前加入 owner 约束；
- left/right slot 加入迟滞；
- orphan hand 接管必须具备 owner 证据；
- hand miss 默认不发布预测框。

验证：

- 左右手交叉不瞬时换槽；
- 异常大 body 不扩大 hand owner；
- hand miss 不发布预测框。

## 5.6 P6 HumanPose 辅助

目标：当 P1-P5 后 hand association 仍不足时，使用 HumanPose evidence。

改动：

- 明确 HumanPose 输入裁剪来自 head-bound body/torso 或业务裁剪区域；
- 将 wrist / elbow / shoulder evidence 作为 hand association 的附加证据；
- pose 不反向推翻 driver head。

P6 不是第一阶段必须实现项。

---

# 6 输出与下游兼容

## 6.1 Face/Head

`DmsHeadPos2Face`、landmark、headpose、gaze、eye 应优先消费 driver head/face 结果。

## 6.2 Body

HumanPose 当前由 body map 触发。head-first 第一阶段应保持 body map ABI，但 body map 语义改为 driver head-bound body/torso evidence 或兼容 body。

## 6.3 Hand

HandPose 和 Handoff 继续消费 left/right hand map。hand map 的发布前提变为 owner 证据成立。

## 6.4 Handoff

Handoff 可继续消费 face/body/hand/handpose/humanpose，但不得把 raw body box 当作 driver identity 的唯一事实源。

---

# 7 日志与验证

## 7.1 建议日志

日志应记录：

- 当前业务模式语义；
- body/hand 是否启用；
- driver identity 来源；
- driver head id；
- bound body id；
- hand owner 来源；
- face/hand reject reason；
- body/hand 陈旧状态清理事件；
- HumanPose evidence 是否参与。

## 7.2 单测建议

- body 中心抖动但 head 稳定；
- face/head only 模式 body/hand 不发布；
- head miss 短时恢复；
- hand crossing；
- orphan face/hand 无 owner evidence。

## 7.3 回放建议

- 2m body 超宽但 head 稳定；
- 2m body/hand 关闭；
- 5m 主驾手伸中控；
- 副驾/后排 head 干扰；
- driver face reject；
- hand miss/reappear。

---

# 8 回滚方式

每阶段应保留可回滚路径：

- P1 可回退到当前固定配置行为；
- P2 可回退到 body fallback driver identity；
- P3 可回退到当前 body/hand 发布；
- P4 可回退到当前 body map 输出；
- P5 可回退到当前 hand slot 逻辑；
- P6 可关闭 HumanPose evidence。

回滚不应破坏四类 map ABI。

---

# 9 非目标

- 不改检测模型输出格式；
- 不改四类 map ABI；
- 不引入 OccupantTrack、PersonTrack、PartTrack；
- 不新增 handTrackId 或 occupantId；
- 不在 track 内部发明车型配置字段名；
- 不把 HumanPose 作为第一阶段必需依赖；
- 不声称 head-first 已实现。
