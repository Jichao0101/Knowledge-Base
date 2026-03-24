# 1 OpenMMLab 整体架构概览

OpenMMLab 不是一个“单一框架”，而是一套**模块化深度学习基础设施**，可以理解为三层结构：

```
┌──────────────────────────────┐
│   下游任务框架（Task Layer）  │
│   mmdetection / mmseg / ...  │
└──────────────▲───────────────┘
               │
┌──────────────┴───────────────┐
│   训练与工程引擎（Engine）    │
│           mmengine           │
└──────────────▲───────────────┘
               │
┌──────────────┴───────────────┐
│  视觉基础库 + 高性能算子层    │
│            mmcv              │
└──────────────────────────────┘

```

一句话总结：

> **mmengine 负责“怎么训练”，mmcv 负责“怎么算得快”，mmdetection 负责“算什么任务”。**

---

# 2 mmengine

## 2.1 mmengine 的定位

**mmengine 是 OpenMMLab 的统一训练与工程框架**，它解决的不是“检测/分割算法”，而是：

- 训练流程如何组织
    
- 模型/数据/优化器如何解耦
    
- 分布式、日志、checkpoint 如何统一管理
    

可以把 mmengine 理解为 **OpenMMLab 版的 PyTorch Lightning + 配置系统 + Registry**。

---

**核心职责：**

- 训练 / 验证 / 测试循环（Runner / Loop）
    
- Hook 机制（日志、评估、checkpoint、EMA 等）
    
- Config 系统（支持 Python 配置）
    
- Registry（模块注册与自动构建）
    
- Optimizer / Scheduler 封装
    
- 分布式训练（DDP / FSDP / ZeRO）
    
- 权重加载、保存、resume
    

**不负责：**

- 具体视觉算子
    
- ROI Align / NMS 等高性能计算
    
- 检测、分割、分类算法本身
    

---

## 2.2 Python 版本兼容性

- mmengine **几乎是纯 Python**
    
- 对 Python 版本非常友好（3.8 / 3.9 / 3.10 / 3.11 通常都能跑）
    
- 很少成为环境问题的根源
    

---

# 3 mmcv：视觉基础库 + C++ / CUDA 加速算子

## 3.1 mmcv 的双重身份

mmcv 实际上是 **两种东西的组合**：

### 3.1.1 A. 纯 Python 视觉工具库

- 数据 pipeline 组件
    
- 图像处理 / 几何操作
    
- 通用工具函数
    
- 结构体（Boxes / Masks 等）
    

👉 **这部分不依赖编译**

---

### 3.1.2 B. C++ / CUDA 扩展算子

- `roi_align`
    
- `nms`
    
- `deform_conv`
    
- `sync_bn`
    
- 各种 ops
    

👉 这些最终以 **`mmcv._ext` 二进制模块** 的形式存在

---

## 3.2 为什么 mmcv 对环境极其敏感？

因为 **mmcv 的 ops 是编译产物**，必须同时匹配：

- Python 版本（cp38 / cp39 / cp310 / cp311）
    
- PyTorch 版本（2.0 / 2.1 / 2.5…）
    
- CUDA 版本（cu118 / cu121 / cu124）
    
- 系统 ABI（manylinux / glibc）
    

只要有一个不匹配，就会出现经典错误：

`ModuleNotFoundError: No module named 'mmcv._ext'`


---

# 4 mmdetection：目标检测任务框架

## 4.1 mmdetection 的定位

**mmdetection 是“检测算法库”**，它本身不关心：

- 训练流程怎么写
    
- ops 是怎么实现的
    

它假设：

- 训练由 mmengine 管
    
- 底层算子由 mmcv 提供
    

---

## 4.2 mmdetection 负责什么？

- 检测模型（Faster R-CNN / YOLO / DETR / …）
    
- Head / Neck / Backbone 组合
    
- Dataset 定义（COCO / VOC / 自定义）
    
- Loss / BBox / Mask 逻辑
    
- 评估指标（mAP 等）
    

---
