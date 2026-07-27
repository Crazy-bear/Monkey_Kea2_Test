# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2026/3/11

内存监控模块
"""
import re
from settings.logging_config import logger
from core.adb_client import ADBClient


class MemoryMonitor:
    def __init__(self, device_id, package_name, adb_client=None):
        self.device_id = device_id
        self.package_name = package_name
        self.adb = adb_client or ADBClient(device_id=device_id)

    def get_memory_usage(self):
        """
        获取应用的内存使用量及分项数据。

        Returns:
            dict: total, java_heap, native_heap, graphics（单位 MB）
        """
        empty = {"total": 0.0, "java_heap": 0.0, "native_heap": 0.0, "graphics": 0.0}
        try:
            output = self.adb.shell("dumpsys", "meminfo", self.package_name, timeout=10)
            if not output.strip():
                logger.error("执行 dumpsys meminfo 命令失败或无输出")
                return empty

            ret = dict(empty)

            m = re.search(r"TOTAL PSS:\s+([\d,]+)", output)
            if m:
                ret["total"] = round(int(m.group(1).replace(",", "")) / 1024, 2)
            else:
                m2 = re.search(r"^\s+TOTAL\s+([\d,]+)", output, re.MULTILINE)
                if m2:
                    ret["total"] = round(int(m2.group(1).replace(",", "")) / 1024, 2)
                else:
                    logger.warning(f"未找到应用 {self.package_name} 的内存使用数据")

            m = re.search(r"Java Heap:\s+([\d,]+)", output)
            if m:
                ret["java_heap"] = round(int(m.group(1).replace(",", "")) / 1024, 2)
            else:
                m = re.search(r"Dalvik Heap\s+([\d,]+)", output)
                if m:
                    ret["java_heap"] = round(int(m.group(1).replace(",", "")) / 1024, 2)

            m = re.search(r"Native Heap:\s+([\d,]+)", output)
            if m:
                ret["native_heap"] = round(int(m.group(1).replace(",", "")) / 1024, 2)
            else:
                m = re.search(r"Native Heap\s+([\d,]+)", output)
                if m:
                    ret["native_heap"] = round(int(m.group(1).replace(",", "")) / 1024, 2)

            m = re.search(r"Graphics:\s+([\d,]+)", output)
            if m:
                ret["graphics"] = round(int(m.group(1).replace(",", "")) / 1024, 2)
            else:
                m = re.search(r"EGL mtrack\s+([\d,]+)", output)
                if m:
                    ret["graphics"] = round(int(m.group(1).replace(",", "")) / 1024, 2)

            return ret
        except Exception as e:
            logger.error(f"获取内存使用量失败: {e}")
            return empty
