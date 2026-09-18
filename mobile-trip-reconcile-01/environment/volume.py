#!/usr/bin/env python3
"""
Press the volume up or down key.

Usage:
  python3 /app/volume.py <up|down>
"""
import sys

sys.path.insert(0, "/app")
from android_tools import adb_shell
from mobile_state import log_action

if len(sys.argv) != 2 or sys.argv[1] not in ("up", "down"):
    print("usage: volume.py <up|down>")
    sys.exit(2)

direction = sys.argv[1]
keycode = "KEYCODE_VOLUME_UP" if direction == "up" else "KEYCODE_VOLUME_DOWN"
adb_shell("input", "keyevent", keycode)
log_action("volume", direction=direction)
print(f"Volume {direction}.")
