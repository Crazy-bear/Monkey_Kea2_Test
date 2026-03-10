# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2025/1/10

登录页面类
"""
from pages.base_page import BasePage


class LoginPage(BasePage):
    """
    登录页面类
    """
    # 元素定位器
    USERNAME_INPUT = "com.aeke.fitnessmirror:id/username_input"
    PASSWORD_INPUT = "com.aeke.fitnessmirror:id/password_input"
    LOGIN_BUTTON = "com.aeke.fitnessmirror:id/login_button"
    ERROR_MESSAGE = "com.aeke.fitnessmirror:id/error_message"
    
    def login(self, username, password):
        """
        登录操作
        
        Args:
            username: 用户名
            password: 密码
        """
        self.send_keys(self.USERNAME_INPUT, username)
        self.send_keys(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)
    
    def get_error_message(self):
        """
        获取错误信息
        
        Returns:
            错误信息文本
        """
        return self.get_text(self.ERROR_MESSAGE)
    
    def is_login_success(self):
        """
        检查登录是否成功
        
        Returns:
            bool: 登录是否成功
        """
        # 这里需要根据实际应用的登录成功判断逻辑来实现
        # 例如检查主页面元素是否显示
        return not self.is_displayed(self.LOGIN_BUTTON)
