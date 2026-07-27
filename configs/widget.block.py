# -*- coding: utf-8 -*-
"""
Kea2 / Fastbot 控件黑名单（力量镜）。
Kea2 仅识别 global_block_widgets / global_block_tree 等函数，不使用 block_widgets 列表。
"""
from kea2.utils import Device


def global_block_widgets(d: "Device"):
    """全局禁止点击的控件（睡眠、折叠、系统危险操作等）。"""
    return [
        # 力量镜系统控制栏 — 误触会导致黑屏/休眠，测试中断
        d(text="Sleep"),
        d(text="睡眠"),
        d(textContains="Sleep"),
        d(text="Fold"),
        d(text="Retract rope"),
        d(text="收绳"),
        # 通用系统危险操作
        d(text="卸载"),
        d(text="清除数据"),
        d(text="强行停止"),
        d(text="恢复出厂设置"),
        d(text="Factory reset"),
        d(text="Uninstall"),
        d(text="Clear data"),
    ]


def global_block_tree(d: "Device"):
    """可选：整块屏蔽媒体/工具栏区域（若仍误触可取消注释并补充 xpath）。"""
    return []
