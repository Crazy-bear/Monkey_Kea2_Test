# -*- coding: utf-8 -*-
"""AI Coach 场景 — 低频哨兵（开始训练入口可见）。"""
from kea2 import precondition, prob, max_tries

from scenarios.base_property import FitnessMirrorPropertyTest


class AICoachTest(FitnessMirrorPropertyTest):

    def _on_ai_coach(self):
        return self.ai_coach_page().is_ai_coach_page_displayed()

    @prob(0.1)
    @max_tries(20)
    @precondition(lambda self: self.explore_or_enter_ready("ai_coach", self._on_ai_coach))
    def test_ai_coach_start_workout_visible(self):
        self.set_perf_phase("ai_coach_start")
        page = self.ai_coach_page()
        if not page.is_ai_coach_page_displayed():
            self.home_page().go_to_ai_coach()
            self.d.sleep(2)
        assert page.is_displayed(page.START_WORKOUT), "Start a Workout 按钮不可见"
        assert page.is_displayed(page.PROFILE_CARD), "Profile 卡片不可见"
        self.finish_module_property()
