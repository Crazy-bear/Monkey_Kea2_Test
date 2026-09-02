# -*- coding: utf-8 -*-
"""将 uiautomator window_dump.xml 解析为按功能分组的元素索引（Markdown）。"""
import argparse
import re
import xml.etree.ElementTree as ET
from pathlib import Path

# 按页面定制的功能分组规则；未匹配页面走通用「其他可点击 / 其他」
PAGE_FEATURE_RULES = {
    "Home": [
        ("顶栏 / 导航", ["ctl_main_title", "iv_head", "tv_name", "tv_page_home", "tv_life_style", "top_strip", "update_point"]),
        ("Home · 随心练", ["grf_free_traing", "Free Workout"]),
        ("Home · AI Coach", ["grf_ai_coach", "AI Coach"]),
        ("Home · 精品课程", ["grf_all_course", "Courses"]),
        ("Home · 运动测评", ["grf_evaluation", "Assessment"]),
        ("Home · 运动计划", ["grf_sports_plan", "Programs", "Join Program"]),
        ("Home · Banner / 周历", ["vp_banner", "tl_days", "hsb_week", "iv_more", "tv_title", "tv_sub_title", "vv_courseVideo", "tv_index_txt", "ll_course_infos", "tv_course_time", "tv_start", "iv_bg"]),
        ("Home · 提醒条", ["hsr_tips", "ll_reminder", "tv_msg", "iv_close"]),
        ("应用内控制栏", ["sys_wifi", "sys_ble", "sys_led", "sys_voice", "sys_bright", "rl_control_root", "v_overlay_mask"]),
        ("底部指示", ["second_oval", "three_oval", "viewpager"]),
    ],
    "Home_NoReminder": [
        ("顶栏 / 导航", ["ctl_main_title", "iv_head", "tv_name", "tv_page_home", "tv_life_style", "top_strip", "update_point"]),
        ("Home · Banner / 周历 / 日程", ["vp_banner", "tl_days", "hsb_week", "iv_more", "tv_title", "tv_index_txt", "ll_course_infos", "tv_course_time", "tv_course_kcal", "tv_course_difficulty", "tv_start", "iv_bg"]),
        ("Home · Today's Effort", ["hsr_tips", "ll_report", "Today's Effort", "ctl_report_infos", "tv_time_length", "tv_kcal", "tv_weight"]),
        ("Home · 随心练", ["grf_free_traing", "Free Workout"]),
        ("Home · AI Coach", ["grf_ai_coach", "AI Coach"]),
        ("Home · 精品课程", ["grf_all_course", "Courses"]),
        ("Home · 运动测评", ["grf_evaluation", "Assessment"]),
        ("Home · 运动计划", ["grf_sports_plan", "Programs"]),
        ("底部指示", ["second_oval", "three_oval", "viewpager"]),
    ],
    "Home_ControlPanel": [
        ("控制栏 · 根与遮罩", ["rl_control_root", "v_overlay_mask", "iv_anchor"]),
        ("控制栏 · 系统菜单", ["sys_menu_ll", "switch_rg"]),
        ("控制栏 · 亮度", ["sys_bright"]),
        ("控制栏 · 音量", ["sys_voice"]),
        ("控制栏 · 蓝牙", ["sys_ble"]),
        ("控制栏 · WiFi", ["sys_wifi"]),
        ("控制栏 · 灯带", ["sys_led"]),
    ],
    "Home_ControlPanel_Brightness": [
        ("控制栏 · 根与遮罩", ["rl_control_root", "v_overlay_mask"]),
        ("控制栏 · 系统菜单", ["sys_menu_ll", "switch_rg", "sys_bright", "sys_voice", "sys_ble", "sys_wifi", "sys_led"]),
        ("控制栏 · 亮度面板", ["sys_progress_ll", "sys_bar_progress_title", "sys_progress_bar_ll", "sys_progress_tv", "sys_progress_bar", "v_system_seekbar", "Brightness", "Screen"]),
    ],
    "Home_ControlPanel_Volume": [
        ("控制栏 · 根与遮罩", ["rl_control_root", "v_overlay_mask"]),
        ("控制栏 · 系统菜单", ["sys_menu_ll", "switch_rg", "sys_bright", "sys_voice", "sys_ble", "sys_wifi", "sys_led"]),
        ("控制栏 · 音量面板", ["sys_progress_ll", "sys_bar_progress_title", "Volume", "sb_volum_mute"]),
        ("控制栏 · 系统音量", ["sys_progress_tv", "System", "sys_progress_bar", "v_system_seekbar"]),
        ("控制栏 · AEKE AI 音量", ["ll_aeke_voice", "tv_aeke_voice", "AEKE AI", "asb_aeke_voice_bar", "v_aeke_seekbar"]),
    ],
    "Home_ControlPanel_Bluetooth": [
        ("控制栏 · 根与遮罩", ["rl_control_root", "v_overlay_mask"]),
        ("控制栏 · 系统菜单", ["sys_menu_ll", "switch_rg", "sys_bright", "sys_voice", "sys_ble", "sys_wifi", "sys_led"]),
        ("控制栏 · 蓝牙面板", ["sys_ble_rl2_new", "sys_new_ble_list_con", "sys_new_ble_head", "sys_ble_title", "Bluetooth"]),
        ("控制栏 · 蓝牙操作", ["sys_add_device", "sb_ble_switch_btn", "Add"]),
        ("控制栏 · 蓝牙设备列表", ["sys_ble_fix", "fix_item_rl", "icon_dev", "name_tv", "bind_status", "right_con", "Unpaired", "Pin Unloader", "Smart Handle"]),
    ],
    "Home_ControlPanel_WiFi": [
        ("控制栏 · 根与遮罩", ["rl_control_root", "v_overlay_mask"]),
        ("控制栏 · 系统菜单", ["sys_menu_ll", "switch_rg", "sys_bright", "sys_voice", "sys_ble", "sys_wifi", "sys_led"]),
        ("控制栏 · 网络面板", ["rl_sys_wifi", "tv_wifi_title", "WLAN", "ctl_wifi_nomal", "ctl_wifi_title_right"]),
        ("控制栏 · 网络操作", ["tv_wifi_refresh", "tv_wifi_delete_curr", "Refresh", "Forget"]),
        ("控制栏 · 当前连接", ["ll_wifi_mine_item", "ll_wifi_name_info", "tv_connected_name", "tv_connected_wifi_tag", "tv_connect_statu", "iv_connect_wifi_level", "Connected"]),
        ("控制栏 · WiFi 列表", ["rv_sys_wifi", "ll_wifi_item", "name_tv", "tv_wifi_tag", "lock_iv", "wifi_iv"]),
    ],
    "Home_ControlPanel_LED": [
        ("控制栏 · 根与遮罩", ["rl_control_root", "v_overlay_mask"]),
        ("控制栏 · 系统菜单", ["sys_menu_ll", "switch_rg", "sys_bright", "sys_voice", "sys_ble", "sys_wifi", "sys_led"]),
        ("控制栏 · 氛围灯面板", ["sys_led_rl", "sys_led_title_tv", "Lighting", "switch_btn_led"]),
        ("控制栏 · 氛围灯亮度", ["sys_led_brightness_tv", "led_brightness_progress_container", "seekbar_led_brightness", "v_led_brightness_seekbar"]),
        ("控制栏 · 氛围灯模式", ["sys_led_mode_tv", "sys_led_mode_rv", "tv_mode_name", "Mode", "Constant", "Breath"]),
        ("控制栏 · 氛围灯颜色", ["sys_led_color_tv", "sys_led_color_rv", "tv_color_name", "Color", "iv_selected", "White", "Red", "Flowing"]),
    ],
    "Home_CalendarMore": [
        ("顶栏 / 导航", ["cl_title", "iv_back", "tv_add", "Add Workout", "Schedule"]),
        ("日程 · 本周统计", ["cl_sport_count", "ll_head", "tv_time_count", "Workouts", "Duration", "Calories", "Volume"]),
        ("日程 · 周切换", ["cs_date", "left_icon", "right_icon", "tv_title", "cl_diary", "tv_to_week_report", "Calendar"]),
        ("日程 · 周日历", ["cs_week", "viewPager", "ll_first", "ll_second", "ll_third", "ll_four", "ll_five", "ll_six", "ll_seven", "ll_circe", "progress_bar", "day1", "day2", "Mon", "Today"]),
        ("日程 · 计划列表", ["recycler_course_view", "rl_all_plan_container", "tv_total_title", "tv_all_plan", "Details", "Custom Courses"]),
        ("日程 · 课程项", ["rl_list", "layout_swipe", "tv_title", "tv_content", "tv_progress", "tv_status", "btn_delete", "btn_edit", "Start", "Completed", "Delay", "Remove"]),
    ],
    "DataCenterDetail": [
        ("顶栏 / 导航", ["nav", "ivLeftIcon", "tvTitle", "Data Center", "titleScrollView"]),
        ("数据中心 · 周期切换", ["tv_date_range", "iv_date_left", "iv_date_right", "tv_this_week", "This week", "container"]),
        ("数据中心 · 汇总统计", ["ll_total_infos", "tv_session_num", "tv_session_unit", "Session", "tv_duration", "tv_duration_unit", "tv_total_volum", "tv_total_volum_unit", "tv_total_kcal", "tv_total_kcal_unit", "Workouts", "Duration", "Volume", "Calories"]),
        ("数据中心 · Progress", ["ctl_workout_progress", "tv_progress_title", "Progress", "fl_week_valus", "fl_volum_infos", "wrbv_week_data", "tv_progress_volum", "tv_progress_calories", "Daily Vol", "Workout days", "Lifted"]),
        ("数据中心 · Preferences", ["ctl_workout_preferences", "tv_preferences_title", "Preferences", "ll_preferences_tips", "tv_preferences_desc_tips", "wr_preferences", "ll_training_list", "ll_bargraph", "tv_name1", "tv_num_unit1", "Qigong", "Strength", "Cardio", "Yoga", "Pilates", "Stretching", "Meditation"]),
    ],
    "FloatingTouch": [
        ("悬浮 Touch · 收起球", ["container_touch_2", "layout_contract_2", "iv_contract_album_img_2"]),
    ],
    "TouchMenu": [
        ("悬浮 Touch · 容器", ["container_touch_2", "layout_expand", "touch_layout_bg", "touch_area"]),
        ("悬浮 Touch · 音乐控制", ["float_music_fl", "float_kugou_music_con", "no_kg_play", "btn_previous", "btn_toggle", "toggle_click_img", "btn_next", "Not Playing"]),
        ("悬浮 Touch · 音量", ["seekbar_volume", "seekbar", "icon"]),
        ("悬浮 Touch · 快捷操作", ["go_back_btn", "go_home_btn", "Fold", "Home"]),
        ("悬浮 Touch · 底部工具", ["bottom_tool_layout", "all_tool", "retrieve_the_rope", "sleep", "screen", "Toolbar", "Retract rope", "Sleep", "Wallpaper"]),
    ],
    "Home_FloatingTouch": [
        ("Home · 常规", ["ctl_main_title", "grf_free_traing", "grf_ai_coach", "ll_report", "Today's Effort"]),
        ("悬浮 Touch · 收起球", ["container_touch_2", "layout_contract_2", "iv_contract_album_img_2"]),
    ],
    "Home_FloatingTouchOpen": [
        ("悬浮 Touch · 展开菜单", ["layout_expand", "go_back_btn", "bottom_tool_layout", "all_tool", "float_music_fl"]),
    ],
    "FreeWorkout": [
        ("顶栏 / 导航", ["nav", "ivLeftIcon", "tvTitle", "Free Workout", "titleScrollView"]),
        ("随心练 · 快捷入口", ["start_now", "select_move", "tv_start_now", "tv_select_move", "Practice Freely", "CUSTOM MOVES", "300+ Moves"]),
        ("随心练 · Tab", ["template", "history", "Preset", "Custom", "history_bottom"]),
        ("随心练 · 课程列表", ["action_list", "layout_swipe", "layout_content", "load_more_loading_view"]),
        ("随心练 · 列表项", ["iv_exercise_image", "tv_title", "tv_duration", "tv_created", "tv_created_date", "btn_view", "btn_delete", "Delete", "View"]),
    ],
    "AICoach": [
        ("顶栏 / 导航", ["nav_aicoach", "ivLeftIcon", "mask_view", "orb_aicoach_avatar"]),
        ("AI Coach · 欢迎区", ["tv_aicoach_greeting", "tv_aicoach_subtitle", "Personal Coach", "Training your workout"]),
        ("AI Coach · 主操作", ["tv_generate_course", "Start a Workout"]),
        ("AI Coach · 档案卡片", ["cl_aicoach_profile_card", "iv_aicoach_profile_header_icon", "tv_aicoach_profile_header", "Profile"]),
        ("AI Coach · 档案字段", ["tv_aicoach_profile_goal_label", "tv_aicoach_profile_level_label", "tv_aicoach_profile_weight_label", "Main Goal", "Fitness Level", "Weight"]),
        ("AI Coach · 档案操作", ["tv_aicoach_profile_update", "Update"]),
    ],
    "Course": [
        ("顶栏 / 导航", ["title_bar", "iv_back", "tv_title", "Courses", "ll_title_right", "tv_title_right_txt", "Favorites"]),
        ("课程 · 分类筛选", ["fl_filter_first", "ctl_filter_first_en", "tl_filter_first", "classify_en_iv", "All", "Strength", "Cardio", "Pilates", "Qigong", "Yoga"]),
        ("课程 · 列表容器", ["vp_course", "rf_refreshLayout", "rv_list"]),
        ("课程 · 列表项", ["rl_container", "iv_course_cover", "tv_title", "ll_consume_container", "tv_time", "tv_calorie", "tv_difficult_desc", "ll_instruments", "tv_flag_course_type"]),
    ],
    "Assessment": [
        ("顶栏 / 导航", ["layout_top", "btn_back", "iv_generate_plan", "btn_generate_plan", "Get Program", "iv_history", "btn_history", "History Report"]),
        ("测评 · 全面评估区", ["layout_title", "tv_title", "tv_sub_title", "Full Assessment", "iv_switch_quick", "btn_full_assessment", "Start"]),
        ("测评 · 项目网格", ["recycler_view_assessments", "ivCoverImage", "tv_assessment_name", "tv_assessment_score", "btn_start_assessment", "Body composition", "Body Posture", "Cardio Endurance"]),
        ("测评 · 健康提示", ["layout_tips", "iv_tips", "tv_tips_title", "Health Reminder"]),
    ],
    "Programs": [
        ("顶栏 / 导航", ["nav", "ivLeftIcon", "tvTitle", "Programs", "titleScrollView", "tv_title_right_txt", "My plan"]),
        ("计划 · 分类筛选", ["rl_select_sort", "tl_select_sort", "All", "Build Strength", "Fat Loss", "Health & Wellness"]),
        ("计划 · 列表容器", ["nsv_scroll_view", "view_page_area", "rv_plan_list"]),
        ("计划 · 列表项", ["iv_bg", "tv_title", "ll_time_target", "tv_time", "tv_effect", "ll_status_desc", "In progress"]),
    ],
    "Profile": [
        ("顶栏 / 导航", ["nav", "ivLeftIcon", "tv_switch", "Logout"]),
        ("个人中心 · 用户信息", ["iv_bg_headImg", "ll_top", "tv_name", "tv_state", "iv_bg_settings"]),
        ("个人中心 · 打卡环", ["rl_win_vip", "double_ring_rl", "double_ring_view", "title_tv", "sub_title_tv", "count_tv", "tv_currCount", "Workout Check-in"]),
        ("个人中心 · 菜单列表", ["settings_rv", "name_tv", "next_iv", "Profile", "Settings", "About", "Help"]),
        ("个人中心 · 版本信息", ["right_tv", "3.0.0"]),
        ("个人中心 · 二维码", ["QRCodeApp_iv", "QRCodeWeChat_iv", "download_tv", "Download APP", "set_qr_tip", "Official Community"]),
    ],
    "Login": [
        ("登录 · 标题", ["family_login_title", "Tap Avatar to Log In"]),
        ("登录 · 成员列表", ["family_mode_ll", "rv_member", "icon_iv", "nane_tv", "tag_administrator", "Admin", "Join"]),
        ("登录 · 品牌区", ["slogan_iv", "slogan_tv", "Strength in Numbers"]),
    ],
    "Settings": [
        ("顶栏 / 导航", ["nav", "ivLeftIcon", "tvTitle", "Settings", "titleScrollView"]),
        ("设置 · 列表", ["settings_detail_rv", "name_tv", "next_iv", "right_tv", "sb_right"]),
        ("设置 · 账户与安全", ["Account Security"]),
        ("设置 · 通用项", ["Assistive Touch", "Language", "Region", "Units", "Date & Time", "Beta"]),
        ("设置 · 训练与显示", ["AI Correction Level", "Drop Protect", "Video Subtitles", "Standard"]),
        ("设置 · 设备", ["Reset Device", "settings_list", "item_power_reboot", "Motor restart"]),
    ],
    "Settings_AccountSecurity": [
        ("顶栏 / 导航", ["nav", "ivLeftIcon", "tvTitle", "Account Security"]),
        ("账户安全 · 操作", ["ll_change_password", "Change Password"]),
    ],
    "Settings_Language": [
        ("顶栏 / 导航", ["nav", "ivLeftIcon", "tvTitle", "Language"]),
        ("语言 · 列表", ["rv_list", "tv_language_name", "iv_check", "English", "简体中文"]),
    ],
    "Settings_Units": [
        ("单位 · 弹窗", ["tv_title", "Units", "unit_metric", "unit_imperial", "btn_left", "btn_right", "Cancel", "OK"]),
    ],
    "Settings_DateTime": [
        ("顶栏 / 导航", ["nav", "ivLeftIcon", "tvTitle", "Date & Time"]),
        ("日期时间 · 选项", ["layout_time_format", "24-Hour Time", "sb_time_format", "layout_auto_time_zone", "Auto-Set Time Zone", "layout_time_zone", "tv_time_zone"]),
    ],
    "Settings_AICorrection": [
        ("AI 纠正 · 弹窗", ["name_tv", "AI Correction Level", "panel", "cancel", "layout_relaxed", "layout_standard", "layout_strict", "Relaxed", "Standard", "Strict", "btn_ok"]),
    ],
    "Settings_ResetDevice": [
        ("重置设备 · 弹窗", ["tv_tips", "Resetting", "iv_close", "tv_cancel", "tv_sure", "Cancel", "Confirm"]),
    ],
    "Lifestyle": [
        ("顶栏 / 导航", ["ctl_main_title", "iv_head", "tv_name", "tv_page_home", "tv_life_style", "top_strip", "update_point"]),
        ("Lifestyle · Games", ["Games", "AI Tech"]),
        ("Lifestyle · VS Mode", ["VS Mode", "Multiplayer Arena"]),
        ("Lifestyle · Wallpaper", ["Wallpaper", "Personalized"]),
        ("Lifestyle · Speaker", ["Speaker", "Bluetooth Audio"]),
        ("Lifestyle · Screen Cast", ["Screen Cast", "4K UHD"]),
        ("功能列表容器", ["rv_funcs", "root_view", "rl_root"]),
        ("底部指示", ["second_oval", "three_oval", "viewpager"]),
    ],
}

HOME_QUICK_REF = [
    ("随心练", "Free Workout", "START_BUTTON", "grf_free_traing", "Free Workout"),
    ("AI Coach", "AI 教练", "AI_COACH_BUTTON", "grf_ai_coach", "AI Coach"),
    ("精品课程", "Courses", "COURSE_BUTTON", "grf_all_course", "Courses"),
    ("运动测评", "Assessment", "ASSESSMENT_BUTTON", "grf_evaluation", "Assessment"),
    ("运动计划", "Programs", "PLAN_BUTTON", "grf_sports_plan", "Programs"),
    ("个人中心", "头像", "PROFILE_BUTTON", "iv_head", "—"),
    ("首页", "首页", "HOME_TAB", "tv_page_home", "Home"),
    ("娱乐", "娱乐", "LIFESTYLE_TAB", "tv_life_style", "Lifestyle"),
]


def short_rid(rid: str) -> str:
    return rid.replace("com.aeke.fitnessmirror:id/", "") if rid else ""


def page_name_from_dump(path: Path) -> str:
    stem = path.stem
    if stem.endswith("_window_dump"):
        return stem[: -len("_window_dump")]
    return stem


def resolve_paths(dump: Path) -> tuple[Path, Path]:
    dump = dump.resolve()
    version_dir = dump.parent.parent if dump.parent.name == "window_dump" else dump.parent
    version = version_dir.name
    page = page_name_from_dump(dump)
    md = version_dir / "elements" / f"{page}_elements.md"
    return dump, md


def _package_from_xml(root) -> str:
    for node in root.iter("node"):
        pkg = node.get("package", "")
        if pkg:
            return pkg
    return "com.aeke.fitnessmirror"


def classify(row: dict, feature_rules) -> str:
    hay = " ".join(filter(None, [row["rid"], row["full_rid"], row["text"], row["desc"]]))
    for group, keys in feature_rules:
        if any(k in hay for k in keys):
            return group
    if row["clickable"]:
        return "其他可点击"
    return "其他"


def parse_dump(path: Path, page_name: str = ""):
    root = ET.fromstring(path.read_text(encoding="utf-8"))
    page_name = page_name or page_name_from_dump(path)
    feature_rules = PAGE_FEATURE_RULES.get(page_name, [])
    rows = []
    for node in root.iter("node"):
        full_rid = node.get("resource-id", "")
        text = (node.get("text") or "").strip()
        desc = (node.get("content-desc") or "").strip()
        cls = node.get("class", "").split(".")[-1]
        clickable = node.get("clickable") == "true"
        bounds = node.get("bounds", "")
        if not full_rid and not text and not desc and not clickable:
            continue
        rows.append({
            "rid": short_rid(full_rid),
            "full_rid": full_rid,
            "text": text,
            "desc": desc,
            "class": cls,
            "clickable": clickable,
            "bounds": bounds,
        })

    seen = set()
    uniq = []
    for r in rows:
        key = (r["full_rid"], r["text"], r["bounds"])
        if key in seen:
            continue
        seen.add(key)
        r["feature"] = classify(r, feature_rules)
        uniq.append(r)
    return uniq


def to_markdown(
    rows,
    source: Path,
    app_version: str,
    page_name: str = "",
    package: str = "",
    activity: str = "",
) -> str:
    page_name = page_name or page_name_from_dump(source)
    root = ET.fromstring(source.read_text(encoding="utf-8"))
    package = package or _package_from_xml(root)
    activity = activity or "—"
    ver = app_version.lstrip("v")

    lines = [
        f"# {page_name} 页元素索引",
        "",
        f"- 来源：`{source.name}`",
        f"- App 版本：{ver}",
        f"- 包名：`{package}`",
        f"- Activity：`{activity}`",
        "",
        "> 由 `python S1Pro_UI/dump_page_ui.py <Page>` 或 `parse_window_dump.py` 生成，勿手改。",
        "",
    ]

    if page_name == "Home" and HOME_QUICK_REF:
        lines.extend([
            "## 快速对照（场景脚本常用）",
            "",
            "| 功能 | 中文 | 定位常量建议 | resource-id | 可见文案 |",
            "|------|------|--------------|-------------|----------|",
        ])
        for func, zh, const, rid, label in HOME_QUICK_REF:
            lines.append(f"| {func} | {zh} | `{const}` | `{rid}` | {label} |")
        lines.append("")

    groups = {}
    for r in rows:
        groups.setdefault(r["feature"], []).append(r)

    feature_rules = PAGE_FEATURE_RULES.get(page_name, [])
    order = [g for g, _ in feature_rules] + ["其他可点击", "其他"]
    seen_groups = set()
    for group in order:
        items = groups.get(group)
        if not items:
            continue
        seen_groups.add(group)
        lines.append(f"## {group}")
        lines.append("")
        lines.append("| resource-id | 文案 | 类型 | 可点 | bounds |")
        lines.append("|-------------|------|------|------|--------|")
        for r in items:
            label = r["text"] or r["desc"] or "—"
            click = "是" if r["clickable"] else "否"
            rid = f"`{r['rid']}`" if r["rid"] else "—"
            lines.append(f"| {rid} | {label} | {r['class']} | {click} | `{r['bounds']}` |")
        lines.append("")

    for group, items in groups.items():
        if group in seen_groups:
            continue
        lines.append(f"## {group}")
        lines.append("")
        lines.append("| resource-id | 文案 | 类型 | 可点 | bounds |")
        lines.append("|-------------|------|------|------|--------|")
        for r in items:
            label = r["text"] or r["desc"] or "—"
            click = "是" if r["clickable"] else "否"
            rid = f"`{r['rid']}`" if r["rid"] else "—"
            lines.append(f"| {rid} | {label} | {r['class']} | {click} | `{r['bounds']}` |")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="解析 window_dump.xml 为 Markdown 元素索引")
    parser.add_argument("dump", nargs="?", help="dump.xml 路径")
    parser.add_argument("-o", "--output", help="输出 .md 路径（默认 <version>/elements/*_elements.md）")
    parser.add_argument("--version", default="", help="App 版本号，如 3.0.0.6858")
    parser.add_argument("--page", default="", help="页面名（默认从文件名推断）")
    parser.add_argument("--package", default="", help="包名（默认从 XML 读取）")
    parser.add_argument("--activity", default="", help="Activity 全名")
    args = parser.parse_args()

    dump = Path(args.dump) if args.dump else None
    if dump is None:
        base = Path(__file__).parent
        candidates = sorted(base.glob("*/window_dump/*_window_dump.xml"))
        if not candidates:
            raise SystemExit("未找到 dump 文件，请指定路径（期望 S1Pro_UI/<version>/window_dump/*.xml）")
        dump = candidates[-1]

    dump = dump.resolve()
    version_dir = dump.parent.parent if dump.parent.name == "window_dump" else dump.parent
    version = args.version or version_dir.name.lstrip("v")
    page_name = args.page or page_name_from_dump(dump)
    _, default_md = resolve_paths(dump)
    out = Path(args.output) if args.output else default_md

    rows = parse_dump(dump, page_name=page_name)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        to_markdown(rows, dump, version, page_name, args.package, args.activity),
        encoding="utf-8",
    )
    print(f"已解析 {len(rows)} 个节点 -> {out}")


if __name__ == "__main__":
    main()
