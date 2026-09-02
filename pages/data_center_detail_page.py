# -*- coding: utf-8 -*-
"""
数据中心详情页 Page Object（AEKE 力量镜 v3.x）。

定位依据：S1Pro_UI/v3.0.0.6858/elements/DataCenterDetail_elements.md
Activity：com.aeke.fitnessmirror.activity.TrainingDataCentreActivity
"""
from pages.base_page import BasePage


class DataCenterDetailPage(BasePage):
    """Data Center 详情 — TrainingDataCentreActivity。"""

    PACKAGE = "com.aeke.fitnessmirror"

    BACK_BUTTON = f"{PACKAGE}:id/ivLeftIcon"
    TITLE = f"{PACKAGE}:id/tvTitle"
    DATE_RANGE = f"{PACKAGE}:id/tv_date_range"
    DATE_PREV = f"{PACKAGE}:id/iv_date_left"
    DATE_NEXT = f"{PACKAGE}:id/iv_date_right"
    THIS_WEEK = f"{PACKAGE}:id/tv_this_week"

    TOTAL_SUMMARY = f"{PACKAGE}:id/ll_total_infos"
    SESSION_VALUE = f"{PACKAGE}:id/tv_session_num"
    SESSION_UNIT = f"{PACKAGE}:id/tv_session_unit"
    DURATION_VALUE = f"{PACKAGE}:id/tv_duration"
    DURATION_UNIT = f"{PACKAGE}:id/tv_duration_unit"
    VOLUME_VALUE = f"{PACKAGE}:id/tv_total_volum"
    VOLUME_UNIT = f"{PACKAGE}:id/tv_total_volum_unit"
    KCAL_VALUE = f"{PACKAGE}:id/tv_total_kcal"
    KCAL_UNIT = f"{PACKAGE}:id/tv_total_kcal_unit"

    PROGRESS_PANEL = f"{PACKAGE}:id/ctl_workout_progress"
    PROGRESS_TITLE = f"{PACKAGE}:id/tv_progress_title"
    TAB_VOLUME = f"{PACKAGE}:id/tv_progress_volum"
    TAB_CALORIES = f"{PACKAGE}:id/tv_progress_calories"
    WEEK_CHART = f"{PACKAGE}:id/wrbv_week_data"

    PREFERENCES_PANEL = f"{PACKAGE}:id/ctl_workout_preferences"
    PREFERENCES_TITLE = f"{PACKAGE}:id/tv_preferences_title"
    TRAINING_LIST = f"{PACKAGE}:id/ll_training_list"

    TITLE_TEXT = "Data Center"
    PROGRESS_TEXT = "Progress"
    PREFERENCES_TEXT = "Preferences"
    THIS_WEEK_TEXT = "This week"

    SUMMARY_LOCATORS = (
        SESSION_VALUE,
        DURATION_VALUE,
        VOLUME_VALUE,
        KCAL_VALUE,
    )

    _DETAIL_ANCHORS = (BACK_BUTTON, TOTAL_SUMMARY, PROGRESS_PANEL, PREFERENCES_PANEL)

    def is_data_center_detail_displayed(self):
        hits = sum(1 for loc in self._DETAIL_ANCHORS if self.is_displayed(loc))
        if hits < 3:
            return False
        return self.device(text=self.TITLE_TEXT).exists or self.is_displayed(self.TOTAL_SUMMARY)

    def summary_stats_visible(self):
        if not self.is_data_center_detail_displayed():
            return False
        labels_ok = (
            self.device(text="Workouts").exists
            and self.device(text="Duration").exists
            and self.device(text="Volume").exists
            and self.device(text="Calories").exists
        )
        if not labels_ok:
            return False
        return all(self.is_displayed(loc) for loc in self.SUMMARY_LOCATORS)

    def progress_section_visible(self):
        return (
            self.is_displayed(self.PROGRESS_PANEL)
            and self.device(text=self.PROGRESS_TEXT).exists
            and self.is_displayed(self.WEEK_CHART)
        )

    def preferences_section_visible(self):
        return (
            self.is_displayed(self.PREFERENCES_PANEL)
            and self.device(text=self.PREFERENCES_TEXT).exists
            and self.is_displayed(self.TRAINING_LIST)
        )

    def press_back(self):
        if self.is_displayed(self.BACK_BUTTON):
            self.click(self.BACK_BUTTON)
            self.device.sleep(0.5)
            return True
        return False

    def switch_progress_tab(self, tab_locator):
        if self.is_displayed(tab_locator):
            self.click(tab_locator)
            self.device.sleep(0.3)
            return True
        return False
