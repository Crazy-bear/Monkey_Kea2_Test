# -*- coding: utf-8 -*-
"""
性能样本的「操作路径」上下文：业务页 / Activity / 属性 phase。

- CoverageSampler 写 ui_context.json（当前页）
- 属性脚本经文件写 perf_phase.txt（跨 Kea2 子进程）
- PerformanceMonitor 采样时读取并打标
- 报告构建时也可对历史样本做 as-of join 回填
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

KEA2_PERF_PHASE_FILE_ENV = "KEA2_PERF_PHASE_FILE"
UI_CONTEXT_FILENAME = "ui_context.json"
PERF_PHASE_FILENAME = "perf_phase.txt"

_TS_FMT = "%Y-%m-%d %H:%M:%S"


def ui_context_path(output_dir: str) -> str:
    return os.path.join(output_dir, UI_CONTEXT_FILENAME)


def perf_phase_path(output_dir: str) -> str:
    return os.path.join(output_dir, PERF_PHASE_FILENAME)


def write_ui_context(path: str, page: Optional[str], activity: str, timestamp: str) -> None:
    payload = {
        "timestamp": timestamp,
        "page": page or "",
        "activity": activity or "",
    }
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)
    except OSError:
        pass


def read_ui_context(path: str) -> Dict[str, str]:
    if not path or not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return {}
        return {
            "timestamp": str(data.get("timestamp") or ""),
            "page": str(data.get("page") or ""),
            "activity": str(data.get("activity") or ""),
        }
    except (OSError, json.JSONDecodeError, TypeError):
        return {}


def write_perf_phase(path: str, name: str) -> None:
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write((name or "default").strip() or "default")
    except OSError:
        pass


def read_perf_phase(path: str) -> Optional[str]:
    if not path or not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read().strip()
        return text or None
    except OSError:
        return None


def resolve_phase_file() -> Optional[str]:
    return os.environ.get(KEA2_PERF_PHASE_FILE_ENV, "").strip() or None


def parse_perf_timestamp(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    for fmt in (_TS_FMT, "%Y-%m-%d %H:%M:%S.%f"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def _path_label(page: str, activity: str) -> str:
    page = (page or "").strip()
    activity = (activity or "").strip()
    if page:
        return page
    if activity:
        short = activity.rsplit(".", 1)[-1]
        return short or activity
    return "未识别"


def annotate_performance_with_coverage(
    performance_rows: List[dict],
    coverage_samples: List[dict],
) -> List[dict]:
    """按时间 as-of join：每个性能点取不晚于它的最近业务页采样。"""
    if not performance_rows:
        return []
    cov = []
    for row in coverage_samples or []:
        ts = parse_perf_timestamp(row.get("timestamp"))
        if ts is None:
            continue
        cov.append((ts, row))
    cov.sort(key=lambda x: x[0])

    out = []
    idx = -1
    for row in performance_rows:
        annotated = dict(row)
        ts = parse_perf_timestamp(row.get("timestamp"))
        if ts is not None and cov:
            while idx + 1 < len(cov) and cov[idx + 1][0] <= ts:
                idx += 1
            if idx >= 0:
                c = cov[idx][1]
                if not annotated.get("page"):
                    annotated["page"] = c.get("page") or ""
                if not annotated.get("activity"):
                    annotated["activity"] = c.get("activity") or ""
        annotated["path"] = _path_label(
            annotated.get("page") or "",
            annotated.get("activity") or "",
        )
        out.append(annotated)
    return out


def _metric_stats(rows: List[dict], key: str) -> Dict[str, float]:
    nums = sorted(float(d.get(key) or 0) for d in rows if float(d.get(key) or 0) > 0)
    if not nums:
        return {"min": 0.0, "max": 0.0, "avg": 0.0, "p95": 0.0, "samples": 0}
    p95_idx = max(0, int(len(nums) * 0.95) - 1)
    return {
        "min": round(min(nums), 2),
        "max": round(max(nums), 2),
        "avg": round(sum(nums) / len(nums), 2),
        "p95": round(nums[p95_idx], 2),
        "samples": len(nums),
    }


def build_path_performance(annotated_rows: List[dict]) -> List[dict]:
    """按业务路径聚合性能；输出问题率/主因，便于快速定位。"""
    buckets: Dict[str, List[dict]] = {}
    for row in annotated_rows or []:
        label = row.get("path") or _path_label(row.get("page") or "", row.get("activity") or "")
        buckets.setdefault(label, []).append(row)

    # 全场 Mem 超标占比：接近满额时视为阈值噪声，不作为路径主因
    all_rows = list(annotated_rows or [])
    global_mem_rate = (
        sum(1 for r in all_rows if r.get("mem_exceed")) / max(len(all_rows), 1)
        if all_rows
        else 0.0
    )
    mem_is_global = global_mem_rate >= 0.85

    result = []
    for path, rows in buckets.items():
        n = len(rows)
        cpu_ex = sum(1 for r in rows if r.get("cpu_exceed"))
        mem_ex = sum(1 for r in rows if r.get("mem_exceed"))
        # 无效 FPS（gfxinfo 无帧占位）不计入卡顿
        fps_low = sum(1 for r in rows if r.get("fps_low") and not r.get("fps_invalid"))
        invalid_fps_n = sum(1 for r in rows if r.get("fps_invalid"))
        bad_samples = sum(
            1
            for r in rows
            if r.get("cpu_exceed")
            or (r.get("mem_exceed") and not mem_is_global)
            or (r.get("fps_low") and not r.get("fps_invalid"))
        )
        differential = cpu_ex + fps_low + (0 if mem_is_global else mem_ex)
        cpu_rate = round(cpu_ex / max(n, 1), 3)
        mem_rate = round(mem_ex / max(n, 1), 3)
        fps_rate = round(fps_low / max(n, 1), 3)
        issue_rate = round(bad_samples / max(n, 1), 3)

        primary = _primary_issue(cpu_rate, mem_rate, fps_rate, mem_is_global)
        level = _path_risk_level(path, n, issue_rate, cpu_rate, fps_rate, differential)
        pages = sorted({(r.get("page") or "") for r in rows if r.get("page")})
        acts = sorted({(r.get("activity") or "") for r in rows if r.get("activity")})
        # FPS 统计仅用有效样本
        fps_rows = [r for r in rows if not r.get("fps_invalid")]
        result.append({
            "path": path,
            "page": pages[0] if len(pages) == 1 else (pages[0] if pages else ""),
            "pages": pages,
            "activities": acts[:3],
            "samples": n,
            "cpu": _metric_stats(rows, "cpu"),
            "mem": _metric_stats(rows, "mem"),
            "fps": _metric_stats(fps_rows, "fps"),
            "cpu_exceed_count": cpu_ex,
            "mem_exceed_count": mem_ex,
            "fps_low_count": fps_low,
            "fps_invalid_count": invalid_fps_n,
            "anomaly_count": cpu_ex + mem_ex + fps_low,
            "bad_samples": bad_samples,
            "anomaly_rate": issue_rate,
            "issue_rate": issue_rate,
            "issue_rate_pct": round(issue_rate * 100, 1),
            "cpu_rate_pct": round(cpu_rate * 100, 1),
            "mem_rate_pct": round(mem_rate * 100, 1),
            "fps_rate_pct": round(fps_rate * 100, 1),
            "differential_count": differential,
            "primary_issue": primary,
            "risk_level": level,
            "is_unknown": path in ("未识别", "unknown", ""),
            "mem_threshold_noisy": mem_is_global,
        })

    # 排序：已识别 > 风险高 > 差分问题多 > 样本多
    level_rank = {"critical": 0, "warn": 1, "watch": 2, "ok": 3, "noise": 4}
    result.sort(
        key=lambda r: (
            1 if r["is_unknown"] else 0,
            level_rank.get(r["risk_level"], 9),
            -r["differential_count"],
            -r["issue_rate"],
            -r["samples"],
        )
    )
    return result


def _primary_issue(cpu_rate, mem_rate, fps_rate, mem_is_global):
    ranked = []
    if fps_rate >= 0.3:
        ranked.append(("FPS卡顿", fps_rate))
    if cpu_rate >= 0.1:
        ranked.append(("CPU尖峰", cpu_rate))
    if mem_rate >= 0.5 and not mem_is_global:
        ranked.append(("内存偏高", mem_rate))
    if not ranked:
        if mem_is_global and mem_rate >= 0.5 and fps_rate < 0.3 and cpu_rate < 0.1:
            return "内存整体偏高(阈值偏严)"
        if fps_rate > 0:
            return "偶发FPS偏低"
        if cpu_rate > 0:
            return "偶发CPU偏高"
        return "无明显特有问题"
    ranked.sort(key=lambda x: -x[1])
    return ranked[0][0]


def _path_risk_level(path, samples, issue_rate, cpu_rate, fps_rate, differential):
    if path in ("未识别", "unknown", ""):
        return "noise"
    if samples < 3:
        return "watch"  # 样本太少，仅供参考
    # 样本不足时最高只给 warn，避免 4 个点标高危误导
    if samples < 8:
        if fps_rate >= 0.5 or cpu_rate >= 0.2:
            return "watch"
        if fps_rate >= 0.25 or cpu_rate >= 0.08:
            return "watch"
        return "ok"
    if fps_rate >= 0.5 or cpu_rate >= 0.2 or (differential >= 20 and issue_rate >= 0.6):
        return "critical"
    if fps_rate >= 0.25 or cpu_rate >= 0.08 or differential >= 8:
        return "warn"
    if issue_rate >= 0.3:
        return "watch"
    return "ok"


def build_path_problem_verdict(path_rows: List[dict], limit: int = 3) -> Dict[str, Any]:
    """报告顶部结论：一眼看出哪几条路径要跟。"""
    rows = path_rows or []
    known = [r for r in rows if not r.get("is_unknown")]
    noise = [r for r in rows if r.get("is_unknown")]
    problems = [r for r in known if r.get("risk_level") in ("critical", "warn")]
    mem_noisy = any(r.get("mem_threshold_noisy") for r in rows)

    headlines = []
    for r in problems[:limit]:
        headlines.append({
            "path": r["path"],
            "risk_level": r["risk_level"],
            "primary_issue": r.get("primary_issue") or "",
            "issue_rate_pct": r.get("issue_rate_pct", 0),
            "samples": r.get("samples", 0),
            "fps_avg": (r.get("fps") or {}).get("avg"),
            "cpu_avg": (r.get("cpu") or {}).get("avg"),
            "summary": (
                f"{r['path']}：{r.get('primary_issue')} "
                f"(问题率 {r.get('issue_rate_pct', 0)}%，样本 {r.get('samples', 0)})"
            ),
        })

    if not headlines and known:
        # 没有明显路径问题时给一句总览
        top = known[0]
        headlines.append({
            "path": top["path"],
            "risk_level": top.get("risk_level") or "ok",
            "primary_issue": top.get("primary_issue") or "",
            "issue_rate_pct": top.get("issue_rate_pct", 0),
            "samples": top.get("samples", 0),
            "fps_avg": (top.get("fps") or {}).get("avg"),
            "cpu_avg": (top.get("cpu") or {}).get("avg"),
            "summary": f"无明显高危路径；停留最多：{top['path']}",
        })

    noise_pct = 0.0
    total = sum(r.get("samples") or 0 for r in rows) or 1
    if noise:
        noise_pct = round(100.0 * sum(r.get("samples") or 0 for r in noise) / total, 1)

    return {
        "headlines": headlines,
        "problem_count": len(problems),
        "mem_threshold_noisy": mem_noisy,
        "unknown_sample_percent": noise_pct,
        "read_hint": (
            "先看「问题路径结论」与下方「排查指引」。"
            "Fastbot 随机探索无法按时间点逐步复现；应用模块锁定向加压验证。"
            "Mem 若几乎全场超标，请优先看 FPS/CPU。"
            + (f" 未识别样本约 {noise_pct}%，以已识别路径为准。" if noise_pct >= 20 else "")
        ),
    }


# 业务页 → --scenarios 别名（用于排查指引）
_PATH_TO_SCENARIO = {
    "Home": "home",
    "Lifestyle": "lifestyle",
    "Course": "course",
    "FreeWorkout": "suixinlian",
    "Assessment": "assessment",
    "AICoach": "ai_coach",
    "Programs": "programs",
}


def build_path_investigations(path_rows: List[dict], limit: int = 5) -> List[dict]:
    """
    把性能异常转成可执行排查项（替代无意义的时间线）。

    Fastbot 稳定性测试无法「按时间点复现」；正确做法是锁模块加压 + 看原生报告截图。
    """
    rows = [
        r for r in (path_rows or [])
        if not r.get("is_unknown") and r.get("risk_level") in ("critical", "warn", "watch")
    ]
    out = []
    for r in rows[:limit]:
        path = r.get("path") or ""
        scenario = _PATH_TO_SCENARIO.get(path) or _PATH_TO_SCENARIO.get(r.get("page") or "")
        primary = r.get("primary_issue") or ""
        actions = []
        if scenario:
            actions.append(
                f"模块锁复跑：python main.py --engine kea2 --scenarios {scenario} --running-minutes 20"
            )
        else:
            actions.append("在对应业务页停留后，用 --scenarios 锁定相近模块复跑加压")
        if "FPS" in primary:
            actions.append(
                "优先查该页动画/列表滑动/视频预览是否掉帧；"
                "打开原生 bug_report 看 Activity 覆盖与 Property 失败统计（有失败截图时会出现在对应条目下）"
            )
        elif "CPU" in primary:
            actions.append(
                "优先查该页进入瞬间的尖峰（网络回调、大图解码）；"
                "对照原生 bug_report 的 Activity/Property 区块"
            )
        elif "内存" in primary or "Mem" in primary:
            actions.append("若全场 Mem 都超，先核对 PERF_MEM_THRESHOLD；否则查该页图片缓存/泄漏")
        else:
            actions.append("打开 Kea2 原生 bug_report，查看 Activity 覆盖与 Property Checking Statistics")
        if (r.get("samples") or 0) < 5:
            actions.append("样本偏少，结论仅供参考；建议加长运行或模块锁后再判")

        acts = r.get("activities") or []
        out.append({
            "path": path,
            "risk_level": r.get("risk_level"),
            "primary_issue": primary,
            "issue_rate_pct": r.get("issue_rate_pct", 0),
            "samples": r.get("samples", 0),
            "fps_avg": (r.get("fps") or {}).get("avg"),
            "cpu_avg": (r.get("cpu") or {}).get("avg"),
            "mem_avg": (r.get("mem") or {}).get("avg"),
            "activities": acts,
            "scenario": scenario or "",
            "actions": actions,
            "why_not_timeline": (
                "随机探索无法用时间戳逐步复现；请用模块锁把压力打到该路径上验证。"
            ),
        })
    return out


def build_anomaly_hotspots(annotated_rows: List[dict], limit: int = 20) -> List[dict]:
    """保留兼容：默认不再作为主报告区块；仅供调试。"""
    hotspots = []
    for row in annotated_rows or []:
        path = row.get("path") or _path_label(row.get("page") or "", row.get("activity") or "")
        if path in ("未识别", "unknown", ""):
            continue  # 未对齐路径对复现无帮助
        flags = []
        if row.get("cpu_exceed"):
            flags.append("CPU超标")
        if row.get("mem_exceed"):
            flags.append("Mem超标")
        if row.get("fps_low"):
            flags.append("FPS低")
        if not flags:
            continue
        # 全场 Mem 噪声时，仅 Mem 超标的点跳过
        if flags == ["Mem超标"]:
            continue
        fps = row.get("fps")
        try:
            fps = round(float(fps), 1) if fps is not None else None
        except (TypeError, ValueError):
            pass
        hotspots.append({
            "timestamp": row.get("timestamp") or "",
            "path": path,
            "page": row.get("page") or "",
            "activity": row.get("activity") or "",
            "activity_short": (row.get("activity") or "").rsplit(".", 1)[-1],
            "phase": row.get("phase") or "default",
            "cpu": row.get("cpu"),
            "mem": row.get("mem"),
            "fps": fps,
            "flags": flags,
            "flag_text": " / ".join(flags),
        })
    hotspots.sort(key=lambda r: r.get("timestamp") or "")
    if limit and len(hotspots) > limit:
        step = max(1, len(hotspots) // limit)
        sampled = hotspots[::step][:limit]
        if hotspots and hotspots[-1] not in sampled:
            sampled[-1] = hotspots[-1]
        return sampled
    return hotspots
