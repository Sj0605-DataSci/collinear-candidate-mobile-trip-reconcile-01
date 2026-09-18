#!/usr/bin/env python3
"""
Background daemon: waits for the agent's first logged action (see
mobile_state.py), then after content_seed.json's sms_new_arrival.delay_seconds
has elapsed, inserts the new message into the Chat thread AND posts a real
Android system notification (a genuine heads-up banner the agent would see
on the home screen or notification shade, not something it has to guess to
poll for) -- this is what actually fires the mid-mission "new text" event.
"""
import json
import sqlite3
import subprocess
import time
from pathlib import Path

ADB = "/opt/android-sdk/platform-tools/adb"
DB_PATH = "/data/tripdesk.db"
LOG_PATH = Path("/app/output/.mission_log.json")


def adb(*args):
    subprocess.run([ADB] + list(args), check=False, capture_output=True, text=True)


def wait_for_first_action():
    while True:
        if LOG_PATH.exists():
            try:
                state = json.loads(LOG_PATH.read_text())
                if state.get("first_action_t"):
                    return state["first_action_t"]
            except (json.JSONDecodeError, OSError):
                pass
        time.sleep(1.0)


def main():
    content = json.load(open("/app/content_seed.json"))
    arrival = content["sms_new_arrival"]

    first_t = wait_for_first_action()
    target_t = first_t + arrival["delay_seconds"]
    while True:
        now = time.time()
        if now >= target_t:
            break
        time.sleep(min(2.0, target_t - now))

    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO messages (sender, text, real_t) VALUES (?, ?, ?)",
                 (arrival["from"], arrival["text"], time.time()))
    conn.commit()
    conn.close()

    preview = arrival["text"][:60] + ("..." if len(arrival["text"]) > 60 else "")
    adb("shell", "cmd", "notification", "post", "-S", "bigtext", "-t", arrival["from"],
        "trip_chat_new_message", f"{arrival['from']}: {preview}")
    print(f"new message delivered at {time.time()}")


if __name__ == "__main__":
    main()
