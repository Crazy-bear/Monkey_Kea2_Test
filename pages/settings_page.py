# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2025/1/10

设置页面类
"""
from pages.base_page import BasePage


class SettingsPage(BasePage):
    """
    设置页面类
    """
    # 元素定位器
    SETTINGS_BUTTON = "com.aeke.fitnessmirror:id/settings_button"
    LOGOUT_BUTTON = "com.aeke.fitnessmirror:id/logout_button"
    ABOUT_BUTTON = "com.aeke.fitnessmirror:id/about_button"
    VERSION_INFO = "com.aeke.fitnessmirror:id/version_info"
    
    def logout(self):
        """
        退出登录
        """
        self.click(self.LOGOUT_BUTTON)
    
    def go_to_about(self):
        """
        进入关于页面
        """
        self.click(self.ABOUT_BUTTON)
    
    def get_version_info(self):
        """
        获取版本信息
        
        Returns:
            版本信息文本
        """
        return self.get_text(self.VERSION_INFO)
    
    def is_settings_page_displayed(self):
        """
        检查设置页面是否显示
        
        Returns:
            bool: 设置页面是否显示
        """
        return self.is_displayed(self.SETTINGS_BUTTON)
