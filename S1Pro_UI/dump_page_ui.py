# -*- coding: utf-8 -*-
"""通过 ADB dump 当前页面 UI 树，归档到 window_dump/ 并解析为 elements/ 下的 Markdown。"""
import argparse
import importlib.util
import re
import sys
from pathlib import Path
from typing import Tuple

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.adb_client import ADBClient
from settings.config import Config

S1PRO_UI = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location(
    "parse_window_dump", S1PRO_UI / "parse_window_dump.py"
)
_parser = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_parser)
parse_dump = _parser.parse_dump
to_markdown = _parser.to_markdown
resolve_paths = _parser.resolve_paths

REMOTE_DUMP = "/sdcard/kea2_window_dump.xml"

# 悬浮 Touch 为 APPLICATION_OVERLAY，adb uiautomator dump 抓不到完整节点，需 uiautomator2。
U2_DUMP_PAGES = frozenset({
    "FloatingTouch",
    "TouchMenu",
    "Home_FloatingTouch",
    "Home_FloatingTouchOpen",
})


def dump_ui_via_u2(device_id: str, local_path: Path) -> None:
    import uiautomator2 as u2

    d = u2.connect(device_id)
    xml = d.dump_hierarchy(compressed=False)
    local_path.parent.mkdir(parents=True, exist_ok=True)
    local_path.write_text(xml, encoding="utf-8")

# 悬浮 Touch 等为 APPLICATION_OVERLAY，adb uiautomator dump 无法捕获，需 uiautomator2。
U2_DUMP_PAGES = frozenset({
    "TouchMenu",
    "FloatingTouch",
    "Home_FloatingTouch",
    "Home_FloatingTouchOpen",
})


def normalize_page_name(name: str) -> str:
    """Home / home -> Home；用于 {Page}_window_dump.xml 命名。"""
    name = name.strip()
    if not name:
        raise ValueError("页面名称不能为空")
    return name[0].upper() + name[1:]


def version_dir_name(version: str) -> str:
    version = (version or "unknown").strip()
    return version if version.startswith("v") else f"v{version}"


def get_app_version(adb: ADBClient, package: str) -> str:
    out = adb.shell("dumpsys", "package", package, timeout=15)
    m = re.search(r"versionName=([^\s]+)", out)
    return m.group(1) if m else "unknown"


def get_current_activity(adb: ADBClient) -> str:
    out = adb.shell("dumpsys", "window", "displays", timeout=15)
    m = re.search(r"mCurrentFocus=Window\{[^}]+\s+\S+/(\S+)\}", out)
    if m:
        return m.group(1)
    m = re.search(r"mFocusedApp=AppWindowToken\{[^}]+\s+token=Token\{[^}]+\s+ActivityRecord\{[^}]+\s+\S+\s+(\S+)\s", out)
    return m.group(1) if m else ""


def dump_ui_to_device(adb: ADBClient) -> None:
    out = adb.shell("uiautomator", "dump", REMOTE_DUMP, timeout=30)
    if "UI hierchary dumped" not in out and "UI hierarchy dumped" not in out:
        raise RuntimeError(f"uiautomator dump 失败: {out.strip() or '(无输出)'}")


def pull_dump(adb: ADBClient, local_path: Path) -> None:
    local_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["adb", "-s", adb.device_id, "pull", REMOTE_DUMP, str(local_path)]
    stdout, stderr = adb.run_command(cmd, capture_output=True, timeout=30)
    if not local_path.is_file() or local_path.stat().st_size == 0:
        raise RuntimeError(f"pull 失败: {stderr or stdout}")
    adb.shell("rm", "-f", REMOTE_DUMP, timeout=10)


def archive_and_parse(
    dump_path: Path,
    *,
    app_version: str,
    page_name: str,
    package: str,
    activity: str,
) -> Path:
    rows = parse_dump(dump_path, page_name=page_name)
    _, md_path = resolve_paths(dump_path)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        to_markdown(rows, dump_path, app_version, page_name, package, activity),
        encoding="utf-8",
    )
    return md_path


def run(page: str, device_id: str = "", package: str = "", version: str = "") -> Tuple[Path, Path]:
    page_name = normalize_page_name(page)
    config = Config()
    device_id = device_id or config.DEVICE_ID
    package = package or config.PACKAGE_NAME

    adb = ADBClient(device_id=device_id)
    if not adb.is_device_connected():
        raise RuntimeError(f"设备未连接: {device_id}")

    app_version = version or get_app_version(adb, package)
    ver_dir = S1PRO_UI / version_dir_name(app_version)
    dump_path = ver_dir / "window_dump" / f"{page_name}_window_dump.xml"
    activity = get_current_activity(adb)

    if page_name in U2_DUMP_PAGES:
        dump_ui_via_u2(device_id, dump_path)
    else:
        dump_ui_to_device(adb)
        pull_dump(adb, dump_path)
    md_path = archive_and_parse(
        dump_path,
        app_version=app_version,
        page_name=page_name,
        package=package,
        activity=activity,
    )
    return dump_path, md_path


def main():
    parser = argparse.ArgumentParser(
        description="ADB dump UI 树 → window_dump/{Page}_window_dump.xml + elements/{Page}_elements.md"
    )
    parser.add_argument("page", help="页面名，如 Home、Course、Profile")
    parser.add_argument("-s", "--device", default="", help="ADB 设备 ID（默认读 config）")
    parser.add_argument("-p", "--package", default="", help="应用包名（默认 com.aeke.fitnessmirror）")
    parser.add_argument("--version", default="", help="App 版本号（默认 adb 读取 versionName）")
    args = parser.parse_args()

    dump_path, md_path = run(args.page, args.device, args.package, args.version)
    rows = parse_dump(dump_path, page_name=normalize_page_name(args.page))
    print(f"已归档 XML  -> {dump_path}")
    print(f"已生成 MD   -> {md_path} ({len(rows)} 个节点)")


if __name__ == "__main__":
    main()
