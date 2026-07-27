# -*- coding: utf-8 -*-
"""
报告数据构建：性能、Kea2、门禁状态合并。
"""
import glob
import json
import os

from orchestrator.kea2_result_parser import kea2_exit_failed, parse_kea2_output


def duration_str_from_seconds(total_seconds):
    total_seconds = int(total_seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    if hours > 0:
        return f"{hours}小时{minutes}分{seconds}秒"
    if minutes > 0:
        return f"{minutes}分{seconds}秒"
    return f"{seconds}秒"


def load_performance_data(performance_dir):
    if not os.path.isdir(performance_dir):
        return None, None
    # performance_summary_*.json 也会匹配 performance_*.json，需排除
    performance_files = [
        p
        for p in glob.glob(os.path.join(performance_dir, "performance_*.json"))
        if "summary" not in os.path.basename(p)
    ]
    summary_files = glob.glob(os.path.join(performance_dir, "performance_summary_*.json"))
    performance_data = None
    performance_summary = None
    if performance_files:
        latest = max(performance_files, key=os.path.getmtime)
        try:
            with open(latest, "r", encoding="utf-8") as f:
                performance_data = json.load(f)
        except Exception:
            pass
    if summary_files:
        latest_summary = max(summary_files, key=os.path.getmtime)
        try:
            with open(latest_summary, "r", encoding="utf-8") as f:
                performance_summary = json.load(f)
        except Exception:
            pass
    return performance_data, performance_summary


def normalize_performance_samples(performance_data):
    """将性能时序数据规范为 list[dict]。"""
    if not performance_data:
        return []
    if isinstance(performance_data, list):
        return [row for row in performance_data if isinstance(row, dict)]
    if isinstance(performance_data, dict):
        for key in ("samples", "data", "records"):
            nested = performance_data.get(key)
            if isinstance(nested, list):
                return [row for row in nested if isinstance(row, dict)]
    return []


def build_phase_performance(performance_data):
    """按 phase 字段分桶统计 CPU/内存/FPS。"""
    rows = normalize_performance_samples(performance_data)
    if not rows:
        return {}

    buckets = {}
    for row in rows:
        phase = row.get("phase") or "default"
        buckets.setdefault(phase, []).append(row)

    def stats(vals, key):
        nums = sorted(float(d.get(key) or 0) for d in vals if float(d.get(key) or 0) > 0)
        if not nums:
            return {"min": 0, "max": 0, "avg": 0, "p95": 0, "samples": 0}
        p95_idx = max(0, int(len(nums) * 0.95) - 1)
        return {
            "min": round(min(nums), 2),
            "max": round(max(nums), 2),
            "avg": round(sum(nums) / len(nums), 2),
            "p95": round(nums[p95_idx], 2),
            "samples": len(nums),
        }

    out = {}
    for phase, rows in buckets.items():
        out[phase] = {
            "cpu": stats(rows, "cpu"),
            "mem": stats(rows, "mem"),
            "fps": stats(rows, "fps"),
        }
    return out


def compute_gate_status(report_data):
    """
    计算 Jenkins / 报告门禁状态。
    """
    reasons = []
    crash_count = report_data.get("crash_count") or 0
    if crash_count > 0:
        reasons.append(f"崩溃 {crash_count} 次")

    kea2 = report_data.get("kea2")
    if kea2 is not None and kea2.get("error_message"):
        reasons.append(kea2.get("error_message"))
    if kea2 is not None and kea2_exit_failed(kea2.get("exit_code", 0)):
        if not any("Kea2" in r for r in reasons):
            reasons.append(f"Kea2 退出码 {kea2.get('exit_code')}")
    if kea2 is not None:
        pv = kea2.get("property_violation_count") or len(kea2.get("property_violations") or [])
        if pv > 0:
            reasons.append(f"属性违反 {pv} 次")

    baseline = report_data.get("baseline_comparison") or {}
    if baseline.get("has_regression"):
        reasons.extend(baseline.get("regressions") or ["性能基线回归"])

    leak = report_data.get("memory_leak_analysis") or {}
    if leak.get("suspected"):
        reasons.append("疑似内存泄漏")

    passed = len(reasons) == 0
    return {"passed": passed, "reasons": reasons}


def load_kea2_from_output_dir(output_dir):
    kea2_dir = os.path.join(output_dir, "kea2")
    meta_file = os.path.join(output_dir, "kea2_run_meta.json")
    if not os.path.isdir(kea2_dir) and not os.path.isfile(meta_file):
        return None
    exit_code = 4
    meta = {}
    if os.path.isfile(meta_file):
        try:
            with open(meta_file, "r", encoding="utf-8") as f:
                meta = json.load(f)
            exit_code = meta.get("exit_code", 4)
        except Exception:
            pass
    kea2 = parse_kea2_output(
        kea2_dir, exit_code, error_message=meta.get("error_message", "")
    )
    kea2["running_minutes"] = meta.get("running_minutes")
    return kea2


def build_report_data(
    config,
    output_meta,
    crashes,
    log_analysis,
    performance_data,
    performance_summary,
    performance_monitor,
    report_generator,
    kea2_result=None,
):
    crash_count = len(crashes)
    engine = output_meta.get("test_engine") or config.TEST_ENGINE
    execution_count = output_meta.get(
        "execution_count",
        config.EVENT_COUNT if engine == "monkey" else config.KEA2_RUNNING_MINUTES,
    )
    execution_label = output_meta.get(
        "execution_label",
        f"{config.EVENT_COUNT} 事件" if engine == "monkey" else f"{config.KEA2_RUNNING_MINUTES} 分钟",
    )

    report_data = {
        "test_engine": engine,
        "device_id": config.DEVICE_ID,
        "package_name": config.PACKAGE_NAME,
        "device_version_name": output_meta.get("device_version_name", config.DeviceVersionName),
        "firmware_version": output_meta.get("firmware_version", config.FirmwareVersion),
        "start_time": output_meta.get("start_time", "N/A"),
        "end_time": output_meta.get("end_time", "N/A"),
        "duration": output_meta.get("duration", "N/A"),
        "seed_value": config.SEED,
        "execution_count": execution_count,
        "execution_label": execution_label,
        "crash_count": crash_count,
        "crashes": crashes,
        "log_analysis": log_analysis,
        "performance_data": performance_data,
        "performance_summary": performance_summary,
        "performance_thresholds": performance_monitor.get_thresholds() if performance_monitor else {},
        "memory_leak_analysis": (
            performance_monitor.get_leak_analysis() if performance_monitor else {}
        ),
        "performance_baseline": report_generator.baseline,
        "phase_performance": build_phase_performance(performance_data),
        "kea2": kea2_result,
        "scenarios": output_meta.get("scenarios"),
        "details": output_meta.get("details", ""),
    }

    if not report_data["details"]:
        if engine == "kea2":
            pv = (kea2_result or {}).get("property_violation_count", 0)
            report_data["details"] = (
                f"Kea2 稳定性测试完成，运行 {config.KEA2_RUNNING_MINUTES} 分钟，"
                f"属性违反 {pv} 次，崩溃 {crash_count} 次。"
            )
        else:
            report_data["details"] = (
                f"Monkey 测试执行完成，共执行 {config.EVENT_COUNT} 个事件，"
                f"检测到 {crash_count} 个崩溃事件。"
            )

    return report_data


def finalize_report_data(report_data, report_generator):
    """应用基线对比并计算门禁。"""
    report_data = dict(report_data)
    report_generator._apply_baseline_comparison(report_data)
    report_data["gate_status"] = compute_gate_status(report_data)
    return report_data
