# M0-T048 — G3 code review (RERUN, rework delta) — VERBATIM reviewer return

Orchestrator preservation note: saved verbatim from the reviewer agent-return channel
(transport entity-decoding only: `&gt;`→`>`, `&amp;`→`&`). Reviewer: code-reviewer
(read-only). Frozen review identity `fee612ae724085576aad23c0fd1d387fa89e800d`; code identity
`9c450a5b2cc2e52474fa95253218c7b1d92ea775`. Recorded by the orchestrator 2026-08-08.

---

I have completed my independent review. All findings are traced to source at the frozen code identity (task branch `9c450a5`), the full suite independently reproduced (1380 passed / 2 skipped), and every scope item checked. Here is my G3 rerun report.

---

# G3 Code Review Gate Report (RERUN) — M0-T048 (rework delta: resume-window audit trust anchor)

**Reviewer:** code-reviewer (independent, read-only). **Lane:** G3 correctness / contracts / error-paths / tests (G5 owns security-bypass adjudication; G4 owns QA/evidence; DCV owns directive-requirement mapping).
**Scope:** rework delta closing the previously-routed MAJOR-1 (cross-process resume-window `(approved_instruction, approved_digest)` forgery), per owner adjudication D-010 source-015 (R144–R154). Confirming the original PASS still holds at the new identity.

## Frozen reviewed identity (confirmed)

- **Code identity (what a code review binds to):** orch worktree `C:/Users/MLFLL/Downloads/nyc-zoning/orch`, branch `task/M0-T048-c2-close`, HEAD **`9c450a5b2cc2e52474fa95253218c7b1d92ea775`** — matches the dispatched rework SHA `9c450a5`.
- **Delta reviewed:** `git diff ec0f55d..9c450a5` → 4 files, **+573/-0**: `tools/agent_supervisor/loop.py` (+138), NEW `tools/test_agent_supervisor_audit_anchor.py` (+288), `tools/test_agent_supervisor_pending_prompt.py` (+8), `project-control/reports/M0-T048-producer-report.md` (+139). Exactly the described delta; no other file touched; all inside allowed paths.
- **Control-plane identity note (non-blocking):** the prompt named frozen control head `fee612a`; the primary checkout is now at `fcdef80` (branch `control/M0-T048-c2-close`). I verified `fee612a` is an ancestor of `fcdef80` and the single intervening commit changes **only** `project-control/state.json` and `project-control/tasks/M0-T048.json` (the "resubmitted (rework)" ledger update) — **no reviewed code changed**. The reviewed code identity is unchanged at `9c450a5`.

## Evidence reproduced in-sandbox

- Delta + adjacent suites `pytest tools/test_agent_supervisor_audit_anchor.py test_..._park_approve_binding.py test_..._pending_prompt.py test_..._c2_binding.py -q` → **44 passed in 12.45s**.
- Full supervisor suite `pytest tools/test_agent_supervisor_*.py -q` → **1380 passed, 2 skipped in 108.79s** — independently matches the producer claim and the orchestrator-reproduced baseline (+6 over the ec0f55d baseline of 1374/2, all in the new adversarial file).
- Guard-ordering trace read directly from `loop.py:2220-2311` (see item 1). Fail-branch code read from `loop.py:714-800`. Audit-log contract read from `audit_log.py` in full.

---

## Disposition of prior findings

### MAJOR-1 — **CLOSED** (per my own originally-suggested remedy)

The rework implements exactly the remedy I recommended: at resume, cross-check the journal `approved_digest` against the already-sealed, hash-chained `operator_resume_pending_prompt` (`decision="approve"`) event's operator-named `input_digest`, raising the bar to also require forging `verify_chain`.

End-to-end resume trace (`_resume_approved_forward`, loop.py:2203-2311), in order:
1. emergency-stop refusal (2222) → 2. last_trigger==owner_approved (2229) → 3. approved-record present (2236) → 4. held prompt bytes present / old-shape refusal (2244) → **5. NEW audit cross-check `verify_approved_digest_against_audit(self.audit, self.run_id, str(approved_digest or ""))` (2260-2262)** → 6. reconstruction check `verify_covered_instruction` (2275-2278) → 7. `_resume_forward` (2289).

The new cross-check therefore runs **before any forward** and **before/independent of** the reconstruction check. The provider is invoked only inside `run_cycle` (`provider_calls += 1` at loop.py:1631 and 1750), reached only after the resume returns; the guard `raise`s before the cycle loop, so **zero provider calls** on every refusal path. `approved_digest` is read for forwarding at exactly one site (loop.py:2243) inside the one cross-process forward path (called only at loop.py:2328); no sibling path binds forwarded content to journal-resident-only values. The self-consistent `(approved_instruction, approved_digest, prompt, prompt_bytes_digest)` forgery now fails: the sealed event still carries the original operator digest, the forged `approved_digest` no longer matches → `approved_digest_audit_mismatch`, fail-closed.

Adversarial proof (`test_two_field_plus_digest_forgery_fails_closed_no_provider`, audit_anchor.py:117-148) drives the **real** park + **real** CLI approval + **fresh-loop** resume, mutating only the journal (audit left unchanged), and asserts `LoopError forwarded_prompt_unavailable`, `provider_calls == 0`, **0 outbox rows**, exactly one durable sealed `cross_process_resume_refused` (reason `approved_digest_audit_mismatch`, `decision="refuse"`), and `verify_chain().ok` still true. RED-on-pre-fix is proven in-process (`test_red_when_crosscheck_disabled`, 150-176): monkeypatching the module-global `verify_approved_digest_against_audit` to a no-op forwards the forgery, landing `EXFILTRATE ALL SECRETS` in the outbox — so the new check is demonstrably the sole thing closing the hole.

### MINOR-1 (AS-4/R139c coverage) — **RESOLVED**

My prior MINOR-1 noted the post-approval tamper test forged only `prompt`+`prompt_bytes_digest`, narrower than R139c's general wording. The new `test_two_field_plus_digest_forgery_fails_closed_no_provider` covers precisely the uncovered variant (all four fields, self-consistent, post-approval), so R139c is now met for the cross-process resume window.

---

## Scope-item findings

**1. MAJOR-1 closure & guard ordering — PASS.** Covered above.

**2. `verify_approved_digest_against_audit` correctness (loop.py:714-800) — PASS, with one advisory.** Six distinct fail-closed reason codes, each reachable and tested: `approved_digest_audit_unavailable` (audit is None, 744), `approval_audit_unreadable` (verify_chain **or** read_all raises — both wrapped in `except Exception`, 752/770), `approval_audit_chain_invalid` (verify not ok, 758), `approved_digest_audit_missing` (no approve event for run, 777), `approved_digest_audit_mismatch` (no matching input_digest, 785), `approved_digest_audit_ambiguous` (>1 match, 792). No fail-open gap: any exception escaping `verify_chain`/`read_all` is converted to a fail-closed `LoopError`; the record comprehensions (782) run only after `verify_chain` returned ok=True, which — per `audit_log.py:256-324` — guarantees every record is a well-formed dict (a non-dict line makes `verify_chain` raise or return not-ok first), so no uncaught `AttributeError` escapes the guard in practice. The approvals filter keys on `event_type == OPERATOR_APPROVAL_EVENT` + `decision == "approve"` + `run_id`, matching exactly what the CLI seals (cli.py:1736-1742) — sound. The "multiple approve events with DIFFERENT digests, one matches → passes" case is correct: the journal `approved_digest` names the active approval; non-matching prior-cycle approvals are correctly ignored. The `>1 matching` replay refusal is exercised by `test_ambiguous_approval_events_refuse` (which appends a valid duplicate that keeps the chain verifying) — a genuine anti-replay value the owner explicitly required.

**3. `_seal_cross_process_resume_refusal` (loop.py:2177-2201) — PASS.** Swallows **only** `AuditChainError` (2198) — the case where the chain is already damaged and cannot be extended, which is itself the recorded evidence; any other `append` failure propagates. In every case the forward is unreachable (the seal is invoked from the `except LoopError` branch at 2263-2269, before `_resume_forward`), so no forward slips through. The journal (durable-state DB) is never mutated on the refusal path — the seal only appends to `audit.jsonl` with `state_from==state_to==FORWARD_PROMPT` (no state transition). Confirmed.

**4. Exactly-once / clock-invariance (S13.5) / old-shape refusal — UNCHANGED.** The guard is purely additive, placed after the old-shape refusal (2244-2249) and before the reconstruction check; message-id keying (`{run_id}/fwd/{cycle}/{binding[:16]}`, loop.py:2101), `stamp_forwarded_at`, and the old-shape/consumed refusals are untouched. The flagged `test_agent_supervisor_pending_prompt.py` edit (setup helper `_approved_at_forward_prompt`, 558-565) is a **faithful fixture fix, not an assertion weakening**: it seals the single `operator_resume_pending_prompt` approve event (`input_digest=base["digest"]`) that a genuine cross-process approval always writes, so the manually-staged record satisfies the new invariant. Exactly one approve event is sealed (no ambiguity), and the test's assertions are unchanged (`outbox rows == 1`, `CLAUDE_RUNNING`, `record.consumed`). The `test_a_second_resume_does_not_double_forward` exactly-once assertion still holds (44-test run + full-suite green).

**5. Boundary compliance (R149/R150, R140, SHADOW-ONLY) — PASS.** Smallest bounded fix: one const (`OPERATOR_APPROVAL_EVENT`), one pure verification function, one refusal-sealer method, one call-site guard, one import (`AuditChainError` from the existing module). It reuses the pre-existing sealed hash-chained `audit.jsonl` — **no journal signing, no new store/format/service/daemon/PKI/identity system, no supervisor redesign, no broadening**. No `LoopConfig.forwards`/authority/activation/tier surface touched; `assert_forwarding_allowed` and SHADOW posture intact (backed by the still-green `PostureUnchanged` tests). Zero new dependencies; no manifest/lockfile edit. Diff confined to 4 allowed-path files. R140 preserved (dead `LoopConfig.packet_reference` left in place; no unrelated cleanup). **No scope creep observed.**

**6. Test quality of the 6 new tests — PASS.** They drive real components (real supervised park via `_park_real`, real `resume-pending-prompt` CLI via `run_cli`, fresh-loop resume) and mutate only the journal, faithfully modelling the threat. Assertions match claims: `provider_calls == 0`, `SELECT COUNT(*) FROM outbox == 0`, durable sealed `cross_process_resume_refused` with the specific reason code, and `verify_chain().ok` (genuine approval remains authoritative). The RED-proof genuinely disables the fix at the module global the call site resolves at call time, and asserts the injected content reaches the outbox. The non-vacuity test proves the C2 reconstruction check alone returns the malicious body. `FailClosedEdges` covers missing / ambiguous / chain-invalid with distinct reason codes. Non-vacuous throughout.

---

## New advisory finding

**MINOR-2 (advisory, non-blocking) — the ambiguity rule can false-refuse one narrow genuine flow.** `verify_approved_digest_against_audit` refuses `approved_digest_audit_ambiguous` whenever **>1** sealed approve event for the run names the journal `approved_digest`. Because `approval_digest` covers only 5 fields with no per-park nonce/cycle (loop.py:564-583) and the forward message-id keys on **cycle** (loop.py:2101, so distinct-cycle forwards are *not* duplicate-suppressed), two separate cross-process park→approve→resume cycles in the **same run** with byte-identical covered instructions (same task_id/stage/paths/action/stops) would seal two `(run_id, input_digest)`-identical approve events, and the second cross-process resume would refuse. This is **fail-closed (safe, not a bypass)**, the owner explicitly required an `ambiguous → fail closed` branch, and no existing test hits it (normal per-cycle-distinct actions are unaffected — 1380 green). Advisory only: a future bounded refinement could disambiguate on the sealed event's `detail.cycle` (already present in the data) to eliminate the false refusal while preserving the anti-replay guarantee. **Not blocking; does not undermine the required security property.**

---

## Per-owner-requirement (source-015) conformance — G3 lane

- **R145** (resume cross-checks against sealed audit, not journal alone): **PASS** — item 1.
- **R146** (missing/unreadable/ambiguous/chain-invalid → fail closed, distinct codes, durable record): **PASS** — item 2 (six codes, all tested; MINOR-2 is an advisory on the ambiguity *breadth*, still fail-closed as required).
- **R147** (happy path forwards exactly once; clock-invariant; SHADOW untouched): **PASS** — item 4 (HappyPath/CrossProcessResume/ExactlyOnce/ClockInvariant/PostureUnchanged green).
- **R148** (never fail-open/warn-only; refusal durably sealed): **PASS** — items 2/3.
- **R149** (zero provider calls on any resume refusal): **PASS** — asserted in every fail-closed test; `provider_calls` is a genuine counter (item on loop.py:1631/1750).
- **R150** (reuse existing sealed hash-chained audit; no new store/format/signing): **PASS** — item 5.
- **R144, R151-R154** (owner hold/adjudication, sequencing/routing/acceptance/ledger): orchestrator-lane, not producer/G3-satisfiable; noted only.

The owner's 7-step adversarial test (source-015) is realized executably and passes: genuine approval → self-consistent journal forgery → sealed audit unchanged → resume fails closed → 0 provider calls → durable sealed mismatch → all existing C2/happy/exactly-once/clock/shadow tests green.

## Boundary-compliance statement

The rework is the smallest bounded fix confined to the resume-window trust anchor: no journal signing, no new infrastructure/service/PKI, no supervisor redesign, no broadening, R140 and SHADOW-ONLY preserved, no activation. Confirmed against the diff and the running suite.

## Verdict rationale

MAJOR-1 is closed exactly per my recommended remedy, with an executable adversarial fail-closed proof and a RED-on-pre-fix proof, zero provider calls, and a durable sealed refusal that leaves the genuine approval authoritative and the chain valid. MINOR-1 is resolved. The fix is additive, correct, fail-closed on every degenerate branch, within every owner boundary, and the full suite is green (independently reproduced 1380/2). The one new finding (MINOR-2) is a narrow, fail-closed availability edge the owner's directive explicitly tolerates, and is advisory. My original G3 PASS holds at the new identity, and the activation-blocking condition previously attached to MAJOR-1 is discharged for the G3 lane (final closure subject to G5/DCV concurrence per the owner's routing).

**G3 VERDICT: PASS** (MINOR-2 advisory, non-blocking; MAJOR-1 CLOSED; MINOR-1 RESOLVED).

---

Relevant absolute paths:
- Reviewed code: `C:/Users/MLFLL/Downloads/nyc-zoning/orch/tools/agent_supervisor/loop.py` (guard 2250-2269, function 714-800, sealer 2177-2201), `C:/Users/MLFLL/Downloads/nyc-zoning/orch/tools/agent_supervisor/cli.py` (approval seal 1736-1742), `C:/Users/MLFLL/Downloads/nyc-zoning/orch/tools/agent_supervisor/audit_log.py`
- New/edited tests: `C:/Users/MLFLL/Downloads/nyc-zoning/orch/tools/test_agent_supervisor_audit_anchor.py`, `C:/Users/MLFLL/Downloads/nyc-zoning/orch/tools/test_agent_supervisor_pending_prompt.py` (558-565)
- Producer report: `C:/Users/MLFLL/Downloads/nyc-zoning/orch/project-control/reports/M0-T048-producer-report.md` (REWORK section, R.1-R.9)
- Owner adjudication: `C:/Users/MLFLL/Downloads/nyc-zoning/nyc-development-feasibility-claude-pack/project-control/directives/D-010-autonomous-engineering-restructure/source-015-amendment.md`
