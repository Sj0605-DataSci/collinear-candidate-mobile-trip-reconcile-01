#!/usr/bin/env python3
"""
Oracle solution: a literal recorded human interaction trace, replayed
through the SAME tool scripts the agent uses (screenshot/tap/swipe/home/
wait) -- not a database shortcut. Mirrors how a person would actually do
this: check Calendar, check Contacts, check Chat (only the pre-correction
picture is up yet), wait around doing other things, re-check Chat, catch
the correction, then book the flight+hotel that matches the corrected
date.

All coordinates were determined by interactively exploring this exact
built image (via `adb shell uiautomator dump` for native UI elements, and
visual inspection at the real 1080x2340 resolution for in-page web
content, which has no accessibility tree) -- not guessed. See
RUN_REPORT.md for the exploration log.

Note on navigation: instruction.md tells the agent it can navigate by
tapping the address bar and typing a URL (validated to work via manual
interactive testing -- see RUN_REPORT.md). For automated oracle replay
specifically, address-bar retyping via blind `input text` + keyevent
timing proved unreliable across repeated runs (Chrome's omnibox
autocomplete/suggestion interaction raced with fixed sleep() delays,
twice landing on an unrelated page). The oracle instead opens each page
via a direct Android VIEW intent, which is deterministic -- this is a
oracle-script robustness choice, not evidence the task requires it; the
task remains solvable via the documented omnibox method.
"""
import subprocess
import sys
import time

TOOLS = "/app"
ADB = "/opt/android-sdk/platform-tools/adb"


def run(script, *args):
    cmd = ["python3", f"{TOOLS}/{script}"] + [str(a) for a in args]
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(f"$ {' '.join(cmd)}\n{r.stdout}{r.stderr}")
    return r


def open_url(url):
    r = subprocess.run([ADB, "shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", url],
                        capture_output=True, text=True)
    print(f"$ am start -d {url}\n{r.stdout}{r.stderr}")
    return r


def main():
    # 1. Look at the phone.
    run("screenshot.py")

    # 2. Open the app drawer to find Calendar (not on the home screen dock).
    run("swipe.py", 540, 2200, 540, 800, 300)
    run("screenshot.py")

    # 3. Open Calendar.
    run("tap.py", 177, 784)
    time.sleep(2)
    run("screenshot.py")

    # First-run onboarding (2 pages) -- a real app's first launch.
    run("tap.py", 1006, 2192)
    time.sleep(1)
    run("tap.py", 539, 2114)
    time.sleep(2)
    run("screenshot.py")  # real calendar agenda: Dentist, Board meeting (Oct 19
                          # 5-6pm -- doesn't block a same-day return), Team standup

    # 3b. A real trip involves more than one contact/app to check. Visit
    # Contacts too and look at Sam's card -- a real, separate native app,
    # not just another page inside Chrome/TripDesk.
    run("home.py")
    time.sleep(1)
    run("swipe.py", 540, 2200, 540, 800, 300)
    time.sleep(1)
    run("screenshot.py")
    run("tap.py", 177, 1097)  # Contacts icon (app drawer)
    time.sleep(2)
    run("screenshot.py")
    run("tap.py", 659, 2193)  # "Skip" on Contacts' own first-run screen
    time.sleep(2)
    run("screenshot.py")
    run("tap.py", 664, 573)  # "Sam" in the contact list
    time.sleep(2)
    run("screenshot.py")  # About Sam: "worth double-checking any date they've
                          # given before locking anything in" -- reinforces
                          # not trusting the first-pass chat read

    # 4. Open Chrome and navigate to the trip Chat thread. Chrome's own
    # first-run nag screens (welcome/notifications/etc -- multiple,
    # appearing unpredictably at different points) are suppressed at boot
    # via chrome-command-line flags -- incidental app chrome, not designed
    # task difficulty; a real device would normally have these already
    # dismissed from prior use anyway.
    run("home.py")
    time.sleep(1)
    run("tap.py", 666, 1910)  # Chrome icon (home screen dock)
    time.sleep(2)
    run("screenshot.py")

    # 5. Now navigate to the trip Chat thread.
    open_url("http://10.0.2.2:8080/chat")
    time.sleep(2)
    run("screenshot.py")  # first pass: calendar + this thread both genuinely
                          # support returning ON the 19th -- nothing here reads
                          # as unresolved, so it would be reasonable to book
                          # off this alone. A careful person still gives it a
                          # bit before treating a same-day travel plan as
                          # locked, the way you'd let a plan sit overnight
                          # before booking something non-refundable.
    for _ in range(9):
        run("wait.py", 55)

    # 6. Re-check Chat for the promised follow-up (reload via the same URL).
    open_url("http://10.0.2.2:8080/chat")
    time.sleep(2)
    run("screenshot.py")  # the corrected message has landed: return by the
                          # 18th, not the 19th

    # 7. Book the flight matching the corrected date (depart 10-12, return
    # 10-18, $260 -- SkyLink, third card on the Flights page).
    open_url("http://10.0.2.2:8080/flights")
    time.sleep(2)
    run("screenshot.py")
    run("tap.py", 192, 1650)  # Select on the $260 SkyLink 10-12->10-18 card
    time.sleep(1)
    run("screenshot.py")

    # 8. Book the matching hotel (Budget Inn Denver, checkout 10-18, $70/night
    # -- first/cheapest card, and the only one with correct dates).
    run("tap.py", 297, 688)  # "Now choose a hotel"
    time.sleep(1)
    run("screenshot.py")
    run("tap.py", 192, 838)  # Select on Budget Inn Denver
    time.sleep(1)
    run("screenshot.py")

    # 9. Review and confirm.
    run("tap.py", 273, 688)  # "Review & Confirm"
    time.sleep(1)
    run("screenshot.py")
    run("tap.py", 263, 1163)  # "Confirm Booking"
    time.sleep(1)
    run("screenshot.py")

    print("oracle_steps complete")


if __name__ == "__main__":
    sys.exit(main())
