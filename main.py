# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2025/1/10

Monkey自动化测试主入口文件
"""

import os
import argparse
import time
from config.config import Config
from core.adb_client import ADBClient
from core.monkey_runner import MonkeyRunner
from core.logcat_handler import LogcatHandler
from core.report_generator import ReportGenerator
from core.utils import get_timestamp, create_output_dirs
from config.logging_config import logger


def main():
    """
    主函数
    """
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Monkey自动化测试工具')
    parser.add_argument('--device', type=str, help='设备ID')
    parser.add_argument('--package', type=str, help='应用包名')
    parser.add_argument('--events', type=int, help='事件数量')
    parser.add_argument('--output', type=str, default='outputs', help='输出目录')
    parser.add_argument('--format', type=str, default='html', choices=['html', 'json'], help='报告格式')
    args = parser.parse_args()
    
    # 初始化配置
    config = Config()
    
    # 覆盖配置（如果命令行参数提供）
    if args.device:
        config.DEVICE_ID = args.device
    if args.package:
        config.PACKAGE_NAME = args.package
    if args.events:
        config.EVENT_COUNT = args.events
    
    # 创建输出目录
    timestamp = get_timestamp()
    output_dir = os.path.join(args.output, timestamp)
    create_output_dirs(output_dir)
    
    # 初始化各个模块
    adb_client = ADBClient()
    monkey_runner = MonkeyRunner(adb_client, config)
    logcat_handler = LogcatHandler(config)
    report_generator = ReportGenerator()
    
    # 准备文件路径
    monkey_log_file = os.path.join(output_dir, 'monkey.log')
    logcat_file = os.path.join(output_dir, 'logcat.log')
    report_file = os.path.join(output_dir, f'report.{args.format}')
    
    # 启动Logcat日志捕获
    logcat_process = logcat_handler.start_logcat(logcat_file)
    
    # 启动实时崩溃检测
    logcat_handler.start_real_time_crash_detection(logcat_file)
    
    # 记录测试开始时间
    start_time = time.strftime('%Y-%m-%d %H:%M:%S')
    start_timestamp = time.time()
    
    logger.info(f"开始Monkey测试 - 设备: {config.DEVICE_ID}, 应用: {config.PACKAGE_NAME}")
    logger.info(f"事件数量: {config.EVENT_COUNT}, 随机种子: {config.SEED}")
    
    # 执行Monkey测试
    try:
        monkey_runner.run_monkey(monkey_log_file)
    except Exception as e:
        logger.error(f"执行Monkey测试时发生错误: {e}")
    finally:
        # 停止Logcat日志捕获
        if logcat_process:
            logcat_handler.stop_logcat()
    
    # 记录测试结束时间
    end_time = time.strftime('%Y-%m-%d %H:%M:%S')
    end_timestamp = time.time()
    duration = f"{int(end_timestamp - start_timestamp)}秒"
    
    # 检测崩溃
    crashes = logcat_handler.detect_crashes(logcat_file)
    crash_count = len(crashes)
    
    # 准备报告数据
    report_data = {
        'device_id': config.DEVICE_ID,
        'package_name': config.PACKAGE_NAME,
        'device_version_name': config.DeviceVersionName,
        'start_time': start_time,
        'end_time': end_time,
        'duration': duration,
        'seed_value': config.SEED,
        'execution_count': config.EVENT_COUNT,
        'crash_count': crash_count,
        'crashes': crashes,
        'details': f"Monkey测试执行完成，共执行{config.EVENT_COUNT}个事件，检测到{crash_count}次崩溃。"
    }
    
    # 生成报告
    report_generator.generate_report(report_data, report_file, args.format)
    
    logger.info(f"Monkey测试完成 - 用时: {duration}, 崩溃次数: {crash_count}")
    logger.info(f"测试报告已生成: {report_file}")


if __name__ == '__main__':
    main()
