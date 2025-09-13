# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2025/1/10
"""

<<<<<<< HEAD
import os
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
            # 检查是否存在模板文件
            template_file = os.path.join(self.template_dir, "report_template.html")
            
            if os.path.exists(template_file):
                # 使用外部模板文件
                template = self.env.get_template("report_template.html")
            else:
                # 使用内置模板
                template = self._get_default_template()
            
            # 渲染模板
            rendered = template.render(data=data)
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # 写入文件
            with open(output_file, "w", encoding="utf-8") as file:
                file.write(rendered)
            
            logger.info(f"HTML 报告已生成: {output_file}")
            return True
        except Exception as e:
            logger.error(f"生成 HTML 报告失败: {e}")
            return False
    
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
                    margin-bottom: 10px;
                }
                .info-label {
                    font-weight: bold;
                    width: 150px;
                }
                .info-value {
                    flex: 1;
                }
                .details {
                    background-color: white;
                    padding: 20px;
                    border-radius: 5px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    white-space: pre-wrap;
                    font-family: monospace;
                    font-size: 14px;
                    line-height: 1.4;
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
            </style>
        </head>
        <body>
            <h1>Monkey 测试报告</h1>
            
            <div class="summary">
                <div class="summary-item">
                    <div class="summary-value">{{ data.execution_count }}</div>
                    <div class="summary-label">执行事件数</div>
                </div>
                <div class="summary-item">
                    <div class="summary-value">{{ data.crash_count }}</div>
                    <div class="summary-label">崩溃次数</div>
                </div>
                <div class="summary-item">
                    <div class="summary-value">{{ data.duration }}</div>
                    <div class="summary-label">测试时长</div>
                </div>
                <div class="summary-item">
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
            
            <div class="info-box">
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
            
            <div class="info-box">
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
            
            {% if data.crashes %}
            <div class="info-box">
                <h2>崩溃信息</h2>
                <div class="details">
                    {% for crash in data.crashes %}
                    {{ crash }}
                    {% endfor %}
                </div>
            </div>
            {% endif %}
            
            <div class="info-box">
                <h2>测试详情</h2>
                <div class="details">{{ data.details }}</div>
            </div>
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
        生成测试报告
        
        Args:
            data: 测试数据
            output_file: 输出文件路径
            format: 报告格式，支持 html 和 json
            
        Returns:
            bool: 生成是否成功
        """
        if format.lower() == "json":
            return self.generate_json_report(data, output_file)
        else:
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
