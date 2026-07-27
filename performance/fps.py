# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2026/3/11

FPS监控模块
"""
import re
from settings.logging_config import logger
from core.adb_client import ADBClient


class FPSMonitor:
    def __init__(self, device_id, package_name, adb_client=None):
        self.device_id = device_id
        self.package_name = package_name
        self.adb = adb_client or ADBClient(device_id=device_id)

    def _reset_frame_stats(self):
        """重置 gfxinfo 帧统计，使后续采样反映当前区间。"""
        self.adb.shell("dumpsys", "gfxinfo", self.package_name, "reset", timeout=5, retry_count=1)

    def _parse_fps(self, output):
        total_frames_match = re.search(r"Total frames rendered:\s+(\d+)", output)
        if total_frames_match:
            percentile_match = re.search(r"50th percentile:\s+([\d.]+)ms", output)
            if percentile_match:
                avg_frame_time = float(percentile_match.group(1))
                if avg_frame_time > 0:
                    return min(1000 / avg_frame_time, 60.0)

        summary_match = re.search(r"Summary.*?Average frame time:\s+([\d.]+)ms", output, re.DOTALL)
        if summary_match:
            avg_frame_time = float(summary_match.group(1))
            if avg_frame_time > 0:
                return min(1000 / avg_frame_time, 60.0)

        frame_timing_match = re.search(r"FrameTiming.*?\s+\d+\s+:\s+([\d.]+)", output, re.DOTALL)
        if frame_timing_match:
            frame_time = float(frame_timing_match.group(1))
            if frame_time > 0:
                return min(1000 / frame_time, 60.0)

        total_frames_match = re.search(r"Total frames rendered:\s+(\d+)", output)
        total_time_match = re.search(r"Total time:\s+([\d.]+)ms", output)
        if total_frames_match and total_time_match:
            total_frames = int(total_frames_match.group(1))
            total_time = float(total_time_match.group(1))
            if total_time > 0:
                return min((total_frames * 1000) / total_time, 60.0)

        return 0.0

    def get_fps(self):
        """
        获取应用的 FPS 值（每次采样前 reset，反映当前区间）。

        Returns:
            float: FPS 值
        """
        try:
            self._reset_frame_stats()
            output = self.adb.shell("dumpsys", "gfxinfo", self.package_name, timeout=5)
            if not output.strip():
                logger.error("执行 dumpsys gfxinfo 命令失败或无输出")
                return 0.0

            fps = self._parse_fps(output)
            if fps <= 0:
                logger.warning(f"未找到应用 {self.package_name} 的 FPS 数据")
            return fps
        except Exception as e:
            logger.error(f"获取 FPS 失败: {e}")
            return 0.0
