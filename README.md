# 项目名称：【A1力量镜】Monkey自动化测试
## 项目介绍
Monkey是一个开源的自动化测试工具，它可以模拟用户的操作行为，并自动执行脚本。本项目基于Monkey工具，为【A1力量镜】应用量身定制了自动化测试方案，用于测试应用的稳定性和可靠性。

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
- 提供详细的测试报告和崩溃分析
- 支持多设备并行测试

## 代码目录结构
```
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
│   ├── coverage/              # 保存代码覆盖率文件
│   └── monkey_logs/           # 保存 monkey 测试日志
│
├── templates/                 # 报告模板
│   └── report_template.html   # HTML 报告模板
│
├── main.py                    # 主入口文件
├── README.md                  # 项目说明文档
└── requirements.txt           # Python 依赖包

```

## 项目技术栈
- Monkey测试工具
- Python编程语言
- ADB命令行工具
- Page Object模式
- 日志处理、报告生成
- Jinja2模板引擎（用于报告生成）
- uiautomator2（用于UI自动化）

## 项目周期
- 2025年1月10日-2026年3月10日

## 快速开始
### 1. 环境准备
- Python 3.7+
- ADB工具
- 连接到电脑的Android设备

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置设备信息
编辑 `config/config.py` 文件，设置设备ID和其他测试参数：
```python
# 设备ID
DEFAULT_DEVICE_ID = "192.168.20.152:5555"

# 测试参数
DEFAULT_MONKEY_COUNT = 10000  # 默认事件数量
DEFAULT_MONKEY_THROTTLE = 100  # 默认事件间隔（毫秒）
```

### 4. 运行测试
#### 方法一：使用主入口文件
```bash
python main.py --device_id 192.168.20.152:5555 --count 10000 --throttle 100
```

#### 方法二：使用测试文件
```bash
python tests/test_monkey.py
```

## 配置说明
### 环境变量
可以通过环境变量覆盖默认配置：
- `MONKEY_DEVICE_ID`：设备ID
- `MONKEY_COUNT`：事件数量
- `MONKEY_THROTTLE`：事件间隔

### 配置文件
也可以在 `config/config.py` 中直接修改默认配置。

## 测试报告
测试完成后，报告将生成在 `outputs/reports/` 目录下，包括：
- HTML格式报告
- JSON格式报告

报告包含以下内容：
- 测试基本信息（设备、时间、事件数等）
- 崩溃信息（如果有）
- 性能数据
- 测试日志

## 常见问题
### 1. 设备连接问题
- 确保设备已通过USB连接到电脑
- 运行 `adb devices` 确认设备已被识别
- 检查设备ID是否正确配置

### 2. 权限问题
- 确保设备已开启USB调试模式
- 对于Android 6.0+设备，需要授予应用权限

### 3. 测试失败问题
- 检查应用是否正常安装
- 查看 `outputs/logs/` 目录下的日志文件
- 检查设备是否有足够的存储空间

## 优化特点
- **统一配置管理**：支持环境变量和配置文件双重配置
- **增强的崩溃检测**：实时监控和分析应用崩溃
- **详细的测试报告**：HTML和JSON格式，包含丰富的测试信息
- **灵活的日志系统**：支持多级别日志和文件轮转
- **Page Object模式**：提高代码可维护性和复用性
- **多设备支持**：可配置不同设备ID进行测试

## 贡献指南
1. Fork本项目
2. 创建功能分支
3. 提交代码
4. 发起Pull Request

## 许可证
本项目采用MIT许可证。
