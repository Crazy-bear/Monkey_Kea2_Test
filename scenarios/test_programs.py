# -*- coding: utf-8 -*-
"""运动计划场景 — 低频哨兵（列表/筛选可见）。"""
from kea2 import precondition, prob, max_tries

from scenarios.base_property import FitnessMirrorPropertyTest


class ProgramsTest(FitnessMirrorPropertyTest):

    def _on_programs(self):
        return self.programs_page().is_programs_page_displayed()

    @prob(0.1)
    @max_tries(20)
    @precondition(lambda self: self.explore_or_enter_ready("programs", self._on_programs))
    def test_programs_list_visible(self):
        self.set_perf_phase("programs_list")
        page = self.programs_page()
        if not page.is_programs_page_displayed():
            self.home_page().go_to_plan()
            self.d.sleep(2)
        assert page.is_displayed(page.PLAN_LIST), "计划列表不可见"
        assert page.is_displayed(page.SORT_BAR), "分类筛选栏不可见"
        self.finish_module_property()
