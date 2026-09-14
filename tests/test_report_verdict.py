# -*- coding: utf-8 -*-
"""报告裁决层单测。"""

from orchestrator.report_verdict import (
    build_executive_verdict,
    compute_gate_status,
    inspect_kea2_bug_report,
    sanitize_performance_samples,
)


class TestReportVerdict:
    def test_sanitize_invalid_fps(self):
        rows = sanitize_performance_samples([
            {"fps": 0.20202020202020202, "fps_low": True, "cpu": 10, "mem": 500},
            {"fps": 45.0, "fps_low": False, "cpu": 10, "mem": 500},
        ], thresholds={"fps": 30})
        assert rows[0]["fps_invalid"] is True
        assert rows[0]["fps_low"] is False
        assert rows[1]["fps_invalid"] is False

    def test_gate_property_is_warn_not_fail(self):
        gate = compute_gate_status({
            "crash_count": 0,
            "kea2": {
                "exit_code": 1,
                "exit_code_label": "1（属性违反）",
                "property_violation_count": 2,
                "property_violations": [
                    {"test": "t.a", "message": "fail×2", "fail": 2, "error": 0}
                ],
                "error_message": "",
            },
            "path_performance": [],
            "memory_leak_analysis": {},
            "baseline_comparison": {},
        })
        assert gate["level"] == "warn"
        assert gate["passed"] is True
        assert gate["reasons_soft"]
        assert not gate["reasons_hard"]

    def test_gate_crash_is_fail(self):
        gate = compute_gate_status({
            "crash_count": 1,
            "kea2": {"exit_code": 0, "property_violation_count": 0, "property_violations": []},
            "path_performance": [],
            "memory_leak_analysis": {},
        })
        assert gate["level"] == "fail"
        assert gate["passed"] is False

    def test_executive_verdict(self):
        data = {
            "crash_count": 0,
            "gate_status": {
                "level": "warn",
                "reasons_hard": [],
                "reasons_soft": ["属性违反 1 次"],
            },
            "kea2": {"property_violation_count": 1},
            "path_problem_verdict": {"headlines": []},
            "path_investigations": [
                {"actions": ["模块锁复跑：python main.py --scenarios home"]}
            ],
        }
        v = build_executive_verdict(data)
        assert v["level"] == "warn"
        assert "告警" in v["stability"] or "可跑通" in v["stability"]
        assert "home" in v["next_step"]

    def test_bug_report_cannot_replace(self):
        info = inspect_kea2_bug_report(None)
        assert info["can_replace_unified_report"] is False
        assert info["role"] == "complement"
