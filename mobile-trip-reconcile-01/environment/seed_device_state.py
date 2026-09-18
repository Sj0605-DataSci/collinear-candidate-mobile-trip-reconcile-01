#!/usr/bin/env python3
"""
Runs once after the emulator has finished booting and adb is connected.
Seeds the real Calendar app (via the calendar content provider) and the
Chat page's initial message thread (direct write into tripdesk.db, since
Chat is a website, not a native provider-backed app).

Real quirks discovered the hard way by testing directly against this
exact built image (not from documentation alone):
- `adb shell` reconstructs argv into ONE command line string for the
  DEVICE's own shell to re-tokenize. Passing the fully pre-quoted command
  as a single argv element (via shlex.quote, joined ourselves) is the only
  reliable way to survive that -- per-argument quoting gets mangled
  because adb re-joins everything with spaces before the device ever sees
  it, silently breaking on spaces AND on unescaped `&` (interpreted as the
  device shell's background-job operator).
- inserting into content://com.android.calendar/calendars requires
  ?caller_is_syncadapter=true plus account_name/account_type as BOTH URI
  query params AND explicit --bind values (missing either raises
  "the name must not be empty: null", a genuinely misleading error).
- the column is `ownerAccount` (camelCase), not `owner_account`.
- dtstart/dtend are epoch-milliseconds and overflow the 32-bit `i` type;
  must use `l` (long).
"""
import datetime
import json
import shlex
import sqlite3
import subprocess
import sys

ADB = "/opt/android-sdk/platform-tools/adb"
DB_PATH = "/data/tripdesk.db"
LOCAL_CAL_URI = ("content://com.android.calendar/calendars"
                  "?caller_is_syncadapter=true&account_name=trip-planner-local&account_type=LOCAL")


def adb_shell(*cmd_parts):
    full = " ".join(shlex.quote(p) for p in cmd_parts)
    r = subprocess.run([ADB, "shell", full], capture_output=True, text=True)
    if r.stderr.strip() or "Error while accessing provider" in r.stdout:
        print(f"adb shell command produced an error -- cmd={full!r} stdout={r.stdout!r} stderr={r.stderr!r}",
              file=sys.stderr)
        sys.exit(1)
    return r.stdout


def _find_id_for_local_account(out):
    # content query output format: "Row: <N> _id=<X>, account_name=<Y>" --
    # the "Row: N" prefix is SPACE-separated from _id=X (not comma-space
    # like the rest), so it must be stripped before splitting on ", ".
    for line in out.splitlines():
        if not line.startswith("Row:") or "account_name=trip-planner-local" not in line:
            continue
        after_row_prefix = line.split(" ", 2)[-1]  # drop "Row:" and the index
        for part in after_row_prefix.split(", "):
            if part.strip().startswith("_id="):
                return part.strip().split("=", 1)[1]
    return None


def get_or_create_local_calendar_id():
    out = adb_shell("content", "query", "--uri", "content://com.android.calendar/calendars",
                     "--projection", "_id:account_name")
    cal_id = _find_id_for_local_account(out)
    if cal_id:
        return cal_id

    adb_shell("content", "insert", "--uri", LOCAL_CAL_URI,
              "--bind", "account_name:s:trip-planner-local",
              "--bind", "account_type:s:LOCAL",
              "--bind", "name:s:TripPlanner",
              "--bind", "calendar_displayName:s:TripPlanner",
              "--bind", "calendar_color:i:-14069085",
              "--bind", "calendar_access_level:i:700",
              "--bind", "ownerAccount:s:trip-planner-local",
              "--bind", "visible:i:1",
              "--bind", "sync_events:i:1")

    out = adb_shell("content", "query", "--uri", "content://com.android.calendar/calendars",
                     "--projection", "_id:account_name")
    cal_id = _find_id_for_local_account(out)
    if cal_id:
        return cal_id
    raise RuntimeError(f"could not create/find local calendar, query returned: {out!r}")


def date_to_epoch_millis(date_str, time_str):
    dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    return int(dt.timestamp() * 1000)


def seed_calendar(events):
    cal_id = get_or_create_local_calendar_id()
    for e in events:
        start_ms = date_to_epoch_millis(e["date"], e["time"])
        end_ms = start_ms + 60 * 60 * 1000
        adb_shell("content", "insert", "--uri", "content://com.android.calendar/events",
                  "--bind", f"calendar_id:i:{cal_id}",
                  "--bind", f"title:s:{e['title']}",
                  "--bind", f"dtstart:l:{start_ms}",
                  "--bind", f"dtend:l:{end_ms}",
                  "--bind", "eventTimezone:s:America/Los_Angeles",
                  "--bind", "hasAlarm:i:0")


def seed_contact(name, note):
    out = adb_shell("content", "insert", "--uri", "content://com.android.contacts/raw_contacts",
                     "--bind", "account_type:n:", "--bind", "account_name:n:")
    raw_id = None
    for line in out.splitlines():
        if "_id=" in line:
            raw_id = line.split("_id=", 1)[1].strip()
    if raw_id is None:
        out = adb_shell("content", "query", "--uri", "content://com.android.contacts/raw_contacts",
                         "--projection", "_id", "--sort", "_id DESC")
        for line in out.splitlines():
            if "_id=" in line:
                raw_id = line.split("_id=", 1)[1].strip()
                break
    adb_shell("content", "insert", "--uri", "content://com.android.contacts/data",
              "--bind", f"raw_contact_id:i:{raw_id}",
              "--bind", "mimetype:s:vnd.android.cursor.item/name",
              "--bind", f"data1:s:{name}")
    adb_shell("content", "insert", "--uri", "content://com.android.contacts/data",
              "--bind", f"raw_contact_id:i:{raw_id}",
              "--bind", "mimetype:s:vnd.android.cursor.item/note",
              "--bind", f"data1:s:{note}")


def seed_chat(messages):
    conn = sqlite3.connect(DB_PATH)
    for m in messages:
        conn.execute("INSERT INTO messages (sender, text, real_t) VALUES (?, ?, 0)", (m["from"], m["text"]))
    conn.commit()
    conn.close()


def main():
    content = json.load(open("/app/content_seed.json"))
    seed_calendar(content["calendar_events"])
    seed_chat(content["sms_thread_existing"])
    seed_contact(content["contact"]["name"], content["contact"]["note"])
    print("device state seeded")


if __name__ == "__main__":
    sys.exit(main())
