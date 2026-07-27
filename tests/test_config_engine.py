# -*- coding: utf-8 -*-
"""Kea2 配置与引擎相关单元测试。"""


class TestConfigEngine:
    def test_default_engine_is_kea2(self):
        from settings.config import Config
        config = Config()
        assert config.TEST_ENGINE == "kea2"

    def test_validate_kea2_ok(self):
        from settings.config import Config
        config = Config(test_engine="kea2")
        ok, errors = config.validate(engine="kea2")
        assert ok, errors

    def test_validate_kea2_fails_no_scenarios(self):
        from settings.config import Config
        config = Config(test_engine="kea2")
        config.KEA2_SCENARIOS_DIR = "nonexistent_scenarios_dir"
        ok, errors = config.validate(engine="kea2")
        assert not ok

    def test_validate_monkey_pct(self):
        from settings.config import Config
        config = Config(test_engine="monkey")
        config.MONKEY_TOUCH_PERCENT = 50
        ok, errors = config.validate(engine="monkey")
        assert not ok

    def test_scenario_filter_aliases(self):
        from settings.config import Config
        config = Config()
        config.set_scenario_filter("suixinlian,course")
        patterns = config.get_scenario_patterns()
        assert "test_suixinlian.py" in patterns
        assert "test_course.py" in patterns

    def test_scenario_filter_all(self):
        from settings.config import Config
        config = Config()
        config.set_scenario_filter("all")
        assert config.get_scenario_patterns() == ["test_*.py"]
