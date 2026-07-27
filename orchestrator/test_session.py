# -*- coding: utf-8 -*-
"""
统一测试会话：并行启动性能监控与 Logcat，供 Kea2 / Monkey 共用。
"""
import time
import threading

from settings.logging_config import logger
from core.logcat_handler import LogcatHandler
from performance.monitor import PerformanceMonitor

_active_monitor = None
_active_monitor_lock = threading.Lock()


def get_active_monitor():
    """供场景脚本设置 phase 时获取当前 PerformanceMonitor。"""
    with _active_monitor_lock:
        return _active_monitor


def set_active_monitor(monitor):
    with _active_monitor_lock:
        global _active_monitor
        _active_monitor = monitor


class TestSession:
    """管理一次稳定性测试的侧车资源。"""

    def __init__(self, config, output_dir, logcat_max_seconds):
        self.config = config
        self.output_dir = output_dir
        self.logcat_file = None
        self.performance_dir = None
        self.logcat_handler = LogcatHandler(config)
        self.performance_monitor = None
        self._logcat_process = None
        self._logcat_max_seconds = logcat_max_seconds
        self.start_time = None
        self.end_time = None
        self.start_timestamp = None

    def start_sidecars(self, logcat_file, performance_dir):
        self.logcat_file = logcat_file
        self.performance_dir = performance_dir
        self.start_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.start_timestamp = time.time()

        self._logcat_process = self.logcat_handler.start_logcat(
            logcat_file, max_duration=self._logcat_max_seconds
        )
        self.performance_monitor = PerformanceMonitor(
            self.config.DEVICE_ID,
            self.config.PACKAGE_NAME,
            performance_dir,
            config=self.config,
        )
        set_active_monitor(self.performance_monitor)
        self.performance_monitor.start()
        logger.info("侧车已启动：Logcat + 性能监控")

    def stop_sidecars(self, wait_after_engine=2):
        self.end_time = time.strftime("%Y-%m-%d %H:%M:%S")
        if self.performance_monitor:
            self.performance_monitor.stop()
            set_active_monitor(None)
        if self._logcat_process:
            if wait_after_engine:
                time.sleep(wait_after_engine)
            self.logcat_handler.stop_logcat()
            logger.info("Logcat 日志捕获已停止")

    def duration_str(self):
        if self.start_timestamp is None:
            return "N/A"
        total = int(time.time() - self.start_timestamp)
        hours = total // 3600
        minutes = (total % 3600) // 60
        seconds = total % 60
        if hours > 0:
            return f"{hours}小时{minutes}分{seconds}秒"
        if minutes > 0:
            return f"{minutes}分{seconds}秒"
        return f"{seconds}秒"
