# -*- coding: utf-8 -*-
"""
悬浮 Touch Page Object（AEKE 力量镜 v3.x）。

定位依据：
- S1Pro_UI/v3.0.0.6858/elements/FloatingTouch_elements.md（收起态）
- S1Pro_UI/v3.0.0.6858/elements/TouchMenu_elements.md（展开态）

悬浮层为 APPLICATION_OVERLAY，需 uiautomator2 dump_hierarchy 才能完整捕获。
"""
from pages.main_activity_page import MainActivityPage


class FloatingTouchPage(MainActivityPage):
    """悬浮 Touch 球与展开菜单 — MainActivity 上的 SYSTEM_ALERT_WINDOW 层。"""

    PACKAGE = "com.aeke.fitnessmirror"

    FAB_ROOT = f"{PACKAGE}:id/container_touch_2"
    FAB_CONTRACT = f"{PACKAGE}:id/layout_contract_2"
    FAB_ICON = f"{PACKAGE}:id/iv_contract_album_img_2"
    MENU_EXPAND = f"{PACKAGE}:id/layout_expand"
    MENU_BG = f"{PACKAGE}:id/touch_layout_bg"

    FOLD_BUTTON = f"{PACKAGE}:id/go_back_btn"
    OVERLAY_HOME = f"{PACKAGE}:id/go_home_btn"
    MUSIC_PANEL = f"{PACKAGE}:id/float_music_fl"
    MUSIC_STATUS = f"{PACKAGE}:id/no_kg_play"
    BTN_PREVIOUS = f"{PACKAGE}:id/btn_previous"
    BTN_TOGGLE = f"{PACKAGE}:id/btn_toggle"
    BTN_NEXT = f"{PACKAGE}:id/btn_next"
    VOLUME_SEEKBAR = f"{PACKAGE}:id/seekbar_volume"

    TOOLBAR = f"{PACKAGE}:id/all_tool"
    RETRACT_ROPE = f"{PACKAGE}:id/retrieve_the_rope"
    SLEEP = f"{PACKAGE}:id/sleep"
    WALLPAPER = f"{PACKAGE}:id/screen"
    BOTTOM_TOOLS = f"{PACKAGE}:id/bottom_tool_layout"

    LABEL_FOLD = "Fold"
    LABEL_HOME = "Home"
    LABEL_TOOLBAR = "Toolbar"
    LABEL_RETRACT = "Retract rope"
    LABEL_SLEEP = "Sleep"
    LABEL_WALLPAPER = "Wallpaper"

    # 稳定性测试禁止点击（进入后设备黑屏）
    BLOCKED_TOOL_IDS = frozenset({SLEEP, WALLPAPER})
    BLOCKED_LABELS = frozenset({LABEL_SLEEP, LABEL_WALLPAPER})

    TOOL_ITEMS = (
        (TOOLBAR, LABEL_TOOLBAR),
        (RETRACT_ROPE, LABEL_RETRACT),
        (SLEEP, LABEL_SLEEP),
        (WALLPAPER, LABEL_WALLPAPER),
    )

    _FAB_ANCHORS = (FAB_ROOT, FAB_CONTRACT, FAB_ICON)
    _MENU_ANCHORS = (MENU_EXPAND, FOLD_BUTTON, BOTTOM_TOOLS)

    def is_fab_visible(self):
        return self.is_displayed(self.FAB_ROOT)

    def is_menu_open(self):
        if self.is_displayed(self.MENU_EXPAND):
            return True
        if self.is_displayed(self.FOLD_BUTTON):
            return True
        hits = sum(1 for loc in self._MENU_ANCHORS if self.is_displayed(loc))
        return hits >= 2

    def ensure_fab_visible(self, max_panel_dismiss=3):
        self._dismiss_overlays(max_panel_dismiss)
        self.switch_to_home_tab()
        self.dismiss_reminder_banner()
        return self.is_fab_visible()

    def open_menu(self):
        if not self.ensure_fab_visible():
            return False
        if self.is_menu_open():
            return True
        for loc in (self.FAB_ICON, self.FAB_CONTRACT, self.FAB_ROOT):
            if self.is_displayed(loc):
                self.click(loc)
                self.device.sleep(0.8)
                break
        return self.is_menu_open()

    def close_menu(self):
        if not self.is_menu_open():
            return True
        if self.is_displayed(self.FOLD_BUTTON):
            self.click(self.FOLD_BUTTON)
            self.device.sleep(0.6)
        else:
            self.device.press("back")
            self.device.sleep(0.5)
        return not self.is_menu_open()

    def click_tool(self, locator):
        if locator in self.BLOCKED_TOOL_IDS:
            return False
        self.click(locator)
        return True

    def click(self, locator):
        if isinstance(locator, str) and locator in self.BLOCKED_TOOL_IDS:
            return
        super().click(locator)

    def menu_tools_visible(self):
        if not self.is_menu_open():
            return False
        for locator, label in self.TOOL_ITEMS:
            if not self.is_displayed(locator):
                return False
            if not self.device(text=label).exists:
                return False
        return True

    def music_panel_visible(self):
        return (
            self.is_menu_open()
            and self.is_displayed(self.MUSIC_PANEL)
            and self.is_displayed(self.BTN_TOGGLE)
        )
