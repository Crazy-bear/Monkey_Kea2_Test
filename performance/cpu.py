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
        """
        初始化CPU监控器
        
        Args:
            device_id: 设备ID
            package_name: 应用包名
        """
        self.device_id = device_id
        self.package_name = package_name
    
    def get_cpu_usage(self):
        """
        获取应用的CPU使用率
        
        Returns:
            float: CPU使用率（百分比）
        """
        try:
            # 使用列表形式的命令，避免shell=True的问题
            # 首先获取应用的PID
            pid_cmd = ['adb', '-s', self.device_id, 'shell', 'pidof', self.package_name]
            pid_result = subprocess.run(pid_cmd, capture_output=True, text=True, timeout=5)
            
            if pid_result.returncode == 0 and pid_result.stdout.strip():
                pid = pid_result.stdout.strip()
                # 使用top命令获取指定PID的CPU使用率
                top_cmd = ['adb', '-s', self.device_id, 'shell', 'top', '-n', '1', '-p', pid]
                top_result = subprocess.run(top_cmd, capture_output=True, text=True, timeout=5)
                
                if top_result.returncode == 0:
                    output = top_result.stdout
                    # 查找包含PID的行
                    lines = output.strip().split('\n')
                    for line in lines:
                        if pid in line:
                            parts = line.strip().split()
                            # 尝试查找CPU使用率
                            for part in parts:
                                if '%' in part:
                                    try:
                                        cpu_usage = float(part.replace('%', ''))
                                        return cpu_usage
                                    except ValueError:
                                        continue
            
            # 如果上面的方法失败，尝试使用ps命令
            ps_cmd = ['adb', '-s', self.device_id, 'shell', 'ps', '-o', 'pid,pcpu,comm']
            ps_result = subprocess.run(ps_cmd, capture_output=True, text=True, timeout=5)
            
            if ps_result.returncode == 0:
                output = ps_result.stdout
                lines = output.strip().split('\n')
                
                # 查找包含包名的行
                for line in lines:
                    # 尝试匹配完整包名或截断的包名
                    if self.package_name in line or self.package_name.split('.')[-1] in line:
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            try:
                                cpu_usage = float(parts[1])
                                return cpu_usage
                            except (ValueError, IndexError):
                                continue
                
                # 尝试查找包含PID的行
                if 'pid' in locals():
                    for line in lines:
                        if pid in line:
                            parts = line.strip().split()
                            if len(parts) >= 2:
                                try:
                                    cpu_usage = float(parts[1])
                                    return cpu_usage
                                except (ValueError, IndexError):
                                    continue
            
            # 如果没有找到，返回0
            logger.warning(f"未找到应用 {self.package_name} 的CPU使用数据")
            return 0.0
            
        except subprocess.TimeoutExpired:
            logger.error("执行命令超时")
            return 0.0
        except Exception as e:
            logger.error(f"获取CPU使用率失败: {e}")
            return 0.0
