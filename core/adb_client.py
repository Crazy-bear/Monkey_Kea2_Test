# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2025/1/10

ADB 命令封装，使用 shell=False 保证跨平台与安全，设备 ID 由调用方传入。
"""

import subprocess
import time
from settings.logging_config import logger

# 默认 ADB 命令超时（秒）
_DEFAULT_TIMEOUT = 30
_DEFAULT_RETRY_COUNT = 3


class ADBClient:
    def __init__(self, device_id=None, retry_count=_DEFAULT_RETRY_COUNT):
        self.device_id = device_id
        self.retry_count = retry_count

    def run_command(
        self,
        cmd,
        monkey_log_file=None,
        capture_output=False,
        timeout=_DEFAULT_TIMEOUT,
        retry_count=None,
    ):
        """
        执行 ADB 命令并返回结果。使用 shell=False，cmd 必须为列表。

        Args:
            cmd: 命令列表，如 ["adb", "-s", "xxx", "shell", "ls"]
            monkey_log_file: 日志文件路径，若提供则 stdout 写入该文件
            capture_output: 是否捕获输出并返回
            timeout: 命令超时秒数，默认 30s；Monkey 长跑命令请传 None
            retry_count: 失败重试次数，默认使用实例配置

        Returns:
            capture_output 为 True 时返回 (stdout, stderr)；
            否则若提供 monkey_log_file 返回 (monkey_log_file, stderr)，否则返回 (stdout, stderr)
        """
        retries = self.retry_count if retry_count is None else retry_count
        last_error = ""
        for attempt in range(retries + 1):
            try:
                if capture_output:
                    result = subprocess.run(
                        cmd, shell=False,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        text=True, timeout=timeout,
                    )
                    if result.returncode == 0 or attempt == retries:
                        return result.stdout, result.stderr
                    last_error = result.stderr or f"exit code {result.returncode}"
                elif monkey_log_file:
                    with open(monkey_log_file, "w", encoding="utf-8") as log_file:
                        result = subprocess.run(
                            cmd, shell=False,
                            stdout=log_file, stderr=subprocess.STDOUT,
                            text=True, timeout=timeout,
                        )
                    if result.returncode == 0 or attempt == retries:
                        return monkey_log_file, result.stderr
                    last_error = result.stderr or f"exit code {result.returncode}"
                else:
                    result = subprocess.run(
                        cmd, shell=False,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        text=True, timeout=timeout,
                    )
                    if result.returncode == 0 or attempt == retries:
                        return result.stdout, result.stderr
                    last_error = result.stderr or f"exit code {result.returncode}"
            except subprocess.TimeoutExpired:
                last_error = f"TimeoutExpired after {timeout}s"
                logger.error(f"ADB 命令超时（{timeout}s）: {' '.join(cmd)}")
            except Exception as e:
                last_error = str(e)
                logger.error(f"ADB 命令执行失败: {e} | cmd={' '.join(cmd)}")

            if attempt < retries:
                backoff = 0.5 * (2 ** attempt)
                logger.warning(
                    f"ADB 命令失败，{backoff:.1f}s 后重试 ({attempt + 1}/{retries}): {' '.join(cmd)}"
                )
                time.sleep(backoff)

        logger.error(f"ADB 命令最终失败: {last_error} | cmd={' '.join(cmd)}")
        return "", last_error

    def get_device_state(self):
        """获取设备连接状态，返回 device/offline/unknown 等。"""
        if not self.device_id:
            return "unknown"
        stdout, _ = self.run_command(
            ["adb", "-s", self.device_id, "get-state"],
            capture_output=True,
            timeout=10,
            retry_count=1,
        )
        state = stdout.strip().lower()
        return state if state else "unknown"

    def is_device_connected(self):
        """检查设备是否处于 device 状态。"""
        return self.get_device_state() == "device"

    def reconnect_device(self):
        """尝试重新连接 TCP 设备。"""
        if not self.device_id or ":" not in self.device_id:
            return False
        stdout, _ = self.run_command(
            ["adb", "connect", self.device_id],
            capture_output=True,
            timeout=15,
            retry_count=1,
        )
        connected = "connected" in stdout.lower() or "already connected" in stdout.lower()
        if connected:
            logger.info(f"设备重连成功: {self.device_id}")
        else:
            logger.warning(f"设备重连失败: {self.device_id} | {stdout}")
        return connected and self.is_device_connected()

    def get_connected_devices(self):
        """
        获取已连接的设备列表。
        """
        stdout, _ = self.run_command(["adb", "devices"], capture_output=True, timeout=10)
        return [
            line.split()[0]
            for line in stdout.splitlines()
            if "\tdevice" in line
        ]

    def launch_app(self, package_name, log_file=None):
        """
        启动应用。使用初始化时传入的 device_id。
        """
        if not self.device_id:
            return "", "device_id not set"
        cmd = [
            "adb", "-s", self.device_id, "shell", "monkey",
            "-p", package_name,
            "-c", "android.intent.category.LAUNCHER", "1",
        ]
        return self.run_command(cmd, log_file, timeout=15)

    def shell(self, *args, timeout=_DEFAULT_TIMEOUT, retry_count=None):
        """
        便捷方法：执行 adb shell 子命令并返回 stdout。

        Args:
            *args: shell 子命令参数，如 "getprop", "ro.build.display.id"
        """
        if not self.device_id:
            return ""
        cmd = ["adb", "-s", self.device_id, "shell", *args]
        stdout, _ = self.run_command(
            cmd, capture_output=True, timeout=timeout, retry_count=retry_count
        )
        return stdout
