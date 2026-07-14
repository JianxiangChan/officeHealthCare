# -*- coding: utf-8 -*-
import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

from reminder.model import Config, ReminderLog, DEFAULT_CONFIG
from reminder.view import TrayView
from reminder.controller import ReminderController


@pytest.fixture
def mock_log():
    return MagicMock(spec=ReminderLog)


@pytest.fixture
def mock_view():
    return MagicMock(spec=TrayView)


@pytest.fixture
def temp_config():
    data = {**DEFAULT_CONFIG, "water_interval_minutes": 1, "stand_interval_minutes": 1, "stand_duration_minutes": 1}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(data, f)
        tmp_path = f.name
    with patch("reminder.model.CONFIG_FILE", Path(tmp_path)):
        yield Config()
    Path(tmp_path).unlink()


class TestReminderController:
    def test_build_menu_returns_items(self, temp_config, mock_log, mock_view):
        mock_log.last.return_value = "上次喝水: 2026-01-01 12:00"
        ctrl = ReminderController(temp_config, mock_log, mock_view)
        menu = ctrl.build_menu()
        items = list(menu)
        assert len(items) > 10

    def test_toggle_enabled_off(self, temp_config, mock_log, mock_view):
        ctrl = ReminderController(temp_config, mock_log, mock_view)
        ctrl.toggle_enabled()
        assert temp_config.enabled is False
        mock_view.show_popup.assert_called()

    def test_toggle_enabled_on(self, temp_config, mock_log, mock_view):
        temp_config.enabled = False
        ctrl = ReminderController(temp_config, mock_log, mock_view)
        ctrl.toggle_enabled()
        assert temp_config.enabled is True
        mock_view.show_popup.assert_called()

    def test_set_water_interval(self, temp_config, mock_log, mock_view):
        ctrl = ReminderController(temp_config, mock_log, mock_view)
        ctrl.set_water_interval(20)
        assert temp_config.water_interval == 20
        mock_view.show_popup.assert_called()
        mock_view.update_menu.assert_called()

    def test_set_stand_duration(self, temp_config, mock_log, mock_view):
        ctrl = ReminderController(temp_config, mock_log, mock_view)
        ctrl.set_stand_duration(30)
        assert temp_config.stand_duration == 30
        mock_view.show_popup.assert_called()

    def test_manual_remind_water(self, temp_config, mock_log, mock_view):
        ctrl = ReminderController(temp_config, mock_log, mock_view)
        ctrl.manual_remind("water")
        mock_log.append.assert_called_with("water")
        mock_view.show_popup.assert_called_once()

    def test_manual_remind_stand(self, temp_config, mock_log, mock_view):
        ctrl = ReminderController(temp_config, mock_log, mock_view)
        ctrl.manual_remind("stand")
        mock_log.append.assert_called_with("stand")
        mock_view.show_popup.assert_called_once()

    def test_stop_cancels_timers(self, temp_config, mock_log, mock_view):
        ctrl = ReminderController(temp_config, mock_log, mock_view)
        ctrl.stop()
        mock_view.stop.assert_called_once()
