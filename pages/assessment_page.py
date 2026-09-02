# -*- coding: utf-8 -*-
"""
Assessment 页 Page Object（AEKE 力量镜 v3.x）。

定位依据：S1Pro_UI/v3.0.0.6858/elements/Assessment_elements.md
"""
from pages.base_page import BasePage


class AssessmentPage(BasePage):
    """运动测评主页 — AssessmentHomeActivity。"""

    PACKAGE = "com.aeke.fitnessmirror"

    BACK_BUTTON = f"{PACKAGE}:id/btn_back"
    GENERATE_PLAN = f"{PACKAGE}:id/btn_generate_plan"
    HISTORY_REPORT = f"{PACKAGE}:id/btn_history"
    FULL_ASSESSMENT_TITLE = f"{PACKAGE}:id/tv_title"
    START_FULL = f"{PACKAGE}:id/btn_full_assessment"
    ASSESSMENT_GRID = f"{PACKAGE}:id/recycler_view_assessments"
    TIPS_PANEL = f"{PACKAGE}:id/layout_tips"

    FULL_TITLE_TEXT = "Full Assessment"
    START_TEXT = "Start"

    _ANCHORS = (BACK_BUTTON, ASSESSMENT_GRID, START_FULL)

    def is_assessment_page_displayed(self):
        hits = sum(1 for loc in self._ANCHORS if self.is_displayed(loc))
        if hits < 2:
            return False
        return (
            self.device(text=self.FULL_TITLE_TEXT).exists
            or self.is_displayed(self.ASSESSMENT_GRID)
        )

    def press_back(self):
        if self.is_displayed(self.BACK_BUTTON):
            self.click(self.BACK_BUTTON)
            self.device.sleep(0.5)
            return True
        return False
