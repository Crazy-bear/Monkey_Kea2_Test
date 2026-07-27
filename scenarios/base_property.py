# -*- coding: utf-8 -*-
"""
力量镜 Kea2 属性测试基类（设备需已预登录至主页）。
"""
import unittest

from pages.main_page import MainPage
from orchestrator.test_session import get_active_monitor


class FitnessMirrorPropertyTest(unittest.TestCase):
    """Kea2 注入 uiautomator2 Device 为 self.d。"""

    d = None

    def main_page(self):
        return MainPage(self.d)

    def on_main_page(self):
        return self.main_page().is_main_page_displayed()

    def set_perf_phase(self, name):
        monitor = get_active_monitor()
        if monitor:
            monitor.set_phase(name)

    def press_back_to_main(self, max_back=3):
        page = self.main_page()
        for _ in range(max_back):
            if page.is_main_page_displayed():
                return True
            self.d.press("back")
            self.d.sleep(1)
        return page.is_main_page_displayed()
