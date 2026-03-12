# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2026/3/11

FPS监控模块
功能：
1. 使用adb shell dumpsys gfxinfo采集FPS数据
2. 支持多设备
3. 解析gfxinfo输出，计算FPS值
"""
import subprocess
import re
from config.logging_config import logger


class FPSMonitor:
    def __init__(self, device_id, package_name):
        """
        初始化FPS监控器
        
        Args:
            device_id: 设备ID
            package_name: 应用包名
        """
        self.device_id = device_id
        self.package_name = package_name
        self.frame_times = []
    
    def get_fps(self):
        """
        获取应用的FPS值
        
        Returns:
            float: FPS值
        """
        try:
            # 使用列表形式的命令，避免shell=True的问题
            # 直接获取gfxinfo数据
            cmd = ['adb', '-s', self.device_id, 'shell', 'dumpsys', 'gfxinfo', self.package_name]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            if result.returncode != 0:
                logger.error(f"执行dumpsys gfxinfo命令失败: {result.stderr}")
                return 0.0
            
            # 解析输出
            output = result.stdout
            
            # 尝试多种方式提取FPS相关数据
            
            # 方式1：查找总帧数和百分位数数据
            total_frames_match = re.search(r'Total frames rendered:\s+(\d+)', output)
            if total_frames_match:
                # 尝试提取50th percentile的帧时间
                percentile_match = re.search(r'50th percentile:\s+([\d.]+)ms', output)
                if percentile_match:
                    avg_frame_time = float(percentile_match.group(1))
                    if avg_frame_time > 0:
                        fps = 1000 / avg_frame_time
                        return min(fps, 60.0)
            
            # 方式2：查找Summary部分的平均帧时间
            summary_match = re.search(r'Summary.*?Average frame time:\s+([\d.]+)ms', output, re.DOTALL)
            if summary_match:
                avg_frame_time = float(summary_match.group(1))
                if avg_frame_time > 0:
                    fps = 1000 / avg_frame_time
                    return min(fps, 60.0)
            
            # 方式3：查找FrameTiming部分
            frame_timing_match = re.search(r'FrameTiming.*?\s+\d+\s+:\s+([\d.]+)', output, re.DOTALL)
            if frame_timing_match:
                frame_time = float(frame_timing_match.group(1))
                if frame_time > 0:
                    fps = 1000 / frame_time
                    return min(fps, 60.0)
            
            # 方式4：查找总帧数和总时间
            total_frames_match = re.search(r'Total frames rendered:\s+(\d+)', output)
            total_time_match = re.search(r'Total time:\s+([\d.]+)ms', output)
            if total_frames_match and total_time_match:
                total_frames = int(total_frames_match.group(1))
                total_time = float(total_time_match.group(1))
                if total_time > 0:
                    fps = (total_frames * 1000) / total_time
                    return min(fps, 60.0)
            
            # 如果都没有找到，返回0
            logger.warning(f"未找到应用 {self.package_name} 的FPS数据")
            return 0.0
            
        except subprocess.TimeoutExpired:
            logger.error("执行dumpsys gfxinfo命令超时")
            return 0.0
        except Exception as e:
            logger.error(f"获取FPS失败: {e}")
            return 0.0
