# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2025/1/10

ADB 命令封装，使用 shell=False 保证跨平台与安全，设备 ID 由调用方传入。
"""

import subprocess
from config.logging_config import logger


class ADBClient:
    def __init__(self, device_id=None):
        """
        Args:
            device_id: 当前使用的设备 ID，所有带 -s 的 ADB 命令均使用此值。
        """
        self.device_id = device_id

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
            try:
                result = subprocess.run(
                    cmd, shell=False,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    text=True, timeout=300
                )
                return (result.stdout or ""), (result.stderr or "")
            except subprocess.TimeoutExpired:
                logger.error("ADB 命令执行超时")
                return "", "Timeout"
            except Exception as e:
                logger.error(f"执行 ADB 命令失败: {e}")
                return "", str(e)

        if monkey_log_file:
            try:
                with open(monkey_log_file, "w", encoding="utf-8") as log_file:
                    result = subprocess.run(
                        cmd, shell=False,
                        stdout=log_file, stderr=subprocess.STDOUT,
                        text=True, timeout=300
                    )
                return monkey_log_file, (result.stderr or "")
            except subprocess.TimeoutExpired:
                logger.error("ADB 命令执行超时")
                return monkey_log_file, "Timeout"
            except Exception as e:
                logger.error(f"执行 ADB 命令失败: {e}")
                return monkey_log_file, str(e)

        try:
            result = subprocess.run(
                cmd, shell=False,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, timeout=300
            )
            return (result.stdout or ""), (result.stderr or "")
        except subprocess.TimeoutExpired:
            logger.error("ADB 命令执行超时")
            return "", "Timeout"
        except Exception as e:
            logger.error(f"执行 ADB 命令失败: {e}")
            return "", str(e)

    def get_connected_devices(self):
        """
        获取已连接的设备列表。
        """
        cmd = ["adb", "devices"]
        stdout, _ = self.run_command(cmd, capture_output=True)
        if not stdout:
            return []
        devices = []
        for line in stdout.splitlines():
            if "device" in line and not line.startswith("List"):
                parts = line.split()
                if parts:
                    devices.append(parts[0])
        return devices

    def launch_app(self, package_name, log_file=None):
        """
        启动应用。使用初始化时传入的 device_id。
        """
        if not self.device_id:
            logger.error("ADBClient 未设置 device_id，无法执行 launch_app")
            return "", "device_id not set"
        cmd = [
            "adb", "-s", self.device_id, "shell", "monkey",
            "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1"
        ]
        return self.run_command(cmd, log_file)
