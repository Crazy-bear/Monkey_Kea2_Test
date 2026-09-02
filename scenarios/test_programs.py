# -*- coding: utf-8 -*-
"""
运动计划场景稳定性属性测试 — v3.x UI。

定位见 pages/programs_page.py 与 S1Pro_UI/v3.0.0.6858/elements/Programs_elements.md。
"""
from kea2 import precondition, prob, max_tries

from scenarios.base_property import FitnessMirrorPropertyTest


class ProgramsTest(FitnessMirrorPropertyTest):

    @prob(0.65)
    @max_tries(3)
    @precondition(lambda self: self.on_home_page())
    def test_enter_programs_stable(self):
        self.set_perf_phase("programs")
        self.home_page().go_to_plan()
        self.d.sleep(2)
        page = self.programs_page()
        assert page.is_programs_page_displayed(), "运动计划页关键元素不可见"
        self.press_back_to_home()

    @prob(0.55)
    @max_tries(3)
    @precondition(lambda self: self.on_home_page())
    def test_programs_list_visible(self):
        self.set_perf_phase("programs_list")
        self.home_page().go_to_plan()
        self.d.sleep(2)
        page = self.programs_page()
        assert page.is_displayed(page.PLAN_LIST), "计划列表不可见"
        assert page.is_displayed(page.SORT_BAR), "分类筛选栏不可见"
        self.press_back_to_home()
