# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2025/1/10

ADB 命令封装，使用 shell=False 保证跨平台与安全，设备 ID 由调用方传入。
"""

import subprocess
from config.config import Config
from config.logging_config import logger
from core.utils import create_output_dirs


class ADBClient:
    def __init__(self, device_id=None):
        self.device_id = device_id or Config.DEVICE_ID

    def run_command(self, cmd, monkey_log_file=None, capture_output=False):
        """
        执行 ADB 命令并返回结果。使用 shell=False，cmd 必须为列表。

        Args:
            cmd: 命令列表，如 ["adb", "-s", "xxx", "shell", "ls"]
            monkey_log_file: 日志文件路径，若提供则 stdout 写入该文件
            capture_output: 是否捕获输出并返回

        Returns:
            capture_output 为 True 时返回 (stdout, stderr)；
            否则若提供 monkey_log_file 返回 (monkey_log_file, stderr)，否则返回 (stdout, stderr)
        """
        if capture_output:
            result = subprocess.run(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return result.stdout, result.stderr
        else:
            if monkey_log_file:
                with open(monkey_log_file, "w") as log_file:
                    result = subprocess.run(cmd, shell=False, stdout=log_file, stderr=subprocess.STDOUT, text=True)
                return monkey_log_file, result.stderr
            else:
                result = subprocess.run(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                return result.stdout, result.stderr

    def get_connected_devices(self):
        """
        获取已连接的设备列表。
        """
        cmd = ["adb", "devices"]
        stdout, _ = self.run_command(cmd, capture_output=True)
        devices = [line.split()[0] for line in stdout.splitlines() if "device" in line and not line.startswith("List")]
        return devices

    def launch_app(self, package_name, log_file=None):
        """
        启动应用。使用初始化时传入的 device_id。
        """
        cmd = ["adb", "-s", self.device_id, "shell", "monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1"]
        return self.run_command(cmd, log_file)
