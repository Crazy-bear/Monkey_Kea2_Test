# -*- coding: utf-8 -*-
"""
AI Coach 页 Page Object（AEKE 力量镜 v3.x）。

定位依据：S1Pro_UI/v3.0.0.6858/elements/AICoach_elements.md
"""
from pages.base_page import BasePage


class AICoachPage(BasePage):
    """AI Coach 主页 — AiCoachHomeActivity。"""

    PACKAGE = "com.aeke.fitnessmirror"

    BACK_BUTTON = f"{PACKAGE}:id/ivLeftIcon"
    GREETING = f"{PACKAGE}:id/tv_aicoach_greeting"
    START_WORKOUT = f"{PACKAGE}:id/tv_generate_course"
    PROFILE_CARD = f"{PACKAGE}:id/cl_aicoach_profile_card"
    PROFILE_UPDATE = f"{PACKAGE}:id/tv_aicoach_profile_update"

    START_WORKOUT_TEXT = "Start a Workout"

    _ANCHORS = (BACK_BUTTON, GREETING, START_WORKOUT, PROFILE_CARD)

    def is_ai_coach_page_displayed(self):
        hits = sum(1 for loc in self._ANCHORS if self.is_displayed(loc))
        return hits >= 2

    def press_back(self):
        if self.is_displayed(self.BACK_BUTTON):
            self.click(self.BACK_BUTTON)
            self.device.sleep(0.5)
            return True
        return False
