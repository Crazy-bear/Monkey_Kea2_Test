# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2026/3/11

性能监控主模块
功能：
1. 管理CPU、内存、FPS监控
2. 支持多设备
3. 线程后台监控
4. 输出CSV和JSON格式数据
5. 生成趋势数据
"""
import threading
import time
import os
import csv
import json
from datetime import datetime
from config.logging_config import logger
from config.config import Config
from performance.cpu import CPUMonitor
from performance.memory import MemoryMonitor
from performance.fps import FPSMonitor


class PerformanceMonitor:
    def __init__(self, device_id, package_name, output_dir, interval=1):
        """
        初始化性能监控器
        
        Args:
            device_id: 设备ID
            package_name: 应用包名
            output_dir: 输出目录
            interval: 监控间隔（秒）
        """
        self.device_id = device_id
        self.package_name = package_name
        self.output_dir = output_dir
        self.interval = interval
        self.is_running = False
        self.thread = None
        self.data = []
        self.leak_analysis = {'suspected': False, 'total_growth_mb': 0, 'leak_segments': 0, 'details': []}

        # 性能阈值
        self.cpu_threshold = Config.PERF_CPU_THRESHOLD
        self.mem_threshold = Config.PERF_MEM_THRESHOLD
        self.fps_threshold = Config.PERF_FPS_THRESHOLD
        self.mem_leak_window = Config.PERF_MEM_LEAK_WINDOW
        self.mem_leak_growth = Config.PERF_MEM_LEAK_GROWTH
        
        # 初始化各个监控器
        self.cpu_monitor = CPUMonitor(device_id, package_name)
        self.memory_monitor = MemoryMonitor(device_id, package_name)
        self.fps_monitor = FPSMonitor(device_id, package_name)
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
    
    def start(self):
        """
        启动性能监控
        """
        if self.is_running:
            logger.warning("性能监控已经在运行中")
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._monitor_loop)
        self.thread.daemon = True
        self.thread.start()
        logger.info(f"性能监控已启动 - 设备: {self.device_id}, 应用: {self.package_name}")
    
    def stop(self):
        """
        停止性能监控
        """
        if not self.is_running:
            logger.warning("性能监控未运行")
            return
        
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        
        # 内存泄漏分析
        self.leak_analysis = self._analyze_memory_leak()
        if self.leak_analysis['suspected']:
            logger.warning(
                f"⚠️  疑似内存泄漏：监控期间内存增长 {self.leak_analysis['total_growth_mb']:.1f} MB，"
                f"检测到 {self.leak_analysis['leak_segments']} 段持续增长"
            )

        # 保存数据
        self._save_data()
        logger.info(f"性能监控已停止 - 共采集 {len(self.data)} 条数据")
    
    def _monitor_loop(self):
        """
        监控循环
        """
        while self.is_running:
            try:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # 采集各项指标
                cpu = self.cpu_monitor.get_cpu_usage()
                mem = self.memory_monitor.get_memory_usage()
                fps = self.fps_monitor.get_fps()
                
                # 保存数据
                self.data.append({
                    'timestamp': timestamp,
                    'cpu': cpu,
                    'mem': mem,
                    'fps': fps,
                    'cpu_exceed': cpu > self.cpu_threshold,
                    'mem_exceed': mem > self.mem_threshold,
                    'fps_low': fps > 0 and fps < self.fps_threshold,
                })
                
                time.sleep(self.interval)
            except Exception as e:
                logger.error(f"监控过程中发生错误: {e}")
                time.sleep(self.interval)
    
    def _analyze_memory_leak(self):
        """
        基于滑动窗口检测内存泄漏：
        - 在 mem_leak_window 大小的窗口内，若内存净增长超过 mem_leak_growth MB，则记为一段泄漏
        - 统计泄漏段数量和总增长量
        """
        result = {'suspected': False, 'total_growth_mb': 0.0, 'leak_segments': 0, 'details': []}
        if len(self.data) < self.mem_leak_window:
            return result

        mem_vals = [d['mem'] for d in self.data]
        w = self.mem_leak_window
        segments = 0
        i = 0
        while i + w <= len(mem_vals):
            window = mem_vals[i:i + w]
            growth = window[-1] - window[0]
            if growth >= self.mem_leak_growth:
                segments += 1
                result['details'].append({
                    'start_idx': i,
                    'end_idx': i + w - 1,
                    'start_time': self.data[i]['timestamp'],
                    'end_time': self.data[i + w - 1]['timestamp'],
                    'growth_mb': round(growth, 2),
                })
                i += w  # 跳过已计入的窗口，避免重叠计数
            else:
                i += 1

        if segments > 0:
            total_growth = mem_vals[-1] - mem_vals[0]
            result['suspected'] = True
            result['leak_segments'] = segments
            result['total_growth_mb'] = round(total_growth, 2)
        return result

    def _save_data(self):
        """
        保存数据到CSV和JSON文件
        """
        if not self.data:
            logger.warning("无数据可保存")
            return
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_file = os.path.join(self.output_dir, f'performance_{timestamp}.csv')
        json_file = os.path.join(self.output_dir, f'performance_{timestamp}.json')
        
        # 保存为CSV
        try:
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['timestamp', 'cpu', 'mem', 'fps']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.data)
            logger.info(f"性能数据已保存到CSV: {csv_file}")
        except Exception as e:
            logger.error(f"保存CSV文件失败: {e}")
        
        # 保存为JSON
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            logger.info(f"性能数据已保存到JSON: {json_file}")
        except Exception as e:
            logger.error(f"保存JSON文件失败: {e}")
    
    def get_data(self):
        """
        获取监控数据
        
        Returns:
            list: 监控数据列表
        """
        return self.data

    def get_thresholds(self):
        """返回当前阈值配置"""
        return {
            'cpu': self.cpu_threshold,
            'mem': self.mem_threshold,
            'fps': self.fps_threshold,
        }

    def get_leak_analysis(self):
        """返回内存泄漏分析结果"""
        return self.leak_analysis
