# -*- coding: utf-8 -*-
"""
Lifestyle Tab 及副页 Page Object（S1Pro 力量镜 v3.x）。

定位依据：
- S1Pro_UI/v3.1.0.7123/elements/Lifestyle_elements.md
- Lifestyle_Games / VSMode / Wallpaper / Speaker / ScreenCast 及 VS 子态 dump
"""
from pages.base_page import BasePage, _element_exists
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

    # 稳定性测试禁止自动进入（Wallpaper 易触发屏保黑屏）
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

    # 中英别名：哨兵/页判定用「任一命中」，不要求英文全齐
    ENTRY_TEXT_ALIASES = (
        (LABEL_GAMES, "游戏"),
        (LABEL_VS_MODE, "VS 模式", "对战"),
        (LABEL_WALLPAPER, "壁纸"),
        (LABEL_SPEAKER, "音箱", "扬声器"),
        (LABEL_SCREEN_CAST, "投屏", "Screen Mirroring"),
    )

    def _entry_visible(self):
        return self.has_any_entry()

    def has_any_entry(self):
        for aliases in self.ENTRY_TEXT_ALIASES:
            if any(_element_exists(self.device(text=label)) for label in aliases):
                return True
        return False

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


class LifestyleGamesPage(BasePage):
    """Games 列表 — GameListActivity。"""

    PACKAGE = "com.aeke.fitnessmirror"

    HOME_BUTTON = f"{PACKAGE}:id/home_iv"
    GAME_LIST = f"{PACKAGE}:id/recyclerView"
    GAME_ITEM = f"{PACKAGE}:id/total"

    _ANCHORS = (HOME_BUTTON, GAME_LIST)

    def is_games_page_displayed(self):
        hits = sum(1 for loc in self._ANCHORS if self.is_displayed(loc))
        return hits >= 2 or (
            self.is_displayed(self.GAME_LIST) and self.is_displayed(self.GAME_ITEM)
        )

    def press_back(self):
        if self.is_displayed(self.HOME_BUTTON):
            self.click(self.HOME_BUTTON)
            self.device.sleep(0.5)
            return True
        return False


class LifestyleVSModePage(BasePage):
    """VS Mode — PKPasswordInputActivity（开局页 / Join / Create）。"""

    PACKAGE = "com.aeke.fitnessmirror"

    LEFT_ICON = f"{PACKAGE}:id/ivLeftIcon"
    START_PK = f"{PACKAGE}:id/start_pk"
    TITLE = f"{PACKAGE}:id/tvTitle"
    BACK_BUTTON = f"{PACKAGE}:id/iv_back"
    JOIN_TAB = f"{PACKAGE}:id/ll_join"
    CREATE_TAB = f"{PACKAGE}:id/ll_create"
    TV_JOIN = f"{PACKAGE}:id/tv_join"
    TV_CREATE = f"{PACKAGE}:id/tv_create"
    KEYBOARD = f"{PACKAGE}:id/ll_keyboard"
    ENTER_ROOM = f"{PACKAGE}:id/tv_addroom"
    SELECT_COURSE = f"{PACKAGE}:id/tv_select_course"
    COURSE_LIST = f"{PACKAGE}:id/rv_course_list"

    TITLE_TEXT = "VS Mode"
    START_PK_TEXT = "Start PK"
    JOIN_TEXT = "Join room"
    CREATE_TEXT = "Create room"
    SELECT_COURSE_TEXT = "Select course"

    def is_landing_displayed(self):
        if self.is_displayed(self.START_PK):
            return True
        return self.device(text=self.START_PK_TEXT).exists and self.is_displayed(self.TITLE)

    def is_join_room_displayed(self):
        if self.is_displayed(self.KEYBOARD) and self.is_displayed(self.ENTER_ROOM):
            return True
        return self.device(text=self.JOIN_TEXT).exists and self.is_displayed(self.KEYBOARD)

    def is_create_room_displayed(self):
        if self.is_displayed(self.SELECT_COURSE) and self.is_displayed(self.COURSE_LIST):
            return True
        return self.device(text=self.SELECT_COURSE_TEXT).exists and self.is_displayed(
            self.COURSE_LIST
        )

    def is_vs_mode_page_displayed(self):
        return (
            self.is_landing_displayed()
            or self.is_join_room_displayed()
            or self.is_create_room_displayed()
        )

    def tap_start_pk(self):
        if self.is_displayed(self.START_PK):
            self.click(self.START_PK)
            self.device.sleep(1)
            return True
        return self._click_text(self.START_PK_TEXT)

    def switch_to_create_room(self):
        if self.is_displayed(self.CREATE_TAB):
            self.click(self.CREATE_TAB)
            self.device.sleep(0.8)
            return True
        return self._click_text(self.CREATE_TEXT)

    def switch_to_join_room(self):
        if self.is_displayed(self.JOIN_TAB):
            self.click(self.JOIN_TAB)
            self.device.sleep(0.8)
            return True
        return self._click_text(self.JOIN_TEXT)

    def press_back(self):
        for loc in (self.BACK_BUTTON, self.LEFT_ICON):
            if self.is_displayed(loc):
                self.click(loc)
                self.device.sleep(0.5)
                return True
        return False

    def _click_text(self, text):
        node = self.device(text=text)
        if _element_exists(node, timeout=2):
            node.click()
            self.device.sleep(0.5)
            return True
        return False


class LifestyleSpeakerPage(BasePage):
    """Speaker — BtSinkAudioActivity（权限弹窗 / 配对引导主页）。"""

    PACKAGE = "com.aeke.fitnessmirror"

    # 蓝牙权限弹窗（Lifestyle_Speaker_elements.md）
    DIALOG_TITLE = f"{PACKAGE}:id/tv_title"
    DIALOG_HINT = f"{PACKAGE}:id/tv_hint"
    BTN_ALLOW = f"{PACKAGE}:id/tv_confirm"
    BTN_QUIT = f"{PACKAGE}:id/tv_cancel"
    DIALOG_CLOSE = f"{PACKAGE}:id/iv_close"

    # 配对引导主页（Lifestyle_Speaker_Main_elements.md）
    CLOSE_BUTTON = f"{PACKAGE}:id/btn_close"
    PAGE_TITLE = f"{PACKAGE}:id/tv_title"
    GUIDE_TEXT = f"{PACKAGE}:id/textView2"
    DEVICE_NAME = f"{PACKAGE}:id/bt_sink_name"
    PAIRING_HINT = f"{PACKAGE}:id/tv_some_id"
    LOADING_ANIM = f"{PACKAGE}:id/loading_anim"

    BT_PROMPT_TITLE = "Bluetooth Required"
    SPEAKER_TITLE = "Speaker"
    ALLOW_TEXT = "Allow"
    QUIT_TEXT = "Quit"

    def is_bluetooth_prompt_displayed(self):
        if self.is_displayed(self.BTN_QUIT) and self.is_displayed(self.BTN_ALLOW):
            return True
        return self.device(text=self.BT_PROMPT_TITLE).exists

    def is_speaker_main_displayed(self):
        if self.is_displayed(self.CLOSE_BUTTON) and self.is_displayed(self.DEVICE_NAME):
            return True
        if self.device(text=self.SPEAKER_TITLE).exists and self.is_displayed(self.GUIDE_TEXT):
            return True
        return self.is_displayed(self.CLOSE_BUTTON) and self.is_displayed(self.GUIDE_TEXT)

    def is_speaker_page_displayed(self):
        return self.is_bluetooth_prompt_displayed() or self.is_speaker_main_displayed()

    def dismiss_without_allow(self):
        """稳定性路径：Quit / 关闭，不点 Allow。"""
        if self.is_displayed(self.BTN_QUIT):
            self.click(self.BTN_QUIT)
            self.device.sleep(0.5)
            return True
        if self.is_displayed(self.DIALOG_CLOSE):
            self.click(self.DIALOG_CLOSE)
            self.device.sleep(0.5)
            return True
        node = self.device(text=self.QUIT_TEXT)
        if _element_exists(node, timeout=1):
            node.click()
            self.device.sleep(0.5)
            return True
        return False

    def press_back(self):
        if self.is_bluetooth_prompt_displayed():
            return self.dismiss_without_allow()
        if self.is_displayed(self.CLOSE_BUTTON):
            self.click(self.CLOSE_BUTTON)
            self.device.sleep(0.5)
            return True
        return self.dismiss_without_allow()


class LifestyleScreenCastPage(BasePage):
    """Screen Cast — ProjectionScreenActivity。"""

    PACKAGE = "com.aeke.fitnessmirror"

    CLOSE_BUTTON = f"{PACKAGE}:id/btn_close"
    WIFI_INFO = f"{PACKAGE}:id/ll_wifiInfo"
    DEVICE_NAME = f"{PACKAGE}:id/tv_deviceName"
    CONTENT_PAGER = f"{PACKAGE}:id/vp_content"
    METHOD_TYPE = f"{PACKAGE}:id/tv_type"

    TITLE_TEXT = "Screen Cast"

    _ANCHORS = (CLOSE_BUTTON, WIFI_INFO, DEVICE_NAME)

    def is_screen_cast_page_displayed(self):
        hits = sum(1 for loc in self._ANCHORS if self.is_displayed(loc))
        if hits >= 2:
            return True
        return self.device(text=self.TITLE_TEXT).exists and self.is_displayed(
            self.CLOSE_BUTTON
        )

    def press_back(self):
        if self.is_displayed(self.CLOSE_BUTTON):
            self.click(self.CLOSE_BUTTON)
            self.device.sleep(0.5)
            return True
        return False


class LifestyleWallpaperPage(BasePage):
    """Wallpaper — ScreenProtectActivity（自动导航仍禁用，仅供断言/手动路径）。"""

    PACKAGE = "com.aeke.fitnessmirror"

    CLOSE_BUTTON = f"{PACKAGE}:id/btn_close"
    TITLE = f"{PACKAGE}:id/tv_title"
    PROTECT_SWITCH = f"{PACKAGE}:id/switch_btn_protect"
    BANNER = f"{PACKAGE}:id/banner_view"
    CURRENT_LABEL = f"{PACKAGE}:id/current_screen_protect_tv"

    TITLE_TEXT = "Wallpaper"

    # 稳定性测试禁止点击
    BLOCKED_IDS = frozenset({PROTECT_SWITCH})

    def is_wallpaper_page_displayed(self):
        if self.is_displayed(self.TITLE) and self.is_displayed(self.CLOSE_BUTTON):
            return True
        return self.device(text=self.TITLE_TEXT).exists and self.is_displayed(
            self.BANNER
        )

    def press_back(self):
        if self.is_displayed(self.CLOSE_BUTTON):
            self.click(self.CLOSE_BUTTON)
            self.device.sleep(0.5)
            return True
        return False
