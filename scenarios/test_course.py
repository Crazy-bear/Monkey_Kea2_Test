# -*- coding: utf-8 -*-
"""
精品课程场景稳定性属性测试 — v3.x UI。

定位见 pages/course_page.py 与 S1Pro_UI/v3.0.0.6858/elements/Course_elements.md。
"""
from kea2 import precondition, prob, max_tries

from scenarios.base_property import FitnessMirrorPropertyTest


class CourseTest(FitnessMirrorPropertyTest):

    @prob(0.7)
    @max_tries(3)
    @precondition(lambda self: self.on_home_page())
    def test_enter_course_stable(self):
        self.set_perf_phase("course")
        self.home_page().go_to_jingpin_course()
        self.d.sleep(2)
        page = self.course_page()
        assert page.is_course_page_displayed(), "精品课程页关键元素不可见"
        self.press_back_to_home()

    @prob(0.55)
    @max_tries(3)
    @precondition(lambda self: self.on_home_page())
    def test_course_list_visible(self):
        self.set_perf_phase("course_list")
        self.home_page().go_to_jingpin_course()
        self.d.sleep(2)
        page = self.course_page()
        assert page.is_displayed(page.COURSE_LIST), "课程列表不可见"
        assert page.is_displayed(page.FILTER_BAR), "分类筛选栏不可见"
        self.press_back_to_home()
