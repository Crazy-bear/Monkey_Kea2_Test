# -*- coding: utf-8 -*-
"""LogRotator 线程安全单元测试。"""

import os
import tempfile
import threading


class TestLogRotator:
    def test_concurrent_writes(self):
        from core.utils import LogRotator

        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "test.log")
            rotator = LogRotator(path, max_size=1024 * 1024)

            def writer(prefix):
                for i in range(100):
                    rotator.write(f"{prefix}-{i}\n")

            threads = [threading.Thread(target=writer, args=(f"t{t}",)) for t in range(5)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            rotator.close()
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            assert content.count("\n") == 500
