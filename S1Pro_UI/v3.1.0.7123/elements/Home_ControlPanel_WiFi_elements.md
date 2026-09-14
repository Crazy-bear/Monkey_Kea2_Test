# Home_ControlPanel_WiFi 页元素索引

- 来源：`Home_ControlPanel_WiFi_window_dump.xml`
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
| `rl_sys_wifi` | — | ViewGroup | 是 | `[354,160][1026,1346]` |
| `rv_sys_wifi` | — | RecyclerView | 否 | `[354,466][1026,1346]` |

## 控制栏 · 网络面板

| resource-id | 文案 | 类型 | 可点 | bounds |
|-------------|------|------|------|--------|
| `tv_wifi_title` | WLAN | TextView | 否 | `[643,160][738,296]` |
| `ctl_wifi_title_right` | — | ViewGroup | 是 | `[893,192][1026,265]` |
| `ctl_wifi_nomal` | — | ViewGroup | 否 | `[354,296][1026,1346]` |
| `tv_wifi_title` | My Networks | TextView | 否 | `[354,466][1026,542]` |
| `tv_wifi_title` | Other Networks | TextView | 否 | `[354,750][1026,826]` |

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
| `tv_connected_name` | AEKE-R&D | TextView | 否 | `[402,331][567,374]` |
| `tv_connected_wifi_tag` | 5G | TextView | 否 | `[583,338][633,366]` |
| `tv_connect_statu` | Connected | TextView | 否 | `[402,382][503,410]` |
| `iv_connect_wifi_level` | — | ImageView | 否 | `[939,351][978,391]` |

## 控制栏 · WiFi 列表

| resource-id | 文案 | 类型 | 可点 | bounds |
|-------------|------|------|------|--------|
| `ll_wifi_item` | — | LinearLayout | 是 | `[354,542][1026,646]` |
| `name_tv` | AEKE | TextView | 否 | `[402,572][484,615]` |
| `tv_wifi_tag` | 5G | TextView | 否 | `[500,579][550,607]` |
| `lock_iv` | — | ImageView | 否 | `[866,576][902,612]` |
| `wifi_iv` | — | ImageView | 否 | `[938,574][978,614]` |
| `ll_wifi_item` | — | LinearLayout | 是 | `[354,646][1026,750]` |
| `name_tv` | AEKE-R&D | TextView | 否 | `[402,676][567,719]` |
| `tv_wifi_tag` | 5G | TextView | 否 | `[583,683][633,711]` |
| `lock_iv` | — | ImageView | 否 | `[866,680][902,716]` |
| `wifi_iv` | — | ImageView | 否 | `[938,678][978,718]` |
| `ll_wifi_item` | — | LinearLayout | 是 | `[354,826][1026,930]` |
| `name_tv` | CT | TextView | 否 | `[402,856][443,899]` |
| `tv_wifi_tag` | 2.4G | TextView | 否 | `[459,863][526,891]` |
| `lock_iv` | — | ImageView | 否 | `[866,860][902,896]` |
| `wifi_iv` | — | ImageView | 否 | `[938,858][978,898]` |
| `ll_wifi_item` | — | LinearLayout | 是 | `[354,930][1026,1034]` |
| `name_tv` | CT-5G | TextView | 否 | `[402,960][498,1003]` |
| `tv_wifi_tag` | 5G | TextView | 否 | `[514,967][564,995]` |
| `lock_iv` | — | ImageView | 否 | `[866,964][902,1000]` |
| `wifi_iv` | — | ImageView | 否 | `[938,962][978,1002]` |
| `ll_wifi_item` | — | LinearLayout | 是 | `[354,1034][1026,1138]` |
| `name_tv` | AEKE-Test | TextView | 否 | `[402,1064][558,1107]` |
| `tv_wifi_tag` | 5G | TextView | 否 | `[574,1071][624,1099]` |
| `lock_iv` | — | ImageView | 否 | `[866,1068][902,1104]` |
| `wifi_iv` | — | ImageView | 否 | `[938,1066][978,1106]` |
| `ll_wifi_item` | — | LinearLayout | 是 | `[354,1138][1026,1242]` |
| `name_tv` | AEKE-US | TextView | 否 | `[402,1168][543,1211]` |
| `tv_wifi_tag` | 5G | TextView | 否 | `[559,1175][609,1203]` |
| `lock_iv` | — | ImageView | 否 | `[866,1172][902,1208]` |
| `wifi_iv` | — | ImageView | 否 | `[938,1170][978,1210]` |
| `ll_wifi_item` | — | LinearLayout | 是 | `[354,1242][1026,1346]` |
| `name_tv` | ChinaNet-tecP | TextView | 否 | `[402,1272][622,1315]` |
| `tv_wifi_tag` | 5G | TextView | 否 | `[638,1279][688,1307]` |
| `lock_iv` | — | ImageView | 否 | `[866,1276][902,1312]` |
| `wifi_iv` | — | ImageView | 否 | `[938,1274][978,1314]` |

## 其他可点击

| resource-id | 文案 | 类型 | 可点 | bounds |
|-------------|------|------|------|--------|
| `container_touch_2` | — | ViewGroup | 是 | `[938,560][1026,648]` |
| `layout_contract_2` | — | ViewGroup | 是 | `[938,560][1026,648]` |
| `iv_contract_album_img_2` | — | ImageView | 是 | `[938,560][1026,648]` |
