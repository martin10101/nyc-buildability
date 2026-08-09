# M0-T054 — Producer report (AOS §6): Unattended main-orchestrator model-turnover watchdog

**Task:** M0-T054 (backend / defect-lane, D-010 source-028, R304–R319 + carried R300–R302, R315–R319)
**Producer:** orchestrator (implementation by backend-engineer producer, opus-4.8; live-proof evidence
orchestrator-captured). **Reviewed code identity:** `3c36c42` (task branch), integrated to main via PR
#211; reviewed HEAD at submit `89c4e30`. **Requested status:** awaiting_gate.

## 1. Objective delivered
A small, independently-live turnover **mechanism** (a process outside the main Claude session) that, on a
Fable-5 quota hard stop: (a) recognizes the grounded/typed exhaustion signal; (b) preserves stopped-session
evidence durably; (c) launches exactly one successor pinned to `claude-opus-4-8` xhigh; (d) loads the
durable handoff; (e) updates only the lawful MUTABLE worker-model selection; (f) resumes idempotently
(exactly-once, no duplicate workers/commits); (g) FAILS CLOSED on ambiguity.

## 2. Files (strictly additive: 14 files, +3500 / −0)
- `tools/agent_supervisor/model_turnover.py` — fail-closed exhaustion classifier (exact weekly phrase /
  typed Fable quota code; transient 429 excluded; ambiguous → FAIL_CLOSED).
- `tools/agent_supervisor/turnover_controller.py` — exactly-once successor decision, single-instance lock,
  duplicate suppression, Fable→Opus audit linkage, safe-stop-if-opus-unavailable.
- `tools/agent_supervisor/turnover_adapters.py` — SingleInstanceContinuationLock, HashChainedAuditSink,
  SupervisorLauncher (model/effort hard-pinned; argv-safe), SupervisorIdentity.
- `tools/agent_supervisor/worker_turnover.py` + `loop.py` (+37/−0) + `cli.py` (+10/−0) — one gated worker
  seam inside the existing checkpoint-not-ok branch; entered only if an integration is injected AND
  classify == FABLE_EXHAUSTED.
- `tools/agent_supervisor/claude_runner.py` — live-signal plumbing (real stream-json `seven_day`
  rate-limit + exhaustion text surfaced so turnover fires in the live loop).
- 5 test files (`tools/test_agent_supervisor_*turnover*.py`) + 2 real Fable-exhaustion fixtures.

## 3. Test evidence
**79 deterministic turnover tests**; full supervisor suite **1481 passed / 2 skipped, 0 failures** (M0-T039
freeze baseline preserved: 1471 + 10 live-signal; every non-exhaustion path byte-for-byte unchanged).
Reproduced independently by the orchestrator and by the three gate reviewers.

## 4. Live proof (R316)
`project-control/reports/M0-T054-live-proof/LIVE-PROOF.md`: real Fable worker exit 1 + real `seven_day`
rate-limit + exact phrase → `classify_exhaustion` → FABLE_EXHAUSTED → one opus-4-8 launch decision +
Fable→Opus audit link → a **real opus-4.8 worker launches** (exit 0). Real fixtures saved. Every real link
proven on an isolated non-product runtime; no production change; no owner `/model`.

## 5. Gate evidence (all PASS at 3c36c42)
- G3 code-reviewer PASS — `M0-T054-G3-code-review.md`
- G5 security-reviewer PASS — `M0-T054-G5-security-review.md`
- DCV directive-compliance-verifier PASS 16/16 — `M0-T054-DCV-verification.md`

## 6. Scope & honest limitation
Delivers the turnover **mechanism** (layer-agnostic detection + actuation + adapters, worker-layer loop
integration, R316 live proof). Production wiring is **record-intent-only**: a confirmed exhaustion is
classified + recorded + surfaced but **never auto-launched** in production, because no runnable mode
authorizes an automatic redispatch (shadow forwards nothing; supervised holds at WAIT_FOR_OWNER;
LIMITED-AUTO off). Live production auto-actuation (both layers) = the owner-gated **R595 activation**,
tracked as follow-up **M0-T056** — not a defect. Protected immutable config, `default_mode=shadow`,
supervised runtime, LIMITED-AUTO-off holds all preserved (doctor proof ALL-12 PASS re-run live).

## 7. Directive coverage
All 16 applicable D-010 requirements independently verified PASS at delivered mechanism scope (see
`verification.json` M0-T054 row + `M0-T054-evidence-map.json`). R305/R306/R310 carry the
live-activation-deferred note (R595/M0-T056); R318 steps 8-10 and R319 item 7 are downstream of the owner
decision. 0 violated, 0 unverifiable.

## 8. Readiness
Ready for G0/G2/G3/G5 gate records + acceptance. Acceptance unblocks M2-T015 unit 3k (resume on opus-4.8).
