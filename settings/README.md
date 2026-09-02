# settings/ — 测试框架运行参数

本目录为 **Python 测试框架** 的配置代码，与 Kea2 的 `configs/`（Fastbot 探索策略）无关。

| 文件 | 说明 |
|------|------|
| `config.py` | `Config` 类：设备 ID、包名、引擎、性能阈值、场景过滤等 |
| `logging_config.py` | 日志输出（控制台 + `outputs/logs/monkey_test.log`） |

优先级：命令行参数 > 环境变量 > 项目根 `config.ini` > 代码默认值。

| config.ini 键 | 环境变量 | 说明 |
|---------------|----------|------|
| `DEVICE_ID` | `MONKEY_DEVICE_ID` | 设备 ID |
| `PACKAGE_NAME` | `MONKEY_PACKAGE_NAME` | 应用包名 |
| `TEST_ENGINE` | `TEST_ENGINE` | `kea2` / `monkey` |
| `KEA2_RUNNING_MINUTES` | `KEA2_RUNNING_MINUTES` | Kea2 时长（分钟） |
| `SCENARIOS` | `KEA2_SCENARIOS` | 场景别名或 `all` |
| `OUTPUT_DIR` / `OUTPUT` | `KEA2_OUTPUT_DIR` | 产出根目录 |

复制 `config.ini.example` 为 `config.ini` 后修改；`config.ini` 可加入 `.gitignore` 避免提交本机设备 ID。

改 Fastbot 黑名单请编辑 **`configs/widget.block.py`**，不要改本目录。
