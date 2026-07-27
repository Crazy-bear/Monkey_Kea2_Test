# -*- coding: utf-8 -*-
"""report_builder 性能数据加载与分 phase 统计。"""

import json
import os
import tempfile


class TestReportBuilderPerformance:
    def test_load_performance_data_excludes_summary_file(self):
        from orchestrator.report_builder import load_performance_data

        with tempfile.TemporaryDirectory() as tmp:
            perf_dir = os.path.join(tmp, "performance")
            os.makedirs(perf_dir)
            samples = [
                {"timestamp": "t1", "phase": "main", "cpu": 10, "mem": 100, "fps": 60},
                {"timestamp": "t2", "phase": "course", "cpu": 20, "mem": 110, "fps": 58},
            ]
            summary = {"sample_count": 2, "cpu": {"avg": 15}}
            with open(os.path.join(perf_dir, "performance_20260723_170000.json"), "w", encoding="utf-8") as f:
                json.dump(samples, f)
            with open(os.path.join(perf_dir, "performance_summary_20260723_170001.json"), "w", encoding="utf-8") as f:
                json.dump(summary, f)

            performance_data, performance_summary = load_performance_data(perf_dir)
            assert isinstance(performance_data, list)
            assert len(performance_data) == 2
            assert performance_data[0]["phase"] == "main"
            assert performance_summary["sample_count"] == 2

    def test_build_phase_performance_ignores_summary_dict(self):
        from orchestrator.report_builder import build_phase_performance

        summary = {"sample_count": 2, "cpu": {"avg": 15}}
        assert build_phase_performance(summary) == {}

    def test_build_phase_performance_groups_by_phase(self):
        from orchestrator.report_builder import build_phase_performance

        data = [
            {"phase": "main", "cpu": 10, "mem": 100, "fps": 60},
            {"phase": "main", "cpu": 20, "mem": 120, "fps": 55},
            {"phase": "course", "cpu": 30, "mem": 130, "fps": 50},
        ]
        out = build_phase_performance(data)
        assert out["main"]["cpu"]["samples"] == 2
        assert out["course"]["cpu"]["avg"] == 30
