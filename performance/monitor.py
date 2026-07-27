# -*- coding: utf-8 -*-
"""
性能监控主模块
"""
import threading
import time
import os
import csv
import json
from datetime import datetime
from settings.logging_config import logger
from core.adb_client import ADBClient
from performance.cpu import CPUMonitor
from performance.memory import MemoryMonitor
from performance.fps import FPSMonitor


class PerformanceMonitor:
    def __init__(self, device_id, package_name, output_dir, interval=None, config=None):
        """
        初始化性能监控器

        Args:
            device_id: 设备 ID
            package_name: 应用包名
            output_dir: 输出目录
            interval: 监控间隔（秒），默认从 config 读取（3s）
            config: Config 实例，用于读取阈值与间隔
        """
        self.device_id = device_id
        self.package_name = package_name
        self.output_dir = output_dir
        self.config = config
        self.interval = interval
        if self.interval is None:
            self.interval = getattr(config, "PERF_MONITOR_INTERVAL", 3.0) if config else 3.0

        self.is_running = False
        self.thread = None
        self.data = []
        self._loop_count = 0
        self._phase = "default"
        self._phase_lock = threading.Lock()
        self.leak_analysis = {
            "suspected": False,
            "total_growth_mb": 0,
            "leak_segments": 0,
            "leak_rate_mb_per_min": 0.0,
            "details": [],
        }

        cfg = config
        self.cpu_threshold = getattr(cfg, "PERF_CPU_THRESHOLD", 80.0) if cfg else 80.0
        self.mem_threshold = getattr(cfg, "PERF_MEM_THRESHOLD", 512.0) if cfg else 512.0
        self.fps_threshold = getattr(cfg, "PERF_FPS_THRESHOLD", 30.0) if cfg else 30.0
        self.mem_leak_window = getattr(cfg, "PERF_MEM_LEAK_WINDOW", 10) if cfg else 10
        self.mem_leak_growth = getattr(cfg, "PERF_MEM_LEAK_GROWTH", 20.0) if cfg else 20.0
        self.fps_sample_every = getattr(cfg, "PERF_FPS_SAMPLE_EVERY", 3) if cfg else 3

        self.adb = ADBClient(device_id=device_id)
        self.cpu_monitor = CPUMonitor(device_id, package_name, self.adb)
        self.memory_monitor = MemoryMonitor(device_id, package_name, self.adb)
        self.fps_monitor = FPSMonitor(device_id, package_name, self.adb)

        os.makedirs(output_dir, exist_ok=True)

    def set_phase(self, name):
        """设置当前业务阶段标签（供场景脚本调用）。"""
        with self._phase_lock:
            self._phase = name or "default"
        logger.debug(f"性能监控 phase -> {self._phase}")

    def get_phase(self):
        with self._phase_lock:
            return self._phase

    def start(self):
        if self.is_running:
            logger.warning("性能监控已经在运行中")
            return
        self.is_running = True
        self._loop_count = 0
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        logger.info(
            f"性能监控已启动 - 设备: {self.device_id}, 应用: {self.package_name}, "
            f"间隔: {self.interval}s"
        )

    def stop(self):
        if not self.is_running:
            logger.warning("性能监控未运行")
            return
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=max(10, self.interval * 2))

        self.leak_analysis = self._analyze_memory_leak()
        if self.leak_analysis["suspected"]:
            logger.warning(
                f"疑似内存泄漏：监控期间内存增长 {self.leak_analysis['total_growth_mb']:.1f} MB，"
                f"检测到 {self.leak_analysis['leak_segments']} 段持续增长"
            )

        self._save_data()
        logger.info(f"性能监控已停止 - 共采集 {len(self.data)} 条数据")

    def _monitor_loop(self):
        while self.is_running:
            loop_start = time.time()
            try:
                self._loop_count += 1
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cpu = self.cpu_monitor.get_cpu_usage()
                mem_data = self.memory_monitor.get_memory_usage()

                sample_fps = (
                    self.fps_sample_every <= 1
                    or self._loop_count == 1
                    or self._loop_count % self.fps_sample_every == 0
                )
                fps = self.fps_monitor.get_fps() if sample_fps else (
                    self.data[-1]["fps"] if self.data else 0.0
                )

                mem_total = mem_data.get("total", 0.0)
                java_heap = mem_data.get("java_heap", 0.0)
                native_heap = mem_data.get("native_heap", 0.0)
                graphics = mem_data.get("graphics", 0.0)
                phase = self.get_phase()

                row = {
                    "timestamp": timestamp,
                    "phase": phase,
                    "cpu": cpu,
                    "mem": mem_total,
                    "java_heap": java_heap,
                    "native_heap": native_heap,
                    "graphics": graphics,
                    "fps": fps,
                    "cpu_exceed": cpu > self.cpu_threshold,
                    "mem_exceed": mem_total > self.mem_threshold,
                    "fps_low": fps > 0 and fps < self.fps_threshold,
                }
                self.data.append(row)

                if row["cpu_exceed"] or row["mem_exceed"] or row["fps_low"]:
                    logger.warning(
                        f"性能阈值告警 phase={phase} CPU={cpu}% Mem={mem_total}MB FPS={fps}"
                    )
            except Exception as e:
                logger.error(f"监控过程中发生错误: {e}")

            elapsed = time.time() - loop_start
            sleep_time = max(0.0, self.interval - elapsed)
            if self.is_running and sleep_time > 0:
                time.sleep(sleep_time)

    def _analyze_memory_leak(self):
        result = {
            "suspected": False,
            "total_growth_mb": 0.0,
            "leak_segments": 0,
            "leak_rate_mb_per_min": 0.0,
            "details": [],
        }
        if len(self.data) < self.mem_leak_window:
            return result

        leak_rate_threshold = getattr(self.config, "PERF_MEM_LEAK_RATE", 5.0) if self.config else 5.0
        r2_min = getattr(self.config, "PERF_MEM_LEAK_R2_MIN", 0.6) if self.config else 0.6

        mem_vals = [d["mem"] for d in self.data]
        w = self.mem_leak_window
        i = 0
        while i + w <= len(mem_vals):
            window_mem = mem_vals[i:i + w]
            xs = list(range(w))
            n = w
            sum_x = sum(xs)
            sum_y = sum(window_mem)
            sum_xy = sum(x * y for x, y in zip(xs, window_mem))
            sum_x2 = sum(x * x for x in xs)
            denom = n * sum_x2 - sum_x ** 2
            if denom == 0:
                i += 1
                continue
            slope = (n * sum_xy - sum_x * sum_y) / denom
            intercept = (sum_y - slope * sum_x) / n
            y_mean = sum_y / n
            ss_tot = sum((y - y_mean) ** 2 for y in window_mem)
            ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(xs, window_mem))
            r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
            slope_per_min = slope * (60.0 / self.interval)
            growth_mb = round(window_mem[-1] - window_mem[0], 2)

            if (
                slope_per_min >= leak_rate_threshold
                and r2 >= r2_min
                and growth_mb >= self.mem_leak_growth
            ):
                seg_start = i

                def seg_growth(key, _start=seg_start, _w=w):
                    vals = [self.data[_start + j].get(key, 0.0) or 0.0 for j in range(_w)]
                    return round(vals[-1] - vals[0], 2)

                java_g = seg_growth("java_heap")
                native_g = seg_growth("native_heap")
                graphics_g = seg_growth("graphics")

                candidates = {"Java Heap": java_g, "Native Heap": native_g, "Graphics": graphics_g}
                positive = {k: v for k, v in candidates.items() if v > 0}
                if positive:
                    leak_type = max(positive, key=positive.get)
                    if positive[leak_type] < growth_mb * 0.3:
                        leak_type = "综合"
                else:
                    leak_type = "综合"

                result["details"].append({
                    "start_idx": i,
                    "end_idx": i + w - 1,
                    "start_time": self.data[i]["timestamp"],
                    "end_time": self.data[i + w - 1]["timestamp"],
                    "growth_mb": growth_mb,
                    "leak_rate_mb_per_min": round(slope_per_min, 2),
                    "r2": round(r2, 3),
                    "leak_type": leak_type,
                    "java_heap_growth": java_g,
                    "native_heap_growth": native_g,
                    "graphics_growth": graphics_g,
                })
                i += w
            else:
                i += 1

        segments = len(result["details"])
        if segments > 0:
            total_growth = mem_vals[-1] - mem_vals[0]
            avg_rate = sum(d["leak_rate_mb_per_min"] for d in result["details"]) / segments
            result["suspected"] = True
            result["leak_segments"] = segments
            result["total_growth_mb"] = round(total_growth, 2)
            result["leak_rate_mb_per_min"] = round(avg_rate, 2)
        return result

    def _build_summary(self):
        if not self.data:
            return {}

        def stats(key):
            vals = sorted(v for d in self.data if (v := float(d.get(key) or 0)) > 0)
            if not vals:
                return {"min": 0, "max": 0, "avg": 0, "p95": 0}
            p95_idx = max(0, int(len(vals) * 0.95) - 1)
            return {
                "min": round(min(vals), 2),
                "max": round(max(vals), 2),
                "avg": round(sum(vals) / len(vals), 2),
                "p95": round(vals[p95_idx], 2),
            }

        return {
            "sample_count": len(self.data),
            "cpu": stats("cpu"),
            "mem": stats("mem"),
            "fps": stats("fps"),
            "exceed_cpu_count": sum(1 for d in self.data if d.get("cpu_exceed")),
            "exceed_mem_count": sum(1 for d in self.data if d.get("mem_exceed")),
            "fps_low_count": sum(1 for d in self.data if d.get("fps_low")),
            "memory_leak": self.leak_analysis,
        }

    def _save_data(self):
        if not self.data:
            logger.warning("无数据可保存")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = os.path.join(self.output_dir, f"performance_{timestamp}.csv")
        json_file = os.path.join(self.output_dir, f"performance_{timestamp}.json")
        summary_file = os.path.join(self.output_dir, f"performance_summary_{timestamp}.json")

        fieldnames = [
            "timestamp", "phase", "cpu", "mem", "java_heap", "native_heap", "graphics", "fps",
            "cpu_exceed", "mem_exceed", "fps_low",
        ]
        try:
            with open(csv_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(self.data)
            logger.info(f"性能数据已保存到 CSV: {csv_file}")
        except Exception as e:
            logger.error(f"保存 CSV 文件失败: {e}")

        try:
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            logger.info(f"性能数据已保存到 JSON: {json_file}")
        except Exception as e:
            logger.error(f"保存 JSON 文件失败: {e}")

        try:
            summary = self._build_summary()
            with open(summary_file, "w", encoding="utf-8") as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            logger.info(f"性能摘要已保存: {summary_file}")
        except Exception as e:
            logger.error(f"保存性能摘要失败: {e}")

    def get_data(self):
        return self.data

    def get_thresholds(self):
        return {"cpu": self.cpu_threshold, "mem": self.mem_threshold, "fps": self.fps_threshold}

    def get_leak_analysis(self):
        return self.leak_analysis

    def get_summary(self):
        return self._build_summary()
