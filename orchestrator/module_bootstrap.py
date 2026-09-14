# -*- coding: utf-8 -*-
"""
Kea2 启动前：若已锁模块且当前不在模块内，用 u2 轻量引导进第一个锁定模块。
避免开局长时间停在 Home 被 Fastbot 乱点。
"""
from __future__ import annotations

from typing import List, Optional, Sequence

from settings.logging_config import logger


def bootstrap_locked_module(device_id: str, lock_modules: Optional[Sequence[str]]) -> bool:
    """
    进入首个锁定模块根页。
    Returns:
        True 表示已在模块内或引导成功；False 表示失败（不阻断 Kea2，仅打日志）。
    """
    if not lock_modules:
        return True
    modules: List[str] = [m for m in lock_modules if m]
    if not modules:
        return True

    try:
        import uiautomator2 as u2
        from pages.home_page import HomePage
        from pages.login_page import LoginPage
        from pages.screensaver_page import ScreensaverPage
        from pages.course_page import CoursePage
        from pages.free_workout_page import FreeWorkoutPage
        from pages.assessment_page import AssessmentPage
        from pages.ai_coach_page import AICoachPage
        from pages.programs_page import ProgramsPage
        from pages.profile_page import ProfilePage
        from pages.schedule_page import SchedulePage
        from pages.lifestyle_page import LifestylePage
        from pages.settings_page import SettingsPage
    except Exception as e:
        logger.warning("模块开局引导跳过（import 失败）: %s", e)
        return False

    try:
        d = u2.connect(device_id)
    except Exception as e:
        logger.warning("模块开局引导跳过（连接设备失败）: %s", e)
        return False

    try:
        d.shell("input keyevent KEYCODE_WAKEUP")
        d.sleep(0.3)
    except Exception:
        pass

    home = HomePage(d)
    target = modules[0]

    # 屏保 / 登录
    for _ in range(3):
        saver = ScreensaverPage(d)
        if saver.is_screensaver_displayed():
            saver.dismiss_by_tap()
            d.sleep(1.0)
            continue
        login = LoginPage(d)
        if login.is_login_page_displayed():
            if not login.login_as_admin():
                logger.warning("模块开局引导：登录恢复失败")
                return False
            d.sleep(1.5)
            continue
        break

    checkers = {
        "home": lambda: home.is_home_page_displayed(),
        "lifestyle": lambda: LifestylePage(d).is_lifestyle_page_displayed(),
        "course": lambda: CoursePage(d).is_course_page_displayed(),
        "suixinlian": lambda: FreeWorkoutPage(d).is_free_workout_page_displayed(),
        "assessment": lambda: AssessmentPage(d).is_assessment_page_displayed(),
        "ai_coach": lambda: AICoachPage(d).is_ai_coach_page_displayed(),
        "programs": lambda: ProgramsPage(d).is_programs_page_displayed(),
        "profile": lambda: ProfilePage(d).is_profile_page_displayed(),
        "schedule": lambda: SchedulePage(d).is_schedule_page_displayed(),
        "settings": lambda: SettingsPage(d).is_settings_page_displayed(),
    }
    check = checkers.get(target)
    if check and check():
        logger.info("模块开局引导：已在 %s", target)
        return True

    if not home.is_home_page_displayed():
        home.ensure_home_surface()
        d.sleep(1.0)

    navigators = {
        "home": lambda: home.ensure_home_surface(),
        "lifestyle": lambda: LifestylePage(d).ensure_lifestyle_surface(),
        "course": home.go_to_jingpin_course,
        "suixinlian": home.go_to_suixinlian,
        "assessment": home.go_to_assessment,
        "ai_coach": home.go_to_ai_coach,
        "programs": home.go_to_plan,
        "profile": home.go_to_profile,
        "schedule": home.go_to_calendar_more,
    }

    if target == "settings":
        try:
            home.go_to_profile()
            d.sleep(1.0)
            ProfilePage(d).go_to_settings()
            d.sleep(1.5)
        except Exception as e:
            logger.warning("模块开局引导导航失败 (settings): %s", e)
            return False
        ok = bool(check and check())
        if ok:
            logger.info("模块开局引导成功 → settings")
        else:
            logger.warning("模块开局引导后未确认在 settings（继续交由属性拉回）")
        return ok

    nav = navigators.get(target)
    if not nav:
        logger.warning("模块开局引导：无导航器 %s，交由属性拉回", target)
        return False

    try:
        nav()
        d.sleep(2.0)
    except Exception as e:
        logger.warning("模块开局引导导航失败 (%s): %s", target, e)
        return False

    ok = bool(check and check())
    if ok:
        logger.info("模块开局引导成功 → %s", target)
    else:
        logger.warning("模块开局引导后未确认在 %s（继续交由属性拉回）", target)
    return ok
