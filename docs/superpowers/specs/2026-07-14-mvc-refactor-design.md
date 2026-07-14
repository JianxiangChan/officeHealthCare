# MVC 重构设计：健康提醒助手

## 概述

将当前单文件 `reminder.py`（~350行）按 MVC 模式拆分为 `reminder/` 包，UI 与逻辑分离，便于维护和扩展。

## 包结构

```
reminder/
├── __init__.py          # 统一导出，run() 组装入口
├── model.py             # 配置、日志、提醒标签数据（纯数据+持久化）
├── view.py              # 托盘图标、菜单构建函数、tkinter 弹窗
├── controller.py        # 定时器调度、坐-站循环逻辑、菜单回调编排
└── main.py              # 启动入口 (替代当前 reminder.py)
```

## 依赖方向

```
main.py ──→ reminder/__init__.py
                   │
                   ▼
            controller.py ──→ model.py (Config, ReminderLog)
                   │        ──→ view.py  (TrayView, build_interval_submenu)
                   │
                   ├── 菜单回调 ◄── view.py (用户点击）
                   └── show_popup ──→ view.py (提醒弹窗）
```

Model 和 View 互不 import，零依赖。所有编排在 Controller。

## 数据流

```
用户点菜单
    │ callback(lambda)
    ▼
Controller
    ├── 读状态 ──→ Model (Config / ReminderLog)
    ├── 更新配置 ──→ Model._save()
    ├── 调度定时器
    │       │
    │       ▼
    │     Timer 到期
    │       │
    │       ▼
    │   Controller._on_xxx()
    │       │
    │       ├──► View.show_popup()
    │       └──► Model.log_reminder()
    │
    └── 刷新菜单 ──→ View.update_menu()
```

## Model 层

### Config
- 路径：`config.json`
- 字段：`water_interval_minutes`, `stand_interval_minutes`, `stand_duration_minutes`, `enabled`
- `load()` → dict + 默认值补全
- `save()` → JSON 写入
- 每个 setter 自动调用 `save()`

### ReminderLog
- 路径：`logs/reminder_log.txt`，自动创建目录
- `append(kind: str)` → 追加时间戳行
- `last(kind: str) → str` → "上次XX: YYYY-MM-DD HH:MM"

### 常量
- `DEFAULT_CONFIG`, `INTERVAL_OPTIONS`, `STAND_DURATION_OPTIONS`, `REMIND_LABELS`

## View 层

### TrayView
- `create_icon(image, tooltip, menu)` → 创建 pystray.Icon
- `update_menu(menu)` → 刷新右键菜单
- `show_popup(title, message, icon_emoji)` → tkinter 置顶弹窗（新线程，Win10浅色风格，点击关闭）
- `stop()` → 关闭托盘

### 独立工具函数
- `create_tray_icon_image()` → 64x64 蓝色水滴 RGBA Image
- `build_interval_submenu(label, options, current, on_select)` → pystray.Menu（纯函数，可复用于间隔和时长菜单）

## Controller 层

### ReminderController

**生命周期**
- `__init__(config, log, view)` — 依赖注入
- `start()` — 启动定时器 + 托盘事件循环（阻塞）
- `stop()` — 取消全部定时器 + 关闭托盘

**菜单构建**
- `build_menu()` → 组合所有 MenuItem，含回调闭包，展示状态文字

**定时器**
- `_start_water_cycle()` — 启动喝水定时器（30分钟循环）
- `_start_sit_stand_cycle()` — 启动坐-站循环（45分→站立→15分→坐下）
- `_on_water_timer()` — 喝水提醒：popup + log + 重启定时器
- `_on_stand_timer()` — 站立提醒：popup + log + 启动站立倒计时
- `_on_stand_duration_end()` — 坐下提醒：popup + log + 重启站起定时器

**用户操作**（菜单回调）
- `toggle_enabled()` — 暂停/恢复，通知
- `set_water_interval(m)`, `set_stand_interval(m)`, `set_stand_duration(m)`
- `manual_remind(kind)` — 立即触发提醒
- `open_log()` — 打开日志文件

## 迁移清单

| 原代码位置 | 新位置 | 说明 |
|---|---|---|
| `load_config/save_config` | `model.py Config` | 封装为类 |
| `_log_reminder` | `model.py ReminderLog` | 封装为类 |
| `create_tray_icon` | `view.py create_tray_icon_image` | 独立函数 |
| `_show_popup` | `view.py TrayView.show_popup` | 实例方法 |
| `_make_menu/_rebuild_menu` | `controller.py build_menu` | 组合逻辑 |
| `_make_interval_submenu/_make_duration_submenu` | `view.py build_interval_submenu` | 纯函数 |
| `_make_callback/_make_duration_callback` | Controller 内部闭包 | 回调在 Controller |
| `_start_timer` | `controller.py` 私有方法 | 定时器工具 |
| `_remind` 逻辑 | `controller.py _on_water_timer/_on_stand_timer` | 拆分 |
| `_remind_sit` | `controller.py _on_stand_duration_end` | 重命名 |
| `start_timers/stop_timers` | `controller.py start/stop` | 生命周期 |
| `_set_interval/_set_duration` | `controller.py set_xxx_interval` | 重命名 |
| `_toggle_enabled/_quit` | `controller.py toggle_enabled/stop` | 重命名 |

## 不变项

- config.json 格式不变
- 日志文件格式不变
- 托盘图标和行为不变
- 通知弹窗样式不变
- 命令行启动方式不变
