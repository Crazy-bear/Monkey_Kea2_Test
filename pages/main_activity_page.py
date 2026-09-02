# -*- coding: utf-8 -*-
"""
MainActivity 公共 Page Object：顶栏 Tab、头像、应用内控制栏。

Home / Lifestyle 两个 Tab 页均在此 Activity 内，具体业务面见 home_page / lifestyle_page。
"""
from pages.base_page import BasePage, _element_exists


class MainActivityPage(BasePage):
    """com.aeke.fitnessmirror.home.MainActivity 公共控件与导航。"""

    PACKAGE = "com.aeke.fitnessmirror"

    # 顶栏 Tab（中文：首页 / 娱乐；界面文案 Home / Lifestyle）
    HOME_TAB = "com.aeke.fitnessmirror:id/tv_page_home"
    LIFESTYLE_TAB = "com.aeke.fitnessmirror:id/tv_life_style"
    MAIN_TITLE_BAR = "com.aeke.fitnessmirror:id/ctl_main_title"
    PROFILE_BUTTON = "com.aeke.fitnessmirror:id/iv_head"

    # 应用内控制栏（WiFi/蓝牙/亮度等）
    CONTROL_PANEL_ROOT = "com.aeke.fitnessmirror:id/rl_control_root"
    CONTROL_OVERLAY_MASK = "com.aeke.fitnessmirror:id/v_overlay_mask"
    CONTROL_WIFI_PANEL = "com.aeke.fitnessmirror:id/rl_sys_wifi"
    CONTROL_DISMISS_IDS = (
        "com.aeke.fitnessmirror:id/cancel",
        "com.aeke.fitnessmirror:id/tv_cancel",
        "com.aeke.fitnessmirror:id/tv_wifi_cancel",
    )
    REMINDER_CLOSE = "com.aeke.fitnessmirror:id/iv_close"

    _CONTROL_PANEL_MARKERS = (
        CONTROL_PANEL_ROOT,
        CONTROL_WIFI_PANEL,
        CONTROL_OVERLAY_MASK,
        "com.aeke.fitnessmirror:id/et_wifi_input_pwd",
    )

    def switch_to_home_tab(self):
        """切换到首页 Tab（界面文案 Home）。"""
        if self.is_displayed(self.HOME_TAB):
            self.click(self.HOME_TAB)
            self.device.sleep(0.5)
            return True
        return False

    def switch_to_lifestyle_tab(self):
        """切换到娱乐 Tab（界面文案 Lifestyle）。"""
        if self.is_displayed(self.LIFESTYLE_TAB):
            self.click(self.LIFESTYLE_TAB)
            self.device.sleep(0.8)
            return True
        return False

    def is_control_panel_open(self):
        return any(self.is_displayed(loc) for loc in self._CONTROL_PANEL_MARKERS)

    def dismiss_control_panel(self):
        if not self.is_control_panel_open():
            return False
        for rid in self.CONTROL_DISMISS_IDS:
            if self.is_displayed(rid):
                self.click(rid)
                self.device.sleep(0.5)
                if not self.is_control_panel_open():
                    return True
        self.device.press("back")
        self.device.sleep(0.5)
        return not self.is_control_panel_open()

    def dismiss_reminder_banner(self):
        if self.is_displayed(self.REMINDER_CLOSE):
            self.click(self.REMINDER_CLOSE)
            self.device.sleep(0.3)
            return True
        return False

    def _dismiss_overlays(self, max_panel_dismiss=3):
        for _ in range(max_panel_dismiss):
            if not self.is_control_panel_open():
                break
            self.dismiss_control_panel()
        self.dismiss_reminder_banner()

    def go_to_profile(self):
        self.click(self.PROFILE_BUTTON)

    def _click_first_text(self, *labels):
        for label in labels:
            node = self.device(text=label)
            if _element_exists(node, timeout=2):
                node.click()
                return True
        return False
