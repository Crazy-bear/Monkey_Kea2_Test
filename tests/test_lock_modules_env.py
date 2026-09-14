# -*- coding: utf-8 -*-
"""模块锁在 Kea2 子进程中的可见性。"""

import os

from orchestrator.test_session import get_lock_modules, set_lock_modules
from orchestrator.module_catalog import KEA2_LOCK_MODULES_ENV


class TestLockModulesEnvFallback:
    def setup_method(self):
        set_lock_modules(None)
        os.environ.pop(KEA2_LOCK_MODULES_ENV, None)

    def teardown_method(self):
        set_lock_modules(None)
        os.environ.pop(KEA2_LOCK_MODULES_ENV, None)

    def test_prefers_in_process_over_env(self):
        os.environ[KEA2_LOCK_MODULES_ENV] = "lifestyle"
        set_lock_modules(["course"])
        assert get_lock_modules() == ["course"]

    def test_falls_back_to_env_in_subprocess_style(self):
        set_lock_modules(None)
        os.environ[KEA2_LOCK_MODULES_ENV] = "course,suixinlian"
        assert get_lock_modules() == ["course", "suixinlian"]

    def test_none_when_unlocked(self):
        set_lock_modules(None)
        os.environ.pop(KEA2_LOCK_MODULES_ENV, None)
        assert get_lock_modules() is None
