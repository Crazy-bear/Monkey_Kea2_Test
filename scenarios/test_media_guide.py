# -*- coding: utf-8 -*-
"""音乐 / K歌 / 使用指南场景。"""
from kea2 import precondition, prob, max_tries

from scenarios.base_property import FitnessMirrorPropertyTest


class MediaGuideTest(FitnessMirrorPropertyTest):

    @prob(0.5)
    @max_tries(3)
    @precondition(lambda self: self.on_main_page())
    def test_music_entry_stable(self):
        self.set_perf_phase("music")
        self.main_page().go_to_music()
        self.d.sleep(2)
        assert self.d(className="android.widget.FrameLayout").exists(timeout=10)
        self.press_back_to_main()

    @prob(0.5)
    @max_tries(3)
    @precondition(lambda self: self.on_main_page())
    def test_karaoke_entry_stable(self):
        self.set_perf_phase("karaoke")
        self.main_page().go_to_karaoke()
        self.d.sleep(2)
        assert self.d(className="android.widget.FrameLayout").exists(timeout=10)
        self.press_back_to_main()

    @prob(0.5)
    @max_tries(3)
    @precondition(lambda self: self.on_main_page())
    def test_guide_entry_stable(self):
        self.set_perf_phase("guide")
        self.main_page().go_to_guide()
        self.d.sleep(2)
        assert self.d(className="android.widget.FrameLayout").exists(timeout=10)
        self.press_back_to_main()
