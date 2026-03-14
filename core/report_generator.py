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
                data["performance_chart_png_base64"] = self._build_performance_chart_png_base64(
                    data["performance_data"]
                )
            else:
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
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f4f4f4;
                }
                h1 {
                    color: #2c3e50;
                    text-align: center;
                    border-bottom: 2px solid #3498db;
                    padding-bottom: 10px;
                }
                h2 {
                    color: #34495e;
                    margin-top: 30px;
                    border-left: 4px solid #3498db;
                    padding-left: 10px;
                }
                .info-box {
                    background-color: white;
                    padding: 20px;
                    border-radius: 5px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    margin-bottom: 20px;
                }
                .info-row {
                    display: flex;
                    margin-bottom: 15px;
                    align-items: flex-start;
                }
                .info-label {
                    font-weight: bold;
                    width: 150px;
                    padding-top: 5px;
                }
                .info-value {
                    flex: 1;
                    line-height: 1.6;
                    padding: 5px 0;
                }
                .details {
                    background-color: white;
                    padding: 15px;
                    border-radius: 5px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    white-space: pre-wrap;
                    font-family: monospace;
                    font-size: 14px;
                    line-height: 1.4;
                }
                .crash-categories-container {
                    background-color: white;
                    padding: 10px;
                    border-radius: 5px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    margin-bottom: 20px;
                }
                .status {
                    display: inline-block;
                    padding: 5px 10px;
                    border-radius: 3px;
                    font-weight: bold;
                }
                .status-success {
                    background-color: #d4edda;
                    color: #155724;
                }
                .status-failed {
                    background-color: #f8d7da;
                    color: #721c24;
                }
                .summary {
                    display: flex;
                    justify-content: space-around;
                    margin: 20px 0;
                }
                .summary-item {
                    text-align: center;
                    background-color: white;
                    padding: 20px;
                    border-radius: 5px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    flex: 1;
                    margin: 0 10px;
                }
                .summary-value {
                    font-size: 24px;
                    font-weight: bold;
                    color: #3498db;
                }
                .summary-label {
                    font-size: 14px;
                    color: #666;
                }
                .crash-category {
                    margin-bottom: 3px;
                }
                .category-header {
                    cursor: pointer;
                    padding: 6px 8px;
                    background-color: #f0f0f0;
                    border-radius: 3px;
                    margin-bottom: 0;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                .category-header:hover {
                    background-color: #e0e0e0;
                }
                .toggle-icon {
                    transition: transform 0.3s;
                    font-size: 12px;
                }
                .toggle-icon.collapsed {
                    transform: rotate(-90deg);
                }
                .crash-details {
                    margin-left: 15px;
                    margin-top: 0;
                    padding: 8px;
                    background-color: #f9f9f9;
                    border-radius: 0 0 3px 3px;
                    border-top: 1px solid #e0e0e0;
                }
                .crash-item {
                    padding: 2px 0;
                    border-bottom: 1px solid #f0f0f0;
                    font-size: 14px;
                }
                .crash-item:last-child {
                    border-bottom: none;
                }
            </style>
            <script>
                function toggleCrashDetails(categoryId) {
                    const details = document.getElementById(categoryId);
                    const header = details.previousElementSibling;
                    const icon = header.querySelector('.toggle-icon');
                    
                    if (details.style.display === 'none') {
                        details.style.display = 'block';
                        icon.classList.remove('collapsed');
                    } else {
                        details.style.display = 'none';
                        icon.classList.add('collapsed');
                    }
                }
            </script>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 1200px; margin: 0 auto; padding: 20px; background-color: #f4f4f4;">
            <h1>Monkey 测试报告</h1>
            
            <div class="summary" style="display:flex; justify-content: space-around; margin: 20px 0; flex-wrap: wrap; gap: 10px;">
                <div class="summary-item" style="text-align:center; background-color:#fff; padding:20px; border-radius:5px; box-shadow:0 2px 4px rgba(0,0,0,0.1); flex:1; min-width: 180px;">
                    <div class="summary-value">{{ data.execution_count }}</div>
                    <div class="summary-label">执行事件数</div>
                </div>
                <div class="summary-item" style="text-align:center; background-color:#fff; padding:20px; border-radius:5px; box-shadow:0 2px 4px rgba(0,0,0,0.1); flex:1; min-width: 180px;">
                    <div class="summary-value">{{ data.crash_count }}</div>
                    <div class="summary-label">崩溃次数</div>
                </div>
                <div class="summary-item" style="text-align:center; background-color:#fff; padding:20px; border-radius:5px; box-shadow:0 2px 4px rgba(0,0,0,0.1); flex:1; min-width: 180px;">
                    <div class="summary-value">{{ data.duration }}</div>
                    <div class="summary-label">测试时长</div>
                </div>
                <div class="summary-item" style="text-align:center; background-color:#fff; padding:20px; border-radius:5px; box-shadow:0 2px 4px rgba(0,0,0,0.1); flex:1; min-width: 180px;">
                    <div class="summary-value">
                        {% if data.crash_count == 0 %}
                        <span class="status status-success">成功</span>
                        {% else %}
                        <span class="status status-failed">失败</span>
                        {% endif %}
                    </div>
                    <div class="summary-label">测试结果</div>
                </div>
            </div>
            
            <div class="info-box" style="background-color:#fff; padding:20px; border-radius:5px; box-shadow:0 2px 4px rgba(0,0,0,0.1); margin-bottom:20px;">
                <h2>设备信息</h2>
                <div class="info-row">
                    <div class="info-label">设备 ID:</div>
                    <div class="info-value">{{ data.device_id }}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">应用包名:</div>
                    <div class="info-value">{{ data.package_name }}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">应用版本:</div>
                    <div class="info-value">{{ data.device_version_name }}</div>
                </div>
            </div>
            
            <div class="info-box" style="background-color:#fff; padding:20px; border-radius:5px; box-shadow:0 2px 4px rgba(0,0,0,0.1); margin-bottom:20px;">
                <h2>测试信息</h2>
                <div class="info-row">
                    <div class="info-label">开始时间:</div>
                    <div class="info-value">{{ data.start_time }}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">结束时间:</div>
                    <div class="info-value">{{ data.end_time }}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">随机种子:</div>
                    <div class="info-value">{{ data.seed_value }}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">事件数量:</div>
                    <div class="info-value">{{ data.execution_count }}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">崩溃次数:</div>
                    <div class="info-value">{{ data.crash_count }}</div>
                </div>
            </div>
            
            {% if data.log_analysis %}
            <div class="info-box" style="background-color:#fff; padding:20px; border-radius:5px; box-shadow:0 2px 4px rgba(0,0,0,0.1); margin-bottom:20px;">
                <h2>日志分析</h2>
                {% if data.log_analysis.crash_categories %}
                <h3>崩溃分类</h3>
                <div class="crash-categories-container">
                    {% for category, count in data.log_analysis.crash_categories.items() %}
                    <div class="crash-category">
                        <div class="category-header" onclick="toggleCrashDetails('{{ category | replace(' ', '_') }}')">
                            <strong>{{ category }}: {{ count }}次</strong> <span class="toggle-icon">▼</span>
                        </div>
                        <div id="{{ category | replace(' ', '_') }}" class="crash-details" style="display: none;">
                            {% for crash in data.log_analysis.crash_details %}
                            {% if crash.category == category %}
                            <div class="crash-item">{{ crash.message | default('无') }}</div>
                            {% endif %}
                            {% endfor %}
                        </div>
                    </div>
                    {% endfor %}
                </div>
                {% endif %}
                
                <div class="info-row">
                    <div class="info-label">分析结论:</div>
                    <div class="info-value">{{ data.log_analysis.analysis_conclusion | default('无') | replace('\n', '<br>') | safe }}</div>
                </div>
            </div>
            {% else %}
            <div class="info-box" style="background-color:#fff; padding:20px; border-radius:5px; box-shadow:0 2px 4px rgba(0,0,0,0.1); margin-bottom:20px;">
                <h2>日志分析</h2>
                <div class="info-row">
                    <div class="info-label">分析结论:</div>
                    <div class="info-value">日志分析未执行</div>
                </div>
            </div>
            {% endif %}
            
            {% if data.performance_data %}
            <div class="info-box" style="background-color:#fff; padding:20px; border-radius:5px; box-shadow:0 2px 4px rgba(0,0,0,0.1); margin-bottom:20px;">
                <h2>性能数据</h2>
                <h3>性能趋势</h3>
                <div class="info-row">
                    <div class="info-value">
                        {% if data.performance_chart_png_base64 %}
                        <img alt="performance chart" style="width:100%; max-height:420px; object-fit:contain; border:1px solid #eee; border-radius:4px; background:#fff;" src="data:image/png;base64,{{ data.performance_chart_png_base64 }}" />
                        {% else %}
                        <div style="color:#666;">性能趋势图未生成（可能是 Jenkins/CSP 禁止脚本，或未安装 matplotlib）。</div>
                        {% endif %}
                    </div>
                </div>
                <h3>性能统计</h3>
                <div class="info-row">
                    <div class="info-label">平均CPU使用率:</div>
                    <div class="info-value">
                        {% if data.performance_data and (data.performance_data | length) > 0 %}
                        {{ "%.2f" | format((data.performance_data | map(attribute='cpu') | sum) / (data.performance_data | length)) }}%
                        {% else %}
                        无数据
                        {% endif %}
                    </div>
                </div>
                <div class="info-row">
                    <div class="info-label">平均内存使用量:</div>
                    <div class="info-value">
                        {% if data.performance_data and (data.performance_data | length) > 0 %}
                        {{ "%.2f" | format((data.performance_data | map(attribute='mem') | sum) / (data.performance_data | length)) }} MB
                        {% else %}
                        无数据
                        {% endif %}
                    </div>
                </div>
                <div class="info-row">
                    <div class="info-label">平均FPS:</div>
                    <div class="info-value">
                        {% if data.performance_data and (data.performance_data | length) > 0 %}
                        {{ "%.2f" | format((data.performance_data | map(attribute='fps') | sum) / (data.performance_data | length)) }}
                        {% else %}
                        无数据
                        {% endif %}
                    </div>
                </div>
            </div>
            {% else %}
            <div class="info-box" style="background-color:#fff; padding:20px; border-radius:5px; box-shadow:0 2px 4px rgba(0,0,0,0.1); margin-bottom:20px;">
                <h2>性能数据</h2>
                <div class="info-row">
                    <div class="info-label">状态:</div>
                    <div class="info-value">性能数据未采集</div>
                </div>
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

=======

from jinja2 import Template


class ReportGenerator:
    def generate_html_report(self, data, output_file):
        """
        生成 HTML 格式的测试报告。
        """
        template = """
        <html>
        <head><title>Monkey Test Report</title></head>
        <body>
            <h1>Test Report</h1>
            <h2>Device Info</h2>
            <p>{{ data.device_info }}</p>
            <h2>Package Name</h2>
            <p>{{ data.package_name }}</p>
            <h2>Device Version Name</h2>
            <p>{{ data.device_version_name }}</p>
            <h2>Start Time</h2>
            <p>{{ data.start_time }}</p>
            <h2>End Time</h2>
            <p>{{ data.end_time }}</p>
            <h2>Duration</h2>
            <p>{{ data.duration }}</p>
            <h2>Seed Value</h2>
            <p>{{ data.seed_value }}</p>
            <h2>Execution Count</h2>
            <p>{{ data.execution_count }}</p>
            <h2>Crash Count</h2>
            <p>{{ data.crash_count }}</p>
            <h2>Details</h2>
            <pre>{{ data.details }}</pre>
        </body>
        </html>
        """
        rendered = Template(template).render(data=data)
        with open(output_file, "w") as file:
            file.write(rendered)
>>>>>>> bc185e8 (Monkey稳定性测试)
