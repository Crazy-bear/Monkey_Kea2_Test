# 项目问题和解决方案文档

## 项目概述
本文档记录了【A1力量镜】Monkey自动化测试项目开发过程中遇到的各种实际问题及其解决方案，为未来类似项目提供参考。

## 设备连接问题

### 问题1：ADB设备连接不稳定
**症状**：设备经常断开连接，ADB命令执行失败。

**原因**：
- USB数据线质量不佳
- 设备USB调试模式不稳定
- ADB服务异常

**解决方案**：
1. 使用高质量的USB数据线
2. 确保设备USB调试模式已正确开启
3. 重启ADB服务：`adb kill-server && adb start-server`
4. 在代码中添加设备连接重试机制

**实现代码**：
```python
# 在ADBClient类中添加设备连接重试机制
def run_command(self, cmd, monkey_log_file=None, capture_output=False, max_retries=3):
    """
    执行 ADB 命令并返回结果，支持重试机制。
    
    Args:
        cmd: 要执行的命令列表
        monkey_log_file: 日志文件路径，如果为None则不保存日志
        capture_output: 是否捕获输出并返回
        max_retries: 最大重试次数
        
    Returns:
        如果capture_output为True，返回(output, error)
        否则返回(monkey_log_file, error)
    """
    retry_count = 0
    while retry_count < max_retries:
        try:
            if capture_output:
                result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                return result.stdout, result.stderr
            else:
                if monkey_log_file:
                    with open(monkey_log_file, "w") as log_file:
                        result = subprocess.run(cmd, shell=True, stdout=log_file, stderr=subprocess.STDOUT, text=True)
                    return monkey_log_file, result.stderr
                else:
                    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    return result.stdout, result.stderr
        except Exception as e:
            retry_count += 1
            if retry_count < max_retries:
                logger.warning(f"ADB命令执行失败，正在重试 ({retry_count}/{max_retries}): {e}")
                time.sleep(2)  # 等待2秒后重试
            else:
                logger.error(f"ADB命令执行失败，已达到最大重试次数: {e}")
                raise
```

### 问题2：设备ID获取失败
**症状**：无法获取设备ID，导致测试无法执行。

**原因**：
- 设备未正确连接
- ADB服务未运行
- 设备驱动未安装

**解决方案**：
1. 检查设备连接状态：`adb devices`
2. 确保ADB服务正常运行
3. 安装设备驱动程序
4. 在配置文件中提供默认设备ID作为备选

**实现代码**：
```python
# 在MonkeyRunner类的初始化方法中添加设备连接检查
def __init__(self, adb_client, config):
    self.adb_client = adb_client
    self.config = config
    # 检查设备是否连接
    devices = adb_client.get_connected_devices()
    if not devices:
        logger.error("未检测到已连接的设备，请检查设备连接状态")
        raise Exception("未检测到已连接的设备")
    # 如果配置中没有指定设备ID，使用第一个检测到的设备
    if not config.DEVICE_ID:
        config.DEVICE_ID = devices[0]
        logger.info(f"未指定设备ID，使用第一个检测到的设备: {config.DEVICE_ID}")
    # 尝试连接设备
    max_retries = 3
    retry_count = 0
    while retry_count < max_retries:
        try:
            self.d = u2.connect(config.DEVICE_ID)
            break
        except Exception as e:
            retry_count += 1
            if retry_count < max_retries:
                logger.warning(f"设备连接失败，正在重试 ({retry_count}/{max_retries}): {e}")
                time.sleep(2)
            else:
                logger.error(f"设备连接失败，已达到最大重试次数: {e}")
                raise
    # 初始化 LogcatHandler
    from core.logcat_handler import LogcatHandler
    self.logcat_handler = LogcatHandler(config)
```

## 测试执行问题

### 问题1：Monkey测试过程中应用崩溃
**症状**：Monkey测试执行过程中应用崩溃，测试提前终止。

**原因**：
- 应用存在稳定性问题
- Monkey事件序列触发了应用bug
- 设备资源不足

**解决方案**：
1. 分析崩溃日志，定位问题原因
2. 优化Monkey事件分布，减少可能导致崩溃的操作
3. 增加设备资源监控，在资源不足时调整测试策略
4. 实现崩溃后自动重启应用的功能

**实现代码**：
```python
# 在run_monkey方法中添加崩溃检测和应用重启功能
def run_monkey(self, monkey_log_file, max_bytes=10 * 1024 * 1024):
    """
    运行 Monkey 测试并实时解析日志，支持日志轮转和崩溃后重启
    """
    try:
        # 创建日志轮转处理器
        # ... 现有代码 ...
        
        # 构建 Monkey 命令
        cmd = [
            "adb", "-s", self.config.DEVICE_ID, "shell", "monkey",
            "-p", self.config.PACKAGE_NAME,   # 应用包名
            "-s", str(self.config.SEED),    # 随机事件种子
            "--throttle", "500",  # 每次事件之间的间隔（毫秒）
            "--pct-touch", "40",    # 触摸事件百分比
            "--pct-motion", "60",   # 滑动事件百分比
            "--pct-syskeys", "0",   # 系统按键事件百分比
            "--ignore-crashes",  # 忽略应用崩溃
            "--ignore-timeouts",    # 忽略超时错误
            "--monitor-native-crashes",  # 监控原生崩溃
            "-v", "-v", "-v",  # 详细日志（拆分为单独参数）
            str(self.config.EVENT_COUNT),  # 事件数量
        ]
        
        logger.info(f"MonkeyRunner: 执行命令: {' '.join(cmd)}")

        # 创建日志轮转对象
        rotator = LogRotator(monkey_log_file, max_bytes)
        
        # 启动实时崩溃检测
        def crash_callback(crash_info):
            logger.warning(f"检测到应用崩溃: {crash_info}")
            # 重启应用
            try:
                logger.info("尝试重启应用...")
                self.adb_client.launch_app(self.config.PACKAGE_NAME)
                logger.info("应用重启成功，继续测试")
            except Exception as e:
                logger.error(f"重启应用失败: {e}")
        
        # 启动实时崩溃检测线程
        crash_detection_thread = threading.Thread(
            target=self.logcat_handler.start_real_time_crash_detection,
            args=(monkey_log_file, crash_callback)
        )
        crash_detection_thread.daemon = True
        crash_detection_thread.start()
        
        # 使用 subprocess.Popen 实时读取日志
        # ... 现有代码 ...
        
    except Exception as e:
        logger.error(f"执行 Monkey 测试时发生错误: {e}")
        if 'rotator' in locals():
            rotator.write(f"\n执行 Monkey 测试时发生错误: {e}\n")
            rotator.close()
```

### 问题2：测试执行速度慢
**症状**：Monkey测试执行速度慢，完成测试需要很长时间。

**原因**：
- 事件间隔设置过大
- 设备性能不足
- 日志捕获开销大

**解决方案**：
1. 优化事件间隔设置，根据设备性能调整
2. 使用性能更好的测试设备
3. 优化日志捕获策略，减少不必要的日志记录
4. 实现并行测试，同时在多个设备上执行测试

**实现代码**：
```python
# 优化日志捕获策略，减少开销
def start_logcat(self, output_file, buffers=None, max_bytes=10 * 1024 * 1024, log_level="W"):
    """
    启动 Logcat 日志捕获，支持日志轮转和日志级别过滤。
    
    Args:
        output_file: 日志输出文件路径
        buffers: 要捕获的日志缓冲区列表，默认包括 main、events、crash
        max_bytes: 日志文件最大大小，默认10MB
        log_level: 日志级别，默认W（警告及以上）
        
    Returns:
        subprocess.Popen: 日志捕获进程
    """
    if buffers is None:
        buffers = ["main", "events", "crash"]
    
    # 构建命令，添加日志级别过滤
    cmd = ["adb", "-s", self.config.DEVICE_ID, "logcat", f"*:{log_level}"]
    for buffer in buffers:
        cmd.extend(["-b", buffer])
    
    try:
        # ... 现有代码 ...
        
    except Exception as e:
        logger.error(f"启动 Logcat 失败: {e}")
        return None
```

## 性能监控问题

### 问题1：CPU使用率监控不准确
**症状**：CPU使用率监控数据波动大，不准确。

**原因**：
- ADB命令获取CPU数据的方式存在误差
- 设备负载变化频繁
- 监控采样间隔不合理

**解决方案**：
1. 优化CPU数据获取命令，使用更准确的方法
2. 增加采样次数，取平均值减少波动
3. 调整采样间隔，平衡准确性和性能开销

**实现代码**：
```python
# 在cpu.py中优化CPU数据获取
def get_cpu_usage(self, package_name):
    """
    获取应用的CPU使用率，使用更准确的方法
    
    Args:
        package_name: 应用包名
        
    Returns:
        float: CPU使用率（百分比）
    """
    try:
        # 使用top命令获取更准确的CPU数据
        cmd = f"adb -s {self.device_id} shell top -n 1 | grep {package_name}"
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # 解析结果
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            cpu_usages = []
            for line in lines:
                parts = line.split()
                if len(parts) > 8:
                    # 提取CPU使用率
                    cpu_usage = float(parts[8].replace('%', ''))
                    cpu_usages.append(cpu_usage)
            
            if cpu_usages:
                # 取平均值减少波动
                return sum(cpu_usages) / len(cpu_usages)
        
        # 如果top命令失败，使用ps命令作为备选
        cmd = f"adb -s {self.device_id} shell ps -o %cpu,pid,comm | grep {package_name}"
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            cpu_usages = []
            for line in lines:
                parts = line.split()
                if len(parts) > 0:
                    try:
                        cpu_usage = float(parts[0])
                        cpu_usages.append(cpu_usage)
                    except ValueError:
                        pass
            
            if cpu_usages:
                return sum(cpu_usages) / len(cpu_usages)
        
        return 0.0
    except Exception as e:
        logger.error(f"获取CPU使用率失败: {e}")
        return 0.0
```

### 问题2：内存监控数据异常
**症状**：内存监控数据显示异常，与实际情况不符。

**原因**：
- 内存计算方式不正确
- 应用内存使用波动大
- 设备内存管理机制影响

**解决方案**：
1. 使用更准确的内存计算方法，区分不同类型的内存使用
2. 增加内存监控的采样频率
3. 分析内存使用趋势，而不仅仅关注单个数据点

**实现代码**：
```python
# 在memory.py中优化内存数据获取
def get_memory_usage(self, package_name):
    """
    获取应用的内存使用情况，区分不同类型的内存
    
    Args:
        package_name: 应用包名
        
    Returns:
        dict: 内存使用情况
    """
    try:
        # 使用dumpsys meminfo命令获取详细内存信息
        cmd = f"adb -s {self.device_id} shell dumpsys meminfo {package_name}"
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.stdout:
            output = result.stdout
            memory_info = {
                'total_pss': 0,
                'java_heap': 0,
                'native_heap': 0,
                'code': 0,
                'stack': 0,
                'graphics': 0,
                'other': 0
            }
            
            # 解析PSS Total
            pss_match = re.search(r'TOTAL\s+:\s+(\d+)', output)
            if pss_match:
                memory_info['total_pss'] = int(pss_match.group(1)) / 1024  # 转换为MB
            
            # 解析其他内存类型
            heap_match = re.search(r'Java Heap:\s+(\d+)', output)
            if heap_match:
                memory_info['java_heap'] = int(heap_match.group(1)) / 1024
            
            native_match = re.search(r'Native Heap:\s+(\d+)', output)
            if native_match:
                memory_info['native_heap'] = int(native_match.group(1)) / 1024
            
            code_match = re.search(r'Code:\s+(\d+)', output)
            if code_match:
                memory_info['code'] = int(code_match.group(1)) / 1024
            
            stack_match = re.search(r'Stack:\s+(\d+)', output)
            if stack_match:
                memory_info['stack'] = int(stack_match.group(1)) / 1024
            
            graphics_match = re.search(r'Graphics:\s+(\d+)', output)
            if graphics_match:
                memory_info['graphics'] = int(graphics_match.group(1)) / 1024
            
            other_match = re.search(r'Other:\s+(\d+)', output)
            if other_match:
                memory_info['other'] = int(other_match.group(1)) / 1024
            
            return memory_info
        
        return {'total_pss': 0, 'java_heap': 0, 'native_heap': 0, 'code': 0, 'stack': 0, 'graphics': 0, 'other': 0}
    except Exception as e:
        logger.error(f"获取内存使用情况失败: {e}")
        return {'total_pss': 0, 'java_heap': 0, 'native_heap': 0, 'code': 0, 'stack': 0, 'graphics': 0, 'other': 0}
```

### 问题3：FPS监控无法获取数据
**症状**：FPS监控返回0或无法获取数据。

**原因**：
- 应用未开启GPU渲染
- 设备不支持FPS获取
- ADB命令执行失败

**解决方案**：
1. 确保应用开启GPU渲染
2. 针对不同设备类型使用不同的FPS获取方法
3. 添加错误处理，在无法获取FPS时给出合理的默认值

**实现代码**：
```python
# 在fps.py中优化FPS数据获取
def get_fps(self, package_name):
    """
    获取应用的FPS（帧率）
    
    Args:
        package_name: 应用包名
        
    Returns:
        float: FPS值
    """
    try:
        # 方法1：使用dumpsys gfxinfo命令
        cmd = f"adb -s {self.device_id} shell dumpsys gfxinfo {package_name}"
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.stdout:
            output = result.stdout
            # 查找FrameTiming部分
            if 'FrameTiming' in output:
                # 解析帧率数据
                frame_times = []
                lines = output.split('\n')
                in_frame_timing = False
                for line in lines:
                    if 'FrameTiming' in line:
                        in_frame_timing = True
                    elif in_frame_timing and line.strip():
                        if line.strip().startswith('---'):
                            break
                        parts = line.strip().split()
                        if len(parts) > 1:
                            try:
                                # 获取每帧耗时（毫秒）
                                frame_time = float(parts[1])
                                frame_times.append(frame_time)
                            except ValueError:
                                pass
                
                if frame_times:
                    # 计算FPS：1000ms / 平均每帧耗时
                    avg_frame_time = sum(frame_times) / len(frame_times)
                    if avg_frame_time > 0:
                        return 1000 / avg_frame_time
        
        # 方法2：使用surfaceflinger命令（备选方法）
        cmd = f"adb -s {self.device_id} shell dumpsys surfaceflinger --latency {package_name}"
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 2:
                # 解析延迟数据
                frame_intervals = []
                for line in lines[2:]:  # 跳过前两行头信息
                    parts = line.strip().split()
                    if len(parts) > 0:
                        try:
                            # 获取帧间隔（纳秒）
                            interval = int(parts[0])
                            if interval > 0:
                                # 转换为毫秒并计算FPS
                                frame_intervals.append(interval / 1000000)
                        except ValueError:
                            pass
                
                if frame_intervals:
                    avg_interval = sum(frame_intervals) / len(frame_intervals)
                    if avg_interval > 0:
                        return 1000 / avg_interval
        
        # 如果所有方法都失败，返回合理的默认值
        return 0.0
    except Exception as e:
        logger.error(f"获取FPS失败: {e}")
        return 0.0
```

## 报告生成问题

### 问题1：报告生成失败
**症状**：测试完成后无法生成报告，或生成的报告格式错误。

**原因**：
- 模板文件不存在或格式错误
- 报告数据格式不正确
- 文件权限问题

**解决方案**：
1. 确保报告模板文件存在且格式正确
2. 验证报告数据格式，确保与模板匹配
3. 检查文件权限，确保可以写入报告文件
4. 添加错误处理，在报告生成失败时提供详细错误信息

**实现代码**：
```python
# 在report_generator.py中优化报告生成
def generate_report(self, report_data, output_file, format_type="html"):
    """
    生成测试报告
    
    Args:
        report_data: 报告数据
        output_file: 输出文件路径
        format_type: 报告格式，支持html和json
        
    Returns:
        bool: 报告生成是否成功
    """
    try:
        # 确保输出目录存在
        output_dir = os.path.dirname(output_file)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        if format_type == "json":
            # 生成JSON格式报告
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            logger.info(f"JSON报告已生成: {output_file}")
            return True
        elif format_type == "html":
            # 检查模板文件是否存在
            template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
            template_file = os.path.join(template_dir, "report_template.html")
            
            if not os.path.exists(template_file):
                logger.error(f"报告模板文件不存在: {template_file}")
                # 使用内置模板作为备选
                html_content = self._get_default_template()
            else:
                # 读取模板文件
                with open(template_file, "r", encoding="utf-8") as f:
                    html_content = f.read()
            
            # 替换模板中的变量
            html_content = self._replace_template_variables(html_content, report_data)
            
            # 写入报告文件
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            logger.info(f"HTML报告已生成: {output_file}")
            return True
        else:
            logger.error(f"不支持的报告格式: {format_type}")
            return False
    except Exception as e:
        logger.error(f"生成报告失败: {e}")
        # 尝试生成简单的文本报告作为备选
        try:
            txt_file = os.path.splitext(output_file)[0] + ".txt"
            with open(txt_file, "w", encoding="utf-8") as f:
                f.write(f"测试报告\n")
                f.write(f"设备ID: {report_data.get('device_id', 'N/A')}\n")
                f.write(f"应用包名: {report_data.get('package_name', 'N/A')}\n")
                f.write(f"开始时间: {report_data.get('start_time', 'N/A')}\n")
                f.write(f"结束时间: {report_data.get('end_time', 'N/A')}\n")
                f.write(f"测试时长: {report_data.get('duration', 'N/A')}\n")
                f.write(f"崩溃次数: {report_data.get('crash_count', 0)}\n")
            logger.info(f"文本报告已生成: {txt_file}")
        except:
            pass
        return False
    
def _get_default_template(self):
    """
    获取默认的HTML报告模板
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Monkey测试报告</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1, h2 { color: #333; }
            table { border-collapse: collapse; width: 100%; margin-top: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .success { color: green; }
            .error { color: red; }
        </style>
    </head>
    <body>
        <h1>Monkey测试报告</h1>
        <table>
            <tr><th>项目</th><th>值</th></tr>
            <tr><td>设备ID</td><td>{{device_id}}</td></tr>
            <tr><td>应用包名</td><td>{{package_name}}</td></tr>
            <tr><td>开始时间</td><td>{{start_time}}</td></tr>
            <tr><td>结束时间</td><td>{{end_time}}</td></tr>
            <tr><td>测试时长</td><td>{{duration}}</td></tr>
            <tr><td>崩溃次数</td><td>{{crash_count}}</td></tr>
        </table>
        {% if crashes %}
        <h2>崩溃信息</h2>
        <ul>
            {% for crash in crashes %}
            <li>{{crash}}</li>
            {% endfor %}
        </ul>
        {% endif %}
        {% if performance_data %}
        <h2>性能数据</h2>
        <table>
            <tr><th>指标</th><th>值</th></tr>
            <tr><td>CPU使用率</td><td>{{performance_data.cpu_usage}}%</td></tr>
            <tr><td>内存使用</td><td>{{performance_data.memory_usage}}MB</td></tr>
            <tr><td>FPS</td><td>{{performance_data.fps}}</td></tr>
        </table>
        {% endif %}
    </body>
    </html>
    """
```

### 问题2：报告内容不完整
**症状**：生成的报告缺少部分数据，如性能数据或崩溃信息。

**原因**：
- 数据收集失败
- 数据处理错误
- 报告模板未包含所有数据字段

**解决方案**：
1. 检查数据收集过程，确保所有数据都被正确收集
2. 优化数据处理逻辑，确保数据完整性
3. 更新报告模板，包含所有必要的数据字段
4. 添加数据验证，确保数据完整性后再生成报告

**实现代码**：
```python
# 在main.py中优化数据收集和报告生成
def main():
    # ... 现有代码 ...
    
    # 准备性能数据
    performance_data = None
    performance_dir = os.path.join(output_dir, 'performance')
    if os.path.exists(performance_dir):
        # 查找最新的性能数据文件
        import glob
        performance_files = glob.glob(os.path.join(performance_dir, 'performance_*.json'))
        if performance_files:
            latest_performance_file = max(performance_files, key=os.path.getmtime)
            try:
                import json
                with open(latest_performance_file, 'r', encoding='utf-8') as f:
                    performance_data = json.load(f)
            except Exception as e:
                logger.error(f"读取性能数据失败: {e}")
                # 尝试读取CSV格式的性能数据作为备选
                csv_files = glob.glob(os.path.join(performance_dir, 'performance_*.csv'))
                if csv_files:
                    latest_csv_file = max(csv_files, key=os.path.getmtime)
                    try:
                        import csv
                        with open(latest_csv_file, 'r', encoding='utf-8') as f:
                            reader = csv.DictReader(f)
                            rows = list(reader)
                            if rows:
                                # 计算平均值
                                cpu_values = []
                                memory_values = []
                                fps_values = []
                                for row in rows:
                                    if 'cpu' in row:
                                        cpu_values.append(float(row['cpu']))
                                    if 'memory' in row:
                                        memory_values.append(float(row['memory']))
                                    if 'fps' in row:
                                        fps_values.append(float(row['fps']))
                                
                                performance_data = {
                                    'cpu_usage': sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                                    'memory_usage': sum(memory_values) / len(memory_values) if memory_values else 0,
                                    'fps': sum(fps_values) / len(fps_values) if fps_values else 0
                                }
                    except Exception as e:
                        logger.error(f"读取CSV性能数据失败: {e}")
    
    # 准备报告数据
    report_data = {
        'device_id': config.DEVICE_ID,
        'package_name': config.PACKAGE_NAME,
        'device_version_name': config.DeviceVersionName,
        'start_time': start_time,
        'end_time': end_time,
        'duration': duration,
        'seed_value': config.SEED,
        'execution_count': config.EVENT_COUNT,
        'crash_count': crash_count,
        'crashes': crashes,
        'log_analysis': log_analysis,
        'performance_data': performance_data,
        'details': f"Monkey测试执行完成，共执行{config.EVENT_COUNT}个事件，检测到{crash_count}次崩溃。"
    }
    
    # 验证报告数据完整性
    required_fields = ['device_id', 'package_name', 'start_time', 'end_time', 'duration']
    for field in required_fields:
        if field not in report_data or not report_data[field]:
            logger.warning(f"报告数据缺少必要字段: {field}")
            # 填充默认值
            report_data[field] = 'N/A'
    
    # 生成报告
    report_generator.generate_report(report_data, report_file, args.format)
    
    logger.info(f"[{end_time}] Monkey测试完成 - 用时: {duration}, 崩溃次数: {crash_count}")
    logger.info(f"[{end_time}] 测试报告已生成: {report_file}")
```

## 配置管理问题

### 问题1：配置参数冲突
**症状**：环境变量和配置文件中的参数冲突，导致测试行为不一致。

**原因**：
- 配置优先级不明确
- 配置加载顺序错误
- 配置验证机制缺失

**解决方案**：
1. 明确配置优先级：环境变量 > 命令行参数 > 配置文件
2. 优化配置加载顺序，确保正确覆盖
3. 添加配置验证，检测并提示配置冲突
4. 提供配置检查命令，验证当前有效配置

**实现代码**：
```python
# 在config.py中优化配置管理
import os

class Config:
    def __init__(self):
        # 从环境变量加载配置（优先级最高）
        self.DEVICE_ID = os.environ.get('MONKEY_DEVICE_ID', "")
        self.PACKAGE_NAME = os.environ.get('MONKEY_PACKAGE_NAME', "com.example.app")
        self.EVENT_COUNT = int(os.environ.get('MONKEY_COUNT', 10000))
        self.SEED = int(os.environ.get('MONKEY_SEED', 12345))
        
        # 从配置文件加载默认值（优先级最低）
        self._load_from_config_file()
        
        # 设备版本信息（运行时获取）
        self.DeviceVersionName = ""
    
    def _load_from_config_file(self):
        """
        从配置文件加载默认值
        """
        try:
            # 这里可以从配置文件加载默认值
            # 例如从config.json或其他配置文件读取
            pass
        except Exception as e:
            logger.error(f"从配置文件加载配置失败: {e}")
    
    def update_from_args(self, args):
        """
        从命令行参数更新配置（优先级高于配置文件，低于环境变量）
        
        Args:
            args: 命令行参数对象
        """
        # 只有当环境变量未设置时，才使用命令行参数
        if args.device and not os.environ.get('MONKEY_DEVICE_ID'):
            self.DEVICE_ID = args.device
        if args.package and not os.environ.get('MONKEY_PACKAGE_NAME'):
            self.PACKAGE_NAME = args.package
        if args.events and not os.environ.get('MONKEY_COUNT'):
            self.EVENT_COUNT = args.events
    
    def validate(self):
        """
        验证配置有效性
        
        Returns:
            bool: 配置是否有效
        """
        errors = []
        if not self.DEVICE_ID:
            errors.append("设备ID未配置")
        if not self.PACKAGE_NAME:
            errors.append("应用包名未配置")
        if self.EVENT_COUNT <= 0:
            errors.append("事件数量必须大于0")
        
        if errors:
            for error in errors:
                logger.error(f"配置错误: {error}")
            return False
        return True
    
    def get_effective_config(self):
        """
        获取当前有效配置
        
        Returns:
            dict: 有效配置
        """
        return {
            'DEVICE_ID': self.DEVICE_ID,
            'PACKAGE_NAME': self.PACKAGE_NAME,
            'EVENT_COUNT': self.EVENT_COUNT,
            'SEED': self.SEED
        }
```

### 问题2：配置文件格式错误
**症状**：配置文件格式错误，导致测试无法启动。

**原因**：
- 配置文件语法错误
- 配置项缺失
- 配置值类型错误

**解决方案**：
1. 提供配置文件模板，确保格式正确
2. 添加配置文件验证，在启动时检查配置格式
3. 提供默认配置值，在配置缺失时使用
4. 详细记录配置错误信息，便于排查

**实现代码**：
```python
# 在config.py中添加配置文件验证
def _load_from_config_file(self):
    """
    从配置文件加载默认值，包含错误处理
    """
    config_file = os.path.join(os.path.dirname(__file__), "config.json")
    if os.path.exists(config_file):
        try:
            import json
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                
                # 验证配置文件格式
                required_fields = ['DEVICE_ID', 'PACKAGE_NAME']
                for field in required_fields:
                    if field not in config_data:
                        logger.warning(f"配置文件缺少必要字段: {field}")
                
                # 加载配置值，使用默认值作为备选
                self.DEVICE_ID = self.DEVICE_ID or config_data.get('DEVICE_ID', "")
                self.PACKAGE_NAME = self.PACKAGE_NAME or config_data.get('PACKAGE_NAME', "com.example.app")
                self.EVENT_COUNT = self.EVENT_COUNT or int(config_data.get('EVENT_COUNT', 10000))
                self.SEED = self.SEED or int(config_data.get('SEED', 12345))
                
        except json.JSONDecodeError as e:
            logger.error(f"配置文件格式错误: {e}")
            # 使用默认值
            self._set_defaults()
        except Exception as e:
            logger.error(f"从配置文件加载配置失败: {e}")
            # 使用默认值
            self._set_defaults()
    else:
        logger.info("配置文件不存在，使用默认值")
        self._set_defaults()

def _set_defaults(self):
    """
    设置默认配置值
    """
    if not self.DEVICE_ID:
        self.DEVICE_ID = ""
    if not self.PACKAGE_NAME:
        self.PACKAGE_NAME = "com.example.app"
    if self.EVENT_COUNT <= 0:
        self.EVENT_COUNT = 10000
    if self.SEED <= 0:
        self.SEED = 12345
```

## 代码质量问题

### 问题1：代码重复度高
**症状**：代码中存在大量重复代码，维护困难。

**原因**：
- 缺乏代码复用意识
- 功能模块划分不合理
- 通用功能未抽象为工具函数

**解决方案**：
1. 识别重复代码，抽象为公共函数或类
2. 优化模块划分，提高代码复用性
3. 建立工具函数库，集中管理通用功能
4. 定期进行代码审查，发现并消除重复代码

**实现代码**：
```python
# 在utils.py中添加通用功能
import os
import time
from config.logging_config import logger

def get_timestamp():
    """
    获取当前时间戳
    
    Returns:
        str: 时间戳字符串
    """
    return time.strftime("%Y%m%d_%H%M%S")

def create_output_dirs(output_dir):
    """
    创建输出目录
    
    Args:
        output_dir: 输出目录路径
    """
    try:
        os.makedirs(os.path.join(output_dir, "logs"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "reports"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "performance"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "monkey_logs"), exist_ok=True)
    except Exception as e:
        logger.error(f"创建输出目录失败: {e}")

class LogRotator:
    """
    日志轮转处理器
    """
    def __init__(self, file_path, max_size):
        self.file_path = file_path
        self.max_size = max_size
        self.file = open(file_path, "w", encoding="utf-8")
        self.closed = False
        self.last_rotate_time = 0
    
    def write(self, data):
        if self.closed:
            return
        try:
            # 检查文件大小
            self.file.write(data)
            self.file.flush()
            
            # 检查是否需要轮转（增加时间间隔，避免频繁轮转）
            current_time = time.time()
            if current_time - self.last_rotate_time > 600:  # 每10分钟轮转一次
                self.file.seek(0, os.SEEK_END)
                if self.file.tell() > self.max_size:
                    self._rotate()
                    self.last_rotate_time = current_time
        except Exception as e:
            logger.error(f"日志写入失败: {e}")
    
    def _rotate(self):
        if self.closed:
            return
        try:
            # 关闭当前文件
            self.file.close()
            
            # 生成带时间戳的新文件名
            base, ext = os.path.splitext(self.file_path)
            timestamp = get_timestamp()
            new_filename = f"{base}_{timestamp}{ext}"
            
            # 重命名当前日志文件
            if os.path.exists(self.file_path):
                os.rename(self.file_path, new_filename)
                logger.info(f"日志文件已轮转: {new_filename}")
            
            # 重新打开日志文件
            self.file = open(self.file_path, "w", encoding="utf-8")
        except Exception as e:
            logger.error(f"日志轮转失败: {e}")
            # 尝试重新打开文件
            try:
                self.file = open(self.file_path, "w", encoding="utf-8")
            except:
                pass
    
    def close(self):
        if not self.closed and self.file:
            try:
                self.file.close()
            except:
                pass
            self.closed = True
```

### 问题2：异常处理不完善
**症状**：代码缺乏异常处理，遇到错误时程序崩溃。

**原因**：
- 开发时未考虑异常情况
- 异常处理逻辑不完善
- 错误信息不明确

**解决方案**：
1. 识别可能的异常情况，添加try-except块
2. 提供详细的错误信息，便于排查问题
3. 实现优雅降级，在遇到非致命错误时继续执行
4. 记录异常日志，便于后续分析

**实现代码**：
```python
# 在adb_client.py中添加完善的异常处理
def get_connected_devices(self):
    """
    获取已连接的设备列表。
    
    Returns:
        list: 设备ID列表
    """
    try:
        cmd = ["adb", "devices"]
        stdout, stderr = self.run_command(cmd, capture_output=True)
        if stderr:
            logger.warning(f"执行adb devices命令时产生错误: {stderr}")
        
        devices = []
        for line in stdout.splitlines():
            if "device" in line and not line.startswith("List"):
                parts = line.split()
                if len(parts) > 0:
                    devices.append(parts[0])
        
        if not devices:
            logger.warning("未检测到已连接的设备")
        
        return devices
    except Exception as e:
        logger.error(f"获取已连接设备列表失败: {e}")
        return []

def launch_app(self, package_name, log_file=None):
    """
    启动应用。
    
    Args:
        package_name: 应用包名
        log_file: 日志文件路径
        
    Returns:
        tuple: (输出结果, 错误信息)
    """
    try:
        if not package_name:
            raise ValueError("应用包名不能为空")
        
        cmd = ["adb", "-s", self.config.DEVICE_ID, "shell", "monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1"]
        return self.run_command(cmd, log_file)
    except Exception as e:
        logger.error(f"启动应用失败: {e}")
        if log_file:
            return log_file, str(e)
        else:
            return "", str(e)
```

## 性能优化问题

### 问题1：内存使用过高
**症状**：测试过程中内存使用过高，导致设备卡顿。

**原因**：
- 内存泄漏
- 数据缓存过大
- 并发操作过多

**解决方案**：
1. 检查代码中的内存泄漏问题
2. 优化数据缓存策略，及时释放不需要的内存
3. 控制并发操作数量，避免资源竞争
4. 使用内存分析工具，识别内存使用热点

**实现代码**：
```python
# 在performance/monitor.py中优化内存使用
def __init__(self, device_id, package_name, output_dir):
    self.device_id = device_id
    self.package_name = package_name
    self.output_dir = output_dir
    self.running = False
    self.monitor_thread = None
    self.cpu_monitor = None
    self.memory_monitor = None
    self.fps_monitor = None
    self.data = []
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

def start(self):
    """
    启动性能监控
    """
    try:
        from performance.cpu import CPUMonitor
        from performance.memory import MemoryMonitor
        from performance.fps import FPSMonitor
        
        self.cpu_monitor = CPUMonitor(self.device_id)
        self.memory_monitor = MemoryMonitor(self.device_id)
        self.fps_monitor = FPSMonitor(self.device_id)
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        logger.info("性能监控已启动")
    except Exception as e:
        logger.error(f"启动性能监控失败: {e}")

def _monitor_loop(self):
    """
    监控循环
    """
    start_time = time.time()
    while self.running:
        try:
            # 收集性能数据
            cpu_usage = self.cpu_monitor.get_cpu_usage(self.package_name)
            memory_info = self.memory_monitor.get_memory_usage(self.package_name)
            fps = self.fps_monitor.get_fps(self.package_name)
            
            # 只保存必要的数据，减少内存使用
            current_time = time.time() - start_time
            self.data.append({
                'time': current_time,
                'cpu': cpu_usage,
                'memory': memory_info.get('total_pss', 0),
                'fps': fps
            })
            
            # 限制数据量，避免内存使用过高
            if len(self.data) > 1000:
                # 只保留最近的500条数据
                self.data = self.data[-500:]
            
            time.sleep(1)  # 每秒收集一次数据
        except Exception as e:
            logger.error(f"性能监控循环出错: {e}")
            time.sleep(1)

def stop(self):
    """
    停止性能监控
    """
    try:
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        # 保存数据并清空内存
        self._save_data()
        self.data = []  # 清空数据，释放内存
        
        logger.info("性能监控已停止")
    except Exception as e:
        logger.error(f"停止性能监控失败: {e}")

def _save_data(self):
    """
    保存性能数据
    """
    try:
        if not self.data:
            return
        
        timestamp = get_timestamp()
        json_file = os.path.join(self.output_dir, f"performance_{timestamp}.json")
        csv_file = os.path.join(self.output_dir, f"performance_{timestamp}.csv")
        
        # 保存为JSON格式
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        
        # 保存为CSV格式
        if self.data:
            keys = self.data[0].keys()
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(self.data)
        
        logger.info(f"性能数据已保存: {json_file}")
    except Exception as e:
        logger.error(f"保存性能数据失败: {e}")
```

### 问题2：CPU使用率过高
**症状**：测试过程中CPU使用率过高，影响测试准确性。

**原因**：
- 循环操作过于密集
- 日志记录过于频繁
- 并发线程过多

**解决方案**：
1. 优化循环操作，减少不必要的计算
2. 调整日志级别，减少日志记录开销
3. 控制线程数量，避免过度并发
4. 使用性能分析工具，识别CPU使用热点

**实现代码**：
```python
# 在monkey_runner.py中优化CPU使用
def run_monkey(self, monkey_log_file, max_bytes=10 * 1024 * 1024):
    """
    运行 Monkey 测试并实时解析日志，支持日志轮转
    """
    try:
        # 创建日志轮转处理器
        rotator = LogRotator(monkey_log_file, max_bytes)
        
        # 构建 Monkey 命令
        cmd = [
            "adb", "-s", self.config.DEVICE_ID, "shell", "monkey",
            "-p", self.config.PACKAGE_NAME,   # 应用包名
            "-s", str(self.config.SEED),    # 随机事件种子
            "--throttle", "500",  # 每次事件之间的间隔（毫秒）
            "--pct-touch", "40",    # 触摸事件百分比
            "--pct-motion", "60",   # 滑动事件百分比
            "--pct-syskeys", "0",   # 系统按键事件百分比
            "--ignore-crashes",  # 忽略应用崩溃
            "--ignore-timeouts",    # 忽略超时错误
            "--monitor-native-crashes",  # 监控原生崩溃
            "-v",  # 只使用一个-v，减少日志输出
            str(self.config.EVENT_COUNT),  # 事件数量
        ]
        
        logger.info(f"MonkeyRunner: 执行命令: {' '.join(cmd)}")

        # 使用 subprocess.Popen 实时读取日志
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        throttle = 0.5  # throttle延迟（秒），与--throttle 500对应
        
        # 减少日志解析频率，每10行解析一次
        line_count = 0
        parse_interval = 10
        
        try:
            # 读取所有输出
            while True:
                line = proc.stdout.readline()
                if not line:
                    break
                line = line.strip()
                rotator.write(line + "\n")
                
                # 检测到事件时添加延迟（因为--throttle在该设备上可能不生效）
                if "Sending" in line:
                    time.sleep(throttle)
                
                # 减少解析频率，降低CPU使用率
                line_count += 1
                if line_count % parse_interval == 0:
                    self.parse_monkey_event(line, rotator)
            
            # 确保等待进程完全结束
            proc.wait(timeout=300)  # 5分钟超时
            
            # 检查进程退出码
            if proc.returncode != 0:
                logger.warning(f"Monkey 测试执行完成，退出码: {proc.returncode}")
                rotator.write(f"\nMonkey 测试执行完成，退出码: {proc.returncode}\n")
            else:
                logger.info("Monkey 测试执行成功")
                rotator.write("\nMonkey 测试执行成功\n")
        except subprocess.TimeoutExpired:
            logger.error("Monkey 测试执行超时")
            rotator.write("\nMonkey 测试执行超时\n")
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except:
                pass
        finally:
            rotator.close()
                
    except Exception as e:
        logger.error(f"执行 Monkey 测试时发生错误: {e}")
        if 'rotator' in locals():
            rotator.write(f"\n执行 Monkey 测试时发生错误: {e}\n")
            rotator.close()
```

## 总结

本项目在开发过程中遇到了多种实际问题，通过系统分析和有针对性的解决方案，成功克服了这些挑战。以下是一些关键经验：

1. **设备管理**：建立稳定的设备连接机制，处理各种设备异常情况，添加重试机制和错误处理
2. **测试策略**：优化测试参数和事件分布，提高测试效率和覆盖度，实现崩溃后自动重启应用
3. **性能监控**：使用多种方法获取性能数据，确保数据准确性，优化数据收集和存储策略
4. **报告系统**：设计灵活的报告模板，确保报告内容完整准确，添加错误处理和备选方案
5. **配置管理**：建立清晰的配置优先级和验证机制，提供详细的错误信息和默认值
6. **代码质量**：注重代码复用和异常处理，提高代码可维护性，定期进行代码审查
7. **性能优化**：定期进行性能分析，优化资源使用，控制内存和CPU使用率

这些经验和解决方案将为未来的自动化测试项目提供宝贵参考，帮助团队更高效地开发和维护测试系统。