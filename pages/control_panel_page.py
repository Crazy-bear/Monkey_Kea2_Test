# -*- coding: utf-8 -*-
"""
应用内控制栏 Page Object（AEKE 力量镜 v3.x）。

定位依据：S1Pro_UI/v3.0.0.6858/elements/Home_ControlPanel_*_elements.md
"""
from pages.main_activity_page import MainActivityPage


class ControlPanelPage(MainActivityPage):
    """MainActivity 内下拉控制栏 — 亮度/音量/蓝牙/WiFi/灯带。"""

    TOP_STRIP = f"{MainActivityPage.PACKAGE}:id/top_strip"
    ANCHOR = f"{MainActivityPage.PACKAGE}:id/iv_anchor"

    SYS_BRIGHT = f"{MainActivityPage.PACKAGE}:id/sys_bright"
    SYS_VOICE = f"{MainActivityPage.PACKAGE}:id/sys_voice"
    SYS_BLE = f"{MainActivityPage.PACKAGE}:id/sys_ble"
    SYS_WIFI = f"{MainActivityPage.PACKAGE}:id/sys_wifi"
    SYS_LED = f"{MainActivityPage.PACKAGE}:id/sys_led"

    WIFI_PANEL = f"{MainActivityPage.PACKAGE}:id/rl_sys_wifi"
    WIFI_TITLE = f"{MainActivityPage.PACKAGE}:id/tv_wifi_title"
    WIFI_REFRESH = f"{MainActivityPage.PACKAGE}:id/tv_wifi_refresh"
    WIFI_FORGET = f"{MainActivityPage.PACKAGE}:id/tv_wifi_delete_curr"
    WIFI_FORGET_AREA = f"{MainActivityPage.PACKAGE}:id/ctl_wifi_title_right"
    WIFI_FORGET_TEXT = "Forget"

    # 稳定性测试禁止点击（Forget 会断开当前 WiFi）
    BLOCKED_WIFI_LOCATORS = frozenset({WIFI_FORGET, WIFI_FORGET_AREA})
    BLOCKED_WIFI_LABELS = frozenset({WIFI_FORGET_TEXT, "忘记"})

    BLE_PANEL = f"{MainActivityPage.PACKAGE}:id/sys_ble_rl2_new"
    BLE_TITLE = f"{MainActivityPage.PACKAGE}:id/sys_ble_title"
    BRIGHTNESS_PANEL = f"{MainActivityPage.PACKAGE}:id/sys_progress_ll"
    BRIGHTNESS_TITLE = f"{MainActivityPage.PACKAGE}:id/sys_bar_progress_title"
    LED_PANEL = f"{MainActivityPage.PACKAGE}:id/sys_led_rl"
    LED_TITLE = f"{MainActivityPage.PACKAGE}:id/sys_led_title_tv"
    VOLUME_MUTE = f"{MainActivityPage.PACKAGE}:id/sb_volum_mute"

    MENU_BUTTONS = (SYS_BRIGHT, SYS_VOICE, SYS_BLE, SYS_WIFI, SYS_LED)

    def open_control_panel(self):
        if self.is_control_panel_open():
            return True
        for loc in (self.TOP_STRIP, self.ANCHOR):
            if self.is_displayed(loc):
                self.click(loc)
                self.device.sleep(0.6)
                if self.is_control_panel_open():
                    return True
        return self.is_control_panel_open()

    def switch_tab(self, tab_locator):
        if not self.open_control_panel():
            return False
        if self.is_displayed(tab_locator):
            self.click(tab_locator)
            self.device.sleep(0.5)
            return True
        return False

    def click(self, locator):
        if isinstance(locator, str) and locator in self.BLOCKED_WIFI_LOCATORS:
            return
        if isinstance(locator, dict):
            value = locator.get("value", "")
            if locator.get("type") == "text" and value in self.BLOCKED_WIFI_LABELS:
                return
        super().click(locator)

    def is_brightness_panel_open(self):
        return self.is_displayed(self.BRIGHTNESS_PANEL) and self.device(text="Brightness").exists

    def is_volume_panel_open(self):
        return self.is_displayed(self.BRIGHTNESS_PANEL) and self.device(text="Volume").exists

    def is_wifi_panel_open(self):
        return self.is_displayed(self.WIFI_PANEL)

    def is_bluetooth_panel_open(self):
        return self.is_displayed(self.BLE_PANEL)

    def is_led_panel_open(self):
        return self.is_displayed(self.LED_PANEL)
