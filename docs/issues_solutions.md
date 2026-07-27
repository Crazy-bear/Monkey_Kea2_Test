# 项目问题和解决方案文档

## 项目概述

本文档记录【A1力量镜】Monkey 自动化测试项目开发过程中遇到的实际问题及解决方案，供后续维护和类似项目参考。

---

## 一、设备连接问题

### 问题1：ADB 设备连接不稳定

**症状**：设备经常断开，ADB 命令执行失败。

**原因**：USB 线质量差、USB 调试模式不稳定、ADB 服务异常。

**解决方案**：
1. 使用高质量 USB 线或改用 TCP 连接（`adb connect <ip>:5555`）
2. 重启 ADB 服务：`adb kill-server && adb start-server`
3. `ADBClient.run_command` 增加 `timeout` 参数，防止命令挂死

**当前实现**（`core/adb_client.py`）：
```python
def run_command(self, cmd, monkey_log_file=None, capture_output=False, timeout=30):
    try:
        result = subprocess.run(cmd, shell=False, ..., timeout=timeout)
        ...
    except subprocess.TimeoutExpired:
        logger.error(f"ADB 命令超时（{timeout}s）: {' '.join(cmd)}")
        return "", f"TimeoutExpired after {timeout}s"
```

---

### 问题2：设备 ID 获取失败

**症状**：无法获取设备 ID，测试无法执行。

**原因**：设备未连接、ADB 服务未运行、驱动未安装。

**解决方案**：
1. `adb devices` 确认设备状态
2. `Config` 提供默认设备 ID，支持环境变量 `MONKEY_DEVICE_ID` 覆盖
3. `ADBClient.get_connected_devices()` 解析 `adb devices` 输出，过滤 `\tdevice` 行（排除 `offline`）

**当前实现**（`core/adb_client.py`）：
```python
def get_connected_devices(self):
    stdout, _ = self.run_command(["adb", "devices"], capture_output=True, timeout=10)
    return [
        line.split()[0]
        for line in stdout.splitlines()
        if "\tdevice" in line
    ]
```

---

## 二、测试执行问题

### 问题1：Monkey 测试过程中应用崩溃导致测试中断

**症状**：Monkey 执行中途因崩溃退出，未完成全部事件。

**原因**：应用稳定性问题，或设备资源不足。

**解决方案**：
- Monkey 命令加 `--ignore-crashes --ignore-timeouts --monitor-native-crashes`，让 Monkey 在崩溃后继续执行
- `LogcatHandler.start_real_time_crash_detection` 提供实时崩溃回调，可在回调中重启应用

**当前实现**（`core/monkey_runner.py`）：
```python
cmd = [
    "adb", "-s", self.config.DEVICE_ID, "shell", "monkey",
    ...
    "--ignore-crashes", "--ignore-timeouts", "--monitor-native-crashes",
    ...
]
```

---

### 问题2：Monkey 日志文件过大

**症状**：长时间测试产生数 GB 日志，磁盘占满。

**原因**：`-v -v -v` 详细模式输出量大。

**解决方案**：`LogRotator` 按文件大小（默认 10MB）+ 时间间隔（默认 10 分钟）自动轮转，旧文件加时间戳保留。

**当前实现**（`core/utils.py`）：
```python
class LogRotator:
    def write(self, data):
        self.file.write(data)
        self.file.flush()
        current_time = time.time()
        if current_time - self.last_rotate_time >= self.rotate_interval_seconds:
            self.file.seek(0, os.SEEK_END)
            if self.file.tell() > self.max_size:
                self._rotate()
                self.last_rotate_time = current_time
```

---

### 问题3：Monkey 命令执行超时挂死

**症状**：`subprocess.run` 无限等待，进程无法退出。

**原因**：`run_command` 原来没有 timeout 参数。

**解决方案**：`ADBClient.run_command` 新增 `timeout` 参数（默认 30s），Monkey 长跑命令传 `timeout=None`，`MonkeyRunner` 使用 `subprocess.Popen` + `proc.wait(timeout=300)` 控制超时。

---

## 三、性能监控问题

### 问题1：CPU 使用率监控不准确

**症状**：CPU 数据波动大，或在某些 ROM 上始终为 0。

**原因**：不同 Android ROM 的 `top` 输出格式差异大，列顺序不固定。

**解决方案**：三级降级策略：
1. `top -n 1 -p <pid>`，解析第 9 列（index 8）
2. `top -n 1` 全量输出，按包名/PID 匹配
3. `/proc/<pid>/stat` 双采样差值计算

**当前实现**（`performance/cpu.py`）：`CPUMonitor.get_cpu_usage()` 依次尝试三种方法，任一成功即返回。

---

### 问题2：内存监控数据异常

**症状**：内存数据与实际不符，或分项数据缺失。

**原因**：`dumpsys meminfo` 在不同 Android 版本格式不同（App Summary 区块 vs 详细表格）。

**解决方案**：每个分项（TOTAL PSS / Java Heap / Native Heap / Graphics）各提供主选 + 次选两种正则，优先匹配 App Summary 格式（Android 6+），兜底匹配详细表格格式。

**当前实现**（`performance/memory.py`）：
```python
# TOTAL PSS 主选（App Summary）
m = re.search(r'TOTAL PSS:\s+([\d,]+)', output)
if not m:
    # 次选（详细表格）
    m = re.search(r'^\s+TOTAL\s+([\d,]+)', output, re.MULTILINE)
```

---

### 问题3：FPS 监控返回 0

**症状**：FPS 数据始终为 0 或无法获取。

**原因**：`dumpsys gfxinfo` 输出格式因 ROM 和渲染模式不同差异较大。

**解决方案**：四种解析策略依次尝试：
1. `Total frames rendered` + `50th percentile` 帧时间
2. `Summary` 区块 `Average frame time`
3. `FrameTiming` 区块第一帧时间
4. `Total frames rendered` + `Total time` 计算平均 FPS

**排查步骤**：
- 开发者选项 → GPU 渲染模式分析 → 在屏幕上显示为条形图（确认 GPU 渲染已开启）
- 确认应用处于前台活跃状态
- 手动执行 `adb shell dumpsys gfxinfo <package>` 确认输出内容

---

### 问题4：内存泄漏误报

**症状**：短时间内存波动被误判为泄漏。

**原因**：仅用增长量判断，无法区分正常波动和真实泄漏。

**解决方案**：滑动窗口 + 线性回归双重判断：
- 斜率 > `PERF_MEM_LEAK_RATE`（默认 5 MB/min）
- R² > `PERF_MEM_LEAK_R2_MIN`（默认 0.6，确保线性相关性）
- 同时分析 Java Heap / Native Heap / Graphics 分项增长，定位泄漏类型

**当前实现**（`performance/monitor.py`）：`_analyze_memory_leak()` 方法。

---

### 问题5：性能数据缺少统计摘要

**症状**：只有原始采样数据，无法快速了解整体性能状况。

**原因**：原 `_save_data` 只保存原始 CSV/JSON，没有聚合统计。

**解决方案**：新增 `_build_summary()` 方法，计算 min/max/avg/p95，并额外保存 `performance_summary_<ts>.json`。

**当前实现**（`performance/monitor.py`）：
```python
def _build_summary(self):
    def stats(key):
        vals = sorted(v for d in self.data if (v := float(d.get(key) or 0)) > 0)
        if not vals:
            return {"min": 0, "max": 0, "avg": 0, "p95": 0}
        p95_idx = max(0, int(len(vals) * 0.95) - 1)
        return {"min": ..., "max": ..., "avg": ..., "p95": vals[p95_idx]}
    return {
        "sample_count": len(self.data),
        "cpu": stats("cpu"),
        "mem": stats("mem"),
        "fps": stats("fps"),
        "exceed_cpu_count": ...,
        "exceed_mem_count": ...,
        "fps_low_count": ...,
        "memory_leak": self.leak_analysis,
    }
```

---

## 四、报告生成问题

### 问题1：报告模板文件不存在

**症状**：`templates/report_template.html` 不存在时报错。

**解决方案**：`ReportGenerator.generate_html_report` 先检查模板文件是否存在，不存在则自动使用 `_get_default_template()` 内置模板，保证报告始终可生成。

---

### 问题2：性能图表在 Jenkins 环境下不显示

**症状**：Jenkins CSP 策略禁止 `data:` URI，base64 PNG 图片无法显示。

**解决方案**：优先生成内联 SVG（`_build_performance_chart_svg`），SVG 直接嵌入 HTML 不受 CSP 限制；matplotlib PNG base64 作为备选。

---

### 问题3：性能数据量大时报告加载慢

**症状**：采样点超过数千条时，HTML 报告 Canvas 图表渲染卡顿。

**解决方案**：报告模板中 JavaScript 自动降采样，超过 200 点时按步长抽样，保证渲染流畅。

```javascript
if (raw.length > 200) {
    var step = Math.ceil(raw.length / 200);
    raw = raw.filter(function(_, i) { return i % step === 0; });
}
```

---

## 五、配置管理问题

### 问题1：requirements.txt 存在 git merge conflict

**症状**：`pip install -r requirements.txt` 报语法错误。

**解决方案**：解决 merge conflict，补充缺失依赖：

```
uiautomator2==2.16.0
Jinja2==3.1.2
matplotlib>=3.5.0
numpy>=1.21.0
pytest>=7.0.0
```

---

### 问题2：日志只输出到控制台，无文件记录

**症状**：测试结束后无法回溯 DEBUG 级别日志。

**解决方案**：`logging_config.py` 新增 `RotatingFileHandler`，DEBUG 及以上写入 `outputs/logs/monkey_test.log`（10MB × 5 备份）。

---

### 问题3：配置优先级不清晰

**当前优先级**（从高到低）：
1. CLI 参数（`--device` / `--package` / `--events`）
2. 环境变量（`MONKEY_DEVICE_ID` 等）
3. `config.ini` 文件
4. `settings/config.py` 默认值

`Config.validate()` 在测试执行前校验必填项，`--validate-only` 模式可在无设备时提前验证。

---

## 六、代码质量问题

### 问题1：循环导入

**症状**：`utils.py` 导入 `logger` 时触发循环导入。

**解决方案**：`utils.py` 中 `logger` 延迟导入（函数内部 `from settings.logging_config import logger`），避免模块加载时的循环依赖。

---

### 问题2：README.md 存在多处 git merge conflict

**症状**：README 包含 `<<<<<<<`、`=======`、`>>>>>>>` 标记，无法正常阅读。

**解决方案**：手动解决所有 conflict，保留最新分支内容，重写为当前实际项目状态。

---

### 问题3：`get_connected_devices` 误匹配 `offline` 设备

**症状**：`adb devices` 输出中 `offline` 设备也被返回。

**原因**：原实现匹配 `"device" in line`，会匹配到 `offline` 行中的包含 `device` 的字符串。

**解决方案**：改为精确匹配 `"\tdevice" in line`，只返回状态为 `device` 的在线设备。

```python
# 修复前
if "device" in line and not line.startswith("List")

# 修复后
if "\tdevice" in line
```
