# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2025/1/10
"""
import os
import datetime
import configparser
from config.logging_config import logger


class Config:
    """
    配置管理类
    支持从环境变量、配置文件和默认值读取配置
    """
    # 默认配置
    DEFAULT_DEVICE_ID = "192.168.20.81:5555"  # 默认手机设备 ID
    DEFAULT_PACKAGE_NAME = "com.aeke.fitnessmirror"  # 设备端测试应用包名
    DEFAULT_EVENT_COUNT = 100000  # 默认事件数量
    
    # 从环境变量读取配置
    DEVICE_ID = os.environ.get('MONKEY_DEVICE_ID', DEFAULT_DEVICE_ID)
    PACKAGE_NAME = os.environ.get('MONKEY_PACKAGE_NAME', DEFAULT_PACKAGE_NAME)
    EVENT_COUNT = int(os.environ.get('MONKEY_EVENT_COUNT', DEFAULT_EVENT_COUNT))
    
    # 尝试从配置文件读取配置
    config_file = 'config.ini'
    if os.path.exists(config_file):
        config = configparser.ConfigParser()
        config.read(config_file)
        if 'DEFAULT' in config:
            DEVICE_ID = config['DEFAULT'].get('DEVICE_ID', DEVICE_ID)
            PACKAGE_NAME = config['DEFAULT'].get('PACKAGE_NAME', PACKAGE_NAME)
            EVENT_COUNT = int(config['DEFAULT'].get('EVENT_COUNT', EVENT_COUNT))
    
    # 随机种子
    SEED = int(datetime.datetime.now().strftime("%Y%m%d%H%M"))  # 随机种子按"年月日时分"格式生成
    # SEED = 202512101346  # 指定种子数
    
    def __init__(self):
        """
        初始化配置，获取应用信息
        """
        self.device_version_name = None
        self._get_app_info()
    
    def _get_app_info(self):
        """
        获取应用信息
        """
        try:
            import uiautomator2 as u2
            d = u2.connect(self.DEVICE_ID)  # 连接设备
            device_info = d.app_info(self.PACKAGE_NAME)
            self.device_version_name = device_info.get('versionName')
            logger.info(f"DeviceVersionName: {self.device_version_name}")
        except Exception as e:
            logger.error(f"获取应用信息失败: {e}")
            self.device_version_name = "Unknown"
    
    @property
    def DeviceVersionName(self):
        """
        获取设备版本名称
        """
        if self.device_version_name is None:
            self._get_app_info()
        return self.device_version_name

