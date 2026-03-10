# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2025/1/10

主界面类
"""
from pages.base_page import BasePage


class MainPage(BasePage):
    """
    主界面类
    """
    # 元素定位器
    随心练_BUTTON = "com.aeke.fitnessmirror:id/suixinlian_button"
    精品课程_BUTTON = "com.aeke.fitnessmirror:id/jingpin_button"
    个人中心_BUTTON = "com.aeke.fitnessmirror:id/profile_button"
    运动计划_BUTTON = "com.aeke.fitnessmirror:id/plan_button"
    运动测评_BUTTON = "com.aeke.fitnessmirror:id/assessment_button"
    音乐_BUTTON = "com.aeke.fitnessmirror:id/music_button"
    K歌_BUTTON = "com.aeke.fitnessmirror:id/karaoke_button"
    使用指南_BUTTON = "com.aeke.fitnessmirror:id/guide_button"
    
    def go_to_suixinlian(self):
        """
        进入随心练页面
        """
        self.click(self.随心练_BUTTON)
    
    def go_to_jingpin_course(self):
        """
        进入精品课程页面
        """
        self.click(self.精品课程_BUTTON)
    
    def go_to_profile(self):
        """
        进入个人中心页面
        """
        self.click(self.个人中心_BUTTON)
    
    def go_to_plan(self):
        """
        进入运动计划页面
        """
        self.click(self.运动计划_BUTTON)
    
    def go_to_assessment(self):
        """
        进入运动测评页面
        """
        self.click(self.运动测评_BUTTON)
    
    def go_to_music(self):
        """
        进入音乐页面
        """
        self.click(self.音乐_BUTTON)
    
    def go_to_karaoke(self):
        """
        进入K歌页面
        """
        self.click(self.K歌_BUTTON)
    
    def go_to_guide(self):
        """
        进入使用指南页面
        """
        self.click(self.使用指南_BUTTON)
    
    def is_main_page_displayed(self):
        """
        检查主页面是否显示
        
        Returns:
            bool: 主页面是否显示
        """
        return self.is_displayed(self.随心练_BUTTON)
