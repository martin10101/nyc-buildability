# G4 Independent QA Gate Report — M0-T045 (R595 supervised rehearsal + Section 16.2 promotion evidence)

**Reviewer:** qa-engineer (read-only, independent; producer != reviewer). **Frozen reviewed SHA:** `f29decc`
(worktree HEAD `a876b15` at review time was ledger-only above it; tools/ + evidence byte-identical).

## 1. Suite + regression scope
- Reviewer's own run: **1317 passed, 2 skipped** (matches claim exactly). The 2 skips are platform-conditional POSIX guards.
- No deleted/renamed test modules (`git diff --diff-filter=DR 1c34def..afc2da5 -- tools/` empty). Both increments touch ONLY tools/. Validator exit 0.

## 2. Independent adversarial probes (reviewer-authored harness, 85/85 PASS)
- **FORWARD_PROMPT cross-process resume 14/14:** happy path forwards once + armed rotation actuates; tampered stored prompt after approval -> `forwarded_prompt_unavailable`, 0 provider calls, journal not advanced; deleted record -> fail-closed; send-then-crash double-resume -> exactly one outbox row (duplicate suppressed).
- **Section 5.2/5.4 catch-all 50/50:** all 10 SECURITY_RELEVANT_CLASSES enumerated via real classifying paths — NONE routes Tier A; permission_settings/hook (incl. `.claude/settings.local.json`, `.claude/hooks/*`, `.git/hooks/*`, `.husky/*`) -> Tier D owner-stop with owner_approval_required=False; mixed change -> strictest tier; ordinary-only control -> Tier A (probe discriminates).
- **Bounded capture / telemetry / fixtures 21/21:** 8 MiB cap with structured marker, never raises, real 500KB child capped at 4 KiB without crash; 5000-digit int -> USAGE_UNKNOWN and later valid lines still parse; empty-shape fixture matches nothing even when forced verified_live=True.

## 3. Rehearsal evidence integrity
- **26/26 SHA-256 manifest matches** (recomputed; zero mismatch/missing/extra).
- **Main-run journal chain complete:** threshold arming (ctx 134,497, unit uninterrupted) -> `owner_approved_pending_prompt` (transition #10; audit seq 17-18) -> `prompt_forwarded` (transition #11, cross_process_resume=True) -> rotation record (handoff `e75d07c0…`, session `sup-5b5f59ac…`; audit seq 22-25: handoff refreshed -> session archived -> rotation complete -> relaunch) -> successor cycle 2 to parked WAIT.
- **Main-run audit chain VERIFY-CLEAN:** 37 events, contiguous, per-record digests recomputed, head anchor matches; the chain spans two OS processes across the rotation and stays one clean chain. Tamper control: one flipped byte -> digest_mismatch detected.
- **Discovery-run:** chain VALID (19 events); old-shape record corroborates R595-F1 and the honest "unresumable" limitation.
- **R5:** consumed-digest re-approval refuses fail-closed.

## MATERIAL FINDING (non-blocking) — estop-run audit chain forked
`verify_chain()` on `estop-run/audit.jsonl` fails `duplicate_sequence` (seq 12/13 duplicated): the `emergency-stop` command and the main loop wrote CONCURRENTLY (both seq-12 records share prev_digest `4becd596` — a fork). NOT blocking because: the system itself surfaces it (`r6-recovery-status.json` carries `audit_chain_ok: false` — damage reported, not hidden; post-estop appends verify-closed); it is outside the two reviewed increments (pre-existing estop/audit concurrency); and no load-bearing R6 claim rests on chain integrity (HALTED, emergency_stop=true, autostart refused, children=[], zero unaccounted — all independently evidenced). At-rest integrity of the sealed artifact is protected by the verified SHA-256 manifest. **Follow-up recommended:** a test locking the forked-chain shape + explicit owner acknowledgement that an emergency stop leaves the audit log unappendable-without-repair.

## 4. Acceptance scenarios
- **AS-1 PASS** (complete live chain in journal + verify-clean audit; R593 closed by evidence, not waiver).
- **AS-2 PASS** (11/11 rows evidenced; GitHub leg = accepted M0-T044 proofs + legitimate owner decision R119).
- **AS-3 PASS** (ceiling stated first and binding; no fixture flips; open owner decisions enumerated).

## 5. Coverage gaps (non-blocking)
estop fork test (above); synthetic workload (disclosed); verified_live fixtures remain fail-closed (procedural duty); cross-process locks adequate.

**G4 VERDICT: PASS**
