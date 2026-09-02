# -*- coding: utf-8 -*-
"""
Settings 列表与子页 Page Object（AEKE 力量镜 v3.x）。

定位依据：S1Pro_UI/v3.0.0.6858/elements/Settings*_elements.md
"""
from pages.base_page import BasePage, _element_exists


class SettingsDetailPage(BasePage):
    """Settings 子页 / 弹窗公共控件。"""

    PACKAGE = "com.aeke.fitnessmirror"
    BACK_BUTTON = f"{PACKAGE}:id/ivLeftIcon"
    TITLE = f"{PACKAGE}:id/tvTitle"

    def press_back(self):
        if self.is_displayed(self.BACK_BUTTON):
            self.click(self.BACK_BUTTON)
            self.device.sleep(0.5)
            return True
        self.device.press("back")
        self.device.sleep(0.5)
        return True

    def is_title_visible(self, title_text):
        return self.device(text=title_text).exists or (
            self.is_displayed(self.TITLE)
            and self.device(resourceId=self.TITLE, text=title_text).exists
        )


class SettingsPage(BasePage):
    """Settings 列表 — SettingDetailActivity。"""

    PACKAGE = "com.aeke.fitnessmirror"

    BACK_BUTTON = f"{PACKAGE}:id/ivLeftIcon"
    TITLE = f"{PACKAGE}:id/tvTitle"
    SETTINGS_LIST = f"{PACKAGE}:id/settings_detail_rv"
    REBOOT_ITEM = f"{PACKAGE}:id/item_power_reboot"

    TITLE_TEXT = "Settings"

    ENTRY_ACCOUNT_SECURITY = "Account Security"
    ENTRY_LANGUAGE = "Language"
    ENTRY_REGION = "Region"
    ENTRY_UNITS = "Units"
    ENTRY_DATE_TIME = "Date & Time"
    ENTRY_AI_CORRECTION = "AI Correction Level"
    ENTRY_RESET_DEVICE = "Reset Device"

    # 稳定性测试禁止点击（会清除本地数据）
    BLOCKED_ENTRIES = frozenset({ENTRY_RESET_DEVICE})

    NAV_ENTRIES = (
        ENTRY_ACCOUNT_SECURITY,
        ENTRY_LANGUAGE,
        ENTRY_UNITS,
        ENTRY_DATE_TIME,
        ENTRY_AI_CORRECTION,
    )

    TOGGLE_ENTRIES = ("Assistive Touch", "Drop Protect", "Video Subtitles")

    _ANCHORS = (BACK_BUTTON, SETTINGS_LIST, TITLE)

    def is_settings_page_displayed(self):
        hits = sum(1 for loc in self._ANCHORS if self.is_displayed(loc))
        if hits < 2:
            return False
        return self.device(text=self.TITLE_TEXT).exists

    def press_back(self):
        if self.is_displayed(self.BACK_BUTTON):
            self.click(self.BACK_BUTTON)
            self.device.sleep(0.5)
            return True
        return False

    def go_to_entry(self, label):
        if label in self.BLOCKED_ENTRIES:
            return False
        node = self.device(text=label)
        if _element_exists(node, timeout=3):
            node.click()
            self.device.sleep(0.8)
            return True
        return False


class SettingsAccountSecurityPage(SettingsDetailPage):
    CHANGE_PASSWORD = f"{SettingsDetailPage.PACKAGE}:id/ll_change_password"
    TITLE_TEXT = "Account Security"

    def is_page_displayed(self):
        return self.is_title_visible(self.TITLE_TEXT) and self.is_displayed(self.CHANGE_PASSWORD)


class SettingsLanguagePage(SettingsDetailPage):
    LANGUAGE_LIST = f"{SettingsDetailPage.PACKAGE}:id/rv_list"
    TITLE_TEXT = "Language"

    def is_page_displayed(self):
        return self.is_title_visible(self.TITLE_TEXT) and self.is_displayed(self.LANGUAGE_LIST)


class SettingsDateTimePage(SettingsDetailPage):
    TIME_FORMAT = f"{SettingsDetailPage.PACKAGE}:id/layout_time_format"
    TIME_ZONE = f"{SettingsDetailPage.PACKAGE}:id/layout_time_zone"
    TITLE_TEXT = "Date & Time"

    def is_page_displayed(self):
        return self.is_title_visible(self.TITLE_TEXT) and self.is_displayed(self.TIME_FORMAT)


class SettingsUnitsDialogPage(BasePage):
    PACKAGE = "com.aeke.fitnessmirror"
    TITLE = f"{PACKAGE}:id/tv_title"
    METRIC = f"{PACKAGE}:id/unit_metric"
    IMPERIAL = f"{PACKAGE}:id/unit_imperial"
    CANCEL = {"type": "text", "value": "Cancel"}
    OK = {"type": "text", "value": "OK"}

    def is_dialog_displayed(self):
        return self.device(text="Units").exists and self.is_displayed(self.METRIC)

    def dismiss(self):
        if self.device(text="Cancel").exists:
            self.click(self.CANCEL)
            self.device.sleep(0.4)
            return True
        return False


class SettingsAICorrectionDialogPage(BasePage):
    PACKAGE = "com.aeke.fitnessmirror"
    PANEL = f"{PACKAGE}:id/panel"
    CANCEL = f"{PACKAGE}:id/cancel"
    OK = f"{PACKAGE}:id/btn_ok"
    RELAXED = f"{PACKAGE}:id/layout_relaxed"
    STANDARD = f"{PACKAGE}:id/layout_standard"
    STRICT = f"{PACKAGE}:id/layout_strict"

    def is_dialog_displayed(self):
        return self.is_displayed(self.PANEL) and self.device(text="AI Correction Level").exists

    def dismiss(self):
        if self.is_displayed(self.CANCEL):
            self.click(self.CANCEL)
            self.device.sleep(0.4)
            return True
        return False


class SettingsResetDeviceDialogPage(BasePage):
    PACKAGE = "com.aeke.fitnessmirror"
    TIPS = f"{PACKAGE}:id/tv_tips"
    CLOSE = f"{PACKAGE}:id/iv_close"
    CANCEL = f"{PACKAGE}:id/tv_cancel"
    CONFIRM = f"{PACKAGE}:id/tv_sure"

    def is_dialog_displayed(self):
        return self.is_displayed(self.TIPS) and self.device(text="Cancel").exists

    def dismiss(self):
        if self.is_displayed(self.CANCEL):
            self.click(self.CANCEL)
            self.device.sleep(0.4)
            return True
        if self.is_displayed(self.CLOSE):
            self.click(self.CLOSE)
            self.device.sleep(0.4)
            return True
        return False
