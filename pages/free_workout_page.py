# -*- coding: utf-8 -*-
"""
Free Workout 页 Page Object（AEKE 力量镜 v3.x）。

定位依据：S1Pro_UI/v3.0.0.6858/elements/FreeWorkout_elements.md
"""
from pages.base_page import BasePage


class FreeWorkoutPage(BasePage):
    """随心练 — Free Workout 主页。"""

    PACKAGE = "com.aeke.fitnessmirror"

    BACK_BUTTON = f"{PACKAGE}:id/ivLeftIcon"
    TITLE = f"{PACKAGE}:id/tvTitle"
    START_NOW = f"{PACKAGE}:id/start_now"
    SELECT_MOVE = f"{PACKAGE}:id/select_move"
    TAB_PRESET = f"{PACKAGE}:id/template"
    TAB_CUSTOM = f"{PACKAGE}:id/history"
    ACTION_LIST = f"{PACKAGE}:id/action_list"

    TITLE_TEXT = "Free Workout"

    _ANCHORS = (BACK_BUTTON, START_NOW, SELECT_MOVE, ACTION_LIST)

    def is_free_workout_page_displayed(self):
        hits = sum(1 for loc in self._ANCHORS if self.is_displayed(loc))
        if hits < 2:
            return False
        return self.device(text=self.TITLE_TEXT).exists or self.is_displayed(self.START_NOW)

    def press_back(self):
        if self.is_displayed(self.BACK_BUTTON):
            self.click(self.BACK_BUTTON)
            self.device.sleep(0.5)
            return True
        return False
