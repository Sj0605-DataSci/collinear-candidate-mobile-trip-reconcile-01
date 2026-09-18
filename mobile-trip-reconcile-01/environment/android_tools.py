"""Shared adb helper used by every agent-facing tool script."""
import shlex
import subprocess
import sys
import time

ADB = "/opt/android-sdk/platform-tools/adb"


def _raw_adb(*args):
    return subprocess.run([ADB] + list(args), capture_output=True, text=True)


def wait_for_boot(timeout_sec=180.0):
    """Defensive readiness wait -- the emulator normally finishes booting
    before the agent's first tool call (the container's entrypoint boots it
    eagerly at startup), but this makes every tool call robust even if a
    call races ahead of that, rather than failing outright."""
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        r = _raw_adb("shell", "getprop", "sys.boot_completed")
        if r.returncode == 0 and r.stdout.strip() == "1":
            return True
        time.sleep(1.0)
    return False


def adb(*args, check=True):
    wait_for_boot()
    result = _raw_adb(*args)
    if check and result.returncode != 0:
        print(f"adb command failed: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    return result.stdout


def adb_shell(*device_cmd_parts, check=True):
    """Runs a command on the DEVICE's own shell. `adb shell` reconstructs
    multiple argv elements into one command line by joining with spaces --
    if any part contains a space (or a shell-special character like `&`),
    that silently breaks (space splits into extra args; `&` gets read as
    the device shell's background-job operator) unless the WHOLE command
    is pre-quoted ourselves and passed as a single argv element, which is
    what this does. Discovered the hard way debugging seed_device_state.py
    -- prefer this over adb('shell', ...) for anything that isn't pure
    numbers/keywords."""
    wait_for_boot()
    full = " ".join(shlex.quote(p) for p in device_cmd_parts)
    result = _raw_adb("shell", full)
    if check and result.returncode != 0:
        print(f"adb shell command failed: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    return result.stdout
