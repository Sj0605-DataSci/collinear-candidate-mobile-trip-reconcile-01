#!/usr/bin/env python3
"""
Press the back button.

Usage:
  python3 /app/back.py
"""
import sys

sys.path.insert(0, "/app")
from android_tools import adb_shell
from mobile_state import log_action

adb_shell("input", "keyevent", "KEYCODE_BACK")
log_action("back")
print("Pressed back. Take a screenshot to see the result.")
