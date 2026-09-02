# Home_ControlPanel_LED 页元素索引

- 来源：`Home_ControlPanel_LED_window_dump.xml`
- App 版本：3.0.0.6858
- 包名：`com.aeke.fitnessmirror`
- Activity：`com.aeke.fitnessmirror.home.MainActivity`

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
| `sys_led_rl` | — | ViewGroup | 否 | `[406,160][1026,1232]` |
| `sys_led_title_tv` | Lighting | TextView | 否 | `[654,200][778,256]` |
| `sys_led_brightness_tv` | Brightness | TextView | 否 | `[454,296][550,324]` |
| `sys_led_mode_tv` | Mode | TextView | 否 | `[454,456][506,484]` |
| `sys_led_mode_rv` | — | RecyclerView | 否 | `[454,516][978,612]` |
| `sys_led_color_tv` | Color | TextView | 否 | `[454,660][503,688]` |
| `sys_led_color_rv` | — | RecyclerView | 否 | `[454,720][978,1184]` |

## 控制栏 · 氛围灯面板

| resource-id | 文案 | 类型 | 可点 | bounds |
|-------------|------|------|------|--------|
| `switch_btn_led` | — | View | 是 | `[882,200][978,256]` |

## 控制栏 · 氛围灯亮度

| resource-id | 文案 | 类型 | 可点 | bounds |
|-------------|------|------|------|--------|
| `led_brightness_progress_container` | — | FrameLayout | 否 | `[454,356][978,408]` |
| `v_led_brightness_seekbar_bottom` | — | View | 否 | `[454,364][978,400]` |
| `seekbar_led_brightness` | — | SeekBar | 否 | `[454,364][978,400]` |
| `v_led_brightness_seekbar_left` | — | View | 否 | `[454,364][490,400]` |

## 控制栏 · 氛围灯模式

| resource-id | 文案 | 类型 | 可点 | bounds |
|-------------|------|------|------|--------|
| `tv_mode_name` | Constant | TextView | 否 | `[529,540][629,588]` |
| `tv_mode_name` | Breath | TextView | 否 | `[816,540][890,588]` |

## 控制栏 · 氛围灯颜色

| resource-id | 文案 | 类型 | 可点 | bounds |
|-------------|------|------|------|--------|
| `iv_selected` | — | ImageView | 否 | `[570,736][602,768]` |
| `tv_color_name` | White | TextView | 否 | `[454,820][618,864]` |
| `tv_color_name` | Red | TextView | 否 | `[634,820][798,864]` |
| `tv_color_name` | Orange | TextView | 否 | `[813,820][977,864]` |
| `tv_color_name` | Yellow | TextView | 否 | `[454,980][618,1024]` |
| `tv_color_name` | Green | TextView | 否 | `[634,980][798,1024]` |
| `tv_color_name` | Cyan | TextView | 否 | `[813,980][977,1024]` |
| `tv_color_name` | Blue | TextView | 否 | `[454,1140][618,1184]` |
| `tv_color_name` | Purple | TextView | 否 | `[634,1140][798,1184]` |
| `tv_color_name` | Flowing | TextView | 否 | `[813,1140][977,1184]` |

## 其他可点击

| resource-id | 文案 | 类型 | 可点 | bounds |
|-------------|------|------|------|--------|
| — | — | ViewGroup | 是 | `[454,516][704,612]` |
| — | — | ViewGroup | 是 | `[728,516][978,612]` |
| — | — | ViewGroup | 是 | `[454,720][618,864]` |
| — | — | ViewGroup | 是 | `[634,720][798,864]` |
| — | — | ViewGroup | 是 | `[813,720][977,864]` |
| — | — | ViewGroup | 是 | `[454,880][618,1024]` |
| — | — | ViewGroup | 是 | `[634,880][798,1024]` |
| — | — | ViewGroup | 是 | `[813,880][977,1024]` |
| — | — | ViewGroup | 是 | `[454,1040][618,1184]` |
| — | — | ViewGroup | 是 | `[634,1040][798,1184]` |
| — | — | ViewGroup | 是 | `[813,1040][977,1184]` |
