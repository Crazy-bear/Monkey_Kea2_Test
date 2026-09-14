# -*- coding: utf-8 -*-
"""报告元数据：Unknown 不得挡住设备版本回填。"""

import json
from pathlib import Path

from orchestrator.report_builder import (
    build_report_data,
    first_good_meta,
    is_blank_meta,
    load_report_only_meta,
)


class _FakeConfig:
    DEVICE_ID = "dev-1"
    PACKAGE_NAME = "com.example.app"
    TEST_ENGINE = "kea2"
    EVENT_COUNT = 100
    KEA2_RUNNING_MINUTES = 10
    SEED = "209912312359"
    DeviceVersionName = "9.9.9"
    FirmwareVersion = "FW-REAL"


class _FakeReportGenerator:
    baseline = None


def test_is_blank_meta_treats_unknown():
    assert is_blank_meta("Unknown")
    assert is_blank_meta("N/A")
    assert is_blank_meta("")
    assert not is_blank_meta("3.2.0.7215")


def test_first_good_meta_skips_unknown():
    assert first_good_meta("Unknown", "3.2.0.7215") == "3.2.0.7215"
    assert first_good_meta(None, "Unknown", default="x") == "x"


def test_load_report_only_meta_overrides_unknown(tmp_path, monkeypatch):
    out = tmp_path / "run"
    out.mkdir()
    (out / "logcat.log").write_text("", encoding="utf-8")
    (out / "report.json").write_text(
        json.dumps(
            {
                "device_id": "dev-1",
                "device_version_name": "Unknown",
                "firmware_version": "Unknown",
                "seed_value": "202601010000",
            }
        ),
        encoding="utf-8",
    )
    meta = load_report_only_meta(str(out), config=_FakeConfig(), kea2_result=None)
    assert meta["device_version_name"] == "9.9.9"
    assert meta["firmware_version"] == "FW-REAL"
    # 旧 report 中的 seed 不可信，未写入 kea2_run_meta 时不回填
    assert "seed_value" not in meta or is_blank_meta(meta.get("seed_value"))
    assert meta.get("report_only") is True


def test_load_report_only_meta_keeps_seed_from_run_meta(tmp_path):
    out = tmp_path / "run"
    out.mkdir()
    (out / "logcat.log").write_text("", encoding="utf-8")
    (out / "kea2_run_meta.json").write_text(
        json.dumps({"seed_value": "202609091739", "exit_code": 0}),
        encoding="utf-8",
    )
    (out / "report.json").write_text(
        json.dumps({"seed_value": "209912312359"}),
        encoding="utf-8",
    )
    meta = load_report_only_meta(str(out), config=_FakeConfig(), kea2_result=None)
    assert meta["seed_value"] == "202609091739"


def test_load_report_only_meta_extracts_fastbot_seed(tmp_path):
    out = tmp_path / "run"
    kea2 = out / "kea2" / "res_x"
    kea2.mkdir(parents=True)
    (out / "logcat.log").write_text("", encoding="utf-8")
    (kea2 / "fastbot_x.log").write_text(
        "// Monkey: seed=1789026342304 count=1000\n",
        encoding="utf-8",
    )
    meta = load_report_only_meta(str(out), config=_FakeConfig(), kea2_result=None)
    assert meta["seed_value"] == "1789026342304"


def test_build_report_data_report_only_does_not_invent_seed():
    data = build_report_data(
        _FakeConfig(),
        {
            "test_engine": "kea2",
            "report_only": True,
            "device_version_name": "Unknown",
            "firmware_version": "Unknown",
        },
        [],
        {},
        None,
        None,
        None,
        _FakeReportGenerator(),
        kea2_result=None,
    )
    assert data["device_version_name"] == "9.9.9"
    assert data["firmware_version"] == "FW-REAL"
    assert data["seed_value"] == "N/A"
