# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2025/1/10
"""

import subprocess
from config.config import Config


class LogcatHandler:
    def start_logcat(self, output_file):
        """
        启动 Logcat 日志捕获。
        """
        process = subprocess.Popen(["adb", "-s", Config.DEVICE_ID, "logcat"], stdout=open(output_file, "w"))
        return process

    def stop_logcat(self, process):
        """
        停止 Logcat 捕获。
        """
        process.terminate()

    def detect_crashes(self, log_file):
        """
        检测日志中的崩溃信息。
        """
        try:
            with open(log_file, "r", encoding="utf-8", errors="ignore") as file:
                crashes = []
                keywords = ["FATAL EXCEPTION", "ANR", "NullPointerException"]
                for line in file:
                    if any(keyword in line for keyword in keywords):
                        crashes.append(line)
        except FileNotFoundError:
            print(f"错误: 日志文件 {log_file} 未找到。")
            return []
        except IOError as e:
            print(f"IO 错误: {e}")
            return []
        return crashes

