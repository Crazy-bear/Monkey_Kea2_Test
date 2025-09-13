# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2025/1/10
"""


class MonkeyRunner:
    def __init__(self, adb_client, config):
        self.adb_client = adb_client
        self.config = config

    def run_monkey(self, monkey_log_file):
        cmd = [
            "adb", "-s", self.config.DEVICE_ID, "shell", "monkey",
            "-p", self.config.PACKAGE_NAME,   # 应用包名
            # "-c", "android.intent.category.LAUNCHER",  # 启动器类别
            # "-c", ".activity.HealthListActivity",  # 启动器类别
            "-s", str(self.config.SEED),    # 随机事件种子
            "--throttle", "200",  # 每次事件之间的间隔（毫秒）
            "--ignore-crashes",  # 忽略应用崩溃
            "--ignore-timeouts",    # 忽略超时错误
            "--pct-touch", "40",    # 触摸事件百分比
            "--pct-motion", "60",   # 滑动事件百分比
            "--pct-syskeys", "0",   # 系统按键事件百分比
            "--monitor-native-crashes",  # 监控原生崩溃
            # "--monitor-native-exceptions",  # 监控原生异常
            # "--ignore-security-exceptions",  # 忽略安全异常
            "-v -v -v",  # 详细日志
            str(self.config.EVENT_COUNT),  # 事件数量
        ]
        # cmd = [str(arg) for arg in cmd]  # 确保 cmd 列表中的每个元素都是字符串
        print(f"MonkeyRunner: {cmd}")
        return self.adb_client.run_command(cmd, monkey_log_file)
