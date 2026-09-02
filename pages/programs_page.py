# -*- coding: utf-8 -*-
"""
Programs 页 Page Object（AEKE 力量镜 v3.x）。

定位依据：S1Pro_UI/v3.0.0.6858/elements/Programs_elements.md
"""
from pages.base_page import BasePage


class ProgramsPage(BasePage):
    """运动计划列表 — AllPlanActivity。"""

    PACKAGE = "com.aeke.fitnessmirror"

    BACK_BUTTON = f"{PACKAGE}:id/ivLeftIcon"
    TITLE = f"{PACKAGE}:id/tvTitle"
    MY_PLAN = f"{PACKAGE}:id/tv_title_right_txt"
    SORT_BAR = f"{PACKAGE}:id/rl_select_sort"
    PLAN_LIST = f"{PACKAGE}:id/rv_plan_list"

    TITLE_TEXT = "Programs"
    MY_PLAN_TEXT = "My plan"

    _ANCHORS = (BACK_BUTTON, PLAN_LIST, SORT_BAR)

    def is_programs_page_displayed(self):
        hits = sum(1 for loc in self._ANCHORS if self.is_displayed(loc))
        if hits < 2:
            return False
        return self.device(text=self.TITLE_TEXT).exists or self.is_displayed(self.PLAN_LIST)

    def press_back(self):
        if self.is_displayed(self.BACK_BUTTON):
            self.click(self.BACK_BUTTON)
            self.device.sleep(0.5)
            return True
        return False
