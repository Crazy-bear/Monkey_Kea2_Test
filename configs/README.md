# Kea2 / Fastbot 配置（`configs/`）

Kea2 **仅读取本目录**（项目根下的 `configs/`）。首次缺失时 `main.py --engine kea2` 会自动执行 `kea2 init`。

## 【S1Pro 力量镜】需维护的文件

| 文件 | 说明 |
|------|------|
| `widget.block.py` | 控件黑名单；可读 `KEA2_LOCK_MODULES`：未锁 lifestyle 屏蔽 Lifestyle Tab，未锁 home 屏蔽 Home Tab；锁 course 时在列表根页屏蔽返回 Home |
| `abl.strings` | Activity **黑名单**（全量 `--scenarios all` 时使用） |
| `awl.strings` | Activity **白名单**（指定模块时由 `module_catalog` 自动生成覆盖） |

### 黑名单 vs 白名单（互斥）

Kea2 **不能同时**开启黑名单与白名单：

| `--scenarios` | Fastbot 参数 | 本地文件 |
|---------------|--------------|----------|
| `all` | `--act-blacklist-file /sdcard/.kea2/abl.strings` | `abl.strings` |
| `course` / `course,suixinlian` 等 | `--act-whitelist-file /sdcard/.kea2/awl.strings` | 自动写 `awl.strings` |

`main.py` 传的是**设备路径**，Kea2 从本目录读取对应文件并 push。**切勿**传 Windows 本地路径，也**不能**只写 flag 不传值（会误解析 `propertytest`）。

模块白名单由 [`orchestrator/module_catalog.py`](../orchestrator/module_catalog.py) 维护；始终包含 `MainActivity`（预登录停在 Home）。登录/屏保 Activity 不进白名单，等价于继续屏蔽。

## 勿改 / 慎改（`kea2 init` 自带）

`max.config`、`max.strings`、`teardown.py`、`version.json` 等由 Kea2 管理，一般无需动。

## 【S1Pro 力量镜】已屏蔽控件

`widget.block.py` 中已屏蔽 **Sleep / Fold / Retract rope** 等系统栏按钮，避免进入睡眠黑屏；对 Sleep/Wallpaper 等使用 **`global_block_tree`**（含子 ImageView），避免 Fastbot 点中子节点绕过屏蔽；并屏蔽 **登录页 Join / Offline Mode**，且 `global_block_tree` 屏蔽登录成员区与屏保图。

另：折叠态 **`rl_control_root`**（约 2px 高、仍 clickable）会被条件屏蔽，否则 Fastbot 日志狂刷 `Sending monkeyEvent` / CLICK，画面几乎不动；控制中心展开（全屏）时不挡。

未锁 **`floating_touch`** 时整块屏蔽悬浮 Touch（`container_touch_2` 等），避免随机事件被悬浮球吸走。

**Sleep / Wallpaper** 用 `@precondition` 强制屏蔽（不能只靠 `global_block_*`）：悬浮层上的 Sleep 一点即设备休眠黑屏，近期跑测日志里确有 `id/sleep` / `id/screen` 被点到。

`abl.strings` 已列入 `LoginEntryActivity`、`ScreenProjectShowActivity`。掉线恢复由属性基类 `ensure_logged_in_home()`（点屏退屏保 → 点 Admin）完成。

## 修改后

直接保存本目录下文件，下次跑测即生效，**无需**其他目录同步。
