# -*- coding: utf-8 -*-
"""Model: config, log, reminder labels -- pure data + persistence, zero deps."""

import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
CONFIG_FILE = BASE_DIR / "config.json"
LOG_FILE = BASE_DIR / "logs" / "reminder_log.txt"

# === Default config ======================================================
DEFAULT_CONFIG = {
    "water_interval_minutes": 30,
    "stand_interval_minutes": 45,
    "stand_duration_minutes": 15,
    "enabled": True,
    "start_time": "08:30",
    "end_time": "20:30",
}

# === Option lists ========================================================
# Water/stand reminder intervals (minutes)
INTERVAL_OPTIONS = [15, 20, 25, 30, 45, 60, 90, 120]
STAND_DURATION_OPTIONS = [5, 10, 15, 20, 30, 45, 60]
TIME_OPTIONS = [
    "06:00", "06:30", "07:00", "07:30", "08:00", "08:30", "09:00", "09:30",
    "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", "13:30",
    "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30",
    "18:00", "18:30", "19:00", "19:30", "20:00", "20:30", "21:00", "21:30", "22:00",
]

# === Reminder labels (UI strings) ========================================
REMIND_LABELS = {
    "water": {
        "name": "喝水",
        "icon": "💧",
        "title": "喝水时间",
        "msg": "起来喝杯水吧~保持水分，精神满满！",
    },
    "stand": {
        "name": "站立",
        "icon": "🧍",
        "title": "活动时间",
        "msg": "久坐提醒！站起来走走，伸个懒腰活动一下~",
    },
    "sit": {
        "name": "坐下",
        "icon": "💺",
        "title": "休息结束",
        "msg": "已站立一会儿了，可以坐下继续工作啦~",
    },
}


class Config:
    """App config backed by config.json.
    
    Each setter auto-saves via _save().
    """

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

    # -- Water interval (minutes) --------------------------------------------
    @property
    def water_interval(self):
        return self._data["water_interval_minutes"]

    @water_interval.setter
    def water_interval(self, value):
        self._data["water_interval_minutes"] = value
        self._save()

    # -- Stand interval (minutes) --------------------------------------------
    @property
    def stand_interval(self):
        return self._data["stand_interval_minutes"]

    @stand_interval.setter
    def stand_interval(self, value):
        self._data["stand_interval_minutes"] = value
        self._save()

    # -- Stand duration (minutes) --------------------------------------------
    @property
    def stand_duration(self):
        return self._data.get("stand_duration_minutes", 15)

    @stand_duration.setter
    def stand_duration(self, value):
        self._data["stand_duration_minutes"] = value
        self._save()

    # -- Daily reminder start time (HH:MM) -----------------------------------
    @property
    def start_time(self):
        return self._data.get("start_time", "08:30")

    @start_time.setter
    def start_time(self, value):
        self._data["start_time"] = value
        self._save()

    # -- Daily reminder end time (HH:MM) -------------------------------------
    @property
    def end_time(self):
        return self._data.get("end_time", "20:30")

    @end_time.setter
    def end_time(self, value):
        self._data["end_time"] = value
        self._save()

    # -- Enable/pause switch -------------------------------------------------
    @property
    def enabled(self):
        return self._data["enabled"]

    @enabled.setter
    def enabled(self, value):
        self._data["enabled"] = value
        self._save()


class ReminderLog:
    """Reminder event log, written to logs/reminder_log.txt."""

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
        return f"上次{name}: 暂无记录"

    @staticmethod
    def heartbeat(status):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"[{ts}] 心跳: {status}\n")
        except Exception:
            pass

    @staticmethod
    def open_file():
        import os
        if LOG_FILE.exists():
            os.startfile(str(LOG_FILE))
