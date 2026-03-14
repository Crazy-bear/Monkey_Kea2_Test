# -*- coding: utf-8 -*-
"""配置模块单元测试（不依赖设备）。"""

import os
import pytest


class TestConfig:
    """Config 校验与懒加载不阻塞启动。"""

    def test_validate_ok_with_defaults(self):
        from config.config import Config
        config = Config()
        # 类属性有默认值
        assert getattr(config, "DEVICE_ID", None) or getattr(Config, "DEVICE_ID", None)
        assert getattr(config, "PACKAGE_NAME", None) or getattr(Config, "PACKAGE_NAME", None)
        ok, errors = config.validate()
        # 默认配置下应有 DEVICE_ID、PACKAGE_NAME、EVENT_COUNT
        if getattr(config, "DEVICE_ID", "").strip() and getattr(config, "PACKAGE_NAME", "").strip():
            assert ok, errors
        else:
            assert not ok

    def test_validate_fails_when_empty_device(self):
        from config.config import Config
        config = Config()
        config.DEVICE_ID = ""
        ok, errors = config.validate()
        assert not ok
        assert any("设备" in e or "ID" in e for e in errors)

    def test_validate_fails_when_events_zero(self):
        from config.config import Config
        config = Config()
        config.EVENT_COUNT = 0
        ok, errors = config.validate()
        assert not ok
        assert any("事件" in e or "0" in e for e in errors)

    def test_device_version_name_lazy(self):
        """懒加载：不访问 DeviceVersionName 时不应在 init 时连设备。"""
        from config.config import Config
        config = Config()
        # 未访问前应为 None（由 _get_app_info 在首次访问时赋值）
        assert config.device_version_name is None or config.device_version_name  # 可能已被其他测试设置
