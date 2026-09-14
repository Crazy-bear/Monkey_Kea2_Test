# -*- coding: utf-8 -*-
"""
Home Tab — 低频哨兵（表面结构可见）。

只确认 Home 主表面还在，不逐条校验全部入口卡片；
不做「进业务再回 Home」导航；锁其它模块时不抢调度。
"""
from kea2 import precondition, prob, max_tries

from scenarios.base_property import FitnessMirrorPropertyTest


class HomeNavigationTest(FitnessMirrorPropertyTest):

    def _on_home(self):
        return self.home_page().is_home_page_displayed()

    @prob(0.1)
    @max_tries(10)
    @precondition(lambda self: self.explore_or_enter_ready("home", self._on_home))
    def test_home_entry_cards_visible(self):
        self.set_perf_phase("home_entries")
        page = self.home_page()
        if not page.is_home_page_displayed():
            page.ensure_home_surface()
            self.d.sleep(1)
        # 弱抽检：与 is_home_page_displayed 同级，避免六入口全齐误报
        assert page.is_home_page_displayed(), "Home 主表面不可见"
        assert page.is_displayed(page.START_BUTTON), "随心练入口不可见"
        self.finish_module_property()
