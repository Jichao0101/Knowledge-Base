---
type: current_maintenance_record
status: verified
topic: Tracking current 文档组按新目录规范 hardening/refactor
lifecycle_classification: hardening_refactor
updated_at: 2026-05-13
---

# 1 Source Inventory

现有 current 文件：

- `02_Projects/DMS/04_Tracking/tracking_overview_current.md`
- `02_Projects/DMS/04_Tracking/tracking_design_current.md`
- `02_Projects/DMS/04_Tracking/tracking_spec_current.md`
- `02_Projects/DMS/04_Tracking/tracking_implementation_current.md`
- `02_Projects/DMS/04_Tracking/tracking_validation_current.md`

根目录保留的稳定入口和方案文档：

- `02_Projects/DMS/04_Tracking/座舱乘员多目标跟踪方案.md`
- `02_Projects/DMS/04_Tracking/座舱多目标跟踪实现.md`
- `02_Projects/DMS/04_Tracking/head-first渐进跟踪方案.md`
- `02_Projects/DMS/04_Tracking/head-first渐进跟踪实现.md`

本轮关联支撑记录：

- `02_Projects/DMS/04_Tracking/Current Maintenance Records/tracking_interfaces_evidence.md`
- `02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪实现闭环记录-2026-03-24.md`
- `02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪设计失配修复闭环记录-2026-03-25.md`
- `02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪生命周期与手部关联设计失配修复闭环记录-2026-03-25.md`
- `02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪功能审核记录-2026-03-27.md`
- `02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪设计失配修复未闭环记录-2026-03-27.md`
- `02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪手部连续性优化闭环记录-2026-03-31.md`
- `02_Projects/DMS/04_Tracking/Current Maintenance Records/DMS主驾打哈欠误报修复闭环记录-2026-04-05.md`
- `02_Projects/DMS/04_Tracking/Current Maintenance Records/后排乘客头部误跟踪为副驾驶修复闭环记录-2026-04-05.md`
- `02_Projects/DMS/04_Tracking/Current Maintenance Records/多目标跟踪快速运动恢复阶段预测更新一致性修复闭环记录-2026-04-05.md`
- `02_Projects/DMS/04_Tracking/Current Maintenance Records/跟踪框越界导致板端coredump调查与修复闭环记录-2026-04-07.md`
- `02_Projects/DMS/04_Tracking/Current Maintenance Records/2m摄像头后排head误绑定主驾修复闭环记录-2026-05-08.md`
- `02_Projects/DMS/04_Tracking/Current Maintenance Records/head-first优先于body-first跟踪主线决策记录-2026-05-09.md`

# 2 Action Taken

- 将 current 维护支撑记录从 Tracking 主题根目录移动到 `Current Maintenance Records/`。
- 保留 active current 文件和稳定方案文档在主题根目录。
- 更新 current 文档、baseline/head-first 文档、records 与 subpower receipt 中的旧路径引用。
- 将 `tracking_overview_current.md` 中原单次恢复完全闭环声明调整为 `recoverability_status: partial`，避免在仍有验证缺口时保留完全可恢复声明。

# 3 Superseded Or Retained Sources

保留在根目录：

- active current 文档组。
- baseline 方案/实现文档。
- head-first 方案/实现文档。

移动到 records：

- 代码评估、修复闭环、审核、决策、接口 evidence 等支撑材料。

# 4 Recoverability Result

结果：`partial`

原因：

- current 组仍可作为默认恢复入口。
- 目录布局已按新规范收敛，支撑记录不再与 active current 并列。
- Tracking current 仍明确存在运行时 replay、区域级唯一性、ID 连续性和 head-first 落地验证缺口，因此不声明单次恢复完全闭环。

# 5 Evidence Gaps

- 未新增代码验证或板端验证。
- 未重新审查 Tracking 代码事实，只做 current 文档组布局和引用 hardening。
- subpower run artifact 内部引用已做路径更新，但未重新生成历史 artifact。
