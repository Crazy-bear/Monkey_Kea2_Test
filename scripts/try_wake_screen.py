# -*- coding: utf-8 -*-
"""试探黑屏/休眠后能否用 screen_on 或电源键点亮（需设备 adb 已连接）。"""
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import uiautomator2 as u2
from settings.config import Config


def adb_shell(device_id, *args):
    cmd = ["adb", "-s", device_id, "shell", *args]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    return (r.stdout or "") + (r.stderr or "")


def screen_state(device_id):
    out = adb_shell(device_id, "dumpsys", "power")
    on = None
    for line in out.splitlines():
        line = line.strip()
        if "Display Power" in line or "mScreenOn" in line or "screenState=" in line:
            if "ON" in line.upper() or "true" in line.lower():
                on = True
            elif "OFF" in line.upper() or "false" in line.lower():
                on = False
    return on, out[:500]


def u2_screen_on(d):
    if hasattr(d, "screen_on"):
        d.screen_on()
        return "d.screen_on()"
    d.jsonrpc.wakeUp()
    return "d.jsonrpc.wakeUp()"


def main():
    config = Config()
    device_id = config.DEVICE_ID
    print(f"设备: {device_id}")

    state, _ = subprocess.run(
        ["adb", "-s", device_id, "get-state"],
        capture_output=True, text=True, timeout=10,
    ).stdout, None
    if "device" not in (state or "").lower():
        print(f"adb 未就绪: {state!r}")
        return 1

    d = u2.connect(device_id)
    info = d.info or {}
    before_adb, _ = screen_state(device_id)
    print("\n=== 唤醒前 ===")
    print(f"u2 info.screenOn: {info.get('screenOn')}")
    print(f"adb dumpsys power (推断): {before_adb}")

    steps = []

    # 1) screen_on / wakeUp
    try:
        method = u2_screen_on(d)
        time.sleep(1.5)
        after = d.info.get("screenOn")
        adb_on, _ = screen_state(device_id)
        steps.append((method, after, adb_on))
        print(f"\n[1] {method} -> screenOn={after}, adb={adb_on}")
    except Exception as e:
        print(f"\n[1] screen_on 失败: {e}")

    # 2) KEYCODE_WAKEUP
    try:
        adb_shell(device_id, "input", "keyevent", "KEYCODE_WAKEUP")
        time.sleep(1.5)
        after = d.info.get("screenOn")
        adb_on, _ = screen_state(device_id)
        steps.append(("KEYCODE_WAKEUP", after, adb_on))
        print(f"[2] KEYCODE_WAKEUP -> screenOn={after}, adb={adb_on}")
    except Exception as e:
        print(f"[2] KEYCODE_WAKEUP 失败: {e}")

    # 3) 电源键
    try:
        d.press("power")
        time.sleep(1.5)
        after = d.info.get("screenOn")
        adb_on, _ = screen_state(device_id)
        steps.append(("press(power)", after, adb_on))
        print(f"[3] press(power) -> screenOn={after}, adb={adb_on}")
    except Exception as e:
        print(f"[3] press(power) 失败: {e}")

    # 4) 再按一次电源（部分设备需双击/切换）
    try:
        d.press("power")
        time.sleep(1.5)
        after = d.info.get("screenOn")
        adb_on, _ = screen_state(device_id)
        steps.append(("press(power) x2", after, adb_on))
        print(f"[4] press(power) 再次 -> screenOn={after}, adb={adb_on}")
    except Exception as e:
        print(f"[4] 第二次 power 失败: {e}")

    # 5) 点击屏幕中央
    try:
        w, h = d.window_size()
        d.click(w // 2, h // 2)
        time.sleep(1.5)
        after = d.info.get("screenOn")
        adb_on, _ = screen_state(device_id)
        steps.append(("click(center)", after, adb_on))
        print(f"[5] click(中心) -> screenOn={after}, adb={adb_on}")
    except Exception as e:
        print(f"[5] click 失败: {e}")

    print("\n=== 唤醒后 ===")
    final_info = d.info or {}
    final_adb, _ = screen_state(device_id)
    print(f"u2 info.screenOn: {final_info.get('screenOn')}")
    print(f"adb dumpsys power (推断): {final_adb}")
    pkg = config.PACKAGE_NAME
    current = d.app_current()
    print(f"当前前台: {current}")

    home_ok = d(resourceId=f"{pkg}:id/grf_free_traing").exists(timeout=3)
    print(f"Home 锚点 START_BUTTON 可见: {home_ok}")

    print("\n=== 结论 ===")
    if final_info.get("screenOn") or final_adb:
        print("屏幕层面：已点亮（或原本即为亮屏）")
    else:
        print("屏幕层面：仍为灭屏/无法确认点亮")
    if home_ok:
        print("业务层面：已在 Home 可操作界面")
    else:
        print("业务层面：未回到 Home（可能仍在 Sleep/Wallpaper/其他页）")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
