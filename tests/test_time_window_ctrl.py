import json
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from reminder.model import Config, ReminderLog, DEFAULT_CONFIG
from reminder.view import TrayView
from reminder.controller import ReminderController


@pytest.fixture
def controller():
    data = {**DEFAULT_CONFIG, "start_time": "08:30", "end_time": "20:30"}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(data, f)
        tp = f.name
    with patch("reminder.model.CONFIG_FILE", Path(tp)):
        config = Config()
        log = MagicMock(spec=ReminderLog)
        view = MagicMock(spec=TrayView)
        yield ReminderController(config, log, view)
    Path(tp).unlink()


class TestActiveWindow:
    def test_inside_window(self, controller):
        now = datetime(2026, 7, 14, 10, 0, 0)
        assert controller._is_in_active_window(now=now) is True

    def test_before_window(self, controller):
        now = datetime(2026, 7, 14, 6, 0, 0)
        assert controller._is_in_active_window(now=now) is False

    def test_after_window(self, controller):
        now = datetime(2026, 7, 14, 22, 0, 0)
        assert controller._is_in_active_window(now=now) is False

    def test_edge_start(self, controller):
        now = datetime(2026, 7, 14, 8, 30, 0)
        assert controller._is_in_active_window(now=now) is True

    def test_edge_end(self, controller):
        now = datetime(2026, 7, 14, 20, 30, 0)
        assert controller._is_in_active_window(now=now) is True


class TestTimerRespectsWindow:
    def test_water_timer_skipped_outside_window(self, controller):
        with patch.object(controller, "_is_in_active_window", return_value=False):
            controller._on_water_timer()
            controller._view.show_popup.assert_not_called()
            controller._log.append.assert_not_called()

    def test_stand_timer_skipped_outside_window(self, controller):
        with patch.object(controller, "_is_in_active_window", return_value=False):
            controller._on_stand_timer()
            controller._view.show_popup.assert_not_called()
            controller._log.append.assert_not_called()

    def test_water_timer_fires_inside_window(self, controller):
        with patch.object(controller, "_is_in_active_window", return_value=True):
            controller._on_water_timer()
            controller._view.show_popup.assert_called_once()
            controller._log.append.assert_called_with("water")

    def test_stand_timer_fires_inside_window(self, controller):
        with patch.object(controller, "_is_in_active_window", return_value=True):
            controller._on_stand_timer()
            controller._view.show_popup.assert_called_once()
            controller._log.append.assert_called_with("stand")


class TestTimeWindowMenu:
    def test_has_start_time_submenu(self, controller):
        menu = controller.build_menu()
        for item in list(menu):
            if hasattr(item, "text") and "开始" in item.text:
                assert item.submenu is not None
                sub_texts = [si.text for si in list(item.submenu)]
                assert any("08:00" in t for t in sub_texts)
                return
        assert False, "No start time submenu"

    def test_has_end_time_submenu(self, controller):
        menu = controller.build_menu()
        for item in list(menu):
            if hasattr(item, "text") and "结束" in item.text:
                assert item.submenu is not None
                sub_texts = [si.text for si in list(item.submenu)]
                assert any("20:00" in t for t in sub_texts)
                return
        assert False, "No end time submenu"

    def test_set_start_time(self, controller):
        controller.set_start_time("08:00")
        assert controller._config.start_time == "08:00"

    def test_set_end_time(self, controller):
        controller.set_end_time("17:00")
        assert controller._config.end_time == "17:00"
