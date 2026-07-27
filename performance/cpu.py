# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2026/3/11

CPU监控模块
"""
import re
from settings.logging_config import logger
from core.adb_client import ADBClient


class CPUMonitor:
    def __init__(self, device_id, package_name, adb_client=None):
        self.device_id = device_id
        self.package_name = package_name
        self.adb = adb_client or ADBClient(device_id=device_id)

    def _run(self, *shell_args, timeout=8):
        out = self.adb.shell(*shell_args, timeout=timeout)
        return out or ""

    def _get_pid(self):
        """获取应用 PID，返回字符串列表（可能多进程）"""
        out = self._run("pidof", self.package_name)
        if out.strip():
            return out.strip().split()
        out = self._run("ps", "-A")
        pids = []
        for line in out.splitlines():
            if self.package_name in line:
                parts = line.split()
                if len(parts) >= 2:
                    pids.append(parts[1])
        return pids

    def get_cpu_usage(self):
        """
        获取应用的 CPU 使用率（%）

        策略：
          1. top -n 1 -p <pid>
          2. top -n 1 全量输出
          3. /proc/<pid>/stat 差值
        """
        try:
            pids = self._get_pid()
            if not pids:
                logger.warning(f"未找到应用 {self.package_name} 的 PID")
                return 0.0

            pid = pids[0]
            out = self._run("top", "-n", "1", "-p", pid)
            cpu = self._parse_top_for_pid(out, pid)
            if cpu is not None:
                return cpu

            out = self._run("top", "-n", "1")
            cpu = self._parse_top_by_name(out, self.package_name, pid)
            if cpu is not None:
                return cpu

            cpu = self._proc_stat_cpu(pid)
            if cpu is not None:
                return cpu

            logger.warning(f"未找到应用 {self.package_name} 的 CPU 数据")
            return 0.0
        except Exception as e:
            logger.error(f"获取 CPU 使用率失败: {e}")
            return 0.0

    def _parse_top_for_pid(self, output, pid):
        if not output:
            return None
        for line in output.splitlines():
            parts = line.split()
            if not parts:
                continue
            if parts[0] == pid:
                cpu = self._try_float_col(parts, 8)
                if cpu is not None:
                    return cpu
                for p in parts[1:]:
                    v = self._try_float(p.rstrip("%"))
                    if v is not None and 0.0 <= v <= 3200.0:
                        return v
        return None

    def _parse_top_by_name(self, output, package_name, pid=None):
        if not output:
            return None
        short_name = package_name.split(".")[-1]
        for line in output.splitlines():
            parts = line.split()
            if not parts:
                continue
            line_lower = line.lower()
            matched = (
                package_name in line or short_name in line_lower
                or (pid and parts[0] == pid)
            )
            if matched:
                if parts[0].upper() in ("PID", "USER", "TID"):
                    continue
                cpu = self._try_float_col(parts, 8)
                if cpu is not None:
                    return cpu
                for p in parts[1:6]:
                    v = self._try_float(p.rstrip("%"))
                    if v is not None and 0.0 < v <= 3200.0:
                        return v
        return None

    def _proc_stat_cpu(self, pid):
        import time

        def read_proc(p):
            return self._run("cat", f"/proc/{p}/stat", "/proc/stat")

        try:
            out1 = read_proc(pid)
            time.sleep(0.5)
            out2 = read_proc(pid)

            def parse(text):
                lines = text.splitlines()
                proc_line = lines[0] if lines else ""
                cpu_line = next((l for l in lines if l.startswith("cpu ")), "")
                proc_vals = proc_line.split()
                cpu_vals = cpu_line.split()
                if len(proc_vals) < 15 or len(cpu_vals) < 5:
                    return None, None
                utime = int(proc_vals[13])
                stime = int(proc_vals[14])
                total = sum(int(x) for x in cpu_vals[1:])
                return utime + stime, total

            p1, t1 = parse(out1)
            p2, t2 = parse(out2)
            if None in (p1, t1, p2, t2) or t2 == t1:
                return None
            return round((p2 - p1) / (t2 - t1) * 100, 2)
        except Exception:
            return None

    @staticmethod
    def _try_float_col(parts, idx):
        if idx < len(parts):
            return CPUMonitor._try_float(parts[idx].rstrip("%"))
        return None

    @staticmethod
    def _try_float(s):
        try:
            return float(s)
        except (ValueError, TypeError):
            return None
