# -*- coding: utf-8 -*-
"""Kea2 runner 命令组装与预检测试。"""

import os
from unittest.mock import patch, MagicMock

from settings.config import Config


class TestKea2Runner:
    def test_build_kea2_command_blacklist_device_path(self):
        from orchestrator.kea2_runner import (
            build_kea2_command,
            build_discover_args,
            KEA2_DEVICE_ABL_PATH,
        )

        config = Config(test_engine="kea2")
        config.DEVICE_ID = "192.168.1.1:5555"
        config.PACKAGE_NAME = "com.aeke.fitnessmirror"
        config.KEA2_RUNNING_MINUTES = 30
        out_dir = os.path.join(config._project_root(), "outputs", "test_kea2")
        cmd = build_kea2_command(config, out_dir)
        cmd.extend(build_discover_args(config))

        assert "--act-blacklist-file" in cmd
        idx = cmd.index("--act-blacklist-file")
        assert cmd[idx + 1] == KEA2_DEVICE_ABL_PATH
        assert cmd[idx + 2] == "propertytest", "propertytest 不能被 blacklist 参数吞掉"

        abl_local = os.path.join(config._project_root(), "configs", "abl.strings")
        if os.path.isfile(abl_local):
            assert not any(
                p.replace("\\", "/").endswith("configs/abl.strings") for p in cmd
            )

    def test_build_discover_args_single_pattern_uses_discover(self):
        from orchestrator.kea2_runner import build_discover_args

        config = Config(test_engine="kea2")
        config.set_scenario_filter("home")
        discover = build_discover_args(config)
        assert discover[:4] == ["propertytest", "discover", "-s", config.get_scenarios_dir()]
        assert discover[-1] == "test_home.py"

    def test_build_discover_args_multi_pattern_uses_modules(self):
        from orchestrator.kea2_runner import build_discover_args

        config = Config(test_engine="kea2")
        config.set_scenario_filter("home,course,data_center")
        discover = build_discover_args(config)
        assert discover[0] == "propertytest"
        assert "discover" not in discover
        assert "scenarios.test_home" in discover
        assert "scenarios.test_course" in discover
        assert "scenarios.test_data_center" in discover

    def test_build_discover_args_all_uses_single_glob(self):
        from orchestrator.kea2_runner import build_discover_args

        config = Config(test_engine="kea2")
        config.set_scenario_filter("all")
        discover = build_discover_args(config)
        assert discover[-1] == "test_*.py"

    @patch("orchestrator.kea2_runner.generate_kea2_native_report")
    @patch("orchestrator.kea2_runner.validate_kea2_preflight", return_value=(True, ""))
    @patch("orchestrator.kea2_runner.subprocess.Popen")
    def test_run_kea2_streams_output(self, mock_popen, _preflight, _mock_report):
        from orchestrator.kea2_runner import run_kea2

        proc = MagicMock()
        proc.stdout = iter(["line1\n", "ERROR: x\n"])
        proc.wait.return_value = None
        proc.returncode = 0
        mock_popen.return_value = proc

        config = Config(test_engine="kea2")
        out = os.path.join(config._project_root(), "outputs", "test_run_kea2")
        os.makedirs(out, exist_ok=True)
        open(os.path.join(out, "res_test"), "w").close()

        code, err = run_kea2(config, out)
        assert code == 0
        assert err == ""
