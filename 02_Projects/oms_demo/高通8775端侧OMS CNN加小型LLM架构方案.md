---
type: project_design
status: draft
project: oms_demo
summary: 以持续 CNN 感知、唯一时序状态演化、版本化事实存储和 VoI 驱动的小型 LLM residual reasoning 实现资源受限端侧 OMS
sources:
  - 用户于 2026-08-24 提供的初始 CNN、Temporal State Engine、Semantic State Store、Event Scheduler 与小型 LLM 架构
  - 用户于 2026-08-24 提供的架构职责边界、状态一致性、端侧调度和量产演进优化要求
scope: 高通 8775 端侧 OMS Demo 的架构设计、接口约束、调度和验证规划
risks:
  - 尚无目标板性能、内存、能耗和热稳定性实测数据
  - 小型 LLM 的场景泛化、复杂推理和量化后能力需要通过统一 Decision Context 任务集验证
  - 结构化语义压缩会丢失未被 CNN 与 Temporal State Engine 显式建模的视觉信息
  - 未经校准的模型置信输出不具有概率意义
updated_at: 2026-08-24
---

# 1 高通 8775 端侧 OMS：CNN + 小型 LLM 架构方案

## 1.1 设计定位

本方案保持“端侧 OMS、资源受限、CNN 高频感知、小型 LLM 低频推理”的原始定位，不试图用 CNN 与 LLM 复刻 VLM 的端到端开放视觉能力。系统拆分为两个时间尺度的问题：

1. 高频视觉感知与状态演化：持续提取人员、物体、姿态、视线和交互观测，并形成稳定状态与事件。
2. 低频场景决策：只在确定性策略无法覆盖、且推理可能改变最终 action 时，基于最小可追溯 Decision Context 进行 residual reasoning。

架构主线固定为：

```text
Image
→ Observation
→ Stable State
→ Event
→ Decision Context
→ Reasoning
→ Policy
```

其中：

- CNN 只生产 observation，不解释跨帧状态。
- Temporal State Engine 是唯一的状态演化与事件生产者。
- Semantic State Store 只保存 authoritative immutable snapshot，不做二次推理。
- Context Selector 只选择已有语义，不创造新的感知事实。
- Lightweight Policy Evaluator 优先覆盖 known/enumerable cases。
- Small LLM 只处理 deterministic policy 未覆盖的 residual/compositional/ambiguous cases。
- 所有 LLM 结果均为 derived inference，不得覆盖 authoritative perception state。

这种分工牺牲未建模视觉信息的开放问答能力，换取更低的计算与内存开销、单一状态所有权、可追溯的错误边界，以及非 LLM baseline 与 LLM 的公平比较能力。

## 1.2 优化后的总体架构

```text
Camera
  │
  ▼
Frame Router / Quality Gate
  │
  ▼
CNN Perception (10～30 FPS, profile-dependent)
  │ Observation
  ▼
Temporal State Engine
Observation_t + State_{t-1} → State_t + Events_t
  │ Stable State + Confirmed Event + Evidence Provenance
  ▼
Semantic State Store
(authoritative / immutable / versioned)
  │
  ├──────────────► Lightweight Policy Evaluator
  │                        │
  │                        ├── resolved
  │                        │      ↓
  │                        │   Policy Engine
  │                        │
  │                        └── unresolved / ambiguous
  │
  ▼
Context Selector
  │
  ▼
Decision Context
(minimal / complete / traceable / model-independent)
  │
  ▼
Event Scheduler / Value-of-Inference
  │
  ▼
Inference Governor
admit / queue / schedule / execute / cancel
deadline / memory / thermal / accelerator budget
  │
  ▼
Model Adapter
JSON / Protobuf → compact DSL / semantic tokens / key-value
  │
  ▼
Small LLM (100M～1B candidate)
  │
  ▼
Constrained Decoder
  │
  ▼
Schema + Evidence + Temporal Validator
  │
  ▼
Policy Engine / HMI / Cabin Applications
  │
  ▼
Interaction Memory
(derived data only; never overwrites perception facts)
```

### 1.2.1 决策路径不是并行竞争关系

Lightweight Policy Evaluator 与 LLM 不并列争夺最终决策权，而是形成 residual reasoning 关系：

```text
Known / enumerable case
→ deterministic handling
→ Policy Engine

Residual / compositional / ambiguous case
→ VoI gate
→ Small LLM
→ Validator
→ Policy Engine
```

如果轻量策略已经确定最终 action，即使场景语义仍存在不影响 action 的歧义，也不调用 LLM。LLM 的目标不是解释所有场景，而是补齐 deterministic policy 的剩余决策域。

### 1.2.2 分层接口、状态所有权与降级契约

| 层 | 输入 | 输出 | 状态所有者与修改权 | 回写规则 | 错误传播与降级 | 主要资源影响 |
|---|---|---|---|---|---|---|
| Frame Router / Quality Gate | Camera frame、采集元数据 | 可用帧、质量标记、任务调度信号 | 只拥有短生命周期帧队列；可丢帧，不修改感知状态 | 不回写下游状态 | 低质量或过期帧被丢弃/降频；质量标记向下游传播 | 图像带宽、预处理延迟、帧缓存 |
| CNN Perception | 可用帧 | 带 evidence ID 的 observation | 只拥有单帧/短批次推理状态；不能形成跨帧 stable state | 不回写 Store 或 Interaction Memory | 模型失败输出 unavailable/unsupported 能力标记；不伪造默认值 | 高频 compute、权重常驻、feature buffer |
| Temporal State Engine | `Observation_t`、`State_{t-1}` | `State_t`、`Events_t`、统计摘要 | 唯一 stable state 与 event lifecycle 所有者；只有它能推进状态 | 只向 Store 发布新版本 snapshot | 冲突保留为 conflict；数据不足为 unknown；能力缺失为 unsupported | 持续低延迟计算、窗口内存 |
| Semantic State Store | stable state、event、evidence | immutable snapshot、latest/history/evidence 查询 | 只拥有版本与生命周期元数据；不做 timeout、聚合或推理 | authoritative 区只接收 Temporal Engine 发布 | 写入失败保留上一完整版本；不生成半完成 snapshot | 状态复制、索引与历史窗口内存 |
| Lightweight Policy Evaluator | authoritative snapshot、策略配置 | resolved action 或 unresolved descriptor | 只拥有确定性规则配置和本次评估结果 | 不能修改 snapshot；resolved 结果提交 Policy Engine | 不匹配即 unresolved，不用猜测填补 | 低延迟、低内存，优先于 LLM |
| Context Selector / Decision Snapshot Builder | authoritative snapshot、可选 Interaction Memory、决策目标 | Decision Context | 只拥有本次决策快照；不得重新解释 stable state | 不回写 authoritative data | 缺必要字段时输出 context_incomplete；unsupported 不触发重采样 | 选择、裁剪、少量复制与序列化 |
| Event Scheduler / VoI | Decision Context、policy resolution、资源摘要 | inference request 或 skip reason | 只拥有触发/cooldown/去重状态 | 不修改感知或决策历史 | VoI 不足、action 已 resolved 或资源压力大时跳过 | 降低 invocation rate 的关键控制点 |
| Inference Governor | inference request、runtime telemetry | admitted/queued/running/cancelled/completed 状态 | 拥有 request lifecycle 与资源 admission | 不回写业务状态 | 超时、过期或被新 snapshot 淘汰时取消/拒绝 | 队列、模型加载、accelerator、memory、thermal |
| Model Adapter / Model | Decision Context | 模型输入与 derived inference | Adapter 拥有编码映射；模型不拥有系统状态 | 模型输出只能送 Validator | 编码不兼容或模型失败则拒绝/回退 baseline | token 数、prefill/decode、临时 buffer |
| Validator / Policy Engine | derived inference、request 元数据、当前 snapshot | validated decision、HMI/action、reject reason | Validator 拥有校验结果；Policy Engine 拥有最终 action | 只将结果写入 Interaction Memory | schema/evidence/temporal 失败即拒绝；保持、no_action 或 deterministic fallback | 低计算，决定 stale result 是否生效 |
| Interaction Memory | validated interpretation、policy/HMI outcome | 带来源的 derived history | 独立于 authoritative Store；只允许决策/交互链写入 | 可被 Context Selector 显式引用，不能反写 perception/event | 来源或 snapshot 不明则不进入下一轮 context | 有界历史存储与检索 |

该表同时定义错误归属：任何模块只能为自己的转换负责，不能在下游通过“补齐语义”掩盖上游缺失。

## 1.3 感知层：输出语义观测，不输出文本

CNN 层输出可计算、可追溯的 observation，不直接生成 prompt 文本，也不把高维 embedding 序列化成数字字符串交给 LLM。后者 token 成本高、数值关系难以由百 M 级模型稳定学习，也会让模型接口绑定 CNN 内部表示。

推荐 observation 至少包含：

- `occupant_id`、`seat_id`、`object_track_id` 及 track generation。
- 类别、属性、姿态、视线区域、物体与人-物关系候选。
- 原始置信分、质量分、遮挡状态、能力支持状态。
- `capture_time`、`processing_time`、source model 和 model version。
- 唯一 evidence ID 及父 evidence 引用。

```json
{
  "evidence_id": "obs_8044",
  "source_model": "gaze_v3",
  "model_version": "3.2.1",
  "capture_time_ms": 372500,
  "processing_time_ms": 372527,
  "subject": "p0",
  "value": "center_display",
  "quality": 0.91,
  "aggregation_level": "observation"
}
```

CNN 只声明它实际支持的能力。某字段未启用对应模型或 label space 不覆盖时，输出 `unsupported`，不能用 `unknown` 掩盖能力缺失。对于必须保留而难以人工离散化的信息，可由小型 projection head 生成有限 semantic code；该 code 仍作为 observation 进入 Temporal State Engine，不直接绕过状态层进入 LLM。

## 1.4 Temporal State Engine

Temporal State Engine 是唯一的状态演化与事件生产者，其正式契约为：

```text
Observation_t + State_{t-1}
    → State_t + Events_t
```

它负责：

- EMA、hysteresis、debounce、duration、进入/退出阈值和置信稳定化。
- occupant/seat/object track binding、generation 切换和关系生命周期。
- 时间窗口统计、状态摘要、持续时间、占比、趋势和最近变化时间。
- conflicting observations、unknown 与 unsupported 的显式处理。
- event forming、confirm/update/expire/retract 生命周期及 evidence 链建立。

Semantic State Store、Context Selector 和 Model Adapter 均不得再次执行这些逻辑。若模型需要“过去 3 秒占比”或“事件是否仍有效”，该结果必须先由 Temporal State Engine 形成，并作为 snapshot 字段发布。

### 1.4.1 三种非确定状态

| 状态 | 语义 | 是否可能通过继续观察恢复 | 调度含义 |
|---|---|---|---|
| `unknown` | 当前数据不足，例如遮挡导致 gaze 暂不可见 | 可能 | 可在能力存在且 VoI 足够时等待或请求更多 evidence |
| `conflict` | 多个观测、模型或时间窗口结论相互矛盾 | 可能，但需冲突消解 | 保留各候选和来源；是否推理取决于 conflict 是否影响 action |
| `unsupported` | 当前系统没有该感知能力或 label space 不覆盖 | 否 | 禁止因该字段反复采样或触发 LLM；只能降级策略或升级能力版本 |

```json
{
  "activity": {
    "status": "unsupported",
    "reason_code": "MODEL_CAPABILITY_NOT_DEPLOYED"
  }
}
```

### 1.4.2 多时间戳语义

OMS 是异步流水线，必须区分：

- `capture_time`：Camera 采集原始图像的时间。
- `processing_time`：当前模块实际处理该数据的时间。
- `state_time`：stable state 或 event 被判定成立的语义时间。
- `inference_start_time` / `inference_end_time`：模型执行时间。

```text
t_capture ≠ t_state ≠ t_inference
```

duration 从定义明确的 state transition 计算，不能用当前处理时间减去任意 observation 时间代替。跨模块延迟分析同时保留四类时间，不覆盖原始时间戳。

### 1.4.3 身份切换与事件生命周期

`occupant_id` 必须与 track generation 或等价 epoch 绑定。身份重建、座位迁移或 track recycle 时：

- 旧 generation 的状态停止演化并按规则 expire/retract。
- 新 generation 不继承旧 occupant 的 stable state。
- Interaction Memory 若需要复用，必须经过 seat/person 关联检查并显式标明 inherited source。
- 由旧 generation 形成且尚未执行的 inference request 进入 cancellation 流程。

| 层级 | 典型周期 | 内容 | 唯一生产者 |
|---|---:|---|---|
| Observation | 单帧或数帧 | CNN 原始结构化输出 | CNN Perception |
| Stable State | 数百毫秒到数秒 | 去抖后的人员、物体、姿态、关系及窗口摘要 | Temporal State Engine |
| Confirmed Event | 数百毫秒到数分钟 | 有生命周期和证据链的语义变化 | Temporal State Engine |

## 1.5 Semantic State Store

Semantic State Store 收敛为纯版本化存储层。它保存 Temporal State Engine 已经完成语义处理的结果，但不执行 timeout、事件聚合、状态推理、冲突消解或二次加工。

职责仅包括：

- immutable snapshot 的原子发布与读取。
- 单调 `snapshot_id`、schema version 和 producer version 管理。
- latest、按版本 history 和按时间范围查询。
- evidence index 与父子引用查询。
- snapshot retention、pin、expire 和回收等生命周期管理。

Store 的生命周期管理只决定“数据版本是否保留”，不决定“业务事件是否超时”。后者只属于 Temporal State Engine。

### 1.5.1 Authoritative 与 derived memory 隔离

原 Scene Memory 拆分为两个互不覆盖的数据域。

**Perception / Event Memory（authoritative data）**只保存 CNN observation、stable state、temporal summary、confirmed event、quality 和 evidence provenance。只有 CNN 与 Temporal State Engine 能产生该域的数据；LLM、Policy Engine 和 HMI 不得修改或反向写入。

**Interaction Memory（derived data）**只保存 previous LLM interpretation、HMI action、policy decision 和 user/system interaction outcome。

任何 Interaction Memory 再进入 Decision Context 时必须显式标识来源、关联 snapshot 和非事实属性：

```json
{
  "source": "previous_llm_decision",
  "snapshot_id": 1842,
  "confidence_level": "medium",
  "decision": "media_selection",
  "derived": true
}
```

禁止形成以下自增强反馈：

```text
LLM 推断
→ 进入下一轮 context
→ 被当成当前感知事实
→ LLM 进一步强化原推断
```

Context Selector 必须将 authoritative facts 与 derived history 放入不同 namespace；模型输出和 Validator 也不得把 derived evidence 引用为直接视觉证据。

### 1.5.2 Snapshot 与 evidence provenance

```json
{
  "schema_version": "oms_state.v2",
  "snapshot_id": 1842,
  "producer_state_version": 611,
  "state_time_ms": 372810,
  "processing_time_ms": 372824,
  "occupants": [
    {
      "occupant_id": "p0",
      "track_generation": 7,
      "seat": "front_left",
      "presence": {"status": "known", "value": "present"},
      "gaze": {
        "status": "known",
        "zone": "center_display",
        "duration_ms": 1600,
        "evidence_refs": ["state_gaze_203"]
      },
      "activity": {
        "status": "unsupported",
        "reason_code": "MODEL_CAPABILITY_NOT_DEPLOYED"
      }
    }
  ],
  "events": [
    {
      "event_id": "evt_71",
      "type": "display_attention_started",
      "lifecycle": "confirmed",
      "subject": "p0",
      "state_time_ms": 372700,
      "evidence_refs": ["state_gaze_203", "obs_8044"]
    }
  ],
  "evidence_index": {
    "obs_8044": {
      "source_model": "gaze_v3",
      "model_version": "3.2.1",
      "capture_time_ms": 372500,
      "processing_time_ms": 372527,
      "subject": "p0",
      "quality": 0.91,
      "aggregation_level": "observation"
    },
    "state_gaze_203": {
      "source_model": "temporal_state_engine",
      "model_version": "state_rules_1.4",
      "state_time_ms": 372700,
      "subject": "p0",
      "quality": 0.88,
      "aggregation_level": "stable_state",
      "parent_evidence_refs": ["obs_8031", "obs_8044"]
    }
  }
}
```

系统必须支持：

```text
Decision
→ Event
→ Stable State
→ Observation
→ Source Model + Model Version
```

的反向 trace。Error analysis 据此将问题定位到 CNN perception、temporal aggregation、semantic mapping、context selection、LLM reasoning 或 policy mapping，而不是统一归因于 LLM。

## 1.6 Event Scheduler：Value-of-Inference 驱动的事件与预算联合调度

Scheduler 的目标从“降低固定推理频率”升级为“降低无效 LLM invocation rate”。它不仅判断场景变化是否足够大，还判断本次推理是否可能改变最终策略。

```text
VoI ≈ decision_change_probability
    × decision_benefit
    - inference_cost
```

工程实现不要求估计真实概率。Lightweight Policy Evaluator 先返回：

```yaml
policy_resolution: resolved | unresolved | ambiguous
decision_relevance: none | low | medium | high
candidate_action: keep_ui | simplify_ui | show_suggestion | no_action | null
```

Scheduler 综合 event importance、semantic delta、ambiguity/conflict 是否影响 action、request urgency、decision relevance、inference cost、cooldown、deduplication 和 resource pressure。

### 1.6.1 触发条件

- Policy Evaluator 返回 unresolved/ambiguous，且 decision relevance 为 medium/high。
- 多个 confirmed event 形成可能改变 action 的组合场景。
- conflict 位于决策关键字段，且模型能基于其他 evidence 缩小策略歧义。
- 上层应用提出具有 deadline 的场景决策请求。
- Interaction Memory 与当前 authoritative state 出现需要重新决策的显著差异。

### 1.6.2 抑制条件

- deterministic policy 已 resolved 最终 action。
- 场景有语义歧义，但不同解释映射到同一 action。
- decision relevance 为 none/low。
- 缺失字段为 unsupported，继续观察或调用 LLM 不会增加 evidence。
- 与最近有效 Decision Context 的语义差异低于阈值。
- 同类 request 处于 cooldown，且没有更高优先级事件。
- Context 不完整、输入质量不足或推理只能放大不确定性。
- 预计完成时间超过 `valid_until` 或资源成本超过当前预算。

```text
priority = event_importance
         + semantic_delta
         + request_urgency
         + decision_relevance
         - inference_cost
         - cooldown_penalty
         - resource_pressure
```

该式用于离散排序，不在缺少实测数据时固化伪精确权重。Scheduler 只创建或抑制 inference request，不拥有模型执行队列；request lifecycle 交给 Inference Governor。

## 1.7 Decision Context 与软件/模型协议

原 `Prompt & Snapshot Builder` 拆分为：

```text
Context Selector
+ Decision Snapshot Builder
+ Model Adapter
```

避免 Semantic State Store、prompt JSON 与具体 LLM 实现直接绑定。

### 1.7.1 Decision Context

Decision Context 定义为：

> 某一次场景决策所需的最小、完整、可追溯语义集合。

它独立于具体模型、prompt 格式和运行位置，同一份 Decision Context 可以供 deterministic Rule Engine、GBDT、Tiny Transformer、Small LLM、replay evaluator 和 future cloud fallback 使用。

Context Selector 只做按任务选择、裁剪和 namespace 隔离，不重新计算 duration、聚合 event 或解释状态。Decision Snapshot Builder 将选中字段冻结为一次决策使用的 immutable context，并附带：

```text
decision_context_id
snapshot_id
context_schema_version
state_time
created_time
valid_until
max_state_age_ms
authoritative_facts
derived_interaction_history
evidence_refs
allowed_scenes
allowed_actions
```

```json
{
  "schema_version": "oms_decision_context.v1",
  "decision_context_id": "ctx_208",
  "request_id": "req_208",
  "snapshot_id": 1842,
  "task": "scene_understanding_and_policy",
  "state_time_ms": 372810,
  "created_time_ms": 372850,
  "valid_until_ms": 373250,
  "max_state_age_ms": 500,
  "authoritative": {
    "occupant_count": 2,
    "p0": {
      "track_generation": 7,
      "gaze": {"status": "known", "value": "center_display", "duration_ms": 1600},
      "posture": {"status": "known", "value": "lean_forward", "duration_ms": 900},
      "activity": {"status": "unsupported"}
    },
    "events": [
      {"event_id": "evt_71", "type": "display_attention_started", "evidence_refs": ["state_gaze_203"]}
    ]
  },
  "derived_history": [
    {
      "source": "previous_llm_decision",
      "snapshot_id": 1835,
      "confidence_level": "medium",
      "decision": "media_selection",
      "derived": true
    }
  ],
  "allowed_scenes": ["media_selection", "navigation_input", "conversation", "unknown"],
  "allowed_actions": ["keep_ui", "simplify_ui", "show_suggestion", "request_more_evidence", "no_action"]
}
```

### 1.7.2 JSON 软件协议与模型内部表示解耦

```text
JSON / Protobuf = system interface

compact DSL / discrete semantic tokens / token IDs
= model interface
```

Model Adapter 可将外部软件协议：

```json
{"gaze": "center_display", "duration_ms": 1600}
```

编码为：

```text
<GZ_CD><DUR_1_2S>
```

也可以使用 compact key-value 表示。该路径必须保持可逆映射、schema version、unknown/conflict/unsupported 区分和 evidence 关联。是否启用由真实 token 数、端侧延迟、准确率、可调试性和 adapter 维护成本共同决定。

### 1.7.3 输出协议与置信表达

初期不允许模型生成看似精确但未经校准的概率。百 M 级模型输出 `0.78` 不等于 78% correctness。优先使用离散、可验证字段：

```json
{
  "schema_version": "oms_model_output.v2",
  "request_id": "req_208",
  "snapshot_id": 1842,
  "scene": "media_selection",
  "action": "keep_ui",
  "confidence_level": "medium",
  "decision_margin": "low",
  "needs_more_evidence": true,
  "evidence_refs": ["evt_71"],
  "reason_code": "GAZE_POSTURE_CONTEXT_MATCH"
}
```

若量产需要概率置信度，应使用独立验证集进行 temperature scaling、isotonic regression 等 calibration，并通过 reliability diagram、ECE、Brier Score 验证；校准器版本必须进入 decision provenance。

Constrained Decoder 负责语法空间，Validator 负责 schema、枚举、数值范围、request/snapshot 对应、evidence 完整性、authoritative/derived namespace、互斥字段、动作白名单和时间有效性。Post-training 重点放在语义正确性、拒答、证据一致性和 residual domain，而不是 JSON 标点。

## 1.8 小型 LLM 的任务边界与模型选择

Small LLM 定义为：

> deterministic policy 无法覆盖的 residual reasoning engine。

它处理组合关系、有限上下文依赖和影响 action 的歧义，但不承担稳定化、事件生产、事实补全、资源调度或最终动作执行。

100M～1B 不是能力同质区间，应按相同 Decision Context 分级验证：

- 约 100M：有限 residual scene 分类、证据选择、动作排序和结构化输出。
- 数百 M：短时上下文、多事件组合和有限歧义处理。
- 接近 1B：资源允许时验证更复杂的多乘员关系、较长上下文和未见组合泛化。

如果 residual task 能被 GBDT、Tiny Transformer 或新增 deterministic policy 稳定覆盖，就不应为了使用 LLM 而扩大 LLM 职责。

### 1.8.1 长期演进机制

```text
高频重复的 LLM pattern
→ 收集 Decision Context + validated outcome
→ 离线分析与规则/分类器候选生成
→ 独立回放、边界和回归验证
→ 下沉为 deterministic policy
→ LLM residual domain 缩小
```

下沉不能由线上 LLM 自动完成。新增 policy 必须有明确适用范围、冲突优先级、回滚版本和与 LLM baseline 的对照证据。

### 1.8.2 Post-training 路径

1. 基于 Decision Context schema 合成覆盖组合、unknown、conflict、unsupported、低质量和过期输入的训练样本。
2. 使用更强教师模型或人工规则生成候选解释，再由人工抽检修正。
3. SFT 学习 OMS ontology、residual boundary、证据约束、拒答和动作白名单。
4. 加入 hard negative：相似状态不同 action、不同解释相同 action、derived history 与 authoritative fact 冲突。
5. 加入非法 evidence、越权动作、伪造感知事实和 stale request 的拒绝样本。
6. 量化后重新评估，不把浮点模型效果直接视为端侧结果。

## 1.9 8775 端侧资源调度原则

当前没有 SA8775P 目标板实测，因此本节只定义 admission control、观测指标和待验证机制，不预设 NPU/GPU/DSP 映射、共驻能力、峰值内存或功耗结论。

Inference Governor 的完整生命周期为：

```text
Admission
→ Queueing
→ Scheduling
→ Execution
→ Cancellation / Completion
```

每个 request 至少维护：

```json
{
  "request_id": "req_208",
  "decision_context_id": "ctx_208",
  "snapshot_id": 1842,
  "priority": "high",
  "deadline_ms": 373200,
  "valid_until_ms": 373250,
  "estimated_cost": "medium",
  "cancel_token": "cancel_req_208"
}
```

Admission 检查 request 是否仍绑定适用 snapshot、预计 queue/load/inference 时间是否满足 deadline、峰值内存是否可接受、accelerator/memory bandwidth/thermal/energy budget 是否允许，以及是否存在可合并、可去重或更高优先级 request。

### 1.9.1 Request cancellation

新 snapshot 使旧 Decision Context 失效时，应尽可能在排队或执行早期主动取消：

```text
snapshot A
→ request A queued/running

scene changes to snapshot B
→ request A no longer useful
→ signal cancel_token(A)
→ reclaim queue slot / runtime resources
```

取消条件包括 occupant generation 改变、关键 event retract、candidate action 已被 deterministic policy resolved、`valid_until` 到期或更高优先级 request 替代。若底层 runtime 无法中断正在执行的算子，至少停止后续 decode，并将结果标记为 cancelled；Validator 仍保留最终 stale check。

### 1.9.2 数据复制与共驻策略

- CNN 高频运行，LLM 低频触发；是否同时常驻由峰值内存和热稳定性实测决定。
- 使用 immutable Decision Context，CNN 可继续处理新帧，LLM 不持有可变 State Store 引用。
- 尽量引用 snapshot/evidence index，避免在 Store、Context 和 Adapter 间复制完整历史。
- 若不能共驻，比较权重分段加载、共享 workspace、冷/热驻留和模型切换成本。
- 对模型输入设置硬 token/byte 上限，优先保留 action-relevant event、conflict 和新变化。
- 分别记录 admission、queue、load、prefill、decode、validation 和 cancellation latency。

## 1.10 降级与故障边界

### 1.10.1 Temporal Validator 与 stale result

LLM request 必须携带 `snapshot_id`、`valid_until` 和 `max_state_age_ms`。Validator 在动作生效前重新读取当前时间和适用 snapshot：

```text
if now > request.valid_until:
    discard(STALE_DEADLINE)

if now - snapshot.state_time > request.max_state_age_ms:
    discard(STALE_STATE)

if occupant_generation_changed(snapshot, latest_snapshot):
    discard(STALE_IDENTITY)

if decision_relevant_state_changed(snapshot, latest_snapshot):
    discard(STALE_CONTEXT)
```

正确但过期的推理结果仍然是不可执行结果。`inference_start_time`、`inference_end_time` 和 validation time 必须进入 decision provenance。

### 1.10.2 故障与降级矩阵

| 场景 | 处理方式 |
|---|---|
| CNN 能力未部署 | 输出 `unsupported`；走不依赖该字段的 policy，不重复请求 evidence |
| 临时遮挡或质量差 | 输出 `unknown`；仅在可恢复且 VoI 足够时等待/请求更多 evidence |
| 多源观测矛盾 | 输出 `conflict` 并保留来源；若不影响 action 则 deterministic resolved |
| Temporal Engine 更新失败 | 不发布新 snapshot；保留上一原子版本并上报 producer error |
| Store 发布失败 | latest 指针不前移，禁止暴露半完成版本 |
| Context 不完整 | 不创建 LLM request，或显式输出 `context_incomplete` |
| 资源不足/热压力高 | Admission 拒绝；使用 deterministic fallback 或 `no_action` |
| request 被新状态淘汰 | 优先 cancel；不能中断时停止 decode，并由 Validator 丢弃 |
| LLM 超时或模型未加载 | 标记 timeout/unavailable，不作用于当前 snapshot |
| 模型输出非法 | Constrained Decoder 优先；Validator 仍失败则拒绝 |
| evidence 不存在或 namespace 越权 | 判为 ungrounded inference 并拒绝 |
| 结果 stale | 拒绝执行，不写为当前 decision；可保留诊断记录 |
| schema/model adapter 不兼容 | 走显式兼容 adapter 或拒绝，不静默字段降级 |
| Interaction Memory 来源不明 | 不进入 Decision Context |

降级顺序原则为：保持 authoritative state 完整性优先，其次 deterministic policy，再次 `no_action`/保持现状；不得为了得到 LLM 输出而放宽 evidence、时间或身份校验。

## 1.11 Demo 分阶段计划

### 1.11.1 阶段 A：任务、状态所有权与协议基线

- 定义 10～20 个高价值 OMS 场景、允许 action、residual boundary 和拒绝边界。
- 固化 Observation、Stable State/Event、Semantic Snapshot、Decision Context、Model Output 五类 schema。
- 明确 authoritative/derived namespace、unknown/conflict/unsupported 和多时间戳语义。
- 用录制或合成状态流建立 deterministic rule baseline。

### 1.11.2 阶段 B：离线 residual reasoning 可行性

- 基于同一 Decision Context 比较 GBDT、Tiny Transformer 和 100M～1B Small LLM。
- 评估场景/action 效果、evidence 一致性、拒答、stale/unsupported 处理和置信校准需求。
- 验证 JSON、compact key-value、DSL/semantic token 在 token 数、延迟和准确率上的差异。
- 建立高频 LLM pattern 的 deterministic policy 下沉候选流程，但不自动上线规则。

### 1.11.3 阶段 C：板端链路与 admission control

- 接入 CNN、Temporal State Engine、State Store、Policy Evaluator、Context Selector 和 Scheduler。
- 实现 admit/queue/schedule/execute/cancel 生命周期及 deadline/validity 校验。
- 测量 CNN 单独、候选模型单独、分时、共驻候选和 cancellation 收益。
- 依据峰值内存、energy、thermal 和持续运行稳定性选择量化及部署配置。

### 1.11.4 阶段 D：闭环与可追溯验证

- 接入 Validator、Policy Engine、HMI 和严格隔离的 Interaction Memory。
- 回放多人、遮挡、身份切换、track recycle、低光、快速变化和稳定长场景。
- 验证 Decision → Event → Stable State → Observation → Source Model 反向 trace。
- 注入超时、非法输出、版本不兼容、过期 snapshot、资源抢占和 cancellation 失败。

### 1.11.5 阶段 E：系统性 ablation

所有模型使用同一 Decision Context 数据集、相同 train/validation/test split 和 action contract。

**Model baseline：**

```text
Baseline 0: deterministic rule
Baseline 1: GBDT / traditional classifier
Baseline 2: Tiny Transformer encoder
Candidate:  Small LLM
```

**Context ablation：**

```text
A0: current stable state only
A1: current state + temporal summary
A2: current state + events
A3: current state + events + interaction memory
```

Interaction Memory 始终保留 derived 标识，A3 不允许把历史推断转成 authoritative feature。除总体指标外，还应按 known、unknown、conflict、unsupported、identity switch 和 stale request 分桶报告，防止平均指标掩盖边界退化。

Demo 的目标不是只证明“LLM 能工作”，而是证明它相对最佳非 LLM baseline 提供了可量化的新增能力。

## 1.12 验收指标

指标同时覆盖语义效果、状态一致性、调度效率、可追溯性和端侧代价。

### 1.12.1 状态与证据

- Observation → Stable State → Event 的 p50/p95 延迟。
- 抖动率、错误 track binding、identity generation 泄漏率。
- unknown/conflict/unsupported 分类准确率及错误恢复行为。
- Decision evidence 完整率和端到端反向 trace 成功率。
- authoritative/derived namespace 污染事件数，目标应为 0。

### 1.12.2 调度与异步执行

- Lightweight Policy resolved rate。
- LLM invocation rate、有效 invocation rate 和无效调用原因分布。
- VoI skip 后 action 不变率，以及错误 skip 导致的决策损失。
- admission reject、queue timeout、pre-execution cancel、mid-execution cancel 和 stale discard 比例。
- 取消操作节省的 decode time、energy 和队列等待。

### 1.12.3 模型与策略

- scene/action macro-F1、关键场景 recall 和 unknown/conflict rejection accuracy。
- evidence grounding、白名单动作合规和 unsupported 误请求率。
- 离散 confidence level 与实际正确率的可靠性；若启用概率校准，则报告 reliability diagram、ECE、Brier Score。
- deterministic、GBDT、Tiny Transformer、Small LLM 在统一 Decision Context 上的对照结果。

### 1.12.4 系统资源

- CNN FPS 降幅。
- admission、queue、load、prefill、decode、validation 的 p50/p95 延迟。
- 峰值内存、平均/峰值能耗、单次 inference energy、持续运行温升和降频情况。
- JSON 与可选 compact representation 的 token/byte 数、adapter 成本和总延迟。

### 1.12.5 LLM Incremental Utility

```text
ΔU = Metric_LLM - Metric_best_non_LLM
```

效果增益与资源代价并列报告，不强制合成为单一 scalar。例如：

```text
+3.2% scene macro-F1
+11% unknown / conflict rejection accuracy
+120 ms p95 latency
+380 MB peak memory
+X mJ per invocation
```

最终判断是：LLM 带来的效果提升是否足以覆盖 latency、memory、energy、thermal 和验证复杂度。上述数字仅展示报告形式，不代表 SA8775P 实测或项目目标值。

具体阈值需在场景集、候选模型和板端测量方案确定后填写，当前不作未经验证的承诺。

## 1.13 当前待决策项

1. Demo 首批 OMS 场景、action ontology、deterministic/residual 边界和策略冲突优先级。
2. CNN 输出采用多头统一模型还是多个轻量模型分频运行，以及各能力的 unsupported 声明方式。
3. Temporal State Engine 的窗口长度、event lifecycle、identity generation 和 conflict resolution 规则。
4. Semantic State Store 的 snapshot retention、evidence index、pin/reclaim 与零拷贝/少拷贝实现。
5. Decision Context 的任务 schema、最小完整性规则、authoritative/derived namespace 和 validity window。
6. VoI 离散规则、decision relevance 标注、inference cost 估计与 invocation budget。
7. LLM、Tiny Transformer、GBDT 候选及统一 replay/evaluation harness。
8. JSON/Protobuf 与 compact DSL/semantic token 的取舍和 Model Adapter 版本策略。
9. CNN 与候选推理模型共驻、分时、动态加载和 cancellation 的板端最优策略。
10. HMI/Policy Engine 对 stale、low-margin、conflict、unsupported 和 cancelled request 的最终处理约定。
11. 量产阶段置信校准、policy 下沉验证、版本回滚和 provenance 保留周期。
