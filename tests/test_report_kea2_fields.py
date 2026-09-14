# -*- coding: utf-8 -*-
"""报告 Kea2 字段集成测试。"""

import json
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
            "performance_thresholds": {"cpu": 80, "mem": 550, "fps": 30},
            "memory_leak_analysis": {},
            "kea2": {
                "exit_code": 0,
                "running_minutes": 60,
                "property_violation_count": 0,
                "property_violations": [],
                "lock_modules": ["course"],
                "exploration": {
                    "tested_activities_count": 2,
                    "total_activities_count": 10,
                    "coverage_percent": 20.0,
                    "business_pages_seen": ["Course"],
                    "business_pages_missed": [],
                    "business_pages_modeled_count": 1,
                    "page_sample_count": 5,
                    "page_hits": {"Course": 4, "Home": 1},
                    "lock_modules": ["course"],
                    "in_module_sample_ratio": 0.8,
                    "in_module_sample_percent": 80.0,
                    "in_module_sample_count": 4,
                    "out_module_sample_count": 1,
                    "dwell_ok": True,
                    "dwell_threshold": 0.6,
                    "activities_table": [
                        {
                            "activity": "com.aeke.fitnessmirror.course.CourseListActivity",
                            "count": 4,
                            "business_pages": ["Course"],
                        }
                    ],
                },
            },
            "lock_modules": ["course"],
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
            assert "Kea2" in html or "探索覆盖" in html
            assert "探索覆盖" in html
            assert "CourseListActivity" in html
            assert "模块内停留" in html
            assert "80%" in html
            assert "S1 Pro" in html
            assert "0（成功）" in html

            json_path = os.path.join(tmp, "report.json")
            assert gen.generate_report(data, json_path, "json")
            payload = json.load(open(json_path, encoding="utf-8"))
            assert payload["kea2"]["exit_code_label"] == "0（成功）"
            assert payload["kea2"]["exploration"]["tested_activities_count"] == 2
            assert payload["kea2"]["exploration"]["in_module_sample_ratio"] == 0.8
            assert payload["kea2"]["exploration"]["dwell_ok"] is True
            assert "Course" in payload["kea2"]["exploration"]["business_pages_seen"]

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
            kea2_result={
                "exit_code": 1,
                "exit_code_label": "1（属性违反）",
                "property_violation_count": 2,
                "property_violations": [
                    {"test": "test_x.Y.test_z", "message": "fail×2", "fail": 2, "error": 0}
                ],
                "error_message": "Traceback (most recent call last):",
            },
        )
        final = finalize_report_data(report_data, gen)
        assert final["gate_status"]["level"] == "warn"
        assert final["gate_status"]["passed"] is True
        reasons = "；".join(final["gate_status"]["reasons"])
        assert "Traceback" not in reasons
        assert "属性违反" in reasons or "退出码" in reasons
        assert final.get("executive_verdict")

    def test_main_activity_maps_to_home_in_exploration(self):
        from orchestrator.kea2_result_parser import merge_exploration_coverage

        exp = merge_exploration_coverage(
            {
                "tested_activities": ["com.aeke.fitnessmirror.home.MainActivity"],
                "activity_count_history": {"com.aeke.fitnessmirror.home.MainActivity": 10},
                "tested_activities_count": 1,
                "total_activities_count": 100,
                "coverage_percent": 1.0,
            },
            {"pages_seen": [], "page_hits": {}, "sample_count": 0},
        )
        assert exp["activities_table"][0]["business_pages"] == ["Home"]
