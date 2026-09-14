# DataCenterDetail 页元素索引

- 来源：`DataCenterDetail_window_dump.xml`
- App 版本：3.1.0.7123
- 包名：`com.aeke.fitnessmirror`
- Activity：`com.aeke.fitnessmirror.activity.TrainingDataCentreActivity`

> 由 `python S1Pro_UI/dump_page_ui.py <Page>` 或 `parse_window_dump.py` 生成，勿手改。

## 顶栏 / 导航

| resource-id | 文案 | 类型 | 可点 | bounds |
|-------------|------|------|------|--------|
| `nav` | — | ViewGroup | 否 | `[0,0][1080,188]` |
| `ivLeftIcon` | — | ImageView | 是 | `[54,46][150,142]` |
| `titleScrollView` | — | HorizontalScrollView | 否 | `[405,62][676,127]` |
| `tvTitle` | Data Center | TextView | 否 | `[405,62][676,127]` |

## 数据中心 · 周期切换

| resource-id | 文案 | 类型 | 可点 | bounds |
|-------------|------|------|------|--------|
| `iv_date_left` | — | ImageView | 是 | `[66,210][102,246]` |
| `tv_date_range` | 08.31-09.06 | TextView | 否 | `[130,196][354,260]` |
| `iv_date_right` | — | ImageView | 否 | `[382,210][418,246]` |
| `tv_this_week` | — | FrameLayout | 否 | `[821,192][1026,264]` |
| `container` | — | ViewGroup | 是 | `[821,192][1026,264]` |
| `text` | This week | TextView | 否 | `[869,206][978,250]` |
| `container_touch_2` | — | ViewGroup | 是 | `[938,560][1026,648]` |

## 数据中心 · 汇总统计

| resource-id | 文案 | 类型 | 可点 | bounds |
|-------------|------|------|------|--------|
| `ll_total_infos` | — | ViewGroup | 否 | `[54,296][1026,486]` |
| `tv_session_num` | 1 | TextView | 否 | `[102,340][133,405]` |
| `tv_session_unit` | Session | TextView | 否 | `[143,366][227,399]` |
| `tv_duration` | 28 | TextView | 否 | `[340,340][402,405]` |
| `tv_duration_unit` | min | TextView | 否 | `[412,366][453,399]` |
| `tv_total_volum` | - | TextView | 否 | `[590,340][612,405]` |
| `tv_total_kcal` | 71 | TextView | 否 | `[828,340][890,405]` |
| `tv_total_kcal_unit` | kcal | TextView | 否 | `[900,364][944,397]` |
| `tv_workout_txt` | Workouts | TextView | 否 | `[102,409][208,442]` |
| `tv_duration_txt` | Duration | TextView | 否 | `[340,409][435,442]` |
| — | Volume | TextView | 否 | `[590,409][673,442]` |
| — | Calories | TextView | 否 | `[828,409][917,442]` |
| `tv_progress_volum` | Volume | TextView | 是 | `[747,572][865,620]` |
| `tv_progress_calories` | Calories | TextView | 是 | `[865,572][988,620]` |

## 数据中心 · Progress

| resource-id | 文案 | 类型 | 可点 | bounds |
|-------------|------|------|------|--------|
| `ctl_workout_progress` | — | ViewGroup | 否 | `[54,518][1026,942]` |
| `tv_progress_title` | Progress | TextView | 否 | `[86,566][217,614]` |
| `wrbv_week_data` | — | View | 否 | `[86,646][994,894]` |

## 数据中心 · Preferences

| resource-id | 文案 | 类型 | 可点 | bounds |
|-------------|------|------|------|--------|
| `ctl_workout_preferences` | — | ViewGroup | 否 | `[54,1807][1026,1920]` |
| `tv_preferences_title` | Preferences | TextView | 否 | `[86,1855][262,1903]` |

## 其他可点击

| resource-id | 文案 | 类型 | 可点 | bounds |
|-------------|------|------|------|--------|
| `iv_muscle_status_info` | Status Info | ImageView | 是 | `[310,1018][350,1058]` |
| `rl_control_root` | — | RelativeLayout | 是 | `[0,2][1080,4]` |
| `layout_contract_2` | — | ViewGroup | 是 | `[938,560][1026,648]` |
| `iv_contract_album_img_2` | — | ImageView | 是 | `[938,560][1026,648]` |

## 其他

| resource-id | 文案 | 类型 | 可点 | bounds |
|-------------|------|------|------|--------|
| `action_bar_root` | — | LinearLayout | 否 | `[0,0][1080,1920]` |
| `android:id/content` | — | FrameLayout | 否 | `[0,0][1080,1920]` |
| `ctl_muscle_status` | — | ViewGroup | 否 | `[54,974][1026,1775]` |
| `tv_muscle_status_title` | Muscle Status | TextView | 否 | `[86,1014][294,1062]` |
| `muscle_status_view` | — | LinearLayout | 否 | `[86,1126][994,1727]` |
| — | Shoulders Recovered 100; Chest Recovered 100; Back Recovered 100; Arms Recovered 100; Core Recovered 100; Glutes Recovered 100; Legs Recovered 100 | LinearLayout | 否 | `[86,1126][994,1646]` |
| — | Fatigued | TextView | 否 | `[303,1694][401,1727]` |
| — | Recovering | TextView | 否 | `[493,1694][615,1727]` |
| — | Recovered | TextView | 否 | `[707,1694][821,1727]` |
| `statusbarutil_translucent_view` | — | View | 否 | `[0,0][1080,48]` |
