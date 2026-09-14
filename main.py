# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2025/1/10

稳定性测试主入口：Kea2（默认）/ Monkey，含性能监控、Logcat、统一报告。
"""

import os
import sys
import argparse
import json

from settings.config import Config
from core.adb_client import ADBClient
from core.monkey_runner import MonkeyRunner
from core.logcat_handler import LogcatHandler
from core.report_generator import ReportGenerator
from core.utils import get_timestamp, create_output_dirs
from settings.logging_config import logger
from orchestrator.test_session import TestSession, set_lock_modules
from orchestrator.kea2_runner import run_kea2
from orchestrator.kea2_result_parser import (
    parse_kea2_output,
    kea2_exit_failed,
    format_exploration_summary,
    extract_fastbot_seed,
)
from orchestrator.module_catalog import resolve_lock_modules_from_config
from orchestrator.report_builder import (
    load_performance_data,
    build_report_data,
    finalize_report_data,
    load_kea2_from_output_dir,
    load_report_only_meta,
    is_blank_meta,
)


def run_validate_only(config, engine=None):
    """仅校验配置并退出，不连接设备。"""
    eng = engine or config.TEST_ENGINE
    ok, errors = config.validate(engine=eng)
    if ok:
        logger.info(f"配置校验通过 (engine={eng})")
        return 0
    for e in errors:
        logger.error(e)
    return 1


def run_report_only(report_from_dir, output_file, format_type="html", baseline_file=None):
    """从已有输出目录生成报告（不执行测试）。"""
    logcat_file = os.path.join(report_from_dir, "logcat.log")
    if not os.path.isfile(logcat_file):
        logger.error(f"未找到 {logcat_file}")
        return 1

    config = Config()
    logcat_handler = LogcatHandler(config)
    crashes = logcat_handler.detect_crashes(logcat_file)
    log_analysis = logcat_handler.analyze_logs(logcat_file)
    performance_data, performance_summary = load_performance_data(
        os.path.join(report_from_dir, "performance")
    )
    kea2_result = load_kea2_from_output_dir(report_from_dir)

    report_generator = ReportGenerator()
    if baseline_file and os.path.isfile(baseline_file):
        report_generator.load_baseline(baseline_file)

    engine = "kea2" if kea2_result else "monkey"
    output_meta = load_report_only_meta(
        report_from_dir, config=config, kea2_result=kea2_result
    )
    output_meta["test_engine"] = engine
    report_data = build_report_data(
        config,
        output_meta,
        crashes,
        log_analysis,
        performance_data,
        performance_summary,
        None,
        report_generator,
        kea2_result=kea2_result,
    )
    report_data = finalize_report_data(report_data, report_generator)
    # 元数据已回填时不再强行覆盖为 N/A
    if output_meta.get("device_id"):
        report_data["device_id"] = output_meta["device_id"]
    if output_meta.get("package_name"):
        report_data["package_name"] = output_meta["package_name"]
    if not is_blank_meta(output_meta.get("device_version_name")):
        report_data["device_version_name"] = output_meta["device_version_name"]
    if not is_blank_meta(output_meta.get("firmware_version")):
        report_data["firmware_version"] = output_meta["firmware_version"]
    if output_meta.get("report_only") and not is_blank_meta(output_meta.get("seed_value")):
        report_data["seed_value"] = output_meta["seed_value"]
    elif output_meta.get("report_only") and is_blank_meta(report_data.get("seed_value")):
        report_data["seed_value"] = "N/A"

    if not output_file:
        output_file = os.path.join(report_from_dir, f"report.{format_type}")
    report_generator.generate_report(report_data, output_file, format_type)

    json_path = os.path.splitext(output_file)[0] + ".json"
    if json_path != output_file:
        report_generator.generate_report(report_data, json_path, "json")

    logger.info(f"报告已生成: {output_file}")
    level = (report_data.get("gate_status") or {}).get("level") or "pass"
    return 0 if level != "fail" else 1


def _write_reports(config, output_dir, report_data, report_generator, format_type):
    report_file = os.path.join(output_dir, f"report.{format_type}")
    report_json_file = os.path.join(output_dir, "report.json")
    report_generator.generate_report(report_data, report_file, format_type)
    report_generator.generate_report(report_data, report_json_file, "json")
    return report_file, report_json_file


def run_monkey_test(config, output_dir, report_generator, format_type):
    adb_client = ADBClient(device_id=config.DEVICE_ID)
    monkey_runner = MonkeyRunner(adb_client, config)

    monkey_log_file = os.path.join(output_dir, "monkey.log")
    logcat_file = os.path.join(output_dir, "logcat.log")
    performance_dir = os.path.join(output_dir, "performance")

    session = TestSession(config, output_dir, config.get_monkey_timeout_seconds() + 120)
    session.start_sidecars(logcat_file, performance_dir)

    device_version_name = config.DeviceVersionName
    firmware_version = config.FirmwareVersion

    logger.info(
        f"开始 Monkey 测试 - 设备: {config.DEVICE_ID}, 事件: {config.EVENT_COUNT}, "
        f"应用: {device_version_name}, 固件: {firmware_version}"
    )
    monkey_ok = False
    try:
        monkey_runner.run_monkey(monkey_log_file)
        monkey_ok = True
    except Exception as e:
        logger.error(f"Monkey 测试异常: {e}")
    finally:
        session.stop_sidecars(wait_after_engine=2 if monkey_ok else 0)

    logcat_handler = LogcatHandler(config)
    crashes = logcat_handler.detect_crashes(logcat_file)
    log_analysis = logcat_handler.analyze_logs(logcat_file)
    performance_data, performance_summary = load_performance_data(performance_dir)
    if session.performance_monitor and session.performance_monitor.get_data():
        performance_data = session.performance_monitor.get_data()
    if performance_summary is None and session.performance_monitor:
        performance_summary = session.performance_monitor.get_summary()

    report_data = build_report_data(
        config,
        {
            "test_engine": "monkey",
            "start_time": session.start_time,
            "end_time": session.end_time,
            "duration": session.duration_str(),
            "execution_count": config.EVENT_COUNT,
            "execution_label": f"{config.EVENT_COUNT} 事件",
            "run_output_dir": output_dir,
            "device_id": config.DEVICE_ID,
            "package_name": config.PACKAGE_NAME,
            "device_version_name": device_version_name,
            "firmware_version": firmware_version,
            "seed_value": config.SEED,
        },
        crashes,
        log_analysis,
        performance_data,
        performance_summary,
        session.performance_monitor,
        report_generator,
        kea2_result=None,
    )
    report_data = finalize_report_data(report_data, report_generator)
    return report_data


def run_kea2_test(config, output_dir, report_generator, format_type):
    logcat_file = os.path.join(output_dir, "logcat.log")
    performance_dir = os.path.join(output_dir, "performance")
    kea2_output_dir = os.path.join(output_dir, "kea2")

    lock_modules = resolve_lock_modules_from_config(config)
    set_lock_modules(lock_modules)

    session = TestSession(config, output_dir, config.get_kea2_logcat_max_seconds())
    session.start_sidecars(logcat_file, performance_dir, enable_coverage_sampler=True)

    # 开跑前固化环境指纹，避免跑完后设备离线或报告回填成 Unknown
    device_version_name = config.DeviceVersionName
    firmware_version = config.FirmwareVersion

    lock_label = ",".join(lock_modules) if lock_modules else "all(全应用)"
    logger.info(
        f"开始 Kea2 测试 - 设备: {config.DEVICE_ID}, "
        f"时长: {config.KEA2_RUNNING_MINUTES} 分钟, 模块: {lock_label}, "
        f"应用: {device_version_name}, 固件: {firmware_version}"
    )
    exit_code = 4
    kea2_error = ""
    try:
        exit_code, kea2_error = run_kea2(config, kea2_output_dir)
    except Exception as e:
        logger.error(f"Kea2 测试异常: {e}")
        kea2_error = str(e)
    finally:
        session.stop_sidecars(wait_after_engine=2)

    seed_value = extract_fastbot_seed(kea2_output_dir, run_output_dir=output_dir) or str(
        config.SEED
    )

    meta = {
        "exit_code": exit_code,
        "error_message": kea2_error,
        "running_minutes": config.KEA2_RUNNING_MINUTES,
        "scenarios": config.get_scenario_patterns(),
        "lock_modules": lock_modules,
        "device_id": config.DEVICE_ID,
        "package_name": config.PACKAGE_NAME,
        "device_version_name": device_version_name,
        "firmware_version": firmware_version,
        # Kea2：Fastbot 日志中的真实 seed；取不到才退回 config.SEED
        "seed_value": seed_value,
        "throttle_ms": int(os.environ.get("KEA2_THROTTLE", "200") or 200),
        "start_time": session.start_time,
        "end_time": session.end_time,
        "duration": session.duration_str(),
    }
    with open(os.path.join(output_dir, "kea2_run_meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    kea2_result = parse_kea2_output(
        kea2_output_dir,
        exit_code,
        error_message=kea2_error,
        run_output_dir=output_dir,
        lock_modules=lock_modules,
    )
    kea2_result["running_minutes"] = config.KEA2_RUNNING_MINUTES
    if kea2_result.get("seed_value"):
        seed_value = str(kea2_result["seed_value"])

    summary = format_exploration_summary(kea2_result.get("exploration"))
    for line in summary.splitlines():
        logger.info(line)

    logcat_handler = LogcatHandler(config)
    crashes = logcat_handler.detect_crashes(logcat_file)
    log_analysis = logcat_handler.analyze_logs(logcat_file)
    performance_data, performance_summary = load_performance_data(performance_dir)
    if session.performance_monitor and session.performance_monitor.get_data():
        performance_data = session.performance_monitor.get_data()
    if performance_summary is None and session.performance_monitor:
        performance_summary = session.performance_monitor.get_summary()

    scenario_label = ",".join(config.get_scenario_patterns())
    report_data = build_report_data(
        config,
        {
            "test_engine": "kea2",
            "start_time": session.start_time,
            "end_time": session.end_time,
            "duration": session.duration_str(),
            "execution_count": config.KEA2_RUNNING_MINUTES,
            "execution_label": f"{config.KEA2_RUNNING_MINUTES} 分钟",
            "scenarios": scenario_label,
            "lock_modules": lock_modules,
            "run_output_dir": output_dir,
            "device_id": config.DEVICE_ID,
            "package_name": config.PACKAGE_NAME,
            "device_version_name": device_version_name,
            "firmware_version": firmware_version,
            "seed_value": seed_value,
            "throttle_ms": int(os.environ.get("KEA2_THROTTLE", "200") or 200),
        },
        crashes,
        log_analysis,
        performance_data,
        performance_summary,
        session.performance_monitor,
        report_generator,
        kea2_result=kea2_result,
    )
    report_data = finalize_report_data(report_data, report_generator)
    return report_data, exit_code


def main():
    parser = argparse.ArgumentParser(description="【S1Pro 力量镜】稳定性测试（Kea2 / Monkey）")
    parser.add_argument("--device", type=str, help="设备 ID")
    parser.add_argument("--package", type=str, help="应用包名")
    parser.add_argument("--events", type=int, help="Monkey 事件数量")
    parser.add_argument(
        "--engine",
        type=str,
        choices=["monkey", "kea2"],
        help="测试引擎（默认 kea2）",
    )
    parser.add_argument("--running-minutes", type=int, help="Kea2 运行时长（分钟）")
    parser.add_argument(
        "--scenarios",
        type=str,
        default=None,
        help="场景模块，逗号分隔或 all（默认读 config.ini / KEA2_SCENARIOS）",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="输出目录（默认读 config.ini / KEA2_OUTPUT_DIR）",
    )
    parser.add_argument(
        "--format",
        type=str,
        default="html",
        choices=["html", "json"],
        help="报告格式",
    )
    parser.add_argument("--profile", type=str, help="config.ini profile 名称")
    parser.add_argument("--baseline", type=str, help="性能基线 JSON 文件路径")
    parser.add_argument("--validate-only", action="store_true", help="仅校验配置后退出")
    parser.add_argument("--report-only", type=str, metavar="DIR", help="从已有日志生成报告")
    parser.add_argument("--report-output", type=str, help="与 --report-only 配合，指定报告输出路径")
    args = parser.parse_args()

    engine = args.engine or os.environ.get("TEST_ENGINE", "kea2")
    config = Config(profile=args.profile, test_engine=engine)
    if args.device:
        config.DEVICE_ID = args.device
    if args.package:
        config.PACKAGE_NAME = args.package
    if args.events:
        config.EVENT_COUNT = args.events
    if args.running_minutes:
        config.KEA2_RUNNING_MINUTES = args.running_minutes
    if args.scenarios is not None:
        config.set_scenario_filter(args.scenarios)

    output_root = args.output if args.output is not None else config.get_output_dir()

    if args.validate_only:
        return run_validate_only(config, engine=config.TEST_ENGINE)

    if args.report_only:
        return run_report_only(
            args.report_only,
            args.report_output,
            args.format,
            baseline_file=args.baseline,
        )

    ok, errors = config.validate(engine=config.TEST_ENGINE)
    if not ok:
        for e in errors:
            logger.error(e)
        return 1

    timestamp = get_timestamp()
    output_dir = os.path.join(output_root, timestamp)
    create_output_dirs(output_dir)

    report_generator = ReportGenerator()
    if args.baseline and os.path.isfile(args.baseline):
        report_generator.load_baseline(args.baseline)

    exit_code = 0
    if config.TEST_ENGINE == "kea2":
        report_data, kea2_exit = run_kea2_test(config, output_dir, report_generator, args.format)
        report_file, report_json_file = _write_reports(
            config, output_dir, report_data, report_generator, args.format
        )
        gate = report_data.get("gate_status", {})
        level = gate.get("level") or ("pass" if gate.get("passed", True) else "fail")
        # CI：仅硬失败（Crash / Kea2 2·3·4）拦截；属性哨兵等为 WARN 不拦
        hard_kea2 = kea2_exit in (2, 3, 4)
        if level == "fail" or hard_kea2:
            exit_code = 1
        logger.info(
            f"Kea2 测试完成 - 门禁: {level.upper()}"
            f"{'（硬失败）' if exit_code else ('（有告警）' if level == 'warn' else '')}, "
            f"报告: {report_file}, {report_json_file}"
        )
    else:
        report_data = run_monkey_test(config, output_dir, report_generator, args.format)
        report_file, report_json_file = _write_reports(
            config, output_dir, report_data, report_generator, args.format
        )
        if report_data.get("gate_status", {}).get("level") == "fail" or not report_data.get(
            "gate_status", {}
        ).get("passed", True):
            # monkey：崩溃等硬失败仍拦截；兼容旧 passed=false
            if report_data.get("gate_status", {}).get("level") == "warn":
                exit_code = 0
            else:
                exit_code = 1
        logger.info(
            f"Monkey 测试完成 - 门禁: {(report_data.get('gate_status') or {}).get('level', '?')}, "
            f"崩溃: {report_data.get('crash_count', 0)}, "
            f"报告: {report_file}, {report_json_file}"
        )

    return exit_code


if __name__ == "__main__":
    sys.exit(main() or 0)
