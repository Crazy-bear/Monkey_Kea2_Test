# 【A1力量镜】稳定性自动化测试（Kea2 + Monkey）

为【A1力量镜】（`com.aeke.fitnessmirror`）定制的 Android 稳定性测试方案。以 **Kea2（Fastbot 随机探索 + 属性测试）** 为主引擎，保留 **Monkey** 冒烟路径；测试期间并行采集 CPU / 内存 / FPS、Logcat 崩溃分析，并输出统一 HTML/JSON 报告，支持 Jenkins 门禁与飞书通知。

> **Python 3.8+**（Kea2 要求） · **ADB** · 已开启 USB 调试的 Android 设备

---

## 项目背景

力量镜为长时运行的健身镜应用，需在真实设备上验证：

- 长时间随机操作下的崩溃、ANR、内存泄漏
- 核心业务路径（随心练、课程、个人中心等）在属性脚本下的可达性与不变量
- 性能是否超出阈值（CPU、内存、FPS）

**测试前提**：设备已 **预登录并停留在主页**，场景脚本从主页出发，不覆盖登录流程。

| 场景模块 | 脚本 | 别名 |
|----------|------|------|
| Home 首页 | `test_home.py` | `home`（`main`/`navigation` 为兼容别名） |
| Lifestyle 娱乐 | `test_lifestyle.py` | `lifestyle`（`media`/`guide` 为兼容别名） |
| 随心练 | `test_suixinlian.py` | `suixinlian` |
| 精品课程 | `test_course.py` | `course` |
| 运动测评 | `test_assessment.py` | `assessment` |
| AI Coach | `test_ai_coach.py` | `ai_coach`, `aicoach` |
| 运动计划 | `test_programs.py` | `programs`, `plan` |
| 个人中心 | `test_profile_plan.py` | `profile` |
| 日历 / 日程 | `test_schedule.py` | `schedule`, `calendar` |
| 控制面板 | `test_control_panel.py` | `control_panel`, `control` |
| 数据中心 | `test_data_center.py` | `data_center`, `datacenter`, `effort` |
| 悬浮 Touch | `test_floating_touch.py` | `floating_touch`, `touch`, `touch_menu` |
| 设置 | `test_settings.py` | `settings` |

Page 定位依据 `S1Pro_UI/v3.0.0.6858/` 下的 UI dump；`--scenarios all` 运行上表全部模块。

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
├── scenarios/              # Kea2 属性脚本
├── pages/                  # Page Object（home_page / lifestyle_page 等）
├── core/                   # ADB、Logcat、报告、Monkey
├── performance/            # 性能监控
├── templates/              # 可选 HTML 报告模板
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

首次运行若缺少 `configs/`，会自动执行 `kea2 init`。力量镜黑名单请维护 **`configs/widget.block.py`**（屏蔽 Sleep 等系统栏按钮）和 **`configs/abl.strings`**。

### 5. Monkey 冒烟（可选）

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
| `--scenarios` | `all` | 场景别名或 `test_*.py`，逗号分隔 |
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
| `report.html` / `report.json` | 统一报告（崩溃、性能、Kea2 属性违规、门禁状态） |
| `kea2/` | Kea2 原始结果、Fastbot 日志 |
| `performance/` | CSV / JSON 性能时序与摘要 |
| `logcat.log` | 测试期间 Logcat |
| `kea2_run_meta.json` | 运行元数据 |

框架日志滚动写入 `outputs/logs/monkey_test.log`。

### 门禁（gate_status）

报告 JSON 中的 `gate_status` 综合判断：崩溃数、Kea2 属性违规、性能超阈等。CI 可根据 `passed` 字段决定构建成败，参见 [`Jenkinsfile.example`](Jenkinsfile.example)。

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
