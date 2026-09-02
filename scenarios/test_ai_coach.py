# -*- coding: utf-8 -*-
"""
AI Coach 场景稳定性属性测试 — v3.x UI。

定位见 pages/ai_coach_page.py 与 S1Pro_UI/v3.0.0.6858/elements/AICoach_elements.md。
"""
from kea2 import precondition, prob, max_tries

from scenarios.base_property import FitnessMirrorPropertyTest


class AICoachTest(FitnessMirrorPropertyTest):

    @prob(0.65)
    @max_tries(3)
    @precondition(lambda self: self.on_home_page())
    def test_enter_ai_coach_stable(self):
        self.set_perf_phase("ai_coach")
        self.home_page().go_to_ai_coach()
        self.d.sleep(2)
        page = self.ai_coach_page()
        assert page.is_ai_coach_page_displayed(), "AI Coach 页关键元素不可见"
        self.press_back_to_home()

    @prob(0.55)
    @max_tries(3)
    @precondition(lambda self: self.on_home_page())
    def test_ai_coach_start_workout_visible(self):
        self.set_perf_phase("ai_coach_start")
        self.home_page().go_to_ai_coach()
        self.d.sleep(2)
        page = self.ai_coach_page()
        assert page.is_displayed(page.START_WORKOUT), "Start a Workout 按钮不可见"
        assert page.is_displayed(page.PROFILE_CARD), "Profile 卡片不可见"
        self.press_back_to_home()
