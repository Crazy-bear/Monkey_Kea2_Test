# -*- coding: utf-8 -*-
"""Page Object 单元测试（mock device）。"""

import os
from unittest.mock import MagicMock

import pytest


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

        dump_path = _dump_path("Home_window_dump.xml")
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
            HomePage.EFFORT_ENTRY,
            HomePage.EFFORT_INFOS,
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
    def _lifestyle_dump_dir(self):
        root = os.path.dirname(os.path.dirname(__file__))
        for ver in ("v3.1.0.7123", "v3.0.0.6858"):
            path = os.path.join(root, "S1Pro_UI", ver, "window_dump")
            if os.path.isdir(path):
                return path
        return None

    def test_lifestyle_locators_match_dump(self):
        from pages.lifestyle_page import LifestylePage

        dump_dir = self._lifestyle_dump_dir()
        if not dump_dir:
            return
        dump_path = os.path.join(dump_dir, "Lifestyle_window_dump.xml")
        if not os.path.isfile(dump_path):
            return
        xml = open(dump_path, encoding="utf-8").read()
        for rid in (LifestylePage.LIFESTYLE_TAB, LifestylePage.FUNCS_LIST):
            assert rid in xml, f"Lifestyle dump 缺少 {rid}"
        for label in LifestylePage.ENTRY_LABELS:
            assert label in xml, f"Lifestyle dump 缺少文案 {label}"

    def test_lifestyle_subpage_locators_match_dump(self):
        from pages.lifestyle_page import (
            LifestyleGamesPage,
            LifestyleVSModePage,
            LifestyleSpeakerPage,
            LifestyleScreenCastPage,
            LifestyleWallpaperPage,
        )

        dump_dir = self._lifestyle_dump_dir()
        if not dump_dir:
            return

        cases = (
            ("Lifestyle_Games_window_dump.xml", (LifestyleGamesPage.HOME_BUTTON, LifestyleGamesPage.GAME_LIST)),
            ("Lifestyle_VSMode_window_dump.xml", (LifestyleVSModePage.START_PK, LifestyleVSModePage.TITLE)),
            ("Lifestyle_Speaker_window_dump.xml", (LifestyleSpeakerPage.BTN_QUIT, LifestyleSpeakerPage.BTN_ALLOW)),
            ("Lifestyle_Speaker_Main_window_dump.xml", (LifestyleSpeakerPage.CLOSE_BUTTON, LifestyleSpeakerPage.DEVICE_NAME)),
            ("Lifestyle_ScreenCast_window_dump.xml", (LifestyleScreenCastPage.CLOSE_BUTTON, LifestyleScreenCastPage.DEVICE_NAME)),
            ("Lifestyle_Wallpaper_window_dump.xml", (LifestyleWallpaperPage.CLOSE_BUTTON, LifestyleWallpaperPage.TITLE)),
        )
        for filename, rids in cases:
            path = os.path.join(dump_dir, filename)
            if not os.path.isfile(path):
                continue
            xml = open(path, encoding="utf-8").read()
            for rid in rids:
                short = rid.split("/")[-1]
                assert short in xml, f"{filename} 缺少 {rid}"

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

    def test_has_any_entry_accepts_chinese_alias(self):
        from pages.lifestyle_page import LifestylePage

        device = MagicMock()
        page = LifestylePage(device)

        def side_effect(**kwargs):
            m = MagicMock()
            m.exists = kwargs.get("text") == "游戏"
            return m

        device.side_effect = side_effect
        assert page.has_any_entry() is True

    def test_games_page_detection(self):
        from pages.lifestyle_page import LifestyleGamesPage

        device = MagicMock()
        page = LifestyleGamesPage(device)

        def side_effect(**kwargs):
            m = MagicMock()
            m.exists = kwargs.get("resourceId") in (
                LifestyleGamesPage.HOME_BUTTON,
                LifestyleGamesPage.GAME_LIST,
            )
            return m

        device.side_effect = side_effect
        assert page.is_games_page_displayed() is True


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


class TestLoginPage:
    def test_locators_match_login_dump(self):
        from pages.login_page import LoginPage

        _assert_ids_in_dump(
            "Login_window_dump.xml",
            (
                LoginPage.TITLE,
                LoginPage.MEMBER_LIST,
                LoginPage.TAG_ADMIN,
                LoginPage.OFFLINE_MODE,
            ),
        )

    def test_is_login_page_requires_anchors(self):
        from pages.login_page import LoginPage

        device = MagicMock()

        def side_effect(**kwargs):
            m = MagicMock()
            rid = kwargs.get("resourceId")
            text = kwargs.get("text")
            m.exists = rid in (LoginPage.TITLE, LoginPage.MEMBER_LIST) or text == LoginPage.TITLE_TEXT
            return m

        device.side_effect = side_effect
        assert LoginPage(device).is_login_page_displayed() is True

    def test_login_as_admin_noop_on_static(self):
        from pages.login_page import LoginPage

        device = MagicMock()
        device.__class__.__name__ = "U2StaticDevice"
        page = LoginPage(device)
        # 无真实 Admin 节点时直接失败；静态设备不应抛错
        assert page.login_as_admin() is False


class TestScreensaverPage:
    def test_locators_match_screensaver_dump(self):
        from pages.screensaver_page import ScreensaverPage

        _assert_ids_in_dump(
            "Screensaver_window_dump.xml",
            (
                ScreensaverPage.SCREEN_IMAGE,
                ScreensaverPage.TIME_HOUR,
                ScreensaverPage.TIME_MINUTE,
            ),
        )

    def test_is_screensaver_requires_two_anchors(self):
        from pages.screensaver_page import ScreensaverPage

        device = MagicMock()

        def side_effect(**kwargs):
            m = MagicMock()
            rid = kwargs.get("resourceId")
            m.exists = rid in (ScreensaverPage.SCREEN_IMAGE, ScreensaverPage.TIME_HOUR)
            return m

        device.side_effect = side_effect
        assert ScreensaverPage(device).is_screensaver_displayed() is True


def _dump_path(name):
    root = os.path.dirname(os.path.dirname(__file__))
    for ver in ("v3.1.0.7123", "v3.0.0.6858"):
        path = os.path.join(root, "S1Pro_UI", ver, "window_dump", name)
        if os.path.isfile(path):
            return path
    return os.path.join(root, "S1Pro_UI", "v3.0.0.6858", "window_dump", name)


def _read_dump(name):
    path = _dump_path(name)
    if not os.path.isfile(path):
        pytest.skip(f"缺少 dump 文件：{path}")
    return open(path, encoding="utf-8").read()


def _static_checker_device(xml):
    """
    构造 Kea2 precondition 用的只读 StaticChecker 设备。

    U2StaticChecker.__init__ 会 adbutils.device() + u2.connect() 连真机，
    这里绕开它只保留 XML 解析部分，保证单测无设备可跑。
    """
    from kea2.u2Driver import U2StaticChecker, U2StaticDevice

    checker = U2StaticChecker.__new__(U2StaticChecker)
    checker.d = U2StaticDevice(script_driver=None)
    return checker.getInstance(xml)


def _assert_ids_in_dump(dump_file, ids):
    dump_path = _dump_path(dump_file)
    if not os.path.isfile(dump_path):
        return
    xml = open(dump_path, encoding="utf-8").read()
    for rid in ids:
        assert rid in xml, f"{dump_file} 缺少 {rid} (checked {dump_path})"


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
        ("DataCenterPage", "Home_window_dump.xml", "pages.data_center_page", "DataCenterPage", (
            "STRIP_ROOT", "REPORT_ENTRY", "REPORT_INFOS", "TIME_VALUE", "KCAL_VALUE", "WEIGHT_VALUE",
        )),
        ("DataCenterDetailPage", "DataCenterDetail_window_dump.xml", "pages.data_center_detail_page", "DataCenterDetailPage", (
            "BACK_BUTTON", "TOTAL_SUMMARY", "PROGRESS_PANEL", "PREFERENCES_PANEL", "WEEK_CHART",
            "MUSCLE_STATUS_PANEL", "MUSCLE_STATUS_TITLE", "MUSCLE_STATUS_VIEW",
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
                DataCenterDetailPage.MUSCLE_STATUS_PANEL,
            ):
                m.exists = True
            elif text == DataCenterDetailPage.TITLE_TEXT:
                m.exists = True
            else:
                m.exists = False
            return m

        device.side_effect = side_effect
        assert page.is_data_center_detail_displayed() is True

    def test_muscle_status_section_visible(self):
        from pages.data_center_detail_page import DataCenterDetailPage

        device = MagicMock()
        page = DataCenterDetailPage(device)

        def side_effect(**kwargs):
            m = MagicMock()
            rid = kwargs.get("resourceId")
            text = kwargs.get("text")
            if rid in (
                DataCenterDetailPage.MUSCLE_STATUS_PANEL,
                DataCenterDetailPage.MUSCLE_STATUS_VIEW,
            ):
                m.exists = True
            elif text == DataCenterDetailPage.MUSCLE_STATUS_TEXT:
                m.exists = True
            else:
                m.exists = False
            return m

        device.side_effect = side_effect
        assert page.muscle_status_section_visible() is True


class TestStaticCheckerCompat:
    def test_dismiss_reminder_no_click_on_static_checker(self):
        from pages.main_activity_page import MainActivityPage

        device = _static_checker_device(_read_dump("Home_window_dump.xml"))
        page = MainActivityPage(device)

        # Home dump 含提醒条关闭按钮；StaticChecker 下 click 应为 no-op，不得抛 TypeError
        page.dismiss_reminder_banner()
        assert page.click(page.REMINDER_CLOSE) is False

    def test_on_home_page_precondition_read_only(self):
        from scenarios.base_property import FitnessMirrorPropertyTest

        case = FitnessMirrorPropertyTest()
        case.d = _static_checker_device(_read_dump("Home_window_dump.xml"))
        assert case.on_home_page() is True
        assert case.needs_session_recovery() is False

    def test_needs_session_recovery_on_login_dump(self):
        from scenarios.base_property import FitnessMirrorPropertyTest

        case = FitnessMirrorPropertyTest()
        case.d = _static_checker_device(_read_dump("Login_window_dump.xml"))
        assert case.needs_session_recovery() is True
        assert case.on_home_page() is False
        # 基类恢复属性应对 CourseTest 等子类可见，避免登录页 0 Checkable
        from scenarios.test_course import CourseTest
        assert hasattr(CourseTest, "test_recover_session")
        assert hasattr(CourseTest, "needs_session_recovery")
