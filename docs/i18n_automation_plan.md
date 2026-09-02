# 力量镜多语言（i18n）适配自动化检测方案

> **状态**：待执行（方案已归档，尚未落地代码）  
> **创建日期**：2026-07-30  
> **关联工具**：`S1Pro_UI/dump_page_ui.py`、`S1Pro_UI/parse_window_dump.py`  
> **App 包名**：`com.aeke.fitnessmirror`

---

## 1. 背景与目标

力量镜项目支持 **14 种语言**。现有 UI dump 流程已能稳定产出 **resource-id + 可见文案 + bounds** 的结构化数据，可在此基础上扩展多语言适配检测。

**核心思路**：「Dump UI + 规则校验 + 基线对照」

- 在同一页面、同一 `resource-id` 上，对比各语言的文案与布局是否合格
- 比纯 Monkey/Kea2 随机探索更适合做 i18n 回归
- 新版本发版后重跑，diff 即可发现退化

---

## 2. 检测维度

| 维度 | 检测方式 | 说明 |
|------|----------|------|
| **翻译覆盖率** | rid 维度：baseline 有文案，目标语言为空/仍是英文 | 漏翻、未加载语言包 |
| **错语言残留** | 脚本检测：英文 locale 出现中文、日文 locale 出现拉丁文等 | 混语、fallback 错误 |
| **文案完整性** | 出现 `???`、占位符 `{0}`、资源 key（如 `home_title`） | 字符串资源缺失 |
| **布局适配** | bounds 宽度 vs 文案长度；TextView 是否被裁切（`…` 或 bounds 贴边） | 德语/法语等长文案溢出 |
| **RTL 适配**（若有阿拉伯语等） | 对比 LTR/RTL 下关键控件 bounds 镜像关系 | 阿拉伯语等 |
| **结构一致性** | 各语言 dump 的 rid 集合 diff | 某语言缺控件、多控件 |
| **动态内容隔离** | 排除用户名、时间、数字、版本号 | 避免误报（如 `tv_name`、时间戳） |

### Dump UI 无法覆盖（需标注为人工/截图/OCR）

- 图片内嵌文字、视频字幕
- 纯 Canvas/自定义绘制文字（不在 accessibility tree 里）
- 字体渲染美感、行距微调

---

## 3. 整体架构

```
┌─────────────────────────────────────────────────────────┐
│  1. 语言切换（ADB / Settings 内切换）                      │
└───────────────────────┬─────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────┐
│  2. 页面导航（复用 pages/ + 现有场景脚本导航到各 Tab）      │
└───────────────────────┬─────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────┐
│  3. dump_page_ui.py（扩展 --locale / --lang）            │
│     → S1Pro_UI/{version}/i18n/{lang}/window_dump/*.xml   │
└───────────────────────┬─────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────┐
│  4. i18n_checker.py（新增）                              │
│     - 解析 XML → 按 rid 建文案索引                        │
│     - 与 baseline（如 en）对照                           │
│     - 规则引擎：空文案 / 混语 / 溢出 / rid 缺失           │
└───────────────────────┬─────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────┐
│  5. 报告：14 语言 × N 页面 矩阵 + 问题清单 + CI 门禁       │
└─────────────────────────────────────────────────────────┘
```

### 建议目录结构

```
S1Pro_UI/v3.0.0.6858/
├── i18n/
│   ├── baseline/          # en-US 基线
│   │   └── window_dump/Home_window_dump.xml
│   ├── zh-CN/
│   ├── zh-TW/
│   ├── ja/
│   └── ... (共 14 种)
├── i18n_catalog/          # 自动生成：rid → 各语言文案对照表
│   └── Home_strings.json
└── reports/
    └── i18n_report_v3.0.0.6858.html
```

---

## 4. 语言切换策略

### 方案 A：App 内 Settings → Language（推荐）

- 与产品实际 i18n 路径一致（读 App 语言包，不是系统 locale）
- 流程：Profile → Settings → Language → 选语言 → 重启/刷新 → 回到 Home
- 需在 Settings 页 dump 一次 Language 列表，建立 **语言名 ↔ locale** 映射（如「简体中文」「English」）

### 方案 B：ADB 改系统 locale（辅助）

```bash
adb shell settings put system system_locales zh-CN
adb shell am broadcast -a android.intent.action.LOCALE_CHANGED
```

- 适合验证「跟随系统语言」逻辑
- 若 App 有独立语言设置，可能与方案 A 不一致，需分开测

**建议**：以 **方案 A 为主**，方案 B 作为补充场景（若产品支持「跟随系统」选项）。

### 14 种语言列表（待产品确认后填入）

```yaml
# settings/i18n.yaml（待创建）
languages:
  - code: en-US
    name: English
    script: latin
    baseline: true
  - code: zh-CN
    name: 简体中文
    script: han
  # ... 其余 12 种语言待补充
```

---

## 5. 页面覆盖范围

沿用现有 dump 页面清单：

| 模块 | 页面 | 优先级 |
|------|------|--------|
| 主流程 | Home、Lifestyle、Profile | P0 |
| 核心业务 | FreeWorkout、Course、Assessment、Programs、AICoach | P0 |
| 次级 | Schedule、DataCenterDetail、ControlPanel 系列 | P1 |

- **P0**：14 语言全量必测
- **P1**：抽样（建议 en / zh-CN / de / ar，代表长短文案 + RTL）

---

## 6. 基线建立与对照逻辑

### Step 1：建立 baseline（建议 en-US）

对 P0 页面执行一次 dump，生成 catalog：

```json
{
  "Home": {
    "grf_free_traing": { "text": "", "child_text": "Free Workout", "bounds": "..." },
    "tv_page_home": { "text": "Home", "bounds": "..." }
  }
}
```

- **定位键**：优先 `resource-id`；无 rid 的用 `(class, bounds 近似区域)` 作弱键
- **排除列表（DYNAMIC_RIDS）**：`tv_name`（用户名）、`top_strip`（时间）、版本号、纯数字

### Step 2：各语言 dump 后自动对比

对每个 `(page, rid)`：

1. **must_translate**：baseline 有非空英文文案 → 目标语言不能为空，且不能等于 baseline（专有名词白名单除外）
2. **script_check**：ja 应含假名/汉字、ko 含韩文、ar 含阿拉伯字符等
3. **overflow_check**：`text_width_est > bounds_width * 0.95` 或 text 以 `…` 结尾
4. **layout_shift**：同 rid 的 bounds 高度/宽度变化超过阈值（如 ±30%）→ 可能换行或挤压

### 专有名词白名单（I18N_WHITELIST，示例）

```
AI Coach, AEKE, Bluetooth, WiFi, WLAN, QR Code, APP, 4K UHD
```

---

## 7. 自动化执行流程

```
for lang in 14_languages:
    switch_language(lang)
    wait_app_ready()
    for page in P0_PAGES:
        navigate_to(page)      # 复用 pages/ + 场景导航
        dump_page_ui(page, locale=lang)

run i18n_checker --baseline en --compare-all
generate report
```

### 耗时优化

- 语言切换后批量 dump，减少冷启动
- P1 页面按语言抽样（4 种代表语言）
- 失败重试 1 次；截图存档便于人工复核
- 单次全量约 2–4 小时（14 语言 × ~15 页面）

---

## 8. 与现有工程集成

| 层级 | 做法 |
|------|------|
| **工具层** | 扩展 `dump_page_ui.py` 增加 `--locale`；新增 `S1Pro_UI/i18n_checker.py` |
| **配置层** | `settings/i18n.yaml`：14 语言 code、显示名、脚本规则、白名单词条 |
| **测试层** | `tests/test_i18n_checker.py`：用已有 XML fixture 做离线 pytest（无需设备） |
| **CI 层** | 独立 Jenkins Job「i18n-regression」，与 Kea2 稳定性测试解耦 |
| **Page Object** | 导航继续用 **resource-id**；检测层单独维护 **rid→各语言期望文案** 表 |

### 已知需改造点

`pages/profile_page.py` 中 `MENU_LABELS = ("Profile", "Settings", ...)` 等 **硬编码英文** 在多语言导航脚本里需改成 rid 或配置化，否则自动化切语言后会导航失败。

---

## 9. 报告示例

### 语言 × 页面 热力矩阵

```
           Home  Course  Profile  ...
zh-CN      ✅     ✅      ⚠️(1)
de         ✅     ❌(3)   ✅
ar         ⚠️(2)  ✅      ✅
...
```

### 问题列表示例

- `[de][Course][tv_difficult_desc]` 文案溢出 bounds `[54,800][200,830]`
- `[ja][Home][tv_start]` 仍为英文 `Join Program`（疑似漏翻）
- `[zh-CN][Profile][name_tv]` 混语：Settings 旁出现英文 `Help`

---

## 10. 分阶段实施计划

| 阶段 | 内容 | 产出 | 预估周期 |
|------|------|------|----------|
| **Phase 0** | 确认 14 语言列表 + Language 设置页 dump + 切换路径 | 语言配置 YAML | 0.5d |
| **Phase 1** | 扩展 dump 支持 locale 目录；P0 页面 × en 基线 | baseline catalog | 1d |
| **Phase 2** | 半自动：人工切语言 + 脚本批量 dump | 14×P0 XML | 1d |
| **Phase 3** | `i18n_checker` + pytest + HTML 报告 | 可 CI 的检测器 | 2d |
| **Phase 4** | 全自动语言切换 + 导航 + 门禁阈值 | 完整流水线 | 2–3d |
| **Phase 5**（可选） | 关键 Banner 截图 + OCR | 图片内嵌文字检测 | 2d |

---

## 11. 风险与应对

| 风险 | 应对 |
|------|------|
| 切换语言需重启 App | 脚本里 `am force-stop` + 重新进入主页 |
| 210+ dump 耗时长 | P0 全量 + P1 抽样；nightly 跑全量 |
| 动态文案误报 | 维护 `DYNAMIC_RIDS` 排除表 |
| 专有名词不应翻译 | `I18N_WHITELIST` |
| 无法从 dump 看图片文字 | 关键 Banner 另加截图 + OCR（Phase 5） |
| App 内语言与系统 locale 不一致 | 方案 A/B 分开测 |

---

## 12. 执行前 Checklist

- [ ] 向产品/研发确认 14 种语言的 locale code 与 Settings 内显示名称
- [ ] dump Language 设置页 UI，建立语言切换自动化路径
- [ ] 确认 App 切换语言后是否需要重启（及等待时长）
- [ ] 确定 baseline 语言（建议 en-US）
- [ ] 确认 P0/P1 页面清单与现有 `S1Pro_UI/v3.0.0.6858/window_dump/` 对齐
- [ ] 评审 `I18N_WHITELIST` 与 `DYNAMIC_RIDS` 初版列表

---

## 13. 相关文件

| 文件 | 说明 |
|------|------|
| `S1Pro_UI/dump_page_ui.py` | 现有 UI dump 入口（待扩展 `--locale`） |
| `S1Pro_UI/parse_window_dump.py` | XML → Markdown 解析（可复用 `parse_dump`） |
| `S1Pro_UI/v3.0.0.6858/window_dump/` | 当前英文 baseline dump |
| `pages/` | Page Object，导航复用 resource-id |
| `scenarios/` | 场景脚本，可参考页面跳转路径 |
