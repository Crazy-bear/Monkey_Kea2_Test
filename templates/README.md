# 报告模板目录

本目录用于放置 Jinja2 HTML 报告模板（`report_template.html`）。

若目录为空或不存在 `report_template.html`，`ReportGenerator` 将自动使用 `core/report_generator.py` 中的**内置默认模板**生成报告，不影响测试流程。

如需自定义报告样式，在此目录添加 `report_template.html` 即可。
