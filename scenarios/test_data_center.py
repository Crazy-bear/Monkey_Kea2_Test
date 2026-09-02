# -*- coding: utf-8 -*-
"""
数据中心（Today's Effort + Data Center 详情）场景稳定性属性测试 — v3.x UI。

定位见 pages/data_center_page.py、pages/data_center_detail_page.py 与
S1Pro_UI/v3.0.0.6858/elements/Home_NoReminder_elements.md、
DataCenterDetail_elements.md。
"""
from kea2 import precondition, prob, max_tries

from scenarios.base_property import FitnessMirrorPropertyTest


class DataCenterTest(FitnessMirrorPropertyTest):

    def _enter_detail_from_home(self):
        strip = self.data_center_page()
        assert strip.go_to_data_center(), "无法点击 Today's Effort 进入数据中心"
        self.d.sleep(2)
        detail = self.data_center_detail_page()
        assert detail.is_data_center_detail_displayed(), "Data Center 详情页关键元素不可见"
        return detail

    @prob(0.55)
    @max_tries(5)
    @precondition(lambda self: self.on_home_page())
    def test_today_effort_strip_visible(self):
        self.set_perf_phase("data_center_strip")
        page = self.data_center_page()
        assert page.ensure_effort_strip(), "Today's Effort 数据条不可见（请先关闭提醒条）"
        assert page.is_effort_label_visible(), "Today's Effort 标题不可见"
        assert page.is_displayed(page.REPORT_INFOS), "运动数据区不可见"

    @prob(0.5)
    @max_tries(5)
    @precondition(lambda self: self.on_home_page())
    def test_today_effort_stats_visible(self):
        self.set_perf_phase("data_center_stats")
        page = self.data_center_page()
        assert page.ensure_effort_strip(), "Today's Effort 数据条不可见"
        assert page.effort_stats_visible(), "时长/卡路里/重量统计不可见"

    @prob(0.45)
    @max_tries(3)
    @precondition(lambda self: self.data_center_page().ensure_effort_strip())
    def test_enter_data_center_and_return(self):
        self.set_perf_phase("data_center_detail")
        self._enter_detail_from_home()
        assert self.press_back_to_home(), "数据中心返回 Home 失败"

    @prob(0.45)
    @max_tries(3)
    @precondition(lambda self: self.data_center_page().ensure_effort_strip())
    def test_data_center_summary_visible(self):
        self.set_perf_phase("data_center_summary")
        detail = self._enter_detail_from_home()
        assert detail.summary_stats_visible(), "Data Center 汇总统计不可见"
        assert self.press_back_to_home(), "数据中心返回 Home 失败"

    @prob(0.4)
    @max_tries(3)
    @precondition(lambda self: self.data_center_page().ensure_effort_strip())
    def test_data_center_progress_and_preferences(self):
        self.set_perf_phase("data_center_sections")
        detail = self._enter_detail_from_home()
        assert detail.progress_section_visible(), "Progress 区块不可见"
        assert detail.preferences_section_visible(), "Preferences 区块不可见"
        assert self.press_back_to_home(), "数据中心返回 Home 失败"

    @prob(0.35)
    @max_tries(3)
    @precondition(lambda self: self.data_center_page().ensure_effort_strip())
    def test_data_center_progress_tab_switch(self):
        self.set_perf_phase("data_center_tabs")
        detail = self._enter_detail_from_home()
        assert detail.switch_progress_tab(detail.TAB_CALORIES), "无法切换到 Calories Tab"
        assert detail.switch_progress_tab(detail.TAB_VOLUME), "无法切换到 Volume Tab"
        assert self.press_back_to_home(), "数据中心返回 Home 失败"
