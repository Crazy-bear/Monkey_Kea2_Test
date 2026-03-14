# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2025/1/10
"""

import os
import time
import datetime

# 避免循环导入，在函数内部导入
logger = None


def _get_logger():
    """
    获取日志记录器
    """
    global logger
    if logger is None:
        from config.logging_config import logger
    return logger


def create_output_dirs(base_dir):
    """
    创建输出目录。
    
    Args:
        base_dir: 目录路径
        
    Returns:
        bool: 创建是否成功
    """
    try:
        os.makedirs(base_dir, exist_ok=True)
        return True
    except Exception as e:
        _get_logger().error(f"创建目录失败: {e}")
        return False


def get_timestamp():
    """
    获取当前时间戳。
    
    Returns:
        str: 时间戳字符串
    """
    try:
        return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    except Exception as e:
        _get_logger().error(f"获取时间戳失败: {e}")
        return "unknown_timestamp"


def safe_open(file_path, mode='r', encoding='utf-8'):
    """
    安全打开文件
    
    Args:
        file_path: 文件路径
        mode: 打开模式
        encoding: 编码
        
    Returns:
        file object 或 None
    """
    try:
        return open(file_path, mode, encoding=encoding)
    except Exception as e:
        _get_logger().error(f"打开文件失败 {file_path}: {e}")
        return None


def safe_close(file_obj):
    """
    安全关闭文件

    Args:
        file_obj: 文件对象
    """
    try:
        if file_obj:
            file_obj.close()
    except Exception as e:
        _get_logger().error(f"关闭文件失败: {e}")


class LogRotator:
    """
    日志轮转处理器：写入超过 max_size 时按时间戳轮转，避免单文件过大。
    """

    def __init__(self, file_path, max_size, rotate_interval_seconds=600):
        self.file_path = file_path
        self.max_size = max_size
        self.rotate_interval_seconds = rotate_interval_seconds
        self.file = open(file_path, "w", encoding="utf-8")
        self.closed = False
        self.last_rotate_time = 0

    def write(self, data):
        if self.closed:
            return
        try:
            self.file.write(data)
            self.file.flush()
            current_time = time.time()
            if current_time - self.last_rotate_time >= self.rotate_interval_seconds:
                self.file.seek(0, os.SEEK_END)
                if self.file.tell() > self.max_size:
                    self._rotate()
                    self.last_rotate_time = current_time
        except Exception as e:
            _get_logger().error(f"日志写入失败: {e}")

    def _rotate(self):
        if self.closed:
            return
        try:
            self.file.close()
            base, ext = os.path.splitext(self.file_path)
            timestamp = get_timestamp()
            new_filename = f"{base}_{timestamp}{ext}"
            if os.path.exists(self.file_path):
                os.rename(self.file_path, new_filename)
                _get_logger().info(f"日志文件已轮转: {new_filename}")
            self.file = open(self.file_path, "w", encoding="utf-8")
        except Exception as e:
            _get_logger().error(f"日志轮转失败: {e}")
            try:
                self.file = open(self.file_path, "w", encoding="utf-8")
            except Exception:
                pass

    def close(self):
        if not self.closed and self.file:
            try:
                self.file.close()
            except Exception:
                pass
            self.closed = True

