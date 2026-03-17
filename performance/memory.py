# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2026/3/11

内存监控模块
功能：
1. 使用adb shell dumpsys meminfo采集内存使用数据
2. 支持多设备
<<<<<<< HEAD
3. 解析meminfo输出，提取指定应用的内存使用情况（含分项：Java Heap、Native Heap、Graphics）
=======
3. 解析meminfo输出，提取指定应用的内存使用情况
>>>>>>> 976242683a0d1be6410f7f88d4d8d6e2b925f14c
"""
import subprocess
import re
from config.logging_config import logger


class MemoryMonitor:
    def __init__(self, device_id, package_name):
        """
        初始化内存监控器
<<<<<<< HEAD

=======
        
>>>>>>> 976242683a0d1be6410f7f88d4d8d6e2b925f14c
        Args:
            device_id: 设备ID
            package_name: 应用包名
        """
        self.device_id = device_id
        self.package_name = package_name
<<<<<<< HEAD

    def get_memory_usage(self):
        """
        获取应用的内存使用量及分项数据（单次 adb 调用，解析多个字段）

        返回 dict，包含：
          - total (float): TOTAL PSS，MB，保留两位小数
          - java_heap (float): Java Heap PSS，MB
          - native_heap (float): Native Heap PSS，MB
          - graphics (float): Graphics PSS，MB

        失败时返回 {"total": 0, "java_heap": 0, "native_heap": 0, "graphics": 0}
        """
        empty = {"total": 0.0, "java_heap": 0.0, "native_heap": 0.0, "graphics": 0.0}
        try:
            cmd = ['adb', '-s', self.device_id, 'shell',
                   'dumpsys', 'meminfo', self.package_name]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode != 0:
                logger.error(f"执行 dumpsys meminfo 命令失败: {result.stderr}")
                return empty

            output = result.stdout
            ret = dict(empty)

            # ── TOTAL PSS（App Summary 区块，Android 6+，最准确）──────────────
            # 格式：  TOTAL PSS:    360515 kB
            m = re.search(r'TOTAL PSS:\s+([\d,]+)', output)
            if m:
                ret['total'] = round(int(m.group(1).replace(',', '')) / 1024, 2)
            else:
                # 次选：TOTAL 行第一列（PSS Total）
                # 格式：       TOTAL    360515   ...
                m2 = re.search(r'^\s+TOTAL\s+([\d,]+)', output, re.MULTILINE)
                if m2:
                    ret['total'] = round(int(m2.group(1).replace(',', '')) / 1024, 2)
                else:
                    logger.warning(f"未找到应用 {self.package_name} 的内存使用数据")

            # ── Java Heap（Dalvik/ART 堆，对应 Java 对象泄漏）────────────────
            # App Summary 格式：  Java Heap:    123456 kB
            m = re.search(r'Java Heap:\s+([\d,]+)', output)
            if m:
                ret['java_heap'] = round(int(m.group(1).replace(',', '')) / 1024, 2)
            else:
                # 详细表格格式：  Dalvik Heap    123456  ...（第一列为 PSS）
                m = re.search(r'Dalvik Heap\s+([\d,]+)', output)
                if m:
                    ret['java_heap'] = round(int(m.group(1).replace(',', '')) / 1024, 2)

            # ── Native Heap（C/C++ 层，对应 JNI/NDK 泄漏）───────────────────
            # App Summary 格式：  Native Heap:  123456 kB
            m = re.search(r'Native Heap:\s+([\d,]+)', output)
            if m:
                ret['native_heap'] = round(int(m.group(1).replace(',', '')) / 1024, 2)
            else:
                # 详细表格格式：  Native Heap   123456  ...
                m = re.search(r'Native Heap\s+([\d,]+)', output)
                if m:
                    ret['native_heap'] = round(int(m.group(1).replace(',', '')) / 1024, 2)

            # ── Graphics（GPU 纹理/缓冲区，对应图形资源泄漏）─────────────────
            # App Summary 格式：  Graphics:     123456 kB
            m = re.search(r'Graphics:\s+([\d,]+)', output)
            if m:
                ret['graphics'] = round(int(m.group(1).replace(',', '')) / 1024, 2)
            else:
                # 详细表格格式：  EGL mtrack    123456  ...
                m = re.search(r'EGL mtrack\s+([\d,]+)', output)
                if m:
                    ret['graphics'] = round(int(m.group(1).replace(',', '')) / 1024, 2)

            return ret

        except subprocess.TimeoutExpired:
            logger.error("执行 dumpsys meminfo 命令超时")
            return empty
        except Exception as e:
            logger.error(f"获取内存使用量失败: {e}")
            return empty
=======
    
    def get_memory_usage(self):
        """
        获取应用的内存使用量
        
        Returns:
            int: 内存使用量（MB）
        """
        try:
            # 构建adb命令
            cmd = [
                'adb', '-s', self.device_id, 'shell', 'dumpsys', 'meminfo', self.package_name
            ]
            
            # 执行命令
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            if result.returncode != 0:
                logger.error(f"执行dumpsys meminfo命令失败: {result.stderr}")
                return 0
            
            # 解析输出
            output = result.stdout
            
            # 查找TOTAL行（匹配多种格式）
            total_match = re.search(r'\s+TOTAL\s+([\d,]+)\s+', output)
            if total_match:
                memory_kb = int(total_match.group(1).replace(',', ''))
                # 转换为MB
                memory_mb = memory_kb // 1024
                return memory_mb
            
            # 如果没有找到，查找App Summary中的TOTAL PSS
            total_pss_match = re.search(r'TOTAL PSS:\s+([\d,]+)', output)
            if total_pss_match:
                memory_kb = int(total_pss_match.group(1).replace(',', ''))
                memory_mb = memory_kb // 1024
                return memory_mb
            
            # 尝试查找其他可能的内存指标
            private_dirty_match = re.search(r'Private Dirty\s+:\s+([\d,]+)', output)
            if private_dirty_match:
                memory_kb = int(private_dirty_match.group(1).replace(',', ''))
                memory_mb = memory_kb // 1024
                return memory_mb
            
            # 如果都没有找到，返回0
            logger.warning(f"未找到应用 {self.package_name} 的内存使用数据")
            return 0
            
        except subprocess.TimeoutExpired:
            logger.error("执行dumpsys meminfo命令超时")
            return 0
        except Exception as e:
            logger.error(f"获取内存使用量失败: {e}")
            return 0
>>>>>>> 976242683a0d1be6410f7f88d4d8d6e2b925f14c
