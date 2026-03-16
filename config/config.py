# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2025/1/10
"""
<<<<<<< HEAD
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
    DEFAULT_DEVICE_ID = "192.168.20.152:5555"  # 默认手机设备 ID
    DEFAULT_PACKAGE_NAME = "com.aeke.fitnessmirror"  # 设备端测试应用包名
    DEFAULT_EVENT_COUNT = 300  # 默认事件数量
    
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
        初始化配置。应用版本信息懒加载，避免无设备时阻塞启动。
        """
        self.device_version_name = None  # 首次访问 DeviceVersionName 时再拉取

    def _get_app_info(self):
        """
        获取应用信息（懒加载，仅在有设备时调用）
        """
        try:
            import uiautomator2 as u2
            d = u2.connect(self.DEVICE_ID)
            device_info = d.app_info(self.PACKAGE_NAME)
            self.device_version_name = device_info.get('versionName') or "Unknown"
            logger.info(f"DeviceVersionName: {self.device_version_name}")
        except Exception as e:
            logger.error(f"获取应用信息失败: {e}")
            self.device_version_name = "Unknown"

    @property
    def DeviceVersionName(self):
        """
        获取设备版本名称（懒加载）
        """
        if self.device_version_name is None:
            self._get_app_info()
        return self.device_version_name or "Unknown"

    def validate(self):
        """
        校验配置是否可用于执行测试（不连接设备）。
        Returns:
            (bool, list): 是否通过，错误信息列表
        """
        errors = []
        if not getattr(self, 'DEVICE_ID', None) or not str(self.DEVICE_ID).strip():
            errors.append("设备ID未配置")
        if not getattr(self, 'PACKAGE_NAME', None) or not str(self.PACKAGE_NAME).strip():
            errors.append("应用包名未配置")
        try:
            c = int(getattr(self, 'EVENT_COUNT', 0))
            if c <= 0:
                errors.append("事件数量必须大于0")
        except (TypeError, ValueError):
            errors.append("事件数量必须为正整数")
        return (len(errors) == 0, errors)

=======
import datetime
import uiautomator2 as u2


class Config:
    # DEVICE_ID = "192.168.20.28:5555"  # 实验室设备 ID
    # DEVICE_ID = "192.168.20.51:5555"  # 何老师设备 ID
    # DEVICE_ID = "192.168.20.121:5555"  # 实验室设备 ID
    # DEVICE_ID = "1MRtest30KP103test"  # 设备 ID
    DEVICE_ID = "192.168.20.46:5555"  # 家彬设备 ID
    # DEVICE_ID = "1ef4a826"  # 手机设备 ID
    # DEVICE_ID = "192.168.20.139:5555"  # 运动空间K1设备 ID
    PACKAGE_NAME = "com.aeke.fitnessmirror"  # 设备端测试应用包名

    # 获取当前应用信息
    d = u2.connect(DEVICE_ID)  # 连接设备
    Deviceinfo = d.app_info(PACKAGE_NAME)


    # print(Deviceinfo)
    DeviceVersionName = Deviceinfo.get('versionName')
    # a = Deviceinfo.get('package')
    # print(a)
    # print("DeviceVersionName:", DeviceVersionName)
    EVENT_COUNT = 1000000    # 事件数量
    SEED = int(datetime.datetime.now().strftime("%Y%m%d%H%M"))  # 随机种子按"年月日时分"格式生成
    # SEED = 202506101100  # 指定种子数值
>>>>>>> bc185e8 (Monkey稳定性测试)
