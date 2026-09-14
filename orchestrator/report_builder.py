# -*- coding: utf-8 -*-
"""
报告数据构建：性能、Kea2、门禁状态合并。
"""
import glob
import json
import os

from orchestrator.kea2_result_parser import (
    format_kea2_exit_code,
    kea2_exit_code_meaning,
    load_page_coverage,
    parse_kea2_output,
    extract_fastbot_seed,
)
from orchestrator.perf_context import (
    annotate_performance_with_coverage,
    build_anomaly_hotspots,
    build_path_investigations,
    build_path_performance,
    build_path_problem_verdict,
)
from orchestrator.report_verdict import (
    build_executive_verdict,
    compute_gate_status,
    enrich_bug_report_links,
    sanitize_performance_samples,
)


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


_BLANK_META = frozenset({None, "", "N/A", "Unknown", "未知", "—", "N/A (report-only)"})


def is_blank_meta(value):
    """版本/设备等字段是否视为未取到（含 Unknown）。"""
    if value is None:
        return True
    if isinstance(value, str) and value.strip() in _BLANK_META:
        return True
    return value in _BLANK_META


def first_good_meta(*values, default="N/A"):
    """按优先级取第一个有效元数据值。"""
    for value in values:
        if not is_blank_meta(value):
            return value
    return default


def _load_kea2_options(output_dir):
    """从 kea2/res_*/options.json 回填 serial / throttle。"""
    kea2_dir = os.path.join(output_dir, "kea2")
    if not os.path.isdir(kea2_dir):
        return {}
    options = {}
    for name in sorted(os.listdir(kea2_dir), reverse=True):
        path = os.path.join(kea2_dir, name, "options.json")
        if not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                options = json.load(f) or {}
            break
        except Exception:
            continue
    meta = {}
    serial = options.get("serial")
    if not is_blank_meta(serial):
        meta["device_id"] = serial
    pkgs = options.get("packageNames") or []
    if isinstance(pkgs, list) and pkgs:
        meta["package_name"] = pkgs[0]
    throttle = options.get("throttle")
    if throttle is not None and str(throttle).strip() != "":
        meta["throttle_ms"] = throttle
    return meta


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


def attach_path_performance(report_data, run_output_dir=None, coverage_samples=None):
    """
    将性能样本对齐到业务页/Activity，生成路径聚合与异常热点。
    优先使用样本自带 page/activity；缺失时用 coverage_pages.json as-of join 回填。
    """
    rows = normalize_performance_samples(report_data.get("performance_data"))
    if not rows:
        report_data["path_performance"] = []
        report_data["path_problem_verdict"] = build_path_problem_verdict([])
        report_data["path_investigations"] = []
        report_data["perf_anomaly_hotspots"] = []
        return report_data

    samples = coverage_samples
    if samples is None and run_output_dir:
        samples = (load_page_coverage(run_output_dir) or {}).get("samples") or []
    annotated = annotate_performance_with_coverage(rows, samples or [])
    annotated = sanitize_performance_samples(
        annotated, thresholds=report_data.get("performance_thresholds") or {}
    )
    report_data["performance_data"] = annotated
    report_data["path_performance"] = build_path_performance(annotated)
    report_data["path_problem_verdict"] = build_path_problem_verdict(
        report_data["path_performance"]
    )
    report_data["path_investigations"] = build_path_investigations(
        report_data["path_performance"]
    )
    report_data["perf_anomaly_hotspots"] = []
    report_data["perf_anomaly_hotspots_debug"] = build_anomaly_hotspots(annotated, limit=20)
    report_data["phase_performance"] = build_phase_performance(annotated)
    return report_data


def _try_load_auto_baseline(run_output_dir):
    """尝试加载 outputs/latest/perf_baseline.json 作为对比基线。"""
    if not run_output_dir:
        return None
    candidates = [
        os.path.join(run_output_dir, "perf_baseline.json"),
        os.path.join(os.path.dirname(run_output_dir.rstrip("\\/")), "latest", "perf_baseline.json"),
    ]
    for path in candidates:
        if not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and ("cpu" in data or "mem" in data or "fps" in data):
                return data
        except Exception:
            continue
    return None


def _write_auto_baseline(run_output_dir, performance_data, performance_summary=None):
    """把本场有效性能摘要写入 latest，供下次对比。"""
    if not run_output_dir:
        return
    rows = sanitize_performance_samples(normalize_performance_samples(performance_data))
    if not rows and not performance_summary:
        return

    def _stats(key, valid_fps_only=False):
        vals = []
        for d in rows:
            if valid_fps_only and d.get("fps_invalid"):
                continue
            try:
                v = float(d.get(key) or 0)
            except (TypeError, ValueError):
                continue
            if v > 0:
                vals.append(v)
        if not vals and isinstance(performance_summary, dict):
            block = performance_summary.get(key) or {}
            return {
                "avg": block.get("avg", 0),
                "p95": block.get("p95", 0),
            }
        if not vals:
            return {"avg": 0, "p95": 0}
        vals = sorted(vals)
        p95_idx = max(0, int(len(vals) * 0.95) - 1)
        return {
            "avg": round(sum(vals) / len(vals), 2),
            "p95": round(vals[p95_idx], 2),
        }

    payload = {
        "cpu": _stats("cpu"),
        "mem": _stats("mem"),
        "fps": _stats("fps", valid_fps_only=True),
        "source_run": os.path.basename(run_output_dir.rstrip("\\/")),
    }
    latest_dir = os.path.join(os.path.dirname(run_output_dir.rstrip("\\/")), "latest")
    for target_dir in (run_output_dir, latest_dir):
        try:
            os.makedirs(target_dir, exist_ok=True)
            with open(os.path.join(target_dir, "perf_baseline.json"), "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
        except OSError:
            pass


# 旧 compute_gate_status 已迁移至 report_verdict.compute_gate_status



def _duration_from_range(start_time, end_time):
    from datetime import datetime

    if not start_time or not end_time or start_time == "N/A" or end_time == "N/A":
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f"):
        try:
            start = datetime.strptime(str(start_time), fmt)
            end = datetime.strptime(str(end_time), fmt)
            return duration_str_from_seconds(max(0, int((end - start).total_seconds())))
        except ValueError:
            continue
    return None


def load_report_only_meta(output_dir, config=None, kea2_result=None):
    """从已有输出目录回填报告元数据（设备/时长/版本等）。"""
    meta = {
        "run_output_dir": output_dir,
        "report_only": True,
        "details": "根据已有输出目录重新生成报告。",
    }
    run_meta_path = os.path.join(output_dir, "kea2_run_meta.json")
    run_meta = {}
    if os.path.isfile(run_meta_path):
        try:
            with open(run_meta_path, "r", encoding="utf-8") as f:
                run_meta = json.load(f) or {}
        except Exception:
            run_meta = {}

    if run_meta.get("running_minutes") is not None:
        mins = run_meta.get("running_minutes")
        meta["execution_count"] = mins
        meta["execution_label"] = f"{mins} 分钟"
    if run_meta.get("lock_modules") is not None:
        meta["lock_modules"] = run_meta.get("lock_modules")
    if run_meta.get("scenarios"):
        sc = run_meta.get("scenarios")
        meta["scenarios"] = ",".join(sc) if isinstance(sc, list) else str(sc)
    for key in (
        "device_id",
        "package_name",
        "device_version_name",
        "firmware_version",
        "seed_value",
        "throttle_ms",
        "command",
    ):
        if not is_blank_meta(run_meta.get(key)):
            meta[key] = run_meta.get(key)

    # Kea2 options.json：serial / package / throttle（历史跑次常缺 meta）
    for key, val in _load_kea2_options(output_dir).items():
        if key not in meta or is_blank_meta(meta.get(key)):
            meta[key] = val

    # Fastbot 真实 seed（优先于 config.SEED；历史跑次从 fastbot_*.log 回填）
    if is_blank_meta(meta.get("seed_value")):
        fb_seed = extract_fastbot_seed(
            os.path.join(output_dir, "kea2"),
            run_output_dir=output_dir,
        )
        if fb_seed:
            meta["seed_value"] = fb_seed
        elif kea2_result and not is_blank_meta(kea2_result.get("seed_value")):
            meta["seed_value"] = kea2_result.get("seed_value")

    # 性能时序推断起止
    perf_data, _ = load_performance_data(os.path.join(output_dir, "performance"))
    rows = normalize_performance_samples(perf_data)
    if rows:
        meta["start_time"] = rows[0].get("timestamp") or "N/A"
        meta["end_time"] = rows[-1].get("timestamp") or "N/A"
        dur = _duration_from_range(meta["start_time"], meta["end_time"])
        if dur:
            meta["duration"] = dur

    # 优先沿用同目录旧 report.json 中的设备字段（完整跑次写入）
    # 注意：Unknown 视为无效，避免挡住后续从设备重新读取
    for name in ("report.json",):
        path = os.path.join(output_dir, name)
        if not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                prev = json.load(f) or {}
        except Exception:
            prev = {}
        for key in (
            "device_id",
            "package_name",
            "device_version_name",
            "firmware_version",
            "start_time",
            "end_time",
            "duration",
            # seed 不从旧 report.json 回填：report-only 曾用当前 config.SEED 污染历史跑次
        ):
            val = prev.get(key)
            if is_blank_meta(val):
                continue
            if key not in meta or is_blank_meta(meta.get(key)):
                meta[key] = val

    if config is not None:
        if is_blank_meta(meta.get("device_id")):
            meta["device_id"] = getattr(config, "DEVICE_ID", None) or "N/A"
        if is_blank_meta(meta.get("package_name")):
            meta["package_name"] = getattr(config, "PACKAGE_NAME", None) or "N/A"
        # 版本缺失时连设备补读；不得用 setdefault 保留 Unknown
        if is_blank_meta(meta.get("device_version_name")):
            meta["device_version_name"] = getattr(config, "DeviceVersionName", None) or "Unknown"
        if is_blank_meta(meta.get("firmware_version")):
            meta["firmware_version"] = getattr(config, "FirmwareVersion", None) or "Unknown"

    if kea2_result and kea2_result.get("running_minutes") and "execution_label" not in meta:
        mins = kea2_result.get("running_minutes")
        meta["execution_count"] = mins
        meta["execution_label"] = f"{mins} 分钟"

    meta.setdefault("start_time", "N/A")
    meta.setdefault("end_time", "N/A")
    meta.setdefault("duration", "N/A")
    return meta


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
        kea2_dir,
        exit_code,
        error_message=meta.get("error_message", ""),
        run_output_dir=output_dir,
        lock_modules=meta.get("lock_modules"),
    )
    kea2["running_minutes"] = meta.get("running_minutes")
    if meta.get("lock_modules") is not None and kea2.get("lock_modules") is None:
        kea2["lock_modules"] = meta.get("lock_modules")
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
        "device_id": first_good_meta(
            output_meta.get("device_id"), getattr(config, "DEVICE_ID", None), default="N/A"
        ),
        "package_name": first_good_meta(
            output_meta.get("package_name"), getattr(config, "PACKAGE_NAME", None), default="N/A"
        ),
        "device_version_name": first_good_meta(
            output_meta.get("device_version_name"),
            getattr(config, "DeviceVersionName", None),
            default="Unknown",
        ),
        "firmware_version": first_good_meta(
            output_meta.get("firmware_version"),
            getattr(config, "FirmwareVersion", None),
            default="Unknown",
        ),
        "start_time": output_meta.get("start_time", "N/A"),
        "end_time": output_meta.get("end_time", "N/A"),
        "duration": output_meta.get("duration", "N/A"),
        "seed_value": (
            first_good_meta(output_meta.get("seed_value"), default="N/A")
            if output_meta.get("report_only")
            else first_good_meta(
                output_meta.get("seed_value"), getattr(config, "SEED", None), default="N/A"
            )
        ),
        "throttle_ms": output_meta.get("throttle_ms"),
        "execution_count": execution_count,
        "execution_label": execution_label,
        "crash_count": crash_count,
        "crashes": crashes,
        "log_analysis": log_analysis,
        "performance_data": performance_data,
        "performance_summary": performance_summary,
        "performance_thresholds": performance_monitor.get_thresholds() if performance_monitor else (
            (performance_summary or {}).get("thresholds") or {}
        ),
        "memory_leak_analysis": (
            performance_monitor.get_leak_analysis()
            if performance_monitor
            else ((performance_summary or {}).get("memory_leak") or {})
        ),
        "performance_baseline": report_generator.baseline,
        "phase_performance": build_phase_performance(performance_data),
        "path_performance": [],
        "perf_anomaly_hotspots": [],
        "run_output_dir": output_meta.get("run_output_dir"),
        "kea2": kea2_result,
        "scenarios": output_meta.get("scenarios"),
        "lock_modules": output_meta.get("lock_modules"),
        "details": output_meta.get("details", ""),
    }

    if not report_data["details"]:
        if engine == "kea2":
            pv = (kea2_result or {}).get("property_violation_count", 0)
            exp = (kea2_result or {}).get("exploration") or {}
            act_n = exp.get("tested_activities_count")
            act_part = (
                f"，探索 Activity {act_n}/{exp.get('total_activities_count') or '?'}"
                if act_n is not None
                else ""
            )
            pages = exp.get("business_pages_seen") or []
            page_part = f"，业务页 {len(pages)} 个" if pages or act_n is not None else ""
            report_data["details"] = (
                f"Kea2 稳定性测试完成，运行 {config.KEA2_RUNNING_MINUTES} 分钟，"
                f"属性违反 {pv} 次，崩溃 {crash_count} 次{act_part}{page_part}。"
            )
        else:
            report_data["details"] = (
                f"Monkey 测试执行完成，共执行 {config.EVENT_COUNT} 个事件，"
                f"检测到 {crash_count} 个崩溃事件。"
            )

    return report_data


def finalize_report_data(report_data, report_generator, run_output_dir=None):
    """应用基线对比、路径性能对齐、原生报告元信息并计算分层门禁。"""
    report_data = dict(report_data)
    kea2 = report_data.get("kea2")
    if isinstance(kea2, dict) and "exit_code" in kea2:
        kea2 = dict(kea2)
        code = kea2.get("exit_code")
        kea2.setdefault("exit_code_meaning", kea2_exit_code_meaning(code))
        kea2.setdefault("exit_code_label", format_kea2_exit_code(code))
        report_data["kea2"] = kea2
    out_dir = run_output_dir or report_data.get("run_output_dir")

    # 自动基线：无显式 baseline 时尝试加载上次 latest
    if not report_data.get("performance_baseline") and not getattr(
        report_generator, "baseline", None
    ):
        auto_base = _try_load_auto_baseline(out_dir)
        if auto_base:
            report_data["performance_baseline"] = auto_base

    attach_path_performance(report_data, run_output_dir=out_dir)
    enrich_bug_report_links(report_data)
    report_generator._apply_baseline_comparison(report_data)
    report_data["gate_status"] = compute_gate_status(report_data)
    report_data["executive_verdict"] = build_executive_verdict(report_data)

    _write_auto_baseline(
        out_dir,
        report_data.get("performance_data"),
        report_data.get("performance_summary"),
    )
    return report_data
