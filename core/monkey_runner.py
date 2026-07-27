# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2025/1/10

MonkeyRunner：执行 adb monkey、可选 UI 坐标解析、设备探活与重连。
"""
import queue
import re
import subprocess
import threading
import time
import uiautomator2 as u2
import xml.etree.ElementTree as ET
from settings.logging_config import logger
from core.utils import LogRotator


class MonkeyRunner:
    def __init__(self, adb_client, config):
        self.adb_client = adb_client
        self.config = config
        self.d = u2.connect(config.DEVICE_ID)

    def _build_monkey_cmd(self):
        """根据 Config 构建 Monkey 命令。"""
        cfg = self.config
        return [
            "adb", "-s", cfg.DEVICE_ID, "shell", "monkey",
            "-p", cfg.PACKAGE_NAME,
            "-s", str(cfg.SEED),
            "--throttle", str(cfg.MONKEY_THROTTLE),
            "--pct-touch", str(cfg.MONKEY_TOUCH_PERCENT),
            "--pct-motion", str(cfg.MONKEY_MOTION_PERCENT),
            "--pct-syskeys", str(cfg.MONKEY_SYSKEYS_PERCENT),
            "--pct-nav", str(cfg.MONKEY_NAV_PERCENT),
            "--pct-majnav", str(cfg.MONKEY_MAJC_PERCENT),
            "--pct-flip", str(cfg.MONKEY_FLIP_PERCENT),
            "--ignore-crashes", "--ignore-timeouts", "--monitor-native-crashes",
            "-v", "-v", "-v",
            str(cfg.EVENT_COUNT),
        ]

    def _ensure_device_connected(self):
        """检查设备连接，必要时重连。"""
        if self.adb_client.is_device_connected():
            return True

        max_attempts = getattr(self.config, "MAX_RECONNECT_ATTEMPTS", 3)
        for attempt in range(1, max_attempts + 1):
            logger.warning(f"设备未连接，尝试重连 ({attempt}/{max_attempts})")
            if self.adb_client.reconnect_device():
                return True
            time.sleep(1.0 * attempt)
        return False

    def _start_device_watchdog(self, stop_event):
        """后台周期性检查设备连接。"""
        interval = getattr(self.config, "DEVICE_CHECK_INTERVAL", 30)

        def watch():
            while not stop_event.is_set():
                if not self.adb_client.is_device_connected():
                    logger.warning("设备连接丢失，尝试恢复...")
                    self._ensure_device_connected()
                stop_event.wait(interval)

        thread = threading.Thread(target=watch, daemon=True)
        thread.start()
        return thread

    def _read_stdout(self, proc, line_queue, stop_event):
        """在独立线程中读取 stdout，避免 readline 无限阻塞。"""
        try:
            for line in iter(proc.stdout.readline, ""):
                if stop_event.is_set():
                    break
                line_queue.put(line)
        except Exception as e:
            logger.debug(f"Monkey stdout 读取结束: {e}")
        finally:
            line_queue.put(None)

    def run_monkey(self, monkey_log_file, max_bytes=10 * 1024 * 1024, parse_ui_interval=None):
        """
        运行 Monkey 测试并实时解析日志，支持日志轮转与总超时。

        Args:
            monkey_log_file: 日志文件路径
            max_bytes: 日志文件最大大小
            parse_ui_interval: 每 N 个事件解析一次 UI（0 表示不解析）
        """
        if parse_ui_interval is None:
            parse_ui_interval = getattr(self.config, "PARSE_UI_INTERVAL", 0)

        if not self._ensure_device_connected():
            raise RuntimeError(f"设备 {self.config.DEVICE_ID} 未连接且重连失败")

        rotator = None
        proc = None
        stop_event = threading.Event()
        watchdog = None

        try:
            cmd = self._build_monkey_cmd()
            logger.info(f"MonkeyRunner: 执行命令: {' '.join(cmd)}")
            rotator = LogRotator(monkey_log_file, max_bytes)
            total_timeout = self.config.get_monkey_timeout_seconds()
            logger.info(f"Monkey 总超时: {total_timeout}s")

            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, shell=False,
            )
            watchdog = self._start_device_watchdog(stop_event)

            line_queue = queue.Queue()
            reader = threading.Thread(
                target=self._read_stdout, args=(proc, line_queue, stop_event), daemon=True
            )
            reader.start()

            event_count = 0
            start_time = time.time()
            timed_out = False

            while True:
                elapsed = time.time() - start_time
                if elapsed > total_timeout:
                    timed_out = True
                    logger.error(f"Monkey 测试总超时 ({total_timeout}s)")
                    rotator.write(f"\nMonkey 测试总超时 ({total_timeout}s)\n")
                    break

                try:
                    line = line_queue.get(timeout=1.0)
                except queue.Empty:
                    if proc.poll() is not None:
                        break
                    continue

                if line is None:
                    break

                line = line.strip()
                rotator.write(line + "\n")

                if parse_ui_interval > 0 and event_count % parse_ui_interval == 0:
                    self.parse_monkey_event(line, rotator)
                if "Sending" in line:
                    event_count += 1

            if timed_out:
                stop_event.set()
                proc.terminate()
                try:
                    proc.wait(timeout=10)
                except Exception:
                    proc.kill()
            else:
                try:
                    proc.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    logger.warning("Monkey 进程 wait 超时，强制终止")
                    proc.terminate()
                    proc.wait(timeout=10)

                if proc.returncode != 0:
                    logger.warning(f"Monkey 测试执行完成，退出码: {proc.returncode}")
                    rotator.write(f"\nMonkey 测试执行完成，退出码: {proc.returncode}\n")
                else:
                    logger.info("Monkey 测试执行成功")
                    rotator.write("\nMonkey 测试执行成功\n")
        except Exception as e:
            logger.error(f"执行 Monkey 测试时发生错误: {e}")
            if rotator is not None:
                rotator.write(f"\n执行 Monkey 测试时发生错误: {e}\n")
            raise
        finally:
            stop_event.set()
            if rotator is not None:
                rotator.close()

    def parse_monkey_event(self, line, log_file_handle):
        """解析 Monkey 输出坐标，并查找对应 UI 元素。"""
        match = re.search(r"Sending Touch .*?\(([\d.]+),([\d.]+)\)", line)
        if match:
            x, y = float(match.group(1)), float(match.group(2))
            try:
                element_info = self.find_element_by_coord(x, y)
                msg = f"[点击坐标 ({x},{y})] → 元素: {element_info}"
            except Exception as e:
                msg = f"[点击坐标 ({x},{y})] → UI解析异常: {e}"
            log_file_handle.write(msg + "\n")

    def find_element_by_coord(self, x, y):
        """深度优先遍历 UI 树，查找包含指定坐标的元素。"""
        xml = self.d.dump_hierarchy()
        root = ET.fromstring(xml)
        best_node_info = None
        max_depth = -1
        clickable_node_info = None

        def traverse(node, depth=0):
            nonlocal best_node_info, max_depth, clickable_node_info
            bounds = node.attrib.get("bounds")
            if bounds:
                try:
                    left_top, right_bottom = bounds.split("][")
                    left_top = left_top.strip("[").split(",")
                    right_bottom = right_bottom.strip("]").split(",")
                    left, top = int(left_top[0]), int(left_top[1])
                    right, bottom = int(right_bottom[0]), int(right_bottom[1])
                    if left <= x <= right and top <= y <= bottom:
                        text = node.attrib.get("text", "")
                        rid = node.attrib.get("resource-id", "")
                        clazz = node.attrib.get("class", "")
                        info = f"text={text}, resource-id={rid}, class={clazz}"
                        if node.attrib.get("clickable") == "true":
                            clickable_node_info = info
                        if depth > max_depth:
                            best_node_info = info
                            max_depth = depth
                except Exception as e:
                    logger.debug(f"解析 UI 元素时发生错误: {e}")
            for child in node:
                traverse(child, depth + 1)

        traverse(root)
        if clickable_node_info:
            return clickable_node_info
        if best_node_info:
            return best_node_info
        return "未找到元素"
