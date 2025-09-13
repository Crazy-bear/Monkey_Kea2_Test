# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2025/1/10
<<<<<<< HEAD

日志配置文件
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from core.utils import get_timestamp, create_output_dirs

# 日志目录
LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs", "logs")
create_output_dirs(LOG_DIR)

# 日志文件名
LOG_FILE = os.path.join(LOG_DIR, f"monkey_test_{get_timestamp()}.log")

# 日志配置
def setup_logger():
    """
    设置日志系统
    
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    # 创建日志记录器
    logger = logging.getLogger("MonkeyTest")
    logger.setLevel(logging.DEBUG)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 创建文件处理器（支持日志轮转）
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    
    # 创建日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 设置处理器的格式
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # 添加处理器到日志记录器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# 导出日志记录器
logger = setup_logger()
=======
"""

import logging


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("outputs/logs/test.log"),
            logging.StreamHandler()
        ]
    )
>>>>>>> bc185e8 (Monkey稳定性测试)
