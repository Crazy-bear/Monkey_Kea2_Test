# -*- coding: utf-8 -*-

"""

力量镜 Kea2 属性测试基类（设备需已预登录至 MainActivity）。

"""

import unittest



from pages.home_page import HomePage

from pages.lifestyle_page import LifestylePage

from pages.course_page import CoursePage

from pages.free_workout_page import FreeWorkoutPage

from pages.ai_coach_page import AICoachPage

from pages.assessment_page import AssessmentPage

from pages.programs_page import ProgramsPage

from pages.profile_page import ProfilePage

from pages.schedule_page import SchedulePage

from pages.control_panel_page import ControlPanelPage

from pages.data_center_page import DataCenterPage

from pages.data_center_detail_page import DataCenterDetailPage

from pages.floating_touch_page import FloatingTouchPage

from pages.settings_page import (
    SettingsPage,
    SettingsAccountSecurityPage,
    SettingsLanguagePage,
    SettingsDateTimePage,
    SettingsUnitsDialogPage,
    SettingsAICorrectionDialogPage,
    SettingsResetDeviceDialogPage,
)

from orchestrator.test_session import get_active_monitor





class FitnessMirrorPropertyTest(unittest.TestCase):

    """Kea2 注入 uiautomator2 Device 为 self.d。"""



    d = None



    def home_page(self):

        return HomePage(self.d)



    def lifestyle_page(self):

        return LifestylePage(self.d)



    def course_page(self):

        return CoursePage(self.d)



    def free_workout_page(self):

        return FreeWorkoutPage(self.d)



    def ai_coach_page(self):

        return AICoachPage(self.d)



    def assessment_page(self):

        return AssessmentPage(self.d)



    def programs_page(self):

        return ProgramsPage(self.d)



    def profile_page(self):

        return ProfilePage(self.d)



    def schedule_page(self):

        return SchedulePage(self.d)



    def control_panel_page(self):

        return ControlPanelPage(self.d)



    def data_center_page(self):

        return DataCenterPage(self.d)



    def data_center_detail_page(self):

        return DataCenterDetailPage(self.d)



    def floating_touch_page(self):

        return FloatingTouchPage(self.d)



    def settings_page(self):

        return SettingsPage(self.d)



    def settings_account_security_page(self):

        return SettingsAccountSecurityPage(self.d)



    def settings_language_page(self):

        return SettingsLanguagePage(self.d)



    def settings_datetime_page(self):

        return SettingsDateTimePage(self.d)



    def settings_units_dialog(self):

        return SettingsUnitsDialogPage(self.d)



    def settings_ai_correction_dialog(self):

        return SettingsAICorrectionDialogPage(self.d)



    def settings_reset_device_dialog(self):

        return SettingsResetDeviceDialogPage(self.d)



    def _is_static_precondition(self):
        from pages.base_page import _is_static_checker_device

        return _is_static_checker_device(self.d)

    def on_settings_page(self):
        page = self.settings_page()
        if page.is_settings_page_displayed():
            return True
        if self._is_static_precondition():
            return False
        if not self.on_home_page():
            return False
        self.home_page().go_to_profile()
        self.d.sleep(1)
        profile = self.profile_page()
        if not profile.is_profile_page_displayed():
            return False
        profile.go_to_settings()
        self.d.sleep(1)
        return page.is_settings_page_displayed()



    def press_back_to_settings(self, max_back=3):
        page = self.settings_page()
        for _ in range(max_back):
            if page.is_settings_page_displayed():
                return True
            if page.is_displayed(page.BACK_BUTTON):
                page.press_back()
            else:
                self.d.press("back")
            self.d.sleep(0.8)
        return page.is_settings_page_displayed()



    def on_home_page(self):
        page = self.home_page()
        if page.is_home_page_displayed():
            return True
        if self._is_static_precondition():
            return False
        return page.ensure_home_surface()

    def on_lifestyle_page(self):
        page = self.lifestyle_page()
        if page.is_lifestyle_page_displayed():
            return True
        if self._is_static_precondition():
            return False
        return page.ensure_lifestyle_surface()



    def set_perf_phase(self, name):

        monitor = get_active_monitor()

        if monitor:

            monitor.set_phase(name)



    def press_back_to_home(self, max_back=3):

        page = self.home_page()

        for _ in range(max_back):

            page.ensure_home_surface()

            if page.is_home_page_displayed():

                return True

            self.d.press("back")

            self.d.sleep(1)

        page.ensure_home_surface()

        return page.is_home_page_displayed()



    def press_back_to_lifestyle(self, max_back=3):

        page = self.lifestyle_page()

        for _ in range(max_back):

            page.ensure_lifestyle_surface()

            if page.is_lifestyle_page_displayed():

                return True

            self.d.press("back")

            self.d.sleep(1)

        page.ensure_lifestyle_surface()

        return page.is_lifestyle_page_displayed()


