# -*- coding: utf-8 -*-
"""
Course 页 Page Object（AEKE 力量镜 v3.x）。

定位依据：S1Pro_UI/v3.0.0.6858/elements/Course_elements.md
"""
from pages.base_page import BasePage


class CoursePage(BasePage):
    """精品课程列表 — CourseListActivity。"""

    PACKAGE = "com.aeke.fitnessmirror"

    BACK_BUTTON = f"{PACKAGE}:id/iv_back"
    TITLE = f"{PACKAGE}:id/tv_title"
    FAVORITES = f"{PACKAGE}:id/tv_title_right_txt"
    FILTER_BAR = f"{PACKAGE}:id/fl_filter_first"
    COURSE_LIST = f"{PACKAGE}:id/rv_list"
    COURSE_ITEM = f"{PACKAGE}:id/rl_container"

    TITLE_TEXT = "Courses"
    FAVORITES_TEXT = "Favorites"

    _ANCHORS = (BACK_BUTTON, COURSE_LIST, FILTER_BAR)

    def is_course_page_displayed(self):
        hits = sum(1 for loc in self._ANCHORS if self.is_displayed(loc))
        if hits < 2:
            return False
        title = self.device(text=self.TITLE_TEXT)
        return title.exists or self.is_displayed(self.COURSE_LIST)

    def press_back(self):
        if self.is_displayed(self.BACK_BUTTON):
            self.click(self.BACK_BUTTON)
            self.device.sleep(0.5)
            return True
        return False
