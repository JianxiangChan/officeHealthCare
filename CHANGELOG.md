# Changelog

## [1.0.0] - 2026-07-14

### Added
- 系统托盘定时喝水/站立提醒
- 坐-站循环提醒：久坐→站立→坐下，形成健康循环
- 时间窗口控制：默认 8:30–20:30 启用提醒，菜单可配置
- 每 5 分钟心跳日志，显示定时器剩余时间
- 站立时长子菜单（5/10/15/20/30/45/60 分钟）
- 上次提醒时间展示 + 日志查看入口
- 版本号系统（VERSION 文件）
- 44 个单元测试（pytest）

### Changed
- MVC 架构重构：Model/View/Controller 分离
- Win10 浅色风格 tkinter 通知弹窗（RDP 全屏可用）
- 注释和 docstring 英文化

### Fixed
- Python pystray lambda 回调兼容问题
- 启动批处理脚本编码问题

### Removed
- 旧单文件 reminder.py（已被 MVC 包替代）
