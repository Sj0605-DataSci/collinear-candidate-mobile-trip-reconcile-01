#!/usr/bin/env python3
"""
Capture the current phone screen. This is your only window into the
device -- there is no accessibility tree, no semantic app list, no "what's
on screen" text dump. Read the image yourself, the way you'd actually look
at your phone.

Usage:
  python3 /app/screenshot.py
"""
import subprocess
import sys

sys.path.insert(0, "/app")
from android_tools import ADB, wait_for_boot
from mobile_state import log_action

wait_for_boot()
result = subprocess.run([ADB, "exec-out", "screencap", "-p"], capture_output=True)
if result.returncode != 0 or not result.stdout:
    print("screenshot failed")
    sys.exit(1)

out_path = "/app/output/screen.png"
with open(out_path, "wb") as f:
    f.write(result.stdout)

log_action("screenshot")
print(f"Screenshot saved to {out_path} -- read this image to see the current phone screen.")
