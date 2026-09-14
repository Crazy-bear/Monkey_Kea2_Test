# -*- coding: utf-8 -*-
"""
解析 Kea2 运行产物：result JSON、HTML 报告路径、属性违反、Activity 覆盖。
"""
import glob
import json
import os
import re

from orchestrator.module_catalog import (
    MAIN,
    MODULE_ACTIVITIES,
    BUSINESS_PAGES,
    activity_to_unique_pages,
    normalize_activity_name,
    page_ids_modeled,
)

DEFAULT_DWELL_OK_RATIO = 0.6

# Fastbot 日志：// Monkey: seed=1789026342304 count=1000
_FASTBOT_SEED_RE = re.compile(
    r"(?://\s*)?Monkey:\s*seed\s*=\s*(\d+)",
    re.IGNORECASE,
)


def extract_fastbot_seed(kea2_output_dir, run_output_dir=None):
    """
    从 Fastbot / logcat 日志提取真实探索 seed。

    Kea2 CLI 通常不透出 seed；实际值写在 fastbot_*.log 的 Monkey 行。
    返回 str 或 None。
    """
    search_roots = []
    if kea2_output_dir:
        search_roots.append(kea2_output_dir)
    if run_output_dir and run_output_dir not in search_roots:
        search_roots.append(run_output_dir)

    candidates = []
    for root in search_roots:
        if not root or not os.path.isdir(root):
            continue
        for pattern in (
            os.path.join(root, "**", "fastbot_*.log"),
            os.path.join(root, "fastbot_*.log"),
            os.path.join(root, "logcat*.log"),
            os.path.join(root, "**", "logcat*.log"),
        ):
            candidates.extend(glob.glob(pattern, recursive=True))

    # 优先 fastbot 日志，再 logcat；同类型取最新
    def _rank(path):
        name = os.path.basename(path).lower()
        pri = 0 if name.startswith("fastbot") else 1
        try:
            mtime = os.path.getmtime(path)
        except OSError:
            mtime = 0
        return (pri, -mtime)

    seen = set()
    for path in sorted(candidates, key=_rank):
        if path in seen:
            continue
        seen.add(path)
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                # seed 通常在文件前部
                head = f.read(256 * 1024)
        except OSError:
            continue
        match = _FASTBOT_SEED_RE.search(head)
        if match:
            return match.group(1)
    return None


def _page_id_to_module():
    return {p["id"]: p.get("module") for p in BUSINESS_PAGES}


def _activity_in_locked_modules(activity, lock_modules):
    act = normalize_activity_name(activity or "")
    if not act or act == MAIN or act.endswith(".MainActivity"):
        return False
    short = act.rsplit(".", 1)[-1]
    for mod in lock_modules:
        for a in MODULE_ACTIVITIES.get(mod, []):
            if a == MAIN or a.endswith(".MainActivity"):
                continue
            if a == act or a.endswith("." + short) or short == a.rsplit(".", 1)[-1]:
                return True
    return False


def _sample_in_locked_module(sample, lock_modules, page_to_mod):
    page = sample.get("page")
    if page and page_to_mod.get(page) in lock_modules:
        return True
    return _activity_in_locked_modules(sample.get("activity"), lock_modules)


def compute_in_module_sample_ratio(page_cov, lock_modules, dwell_threshold=DEFAULT_DWELL_OK_RATIO):
    """根据采样计算锁定模块内停留占比。无锁模块时返回 ratio=None。"""
    if not lock_modules:
        return {
            "in_module_sample_ratio": None,
            "in_module_sample_count": 0,
            "out_module_sample_count": 0,
            "dwell_ok": None,
            "dwell_threshold": dwell_threshold,
            "lock_modules": None,
        }
    page_to_mod = _page_id_to_module()
    samples = page_cov.get("samples") or []
    in_count = 0
    out_count = 0
    if samples:
        for s in samples:
            if _sample_in_locked_module(s, lock_modules, page_to_mod):
                in_count += 1
            else:
                out_count += 1
    else:
        # 无明细时用 page_hits 近似
        hits = page_cov.get("page_hits") or {}
        for page, n in hits.items():
            n = int(n or 0)
            if page_to_mod.get(page) in lock_modules:
                in_count += n
            else:
                out_count += n
    total = in_count + out_count
    ratio = round(100.0 * in_count / total, 2) if total else 0.0
    # 对外用 0~1 比例更利于平台；同时给 percent 便于展示
    ratio_01 = round(in_count / total, 4) if total else 0.0
    return {
        "in_module_sample_ratio": ratio_01,
        "in_module_sample_percent": ratio,
        "in_module_sample_count": in_count,
        "out_module_sample_count": out_count,
        "dwell_ok": (ratio_01 >= dwell_threshold) if total else False,
        "dwell_threshold": dwell_threshold,
        "lock_modules": list(lock_modules),
    }


def merge_exploration_coverage(activity_cov, page_cov, lock_modules=None):
    """合并 Activity 覆盖与业务页采样。"""
    tested = activity_cov.get("tested_activities") or []
    history = activity_cov.get("activity_count_history") or {}
    pages_from_act = []
    for act in tested:
        pages_from_act.extend(activity_to_unique_pages(act))
    pages_sampled = page_cov.get("pages_seen") or []
    pages_seen = sorted(set(pages_from_act) | set(pages_sampled))
    modeled = page_ids_modeled(lock_modules)
    pages_hit = [p for p in pages_seen if p in modeled]
    pages_missed = [p for p in modeled if p not in pages_hit]

    activities_table = []
    for act in tested:
        pages = activity_to_unique_pages(act)
        if not pages and (act == MAIN or str(act).endswith(".MainActivity")):
            pages = ["Home"]
        activities_table.append({
            "activity": act,
            "count": int(history.get(act, 0) or 0),
            "business_pages": pages or ["未建模"],
        })
    activities_table.sort(key=lambda r: (-r["count"], r["activity"]))

    total = activity_cov.get("total_activities_count") or 0
    tested_n = activity_cov.get("tested_activities_count") or len(tested)
    cov = activity_cov.get("coverage_percent")
    if cov is None and total:
        cov = round(100.0 * tested_n / total, 4)

    dwell = compute_in_module_sample_ratio(page_cov, lock_modules)

    return {
        "tested_activities": tested,
        "tested_activities_count": tested_n,
        "total_activities_count": total,
        "coverage_percent": cov,
        "activity_count_history": history,
        "activities_table": activities_table,
        "business_pages_seen": pages_hit,
        "business_pages_missed": pages_missed,
        "business_pages_modeled_count": len(modeled),
        "page_hits": page_cov.get("page_hits") or {},
        "page_sample_count": page_cov.get("sample_count") or 0,
        "lock_modules": dwell.get("lock_modules"),
        "in_module_sample_ratio": dwell.get("in_module_sample_ratio"),
        "in_module_sample_percent": dwell.get("in_module_sample_percent"),
        "in_module_sample_count": dwell.get("in_module_sample_count"),
        "out_module_sample_count": dwell.get("out_module_sample_count"),
        "dwell_ok": dwell.get("dwell_ok"),
        "dwell_threshold": dwell.get("dwell_threshold"),
    }


def _latest_file(pattern):
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def _extract_violations(data):
    """从 Kea2 result JSON 提取属性违反。

    兼容：
    - 标准 list：property_violations / violations
    - Kea2 实际格式：{test_name: {fail, error, executed, ...}, ...}
    - results 列表
    """
    violations = []
    if not isinstance(data, dict):
        return violations

    for key in ("propertyViolations", "property_violations", "violations"):
        items = data.get(key)
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    violations.append(item)
                else:
                    violations.append({"message": str(item)})
            return violations

    results = data.get("results") or data.get("testResults") or []
    if isinstance(results, list) and results:
        for r in results:
            if not isinstance(r, dict):
                continue
            if r.get("status") in ("FAIL", "fail", "failure") or r.get("failed"):
                violations.append({
                    "test": r.get("test") or r.get("name") or r.get("property"),
                    "message": r.get("message") or r.get("detail") or str(r),
                })
        if violations:
            return violations

    # Kea2 property summary map
    for name, info in data.items():
        if not isinstance(info, dict):
            continue
        if info.get("kind") not in (None, "property", "Property"):
            # 无 kind 时仍可能是属性行（含 fail/executed）
            if not any(k in info for k in ("fail", "error", "executed", "precond_satisfied")):
                continue
        fail = int(info.get("fail") or 0)
        error = int(info.get("error") or 0)
        if fail <= 0 and error <= 0:
            continue
        parts = []
        if fail:
            parts.append(f"fail×{fail}")
        if error:
            parts.append(f"error×{error}")
        executed = info.get("executed")
        if executed is not None:
            parts.append(f"executed={executed}")
        violations.append({
            "test": name,
            "message": "，".join(parts),
            "fail": fail,
            "error": error,
            "executed": executed,
        })
    return violations


def property_violation_total(violations):
    """属性违反总次数：优先累加 fail+error，否则按条数。"""
    if not violations:
        return 0
    total = 0
    has_count = False
    for v in violations:
        if not isinstance(v, dict):
            continue
        if "fail" in v or "error" in v:
            has_count = True
            total += int(v.get("fail") or 0) + int(v.get("error") or 0)
    return total if has_count else len(violations)


def summarize_property_violations(violations, limit=5):
    """门禁/错误信息用的短摘要。"""
    if not violations:
        return ""
    total = property_violation_total(violations)
    lines = []
    for v in violations[:limit]:
        if isinstance(v, dict):
            test = v.get("test") or ""
            msg = v.get("message") or ""
            short = test.rsplit(".", 1)[-1] if test else ""
            lines.append(f"{short or 'property'}: {msg}".strip(": "))
        else:
            lines.append(str(v))
    more = f" 等共 {len(violations)} 项" if len(violations) > limit else ""
    head = f"属性违反 {total} 次"
    return head + "（" + "；".join(lines) + more + "）"


def is_noisy_kea2_error(message):
    """堆栈首行等无信息文案，不宜直接展示为门禁原因。"""
    if not message:
        return True
    text = str(message).strip()
    if not text:
        return True
    noisy_prefixes = (
        "Traceback (most recent call last):",
        "Traceback (most recent call last)",
        "File \"",
    )
    if text in noisy_prefixes or text.startswith(noisy_prefixes):
        return True
    if text.startswith("Traceback"):
        return True
    return False


def sanitize_kea2_error_message(message, exit_code=0, violations=None):
    """将嘈杂/空错误替换为可读摘要。"""
    if message and not is_noisy_kea2_error(message):
        return str(message).strip()[:500]
    summary = summarize_property_violations(violations or [])
    if summary:
        return summary
    if exit_code:
        return f"Kea2 退出码 {format_kea2_exit_code(exit_code)}"
    return ""


def _find_html_report(kea2_output_dir):
    for pattern in (
        os.path.join(kea2_output_dir, "**", "bug_report.html"),
        os.path.join(kea2_output_dir, "res_*", "bug_report.html"),
        os.path.join(kea2_output_dir, "**", "index.html"),
        os.path.join(kea2_output_dir, "res_*", "index.html"),
    ):
        hit = _latest_file(pattern)
        if hit:
            return hit
    return None


def _extract_coverage_from_html(html_path):
    """从 bug_report.html 的 coverageData JS 变量解析 Activity 覆盖。"""
    empty = {
        "tested_activities": [],
        "activity_count_history": {},
        "total_activities_count": 0,
        "tested_activities_count": 0,
        "coverage_percent": None,
    }
    if not html_path or not os.path.isfile(html_path):
        return empty
    try:
        with open(html_path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError:
        return empty

    m = re.search(r"var coverageData\s*=\s*(\[.*?\]);", text, re.DOTALL)
    if not m:
        return empty
    try:
        data = json.loads(m.group(1))
    except json.JSONDecodeError:
        return empty
    if not data:
        return empty
    last = data[-1] if isinstance(data, list) else data
    if not isinstance(last, dict):
        return empty
    tested = last.get("testedActivities") or []
    history = last.get("activityCountHistory") or {}
    total = int(last.get("totalActivitiesCount") or 0)
    tested_n = int(last.get("testedActivitiesCount") or len(tested))
    cov = last.get("coverage")
    return {
        "tested_activities": [normalize_activity_name(a) for a in tested],
        "activity_count_history": {
            normalize_activity_name(k): int(v) for k, v in history.items()
        },
        "total_activities_count": total,
        "tested_activities_count": tested_n,
        "coverage_percent": round(float(cov), 4) if cov is not None else None,
    }


def _extract_coverage_from_fastbot_log(kea2_output_dir):
    """回退：从 fastbot_*.log 的 Explored app activities 段解析。"""
    empty = {
        "tested_activities": [],
        "activity_count_history": {},
        "total_activities_count": 0,
        "tested_activities_count": 0,
        "coverage_percent": None,
    }
    log = _latest_file(os.path.join(kea2_output_dir, "**", "fastbot_*.log"))
    if not log:
        return empty
    try:
        with open(log, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError:
        return empty

    tested = []
    in_explored = False
    coverage = None
    for line in lines:
        if "Explored app activities:" in line:
            in_explored = True
            continue
        if in_explored:
            if "Activity of Coverage:" in line:
                m = re.search(r"Activity of Coverage:\s*([\d.]+)", line)
                if m:
                    coverage = float(m.group(1))
                in_explored = False
                continue
            m = re.search(r"\d+\s+(com\.\S+)", line)
            if m:
                tested.append(normalize_activity_name(m.group(1)))
            elif "Dropped:" in line or "Monkey finished" in line:
                in_explored = False
    return {
        "tested_activities": tested,
        "activity_count_history": {a: 1 for a in tested},
        "total_activities_count": 0,
        "tested_activities_count": len(tested),
        "coverage_percent": coverage,
    }


def load_page_coverage(output_dir):
    """读取 CoverageSampler 产出的 coverage_pages.json。"""
    path = os.path.join(output_dir, "coverage_pages.json")
    if not os.path.isfile(path):
        # 也可能在 output_dir 的父级（若误传 kea2 子目录）
        parent = os.path.dirname(output_dir.rstrip("\\/"))
        alt = os.path.join(parent, "coverage_pages.json")
        path = alt if os.path.isfile(alt) else path
    if not os.path.isfile(path):
        return {"pages_seen": [], "page_hits": {}, "sample_count": 0}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"pages_seen": [], "page_hits": {}, "sample_count": 0}


def parse_kea2_output(
    kea2_output_dir,
    exit_code,
    error_message="",
    run_output_dir=None,
    lock_modules=None,
):
    """
    解析 Kea2 输出目录。

    Returns:
        dict: exit_code, property_violations, exploration 覆盖等
    """
    result = {
        "exit_code": exit_code,
        "exit_code_meaning": kea2_exit_code_meaning(exit_code),
        "exit_code_label": format_kea2_exit_code(exit_code),
        "running_minutes": None,
        "property_violations": [],
        "property_violation_count": 0,
        "crash_detected": exit_code in (2, 3),
        "report_path": None,
        "result_json_path": None,
        "raw_summary": {},
        "error_message": "",
        "exploration": None,
        "lock_modules": lock_modules,
    }
    if not kea2_output_dir or not os.path.isdir(kea2_output_dir):
        return result

    result_json = _latest_file(os.path.join(kea2_output_dir, "**", "result_*.json"))
    if not result_json:
        result_json = _latest_file(os.path.join(kea2_output_dir, "result_*.json"))
    if result_json:
        result["result_json_path"] = result_json
        try:
            with open(result_json, "r", encoding="utf-8") as f:
                data = json.load(f)
            result["raw_summary"] = data if isinstance(data, dict) else {}
            result["property_violations"] = _extract_violations(data)
            result["property_violation_count"] = property_violation_total(
                result["property_violations"]
            )
            if data.get("crashDetected") or data.get("crash_detected"):
                result["crash_detected"] = True
        except Exception:
            pass

    # 真实 Fastbot seed（与 config.SEED / Monkey 种子不是同一套）
    seed = extract_fastbot_seed(kea2_output_dir, run_output_dir=run_output_dir)
    if seed:
        result["seed_value"] = seed

    html_report = _find_html_report(kea2_output_dir)
    if html_report:
        result["report_path"] = html_report

    act_cov = _extract_coverage_from_html(html_report)
    if not act_cov.get("tested_activities"):
        act_cov = _extract_coverage_from_fastbot_log(kea2_output_dir)

    page_root = run_output_dir or os.path.dirname(kea2_output_dir.rstrip("\\/"))
    page_cov = load_page_coverage(page_root)
    result["exploration"] = merge_exploration_coverage(
        act_cov, page_cov, lock_modules=lock_modules
    )

    result["error_message"] = sanitize_kea2_error_message(
        error_message,
        exit_code=exit_code,
        violations=result["property_violations"],
    )
    if not result["error_message"] and exit_code == 4 and not result["result_json_path"]:
        result["error_message"] = "Kea2 未正常完成，请检查 configs/ 是否已 init 及设备连接"

    return result


# Kea2 官方语义（进程 returncode）
KEA2_EXIT_CODE_MEANINGS = {
    0: "成功",
    1: "属性违反",
    2: "Crash/ANR",
    3: "属性违反 + Crash/ANR",
    4: "运行时错误",
}


def kea2_exit_code_meaning(exit_code):
    """返回退出码中文释义；未知码返回「未知」。"""
    try:
        code = int(exit_code)
    except (TypeError, ValueError):
        return "未知"
    return KEA2_EXIT_CODE_MEANINGS.get(code, "未知")


def format_kea2_exit_code(exit_code):
    """报告展示：`1（属性违反）`。"""
    if exit_code is None or exit_code == "":
        return "N/A"
    return f"{exit_code}（{kea2_exit_code_meaning(exit_code)}）"


def kea2_exit_failed(exit_code):
    """Kea2 退出码是否应视为失败（Jenkins 门禁）。"""
    return exit_code in (1, 2, 3, 4)


def format_exploration_summary(exploration):
    """终端摘要几行。"""
    if not exploration:
        return "探索覆盖: 无数据"
    tested_n = exploration.get("tested_activities_count") or 0
    total = exploration.get("total_activities_count") or 0
    cov = exploration.get("coverage_percent")
    pages = exploration.get("business_pages_seen") or []
    cov_s = f"{cov:.2f}%" if cov is not None else "N/A"
    lines = [
        f"探索覆盖: Activity {tested_n}/{total or '?'} ({cov_s})",
        f"已识别业务页 ({len(pages)}): {', '.join(pages) or '(无)'}",
    ]
    ratio = exploration.get("in_module_sample_ratio")
    if ratio is not None:
        pct = exploration.get("in_module_sample_percent")
        if pct is None:
            pct = round(100.0 * ratio, 2)
        dwell = exploration.get("dwell_ok")
        dwell_s = "达标" if dwell else "未达标"
        locks = exploration.get("lock_modules") or []
        lines.append(
            f"模块内停留: {pct}% "
            f"({exploration.get('in_module_sample_count', 0)}/"
            f"{(exploration.get('in_module_sample_count') or 0) + (exploration.get('out_module_sample_count') or 0)}) "
            f"锁[{','.join(locks)}] {dwell_s}"
        )
    missed = exploration.get("business_pages_missed") or []
    if missed:
        lines.append(f"未命中一二级页 ({len(missed)}): {', '.join(missed[:12])}"
                     + ("..." if len(missed) > 12 else ""))
    return "\n".join(lines)
