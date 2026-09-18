# Response to review feedback

Addressing each point directly, in order. Nothing here is spin -- where
the critique is correct, it's agreed with and either fixed or disclosed
as a real, unresolved limitation.

## 1. "Delay was tuned to this model's pace"

**Correct, and worth being precise about what that does and doesn't
mean.** `delay_seconds` (150s -> 480s) was calibrated against
`claude-fable-5.1-high`'s own observed pace (two 150s trials both read
Chat only after the correction had already silently landed, ~490-500s
in). At 480s, the same model consistently reads Chat *before* the
correction and fails to re-check (4/4). The oracle still passes at 480s
(3x, `overall: 1.0`), so the task remains solvable -- the calibration
didn't make it unsolvable, it made the trap *actually fire* against this
model instead of accidentally missing it.

What this does **not** establish: that 480s would fail "every strong
agent," or that this is a delay chosen to be unbeatable in general. It's
honestly a per-model-calibrated trap, the same way most timing-based
long-horizon evals need some calibration against the actor's real latency
to be meaningful at all (an event that always lands before *or* always
after any plausible agent pace tests nothing). The fair framing: this is
evidence that `claude-fable-5.1-high` fails a re-verification requirement
timed to its own natural pace, not evidence that the delay would defeat a
materially faster or slower agent. Testing across models at different
paces (rather than one calibration point) is the correct way to
generalize this claim, and hasn't been done -- see the response to point
4.

## 2. "Hard to reproduce"

**Correct, disclosed, not fixed.** ARM64 + KVM + `--privileged` +
an unofficial emulator binary + host QEMU binfmt registration is real
friction beyond a normal x86 laptop checkout. This was already documented
in `DESIGN_DOC.md` Section 7 and the new Section 7a (added in response to
this exact concern) is explicit that ARM64 + hardware-accelerated
virtualization is the actual, non-negotiable requirement -- any ARM64
host with KVM works (cloud ARM64 bare-metal, another ARM64 workstation),
not just this specific DGX Spark. It does **not** run on x86_64 at all,
with or without KVM, because the vendored emulator binary is an ARM64
build. This should be read as a declared special-resource requirement,
the same category as a GPU requirement on other tasks -- not something
this submission claims is a normal checkout.

## 3. "Traces are not in the GitHub repo"

**Fixed.** The full raw `claude-code.txt` stream-json traces (reasoning +
every tool call + every result, chronological) for all 4 real
`claude-fable-5.1-high` trials, plus all 3 oracle traces and the 4
OpenRouter trials (2 completed pre-recalibration, 2 infra failures), are
now committed under `evidence/<label>__<trial-id>/`. Total added: ~49MB,
comfortably within normal repo size. `jobs/` itself (223MB, full ATIF
trajectory.json conversions + duplicated raw content) remains excluded
via `.gitignore` -- that's bulk re-derivable data, not unique evidence;
the `claude-code.txt` files now in `evidence/` contain the same
information (raw reasoning, tool calls, tool results) at a fraction of
the size.

## 4. "No GPT completed run"

**Correct, and still true.** One GPT-6-astra-high attempt was made and
hit a genuine OpenRouter infra failure (ZDR policy block, then separately
a `402 Payment Required` on a different key) -- both are infra failures,
not model evidence, and are labeled as such in `evidence/` and
`RUN_REPORT.md`. No GPT-6-astra trial has completed. At the time of this
response, remaining OpenRouter budget is **$10.33**, and a completed
trial has cost ~$18-20 in this task's observed range -- not confirmed
enough for one reliable completed run. This is an open gap, not something
resolved by re-framing: **the model-comparison claim in this submission
is Fable-only** and should be read that way. Getting a completed GPT run
would need either more OpenRouter budget or GPT access through a
non-metered route (no equivalent to the Claude Code/OAuth path exists for
GPT here).

## 5. "Instruction already hints at the trap"

**Correct, and treated here as a feature, not a bug to fix.** The
Contacts note ("worth double-checking any date they've given before
locking anything in") is a real, discoverable signal, deliberately placed
in a third app the agent has no obligation to open. Its presence is
disclosed in `DESIGN_DOC.md` Section 4, point 3, explicitly as something
that "helps fairness" -- a model that fails despite a legible hint in the
information already available to it (not a hint added to the *task
instructions* directly, which would be different and would weaken the
result) is a stronger, not weaker, failure signal. All 4 real trials had
access to this hint (Contacts is documented as an app to check in
`instruction.md`) and still failed identically. This is intentional and
correctly identified by the review -- no change made here, only this
clarification of why it stands.

## Bottom line on the "conditional pass" framing

Agreed on all three hold items:
- (a) traces uploaded -- done, see point 3.
- (b) 480s delay described accurately as calibrated to this model's
  observed pace, not claimed to generalize to all strong agents -- done,
  see point 1, and DESIGN_DOC.md updated to match.
- (c) ARM64 noted as a special resource -- already present, reinforced
  with the new Section 7a in DESIGN_DOC.md.

The GPT gap (point 4) is not resolved and is not claimed to be. The
reported result is: **`claude-fable-5.1-high` fails this task
consistently and reproducibly (4/4) under a trap calibrated to its own
pace; the oracle proves the task solvable; no comparable completed-run
evidence exists yet for a second model.**
