#!/usr/bin/env python3
"""
Open the recent-apps switcher (shows recently used apps as cards).

Usage:
  python3 /app/recents.py
"""
import sys

sys.path.insert(0, "/app")
from android_tools import adb_shell
from mobile_state import log_action

adb_shell("input", "keyevent", "KEYCODE_APP_SWITCH")
log_action("recents")
print("Opened recent apps. Take a screenshot to see the result.")
