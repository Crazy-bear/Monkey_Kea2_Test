# -*- coding: utf-8 -*-
"""ADBClient 单元测试（不依赖真实设备）。"""

import pytest


class TestADBClient:
    def test_init_device_id(self):
        from core.adb_client import ADBClient
        client = ADBClient(device_id="192.168.1.1:5555")
        assert client.device_id == "192.168.1.1:5555"

    def test_launch_app_requires_device_id(self):
        from core.adb_client import ADBClient
        client = ADBClient(device_id=None)
        out, err = client.launch_app("com.test.app")
        assert "device_id not set" in err or "not set" in err

    def test_run_command_capture_output(self):
        """run_command(capture_output=True) 应返回 (stdout, stderr)，且使用 shell=False。"""
        from core.adb_client import ADBClient
        client = ADBClient(device_id="dummy")
        # 执行一个必然存在的命令（如 adb version）以验证 shell=False 可用
        import sys
        if sys.platform == "win32":
            cmd = ["cmd", "/c", "echo", "ok"]
        else:
            cmd = ["echo", "ok"]
        stdout, stderr = client.run_command(cmd, capture_output=True)
        assert "ok" in stdout or stdout.strip() == "ok"

    def test_get_connected_devices_returns_list(self):
        from core.adb_client import ADBClient
        client = ADBClient()
        devices = client.get_connected_devices()
        assert isinstance(devices, list)
