# settings/ — 测试框架运行参数

本目录为 **Python 测试框架** 的配置代码，与 Kea2 的 `configs/`（Fastbot 探索策略）无关。

| 文件 | 说明 |
|------|------|
| `config.py` | `Config` 类：设备 ID、包名、引擎、性能阈值、场景过滤等 |
| `logging_config.py` | 日志输出（控制台 + `outputs/logs/monkey_test.log`） |

优先级：环境变量 > 项目根 `config.ini` > 代码默认值。

改 Fastbot 黑名单请编辑 **`configs/widget.block.py`**，不要改本目录。
