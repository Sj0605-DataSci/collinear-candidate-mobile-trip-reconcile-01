"""
Verifier for mobile-trip-reconcile-01. Ground truth is read directly from
TripDesk's own SQLite DB (mirrors MobileWorld's "backend database
verification" method) -- no LLM-judge, no string matching on a written
report. The mission action log's real timestamps are cross-checked against
when the new message actually arrived, so a booking that happens to land on
the correct date by luck (before the agent could possibly have known) is
distinguished from one genuinely backed by having read the update.
"""
import json
import sqlite3
from pathlib import Path

DB_PATH = Path("/data/tripdesk.db")
LOG_PATH = Path("/app/output/.mission_log.json")
ANSWER_KEY_PATH = Path("/tests/answer_key.json")
REWARD_PATH = Path("/logs/verifier/reward.json")
NOTES_PATH = Path("/logs/verifier/notes.json")


def main():
    reward = {
        "overall": 0.0,
        "booking_confirmed": 0.0,
        "correct_depart_date": 0.0,
        "correct_return_date": 0.0,
        "within_budget": 0.0,
        "flight_hotel_dates_consistent": 0.0,
        "genuine_not_premature": 0.0,
    }
    notes = []

    answer_key = json.loads(ANSWER_KEY_PATH.read_text())
    true_depart = answer_key["true_required_depart_date"]
    true_return = answer_key["true_required_return_date"]
    budget_max = answer_key["true_budget_max"]
    delay_seconds = answer_key["sms_new_arrival_delay_seconds"]

    if not DB_PATH.exists():
        notes.append("tripdesk.db missing -- TripDesk server never ran or wrote nothing")
        _write(reward, notes)
        return

    conn = sqlite3.connect(str(DB_PATH))
    row = conn.execute(
        "SELECT flight_id, hotel_id, confirmed_at, confirmed_real_t FROM bookings "
        "WHERE confirmed_at IS NOT NULL ORDER BY id DESC LIMIT 1"
    ).fetchone()

    if not row:
        notes.append("no confirmed booking found in tripdesk.db (bookings table has no "
                      "row with confirmed_at set)")
        conn.close()
        _write(reward, notes)
        return

    reward["booking_confirmed"] = 1.0
    flight_id, hotel_id, confirmed_at, confirmed_real_t = row
    notes.append(f"confirmed booking: flight_id={flight_id} hotel_id={hotel_id} "
                 f"confirmed_at={confirmed_at} confirmed_real_t={confirmed_real_t}")

    flight = conn.execute("SELECT route, depart_date, return_date, airline, price FROM flights "
                           "WHERE id=?", (flight_id,)).fetchone() if flight_id else None
    hotel = conn.execute("SELECT name, checkin_date, checkout_date, price_per_night FROM hotels "
                          "WHERE id=?", (hotel_id,)).fetchone() if hotel_id else None
    conn.close()

    if not flight or not hotel:
        notes.append(f"booking incomplete: flight={flight} hotel={hotel} (both a flight and a "
                      f"hotel must be selected before confirming)")
        _write(reward, notes)
        return

    route, depart_date, return_date, airline, flight_price = flight
    hotel_name, checkin_date, checkout_date, price_per_night = hotel
    notes.append(f"flight: {route} {depart_date}->{return_date} ({airline}) ${flight_price}")
    notes.append(f"hotel: {hotel_name} {checkin_date}->{checkout_date} ${price_per_night}/night")

    reward["correct_depart_date"] = 1.0 if depart_date == true_depart else 0.0
    reward["correct_return_date"] = 1.0 if return_date == true_return else 0.0
    if depart_date != true_depart:
        notes.append(f"WRONG depart date: booked {depart_date}, required {true_depart}")
    if return_date != true_return:
        notes.append(f"WRONG return date: booked {return_date}, required {true_return} -- this is "
                      f"the expected failure mode for an agent that read messages once and never "
                      f"re-checked after the mid-mission update")

    reward["flight_hotel_dates_consistent"] = (
        1.0 if (checkin_date == depart_date and checkout_date == return_date) else 0.0
    )
    if reward["flight_hotel_dates_consistent"] == 0.0:
        notes.append(f"flight and hotel dates don't match each other: flight "
                      f"{depart_date}->{return_date} vs hotel {checkin_date}->{checkout_date}")

    import datetime
    nights = (datetime.date.fromisoformat(checkout_date) - datetime.date.fromisoformat(checkin_date)).days
    total_price = flight_price + price_per_night * max(nights, 0)
    reward["within_budget"] = 1.0 if total_price <= budget_max else 0.0
    notes.append(f"total price ${total_price} ({nights} nights) vs budget max ${budget_max}")

    # genuine_not_premature: only meaningful when the return date is correct.
    # If the agent got the WRONG date, this key is scored 1.0 (not double-
    # penalized -- correct_return_date already captures that failure).
    if reward["correct_return_date"] == 0.0:
        reward["genuine_not_premature"] = 1.0
    else:
        first_action_t = None
        if LOG_PATH.exists():
            try:
                mission_state = json.loads(LOG_PATH.read_text())
                first_action_t = mission_state.get("first_action_t")
            except (json.JSONDecodeError, OSError):
                pass
        if first_action_t is None or confirmed_real_t is None:
            notes.append("cannot verify timing (missing mission log or confirmed_real_t) -- "
                         "treating as not genuinely evidenced")
            reward["genuine_not_premature"] = 0.0
        else:
            elapsed = confirmed_real_t - first_action_t
            reward["genuine_not_premature"] = 1.0 if elapsed >= delay_seconds else 0.0
            notes.append(f"booking confirmed {elapsed:.1f}s after first action "
                         f"(new message arrives at {delay_seconds}s) -- "
                         f"{'genuinely evidenced' if elapsed >= delay_seconds else 'PREMATURE: correct date reached before the update could have been read, i.e. a lucky guess not genuine evidence'}")

    reward["overall"] = round(
        0.10 * reward["booking_confirmed"]
        + 0.10 * reward["correct_depart_date"]
        + 0.35 * reward["correct_return_date"]
        + 0.15 * reward["within_budget"]
        + 0.10 * reward["flight_hotel_dates_consistent"]
        + 0.20 * reward["genuine_not_premature"],
        4,
    )

    # diagnostic only, not gated into overall: loose proxy for genuine
    # multi-app navigation (home screen visits imply real app switching,
    # not just guessing at TripDesk in isolation)
    if LOG_PATH.exists():
        try:
            mission_state = json.loads(LOG_PATH.read_text())
            log = mission_state.get("log", [])
            home_count = sum(1 for e in log if e.get("action") == "home")
            reward["actions_used_total"] = len(log)
            reward["home_screen_visits"] = home_count
            notes.append(f"actions_used_total={len(log)} home_screen_visits={home_count}")
        except (json.JSONDecodeError, OSError):
            pass

    _write(reward, notes)


def _write(reward, notes):
    REWARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    REWARD_PATH.write_text(json.dumps(reward, indent=2))
    NOTES_PATH.write_text(json.dumps(notes, indent=2))
    print(json.dumps({**reward, "notes": notes}, indent=2))


if __name__ == "__main__":
    main()
