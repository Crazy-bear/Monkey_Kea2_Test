# -*- coding: utf-8 -*-
"""配置模块单元测试（不依赖设备）。"""

import os
import pytest


class TestConfig:
    """Config 校验与懒加载不阻塞启动。"""

    def test_validate_ok_with_defaults(self):
        from settings.config import Config
        config = Config(test_engine="kea2")
        assert getattr(config, "DEVICE_ID", None) or getattr(Config, "DEVICE_ID", None)
        assert getattr(config, "PACKAGE_NAME", None) or getattr(Config, "PACKAGE_NAME", None)
        ok, errors = config.validate(engine="kea2")
        if getattr(config, "DEVICE_ID", "").strip() and getattr(config, "PACKAGE_NAME", "").strip():
            assert ok, errors
        else:
            assert not ok

    def test_validate_fails_when_empty_device(self):
        from settings.config import Config
        config = Config()
        config.DEVICE_ID = ""
        ok, errors = config.validate()
        assert not ok
        assert any("设备" in e or "ID" in e for e in errors)

    def test_validate_fails_when_events_zero(self):
        from settings.config import Config
        config = Config(test_engine="monkey")
        config.EVENT_COUNT = 0
        ok, errors = config.validate(engine="monkey")
        assert not ok
        assert any("事件" in e or "0" in e for e in errors)

    def test_device_version_name_lazy(self):
        """懒加载：不访问 DeviceVersionName 时不应在 init 时连设备。"""
        from settings.config import Config
        config = Config()
        assert config.device_version_name is None

    def test_reload_updates_config(self, monkeypatch):
        from settings.config import Config
        monkeypatch.setenv("MONKEY_EVENT_COUNT", "500")
        config = Config()
        config.reload()
        assert config.EVENT_COUNT == 500

    def test_get_profiles_default(self):
        from settings.config import Config
        profiles = Config.get_profiles("nonexistent.ini")
        assert "DEFAULT" in profiles

    def test_monkey_timeout_calculation(self):
        from settings.config import Config
        config = Config()
        config.EVENT_COUNT = 100
        config.MONKEY_THROTTLE = 500
        config.MONKEY_TIMEOUT_BUFFER = 60
        assert config.get_monkey_timeout_seconds() == 110
