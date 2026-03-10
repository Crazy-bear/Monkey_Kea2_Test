# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2025/1/10

示例功能页面类
"""
from pages.base_page import BasePage


class ExamplePage(BasePage):
    """
    示例功能页面类
    """
    # 元素定位器
    EXAMPLE_BUTTON = "com.aeke.fitnessmirror:id/example_button"
    EXAMPLE_TEXT = "com.aeke.fitnessmirror:id/example_text"
    
    def click_example_button(self):
        """
        点击示例按钮
        """
        self.click(self.EXAMPLE_BUTTON)
    
    def get_example_text(self):
        """
        获取示例文本
        
        Returns:
            示例文本
        """
        return self.get_text(self.EXAMPLE_TEXT)
    
    def is_example_page_displayed(self):
        """
        检查示例页面是否显示
        
        Returns:
            bool: 示例页面是否显示
        """
        return self.is_displayed(self.EXAMPLE_BUTTON)
