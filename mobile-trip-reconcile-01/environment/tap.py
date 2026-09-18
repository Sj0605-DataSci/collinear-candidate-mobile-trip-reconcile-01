#!/usr/bin/env python3
"""
Tap the screen at a specific pixel coordinate, matching what you see in the
last screenshot (0,0 is the top-left corner; the screen is 1080 wide by
2340 tall). Find the coordinate yourself by looking at the image -- there
is no element list or accessibility ID to target by name.

Usage:
  python3 /app/tap.py <x> <y>
"""
import sys

sys.path.insert(0, "/app")
from android_tools import adb_shell
from mobile_state import log_action

if len(sys.argv) != 3:
    print("usage: tap.py <x> <y>")
    sys.exit(2)

x, y = int(sys.argv[1]), int(sys.argv[2])
adb_shell("input", "tap", str(x), str(y))
log_action("tap", x=x, y=y)
print(f"Tapped ({x}, {y}). Take a screenshot to see the result.")
