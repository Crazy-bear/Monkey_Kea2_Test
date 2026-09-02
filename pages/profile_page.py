# -*- coding: utf-8 -*-
"""
Profile 页 Page Object（AEKE 力量镜 v3.x）。

定位依据：S1Pro_UI/v3.0.0.6858/elements/Profile_elements.md
"""
from pages.base_page import BasePage


class ProfilePage(BasePage):
    """个人中心 — SettingsActivity。"""

    PACKAGE = "com.aeke.fitnessmirror"

    BACK_BUTTON = f"{PACKAGE}:id/ivLeftIcon"
    LOGOUT = f"{PACKAGE}:id/tv_switch"
    USER_NAME = f"{PACKAGE}:id/tv_name"
    CHECKIN_CARD = f"{PACKAGE}:id/rl_win_vip"
    SETTINGS_LIST = f"{PACKAGE}:id/settings_rv"
    QR_APP = f"{PACKAGE}:id/QRCodeApp_iv"
    QR_WECHAT = f"{PACKAGE}:id/QRCodeWeChat_iv"

    MENU_LABELS = ("Profile", "Settings", "About", "Help")
    MENU_SETTINGS = "Settings"
    LOGOUT_TEXT = "Logout"

    _ANCHORS = (BACK_BUTTON, SETTINGS_LIST, CHECKIN_CARD)

    def is_profile_page_displayed(self):
        hits = sum(1 for loc in self._ANCHORS if self.is_displayed(loc))
        if hits < 2:
            return False
        return any(self.device(text=label).exists for label in self.MENU_LABELS)

    def press_back(self):
        if self.is_displayed(self.BACK_BUTTON):
            self.click(self.BACK_BUTTON)
            self.device.sleep(0.5)
            return True
        return False

    def go_to_settings(self):
        self.device(text=self.MENU_SETTINGS).click()
        self.device.sleep(0.8)
