# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2025/1/10

Monkey 自动化测试主入口，支持完整测试、仅校验配置、仅生成报告（便于 Jenkins/CI）。
"""

import os
import sys
import argparse
import time
import glob
import json
from config.config import Config
from core.adb_client import ADBClient
from core.monkey_runner import MonkeyRunner
from core.logcat_handler import LogcatHandler
from core.report_generator import ReportGenerator
from core.utils import get_timestamp, create_output_dirs
from config.logging_config import logger
from performance.monitor import PerformanceMonitor


def _duration_str(total_seconds):
    total_seconds = int(total_seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    if hours > 0:
        return f"{hours}小时{minutes}分{seconds}秒"
    if minutes > 0:
        return f"{minutes}分{seconds}秒"
    return f"{seconds}秒"


def run_validate_only(config):
    """仅校验配置并退出，不连接设备。适用于 CI 检查或 Jenkins 参数校验。"""
    ok, errors = config.validate()
    if ok:
        logger.info("配置校验通过")
        return 0
    for e in errors:
        logger.error(e)
    return 1


def run_report_only(report_from_dir, output_file, format_type="html"):
    """
    从已有输出目录生成报告（不执行 Monkey），便于 Jenkins 二次报告或补生成。
    report_from_dir 应包含 logcat.log、monkey.log，以及可选的 performance/performance_*.json。
    """
    logcat_file = os.path.join(report_from_dir, "logcat.log")
    if not os.path.isfile(logcat_file):
        logger.error(f"未找到 {logcat_file}")
        return 1
    logcat_handler = LogcatHandler(Config())
    # 临时设置设备信息为未知（无设备连接）
    crashes = logcat_handler.detect_crashes(logcat_file)
    log_analysis = logcat_handler.analyze_logs(logcat_file)

    performance_data = None
    performance_dir = os.path.join(report_from_dir, "performance")
    if os.path.isdir(performance_dir):
        performance_files = glob.glob(os.path.join(performance_dir, "performance_*.json"))
        if performance_files:
            latest = max(performance_files, key=os.path.getmtime)
            try:
                with open(latest, "r", encoding="utf-8") as f:
                    performance_data = json.load(f)
            except Exception as e:
                logger.error(f"读取性能数据失败: {e}")

    report_data = {
        "device_id": "N/A (report-only)",
        "package_name": "N/A",
        "device_version_name": "N/A",
        "start_time": "N/A",
        "end_time": "N/A",
        "duration": "N/A",
        "seed_value": 0,
        "execution_count": 0,
        "crash_count": len(crashes),
        "crashes": crashes,
        "log_analysis": log_analysis,
        "performance_data": performance_data,
        "details": "仅根据已有日志生成报告。",
    }
    if not output_file:
        output_file = os.path.join(report_from_dir, f"report.{format_type}")
    ReportGenerator().generate_report(report_data, output_file, format_type)
    logger.info(f"报告已生成: {output_file}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Monkey 自动化测试工具")
    parser.add_argument("--device", type=str, help="设备 ID")
    parser.add_argument("--package", type=str, help="应用包名")
    parser.add_argument("--events", type=int, help="事件数量")
    parser.add_argument("--output", type=str, default="outputs", help="输出目录")
    parser.add_argument("--format", type=str, default="html", choices=["html", "json"], help="报告格式")
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="仅校验配置后退出（不连接设备，适用于 Jenkins）",
    )
    parser.add_argument(
        "--report-only",
        type=str,
        metavar="DIR",
        help="从指定目录根据已有日志生成报告，不执行 Monkey（适用于 Jenkins 补报告）",
    )
    parser.add_argument(
        "--report-output",
        type=str,
        help="与 --report-only 配合，指定报告输出路径",
    )
    args = parser.parse_args()

    config = Config()
    if args.device:
        config.DEVICE_ID = args.device
    if args.package:
        config.PACKAGE_NAME = args.package
    if args.events:
        config.EVENT_COUNT = args.events

    if args.validate_only:
        return run_validate_only(config)

    if args.report_only:
        return run_report_only(
            args.report_only,
            args.report_output,
            args.format,
        )

    ok, errors = config.validate()
    if not ok:
        for e in errors:
            logger.error(e)
        return 1

    timestamp = get_timestamp()
    output_dir = os.path.join(args.output, timestamp)
    create_output_dirs(output_dir)

    adb_client = ADBClient(device_id=config.DEVICE_ID)
    monkey_runner = MonkeyRunner(adb_client, config)
    logcat_handler = LogcatHandler(config)
    report_generator = ReportGenerator()

    monkey_log_file = os.path.join(output_dir, "monkey.log")
    logcat_file = os.path.join(output_dir, "logcat.log")
    report_file = os.path.join(output_dir, f"report.{args.format}")
    performance_dir = os.path.join(output_dir, "performance")

    logcat_process = logcat_handler.start_logcat(logcat_file)
    performance_monitor = PerformanceMonitor(config.DEVICE_ID, config.PACKAGE_NAME, performance_dir)
    performance_monitor.start()

    start_time = time.strftime("%Y-%m-%d %H:%M:%S")
    start_timestamp = time.time()
    logger.info(f"[{start_time}] 开始 Monkey 测试 - 设备: {config.DEVICE_ID}, 应用: {config.PACKAGE_NAME}")
    logger.info(f"[{start_time}] 事件数量: {config.EVENT_COUNT}, 随机种子: {config.SEED}")

    monkey_process_completed = False
    try:
        monkey_runner.run_monkey(monkey_log_file)
        monkey_process_completed = True
    except Exception as e:
        logger.error(f"执行 Monkey 测试时发生错误: {e}")
    finally:
        performance_monitor.stop()
        if logcat_process and monkey_process_completed:
            time.sleep(2)
            logcat_handler.stop_logcat()
            logger.info("Logcat 日志捕获已停止（Monkey 测试完成）")
        elif logcat_process:
            logger.warning("Monkey 测试异常，停止 Logcat 日志捕获")
            logcat_handler.stop_logcat()

    end_time = time.strftime("%Y-%m-%d %H:%M:%S")
    end_timestamp = time.time()
    duration = _duration_str(end_timestamp - start_timestamp)

    crashes = logcat_handler.detect_crashes(logcat_file)
    crash_count = len(crashes)
    logger.info("开始分析日志文件...")
    log_analysis = logcat_handler.analyze_logs(logcat_file)
    logger.debug("日志分析结果: %s", log_analysis)

    performance_data = None
    if os.path.isdir(performance_dir):
        performance_files = glob.glob(os.path.join(performance_dir, "performance_*.json"))
        if performance_files:
            latest_performance_file = max(performance_files, key=os.path.getmtime)
            try:
                with open(latest_performance_file, "r", encoding="utf-8") as f:
                    performance_data = json.load(f)
            except Exception as e:
                logger.error(f"读取性能数据失败: {e}")

    report_data = {
        "device_id": config.DEVICE_ID,
        "package_name": config.PACKAGE_NAME,
        "device_version_name": config.DeviceVersionName,
        "firmware_version": config.FirmwareVersion,
        "start_time": start_time,
        "end_time": end_time,
        "duration": duration,
        "seed_value": config.SEED,
        "execution_count": config.EVENT_COUNT,
        "crash_count": crash_count,
        "crashes": crashes,
        "log_analysis": log_analysis,
        "performance_data": performance_data,
        "performance_thresholds": performance_monitor.get_thresholds(),
        "memory_leak_analysis": performance_monitor.get_leak_analysis(),
        "details": f"Monkey 测试执行完成，共执行 {config.EVENT_COUNT} 个事件，检测到 {crash_count} 次崩溃。",
    }
    report_generator.generate_report(report_data, report_file, args.format)

    logger.info(f"[{end_time}] Monkey 测试完成 - 用时: {duration}, 崩溃次数: {crash_count}")
    logger.info(f"[{end_time}] 测试报告已生成: {report_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
