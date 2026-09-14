# -*- coding: utf-8 -*-
"""
屏保页 Page Object（S1Pro 力量镜 v3.x）。

定位依据：S1Pro_UI/v3.1.0.7123/elements/Screensaver_elements.md
用途：检测到屏保后点击屏幕退出；退出后可能仍登录主页，也可能落到登录页。
"""
from pages.base_page import BasePage, _is_static_checker_device


class ScreensaverPage(BasePage):
    """壁纸屏保 — ScreenProjectShowActivity。"""

    PACKAGE = "com.aeke.fitnessmirror"
    ACTIVITY = f"{PACKAGE}.screen.ScreenProjectShowActivity"

    SCREEN_IMAGE = f"{PACKAGE}:id/screen_image"
    TIME_HOUR = f"{PACKAGE}:id/time_hour"
    TIME_MINUTE = f"{PACKAGE}:id/time_minute"
    DATE_INFO = f"{PACKAGE}:id/chinese_data_info"

    _ANCHORS = (SCREEN_IMAGE, TIME_HOUR, TIME_MINUTE)

    def is_screensaver_displayed(self):
        hits = sum(1 for loc in self._ANCHORS if self.is_displayed(loc))
        if hits >= 2:
            return True
        # 屏保节点少，双锚点即可；再兜底 Activity 名
        if _is_static_checker_device(self.device):
            return hits >= 1 and self.is_displayed(self.SCREEN_IMAGE)
        try:
            act = (self.device.app_current() or {}).get("activity") or ""
            if "ScreenProjectShowActivity" in act:
                return True
        except Exception:
            pass
        return False

    def dismiss_by_tap(self):
        """点击屏幕中心退出屏保。"""
        if _is_static_checker_device(self.device):
            return False
        try:
            w, h = self.device.window_size()
            self.device.click(w // 2, h // 2)
        except Exception:
            try:
                self.device.screen_on()
            except Exception:
                return False
        self.device.sleep(2.0)
        return not self.is_screensaver_displayed()
