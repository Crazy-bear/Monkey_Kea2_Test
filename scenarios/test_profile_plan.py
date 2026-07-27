# -*- coding: utf-8 -*-
"""个人中心 / 运动计划 / 运动测评场景。"""
from kea2 import precondition, prob, max_tries

from scenarios.base_property import FitnessMirrorPropertyTest


class ProfilePlanTest(FitnessMirrorPropertyTest):

    @prob(0.6)
    @max_tries(3)
    @precondition(lambda self: self.on_main_page())
    def test_profile_entry_stable(self):
        self.set_perf_phase("profile")
        self.main_page().go_to_profile()
        self.d.sleep(2)
        assert self.d(className="android.widget.FrameLayout").exists(timeout=10)
        self.press_back_to_main()

    @prob(0.6)
    @max_tries(3)
    @precondition(lambda self: self.on_main_page())
    def test_plan_entry_stable(self):
        self.set_perf_phase("plan")
        self.main_page().go_to_plan()
        self.d.sleep(2)
        assert self.d(className="android.widget.FrameLayout").exists(timeout=10)
        self.press_back_to_main()

    @prob(0.6)
    @max_tries(3)
    @precondition(lambda self: self.on_main_page())
    def test_assessment_entry_stable(self):
        self.set_perf_phase("assessment")
        self.main_page().go_to_assessment()
        self.d.sleep(2)
        assert self.d(className="android.widget.FrameLayout").exists(timeout=10)
        self.press_back_to_main()
