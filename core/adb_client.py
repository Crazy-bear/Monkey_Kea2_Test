# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2025/1/10
"""

import subprocess
from config.config import Config
<<<<<<< HEAD
from config.logging_config import logger
=======
>>>>>>> bc185e8 (Monkey稳定性测试)
from core.utils import create_output_dirs


class ADBClient:
<<<<<<< HEAD
    def run_command(self, cmd, monkey_log_file=None, capture_output=False):
        """
        执行 ADB 命令并返回结果。
        
        Args:
            cmd: 要执行的命令列表
            monkey_log_file: 日志文件路径，如果为None则不保存日志
            capture_output: 是否捕获输出并返回
            
        Returns:
            如果capture_output为True，返回(output, error)
            否则返回(monkey_log_file, error)
        """
        if capture_output:
            result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return result.stdout, result.stderr
        else:
            if monkey_log_file:
                with open(monkey_log_file, "w") as log_file:
                    result = subprocess.run(cmd, shell=True, stdout=log_file, stderr=subprocess.STDOUT, text=True)
                return monkey_log_file, result.stderr
            else:
                result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                return result.stdout, result.stderr
=======
    @staticmethod
    def run_command(cmd, monkey_log_file):
        """
        执行 ADB 命令并返回结果。
        """
        with open(monkey_log_file, "w") as log_file:
            result = subprocess.run(cmd, shell=True, stdout=log_file, stderr=subprocess.STDOUT, text=True)
        return monkey_log_file, result.stderr
>>>>>>> bc185e8 (Monkey稳定性测试)

    def get_connected_devices(self):
        """
        获取已连接的设备列表。
        """
        cmd = ["adb", "devices"]
<<<<<<< HEAD
        stdout, _ = self.run_command(cmd, capture_output=True)
        devices = [line.split()[0] for line in stdout.splitlines() if "device" in line and not line.startswith("List")]
        return devices

    def launch_app(self, package_name, log_file=None):
=======
        stdout, _ = self.run_command(cmd)
        devices = [line.split()[0] for line in stdout.splitlines() if "device" in line and not line.startswith("List")]
        return devices

    def launch_app(self, package_name):
>>>>>>> bc185e8 (Monkey稳定性测试)
        """
        启动应用。
        """
        cmd = ["adb", "-s", Config.DEVICE_ID, "shell", "monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1"]
<<<<<<< HEAD
        return self.run_command(cmd, log_file)

=======
        return self.run_command(cmd)
>>>>>>> bc185e8 (Monkey稳定性测试)
