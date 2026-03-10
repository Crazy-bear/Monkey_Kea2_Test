# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2025/1/10

基础页面类，提供通用方法
"""
import uiautomator2 as u2


class BasePage:
    """
    基础页面类
    """
    def __init__(self, device):
        """
        初始化基础页面
        
        Args:
            device: uiautomator2设备实例
        """
        self.device = device
    
    def click(self, locator):
        """
        点击元素
        
        Args:
            locator: 元素定位器
        """
        self.device(resourceId=locator).click()
    
    def send_keys(self, locator, text):
        """
        输入文本
        
        Args:
            locator: 元素定位器
            text: 要输入的文本
        """
        self.device(resourceId=locator).set_text(text)
    
    def get_text(self, locator):
        """
        获取元素文本
        
        Args:
            locator: 元素定位器
            
        Returns:
            元素文本
        """
        return self.device(resourceId=locator).get_text()
    
    def is_displayed(self, locator):
        """
        检查元素是否显示
        
        Args:
            locator: 元素定位器
            
        Returns:
            bool: 元素是否显示
        """
        return self.device(resourceId=locator).exists
    
    def wait_until_displayed(self, locator, timeout=10):
        """
        等待元素显示
        
        Args:
            locator: 元素定位器
            timeout: 超时时间（秒）
            
        Returns:
            bool: 元素是否在超时前显示
        """
        return self.device(resourceId=locator).wait(timeout=timeout)
