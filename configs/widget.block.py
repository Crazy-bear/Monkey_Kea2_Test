# -*- coding: utf-8 -*-
"""
Kea2 / Fastbot 控件黑名单（【S1Pro 力量镜】）。

模块锁（KEA2_LOCK_MODULES）时：
- 未锁 lifestyle → 屏蔽 Lifestyle Tab
- 未锁 home → 屏蔽 Home Tab，减少锁模块时被点回主页
- 锁 course 且未锁 home → 在课程列表根页屏蔽 iv_back（避免直接退回 Home；详情返回仍可用）

未锁 floating_touch（含 --scenarios all）时屏蔽悬浮 Touch 球/展开层，
避免 Fastbot 把事件全吸到悬浮球上、业务页几乎不动。
"""
import os

from kea2.utils import Device
from kea2.keaUtils import precondition

PKG = "com.aeke.fitnessmirror"


def _lock_modules():
    raw = os.environ.get("KEA2_LOCK_MODULES", "").strip()
    if not raw:
        return None
    return {m.strip().lower() for m in raw.split(",") if m.strip()}


def _locks_modules_without_home():
    lock = _lock_modules()
    return lock is not None and "home" not in lock


def _should_block_floating_touch():
    """显式锁 floating_touch 时不挡；其余场景都挡悬浮层。"""
    lock = _lock_modules()
    return not (lock is not None and "floating_touch" in lock)


def _course_list_root_visible(d: "Device") -> bool:
    """课程列表根页：有列表 + 筛选，用于限制只挡列表上的返回。"""
    try:
        return bool(
            d(resourceId=f"{PKG}:id/rv_list").exists
            and d(resourceId=f"{PKG}:id/fl_filter_first").exists
        )
    except Exception:
        return False


def _widget_bounds_hw(info) -> tuple:
    """从 u2/Kea2 node.info 解析宽高；失败返回 (0, 0)。"""
    if not isinstance(info, dict):
        return (0, 0)
    b = info.get("bounds")
    try:
        if isinstance(b, dict):
            w = int(b.get("right", 0)) - int(b.get("left", 0))
            h = int(b.get("bottom", 0)) - int(b.get("top", 0))
            return (max(w, 0), max(h, 0))
        # 形如 [0,2][1080,4]
        import re

        m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", str(b or ""))
        if not m:
            return (0, 0)
        left, top, right, bottom = map(int, m.groups())
        return (max(right - left, 0), max(bottom - top, 0))
    except Exception:
        return (0, 0)


def _control_root_collapsed(d: "Device") -> bool:
    """
    折叠态系统控制条：clickable 但高度仅约 2px（如 [0,2][1080,4]）。
    Fastbot 会反复点它，日志有 Sending monkeyEvent，画面几乎不动。
    展开态（控制中心全屏）高度很大，不屏蔽。
    """
    try:
        node = d(resourceId=f"{PKG}:id/rl_control_root")
        if not getattr(node, "exists", False):
            return False
        info = getattr(node, "info", None) or {}
        _w, h = _widget_bounds_hw(info)
        return 0 < h <= 20
    except Exception:
        return False


def global_block_widgets(d: "Device"):
    """全局禁止点击的控件（睡眠、折叠、系统危险操作等）。"""
    blocked = [
        d(text="Sleep"),
        d(text="睡眠"),
        d(textContains="Sleep"),
        d(textContains="睡眠"),
        d(text="Wallpaper"),
        d(text="壁纸"),
        d(resourceId=f"{PKG}:id/sleep"),
        d(resourceId=f"{PKG}:id/screen"),
        d(text="Fold"),
        d(text="折叠"),
        d(resourceId=f"{PKG}:id/go_back_btn"),
        d(text="Retract rope"),
        d(text="收绳"),
        d(resourceId=f"{PKG}:id/retrieve_the_rope"),
        d(resourceId=f"{PKG}:id/retrieve_the_rope_text"),
        d(text="卸载"),
        d(text="清除数据"),
        d(text="强行停止"),
        d(text="恢复出厂设置"),
        d(text="Factory reset"),
        d(text="Uninstall"),
        d(text="Clear data"),
        d(text="Reset Device"),
        d(resourceId=f"{PKG}:id/tv_sure"),
        d(text="Forget"),
        d(text="忘记"),
        d(resourceId=f"{PKG}:id/tv_wifi_delete_curr"),
        d(resourceId=f"{PKG}:id/ctl_wifi_title_right"),
        d(text="Join"),
        d(text="Offline Mode"),
        d(textContains="Offline"),
        d(resourceId=f"{PKG}:id/ll_offlineMode"),
        d(resourceId=f"{PKG}:id/iv_offlineMode_question"),
        d(resourceId=f"{PKG}:id/tv_offlineMode"),
        # 登录页品牌图：clickable 但无业务意义，会吸走 Fastbot 点击
        d(resourceId=f"{PKG}:id/slogan_iv"),
        d(resourceId=f"{PKG}:id/slogan_tv"),
    ]
    lock = _lock_modules()
    if lock is not None and "lifestyle" not in lock:
        blocked.extend(
            [
                d(text="Lifestyle"),
                d(text="娱乐"),
                d(resourceId=f"{PKG}:id/tv_life_style"),
            ]
        )
    if _locks_modules_without_home():
        blocked.extend(
            [
                d(text="Home"),
                d(resourceId=f"{PKG}:id/tv_page_home"),
            ]
        )
    return blocked


def global_block_tree(d: "Device"):
    """整块屏蔽：登录区、屏保、悬浮菜单危险按钮（含子节点）。"""
    return [
        d(resourceId=f"{PKG}:id/family_mode_ll"),
        d(resourceId=f"{PKG}:id/rv_member"),
        d(resourceId=f"{PKG}:id/screen_image"),
        d(resourceId=f"{PKG}:id/sleep"),
        d(resourceId=f"{PKG}:id/screen"),
        d(resourceId=f"{PKG}:id/retrieve_the_rope"),
        d(resourceId=f"{PKG}:id/go_back_btn"),
        d(resourceId=f"{PKG}:id/bottom_tool_layout"),
    ]


@precondition(lambda d: True)
def block_device_sleep_and_wallpaper(d: "Device"):
    """
    强制屏蔽 Sleep / Wallpaper（及同组危险工具）。
    悬浮 Touch 展开后点 Sleep 会进设备休眠黑屏；Wallpaper 易进屏保黑屏。
    注意：仅写在 global_block_widgets/tree 时，悬浮层上的这些节点仍可能被 Fastbot 点到
    （与悬浮球相同，必须用 @precondition 块函数）。
    """
    return [
        d(resourceId=f"{PKG}:id/sleep"),
        d(resourceId=f"{PKG}:id/screen"),
        d(resourceId=f"{PKG}:id/screen_text"),
        d(text="Sleep"),
        d(text="睡眠"),
        d(textContains="Sleep"),
        d(textContains="睡眠"),
        d(text="Wallpaper"),
        d(text="壁纸"),
        d(textContains="Wallpaper"),
        d(resourceId=f"{PKG}:id/retrieve_the_rope"),
        d(resourceId=f"{PKG}:id/retrieve_the_rope_text"),
        d(text="Retract rope"),
        d(text="收绳"),
        d(resourceId=f"{PKG}:id/go_back_btn"),
        d(text="Fold"),
        d(text="折叠"),
        d(resourceId=f"{PKG}:id/bottom_tool_layout"),
        d(resourceId=f"{PKG}:id/all_tool"),
        d(resourceId=f"{PKG}:id/all_tool_text"),
    ]


@precondition(lambda d: _should_block_floating_touch())
def block_floating_touch_overlay(d: "Device"):
    """
    未测 floating_touch 时屏蔽悬浮球/展开层。
    须用 @precondition 块函数：仅写在 global_block_tree 时 Fastbot 仍会点到悬浮层。
    """
    return [
        d(resourceId=f"{PKG}:id/container_touch_2"),
        d(resourceId=f"{PKG}:id/layout_contract_2"),
        d(resourceId=f"{PKG}:id/iv_contract_album_img_2"),
        d(resourceId=f"{PKG}:id/layout_expand"),
        d(resourceId=f"{PKG}:id/touch_layout_bg"),
        d(resourceId=f"{PKG}:id/float_music_fl"),
        d(resourceId=f"{PKG}:id/float_kugou_music_con"),
        d(resourceId=f"{PKG}:id/go_home_btn"),
        d(resourceId=f"{PKG}:id/all_tool"),
        d(resourceId=f"{PKG}:id/all_tool_text"),
        # 双保险：即使菜单已展开，也不让点到休眠/壁纸
        d(resourceId=f"{PKG}:id/sleep"),
        d(resourceId=f"{PKG}:id/screen"),
        d(resourceId=f"{PKG}:id/screen_text"),
        d(resourceId=f"{PKG}:id/bottom_tool_layout"),
    ]


@precondition(
    lambda d: bool(
        getattr(d(resourceId=f"{PKG}:id/family_mode_ll"), "exists", False)
        or getattr(d(resourceId=f"{PKG}:id/rv_member"), "exists", False)
        or getattr(d(resourceId=f"{PKG}:id/slogan_iv"), "exists", False)
    )
)
def block_login_decoy_widgets(d: "Device"):
    """登录页装饰/无效可点控件，避免恢复前 Fastbot 空转。"""
    return [
        d(resourceId=f"{PKG}:id/slogan_iv"),
        d(resourceId=f"{PKG}:id/slogan_tv"),
        d(resourceId=f"{PKG}:id/family_login_title"),
    ]


@precondition(lambda d: _control_root_collapsed(d))
def block_collapsed_control_root(d: "Device"):
    """屏蔽折叠态 rl_control_root，避免空转点击。"""
    return [d(resourceId=f"{PKG}:id/rl_control_root")]


@precondition(
    lambda d: (
        _locks_modules_without_home()
        and "course" in (_lock_modules() or set())
        and _course_list_root_visible(d)
    )
)
def block_course_list_back_to_home(d: "Device"):
    """课程列表根页的返回会回到 Home；模块锁时屏蔽，把时间留给页内探索。"""
    return [d(resourceId=f"{PKG}:id/iv_back")]
