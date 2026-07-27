# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2025/1/10

基础页面类，提供通用方法，支持多种定位策略。
"""


def _resolve_selector(device, locator):
    """
    将定位器解析为 uiautomator2 选择器。

    Args:
        device: uiautomator2 设备实例
        locator: resourceId 字符串，或 {"type": "...", "value": "..."} 字典

    Returns:
        uiautomator2 元素对象
    """
    if isinstance(locator, dict):
        loc_type = locator.get("type", "resourceId")
        value = locator.get("value", "")
        if loc_type == "text":
            return device(text=value)
        if loc_type == "textContains":
            return device(textContains=value)
        if loc_type == "className":
            return device(className=value)
        if loc_type == "description":
            return device(description=value)
        return device(resourceId=value)
    return device(resourceId=locator)


class BasePage:
    """基础页面类"""

    def __init__(self, device):
        self.device = device

    def click(self, locator):
        _resolve_selector(self.device, locator).click()

    def send_keys(self, locator, text):
        _resolve_selector(self.device, locator).set_text(text)

    def get_text(self, locator):
        return _resolve_selector(self.device, locator).get_text()

    def is_displayed(self, locator):
        return _resolve_selector(self.device, locator).exists

    def wait_until_displayed(self, locator, timeout=10):
        return _resolve_selector(self.device, locator).wait(timeout=timeout)
