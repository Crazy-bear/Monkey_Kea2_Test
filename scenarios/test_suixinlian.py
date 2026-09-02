# -*- coding: utf-8 -*-
"""
随心练场景稳定性属性测试 — v3.x UI。

定位见 pages/free_workout_page.py 与 S1Pro_UI/v3.0.0.6858/elements/FreeWorkout_elements.md。
"""
from kea2 import precondition, prob, max_tries

from scenarios.base_property import FitnessMirrorPropertyTest


class SuixinlianTest(FitnessMirrorPropertyTest):

    @prob(0.7)
    @max_tries(3)
    @precondition(lambda self: self.on_home_page())
    def test_enter_suixinlian_stable(self):
        self.set_perf_phase("suixinlian")
        self.home_page().go_to_suixinlian()
        self.d.sleep(2)
        page = self.free_workout_page()
        assert page.is_free_workout_page_displayed(), "随心练页关键元素不可见"
        self.press_back_to_home()

    @prob(0.55)
    @max_tries(3)
    @precondition(lambda self: self.on_home_page())
    def test_suixinlian_shortcuts_visible(self):
        self.set_perf_phase("suixinlian_shortcuts")
        self.home_page().go_to_suixinlian()
        self.d.sleep(2)
        page = self.free_workout_page()
        assert page.is_displayed(page.START_NOW), "START NOW 入口不可见"
        assert page.is_displayed(page.SELECT_MOVE), "CUSTOM MOVES 入口不可见"
        self.press_back_to_home()
