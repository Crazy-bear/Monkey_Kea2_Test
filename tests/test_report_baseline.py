# -*- coding: utf-8 -*-
"""报告基线对比与 XML 转义单元测试。"""

import json
import os
import tempfile
import xml.etree.ElementTree as ET


class TestReportBaseline:
    def test_baseline_comparison_detects_regression(self):
        from core.report_generator import ReportGenerator

        gen = ReportGenerator()
        gen.baseline = {"cpu": {"avg": 10, "p95": 15}, "mem": {"avg": 100, "p95": 150}, "fps": {"avg": 55}}
        data = {
            "performance_data": [
                {"cpu": 50, "mem": 200, "fps": 40},
                {"cpu": 55, "mem": 220, "fps": 38},
            ]
        }
        result = gen._apply_baseline_comparison(data)
        assert result["baseline_comparison"]["has_regression"] is True
        assert len(result["baseline_comparison"]["regressions"]) > 0

    def test_load_baseline_from_file(self):
        from core.report_generator import ReportGenerator

        gen = ReportGenerator()
        baseline = {"cpu": {"avg": 20, "p95": 30}}
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "baseline.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(baseline, f)
            loaded = gen.load_baseline(path)
            assert loaded == baseline


class TestEscapeXml:
    def test_escape_xml_all_special_chars(self):
        from core.report_generator import _escape_xml

        raw = 'a & b < c > d " e \' f'
        escaped = _escape_xml(raw)
        assert "&amp;" in escaped
        assert "&lt;" in escaped
        assert "&gt;" in escaped
        assert "&quot;" in escaped
        assert "&apos;" in escaped
        ET.fromstring(f'<svg><text>{escaped}</text></svg>')
