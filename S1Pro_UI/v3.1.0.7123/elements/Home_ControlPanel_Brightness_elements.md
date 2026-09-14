# Home_ControlPanel_Brightness 页元素索引

- 来源：`Home_ControlPanel_Brightness_window_dump.xml`
- App 版本：3.1.0.7123
- 包名：`com.aeke.fitnessmirror`
- Activity：`-`

> 由 `python S1Pro_UI/dump_page_ui.py <Page>` 或 `parse_window_dump.py` 生成，勿手改。

## 控制栏 · 根与遮罩

| resource-id | 文案 | 类型 | 可点 | bounds |
|-------------|------|------|------|--------|
| `rl_control_root` | — | RelativeLayout | 是 | `[0,0][1080,1920]` |
| `v_overlay_mask` | — | View | 是 | `[0,160][1080,1920]` |

## 控制栏 · 系统菜单

| resource-id | 文案 | 类型 | 可点 | bounds |
|-------------|------|------|------|--------|
| `sys_menu_ll` | — | ViewGroup | 是 | `[0,0][1080,160]` |
| `switch_rg` | — | RadioGroup | 否 | `[562,48][1026,112]` |
| `sys_bright` | — | RadioButton | 是 | `[562,48][626,112]` |
| `sys_voice` | — | RadioButton | 是 | `[662,48][726,112]` |
| `sys_ble` | — | RadioButton | 是 | `[762,48][826,112]` |
| `sys_wifi` | — | RadioButton | 是 | `[862,48][926,112]` |
| `sys_led` | — | RadioButton | 是 | `[962,48][1026,112]` |

## 控制栏 · 亮度面板

| resource-id | 文案 | 类型 | 可点 | bounds |
|-------------|------|------|------|--------|
| `sys_progress_ll` | — | LinearLayout | 是 | `[354,160][1026,436]` |
| `sys_bar_progress_title` | Brightness | TextView | 否 | `[610,200][771,256]` |
| `sys_progress_bar_ll` | — | LinearLayout | 否 | `[402,296][978,352]` |
| `sys_progress_tv` | Screen | TextView | 否 | `[402,310][538,338]` |
| `v_system_seekbar_bottom` | — | View | 否 | `[564,306][972,342]` |
| `sys_progress_bar` | 37.0 | SeekBar | 否 | `[564,306][972,342]` |
| `v_system_seekbar_left` | — | View | 否 | `[564,306][600,342]` |

## 其他可点击

| resource-id | 文案 | 类型 | 可点 | bounds |
|-------------|------|------|------|--------|
| `container_touch_2` | — | ViewGroup | 是 | `[938,560][1026,648]` |
| `layout_contract_2` | — | ViewGroup | 是 | `[938,560][1026,648]` |
| `iv_contract_album_img_2` | — | ImageView | 是 | `[938,560][1026,648]` |
