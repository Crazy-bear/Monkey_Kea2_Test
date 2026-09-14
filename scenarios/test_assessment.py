# -*- coding: utf-8 -*-
"""运动测评场景 — 低频哨兵（宫格可见）。"""
from kea2 import precondition, prob, max_tries

from scenarios.base_property import FitnessMirrorPropertyTest


class AssessmentTest(FitnessMirrorPropertyTest):

    def _on_assessment(self):
        return self.assessment_page().is_assessment_page_displayed()

    @prob(0.1)
    @max_tries(20)
    @precondition(lambda self: self.explore_or_enter_ready("assessment", self._on_assessment))
    def test_assessment_grid_visible(self):
        self.set_perf_phase("assessment_grid")
        page = self.assessment_page()
        if not page.is_assessment_page_displayed():
            self.home_page().go_to_assessment()
            self.d.sleep(2)
        assert page.is_displayed(page.ASSESSMENT_GRID), "测评项目网格不可见"
        assert page.is_displayed(page.START_FULL), "全面测评 Start 按钮不可见"
        self.finish_module_property()
