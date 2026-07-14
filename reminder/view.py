# -*- coding: utf-8 -*-
"""View: tray icon, menu builder, tkinter popup notification."""

import threading
import tkinter as tk

import pystray
from PIL import Image, ImageDraw


def create_tray_icon_image():
    """Generate 64x64 blue droplet tray icon (RGBA)."""
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([4, 8, 60, 60], fill=(41, 128, 255, 255))
    draw.polygon([(32, 2), (12, 24), (52, 24)], fill=(41, 128, 255, 255))
    draw.ellipse([18, 18, 30, 30], fill=(255, 255, 255, 120))
    draw.ellipse([36, 24, 42, 30], fill=(255, 255, 255, 60))
    return img


def build_interval_submenu(options, current, on_select, suffix="分钟"):
    """Build a pystray.Menu submenu for selecting an integer option.

    Args:
        options: list of int values
        current: the currently selected value
        on_select: callable(value) called when user selects an option
    """
    items = []
    for m in options:
        check = "✅ " if m == current else ""
        label = f"{m}分钟{check}"
        def make_cb(val):
            def cb(icon, item):
                on_select(val)
            return cb
        items.append(
            pystray.MenuItem(label, make_cb(m))
        )
    return pystray.Menu(*items)


class TrayView:
    """System tray icon view + tkinter notification popup."""

    def __init__(self):
        self._icon = None

    def create_icon(self, image, tooltip, menu):
        """Create tray icon instance."""
        self._icon = pystray.Icon("health_reminder", image, tooltip, menu)

    def update_menu(self, menu):
        """Refresh right-click menu at runtime (after config change)."""
        if self._icon:
            self._icon.menu = menu
            self._icon.update_menu()

    def run(self):
        """Start tray event loop (blocking until stop())."""
        """Blocking event loop."""
        if self._icon:
            self._icon.run()

    def stop(self):
        """Stop tray event loop."""
        if self._icon:
            self._icon.stop()

    @staticmethod
    def show_popup(title, message, icon):
        """Show Win10 light-theme popup (runs in new daemon thread, non-blocking)."""

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
