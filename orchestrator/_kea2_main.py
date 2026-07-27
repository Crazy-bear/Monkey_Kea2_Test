# -*- coding: utf-8 -*-
"""
Kea2 CLI 入口包装。
- python -B：避免 site-packages 写 __pycache__ 权限问题
- 预置项目根到 sys.path：unittest discover 只加入 scenarios/，场景脚本需 import pages 等
"""
import os
import sys


def _ensure_project_root_on_path():
    root = os.path.abspath(os.getcwd())
    if root not in sys.path:
        sys.path.insert(0, root)


_ensure_project_root_on_path()

from kea2.cli import main

if __name__ == "__main__":
    raise SystemExit(main() or 0)
