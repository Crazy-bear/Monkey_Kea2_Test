# -*- coding: utf-8 -*-
"""BasePage 与 MainPage 单元测试（mock device）。"""

import os
import re
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


class TestMainPage:
    def test_locators_match_window_dump(self):
        """window_dump.xml 中的 resource-id 应与 MainPage 常量一致。"""
        from pages.main_page import MainPage

        dump_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "window_dump.xml"
        )
        if not os.path.isfile(dump_path):
            return
        xml = open(dump_path, encoding="utf-8").read()
        ids = [
            MainPage.HOME_TAB,
            MainPage.START_BUTTON,
            MainPage.COURSE_BUTTON,
            MainPage.PLAN_BUTTON,
            MainPage.ASSESSMENT_BUTTON,
            MainPage.PROFILE_BUTTON,
        ]
        for rid in ids:
            assert rid in xml, f"window_dump 缺少 {rid}"

    def test_is_main_page_requires_two_anchors(self):
        from pages.main_page import MainPage

        device = MagicMock()

        def exists_side_effect(**kwargs):
            m = MagicMock()
            rid = kwargs.get("resourceId")
            m.exists = rid in (
                MainPage.MAIN_TITLE_BAR,
                MainPage.START_BUTTON,
            )
            return m

        device.side_effect = exists_side_effect
        page = MainPage(device)
        assert page.is_main_page_displayed() is True

    def test_english_locator_names(self):
        from pages.main_page import MainPage

        assert hasattr(MainPage, "START_BUTTON")
        assert hasattr(MainPage, "COURSE_BUTTON")
        assert MainPage.START_BUTTON.endswith("grf_free_traing")
