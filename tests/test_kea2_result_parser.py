# -*- coding: utf-8 -*-
"""Kea2 结果解析测试。"""

import json
import os
import tempfile

from orchestrator.kea2_result_parser import (
    parse_kea2_output,
    kea2_exit_failed,
    format_kea2_exit_code,
    kea2_exit_code_meaning,
    _extract_violations,
    merge_exploration_coverage,
    format_exploration_summary,
    compute_in_module_sample_ratio,
    _extract_coverage_from_html,
)
from orchestrator.module_catalog import MAIN


class TestKea2ResultParser:
    def test_extract_violations_from_list(self):
        data = {"property_violations": [{"test": "t1", "message": "failed"}]}
        assert len(_extract_violations(data)) == 1

    def test_extract_violations_from_kea2_summary_map(self):
        from orchestrator.kea2_result_parser import property_violation_total

        data = {
            "test_lifestyle.LifestyleNavigationTest.test_lifestyle_entries_visible": {
                "kind": "property",
                "precond_satisfied": 100,
                "executed": 6,
                "fail": 6,
                "error": 0,
            },
            "test_assessment.AssessmentTest.test_assessment_grid_visible": {
                "kind": "property",
                "executed": 8,
                "fail": 1,
                "error": 0,
            },
            "test_home.HomeNavigationTest.test_home_entry_cards_visible": {
                "kind": "property",
                "executed": 2,
                "fail": 0,
                "error": 0,
            },
        }
        violations = _extract_violations(data)
        assert len(violations) == 2
        assert property_violation_total(violations) == 7

    def test_sanitize_noisy_traceback(self):
        from orchestrator.kea2_result_parser import sanitize_kea2_error_message

        msg = sanitize_kea2_error_message(
            "Traceback (most recent call last):",
            exit_code=1,
            violations=[{
                "test": "test_lifestyle.X.test_y",
                "message": "fail×2",
                "fail": 2,
                "error": 0,
            }],
        )
        assert "Traceback" not in msg
        assert "属性违反" in msg

    def test_kea2_exit_failed(self):
        assert kea2_exit_failed(1)
        assert kea2_exit_failed(2)
        assert not kea2_exit_failed(0)

    def test_format_kea2_exit_code(self):
        assert kea2_exit_code_meaning(1) == "属性违反"
        assert format_kea2_exit_code(1) == "1（属性违反）"
        assert format_kea2_exit_code(0) == "0（成功）"
        assert format_kea2_exit_code(2) == "2（Crash/ANR）"
        assert format_kea2_exit_code(3) == "3（属性违反 + Crash/ANR）"
        assert format_kea2_exit_code(4) == "4（运行时错误）"

    def test_parse_kea2_output_with_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            result_path = os.path.join(tmp, "result_123.json")
            with open(result_path, "w", encoding="utf-8") as f:
                json.dump({
                    "property_violations": [{"message": "assert failed"}],
                    "crash_detected": False,
                }, f)
            parsed = parse_kea2_output(tmp, 0)
            assert parsed["property_violation_count"] == 1
            assert parsed["result_json_path"] == result_path
            assert parsed["exploration"] is not None

    def test_extract_coverage_from_html_script(self):
        html = """
        <html><script>
        var coverageData = [{
          "testedActivities": [
            "com.aeke.fitnessmirror.home.MainActivity",
            "com.aeke.fitnessmirror.course.CourseListActivity"
          ],
          "activityCountHistory": {
            "com.aeke.fitnessmirror.home.MainActivity": 10,
            "com.aeke.fitnessmirror.course.CourseListActivity": 3
          },
          "totalActivitiesCount": 100,
          "testedActivitiesCount": 2,
          "coverage": 2.0
        }];
        </script></html>
        """
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bug_report.html")
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            cov = _extract_coverage_from_html(path)
            assert cov["tested_activities_count"] == 2
            assert cov["total_activities_count"] == 100
            assert any("MainActivity" in a for a in cov["tested_activities"])

    def test_merge_shared_main_needs_sampler(self):
        act_cov = {
            "tested_activities": [MAIN],
            "tested_activities_count": 1,
            "total_activities_count": 50,
            "activity_count_history": {MAIN: 5},
            "coverage_percent": 2.0,
        }
        page_cov = {
            "pages_seen": ["Home"],
            "page_hits": {"Home": 2},
            "sample_count": 3,
        }
        merged = merge_exploration_coverage(act_cov, page_cov, lock_modules=["home"])
        assert "Home" in merged["business_pages_seen"]
        assert MAIN in merged["tested_activities"]
        row = next(r for r in merged["activities_table"] if "MainActivity" in r["activity"])
        assert row["business_pages"] == ["Home"]

    def test_format_exploration_summary(self):
        text = format_exploration_summary({
            "tested_activities_count": 6,
            "total_activities_count": 180,
            "coverage_percent": 3.33,
            "business_pages_seen": ["Home", "Course"],
            "business_pages_missed": ["Lifestyle"],
            "lock_modules": ["course"],
            "in_module_sample_ratio": 0.75,
            "in_module_sample_percent": 75.0,
            "in_module_sample_count": 15,
            "out_module_sample_count": 5,
            "dwell_ok": True,
        })
        assert "6/180" in text
        assert "Home" in text
        assert "模块内停留" in text
        assert "75.0%" in text
        assert "达标" in text

    def test_in_module_ratio_from_page_hits(self):
        page_cov = {
            "page_hits": {"Course": 8, "Home": 2},
            "sample_count": 10,
        }
        dwell = compute_in_module_sample_ratio(page_cov, ["course"], dwell_threshold=0.6)
        assert dwell["in_module_sample_count"] == 8
        assert dwell["out_module_sample_count"] == 2
        assert dwell["in_module_sample_ratio"] == 0.8
        assert dwell["dwell_ok"] is True

    def test_in_module_ratio_from_samples(self):
        page_cov = {
            "samples": [
                {"page": "Course", "activity": "x.CourseListActivity"},
                {"page": "Home", "activity": MAIN},
                {"page": "Course", "activity": "x.CourseListActivity"},
            ],
            "page_hits": {"Course": 2, "Home": 1},
        }
        dwell = compute_in_module_sample_ratio(page_cov, ["course"])
        assert dwell["in_module_sample_count"] == 2
        assert dwell["out_module_sample_count"] == 1
        assert dwell["dwell_ok"] is True

    def test_in_module_ratio_unlocked_is_none(self):
        dwell = compute_in_module_sample_ratio({"page_hits": {"Home": 3}}, None)
        assert dwell["in_module_sample_ratio"] is None
        assert dwell["dwell_ok"] is None

    def test_merge_includes_dwell_fields(self):
        act_cov = {
            "tested_activities": ["com.aeke.fitnessmirror.course.CourseListActivity"],
            "tested_activities_count": 1,
            "total_activities_count": 50,
            "activity_count_history": {
                "com.aeke.fitnessmirror.course.CourseListActivity": 9,
            },
            "coverage_percent": 2.0,
        }
        page_cov = {
            "pages_seen": ["Course", "Home"],
            "page_hits": {"Course": 9, "Home": 1},
            "sample_count": 10,
        }
        merged = merge_exploration_coverage(act_cov, page_cov, lock_modules=["course"])
        assert merged["in_module_sample_ratio"] == 0.9
        assert merged["dwell_ok"] is True
        assert merged["lock_modules"] == ["course"]
