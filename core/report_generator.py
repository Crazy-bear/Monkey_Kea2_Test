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
                # Jenkins 常见 CSP 可能禁止 img 的 data: URI，因此优先生成内联 SVG
                data["performance_chart_svg"] = self._build_performance_chart_svg(data["performance_data"])
                data["performance_chart_png_base64"] = self._build_performance_chart_png_base64(
                    data["performance_data"]
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
        将性能数据规范为 list of dict，每项含 timestamp, cpu, mem, fps。
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
            })
        return result if result else None

    def _build_performance_chart_png_base64(self, performance_data):
        """
        使用 matplotlib 生成性能趋势图并以内嵌 base64 PNG 形式返回。
        这样在 Jenkins（CSP/sandbox 禁止脚本/外链）中也能显示图表。
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

        try:
            labels = [str(i.get("timestamp", "")) for i in performance_data]
            cpu = [float(i.get("cpu", 0) or 0) for i in performance_data]
            mem = [float(i.get("mem", 0) or 0) for i in performance_data]
            fps = [float(i.get("fps", 0) or 0) for i in performance_data]

            fig, ax1 = plt.subplots(figsize=(10, 4), dpi=120)
            ax1.plot(cpu, color="#ff6384", linewidth=1.5, label="CPU(%)")
            ax1.plot(mem, color="#36a2eb", linewidth=1.5, label="Mem(MB)")
            ax1.set_ylabel("CPU / Mem")
            ax1.grid(True, alpha=0.25)

            ax2 = ax1.twinx()
            ax2.plot(fps, color="#4bc0c0", linewidth=1.5, label="FPS")
            ax2.set_ylabel("FPS")

            # x 轴标签过密时抽样显示
            if labels:
                step = max(1, len(labels) // 8)
                ax1.set_xticks(list(range(0, len(labels), step)))
                ax1.set_xticklabels([labels[i] for i in range(0, len(labels), step)], rotation=20, ha="right")

            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=8)

            fig.tight_layout()
            buf = io.BytesIO()
            fig.savefig(buf, format="png")
            plt.close(fig)
            buf.seek(0)
            return base64.b64encode(buf.read()).decode("ascii")
        except Exception as e:
            logger.error(f"生成性能图失败: {e}")
            return None

    def _build_performance_chart_svg(self, performance_data, width=980, height=360, padding=40):
        """
        生成内联 SVG 折线图（CPU/Mem/FPS），避免 Jenkins CSP 阻断脚本或 data: 图片。
        返回 SVG 字符串（包含 <svg> ... </svg>），用于模板中 safe 渲染。
        """
        if not performance_data:
            return None
        try:
            labels = [str(i.get("timestamp", "")) for i in performance_data]
            cpu = [float(i.get("cpu", 0) or 0) for i in performance_data]
            mem = [float(i.get("mem", 0) or 0) for i in performance_data]
            fps = [float(i.get("fps", 0) or 0) for i in performance_data]

            n = len(performance_data)
            if n < 2:
                return None

            # X 坐标映射
            x0 = padding
            x1 = width - padding
            y0 = padding
            y1 = height - padding
            def x_at(idx):
                return x0 + (x1 - x0) * (idx / (n - 1))

            # Y 坐标（上小下大）
            def scale_series(values):
                vmin = min(values)
                vmax = max(values)
                if vmax == vmin:
                    vmax = vmin + 1.0
                def y_at(v):
                    return y1 - (y1 - y0) * ((v - vmin) / (vmax - vmin))
                return y_at, vmin, vmax

            y_cpu, cpu_min, cpu_max = scale_series(cpu)
            y_mem, mem_min, mem_max = scale_series(mem)
            y_fps, fps_min, fps_max = scale_series(fps)

            def polyline_points(values, y_map):
                pts = []
                for i, v in enumerate(values):
                    pts.append(f"{x_at(i):.1f},{y_map(v):.1f}")
                return " ".join(pts)

            cpu_pts = polyline_points(cpu, y_cpu)
            mem_pts = polyline_points(mem, y_mem)
            fps_pts = polyline_points(fps, y_fps)

            # X 轴标签抽样
            step = max(1, n // 6)
            x_labels = []
            for i in range(0, n, step):
                txt = labels[i]
                x = x_at(i)
                x_labels.append(
                    f'<text x="{x:.1f}" y="{height-12}" font-size="10" fill="#666" text-anchor="middle">{_escape_xml(txt)}</text>'
                )

            # 画布与网格
            grid = []
            for k in range(5):
                y = y0 + (y1 - y0) * (k / 4)
                grid.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="#eee" />')

            svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="性能趋势图">
  <rect x="0" y="0" width="{width}" height="{height}" rx="4" ry="4" fill="#ffffff" stroke="#eeeeee"/>
  {"".join(grid)}
  <line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="#ccc"/>
  <line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="#ccc"/>

  <polyline fill="none" stroke="#ff6384" stroke-width="2" points="{cpu_pts}" />
  <polyline fill="none" stroke="#36a2eb" stroke-width="2" points="{mem_pts}" />
  <polyline fill="none" stroke="#4bc0c0" stroke-width="2" points="{fps_pts}" />

  <g>
    <rect x="{padding}" y="10" width="240" height="26" rx="4" ry="4" fill="#fff" stroke="#eee"/>
    <circle cx="{padding+12}" cy="23" r="4" fill="#ff6384"/><text x="{padding+22}" y="27" font-size="11" fill="#333">CPU(%)</text>
    <circle cx="{padding+82}" cy="23" r="4" fill="#36a2eb"/><text x="{padding+92}" y="27" font-size="11" fill="#333">Mem(MB)</text>
    <circle cx="{padding+165}" cy="23" r="4" fill="#4bc0c0"/><text x="{padding+175}" y="27" font-size="11" fill="#333">FPS</text>
  </g>

  <g>
    {"".join(x_labels)}
  </g>
</svg>
""".strip()
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

            <!-- 顶部统计卡片：用 table 布局替代 flex，兼容 Jenkins CSP -->
            <table style="width:100%;border-collapse:separate;border-spacing:10px;margin:20px 0;">
                <tr>
                    <td style="text-align:center;background-color:#fff;padding:20px;border-radius:5px;box-shadow:0 2px 4px rgba(0,0,0,0.1);width:25%;">
                        <div style="font-size:28px;font-weight:bold;color:#3498db;">{{ data.execution_count }}</div>
                        <div style="font-size:13px;color:#666;margin-top:4px;">执行事件数</div>
                    </td>
                    <td style="text-align:center;background-color:#fff;padding:20px;border-radius:5px;box-shadow:0 2px 4px rgba(0,0,0,0.1);width:25%;">
                        <div style="font-size:28px;font-weight:bold;color:#3498db;">{{ data.crash_count }}</div>
                        <div style="font-size:13px;color:#666;margin-top:4px;">崩溃次数</div>
                    </td>
                    <td style="text-align:center;background-color:#fff;padding:20px;border-radius:5px;box-shadow:0 2px 4px rgba(0,0,0,0.1);width:25%;">
                        <div style="font-size:28px;font-weight:bold;color:#3498db;">{{ data.duration }}</div>
                        <div style="font-size:13px;color:#666;margin-top:4px;">测试时长</div>
                    </td>
                    <td style="text-align:center;background-color:#fff;padding:20px;border-radius:5px;box-shadow:0 2px 4px rgba(0,0,0,0.1);width:25%;">
                        <div style="font-size:22px;font-weight:bold;">
                            {% if data.crash_count == 0 %}
                            <span style="display:inline-block;padding:6px 14px;border-radius:3px;font-weight:bold;background-color:#d4edda;color:#155724;">成功</span>
                            {% else %}
                            <span style="display:inline-block;padding:6px 14px;border-radius:3px;font-weight:bold;background-color:#f8d7da;color:#721c24;">失败</span>
                            {% endif %}
                        </div>
                        <div style="font-size:13px;color:#666;margin-top:4px;">测试结果</div>
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
                    <details style="margin-bottom:4px;">
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
                <div style="margin-bottom:15px;">
                    {% if data.performance_chart_svg %}
                    <div style="width:100%;overflow:auto;">{{ data.performance_chart_svg | safe }}</div>
                    {% elif data.performance_chart_png_base64 %}
                    <img alt="performance chart" style="width:100%;max-height:420px;border:1px solid #eee;border-radius:4px;background:#fff;" src="data:image/png;base64,{{ data.performance_chart_png_base64 }}" />
                    {% else %}
                    <p style="color:#666;">性能趋势图未生成。</p>
                    {% endif %}
                </div>
                <h3 style="color:#34495e;">性能统计</h3>
                <table style="width:100%;border-collapse:collapse;">
                    <tr>
                        <td style="font-weight:bold;width:150px;padding:6px 0;">平均CPU使用率:</td>
                        <td style="padding:6px 0;">
                            {% if data.performance_data and (data.performance_data | length) > 0 %}
                            {{ "%.2f" | format((data.performance_data | map(attribute='cpu') | sum) / (data.performance_data | length)) }}%
                            {% else %}无数据{% endif %}
                        </td>
                    </tr>
                    <tr>
                        <td style="font-weight:bold;padding:6px 0;">平均内存使用量:</td>
                        <td style="padding:6px 0;">
                            {% if data.performance_data and (data.performance_data | length) > 0 %}
                            {{ "%.2f" | format((data.performance_data | map(attribute='mem') | sum) / (data.performance_data | length)) }} MB
                            {% else %}无数据{% endif %}
                        </td>
                    </tr>
                    <tr>
                        <td style="font-weight:bold;padding:6px 0;">平均FPS:</td>
                        <td style="padding:6px 0;">
                            {% if data.performance_data and (data.performance_data | length) > 0 %}
                            {{ "%.2f" | format((data.performance_data | map(attribute='fps') | sum) / (data.performance_data | length)) }}
                            {% else %}无数据{% endif %}
                        </td>
                    </tr>
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

