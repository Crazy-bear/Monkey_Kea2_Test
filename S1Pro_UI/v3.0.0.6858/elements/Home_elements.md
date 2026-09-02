# Home 页元素索引

- 来源：`Home_window_dump.xml`
- App 版本：3.0.0.6858
- 包名：`com.aeke.fitnessmirror`
- Activity：`—`

> 由 `python S1Pro_UI/dump_page_ui.py <Page>` 或 `parse_window_dump.py` 生成，勿手改。

## 快速对照（场景脚本常用）

| 功能 | 中文 | 定位常量建议 | resource-id | 可见文案 |
|------|------|--------------|-------------|----------|
| 随心练 | Free Workout | `START_BUTTON` | `grf_free_traing` | Free Workout |
| AI Coach | AI 教练 | `AI_COACH_BUTTON` | `grf_ai_coach` | AI Coach |
| 精品课程 | Courses | `COURSE_BUTTON` | `grf_all_course` | Courses |
| 运动测评 | Assessment | `ASSESSMENT_BUTTON` | `grf_evaluation` | Assessment |
| 运动计划 | Programs | `PLAN_BUTTON` | `grf_sports_plan` | Programs |
| 个人中心 | 头像 | `PROFILE_BUTTON` | `iv_head` | — |
| 首页 | 首页 | `HOME_TAB` | `tv_page_home` | Home |
| 娱乐 | 娱乐 | `LIFESTYLE_TAB` | `tv_life_style` | Lifestyle |

## 顶栏 / 导航

| resource-id | 文案 | 类型 | 可点 | bounds |
|-------------|------|------|------|--------|
| `ctl_main_title` | — | ViewGroup | 否 | `[0,0][1080,160]` |
| `iv_head` | — | ImageView | 是 | `[54,40][134,120]` |
| `tv_name` | hjx | TextView | 是 | `[166,56][209,104]` |
| `update_point` | — | View | 否 | `[217,56][229,68]` |
| `tv_page_home` | Home | TextView | 是 | `[670,50][830,110]` |
| `tv_life_style` | Lifestyle | TextView | 是 | `[860,50][1020,110]` |
| `top_strip` | 09:48 AM | TextView | 是 | `[470,8][610,61]` |
| `tv_name` | Mon | TextView | 否 | `[54,160][129,222]` |
| `tv_name` | Tue | TextView | 否 | `[129,160][215,222]` |
| `tv_name` | Wed | TextView | 否 | `[215,160][311,222]` |
| `tv_name` | Thu | TextView | 否 | `[311,160][398,222]` |
| `tv_name` | Today | TextView | 否 | `[398,160][514,222]` |
| `tv_name` | Sat | TextView | 否 | `[514,160][595,222]` |
| `tv_name` | Sun | TextView | 否 | `[595,160][682,222]` |

## Home · 随心练

| resource-id | 文案 | 类型 | 可点 | bounds |
|-------------|------|------|------|--------|
| `grf_free_traing` | — | FrameLayout | 是 | `[54,796][522,1184]` |
| — | Free Workout | TextView | 否 | `[94,828][347,884]` |

## Home · AI Coach

| resource-id | 文案 | 类型 | 可点 | bounds |
|-------------|------|------|------|--------|
| `grf_ai_coach` | — | FrameLayout | 是 | `[558,796][1026,972]` |
| — | AI Coach | TextView | 否 | `[598,840][731,888]` |

## Home · 精品课程

| resource-id | 文案 | 类型 | 可点 | bounds |
|-------------|------|------|------|--------|
| — | Custom Courses | TextView | 否 | `[94,892][303,932]` |
| `grf_all_course` | — | FrameLayout | 是 | `[558,1008][1026,1184]` |
| — | Courses | TextView | 否 | `[598,1052][719,1100]` |

## Home · 运动测评

| resource-id | 文案 | 类型 | 可点 | bounds |
|-------------|------|------|------|--------|
| `grf_evaluation` | — | FrameLayout | 是 | `[54,1220][522,1396]` |
| — | Assessment | TextView | 否 | `[94,1264][272,1312]` |

## Home · 运动计划

| resource-id | 文案 | 类型 | 可点 | bounds |
|-------------|------|------|------|--------|
| `tv_title` | Fitness Programs for You | TextView | 否 | `[54,320][609,385]` |
| `tv_start` | Join Program | TextView | 否 | `[54,465][305,545]` |
| `grf_sports_plan` | — | FrameLayout | 是 | `[558,1220][1026,1396]` |
| — | Programs | TextView | 否 | `[598,1264][741,1312]` |

## Home · Banner / 周历

| resource-id | 文案 | 类型 | 可点 | bounds |
|-------------|------|------|------|--------|
| `hsb_week` | — | FrameLayout | 否 | `[0,160][1080,660]` |
| `vp_banner` | — | FrameLayout | 否 | `[0,160][1080,660]` |
| `tv_sub_title` | Designed by AEKE Fitness Experts | TextView | 否 | `[54,393][430,433]` |
| `vv_courseVideo` | — | SimpleVideoView | 否 | `[564,180][1080,660]` |
| `tl_days` | — | HorizontalScrollView | 否 | `[54,160][682,248]` |
| `iv_more` | — | ImageView | 是 | `[970,176][1026,232]` |

## Home · 提醒条

| resource-id | 文案 | 类型 | 可点 | bounds |
|-------------|------|------|------|--------|
| `hsr_tips` | — | FrameLayout | 否 | `[0,660][1080,760]` |
| `ll_reminder` | — | LinearLayout | 否 | `[54,660][1026,760]` |
| `tv_msg` | Report is not ready yet. Please wait. | TextView | 否 | `[150,688][800,732]` |
| `iv_close` | — | ImageView | 是 | `[958,694][990,726]` |

## 底部指示

| resource-id | 文案 | 类型 | 可点 | bounds |
|-------------|------|------|------|--------|
| `viewpager` | — | ViewPager | 否 | `[0,160][1080,1920]` |
| `second_oval` | — | ImageView | 否 | `[514,1872][550,1888]` |
| `three_oval` | — | ImageView | 否 | `[566,1872][582,1888]` |

## 其他可点击

| resource-id | 文案 | 类型 | 可点 | bounds |
|-------------|------|------|------|--------|
| — | — | ViewGroup | 是 | `[0,160][1080,660]` |
| — | — | LinearLayout | 是 | `[54,160][129,248]` |
| — | — | LinearLayout | 是 | `[129,160][215,248]` |
| — | — | LinearLayout | 是 | `[215,160][311,248]` |
| — | — | LinearLayout | 是 | `[311,160][398,248]` |
| — | — | LinearLayout | 是 | `[514,160][595,248]` |
| — | — | LinearLayout | 是 | `[595,160][682,248]` |
| `tv_start` | Start | TextView | 是 | `[812,678][922,742]` |

## 其他

| resource-id | 文案 | 类型 | 可点 | bounds |
|-------------|------|------|------|--------|
| `action_bar_root` | — | LinearLayout | 否 | `[0,0][1080,1920]` |
| `android:id/content` | — | FrameLayout | 否 | `[0,0][1080,1920]` |
| `rl_top_container` | — | FrameLayout | 否 | `[0,160][1080,660]` |
| — | Just for You | TextView | 否 | `[598,888][726,928]` |
| — | Diverse Workouts | TextView | 否 | `[598,1100][790,1140]` |
| — | Know Yourself Better | TextView | 否 | `[94,1312][325,1352]` |
| — | Workout Plans | TextView | 否 | `[598,1312][757,1352]` |
| `statusbarutil_translucent_view` | — | View | 否 | `[0,0][1080,48]` |
