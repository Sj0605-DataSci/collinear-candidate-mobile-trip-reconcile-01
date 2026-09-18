#!/usr/bin/env python3
"""
Swipe from one point to another (e.g. to scroll a page or a list). Duration
is in milliseconds; a slower/longer swipe scrolls less per gesture, a fast
short one flings further.

Usage:
  python3 /app/swipe.py <x1> <y1> <x2> <y2> [duration_ms]
"""
import sys

sys.path.insert(0, "/app")
from android_tools import adb_shell
from mobile_state import log_action

if len(sys.argv) not in (5, 6):
    print("usage: swipe.py <x1> <y1> <x2> <y2> [duration_ms]")
    sys.exit(2)

x1, y1, x2, y2 = (int(a) for a in sys.argv[1:5])
duration = sys.argv[5] if len(sys.argv) == 6 else "300"
adb_shell("input", "swipe", str(x1), str(y1), str(x2), str(y2), duration)
log_action("swipe", x1=x1, y1=y1, x2=x2, y2=y2, duration_ms=int(duration))
print(f"Swiped ({x1},{y1}) -> ({x2},{y2}). Take a screenshot to see the result.")
