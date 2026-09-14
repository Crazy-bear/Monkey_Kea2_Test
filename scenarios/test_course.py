# -*- coding: utf-8 -*-
"""
精品课程场景 — 低频哨兵（列表/筛选可见）。

进模块靠 test_pull / 开局引导；本文件不做进退导航。
"""
from kea2 import precondition, prob, max_tries

from scenarios.base_property import FitnessMirrorPropertyTest


class CourseTest(FitnessMirrorPropertyTest):

    def _on_course(self):
        return self.course_page().is_course_page_displayed()

    @prob(0.1)
    @max_tries(20)
    @precondition(lambda self: self.explore_or_enter_ready("course", self._on_course))
    def test_course_list_visible(self):
        self.set_perf_phase("course_list")
        page = self.course_page()
        if not page.is_course_page_displayed():
            self.home_page().go_to_jingpin_course()
            self.d.sleep(2)
        assert page.is_displayed(page.COURSE_LIST), "课程列表不可见"
        assert page.is_displayed(page.FILTER_BAR), "分类筛选栏不可见"
        self.finish_module_property()
