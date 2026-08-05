# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python tools/current_state.py` — and reconcile against
the remote: **origin/main may have advanced, so do not trust any SHA written here as still-current.**
This file is orientation only. Operating rules, gates, and workflow routes live in `CLAUDE.md`.

Refreshed **2026-08-04 (late evening)**, at the V1.2.2-integrated / Fable-5-review-held point.

## Where things are

| | |
|---|---|
| `origin/main` | `cb9a999` (owner's PR #150 merge; unchanged all session) |
| task branch | `task/M0-T036-supervisor-bridge` tip **`b95ebf7`** (V1.2.2 frozen for the held review) |
| accepted tasks | **55** (unchanged tonight — nothing was accepted; nothing merged) |
| registries | D-004 **v27** (760 ids, thru am.27) · D-006 · D-007 **v13** (608 ids, thru am.12) |

## 1. OWNER-GATED RIGHT NOW (do not act without a fresh owner instruction)

- **Fable-5 re-review is HELD (D-007-R607).** The fresh G3/G4 verdicts over the V1.2.2 delta are
  **not dispatched** — the owner's Fable 5 window is exhausted and **resets Thursday**; the owner
  says so explicitly. Reviewer pins never fall back (D-004-R757/R748): they wait.
- **M0-T034** sits at `awaiting_gate`, queued at submit for the owner's return. Note it still has
  **no G0 and no G2 record** (only G3/G5 round-3 PASS), so acceptance is mechanically impossible
  until those exist — that is outstanding work, not merely an owner decision (CPV F-CPΔ2-3).
- **M0-T036 acceptance** needs the held re-review first; **D-004-R745's "live-exercised rotation"
  remains UNSATISFIED** (see §3) and must not be counted complete.
- Standing: no merge without owner execution (R721); supervised single-forward rehearsal and all
  activation NOT authorized, shadow-only for real work (D-007-R600); no npm install anywhere,
  apps/web lockfile frozen; deployment/G6/Graphify/expansion/survey holds unchanged.

## 2. M0-T036 — V1.2 re-gated, V1.2.2 built and frozen (99%, in_progress)

**The V1.2 delta re-gate + held G2 wave ran tonight at frozen `98da15e`** (owner authorization
D-007-R599/D-004-R749, window declared live at the time). Six independent Fable-5-pinned reviewers,
all returns preserved verbatim in `project-control/reports/`:

| Leg | Verdict | Gate record |
|---|---|---|
| G2 self-check (`M0-T036-G2-selfcheck-review.md`) | PASS | recorded — M0-T036's first G2 |
| G3 code (`…-V1.2-G3-code-delta-review.md`) | PASS + F-1 **BLOCKING** | recorded |
| G4 QA (`…-V1.2-G4-qa-delta-review.md`) | **FAIL** (F1) | recorded |
| G5 security (`…-V1.2-G5-security-delta-review.md`) | PASS (F-1 non-blocking) | recorded |
| CPV (`…-V1.2-CPV-control-plane-delta-review.md`) | PASS, 5 informational | report on file |
| DCV (`…-V1.2-DCV-directive-compliance-delta-review.md`) | PASS, per-ID table | report on file |

**Three reviewers converged on one real defect**: the V1.2.1 quota substitution was **record-only** —
it wrote truthful-looking `model_substitution` events while the relaunched unit still launched on the
pinned (exhausted) model, and `expected_model` staying pinned would perpetually re-flag
`model_downgrade`.

**V1.2.2 (integrated at `b95ebf7`, verbatim diff `reports/M0-T036-V1.2.2.diff`)** fixes it *and*
implements the owner's corrected design (D-007 am.12 / D-004 am.27): a fixed `[model_chain]`
preference chain in the **immutable** config (`claude-fable-5 → claude-opus-4-8 → claude-opus-4-7 →
STOP+notify`), availability decided by an **actual launch probe of the exact id** (never a picker),
`_actuate_model` rebinding the runner before any record is written (switch / return-to-pin /
crash-resume), ids outside the chain unselectable, chain exhaustion stopping + refreshing the handoff
+ queuing an owner ask. Orchestrator-role only; reviewer path untouched.

Orchestrator verification: 8/8 producer hashes match; supervisor suite **1148 passed / 2 skipped**
(+27, zero regressions); whole `tools/` tree **1348 / 2**. The hard requirement (D-007-R605) was
verified by an **independent mutation check** — removing `self._actuate_model(selected)` makes
`RealProcessSwitchTests::test_a_real_process_comes_up_on_opus_4_8_after_a_fable_5_exhaustion` fail,
so the test genuinely proves a spawned process received `--model claude-opus-4-8` on its real argv.

### Producer-disclosed limitations — carried to the held gate, NOT resolved

1. **`QUOTA_EXHAUSTION_SIGNAL_VERIFIED = False`** — the live CLI's account-quota stderr/exit signal
   has never been captured, so **no classifier is wired in production and the chain step will not
   fire live** until it is; the fail-closed pause holds. Surfaced by `doctor`. Needs a follow-up
   task to capture the real signal.
2. The switch fires at a rotation **seam**; a quota exhaustion arriving as a mid-unit launch failure
   still ends at `no_valid_checkpoint`.
3. `expected_model` now moves with the switched model — changes `--expected-worker-model` probe-knob
   behavior after a switch.
4. V1.2.1's `ModelSubstitutionTests` were rewritten as `ModelChainSwitchTests`; the
   `SUBSTITUTE_MODEL` constant is deleted (its "the ONLY substitute" claim is now false).

## 3. Live exercises — what is and is NOT proven (`reports/M0-T036-V1.2-live-exercises/`)

Eight runs preserved verbatim (ex1, ex2a–d, ex3a–c), synthetic probe units only, nothing forwarded
(`forwarded_message_ids` empty in every run; DCV additionally confirmed **outbox=0 / effects=0** in
every preserved journal).

- **Exercise 1 — live allow round-trip: PASS.** QA gap 1 CLOSED: the wired broker approved an
  `AUTO in_scope_file_write`, the tool actually executed, and the CLI's `setMode:acceptEdits`
  always-allow suggestion was rejected.
- **Live model-mismatch detection: PASS** (D-004-R745's mismatch leg CLOSED). The worker never
  launched on the fake id.
- **Seam rotation ACTUATION: NOT achieved live — `rotations=0` in all eight runs.** Both triggers
  armed live and were audited (`context_threshold`, `model_downgrade`), but the actuator remains
  unit-suite-proven only. **D-004-R745's "at least one LIVE-EXERCISED rotation" is UNSATISFIED**;
  DCV states this without softening and it must not be counted at acceptance.

**FIRST-CLASS FINDING (returns to the owner):** a live supervised run cannot reach the rotation seam.
Two independent causes, both confirmed by G3 and G4 in source: (1) a held forwarded prompt has **no
operator continuation path** — `owner_approved_pending_prompt` / `owner_answer_validated` exist in
the state table but **no CLI command fires them** (the exact analogue of pilot finding F-2, which
V1.1's `clear-recovery` fixed for `PAUSED_RECOVERY`); (2) digest pre-approval **cannot converge** on
a live reviewer — six runs with byte-identical prompts produced six distinct decision digests. The
proposed cure (a CLI command firing `owner_approved_pending_prompt` against the durable
`pending_prompt/<run_id>` record) is **new scope, correctly NOT built**. G5 conditions any such
command on: owner echoes the stored digest, single-use on the same journal, routed through
`verify_before_execute`, and **only after** the empty-binding defect below is fixed.

## 4. Open follow-ups (not authorized tonight; for the owner to schedule)

- **Capture the live quota-exhaustion signal** and wire the classifier — without it the model chain
  cannot fire in production (limitation 1 above).
- **Held-prompt continuation command** — unblocks live seam/rotation verification and R745.
- **Empty approval bindings** (G5 F-2 / G3 F-3): the assembled loop passes empty `head_sha`,
  `origin_main_sha`, and `executable_identity` into every approval binding — live-confirmed
  (`executable_identity: {}` in ex1). Weakens no deny today, but is a **precondition** for the
  continuation command.
- Lower priority: G4 F2 untested branches, G3 F-5 (continuation gating broader than entry
  authorization), G3 F-7 (`rotation_pending` survives across runs), G5 F-3 (redact local paths if
  the repo ever goes public), CPV F-CPΔ2-1..5.
- **M0-T034's G0 + G2 records** (see §1).

## 5. Standing discipline (carry forward)

- **Ledger writes go through `tools/project_control.py` ONLY.** Every directive amendment gets a
  `manifest.audit_log` entry AT capture time. Registry must validate clean.
- **NEW — EOL/digest trap (cost a real integrity defect tonight, fixed at `7df44b3`):**
  `.gitattributes` pins `project-control/directives/** text eol=lf`, but Python text-mode writes on
  Windows emit CRLF. Digests computed over the working copy then matched **only this machine** and
  failed on every fresh checkout and in CI. **Always write registry files with explicit LF**
  (`open(p,'wb')` / `newline=''`) and verify `recorded == canonical committed bytes`, not just
  `recorded == disk`. Found by a producer whose clean worktree reproduced what this checkout could
  not see — a reminder that "the validator passes here" is not evidence.
- **Model ids are exact strings.** 19 producer agent files pin `claude-opus-4-8` + `effort: high`;
  6 files (5 gate reviewers + orchestrator) pin `claude-fable-5`, no effort key; `settings.json`
  default is `claude-fable-5`. Nothing may resolve to `opus-5`. **Observed 2026-08-04 on Claude Code
  2.1.220: `/model claude-opus-4-8` did NOT switch the session** (it kept Opus 5), and `opus 4.8` is
  "not found" — the picker is not a reliable availability oracle, which is exactly why D-004-R752/R753
  require launch-probe determination. Whether `claude-opus-4-8` is still launchable on this build is
  **open and worth probing**.
- Reviewers are read-only, may signal idle without delivering — demand the full return and preserve
  it verbatim on arrival. Producers are unnamed/worktree-isolated; gate-class spawns are pinned.
- **Background agents can stall silently.** One producer hung ~2h before its watchdog fired
  (partial, broken edits, discarded). Check liveness rather than assuming "still running".
- Controller checkout `C:\SupervisorController` is owner-plane — the OWNER pulls it. Runtime dirs
  under `%LOCALAPPDATA%\NYCBuildabilitySupervisor\` are owner-plane; never touch.
- Owner-plane local state (never touch): the modified backend-engineer memory file, untracked
  agent-memory files, `.claude/settings.local.json.bak-2026-08-03`, the stale `worktree-agent-*`
  branches/worktrees, the `bad-amend-backup` and owner `git stash` entries. Untracked
  `supervisor_journal.sqlite3-shm/-wal` sidecars under the live-exercise pack are review artifacts —
  do not commit them.

## 6. Session-end status

Nothing is running in the background. Everything is committed and pushed at **`b95ebf7`**; the main
checkout is clean. Nothing was merged, nothing accepted, and no owner gate closed in the owner's
absence (D-007-R601, independently confirmed by CPV and DCV). A fresh session takes over from here:
the next action is the owner's — say the Fable 5 window has reset (Thursday) and the held re-review
of the V1.2.2 delta dispatches at `b95ebf7`.
