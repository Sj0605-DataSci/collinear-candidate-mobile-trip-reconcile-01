#!/usr/bin/env python3
"""
Wait for real seconds to pass (e.g. to let a page finish loading, or to
deliberately pause). Capped at 60s per call -- call it again if you need
to wait longer.

Usage:
  python3 /app/wait.py <seconds>
"""
import sys
import time

sys.path.insert(0, "/app")
from mobile_state import log_action

if len(sys.argv) != 2:
    print("usage: wait.py <seconds>")
    sys.exit(2)

seconds = max(0.0, min(float(sys.argv[1]), 60.0))
time.sleep(seconds)
log_action("wait", seconds=seconds)
print(f"Waited {seconds:.1f}s.")
