# -*- coding: utf-8 -*-
"""
应用内控制栏场景稳定性属性测试 — v3.x UI。

定位见 pages/control_panel_page.py 与 S1Pro_UI/v3.0.0.6858/elements/Home_ControlPanel_*_elements.md。
"""
from kea2 import precondition, prob, max_tries

from scenarios.base_property import FitnessMirrorPropertyTest


class ControlPanelTest(FitnessMirrorPropertyTest):

    @prob(0.55)
    @max_tries(3)
    @precondition(lambda self: self.on_home_page())
    def test_open_control_panel(self):
        self.set_perf_phase("control_panel")
        panel = self.control_panel_page()
        assert panel.open_control_panel(), "无法打开应用内控制栏"
        for btn in panel.MENU_BUTTONS:
            assert panel.is_displayed(btn), f"控制栏菜单按钮不可见: {btn}"
        panel.dismiss_control_panel()

    @prob(0.5)
    @max_tries(3)
    @precondition(lambda self: self.on_home_page())
    def test_control_panel_wifi_tab(self):
        self.set_perf_phase("control_wifi")
        panel = self.control_panel_page()
        assert panel.switch_tab(panel.SYS_WIFI), "无法切换到 WiFi 面板"
        assert panel.is_wifi_panel_open(), "WiFi 面板未展开"
        panel.dismiss_control_panel()

    @prob(0.5)
    @max_tries(3)
    @precondition(lambda self: self.on_home_page())
    def test_control_panel_bluetooth_tab(self):
        self.set_perf_phase("control_bluetooth")
        panel = self.control_panel_page()
        assert panel.switch_tab(panel.SYS_BLE), "无法切换到蓝牙面板"
        assert panel.is_bluetooth_panel_open(), "蓝牙面板未展开"
        panel.dismiss_control_panel()

    @prob(0.45)
    @max_tries(3)
    @precondition(lambda self: self.on_home_page())
    def test_control_panel_brightness_tab(self):
        self.set_perf_phase("control_brightness")
        panel = self.control_panel_page()
        assert panel.switch_tab(panel.SYS_BRIGHT), "无法切换到亮度面板"
        assert panel.is_brightness_panel_open(), "亮度面板未展开"
        panel.dismiss_control_panel()

    @prob(0.45)
    @max_tries(3)
    @precondition(lambda self: self.on_home_page())
    def test_control_panel_volume_tab(self):
        self.set_perf_phase("control_volume")
        panel = self.control_panel_page()
        assert panel.switch_tab(panel.SYS_VOICE), "无法切换到音量面板"
        assert panel.is_volume_panel_open(), "音量面板未展开"
        panel.dismiss_control_panel()

    @prob(0.4)
    @max_tries(3)
    @precondition(lambda self: self.on_home_page())
    def test_control_panel_led_tab(self):
        self.set_perf_phase("control_led")
        panel = self.control_panel_page()
        assert panel.switch_tab(panel.SYS_LED), "无法切换到灯带面板"
        assert panel.is_led_panel_open(), "灯带面板未展开"
        panel.dismiss_control_panel()
