# -*- coding: utf-8 -*-
"""主页导航 invariant：各业务入口可见（v3.x Home UI）。"""
from kea2 import precondition, prob, max_tries

from scenarios.base_property import FitnessMirrorPropertyTest


class MainNavigationTest(FitnessMirrorPropertyTest):

    @prob(0.5)
    @max_tries(5)
    @precondition(lambda self: self.on_main_page())
    def test_main_entries_visible(self):
        self.set_perf_phase("main")
        page = self.main_page()
        assert page.is_displayed(page.START_BUTTON), "Free Workout 入口不可见"
        assert page.is_displayed(page.COURSE_BUTTON), "Courses 入口不可见"
        assert page.is_displayed(page.PLAN_BUTTON), "Programs 入口不可见"
