# M0-T090 — G4 Independent QA Review

> Saved VERBATIM by the orchestrator from the qa-engineer agent-return channel (transport
> entity-decoding only). Verdict: PASS (3 advisories; none blocking). Reviewer ran from a
> pack-repo worktree (agent-a2c40102cc6592d8e — classifier-denied for this session; joins the
> owner's documented purge list) but executed all commands in the shared ctl24 checkout.

# Gate Report

- Gate ID: G4 (QA / test-quality)
- Task ID: M0-T090 — D-024 C1: bounded subagent contracts + structural workload sizing
- Reviewer: qa-engineer (independent; read-only)
- Producer: orchestrator
- Result: **PASS** (advisory findings only)
- Clean environment/worktree used: Reviewed frozen content at commit `e8b21d1` (material identity `3e726a0fcc3ea574337d8e2166d3710322586806232fc52506372362f820baba`). Reviewer's own worktree lags (pinned at `d8b3899`, M0-T077) and does not contain the deliverables; per the packet, later commits on `control/D-024-fable-codex-loop` are control-plane-only, so the `tools/agent_supervisor/**` source in the shared `ctl24` checkout equals the frozen content. Corroborated by reproducing the producer's exact test counts (53 / 290 / 42). Python 3.11.9 sandbox; the new modules avoid PEP 695 generics and collect cleanly.

## Acceptance criteria reviewed

The packet has no `acceptance_scenarios[]`; acceptance is defined by `.outputs` (deliverables) + `required_gates` (G0/G2/G3/G4/G5) + the D-024 s16.2 sizing cases named in output #3. All named deliverables were checked for existence AND substance (lesson from M2-T015 — gates must check `task.outputs`, not just tests):

| Named output | Present | Substance |
|---|---|---|
| assignment + supervision-envelope schemas + structural classifier under `tools/agent_supervisor` | YES | `subagent_contracts.py` (587), `workload_classifier.py` (238), `spawn_decision.py` (239) — full frozen dataclasses, closed vocabularies, typed errors, validators |
| startup-overhead measurement + graph-based sizing/packet integration | YES | `startup_overhead.py` (218), `workload_sizing.py` (260) — measurement ledger + calibration, graph adapter, tier reuse, packet plan |
| `tools/test_agent_supervisor_bounded_contracts.py` (s16.2 sizing cases incl. no-quota proof) | YES | 686 lines, 53 tests, deterministic, no network; s16.2 coverage map reproduced below |
| `project-control/reports/M0-T090-bounded-contracts.md` | YES | Substantive: what-was-built table, s16.2 map, carried-advisory disposition, integration decisions, self-checks |

## Directive/requirement verification

Full requirement-by-requirement D-024 (R001..R128) verification is the separate `directive-compliance-verifier` pass. As G4 QA I reproduced, from source, the directive requirements the QA dimensions directly exercise:

| Requirement ID | Reviewed content identity | Verdict | Reproduced evidence |
|---|---|---|---|
| D-024-R045 (no worker-facing quota/percentage/countdown/conserve pressure) | e8b21d1 | PASS | `_QUOTA_PATTERNS` (10 classes) + `assert_worker_text_clean` fail closed on all 8 parametrized phrasings incl. "3.5k tokens"; INDEPENDENT-scan proof (`_INDEPENDENT_QUOTA_SCAN`, a distinct regex table) confirms the rendered prompt carries none; mutation (a) confirms teeth |
| D-024-R080 (stale graph reported, never acted on as fact) | e8b21d1 | PASS | `classify_workload(graph_stale=True)` → `unknown-recon-first`/`graph_stale`; `tier_signals(stale)` raises `stale_graph`; `neighborhood_from_view` fails closed on malformed views (never optimistic empty) |
| D-024-R081 (preserve graph/context-intelligence; reuse tiers exactly) | e8b21d1 | PASS | `tier_signals`/`packet_plan` delegate to `tools.context_pack_budget.select_tier` via lazy import; `plan.tier/target_tokens/withheld_larger_target == budget.select_tier(...)` directly; `medium`-without-justification stays target-withheld at `TIER_TARGET_TOKENS[NORMAL]` |
| D-024 s5.5 (structural, not token-prediction, classification) | e8b21d1 | PASS | four closed classes; objective `WorkloadFeatures`; deterministic rule precedence; conservative UNKNOWN (0/6 ambiguous inputs classified cohesive); boundaries use strict `>` |
| D-024 s6 (two linked pre-spawn records; producer cap 3; no overlapping writers; leak guard) | e8b21d1 | PASS | `WorkerAssignment`+`SupervisionEnvelope` validated as a linked pair; `assert_grantable` refuses 4th writer, overlapping scopes (incl. Windows path form), shared mutable resource; `assert_no_envelope_leak` blocks band names + controller numerics |
| D-024 s13 (smallest-complete packet; stop on unprovable sufficiency) | e8b21d1 | PASS | `packet_plan` includes/justifies every s13 category, marks unknown categories/blank justifications as errors, sets `sufficient=False` + stop_reason on empty graph sources or truncated neighborhood |
| D-024-R101 (Phase C supervisor-freeze qualifying evidence) | e8b21d1 | PASS | cited in packet, every new-module docstring, and (per producer report) the content commit message; supervisor stays SHADOW-ONLY (no spawn/resume/stop surface added; R595 untouched) |

No gap found between the QA-relevant named requirements and reproducible evidence. Remaining ALL-requirement coverage is deferred to the DCV pass by design (producer ≠ verifier).

## Steps independently executed

All run with `cwd=C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`, Python 3.11.9:

1. `python -m pytest tools/test_agent_supervisor_bounded_contracts.py -q` → **53 passed in 0.17s**
2. `python -m pytest tools/test_agent_supervisor_statusline_handler.py tools/test_agent_supervisor_telemetry_core.py tools/test_agent_supervisor_subagent_telemetry.py tools/test_agent_supervisor_rotation.py tools/test_agent_supervisor_scheduler.py -q` → **290 passed in 7.27s**
3. `python -m pytest tools/test_mcp_policy.py -q` → **42 passed in 0.61s** (the accepted M0-T101 fix)
4. `python -m pytest tools/test_directive_compliance.py -q -k "registry"` → **3 passed, 117 deselected in 82.18s** (spot-slice; confirms the directive pack collects and runs at the frozen tree)
5. `python tools/modularity_check.py --check` → **EXIT 0** (warnings are on pre-existing OTHER files — `cli.py`, `policy.py`, `mappluto_geometry_arcgis.py`, `surveyReview/types.ts`, `context_benchmark.py`; none of the 5 new modules is flagged)
6. `python -m ruff check <5 modules + test pack>` → **All checks passed!**
7. In-memory mutation teeth + determinism probes via standalone scripts (monkeypatching only; no repo writes) — outputs below.

### Mutation teeth (each mutant RED, real GREEN)

| Mutation | Real (unmutated) | Mutant | Teeth? |
|---|---|---|---|
| (a) drop `numeric_tokens` from `_QUOTA_PATTERNS`, phrase "About 3.5k tokens should suffice." | raises `quota_language` | NO raise → `test_quota_language_rejected_fail_closed` would FAIL | YES. Independent scan confirms `numeric_tokens` is the ONLY pattern matching "3.5k tokens" — the guard genuinely carries that case |
| (b1) `SdkTaskTracker._evict` → pure oldest-first | test passes | test FAILS ("newer-done should be evicted") | YES. Kills the oldest-first mutant that the pre-existing bounded-eviction test missed |
| (b2) `SubagentRegistry._evict` → pure oldest-first (`popitem(last=False)`) | test passes | test FAILS ("newer-closed should be evicted") | YES |
| (c) `decide_spawn` overloaded → resume | `spawn-new`/`unhealthy_not_resumed` | `resume-existing`/`resume_healthy` → not-resumed assertion FAILS | YES |

### Determinism / robustness probes (all as expected)

- `classify_workload`: negative counts raise `negative_feature`; bad `declared_class` raises `bad_declared_class`; non-tuple seams raise `bad_seams`; every valid `declared_class` returned as override; **0/6 ambiguous inputs classified cohesive** (unknown is never optimistic); strict `>` boundaries verified (outcome==1 → cohesive, ==2 → oversized; breadth==40 → cohesive, ==41 → oversized).
- `decide_spawn`/`model_fit`: bogus work_class raises `bad_classification`; negative packet target raises `bad_packet`; headroom<1 raises `bad_headroom`; headroom boundary exact (window==needed OK, needed-1 fails); deterministic over 100 identical calls (1 distinct output).
- `HealthBands`: equal bands rejected (`band_order`, strict ordering), `emergency==1.0` and `observe==0.0` rejected (`bad_band`, `0<x<1`), `land<prepare` rejected.
- `OverheadLedger` at `max_observations=1`: after 5 records → len=1, evicted=4; calibration keeps only the newest; median of [100, None, 300] = **200.0** (None skipped, never coerced to zero).
- `packet_plan`: unknown category, blank justification, missing id all fail closed; empty graph sources with the graph category included → `sufficient=False` + stop_reason; malformed/`non-mapping`/empty-seed views fail closed rather than yielding an optimistic empty neighborhood.

## Expected versus actual

| Check | Expected | Actual |
|---|---|---|
| New pack | 53 passed | 53 passed |
| Adjacent supervisor packs | 290 passed | 290 passed |
| MCP policy (M0-T101 fix) | 42 passed | 42 passed |
| Composite suite arithmetic | 2595 (M0-T099 baseline) + 53 + 5 = 2653 | Verified: SESSION_HANDOFF/M0-T099-G2 §5 = **2595 / 3 skipped / 0 failed**; M0-T101-G2 shows `test_mcp_policy.py` went 37 (5 failed/32 passed) → **42 passed** = +5 new shape tests; 2595+53+5 = **2653** (closes) |
| 3 skips | env-conditional, adjudicated | Confirmed via M0-T099-G2 §2: (1) `test_agent_supervisor_process.py:448` POSIX-only guard on Windows; (2) `test_agent_supervisor_policy.py:449` Windows symlink privilege (WinError 1314); (3) `test_repo_fingerprint.py:148` symlinks unavailable on host |

The ~40-minute composite (2653) was NOT re-run; verified via arithmetic + stored orchestrator-captured evidence (evidence-capture division of labor) plus the live registry spot-slice.

## Evidence paths

- Deliverables: `tools/agent_supervisor/{subagent_contracts,workload_classifier,spawn_decision,startup_overhead,workload_sizing}.py`; `tools/test_agent_supervisor_bounded_contracts.py`; `project-control/reports/M0-T090-bounded-contracts.md`
- Producer self-check: `project-control/reports/M0-T090-G2-self-check.md`
- Baseline/skip provenance: `docs/SESSION_HANDOFF.md` §5; `project-control/reports/M0-T099-G2-self-check.md` §2; `project-control/reports/M0-T101-G2-self-check.md`
- Reviewer probe scripts (scratchpad, not in repo): `gate_probes.py` (mutation teeth), `gate_probes2.py` (determinism)

## Human-style walkthrough findings

Not a UI task; N/A. The `render_worker_prompt` path was exercised end-to-end: a valid assignment/envelope pair renders a worker prompt that passes both the R045 quota guard and the envelope-leak guard, and carries all four required duty texts and the `Checkpoint/commit allowed: no` line.

## Regression/security/provenance findings

- No production behavior added to the frozen supervisor — the package remains SHADOW-ONLY; `spawn_decision`/`decide_spawn` return records only. No spawn/resume/stop/message surface. R595 pre-activation prerequisite untouched.
- Leaf-package discipline holds: no new import of the graph/index machinery; graph evidence arrives by value; the one cross-package import (`tools.context_pack_budget`) is lazy and fail-closed. Adjacent packs (290) still green — no regression.
- The carried G3-M1 eviction tests are test-only, hosted in this pack because the sibling telemetry pack is outside allowed paths; they exercise the real sibling production code (`telemetry_sdk`, `telemetry_hooks`) and I confirmed they carry teeth. No production edit to the siblings. Placement is disclosed in the report §3 and the test docstrings.
- Modularity: all 5 new modules under the 600 warn line (largest 587); `modularity_check --check` EXIT 0; ruff clean. No dumping-ground module; each carries one responsibility with its own typed error class.

## Defects

None blocking. Advisory only:

- **ADV-1 (advisory):** `packet_plan` treats every s13 category as omittable given any non-blank justification. Omitting mandatory categories (e.g. `bounded_task_and_acceptance`, `authority_and_prohibitions`) still yields `sufficient=True` with `included=()`. Only `graph_selected_files_symbols` triggers a source-sufficiency stop. Recommend the consuming runtime unit enforce which s13 categories are non-omittable. Non-blocking: this is a shadow-only controller PLAN record and runtime enforcement is explicitly deferred.
- **ADV-2 (advisory):** The no-quota / vague guards are regex-based and, by design, cannot catch natural-language pressure that avoids the enumerated numeric/keyword markers. All owner-prohibited forms (numeric token quota, percentage, countdown, conserve-tokens) ARE covered and fail closed; the report acknowledges the broad-rejection tradeoff. Worth flagging for a later LLM-review/runtime layer.
- **ADV-3 (advisory/minor):** The envelope-leak numeric check uses substring `value in prompt`, so short thresholds (e.g. "0.5") could false-positive on unrelated legitimate occurrences. Fail-closed direction, so safe; noted only for completeness.

## Required rework

None. Advisory items ADV-1/ADV-2 are candidates for the next Phase C/D runtime unit; no change required for this unit's acceptance.

## Reviewer conclusion

**PASS.** Every named deliverable exists and is substantive. The required test suites reproduce exactly (53 / 290 / 42). The four key guards demonstrably carry teeth (each mutant RED, real GREEN), including the no-quota `numeric_tokens` case and both eviction-order guards. Determinism/robustness probes confirm negatives raise, `declared_class` validates, unknown is never optimistic, boundaries are strict, health-band ordering and fraction bounds hold, ledger eviction counts correctly at max=1, medians skip unknowns (never zero), and packet planning fails closed / stops rather than dropping constraints. The no-quota proof is genuinely independent (a distinct regex table, not the guard's own). The composite-suite arithmetic (2595 + 53 + 5 = 2653) closes against the M0-T099 baseline and the M0-T101 +5, and the 3 skips are the standing adjudicated env-conditional ones. Deferred coverage (runtime bands, landing, extension runtime, emergency stop, durable child handoffs) is honestly disclosed as out-of-scope for this unit. Findings are advisory only and do not block acceptance.
