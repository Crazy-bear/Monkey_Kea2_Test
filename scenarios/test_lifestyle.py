# -*- coding: utf-8 -*-
"""
Lifestyle Tab 专项属性测试 — v3.x UI。

定位见 pages/lifestyle_page.py 与 S1Pro_UI/v3.0.0.6858/elements/Lifestyle_elements.md。
"""
from kea2 import precondition, prob, max_tries

from scenarios.base_property import FitnessMirrorPropertyTest


class LifestyleNavigationTest(FitnessMirrorPropertyTest):

    def _assert_enter_and_return(self, navigate, phase, label):
        self.set_perf_phase(phase)
        navigate()
        self.d.sleep(2)
        assert self.d(className="android.widget.FrameLayout").exists(timeout=10), (
            f"{label} 进入后无可用界面"
        )
        assert self.press_back_to_lifestyle(), f"{label} 返回 Lifestyle 失败"

    @prob(0.6)
    @max_tries(5)
    @precondition(lambda self: self.on_lifestyle_page())
    def test_lifestyle_tab_visible(self):
        self.set_perf_phase("lifestyle_tab")
        page = self.lifestyle_page()
        assert page.is_displayed(page.LIFESTYLE_TAB), "Lifestyle Tab 不可见"
        assert page.is_displayed(page.MAIN_TITLE_BAR), "顶栏不可见"
        assert page.is_displayed(page.FUNCS_LIST), "娱乐功能列表不可见"

    @prob(0.6)
    @max_tries(5)
    @precondition(lambda self: self.on_lifestyle_page())
    def test_lifestyle_entries_visible(self):
        self.set_perf_phase("lifestyle_entries")
        page = self.lifestyle_page()
        for label in page.ENTRY_LABELS:
            assert page.device(text=label).exists, f"{label} 入口不可见"

    @prob(0.55)
    @max_tries(3)
    @precondition(lambda self: self.on_lifestyle_page())
    def test_enter_games_and_return(self):
        page = self.lifestyle_page()
        self._assert_enter_and_return(page.go_to_games, "lifestyle_games", "Games")

    @prob(0.55)
    @max_tries(3)
    @precondition(lambda self: self.on_lifestyle_page())
    def test_enter_vs_mode_and_return(self):
        page = self.lifestyle_page()
        self._assert_enter_and_return(page.go_to_vs_mode, "lifestyle_vs_mode", "VS Mode")

    @prob(0.55)
    @max_tries(3)
    @precondition(lambda self: self.on_lifestyle_page())
    def test_enter_speaker_and_return(self):
        page = self.lifestyle_page()
        self._assert_enter_and_return(page.go_to_speaker, "lifestyle_speaker", "Speaker")

    @prob(0.5)
    @max_tries(3)
    @precondition(lambda self: self.on_lifestyle_page())
    def test_enter_screen_cast_and_return(self):
        page = self.lifestyle_page()
        self._assert_enter_and_return(
            page.go_to_screen_cast, "lifestyle_screen_cast", "Screen Cast"
        )
