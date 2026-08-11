# M2-T016 backend slice — G5 security/safety gate (security-reviewer) — VERDICT: PASS (F1 MEDIUM required pre-wiring)

Saved verbatim by the orchestrator (transport only). Reviewer: `security-reviewer` (independent, read-only;
≠ producer `backend-engineer`). Reviewed SHA `5d2ebbb` (worktree `agent-a8724b1c4277f23fe`, base `37667ff`).
Additive confirmed (only the 3 impl + 3 test files). Gate modules byte-unchanged.

---

## VERDICT: PASS

No critical or high blocking defects. The forge-a-confirmation and principal-from-payload defenses are correct and reproduced. One MEDIUM (F1) + three LOW advisories. F1 is a required tracked follow-up before this slice is wired to a real authenticated route; non-blocking for this backend-only disclosed slice (no route exists yet; path is fully audited/guardable).

## Reproduction
- `pytest tests/documents/test_review_authz.py test_review_events.py -q` → 142 passed; `test_review_actions.py` → 39 passed (181 total; the 3 files don't transitively import PEP-695 `units.py`).
- `git diff --stat 37667ff 5d2ebbb -- state.py promotion.py correction_history.py gate.py isolation.py errors.py models.py` → empty (gate modules unmodified).

## The 8 security questions
1. **No forged promotion / no auto-confirm — PASS.** `professionally_confirmed` only via `confirm_document` requiring QUALIFIED_PROFESSIONAL role + `promotion_gated_transition` with server-computed `store.promotion_verdict()` per material fact; request DTO has no verdict/confidence/"confirmed" field; `evaluate_promotion` gives confidence/method zero weight; confirmed edges are `_HUMAN`-only.
2. **Principal integrity — PASS in-slice** (role derived server-side from closed `CorrectingPrincipal` map, never from payload; fail-closed on unknown/AI/empty) + one CRITICAL integration note F5.
3. **Immutability & provenance — PASS** (no handler writes `original_value`/`baseline_*`; corrections append-only + CAS; closed correction-entry key contract blocks smuggling). See F4.
4. **Gate reuse — PASS** (gate modules byte-unchanged; slice only calls `promotion_gated_transition`; raw `transition()` never invoked).
5. **Injection / adversarial — PASS** (no eval/exec/subprocess/open/format/pickle; digest used only as key/hash; optimistic concurrency via fingerprint + CAS fails closed).
6. **Audit completeness — PASS** (every action appends a `ReviewAuditEvent` + enqueues recalc; pro event without actor_id refused at construction).
7. **B-001 honesty — PASS** (`ReviewStore` Protocol seam; only in-memory test store; no logging; metadata-only payloads).
8. **Downstream honesty — PASS with F1 caveat** (rejected→BLOCKED, refused→BLOCKED, promotable-unconfirmed→PROVISIONAL, confirmed→None; only 1.4.0 vocabulary; never "verified"; clears only via evidence-state change).

## Findings
- **F1 — MEDIUM (required pre-wiring; non-blocking for this routeless slice).** `correct_fact`/`reject_fact` have no document-lifecycle precondition; on a `professionally_confirmed` document a user correction stays `confirmed`, `downstream_impact=None`, doc stays `professionally_confirmed` — bypassing "reopening is visible and audited, never silent." Reproduced (user correction on a confirmed doc → value=9999, confirmation=confirmed, impact=None). Not a forged-confirmation/escalation (reaching `confirmed` still needs the professional + server gate; the edit is attributed/audited). Remediation: refuse `correct_fact`/`reject_fact` when `record.state is PROFESSIONALLY_CONFIRMED` (require explicit `reopen_document`/edge-12 first), or reset the fact's `professional_confirmation` and force a reopen; add regression test.
- **F2 — LOW.** `confirm_document` non-atomic: doc saved confirmed, then per-fact loop; a mid-loop `ConcurrentReviewModification` leaves doc confirmed with some facts unconfirmed (fails loudly). Production `ReviewStore` must bind transition + all per-fact confirmations + audit in one transaction.
- **F3 — LOW.** reject_fact/per-fact confirm use `correction_history` as CAS token; concurrent `professional_confirmation` writes not lock-covered (last-write-wins; both authorized + audited — consistency nit).
- **F4 — LOW.** `expected_original` cross-check compares the fact's own field to itself (== G3 A1); real guarantee (no handler writes original_value) still holds; pass a truly independent original when retrievable.
- **F5 — CRITICAL wiring note (not a defect in reviewed code).** The safety chain rests on the unwritten route/store: the route MUST populate `ReviewPrincipal` from the authenticated channel (never the body), and the production `ReviewStore` MUST validate the `sha256:` digest and compute `promotion_verdict` solely from stored deterministic results. Carry as a hard requirement on the B-001 route/store task.

## Recommendation
Record G5 = PASS. Remediate F1 (doc-state precondition / auto-reopen on post-confirmation edits + regression test); carry F2/F5 as explicit requirements on the B-001 route/store binding; F3/F4 minor, same follow-up.
