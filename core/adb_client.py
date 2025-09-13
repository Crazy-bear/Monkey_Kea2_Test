# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2025/1/10
"""

import subprocess
from config.config import Config
from core.utils import create_output_dirs


class ADBClient:
    @staticmethod
    def run_command(cmd, monkey_log_file):
        """
        执行 ADB 命令并返回结果。
        """
        with open(monkey_log_file, "w") as log_file:
            result = subprocess.run(cmd, shell=True, stdout=log_file, stderr=subprocess.STDOUT, text=True)
        return monkey_log_file, result.stderr

    def get_connected_devices(self):
        """
        获取已连接的设备列表。
        """
        cmd = ["adb", "devices"]
        stdout, _ = self.run_command(cmd)
        devices = [line.split()[0] for line in stdout.splitlines() if "device" in line and not line.startswith("List")]
        return devices

    def launch_app(self, package_name):
        """
        启动应用。
        """
        cmd = ["adb", "-s", Config.DEVICE_ID, "shell", "monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1"]
        return self.run_command(cmd)
