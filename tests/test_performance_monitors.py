# -*- coding: utf-8 -*-
"""性能监控模块单元测试（mock ADBClient，无需设备）。"""

from unittest.mock import MagicMock


class TestCPUMonitor:
    def test_parse_top_for_pid(self):
        from performance.cpu import CPUMonitor

        monitor = CPUMonitor("dummy", "com.test.app")
        output = "  PID USER PR NI VIRT RES SHR S CPU MEM TIME ARGS\n1234 u0 0 10 1G 100M 50M S 25.5 5.0 0:01 com.test.app\n"
        cpu = monitor._parse_top_for_pid(output, "1234")
        assert cpu == 25.5

    def test_get_cpu_usage_with_mock_adb(self):
        from performance.cpu import CPUMonitor

        adb = MagicMock()
        adb.shell.side_effect = [
            "1234\n",
            "  PID USER PR NI VIRT RES SHR S CPU MEM TIME ARGS\n1234 u0 0 10 1G 100M 50M S 12.0 5.0 0:01 com.test.app\n",
        ]
        monitor = CPUMonitor("dummy", "com.test.app", adb_client=adb)
        assert monitor.get_cpu_usage() == 12.0


class TestMemoryMonitor:
    def test_get_memory_usage_parses_total(self):
        from performance.memory import MemoryMonitor

        adb = MagicMock()
        adb.shell.return_value = "  TOTAL PSS:   204800 kB\n  Java Heap:    51200 kB\n"
        monitor = MemoryMonitor("dummy", "com.test.app", adb_client=adb)
        result = monitor.get_memory_usage()
        assert result["total"] == 200.0
        assert result["java_heap"] == 50.0


class TestFPSMonitor:
    def test_get_fps_resets_before_read(self):
        from performance.fps import FPSMonitor

        adb = MagicMock()
        adb.shell.side_effect = [
            "",
            "Total frames rendered: 60\n50th percentile: 16ms\n",
        ]
        monitor = FPSMonitor("dummy", "com.test.app", adb_client=adb)
        fps = monitor.get_fps()
        assert fps > 0
        assert adb.shell.call_args_list[0][0][0:4] == ("dumpsys", "gfxinfo", "com.test.app", "reset")

    def test_parse_fps_from_percentile(self):
        from performance.fps import FPSMonitor

        monitor = FPSMonitor("dummy", "com.test.app")
        output = "Total frames rendered: 100\n50th percentile: 16.67ms\n"
        assert abs(monitor._parse_fps(output) - 59.99) < 1


class TestPerformanceMonitor:
    def test_default_interval_from_config(self):
        from performance.monitor import PerformanceMonitor
        from settings.config import Config

        config = Config()
        monitor = PerformanceMonitor("d", "com.test", "/tmp/out", config=config)
        assert monitor.interval == config.PERF_MONITOR_INTERVAL

    def test_set_phase(self):
        from performance.monitor import PerformanceMonitor

        monitor = PerformanceMonitor("d", "com.test", "/tmp/out")
        monitor.set_phase("suixinlian")
        assert monitor.get_phase() == "suixinlian"

    def test_leak_requires_growth_threshold(self):
        from performance.monitor import PerformanceMonitor

        monitor = PerformanceMonitor("d", "com.test", "/tmp/out")
        monitor.interval = 3.0
        monitor.mem_leak_window = 5
        monitor.mem_leak_growth = 100.0
        # 小增长不应判泄漏
        for i in range(8):
            monitor.data.append({
                "timestamp": f"t{i}",
                "mem": 100 + i * 0.5,
                "java_heap": 0,
                "native_heap": 0,
                "graphics": 0,
            })
        result = monitor._analyze_memory_leak()
        assert result["suspected"] is False
