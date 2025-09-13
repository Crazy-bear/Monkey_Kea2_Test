# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2025/1/10
"""

import os
import datetime


def create_output_dirs(base_dir):
    """
    创建输出目录。
    """
    os.makedirs(base_dir, exist_ok=True)


def get_timestamp():
    """
    获取当前时间戳。
    """
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
