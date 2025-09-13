# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2025/1/10
"""

import os
import datetime
from core.utils import create_output_dirs, get_timestamp
from core.adb_client import ADBClient
from core.monkey_runner import MonkeyRunner
from core.logcat_handler import LogcatHandler
from core.report_generator import ReportGenerator
from config.config import Config


def test_monkey():
    print(f"...开始运行monkey测试...")
    # 记录测试开始时间
    start_time = datetime.datetime.now()
    print(f"测试开始时间: {start_time}")

    # 确保输出目录存在
    base_dir = r"G:\Test\Monkey_test"  # 定义基础目录
    create_output_dirs(base_dir)

    # 初始化模块
    adb_client = ADBClient()
    monkey_runner = MonkeyRunner(adb_client, Config)
    logcat_handler = LogcatHandler()
    report_generator = ReportGenerator()

    # 动态生成日志文件名
    logcat_file = f"{base_dir}/outputs/logs/logcat_{get_timestamp()}.txt"
    report_file = f"{base_dir}/outputs/reports/test_report_{get_timestamp()}.html"
    monkey_log_file = f"{base_dir}/outputs/monkey_logs/Monkey_report_{get_timestamp()}.txt"

    # 开始捕获日志
    try:
        logcat_process = logcat_handler.start_logcat(logcat_file)
    except Exception as e:
        print(f"启动日志捕获失败: {e}")
        return  # 直接返回，避免后续代码执行

    # 运行monkey测试
    try:
        monkey_runner.run_monkey(monkey_log_file)
    finally:
        logcat_handler.stop_logcat(logcat_process)

    # 崩溃检测异常处理
    if os.path.exists(logcat_file):
        crashes = logcat_handler.detect_crashes(logcat_file)    # 检查崩溃
    else:
        print(f"日志文件不存在: {logcat_file}")
        crashes = []

    # 记录测试结束时间
    end_time = datetime.datetime.now()
    print(f"测试结束时间: {end_time}")

    # 计算测试时长
    duration = end_time - start_time
    print(f"测试时长: {duration}")

    # 生成报告
    data = {
        "device_info": Config.DEVICE_ID,
        "package_name": Config.PACKAGE_NAME,
        "device_version_name": Config.DeviceVersionName,
        "crash_count": len(crashes),
        "details": "\n".join(crashes),
        # "test_time": get_timestamp(),
        "seed_value": Config.SEED,
        "execution_count": Config.EVENT_COUNT,
        "start_time": start_time,
        "end_time": end_time,
        "duration": duration,
    }
    report_generator.generate_html_report(data, report_file)
    print(f"Monkey测试报告完成: {report_file}")


if __name__ == "__main__":

    # 运行测试，异常处理，捕获异常

    try:
        test_monkey()
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
