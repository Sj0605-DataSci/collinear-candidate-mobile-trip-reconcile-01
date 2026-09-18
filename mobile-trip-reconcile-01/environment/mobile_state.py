"""
Shared mission-log module used by every agent-facing tool script. The
mission "starts" (for the purposes of the scheduled incoming message) at
the timestamp of the agent's FIRST logged action -- not container boot --
so Docker/emulator boot latency never eats into the agent's real budget.
"""
import fcntl
import json
import time
from pathlib import Path

LOG_PATH = Path("/app/output/.mission_log.json")


def _load():
    if LOG_PATH.exists():
        return json.loads(LOG_PATH.read_text())
    return {"first_action_t": None, "log": []}


def log_action(action, **details):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    lock_path = LOG_PATH.with_suffix(".lock")
    with open(lock_path, "w") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        state = _load()
        now = time.time()
        if state["first_action_t"] is None:
            state["first_action_t"] = now
        entry = {"action": action, "real_t": now, **details}
        state["log"].append(entry)
        LOG_PATH.write_text(json.dumps(state))
        fcntl.flock(lf, fcntl.LOCK_UN)
    return state
