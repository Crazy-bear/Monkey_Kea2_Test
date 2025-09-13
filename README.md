# 项目名称：【A1力量镜】Monkey自动化测试
## 项目介绍
Monkey是一个开源的自动化测试工具，它可以模拟用户的操作行为，并自动执行脚本。Monkey可以用来测试Web应用、移动应用、桌面应用、游戏等。
## 项目背景
用于测试【A1力量镜】的稳定性，主要测试场景为：
- 登录页面
- 随心练
- 精品课程（AI课程、跟练课程）
- 个人中心
- 运动计划
- 运动测评
- 音乐
- K歌
- 使用指南

## 项目目标
- 实现Monkey自动化测试脚本，并通过测试用例验证稳定性，发现bug并修复
- 优化脚本，提升测试效率

## 代码目录结构
```
├── README.md
├── Monkey_test/
│
├── config/
│   ├── config.py              # 配置文件（设备信息、测试参数）
│   └── logging_config.py      # 日志配置
│
├── core/
│   ├── adb_client.py          # 封装 ADB 操作的核心类
│   ├── monkey_runner.py       # Monkey 测试核心逻辑
│   ├── logcat_handler.py      # Logcat 捕获和处理
│   ├── report_generator.py    # 测试报告生成模块
│   └── utils.py               # 通用工具函数
│
├── pages/                     # Page Object 层（针对目标应用的页面）
│   ├── base_page.py           # 基础页面类，提供通用方法
│   ├── login_page.py          # 登录页面
│   ├── main_page.py           # 主界面
│   ├── settings_page.py       # 设置页面
│   └── example_page.py        # 示例功能页面
│
├── tests/                     # 测试用例
│   ├── test_monkey.py         # Monkey 测试入口
│   ├── test_crash_detection.py# 崩溃检测测试
│   ├── test_parallel_run.py   # 多设备并行测试
│   └── test_report.py         # 报告生成测试
│
├── outputs/                   # 测试输出（日志和报告）
│   ├── logs/                  # 保存 logcat 和测试日志
│   ├── reports/               # 保存 HTML 或其他格式的测试报告
│   └── coverage/              # 保存代码覆盖率文件
│   └── monkey_logs/           # 保存 monkey 测试日志
├── README.md                  # 项目说明文档
└── requirements.txt           # Python 依赖包

```

## 项目技术栈
- Monkey测试工具
- Python编程语言
- ADB命令行工具
- Page Object模式
- 日志处理、报告生成

## 项目周期
- 2025年1月10日-2025年2月30日
