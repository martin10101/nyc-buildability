# M0-T093 — Unit H1: guardrail-refusal classification + bounded 4.8 bridge — D-024 Phase E

Producer: fable-orchestrator-session (orchestrator). Supervisor-freeze qualifying evidence:
**D-024-R103** (Phase E; packet-named). Status: **IMPLEMENTED** — the seq-19 session staged
this pack at a clean seam (the unit-F/G pattern); the seq-20 successor session implemented it
from the frozen pack (§4 evidence). Applicable set: **49 requirements** (R068–R075 Phase-E
core, R103/R110, R165/R177, + the standing conduct/identity/testing set; re-resolved live via
`evaluate_task_refs` after the c7c0a36 packet amendment: ok=true, 49 ids, no missing/invalid).

## 0. Reuse boundary (R018: prove existing architecture, extend — never duplicate)

| Existing surface (REUSE, do not duplicate) | What it already provides | Unit-H1 extension |
|---|---|---|
| `model_turnover.py` (`ExhaustionClassification`, `TurnoverEvidence`, `ExhaustionVerdict`, `classify_exhaustion`, `_LIMIT_HINT`/`_NETWORK_AMBIGUITY`/`_PERMISSION_DENIED` patterns) | the EXISTING conservative evidence-based classifier for quota/limit exhaustion, with network-ambiguity and permission-denied separation | NEW `guardrail_refusal.py`: a DISTINCT classifier for the narrowly recognized Fable-5 guardrail-refusal shape (R068). It must reuse the evidence-object style and the negative guards (security-test failure, permission denial, credential boundary, unknown prompt, genuinely prohibited request, quota/limit) but keep its OWN triggers/counters/transitions — R075 demands the two policies stay distinct and never cross-actuate |
| `claude_runner.py` (`QUOTA_EXHAUSTION_FIXTURES`, `classify_quota_exhaustion`, `QUOTA_EXHAUSTION_SIGNAL_VERIFIED`) | the live detect-and-hold quota policy (D-007 am.12 / R603–R608) | the bridge REFUSES to actuate on anything this classifier claims (S2); quota keeps its hold path untouched |
| `approved_models.py` (allowlist + probe ledger) + `policy.resolve_model` | owner-approved model options only; no silent substitution | the "exact allowlisted continue-with-4.8 option" check (R069): the continuation choice must match an interface-presented, config-allowlisted option — never an arbitrary approval/prompt answer |
| `workload_classifier.classify_workload` + `spawn_decision.model_fit` | lower-tier workload-fit + stricter health-profile rules | R072 lower-tier continuation consults these; never a different task/broader scope |
| `child_handoff.py` (`ChildHandoff`, `TurnoverCoordinator`) + `handoff.py` | bounded-children collection + durable VERIFIED handoff | bridge steps (2)–(4) of R070: finish smallest atomic operation, collect already-running bounded children, checkpoint, durable handoff — compose these, do not rebuild |
| `state_machine.py` (additive states/transitions; unit-F precedent: +4 states/+17 transitions) | the governed transition graph with GRACEFUL_STOPPING et al. | additive bridge states (e.g. `GUARDRAIL_BRIDGE`, `REPRESENT_FABLE`) + triggers; every entry/exit journaled; phase1 count assertion updated WITH citation (the unit-F worked pattern) |
| `durable_state.DurableJournal` (`set_state`/`get_state`/CAS) + unit-F `epoch_lease` boot reconciliation | durable, restart-surviving records | R071 two-attempt re-entry counter as a journal key, digest-bound to the refused request, surviving restart (S14); no infinite ping-pong |
| `refusals.py` (typed outcomes, stable exit codes) | machine-readable refusal contract | new reason codes only; no new exit-code outcomes unless genuinely new class |
| `subagent_contracts.assert_worker_text_clean` + `redaction.py` | worker-text hygiene + redaction | the R071/R073 re-presentation transform emits clean, redacted, semantic-preserving text; journaled "without unnecessary sensitive content" (R070 step 1) |
| `worker_turnover.py` / `turnover_controller.py` (M0-T054/T056) | the exact-once single-redispatch precedent under owner gates | the bridge's "first-safe-seam retirement to fresh Fable 5" mirrors this discipline; actuation stays record-intent-only wherever the live interface choice is not owner-authorized (SHADOW-ONLY stands) |
| unit-G `operator_status` labeled-facts pattern | honest sourced/confidence status facts | bridge/refusal state surfaces as labeled status facts (unknown never zero) |

Genuine gaps (the ONLY things to build): `guardrail_refusal.py` (classifier + negative guards),
`refusal_bridge.py` (R070 bridge restrictions + seam retirement + re-entry counter +
re-presentation transform with R073 semantic-preservation rules), additive state-machine
states/transitions, thin wiring into the loop's existing decision points, and the §1 matrix
as `tools/test_agent_supervisor_guardrail_bridge.py`.

## 1. Acceptance-scenario pack (pre-implementation; section-16.4 matrix — R110)

| ID | Scenario (Given / When / Then) | Kind | Key reqs |
|---|---|---|---|
| S1 exact recognized refusal | Given a narrowly recognized Fable-5 guardrail-refusal shape (fixture), when classified, then the verdict is `guardrail_refusal` with the evidence recorded and task identity + exact authorization/acceptance criteria preserved in the journal entry (no unnecessary sensitive content). | deterministic (fixtures) | R068/R070/R103 |
| S2 quota cannot enter the bridge | Given quota/rate-limit exhaustion evidence (reuse `model_turnover`/`claude_runner` fixtures), when classified, then it follows the SEPARATE detect-and-hold policy and the bridge REFUSES to actuate; triggers/counters/transitions provably distinct (different journal keys, different states). | deterministic | R075/R110/R184 |
| S3 unrecognized-similar does not actuate | Given refusal-LOOKING but unrecognized output, when classified, then NO actuation — conservative unknown, recorded, held for review. | deterministic | R068/R110 |
| S4 security failure is not a refusal | Given a real failing security test / policy violation output, when classified, then it is a defect signal, never a routing event. | deterministic | R068/R110 |
| S5 unknown approval never auto-answered | Given an unknown approval/permission/credential/destructive prompt, when the bridge is active, then it is NEVER automatically answered (only the exact allowlisted continuation option is selectable). | deterministic | R069/R110 |
| S6 exact allowlisted continue-with-4.8 | Given the interface presents the exact allowlisted continue-with-4.8 option after a recognized refusal, when the policy evaluates, then that single option is selectable (recorded actuation-intent under SHADOW-ONLY); any other option shape refuses. | deterministic | R069/R070 |
| S7 bridge cannot expand | Given the 4.8 bridge active, when it attempts a new task/investigation/subagent/scope, then the restriction layer refuses mechanically (typed error), and only finish-smallest-atomic-operation / collect-children / checkpoint / handoff are permitted. | deterministic | R070/R110 |
| S8 bounded children reconcile | Given already-running bounded subagents, when the bridge runs, then they finish and reconcile via the existing `child_handoff` machinery; none are orphaned or spawned anew. | deterministic | R070/R110 |
| S9 first-valid-seam retirement | Given the bridge reaches the first valid seam, when it lands, then it retires to fresh Fable 5 with a complete bounded durable handoff (existing handoff machinery), never continuing past the seam. | deterministic | R070/R103/R110 |
| S10 bridge output reviewed | Given useful bridge output, when the unit completes, then it enters the SAME review path as any producer output (never auto-accepted); defective bridge output is rejected by that path. | deterministic | R074/R110 |
| S11 semantic-preserving re-presentation | Given a refused legitimate request, when re-presented, then purpose/authorization/constraints/acceptance criteria are PRESERVED (tests prove invariants); clarification only — never euphemism, encoding, fragmentation, constraint deletion, or authority escalation (negative tests for each prohibited transform). | deterministic | R071/R073 |
| S12 first re-entry success path | Given re-presentation attempt 1 succeeds, when classified, then the counter clears/records success and normal flow resumes. | deterministic | R071 |
| S13 two-attempt cap → configured behavior | Given two fresh Fable-5 re-entries both receive the recognized refusal, when the cap trips, then the configured lower-tier continuation (workload-fit + stricter health profile, same bounded task only) or BLOCKED behavior per live policy engages; a higher-precedence policy forbidding it wins. | deterministic | R071/R072 |
| S14 counter survives restart | Given attempt 1 recorded then controller restart, when the same refused request re-appears, then the durable counter continues at 2 (digest-bound; boot reconciliation), never resets. | deterministic | R071/R110 |
| S15 fallbackModel does not replace policy | Given Claude Code's native fallbackModel setting, when a guardrail refusal or quota event occurs, then the custom policies govern (native fallback covers only supported availability/overload cases) — asserted at the policy/config boundary. | deterministic | R165 |
| S16 no worker pollution + distinct triggers | Given all bridge/refusal text and journal entries, when composed, then `assert_worker_text_clean` passes and refusal-vs-quota triggers remain distinct typed codes end-to-end. | deterministic | R045/R184 |
| C1 live refusal canary (OWNER-GATED) | Given the installed terminal, when an owner-approved exact-command canary elicits a live recognized refusal shape, then the classification fixture is upgraded to measured-live (R192/R197 pattern). | live canary (owner exact-command) | R068/R149/R183 |

## 2. Owner-gated items (flagged, not blocking the deterministic core)

- **C1 live refusal canary**: the recognized-refusal SHAPE on the installed version is
  fixture-confidence until an owner-approved live capture (same discipline as every prior C1);
  the classifier ships conservative — unrecognized shapes NEVER actuate (S3).
- **Live actuation of the continue-with-4.8 interface choice** stays behind the standing
  SHADOW-ONLY/R595 posture: the deterministic core records actuation-intent; live clicking is
  never enabled by this unit.

## 3. Implementation guidance for the successor (not yet done)

- **Modularity:** two NEW focused modules (`guardrail_refusal.py`, `refusal_bridge.py`);
  additive `state_machine` edits with the phase1-count citation pattern; thin loop wiring.
  cli.py is symbol-warned — do NOT grow it beyond registration if any verb is needed
  (none is expected; the bridge is loop-internal).
- **R075 separation proof:** the matrix must show BOTH directions — quota evidence never
  classifies as refusal AND refusal evidence never classifies as quota (parameterized
  fixtures from `model_turnover`'s existing pattern set).
- **R073 transform:** implement re-presentation as a deterministic, testable function over a
  structured request record (purpose/authorization/constraints/criteria fields), never
  free-prose rewriting; semantic-preservation tests compare field sets, not vibes.
- **Counter key:** digest-bound (`request_digest`) journal key, e.g.
  `guardrail_reentry/<digest>`; CAS or read-modify-write inside the journal transaction;
  boot reconciliation reads it (unit-F `reconcile_on_boot` precedent).
- **Fixtures:** put recognized/unrecognized refusal shapes in
  `tools/agent_supervisor/fixtures/` (documentation-confidence until C1), mirroring the
  2_1_248 capture conventions.
- **Test file:** `tools/test_agent_supervisor_guardrail_bridge.py` (the §1 matrix; R110
  names the required cases; targeted mutation pass per the unit-F/G method — and NEVER run
  mutants while a suite runs in the background).
- **DCV scale:** 49 applicable requirements — build the evidence map per behavior cluster;
  `M0-T094-evidence-map.json` and `M0-T092-evidence-map.json` are the worked templates.
- **Environment:** long background python runs are externally killed on this box — run
  suites in foreground chunks (see the seq-19 handoff §7 facts).

## 4. Evidence (implementation session, 2026-08-28, seq-20 successor)

Bootstrap Gate 0 (R125–R128): passed BEFORE any write — primary cwd IS the worktree root
(`git rev-parse --show-toplevel` = `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`), branch
`control/D-024-fable-codex-loop`, HEAD `84f658e` clean and == origin at start; NO MCP tools
attached to the live session (toolset enumerated: zero `mcp__*` entries).

Deliverable commits: `c7c0a36` (packet allowed_paths surgical amendment — the 387f530
precedent; the two state-count assertion files M0-T092 also carried), `633a9d1`
(implementation), `0f4fc6a` (mutation-survivor test-gap closure). All cite D-024-R103.

### 4.1 Prove-first reuse (R018)

Reused exactly as §0 planned: `model_turnover` negative guards/normalization/attribution via
NEW additive public aliases (no duplication); `classify_exhaustion` as the quota-direction
delegate; `claude_runner` quota corpus untouched; `approved_models` exact membership (R069);
`workload_classifier` + `spawn_decision.model_fit` (R072); `child_handoff.TurnoverCoordinator`
(child drain); `handoff.Handoff`/`validate_handoff` (retirement); `durable_state` CAS
(counter); `assert_worker_text_clean` + `redact_text` (hygiene); `worker_turnover.
WorkerTurnoverIntegration` as the seam-object pattern; the unit-F additive-state pattern.
Genuine gaps built (only the §0 list): `guardrail_refusal.py`, `refusal_bridge.py`,
`fixtures/guardrail_refusal_shapes_2_1_248.json`, +2 states/+11 documented transitions,
thin loop seam AFTER the quota seam (R075 ordering), and the §1 matrix test file.

### 4.2 Modularity

A `baseline_growth` FAIL appeared on grandfathered `loop.py` (baseline 1899 SLOC, allowance
+190; the seam pushed it to 2100). Resolved by the unit-G precedent — facade-preserving
split, NOT an exception record: the pending-prompt approval-binding block (327 physical
lines: `approval_digest`, parked/approved/consumed records, M0-T048 covered-instruction
reconstruction, sealed-audit cross-check) moved VERBATIM to NEW `pending_prompt.py`;
`loop.py` re-exports every public name. Its four accepted test packs pass unchanged
(pending_prompt 19, park_approve_binding 9, audit_anchor 6, c2_binding 10).
`modularity_check --check`: **0 failures**. ruff 0.13.0 (the CI-pinned version): **0
findings on every new/changed surface**; the 5 `loop.py` F401s predate this unit at the
accepted HEAD (verified via `git show HEAD:` — same 5 lines, recorded not hidden).

### 4.3 Matrix + mutation

`tools/test_agent_supervisor_guardrail_bridge.py`: **71 tests, 0 failures** — S1–S16 incl.
BOTH-direction quota-vs-refusal separation (S2 parameterized over the model_turnover/
claude_runner shape set in each direction), restart-surviving digest-bound counter on a
reopened real journal (S14), real-`SupervisedLoop` seam tests (recognized refusal →
`guardrail_refusal_recorded` + PAUSED_RECOVERY + journaled identity-preserving record;
ordinary/refusal-looking failures → the existing `no_valid_checkpoint` unchanged; absent
integration → unchanged; quota-first ordering with both seams injected), and the
activated-path state walk (refusal → bridge → seam → fresh session → re-present →
accept/repeat/cap-blocked).

Targeted mutation pass (unit-F/G method; serial, never during a live suite): **10/10
non-equivalent mutants KILLED** — M1 skip quota delegate, M2 drop authorization proof,
M3 refusal-looking→recognized, M4 drop attribution, M5 cap=3, M6 cap counts succeeded
records, M7 spawn-subagent permitted, M8 retire never latches, M9 continuation matches
kind only, M10 constraint deletion allowed. M6/M7 initially SURVIVED → two test gaps
closed in `0f4fc6a` (hardcoded forbidden-op names; success-at-cap-boundary) → re-run
KILLED. One analyzed EQUIVALENT mutant documented (not run): swapping the two loop seam
blocks is observationally equivalent for every classifiable input because the classifier's
own quota-direction delegate (M1, killed) enforces the R075 separation regardless of
consultation order; the loop ordering is defense in depth.

### 4.4 Composed suite (foreground chunks; long background python runs are externally killed here)

Chunk A (21 supervisor files): **717 ran, 0 failures**. Chunk B (19): **808 ran, 0
failures, 2 skipped**. Chunk C (16): **531 ran, 0 failures**. Chunk D (24 tool files):
**417 ran, 0 failures, 1 skipped**. pytest pair (event_bus + goal_integration): **76
passed**. `test_directive_compliance` by class groups (5 chunks): **120 ran, 0 failures**
(29 + 6 + 20 + 33 + 32). **Composed total: 2,669 ran / 0 failures / 3 skipped.**
`validate_directive_compliance.py --check`: **EXIT=0** after the c7c0a36 packet amendment
and this unit's report/evidence-map. CI on the pushed SHA is the confirming whole-suite run.

### 4.5 Owner-gated residuals (§2 unchanged)

C1 live refusal canary (R192/R197 exact-command) still pending-owner: the corpus stays
documentation-confidence (`verified_live=false` everywhere — asserted by a test). Live
actuation of the continue-with-4.8 choice stays behind SHADOW-ONLY/R595;
`assert_actuation_permitted` double-gates it mechanically and is proven to refuse each
half-gate. DCV evidence map: `project-control/reports/M0-T093-evidence-map.json` (49 rows).
