# -*- coding: utf-8 -*-
"""
Lifestyle Tab Page Object（AEKE 力量镜 v3.x）。

定位依据：S1Pro_UI/v3.0.0.6858/elements/Lifestyle_elements.md
"""
from pages.base_page import _element_exists
from pages.main_activity_page import MainActivityPage


class LifestylePage(MainActivityPage):
    """娱乐 Tab — Games / VS Mode / Wallpaper / Speaker / Screen Cast。"""

    FUNCS_LIST = "com.aeke.fitnessmirror:id/rv_funcs"
    ENTRY_ROOT = "com.aeke.fitnessmirror:id/rl_root"

    LABEL_GAMES = "Games"
    LABEL_VS_MODE = "VS Mode"
    LABEL_WALLPAPER = "Wallpaper"
    LABEL_SPEAKER = "Speaker"
    LABEL_SCREEN_CAST = "Screen Cast"

    # 稳定性测试禁止点击（Wallpaper 进入后设备黑屏）
    BLOCKED_LABELS = frozenset({LABEL_WALLPAPER, "壁纸"})

    ENTRY_LABELS = (
        LABEL_GAMES,
        LABEL_VS_MODE,
        LABEL_WALLPAPER,
        LABEL_SPEAKER,
        LABEL_SCREEN_CAST,
    )

    _LIFESTYLE_ANCHORS = (
        MainActivityPage.MAIN_TITLE_BAR,
        MainActivityPage.LIFESTYLE_TAB,
        FUNCS_LIST,
    )

    def _entry_visible(self):
        return any(_element_exists(self.device(text=label)) for label in self.ENTRY_LABELS)

    def is_lifestyle_page_displayed(self):
        hits = sum(1 for loc in self._LIFESTYLE_ANCHORS if self.is_displayed(loc))
        if hits < 2:
            return False
        return self._entry_visible()

    def ensure_lifestyle_surface(self, max_panel_dismiss=3):
        self._dismiss_overlays(max_panel_dismiss)
        self.switch_to_lifestyle_tab()
        return self.is_lifestyle_page_displayed()

    def go_to_entry(self, *labels):
        if any(label in self.BLOCKED_LABELS for label in labels):
            return False
        self.ensure_lifestyle_surface()
        return self._click_first_text(*labels)

    def go_to_games(self):
        return self.go_to_entry(self.LABEL_GAMES, "游戏")

    def go_to_vs_mode(self):
        return self.go_to_entry(self.LABEL_VS_MODE, "VS 模式", "对战")

    def go_to_wallpaper(self):
        return self.go_to_entry(self.LABEL_WALLPAPER, "壁纸")

    def go_to_speaker(self):
        return self.go_to_entry(self.LABEL_SPEAKER, "音箱", "扬声器")

    def go_to_screen_cast(self):
        return self.go_to_entry(self.LABEL_SCREEN_CAST, "投屏", "Screen Mirroring")
