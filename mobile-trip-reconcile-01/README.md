# mobile-trip-reconcile-01

A real ARM64 Android emulator (KVM-accelerated), raw screenshot/tap/swipe
action space -- no accessibility tree, no "open app by name" shortcut.
The agent plans a trip (one flight + one hotel, booked on a Chrome-hosted
site called TripDesk) that matches what a contact actually needs, by
cross-referencing a real native Calendar app, a real native Contacts app,
and a Chat thread. Partway through, a corrected message arrives as a real
Android system notification, overturning the return-date conclusion the
information available at t=0 reasonably supported.

Start here:
- [`DESIGN_DOC.md`](DESIGN_DOC.md) -- task idea, methodology lineage
  (MobileWorld/AndroidWorld inspiration, net-new content), the 8 designed
  failure surfaces, a full fairness audit against the assignment rubric,
  disclosed reproducibility caveats, and economic-viability analysis.
- [`RUN_REPORT.md`](RUN_REPORT.md) -- oracle result (3x independent
  `overall: 1.0`), target-model result (`claude-fable-5.1-high`, 4/4 real
  trials at `overall: 0.65`, identical failure every time), the
  OpenRouter -> Claude Code/OAuth billing-route switch and why, full trace
  locations.
- [`REVIEWER_RESPONSE.md`](REVIEWER_RESPONSE.md) -- direct response to
  external review: what's fixed (raw traces now in `evidence/`), what's
  disclosed and not fixed (ARM64/KVM reproducibility friction, no
  completed GPT-model run), and where a claim's scope was narrowed
  (the 480s trap is calibrated to this model's pace, not a
  generalizable-to-any-agent delay).

## Task idea, in one paragraph

Not "can the model book a flight" (saturated). The target capability is
whether an agent's final action reflects genuinely re-verified, current
state or a stale first pass that was never re-checked -- tested with a
real mid-mission event (a corrected message, delivered as a real Android
notification, timed off the agent's own first real action) that overturns
a conclusion the agent's t=0 information reasonably supported.

## Fairness rationale (short version; full audit in DESIGN_DOC.md)

- Solvable: proven via 2 independent `harbor run -a oracle -y` passes,
  `overall: 1.0` both times, using the same tool scripts the agent uses
  (`solution/oracle_steps.py` is a literal recorded human-style trace, not
  a database shortcut).
- Non-brittle: the pre-correction read (return on the 19th) is the
  reasonable conclusion from real information, not a trick -- documented
  explicitly in `tests/answer_key.json`'s own notes field. The agent is
  only penalized for not re-checking after being told things changed.
- Net-new: no scenario, asset, app, or task text is copied from
  MobileWorld, AndroidWorld, or any prior Collinear task. Only public
  methodology (backend-DB verification, real device state, cross-app
  requirement) is shared.
- Unambiguous, backend-verified grading: `tests/verify.py` reads
  TripDesk's own SQLite DB directly -- no LLM judge, no report
  string-matching.

## Economic realism (short version; full analysis in DESIGN_DOC.md)

This is a long-horizon, image-heavy task by design -- the screenshot
history accumulating over 40-70 turns *is* the capability under test --
run at `reasoning_effort=high`. That's genuinely expensive per trial
(~$20/completed trial via OpenRouter pay-per-token). Under a small fixed
budget, this task supports at most one or two trials via metered billing;
the 4 real trials reported here were run via Harbor's `claude-code` agent
against a Claude subscription's included usage instead, once OpenRouter
budget was exhausted mid-project -- disclosed plainly in `RUN_REPORT.md`,
not glossed over.

## Verifier design

`tests/verify.py` reads `/data/tripdesk.db` (TripDesk's own SQLite state)
directly after the agent's session ends. Six gating metrics
(`booking_confirmed`, `correct_depart_date`, `correct_return_date`,
`within_budget`, `flight_hotel_dates_consistent`, `genuine_not_premature`)
combine into a weighted `overall` score; two diagnostic-only fields
(`actions_used_total`, `home_screen_visits`) are reported but not graded.
`genuine_not_premature` cross-references the booking's real confirm
timestamp against the mid-mission message's real arrival time, so a
correct-date booking that could only have been a lucky guess (confirmed
before the correction could possibly have been read) is distinguished
from one genuinely backed by re-checking.

## Evidence

4/4 real `claude-fable-5.1-high` trials at the current calibration
confirmed the identical wrong booking (flight_id=1, hotel_id=2, return
date 2026-10-19 instead of the required 2026-10-18, `overall: 0.65` every
time). Full per-turn traces (`agent/claude-code.txt` / `agent/codex.txt`,
raw stream-json) and per-trial `verifier/reward.json` +
`verifier/notes.json` are preserved under each trial's job directory --
see `RUN_REPORT.md` for the exact paths and the full results table.

## Video walkthrough

Not recorded for this submission -- the full reasoning/tool-call trace
for every trial (identical information to a walkthrough, at higher
fidelity) is available in the raw logs referenced above and in
`RUN_REPORT.md`.
