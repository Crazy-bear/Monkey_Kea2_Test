# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2025/1/10

Logcat 捕获与崩溃检测/分析。
"""

import re
import subprocess
import threading
import time
from settings.logging_config import logger
from core.utils import LogRotator

# 崩溃事件锚点：以这些模式识别独立崩溃事件，避免逐行误报
_CRASH_ANCHOR_PATTERNS = [
    re.compile(r"FATAL EXCEPTION", re.IGNORECASE),
    re.compile(r"ANR in ", re.IGNORECASE),
    # 避免匹配 app_process: / ExecuteForProcess: 等误报
    re.compile(r"(?<![A-Za-z_])Process:\s+\S+", re.IGNORECASE),
    re.compile(r"Fatal signal \d+", re.IGNORECASE),
    re.compile(r"libc\s*:\s*Fatal signal", re.IGNORECASE),
]

_EXCEPTION_CATEGORIES = [
    "NullPointerException",
    "OutOfMemoryError",
    "IllegalStateException",
    "RuntimeException",
    "ClassCastException",
    "IndexOutOfBoundsException",
    "IOException",
    "ANR",
]


def _line_matches_package(line, package_name):
    """行是否与目标包相关（用于过滤无关进程日志）。"""
    if not package_name:
        return True
    short = package_name.split(".")[-1]
    return package_name in line or short in line


def _classify_exception_line(line):
    """将异常行归类。"""
    if "ANR in" in line or re.search(r"\bANR\b", line):
        return "ANR"
    for cat in _EXCEPTION_CATEGORIES:
        if cat == "ANR":
            continue
        if cat in line:
            return cat
    return "Other"


def extract_crash_events(lines, package_name=None):
    """
    从 logcat 行列表中提取去重后的崩溃事件。

    策略：
    - 以 FATAL EXCEPTION / ANR in / Process: 等为锚点识别事件
    - 同一堆栈内重复行只计一次
    - 可选按包名过滤

    Returns:
        list[dict]: 每项含 category, message, signature
    """
    events = []
    seen_signatures = set()
    current_event = None

    def flush_event():
        nonlocal current_event
        if not current_event:
            return
        sig = current_event["signature"]
        if sig not in seen_signatures:
            seen_signatures.add(sig)
            events.append({
                "category": current_event["category"],
                "message": current_event["message"],
                "signature": sig,
            })
        current_event = None

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        is_anchor = any(p.search(line) for p in _CRASH_ANCHOR_PATTERNS)
        is_exception = any(cat in line for cat in _EXCEPTION_CATEGORIES if cat != "ANR")
        is_anr = "ANR in" in line

        if is_anchor or is_anr or (is_exception and "Exception" in line):
            if package_name and not _line_matches_package(line, package_name):
                if not is_anchor and not is_anr:
                    continue

            flush_event()
            category = _classify_exception_line(line)
            current_event = {
                "category": category,
                "message": line,
                "signature": f"{category}:{line[:200]}",
            }
        elif current_event and (line.startswith("at ") or line.startswith("Caused by:")):
            current_event["message"] += "\n" + line
            current_event["signature"] = f"{current_event['category']}:{current_event['message'][:300]}"

    flush_event()
    return events


class LogcatHandler:
    def __init__(self, config):
        self.config = config
        self.process = None
        self.crash_callback = None
        self._output_thread = None
        self._auto_stop_timer = None

    def start_logcat(self, output_file, buffers=None, max_bytes=10 * 1024 * 1024, max_duration=None):
        """
        启动 Logcat 日志捕获，支持日志轮转与可选超时自动停止。

        Args:
            output_file: 日志输出文件路径
            buffers: 要捕获的日志缓冲区列表
            max_bytes: 日志文件最大大小
            max_duration: 可选，最大捕获时长（秒），到期自动 stop_logcat

        Returns:
            subprocess.Popen 或 None
        """
        if buffers is None:
            buffers = ["main", "events", "crash"]

        cmd = ["adb", "-s", self.config.DEVICE_ID, "logcat"]
        for buffer in buffers:
            cmd.extend(["-b", buffer])

        try:
            subprocess.run(
                ["adb", "-s", self.config.DEVICE_ID, "logcat", "-c"],
                shell=False,
                capture_output=True,
                timeout=15,
            )
            logger.info("已清空设备 Logcat 缓冲区")
        except Exception as e:
            logger.warning(f"清空 Logcat 缓冲区失败（将继续捕获）: {e}")

        try:
            rotator = LogRotator(output_file, max_bytes)

            process = subprocess.Popen(
                cmd,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="ignore",
            )

            def handle_output():
                try:
                    for line in process.stdout:
                        rotator.write(line)
                except Exception as e:
                    logger.error(f"处理日志输出时发生错误: {e}")
                finally:
                    rotator.close()

            self._output_thread = threading.Thread(target=handle_output, daemon=True)
            self._output_thread.start()

            self.process = process
            logger.info(f"Logcat 日志捕获已启动，输出到: {output_file}")

            if max_duration and max_duration > 0:
                def auto_stop():
                    time.sleep(max_duration)
                    if self.process and self.process.poll() is None:
                        logger.info(f"Logcat 达到 max_duration={max_duration}s，自动停止")
                        self.stop_logcat()

                self._auto_stop_timer = threading.Timer(max_duration, auto_stop)
                self._auto_stop_timer.daemon = True
                self._auto_stop_timer.start()

            return process
        except Exception as e:
            logger.error(f"启动 Logcat 失败: {e}")
            return None

    def stop_logcat(self):
        """停止 Logcat 捕获。"""
        if self._auto_stop_timer:
            self._auto_stop_timer.cancel()
            self._auto_stop_timer = None

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
        检测日志中的崩溃事件（去重后）。

        Returns:
            list[dict]: 崩溃事件列表
        """
        try:
            with open(log_file, "r", encoding="utf-8", errors="ignore") as file:
                lines = file.readlines()
            package = getattr(self.config, "PACKAGE_NAME", None)
            return extract_crash_events(lines, package_name=package)
        except FileNotFoundError:
            logger.error(f"错误: 日志文件 {log_file} 未找到。")
        except OSError as e:
            logger.error(f"IO 错误: {e}")
        except Exception as e:
            logger.error(f"检测崩溃时发生错误: {e}")
        return []

    def analyze_logs(self, log_file):
        """
        分析日志文件，提供崩溃分类与结论。

        Returns:
            dict: 日志分析结果
        """
        analysis_result = {
            "crash_categories": {},
            "total_crashes": 0,
            "analysis_conclusion": "",
            "crash_details": [],
        }

        try:
            logger.info(f"开始分析日志文件: {log_file}")
            events = self.detect_crashes(log_file)
            crash_categories = {cat: 0 for cat in _EXCEPTION_CATEGORIES + ["Other"]}

            for event in events:
                cat = event.get("category", "Other")
                if cat not in crash_categories:
                    cat = "Other"
                crash_categories[cat] += 1
                analysis_result["crash_details"].append({
                    "category": cat,
                    "message": event.get("message", ""),
                })

            analysis_result["crash_categories"] = {
                k: v for k, v in crash_categories.items() if v > 0
            }
            total_crashes = len(events)
            analysis_result["total_crashes"] = total_crashes

            if total_crashes == 0:
                analysis_result["analysis_conclusion"] = "未检测到崩溃，应用稳定性良好。"
            else:
                most_common = max(analysis_result["crash_categories"].items(), key=lambda x: x[1])
                analysis_result["analysis_conclusion"] = (
                    f"共检测到 {total_crashes} 个崩溃事件，"
                    f"其中最常见类型为 {most_common[0]}（{most_common[1]} 次）。"
                )

            logger.info(f"日志分析完成，崩溃事件数: {total_crashes}")
        except FileNotFoundError:
            logger.error(f"错误: 日志文件 {log_file} 未找到。")
            analysis_result["analysis_conclusion"] = "无法分析日志，文件未找到。"
        except Exception as e:
            logger.error(f"分析日志时发生错误: {e}")
            analysis_result["analysis_conclusion"] = f"分析日志时发生错误: {e}"

        return analysis_result

    def start_real_time_crash_detection(self, log_file, callback=None):
        """启动实时崩溃检测（基于事件锚点）。"""
        self.crash_callback = callback
        seen = set()

        def monitor_logs():
            last_position = 0
            while self.process and self.process.poll() is None:
                try:
                    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                        f.seek(last_position)
                        new_content = f.read()
                        last_position = f.tell()

                    if new_content:
                        package = getattr(self.config, "PACKAGE_NAME", None)
                        for event in extract_crash_events(new_content.splitlines(), package):
                            sig = event["signature"]
                            if sig not in seen:
                                seen.add(sig)
                                if self.crash_callback:
                                    self.crash_callback(event)
                                logger.warning(f"实时检测到崩溃: {event['message'][:200]}")
                except Exception as e:
                    logger.error(f"监控日志时发生错误: {e}")
                time.sleep(1)

        monitor_thread = threading.Thread(target=monitor_logs, daemon=True)
        monitor_thread.start()
        logger.info("实时崩溃检测已启动")
