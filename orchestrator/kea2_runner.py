# -*- coding: utf-8 -*-
"""
组装并执行 kea2 run 子进程。

Kea2 CLI 注意点（踩坑汇总）：
1. --act-blacklist-file 的值必须是设备路径；本地 configs/abl.strings 由 Kea2 内部 push。
2. 不能只写 --act-blacklist-file 无值，否则 argparse 会把 propertytest 当下一个参数值，
   导致 UnboundLocalError / discover 失败。
3. 子进程需 PYTHONPATH=项目根，否则 scenarios/pages 无法 import。
"""
import os
import re
import shutil
import subprocess
import sys

from settings.logging_config import logger
from orchestrator.kea2_project import (
    ensure_kea2_project_ready,
    generate_kea2_native_report,
    build_kea2_subprocess_env,
)
from orchestrator.module_catalog import (
    KEA2_DEVICE_AWL_PATH,
    KEA2_LOCK_MODULES_ENV,
    resolve_lock_modules_from_config,
    whitelist_activities_for_modules,
    write_awl_strings,
)

# Kea2 fastbotManager 推送本地 configs/abl.strings 到此设备路径
KEA2_DEVICE_ABL_PATH = "/sdcard/.kea2/abl.strings"


def _kea2_executable():
    wrapper = os.path.join(os.path.dirname(__file__), "_kea2_main.py")
    if os.path.isfile(wrapper):
        return [sys.executable, "-B", wrapper]
    exe = shutil.which("kea2")
    if exe:
        return [exe]
    scripts = os.path.join(os.path.dirname(sys.executable), "Scripts", "kea2.exe")
    if os.path.isfile(scripts):
        return [scripts]
    return ["kea2"]


def build_kea2_command(config, kea2_output_dir, lock_modules=None):
    """构建 kea2 run 命令（不含 propertytest discover 部分）。

    指定模块时写 awl.strings 并传白名单（与黑名单互斥）；
    all 时传现有黑名单。
    """
    cmd = [
        *_kea2_executable(),
        "run",
        "-s", config.DEVICE_ID,
        "-p", config.PACKAGE_NAME,
        "-o", kea2_output_dir,
        "--running-minutes", str(config.KEA2_RUNNING_MINUTES),
        "--throttle", str(config.KEA2_THROTTLE),
    ]
    if config.KEA2_MAX_STEP:
        cmd.extend(["--max-step", str(config.KEA2_MAX_STEP)])

    project_root = config._project_root()
    if lock_modules:
        acts = whitelist_activities_for_modules(lock_modules)
        write_awl_strings(project_root, acts)
        cmd.extend(["--act-whitelist-file", KEA2_DEVICE_AWL_PATH])
        logger.info(
            "模块锁白名单 (%s): %d 个 Activity",
            ",".join(lock_modules),
            len(acts),
        )
    else:
        abl = os.path.join(project_root, "configs", "abl.strings")
        if os.path.isfile(abl) and os.path.getsize(abl) > 0:
            cmd.extend(["--act-blacklist-file", KEA2_DEVICE_ABL_PATH])

    return cmd


def _pattern_to_module(pattern):
    """test_home.py -> scenarios.test_home（供 unittest 按模块加载）。"""
    name = os.path.basename(pattern)
    if name.endswith(".py"):
        name = name[:-3]
    return f"scenarios.{name}"


def build_discover_args(config):
    """propertytest 子命令参数（作为 kea2 run 的 trailing extra）。

    unittest discover 多次 ``-p`` 时 argparse 只保留最后一个，导致仅末位脚本被 Load property。
    多场景时用 ``scenarios.test_xxx`` 模块列表；单场景或 ``test_*.py`` 仍走 discover。
    """
    scenarios_dir = config.get_scenarios_dir()
    patterns = config.get_scenario_patterns()
    if len(patterns) == 1:
        return ["propertytest", "discover", "-s", scenarios_dir, "-p", patterns[0]]
    modules = [_pattern_to_module(p) for p in patterns]
    return ["propertytest", *modules]


def validate_kea2_preflight(config):
    """
    启动 Kea2 前校验：项目初始化、场景 import、ADB 设备。
    Returns:
        (bool, str): 是否通过，错误信息
    """
    project_root = config._project_root()
    ok, err = ensure_kea2_project_ready(project_root)
    if not ok:
        return False, err

    scenarios_dir = config.get_scenarios_dir()
    if not os.path.isdir(scenarios_dir):
        return False, f"场景目录不存在: {scenarios_dir}"

    patterns = config.get_scenario_patterns()
    import glob
    scripts = []
    for pat in patterns:
        scripts.extend(glob.glob(os.path.join(scenarios_dir, pat)))
    if not scripts:
        return False, f"未找到场景脚本: {patterns}"

    env = build_kea2_subprocess_env(project_root)
    if len(patterns) == 1:
        probe_paths = [os.path.join(scenarios_dir, os.path.basename(scripts[0]))]
    else:
        probe_paths = scripts

    for probe in probe_paths:
        proc = subprocess.run(
            [
                sys.executable, "-c",
                "import importlib.util, sys, os; "
                "root=os.environ.get('PYTHONPATH','').split(os.pathsep)[0]; "
                "scenarios=sys.argv[1]; path=sys.argv[2]; "
                "sys.path.insert(0, root); "
                "spec=importlib.util.spec_from_file_location('kea2_probe', path); "
                "m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)",
                scenarios_dir,
                probe,
            ],
            cwd=project_root,
            env=env,
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            detail = (proc.stderr or proc.stdout or "").strip()
            return False, f"场景脚本 import 失败 ({os.path.basename(probe)}): {detail[:400]}"

    try:
        from core.adb_client import ADBClient
        adb = ADBClient(device_id=config.DEVICE_ID)
        devices = adb.get_connected_devices()
        if config.DEVICE_ID not in devices:
            return False, f"设备未连接: {config.DEVICE_ID}，当前: {devices or '无'}"
        # Fastbot NanoHTTPD 需要可写 tmp；本机 ROM 没有 /tmp。
        adb.run_command(
            ["adb", "-s", config.DEVICE_ID, "shell", "mkdir", "-p", "/data/local/tmp"],
            capture_output=True,
        )
    except Exception as e:
        return False, f"ADB 检查失败: {e}"

    return True, ""


def _has_kea2_artifacts(kea2_output_dir):
    if not os.path.isdir(kea2_output_dir):
        return False
    for name in os.listdir(kea2_output_dir):
        if name.startswith("result_") or name.startswith("res_"):
            return True
    return False


def _parse_kea2_failure(combined, exit_code):
    """从子进程输出提取可读错误信息。"""
    if "PermissionError" in combined or "Permission denied" in combined:
        return (
            "Kea2 PermissionError（site-packages __pycache__）。"
            "请确认 configs/__pycache__ 已存在（最新代码会自动创建）。"
        )
    if "UnboundLocalError" in combined and "current" in combined:
        return (
            "Kea2 命令行解析失败：--act-blacklist-file 误吞 propertytest。"
            "请更新 orchestrator/kea2_runner.py（需传设备路径 /sdcard/.kea2/abl.strings）。"
        )
    if "ModuleNotFoundError" in combined or "No module named 'scenarios'" in combined:
        return "场景 import 失败：缺少 PYTHONPATH=项目根。"
    # Fastbot 崩溃后的清理也会带 AdbError，须先于通用 ADB 判断。
    if (
        "Fastbot Aborted" in combined
        or "getTmpBucket" in combined
        or "NanoHTTPD" in combined
    ):
        return (
            "Fastbot 代理进程崩溃：NanoHTTPD 无法创建临时文件（设备没有可写 /tmp）。"
            "已在 Kea2 启动命令中指定 java.io.tmpdir=/data/local/tmp，请重新跑测。"
        )
    if "Unable to connect to uiautomator2 server" in combined:
        # 启动瞬间常见一次 retry；若已连上或退出码为 0，不算失败原因
        recovered = (
            exit_code == 0
            or "Connected to fastbot server" in combined
            or "// Monkey finished" in combined
            or "Bug report saved" in combined
        )
        if not recovered:
            return (
                "无法连接 uiautomator2。请执行 python -m uiautomator2 init，"
                "并确认设备未休眠、ATX 仍在运行。"
            )
    if "AdbError" in combined or "adbutils.errors.AdbError" in combined:
        return (
            "ADB push/pull 失败。若含 act-blacklist-file，"
            "请确认未传 Windows 本地路径；设备需可写 /sdcard/.kea2/。"
        )
    if "not initialized" in combined.lower():
        return "Kea2 项目未初始化，请在项目根执行 kea2 init"

    # 属性失败：优先摘要，避免把 Traceback 首行当原因
    m = re.search(
        r"\[Property Execution Summary\]\s*Errors:\s*(\d+)\s*,\s*Fails:\s*(\d+)",
        combined,
    )
    if m:
        errors, fails = int(m.group(1)), int(m.group(2))
        if fails or errors:
            return f"属性执行失败：Fails={fails}, Errors={errors}"

    assert_lines = [
        ln.strip()
        for ln in combined.splitlines()
        if "AssertionError" in ln or "assert " in ln.lower()
    ]
    if assert_lines:
        # 去重并截断
        uniq = []
        for ln in assert_lines:
            if ln not in uniq:
                uniq.append(ln)
        return ("；".join(uniq[:3]))[:500]

    if exit_code != 0:
        for line in combined.splitlines():
            text = line.strip()
            if not text:
                continue
            if text.startswith("Traceback") or text.startswith("File \""):
                continue
            if "Error" in text or "ERROR" in text or "Failed" in text:
                return text[:500]
        from orchestrator.kea2_result_parser import format_kea2_exit_code

        return f"Kea2 退出码 {format_kea2_exit_code(exit_code)}"
    return ""


def run_kea2(config, kea2_output_dir, cwd=None):
    """
    执行 Kea2 测试。

    Returns:
        tuple: (exit_code, error_message)
    """
    os.makedirs(kea2_output_dir, exist_ok=True)
    project_root = config._project_root()
    run_cwd = cwd or project_root

    ok, err = validate_kea2_preflight(config)
    if not ok:
        logger.error(err)
        return 4, err

    lock_modules = resolve_lock_modules_from_config(config)
    if lock_modules:
        from orchestrator.module_bootstrap import bootstrap_locked_module

        bootstrap_locked_module(config.DEVICE_ID, lock_modules)

    cmd = build_kea2_command(config, kea2_output_dir, lock_modules=lock_modules)
    cmd.extend(build_discover_args(config))

    logger.info(f"启动 Kea2: {' '.join(cmd)}")

    env = build_kea2_subprocess_env(project_root)
    if lock_modules:
        env[KEA2_LOCK_MODULES_ENV] = ",".join(lock_modules)
    else:
        env.pop(KEA2_LOCK_MODULES_ENV, None)
    log_path = os.path.join(os.path.dirname(kea2_output_dir), "kea2_subprocess.log")
    output_lines = []

    try:
        proc = subprocess.Popen(
            cmd,
            cwd=run_cwd,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        assert proc.stdout is not None
        for line in proc.stdout:
            line = line.rstrip("\n\r")
            output_lines.append(line)
            if line.strip():
                if any(k in line for k in ("ERROR", "Error", "Traceback", "Permission", "AdbError")):
                    logger.error(line)
                else:
                    logger.info(line)
        proc.wait()
        exit_code = proc.returncode if proc.returncode is not None else 4

        combined = "\n".join(output_lines)
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(combined)
            logger.info(f"Kea2 子进程完整日志: {log_path}")
        except OSError:
            pass

        error_msg = _parse_kea2_failure(combined, exit_code)

        if exit_code == 0 and not _has_kea2_artifacts(kea2_output_dir):
            exit_code = 4
            error_msg = error_msg or "Kea2 未产生测试结果（可能未真正运行）"

        if exit_code == 0 or _has_kea2_artifacts(kea2_output_dir):
            generate_kea2_native_report(project_root, kea2_output_dir)

        logger.info(f"Kea2 退出码: {exit_code}")
        return exit_code, error_msg
    except FileNotFoundError:
        msg = "未找到 kea2 命令，请执行: pip install kea2-python"
        logger.error(msg)
        return 4, msg
    except Exception as e:
        logger.error(f"Kea2 执行异常: {e}")
        return 4, str(e)
