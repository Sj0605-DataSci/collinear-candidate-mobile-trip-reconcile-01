#!/usr/bin/env python3
"""
Type text into whatever field is currently focused (tap the field first).

Usage:
  python3 /app/type_text.py "some text to type"
"""
import sys

sys.path.insert(0, "/app")
from android_tools import adb_shell
from mobile_state import log_action

if len(sys.argv) != 2:
    print('usage: type_text.py "text to type"')
    sys.exit(2)

text = sys.argv[1]
# `input text` itself requires spaces escaped as %s (its own arg parsing,
# separate from shell quoting); adb_shell handles shell-special characters
# (&, quotes, etc.) that might still be in the text
escaped = text.replace("%", "%25").replace(" ", "%s")
adb_shell("input", "text", escaped)
log_action("type_text", text=text)
print(f"Typed: {text}")
