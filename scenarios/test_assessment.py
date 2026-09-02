# -*- coding: utf-8 -*-
"""
运动测评场景稳定性属性测试 — v3.x UI。

定位见 pages/assessment_page.py 与 S1Pro_UI/v3.0.0.6858/elements/Assessment_elements.md。
"""
from kea2 import precondition, prob, max_tries

from scenarios.base_property import FitnessMirrorPropertyTest


class AssessmentTest(FitnessMirrorPropertyTest):

    @prob(0.65)
    @max_tries(3)
    @precondition(lambda self: self.on_home_page())
    def test_enter_assessment_stable(self):
        self.set_perf_phase("assessment")
        self.home_page().go_to_assessment()
        self.d.sleep(2)
        page = self.assessment_page()
        assert page.is_assessment_page_displayed(), "运动测评页关键元素不可见"
        self.press_back_to_home()

    @prob(0.55)
    @max_tries(3)
    @precondition(lambda self: self.on_home_page())
    def test_assessment_grid_visible(self):
        self.set_perf_phase("assessment_grid")
        self.home_page().go_to_assessment()
        self.d.sleep(2)
        page = self.assessment_page()
        assert page.is_displayed(page.ASSESSMENT_GRID), "测评项目网格不可见"
        assert page.is_displayed(page.START_FULL), "全面测评 Start 按钮不可见"
        self.press_back_to_home()
