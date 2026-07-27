# Kea2 / Fastbot 配置（`configs/`）

Kea2 **仅读取本目录**（项目根下的 `configs/`）。首次缺失时 `main.py --engine kea2` 会自动执行 `kea2 init`。

## 力量镜需维护的文件

| 文件 | 说明 |
|------|------|
| `widget.block.py` | 控件黑名单，使用 `global_block_widgets(d)` 函数 |
| `abl.strings` | Activity 黑名单（每行一个 Activity 类名） |

`main.py` 跑 Kea2 时会传 `--act-blacklist-file /sdcard/.kea2/abl.strings`（**设备路径**），Kea2 从本目录读取 `abl.strings` 并 push。**切勿**传 Windows 本地路径，也**不能**只写 flag 不传值（会误解析 `propertytest`）。

## 勿改 / 慎改（`kea2 init` 自带）

`max.config`、`max.strings`、`teardown.py`、`version.json` 等由 Kea2 管理，一般无需动。

## 力量镜已屏蔽控件

`widget.block.py` 中已屏蔽 **Sleep / Fold / Retract rope** 等系统栏按钮，避免进入睡眠黑屏。

## 修改后

直接保存本目录下文件，下次跑测即生效，**无需**其他目录同步。
