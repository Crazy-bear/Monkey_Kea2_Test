# -*- coding: utf-8 -*-
"""报告生成模块单元测试。"""

import os
import tempfile
import pytest


class TestReportGenerator:
    def test_normalize_performance_data_none(self):
        from core.report_generator import ReportGenerator
        gen = ReportGenerator()
        assert gen._normalize_performance_data(None) is None

    def test_normalize_performance_data_empty_list(self):
        from core.report_generator import ReportGenerator
        gen = ReportGenerator()
        assert gen._normalize_performance_data([]) is None

    def test_normalize_performance_data_valid_list(self):
        from core.report_generator import ReportGenerator
        gen = ReportGenerator()
        data = [
            {"timestamp": "2025-01-01 12:00:00", "cpu": 10.5, "mem": 100, "fps": 30},
            {"timestamp": "2025-01-01 12:01:00", "cpu": 20, "mem": 150},
        ]
        out = gen._normalize_performance_data(data)
        assert out is not None
        assert len(out) == 2
        assert out[0]["cpu"] == 10.5 and out[0]["mem"] == 100 and out[0]["fps"] == 30
        assert out[1]["fps"] == 0  # 缺失补 0

    def test_generate_json_report(self):
        from core.report_generator import ReportGenerator
        gen = ReportGenerator()
        data = {
            "device_id": "test_device",
            "package_name": "com.test.app",
            "device_version_name": "1.0",
            "start_time": "2025-01-01 10:00:00",
            "end_time": "2025-01-01 11:00:00",
            "duration": "1小时0分0秒",
            "seed_value": 12345,
            "execution_count": 100,
            "crash_count": 0,
            "crashes": [],
            "log_analysis": {"analysis_conclusion": "无崩溃", "crash_categories": {}, "total_crashes": 0, "crash_details": []},
            "performance_data": [{"timestamp": "t1", "cpu": 5, "mem": 50, "fps": 60}],
            "details": "测试",
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "report.json")
            ok = gen.generate_report(data, path, "json")
            assert ok
            assert os.path.isfile(path)
            import json
            with open(path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            assert loaded["device_id"] == "test_device"
            assert loaded["crash_count"] == 0
            assert isinstance(loaded.get("performance_data"), list)

    def test_generate_html_report_no_template_dir(self):
        """无外部模板时使用内置模板生成 HTML。"""
        from core.report_generator import ReportGenerator
        gen = ReportGenerator()
        data = {
            "device_id": "test",
            "package_name": "com.test",
            "device_version_name": "1.0",
            "start_time": "2025-01-01 10:00:00",
            "end_time": "2025-01-01 11:00:00",
            "duration": "1小时",
            "seed_value": 1,
            "execution_count": 10,
            "crash_count": 0,
            "crashes": [],
            "log_analysis": None,
            "performance_data": None,
            "details": "测试",
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "report.html")
            ok = gen.generate_html_report(data, path)
            assert ok
            assert os.path.isfile(path)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            assert "Monkey" in content or "测试" in content
            assert "test" in content
