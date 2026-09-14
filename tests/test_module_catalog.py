# -*- coding: utf-8 -*-
"""module_catalog 白名单并集与场景解析测试。"""

import os
import tempfile

from orchestrator.module_catalog import (
    MAIN,
    activity_to_unique_pages,
    normalize_module_name,
    page_ids_modeled,
    resolve_lock_modules,
    resolve_lock_modules_from_config,
    whitelist_activities_for_modules,
    write_awl_strings,
)
from settings.config import Config


class TestModuleCatalog:
    def test_normalize_aliases(self):
        assert normalize_module_name("suixinlian") == "suixinlian"
        assert normalize_module_name("test_course.py") == "course"
        assert normalize_module_name("aicoach") == "ai_coach"

    def test_resolve_lock_modules_all_is_none(self):
        assert resolve_lock_modules(None) is None
        assert resolve_lock_modules([]) is None
        config = Config(test_engine="kea2")
        config.set_scenario_filter("all")
        assert resolve_lock_modules_from_config(config) is None

    def test_resolve_lock_modules_multi(self):
        mods = resolve_lock_modules(["course", "suixinlian", "course"])
        assert mods == ["course", "suixinlian"]

    def test_whitelist_union_includes_main(self):
        acts = whitelist_activities_for_modules(["course", "suixinlian"])
        assert MAIN in acts
        joined = "\n".join(acts)
        assert "CourseListActivity" in joined
        assert "ActionEditIndexActivity" in joined

    def test_write_awl_strings(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_awl_strings(tmp, [MAIN, "com.aeke.fitnessmirror.course.CourseListActivity"])
            assert path.endswith("awl.strings")
            lines = open(path, encoding="utf-8").read().strip().splitlines()
            assert MAIN in lines

    def test_activity_unique_pages_vs_shared_main(self):
        course_act = "com.aeke.fitnessmirror.course.CourseListActivity"
        assert "Course" in activity_to_unique_pages(course_act)
        # MainActivity 为共享，不直接映射业务页
        assert activity_to_unique_pages(MAIN) == []

    def test_page_ids_modeled_filtered_by_module(self):
        all_ids = page_ids_modeled(None)
        course_ids = page_ids_modeled(["course"])
        assert "Course" in course_ids
        assert len(course_ids) < len(all_ids)
        assert "Lifestyle" not in course_ids
