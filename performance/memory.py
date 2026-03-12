# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2026/3/11

内存监控模块
功能：
1. 使用adb shell dumpsys meminfo采集内存使用数据
2. 支持多设备
3. 解析meminfo输出，提取指定应用的内存使用情况
"""
import subprocess
import re
from config.logging_config import logger


class MemoryMonitor:
    def __init__(self, device_id, package_name):
        """
        初始化内存监控器
        
        Args:
            device_id: 设备ID
            package_name: 应用包名
        """
        self.device_id = device_id
        self.package_name = package_name
    
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
