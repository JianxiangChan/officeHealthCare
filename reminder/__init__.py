# -*- coding: utf-8 -*-
from .controller import ReminderController
from .model import Config, ReminderLog
from .view import TrayView


def run():
    config = Config()
    log = ReminderLog()
    view = TrayView()
    ctrl = ReminderController(config, log, view)
    ctrl.start()  # blocks on pystray event loop
