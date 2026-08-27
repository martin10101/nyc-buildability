# M0-T106 G4 QA review — round 1 (VERBATIM reviewer return; transport entity-decoding only)

Saved by the orchestrator per the report-preservation rule. Reviewer: qa-engineer (independent,
read-only, dispatched 2026-08-27). Verdict returned: **PASS-with-required-corrections** (M1
MEDIUM blocking).

---

# G4 QA GATE REPORT — M0-T106 (D-024 Amendment 3 unit E: bounded /goal integration)

**Reviewer:** qa-engineer (independent; read-only) · **Gate:** G4 · **Date:** 2026-08-27
**Producer:** fable-orchestrator-session · **Reviewer ≠ producer:** confirmed

**Frozen identity verified:** deliverable commit `c3f376882690a0460222f26612e03fcbf02608bd`; live HEAD `ff2e2a8…`; both objects present in the worktree object store. Reviewed via read-only `git archive c3f3768 | tar -x` export (worktree lagged at `d8b3899`).
**Applicable requirements:** D-024-R152, D-024-R162, D-024-R174.

## VERDICT: PASS-with-required-corrections
One MEDIUM correction (**M1**) BLOCKS acceptance. The deterministic core is otherwise strong: 31/31 scenario tests directly mapped, full `tools/` regression clean, 2/2 re-applied mutants killed, fixture 100% traceable to the accepted snapshot, and all R045 / version-gate / verdict / clearing / resume / autocompact behavior verified (including verbatim documented phrasings). M1 is a small, well-scoped hardening.

---

## Reproduction environment
Python 3.11.9; pytest 8.4.2; ruff 0.13.0; `claude --version` = **2.1.247 (Claude Code)** (matches producer & fixture). Note: repo targets 3.12 (PEP 695); `services/api` has 15 pre-existing SyntaxError collection failures on 3.11 — environmental and out of scope for `tools/`.

## Duty 1 — Scenario-to-test traceability (S1–S11)
Every scenario has a DIRECT test; all 31 pass. Weaker-proxy / gaps flagged.

| Scenario | Test(s) | Coverage |
|---|---|---|
| S1 condition composition | test_s1_condition_has_all_documented_parts, _one_task_only, _campaign_scale_refused, _direct_construction_cannot_drop_the_bound, _ceiling_and_required_parts | DIRECT, strong (parts, bound, ≤4000, one-task binding, foreign-task refusal) |
| S2 no-token-pressure (R045) | test_s2_token_pressure_fails_closed, _clean_condition_passes_r045 | DIRECT for end_state vector; **constraints vector not directly tested** (validator covers full text — I confirmed via probe P4). Minor (L2) |
| S3 verdict ingestion | test_s3_documented_verdicts_normalize, _unknown_verdict_is_unknown | DIRECT for normalize_verdict; **"typed record / reason bounded-sanitized" is broader than tested** — the 160-char `reason_excerpt` cap is never asserted. Minor (L2) |
| S4 clearing classes | test_s4_four_unrecoverable_classes, _host_managed_auth_stays_active, _transient_stays_active, _user_clear_and_no_goal_and_unknown | DIRECT, strong; verbatim phrasings verified (probe P5) |
| S5 no-progress | test_s5_no_progress_pause_is_structural_and_goal_stays_set | DIRECT (structural: paused / cleared / running / unknown) |
| S6 resume semantics | 4 tests incl. pre-2.1.239 picker exclusion + honest unknown | DIRECT, strong |
| S7 check-in schedule | test_s7_default_cadence_doubles_capped_at_4x, _env_scales_and_zero_disables, _malformed_env_fails_visible, _version_gates_honest | DIRECT, strong |
| S8 check-in ingestion | test_s8_checkin_lands_in_durable_bus_with_dedup, _unknown_kind_recorded_honestly | DIRECT for durable-landing + true-replay dedup + unknown-kind. **Distinct-records-not-collapsed boundary is UNTESTED** → M1 |
| S9 goal-status telemetry | test_s9_status_numbers_labelled, _absent_numbers_unknown_never_zero | DIRECT, strong (R042 labels, absent→unknown, bool/neg/str→unknown) |
| S10 autocompact policy | test_s10_context_overflow_is_turnover_seam, _other_clearings_are_not_the_seam_trigger | DIRECT, mutation-proven |
| S11 docs drift | test_s11_fixture_valid_and_no_drift_recorded, _code_matches_fixture_facts, _version_helpers | DIRECT — pins fixture↔code on every constant; leak-guarded |

## Duty 2 — Re-run evidence (exact counts, my machine, frozen tree)
- Goal pack: **31 passed** (0.42s)
- Event-bus pack (publish_typed additive): **38 passed** (2.20s)
- bounded_contracts (R045 validator source): **53 passed** · telemetry_core (records/journal): **53 passed** · native_adapter (unit C): **58 passed**
- 278 targeted slice (goal+event_bus+telemetry_core+subagent_telemetry+native_adapter+bounded_contracts): **278 passed** (8.62s) — reproduces the producer's figure exactly.
- **Full `tools/` suite (I ran it, since producer's full runs were stopped): 2830 passed / 5 failed / 5 skipped in 671s (~11 min).** All 5 failures are `.git`-absence artifacts of the git-archive export (`not_a_repo` / `git ls-files failed 128`: test_repo_fingerprint, test_modularity_check::RealRepoTests, test_repo_index_baseline/incremental, test_context_integration::Proof7) — **none in agent_supervisor, none in unit E's changed set**. This is strong independent evidence of zero regression for a new-files-plus-one-additive-method diff.
- Diff confirmed **purely additive**: event_bus.py `+19 / -0` (the `publish_typed` method only; existing publish paths byte-unchanged); goal_* files and fixture are new. Line counts match report exactly (153/240/170/311/346).
- **Adequacy judgment:** the producer's targeted-slice + clean-collection + CI evidence is adequate for this diff shape, and I independently upgraded it with a full `tools/` run. Adequate. ✅

## Duty 3 — Adversarial probes (10 categories, all executed)
- **4000/4001 chars:** 4000 constructs (== ceiling), 4001 rejected. ✅
- **own vs foreign task_id in end_state:** own task_id repeated → allowed; different task_id → rejected. Correct (`t != self.task_id`). ✅
- **Campaign tripwire bypass:** "finish the milestone", "the rest of the backlog", "wrap up the project", "complete the remaining work" all **SLIP THROUGH** the heuristic; "entire/whole campaign", "every/all remaining tasks/units" refused. → **L1** (structural one-task binding is the primary R152 guard and holds; heuristic is disclosed defense-in-depth with real gaps).
- **R045 poison via constraints:** all four poison phrases in a *constraint* → rejected (validator sees full text). ✅
- **Verbatim documented cause phrasings:** context_overflow / credit_exhausted / model_unavailable / auth_failure all classify correctly. ✅
- **Marker collision (model+context):** context wins (order priority auth>credit>context>model); "model credit balance" → credit. Deterministic; documented phrasings unaffected. → **A2** (generic "context" marker could misclassify hypothetical future phrasings).
- **env whitespace/plus:** "  15  "→15, "+15"→15, "015"→15, "  "(blank)→REJECTED fail-visible. Note "1_0"→10 (Python int underscore separators) → **A4** cosmetic.
- **checkin count=0:** empty offsets, enabled=True (consistent); count=-1 rejected. ✅
- **idle cap boundaries:** 2.1.235→0, 2.1.236→None(uncapped), 2.1.245→None(uncapped), 2.1.246→3, garbled→None. Boundaries exactly correct. → **A1** (None overloads "uncapped-known" and "unknown"; disclosed in docstring).
- **publish_typed false-dedup:** two check-ins with **identical attributes + different timestamps + no `sequence` → SECOND COLLAPSED** (dups=1); with distinct `sequence` → both stored; true replay (same seq) → deduped. → **M1** (see below).

## Duty 4 — Mutation plausibility (2 of 9 re-applied outside the repo)
- `backoff-cap-removed` (`gap = min(gap*2, cap)` → `gap = gap*2`): **test_s7 FAILS** — offsets diverge to uncapped (30,90,210,**450,930**) vs (30,90,210,330,450). KILLED. ✅
- `seam-trigger-any-unrecoverable` (drop `and clazz=="context_overflow"`): **test_s10_other_clearings_are_not_the_seam_trigger FAILS** — credit_exhausted wrongly returns True. KILLED. ✅
Both revert cleanly. Mutation harness is genuine (not vacuous).

## Duty 5 — Fixture honesty
Every fact in `goal_semantics_2_1_247.json` traces to the accepted M0-T102 snapshot (verdicts, warning prefix/suffix, four clearing classes + host-managed nuance, transient-stays-active, no-progress, resume routes/counters, check-in cadence/env/caps, delivery kinds, 4000 ceiling, availability/trust, evaluator/env-var warning, non-interactive). **Version gates match code exactly** (2.1.234 / 2.1.236 / 2.1.246 / 2.1.239). Drift `[]` is consistent with the snapshot. No invented behavior; no path/username/UUID leaks (independent scan clean; only hit is the benign in-test needle assertion). → **A3**: the snapshot's pre-2.1.239 "turn-end check-in recurs at first interval" fact (snapshot line 143) is not captured in the fixture and `checkin_schedule` doesn't model that pre-2.1.239 turn-end/idle backoff split — out of the 2.1.246+ operational range, so non-material; note for completeness.

## Duty 6 — Report / G2 accuracy (M0-T104 typo precedent)
All numbers reproduce: line counts 153/240/170/311(+19)/346 exact; 31 / 38 / 278 exact; ruff 0.13.0 "All checks passed" on the 5 files; modularity thresholds warn=600/hard=1000 with largest changed file 311 → comfortably clean. **The "2,720 whole-tree, zero errors" figure IS reproducible** and honestly disclosed: `tools/` (2,840) minus `test_directive_compliance.py` (120) = **2,720, zero collection errors**. The label "whole-tree" denotes the `tools/` supervisor test tree, not the whole repo (whole repo = 4,540 tests + 15 pre-existing 3.12 `services/api` errors). → **A4** labeling nuance only; no numeric defect. C1 live canary correctly flagged owner-gated (R192/R197) and NOT executed, per unit-C/D precedent; R162 = the owner-approval-gate pattern, satisfied by the C1 flagging.

---

## FINDINGS

### M1 — MEDIUM (REQUIRED CORRECTION — blocks acceptance)
**`publish_typed` dedup collapses two genuinely-distinct check-in records that share identical attributes; check-in sequence integrity depends on an undocumented, untested caller-supplied discriminator.**
`DurableEventBus.publish_typed` keys on `record_type + session_id + task_id + canonical(attributes)` and **deliberately excludes `timestamp_utc`**. Excluding the timestamp is *correct* (it's ingestion-time, so including it would break true-replay idempotency — the bus's whole purpose; I confirmed a same-`sequence` replay still dedups). BUT `goal_checkins.ingest_checkin` reads `sequence` as **optional**; when the observed check-in payload carries no distinguishing field, two genuinely-distinct consecutive check-ins (e.g., idle check-in #1 and #2 for the same still-running task) produce byte-identical attributes and **the second is silently dropped as a "duplicate no-op"** (reproduced: probe P10, `dups=1`). This undercounts check-ins and specifically defeats the R174 idle-cap-of-3 corroboration use case. The `/goal` docs specify no check-in payload schema, so the presence of a discriminator is an **unverified assumption** in a durable seam — and there is **no test** asserting distinct check-ins survive (S8 only exercises the identical-payload true-replay case), and **no documented caller contract**.
**Required correction (small):** (a) document the caller contract that check-in observations MUST carry a stable per-delivery discriminator (a `sequence`/delivery id that is identical across replays but distinct across deliveries), and/or make a missing discriminator fail-visible rather than silently collapsing; and (b) add a regression test asserting that two distinct check-ins (differing only by `sequence`/ordinal) both persist while a byte-identical re-delivery dedups. The underlying design is sound; this closes the silent-undercount boundary the task directed me to probe.

### L1 — LOW (non-blocking; recommend hardening)
Campaign-scale tripwire (`_CAMPAIGN_SCALE_RE`) misses common phrasings — "finish the milestone", "the rest of the backlog", "wrap up the project", "complete the remaining work" all compose a valid condition. Disclosed as heuristic; the **structural one-task binding is the primary R152 control and holds**, but it does not constrain condition *text* semantics, so the tripwire is the only guard on text. Recommend widening the regex (verbs finish/complete/wrap-up + this/the milestone/backlog/project/campaign).

### L2 — LOW (non-blocking; test completeness)
Two direct-coverage gaps the behaviors already satisfy but tests don't assert: (i) S2 R045 poison via *constraints* (validator covers it — probe P4 confirms; add an assertion); (ii) S3 the "typed record / bounded reason" claim — the 160-char `reason_excerpt` cap is never asserted.

### A1–A4 — ADVISORY (no action required)
- **A1** `idle_checkin_cap()` returns `None` for both "uncapped-known" (2.1.236–2.1.245) and "unparseable-unknown"; disclosed in docstring; non-operational at 2.1.247.
- **A2** `classify_goal_message` marker-order collision resolves deterministically (auth>credit>context>model); generic "context" marker is a mild future-fragility; all documented phrasings correct.
- **A3** Fixture omits the snapshot's pre-2.1.239 turn-end-recurrence fact; `checkin_schedule` doesn't model that split; out of the 2.1.246+ range.
- **A4** `int("1_0")`→10 (Python underscore separators) accepted for the env var; and "whole-tree" in G2 means the `tools/` subtree (number reproduces exactly).

---

## Scope / modularity note (informational)
The deliverable commit also touches `project-control/state.json`, `project-control/tasks/M0-T106.json`, and adds `M0-T106-G2-self-check.md` + `M0-T106-evidence-map.json` beyond the single report named in `allowed_paths`. These are the orchestrator-as-producer ledger/evidence bookkeeping consistent with the M0-T104/T105 governance pattern (ADR-005) — not a producer-scope code edit. Not a defect; noted for completeness.

## Requirement coverage (QA view; formal PASS/FAIL is the directive-compliance-verifier's)
- **R152** (one cohesive task, never one goal for the campaign): structural one-task binding + foreign-task refusal + tripwire + tests → evidence PRESENT (L1 caveat on tripwire breadth, non-blocking).
- **R162** (owner-approval-gate pattern for the live canary): C1 correctly flagged owner-gated and not executed → PRESENT.
- **R174** (bounded /goal continuation, background-agent check-ins, idle cap): goal_checkins + goal_outcomes + event_bus + tests → PRESENT; M1 is a quality gap *within* R174's check-in-ingestion scope, not a failure to deliver it.

**Bottom line:** PASS-with-required-corrections. Resolve **M1** (document the check-in discriminator contract + add the distinct-records regression test) before acceptance; **L1/L2** recommended in the same pass; **A1–A4** advisory. No git/gh/project_control mutations were performed. Orchestrator: please record this gate verbatim.
