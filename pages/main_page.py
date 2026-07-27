# -*- coding: utf-8 -*-
"""
主界面 Page Object（AEKE 力量镜 v3.x Home 页）。

定位依据：项目根目录 window_dump.xml（2026-07-23，包名 com.aeke.fitnessmirror，Home Tab）。
"""
from pages.base_page import BasePage


class MainPage(BasePage):
    """Home 主页 — Free Workout / Courses / Programs 等入口。"""

    PACKAGE = "com.aeke.fitnessmirror"

    # 顶栏 Tab
    HOME_TAB = "com.aeke.fitnessmirror:id/tv_page_home"
    LIFESTYLE_TAB = "com.aeke.fitnessmirror:id/tv_life_style"
    MAIN_TITLE_BAR = "com.aeke.fitnessmirror:id/ctl_main_title"

    # Home 页业务入口（与旧版常量名兼容）
    START_BUTTON = "com.aeke.fitnessmirror:id/grf_free_traing"       # Free Workout / 随心练
    AI_COACH_BUTTON = "com.aeke.fitnessmirror:id/grf_ai_coach"       # AI Coach
    COURSE_BUTTON = "com.aeke.fitnessmirror:id/grf_all_course"       # Courses / 精品课程
    ASSESSMENT_BUTTON = "com.aeke.fitnessmirror:id/grf_evaluation"   # Assessment / 运动测评
    PLAN_BUTTON = "com.aeke.fitnessmirror:id/grf_sports_plan"        # Programs / 运动计划
    PROFILE_BUTTON = "com.aeke.fitnessmirror:id/iv_head"             # 头像 → 个人中心

    _HOME_ANCHORS = (MAIN_TITLE_BAR, START_BUTTON, HOME_TAB)

    def ensure_home_tab(self):
        """确保处于 Home Tab（若在 Lifestyle 则切回）。"""
        if self.is_displayed(self.HOME_TAB):
            self.click(self.HOME_TAB)
            self.device.sleep(0.5)

    def is_main_page_displayed(self):
        """至少命中两个主页锚点即视为在 Home 主页。"""
        hits = sum(1 for loc in self._HOME_ANCHORS if self.is_displayed(loc))
        return hits >= 2

    def go_to_suixinlian(self):
        self.ensure_home_tab()
        self.click(self.START_BUTTON)

    def go_to_jingpin_course(self):
        self.ensure_home_tab()
        self.click(self.COURSE_BUTTON)

    def go_to_profile(self):
        self.click(self.PROFILE_BUTTON)

    def go_to_plan(self):
        self.ensure_home_tab()
        self.click(self.PLAN_BUTTON)

    def go_to_assessment(self):
        self.ensure_home_tab()
        self.click(self.ASSESSMENT_BUTTON)

    def go_to_lifestyle_tab(self):
        self.click(self.LIFESTYLE_TAB)
        self.device.sleep(1)

    def _click_first_text(self, *labels):
        for label in labels:
            node = self.device(text=label)
            if node.exists(timeout=2):
                node.click()
                return True
        return False

    def go_to_music(self):
        self.go_to_lifestyle_tab()
        self._click_first_text("Music", "音乐")

    def go_to_karaoke(self):
        self.go_to_lifestyle_tab()
        self._click_first_text("Karaoke", "K歌", "卡拉OK")

    def go_to_guide(self):
        self.go_to_lifestyle_tab()
        self._click_first_text("Guide", "使用指南", "User Guide")
