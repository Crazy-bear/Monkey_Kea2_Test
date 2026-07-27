# -*- coding: utf-8 -*-
"""报告 Kea2 字段集成测试。"""

import os
import tempfile

from core.report_generator import ReportGenerator
from orchestrator.report_builder import build_report_data, finalize_report_data


class TestReportKea2Fields:
    def test_html_report_with_kea2_section(self):
        gen = ReportGenerator()
        data = finalize_report_data({
            "test_engine": "kea2",
            "device_id": "d1",
            "package_name": "com.aeke.fitnessmirror",
            "device_version_name": "1.0",
            "firmware_version": "fw",
            "start_time": "t0",
            "end_time": "t1",
            "duration": "1分0秒",
            "seed_value": 1,
            "execution_count": 60,
            "execution_label": "60 分钟",
            "crash_count": 0,
            "crashes": [],
            "log_analysis": {},
            "performance_data": [{"timestamp": "t", "cpu": 10, "mem": 100, "fps": 60, "phase": "main"}],
            "performance_summary": {},
            "performance_thresholds": {"cpu": 80, "mem": 512, "fps": 30},
            "memory_leak_analysis": {},
            "kea2": {
                "exit_code": 0,
                "running_minutes": 60,
                "property_violation_count": 0,
                "property_violations": [],
            },
            "phase_performance": {
                "main": {
                    "cpu": {"avg": 10, "samples": 1},
                    "mem": {"avg": 100, "samples": 1},
                    "fps": {"avg": 60, "samples": 1},
                }
            },
            "details": "ok",
        }, gen)

        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "report.html")
            assert gen.generate_report(data, path, "html")
            html = open(path, encoding="utf-8").read()
            assert "Kea2" in html
            assert "力量镜稳定性测试报告" in html

    def test_gate_status_fail_on_violations(self):
        gen = ReportGenerator()
        report_data = build_report_data(
            __import__("settings.config", fromlist=["Config"]).Config(test_engine="kea2"),
            {"test_engine": "kea2", "start_time": "a", "end_time": "b", "duration": "1分"},
            [],
            {},
            None,
            None,
            None,
            gen,
            kea2_result={"exit_code": 1, "property_violation_count": 2, "property_violations": [{}, {}]},
        )
        final = finalize_report_data(report_data, gen)
        assert final["gate_status"]["passed"] is False
