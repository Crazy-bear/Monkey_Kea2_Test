# -*- coding: utf-8 -*-
"""
解析 Kea2 运行产物：result JSON、HTML 报告路径、属性违反列表。
"""
import glob
import json
import os


def _latest_file(pattern):
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def _extract_violations(data):
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
    if isinstance(results, list):
        for r in results:
            if not isinstance(r, dict):
                continue
            if r.get("status") in ("FAIL", "fail", "failure") or r.get("failed"):
                violations.append({
                    "test": r.get("test") or r.get("name") or r.get("property"),
                    "message": r.get("message") or r.get("detail") or str(r),
                })
    return violations


def _find_html_report(kea2_output_dir):
    for pattern in (
        os.path.join(kea2_output_dir, "**", "index.html"),
        os.path.join(kea2_output_dir, "res_*", "index.html"),
    ):
        hit = _latest_file(pattern)
        if hit:
            return hit
    return None


def parse_kea2_output(kea2_output_dir, exit_code, error_message=""):
    """
    解析 Kea2 输出目录。

    Returns:
        dict: exit_code, running_minutes, property_violations, crash_detected, report_path, result_json_path
    """
    result = {
        "exit_code": exit_code,
        "running_minutes": None,
        "property_violations": [],
        "property_violation_count": 0,
        "crash_detected": exit_code in (2, 3),
        "report_path": None,
        "result_json_path": None,
        "raw_summary": {},
        "error_message": "",
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
            result["property_violation_count"] = len(result["property_violations"])
            if data.get("crashDetected") or data.get("crash_detected"):
                result["crash_detected"] = True
        except Exception:
            pass

    html_report = _find_html_report(kea2_output_dir)
    if html_report:
        result["report_path"] = html_report

    if error_message:
        result["error_message"] = error_message
    elif exit_code == 4 and not result["result_json_path"]:
        result["error_message"] = "Kea2 未正常完成，请检查 configs/ 是否已 init 及设备连接"

    return result


def kea2_exit_failed(exit_code):
    """Kea2 退出码是否应视为失败（Jenkins 门禁）。"""
    return exit_code in (1, 2, 3, 4)
