# -*- coding: utf-8 -*-
"""
Settings 场景稳定性属性测试 — v3.x UI。

定位见 pages/settings_page.py 与 S1Pro_UI/v3.0.0.6858/elements/Settings*_elements.md。
"""
from kea2 import precondition, prob, max_tries

from scenarios.base_property import FitnessMirrorPropertyTest


class SettingsTest(FitnessMirrorPropertyTest):

    def _enter_detail_and_return(self, navigate, phase, check):
        self.set_perf_phase(phase)
        navigate()
        self.d.sleep(1.2)
        assert check(), "Settings 子页关键元素不可见"
        assert self.press_back_to_settings() or self.press_back_to_home(), "返回 Settings 失败"

    @prob(0.5)
    @max_tries(3)
    @precondition(lambda self: self.on_home_page())
    def test_enter_settings_from_profile(self):
        self.set_perf_phase("settings_entry")
        profile = self.profile_page()
        self.home_page().go_to_profile()
        self.d.sleep(1.5)
        assert profile.is_profile_page_displayed(), "个人中心不可见"
        profile.go_to_settings()
        self.d.sleep(1)
        assert self.settings_page().is_settings_page_displayed(), "Settings 列表不可见"
        self.press_back_to_home()

    @prob(0.45)
    @max_tries(3)
    @precondition(lambda self: self.on_settings_page())
    def test_settings_list_entries_visible(self):
        self.set_perf_phase("settings_list")
        page = self.settings_page()
        for label in page.NAV_ENTRIES:
            assert page.device(text=label).exists, f"{label} 不可见"

    @prob(0.4)
    @max_tries(3)
    @precondition(lambda self: self.on_settings_page())
    def test_account_security_page(self):
        page = self.settings_page()
        self._enter_detail_and_return(
            lambda: page.go_to_entry(page.ENTRY_ACCOUNT_SECURITY),
            "settings_account_security",
            lambda: self.settings_account_security_page().is_page_displayed(),
        )

    @prob(0.4)
    @max_tries(3)
    @precondition(lambda self: self.on_settings_page())
    def test_language_page(self):
        page = self.settings_page()
        self._enter_detail_and_return(
            lambda: page.go_to_entry(page.ENTRY_LANGUAGE),
            "settings_language",
            lambda: self.settings_language_page().is_page_displayed(),
        )

    @prob(0.4)
    @max_tries(3)
    @precondition(lambda self: self.on_settings_page())
    def test_date_time_page(self):
        page = self.settings_page()
        self._enter_detail_and_return(
            lambda: page.go_to_entry(page.ENTRY_DATE_TIME),
            "settings_date_time",
            lambda: self.settings_datetime_page().is_page_displayed(),
        )

    @prob(0.35)
    @max_tries(3)
    @precondition(lambda self: self.on_settings_page())
    def test_units_dialog(self):
        self.set_perf_phase("settings_units")
        page = self.settings_page()
        assert page.go_to_entry(page.ENTRY_UNITS), "无法打开 Units"
        self.d.sleep(0.8)
        dialog = self.settings_units_dialog()
        assert dialog.is_dialog_displayed(), "Units 弹窗不可见"
        assert dialog.dismiss(), "无法关闭 Units 弹窗"
        assert page.is_settings_page_displayed(), "关闭后未回到 Settings"

    @prob(0.35)
    @max_tries(3)
    @precondition(lambda self: self.on_settings_page())
    def test_ai_correction_dialog(self):
        self.set_perf_phase("settings_ai_correction")
        page = self.settings_page()
        assert page.go_to_entry(page.ENTRY_AI_CORRECTION), "无法打开 AI Correction"
        self.d.sleep(0.8)
        dialog = self.settings_ai_correction_dialog()
        assert dialog.is_dialog_displayed(), "AI Correction 弹窗不可见"
        assert dialog.dismiss(), "无法关闭 AI Correction 弹窗"
        assert page.is_settings_page_displayed(), "关闭后未回到 Settings"
