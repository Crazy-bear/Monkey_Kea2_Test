# -*- coding: utf-8 -*-
"""批量 dump Settings 子页面（设备需停留在 Settings 列表或已登录可导航至 Settings）。"""
import importlib.util
import sys
from pathlib import Path

import uiautomator2 as u2

ROOT = Path(__file__).resolve().parent.parent
S1PRO_UI = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from settings.config import Config

_spec = importlib.util.spec_from_file_location(
    "parse_window_dump", S1PRO_UI / "parse_window_dump.py"
)
_parser = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_parser)

PKG = "com.aeke.fitnessmirror"

# (dump 页面名, 列表项文案, 特殊打开方式)
DETAIL_PAGES = (
    ("Settings_AccountSecurity", "Account Security", None),
    ("Settings_Language", "Language", None),
    ("Settings_Region", "Region", "region_picker"),
    ("Settings_Units", "Units", None),
    ("Settings_DateTime", "Date & Time", None),
    ("Settings_AICorrection", "AI Correction Level", None),
    ("Settings_ResetDevice", "Reset Device", None),
)


def open_detail(d, label, mode):
    if mode == "region_picker":
        row = d(text=label)
        if not row.exists(timeout=3):
            return False
        d.xpath(f'//*[@text="{label}"]/..').click()
        d.sleep(1.2)
        return True
    item = d(text=label)
    if not item.exists(timeout=3):
        return False
    item.click()
    d.sleep(1.2)
    return True


def ensure_settings_list(d):
    title = d(text="Settings", resourceId=f"{PKG}:id/tvTitle")
    if title.exists(timeout=2):
        return True
    back = d(resourceId=f"{PKG}:id/ivLeftIcon")
    for _ in range(4):
        if title.exists(timeout=1):
            return True
        if back.exists(timeout=1):
            back.click()
            d.sleep(0.6)
    return title.exists(timeout=2)


def archive(page_name, xml, app_version):
    ver_dir = S1PRO_UI / f"v{app_version.lstrip('v')}"
    if not ver_dir.name.startswith("v"):
        ver_dir = S1PRO_UI / f"v{app_version}"
    dump_path = ver_dir / "window_dump" / f"{page_name}_window_dump.xml"
    dump_path.parent.mkdir(parents=True, exist_ok=True)
    dump_path.write_text(xml, encoding="utf-8")
    rows = _parser.parse_dump(dump_path, page_name=page_name)
    _, md_path = _parser.resolve_paths(dump_path)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        _parser.to_markdown(rows, dump_path, app_version, page_name, PKG, ""),
        encoding="utf-8",
    )
    return dump_path, md_path, len(rows)


def main():
    config = Config()
    d = u2.connect(config.DEVICE_ID)
    out = adb_version = d.app_info(PKG)["versionName"]

    # 主 Settings 列表
    if ensure_settings_list(d):
        xml = d.dump_hierarchy(compressed=False)
        p, m, n = archive("Settings", xml, out)
        print(f"Settings -> {p} ({n} nodes)")

    for page_name, label, mode in DETAIL_PAGES:
        if not ensure_settings_list(d):
            print(f"skip {page_name}: 不在 Settings 列表")
            continue
        if not open_detail(d, label, mode):
            print(f"skip {page_name}: 未找到 {label}")
            continue
        xml = d.dump_hierarchy(compressed=False)
        p, m, n = archive(page_name, xml, out)
        print(f"{page_name} -> {p} ({n} nodes)")
        # 返回 Settings 列表：先关弹窗，再按返回
        for btn_text in ("Cancel", "OK"):
            btn = d(text=btn_text)
            if btn.exists(timeout=1):
                btn.click()
                d.sleep(0.5)
                break
        back = d(resourceId=f"{PKG}:id/ivLeftIcon")
        for _ in range(3):
            if d(text="Settings", resourceId=f"{PKG}:id/tvTitle").exists(timeout=1):
                break
            if back.exists(timeout=1):
                back.click()
                d.sleep(0.6)
            else:
                d.press("back")
                d.sleep(0.6)

    print("done")


if __name__ == "__main__":
    main()
