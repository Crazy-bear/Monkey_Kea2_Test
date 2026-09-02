# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2025/1/10

基础页面类，提供通用方法，支持多种定位策略。
"""


def _text_selector(device, text):
    """
    构造 text 选择器。Kea2 将 @text 拼进 XPath 单引号字面量，含引号的文案会触发 XPathEvalError。
    """
    if not text:
        return device(text=text)
    if "'" in text or '"' in text:
        token = next((part for part in reversed(text.replace("'", " ").split()) if part), text)
        return device(textContains=token)
    return device(text=text)


def _is_static_checker_device(device):
    """Kea2 precondition 注入 U2StaticDevice，不可执行真实 UI 操作。"""
    try:
        from kea2.u2Driver import U2StaticDevice
        return isinstance(device, U2StaticDevice)
    except ImportError:
        return False


def _element_exists(selector, timeout=0):
    """
    兼容 uiautomator2 Exists 对象与 Kea2 StaticU2UiObject 的 bool exists 属性。
    """
    exists = selector.exists
    if isinstance(exists, bool):
        return exists
    if timeout:
        return exists(timeout=timeout)
    return bool(exists)


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
            return _text_selector(device, value)
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
        if _is_static_checker_device(self.device):
            return False
        _resolve_selector(self.device, locator).click()
        return True

    def send_keys(self, locator, text):
        if _is_static_checker_device(self.device):
            return False
        _resolve_selector(self.device, locator).set_text(text)
        return True

    def get_text(self, locator):
        return _resolve_selector(self.device, locator).get_text()

    def is_displayed(self, locator):
        return _element_exists(_resolve_selector(self.device, locator))

    def text_exists(self, text):
        """按文案判断元素是否存在（兼容含单引号的界面文案）。"""
        return _element_exists(_text_selector(self.device, text))

    def wait_until_displayed(self, locator, timeout=10):
        if _is_static_checker_device(self.device):
            return self.is_displayed(locator)
        return _resolve_selector(self.device, locator).wait(timeout=timeout)
