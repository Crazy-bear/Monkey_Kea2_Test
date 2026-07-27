# -*- coding: utf-8 -*-
"""Kea2 结果解析测试。"""

import json
import os
import tempfile

from orchestrator.kea2_result_parser import parse_kea2_output, kea2_exit_failed, _extract_violations


class TestKea2ResultParser:
    def test_extract_violations_from_list(self):
        data = {"property_violations": [{"test": "t1", "message": "failed"}]}
        assert len(_extract_violations(data)) == 1

    def test_kea2_exit_failed(self):
        assert kea2_exit_failed(1)
        assert kea2_exit_failed(2)
        assert not kea2_exit_failed(0)

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
