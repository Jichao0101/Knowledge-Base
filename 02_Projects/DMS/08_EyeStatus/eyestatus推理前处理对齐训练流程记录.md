# 1 eyestatus推理前处理对齐训练流程记录

- 状态：closed_with_compile_success
- 日期：2026-05-01
- 归属：DMS / EyeStatus Deployment
- 来源：本次 subpower 处理记录、`/home/jichao/dms` 代码修改、`eyestatus_gpu:/workspace` 训练仓预处理检查、`bash scripts/compile_j6b.sh` 编译输出
- 适用范围：dms 仓库中 `EyeStatusModel` 的推理前处理与训练侧 Stage D ROI 输入协议对齐
- 不适用范围：通用 VP resize 规范、板端运行结论、模型精度结论

## 1.1 背景

目标是将 dms 仓库中睁闭眼模型 `eyestatus` 的推理前处理对齐模型训练过程。

训练仓检查到的正式输入链路为：

- Stage D 导出 ROI：`SquareCrop + OOB Const Padding`
- 方形 ROI 以眼框中心为中心，`side = max(bbox_w, bbox_h) * square_k`
- 当前默认 `square_k = 1.0`
- 超出图像边界的区域按对应边补常数 `114`
- 训练入口再将 ROI `Resize((128, 128))`
- 训练文档明确不再将 `reflect` / `replicate padding` 作为正式训练输入协议

dms 当前可用输入来自 68 点 landmarks，训练仓没有定义 68 点到眼框的转换规则。因此本次沿用 dms 已有的左右眼 6 点集合生成 per-eye bbox，只替换后续 ROI 构造、padding 和 resize 方式。

## 1.2 修改内容

修改文件：

- `/home/jichao/dms/source/models/eye_status_model.cpp`
- `/home/jichao/dms/include/models/eye_status_model.h`

关键变化：

- 移除旧的 `resizeKeepRatioLongSide` 加 `reflectPadToSquare` 路径。
- 由 6 个眼部 landmark 计算 tight bbox。
- 按 `side = max(width, height)` 构造训练侧默认 `square_k=1.0` 的方形 ROI。
- 对越界区域先在方形 Y ROI 画布上按边补常数 `114`。
- 对 RGB 输入先转 Y，以适配 `UtilsDomain::VpRoiResize_Y` 的 Y-only 输入要求。
- 使用 `UtilsDomain::AdjustRoiForEvenPadding` 调整 VP ROI，满足上下 padding 偶数约束。
- 使用 `UtilsDomain::VpRoiResize_Y` 将方形 ROI resize 到 `128x128`。
- `PostProcess` 和标签映射保持不变。

## 1.3 评审与返工

初始评审指出的主要风险：

- Y-only VP resize 会使 RGB 本地测试输入直接失败。
- 直接对 clipped ROI 做 VP letterbox 会改变越界 padding 的方向语义。
- VP 内存部分初始化失败时可能泄漏。

返工处理：

- `CV_8UC3` 输入先转 `CV_8UC1`。
- 先构造完整方形 ROI 画布并按边补 `114`，再 VP resize，避免越界 padding 被居中到错误方向。
- VP resize 改为调用 `J6bVpProcessor::VpRoiResize_Y` 接口，由 processor 层通过 `VpMemBase` / `VpMem_Y` 管理算子内存；模型代码不再直接调用 `hbUCPMallocCached` / `hbDSPAddrMap` / `hbUCPFree`。

## 1.4 验证结果

验证命令：

```bash
bash scripts/compile_j6b.sh
```

结果：

- CMake/make 阶段完成到 `[100%] Built target sdk`。
- 脚本最终返回 1 的原因是后续传板阶段 `192.168.2.10` SSH/SCP 连接断开。
- 用户确认当前未联通板端，编译成功即可视为成功。
- `git diff --check` 通过。

## 1.5 风险与边界

- 训练证据侧 ROI 是 RGB 图片并经过 ImageNet normalize；本次运行时按用户要求使用 `VpRoiResize_Y`，因此 Y-only 输入仍是部署模型契约假设，未在板端验证。
- 板端验证未执行，原因是当前板端不可达。
- 训练仓只定义 per-eye bbox 之后的 Stage D 规则，没有定义 68 点 landmarks 到眼框 bbox 的转换规则。
- `expand_percent` / `vertical_boost` 配置仍会读取，但本次对齐训练侧默认 `square_k=1.0`，未继续用于 ROI 扩张。

## 1.6 后续建议

- 板端恢复后，补跑 eyestatus 样例并记录输入 crop dump 与分类输出。
- 如部署模型确认为 RGB/ImageNet normalize 输入，需要重新评估是否应使用 RGB/NV12 路径而非 Y-only `VpRoiResize_Y`。
- 若训练侧后续调整 `square_k`，dms 侧应同步配置化该参数。
