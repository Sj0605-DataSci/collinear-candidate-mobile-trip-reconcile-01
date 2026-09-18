# Storyboard: two trajectories through mobile-trip-reconcile-01

All screenshots in `screenshots/` are **real captures** from a live build
of this task (same Docker image, same tool scripts the agent/oracle use --
`screenshot.py`, `tap.py`, etc. via `adb`), not mockups. One caveat: this
particular capture run used a slightly older image build, so
`07-shared-sam-contact-card.png` still shows the old Contacts hint text
that has since been removed from the task (see DESIGN_DOC.md) -- treat
that one frame as illustrative of the *app*, not of current task content.

Two people/agents can watch the identical shared prefix (frames 1-12) and
end up in completely different places depending on one decision at frame
12: which flight+hotel combo to pick. That divergence *is* the whole
point of the task.

## Shared prefix (both trajectories start identically)

| # | File | What's happening | Suggested caption |
|---|---|---|---|
| 1 | `01-shared-home.png` | Real Android home screen, app icons only -- no accessibility tree, no app list. | "This is the only view either trajectory gets: a real phone screen." |
| 2 | `02-shared-app-drawer.png` | Swiped up from home to see the full app drawer (Calendar isn't on the dock). | "Finding Calendar means knowing to swipe up, like a real phone." |
| 3 | `03-shared-calendar-loading.png` | Calendar's own splash/loading screen after tapping its icon. | (transition frame, can be cut short in edit) |
| 4 | `04-shared-calendar-agenda.png` | Real Calendar agenda: Dentist Oct 5, Board meeting Oct 19 5-6pm, Team standup Oct 20. | "Board meeting is at 5pm on the 19th -- doesn't block a same-day flight home. This is genuinely useful, correct information." |
| 5 | `05-shared-contacts-onboarding.png` | Contacts app's own first-run "back up with Google" screen (Skip tapped next). | "Every app has its own onboarding, same as a real device fresh out of the box." |
| 6 | `06-shared-contacts-list.png` | Contacts list with Sam visible. | |
| 7 | `07-shared-sam-contact-card.png` | Sam's contact card, with a note field. | See caveat above -- this frame is from an older build. |
| 8 | `08-shared-chrome-open.png` | Chrome opened from the home screen dock. | "Chrome is how both the Chat and TripDesk site get opened -- same as any bookmarked site on a real phone." |
| 9 | `09-shared-chat-precorrection.png` | Chat with Sam, first read: Oct 12 out, "totally fine flying back ON the 19th, no need to rush the 18th," budget under $900. | **The key frame.** "At this exact moment, this is a completely reasonable, correct reading of the situation. Nothing here is a trick." |
| 10 | `10-shared-notification-icon-appears.png` | A new notification icon (small chat bubble) appears in the status bar -- captured mid-navigation, showing the icon change is real and passive. | "Time passes. A correction lands as a real Android notification -- nobody has to be told to expect it." |
| 10b | `10b-shared-home-with-icon.png` | Home screen with the new notification icon visible in the status bar. | "Whether anyone notices this icon is the whole test." |
| 11 | `11-shared-notification-shade.png` | Notification shade pulled down, showing "Sam: [message preview]." | "Pulling the shade down is a deliberate choice -- nothing forces it." |
| 12 | `12-shared-flights-list.png` | TripDesk Flights page: 4 options, different airlines/dates/prices. | "Now the trajectories diverge, based on which flight gets picked here." |

## Trajectory A: correct (what the oracle does)

The oracle re-reads Chat *after* frame 11 -- catching the corrected
message ("actually DO need to be back by the 18th now") -- **before**
picking a flight. It then picks accordingly.

| # | File | What's happening | Suggested caption |
|---|---|---|---|
| 15 | `15-trajA-mytrip-correct-date.png` | My Trip: SkyLink flight + Budget Inn Denver hotel, both Oct 12->Oct 18, $260+$70/night = $680, under budget. | "Correct dates, correct combo, confirmed only after re-checking." |
| 16 | `16-trajA-confirmed-correct.png` | "Booked! Your trip is confirmed." | "This is what a genuinely re-verified booking looks like -- indistinguishable on this screen alone from the wrong one. The difference was upstream." |

Full recorded trace of this path: `solution/oracle_steps.py` (the literal
script), `evidence/oracle-*/oracle.txt` (raw logs, 3 independent runs, all
`overall: 1.0`).

## Trajectory B: the real model failure

This is what actually happened in all 4 real `claude-fable-5.1-high`
trials (see RUN_REPORT.md): the model read Chat once (frame 9), formed a
reasonable but now-stale conclusion, and never went back to re-check it
before confirming -- even though it did pull the notification shade once
(frame 11) at some point in its own run.

| # | File | What's happening | Suggested caption |
|---|---|---|---|
| 13 | `13-trajB-mytrip-stale-date.png` | My Trip: SkyLink flight + Midtown Suites hotel, both Oct 12->Oct 19, $220+$90/night = $850 -- still under budget, still internally consistent, still the *wrong* date. | "Everything here looks fine in isolation. That's exactly the trap." |
| 14 | `14-trajB-confirmed-WRONG.png` | "Booked! Your trip is confirmed." -- same success text as Trajectory A. | "The app doesn't tell you you're wrong. Nothing does, unless you went back and checked." |

Full recorded traces of this exact failure (4 real trials, all identical):
`evidence/claudecode-postrecal-*/claude-code.txt` (raw reasoning + every
tool call, chronological).

## Notes for editing into a video (Remotion)

- The shared prefix (frames 1-12) only needs to be shown *once*; the video
  should visually fork at frame 12 into two side-by-side or sequential
  paths (A then B, or split-screen from frame 13 onward).
- Frames 14 and 16 are visually near-identical ("Booked! Your trip is
  confirmed.") -- that's intentional and worth calling out explicitly in
  narration/captions: the app gives no success/failure signal itself: the
  only way to know which trajectory happened is by comparing the My Trip
  page (13 vs 15) against what Chat actually said after re-checking.
- Real audio/narration could read the suggested captions above directly,
  or read from the corresponding `evidence/*/*.txt` trace for verbatim
  reasoning text (e.g. the model's actual final summary message, quoted
  in `RUN_REPORT.md`).
