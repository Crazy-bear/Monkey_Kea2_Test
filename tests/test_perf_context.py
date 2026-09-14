# -*- coding: utf-8 -*-
"""性能路径对齐与聚合。"""

from orchestrator.perf_context import (
    annotate_performance_with_coverage,
    build_anomaly_hotspots,
    build_path_performance,
)
from orchestrator.report_builder import attach_path_performance


class TestPerfContext:
    def test_asof_join_assigns_page(self):
        perf = [
            {"timestamp": "2026-09-11 16:55:10", "cpu": 10, "mem": 500, "fps": 60},
            {"timestamp": "2026-09-11 16:55:40", "cpu": 90, "mem": 520, "fps": 20,
             "cpu_exceed": True, "fps_low": True},
        ]
        cov = [
            {"timestamp": "2026-09-11 16:55:00", "page": "Home", "activity": "MainActivity"},
            {"timestamp": "2026-09-11 16:55:30", "page": "Course", "activity": "CourseListActivity"},
        ]
        out = annotate_performance_with_coverage(perf, cov)
        assert out[0]["page"] == "Home"
        assert out[0]["path"] == "Home"
        assert out[1]["page"] == "Course"
        assert out[1]["path"] == "Course"

    def test_path_performance_ranks_by_anomaly(self):
        rows = [
            {"path": "Home", "page": "Home", "cpu": 10, "mem": 500, "fps": 60,
             "cpu_exceed": False, "mem_exceed": False, "fps_low": False},
            {"path": "Course", "page": "Course", "cpu": 90, "mem": 520, "fps": 20,
             "cpu_exceed": True, "mem_exceed": False, "fps_low": True},
            {"path": "Course", "page": "Course", "cpu": 95, "mem": 530, "fps": 18,
             "cpu_exceed": True, "mem_exceed": False, "fps_low": True},
        ]
        ranked = build_path_performance(rows)
        assert ranked[0]["path"] == "Course"
        assert ranked[0]["risk_level"] in ("critical", "warn", "watch")
        assert ranked[0]["primary_issue"]

    def test_path_verdict_highlights_home_fps(self):
        from orchestrator.perf_context import build_path_problem_verdict, build_path_investigations

        rows = []
        for _ in range(20):
            rows.append({
                "path": "Home", "page": "Home", "cpu": 20, "mem": 560, "fps": 5,
                "cpu_exceed": False, "mem_exceed": True, "fps_low": True,
            })
        for _ in range(20):
            rows.append({
                "path": "未识别", "cpu": 20, "mem": 560, "fps": 5,
                "cpu_exceed": False, "mem_exceed": True, "fps_low": True,
            })
        paths = build_path_performance(rows)
        verd = build_path_problem_verdict(paths)
        assert verd["headlines"]
        assert verd["headlines"][0]["path"] == "Home"
        assert verd["mem_threshold_noisy"] is True
        inv = build_path_investigations(paths)
        assert inv and inv[0]["path"] == "Home"
        assert any("scenarios home" in a for a in inv[0]["actions"])

    def test_anomaly_hotspots(self):
        rows = [
            {"timestamp": "t1", "path": "Home", "cpu": 10, "mem": 500, "fps": 60},
            {"timestamp": "t2", "path": "Course", "page": "Course",
             "activity": "com.aeke.CourseListActivity",
             "cpu": 90, "mem": 520, "fps": 20,
             "cpu_exceed": True, "fps_low": True},
        ]
        hot = build_anomaly_hotspots(rows)
        assert len(hot) == 1
        assert hot[0]["path"] == "Course"
        assert "CPU超标" in hot[0]["flag_text"]
        assert hot[0]["activity_short"] == "CourseListActivity"

    def test_attach_path_performance_on_report(self):
        report = {
            "performance_data": [
                {"timestamp": "2026-09-11 16:55:10", "phase": "default",
                 "cpu": 80, "mem": 600, "fps": 10,
                 "cpu_exceed": False, "mem_exceed": True, "fps_low": True},
            ]
        }
        cov = [{"timestamp": "2026-09-11 16:55:00", "page": "Programs",
                "activity": "AllPlanActivity"}]
        attach_path_performance(report, coverage_samples=cov)
        assert report["path_performance"][0]["path"] == "Programs"
        assert report["path_investigations"]
        assert report["perf_anomaly_hotspots"] == []
        assert report.get("perf_anomaly_hotspots_debug") is not None
