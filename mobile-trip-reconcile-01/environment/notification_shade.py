#!/usr/bin/env python3
"""
Pull down the notification shade to see current notifications.

Usage:
  python3 /app/notification_shade.py
"""
import sys

sys.path.insert(0, "/app")
from android_tools import adb_shell
from mobile_state import log_action

adb_shell("cmd", "statusbar", "expand-notifications")
log_action("notification_shade")
print("Opened the notification shade. Take a screenshot to see the result.")
