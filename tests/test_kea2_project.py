# -*- coding: utf-8 -*-
"""Kea2 项目初始化与 config 同步规避。"""

import os
import tempfile


class TestKea2ProjectPatch:
    def test_patch_creates_pycache_in_configs(self):
        from orchestrator.kea2_project import _patch_kea2_config_sync_bug

        with tempfile.TemporaryDirectory() as tmp:
            configs = os.path.join(tmp, "configs")
            os.makedirs(configs)
            _patch_kea2_config_sync_bug(configs)
            assert os.path.isdir(os.path.join(configs, "__pycache__"))

    def test_build_kea2_subprocess_env_sets_pythonpath(self):
        from orchestrator.kea2_project import build_kea2_subprocess_env

        with tempfile.TemporaryDirectory() as tmp:
            env = build_kea2_subprocess_env(tmp)
            assert os.path.abspath(tmp) in os.path.abspath(env["PYTHONPATH"])
            assert env["PYTHONDONTWRITEBYTECODE"] == "1"

    def test_scenario_discover_import_with_pythonpath(self):
        """模拟 Kea2 unittest discover 的 import 行为。"""
        import importlib.util
        import sys

        root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        scenarios = os.path.join(root, "scenarios")
        env = os.environ.copy()
        env["PYTHONPATH"] = root
        # 子进程验证（与 kea2 一致）
        code = (
            "import os, sys, importlib.util; "
            f"root=r'{root}'; scenarios=r'{scenarios}'; "
            "sys.path.insert(0, scenarios); "
            "spec=importlib.util.spec_from_file_location('test_course', os.path.join(scenarios,'test_course.py')); "
            "m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); "
            "print('ok')"
        )
        proc = __import__("subprocess").run(
            [sys.executable, "-c", code],
            env=env,
            capture_output=True,
            text=True,
            cwd=root,
        )
        assert proc.returncode == 0, proc.stderr
        assert "ok" in proc.stdout

    def test_ensure_ready_applies_patch(self):
        from orchestrator.kea2_project import ensure_kea2_project_ready

        with tempfile.TemporaryDirectory() as tmp:
            configs = os.path.join(tmp, "configs")
            os.makedirs(configs)
            ok, err = ensure_kea2_project_ready(tmp)
            assert ok is True
            assert err == ""
            assert os.path.isdir(os.path.join(configs, "__pycache__"))
