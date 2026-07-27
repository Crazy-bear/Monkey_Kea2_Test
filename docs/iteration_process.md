# 项目迭代过程文档

## 项目概述

本项目是为【A1力量镜】应用量身定制的 Monkey 自动化测试方案，用于测试应用的稳定性和可靠性。项目周期为 2025年1月10日 至 2026年3月12日。

---

## 迭代阶段

### 第一阶段：项目初始化（2025年1月10日 - 2025年2月10日）

- 确定项目目标和范围
- 搭建基础项目结构（settings / core / pages / tests）
- 配置开发环境（Python 3.7+、ADB、uiautomator2）
- 实现基本的 Monkey 事件注入功能

### 第二阶段：核心功能开发（2025年2月11日 - 2025年4月30日）

- 实现 `ADBClient`：封装 ADB 命令，`shell=False` 保证跨平台安全
- 开发 `MonkeyRunner`：Monkey 事件执行、实时日志轮转、UI 元素深度优先解析
- 实现 `LogcatHandler`：Logcat 捕获（多 buffer）、8 类崩溃检测与分类分析
- 开发 `ReportGenerator`：HTML/JSON 报告，内联 SVG + Canvas 双图表方案
- 实现 Page Object 模式：`BasePage` / `LoginPage` / `MainPage` / `SettingsPage`
- 完善 `Config`：三级配置（环境变量 > 配置文件 > 默认值），懒加载设备版本信息

### 第三阶段：性能监控集成（2025年5月1日 - 2025年7月31日）

- 开发 `CPUMonitor`：三级降级策略（`top -p` → `top` 全量 → `/proc/stat` 双采样）
- 开发 `MemoryMonitor`：`dumpsys meminfo` 解析 TOTAL PSS / Java Heap / Native Heap / Graphics
- 开发 `FPSMonitor`：`dumpsys gfxinfo` 四种解析策略，兼容不同 ROM
- 开发 `PerformanceMonitor`：后台线程采集、CSV/JSON 输出、阈值告警

### 第四阶段：测试验证与优化（2025年8月1日 - 2025年12月31日）

- 执行大规模 Monkey 测试，覆盖主要功能场景
- 分析崩溃日志，定位并推动修复稳定性问题
- 优化 Monkey 事件分布（touch 40% / motion 60% / syskeys 0%）
- 实现内存泄漏检测：滑动窗口 + 线性回归（斜率 + R²），定位泄漏分项
- 添加性能统计摘要（min / max / avg / p95）
- 完善单元测试，支持无设备 CI 校验

### 第五阶段：最终完善与部署（2026年1月1日 - 2026年3月12日）

- 优化 `logging_config.py`：新增 `RotatingFileHandler`，DEBUG 级别写入文件
- 优化 `ADBClient`：所有命令增加 `timeout` 参数，防止命令挂死
- 优化 `PerformanceMonitor._save_data`：新增 `_build_summary()` 输出统计摘要 JSON
- 修复 `requirements.txt` merge conflict，补充 `matplotlib`、`numpy`、`pytest` 依赖
- 修复 `README.md` 多处 git merge conflict，重写为当前实际状态
- 完善 `docs/` 文档，与代码实现保持同步

---

## 关键里程碑

| 时间 | 里程碑 |
|------|--------|
| 2025年2月10日 | 完成项目初始化，实现基本 Monkey 测试功能 |
| 2025年4月30日 | 完成核心功能开发（ADB、Monkey、Logcat、报告、Page Object） |
| 2025年7月31日 | 完成性能监控集成（CPU / 内存 / FPS） |
| 2025年12月31日 | 完成测试验证与优化（内存泄漏检测、性能摘要、单元测试） |
| 2026年3月12日 | 完成最终完善与部署，交付完整自动化测试方案 |
| 2026年7月 | **Kea2 融合**：双引擎编排、场景化属性脚本、统一报告门禁、Jenkins 扩展 |

---

## 第六阶段：Kea2 融合（2026年7月）

- 接入 Kea2：`orchestrator/`、`scenarios/`、`configs/`（唯一 Kea2 配置目录）
- `main.py` 支持 `--engine kea2|monkey`，默认 Kea2
- 性能监控 P0：补偿采样间隔、FPS 降频、phase 标签、泄漏 growth 阈值
- 报告扩展：Kea2 摘要、`gate_status`、分场景性能表
- Jenkins 后置脚本：门禁与飞书字段扩展

---

## 技术演进

### 架构设计

| 阶段 | 架构 |
|------|------|
| 初始 | 单脚本，硬编码配置 |
| 当前 | 分层模块化：settings / core / performance / pages / orchestrator / scenarios / tests |

### 配置管理

| 阶段 | 方式 |
|------|------|
| 初始 | 硬编码 |
| 当前 | 环境变量 > `config.ini` > 默认值，支持 CLI 参数覆盖，`validate()` 校验 |

### 日志系统

| 阶段 | 方式 |
|------|------|
| 初始 | 仅控制台输出 |
| 当前 | 控制台（INFO+）+ 滚动文件（DEBUG+，10MB × 5备份），`LogRotator` 支持 Monkey/Logcat 日志轮转 |

### 报告系统

| 阶段 | 方式 |
|------|------|
| 初始 | 纯文本日志 |
| 当前 | HTML（内联 SVG + Canvas 交互图表）+ JSON，支持阈值线、超标标注、泄漏区间高亮 |

### 性能监控

| 阶段 | 能力 |
|------|------|
| 初始 | 无 |
| 当前 | CPU / 内存（含分项）/ FPS 后台线程采集，滑动窗口 + 线性回归内存泄漏检测，min/max/avg/p95 统计摘要 |

---

## 项目成果

1. 完整的 Monkey 自动化测试流程，支持 CI/CD 集成
2. 实时性能监控系统，支持内存泄漏自动检测与定位
3. 详细的 HTML/JSON 测试报告，含交互式性能趋势图
4. 8 类崩溃自动检测与分类分析
5. 无设备单元测试，支持 Jenkins 流水线配置校验

---

## 未来规划

1. 多设备并行测试支持
2. 崩溃后自动重启应用，继续执行剩余事件
3. 性能基线对比（与历史测试结果比较，自动判断劣化）
4. AI 辅助崩溃分析（结合 LLM 解读 stack trace）
5. 可视化仪表盘（历史趋势、多版本对比）
6. 云端设备支持（接入云测平台）
