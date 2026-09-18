#!/usr/bin/env python3
"""
Long-press (hold) the screen at a specific pixel coordinate -- e.g. to
select text or trigger a context menu.

Usage:
  python3 /app/long_press.py <x> <y> [duration_ms]
"""
import sys

sys.path.insert(0, "/app")
from android_tools import adb_shell
from mobile_state import log_action

if len(sys.argv) not in (3, 4):
    print("usage: long_press.py <x> <y> [duration_ms]")
    sys.exit(2)

x, y = int(sys.argv[1]), int(sys.argv[2])
duration = sys.argv[3] if len(sys.argv) == 4 else "800"
adb_shell("input", "swipe", str(x), str(y), str(x), str(y), duration)
log_action("long_press", x=x, y=y, duration_ms=int(duration))
print(f"Long-pressed ({x}, {y}). Take a screenshot to see the result.")
