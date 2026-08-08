# M0-T048 — G4 QA review (RERUN, rework delta) — VERBATIM reviewer return

Orchestrator preservation note: saved verbatim from the reviewer agent-return channel
(transport entity-decoding only: `&lt;`→`<`, `&gt;`→`>`). Reviewer: qa-engineer (independent,
producer ≠ reviewer). Frozen review identity `fee612ae724085576aad23c0fd1d387fa89e800d`; code
identity `9c450a5`. Recorded by the orchestrator 2026-08-08.

---

I have complete, independently-reproduced evidence for all 8 owner properties. My worktree is restored clean. Here is my full G4 rerun report.

---

# G4 QA GATE REPORT (RERUN) — M0-T048 (C2 closure, G3 MAJOR-1 rework)

**Task:** M0-T048 — cross-process resume-window trust anchor (D-010 source-015, R144–R154)
**Gate:** G4 (independent QA), rework delta
**Reviewer:** qa-engineer (independent; read-only). Producer ≠ reviewer.
**Reviewed identity (frozen):** `fee612ae724085576aad23c0fd1d387fa89e800d` (control/M0-T048-c2-close merge head). Rework code head `9c450a5`.
**Method:** Created a detached checkout of the frozen SHA in my own isolated worktree, ran the suite and my own in-process mutation probes at that identity, then restored the worktree to its original branch (clean). All throwaway probes were written outside the repo. No tracked file, ledger, or git-integration state was modified.
**Verdict: PASS.**

---

## Property-by-property findings

### P1 — Full supervisor suite (owner-expected 1380 passed / 2 skipped)
Command (my run, at frozen SHA):
```
python -m pytest tools/test_agent_supervisor_*.py -q
→ 1380 passed, 2 skipped in 122.64s
```
**Exact match** to the owner-mandated count. New file adds 6 tests; delta over the pre-rework C2 baseline (1374) is +6, 0 failures, 0 new skips. **PASS.**

### P2 — Owner adversarial test implements steps 1–7 EXACTLY
`AuditAnchorForgery::test_two_field_plus_digest_forgery_fails_closed_no_provider` (verified line-by-line against the verbatim directive):

| Owner step | Implementation | Verified |
|---|---|---|
| (1) genuine operator approval | `_genuine_approval()` → real `_park_real()` + real CLI `resume-pending-prompt --approve-prompt-digest <operator_digest>`; asserts code 0 and `approved_digest == operator_digest`. The CLI seals the operator-approval event (cli.py:1736). | ✓ genuine, not staged |
| (2) self-consistent journal mutation of approved_instruction + approved_digest (+ prompt/prompt_bytes_digest) | `_forge_all_four_fields()` sets a new malicious instruction, `new_digest=approval_digest(mal)`, `new_prompt=build_forwarded_prompt(mal)`, `prompt_bytes_digest=digest_of(new_prompt)` — all four self-consistent. | ✓ |
| (3) sealed operator-approval audit record UNCHANGED | only `_set_pending(forged)` (journal write); audit file untouched. | ✓ |
| (4) resume | fresh `loop3.run(...)` from FORWARD_PROMPT (separate loop, shares only the durable journal). | ✓ |
| (5) fail closed | `assertRaises(LoopError)`, code `forwarded_prompt_unavailable`. | ✓ |
| (6) provider calls == 0 | `loop3.provider_calls == 0` **and** `SELECT COUNT(*) FROM outbox == 0` (the discriminating assertion). | ✓ (see Advisory 1) |
| (7) mismatch/refusal durably recorded | exactly one sealed `cross_process_resume_refused` event, `decision="refuse"`, `reason="approved_digest_audit_mismatch"`, and `verify_chain().ok is True` after the refusal (genuine approval event stays authoritative). | ✓ |

All seven properties are concretely asserted, not narrated. **PASS.**

### P3 — Independent RED-on-pre-fix (my own in-process mutation)
My throwaway probe (outside the repo) neutralized the new cross-check and re-ran the OWNER adversarial test:
```
PROBE 1  CONTROL  (check ENABLED) : PASSED (fail-closed held)
PROBE 1  MUTATION (check DISABLED): FAILED: LoopError not raised
PROBE 2  check disabled → outbox rows: 1 | EXFILTRATE present: True | provider_calls: 0
```
With `lp.verify_approved_digest_against_audit` monkeypatched to a no-op, the forged `EXFILTRATE ALL SECRETS` body reaches the outbox and the fail-closed test turns RED — proving the new cross-check, not an incidental guard, is what closes the hole. The always-on `test_red_when_crosscheck_disabled` pins the same pre-fix behavior (asserts an outbox envelope containing the injected marker); my PROBE 2 independently reproduces it. **PASS.**

### P4 — Non-vacuity (the cross-check is the operative defense, not redundant)
`test_non_vacuity_reconstruction_check_alone_would_forward` calls the C2 reconstruction check on the forgery and asserts it returns the malicious body. My PROBE 3 confirms it independently:
```
PROBE 3  verify_covered_instruction ALONE returns malicious body: True | EXFILTRATE present: True
```
The self-consistent forgery satisfies the C2 reconstruction check ALONE (the forged instruction reproduces the forged digest and body), so pre-fix the injection would forward. Only the new audit cross-check refuses. **PASS.**

### P5 — Fail-closed edges + my gap probes
Named tests (all green, distinct reason codes, zero provider, durable record, chain re-verified):
- missing approval → `test_missing_approval_event_refuses` → `approved_digest_audit_missing`
- ambiguous/duplicated → `test_ambiguous_approval_events_refuse` → `approved_digest_audit_ambiguous`
- chain tamper → `test_chain_tamper_is_detected_and_refuses` → `approval_audit_chain_invalid` (and chain remains invalid after)

The function `verify_approved_digest_against_audit` carries six distinct fail-closed codes: `unavailable / unreadable / chain_invalid / missing / mismatch / ambiguous`. My own gap probes (beyond the producer's set):
```
PROBE 4  audit=None on resume path → raised forwarded_prompt_unavailable | outbox 0 | provider 0  (no fail-open)
PROBE 5  genuine approved_digest → PASS (no false refusal)
PROBE 5  forged digest          → approved_digest_audit_mismatch
PROBE 5  wrong run_id           → approved_digest_audit_missing
```
The audit=None branch (theoretically unreachable in the normal build, since `_build_loop` always supplies an AuditLog) still fails closed rather than open — correct defensive posture. **PASS** (one by-design observation in Advisory 2).

### P6 — Regression + adjudication of the flagged setup edit
Regression classes I re-ran verbosely, all green:
- `c2_binding` (10): TwoFieldForgery, HappyPathBinding, ClockInvariant, PostureUnchanged, FailClosedReasonCodes
- `park_approve_binding` (9): incl. TamperAfterApproval, HappyPath, ApprovePendingPromptUnitTests
- exactly-once: `LoopResumeForwardExactlyOnceTests::test_a_second_resume_does_not_double_forward`
- cross-process: `CrossProcessResumeTests::test_park_then_cli_approve_then_fresh_start_forwards_once_and_rotates` (13 passed / 6 deselected in the filtered run)

**Setup-edit adjudication (the load-bearing question).** The +8-line change makes `LoopResumeForwardExactlyOnceTests._approved_at_forward_prompt` seal an `operator_resume_pending_prompt` (decision=`approve`, `input_digest=base["digest"]`) event, with the journal `approved_digest == base["digest"]`. I verified from **cli.py:1731–1742** that a REAL approval ALWAYS (a) transitions on `owner_approved_pending_prompt`, then (b) seals exactly that event with `input_digest=recorded`, then (c) binds `approved_digest=recorded` via `approve_pending_prompt` — so genuinely `approved_digest == input_digest`. The setup now **mirrors production reality**; it does not mask a false-refusal the field would hit. This is corroborated behaviorally by the genuine end-to-end `CrossProcessResumeTests` test (real CLI approve + fresh-loop forward driven through the new guard) forwarding **exactly once with no false refusal**, and by my PROBE 5 (a genuine operator digest passes the new function directly). Without the setup edit the fixture would have staged an approved record with no sealed approval event — a state production never produces — and the new guard would correctly refuse it; so the edit corrects an unfaithful fixture rather than hiding a defect. **PASS.**

### P7 — Exactly-once preserved
`test_a_second_resume_does_not_double_forward` (crash between send and consume → second FORWARD_PROMPT entry) yields exactly one outbox row, journal at CLAUDE_RUNNING, record consumed. The new guard is a pure, idempotent read of the audit chain that passes on a genuine record on both the first and the retry attempt, so it introduces no double-forward and does not block the duplicate-suppressed retry. `CrossProcessResumeTests` also asserts a single forward. **PASS.**

### P8 — Clock invariance
The cross-check compares the journal `approved_digest` against the sealed event `input_digest`; both are the timestamp-free operator-named `approval_digest`. The forward-time clock is appended only by `stamp_forwarded_at` and is excluded from the binding (message id keys on the approval binding). `ClockInvariant::test_clock_only_change_does_not_invalidate_the_approval` is green. The new anchor is timestamp-independent by construction. **PASS.**

---

## Scope / boundary corroboration (advisory to G3/G5/DCV lanes)
The rework commit `9c450a5` is **purely additive — 573 insertions, 0 deletions** across exactly four files: `loop.py` (+138), the new `test_agent_supervisor_audit_anchor.py` (+288), the `pending_prompt.py` setup (+8), and the producer report (+139). Grep of loop.py additions for `assert_forwarding_allowed | forwards= | default_mode | activate | supervised_auto | tier_ | autonomy | LoopConfig.forwards` returned **nothing**; `cli.py` is unchanged (the fix reuses the pre-existing M0-T046 sealed event). This is consistent with R140 (no removal/refactor), no new infrastructure, and SHADOW-ONLY untouched — the `PostureUnchanged` behavioural backstop is green.

---

## Advisory notes (non-blocking)

1. **`provider_calls == 0` is non-discriminating in this harness.** With `max_cycles=1` the counter is 0 whether the forgery is refused or forwarded (my PROBE 2 shows `provider_calls: 0` even when the malicious body reached the outbox). The owner's step-6 property is literally satisfied, and the test is non-vacuous overall — but the discriminating assertion is `outbox count == 0` on refusal vs `outbox == 1 (EXFILTRATE present)` on the RED path, not the provider counter. Consider (future, optional) exercising a resume with `max_cycles ≥ 2` so `provider_calls` also becomes discriminating; not required for this gate.

2. **Best-effort refusal seal on an already-broken chain.** `_seal_cross_process_resume_refusal` swallows `AuditChainError` (append refuses to extend a damaged chain), so in a pathological "audit tail unappenable" corruption the distinct `cross_process_resume_refused` event would be skipped. In that case the durably-broken chain is itself the evidence and fail-closed/zero-forward/zero-provider still hold; in every realistic tamper case tested (mismatch/missing/ambiguous/middle-record chain tamper) the refusal IS sealed. Documented by-design; low severity.

3. **Ambiguity rule is conservative.** If two DISTINCT cycles of one run ever produced byte-identical approval instructions (identical task_id/stage/action/paths/stops → identical `approval_digest`), the second resume would refuse `approved_digest_audit_ambiguous`. This is unlikely (per-cycle requested-action text differs) and fail-closed is the owner-mandated safe direction — an observation, not a defect.

4. **Anchor trust root.** The defense rests on `AuditLog.verify_chain()` (M0-T046 accepted infrastructure), which is out of this task's scope; the chain-tamper test confirms it detects the specific forgery attempted here.

---

## Verdict
**PASS.** The rework closes G3 MAJOR-1: at cross-process resume the journal `approved_digest` is cross-checked against the sealed, hash-chained operator-approval audit event before any forward. The owner's 8-step adversarial harness is implemented exactly; I independently mutation-proved the fix is the operative defense (RED-on-pre-fix reproduced with my own in-process neutralization, malicious body reaching the outbox when disabled); the C2 reconstruction check alone is shown insufficient (non-vacuity); missing/ambiguous/chain-invalid/audit-None edges all fail closed with distinct codes, zero provider calls, and a durable record; and the C2, happy-path, exactly-once, clock-invariant, cross-process-resume, and shadow-posture regressions are green. Full suite 1380 passed / 2 skipped at the frozen SHA. The flagged setup edit faithfully mirrors what a genuine CLI approval seals (cli.py:1736–1742) and does not mask a production false-refusal. The four advisory notes are non-blocking.

**Files reviewed (frozen SHA `fee612ae…`):**
- `tools/agent_supervisor/loop.py` — `verify_approved_digest_against_audit` (714–795), guard in `_resume_approved_forward` (2260–2269), `_seal_cross_process_resume_refusal` (2177–2201), `OPERATOR_APPROVAL_EVENT` (711)
- `tools/agent_supervisor/cli.py` — genuine-approval seal path (1704–1754)
- `tools/test_agent_supervisor_audit_anchor.py` — 6 tests (new)
- `tools/test_agent_supervisor_pending_prompt.py` — setup edit (547–566) + exactly-once/cross-process regressions
- `tools/test_agent_supervisor_park_approve_binding.py` — `_CrossProcessHarness`
- `project-control/reports/M0-T048-producer-report.md` — REWORK section (§§R.1–R.9)

(My throwaway probe lives outside the repo at the session scratchpad `.../scratchpad/qa_probe.py`; no repo/ledger/git state was modified — worktree restored to `worktree-agent-aea0c140451b2583a` @ `9c2ec25`.)
