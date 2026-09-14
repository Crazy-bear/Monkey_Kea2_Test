# -*- coding: utf-8 -*-
"""
模块锁占位脚本（文件名故意不用 test_ 前缀，避免 --scenarios all 的 test_*.py 加载）。

用于 settings / profile / schedule 等属性哨兵已归档的模块：
仍可通过 --scenarios settings 解析锁模块并加载基类围栏（recover / pull）。
"""
from scenarios.base_property import FitnessMirrorPropertyTest


class LockFenceOnly(FitnessMirrorPropertyTest):
    """无额外抽检；依赖基类 test_recover_session / test_pull_to_locked_module。"""
    pass
