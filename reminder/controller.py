# -*- coding: utf-8 -*-
"""Controller: timer orchestration, menu callbacks, sit-stand cycle."""

import threading
from datetime import datetime

import pystray

from .model import (
    INTERVAL_OPTIONS,
    REMIND_LABELS,
    STAND_DURATION_OPTIONS,
    TIME_OPTIONS,
    get_version,
)
from .view import (
    TrayView,
    build_interval_submenu,
    create_tray_icon_image,
)


class ReminderController:

    def __init__(self, config, log, view):
        self._config = config
        self._log = log
        self._view: TrayView = view
        self._water_timer = None
        self._stand_timer = None
        self._standing_timer = None
        self._heartbeat_timer = None
        self._water_timer_start = None
        self._stand_timer_start = None

        # === Timer utilities =====================================================

    @staticmethod
    def _start_timer(interval_sec, callback):
        """Create a daemon timer thread."""
        t = threading.Timer(interval_sec, callback)
        t.daemon = True
        t.start()
        return t

    def _cancel_timer(self, timer):
        """Safely cancel a timer (ignore already-expired)."""
        if timer:
            timer.cancel()

    def _is_in_active_window(self, now=None):
        if now is None:
            now = datetime.now()
        start_dt = datetime.strptime(self._config.start_time, "%H:%M")
        end_dt = datetime.strptime(self._config.end_time, "%H:%M")
        return start_dt.time() <= now.time() <= end_dt.time()

    # -- Timer scheduling -----------------------------------------------------

    def _schedule_water(self):
        from datetime import datetime
        self._water_timer_start = datetime.now()
        """Schedule next water reminder."""
        self._cancel_timer(self._water_timer)
        self._water_timer = self._start_timer(
            self._config.water_interval * 60, self._on_water_timer
        )

    def _schedule_stand(self):
        from datetime import datetime
        self._stand_timer_start = datetime.now()
        """Schedule next stand reminder."""
        self._cancel_timer(self._stand_timer)
        self._stand_timer = self._start_timer(
            self._config.stand_interval * 60, self._on_stand_timer
        )

    def _schedule_standing(self):
        """Schedule stand-duration-end reminder."""
        self._cancel_timer(self._standing_timer)
        self._standing_timer = self._start_timer(
            self._config.stand_duration * 60, self._on_stand_duration_end
        )

    def _on_water_timer(self):
        if not self._config.enabled:
            return
        self._schedule_water()
        if not self._is_in_active_window():
            return
        info = REMIND_LABELS["water"]
        self._log.append("water")
        self._view.show_popup(info["title"], info["msg"], info["icon"])

    def _on_stand_timer(self):
        """Stand timer fired: show popup, log, start stand-duration countdown."""
        if not self._config.enabled:
            return
        self._schedule_standing()
        if not self._is_in_active_window():
            return
        info = REMIND_LABELS["stand"]
        self._log.append("stand")
        self._view.show_popup(info["title"], info["msg"], info["icon"])

    def _on_stand_duration_end(self):
        """Stand duration ended: prompt to sit, restart stand timer."""
        if not self._config.enabled:
            return
        info = REMIND_LABELS["sit"]
        self._log.append("sit")
        self._view.show_popup(info["title"], info["msg"], info["icon"])
        self._schedule_stand()
        self._schedule_heartbeat()
        self._standing_timer = None
        self._view.update_menu(self.build_menu())

    def build_menu(self):
        """Build the full system tray right-click menu."""
        enabled = self._config.enabled
        w = self._log.last("water")
        s = self._log.last("stand")

        def status():
            return "  🧍 站立中..." if self._standing_timer else "  💺 坐着"

        return pystray.Menu(
            pystray.MenuItem("💧 健康提醒助手", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("喝水间隔",
                             build_interval_submenu(INTERVAL_OPTIONS, self._config.water_interval,
                                                    self.set_water_interval)),
            pystray.MenuItem("站立间隔",
                             build_interval_submenu(INTERVAL_OPTIONS, self._config.stand_interval,
                                                    self.set_stand_interval)),
            pystray.MenuItem("站立时长",
                             build_interval_submenu(STAND_DURATION_OPTIONS, self._config.stand_duration,
                                                    self.set_stand_duration)),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("开始时间",
                             build_interval_submenu(TIME_OPTIONS, self._config.start_time,
                                                    self.set_start_time, suffix="")),
            pystray.MenuItem("结束时间",
                             build_interval_submenu(TIME_OPTIONS, self._config.end_time,
                                                    self.set_end_time, suffix="")),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "✅ 已启用" if enabled else "⏸ 已暂停",
                lambda icon, item: self.toggle_enabled(),
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("💧 立即喝水提醒", lambda icon, item: self.manual_remind("water")),
            pystray.MenuItem("🧍 立即站立提醒", lambda icon, item: self.manual_remind("stand")),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(w, None, enabled=False),
            pystray.MenuItem(s, None, enabled=False),
            pystray.MenuItem("📋 查看提醒日志", lambda icon, item: self._log.open_file()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(status(), None, enabled=False),
            pystray.MenuItem("退出", lambda icon, item: self.stop()),
        )

    def set_start_time(self, value):
        self._config.start_time = value
        self._view.update_menu(self.build_menu())

    def set_end_time(self, value):
        self._config.end_time = value
        self._view.update_menu(self.build_menu())

    def toggle_enabled(self):
        self._config.enabled = not self._config.enabled
        if self._config.enabled:
            self._start_all_timers()
            self._view.show_popup("提醒已恢复", "健康提醒已重新开启", "🔔")
        else:
            self._cancel_all_timers()
            self._view.show_popup("提醒已暂停", "健康提醒已暂停，好好休息吧~", "🔕")
        self._view.update_menu(self.build_menu())

    def set_water_interval(self, minutes):
        self._config.water_interval = minutes
        self._schedule_water()
        info = REMIND_LABELS["water"]
        self._view.show_popup("设置已更新", f"{info['name']}提醒间隔已设为 {minutes} 分钟", info["icon"])
        self._view.update_menu(self.build_menu())

    def set_stand_interval(self, minutes):
        self._config.stand_interval = minutes
        self._schedule_stand()
        self._schedule_heartbeat()
        info = REMIND_LABELS["stand"]
        self._view.show_popup("设置已更新", f"{info['name']}提醒间隔已设为 {minutes} 分钟", info["icon"])
        self._view.update_menu(self.build_menu())

    def set_stand_duration(self, minutes):
        self._config.stand_duration = minutes
        info = REMIND_LABELS["stand"]
        self._view.show_popup("设置已更新", f"站立时长已设为 {minutes} 分钟", info["icon"])
        self._view.update_menu(self.build_menu())

    def manual_remind(self, kind):
        """Trigger an immediate reminder of the given kind."""
        info = REMIND_LABELS[kind]
        self._log.append(kind)
        self._view.show_popup(info["title"], info["msg"], info["icon"])
        if kind == "water":
            self._schedule_water()
        elif kind == "stand":
            self._schedule_standing()

    def _schedule_heartbeat(self):
        self._cancel_timer(self._heartbeat_timer)
        self._heartbeat_timer = self._start_timer(300, self._on_heartbeat)

    def _on_heartbeat(self, now=None):
        from datetime import datetime
        if now is None:
            now = datetime.now()
        wr = self._water_timer_start
        sr = self._stand_timer_start
        w_remain = max(0, int((self._config.water_interval * 60 - (now - wr).total_seconds()) / 60)) if wr else self._config.water_interval
        s_remain = max(0, int((self._config.stand_interval * 60 - (now - sr).total_seconds()) / 60)) if sr else self._config.stand_interval
        s = "HB: v{} w{}({}m) s{}({}m) win={}-{} {}".format(get_version(), 
            self._config.water_interval, w_remain,
            self._config.stand_interval, s_remain,
            self._config.start_time, self._config.end_time,
            "on" if self._config.enabled else "off",
        )
        self._log.heartbeat(s)
        self._heartbeat_timer = None
        self._schedule_heartbeat()

    def _start_all_timers(self):
        self._schedule_water()
        self._schedule_stand()
        self._schedule_heartbeat()

    def _cancel_all_timers(self):
        for t in (self._water_timer, self._stand_timer, self._standing_timer):
            self._cancel_timer(t)
        self._water_timer = None
        self._stand_timer = None
        self._standing_timer = None
        self._heartbeat_timer = None
        self._water_timer_start = None
        self._stand_timer_start = None

    def start(self):
        """App entry: create tray icon, start timers, enter event loop (blocking)."""
        icon_img = create_tray_icon_image()
        self._view.create_icon(icon_img, "健康提醒助手", self.build_menu())
        self._start_all_timers()
        if self._log.has_standing_without_sit():
            self._on_stand_duration_end()
        self._view.run()

    def stop(self):
        """Exit app: cancel all timers, close tray icon."""
        self._cancel_all_timers()
        self._view.stop()
