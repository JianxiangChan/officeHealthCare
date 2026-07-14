# -*- coding: utf-8 -*-
"""Controller: timer orchestration, menu callbacks, sit-stand cycle."""

import threading

import pystray

from .model import (
    INTERVAL_OPTIONS,
    REMIND_LABELS,
    STAND_DURATION_OPTIONS,
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

    @staticmethod
    def _start_timer(interval_sec, callback):
        t = threading.Timer(interval_sec, callback)
        t.daemon = True
        t.start()
        return t

    def _cancel_timer(self, timer):
        if timer:
            timer.cancel()

    def _schedule_water(self):
        self._cancel_timer(self._water_timer)
        self._water_timer = self._start_timer(
            self._config.water_interval * 60, self._on_water_timer
        )

    def _schedule_stand(self):
        self._cancel_timer(self._stand_timer)
        self._stand_timer = self._start_timer(
            self._config.stand_interval * 60, self._on_stand_timer
        )

    def _schedule_standing(self):
        self._cancel_timer(self._standing_timer)
        self._standing_timer = self._start_timer(
            self._config.stand_duration * 60, self._on_stand_duration_end
        )

    def _on_water_timer(self):
        if not self._config.enabled:
            return
        info = REMIND_LABELS["water"]
        self._log.append("water")
        self._view.show_popup(info["title"], info["msg"], info["icon"])
        self._schedule_water()

    def _on_stand_timer(self):
        if not self._config.enabled:
            return
        info = REMIND_LABELS["stand"]
        self._log.append("stand")
        self._view.show_popup(info["title"], info["msg"], info["icon"])
        self._schedule_standing()

    def _on_stand_duration_end(self):
        if not self._config.enabled:
            return
        info = REMIND_LABELS["sit"]
        self._log.append("sit")
        self._view.show_popup(info["title"], info["msg"], info["icon"])
        self._schedule_stand()
        self._standing_timer = None
        self._view.update_menu(self.build_menu())

    def build_menu(self):
        enabled = self._config.enabled
        w = self._log.last("water")
        s = self._log.last("stand")

        def status():
            return "  \U0001f9cd \u7ad9\u7acb\u4e2d..." if self._standing_timer else "  \U0001f4ba \u5750\u7740"

        return pystray.Menu(
            pystray.MenuItem("\U0001f4a7 \u5065\u5eb7\u63d0\u9192\u52a9\u624b", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("\u559d\u6c34\u95f4\u9694",
                             build_interval_submenu(INTERVAL_OPTIONS, self._config.water_interval,
                                                    self.set_water_interval)),
            pystray.MenuItem("\u7ad9\u7acb\u95f4\u9694",
                             build_interval_submenu(INTERVAL_OPTIONS, self._config.stand_interval,
                                                    self.set_stand_interval)),
            pystray.MenuItem("\u7ad9\u7acb\u65f6\u957f",
                             build_interval_submenu(STAND_DURATION_OPTIONS, self._config.stand_duration,
                                                    self.set_stand_duration)),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "\u2705 \u5df2\u542f\u7528" if enabled else "\u23f8 \u5df2\u6682\u505c",
                lambda icon, item: self.toggle_enabled(),
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("\U0001f4a7 \u7acb\u5373\u559d\u6c34\u63d0\u9192", lambda icon, item: self.manual_remind("water")),
            pystray.MenuItem("\U0001f9cd \u7acb\u5373\u7ad9\u7acb\u63d0\u9192", lambda icon, item: self.manual_remind("stand")),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(w, None, enabled=False),
            pystray.MenuItem(s, None, enabled=False),
            pystray.MenuItem("\U0001f4cb \u67e5\u770b\u63d0\u9192\u65e5\u5fd7", lambda icon, item: self._log.open_file()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(status(), None, enabled=False),
            pystray.MenuItem("\u9000\u51fa", lambda icon, item: self.stop()),
        )

    def toggle_enabled(self):
        self._config.enabled = not self._config.enabled
        if self._config.enabled:
            self._start_all_timers()
            self._view.show_popup("\u63d0\u9192\u5df2\u6062\u590d", "\u5065\u5eb7\u63d0\u9192\u5df2\u91cd\u65b0\u5f00\u542f", "\U0001f514")
        else:
            self._cancel_all_timers()
            self._view.show_popup("\u63d0\u9192\u5df2\u6682\u505c", "\u5065\u5eb7\u63d0\u9192\u5df2\u6682\u505c\uff0c\u597d\u597d\u4f11\u606f\u5427~", "\U0001f515")
        self._view.update_menu(self.build_menu())

    def set_water_interval(self, minutes):
        self._config.water_interval = minutes
        self._schedule_water()
        info = REMIND_LABELS["water"]
        self._view.show_popup("\u8bbe\u7f6e\u5df2\u66f4\u65b0", f"{info['name']}\u63d0\u9192\u95f4\u9694\u5df2\u8bbe\u4e3a {minutes} \u5206\u949f", info["icon"])
        self._view.update_menu(self.build_menu())

    def set_stand_interval(self, minutes):
        self._config.stand_interval = minutes
        self._schedule_stand()
        info = REMIND_LABELS["stand"]
        self._view.show_popup("\u8bbe\u7f6e\u5df2\u66f4\u65b0", f"{info['name']}\u63d0\u9192\u95f4\u9694\u5df2\u8bbe\u4e3a {minutes} \u5206\u949f", info["icon"])
        self._view.update_menu(self.build_menu())

    def set_stand_duration(self, minutes):
        self._config.stand_duration = minutes
        info = REMIND_LABELS["stand"]
        self._view.show_popup("\u8bbe\u7f6e\u5df2\u66f4\u65b0", f"\u7ad9\u7acb\u65f6\u957f\u5df2\u8bbe\u4e3a {minutes} \u5206\u949f", info["icon"])
        self._view.update_menu(self.build_menu())

    def manual_remind(self, kind):
        info = REMIND_LABELS[kind]
        self._log.append(kind)
        self._view.show_popup(info["title"], info["msg"], info["icon"])
        if kind == "water":
            self._schedule_water()
        elif kind == "stand":
            self._schedule_standing()

    def _start_all_timers(self):
        self._schedule_water()
        self._schedule_stand()

    def _cancel_all_timers(self):
        for t in (self._water_timer, self._stand_timer, self._standing_timer):
            self._cancel_timer(t)
        self._water_timer = None
        self._stand_timer = None
        self._standing_timer = None

    def start(self):
        icon_img = create_tray_icon_image()
        self._view.create_icon(icon_img, "\u5065\u5eb7\u63d0\u9192\u52a9\u624b", self.build_menu())
        self._start_all_timers()
        self._view.run()

    def stop(self):
        self._cancel_all_timers()
        self._view.stop()
