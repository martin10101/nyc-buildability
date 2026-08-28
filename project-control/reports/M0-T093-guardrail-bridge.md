# M0-T093 — Unit H1: guardrail-refusal classification + bounded 4.8 bridge — D-024 Phase E

Producer: fable-orchestrator-session (orchestrator). Supervisor-freeze qualifying evidence:
**D-024-R103** (Phase E; packet-named). Status: **STAGED (claim + G0 + scenario pack)** — the
seq-19 session accepted unit G, claimed this unit, and authored this pack at a clean seam under
the D-010 R113/R114 rotate-at-seam ceiling (the same pattern that staged units F and G). The
successor implements from this frozen pack with a fresh context budget. No implementation code
is written at this staging seam. Applicable set: **49 requirements** (R068–R075 Phase-E core,
R103/R110, R165/R177, + the standing conduct/identity/testing set; resolve live via
`evaluate_task_refs`).

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

## 4. Evidence (populated during implementation — successor)

(pending — staging seam only)
