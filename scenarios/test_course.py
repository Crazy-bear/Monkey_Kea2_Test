# -*- coding: utf-8 -*-
"""精品课程场景稳定性属性测试。"""
from kea2 import precondition, prob, max_tries

from scenarios.base_property import FitnessMirrorPropertyTest


class CourseTest(FitnessMirrorPropertyTest):

    @prob(0.7)
    @max_tries(3)
    @precondition(lambda self: self.on_main_page())
    def test_enter_course_stable(self):
        self.set_perf_phase("course")
        page = self.main_page()
        page.go_to_jingpin_course()
        self.d.sleep(2)
        assert self.d(className="android.widget.FrameLayout").exists(timeout=10)
        self.press_back_to_main()
