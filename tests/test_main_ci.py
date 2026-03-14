# -*- coding: utf-8 -*-
"""主流程 CI 入口测试：--validate-only、--report-only（无需设备）。"""

import os
import sys
import tempfile
import pytest


def test_validate_only_exit_zero(monkeypatch):
    """--validate-only 在配置有效时应退出码 0。"""
    monkeypatch.setattr(sys, "argv", ["main.py", "--validate-only"])
    # 确保有默认配置
    import main
    exit_code = main.main()
    assert exit_code == 0


def test_report_only_from_dir():
    """--report-only 从包含 logcat.log 的目录生成报告。"""
    with tempfile.TemporaryDirectory() as tmp:
        logcat_path = os.path.join(tmp, "logcat.log")
        with open(logcat_path, "w", encoding="utf-8") as f:
            f.write("some log line\n")
        report_path = os.path.join(tmp, "report_ci.html")
        import main
        code = main.run_report_only(tmp, report_path, "html")
        assert code == 0
        assert os.path.isfile(report_path)


def test_report_only_missing_dir():
    """--report-only 目录无 logcat.log 时应返回非 0。"""
    with tempfile.TemporaryDirectory() as tmp:
        import main
        code = main.run_report_only(tmp, None, "html")
        assert code != 0
