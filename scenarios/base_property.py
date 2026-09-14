# -*- coding: utf-8 -*-
"""
【S1Pro 力量镜】Kea2 属性测试基类（设备需已预登录至 MainActivity）。

掉到屏保 / 登录页时：
- Fastbot 不随机点登录区（见 configs/widget.block.py）
- 由基类属性 test_recover_session 点 Admin / 退屏保恢复
- 其它属性的 ensure_logged_in_home() 在执行期也可恢复

注意：precondition 静态检查阶段不会点登录；若只有 on_home_page() 类属性，
停在登录页会变成「0 Checkable property」死锁，故必须有本恢复属性。
"""
import unittest

from kea2 import precondition, prob, max_tries

from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.screensaver_page import ScreensaverPage
from pages.lifestyle_page import (
    LifestylePage,
    LifestyleGamesPage,
    LifestyleVSModePage,
    LifestyleSpeakerPage,
    LifestyleScreenCastPage,
    LifestyleWallpaperPage,
)
from pages.course_page import CoursePage
from pages.free_workout_page import FreeWorkoutPage
from pages.ai_coach_page import AICoachPage
from pages.assessment_page import AssessmentPage
from pages.programs_page import ProgramsPage
from pages.profile_page import ProfilePage
from pages.schedule_page import SchedulePage
from pages.control_panel_page import ControlPanelPage
from pages.data_center_page import DataCenterPage
from pages.data_center_detail_page import DataCenterDetailPage
from pages.floating_touch_page import FloatingTouchPage
from pages.settings_page import (
    SettingsPage,
    SettingsAccountSecurityPage,
    SettingsLanguagePage,
    SettingsDateTimePage,
    SettingsUnitsDialogPage,
    SettingsAICorrectionDialogPage,
    SettingsResetDeviceDialogPage,
)
from orchestrator.test_session import get_active_monitor, get_lock_modules


class FitnessMirrorPropertyTest(unittest.TestCase):
    """Kea2 注入 uiautomator2 Device 为 self.d。"""



    d = None



    def home_page(self):

        return HomePage(self.d)

    def login_page(self):
        return LoginPage(self.d)

    def screensaver_page(self):
        return ScreensaverPage(self.d)

    def lifestyle_page(self):

        return LifestylePage(self.d)

    def lifestyle_games_page(self):
        return LifestyleGamesPage(self.d)

    def lifestyle_vs_mode_page(self):
        return LifestyleVSModePage(self.d)

    def lifestyle_speaker_page(self):
        return LifestyleSpeakerPage(self.d)

    def lifestyle_screen_cast_page(self):
        return LifestyleScreenCastPage(self.d)

    def lifestyle_wallpaper_page(self):
        return LifestyleWallpaperPage(self.d)

    def course_page(self):

        return CoursePage(self.d)



    def free_workout_page(self):

        return FreeWorkoutPage(self.d)



    def ai_coach_page(self):

        return AICoachPage(self.d)



    def assessment_page(self):

        return AssessmentPage(self.d)



    def programs_page(self):

        return ProgramsPage(self.d)



    def profile_page(self):

        return ProfilePage(self.d)



    def schedule_page(self):

        return SchedulePage(self.d)



    def control_panel_page(self):

        return ControlPanelPage(self.d)



    def data_center_page(self):

        return DataCenterPage(self.d)



    def data_center_detail_page(self):

        return DataCenterDetailPage(self.d)



    def floating_touch_page(self):

        return FloatingTouchPage(self.d)



    def settings_page(self):

        return SettingsPage(self.d)



    def settings_account_security_page(self):

        return SettingsAccountSecurityPage(self.d)



    def settings_language_page(self):

        return SettingsLanguagePage(self.d)



    def settings_datetime_page(self):

        return SettingsDateTimePage(self.d)



    def settings_units_dialog(self):

        return SettingsUnitsDialogPage(self.d)



    def settings_ai_correction_dialog(self):

        return SettingsAICorrectionDialogPage(self.d)



    def settings_reset_device_dialog(self):

        return SettingsResetDeviceDialogPage(self.d)



    def _is_static_precondition(self):
        from pages.base_page import _is_static_checker_device

        return _is_static_checker_device(self.d)

    def on_settings_page(self):
        page = self.settings_page()
        if page.is_settings_page_displayed():
            return True
        if self._is_static_precondition():
            return False
        if not self.on_home_page():
            return False
        self.home_page().go_to_profile()
        self.d.sleep(1)
        profile = self.profile_page()
        if not profile.is_profile_page_displayed():
            return False
        profile.go_to_settings()
        self.d.sleep(1)
        return page.is_settings_page_displayed()



    def press_back_to_settings(self, max_back=3):
        page = self.settings_page()
        for _ in range(max_back):
            if page.is_settings_page_displayed():
                return True
            if page.is_displayed(page.BACK_BUTTON):
                page.press_back()
            else:
                self.d.press("back")
            self.d.sleep(0.8)
        return page.is_settings_page_displayed()



    def is_on_screensaver(self):
        return self.screensaver_page().is_screensaver_displayed()

    def is_on_login_page(self):
        return self.login_page().is_login_page_displayed()

    def needs_session_recovery(self):
        """静态/动态均可：当前是否在登录页或屏保（需属性脚本恢复）。"""
        return self.is_on_login_page() or self.is_on_screensaver()

    def should_pull_to_locked_module(self):
        """
        模块锁下已离开目标表面时拉回（静态可判定）。
        已在任一锁定模块根页或模块内子 Activity 则 False，把时间留给 Fastbot 页内探索。
        """
        modules = self.lock_modules()
        if not modules:
            return False
        if self.needs_session_recovery():
            return False
        return not any(self.is_within_module(m) for m in modules)

    def stay_on_locked_module_after_property(self):
        """属性结束后：模块锁则留在模块表面，全量才回 Home。"""
        modules = self.lock_modules()
        if modules and "home" not in modules:
            return self.ensure_locked_module_surface()
        return self.press_back_to_home()

    def explore_or_enter_ready(self, module, is_on_root):
        """
        属性调度入口：
        - 已在模块根页 → True
        - 任意模块锁开启 → False（进模块只靠 test_pull / 开局引导，避免 Home 刷进模块）
        - 全量 → 可从 Home 导航进入
        """
        if is_on_root():
            return True
        if self.lock_modules() is not None:
            return False
        if self._is_static_precondition():
            return self.home_page().is_home_page_displayed()
        if not self.on_home_page():
            return False
        return self.navigate_to_module_root(module)

    def finish_module_property(self):
        """模块锁：属性结束后留在模块；全量：回 Home。"""
        modules = self.lock_modules()
        if modules and "home" not in modules:
            return
        self.press_back_to_home()

    @prob(1.0)
    @max_tries(5)
    @precondition(lambda self: self.needs_session_recovery())
    def test_recover_session(self):
        """
        登录/屏保恢复属性：打破「0 Checkable」死锁。
        Fastbot 被屏蔽登录区时，只能靠本属性点 Admin / 退屏保。
        模块锁时恢复后拉回目标模块根页。
        """
        self.set_perf_phase("session_recover")
        assert self.ensure_logged_in_home(), "无法从登录页/屏保恢复到 Home"
        if self.lock_modules():
            assert self.ensure_locked_module_surface(), "会话恢复后未能进入锁定模块"

    @prob(1.0)
    @precondition(lambda self: self.should_pull_to_locked_module())
    def test_pull_to_locked_module(self):
        """
        模块锁引导：离开目标模块（如回到 Home）时拉回，再交给 Fastbot 随机探索。
        概率 1.0：在「已离开模块」时优先于其它属性，避免与课程抽检抢调度。
        不加 max_tries，整场可持续纠正。
        """
        self.set_perf_phase("module_lock_pull")
        assert self.ensure_locked_module_surface(), "未能拉回锁定模块表面"

    def ensure_logged_in_home(self, max_rounds=3):
        """
        退出屏保 → 若在登录页则点 Admin → 回到 Home 表面。
        静态 precondition 下只读判断，不执行点击。
        """
        home = self.home_page()
        if home.is_home_page_displayed():
            return True
        if self._is_static_precondition():
            return False

        # Sleep / 息屏后界面无响应：先唤醒再恢复会话
        try:
            self.d.shell("input keyevent KEYCODE_WAKEUP")
            self.d.sleep(0.4)
        except Exception:
            pass

        for _ in range(max_rounds):
            if home.is_home_page_displayed():
                return home.ensure_home_surface()

            # 蓝牙连接/帮助等弹层会挡住 Admin，先尝试关掉
            try:
                for tip in ("Cancel", "取消", "Close", "关闭", "OK", "确定"):
                    btn = self.d(text=tip)
                    if btn.exists:
                        btn.click()
                        self.d.sleep(0.6)
                        break
            except Exception:
                pass

            saver = self.screensaver_page()
            if saver.is_screensaver_displayed():
                saver.dismiss_by_tap()
                continue

            login = self.login_page()
            if login.is_login_page_displayed():
                if not login.login_as_admin():
                    return False
                continue

            # 已在 MainActivity 其它 Tab / 遮罩上
            if home.is_displayed(home.MAIN_TITLE_BAR) or home.is_displayed(home.HOME_TAB):
                return home.ensure_home_surface()

            # 兜底：点一下屏幕中心（可能仍是淡出屏保 / 息屏亮起后）
            try:
                w, h = self.d.window_size()
                self.d.click(w // 2, h // 2)
                self.d.sleep(1.5)
            except Exception:
                break

        return home.ensure_home_surface()

    def on_home_page(self):
        page = self.home_page()
        if page.is_home_page_displayed():
            return True
        if self._is_static_precondition():
            return False
        if not self.ensure_logged_in_home():
            return False
        return page.ensure_home_surface()

    def on_lifestyle_page(self):
        page = self.lifestyle_page()
        if page.is_lifestyle_page_displayed():
            return True
        if self._is_static_precondition():
            return False
        if not self.ensure_logged_in_home():
            return False
        return page.ensure_lifestyle_surface()



    def set_perf_phase(self, name):
        monitor = get_active_monitor()
        if monitor:
            monitor.set_phase(name)
            return
        # Kea2 子进程无 monitor：写 phase 文件供主进程 PerformanceMonitor 读取
        from orchestrator.perf_context import resolve_phase_file, write_perf_phase

        path = resolve_phase_file()
        if path:
            write_perf_phase(path, name)



    def press_back_to_home(self, max_back=3):
        # 模块锁且未锁 home：回到模块根页，避免又把探索送回首页
        modules = self.lock_modules()
        if modules and "home" not in modules:
            return self.return_to_module_surface(max_back=max_back)

        if not self._is_static_precondition():
            if self.is_on_screensaver() or self.is_on_login_page():
                if self.ensure_logged_in_home():
                    return True

        page = self.home_page()

        for _ in range(max_back):

            page.ensure_home_surface()

            if page.is_home_page_displayed():

                return True

            self.d.press("back")

            self.d.sleep(1)

        page.ensure_home_surface()

        return page.is_home_page_displayed()



    def press_back_to_lifestyle(self, max_back=5):
        page = self.lifestyle_page()
        for _ in range(max_back):
            if page.is_lifestyle_page_displayed():
                return True

            games = self.lifestyle_games_page()
            if games.is_games_page_displayed() and games.press_back():
                self.d.sleep(0.8)
                continue

            vs = self.lifestyle_vs_mode_page()
            if vs.is_vs_mode_page_displayed() and vs.press_back():
                self.d.sleep(0.8)
                continue

            speaker = self.lifestyle_speaker_page()
            if speaker.is_speaker_page_displayed() and speaker.press_back():
                self.d.sleep(0.8)
                continue

            cast = self.lifestyle_screen_cast_page()
            if cast.is_screen_cast_page_displayed() and cast.press_back():
                self.d.sleep(0.8)
                continue

            wallpaper = self.lifestyle_wallpaper_page()
            if wallpaper.is_wallpaper_page_displayed() and wallpaper.press_back():
                self.d.sleep(0.8)
                continue

            self.d.press("back")
            self.d.sleep(0.8)

        page.ensure_lifestyle_surface()
        return page.is_lifestyle_page_displayed()

    def lock_modules(self):
        """当前模块锁列表；None 表示全量。"""
        return get_lock_modules()

    def is_on_module_root(self, module):
        checkers = {
            "home": lambda: self.home_page().is_home_page_displayed(),
            "lifestyle": lambda: self.lifestyle_page().is_lifestyle_page_displayed(),
            "suixinlian": lambda: self.free_workout_page().is_free_workout_page_displayed(),
            "course": lambda: self.course_page().is_course_page_displayed(),
            "assessment": lambda: self.assessment_page().is_assessment_page_displayed(),
            "ai_coach": lambda: self.ai_coach_page().is_ai_coach_page_displayed(),
            "programs": lambda: self.programs_page().is_programs_page_displayed(),
            "profile": lambda: self.profile_page().is_profile_page_displayed(),
            "schedule": lambda: self.schedule_page().is_schedule_page_displayed(),
            "settings": lambda: self.settings_page().is_settings_page_displayed(),
            "data_center": lambda: (
                self.data_center_detail_page().is_data_center_detail_displayed()
                or self.data_center_page().is_effort_strip_visible()
            ),
            "control_panel": lambda: self.control_panel_page().is_control_panel_open(),
            "floating_touch": lambda: self.floating_touch_page().is_fab_visible(),
        }
        fn = checkers.get(module)
        return bool(fn and fn())

    def is_within_module(self, module):
        """
        是否仍在模块探索范围内（根页或白名单内非 MainActivity 的子页）。
        MainActivity 不计入课程等模块「页内」，以便从 Home 拉回。
        """
        if self.is_on_module_root(module):
            return True
        from orchestrator.module_catalog import MAIN, MODULE_ACTIVITIES, normalize_activity_name

        try:
            cur = (self.d.app_current() or {}).get("activity") or ""
        except Exception:
            return False
        act = normalize_activity_name(cur)
        if not act or act == MAIN or act.endswith(".MainActivity"):
            return False
        short = act.rsplit(".", 1)[-1]
        for a in MODULE_ACTIVITIES.get(module) or []:
            if a == MAIN or a.endswith(".MainActivity"):
                continue
            if a == act or a.endswith("." + short) or short == a.rsplit(".", 1)[-1]:
                return True
        return False

    def navigate_to_module_root(self, module):
        """从 Home 走进模块根页（模块锁引导）。"""
        if self._is_static_precondition():
            return self.is_on_module_root(module)
        if module == "home":
            return self.on_home_page()
        if module == "lifestyle":
            return self.on_lifestyle_page()
        if not self.on_home_page():
            return False
        home = self.home_page()
        if module == "suixinlian":
            home.go_to_suixinlian()
            self.d.sleep(1.5)
            return self.free_workout_page().is_free_workout_page_displayed()
        if module == "course":
            home.go_to_jingpin_course()
            self.d.sleep(1.5)
            return self.course_page().is_course_page_displayed()
        if module == "assessment":
            home.go_to_assessment()
            self.d.sleep(1.5)
            return self.assessment_page().is_assessment_page_displayed()
        if module == "ai_coach":
            home.go_to_ai_coach()
            self.d.sleep(1.5)
            return self.ai_coach_page().is_ai_coach_page_displayed()
        if module == "programs":
            home.go_to_plan()
            self.d.sleep(1.5)
            return self.programs_page().is_programs_page_displayed()
        if module == "profile":
            home.go_to_profile()
            self.d.sleep(1.5)
            return self.profile_page().is_profile_page_displayed()
        if module == "schedule":
            home.go_to_calendar_more()
            self.d.sleep(1.5)
            return self.schedule_page().is_schedule_page_displayed()
        if module == "settings":
            return self.on_settings_page()
        if module == "data_center":
            strip = self.data_center_page()
            if strip.go_to_data_center():
                self.d.sleep(1.5)
                return self.data_center_detail_page().is_data_center_detail_displayed()
            return strip.is_effort_strip_visible()
        if module == "control_panel":
            panel = self.control_panel_page()
            panel.open_control_panel()
            self.d.sleep(0.8)
            return panel.is_control_panel_open()
        if module == "floating_touch":
            return self.floating_touch_page().ensure_fab_visible()
        return False

    def return_to_module_surface(self, max_back=5):
        """
        属性脚本结束后的返回：
        - 全量：回 Home
        - 模块锁：若已在任一锁定模块内则保持；否则导航进第一个不在范围内的锁定模块
        """
        modules = self.lock_modules()
        if not modules:
            return self.press_back_to_home(max_back=max_back)

        if self._is_static_precondition():
            return any(self.is_within_module(m) for m in modules)

        if self.needs_session_recovery():
            if not self.ensure_logged_in_home():
                return False

        if any(self.is_within_module(m) for m in modules):
            return True

        for _ in range(max_back):
            if any(self.is_within_module(m) for m in modules):
                return True
            if "lifestyle" in modules and self.press_back_to_lifestyle(max_back=1):
                continue
            if "settings" in modules and self.press_back_to_settings(max_back=1):
                continue
            self.d.press("back")
            self.d.sleep(0.8)

        for m in modules:
            if self.is_within_module(m):
                return True
            if self.navigate_to_module_root(m):
                return True
        return any(self.is_within_module(m) for m in modules)

    def ensure_locked_module_surface(self):
        """模块锁时：若不在任一目标模块内则引导进入第一个缺失模块。"""
        modules = self.lock_modules()
        if not modules:
            return True
        if self._is_static_precondition():
            return any(self.is_within_module(m) for m in modules)
        if any(self.is_within_module(m) for m in modules):
            return True
        if self.needs_session_recovery():
            if not self.ensure_logged_in_home():
                return False
        for m in modules:
            if self.is_within_module(m):
                return True
            if self.navigate_to_module_root(m):
                return True
        return any(self.is_within_module(m) for m in modules)


