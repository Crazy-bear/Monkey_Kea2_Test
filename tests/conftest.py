# -*- coding: utf-8 -*-
"""单元测试全局夹具：保证用例不连真实设备。"""

import pytest


@pytest.fixture(autouse=True)
def stub_device_probes(monkeypatch):
    """
    Config.DeviceVersionName / FirmwareVersion 是懒加载属性，首次读取会 u2.connect + adb shell。
    无设备的 CI 节点上每次要等到超时才退回 Unknown。
    """
    from settings.config import Config

    monkeypatch.setattr(
        Config, "DeviceVersionName", property(lambda self: "test-app-version")
    )
    monkeypatch.setattr(
        Config, "FirmwareVersion", property(lambda self: "test-firmware")
    )
