# -*- coding: utf-8 -*-
"""
低频业务页采样：app_current + 少量 resource-id 锚点，不做全量 dump。
"""
from __future__ import annotations

import json
import os
import threading
import time
from typing import Dict, List, Optional, Set

from settings.logging_config import logger
from orchestrator.module_catalog import (
    BUSINESS_PAGES,
    normalize_activity_name,
)
from orchestrator.perf_context import ui_context_path, write_ui_context


class CoverageSampler:
    """后台线程：周期性识别当前业务页，写入 coverage_pages.json。"""

    def __init__(self, device_id: str, output_path: str, interval_seconds: float = 12.0):
        self.device_id = device_id
        self.output_path = output_path
        self.interval_seconds = max(5.0, float(interval_seconds))
        self._stop = threading.Event()
        self._thread = None
        self._lock = threading.Lock()
        self._seen_pages: Set[str] = set()
        self._hits: Dict[str, int] = {}
        self._samples: List[dict] = []
        self._last_activity = ""
        self._ui_context_path = ui_context_path(os.path.dirname(output_path) or ".")

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, name="CoverageSampler", daemon=True)
        self._thread.start()
        logger.info("业务页采样已启动 interval=%.1fs → %s", self.interval_seconds, self.output_path)

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=self.interval_seconds + 5)
            self._thread = None
        self._flush()
        logger.info(
            "业务页采样已停止 — 识别 %d 个页面: %s",
            len(self._seen_pages),
            ",".join(sorted(self._seen_pages)) or "(无)",
        )

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "pages_seen": sorted(self._seen_pages),
                "page_hits": dict(self._hits),
                "sample_count": len(self._samples),
                # 全量时间线：供性能报告 as-of join（不再截断为末尾 50 条）
                "samples": list(self._samples),
            }

    def _run(self):
        while not self._stop.wait(self.interval_seconds):
            try:
                self._sample_once()
            except Exception as e:
                logger.debug("CoverageSampler 采样失败: %s", e)

    def _sample_once(self):
        import uiautomator2 as u2

        d = u2.connect(self.device_id)
        cur = d.app_current() or {}
        activity = normalize_activity_name(cur.get("activity") or "")
        self._last_activity = activity
        page_id = self._match_page(d, activity)
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        row = {"timestamp": ts, "activity": activity, "page": page_id}
        with self._lock:
            self._samples.append(row)
            if page_id:
                self._seen_pages.add(page_id)
                self._hits[page_id] = self._hits.get(page_id, 0) + 1
        write_ui_context(self._ui_context_path, page_id, activity, ts)
        self._flush()

    def _match_page(self, d, activity: str) -> Optional[str]:
        if not activity:
            return None
        short = activity.rsplit(".", 1)[-1]
        candidates = []
        for p in BUSINESS_PAGES:
            for a in p.get("activities") or []:
                if a == activity or a.endswith("." + short) or short == a.rsplit(".", 1)[-1]:
                    candidates.append(p)
                    break
        if not candidates:
            return None

        # 优先匹配带锚点的共享页
        shared = [p for p in candidates if p.get("shared") and p.get("anchors")]
        for p in shared:
            if self._anchors_hit(d, p["anchors"]):
                return p["id"]

        unique = [p for p in candidates if not p.get("shared")]
        if len(unique) == 1:
            return unique[0]["id"]
        if unique:
            return unique[0]["id"]

        # 共享页但锚点未命中：不记业务页（避免把 Lifestyle 记成 Home）
        return None

    @staticmethod
    def _anchors_hit(d, anchors: List[str], min_hits: int = 1) -> bool:
        hits = 0
        for rid in anchors:
            try:
                if d(resourceId=rid).exists:
                    hits += 1
                    if hits >= min_hits:
                        return True
            except Exception:
                continue
        return False

    def _flush(self):
        data = self.snapshot()
        try:
            os.makedirs(os.path.dirname(self.output_path) or ".", exist_ok=True)
            with open(self.output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except OSError as e:
            logger.debug("写入 coverage_pages.json 失败: %s", e)
