# Commissioning journey 4: the M0-T130 fix WORKED end-to-end, first live Codex review completed — Codex returned HALT_UNSAFE (reviewer sandbox cannot read the repository) — one consolidated assessment (D-024-R394)

Recorded by the orchestrator 2026-08-31 (session `session_01SfXcRw7emzdojCDJmKxNTM`).
The owner personally typed Step 1 (`clear-recovery`, transition 27) and the corrected
Step 2 with the fresh `--run-id run_m0t107_j4` (the budget machinery's own printed
remedy after the durable `consecutive_invalid_outputs` 3/3 tally correctly refused the
spent lineage id — a designed refusal, not a defect; the spent `run_33dfa57d54db`
record stays as evidence). Result: **DISPATCHED**, one full cycle, final state
**HALTED** (`halt_unsafe`, exit 10), one counted touch (1 of 2 on the new run; S16.7
campaign-cumulative excess continues). Per R394: no retry; everything preserved; this
is the one consolidated assessment.

## 1. What this journey PROVED (all primary evidence; the farthest yet, by two stages)

| Fact | Evidence |
|---|---|
| 1-2: fresh Fable 5 worker in `wt-m0t107` | transition 29: session `15cd9b3d...`, `job_object`, 19:55Z |
| **The M0-T130 fix works live, end to end** | the worker ran ~7 minutes of REAL work (503,549-byte transcript vs journey-3's truncated 65KB); no premature reserved-turn, no wall-timeout ride; the unit closed at genuine idle |
| **3: a VALID checkpoint reached Codex — first time in the campaign** | transitions 30-32: `valid_checkpoint_received` (`run_m0t107_j4-cp1`, digest `59054f94...`) -> `checkpoint_validated` -> digest-bound evidence packet (46,139 B, `6125895e...`) |
| **4: Codex completed an independent review — first live review ever** | audit 81: `codex_review_decision`, model `gpt-5.6-sol` (allowlisted), attempts 1, returncode 0; schema-valid decision correlated to the checkpoint (transitions 33-34) |
| Safety machinery honored the verdict exactly | transition 35: `decision_halt_unsafe` -> HALTED; **no advancement recorded** (exactly-once preserved; `task_advancement/*` absent), M0-T109 never dispatched, queue snapshot consistent |

## 2. The verdict and its root cause

Codex's decision: **HALT_UNSAFE**, blocking finding (verbatim): *"The mandatory fresh,
read-only repository review cannot be performed because the execution policy blocks
repository reads. Accepting or continuing from untrusted packet claims would violate
the independent-verification requirement."* This is the reviewer doing its job
honestly: it refused to rubber-stamp the worker's claims without its own repository
reads.

**Why its reads were blocked (assessed from preserved evidence + the reviewer argv;
not live-probed — R394, no provider contact for diagnosis):** the reviewer is invoked
as `codex exec -C <repo> -m gpt-5.6-sol --ephemeral --ignore-user-config
--strict-config --sandbox read-only --json ...` (codex_reviewer.py:110-122; the
read-only sandbox is mandatory by design, S13.12 invariant 10). Two candidate
mechanisms, both first-contact environment gaps:
1. **codex-cli 0.146.0 sandbox enforcement on WINDOWS**: the `read-only` sandbox has
   no native Windows implementation; under `exec` (non-interactive, no approvals
   possible) + `--strict-config`, the harness fail-closes command/file access the
   model requests — matching "execution policy blocks repository reads" exactly.
2. **Linked-worktree `.git` redirection**: `wt-m0t107/.git` is a FILE pointing at
   `nyc-development-feasibility-claude-pack/.git/worktrees/wt-m0t107` — OUTSIDE the
   `-C` root; a path-scoped read sandbox would deny every git operation in the
   worktree even if reads inside `-C` were allowed.
**Why certification could not catch it:** the golden pack certifies the review
CHANNEL with a fake codex (deliberately, R220/R221 — no provider consumption);
the only live codex evidence ever recorded was the version probe. Tonight was the
first live `codex exec` review on this host: the transport, schema, model allowlist,
decision validation, and halt policy all worked; the reviewer's own filesystem/command
access is the one unmeasured surface, and it fail-closed honestly.

## 3. The new owner decision (nothing retried; journal preserved at HALTED)

1. **Bounded reviewer-access diagnostic + fix task (recommended).** Step 1: ONE
   owner-authorized minimal live probe on this host — a tiny `codex exec --sandbox
   read-only` unit in a scratch git directory asked to run `git status --porcelain`
   and report what the harness permits — to discriminate mechanism 1 vs 2 and measure
   the actual policy surface (R233 discipline: a measured installed-version fixture).
   Step 2: the bounded fix the measurement dictates (e.g., a Windows-compatible
   read-access shape for the reviewer, or binding the reviewer to a self-contained
   clone instead of a linked worktree, or an explicitly owner-approved widening of
   the reviewer's READ policy — never write access), under the standard defect lane;
   any supervisor change re-triggers R247 (now fast).
2. **Not recommended without deliberate design:** weakening the review contract so
   Codex verifies only the supplied evidence packet without live reads — Codex itself
   named that as the violation; it would trade away the independent-verification
   property the whole loop exists to prove.
3. **Restart path when ready:** the journal rests at **HALTED**, whose exit is the
   owner-restart channel (`owner-restart`, the live-proven HALTED->IDLE edge), then a
   fresh start. Not to be typed until the reviewer-access fix lands — the same halt
   would recur.

Preservation: journal HALTED (transitions 35, audit 85); worker transcript intact;
evidence packet + decision digests recorded; `wt-m0t107` clean `c5c6ff7` (the worker's
plan-stage work produced no file changes — M0-T107 is a planning deliverable and the
unit ended at checkpoint, not at deliverable completion); `wt-m0t109` clean `1c06957`;
queue + packet digests unchanged; PR #241 OPEN untouched; no supervisor file changed
by this journey (certification `37020c37` stands).
