# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2025/1/10
"""


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
