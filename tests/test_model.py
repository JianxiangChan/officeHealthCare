# -*- coding: utf-8 -*-
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from reminder.model import Config, ReminderLog, REMIND_LABELS, DEFAULT_CONFIG


class TestConfig:
    def test_load_defaults(self):
        with patch("reminder.model.CONFIG_FILE", Path("/nonexistent/config.json")):
            config = Config()
            assert config.water_interval == 30
            assert config.stand_interval == 45
            assert config.stand_duration == 15
            assert config.enabled is True

    def test_load_from_file(self):
        data = {**DEFAULT_CONFIG, "water_interval_minutes": 20, "enabled": False}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(data, f)
            tmp_path = f.name
        try:
            with patch("reminder.model.CONFIG_FILE", Path(tmp_path)):
                config = Config()
                assert config.water_interval == 20
                assert config.enabled is False
                assert config.stand_interval == 45  # default preserved
        finally:
            Path(tmp_path).unlink()

    def test_save_persists(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f)
            tmp_path = f.name
        try:
            with patch("reminder.model.CONFIG_FILE", Path(tmp_path)):
                config = Config()
                config.water_interval = 15
                # reload and verify
                config2 = Config()
                assert config2.water_interval == 15
        finally:
            Path(tmp_path).unlink()

    def test_setter_triggers_save(self, tmp_path):
        cfg_file = tmp_path / "config.json"
        cfg_file.write_text(json.dumps(DEFAULT_CONFIG), encoding="utf-8")
        with patch("reminder.model.CONFIG_FILE", cfg_file):
            config = Config()
            config.stand_duration = 30
            data = json.loads(cfg_file.read_text("utf-8"))
            assert data["stand_duration_minutes"] == 30


class TestReminderLog:
    def test_append_and_last(self, tmp_path):
        log_file = tmp_path / "reminder_log.txt"
        with patch("reminder.model.LOG_FILE", log_file):
            ReminderLog.append("water")
            ReminderLog.append("stand")
            content = log_file.read_text("utf-8")
            assert "喝水" in content
            assert "站立" in content
            last_water = ReminderLog.last("water")
            assert "上次喝水" in last_water

    def test_last_returns_default_when_empty(self, tmp_path):
        log_file = tmp_path / "nonexistent.log"
        with patch("reminder.model.LOG_FILE", log_file):
            result = ReminderLog.last("water")
            assert "暂无记录" in result


class TestLabels:
    def test_all_kinds_have_required_keys(self):
        for kind in ("water", "stand", "sit"):
            label = REMIND_LABELS[kind]
            assert "name" in label
            assert "icon" in label
            assert "title" in label
            assert "msg" in label
