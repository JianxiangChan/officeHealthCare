# -*- coding: utf-8 -*-
"""
健康提醒助手 - Windows 系统托盘小程序
定时提醒喝水 & 站立活动

用法:
    pythonw reminder.py     (无控制台窗口，推荐)
    python  reminder.py     (带控制台窗口，调试用)
"""

import json
import os
import sys
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path

import pystray
from PIL import Image, ImageDraw


# === 常量 ===================================================================

CONFIG_FILE = Path(__file__).parent / "config.json"
LOG_FILE = Path(__file__).parent / "logs" / "reminder_log.txt"

DEFAULT_CONFIG = {
    "water_interval_minutes": 30,
    "stand_interval_minutes": 45,
    "enabled": True,
}

INTERVAL_OPTIONS = [15, 20, 25, 30, 45, 60, 90, 120]

REMIND_LABELS = {
    "water": {
        "name": "喝水",
        "icon": "\U0001f4a7",
        "title": "喝水时间",
        "msg": "起来喝杯水吧~保持水分，精神满满！",
    },
    "stand": {
        "name": "站立",
        "icon": "\U0001f9cd",
        "title": "活动时间",
        "msg": "久坐提醒！站起来走走，伸个懒腰活动一下~",
    },
}


# === 工具函数 ===============================================================

def load_config():
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text("utf-8"))
            return {**DEFAULT_CONFIG, **data}
        except Exception:
            pass
    return dict(DEFAULT_CONFIG)


def save_config(config):
    CONFIG_FILE.write_text(
        json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def create_tray_icon():
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([4, 8, 60, 60], fill=(41, 128, 255, 255))
    draw.polygon([(32, 2), (12, 24), (52, 24)], fill=(41, 128, 255, 255))
    draw.ellipse([18, 18, 30, 30], fill=(255, 255, 255, 120))
    draw.ellipse([36, 24, 42, 30], fill=(255, 255, 255, 60))
    return img


def _log_reminder(kind):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    name = REMIND_LABELS[kind]["name"]
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {name}\n")
    except Exception:
        pass


def _show_popup(title, message, icon):
    """Win10浅色风格通知弹窗 - 在新线程中运行"""
    def _run():
        root = tk.Tk()
        root.overrideredirect(True)
        root.attributes("-topmost", True)

        BG = "#ffffff"
        BORDER = "#e0e0e0"
        ACCENT = "#0078d4"
        FG = "#1a1a1a"
        FG_SEC = "#5a5a5a"
        HINT = "#aaaaaa"

        root.configure(bg=BORDER)
        w, h = 340, 90
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        x = sw - w - 16
        y = sh - h - 60
        root.geometry(f"{w}x{h}+{x}+{y}")

        inner = tk.Frame(root, bg=BG, bd=0)
        inner.pack(fill="both", expand=True, padx=1, pady=1)

        accent_bar = tk.Frame(inner, bg=ACCENT, width=4)
        accent_bar.pack(side="left", fill="y")

        content = tk.Frame(inner, bg=BG)
        content.pack(side="left", fill="both", expand=True, padx=(14, 10), pady=(10, 10))

        top = tk.Frame(content, bg=BG)
        top.pack(fill="x")

        icon_label = tk.Label(top, text=icon, font=("Segoe UI", 14), bg=BG)
        icon_label.pack(side="left", padx=(0, 8))

        title_label = tk.Label(top, text=title, font=("Microsoft YaHei UI", 11, "bold"),
                               bg=BG, fg=FG)
        title_label.pack(side="left")

        close_hint = tk.Label(top, text="点击关闭", font=("Microsoft YaHei UI", 8),
                              bg=BG, fg=HINT)
        close_hint.pack(side="right", padx=(0, 4))

        msg_label = tk.Label(content, text=message, font=("Microsoft YaHei UI", 9),
                             bg=BG, fg=FG_SEC, anchor="w", justify="left",
                             wraplength=290)
        msg_label.pack(fill="x", pady=(4, 0))

        widgets = (root, inner, content, top, icon_label, title_label, msg_label, close_hint, accent_bar)
        for wgt in widgets:
            wgt.bind("<Button-1>", lambda e: root.destroy())
            wgt.configure(cursor="hand2")

        root.mainloop()

    t = threading.Thread(target=_run, daemon=True)
    t.start()


# === 应用主体 ===============================================================

class ReminderApp:

    def __init__(self):
        self.config = load_config()
        self._water_timer = None
        self._stand_timer = None
        self._icon = None

    # -- 定时器 ---------------------------------------------------------------

    @staticmethod
    def _start_timer(interval_sec, callback):
        t = threading.Timer(interval_sec, callback)
        t.daemon = True
        t.start()
        return t

    def _remind(self, kind):
        if not self.config["enabled"]:
            return
        info = REMIND_LABELS[kind]
        _log_reminder(kind)
        _show_popup(info["title"], info["msg"], info["icon"])

        key = f"{kind}_interval_minutes"
        timer = self._start_timer(
            self.config[key] * 60,
            lambda k=kind: self._remind(k),
        )
        setattr(self, f"_{kind}_timer", timer)

    def start_timers(self):
        self.stop_timers()
        if not self.config["enabled"]:
            return
        for kind in ("water", "stand"):
            key = f"{kind}_interval_minutes"
            timer = self._start_timer(
                self.config[key] * 60,
                lambda k=kind: self._remind(k),
            )
            setattr(self, f"_{kind}_timer", timer)

    def stop_timers(self):
        for kind in ("water", "stand"):
            t = getattr(self, f"_{kind}_timer", None)
            if t:
                t.cancel()
                setattr(self, f"_{kind}_timer", None)

    # -- 右键菜单 -------------------------------------------------------------

    def _make_interval_submenu(self, kind):
        current = self.config[f"{kind}_interval_minutes"]
        items = []
        for m in INTERVAL_OPTIONS:
            check = '\u2705 ' if m == current else ''
            label = f"{m}分钟{check}"
            items.append(
                pystray.MenuItem(label, self._make_callback(kind, m))
            )
        return pystray.Menu(*items)

    def _make_callback(self, kind, minutes):
        def callback(icon, item):
            self._set_interval(kind, minutes)
        return callback

    def _last_reminder_text(self, kind):
        name = REMIND_LABELS[kind]["name"]
        try:
            if LOG_FILE.exists():
                lines = LOG_FILE.read_text("utf-8").strip().split("\n")
                for line in reversed(lines):
                    if name in line:
                        return f"  上次{name}: {line[1:17]}"
        except Exception:
            pass
        return f"  上次{name}: 暂无记录"

    def _make_menu(self):
        enabled = self.config["enabled"]
        w = self._last_reminder_text("water")
        s = self._last_reminder_text("stand")
        return pystray.Menu(
            pystray.MenuItem("\U0001f4a7 健康提醒助手", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("喝水间隔", self._make_interval_submenu("water")),
            pystray.MenuItem("站立间隔", self._make_interval_submenu("stand")),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "\u2705 已启用" if enabled else "\u23f8 已暂停",
                lambda icon, item: self._toggle_enabled(),
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("\U0001f4a7 立即喝水提醒", lambda icon, item: self._remind("water")),
            pystray.MenuItem("\U0001f9cd 立即站立提醒", lambda icon, item: self._remind("stand")),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(w, None, enabled=False),
            pystray.MenuItem(s, None, enabled=False),
            pystray.MenuItem("\U0001f4cb 查看提醒日志", self._open_log),
            pystray.MenuItem("退出", lambda icon, item: self._quit()),
        )

    @staticmethod
    def _open_log(icon, item):
        if LOG_FILE.exists():
            os.startfile(str(LOG_FILE))

    def _rebuild_menu(self):
        if self._icon:
            self._icon.menu = self._make_menu()
            self._icon.update_menu()

    def _set_interval(self, kind, minutes):
        self.config[f"{kind}_interval_minutes"] = minutes
        save_config(self.config)
        self.start_timers()
        info = REMIND_LABELS[kind]
        _show_popup("设置已更新", f"{info['name']}提醒间隔已设为 {minutes} 分钟", info["icon"])
        self._rebuild_menu()

    def _toggle_enabled(self):
        self.config["enabled"] = not self.config["enabled"]
        save_config(self.config)
        if self.config["enabled"]:
            self.start_timers()
            _show_popup("提醒已恢复", "健康提醒已重新开启", "\U0001f514")
        else:
            self.stop_timers()
            _show_popup("提醒已暂停", "健康提醒已暂停，好好休息吧~", "\U0001f515")
        self._rebuild_menu()

    def _quit(self):
        self.stop_timers()
        if self._icon:
            self._icon.stop()
        sys.exit(0)

    # -- 入口 ----------------------------------------------------------------

    def run(self):
        icon_img = create_tray_icon()
        self._icon = pystray.Icon(
            "health_reminder",
            icon_img,
            "健康提醒助手",
            self._make_menu(),
        )
        self.start_timers()
        self._icon.run()


if __name__ == "__main__":
    app = ReminderApp()
    app.run()
