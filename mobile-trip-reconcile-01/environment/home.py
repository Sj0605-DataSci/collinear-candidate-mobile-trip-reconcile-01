#!/usr/bin/env python3
"""
Press the home button, returning to the phone's home screen. Use this to
switch apps -- there is no "open app by name" shortcut; find the app's
icon on the home screen (or in the app drawer) and tap it yourself, the
way you would on a real phone.

Usage:
  python3 /app/home.py
"""
import sys

sys.path.insert(0, "/app")
from android_tools import adb_shell
from mobile_state import log_action

adb_shell("input", "keyevent", "KEYCODE_HOME")
log_action("home")
print("Pressed home. Take a screenshot to see the home screen.")
