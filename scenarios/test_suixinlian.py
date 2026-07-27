# -*- coding: utf-8 -*-
"""随心练场景稳定性属性测试。"""
from kea2 import precondition, prob, max_tries

from scenarios.base_property import FitnessMirrorPropertyTest


class SuixinlianTest(FitnessMirrorPropertyTest):

    @prob(0.7)
    @max_tries(3)
    @precondition(lambda self: self.on_main_page())
    def test_enter_suixinlian_stable(self):
        self.set_perf_phase("suixinlian")
        page = self.main_page()
        page.go_to_suixinlian()
        self.d.sleep(2)
        # 离开主页后界面应仍有可交互内容（训练页/列表）
        assert self.d(className="android.widget.FrameLayout").exists(timeout=10)
        self.press_back_to_main()
