# -*- coding: utf-8 -*-
"""
Home Tab 专项属性测试 — v3.x UI。

定位见 pages/home_page.py 与 S1Pro_UI/v3.0.0.6858/elements/Home_elements.md。
"""
from kea2 import precondition, prob, max_tries

from scenarios.base_property import FitnessMirrorPropertyTest


class HomeNavigationTest(FitnessMirrorPropertyTest):

    def _assert_enter_and_return(self, navigate, phase, label):
        self.set_perf_phase(phase)
        navigate()
        self.d.sleep(2)
        assert self.d(className="android.widget.FrameLayout").exists(timeout=10), (
            f"{label} 进入后无可用界面"
        )
        assert self.press_back_to_home(), f"{label} 返回 Home 失败"

    @prob(0.6)
    @max_tries(5)
    @precondition(lambda self: self.on_home_page())
    def test_home_tab_visible(self):
        self.set_perf_phase("home_tab")
        shell = self.home_page()
        assert shell.is_displayed(shell.HOME_TAB), "Home Tab 不可见"
        assert shell.is_displayed(shell.MAIN_TITLE_BAR), "顶栏不可见"

    @prob(0.6)
    @max_tries(5)
    @precondition(lambda self: self.on_home_page())
    def test_home_entry_cards_visible(self):
        self.set_perf_phase("home_entries")
        page = self.home_page()
        checks = (
            (page.START_BUTTON, "随心练 / Free Workout"),
            (page.AI_COACH_BUTTON, "AI Coach"),
            (page.COURSE_BUTTON, "精品课程 / Courses"),
            (page.ASSESSMENT_BUTTON, "运动测评 / Assessment"),
            (page.PLAN_BUTTON, "运动计划 / Programs"),
            (page.PROFILE_BUTTON, "个人中心 / 头像"),
        )
        for locator, label in checks:
            assert page.is_displayed(locator), f"{label} 入口不可见"

    @prob(0.55)
    @max_tries(3)
    @precondition(lambda self: self.on_home_page())
    def test_enter_suixinlian_and_return(self):
        page = self.home_page()
        self._assert_enter_and_return(page.go_to_suixinlian, "home_suixinlian", "随心练")

    @prob(0.55)
    @max_tries(3)
    @precondition(lambda self: self.on_home_page())
    def test_enter_ai_coach_and_return(self):
        page = self.home_page()
        self._assert_enter_and_return(page.go_to_ai_coach, "home_ai_coach", "AI Coach")

    @prob(0.55)
    @max_tries(3)
    @precondition(lambda self: self.on_home_page())
    def test_enter_course_and_return(self):
        page = self.home_page()
        self._assert_enter_and_return(page.go_to_jingpin_course, "home_course", "精品课程")

    @prob(0.55)
    @max_tries(3)
    @precondition(lambda self: self.on_home_page())
    def test_enter_assessment_and_return(self):
        page = self.home_page()
        self._assert_enter_and_return(page.go_to_assessment, "home_assessment", "运动测评")

    @prob(0.55)
    @max_tries(3)
    @precondition(lambda self: self.on_home_page())
    def test_enter_plan_and_return(self):
        page = self.home_page()
        self._assert_enter_and_return(page.go_to_plan, "home_plan", "运动计划")

    @prob(0.5)
    @max_tries(3)
    @precondition(lambda self: self.on_home_page())
    def test_enter_profile_and_return(self):
        page = self.home_page()
        self._assert_enter_and_return(page.go_to_profile, "home_profile", "个人中心")

    @prob(0.45)
    @max_tries(3)
    @precondition(lambda self: self.on_home_page())
    def test_enter_schedule_and_return(self):
        page = self.home_page()
        self._assert_enter_and_return(page.go_to_calendar_more, "home_schedule", "日程详情")

    @prob(0.45)
    @max_tries(5)
    @precondition(lambda self: self.on_home_page())
    def test_today_effort_on_home_visible(self):
        self.set_perf_phase("home_data_center")
        page = self.data_center_page()
        assert page.ensure_effort_strip(), "Home 页 Today's Effort 数据条不可见"
        assert page.effort_stats_visible(), "Home 页运动统计不可见"
