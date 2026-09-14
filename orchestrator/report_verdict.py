# -*- coding: utf-8 -*-
"""
报告裁决层：门禁分层、首屏 Verdict、指标去噪、原生 bug_report 能力说明。
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

# gfxinfo 在无帧/reset 后常见占位低值（如 0.202…），不可当作真实卡顿
FPS_INVALID_BELOW = 1.0
MIN_PATH_SAMPLES_FOR_CRITICAL = 8


def sanitize_performance_samples(rows: List[dict], thresholds: Optional[dict] = None) -> List[dict]:
    """清洗性能样本：按当前阈值重算超标标记，并剔除无效 FPS 假卡顿。"""
    thr = thresholds or {}
    fps_thr = float(thr.get("fps") or 30.0)
    cpu_thr = thr.get("cpu")
    mem_thr = thr.get("mem")
    try:
        cpu_thr = float(cpu_thr) if cpu_thr is not None else None
    except (TypeError, ValueError):
        cpu_thr = None
    try:
        mem_thr = float(mem_thr) if mem_thr is not None else None
    except (TypeError, ValueError):
        mem_thr = None

    out = []
    for row in rows or []:
        r = dict(row)
        try:
            fps = float(r.get("fps") or 0)
        except (TypeError, ValueError):
            fps = 0.0
        invalid = fps <= 0 or fps < FPS_INVALID_BELOW
        r["fps_invalid"] = invalid
        if invalid:
            r["fps_low"] = False
            r["fps_valid_value"] = None
        else:
            r["fps_valid_value"] = fps
            r["fps_low"] = fps < fps_thr

        if cpu_thr is not None:
            try:
                r["cpu_exceed"] = float(r.get("cpu") or 0) > cpu_thr
            except (TypeError, ValueError):
                r["cpu_exceed"] = False
        if mem_thr is not None:
            try:
                r["mem_exceed"] = float(r.get("mem") or 0) > mem_thr
            except (TypeError, ValueError):
                r["mem_exceed"] = False
        out.append(r)
    return out


def inspect_kea2_bug_report(report_path: Optional[str]) -> Dict[str, Any]:
    """检查原生 bug_report 是否存在、是否含截图，以及能力边界。"""
    info = {
        "exists": False,
        "path": report_path or "",
        "relative_path": report_path or "",
        "has_screenshots": False,
        "screenshot_count": 0,
        "can_replace_unified_report": False,
        "role": "complement",
        "provides": [
            "Activity / Widget 覆盖趋势",
            "Property 执行统计",
            "Fastbot Crash/ANR 事件",
        ],
        "missing": [
            "CPU / Mem / FPS 时序与路径性能",
            "业务页停留与模块锁 dwell",
            "Logcat 分类崩溃（侧车）",
            "分层门禁 / 排查指引 / 环境指纹",
        ],
        "summary": "",
    }
    if not report_path or not os.path.isfile(report_path):
        info["summary"] = "本场未找到 Kea2 原生 bug_report.html"
        return info

    info["exists"] = True
    parent = os.path.dirname(report_path)
    pngs = []
    for root, _dirs, files in os.walk(parent):
        for name in files:
            if name.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                pngs.append(os.path.join(root, name))
    info["screenshot_count"] = len(pngs)
    info["has_screenshots"] = len(pngs) > 0
    # 统一报告不可被替代
    info["can_replace_unified_report"] = False
    if info["has_screenshots"]:
        info["summary"] = f"原生报告可用，含 {info['screenshot_count']} 张截图（属性失败/Crash 现场）"
    else:
        info["summary"] = "原生报告可用，但本场无截图（仅覆盖与 Property/Crash 统计）"
    return info


def compute_gate_status(report_data: dict) -> Dict[str, Any]:
    """
    分层门禁：
    - fail：Crash/ANR、Kea2 exit 2/3/4
    - warn：属性违反(exit1)、疑似泄漏、基线回归、路径性能告警
    - pass：无上述项
    """
    from orchestrator.kea2_result_parser import (
        format_kea2_exit_code,
        is_noisy_kea2_error,
        summarize_property_violations,
    )

    hard: List[str] = []
    soft: List[str] = []

    crash_count = report_data.get("crash_count") or 0
    if crash_count > 0:
        hard.append(f"崩溃 {crash_count} 次")

    kea2 = report_data.get("kea2")
    if kea2 is not None:
        code = kea2.get("exit_code", 0)
        label = kea2.get("exit_code_label") or format_kea2_exit_code(code)
        if code in (2, 3):
            hard.append(f"Kea2 退出码 {label}")
        elif code == 4:
            hard.append(f"Kea2 退出码 {label}")
        elif code == 1:
            soft.append(f"Kea2 退出码 {label}（属性哨兵，非 Crash）")

        if kea2.get("crash_detected") and not any("崩溃" in r for r in hard):
            hard.append("Kea2 检测到 Crash/ANR")

        pv = kea2.get("property_violation_count") or len(kea2.get("property_violations") or [])
        if pv > 0:
            summary = summarize_property_violations(kea2.get("property_violations") or [])
            soft.append((summary or f"属性违反 {pv} 次") + "（哨兵抽检，建议模块锁复核）")

        err = (kea2.get("error_message") or "").strip()
        if err and not is_noisy_kea2_error(err, exit_code=code):
            blob = hard + soft
            if not any(err == r or err in r or r in err for r in blob):
                if code in (2, 3, 4):
                    hard.append(err[:200])
                elif not err.startswith("属性违反") and "退出码" not in err:
                    soft.append(err[:200])

    baseline = report_data.get("baseline_comparison") or {}
    if baseline.get("has_regression"):
        soft.extend(baseline.get("regressions") or ["性能基线回归"])

    leak = report_data.get("memory_leak_analysis") or {}
    if leak.get("suspected"):
        growth = leak.get("total_growth_mb")
        soft.append(
            f"疑似内存泄漏"
            + (f"（增长 {growth} MB）" if growth is not None else "")
            + "（需模块锁加压确认）"
        )

    # 路径性能：仅样本充足的 critical 进 WARN
    for row in report_data.get("path_performance") or []:
        if row.get("is_unknown"):
            continue
        if row.get("risk_level") != "critical":
            continue
        if (row.get("samples") or 0) < MIN_PATH_SAMPLES_FOR_CRITICAL:
            soft.append(
                f"路径 {row.get('path')} 疑似 {row.get('primary_issue')}，但样本不足"
                f"（{row.get('samples')}），仅供参考"
            )
            continue
        soft.append(
            f"路径性能告警：{row.get('path')} — {row.get('primary_issue')}"
            f"（问题率 {row.get('issue_rate_pct', 0)}%）"
        )

    if hard:
        level = "fail"
    elif soft:
        level = "warn"
    else:
        level = "pass"

    return {
        "passed": level != "fail",  # CI 默认仅硬失败拦截
        "level": level,
        "reasons": hard + soft,  # 兼容旧字段
        "reasons_hard": hard,
        "reasons_soft": soft,
        "blocking": hard,
        "warnings": soft,
    }


def build_executive_verdict(report_data: dict) -> Dict[str, Any]:
    """首屏三句话：稳不稳 / 主风险 / 下一步。"""
    gate = report_data.get("gate_status") or {}
    level = gate.get("level") or ("pass" if gate.get("passed", True) else "fail")
    crash = report_data.get("crash_count") or 0
    kea2 = report_data.get("kea2") or {}
    pv = kea2.get("property_violation_count") or 0

    if level == "fail":
        stability = "不稳定（存在 Crash/运行失败，建议拦截发布）"
    elif level == "warn":
        stability = "基本可跑通，但有告警（属性哨兵/性能/泄漏需复核，默认不拦发布）"
    else:
        stability = "本场未发现硬性稳定性失败"

    # 主风险
    main_risk = "无"
    headlines = (report_data.get("path_problem_verdict") or {}).get("headlines") or []
    hard = gate.get("reasons_hard") or gate.get("blocking") or []
    soft = gate.get("reasons_soft") or gate.get("warnings") or []
    if hard:
        main_risk = hard[0]
    elif headlines and headlines[0].get("risk_level") in ("critical", "warn"):
        h = headlines[0]
        main_risk = f"{h.get('path')} — {h.get('primary_issue')}（问题率 {h.get('issue_rate_pct')}%）"
    elif soft:
        main_risk = soft[0]
    elif pv:
        main_risk = f"属性哨兵违反 {pv} 次"

    # 下一步
    next_step = "保持观察，可合入/提测"
    inv = report_data.get("path_investigations") or []
    if hard:
        next_step = "先查 Crash/ANR 与 Logcat，阻断发布直至硬失败清零"
    elif inv and inv[0].get("actions"):
        next_step = inv[0]["actions"][0]
    elif soft:
        next_step = "按告警项做模块锁加压或调阈值后复跑"

    return {
        "level": level,
        "stability": stability,
        "main_risk": main_risk,
        "next_step": next_step,
        "crash_count": crash,
        "property_violation_count": pv,
        "property_is_sentinel": True,
    }


def enrich_bug_report_links(report_data: dict) -> dict:
    """为报告补充原生 bug_report 元信息与相对链接。"""
    kea2 = report_data.get("kea2")
    if not isinstance(kea2, dict):
        return report_data
    path = kea2.get("report_path") or ""
    # 尽量转成相对 run_output_dir 的链接，便于本地打开
    run_dir = report_data.get("run_output_dir") or ""
    rel = path
    if path and run_dir:
        try:
            rel = os.path.relpath(path, run_dir)
        except ValueError:
            rel = path
    info = inspect_kea2_bug_report(path if path and os.path.isfile(path) else (
        os.path.join(run_dir, path) if run_dir and path else path
    ))
    # 若相对路径拼出来能找到
    if not info["exists"] and run_dir and path:
        cand = path if os.path.isabs(path) else os.path.join(run_dir, path)
        info = inspect_kea2_bug_report(cand)
        if info["exists"]:
            try:
                rel = os.path.relpath(cand, run_dir)
            except ValueError:
                rel = cand
    info["relative_path"] = rel.replace("\\", "/")
    kea2 = dict(kea2)
    kea2["bug_report_info"] = info
    report_data["kea2"] = kea2
    report_data["kea2_bug_report"] = info
    return report_data
