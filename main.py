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
from performance.monitor import PerformanceMonitor


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
    performance_dir = os.path.join(output_dir, 'performance')
    
    # 启动Logcat日志捕获
    logcat_process = logcat_handler.start_logcat(logcat_file)
    
    # 初始化性能监控
    performance_monitor = PerformanceMonitor(config.DEVICE_ID, config.PACKAGE_NAME, performance_dir)
    # 启动性能监控
    performance_monitor.start()
    
    # 启动实时崩溃检测
    # logcat_handler.start_real_time_crash_detection(logcat_file)
    
    # 记录测试开始时间
    start_time = time.strftime('%Y-%m-%d %H:%M:%S')
    start_timestamp = time.time()
    
    logger.info(f"[{start_time}] 开始Monkey测试 - 设备: {config.DEVICE_ID}, 应用: {config.PACKAGE_NAME}")
    logger.info(f"[{start_time}] 事件数量: {config.EVENT_COUNT}, 随机种子: {config.SEED}")
    
    # 执行Monkey测试
    monkey_process_completed = False
    try:
        monkey_runner.run_monkey(monkey_log_file)
        monkey_process_completed = True
    except Exception as e:
        logger.error(f"执行Monkey测试时发生错误: {e}")
    finally:
            # 停止性能监控（无论Logcat是否启动成功）
            performance_monitor.stop()
            
            # 确保Monkey测试真正完成后再停止Logcat日志捕获
            if logcat_process and monkey_process_completed:
                # 等待一小段时间，确保所有日志都被捕获
                time.sleep(2)
                logcat_handler.stop_logcat()
                logger.info("Logcat日志捕获已停止（Monkey测试完成）")
            elif logcat_process:
                logger.warning("Monkey测试异常，停止Logcat日志捕获")
                logcat_handler.stop_logcat()
    
    # 记录测试结束时间
    end_time = time.strftime('%Y-%m-%d %H:%M:%S')
    end_timestamp = time.time()
    
    # 将秒数转换为时分秒格式
    total_seconds = int(end_timestamp - start_timestamp)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    if hours > 0:
        duration = f"{hours}小时{minutes}分{seconds}秒"
    elif minutes > 0:
        duration = f"{minutes}分{seconds}秒"
    else:
        duration = f"{seconds}秒"
    
    # 检测崩溃
    crashes = logcat_handler.detect_crashes(logcat_file)
    crash_count = len(crashes)
    
    # 分析日志
    print("开始分析日志文件...")
    log_analysis = logcat_handler.analyze_logs(logcat_file)
    print(f"日志分析结果: {log_analysis}")
    
    # 准备性能数据
    performance_data = None
    performance_dir = os.path.join(output_dir, 'performance')
    if os.path.exists(performance_dir):
        # 查找最新的性能数据文件
        import glob
        performance_files = glob.glob(os.path.join(performance_dir, 'performance_*.json'))
        if performance_files:
            latest_performance_file = max(performance_files, key=os.path.getmtime)
            try:
                import json
                with open(latest_performance_file, 'r', encoding='utf-8') as f:
                    performance_data = json.load(f)
            except Exception as e:
                logger.error(f"读取性能数据失败: {e}")
    
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
        'log_analysis': log_analysis,
        'performance_data': performance_data,
        'details': f"Monkey测试执行完成，共执行{config.EVENT_COUNT}个事件，检测到{crash_count}次崩溃。"
    }
    
    # 打印报告数据
    print(f"报告数据包含log_analysis: {'log_analysis' in report_data}")
    print(f"log_analysis类型: {type(report_data.get('log_analysis'))}")
    
    # 生成报告
    report_generator.generate_report(report_data, report_file, args.format)
    
    logger.info(f"[{end_time}] Monkey测试完成 - 用时: {duration}, 崩溃次数: {crash_count}")
    logger.info(f"[{end_time}] 测试报告已生成: {report_file}")


if __name__ == '__main__':
    main()
