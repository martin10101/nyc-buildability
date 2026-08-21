# M0-T079 G5 security re-review, round 2 (verbatim reviewer return)

Saved VERBATIM by the orchestrator from the read-only reviewer agent's return channel
(report-preservation rule). Reviewer: t079-g5-rereview2 (independent; the first re-review
agent failed on a transient 529 and was re-dispatched fresh). Verdict PASS — both round-1
must-fix confirmed closed. Raw-DB residual disposition accepted (ACL hardening at owner
checkpoint; recommended for the R595 activation checklist). One free hardening (require the
budget digest) folded into round-3.

---

# G5 SECURITY RE-REVIEW — M0-T079 round 2 — FINAL

## VERDICT: PASS

Both round-1 must-fix are closed. No new must-fix or important finding was introduced. The corrections are additive and did not touch containment, the audit chain, R595, or the activation surface.

## M1 / C1 — the in-band budget self-reset is CLOSED

Re-ran the round-1 attack and twelve neighbours against the corrected `start()` using raw SQLite writes into throwaway journals outside the repo. The specific round-1 must-fix — a run nulling `started_at_epoch` through the code's own `start()` path to mint a fresh unbounded budget — now refuses, typed `budget_record_malformed`, sealed with a `run_budget_refused` audit event. Every corruption shape refuses: non-Mapping payload, JSON `null` payload, string payload, absent `started_at_epoch`, non-numeric, `0`, negative, `True`, NaN, unreadable budget block, non-Mapping budget block, and a budget block rewritten against its recorded digest (`budget_record_tampered`). Legitimate cases behave: genuinely absent row = first launch, honest same-bounds reopen resumes with elapsed 3000s and tallies intact, honest different-bounds relaunch = `budget_conflict`. `_ABSENT` sentinel sound because `get_state` returns its default only when the SQLite row is missing.

Residual (all requiring raw SQLite write access to the un-ACL'd journal DB): a true row `DELETE` yields `_ABSENT` → fresh budget; a fully-forged well-formed record with a recomputed unkeyed `budget_digest` is accepted; a cheaper variant G3 did not name — dropping the `budget_digest` field and rewriting the budget block, because the check reads `if recorded_digest and recorded_digest != ...` so an absent digest skips the tamper check; and raw-rewriting `elapsed_high_water_seconds`/`counters`/`started_at_epoch` on an otherwise honest record, since nothing outside the bounds block is digest-covered.

Security judgment: closing the in-band path is sufficient for this gate, and the raw-DB residual should stay deferred to ACL hardening rather than forced into code now. A keyed/HMAC digest cannot help — the adversary is the worker running as the same OS user on the same host; any key the supervisor can read to compute the MAC, the worker can read too. No key material exists on this build (`hmac` used only as `compare_digest`; `secrets.token_hex` mints per-request nonces; no keyring/DPAPI/CryptProtect). The boundary this build uses is elevation, already written and reviewed: `harden_controller_config.ps1` transfers ownership to Administrators, grants Read+Execute only, withholds AddFile/DeleteChild. Applying that to the journal DB directory closes all four residuals as a class — including the fourth, which no digest scheme reaches. Recommendation (not a gate condition): name the journal-DB ACL item on the R595 activation checklist as a prerequisite, not only in D-023-campaign-findings.md. Supervisor is SHADOW-ONLY and activation separately gated, so this does not block acceptance.

## M2 / C2 — the credential leak is CLOSED, proven end to end

With a real `git remote add origin https://x-access-token:ghp_FAKE...@github.com/o/r.git` in a temp checkout, ran the actual `start` far enough to execute the live probes. In `--json` (exit 11) and human mode the token appears nowhere in stdout or stderr. Probe evidence intact — `"remote_url": "[REDACTED:basic_auth_url]github.com/o/r.git"` — so redaction is by masking, not dropping. Side channels clean: no PAT in `audit.jsonl`, none at rest in the journal SQLite, none anywhere under the runtime dir. `cli.py:_emit` (~1748-1761) routes both JSON and human output through `redact_structure`; `refusals.emit` (~154-170) does both channels. Those are the only `print` sites in the package outside cli.py's per-command printers; zero use of `logging`.

One other transmission path — pre-existing, NOT introduced by T079: `cmd_status --json` (`cli.py:1477`) prints journal-derived content with a bare `json.dumps`; a credential planted in a transition detail reaches stdout. Out of scope (T079's only cmd_status change is a prose string; nothing T079 writes puts a remote URL at rest), but it contradicts the generalization C2's docstring now asserts ("stdout is a TRANSMISSION … like every other"), which holds for `_emit`/`refusals.emit` but not the sibling command printers.

## The six important corrections

C3 closed and clean — process.py delta is 26 pure-addition lines (a new `OWNER_ACTIVATION_ARGUMENTS` constant + one refusal branch); deny fires on the exact token, uppercase, and `=`-form, confirmed through the real synthesized-argv path; `assert_argv_safe` applies only to child argv the package synthesizes, never the operator's own sys.argv. C4 closed — day-1 cap reads exhausted, clock rolled to day 2 reads not-exhausted (per-day regained), per-task counter stays exhausted across days (per-run monotonic). C5 closed — `run_live_probes` wraps each probe in `_isolated` (raise → `_unknown`, others still run); from_dict corruption → `BudgetError:unreadable_budget`; unknown tally → `BudgetError:unknown_counter_limit`; no untyped escape. C6 closed and verified through the real hash-chained log — `run_budget_refused` at seq 2 with correct prev_digest, verify_chain ok, tamper flips it False; `bounded_mode_launch_refused` sealed at exit 16 for both asymmetric cases; breaker-trip append outside the `if trigger:` guard so a `trigger=""` trip is recorded. Activation surface unchanged — one production assignment of `owner_enabled_bounded_auto` (cli.py:2848 reading getattr); the only `=True` is the doctor self-test proving the enable is rejected on non-gated modes. C7 closed — no-input `start` exits 13 `missing_required_inputs`, no traceback; genuine dispatch still exits 0. C8 closed — `open_blockers_for` reads blockers/B-*.json status open, word-bounded, fails closed to `blockers_unreadable`.

## Held properties — all still hold

The containment enforcement block in loop.py hashes identically at pre-T079 `e830c4b^`, round-1 `e830c4b`, and HEAD — sha256 `8deac3cc…`, byte-identical across all three; round-2's only loop.py change is the 15-line C6 append. Audit chain no bypass. R595 untouched (only activation strings in the diff are README prose reaffirming the hold, the C3 deny-set which tightens, and the C6 seal which records refused attempts). Neither C3 nor C6 altered containment or added an approval path.

Regression suite: 1752 passed, 2 skipped, 0 failed (555 deselected), 217.67s, exit 0. modularity_check --check: 0 failures, 5 pre-existing warnings.

## Residual minors

The `budget_digest` drop variant is worth acting on and is free: `_first_launch` always writes that field, so no legitimate record can lack it — requiring it (`if not recorded_digest: refuse`) breaks nothing while removing the cheapest raw-DB rewrite. Beyond that: `assert_argv_safe` does not strip whitespace before comparing (inert — argparse rejects a padded flag; gap pre-existed on the hard-deny set, so C3 is consistent not newly asymmetric); `cmd_status --json` leaks journal content (pre-existing, above); a missing `blockers/` directory returns "nothing blocking" (but probe_task_authority refuses earlier with `ledger_record_missing` when the control plane is absent); `check()` ignores counter names absent from `limits` (restore_counters catches a rename first on the real path). Did not re-litigate the round-1 minor list item by item; C10-C12 addressed several.

REVIEWED IDENTITY: 68adb6bf73870bf405bad79295167872f0cbba2f (tools/agent_supervisor tree 04e3a07e5c9c5435d05551a449fbef530d043c2f; working tree clean apart from the pre-existing untracked M0-T079-G3-rereview.md, which the reviewer did not create).

COMMANDS RUN: git rev-parse/status/log/show/diff (scoped diffs of process.py, loop.py, start_gate.py, cli.py vs e830c4b and e830c4b^); git grep for the enable flag, HMAC/key material, LoopConfig( sites, dynamic-set idioms; pytest -k agent_supervisor; modularity_check --check; cli start/status/doctor --help + live invocations against throwaway checkouts; four read-only scratchpad harnesses run outside the repo (g5r2_m1_attack.py 17 budget-tamper cases over raw SQLite; g5r2_m2_leak.sh end-to-end PAT-remote leak both modes + at-rest side channels; g5r2_c3_c8.py; g5r2_c6_c7.py real hash-chained audit verification). No repo writes, no git mutations, no tools/project_control.py.
