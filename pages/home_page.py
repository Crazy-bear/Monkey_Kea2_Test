# -*- coding: utf-8 -*-
"""
Home Tab Page Object（S1Pro 力量镜 v3.x）。

定位依据：S1Pro_UI/v3.1.0.7123/elements/Home_elements.md
（兼容旧版 v3.0.0.6858；提醒条态已弱化，默认展示 Today's Effort）
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

    # Today's Effort 数据条（进入 Data Center）
    EFFORT_STRIP = "com.aeke.fitnessmirror:id/hsr_tips"
    EFFORT_ENTRY = "com.aeke.fitnessmirror:id/ll_report"
    EFFORT_INFOS = "com.aeke.fitnessmirror:id/ctl_report_infos"

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

    def go_to_data_center(self):
        """点击 Today's Effort 条进入数据中心详情。"""
        self.ensure_home_surface()
        if self.is_displayed(self.EFFORT_ENTRY):
            self.click(self.EFFORT_ENTRY)
            self.device.sleep(0.8)
            return True
        return False
