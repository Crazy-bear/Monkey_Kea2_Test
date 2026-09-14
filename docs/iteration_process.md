# 项目迭代过程文档

## 项目概述

本项目是为【S1Pro 力量镜】应用量身定制的稳定性自动化测试方案，以 Kea2（Fastbot 随机探索 + 属性测试）为主引擎，保留 Monkey 冒烟路径。项目自 2025年1月10日 启动，2026年3月12日 交付首个完整方案，此后持续迭代。

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
| 2026年9月 | **模块锁与可判定报告**：白名单探索、覆盖采样、分层门禁与首屏结论 |

---

## 第六阶段：Kea2 融合（2026年7月）

- 接入 Kea2：`orchestrator/`、`scenarios/`、`configs/`（唯一 Kea2 配置目录）
- `main.py` 支持 `--engine kea2|monkey`，默认 Kea2
- 性能监控 P0：补偿采样间隔、FPS 降频、phase 标签、泄漏 growth 阈值
- 报告扩展：Kea2 摘要、`gate_status`、分场景性能表
- Jenkins 后置脚本：门禁与飞书字段扩展

---

## 第七阶段：模块锁与可判定报告（2026年8月 - 2026年9月）

Kea2 融合后暴露两个问题：全应用随机探索无法按模块定向加压；报告只有「过 / 不过」，测试人员拿不到下一步动作。本阶段围绕**探索可控**与**结论可判定**展开。

### 探索范围可控

- `orchestrator/module_catalog.py` 维护模块 → Activity / 业务页映射
- 非 `all` 场景改用 Activity 白名单 `configs/awl.strings`，与全量时的黑名单互斥
- `orchestrator/module_bootstrap.py` 开跑前把设备引导进模块根页
- `configs/widget.block.py` 按 `KEA2_LOCK_MODULES` 屏蔽跨模块 Tab
- Home 与 Lifestyle 共用 `MainActivity`，白名单无法在组件层拆开，靠控件屏蔽 + 属性围栏拉回

### 属性脚本重新定位

- 从「UI 路径回归」收敛为「围栏 + 极简哨兵」，路径正确性交给独立 UI 自动化
- 基类提供两条围栏：`test_recover_session`（掉登录/屏保自动恢复）、`test_pull_to_locked_module`
- 新增 `pages/login_page.py`、`pages/screensaver_page.py` 支撑会话恢复
- 6 个导航深链路脚本移入 `scenarios/archive/`，别名仍可做模块锁白名单，属性加载占位 `lock_fence.py`

### 探索覆盖可见

- `orchestrator/coverage_sampler.py` 旁路采样当前页，产出 `coverage_pages.json`
- 报告列出已测 Activity、已识别与未命中的业务页
- 锁模块时输出模块内停留占比 `in_module_sample_ratio` 与 `dwell_ok`
- 从 `fastbot_*.log` 解析真实探索 seed，不再用 `MONKEY_SEED` 顶替

### 测试结论可判定

- `gate_status` 拆为 `level`（pass / warn / fail）+ `reasons_hard` / `reasons_soft`，仅 Crash·ANR 与 Kea2 exit 2/3/4 硬拦发布
- 新增 `executive_verdict`：稳定性、主风险、下一步三句话，直接给出复跑命令
- `orchestrator/perf_context.py` 按业务路径聚合 CPU / 内存 / FPS，输出 `path_performance` 与排查指引
- 修复门禁把 Kea2 日志里的 Traceback 当作失败原因

### 工程质量

- UI 基线更新到 v3.1.0.7123（34 个页面 dump + 元素清单）
- 单测扩到 137 例，覆盖新增的编排模块
- `tests/conftest.py` 打桩设备版本探测，StaticChecker 用例绕开 `u2.connect`，无设备环境 3 秒跑完

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
| Kea2 融合 | HTML（内联 SVG + Canvas 交互图表）+ JSON，支持阈值线、超标标注、泄漏区间高亮 |
| 当前 | 加分层门禁（pass / warn / fail）、首屏三句话结论、探索覆盖与业务路径性能，`report.json` 对下游稳定字段化 |

### 探索策略

| 阶段 | 方式 |
|------|------|
| Monkey 期 | 全应用随机事件，无范围控制 |
| Kea2 融合 | 全应用 Fastbot 探索 + 场景属性脚本 |
| 当前 | `all` 走黑名单全量；指定模块走 Activity 白名单 + 控件屏蔽 + 属性围栏拉回 |

### 性能监控

| 阶段 | 能力 |
|------|------|
| 初始 | 无 |
| 当前 | CPU / 内存（含分项）/ FPS 后台线程采集，滑动窗口 + 线性回归内存泄漏检测，min/max/avg/p95 统计摘要 |

---

## 项目成果

1. Kea2 + Monkey 双引擎稳定性测试流程，支持 CI/CD 集成
2. 按模块锁定探索范围，配合属性围栏做定向加压
3. 实时性能监控系统，支持内存泄漏自动检测与按业务路径定位
4. HTML/JSON 报告含分层门禁、首屏结论、探索覆盖与性能趋势
5. 8 类崩溃自动检测与分类分析
6. 137 例无设备单元测试，支持 Jenkins 流水线配置校验

---

## 待办

### 近期

1. FPS 采集校准：实跑均值 3.87 / 14.59 明显偏低，需确认 `dumpsys gfxinfo` 在该 ROM 上的解析分支
2. `--report-only` 彻底离线化：回放历史产出时仍会连设备取版本，污染旧报告
3. UI 基线升级到 3.2.0.7215，统一 `pages/` 与 `tests/` 的引用路径
4. Lifestyle 入口哨兵改 resource-id 定位，判断 `Games` 是真缺陷还是文案定位问题
5. 覆盖率策略：单次全量探索 Activity 覆盖仅 5%，改为 nightly 跑模块锁矩阵

### 中长期

1. 多语言（i18n）适配自动检测（方案见 `docs/i18n_automation_plan.md`）
2. 多设备并行测试支持
3. 崩溃后自动重启应用，继续执行剩余事件
4. AI 辅助崩溃分析（结合 LLM 解读 stack trace）
5. 可视化仪表盘（历史趋势、多版本对比）
6. 云端设备支持（接入云测平台）
