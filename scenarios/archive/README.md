# 已归档的属性脚本

以下脚本含高概率导航/进退链路，与「Fastbot 为主、属性只做围栏+极简哨兵」冲突，故移出 `scenarios/` 根目录，避免 `--scenarios all` 的 `test_*.py` discover 加载。

| 文件 | 原模块别名 |
|------|------------|
| `test_settings.py` | `settings` |
| `test_control_panel.py` | `control_panel` / `control` |
| `test_data_center.py` | `data_center` / `effort` |
| `test_schedule.py` | `schedule` / `calendar` |
| `test_profile_plan.py` | `profile` |
| `test_floating_touch.py` | `floating_touch` / `touch` |

启用方式：拷回 `scenarios/` 并恢复 `settings/config.py` 中对应 `SCENARIO_ALIASES` 指向该文件。

当前归档模块的别名仍映射到 `scenarios/lock_fence.py`（非 `test_*`），因此：
- `--scenarios settings` 等仍可做 **模块锁 + 基类围栏**
- `--scenarios all` **不会**加载这些归档抽检

业务规避（Sleep / 悬浮球等）仍由 `configs/widget.block.py` 负责，不依赖本目录脚本。
