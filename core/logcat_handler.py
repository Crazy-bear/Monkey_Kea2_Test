# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2025/1/10
"""

import subprocess
import threading
import time
from config.logging_config import logger


class LogcatHandler:
    def __init__(self, config):
        """
        初始化 LogcatHandler
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.process = None
        self.crash_callback = None
    
    def start_logcat(self, output_file, buffers=None):
        """
        启动 Logcat 日志捕获。
        
        Args:
            output_file: 日志输出文件路径
            buffers: 要捕获的日志缓冲区列表，默认包括 main、events、crash
            
        Returns:
            subprocess.Popen: 日志捕获进程
        """
        if buffers is None:
            buffers = ["main", "events", "crash"]
        
        # 构建命令
        cmd = ["adb", "-s", self.config.DEVICE_ID, "logcat"]
        for buffer in buffers:
            cmd.extend(["-b", buffer])
        
        try:
            # 打开文件用于写入
            with open(output_file, "w", encoding="utf-8") as f:
                self.process = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT)
            logger.info(f"Logcat 日志捕获已启动，输出到: {output_file}")
            return self.process
        except Exception as e:
            logger.error(f"启动 Logcat 失败: {e}")
            return None

    def stop_logcat(self):
        """
        停止 Logcat 捕获。
        """
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
                logger.info("Logcat 日志捕获已停止")
            except Exception as e:
                logger.error(f"停止 Logcat 失败: {e}")
            finally:
                self.process = None

    def detect_crashes(self, log_file):
        """
        检测日志中的崩溃信息。
        
        Args:
            log_file: 日志文件路径
            
        Returns:
            list: 崩溃信息列表
        """
        crashes = []
        try:
            with open(log_file, "r", encoding="utf-8", errors="ignore") as file:
                # 增加更多崩溃类型检测
                crash_keywords = [
                    "FATAL EXCEPTION",
                    "ANR",
                    "NullPointerException",
                    "OutOfMemoryError",
                    "IllegalStateException",
                    "RuntimeException",
                    "ClassCastException",
                    "IndexOutOfBoundsException",
                    "IOException",
                    "Error",
                    "Crash"
                ]
                
                # 读取并分析日志
                for line in file:
                    if any(keyword in line for keyword in crash_keywords):
                        crashes.append(line.strip())
        except FileNotFoundError:
            logger.error(f"错误: 日志文件 {log_file} 未找到。")
        except IOError as e:
            logger.error(f"IO 错误: {e}")
        except Exception as e:
            logger.error(f"检测崩溃时发生错误: {e}")
        
        return crashes
    
    def start_real_time_crash_detection(self, log_file, callback=None):
        """
        启动实时崩溃检测
        
        Args:
            log_file: 日志文件路径
            callback: 崩溃检测回调函数
        """
        self.crash_callback = callback
        
        def monitor_logs():
            """监控日志文件的变化"""
            last_position = 0
            crash_keywords = [
                "FATAL EXCEPTION",
                "ANR",
                "NullPointerException",
                "OutOfMemoryError",
                "IllegalStateException",
                "RuntimeException"
            ]
            
            while self.process and self.process.poll() is None:
                try:
                    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                        f.seek(last_position)
                        new_lines = f.readlines()
                        last_position = f.tell()
                        
                        for line in new_lines:
                            if any(keyword in line for keyword in crash_keywords):
                                if self.crash_callback:
                                    self.crash_callback(line.strip())
                                logger.warning(f"实时检测到崩溃: {line.strip()}")
                except Exception as e:
                    logger.error(f"监控日志时发生错误: {e}")
                
                time.sleep(1)  # 每秒检查一次
        
        # 启动监控线程
        monitor_thread = threading.Thread(target=monitor_logs)
        monitor_thread.daemon = True
        monitor_thread.start()
        logger.info("实时崩溃检测已启动")


