# -*- coding: utf-8 -*-
"""
功能模块目录：场景别名 → Activity 白名单 + 一二级业务页锚点。

`--scenarios all` 不启用白名单；指定模块时并集写入 configs/awl.strings。
"""
from __future__ import annotations

import os
from typing import Dict, Iterable, List, Optional, Sequence, Set

PKG = "com.aeke.fitnessmirror"
MAIN = f"{PKG}.home.MainActivity"

# 场景别名 / 脚本名 → 规范模块名
ALIAS_TO_MODULE = {
    "home": "home",
    "main": "home",
    "navigation": "home",
    "lifestyle": "lifestyle",
    "media": "lifestyle",
    "guide": "lifestyle",
    "suixinlian": "suixinlian",
    "course": "course",
    "profile": "profile",
    "plan": "programs",
    "programs": "programs",
    "assessment": "assessment",
    "ai_coach": "ai_coach",
    "aicoach": "ai_coach",
    "schedule": "schedule",
    "calendar": "schedule",
    "control_panel": "control_panel",
    "control": "control_panel",
    "data_center": "data_center",
    "datacenter": "data_center",
    "effort": "data_center",
    "floating_touch": "floating_touch",
    "touch": "floating_touch",
    "touch_menu": "floating_touch",
    "settings": "settings",
    "test_home.py": "home",
    "test_lifestyle.py": "lifestyle",
    "test_suixinlian.py": "suixinlian",
    "test_course.py": "course",
    "test_profile_plan.py": "profile",
    "test_programs.py": "programs",
    "test_assessment.py": "assessment",
    "test_ai_coach.py": "ai_coach",
    "test_schedule.py": "schedule",
    "test_control_panel.py": "control_panel",
    "test_data_center.py": "data_center",
    "test_floating_touch.py": "floating_touch",
    "test_settings.py": "settings",
}

# 每个模块的白名单 Activity（不含登录/屏保）
MODULE_ACTIVITIES: Dict[str, List[str]] = {
    "home": [MAIN],
    "lifestyle": [
        MAIN,
        f"{PKG}.activity.GameListActivity",
        f"{PKG}.pk.PKPasswordInputActivity",
        f"{PKG}.pk.PreparePkActivity",
        f"{PKG}.pk.PKRoomWaitActivity",
        f"{PKG}.pk.MultiPKEndActivity",
        f"{PKG}.pk.PKAICourseActivity",
        f"{PKG}.bt.ui.BtSinkAudioActivity",
        f"{PKG}.projectionscreen.ProjectionScreenActivity",
        f"{PKG}.projectionscreen.ProjectionSimpleEducationActivity",
        f"{PKG}.screen.ScreenProtectActivity",
    ],
    "suixinlian": [
        MAIN,
        f"{PKG}.actionlibrary.ActionEditIndexActivity",
        f"{PKG}.actionlibrary.ActionPlayActivity",
        f"{PKG}.actionlibrary.ActionResultActivity",
        f"{PKG}.actionlibrary.TargetSelectionActivity",
        f"{PKG}.actionlibrary.selectMovement.SelectMovementActivity",
        f"{PKG}.actionlibrary.NewComboActionDetailsActivity",
        f"{PKG}.actionlibrary.GeneratedRecordsActivity",
    ],
    "course": [
        MAIN,
        f"{PKG}.course.CourseListActivity",
        f"{PKG}.course.CourseDetailsNewActivity",
        f"{PKG}.course.MyCoursesActivity",
        f"{PKG}.course.GeneralCourseActivity",
        f"{PKG}.course.AICourseActivity",
        f"{PKG}.course.SubtitleCourseActivity",
        f"{PKG}.course.FollowUpStrengthCourseActivity",
        f"{PKG}.course.CourseResultActivity",
        f"{PKG}.course.GeneralTraningEndActivity",
        f"{PKG}.course.AITraningEndActivity",
        f"{PKG}.course.StrengthTrainingEndActivity",
        f"{PKG}.aicourse.detail.CourseDetailsActivity",
    ],
    "assessment": [
        MAIN,
        f"{PKG}.assessment.ui.AssessmentHomeActivity",
        f"{PKG}.assessment.ui.CustomizedPlanDetailActivity",
        f"{PKG}.assessment.ui.assessments.BodyPostureAssessmentActivity",
        f"{PKG}.assessment.ui.assessments.MuscleStrengthAssessmentActivity",
        f"{PKG}.assessment.ui.assessments.CardioEnduranceAssessmentActivity",
        f"{PKG}.assessment.ui.assessments.BodyFlexibilityAssessmentActivity",
        f"{PKG}.assessment.ui.assessments.BodyCompositionAssessmentActivity",
        f"{PKG}.assessment.ui.assessments.ProperFormAssessmentActivity",
        f"{PKG}.assessment.ui.reports.AssessmentHistoryReportsActivity",
        f"{PKG}.assessment.ui.reports.AssessmentSummaryReportActivity",
    ],
    "ai_coach": [
        MAIN,
        f"{PKG}.aicoach.activity.AiCoachHomeActivity",
        f"{PKG}.aicoach.activity.CourseDetailActivity",
        f"{PKG}.actionlibrary.aicourse.AiCourseStartTrainingActivity",
    ],
    "programs": [
        MAIN,
        f"{PKG}.activity.AllPlanActivity",
        f"{PKG}.activity.MyPlanListActivity",
        f"{PKG}.activity.PlanDetailNewActivity",
        f"{PKG}.activity.PlanCourseListActivity",
        f"{PKG}.activity.DiaryPlanShowActivity",
    ],
    "profile": [
        MAIN,
        f"{PKG}.activity.SettingsActivity",
        f"{PKG}.userprofile.ui.UserProfileActivity",
    ],
    "schedule": [
        MAIN,
        f"{PKG}.activity.ScheduleNewActivity",
    ],
    "control_panel": [MAIN],
    "data_center": [
        MAIN,
        f"{PKG}.activity.TrainingDataCentreActivity",
        f"{PKG}.activity.WeekReportActivity",
    ],
    "floating_touch": [MAIN],
    "settings": [
        MAIN,
        f"{PKG}.activity.SettingsActivity",
        f"{PKG}.activity.SettingDetailActivity",
        f"{PKG}.activity.UserSecurityActivity",
        f"{PKG}.activity.LanguageOptionListActivity",
        f"{PKG}.activity.DateTimeSettingsActivity",
        f"{PKG}.activity.SelectLanguageActivity",
        f"{PKG}.activity.SelectRegionActivity",
        f"{PKG}.activity.TimeZoneListActivity",
    ],
}

# 一二级业务页：shared=True 时需锚点采样才能区分
# anchors: resource-id 列表（可带完整包名或短名）
BUSINESS_PAGES: List[dict] = [
    {
        "id": "Home",
        "level": 1,
        "module": "home",
        "activities": [MAIN],
        "shared": True,
        "anchors": [f"{PKG}:id/tv_page_home", f"{PKG}:id/grf_free_traing"],
    },
    {
        "id": "Lifestyle",
        "level": 1,
        "module": "lifestyle",
        "activities": [MAIN],
        "shared": True,
        "anchors": [f"{PKG}:id/tv_life_style", f"{PKG}:id/rv_funcs"],
    },
    {
        "id": "FloatingTouch",
        "level": 2,
        "module": "floating_touch",
        "activities": [MAIN],
        "shared": True,
        "anchors": [f"{PKG}:id/container_touch_2", f"{PKG}:id/layout_contract_2"],
    },
    {
        "id": "Home_ControlPanel",
        "level": 2,
        "module": "control_panel",
        "activities": [MAIN],
        "shared": True,
        "anchors": [f"{PKG}:id/rl_control_root", f"{PKG}:id/top_strip"],
    },
    {
        "id": "DataCenter",
        "level": 2,
        "module": "data_center",
        "activities": [MAIN],
        "shared": True,
        "anchors": [f"{PKG}:id/hsr_tips", f"{PKG}:id/ll_report"],
    },
    {
        "id": "FreeWorkout",
        "level": 2,
        "module": "suixinlian",
        "activities": [f"{PKG}.actionlibrary.ActionEditIndexActivity"],
        "shared": False,
        "anchors": [],
    },
    {
        "id": "Course",
        "level": 2,
        "module": "course",
        "activities": [f"{PKG}.course.CourseListActivity"],
        "shared": False,
        "anchors": [],
    },
    {
        "id": "Assessment",
        "level": 2,
        "module": "assessment",
        "activities": [f"{PKG}.assessment.ui.AssessmentHomeActivity"],
        "shared": False,
        "anchors": [],
    },
    {
        "id": "AICoach",
        "level": 2,
        "module": "ai_coach",
        "activities": [f"{PKG}.aicoach.activity.AiCoachHomeActivity"],
        "shared": False,
        "anchors": [],
    },
    {
        "id": "Programs",
        "level": 2,
        "module": "programs",
        "activities": [f"{PKG}.activity.AllPlanActivity"],
        "shared": False,
        "anchors": [],
    },
    {
        "id": "Profile",
        "level": 2,
        "module": "profile",
        "activities": [f"{PKG}.activity.SettingsActivity"],
        "shared": False,
        "anchors": [],
    },
    {
        "id": "Home_CalendarMore",
        "level": 2,
        "module": "schedule",
        "activities": [f"{PKG}.activity.ScheduleNewActivity"],
        "shared": False,
        "anchors": [],
    },
    {
        "id": "DataCenterDetail",
        "level": 2,
        "module": "data_center",
        "activities": [f"{PKG}.activity.TrainingDataCentreActivity"],
        "shared": False,
        "anchors": [],
    },
    {
        "id": "Settings",
        "level": 2,
        "module": "settings",
        "activities": [f"{PKG}.activity.SettingDetailActivity"],
        "shared": True,
        "anchors": [f"{PKG}:id/settings_detail_rv", f"{PKG}:id/tvTitle"],
    },
    {
        "id": "Settings_AccountSecurity",
        "level": 2,
        "module": "settings",
        "activities": [f"{PKG}.activity.UserSecurityActivity"],
        "shared": False,
        "anchors": [],
    },
    {
        "id": "Settings_Language",
        "level": 2,
        "module": "settings",
        "activities": [f"{PKG}.activity.LanguageOptionListActivity"],
        "shared": False,
        "anchors": [],
    },
    {
        "id": "Settings_DateTime",
        "level": 2,
        "module": "settings",
        "activities": [f"{PKG}.activity.DateTimeSettingsActivity"],
        "shared": False,
        "anchors": [],
    },
    {
        "id": "Lifestyle_Games",
        "level": 2,
        "module": "lifestyle",
        "activities": [f"{PKG}.activity.GameListActivity"],
        "shared": False,
        "anchors": [],
    },
    {
        "id": "Lifestyle_VSMode",
        "level": 2,
        "module": "lifestyle",
        "activities": [f"{PKG}.pk.PKPasswordInputActivity"],
        "shared": True,
        "anchors": [f"{PKG}:id/btn_start_pk", f"{PKG}:id/tv_title"],
    },
    {
        "id": "Lifestyle_Speaker",
        "level": 2,
        "module": "lifestyle",
        "activities": [f"{PKG}.bt.ui.BtSinkAudioActivity"],
        "shared": False,
        "anchors": [],
    },
    {
        "id": "Lifestyle_ScreenCast",
        "level": 2,
        "module": "lifestyle",
        "activities": [f"{PKG}.projectionscreen.ProjectionScreenActivity"],
        "shared": False,
        "anchors": [],
    },
    {
        "id": "Lifestyle_Wallpaper",
        "level": 2,
        "module": "lifestyle",
        "activities": [f"{PKG}.screen.ScreenProtectActivity"],
        "shared": False,
        "anchors": [],
    },
    {
        "id": "Login",
        "level": 1,
        "module": None,
        "activities": [f"{PKG}.login_signup.LoginEntryActivity"],
        "shared": False,
        "anchors": [],
    },
    {
        "id": "Screensaver",
        "level": 1,
        "module": None,
        "activities": [f"{PKG}.screen.ScreenProjectShowActivity"],
        "shared": False,
        "anchors": [],
    },
]

KEA2_LOCK_MODULES_ENV = "KEA2_LOCK_MODULES"
KEA2_DEVICE_AWL_PATH = "/sdcard/.kea2/awl.strings"


def normalize_module_name(name: str) -> Optional[str]:
    if not name:
        return None
    key = name.strip().lower()
    if key.endswith(".py") and not key.startswith("test_"):
        key = f"test_{key}"
    return ALIAS_TO_MODULE.get(key)


def resolve_lock_modules(scenario_filter: Optional[Sequence[str]]) -> Optional[List[str]]:
    """
    None / empty → 全量（不锁模块）。
    否则返回去重后的规范模块名列表。
    """
    if not scenario_filter:
        return None
    modules: List[str] = []
    seen: Set[str] = set()
    for raw in scenario_filter:
        mod = normalize_module_name(raw)
        if not mod:
            # test_xxx.py 未登记时跳过
            continue
        if mod not in seen:
            seen.add(mod)
            modules.append(mod)
    return modules or None


def resolve_lock_modules_from_config(config) -> Optional[List[str]]:
    """从 Config._scenario_filter 解析锁模块列表。"""
    return resolve_lock_modules(getattr(config, "_scenario_filter", None))


def whitelist_activities_for_modules(modules: Iterable[str]) -> List[str]:
    """模块并集 + 始终包含 MainActivity（预登录入口）。"""
    acts: Set[str] = {MAIN}
    for mod in modules:
        for a in MODULE_ACTIVITIES.get(mod, []):
            acts.add(a)
    return sorted(acts)


def write_awl_strings(project_root: str, activities: Sequence[str]) -> str:
    """写入 configs/awl.strings，返回本地路径。"""
    path = os.path.join(project_root, "configs", "awl.strings")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for act in activities:
            f.write(f"{act}\n")
    return path


def business_pages_for_modules(modules: Optional[Sequence[str]] = None) -> List[dict]:
    """返回关注的业务页定义；modules=None 返回全部已建模页。"""
    if modules is None:
        return list(BUSINESS_PAGES)
    mod_set = set(modules)
    return [p for p in BUSINESS_PAGES if p.get("module") in mod_set or p.get("module") is None]


def page_ids_modeled(modules: Optional[Sequence[str]] = None) -> List[str]:
    return [p["id"] for p in business_pages_for_modules(modules) if p.get("module") is not None]


def activity_to_unique_pages(activity: str) -> List[str]:
    """非共享 Activity → 直接映射的业务页 id。"""
    short = activity.split("/")[-1] if "/" in activity else activity
    hits = []
    for p in BUSINESS_PAGES:
        if p.get("shared"):
            continue
        for a in p.get("activities") or []:
            if a == activity or a.endswith(short) or short.endswith(a.split(".")[-1]):
                hits.append(p["id"])
                break
    return hits


def normalize_activity_name(activity: str) -> str:
    """统一为完整类名。"""
    if not activity:
        return ""
    act = activity.strip()
    if act.startswith("."):
        return f"{PKG}{act}"
    if "/" in act:
        # package/activity
        pkg, name = act.split("/", 1)
        if name.startswith("."):
            return f"{pkg}{name}"
        if "." not in name:
            return f"{pkg}.{name}"
        return name if name.startswith(PKG) else name
    if act.startswith(PKG):
        return act
    if act.startswith("com."):
        return act
    return f"{PKG}.{act}"
