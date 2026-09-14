# -*- coding: utf-8 -*-
"""CoverageSampler 页面匹配夹具（不连设备）。"""

from unittest.mock import MagicMock

from orchestrator.coverage_sampler import CoverageSampler
from orchestrator.module_catalog import MAIN


class TestCoverageSamplerMatch:
    def test_unique_activity_maps_directly(self):
        sampler = CoverageSampler("dev", "out.json")
        d = MagicMock()
        page = sampler._match_page(
            d, "com.aeke.fitnessmirror.course.CourseListActivity"
        )
        assert page == "Course"

    def test_shared_main_requires_home_anchor(self):
        sampler = CoverageSampler("dev", "out.json")
        d = MagicMock()

        def exists_side_effect():
            return True

        # resourceId(...).exists
        node = MagicMock()
        node.exists = True
        d.side_effect = None
        d.return_value = node

        # d(resourceId=rid) → node
        def call_factory(**kwargs):
            rid = kwargs.get("resourceId", "")
            n = MagicMock()
            # Home 锚点
            n.exists = rid in (
                "com.aeke.fitnessmirror:id/tv_page_home",
                "com.aeke.fitnessmirror:id/grf_free_traing",
            )
            return n

        d.side_effect = None
        d.__call__ = MagicMock(side_effect=call_factory)

        # u2 device is called as d(resourceId=...)
        device = MagicMock()
        device.side_effect = call_factory

        page = sampler._match_page(device, MAIN)
        assert page == "Home"

    def test_shared_main_without_anchor_returns_none(self):
        sampler = CoverageSampler("dev", "out.json")
        device = MagicMock()

        def call_factory(**kwargs):
            n = MagicMock()
            n.exists = False
            return n

        device.side_effect = call_factory
        page = sampler._match_page(device, MAIN)
        assert page is None
