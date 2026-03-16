# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2025/1/10
"""

<<<<<<< HEAD
import os
import base64
import io
from jinja2 import Template, FileSystemLoader, Environment
from config.logging_config import logger


class ReportGenerator:
    """
    测试报告生成器
    """
    def __init__(self, template_dir=None):
        """
        初始化报告生成器
        
        Args:
            template_dir: 模板文件目录
        """
        self.template_dir = template_dir or os.path.join(os.path.dirname(__file__), "..", "templates")
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
    
    def generate_html_report(self, data, output_file):
        """
        生成 HTML 格式的测试报告。
        
        Args:
            data: 测试数据
            output_file: 输出文件路径
            
        Returns:
            bool: 生成是否成功
        """
        try:
            data = dict(data)
            if data.get("performance_data") is not None:
                data["performance_data"] = self._normalize_performance_data(data["performance_data"])
            if data.get("performance_data"):
                thresholds = data.get("performance_thresholds") or {}
                leak = data.get("memory_leak_analysis") or {}
                # Jenkins 常见 CSP 可能禁止 img 的 data: URI，因此优先生成内联 SVG
                data["performance_chart_svg"] = self._build_performance_chart_svg(
                    data["performance_data"], thresholds=thresholds, leak_analysis=leak
                )
                data["performance_chart_png_base64"] = self._build_performance_chart_png_base64(
                    data["performance_data"], thresholds=thresholds, leak_analysis=leak
                )
            else:
                data["performance_chart_svg"] = None
                data["performance_chart_png_base64"] = None

            template_file = os.path.join(self.template_dir, "report_template.html")
            if os.path.exists(template_file):
                template = self.env.get_template("report_template.html")
            else:
                template = self._get_default_template()

            rendered = template.render(data=data)
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as file:
                file.write(rendered)
            logger.info(f"HTML 报告已生成: {output_file}")
            return True
        except Exception as e:
            logger.error(f"生成 HTML 报告失败: {e}")
            return False

    def _normalize_performance_data(self, performance_data):
        """
        将性能数据规范为 list of dict，每项含 timestamp, cpu, mem, fps 及超标标记。
        空或非法则返回 None，便于模板统一判断。
        """
        if performance_data is None:
            return None
        if not isinstance(performance_data, list):
            return None
        result = []
        for item in performance_data:
            if not isinstance(item, dict):
                continue
            result.append({
                "timestamp": item.get("timestamp", ""),
                "cpu": float(item.get("cpu", 0) or 0),
                "mem": float(item.get("mem", 0) or 0),
                "fps": float(item.get("fps", 0) or 0),
                "cpu_exceed": bool(item.get("cpu_exceed", False)),
                "mem_exceed": bool(item.get("mem_exceed", False)),
                "fps_low": bool(item.get("fps_low", False)),
            })
        return result if result else None

    def _build_performance_chart_png_base64(self, performance_data, thresholds=None, leak_analysis=None):
        """
        使用 matplotlib 生成性能趋势图并以内嵌 base64 PNG 形式返回。
        支持阈值线标注和内存泄漏区间高亮。
        """
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
        except Exception as e:
            logger.warning(f"matplotlib 不可用，跳过性能图生成: {e}")
            return None

        if not performance_data:
            return None

        thresholds = thresholds or {}

        try:
            labels = [str(i.get("timestamp", "")) for i in performance_data]
            cpu = [float(i.get("cpu", 0) or 0) for i in performance_data]
            mem = [float(i.get("mem", 0) or 0) for i in performance_data]
            fps = [float(i.get("fps", 0) or 0) for i in performance_data]
            xs = list(range(len(cpu)))

            fig, ax1 = plt.subplots(figsize=(10, 4), dpi=120)
            ax1.plot(xs, cpu, color="#ff6384", linewidth=1.5, label="CPU(%)")
            ax1.plot(xs, mem, color="#36a2eb", linewidth=1.5, label="Mem(MB)")
            ax1.set_ylabel("CPU / Mem")
            ax1.grid(True, alpha=0.25)

            # CPU 阈值线
            if thresholds.get('cpu'):
                ax1.axhline(y=thresholds['cpu'], color="#ff6384", linestyle='--', linewidth=1,
                            alpha=0.7, label=f"CPU阈值({thresholds['cpu']}%)")
            # Mem 阈值线
            if thresholds.get('mem'):
                ax1.axhline(y=thresholds['mem'], color="#36a2eb", linestyle='--', linewidth=1,
                            alpha=0.7, label=f"Mem阈值({thresholds['mem']}MB)")

            # 标注 CPU/Mem 超标点
            cpu_ex = [i for i, d in enumerate(performance_data) if d.get('cpu_exceed')]
            mem_ex = [i for i, d in enumerate(performance_data) if d.get('mem_exceed')]
            if cpu_ex:
                ax1.scatter(cpu_ex, [cpu[i] for i in cpu_ex], color="#ff0000", s=30, zorder=5, label="CPU超标")
            if mem_ex:
                ax1.scatter(mem_ex, [mem[i] for i in mem_ex], color="#0055ff", s=30, zorder=5, label="Mem超标")

            ax2 = ax1.twinx()
            ax2.plot(xs, fps, color="#4bc0c0", linewidth=1.5, label="FPS")
            ax2.set_ylabel("FPS")

            # FPS 阈值线
            if thresholds.get('fps'):
                ax2.axhline(y=thresholds['fps'], color="#4bc0c0", linestyle='--', linewidth=1,
                            alpha=0.7, label=f"FPS阈值({thresholds['fps']})")
            # 标注 FPS 低帧点
            fps_low = [i for i, d in enumerate(performance_data) if d.get('fps_low')]
            if fps_low:
                ax2.scatter(fps_low, [fps[i] for i in fps_low], color="#ff8800", s=30, zorder=5, label="FPS过低")

            # 内存泄漏区间高亮
            if leak_analysis and leak_analysis.get('suspected'):
                for seg in leak_analysis.get('details', []):
                    ax1.axvspan(seg['start_idx'], seg['end_idx'],
                                alpha=0.12, color='orange', label='疑似泄漏区间')

            # x 轴标签过密时抽样显示
            if labels:
                step = max(1, len(labels) // 8)
                ax1.set_xticks(list(range(0, len(labels), step)))
                ax1.set_xticklabels([labels[i] for i in range(0, len(labels), step)], rotation=20, ha="right")

            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            # 去重图例
            seen = set()
            combined = [(l, lb) for l, lb in zip(lines1 + lines2, labels1 + labels2) if lb not in seen and not seen.add(lb)]
            ax1.legend([c[0] for c in combined], [c[1] for c in combined], loc="upper left", fontsize=7)

            fig.tight_layout()
            buf = io.BytesIO()
            fig.savefig(buf, format="png")
            plt.close(fig)
            buf.seek(0)
            return base64.b64encode(buf.read()).decode("ascii")
        except Exception as e:
            logger.error(f"生成性能图失败: {e}")
            return None

    def _build_performance_chart_svg(self, performance_data, width=980, height=380, padding=40,
                                     thresholds=None, leak_analysis=None):
        """
        生成内联 SVG 折线图（CPU/Mem/FPS），支持阈值线、超标标注和内存泄漏区间高亮。
        返回 SVG 字符串（包含 <svg> ... </svg>），用于模板中 safe 渲染。
        """
        if not performance_data:
            return None
        thresholds = thresholds or {}
        leak_analysis = leak_analysis or {}
        try:
            labels = [str(i.get("timestamp", "")) for i in performance_data]
            cpu = [float(i.get("cpu", 0) or 0) for i in performance_data]
            mem = [float(i.get("mem", 0) or 0) for i in performance_data]
            fps = [float(i.get("fps", 0) or 0) for i in performance_data]

            n = len(performance_data)
            if n < 2:
                return None

            x0, x1 = padding, width - padding
            y0, y1 = padding + 20, height - padding

            def x_at(idx):
                return x0 + (x1 - x0) * (idx / (n - 1))

            def scale_series(values):
                vmin, vmax = min(values), max(values)
                if vmax == vmin:
                    vmax = vmin + 1.0
                def y_at(v):
                    return y1 - (y1 - y0) * ((v - vmin) / (vmax - vmin))
                return y_at, vmin, vmax

            y_cpu, cpu_min, cpu_max = scale_series(cpu)
            y_mem, mem_min, mem_max = scale_series(mem)
            y_fps, fps_min, fps_max = scale_series(fps)

            def polyline_points(values, y_map):
                return " ".join(f"{x_at(i):.1f},{y_map(v):.1f}" for i, v in enumerate(values))

            cpu_pts = polyline_points(cpu, y_cpu)
            mem_pts = polyline_points(mem, y_mem)
            fps_pts = polyline_points(fps, y_fps)

            # X 轴标签
            step = max(1, n // 6)
            x_labels = [
                f'<text x="{x_at(i):.1f}" y="{height - 8}" font-size="10" fill="#666" text-anchor="middle">{_escape_xml(labels[i])}</text>'
                for i in range(0, n, step)
            ]

            # 网格线
            grid = [
                f'<line x1="{x0}" y1="{y0 + (y1 - y0) * k / 4:.1f}" x2="{x1}" y2="{y0 + (y1 - y0) * k / 4:.1f}" stroke="#eee" />'
                for k in range(5)
            ]

            # 阈值线（CPU/Mem 共用左轴坐标系，FPS 用右轴）
            threshold_lines = []
            if thresholds.get('cpu') is not None:
                ty = y_cpu(thresholds['cpu'])
                if y0 <= ty <= y1:
                    threshold_lines.append(
                        f'<line x1="{x0}" y1="{ty:.1f}" x2="{x1}" y2="{ty:.1f}" stroke="#ff6384" stroke-width="1.5" stroke-dasharray="6,3" opacity="0.8"/>'
                        f'<text x="{x1 - 4}" y="{ty - 3:.1f}" font-size="10" fill="#ff6384" text-anchor="end">CPU阈值 {thresholds["cpu"]}%</text>'
                    )
            if thresholds.get('mem') is not None:
                ty = y_mem(thresholds['mem'])
                if y0 <= ty <= y1:
                    threshold_lines.append(
                        f'<line x1="{x0}" y1="{ty:.1f}" x2="{x1}" y2="{ty:.1f}" stroke="#36a2eb" stroke-width="1.5" stroke-dasharray="6,3" opacity="0.8"/>'
                        f'<text x="{x1 - 4}" y="{ty - 3:.1f}" font-size="10" fill="#36a2eb" text-anchor="end">Mem阈值 {thresholds["mem"]}MB</text>'
                    )
            if thresholds.get('fps') is not None:
                ty = y_fps(thresholds['fps'])
                if y0 <= ty <= y1:
                    threshold_lines.append(
                        f'<line x1="{x0}" y1="{ty:.1f}" x2="{x1}" y2="{ty:.1f}" stroke="#4bc0c0" stroke-width="1.5" stroke-dasharray="6,3" opacity="0.8"/>'
                        f'<text x="{x0 + 4}" y="{ty - 3:.1f}" font-size="10" fill="#4bc0c0" text-anchor="start">FPS阈值 {thresholds["fps"]}</text>'
                    )

            # 超标标注点
            exceed_marks = []
            for i, d in enumerate(performance_data):
                if d.get('cpu_exceed'):
                    cx, cy = x_at(i), y_cpu(cpu[i])
                    exceed_marks.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="5" fill="#ff0000" opacity="0.85"><title>CPU超标: {cpu[i]:.1f}%</title></circle>')
                if d.get('mem_exceed'):
                    cx, cy = x_at(i), y_mem(mem[i])
                    exceed_marks.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="5" fill="#0044cc" opacity="0.85"><title>Mem超标: {mem[i]:.1f}MB</title></circle>')
                if d.get('fps_low'):
                    cx, cy = x_at(i), y_fps(fps[i])
                    exceed_marks.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="5" fill="#ff8800" opacity="0.85"><title>FPS过低: {fps[i]:.1f}</title></circle>')

            # 内存泄漏区间高亮
            leak_rects = []
            if leak_analysis.get('suspected'):
                for seg in leak_analysis.get('details', []):
                    rx = x_at(seg['start_idx'])
                    rw = x_at(seg['end_idx']) - rx
                    leak_rects.append(
                        f'<rect x="{rx:.1f}" y="{y0}" width="{rw:.1f}" height="{y1 - y0}" fill="orange" opacity="0.12"/>'
                        f'<text x="{rx + rw/2:.1f}" y="{y0 + 12}" font-size="10" fill="#cc6600" text-anchor="middle">⚠ 疑似泄漏 +{seg["growth_mb"]}MB</text>'
                    )

            svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="性能趋势图">
  <rect x="0" y="0" width="{width}" height="{height}" rx="4" ry="4" fill="#ffffff" stroke="#eeeeee"/>
  {"".join(grid)}
  {"".join(leak_rects)}
  <line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="#ccc"/>
  <line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="#ccc"/>
  {"".join(threshold_lines)}
  <polyline fill="none" stroke="#ff6384" stroke-width="2" points="{cpu_pts}" />
  <polyline fill="none" stroke="#36a2eb" stroke-width="2" points="{mem_pts}" />
  <polyline fill="none" stroke="#4bc0c0" stroke-width="2" points="{fps_pts}" />
  {"".join(exceed_marks)}
  <g>
    <rect x="{padding}" y="6" width="320" height="22" rx="3" ry="3" fill="#fff" stroke="#eee"/>
    <circle cx="{padding+10}" cy="17" r="4" fill="#ff6384"/><text x="{padding+18}" y="21" font-size="11" fill="#333">CPU(%)</text>
    <circle cx="{padding+80}" cy="17" r="4" fill="#36a2eb"/><text x="{padding+88}" y="21" font-size="11" fill="#333">Mem(MB)</text>
    <circle cx="{padding+162}" cy="17" r="4" fill="#4bc0c0"/><text x="{padding+170}" y="21" font-size="11" fill="#333">FPS</text>
    <circle cx="{padding+210}" cy="17" r="4" fill="#ff0000"/><text x="{padding+218}" y="21" font-size="11" fill="#333">超标</text>
    <circle cx="{padding+258}" cy="17" r="4" fill="#ff8800"/><text x="{padding+266}" y="21" font-size="11" fill="#333">FPS低</text>
  </g>
  <g>{"".join(x_labels)}</g>
</svg>""".strip()
            return svg
        except Exception as e:
            logger.error(f"生成 SVG 性能图失败: {e}")
            return None
    
    def _get_default_template(self):
        """
        获取默认模板
        
        Returns:
            Template: 默认模板
        """
        template_content = """
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Monkey Test Report</title>
        </head>
        <body style="font-family:Arial,sans-serif;line-height:1.6;color:#333;max-width:1200px;margin:0 auto;padding:20px;background-color:#f4f4f4;">
            <h1 style="color:#2c3e50;text-align:center;border-bottom:2px solid #3498db;padding-bottom:10px;">Monkey 测试报告</h1>

            <!-- 顶部统计卡片 -->
            <table width="100%" cellpadding="0" cellspacing="8" style="margin:20px 0;">
                <tr>
                    <td width="25%" style="text-align:center;background-color:#ffffff;padding:20px 10px;border:2px solid #3498db;">
                        <div style="font-size:30px;font-weight:bold;color:#3498db;">{{ data.execution_count }}</div>
                        <div style="font-size:13px;color:#666;margin-top:6px;">执行事件数</div>
                    </td>
                    <td width="25%" style="text-align:center;background-color:#ffffff;padding:20px 10px;border:2px solid #3498db;">
                        <div style="font-size:30px;font-weight:bold;color:#3498db;">{{ data.crash_count }}</div>
                        <div style="font-size:13px;color:#666;margin-top:6px;">崩溃次数</div>
                    </td>
                    <td width="25%" style="text-align:center;background-color:#ffffff;padding:20px 10px;border:2px solid #3498db;">
                        <div style="font-size:30px;font-weight:bold;color:#3498db;">{{ data.duration }}</div>
                        <div style="font-size:13px;color:#666;margin-top:6px;">测试时长</div>
                    </td>
                    <td width="25%" style="text-align:center;background-color:#ffffff;padding:20px 10px;border:2px solid #3498db;">
                        {% if data.crash_count == 0 %}
                        <div style="font-size:22px;font-weight:bold;color:#155724;background-color:#d4edda;padding:6px;">成功</div>
                        {% else %}
                        <div style="font-size:22px;font-weight:bold;color:#721c24;background-color:#f8d7da;padding:6px;">失败</div>
                        {% endif %}
                        <div style="font-size:13px;color:#666;margin-top:6px;">测试结果</div>
                    </td>
                </tr>
            </table>

            <!-- 设备信息 -->
            <div style="background-color:#fff;padding:20px;border-radius:5px;box-shadow:0 2px 4px rgba(0,0,0,0.1);margin-bottom:20px;">
                <h2 style="color:#34495e;margin-top:10px;border-left:4px solid #3498db;padding-left:10px;">设备信息</h2>
                <table style="width:100%;border-collapse:collapse;">
                    <tr><td style="font-weight:bold;width:150px;padding:6px 0;">设备 ID:</td><td style="padding:6px 0;">{{ data.device_id }}</td></tr>
                    <tr><td style="font-weight:bold;padding:6px 0;">应用包名:</td><td style="padding:6px 0;">{{ data.package_name }}</td></tr>
                    <tr><td style="font-weight:bold;padding:6px 0;">应用版本:</td><td style="padding:6px 0;">{{ data.device_version_name }}</td></tr>
                    <tr><td style="font-weight:bold;padding:6px 0;">主板固件:</td><td style="padding:6px 0;">{{ data.firmware_version | default('未知') }}</td></tr>
                </table>
            </div>

            <!-- 测试信息 -->
            <div style="background-color:#fff;padding:20px;border-radius:5px;box-shadow:0 2px 4px rgba(0,0,0,0.1);margin-bottom:20px;">
                <h2 style="color:#34495e;margin-top:10px;border-left:4px solid #3498db;padding-left:10px;">测试信息</h2>
                <table style="width:100%;border-collapse:collapse;">
                    <tr><td style="font-weight:bold;width:150px;padding:6px 0;">开始时间:</td><td style="padding:6px 0;">{{ data.start_time }}</td></tr>
                    <tr><td style="font-weight:bold;padding:6px 0;">结束时间:</td><td style="padding:6px 0;">{{ data.end_time }}</td></tr>
                    <tr><td style="font-weight:bold;padding:6px 0;">随机种子:</td><td style="padding:6px 0;">{{ data.seed_value }}</td></tr>
                    <tr><td style="font-weight:bold;padding:6px 0;">事件数量:</td><td style="padding:6px 0;">{{ data.execution_count }}</td></tr>
                    <tr><td style="font-weight:bold;padding:6px 0;">崩溃次数:</td><td style="padding:6px 0;">{{ data.crash_count }}</td></tr>
                </table>
            </div>

            <!-- 日志分析 -->
            {% if data.log_analysis %}
            <div style="background-color:#fff;padding:20px;border-radius:5px;box-shadow:0 2px 4px rgba(0,0,0,0.1);margin-bottom:20px;">
                <h2 style="color:#34495e;margin-top:10px;border-left:4px solid #3498db;padding-left:10px;">日志分析</h2>
                {% if data.log_analysis.crash_categories %}
                <h3 style="color:#34495e;">崩溃分类</h3>
                <div style="margin-bottom:20px;">
                    {% for category, count in data.log_analysis.crash_categories.items() %}
                    {# 第一个默认展开，其余折叠 #}
                    <details style="margin-bottom:4px;" {% if loop.first %}open{% endif %}>
                        <summary style="cursor:pointer;padding:6px 8px;background-color:#f0f0f0;border-radius:3px;">
                            <strong>{{ category }}: {{ count }}次</strong>
                        </summary>
                        <div style="margin-left:15px;padding:8px;background-color:#f9f9f9;border-top:1px solid #e0e0e0;">
                            {% for crash in data.log_analysis.crash_details %}
                            {% if crash.category == category %}
                            <div style="padding:2px 0;border-bottom:1px solid #f0f0f0;font-size:14px;">{{ crash.message | default('无') }}</div>
                            {% endif %}
                            {% endfor %}
                        </div>
                    </details>
                    {% endfor %}
                </div>
                {% endif %}
                <table style="width:100%;border-collapse:collapse;">
                    <tr>
                        <td style="font-weight:bold;width:150px;padding:6px 0;vertical-align:top;">分析结论:</td>
                        <td style="padding:6px 0;">{{ data.log_analysis.analysis_conclusion | default('无') | replace('\n', '<br>') | safe }}</td>
                    </tr>
                </table>
            </div>
            {% else %}
            <div style="background-color:#fff;padding:20px;border-radius:5px;box-shadow:0 2px 4px rgba(0,0,0,0.1);margin-bottom:20px;">
                <h2 style="color:#34495e;margin-top:10px;border-left:4px solid #3498db;padding-left:10px;">日志分析</h2>
                <p style="color:#666;">日志分析未执行</p>
            </div>
            {% endif %}

            <!-- 性能数据 -->
            {% if data.performance_data %}
            <div style="background-color:#fff;padding:20px;border-radius:5px;box-shadow:0 2px 4px rgba(0,0,0,0.1);margin-bottom:20px;">
                <h2 style="color:#34495e;margin-top:10px;border-left:4px solid #3498db;padding-left:10px;">性能数据</h2>
                <h3 style="color:#34495e;">性能趋势</h3>

                <div style="position:relative;margin-bottom:4px;">
                    <canvas id="perfChart" style="width:100%;display:block;"></canvas>
                    <!-- tooltip 浮层 -->
                    <div id="perfTooltip" style="display:none;position:absolute;background:rgba(30,30,30,0.88);color:#fff;padding:10px 14px;border-radius:6px;font-size:13px;pointer-events:none;white-space:nowrap;z-index:10;"></div>
                </div>
                <p style="font-size:12px;color:#999;margin:4px 0 20px 0;">💡 鼠标悬停查看数值 &nbsp;·&nbsp; 滚轮缩放 X 轴 &nbsp;·&nbsp; 拖拽平移</p>
                <script>
                (function() {
                    var raw = {{ data.performance_data | tojson }};

                    // 抽样：超过200点时降采样
                    if (raw.length > 200) {
                        var step = Math.ceil(raw.length / 200);
                        raw = raw.filter(function(_,i){ return i % step === 0; });
                    }

                    var labels = raw.map(function(d){ return d.timestamp || ''; });
                    var cpu    = raw.map(function(d){ return +d.cpu || 0; });
                    var mem    = raw.map(function(d){ return +d.mem || 0; });
                    var fps    = raw.map(function(d){ return +d.fps || 0; });
                    var cpuExceed = raw.map(function(d){ return !!d.cpu_exceed; });
                    var memExceed = raw.map(function(d){ return !!d.mem_exceed; });
                    var fpsLow    = raw.map(function(d){ return !!d.fps_low; });
                    var n      = raw.length;

                    var thresholds = {{ data.performance_thresholds | default({}) | tojson }};
                    var leakAnalysis = {{ data.memory_leak_analysis | default({}) | tojson }};

                    var canvas  = document.getElementById('perfChart');
                    var tooltip = document.getElementById('perfTooltip');
                    var W = canvas.parentElement.clientWidth || 900;
                    var H = 380;
                    canvas.width  = W;
                    canvas.height = H;
                    var ctx = canvas.getContext('2d');

                    // 布局常量
                    var PAD_L = 120, PAD_R = 72, PAD_T = 36, PAD_B = 56;
                    var chartW = W - PAD_L - PAD_R;
                    var chartH = H - PAD_T - PAD_B;

                    // 视口（用于缩放/平移）
                    var viewStart = 0, viewEnd = n - 1;

                    function minMax(arr, s, e) {
                        var mn = Infinity, mx = -Infinity;
                        for (var i = s; i <= e; i++) { if (arr[i] < mn) mn = arr[i]; if (arr[i] > mx) mx = arr[i]; }
                        if (mn === mx) { mn -= 1; mx += 1; }
                        return [mn, mx];
                    }

                    function niceStep(range, ticks) {
                        var raw = range / ticks;
                        var mag = Math.pow(10, Math.floor(Math.log10(raw)));
                        var norm = raw / mag;
                        var nice = norm < 1.5 ? 1 : norm < 3 ? 2 : norm < 7 ? 5 : 10;
                        return nice * mag;
                    }

                    function xAt(i) { return PAD_L + (i - viewStart) / (viewEnd - viewStart) * chartW; }
                    function yAt(v, mn, mx) { return PAD_T + chartH - (v - mn) / (mx - mn) * chartH; }

                    function draw() {
                        ctx.clearRect(0, 0, W, H);
                        var vs = Math.round(viewStart), ve = Math.round(viewEnd);

                        var cpuMM = minMax(cpu, vs, ve);
                        var memMM = minMax(mem, vs, ve);
                        var fpsMM = minMax(fps, vs, ve);

                        // 背景
                        ctx.fillStyle = '#fafafa';
                        ctx.fillRect(PAD_L, PAD_T, chartW, chartH);

                        // 左Y轴(CPU) 刻度 — 红色
                        ctx.strokeStyle = '#e8e8e8'; ctx.lineWidth = 1;
                        var cpuStep = niceStep(cpuMM[1] - cpuMM[0], 5);
                        var cpuBase = Math.floor(cpuMM[0] / cpuStep) * cpuStep;
                        for (var v = cpuBase; v <= cpuMM[1] + cpuStep; v += cpuStep) {
                            var y = yAt(v, cpuMM[0], cpuMM[1]);
                            if (y < PAD_T || y > PAD_T + chartH) continue;
                            ctx.beginPath(); ctx.moveTo(PAD_L, y); ctx.lineTo(PAD_L + chartW, y); ctx.stroke();
                            ctx.fillStyle = '#e74c3c'; ctx.font = '11px Arial'; ctx.textAlign = 'right';
                            ctx.fillText(v.toFixed(1) + '%', PAD_L - 6, y + 4);
                        }

                        // 左Y轴第二列(Mem) 刻度 — 蓝色，紧贴图表左侧内侧
                        var memStep = niceStep(memMM[1] - memMM[0], 5);
                        var memBase = Math.floor(memMM[0] / memStep) * memStep;
                        for (var mv = memBase; mv <= memMM[1] + memStep; mv += memStep) {
                            var my = yAt(mv, memMM[0], memMM[1]);
                            if (my < PAD_T || my > PAD_T + chartH) continue;
                            ctx.fillStyle = '#3498db'; ctx.font = '11px Arial'; ctx.textAlign = 'right';
                            ctx.fillText(mv.toFixed(0) + 'M', PAD_L - 6 - 52, my + 4);
                        }

                        // 右Y轴(FPS) 刻度
                        var fpsStep = niceStep(fpsMM[1] - fpsMM[0], 5);
                        var fpsBase = Math.floor(fpsMM[0] / fpsStep) * fpsStep;
                        for (var fv = fpsBase; fv <= fpsMM[1] + fpsStep; fv += fpsStep) {
                            var fy = yAt(fv, fpsMM[0], fpsMM[1]);
                            if (fy < PAD_T || fy > PAD_T + chartH) continue;
                            ctx.fillStyle = '#2ecc71'; ctx.textAlign = 'left';
                            ctx.fillText(fv.toFixed(1), PAD_L + chartW + 6, fy + 4);
                        }

                        // X轴刻度
                        var tickCount = Math.min(8, ve - vs + 1);
                        var tickStep  = Math.max(1, Math.round((ve - vs) / tickCount));
                        ctx.fillStyle = '#666'; ctx.font = '11px Arial'; ctx.textAlign = 'center';
                        for (var ti = vs; ti <= ve; ti += tickStep) {
                            var tx = xAt(ti);
                            ctx.beginPath(); ctx.strokeStyle = '#ccc'; ctx.moveTo(tx, PAD_T + chartH); ctx.lineTo(tx, PAD_T + chartH + 4); ctx.stroke();
                            var lbl = labels[ti] || '';
                            if (lbl.length > 19) lbl = lbl.slice(11); // 只显示时间部分
                            ctx.fillText(lbl, tx, PAD_T + chartH + 16);
                        }

                        // 轴边框
                        ctx.strokeStyle = '#ccc'; ctx.lineWidth = 1;
                        ctx.strokeRect(PAD_L, PAD_T, chartW, chartH);

                        // 折线绘制函数
                        function drawLine(arr, mm, color, alpha) {
                            ctx.beginPath();
                            ctx.strokeStyle = color; ctx.lineWidth = 2;
                            for (var i = vs; i <= ve; i++) {
                                var px = xAt(i), py = yAt(arr[i], mm[0], mm[1]);
                                if (i === vs) ctx.moveTo(px, py); else ctx.lineTo(px, py);
                            }
                            ctx.stroke();
                            // 填充
                            ctx.lineTo(xAt(ve), PAD_T + chartH);
                            ctx.lineTo(xAt(vs), PAD_T + chartH);
                            ctx.closePath();
                            ctx.fillStyle = alpha;
                            ctx.fill();
                        }

                        drawLine(cpu, cpuMM, '#e74c3c', 'rgba(231,76,60,0.07)');
                        drawLine(mem, memMM, '#3498db', 'rgba(52,152,219,0.07)');
                        drawLine(fps, fpsMM, '#2ecc71', 'rgba(46,204,113,0.07)');

                        // 内存泄漏区间高亮
                        if (leakAnalysis && leakAnalysis.suspected && leakAnalysis.details) {
                            leakAnalysis.details.forEach(function(seg) {
                                var rx = xAt(seg.start_idx), rw = xAt(seg.end_idx) - xAt(seg.start_idx);
                                ctx.fillStyle = 'rgba(255,165,0,0.12)';
                                ctx.fillRect(rx, PAD_T, rw, chartH);
                                ctx.fillStyle = '#cc6600'; ctx.font = '10px Arial'; ctx.textAlign = 'center';
                                ctx.fillText('⚠ +' + seg.growth_mb + 'MB', rx + rw / 2, PAD_T + 12);
                            });
                        }

                        // 阈值线
                        ctx.setLineDash([6, 3]);
                        ctx.lineWidth = 1.5;
                        if (thresholds.cpu != null) {
                            var ty = yAt(thresholds.cpu, cpuMM[0], cpuMM[1]);
                            if (ty >= PAD_T && ty <= PAD_T + chartH) {
                                ctx.beginPath(); ctx.strokeStyle = 'rgba(231,76,60,0.75)';
                                ctx.moveTo(PAD_L, ty); ctx.lineTo(PAD_L + chartW, ty); ctx.stroke();
                                ctx.fillStyle = '#e74c3c'; ctx.font = '10px Arial'; ctx.textAlign = 'right';
                                ctx.fillText('CPU阈值 ' + thresholds.cpu + '%', PAD_L + chartW - 4, ty - 3);
                            }
                        }
                        if (thresholds.mem != null) {
                            var my2 = yAt(thresholds.mem, memMM[0], memMM[1]);
                            if (my2 >= PAD_T && my2 <= PAD_T + chartH) {
                                ctx.beginPath(); ctx.strokeStyle = 'rgba(52,152,219,0.75)';
                                ctx.moveTo(PAD_L, my2); ctx.lineTo(PAD_L + chartW, my2); ctx.stroke();
                                ctx.fillStyle = '#3498db'; ctx.font = '10px Arial'; ctx.textAlign = 'right';
                                ctx.fillText('Mem阈值 ' + thresholds.mem + 'MB', PAD_L + chartW - 4, my2 - 3);
                            }
                        }
                        if (thresholds.fps != null) {
                            var fy2 = yAt(thresholds.fps, fpsMM[0], fpsMM[1]);
                            if (fy2 >= PAD_T && fy2 <= PAD_T + chartH) {
                                ctx.beginPath(); ctx.strokeStyle = 'rgba(46,204,113,0.75)';
                                ctx.moveTo(PAD_L, fy2); ctx.lineTo(PAD_L + chartW, fy2); ctx.stroke();
                                ctx.fillStyle = '#2ecc71'; ctx.font = '10px Arial'; ctx.textAlign = 'left';
                                ctx.fillText('FPS阈值 ' + thresholds.fps, PAD_L + 4, fy2 - 3);
                            }
                        }
                        ctx.setLineDash([]);

                        // 超标点标注
                        for (var si = vs; si <= ve; si++) {
                            if (cpuExceed[si]) {
                                ctx.beginPath(); ctx.arc(xAt(si), yAt(cpu[si], cpuMM[0], cpuMM[1]), 5, 0, Math.PI*2);
                                ctx.fillStyle = '#ff0000'; ctx.fill();
                            }
                            if (memExceed[si]) {
                                ctx.beginPath(); ctx.arc(xAt(si), yAt(mem[si], memMM[0], memMM[1]), 5, 0, Math.PI*2);
                                ctx.fillStyle = '#0044cc'; ctx.fill();
                            }
                            if (fpsLow[si]) {
                                ctx.beginPath(); ctx.arc(xAt(si), yAt(fps[si], fpsMM[0], fpsMM[1]), 5, 0, Math.PI*2);
                                ctx.fillStyle = '#ff8800'; ctx.fill();
                            }
                        }

                        // Y轴标题
                        ctx.save();
                        ctx.translate(14, PAD_T + chartH / 2);
                        ctx.rotate(-Math.PI / 2);
                        ctx.fillStyle = '#e74c3c'; ctx.font = 'bold 11px Arial'; ctx.textAlign = 'center';
                        ctx.fillText('CPU(%)', 0, 0);
                        ctx.restore();

                        ctx.save();
                        ctx.translate(36, PAD_T + chartH / 2);
                        ctx.rotate(-Math.PI / 2);
                        ctx.fillStyle = '#3498db'; ctx.font = 'bold 11px Arial'; ctx.textAlign = 'center';
                        ctx.fillText('Mem(MB)', 0, 0);
                        ctx.restore();

                        ctx.save();
                        ctx.translate(W - 14, PAD_T + chartH / 2);
                        ctx.rotate(Math.PI / 2);
                        ctx.fillStyle = '#2ecc71'; ctx.font = 'bold 12px Arial'; ctx.textAlign = 'center';
                        ctx.fillText('FPS', 0, 0);
                        ctx.restore();

                        // 图例
                        var legends = [['CPU (%)', '#e74c3c'], ['Mem (MB)', '#3498db'], ['FPS', '#2ecc71'],
                                       ['超标', '#ff0000'], ['FPS低', '#ff8800']];
                        var lx = PAD_L;
                        legends.forEach(function(lg) {
                            ctx.fillStyle = lg[1];
                            ctx.fillRect(lx, 10, 14, 14);
                            ctx.fillStyle = '#333'; ctx.font = '12px Arial'; ctx.textAlign = 'left';
                            ctx.fillText(lg[0], lx + 18, 22);
                            lx += ctx.measureText(lg[0]).width + 40;
                        });
                    }

                    draw();

                    // ---- 交互：hover tooltip ----
                    canvas.addEventListener('mousemove', function(e) {
                        var rect = canvas.getBoundingClientRect();
                        var mx = e.clientX - rect.left;
                        var my = e.clientY - rect.top;
                        if (mx < PAD_L || mx > PAD_L + chartW || my < PAD_T || my > PAD_T + chartH) {
                            tooltip.style.display = 'none';
                            draw();
                            return;
                        }
                        var vs = Math.round(viewStart), ve = Math.round(viewEnd);
                        var idx = Math.round(vs + (mx - PAD_L) / chartW * (ve - vs));
                        idx = Math.max(vs, Math.min(ve, idx));

                        var cpuMM = minMax(cpu, vs, ve);
                        var memMM = minMax(mem, vs, ve);
                        var fpsMM = minMax(fps, vs, ve);

                        draw();

                        // 竖线
                        var lx = xAt(idx);
                        ctx.beginPath(); ctx.strokeStyle = 'rgba(0,0,0,0.25)'; ctx.lineWidth = 1;
                        ctx.setLineDash([4, 3]);
                        ctx.moveTo(lx, PAD_T); ctx.lineTo(lx, PAD_T + chartH);
                        ctx.stroke(); ctx.setLineDash([]);

                        // 圆点
                        [[cpu, cpuMM, '#e74c3c'], [mem, memMM, '#3498db'], [fps, fpsMM, '#2ecc71']].forEach(function(s) {
                            var py = yAt(s[0][idx], s[1][0], s[1][1]);
                            ctx.beginPath(); ctx.arc(lx, py, 5, 0, Math.PI * 2);
                            ctx.fillStyle = s[2]; ctx.fill();
                            ctx.strokeStyle = '#fff'; ctx.lineWidth = 2; ctx.stroke();
                        });

                        // tooltip 内容
                        tooltip.innerHTML =
                            '<div style="font-weight:bold;margin-bottom:6px;color:#ddd;">' + (labels[idx] || '') + '</div>' +
                            '<div style="color:#e74c3c;">● CPU: ' + cpu[idx].toFixed(2) + ' %' + (cpuExceed[idx] ? ' <span style="color:#ff4444">⚠超标</span>' : '') + '</div>' +
                            '<div style="color:#5dade2;">● Mem: ' + mem[idx].toFixed(2) + ' MB' + (memExceed[idx] ? ' <span style="color:#4488ff">⚠超标</span>' : '') + '</div>' +
                            '<div style="color:#2ecc71;">● FPS: ' + fps[idx].toFixed(2) + (fpsLow[idx] ? ' <span style="color:#ff8800">⚠过低</span>' : '') + '</div>';

                        var tx = lx + 14;
                        if (tx + 180 > W) tx = lx - 190;
                        tooltip.style.left = tx + 'px';
                        tooltip.style.top  = (PAD_T + 10) + 'px';
                        tooltip.style.display = 'block';
                    });

                    canvas.addEventListener('mouseleave', function() {
                        tooltip.style.display = 'none';
                        draw();
                    });

                    // ---- 交互：滚轮缩放 ----
                    canvas.addEventListener('wheel', function(e) {
                        e.preventDefault();
                        var rect = canvas.getBoundingClientRect();
                        var mx = e.clientX - rect.left;
                        var ratio = (mx - PAD_L) / chartW;
                        ratio = Math.max(0, Math.min(1, ratio));
                        var span = viewEnd - viewStart;
                        var factor = e.deltaY > 0 ? 1.15 : 0.87;
                        var newSpan = Math.max(4, Math.min(n - 1, span * factor));
                        var center = viewStart + ratio * span;
                        viewStart = Math.max(0, center - ratio * newSpan);
                        viewEnd   = Math.min(n - 1, viewStart + newSpan);
                        if (viewEnd === n - 1) viewStart = Math.max(0, viewEnd - newSpan);
                        draw();
                    }, { passive: false });

                    // ---- 交互：拖拽平移 ----
                    var dragX = null, dragVS = null;
                    canvas.addEventListener('mousedown', function(e) {
                        dragX = e.clientX; dragVS = viewStart;
                        canvas.style.cursor = 'grabbing';
                    });
                    window.addEventListener('mousemove', function(e) {
                        if (dragX === null) return;
                        var rect = canvas.getBoundingClientRect();
                        var dx = e.clientX - dragX;
                        var span = viewEnd - viewStart;
                        var shift = -dx / chartW * span;
                        viewStart = Math.max(0, Math.min(n - 1 - span, dragVS + shift));
                        viewEnd   = viewStart + span;
                        draw();
                    });
                    window.addEventListener('mouseup', function() {
                        dragX = null; canvas.style.cursor = 'default';
                    });

                    // 窗口resize重绘
                    window.addEventListener('resize', function() {
                        W = canvas.parentElement.clientWidth || 900;
                        canvas.width = W;
                        chartW = W - PAD_L - PAD_R;
                        draw();
                    });
                })();
                </script>

                <h3 style="color:#34495e;">性能统计</h3>

                <!-- 阈值配置说明 -->
                {% if data.performance_thresholds %}
                <p style="font-size:12px;color:#888;margin:0 0 8px 0;">
                    阈值设定：CPU ≤ {{ data.performance_thresholds.cpu }}%　Mem ≤ {{ data.performance_thresholds.mem }} MB　FPS ≥ {{ data.performance_thresholds.fps }}
                    &nbsp;·&nbsp; 图表中 <span style="color:#ff0000;font-weight:bold;">●</span> CPU超标 &nbsp;
                    <span style="color:#0044cc;font-weight:bold;">●</span> Mem超标 &nbsp;
                    <span style="color:#ff8800;font-weight:bold;">●</span> FPS过低 &nbsp;
                    <span style="background:rgba(255,165,0,0.3);padding:0 4px;">橙色区间</span> 疑似内存泄漏
                </p>
                {% endif %}

                <!-- 内存泄漏警告 -->
                {% if data.memory_leak_analysis and data.memory_leak_analysis.suspected %}
                <div style="background-color:#fff3cd;border:1px solid #ffc107;border-radius:4px;padding:12px 16px;margin-bottom:12px;">
                    <strong style="color:#856404;">⚠ 疑似内存泄漏</strong>
                    <span style="color:#856404;margin-left:8px;">
                        监控期间内存净增长 {{ "%.1f" | format(data.memory_leak_analysis.total_growth_mb) }} MB，
                        检测到 {{ data.memory_leak_analysis.leak_segments }} 段持续增长区间（图表橙色区域）。
                        建议检查是否存在未释放的资源或循环引用。
                    </span>
                    {% if data.memory_leak_analysis.details %}
                    <ul style="margin:8px 0 0 0;padding-left:20px;font-size:13px;color:#856404;">
                        {% for seg in data.memory_leak_analysis.details %}
                        <li>{{ seg.start_time }} → {{ seg.end_time }}，增长 {{ seg.growth_mb }} MB</li>
                        {% endfor %}
                    </ul>
                    {% endif %}
                </div>
                {% endif %}

                <table style="width:100%;border-collapse:collapse;">
                    <tr style="background-color:#f8f9fa;">
                        <td style="font-weight:bold;width:160px;padding:6px 8px;border:1px solid #dee2e6;color:#666;">指标</td>
                        <td style="font-weight:bold;padding:6px 8px;border:1px solid #dee2e6;color:#e74c3c;text-align:center;">平均值</td>
                        <td style="font-weight:bold;padding:6px 8px;border:1px solid #dee2e6;color:#e67e22;text-align:center;">最大值</td>
                        <td style="font-weight:bold;padding:6px 8px;border:1px solid #dee2e6;color:#27ae60;text-align:center;">最小值</td>
                    </tr>
                    {% if data.performance_data and (data.performance_data | length) > 0 %}
                    {% set cpu_vals = data.performance_data | map(attribute='cpu') | list %}
                    {% set mem_vals = data.performance_data | map(attribute='mem') | list %}
                    {% set fps_vals = data.performance_data | map(attribute='fps') | list %}
                    <tr>
                        <td style="padding:6px 8px;border:1px solid #dee2e6;font-weight:bold;">CPU 使用率</td>
                        <td style="padding:6px 8px;border:1px solid #dee2e6;text-align:center;">{{ "%.2f" | format(cpu_vals | sum / cpu_vals | length) }}%</td>
                        <td style="padding:6px 8px;border:1px solid #dee2e6;text-align:center;color:#e67e22;">{{ "%.2f" | format(cpu_vals | max) }}%</td>
                        <td style="padding:6px 8px;border:1px solid #dee2e6;text-align:center;color:#27ae60;">{{ "%.2f" | format(cpu_vals | min) }}%</td>
                    </tr>
                    <tr style="background-color:#f8f9fa;">
                        <td style="padding:6px 8px;border:1px solid #dee2e6;font-weight:bold;">内存使用量</td>
                        <td style="padding:6px 8px;border:1px solid #dee2e6;text-align:center;">{{ "%.2f" | format(mem_vals | sum / mem_vals | length) }} MB</td>
                        <td style="padding:6px 8px;border:1px solid #dee2e6;text-align:center;color:#e67e22;">{{ "%.2f" | format(mem_vals | max) }} MB</td>
                        <td style="padding:6px 8px;border:1px solid #dee2e6;text-align:center;color:#27ae60;">{{ "%.2f" | format(mem_vals | min) }} MB</td>
                    </tr>
                    <tr>
                        <td style="padding:6px 8px;border:1px solid #dee2e6;font-weight:bold;">FPS</td>
                        <td style="padding:6px 8px;border:1px solid #dee2e6;text-align:center;">{{ "%.2f" | format(fps_vals | sum / fps_vals | length) }}</td>
                        <td style="padding:6px 8px;border:1px solid #dee2e6;text-align:center;color:#27ae60;">{{ "%.2f" | format(fps_vals | max) }}</td>
                        <td style="padding:6px 8px;border:1px solid #dee2e6;text-align:center;color:#e67e22;">{{ "%.2f" | format(fps_vals | min) }}</td>
                    </tr>
                    {% else %}
                    <tr><td colspan="4" style="padding:8px;border:1px solid #dee2e6;color:#666;">无数据</td></tr>
                    {% endif %}
                </table>
            </div>
            {% else %}
            <div style="background-color:#fff;padding:20px;border-radius:5px;box-shadow:0 2px 4px rgba(0,0,0,0.1);margin-bottom:20px;">
                <h2 style="color:#34495e;margin-top:10px;border-left:4px solid #3498db;padding-left:10px;">性能数据</h2>
                <p style="color:#666;">性能数据未采集</p>
            </div>
            {% endif %}

        </body>
        </html>
        """
        return Template(template_content)

    def generate_json_report(self, data, output_file):
        """
        生成 JSON 格式的测试报告
        
        Args:
            data: 测试数据
            output_file: 输出文件路径
            
        Returns:
            bool: 生成是否成功
        """
        try:
            import json
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # 写入 JSON 文件
            with open(output_file, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
            
            logger.info(f"JSON 报告已生成: {output_file}")
            return True
        except Exception as e:
            logger.error(f"生成 JSON 报告失败: {e}")
            return False
    
    def generate_report(self, data, output_file, format="html"):
        """
        生成测试报告。会先规范化 performance_data。
        """
        data = dict(data)
        data["performance_data"] = self._normalize_performance_data(data.get("performance_data"))
        if format.lower() == "json":
            return self.generate_json_report(data, output_file)
        return self.generate_html_report(data, output_file)


def _escape_xml(text: str) -> str:
    if text is None:
        return ""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )

