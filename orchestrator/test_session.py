# -*- coding: utf-8 -*-
"""
统一测试会话：并行启动性能监控与 Logcat，供 Kea2 / Monkey 共用。
"""
import os
import time
import threading

from settings.logging_config import logger
from core.logcat_handler import LogcatHandler
from performance.monitor import PerformanceMonitor
from orchestrator.perf_context import (
    KEA2_PERF_PHASE_FILE_ENV,
    perf_phase_path,
    ui_context_path,
)

_active_monitor = None
_active_monitor_lock = threading.Lock()
_lock_modules = None
_lock_modules_lock = threading.Lock()


def get_active_monitor():
    """供场景脚本设置 phase 时获取当前 PerformanceMonitor。"""
    with _active_monitor_lock:
        return _active_monitor


def set_active_monitor(monitor):
    with _active_monitor_lock:
        global _active_monitor
        _active_monitor = monitor


def get_lock_modules():
    """当前 Kea2 模块锁列表；None 表示全量探索。

    优先读进程内 set_lock_modules；Kea2 子进程无该状态时回退环境变量
    KEA2_LOCK_MODULES（由 kea2_runner 注入）。
    """
    with _lock_modules_lock:
        if _lock_modules is not None:
            return list(_lock_modules)
    raw = os.environ.get("KEA2_LOCK_MODULES", "").strip()
    if not raw:
        return None
    return [m.strip().lower() for m in raw.split(",") if m.strip()]


def set_lock_modules(modules):
    with _lock_modules_lock:
        global _lock_modules
        _lock_modules = list(modules) if modules is not None else None


class TestSession:
    """管理一次稳定性测试的侧车资源。"""

    def __init__(self, config, output_dir, logcat_max_seconds):
        self.config = config
        self.output_dir = output_dir
        self.logcat_file = None
        self.performance_dir = None
        self.logcat_handler = LogcatHandler(config)
        self.performance_monitor = None
        self.coverage_sampler = None
        self._logcat_process = None
        self._logcat_max_seconds = logcat_max_seconds
        self.start_time = None
        self.end_time = None
        self.start_timestamp = None

    def start_sidecars(self, logcat_file, performance_dir, enable_coverage_sampler=False):
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
            ui_context_file=ui_context_path(self.output_dir),
            phase_file=perf_phase_path(self.output_dir),
        )
        os.environ[KEA2_PERF_PHASE_FILE_ENV] = perf_phase_path(self.output_dir)
        set_active_monitor(self.performance_monitor)
        self.performance_monitor.start()

        if enable_coverage_sampler:
            from orchestrator.coverage_sampler import CoverageSampler

            interval = float(os.environ.get("KEA2_COVERAGE_SAMPLE_INTERVAL", "12"))
            path = os.path.join(self.output_dir, "coverage_pages.json")
            self.coverage_sampler = CoverageSampler(
                self.config.DEVICE_ID, path, interval_seconds=interval
            )
            self.coverage_sampler.start()

        logger.info("侧车已启动：Logcat + 性能监控%s", " + 业务页采样" if enable_coverage_sampler else "")

    def stop_sidecars(self, wait_after_engine=2):
        self.end_time = time.strftime("%Y-%m-%d %H:%M:%S")
        if self.coverage_sampler:
            self.coverage_sampler.stop()
            self.coverage_sampler = None
        if self.performance_monitor:
            self.performance_monitor.stop()
            set_active_monitor(None)
        os.environ.pop(KEA2_PERF_PHASE_FILE_ENV, None)
        if self._logcat_process:
            if wait_after_engine:
                time.sleep(wait_after_engine)
            self.logcat_handler.stop_logcat()
            logger.info("Logcat 日志捕获已停止")
        set_lock_modules(None)

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
