# Run Report: mobile-trip-reconcile-01

## Summary

`claude-fable-5.1` at `reasoning_effort=high` **fails this task consistently**:
**4/4 real rollouts** (1 exploratory + 3 repeated) confirmed the exact same
wrong booking -- flight_id=1 + hotel_id=2, return date 2026-10-19 instead of
the required 2026-10-18 -- for `overall: 0.65` every time. The oracle
(literal recorded human-style trace, not a shortcut) passes cleanly at
`overall: 1.0`. The task is solvable; the model's specific, repeatable
failure is not re-checking a plausible first-pass conclusion after being
told the situation changed.

## Setup actually used (disclosed, not glossed over)

Rollouts were run via **Harbor's `claude-code` agent using OAuth
subscription auth** (`claude setup-token` -> `CLAUDE_CODE_OAUTH_TOKEN` +
`CLAUDE_FORCE_OAUTH=1`), **not** OpenRouter. This was a deliberate,
disclosed switch made mid-project:

- The original plan was OpenRouter (`-a codex -m anthropic/claude-fable-5.1
  --ak reasoning_effort=high`). Two real OpenRouter trials were run this
  way and are also reported below (see "Pre-recalibration trials").
- OpenRouter cost turned out to be ~$20/completed trial (66 actions) and
  ~$12 even on a trial that failed 25 turns in with a `402 Payment
  Required`, largely due to the accumulating-screenshot-history design that
  makes this a legitimate long-horizon/context-rot task in the first place
  (see DESIGN.md Section 8). Remaining OpenRouter budget after those two
  runs was ~$10 -- not enough for one more full trial, let alone 5.
- Harbor also ships a `claude-code` agent that authenticates against a
  Claude subscription's included usage (Pro/Max rate-limited window)
  instead of per-token API billing. Switching to it required two task.toml
  fixes (both applied and now in this repo):
  1. `[agent].allowed_hosts` needed `downloads.claude.ai`,
     `api.anthropic.com`, `claude.ai`, `console.anthropic.com`,
     `statsig.anthropic.com` added (was OpenRouter-only).
  2. `[environment].network_mode` needed to change from `no-network` to
     `allowlist` with the same host list -- the `claude-code` CLI installs
     and authenticates *inside* the same environment container at agent
     runtime, not in a separate sidecar, so `[agent]`'s policy alone didn't
     cover that traffic.
  3. Model ID needed to be `claude-fable-5-1` (hyphens), not
     `claude-fable-5.1` (dot) -- OpenRouter tolerated the dotted alias;
     direct Anthropic auth did not.
- This is a real, disclosed tradeoff: OpenRouter's pay-per-token billing is
  unambiguously clean for reproducing this exact result set under someone
  else's budget; the `claude-code`/OAuth route used here draws on a
  personal Claude subscription's included usage instead, which is
  appropriate for a single operator validating a task design but is not
  how a third party would reproduce cost-for-cost.

## Results (5-trial industry-standard n, using claude-code/OAuth)

| Trial | Route | flight/hotel booked | return_date | overall | genuine_not_premature | actions |
|---|---|---|---|---|---|---|
| Exploratory (pre-recal, 150s delay) | codex/OpenRouter | correct | 2026-10-18 | 1.0 | 1.0 (accidentally -- see below) | 66 |
| Exploratory 2 (pre-recal, 150s delay) | codex/OpenRouter | correct | 2026-10-18 | 1.0 | 1.0 (accidentally) | 36 |
| Recal-1 (480s delay) | codex/OpenRouter | -- | -- | infra failure (`402 Payment Required`, mid-run) | -- | 25 (partial) |
| Recal-2 (480s delay) | claude-code/OAuth | flight_id=1, hotel_id=2 | **2026-10-19 (WRONG)** | **0.65** | 1.0 | 72 |
| Recal-3 (480s delay) | claude-code/OAuth | flight_id=1, hotel_id=2 | **2026-10-19 (WRONG)** | **0.65** | 1.0 | 74 |
| Recal-4 (480s delay) | claude-code/OAuth | flight_id=1, hotel_id=2 | **2026-10-19 (WRONG)** | **0.65** | 1.0 | 74 |
| Recal-5 (480s delay) | claude-code/OAuth | flight_id=1, hotel_id=2 | **2026-10-19 (WRONG)** | **0.65** | 1.0 | 73 |

**4/4 trials at the corrected 480s calibration produced the identical
failure** (Recal-1 was an OpenRouter infra failure, not model evidence;
excluded from the failure-rate count). This is not a single bad rollout --
the model's specific miscalibration (form a conclusion at t=0, check the
notification shade once, don't treat "nothing new" there as reason to
re-read Chat, confirm) reproduces exactly, same flight/hotel IDs, same
price, near-identical action counts (72-74) every time.

Note on `genuine_not_premature: 1.0` despite the wrong date: per
`tests/verify.py`'s own design (see comment at
[tests/verify.py:101-105](tests/verify.py#L101-L105)), this field is only
meaningful -- and only scored -- when `correct_return_date` is already 1.0.
When the date itself is wrong, it's scored 1.0 by convention so the failure
isn't double-counted across two metrics; the actual failure signal here is
entirely in `correct_return_date: 0.0`.

## Calibration history (why 150s -> 480s)

See DESIGN.md Section 6 for the full table. Short version: at the original
150s delay, two real trials both confirmed the *correct* date -- but only
because the model's own natural pace (~490-500s to first read Chat) meant
the correction had already silently landed before it ever checked. That
was a clean pass that tested nothing. `delay_seconds` was raised to 480s
(just under that observed natural pace) so a careful agent reliably reads
Chat *before* the correction lands and must deliberately return later to
catch it -- which is exactly the capability gap the 4 consistent failures
above now demonstrate.

## Oracle validation

`harbor run -p . -a oracle -y`, run twice independently against this exact
image:
- Pre-recalibration (150s): `overall: 1.0`.
- Post-recalibration (480s): `overall: 1.0`, booking confirmed at 541.7s
  (past the 480s threshold), `genuine_not_premature: 1.0`.

The oracle (`solution/oracle_steps.py`) is a literal recorded human-style
trace -- Calendar, then Contacts, then Chat, a real ~495s wait, re-check
Chat, then book -- replayed through the identical tool scripts
(`screenshot.py`/`tap.py`/etc.) the agent uses, not a database shortcut.
This proves the task is solvable and that the recalibrated timing doesn't
break a correct solution path.

## How a human would actually do this

Walking through it the way a person would, with real screenshots at each
step (`media/screenshots/`, all real captures from a live build of this
task -- not mockups; full storyboard with suggested captions and video-
editing notes in `media/STORYBOARD.md`):

1. **Look at the phone.** No app list, no "what's on screen" description --
   just a home screen (`01-shared-home.png`). Calendar isn't on the dock,
   so swipe up to the app drawer (`02-shared-app-drawer.png`) to find it.
2. **Check Calendar first**, since that's usually the most reliable
   source for "am I free on this date." Real agenda view
   (`04-shared-calendar-agenda.png`): Dentist Oct 5, Board meeting Oct 19
   5-6pm, Team standup Oct 20. The board meeting doesn't block flying
   home *on* the 19th -- it's in the evening.
3. **Check Contacts too**, since Sam is a real saved contact and might
   have a note worth reading (`07-shared-sam-contact-card.png`).
4. **Open Chrome, go to Chat with Sam** (`08-shared-chrome-open.png`,
   `09-shared-chat-precorrection.png`). At this exact moment, the honest,
   reasonable reading is: fly out the 12th, fly back the 19th (board
   meeting doesn't conflict), keep the total under $900. **This is not a
   trick reading** -- it's what a careful person would also conclude
   right now, from real information.
5. **A careful person still doesn't lock in a non-refundable booking
   the instant they've read one message.** They'd give it some time --
   check email again before confirming a big purchase, let a decision
   sit overnight, whatever the real-world equivalent is. During that
   gap, a real notification arrives (`10-shared-notification-icon-appears.png`,
   `10b-shared-home-with-icon.png`) -- a small icon in the status bar,
   easy to miss if not looking for it.
6. **Noticing it (or just habitually re-checking Chat before booking
   something real) is the actual test.** Pulling the shade down
   (`11-shared-notification-shade.png`) shows "Sam: ..." -- worth
   re-opening Chat for the full message: the return date actually needs
   to be the 18th now, not the 19th.
7. **Only now go pick a flight and hotel** (`12-shared-flights-list.png`),
   this time filtering for the *corrected* return date (the 18th), not
   the one first read.
8. **Review together on My Trip, then confirm**
   (`15-trajA-mytrip-correct-date.png` -> `16-trajA-confirmed-correct.png`).

Total: roughly 40 real actions (taps, swipes, screenshots, a real ~9-minute
wait for the correction to land), which is exactly what the oracle does --
see `solution/oracle_steps.py` for the literal recorded script.

## Where the real model diverged

All 4 real `claude-fable-5.1-high` trials followed steps 1-4 identically
to the human walkthrough above -- same apps, same reasonable first
conclusion at step 4. The divergence happened at step 6: the model did
check the notification shade at some point in its run, but treated
"nothing new right now" as sufficient and went straight to booking off
its original read, without returning to Chat again before confirming.
The result (`13-trajB-mytrip-stale-date.png` -> `14-trajB-confirmed-WRONG.png`)
looks nearly identical to the correct outcome on-screen -- same "Booked!"
message, same internally-consistent flight+hotel pairing, still under
budget -- the only difference is the date, and nothing in the app itself
flags that difference. Catching it requires having gone back to Chat one
more time, which none of the 4 trials did.

## Traces

Full per-turn reasoning + tool-call traces for every trial listed above are
committed to this repo under `evidence/<label>__mobile-trip-reconcile-01__<trial-id>/`
(`claude-code.txt` for OAuth trials, `codex.txt` for OpenRouter trials,
`oracle.txt` for oracle runs) -- raw `stream-json`, one event per line,
including thinking blocks, every tool call and its result, in
chronological order. `reward.json` and `notes.json` in each trial
directory hold the graded outcome and the human-readable breakdown quoted
in the table above. (`jobs/` itself, the full local run directory these
were extracted from, is gitignored and not part of this repo -- it
contains bulk re-derivable data like full ATIF trajectory.json
conversions; `evidence/` is the curated, pushed subset.)

Direct paths for the 4 real target-model failures:
- `evidence/claudecode-postrecal-1__mobile-trip-reconcile-01__mTLCYQq/claude-code.txt`
- `evidence/claudecode-postrecal-2to4__mobile-trip-reconcile-01__cQmv2vU/claude-code.txt`
- `evidence/claudecode-postrecal-2to4__mobile-trip-reconcile-01__cXbJrY9/claude-code.txt`
- `evidence/claudecode-postrecal-2to4__mobile-trip-reconcile-01__rpRsTRz/claude-code.txt`

## Design and fairness documentation

See `DESIGN.md` for: the full trap enumeration (8 distinct designed
failure surfaces, not just the timing trap), the fairness audit against
the assignment's rubric (solvable / unambiguous / substantive /
reproducible / non-brittle / net-new), disclosed reproducibility caveats
(ARM64-only, host QEMU binfmt registration), and the economic-viability
analysis (why this task is expensive to run and what that means under a
small fixed budget).
