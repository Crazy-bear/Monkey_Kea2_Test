# -*- coding: utf-8 -*-
"""
确保 Kea2 项目已初始化（项目根目录存在 configs/ 目录）。
Kea2 CLI 从 cwd 向上查找 configs/，未找到则立即退出。
"""
import os
import subprocess
import sys
from pathlib import Path

from settings.logging_config import logger


def build_kea2_subprocess_env(project_root=None):
    """
    Kea2 子进程环境：禁止写 pyc，并将项目根加入 PYTHONPATH。
    unittest discover 仅把 scenarios/ 加入 sys.path，场景脚本中的
    `from scenarios.*` / `from pages.*` 依赖项目根在 PYTHONPATH 中。
    """
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    if project_root:
        root = os.path.abspath(project_root)
        prev = env.get("PYTHONPATH", "")
        if prev:
            parts = [p for p in prev.split(os.pathsep) if p and os.path.abspath(p) != root]
            env["PYTHONPATH"] = os.pathsep.join([root] + parts)
        else:
            env["PYTHONPATH"] = root
    return env


def _kea2_subprocess_env(project_root=None):
    return build_kea2_subprocess_env(project_root)


def _kea2_executable():
    import shutil
    wrapper = Path(__file__).parent / "_kea2_main.py"
    if wrapper.is_file():
        return [sys.executable, "-B", str(wrapper)]
    exe = shutil.which("kea2")
    if exe:
        return [exe]
    scripts = Path(sys.executable).parent / "Scripts" / "kea2.exe"
    return [str(scripts)] if scripts.is_file() else ["kea2"]


def _patch_kea2_config_sync_bug(configs_dir):
    """
    规避 Kea2 version_manager 缺陷：assets/fastbot_configs/__pycache__ 会被当作
    「新配置文件」用 shutil.copy2 复制，在 site-packages 只读时会 PermissionError。
    在本地 configs/ 预建 __pycache__ 目录即可跳过该复制。
    """
    os.makedirs(os.path.join(configs_dir, "__pycache__"), exist_ok=True)


def ensure_kea2_project_ready(project_root):
    """
    若 configs/ 不存在则执行 kea2 init。

    Returns:
        (bool, str): 是否就绪，错误信息
    """
    configs_dir = os.path.join(project_root, "configs")
    if not os.path.isdir(configs_dir):
        logger.info("未检测到 configs/，正在执行 kea2 init ...")
        try:
            proc = subprocess.run(
                [*_kea2_executable(), "init"],
                cwd=project_root,
                shell=False,
                capture_output=True,
                text=True,
                env=_kea2_subprocess_env(project_root),
            )
            if proc.returncode != 0 and not os.path.isdir(configs_dir):
                err = (proc.stderr or proc.stdout or "").strip()
                return False, err or "kea2 init 失败"
        except FileNotFoundError:
            return False, "未找到 kea2 命令，请 pip install kea2-python"

    if not os.path.isdir(configs_dir):
        return False, "Kea2 项目未初始化，请在项目根目录执行: kea2 init"

    _patch_kea2_config_sync_bug(configs_dir)
    return True, ""


def generate_kea2_native_report(project_root, kea2_output_dir):
    """调用 kea2 report 生成 Kea2 原生 HTML 报告（若产出目录存在）。"""
    if not kea2_output_dir or not os.path.isdir(kea2_output_dir):
        return None
    try:
        proc = subprocess.run(
            [*_kea2_executable(), "report", "-p", kea2_output_dir],
            cwd=project_root,
            shell=False,
            capture_output=True,
            text=True,
            env=_kea2_subprocess_env(project_root),
        )
        if proc.returncode == 0:
            logger.info("Kea2 原生报告已生成")
            return proc.stdout.strip() or kea2_output_dir
        logger.warning(f"kea2 report 未成功: {(proc.stderr or proc.stdout or '').strip()}")
    except Exception as e:
        logger.warning(f"kea2 report 异常: {e}")
    return None
