# -*- coding: utf-8 -*-
"""
Schedule 页 Page Object（AEKE 力量镜 v3.x）。

定位依据：S1Pro_UI/v3.0.0.6858/elements/Home_CalendarMore_elements.md
"""
from pages.base_page import BasePage


class SchedulePage(BasePage):
    """日程详情 — ScheduleNewActivity。"""

    PACKAGE = "com.aeke.fitnessmirror"

    BACK_BUTTON = f"{PACKAGE}:id/iv_back"
    ADD_WORKOUT = f"{PACKAGE}:id/tv_add"
    WEEK_STATS = f"{PACKAGE}:id/cl_sport_count"
    WEEK_CALENDAR = f"{PACKAGE}:id/cs_week"
    COURSE_LIST = f"{PACKAGE}:id/recycler_course_view"
    CALENDAR_LINK = f"{PACKAGE}:id/tv_to_week_report"

    TITLE_TEXT = "Schedule"
    ADD_WORKOUT_TEXT = "Add Workout"

    _ANCHORS = (BACK_BUTTON, WEEK_STATS, COURSE_LIST)

    def is_schedule_page_displayed(self):
        hits = sum(1 for loc in self._ANCHORS if self.is_displayed(loc))
        if hits < 2:
            return False
        return (
            self.device(text=self.TITLE_TEXT).exists
            or self.device(text=self.ADD_WORKOUT_TEXT).exists
        )

    def press_back(self):
        if self.is_displayed(self.BACK_BUTTON):
            self.click(self.BACK_BUTTON)
            self.device.sleep(0.5)
            return True
        return False
