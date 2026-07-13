# 健康提醒助手 (Health Reminder)

一个轻量级的 Windows 系统托盘定时提醒工具，帮助你养成健康的饮水与站立习惯。

## 功能

- **定时喝水提醒** — 可自定义间隔（15/20/25/30/45/60/90/120 分钟）
- **定时站立提醒** — 久坐提醒，活动一下
- **Win10 浅色通知弹窗** — tkinter 置顶弹窗，远程桌面（RDP）全屏模式下依然可见
- **系统托盘图标** — 蓝色水滴，右键菜单操作
- **提醒日志** — 记录每次提醒，可在菜单中查看上次提醒时间
- **一键开关** — 随时启用/暂停所有提醒

## 截图

![托盘菜单](icon_preview.png)

## 安装

```bash
pip install -r requirements.txt
```

## 使用

```bash
# 普通启动（带控制台窗口，适合调试）
python reminder.py

# 无窗口后台运行（推荐）
pythonw reminder.py

# 或直接双击
启动健康提醒.bat
```

启动后系统托盘会出现蓝色水滴图标 💧，右键即可配置间隔、手动触发提醒或查看日志。

## 配置

所有设置保存在 `config.json`：

```json
{
  "water_interval_minutes": 30,
  "stand_interval_minutes": 45,
  "enabled": true
}
```

## 提醒日志

每次提醒都会记录到 `reminder_log.txt`，右键菜单可查看。

## 技术栈

- Python 3.8+
- pystray（系统托盘）
- Pillow（图标生成）
- tkinter（通知弹窗）

## 适用场景

- 远程办公（RDP 全屏下通知可见）
- 长时间编码/设计工作的健康管理
- 办公族久坐提醒

## License

MIT
