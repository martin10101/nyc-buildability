# M0-T079 G3 focused re-review, round 2 (verbatim reviewer return)

Saved VERBATIM by the orchestrator from the read-only reviewer agent's return channel
(report-preservation rule). Reviewer: t079-g3-rereview (independent). Verdict PASS with two
important residuals (R-2, R-3) requiring a round-3 micro-correction before acceptance, and an
honest-scoping note on C1 recorded against the deferred ACL item.

---

# G3 focused RE-REVIEW — M0-T079 round 2

## Verdict: PASS

Three of the four round-1 important findings are fully resolved (I-1, I-2, I-3). **I-4 is only partially resolved.** Two important residuals remain, both requiring rework before acceptance under gate-verdict semantics. No regressions and no weakened detection anywhere in the changed surface.

Observed suite: **1752 passed / 0 failed / 2 skipped** (555 deselected, 277s), matching the producer's claim exactly.
`python tools/modularity_check.py --check`: **failures 0, warnings 5** — the same five pre-existing warnings. `cli.py` 3477 / `loop.py` 2800 / `recovery_probes.py` 693 lines; no file fails its limit.

## Round-1 findings

**I-1 (blocker authority) → C8: RESOLVED.** `open_blockers_for` (`probe_control_plane.py:99-145`) reads `project-control/blockers/B-*.json`, filters `status in ("open","")`, and matches with the byte-identical word-bounded regex `_blocker_references` uses (`project_control.py:1176`), across both `affects` and `detail`, rework-id included. No free-form task-field blocker read survives anywhere in `tools/agent_supervisor/`. Re-derived against the LIVE ledger: `M0-T019 → []` (carries a resolved `B-017`, so it now dispatches — the exact broken case), `M3-T002 → ['B-001']`, `M3-T005 → ['B-001','B-011']`, so a live OPEN blocker record genuinely refuses. The replaced test did assert the DEFECT; its 8 replacements assert the authoritative source, and `blockers_unreadable` fails closed as UNDETERMINED.

**I-2 (deadline) → C9: RESOLVED.** `deadline_blocks_dispatch` (`start_gate.py:224-256`) gates on the probe's clock-computed `outstanding`, defaults every unknown to blocking, steps aside only when the deadline is the sole blocker. `parse_utc_instant` (`recovery_probes.py:474`) parses real instants. The `honest_reason_code` fix is correct and tested: expired deadline + manual pause reports `safe_but_forbidden` at exit 14, not `deadline_restored`.

**I-3 (drift re-pin) → C10: RESOLVED.** `--repin-cli-identity` wired end to end (`cli.py:3285` → `start_gate.py:164` → `recovery_probes.py:657`). Detection untouched — `if drifted and not repin: return _fail(...)`. Provenance + `cli_identity_repinned` audit event recorded; test walks all four states through the real CLI.

**I-4 (exhaustion escape) → C11: PARTIALLY resolved — see R-2.**

## C1 sentinel / refusal code correctness — CORRECT

The `_ABSENT` sentinel is genuinely sound. `get_state` returns its default **only** when the row is absent (`durable_state.py:385-389`), so a row holding JSON `null` reads back as `None` and cannot be mistaken for a missing row. Verified empirically. `_resume` (`run_budget.py:374-431`) refuses all five shapes with typed, audited errors and never falls through. The refusal chain in `cmd_start` (`cli.py:2973-3069`) is strict if/elif/else — every branch assigns a typed refusal; line 3113 returns before any success path. No fall-through. C5: `_isolated` (`recovery_probes.py:612`) catches `Exception` so every probe answers. C2: redaction at the transmission boundary in both `_emit` (`cli.py:1757-1761`) and `refusals.emit` (`refusals.py:162-169`). Extraction facade holds; amended tests are strengthenings.

## Residual findings

**IMPORTANT — R-2: C11's remedy is not on the path the operator reads (`start_gate.py:312-318`, `run_budget.py:673-694`).** `check()` names the escape (`run_budget.py:534-537`: "Start a NEW run id (`--run-id <fresh-id>`)"), but that text goes only to durable `exit_detail` and the audit log. The refusal the operator sees (`dispatched_run_refusal`) has a static message and detail = `report()`, which omits `exit_detail`. Reproduced exit-15 output for an exhausted `claude_runs_per_task` shows no `--run-id` anywhere; wall-clock exhaustion (`run_budget.py:546-550`) doesn't name it either. The correction required the message to name `--run-id`; what landed is the help text (real, good) plus an internal string. Consequence: an operator who trips the I-4 trap still reads a message with no remedy. One-line fix — add `exit_detail` to `report()`, or name the flag in the static message. Related wart: this path reports `dispatched: true` for a run that executed zero cycles.

**IMPORTANT — R-3: the M-3 deferral's stated reason was not performed (producer report §3.4 vs §deferrals).** The report defers M-3 with "I have corrected the report's blanket claim instead of the code." The blanket claim is unchanged: §3.4 still reads verbatim "Every trip is a synchronous pause **before** the counted thing happens", and the correction commit does not touch those lines. `restart_attempts` still ticks after the relaunch (`loop.py:2772-2773`). The code deferral is defensible — a restart that already happened cannot be undone by a breaker — but the gate-evidence report carries a false technical claim plus a false statement that it was corrected. Fix is a one-line report edit.

**Minors**

1. `cli.py:3117` — the comment "Missing-input stops still exit 0" is now false; C7 routes them to exit 13. Stale comment.
2. `probe_result.py:49-59` — `_ok`/`_fail`/`_unknown` are byte-identical duplicates of `ok_probe`/`fail_probe`/`unknown_probe` (89-100) and nothing imports them. Dead duplicate constructors; a later change to one would silently diverge.
3. `probe_control_plane.py:137` omits the `.strip()` `accept()` applies (`project_control.py:1241`), so `" open "` would be skipped by the probe but treated as blocking by `accept()`. No live record has whitespace; theoretical.
4. **C1's residual, to be recorded against the ACL item.** `test_a_deleted_record_refuses_rather_than_starting_over` deletes nothing — it calls `set_state(key, None)`, the null-row case. A true row deletion still yields `_ABSENT` → fresh budget (measured: 3600s/3000s-elapsed/40 tallies became 36000s/0.0/`{}`), and a forged well-formed record with a recomputed `budget_digest` is accepted since `digest_of` is unkeyed. Defensible — the package exposes no delete API, so `set_state(key, None)` is its only in-band clear, and both remaining shapes need raw SQLite access (the deferred journal-DB ACL hardening). But "C1 removes the exploit", used to justify that deferral, is stronger than what is true; the residual (row-deletion + forged-record-with-recomputed-digest via raw DB write) should be recorded explicitly against the ACL item.
5. `probe_cli_capability_manifest`'s docstring says re-pin is "not reachable from a synthesized argv", but `--repin-cli-identity` is not in `OWNER_ACTIVATION_ARGUMENTS` (`process.py:98-100`); nothing enforces it. True today only because no synthesized argv includes the flag.
6. `start_gate.py:272` stray spaces mid-expression. Cosmetic.

**Deferred minors are legitimate.** M-4 (`_previous_checkpoint_id`, per-process): persisting it is new behavior not a correction, and total livelock stays bounded because escaping requires restarts and `restart_attempts` is durable per-run. M-3's *code* deferral is legitimate; only its stated remedy was not carried out (R-3).

## Commands run — all read-only

git rev-parse/log/status/show/diff (read-only forms incl. 41d0490^ extraction), full `pytest -k agent_supervisor` suite + 7 individual node-id spot-checks (blocker authority, nulled start instant, expired deadline, drift re-pin, credential redaction, real-hold-not-excused), modularity_check --check/--report, three scratchpad read-only Python probes (live open_blockers_for re-derivation, _ABSENT boundary, C11 operator-visibility). No repository file created/edited/deleted; no git mutation; no tools/project_control.py.

**Reviewed identity: `68adb6bf73870bf405bad79295167872f0cbba2f`** (round-2 task commit `41d0490`), working tree clean.
