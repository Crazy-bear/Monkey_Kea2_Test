# -*- coding: utf-8 -*-
"""
悬浮 Touch 场景稳定性属性测试 — v3.x UI。

定位见 pages/floating_touch_page.py 与
S1Pro_UI/v3.0.0.6858/elements/FloatingTouch_elements.md、TouchMenu_elements.md。
"""
from kea2 import precondition, prob, max_tries

from scenarios.base_property import FitnessMirrorPropertyTest


class FloatingTouchTest(FitnessMirrorPropertyTest):

    @prob(0.55)
    @max_tries(5)
    @precondition(lambda self: self.on_home_page())
    def test_floating_touch_fab_visible(self):
        self.set_perf_phase("floating_touch_fab")
        page = self.floating_touch_page()
        assert page.ensure_fab_visible(), "悬浮 Touch 球不可见"

    @prob(0.5)
    @max_tries(3)
    @precondition(lambda self: self.floating_touch_page().ensure_fab_visible())
    def test_open_touch_menu(self):
        self.set_perf_phase("floating_touch_open")
        page = self.floating_touch_page()
        assert page.open_menu(), "无法展开悬浮 Touch 菜单"
        assert page.menu_tools_visible(), "底部工具栏项不可见"
        assert page.music_panel_visible(), "音乐控制区不可见"
        assert page.close_menu(), "无法收起悬浮 Touch 菜单"

    @prob(0.45)
    @max_tries(3)
    @precondition(lambda self: self.floating_touch_page().ensure_fab_visible())
    def test_touch_menu_toolbar_entry(self):
        self.set_perf_phase("floating_touch_toolbar")
        page = self.floating_touch_page()
        assert page.open_menu(), "无法展开悬浮 Touch 菜单"
        assert page.click_tool(page.TOOLBAR), "Toolbar 不可点击"
        self.d.sleep(1.5)
        assert self.d(className="android.widget.FrameLayout").exists(timeout=10), (
            "Toolbar 进入后无可用界面"
        )
        assert self.press_back_to_home(), "Toolbar 返回 Home 失败"
        page.close_menu()
