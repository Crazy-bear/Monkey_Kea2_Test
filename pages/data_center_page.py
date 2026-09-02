# -*- coding: utf-8 -*-
"""
数据中心（Today's Effort）Page Object — Home 页运动数据条。

定位依据：S1Pro_UI/v3.0.0.6858/elements/Home_NoReminder_elements.md
提醒条态见 Home_elements.md（ll_reminder / tv_msg）。
"""
from pages.main_activity_page import MainActivityPage


class DataCenterPage(MainActivityPage):
    """Home Tab 内 Today's Effort 数据条 — 点击进入数据中心详情。"""

    PACKAGE = "com.aeke.fitnessmirror"

    STRIP_ROOT = f"{PACKAGE}:id/hsr_tips"
    REPORT_ENTRY = f"{PACKAGE}:id/ll_report"
    REPORT_INFOS = f"{PACKAGE}:id/ctl_report_infos"

    TIME_VALUE = f"{PACKAGE}:id/tv_time_length"
    TIME_UNIT = f"{PACKAGE}:id/tv_time_unit"
    KCAL_VALUE = f"{PACKAGE}:id/tv_kcal"
    KCAL_UNIT = f"{PACKAGE}:id/tv_kcal_unit"
    WEIGHT_VALUE = f"{PACKAGE}:id/tv_weight"
    WEIGHT_UNIT = f"{PACKAGE}:id/tv_weight_unit"

    REMINDER_CONTAINER = f"{PACKAGE}:id/ll_reminder"
    REMINDER_MSG = f"{PACKAGE}:id/tv_msg"
    REMINDER_START = {"type": "text", "value": "Start"}

    LABEL_TEXT = "Today's Effort"
    TIME_UNIT_TEXT = "min"
    KCAL_UNIT_TEXT = "kcal"
    WEIGHT_UNIT_TEXT = "kg"

    STAT_LOCATORS = (
        TIME_VALUE,
        TIME_UNIT,
        KCAL_VALUE,
        KCAL_UNIT,
        WEIGHT_VALUE,
        WEIGHT_UNIT,
    )

    _EFFORT_ANCHORS = (REPORT_ENTRY, REPORT_INFOS, STRIP_ROOT)

    def is_reminder_strip_visible(self):
        return self.is_displayed(self.REMINDER_CONTAINER)

    def is_effort_label_visible(self):
        return self.text_exists(self.LABEL_TEXT)

    def is_effort_strip_visible(self):
        if not self.text_exists(self.LABEL_TEXT):
            return False
        hits = sum(1 for loc in self._EFFORT_ANCHORS if self.is_displayed(loc))
        return hits >= 2

    def ensure_effort_strip(self, max_panel_dismiss=3):
        """关闭提醒条/控制栏遮罩，确保处于 Today's Effort 数据条态。"""
        self._dismiss_overlays(max_panel_dismiss)
        self.switch_to_home_tab()
        self.dismiss_reminder_banner()
        self.device.sleep(0.3)
        return self.is_effort_strip_visible()

    def effort_stats_visible(self):
        if not self.is_effort_strip_visible():
            return False
        units_ok = (
            self.text_exists(self.TIME_UNIT_TEXT)
            and self.text_exists(self.KCAL_UNIT_TEXT)
            and self.text_exists(self.WEIGHT_UNIT_TEXT)
        )
        if not units_ok:
            return False
        return all(self.is_displayed(loc) for loc in self.STAT_LOCATORS)

    def go_to_data_center(self):
        self.ensure_effort_strip()
        if self.is_displayed(self.REPORT_ENTRY):
            self.click(self.REPORT_ENTRY)
            self.device.sleep(0.8)
            return True
        return False
