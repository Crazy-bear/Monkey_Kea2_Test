# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2025/1/10

日志配置文件
"""

import logging
import os
from logging.handlers import RotatingFileHandler

# 日志输出目录（outputs/logs/）
_LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs", "logs")


def setup_logger():
    """
    设置日志系统，同时输出到控制台和滚动文件。

    Returns:
        logging.Logger: 配置好的日志记录器
    """
    logger = logging.getLogger("MonkeyTest")
    logger.setLevel(logging.DEBUG)

    # 避免重复添加处理器
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 控制台处理器（INFO 及以上）
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件处理器（DEBUG 及以上，最大 10MB，保留 5 个备份）
    try:
        os.makedirs(_LOG_DIR, exist_ok=True)
        file_handler = RotatingFileHandler(
            os.path.join(_LOG_DIR, "monkey_test.log"),
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception:
        # 无法创建文件 handler 时仅使用控制台，不影响主流程
        pass

    return logger


# 导出日志记录器
logger = setup_logger()
