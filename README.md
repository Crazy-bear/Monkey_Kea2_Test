# 【S1Pro 力量镜】稳定性自动化测试（Kea2 + Monkey）

为【S1Pro 力量镜】（`com.aeke.fitnessmirror`）定制的 Android 稳定性测试方案。以 **Kea2（Fastbot 随机探索 + 属性测试）** 为主引擎，保留 **Monkey** 冒烟路径；测试期间并行采集 CPU / 内存 / FPS、Logcat 崩溃分析，并输出统一 HTML/JSON 报告，支持 Jenkins 门禁与飞书通知。

> **Python 3.8+**（Kea2 要求） · **ADB** · 已开启 USB 调试的 Android 设备

---

## 项目背景

【S1Pro 力量镜】为长时运行的健身镜应用，需在真实设备上验证：

- 长时间 **Fastbot 随机操作**下的崩溃、ANR、内存泄漏
- 掉登录/屏保后的自动恢复，以及按模块锁时把探索拉回目标模块（属性**围栏**）
- 性能是否超出阈值（CPU、内存、FPS）

属性脚本定位为 **围栏 + 极简哨兵**（非完整 UI 路径回归）；业务路径正确性请用独立 UI 自动化。规避 Sleep/登录区/悬浮球等靠 `configs/widget.block.py`。

**测试前提**：设备已 **预登录并停留在主页**，场景脚本从主页出发。若运行中进入屏保或登录页，基类会自动点屏退出并以 **Admin** 成员恢复主页；登录页不做 Fastbot 随机探索。

### 活跃属性脚本（`scenarios/test_*.py`，`--scenarios all` 会加载）

| 场景模块 | 脚本 | 别名 | 哨兵 |
|----------|------|------|------|
| Home 首页 | `test_home.py` | `home`（`main`/`navigation`） | 主表面 + 随心练入口 |
| Lifestyle 娱乐 | `test_lifestyle.py` | `lifestyle`（`media`/`guide`） | 功能列表 + 任一入口 |
| 随心练 | `test_suixinlian.py` | `suixinlian` | 快捷入口可见 |
| 精品课程 | `test_course.py` | `course` | 列表/筛选可见 |
| 运动测评 | `test_assessment.py` | `assessment` | 宫格可见 |
| AI Coach | `test_ai_coach.py` | `ai_coach`, `aicoach` | Start Workout 可见 |
| 运动计划 | `test_programs.py` | `programs`, `plan` | 列表/筛选可见 |

基类围栏（所有活跃脚本继承）：`test_recover_session`、`test_pull_to_locked_module`（见 `scenarios/base_property.py`）。

### 已归档（导航深链路，见 `scenarios/archive/`）

设置 / 控制面板 / 数据中心 / 日程 / 个人中心 / 悬浮 Touch 的旧属性脚本已移出 discover。  
仍可用别名做 **模块锁白名单**（如 `--scenarios settings`），属性仅加载占位 `lock_fence.py`（围栏、无抽检）。

---

## 架构概览

```
main.py
  ├─ engine=kea2（默认）
  │    ├─ orchestrator/kea2_runner   → Kea2 CLI + Fastbot
  │    ├─ scenarios/                 → 属性测试脚本（复用 pages/）
  │    └─ configs/                   → Fastbot 黑白名单（Kea2 固定目录名）
  ├─ engine=monkey                   → core/monkey_runner 冒烟
  └─ 并行（两种引擎共用）
       ├─ performance/monitor       → CPU / 内存 / FPS
       ├─ core/logcat_handler        → 崩溃检测
       └─ core/report_generator      → report.html / report.json + 门禁
```

**两个「配置」目录，职责不同：**

| 目录 | 用途 | 典型修改 |
|------|------|----------|
| `settings/` | 框架运行参数（Python 代码） | 设备 ID、时长、性能阈值 |
| `configs/` | Kea2/Fastbot 探索策略 | `widget.block.py`、`abl.strings` |

详见 [`settings/README.md`](settings/README.md)、[`configs/README.md`](configs/README.md)。

---

## 目录结构

```
├── main.py                 # 主入口
├── settings/               # 框架配置（config.py、logging）
├── configs/                # Kea2/Fastbot 配置（自动 kea2 init）
├── orchestrator/           # 测试编排（Kea2 运行、报告组装）
├── scenarios/              # Kea2 属性脚本（围栏+哨兵；archive/ 为已停用导航类）
├── pages/                  # Page Object（home_page / lifestyle_page 等）
├── core/                   # ADB、Logcat、报告、Monkey
├── performance/            # 性能监控
├── templates/              # 可选 HTML 报告模板
├── S1Pro_UI/               # 各版本 UI dump 与元素清单（定位基线）
├── tests/                  # 单元测试（pytest，无需设备）
├── docs/                   # 迭代记录、问题解决方案
├── outputs/                # 测试产出（gitignore）
└── Jenkinsfile.example     # CI 门禁 + 飞书通知示例
```

---

## 技术栈

- **Kea2 / Fastbot** — 场景化随机探索与属性测试
- **Android Monkey** — 轻量冒烟
- **Python 3.8+** · **uiautomator2** · **ADB**
- **Page Object** — 场景脚本与 UI 定位解耦
- **Jinja2** — HTML 报告（可自定义 `templates/report_template.html`）
- **pytest** — 单元测试与 CI 校验

---

## 快速开始

### 1. 环境准备

- 安装 [ADB](https://developer.android.com/tools/adb)，设备可通过 `adb devices` 识别
- Python 3.8+ 虚拟环境（推荐）

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 校验配置（无需设备）

```bash
python main.py --validate-only --engine kea2
pytest tests/ -v
```

### 4. 运行 Kea2 稳定性测试（默认引擎）

```bash
python main.py --engine kea2 \
  --device 192.168.20.81:5555 \
  --package com.aeke.fitnessmirror \
  --running-minutes 60 \
  --scenarios all \
  --output outputs
```

首次运行若缺少 `configs/`，会自动执行 `kea2 init`。【S1Pro 力量镜】黑名单请维护 **`configs/widget.block.py`**（屏蔽 Sleep 等系统栏按钮）和 **`configs/abl.strings`**。

**按模块锁探索**（仅 Kea2；Monkey 不受影响）：`--scenarios` 指定单/多模块时，Fastbot 使用 Activity **白名单**（写入 `configs/awl.strings`），与全量时的 **黑名单**互斥；属性脚本中的 `test_pull_to_locked_module` 会把探索拉回目标模块。`--scenarios all` 仍为全应用探索 + 登录/屏保 Activity 黑名单；活跃属性仅为围栏 + 上表低频哨兵。

```bash
# 单模块 / 多模块
python main.py --engine kea2 --scenarios course --running-minutes 10
python main.py --engine kea2 --scenarios course,suixinlian --running-minutes 20
```

> **限制**：Home 与 Lifestyle 共用 `MainActivity`，白名单无法在组件层拆开；未选 `lifestyle` 时由 `widget.block.py` 按 `KEA2_LOCK_MODULES` 屏蔽 Lifestyle Tab，并结合引导脚本拉回。

跑完后终端会打印探索摘要；统一报告「探索覆盖」区块与 `report.json` → `kea2.exploration` 列出已测 Activity 与已识别的一二级业务页（共享 Activity 依赖低频锚点采样）。锁模块时还会给出 **模块内停留占比**（`in_module_sample_ratio`，默认 ≥0.6 视为 `dwell_ok`）。

### 5. Monkey 冒烟（可选）

Monkey 路径、事件配比与崩溃忽略策略保持原样，不随 Kea2 模块锁变化：

```bash
python main.py --engine monkey \
  --device <DEVICE_ID> \
  --package com.aeke.fitnessmirror \
  --events 5000 \
  --output outputs
```

### 6. 从已有产出补生成报告

```bash
python main.py --report-only outputs/2026-07-23_16-27-53 --format html
```

---

## 命令行参数

| 参数 | 默认 | 说明 |
|------|------|------|
| `--engine` | `kea2` | `kea2` 或 `monkey` |
| `--device` | 见 settings | 设备 ID（`adb devices`） |
| `--package` | `com.aeke.fitnessmirror` | 应用包名 |
| `--running-minutes` | 60 | Kea2 运行时长（分钟） |
| `--scenarios` | `all` | 场景别名或 `test_*.py`，逗号分隔；Kea2 下非 `all` 时启用模块锁白名单 |
| `--events` | 100 | Monkey 事件数（仅 monkey 引擎） |
| `--output` | `outputs` | 产出根目录 |
| `--format` | `html` | 报告格式：`html` / `json` |
| `--profile` | `DEFAULT` | `config.ini` 中的 profile |
| `--baseline` | — | 性能基线 JSON，用于回归对比 |
| `--validate-only` | — | 仅校验配置，不连设备 |
| `--report-only DIR` | — | 从已有目录生成报告 |
| `--report-output FILE` | — | 配合 `--report-only` 指定输出路径 |

---

## 配置说明

**优先级**：命令行参数 > 环境变量 > 项目根 `config.ini` > `settings/config.py` 默认值。

### 常用环境变量

| 变量 | 说明 |
|------|------|
| `TEST_ENGINE` | `kea2` / `monkey` |
| `MONKEY_DEVICE_ID` | 设备 ID |
| `MONKEY_PACKAGE_NAME` | 包名 |
| `KEA2_RUNNING_MINUTES` | Kea2 时长 |
| `KEA2_SCENARIOS` | 场景别名或 `all` |
| `KEA2_OUTPUT_DIR` | 产出根目录 |
| `KEA2_THROTTLE` | Fastbot 操作间隔（ms） |
| `PERF_CPU_THRESHOLD` | CPU 告警阈值（%） |
| `PERF_MEM_THRESHOLD` | 内存告警阈值（MB） |
| `PERF_FPS_THRESHOLD` | FPS 告警阈值 |

完整列表见 [`settings/config.py`](settings/config.py)。

### config.ini（可选）

在项目根创建 `config.ini`，按 profile 覆盖设备与参数：

```ini
[DEFAULT]
DEVICE_ID = 192.168.20.81:5555
PACKAGE_NAME = com.aeke.fitnessmirror
KEA2_RUNNING_MINUTES = 120
TEST_ENGINE = kea2
SCENARIOS = main
OUTPUT_DIR = outputs
```

配置好后可简化为：`python main.py`（参数仍可通过命令行覆盖）。

---

## 测试产出

每次运行在 `outputs/<timestamp>/` 下生成：

| 路径 | 内容 |
|------|------|
| `report.html` / `report.json` | 统一报告（崩溃、性能、Kea2 属性违规、探索覆盖、门禁状态） |
| `kea2/` | Kea2 原始结果、Fastbot 日志 |
| `coverage_pages.json` | 业务页低频采样结果（Kea2） |
| `performance/` | CSV / JSON 性能时序与摘要 |
| `logcat.log` | 测试期间 Logcat |
| `kea2_run_meta.json` | 运行元数据（含 `lock_modules`） |

框架日志滚动写入 `outputs/logs/monkey_test.log`。

### 门禁（gate_status）

分层门禁（稳定性专业口径）：

| level | `passed` | 含义 | CI 建议 |
|-------|----------|------|---------|
| `pass` | true | 无硬失败、无告警 | 绿 |
| `warn` | true | 属性哨兵 / 疑似泄漏 / 路径性能等 | 绿但飞书标黄 |
| `fail` | false | Crash/ANR 或 Kea2 exit 2/3/4 | 红，拦截 |

字段：`gate_status.level`、`reasons_hard`、`reasons_soft`（`reasons` 为二者合并，兼容旧消费方）。

**Kea2 原生 `bug_report.html`**：仅作互补（Activity/Widget/Property/Crash），**不能替代**统一报告（无 CPU·Mem·FPS 路径分析、无分层门禁、无业务页 dwell）。报告内提供链接与可选 iframe 预览。

### 平台契约：`report.json` 关键字段

下游（Jenkins / 飞书 / 质量平台）建议只依赖下列稳定字段；未列出的键可能随版本增减。

| 路径 | 类型 | 说明 |
|------|------|------|
| `gate_status.passed` | bool | 硬失败是否通过（warn 时仍为 true） |
| `gate_status.level` | string | `pass` / `warn` / `fail` |
| `gate_status.reasons_hard` | string[] | 硬失败原因 |
| `gate_status.reasons_soft` | string[] | 告警原因 |
| `gate_status.reasons` | string[] | hard+soft 合并（兼容） |
| `executive_verdict` | object | 首屏三句话：stability / main_risk / next_step |
| `test_engine` | string | `kea2` / `monkey` |
| `lock_modules` | string[] \| null | 本次模块锁；`all` 时为 null |
| `kea2.exit_code` | int | Kea2 进程退出码：0 成功 / 1 属性违反 / 2 Crash·ANR / 3 两者兼有 / 4 运行时错误 |
| `kea2.exit_code_label` | str | 报告展示用，如 `1（属性违反）` |
| `kea2.property_violation_count` | int | 属性违反数 |
| `kea2.bug_report_info` | object | 原生报告是否存在、有无截图、能力说明 |
| `kea2.lock_modules` | string[] \| null | 与顶层 `lock_modules` 对齐 |
| `kea2.exploration.tested_activities_count` | int | 已测 Activity 数 |
| `kea2.exploration.coverage_percent` | number \| null | Activity 覆盖率 |
| `kea2.exploration.business_pages_seen` | string[] | 已识别业务页 |
| `kea2.exploration.business_pages_missed` | string[] | 建模但未命中的业务页 |
| `kea2.exploration.page_hits` | object | 业务页采样次数 |
| `kea2.exploration.in_module_sample_ratio` | number \| null | 锁模块时：模块内采样占比（0~1）；未锁为 null |
| `kea2.exploration.in_module_sample_percent` | number \| null | 同上百分比展示 |
| `kea2.exploration.dwell_ok` | bool \| null | 是否 ≥ `dwell_threshold`（默认 0.6） |
| `kea2.exploration.dwell_threshold` | number | 停留达标门槛 |
| `path_performance` | array | 按业务路径聚合的性能与风险 |
| `path_investigations` | array | 可执行排查指引 |
| `crash_count` | int | 崩溃数 |
| `duration` | string | 可读时长 |
| `seed_value` | number/str | Fastbot 真实探索 seed（从 `fastbot_*.log` 的 `Monkey: seed=` 解析并写入 meta；非 Monkey 的 `MONKEY_SEED`） |

> `in_module_sample_ratio` 优先用 `coverage_pages.json` 的逐条 `samples`；无明细时用 `page_hits` 近似。多模块锁为 **并集**（任一锁模块内的采样都算「内」）。

---

## Jenkins / CI 建议

```bash
# 流水线前置：无设备节点
pip install -r requirements.txt
python main.py --validate-only --engine kea2
pytest tests/ -v

# 有设备节点
python main.py --engine kea2 \
  --device $DEVICE_ID \
  --package com.aeke.fitnessmirror \
  --running-minutes $RUNNING_MINUTES \
  --scenarios "${SCENARIOS:-all}" \
  --output outputs
```

后置脚本解析 `report.json`、推送飞书通知的示例见 `Jenkinsfile.example`。

---

## 常见问题

| 现象 | 处理 |
|------|------|
| `UnboundLocalError: current` / 秒退 | `--act-blacklist-file` 必须带设备路径 `/sdcard/.kea2/abl.strings`，不能只写 flag |
| `AdbError: FAIL`（push 黑名单） | 勿传 Windows 本地路径给 `--act-blacklist-file` |
| `No module named 'scenarios'` | 使用最新代码（自动 `PYTHONPATH=项目根`） |
| `PermissionError` … `__pycache__` | 最新代码会在 `configs/` 预建 `__pycache__` |
| 秒停、无 `res_*` 产出 | 查看 `outputs/<dir>/kea2_subprocess.log` 完整 Kea2 日志 |
| 镜子黑屏 / 睡眠 | 检查 `configs/widget.block.py` 是否屏蔽 Sleep |
| ADB / pidof 报错 | 可调大 `PERF_MONITOR_INTERVAL` 降低 ADB 争抢 |

更多排查见 [`docs/issues_solutions.md`](docs/issues_solutions.md)。

---

## 相关文档

- [`docs/iteration_process.md`](docs/iteration_process.md) — 迭代与架构演进
- [`docs/issues_solutions.md`](docs/issues_solutions.md) — 问题与解决方案
- [`settings/README.md`](settings/README.md) — 框架配置说明
- [`configs/README.md`](configs/README.md) — Fastbot 配置说明

---

## 许可证

MIT License
