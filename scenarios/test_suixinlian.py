# -*- coding: utf-8 -*-
"""
随心练场景 — 低频哨兵（快捷入口可见）。

进模块靠 test_pull / 开局引导；本文件不做进退导航。
"""
from kea2 import precondition, prob, max_tries

from scenarios.base_property import FitnessMirrorPropertyTest


class SuixinlianTest(FitnessMirrorPropertyTest):

    def _on_suixinlian(self):
        return self.free_workout_page().is_free_workout_page_displayed()

    @prob(0.1)
    @max_tries(20)
    @precondition(lambda self: self.explore_or_enter_ready("suixinlian", self._on_suixinlian))
    def test_suixinlian_shortcuts_visible(self):
        self.set_perf_phase("suixinlian_shortcuts")
        page = self.free_workout_page()
        if not page.is_free_workout_page_displayed():
            self.home_page().go_to_suixinlian()
            self.d.sleep(2)
        assert page.is_displayed(page.START_NOW), "START NOW 入口不可见"
        assert page.is_displayed(page.SELECT_MOVE), "CUSTOM MOVES 入口不可见"
        self.finish_module_property()
