# -*- coding: utf-8 -*-
"""widget.block 模块锁相关行为（不依赖真实设备）。"""
import importlib.util
import os
import sys
import types


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WIDGET_BLOCK_PATH = os.path.join(ROOT, "configs", "widget.block.py")


def _load_widget_block(monkeypatch, lock_env):
    """注入假 kea2 后按文件路径加载 widget.block.py。"""
    kea2 = types.ModuleType("kea2")
    kea2_utils = types.ModuleType("kea2.utils")
    kea2_kea = types.ModuleType("kea2.keaUtils")

    class Device:
        pass

    def precondition(fn=None):
        # @precondition(lambda d: ...) → 返回装饰器；勿把条件函数当被装饰函数
        def deco(f):
            return f

        return deco

    kea2_utils.Device = Device
    kea2_kea.precondition = precondition
    monkeypatch.setitem(sys.modules, "kea2", kea2)
    monkeypatch.setitem(sys.modules, "kea2.utils", kea2_utils)
    monkeypatch.setitem(sys.modules, "kea2.keaUtils", kea2_kea)

    if lock_env is None:
        monkeypatch.delenv("KEA2_LOCK_MODULES", raising=False)
    else:
        monkeypatch.setenv("KEA2_LOCK_MODULES", lock_env)

    name = "widget_block_under_test"
    sys.modules.pop(name, None)
    spec = importlib.util.spec_from_file_location(name, WIDGET_BLOCK_PATH)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


class TestWidgetBlockLock:
    def test_no_lock_skips_home_tab_block(self, monkeypatch):
        wb = _load_widget_block(monkeypatch, None)
        assert wb._lock_modules() is None
        assert not wb._locks_modules_without_home()

    def test_course_lock_blocks_home_and_lifestyle_tabs(self, monkeypatch):
        wb = _load_widget_block(monkeypatch, "course")
        assert wb._lock_modules() == {"course"}
        assert wb._locks_modules_without_home()

        class FakeSelector:
            def __init__(self, **kwargs):
                self.kwargs = kwargs

            def exists(self):
                return False

        class FakeDevice:
            def __call__(self, **kwargs):
                return FakeSelector(**kwargs)

        blocked = wb.global_block_widgets(FakeDevice())
        texts = [getattr(s, "kwargs", {}).get("text") for s in blocked]
        rids = [getattr(s, "kwargs", {}).get("resourceId") for s in blocked]
        assert "Home" in texts
        assert "Lifestyle" in texts
        assert any(r and r.endswith("tv_page_home") for r in rids)

    def test_home_in_lock_keeps_home_tab(self, monkeypatch):
        wb = _load_widget_block(monkeypatch, "home,course")
        assert not wb._locks_modules_without_home()

        class FakeDevice:
            def __call__(self, **kwargs):
                return types.SimpleNamespace(kwargs=kwargs, exists=lambda: False)

        blocked = wb.global_block_widgets(FakeDevice())
        texts = [getattr(s, "kwargs", {}).get("text") for s in blocked]
        assert "Home" not in texts
        assert "Lifestyle" in texts

    def test_collapsed_control_root_detection(self, monkeypatch):
        wb = _load_widget_block(monkeypatch, "suixinlian")

        class CollapsedNode:
            exists = True
            info = {"bounds": {"left": 0, "top": 2, "right": 1080, "bottom": 4}}

        class ExpandedNode:
            exists = True
            info = {"bounds": {"left": 0, "top": 0, "right": 1080, "bottom": 1920}}

        class FakeDevice:
            def __init__(self, node):
                self._node = node

            def __call__(self, **kwargs):
                return self._node

        assert wb._control_root_collapsed(FakeDevice(CollapsedNode()))
        assert not wb._control_root_collapsed(FakeDevice(ExpandedNode()))
        assert wb._widget_bounds_hw({"bounds": "[0,2][1080,4]"}) == (1080, 2)
        blocked = wb.block_collapsed_control_root(FakeDevice(CollapsedNode()))
        assert blocked and blocked[0].info["bounds"]["bottom"] == 4

    def test_block_floating_touch_unless_locked(self, monkeypatch):
        wb = _load_widget_block(monkeypatch, "course")
        assert wb._should_block_floating_touch()

        class FakeDevice:
            def __call__(self, **kwargs):
                return types.SimpleNamespace(kwargs=kwargs, exists=False)

        blocked = wb.block_floating_touch_overlay(FakeDevice())
        rids = [getattr(s, "kwargs", {}).get("resourceId") for s in blocked]
        assert any(r and r.endswith("container_touch_2") for r in rids)
        assert any(r and r.endswith("iv_contract_album_img_2") for r in rids)

        wb2 = _load_widget_block(monkeypatch, "floating_touch")
        assert not wb2._should_block_floating_touch()

    def test_always_block_sleep_wallpaper(self, monkeypatch):
        wb = _load_widget_block(monkeypatch, "course")

        class FakeDevice:
            def __call__(self, **kwargs):
                return types.SimpleNamespace(kwargs=kwargs, exists=False)

        blocked = wb.block_device_sleep_and_wallpaper(FakeDevice())
        rids = [getattr(s, "kwargs", {}).get("resourceId") for s in blocked]
        texts = [getattr(s, "kwargs", {}).get("text") for s in blocked]
        assert any(r and r.endswith(":id/sleep") for r in rids)
        assert any(r and r.endswith(":id/screen") for r in rids)
        assert "Sleep" in texts
        assert "Wallpaper" in texts
