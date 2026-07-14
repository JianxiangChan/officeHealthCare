# 健康提醒助手 (Health Reminder)

轻量级 Windows 系统托盘定时提醒工具，帮助你养成健康的饮水与站立习惯。

## 功能

- **定时喝水提醒** — 可自定义间隔（15/20/25/30/45/60/90/120 分钟）
- **坐-站循环提醒** — 久坐提醒站立，站立 N 分钟后提醒坐下，形成健康循环
- **时间窗口控制** — 默认 8:30–20:30 启用提醒，可在菜单中配置起止时间
- **Win10 浅色通知弹窗** — tkinter 置顶弹窗，远程桌面（RDP）全屏模式下依然可见
- **系统托盘图标** — 蓝色水滴，右键菜单操作
- **提醒日志** — 记录每次提醒，可在菜单中查看上次提醒时间
- **一键开关** — 随时启用/暂停所有提醒

## 项目结构（MVC 架构）

`
reminder/
├── main.py                 # 启动入口
├── 启动健康提醒.bat          # Windows 双击启动脚本
├── config.json             # 用户配置文件
├── requirements.txt
├── reminder/               # MVC 包
│   ├── __init__.py         # run() 组装入口
│   ├── model.py            # Model: 配置、日志、提醒文案
│   ├── view.py             # View: 托盘图标、菜单构建、弹窗
│   └── controller.py       # Controller: 定时器调度、坐-站循环
├── tests/                  # 单元测试（37 cases, pytest）
│   ├── test_model.py
│   ├── test_view.py
│   ├── test_controller.py
│   ├── test_time_window.py
│   └── test_time_window_ctrl.py
└── logs/                   # 提醒日志目录（自动创建）
    └── reminder_log.txt
`

## 安装

`ash
pip install -r requirements.txt
`

## 使用

`ash
# 普通启动（带控制台窗口，适合调试）
python main.py

# 无窗口后台运行（推荐）
pythonw main.py

# 或直接双击
启动健康提醒.bat
`

启动后系统托盘会出现蓝色水滴图标，右键即可配置间隔、时间窗口、手动触发提醒或查看日志。

## 运行测试

`ash
python -m pytest tests/ -v
`

## 配置

所有设置保存在 config.json：

`json
{
  "water_interval_minutes": 30,
  "stand_interval_minutes": 45,
  "stand_duration_minutes": 15,
  "enabled": true,
  "start_time": "08:30",
  "end_time": "20:30"
}
`

| 字段 | 说明 |
|---|---|
| water_interval_minutes | 喝水提醒间隔 |
| stand_interval_minutes | 坐多久后提醒站立 |
| stand_duration_minutes | 站立多久后提醒坐下 |
| start_time / end_time | 每日提醒时间窗口 |
| enabled | 启用/暂停 |

## 技术栈

- Python 3.8+
- pystray（系统托盘）
- Pillow（图标生成）
- tkinter（通知弹窗）
- pytest（测试框架）

## License

MIT
