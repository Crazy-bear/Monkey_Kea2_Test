# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2026/3/11

CPU监控模块
功能：
1. 使用adb shell top采集CPU使用率
2. 支持多设备
3. 解析top命令输出，提取指定应用的CPU使用率
"""
import subprocess
import re
from config.logging_config import logger


class CPUMonitor:
    def __init__(self, device_id, package_name):
        self.device_id = device_id
        self.package_name = package_name

    def _run(self, cmd, timeout=8):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, shell=False)
            return r.stdout if r.returncode == 0 else ""
        except Exception:
            return ""

    def _get_pid(self):
        """获取应用 PID，返回字符串列表（可能多进程）"""
        out = self._run(['adb', '-s', self.device_id, 'shell', 'pidof', self.package_name])
        if out.strip():
            return out.strip().split()
        # 兜底：用 ps 查找
        out = self._run(['adb', '-s', self.device_id, 'shell', 'ps', '-A'])
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
          1. top -n 1 -p <pid>  解析进程行的 CPU 列（第9列，Android top 格式）
          2. 兜底：top -n 1 全量输出，按包名/PID 匹配
          3. 再兜底：/proc/<pid>/stat 计算 CPU 占用

        Returns:
            float: CPU 使用率（%），失败返回 0.0
        """
        try:
            pids = self._get_pid()
            if not pids:
                logger.warning(f"未找到应用 {self.package_name} 的 PID")
                return 0.0

            pid = pids[0]

            # ── 方法1：top -n 1 -p <pid> ─────────────────────────────────
            # Android top 输出格式（列顺序）：
            # PID  USER  PR  NI  VIRT  RES  SHR  S  %CPU  %MEM  TIME+  COMMAND
            out = self._run(['adb', '-s', self.device_id, 'shell', 'top', '-n', '1', '-p', pid])
            cpu = self._parse_top_for_pid(out, pid)
            if cpu is not None:
                return cpu

            # ── 方法2：top -n 1 全量，按包名匹配 ────────────────────────
            out = self._run(['adb', '-s', self.device_id, 'shell', 'top', '-n', '1'])
            cpu = self._parse_top_by_name(out, self.package_name, pid)
            if cpu is not None:
                return cpu

            # ── 方法3：/proc/<pid>/stat（两次采样差值）──────────────────
            cpu = self._proc_stat_cpu(pid)
            if cpu is not None:
                return cpu

            logger.warning(f"未找到应用 {self.package_name} 的 CPU 数据")
            return 0.0

        except Exception as e:
            logger.error(f"获取 CPU 使用率失败: {e}")
            return 0.0

    def _parse_top_for_pid(self, output, pid):
        """解析 top 输出，找到 pid 对应行，提取 CPU 列"""
        if not output:
            return None
        for line in output.splitlines():
            parts = line.split()
            if not parts:
                continue
            # 第一列是 PID
            if parts[0] == pid:
                # Android top: PID USER PR NI VIRT RES SHR S %CPU %MEM TIME ARGS
                # %CPU 在第9列（index 8）
                cpu = self._try_float_col(parts, 8)
                if cpu is not None:
                    return cpu
                # 有些 ROM 格式不同，遍历找第一个合理的百分比数字
                for p in parts[1:]:
                    v = self._try_float(p.rstrip('%'))
                    if v is not None and 0.0 <= v <= 3200.0:
                        return v
        return None

    def _parse_top_by_name(self, output, package_name, pid=None):
        """在全量 top 输出中按包名或 PID 匹配"""
        if not output:
            return None
        short_name = package_name.split('.')[-1]
        for line in output.splitlines():
            parts = line.split()
            if not parts:
                continue
            line_lower = line.lower()
            matched = (package_name in line or short_name in line_lower
                       or (pid and parts[0] == pid))
            if matched:
                # 跳过标题行
                if parts[0].upper() in ('PID', 'USER', 'TID'):
                    continue
                cpu = self._try_float_col(parts, 8)
                if cpu is not None:
                    return cpu
                # 遍历找合理数值
                for p in parts[1:6]:
                    v = self._try_float(p.rstrip('%'))
                    if v is not None and 0.0 < v <= 3200.0:
                        return v
        return None

    def _proc_stat_cpu(self, pid):
        """
        通过 /proc/<pid>/stat 和 /proc/stat 计算 CPU 占用率（两次采样，间隔 0.5s）
        """
        import time

        def read_proc(p):
            out = self._run(['adb', '-s', self.device_id, 'shell',
                             'cat', f'/proc/{p}/stat', '/proc/stat'])
            return out

        try:
            out1 = read_proc(pid)
            time.sleep(0.5)
            out2 = read_proc(pid)

            def parse(text):
                lines = text.splitlines()
                proc_line = lines[0] if lines else ''
                cpu_line = next((l for l in lines if l.startswith('cpu ')), '')
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
            return CPUMonitor._try_float(parts[idx].rstrip('%'))
        return None

    @staticmethod
    def _try_float(s):
        try:
            return float(s)
        except (ValueError, TypeError):
            return None
