# -*- coding: utf-8 -*-
"""
个人中心场景稳定性属性测试 — v3.x UI。

定位见 pages/profile_page.py 与 S1Pro_UI/v3.0.0.6858/elements/Profile_elements.md。
"""
from kea2 import precondition, prob, max_tries

from scenarios.base_property import FitnessMirrorPropertyTest


class ProfilePlanTest(FitnessMirrorPropertyTest):

    @prob(0.6)
    @max_tries(3)
    @precondition(lambda self: self.on_home_page())
    def test_profile_entry_stable(self):
        self.set_perf_phase("profile")
        self.home_page().go_to_profile()
        self.d.sleep(2)
        page = self.profile_page()
        assert page.is_profile_page_displayed(), "个人中心页关键元素不可见"
        self.press_back_to_home()

    @prob(0.55)
    @max_tries(3)
    @precondition(lambda self: self.on_home_page())
    def test_profile_menu_visible(self):
        self.set_perf_phase("profile_menu")
        self.home_page().go_to_profile()
        self.d.sleep(2)
        page = self.profile_page()
        for label in page.MENU_LABELS:
            assert page.device(text=label).exists, f"{label} 菜单项不可见"
        self.press_back_to_home()
