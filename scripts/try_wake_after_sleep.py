# -*- coding: utf-8 -*-
"""从 Home 进入 Sleep/Wallpaper 黑屏，再试探唤醒。"""
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import uiautomator2 as u2
from settings.config import Config

PKG = "com.aeke.fitnessmirror"
MAIN = f"{PKG}/.home.MainActivity"
SLEEP_ID = f"{PKG}:id/sleep"
WALLPAPER_ID = f"{PKG}:id/screen"
HOME_ANCHOR = f"{PKG}:id/grf_free_traing"
FAB = f"{PKG}:id/container_touch_2"
MENU = f"{PKG}:id/layout_expand"


def read_state(d):
    info = d.info or {}
    xml = d.dump_hierarchy(compressed=True)
    return {
        "screenOn": info.get("screenOn"),
        "xml_len": len(xml),
        "home": d(resourceId=HOME_ANCHOR).exists(timeout=2),
        "fab": d(resourceId=FAB).exists(timeout=2),
        "menu": d(resourceId=MENU).exists(timeout=1),
        "activity": d.app_current().get("activity"),
    }


def go_home(d):
    d.app_start(PKG, ".home.MainActivity", stop=False)
    time.sleep(2)
    for _ in range(4):
        if d(resourceId=HOME_ANCHOR).exists(timeout=2):
            return True
        d.press("back")
        time.sleep(0.8)
    d.app_start(PKG, ".home.MainActivity", stop=True)
    time.sleep(3)
    return d(resourceId=HOME_ANCHOR).exists(timeout=5)


def open_menu_click(d, rid, name):
    if not d(resourceId=FAB).exists(timeout=5):
        return False, "悬浮球不可见"
    d(resourceId=FAB).click()
    time.sleep(1.2)
    if not d(resourceId=MENU).exists(timeout=3):
        return False, "菜单未展开"
    btn = d(resourceId=rid)
    if not btn.exists(timeout=3):
        return False, f"{name} 按钮不可见"
    before = read_state(d)
    btn.click()
    time.sleep(2.5)
    after = read_state(d)
    return True, (before, after)


def wake_sequence(d, label):
    print(f"\n--- 唤醒序列: {label} ---")
    steps = [
        ("screen_on", lambda: d.screen_on()),
        ("power", lambda: d.press("power")),
        ("click_center", lambda: d.click(*[x // 2 for x in d.window_size()])),
        ("home", lambda: d.press("home")),
        ("back", lambda: d.press("back")),
    ]
    for name, fn in steps:
        fn()
        time.sleep(2)
        s = read_state(d)
        print(
            f"  {name}: screenOn={s['screenOn']} xml={s['xml_len']} "
            f"home={s['home']} fab={s['fab']} act={s['activity']}"
        )
        if s["home"]:
            print(f"  => 已回 Home（{name}）")
            return True
    return False


def test_mode(d, rid, name):
    print(f"\n{'='*12} 测试 {name} {'='*12}")
    if not go_home(d):
        print("无法回到 Home，跳过")
        return
    print("Home OK:", read_state(d))
    ok, result = open_menu_click(d, rid, name)
    if not ok:
        print("进入失败:", result)
        return
    before, after = result
    print(f"点击前: xml={before['xml_len']} home={before['home']} menu={before['menu']}")
    print(f"点击后: xml={after['xml_len']} home={after['home']} fab={after['fab']} act={after['activity']}")
    changed = before["xml_len"] != after["xml_len"] or before["home"] != after["home"]
    print("UI 变化:", "有" if changed else "无明显变化（可能未进入黑屏）")
    recovered = wake_sequence(d, name)
    print("恢复 Home:", "成功" if recovered else "失败")


def main():
    d = u2.connect(Config().DEVICE_ID)
    test_mode(d, SLEEP_ID, "Sleep")
    go_home(d)
    test_mode(d, WALLPAPER_ID, "Wallpaper")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
