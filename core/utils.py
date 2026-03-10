# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2025/1/10
"""

import os
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

