# -*- coding: utf-8 -*-
import pystray
from unittest.mock import MagicMock, patch

import pytest

from reminder.view import (
    build_interval_submenu,
    create_tray_icon_image,
    TrayView,
)


class TestBuildIntervalSubmenu:
    def test_returns_menu_with_correct_count(self):
        called_with = []
        menu = build_interval_submenu([15, 30, 45], 30, lambda v: called_with.append(v))
        items = list(menu)
        assert len(items) == 3

    def test_current_value_has_checkmark(self):
        menu = build_interval_submenu([15, 30], 15, lambda v: None)
        items = list(menu)
        assert chr(0x2705) in items[0].text
        assert chr(0x2705) not in items[1].text

    def test_callback_receives_correct_value(self):
        called_with = []
        menu = build_interval_submenu([15, 30], 15, lambda v: called_with.append(v))
        items = list(menu)
        items[1]._action(None, items[1])
        assert called_with == [30]


class TestCreateIcon:
    def test_returns_64x64_rgba(self):
        img = create_tray_icon_image()
        assert img.size == (64, 64)
        assert img.mode == "RGBA"


class TestTrayView:
    def test_show_popup_starts_thread(self):
        view = TrayView()
        with patch("threading.Thread") as mock_thread:
            view.show_popup("Test", "Message", "X")
            mock_thread.assert_called_once()

    def test_create_icon_sets_icon(self):
        view = TrayView()
        img = create_tray_icon_image()
        menu = pystray.Menu(pystray.MenuItem("test", lambda: None))
        view.create_icon(img, "Test", menu)
        assert view._icon is not None
        assert view._icon.name == "health_reminder"
