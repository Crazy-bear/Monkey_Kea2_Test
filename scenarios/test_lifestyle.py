# -*- coding: utf-8 -*-
"""
Lifestyle Tab — 低频哨兵（表面结构可见）。

只确认娱乐 Tab 功能区还在，不逐条校验 Games/VS 等入口文案；
不做进退链路；锁其它模块时不抢调度。
"""
from kea2 import precondition, prob, max_tries

from scenarios.base_property import FitnessMirrorPropertyTest


class LifestyleNavigationTest(FitnessMirrorPropertyTest):

    def _on_lifestyle(self):
        return self.lifestyle_page().is_lifestyle_page_displayed()

    @prob(0.1)
    @max_tries(10)
    @precondition(lambda self: self.explore_or_enter_ready("lifestyle", self._on_lifestyle))
    def test_lifestyle_entries_visible(self):
        self.set_perf_phase("lifestyle_entries")
        page = self.lifestyle_page()
        if not page.is_lifestyle_page_displayed():
            page.ensure_lifestyle_surface()
            self.d.sleep(1)
        # 弱抽检：功能列表 + 任一入口即可，避免文案/滚动导致误报 exit 1
        assert page.is_displayed(page.FUNCS_LIST), "Lifestyle 功能列表不可见"
        assert page.has_any_entry(), "Lifestyle 无可见入口"
        self.finish_module_property()
