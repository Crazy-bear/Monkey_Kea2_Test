# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2025/1/10
"""
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
