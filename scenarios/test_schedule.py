# -*- coding: utf-8 -*-
"""
日程详情场景稳定性属性测试 — v3.x UI。

定位见 pages/schedule_page.py 与 S1Pro_UI/v3.0.0.6858/elements/Home_CalendarMore_elements.md。
"""
from kea2 import precondition, prob, max_tries

from scenarios.base_property import FitnessMirrorPropertyTest


class ScheduleTest(FitnessMirrorPropertyTest):

    @prob(0.55)
    @max_tries(3)
    @precondition(lambda self: self.on_home_page())
    def test_enter_schedule_stable(self):
        self.set_perf_phase("schedule")
        self.home_page().go_to_calendar_more()
        self.d.sleep(2)
        page = self.schedule_page()
        assert page.is_schedule_page_displayed(), "日程详情页关键元素不可见"
        self.press_back_to_home()

    @prob(0.5)
    @max_tries(3)
    @precondition(lambda self: self.on_home_page())
    def test_schedule_week_stats_visible(self):
        self.set_perf_phase("schedule_stats")
        self.home_page().go_to_calendar_more()
        self.d.sleep(2)
        page = self.schedule_page()
        assert page.is_displayed(page.WEEK_STATS), "本周统计区不可见"
        assert page.is_displayed(page.WEEK_CALENDAR), "周日历不可见"
        self.press_back_to_home()
