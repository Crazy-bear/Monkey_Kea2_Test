# Home_ControlPanel_WiFi 页元素索引

- 来源：`Home_ControlPanel_WiFi_window_dump.xml`
- App 版本：3.0.0.6858
- 包名：`com.aeke.fitnessmirror`
- Activity：`—`

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
| `rl_sys_wifi` | — | ViewGroup | 是 | `[354,160][1026,1346]` |
| `rv_sys_wifi` | — | RecyclerView | 否 | `[354,466][1026,1346]` |

## 控制栏 · 网络面板

| resource-id | 文案 | 类型 | 可点 | bounds |
|-------------|------|------|------|--------|
| `tv_wifi_title` | WLAN | TextView | 否 | `[643,160][738,296]` |
| `ctl_wifi_title_right` | — | ViewGroup | 是 | `[893,192][1026,265]` |
| `ctl_wifi_nomal` | — | ViewGroup | 否 | `[354,296][1026,1346]` |

## 控制栏 · 网络操作

| resource-id | 文案 | 类型 | 可点 | bounds |
|-------------|------|------|------|--------|
| `tv_wifi_refresh` | Refresh | TextView | 是 | `[382,198][505,258]` |
| `tv_wifi_delete_curr` | Forget | TextView | 是 | `[893,192][1006,265]` |

## 控制栏 · 当前连接

| resource-id | 文案 | 类型 | 可点 | bounds |
|-------------|------|------|------|--------|
| `ll_wifi_mine_item` | — | LinearLayout | 是 | `[354,296][1026,446]` |
| `ll_wifi_name_info` | — | LinearLayout | 否 | `[402,331][851,410]` |
| `tv_connected_name` | AEKE | TextView | 否 | `[402,331][484,374]` |
| `tv_connected_wifi_tag` | 5G | TextView | 否 | `[500,338][550,366]` |
| `tv_connect_statu` | Connected | TextView | 否 | `[402,382][503,410]` |
| `iv_connect_wifi_level` | — | ImageView | 否 | `[939,351][978,391]` |

## 控制栏 · WiFi 列表

| resource-id | 文案 | 类型 | 可点 | bounds |
|-------------|------|------|------|--------|
| `ll_wifi_item` | — | LinearLayout | 是 | `[354,466][1026,570]` |
| `name_tv` | AEKE-R&D | TextView | 否 | `[402,496][567,539]` |
| `tv_wifi_tag` | 5G | TextView | 否 | `[583,503][633,531]` |
| `lock_iv` | — | ImageView | 否 | `[866,500][902,536]` |
| `wifi_iv` | — | ImageView | 否 | `[938,498][978,538]` |
| `ll_wifi_item` | — | LinearLayout | 是 | `[354,570][1026,674]` |
| `name_tv` | AEKE-Test | TextView | 否 | `[402,600][558,643]` |
| `tv_wifi_tag` | 5G | TextView | 否 | `[574,607][624,635]` |
| `lock_iv` | — | ImageView | 否 | `[866,604][902,640]` |
| `wifi_iv` | — | ImageView | 否 | `[938,602][978,642]` |
| `ll_wifi_item` | — | LinearLayout | 是 | `[354,674][1026,778]` |
| `name_tv` | AEKE-US | TextView | 否 | `[402,704][543,747]` |
| `tv_wifi_tag` | 5G | TextView | 否 | `[559,711][609,739]` |
| `lock_iv` | — | ImageView | 否 | `[866,708][902,744]` |
| `wifi_iv` | — | ImageView | 否 | `[938,706][978,746]` |
| `ll_wifi_item` | — | LinearLayout | 是 | `[354,778][1026,882]` |
| `name_tv` | CT | TextView | 否 | `[402,808][443,851]` |
| `tv_wifi_tag` | 2.4G | TextView | 否 | `[459,815][526,843]` |
| `lock_iv` | — | ImageView | 否 | `[866,812][902,848]` |
| `wifi_iv` | — | ImageView | 否 | `[938,810][978,850]` |
| `ll_wifi_item` | — | LinearLayout | 是 | `[354,882][1026,986]` |
| `name_tv` | CT-5G | TextView | 否 | `[402,912][498,955]` |
| `tv_wifi_tag` | 5G | TextView | 否 | `[514,919][564,947]` |
| `lock_iv` | — | ImageView | 否 | `[866,916][902,952]` |
| `wifi_iv` | — | ImageView | 否 | `[938,914][978,954]` |
| `ll_wifi_item` | — | LinearLayout | 是 | `[354,986][1026,1090]` |
| `name_tv` | aeke-t1 | TextView | 否 | `[402,1016][521,1059]` |
| `tv_wifi_tag` | 5G | TextView | 否 | `[537,1023][587,1051]` |
| `wifi_iv` | — | ImageView | 否 | `[938,1018][978,1058]` |
| `ll_wifi_item` | — | LinearLayout | 是 | `[354,1090][1026,1194]` |
| `name_tv` | Guest | TextView | 否 | `[402,1120][490,1163]` |
| `tv_wifi_tag` | 2.4G | TextView | 否 | `[506,1127][573,1155]` |
| `lock_iv` | — | ImageView | 否 | `[866,1124][902,1160]` |
| `wifi_iv` | — | ImageView | 否 | `[938,1122][978,1162]` |
| `ll_wifi_item` | — | LinearLayout | 是 | `[354,1194][1026,1298]` |
| `name_tv` | MAXHUB-099 | TextView | 否 | `[402,1224][616,1267]` |
| `tv_wifi_tag` | 5G | TextView | 否 | `[632,1231][682,1259]` |
| `lock_iv` | — | ImageView | 否 | `[866,1228][902,1264]` |
| `wifi_iv` | — | ImageView | 否 | `[938,1226][978,1266]` |
| `ll_wifi_item` | — | LinearLayout | 是 | `[354,1298][1026,1346]` |
| `name_tv` | ChinaNet-tecP | TextView | 否 | `[402,1328][623,1346]` |
| `tv_wifi_tag` | 5G | TextView | 否 | `[639,1335][689,1346]` |
| `lock_iv` | — | ImageView | 否 | `[866,1332][902,1346]` |
| `wifi_iv` | — | ImageView | 否 | `[938,1330][978,1346]` |
