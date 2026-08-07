# G3 Code Review Gate Report — M0-T045 (R595 supervised rehearsal + Section 16.2 promotion evidence)

**Reviewer:** code-reviewer (independent, read-only). **Frozen reviewed SHA:** `f29deccc3add6bde9c0b112f7c5946347074f297`
(worktree HEAD `a876b15` at review time was ledger-only above it — no code, review identity holds).
**Increments reviewed:** `4db6a71` (hardening) + `afc2da5` (R595-F1 fix) + evidence commits `ba01e18`/`49fcc43`/`f29decc`.
**Reviewer's own suite run:** 1317 passed, 2 skipped (exit 0) — matches producer exactly.

## Per-check results (all PASS)
1. Scope/freeze: both increments strictly inside allowed_paths (inc1: 6 sources + 8 test modules; inc2: cli.py, loop.py, pending_prompt tests); no M0-T045 commit touches any forbidden path; stdlib-only (all new imports internal).
2. C1 catch-all: `_CATCHALL_SECURITY_FILE_CLASSES` DERIVED from `SECURITY_RELEVANT_CLASSES` (cannot drift); permission_settings/hook -> Tier D owner-stop; remaining classes -> Tier B; `test_no_security_relevant_class_ever_routes_tier_a` iterates every member.
3. C2: empty-authorized_branch deny placed AFTER hard-deny block so main/master/force keep their codes.
4. C3: `guard_extra_specs` (collision + destructive) wired in `__init__`; invariant-9 extended to instances.
5. C4/C5: redaction discipline via `redaction.redact_text`; `audit_flow_result` covers performed AND refused.
6. B1/B3: both untrusted-stream scans catch `(JSONDecodeError, ValueError)`; bounded capture with structured marker, never raises.
7. Inc2 resume: verifies emergency-stop, last-trigger, approved record, prompt bytes, digest match — all BEFORE any provider call; forward-exactly-once shared via extracted `_forward_outbox` (identical message-id formula); S7 table and CYCLE_ENTRY_STATES untouched (transition to CLAUDE_RUNNING happens before the entry guard); old-shape fails closed; re-approval dead (state guard + missing digest key); SHADOW-ONLY preserved (`assert_forwarding_allowed`).
8. Fail-closed: all six degenerate entries assert `forwarded_prompt_unavailable`, `provider_calls==0`, no prompts, state unchanged. Crash-then-resume: no double forward (outbox suppression).
9. AS-1: seam actuation verified in `main-run/r4b-start-output.json` (forward id `run_r595_rehearsal_b/fwd/1/a4c3d170e7a0558d`; rotation `context_threshold`; session `sup-5b5f59acaddd41bd8fe1673ddae0f8b5`; handoff digest `e75d07c0…`) AND corroborated in committed `main-run/audit.jsonl` (threshold x8, digest x4, session x2).
10. Evidence manifest: 6 sampled files re-hashed — all match byte-for-byte.
11. AS-2/AS-3: all 11 pack rows linked; ceiling stated first, no activation overclaim. Honesty disclosures hold against code and evidence (no fixture flipped `verified_live`).

## Defects
None MAJOR/MINOR. Three INFO:
- **INFO-1:** the three `supervisor_journal.sqlite3` files are git-ignored, so the sealed bundle commits their SHA-256 (in EVIDENCE_MANIFEST.json) but not the binaries; every substantive AS-1 fact is present in committed JSON + audit.jsonl. Out-of-band integrity preserved via the recorded hashes.
- **INFO-2:** rehearsal report header still says "IN PROGRESS"; the FINAL RESULTS body is authoritative. (Left as-is: the file is inside the task's submitted content identity.)
- **INFO-3:** producer-report/evidence-map/evidence-dir are standard gate deliverables under `project-control/reports/` not individually enumerated in allowed_paths; they touch no forbidden path. Noted for the record.

**G3 VERDICT: PASS**
