# -*- coding: utf-8 -*-
"""Page Object 单元测试（mock device）。"""

import os
from unittest.mock import MagicMock


class TestBasePage:
    def test_click_resource_id_string(self):
        from pages.base_page import BasePage

        device = MagicMock()
        page = BasePage(device)
        page.click("com.test:id/button")
        device.assert_called_with(resourceId="com.test:id/button")
        device.return_value.click.assert_called_once()

    def test_click_text_locator_dict(self):
        from pages.base_page import BasePage

        device = MagicMock()
        page = BasePage(device)
        page.click({"type": "text", "value": "登录"})
        device.assert_called_with(text="登录")

    def test_text_exists_uses_text_contains_for_apostrophe(self):
        from pages.base_page import BasePage

        device = MagicMock()
        page = BasePage(device)
        device.return_value.exists = True
        assert page.text_exists("Today's Effort") is True
        device.assert_called_with(textContains="Effort")


class TestHomePage:
    def test_locators_match_home_dump(self):
        from pages.home_page import HomePage

        dump_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "S1Pro_UI",
            "v3.0.0.6858",
            "window_dump",
            "Home_window_dump.xml",
        )
        if not os.path.isfile(dump_path):
            return
        xml = open(dump_path, encoding="utf-8").read()
        for rid in (
            HomePage.HOME_TAB,
            HomePage.START_BUTTON,
            HomePage.COURSE_BUTTON,
            HomePage.PLAN_BUTTON,
            HomePage.ASSESSMENT_BUTTON,
            HomePage.PROFILE_BUTTON,
        ):
            assert rid in xml, f"Home dump 缺少 {rid}"

    def test_is_home_page_requires_two_anchors(self):
        from pages.home_page import HomePage

        device = MagicMock()

        def side_effect(**kwargs):
            m = MagicMock()
            rid = kwargs.get("resourceId")
            m.exists = rid in (HomePage.MAIN_TITLE_BAR, HomePage.START_BUTTON)
            return m

        device.side_effect = side_effect
        page = HomePage(device)
        assert page.is_home_page_displayed() is True


class TestLifestylePage:
    def test_lifestyle_locators_match_dump(self):
        from pages.lifestyle_page import LifestylePage

        dump_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "S1Pro_UI",
            "v3.0.0.6858",
            "window_dump",
            "Lifestyle_window_dump.xml",
        )
        if not os.path.isfile(dump_path):
            return
        xml = open(dump_path, encoding="utf-8").read()
        for rid in (LifestylePage.LIFESTYLE_TAB, LifestylePage.FUNCS_LIST):
            assert rid in xml, f"Lifestyle dump 缺少 {rid}"
        for label in LifestylePage.ENTRY_LABELS:
            assert label in xml, f"Lifestyle dump 缺少文案 {label}"

    def test_is_lifestyle_page_requires_entries(self):
        from pages.lifestyle_page import LifestylePage

        device = MagicMock()
        page = LifestylePage(device)

        def side_effect(**kwargs):
            m = MagicMock()
            rid = kwargs.get("resourceId")
            text = kwargs.get("text")
            if rid in (LifestylePage.MAIN_TITLE_BAR, LifestylePage.LIFESTYLE_TAB, LifestylePage.FUNCS_LIST):
                m.exists = True
            elif text == LifestylePage.LABEL_GAMES:
                m.exists = True
            else:
                m.exists = False
            return m

        device.side_effect = side_effect
        assert page.is_lifestyle_page_displayed() is True


class TestMainActivityPage:
    def test_control_panel_open_detects_wifi_panel(self):
        from pages.main_activity_page import MainActivityPage

        device = MagicMock()
        page = MainActivityPage(device)

        def side_effect(**kwargs):
            m = MagicMock()
            m.exists = kwargs.get("resourceId") == MainActivityPage.CONTROL_WIFI_PANEL
            return m

        device.side_effect = side_effect
        assert page.is_control_panel_open() is True

    def test_ensure_home_surface_dismisses_control_panel(self):
        from pages.main_activity_page import MainActivityPage
        from pages.home_page import HomePage

        device = MagicMock()
        page = HomePage(device)
        calls = {"panel": 1}

        def side_effect(**kwargs):
            rid = kwargs.get("resourceId")
            m = MagicMock()
            if rid in MainActivityPage._CONTROL_PANEL_MARKERS:
                m.exists = calls["panel"] > 0
            elif rid == MainActivityPage.CONTROL_DISMISS_IDS[0]:
                m.exists = calls["panel"] > 0
            elif rid in HomePage._HOME_ANCHORS:
                m.exists = calls["panel"] == 0
            else:
                m.exists = False
            return m

        device.side_effect = side_effect

        def click_effect(locator):
            if locator == MainActivityPage.CONTROL_DISMISS_IDS[0]:
                calls["panel"] = 0

        page.click = MagicMock(side_effect=click_effect)
        assert page.ensure_home_surface() is True
        page.click.assert_called()


def _dump_path(name):
    return os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "S1Pro_UI",
        "v3.0.0.6858",
        "window_dump",
        name,
    )


def _assert_ids_in_dump(dump_file, ids):
    dump_path = _dump_path(dump_file)
    if not os.path.isfile(dump_path):
        return
    xml = open(dump_path, encoding="utf-8").read()
    for rid in ids:
        assert rid in xml, f"{dump_file} 缺少 {rid}"


class TestSubPagesDumpAlignment:
    PAGE_CASES = (
        ("CoursePage", "Course_window_dump.xml", "pages.course_page", "CoursePage", (
            "BACK_BUTTON", "COURSE_LIST", "FILTER_BAR",
        )),
        ("FreeWorkoutPage", "FreeWorkout_window_dump.xml", "pages.free_workout_page", "FreeWorkoutPage", (
            "BACK_BUTTON", "START_NOW", "SELECT_MOVE",
        )),
        ("AICoachPage", "AICoach_window_dump.xml", "pages.ai_coach_page", "AICoachPage", (
            "BACK_BUTTON", "GREETING", "START_WORKOUT",
        )),
        ("AssessmentPage", "Assessment_window_dump.xml", "pages.assessment_page", "AssessmentPage", (
            "BACK_BUTTON", "ASSESSMENT_GRID", "START_FULL",
        )),
        ("ProgramsPage", "Programs_window_dump.xml", "pages.programs_page", "ProgramsPage", (
            "BACK_BUTTON", "PLAN_LIST", "SORT_BAR",
        )),
        ("ProfilePage", "Profile_window_dump.xml", "pages.profile_page", "ProfilePage", (
            "BACK_BUTTON", "SETTINGS_LIST", "CHECKIN_CARD",
        )),
        ("SchedulePage", "Home_CalendarMore_window_dump.xml", "pages.schedule_page", "SchedulePage", (
            "BACK_BUTTON", "WEEK_STATS", "COURSE_LIST",
        )),
        ("ControlPanelPage", "Home_ControlPanel_window_dump.xml", "pages.control_panel_page", "ControlPanelPage", (
            "SYS_BRIGHT", "SYS_VOICE", "SYS_BLE", "SYS_WIFI", "SYS_LED",
        )),
        ("DataCenterPage", "Home_NoReminder_window_dump.xml", "pages.data_center_page", "DataCenterPage", (
            "STRIP_ROOT", "REPORT_ENTRY", "REPORT_INFOS", "TIME_VALUE", "KCAL_VALUE", "WEIGHT_VALUE",
        )),
        ("DataCenterDetailPage", "DataCenterDetail_window_dump.xml", "pages.data_center_detail_page", "DataCenterDetailPage", (
            "BACK_BUTTON", "TOTAL_SUMMARY", "PROGRESS_PANEL", "PREFERENCES_PANEL", "WEEK_CHART",
        )),
        ("FloatingTouchPage", "FloatingTouch_window_dump.xml", "pages.floating_touch_page", "FloatingTouchPage", (
            "FAB_ROOT", "FAB_CONTRACT", "FAB_ICON",
        )),
        ("FloatingTouchPageOpen", "TouchMenu_window_dump.xml", "pages.floating_touch_page", "FloatingTouchPage", (
            "MENU_EXPAND", "FOLD_BUTTON", "BOTTOM_TOOLS", "BTN_TOGGLE", "TOOLBAR",
        )),
        ("SettingsPage", "Settings_window_dump.xml", "pages.settings_page", "SettingsPage", (
            "BACK_BUTTON", "SETTINGS_LIST", "TITLE",
        )),
        ("SettingsAccountSecurityPage", "Settings_AccountSecurity_window_dump.xml", "pages.settings_page", "SettingsAccountSecurityPage", (
            "BACK_BUTTON", "CHANGE_PASSWORD",
        )),
        ("SettingsLanguagePage", "Settings_Language_window_dump.xml", "pages.settings_page", "SettingsLanguagePage", (
            "BACK_BUTTON", "LANGUAGE_LIST",
        )),
        ("SettingsDateTimePage", "Settings_DateTime_window_dump.xml", "pages.settings_page", "SettingsDateTimePage", (
            "BACK_BUTTON", "TIME_FORMAT", "TIME_ZONE",
        )),
    )

    def test_page_locators_match_dumps(self):
        import importlib

        for _, dump_file, module_name, class_name, attrs in self.PAGE_CASES:
            mod = importlib.import_module(module_name)
            cls = getattr(mod, class_name)
            _assert_ids_in_dump(dump_file, tuple(getattr(cls, a) for a in attrs))


class TestDataCenterDetailPage:
    def test_is_detail_page_requires_three_anchors(self):
        from pages.data_center_detail_page import DataCenterDetailPage

        device = MagicMock()
        page = DataCenterDetailPage(device)

        def side_effect(**kwargs):
            m = MagicMock()
            rid = kwargs.get("resourceId")
            text = kwargs.get("text")
            if rid in (
                DataCenterDetailPage.BACK_BUTTON,
                DataCenterDetailPage.TOTAL_SUMMARY,
                DataCenterDetailPage.PROGRESS_PANEL,
                DataCenterDetailPage.PREFERENCES_PANEL,
            ):
                m.exists = True
            elif text == DataCenterDetailPage.TITLE_TEXT:
                m.exists = True
            else:
                m.exists = False
            return m

        device.side_effect = side_effect
        assert page.is_data_center_detail_displayed() is True


class TestStaticCheckerCompat:
    def test_dismiss_reminder_no_click_on_static_checker(self):
        from kea2.u2Driver import U2StaticChecker
        from pages.main_activity_page import MainActivityPage

        dump_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "S1Pro_UI",
            "v3.0.0.6858",
            "window_dump",
            "Home_window_dump.xml",
        )
        if not os.path.isfile(dump_path):
            return

        xml = open(dump_path, encoding="utf-8").read()
        device = U2StaticChecker().getInstance(xml)
        page = MainActivityPage(device)

        # Home dump 含提醒条关闭按钮；StaticChecker 下 click 应为 no-op，不得抛 TypeError
        page.dismiss_reminder_banner()
        assert page.click(page.REMINDER_CLOSE) is False

    def test_on_home_page_precondition_read_only(self):
        from kea2.u2Driver import U2StaticChecker
        from scenarios.base_property import FitnessMirrorPropertyTest

        dump_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "S1Pro_UI",
            "v3.0.0.6858",
            "window_dump",
            "Home_window_dump.xml",
        )
        if not os.path.isfile(dump_path):
            return

        xml = open(dump_path, encoding="utf-8").read()
        case = FitnessMirrorPropertyTest()
        case.d = U2StaticChecker().getInstance(xml)
        assert case.on_home_page() is True
