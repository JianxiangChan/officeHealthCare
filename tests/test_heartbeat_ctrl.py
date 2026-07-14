# -*- coding: utf-8 -*-
import json, tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from reminder.model import Config, ReminderLog, DEFAULT_CONFIG
from reminder.view import TrayView
from reminder.controller import ReminderController


@pytest.fixture
def controller():
    data = {**DEFAULT_CONFIG}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(data, f)
        tp = f.name
    with patch("reminder.model.CONFIG_FILE", Path(tp)):
        config = Config()
        log = MagicMock(spec=ReminderLog)
        view = MagicMock(spec=TrayView)
        yield ReminderController(config, log, view)
    Path(tp).unlink()


class TestControllerHeartbeat:
    def test_start_all_timers_starts_heartbeat(self, controller):
        controller._start_all_timers()
        assert controller._heartbeat_timer is not None

    def test_on_heartbeat_logs_status(self, controller):
        controller._on_heartbeat()
        controller._log.heartbeat.assert_called_once()

    def test_on_heartbeat_reschedules(self, controller):
        controller._on_heartbeat()
        assert controller._heartbeat_timer is not None

    def test_cancel_all_timers_cancels_heartbeat(self, controller):
        controller._start_all_timers()
        controller._cancel_all_timers()
        assert controller._heartbeat_timer is None

    def test_heartbeat_shows_remaining_time(self, controller):
        from datetime import datetime
        controller._schedule_water()
        controller._schedule_stand()
        controller._water_timer_start = datetime(2026, 7, 14, 10, 0, 0)
        controller._stand_timer_start = datetime(2026, 7, 14, 10, 0, 0)
        now = datetime(2026, 7, 14, 10, 5, 0)
        controller._on_heartbeat(now=now)
        call_args = controller._log.heartbeat.call_args[0][0]
        assert "25m" in call_args
        assert "40m" in call_args

    def test_schedule_water_sets_start_timestamp(self, controller):
        controller._schedule_water()
        assert controller._water_timer_start is not None, '_schedule_water must set _water_timer_start'

    def test_schedule_stand_sets_start_timestamp(self, controller):
        controller._schedule_stand()
        assert controller._stand_timer_start is not None, '_schedule_stand must set _stand_timer_start'
