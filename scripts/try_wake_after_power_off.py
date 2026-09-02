# -*- coding: utf-8 -*-
"""先灭屏再试探 screen_on / 电源键能否点亮。"""
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import uiautomator2 as u2
from settings.config import Config

PKG = "com.aeke.fitnessmirror"


def adb_shell(device_id, *args):
    cmd = ["adb", "-s", device_id, "shell", *args]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    return (r.stdout or "") + (r.stderr or "")


def read_screen(d, device_id):
    info_on = (d.info or {}).get("screenOn")
    out = adb_shell(device_id, "dumpsys", "display")
    display_on = None
    for line in out.splitlines():
        if "mScreenState=" in line:
            display_on = "ON" in line.upper()
            break
    return info_on, display_on


def try_wake(d, device_id, label, action):
    action()
    time.sleep(2)
    info_on, display_on = read_screen(d, device_id)
    print(f"  [{label}] u2.screenOn={info_on}, display={display_on}")
    return info_on, display_on


def main():
    config = Config()
    device_id = config.DEVICE_ID
    d = u2.connect(device_id)

    print("=== 1. 灭屏前 ===")
    print(read_screen(d, device_id))

    print("\n=== 2. 模拟灭屏：按一次电源键 ===")
    d.press("power")
    time.sleep(2)
    before_wake = read_screen(d, device_id)
    print(f"灭屏后: u2.screenOn={before_wake[0]}, display={before_wake[1]}")

    if before_wake[0] is not False and before_wake[1] is not False:
        print("（设备可能未真正灭屏，或 Sleep 模式与系统灭屏不同）")

    print("\n=== 3. 依次尝试唤醒 ===")
    results = []

    results.append(try_wake(d, device_id, "screen_on", lambda: d.screen_on()))

    results.append(
        try_wake(
            d,
            device_id,
            "KEYCODE_WAKEUP",
            lambda: adb_shell(device_id, "input", "keyevent", "224"),
        )
    )

    results.append(try_wake(d, device_id, "press(power)", lambda: d.press("power")))

    w, h = d.window_size()
    results.append(
        try_wake(d, device_id, "click(center)", lambda: d.click(w // 2, h // 2))
    )

    print("\n=== 4. 唤醒后前台与 Home ===")
    print(f"app_current: {d.app_current()}")
    home_ok = d(resourceId=f"{PKG}:id/grf_free_traing").exists(timeout=3)
    print(f"Home START_BUTTON: {home_ok}")

    lit = any(r[0] or r[1] for r in results if r[0] is not False or r[1] is not False)
    print("\n=== 结论（系统灭屏场景）===")
    if before_wake[0] is False or before_wake[1] is False:
        if lit:
            print("screen_on / 电源键 / 点击 至少有一种能点亮系统屏幕")
        else:
            print("未能确认点亮（请查看上方每步 screenOn 输出）")
    else:
        print("未能进入系统灭屏状态，无法验证唤醒；Sleep/Wallpaper 黑屏需单独测")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
