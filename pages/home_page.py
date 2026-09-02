# -*- coding: utf-8 -*-
"""
Home Tab Page Object（AEKE 力量镜 v3.x）。

定位依据：S1Pro_UI/v3.0.0.6858/elements/Home_elements.md
"""
from pages.main_activity_page import MainActivityPage


class HomePage(MainActivityPage):
    """首页 Tab — Free Workout / Courses / Programs 等入口。"""

    START_BUTTON = "com.aeke.fitnessmirror:id/grf_free_traing"
    AI_COACH_BUTTON = "com.aeke.fitnessmirror:id/grf_ai_coach"
    COURSE_BUTTON = "com.aeke.fitnessmirror:id/grf_all_course"
    ASSESSMENT_BUTTON = "com.aeke.fitnessmirror:id/grf_evaluation"
    PLAN_BUTTON = "com.aeke.fitnessmirror:id/grf_sports_plan"
    CALENDAR_MORE = "com.aeke.fitnessmirror:id/iv_more"
    WEEK_CALENDAR = "com.aeke.fitnessmirror:id/tl_days"
    BANNER_AREA = "com.aeke.fitnessmirror:id/hsb_week"

    _HOME_ANCHORS = (
        MainActivityPage.MAIN_TITLE_BAR,
        START_BUTTON,
        MainActivityPage.HOME_TAB,
    )

    def is_home_page_displayed(self):
        hits = sum(1 for loc in self._HOME_ANCHORS if self.is_displayed(loc))
        return hits >= 2

    def ensure_home_surface(self, max_panel_dismiss=3):
        self._dismiss_overlays(max_panel_dismiss)
        self.switch_to_home_tab()
        return self.is_home_page_displayed()

    def go_to_suixinlian(self):
        self.switch_to_home_tab()
        self.click(self.START_BUTTON)

    def go_to_jingpin_course(self):
        self.switch_to_home_tab()
        self.click(self.COURSE_BUTTON)

    def go_to_plan(self):
        self.switch_to_home_tab()
        self.click(self.PLAN_BUTTON)

    def go_to_assessment(self):
        self.switch_to_home_tab()
        self.click(self.ASSESSMENT_BUTTON)

    def go_to_ai_coach(self):
        self.switch_to_home_tab()
        self.click(self.AI_COACH_BUTTON)

    def go_to_calendar_more(self):
        self.switch_to_home_tab()
        self.click(self.CALENDAR_MORE)
