# -*- coding: utf-8 -*-
"""Model: config, log, labels - pure data + persistence."""

import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
CONFIG_FILE = BASE_DIR / "config.json"
LOG_FILE = BASE_DIR / "logs" / "reminder_log.txt"

DEFAULT_CONFIG = {
    "water_interval_minutes": 30,
    "stand_interval_minutes": 45,
    "stand_duration_minutes": 15,
    "enabled": True,
    "start_time": "08:30",
    "end_time": "20:30",
}

INTERVAL_OPTIONS = [15, 20, 25, 30, 45, 60, 90, 120]
STAND_DURATION_OPTIONS = [5, 10, 15, 20, 30, 45, 60]
TIME_OPTIONS = [
    "06:00", "06:30", "07:00", "07:30", "08:00", "08:30", "09:00", "09:30",
    "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", "13:30",
    "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30",
    "18:00", "18:30", "19:00", "19:30", "20:00", "20:30", "21:00", "21:30", "22:00",
]

REMIND_LABELS = {
    "water": {
        "name": "\u559d\u6c34",
        "icon": "\U0001f4a7",
        "title": "\u559d\u6c34\u65f6\u95f4",
        "msg": "\u8d77\u6765\u559d\u676f\u6c34\u5427~\u4fdd\u6301\u6c34\u5206\uff0c\u7cbe\u795e\u6ee1\u6ee1\uff01",
    },
    "stand": {
        "name": "\u7ad9\u7acb",
        "icon": "\U0001f9cd",
        "title": "\u6d3b\u52a8\u65f6\u95f4",
        "msg": "\u4e45\u5750\u63d0\u9192\uff01\u7ad9\u8d77\u6765\u8d70\u8d70\uff0c\u4f38\u4e2a\u61d2\u8170\u6d3b\u52a8\u4e00\u4e0b~",
    },
    "sit": {
        "name": "\u5750\u4e0b",
        "icon": "\U0001f4ba",
        "title": "\u4f11\u606f\u7ed3\u675f",
        "msg": "\u5df2\u7ad9\u7acb\u4e00\u4f1a\u513f\u4e86\uff0c\u53ef\u4ee5\u5750\u4e0b\u7ee7\u7eed\u5de5\u4f5c\u5566~",
    },
}


class Config:
    """Application config backed by config.json."""

    def __init__(self):
        self._data = self._load()

    @staticmethod
    def _load():
        if CONFIG_FILE.exists():
            try:
                data = json.loads(CONFIG_FILE.read_text("utf-8"))
                return {**DEFAULT_CONFIG, **data}
            except Exception:
                pass
        return dict(DEFAULT_CONFIG)

    def _save(self):
        CONFIG_FILE.write_text(
            json.dumps(self._data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    # -- typed accessors ----------------------------------------------------

    @property
    def water_interval(self):
        return self._data["water_interval_minutes"]

    @water_interval.setter
    def water_interval(self, value):
        self._data["water_interval_minutes"] = value
        self._save()

    @property
    def stand_interval(self):
        return self._data["stand_interval_minutes"]

    @stand_interval.setter
    def stand_interval(self, value):
        self._data["stand_interval_minutes"] = value
        self._save()

    @property
    def stand_duration(self):
        return self._data.get("stand_duration_minutes", 15)

    @stand_duration.setter
    def stand_duration(self, value):
        self._data["stand_duration_minutes"] = value
        self._save()

    @property
    def start_time(self):
        return self._data.get("start_time", "08:30")

    @start_time.setter
    def start_time(self, value):
        self._data["start_time"] = value
        self._save()

    @property
    def end_time(self):
        return self._data.get("end_time", "20:30")

    @end_time.setter
    def end_time(self, value):
        self._data["end_time"] = value
        self._save()

    @property
    def enabled(self):
        return self._data["enabled"]

    @enabled.setter
    def enabled(self, value):
        self._data["enabled"] = value
        self._save()


class ReminderLog:
    """Persistent reminder event log."""

    @staticmethod
    def append(kind):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        name = REMIND_LABELS[kind]["name"]
        try:
            LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"[{ts}] {name}\n")
        except Exception:
            pass

    @staticmethod
    def last(kind):
        name = REMIND_LABELS[kind]["name"]
        try:
            if LOG_FILE.exists():
                lines = LOG_FILE.read_text("utf-8").strip().split("\n")
                for line in reversed(lines):
                    if name in line:
                        return f"上次{name}: {line[1:17]}"
        except Exception:
            pass
        return f"上次{name}: \u6682\u65e0\u8bb0\u5f55"

    @staticmethod
    def open_file():
        import os
        if LOG_FILE.exists():
            os.startfile(str(LOG_FILE))
