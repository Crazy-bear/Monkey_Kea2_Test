# -*- coding: utf-8 -*-
"""LogcatHandler 崩溃检测单元测试（无需设备）。"""

import os
import tempfile


SAMPLE_LOG = """
03-17 10:00:01.123  1234  5678 E AndroidRuntime: FATAL EXCEPTION: main
03-17 10:00:01.124  1234  5678 E AndroidRuntime: Process: com.aeke.fitnessmirror, PID: 1234
03-17 10:00:01.125  1234  5678 E AndroidRuntime: java.lang.NullPointerException: test crash
03-17 10:00:01.126  1234  5678 E AndroidRuntime:     at com.aeke.fitnessmirror.MainActivity.onCreate(MainActivity.java:42)
03-17 10:00:02.000  1234  5678 W System.err: java.io.IOException: network timeout
03-17 10:00:03.000  1234  5678 D SomeTag: normal debug line with Error in message
03-17 10:00:04.000  1234  5678 E ActivityManager: ANR in com.aeke.fitnessmirror
"""


class TestLogcatHandler:
    def test_extract_crash_events_deduplicates_stack(self):
        from core.logcat_handler import extract_crash_events

        events = extract_crash_events(SAMPLE_LOG.splitlines(), "com.aeke.fitnessmirror")
        assert len(events) >= 2
        categories = {e["category"] for e in events}
        assert "NullPointerException" in categories or "Other" in categories
        assert "ANR" in categories

    def test_detect_crashes_ignores_generic_error_lines(self):
        from core.logcat_handler import LogcatHandler
        from settings.config import Config

        with tempfile.TemporaryDirectory() as tmp:
            log_path = os.path.join(tmp, "logcat.log")
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(SAMPLE_LOG)

            handler = LogcatHandler(Config())
            crashes = handler.detect_crashes(log_path)
            assert isinstance(crashes, list)
            assert len(crashes) < 10
            messages = " ".join(c["message"] for c in crashes)
            assert "FATAL EXCEPTION" in messages or "ANR" in messages

    def test_analyze_logs_returns_event_count(self):
        from core.logcat_handler import LogcatHandler
        from settings.config import Config

        with tempfile.TemporaryDirectory() as tmp:
            log_path = os.path.join(tmp, "logcat.log")
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(SAMPLE_LOG)

            handler = LogcatHandler(Config())
            result = handler.analyze_logs(log_path)
            assert "total_crashes" in result
            assert result["total_crashes"] == len(handler.detect_crashes(log_path))

    def test_ignore_libprocessgroup_false_positive(self):
        from core.logcat_handler import extract_crash_events

        lines = [
            "07-23 16:40:03.591   672   722 W libprocessgroup: SetCgroup::ExecuteForProcess: failed to open /dev/stune/background/cgroup.procs",
            "07-23 16:40:02.626  3933  3933 I app_process: System.exit called, status: 0",
        ]
        events = extract_crash_events(lines)
        assert events == []
