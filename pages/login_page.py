# -*- coding: utf-8 -*-
"""
登录页 Page Object（S1Pro 力量镜 v3.x）。

定位依据：S1Pro_UI/v3.1.0.7123/elements/Login_elements.md
用途：会话掉线后的恢复（点 Admin 成员头像回主页），不作为随机探索目标。
"""
from pages.base_page import BasePage, _element_exists, _is_static_checker_device


class LoginPage(BasePage):
    """家庭成员登录入口 — LoginEntryActivity。"""

    PACKAGE = "com.aeke.fitnessmirror"
    ACTIVITY = f"{PACKAGE}.login_signup.LoginEntryActivity"

    TITLE = f"{PACKAGE}:id/family_login_title"
    MEMBER_LIST = f"{PACKAGE}:id/rv_member"
    FAMILY_ROOT = f"{PACKAGE}:id/family_mode_ll"
    TAG_ADMIN = f"{PACKAGE}:id/tag_administrator"
    MEMBER_NAME = f"{PACKAGE}:id/nane_tv"
    MEMBER_ICON = f"{PACKAGE}:id/icon_iv"
    OFFLINE_MODE = f"{PACKAGE}:id/ll_offlineMode"
    OFFLINE_MODE_TEXT = f"{PACKAGE}:id/tv_offlineMode"
    SLOGAN = f"{PACKAGE}:id/slogan_tv"

    TITLE_TEXT = "Tap Avatar to Log In"
    ADMIN_TEXT = "Admin"
    JOIN_TEXT = "Join"
    OFFLINE_TEXT = "Offline Mode"

    # 稳定性测试禁止随机探索的入口
    BLOCKED_LABELS = frozenset({JOIN_TEXT, OFFLINE_TEXT})

    _ANCHORS = (TITLE, MEMBER_LIST, FAMILY_ROOT)

    def is_login_page_displayed(self):
        hits = sum(1 for loc in self._ANCHORS if self.is_displayed(loc))
        if hits >= 2:
            return True
        return self.text_exists(self.TITLE_TEXT) and self.is_displayed(self.MEMBER_LIST)

    def has_admin_member(self):
        return self.is_displayed(self.TAG_ADMIN) or self.text_exists(self.ADMIN_TEXT)

    def _click_admin_parent(self):
        """点击带 Admin 标签的成员卡片（可点父 ViewGroup）。"""
        xpath = f'//*[@resource-id="{self.TAG_ADMIN}"]/..'
        try:
            node = self.device.xpath(xpath)
            if _element_exists(node, timeout=2):
                node.click()
                return True
        except Exception:
            pass

        tag = self.device(resourceId=self.TAG_ADMIN)
        if not _element_exists(tag, timeout=2):
            tag = self.device(text=self.ADMIN_TEXT)
        if not _element_exists(tag, timeout=2):
            return False

        try:
            bounds = tag.info.get("bounds") or {}
            left = int(bounds.get("left", 0))
            right = int(bounds.get("right", 0))
            top = int(bounds.get("top", 0))
            bottom = int(bounds.get("bottom", 0))
            if right > left and bottom > top:
                # Admin 标签在卡片顶部，点击略下方命中头像区域
                cx = (left + right) // 2
                cy = bottom + max(40, (bottom - top))
                self.device.click(cx, cy)
                return True
        except Exception:
            pass
        return False

    def login_as_admin(self):
        """选择带 Admin 标签的成员头像进入主页。"""
        if _is_static_checker_device(self.device):
            return False
        if not self.is_login_page_displayed():
            return False
        if not self.has_admin_member():
            return False
        if not self._click_admin_parent():
            return False
        self.device.sleep(2.0)
        return not self.is_login_page_displayed()
