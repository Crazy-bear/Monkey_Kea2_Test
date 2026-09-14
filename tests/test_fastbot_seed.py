# -*- coding: utf-8 -*-
"""Fastbot seed 提取。"""

from orchestrator.kea2_result_parser import extract_fastbot_seed


def test_extract_fastbot_seed_from_log(tmp_path):
    kea2 = tmp_path / "kea2" / "res_1"
    kea2.mkdir(parents=True)
    (kea2 / "fastbot_1.log").write_text(
        "[Fastbot][2026-09-09 17:39:37.627] // Monkey: seed=1789026342304 count=1000\n",
        encoding="utf-8",
    )
    assert extract_fastbot_seed(str(tmp_path / "kea2")) == "1789026342304"


def test_extract_fastbot_seed_missing(tmp_path):
    kea2 = tmp_path / "kea2"
    kea2.mkdir()
    assert extract_fastbot_seed(str(kea2)) is None
