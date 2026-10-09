# M0-T090 — G3 Independent Code Review

> Saved VERBATIM by the orchestrator from the code-reviewer agent-return channel (transport
> entity-decoding only). Verdict: PASS with findings (2 major / 4 minor / 3 nit; none
> blocking; majors required before any future activation of the contract machinery).

# Gate Report

- **Gate ID:** G3 (independent code review)
- **Task ID:** M0-T090 — D-024 Phase C1: bounded subagent contracts + structural workload sizing
- **Reviewer:** code-reviewer (independent; read-only)
- **Producer:** orchestrator
- **Result:** **PASS (with findings)** — 2 major, 4 minor, 3 nit; none blocking
- **Clean environment/worktree used:** Reviewed the frozen content of commit `e8b21d1` (labeled material identity `3e726a0f…baba` at G2). Verified read-only that the five modules, the test pack, and the report are **byte-identical** between `e8b21d1` and current `HEAD` (`68d6f02`): `git diff --stat e8b21d1 HEAD -- tools/agent_supervisor tools/test_agent_supervisor_bounded_contracts.py project-control/reports/M0-T090-bounded-contracts.md` is empty; all post-freeze commits touch only control-plane files (`gates/`, `reports/*.json`, `state.json`, `tasks/`, directive `verification.json`). Freeze integrity holds.

## Acceptance criteria reviewed

The packet carries `acceptance_scenarios: []`; acceptance is the s16.2 sizing/no-quota matrix expressed as executable tests plus the four named `outputs`. All four outputs are present: the assignment + supervision-envelope schemas and structural classifier, the startup-overhead measurement + graph-based sizing/packet integration, `tools/test_agent_supervisor_bounded_contracts.py`, and the producer report. Test pack runs green: `python -m pytest tools/test_agent_supervisor_bounded_contracts.py -q` → **53 passed in 0.21s**.

## Directive/requirement verification

Scope note: full independent compliance over all 46 applicable D-024 requirements is the `directive-compliance-verifier` pass (producer ≠ verifier), recorded separately in the directive `verification.json`. Below I verify, at frozen content `e8b21d1`, the **code-level encoding fidelity** of the requirements the modules explicitly claim to encode — re-derived from `source-001.md` and `requirements.json`, not from the producer's map.

| Requirement ID | Reviewed content identity | Verdict | Reproduced evidence |
|---|---|---|---|
| D-024-R101 (Phase C: assignment/envelope schemas, structural classifier, startup overhead, graph sizing, Goldilocks) | e8b21d1 | PASS | Requirement text matches task scope. Cited in packet objective, in **all five** module docstrings + the test-pack docstring, and in the content commit message `M0-T090 content: … (D-024-R101)`. Supervisor-freeze §3 citation duty satisfied (packet + docstrings + commit). |
| D-024-R045 (no numeric token limits/targets/percentages/countdown/conserve-pressure in any worker-facing field) | e8b21d1 | PASS-with-gap | `assert_worker_text_clean` + `_QUOTA_PATTERNS` scans every `worker_text_fields()` string and the rendered prompt; 8 canonical prohibited phrasings caught (`test_quota_language_rejected_fail_closed`). Paraphrase gaps documented in **Finding B** (defense-in-depth, non-blocking). |
| D-024-R080 (graph is index not authority; stale data reported, never acted on as fact) | e8b21d1 | PASS | `WorkloadFeatures.graph_stale` → `classify_workload` returns `unknown-recon-first`/`graph_stale`; `GraphNeighborhood.stale` → `tier_signals` raises `SizingError("stale_graph")`. Proven by `test_stale_graph_is_reported_never_used`. |
| D-024-R081 (retain adaptive packet tiers/limits; never omit required evidence to fit) | e8b21d1 | PASS | `workload_sizing` genuinely **reuses** `context_pack_budget.select_tier`/`TierSignals` via a lazy import (no reimplemented tier table); `packet_plan` records omissions with justification and STOPs on unprovable sufficiency. `test_tier_selection_reuses_the_accepted_tiers_exactly`, `test_medium_without_justification_stays_withheld` pass; the drift-locked `test_context_pack.py` still green. |
| D-024-R100 (Phase B telemetry pipeline reuse) | e8b21d1 | PASS | `StartupObservation.to_record()` emits a valid `TelemetryRecord`; categories/labels legal (see Dimension 5). |

s5.5 / s6 / s13 / s16.2 prose anchors: the classifier's four classes, the Goldilocks decision vocabulary, the two-linked-records contract, the private-band ladder, and the smallest-complete packet plan all map faithfully to the directive text (details below).

## Steps independently executed

1. `git log/diff/rev-parse` — confirmed frozen content unchanged post-`e8b21d1` (control-plane only).
2. Read all five modules, the 686-line test pack, the report, and the real integration targets (`tools/repo_views.py:178-207`, `tools/context_pack_budget.py`, `tools/agent_supervisor/telemetry_records.py`, `telemetry_sdk.py::_evict`, `telemetry_hooks.py::_evict`).
3. `python -m pytest tools/test_agent_supervisor_bounded_contracts.py -q` → **53 passed**.
4. `python -m pytest` over `telemetry_core / subagent_telemetry / statusline_handler / rotation / scheduler / context_pack` → **305 passed** (no regression from the new modules; freeze-baseline duty).
5. `python tools/modularity_check.py --check` → **failures 0**, no warning on any new module (largest new module 587 lines < 600 warn line); `ruff check` over all six files → **All checks passed!**.
6. Reproduced the guard edge-case findings with single-line `python -c` probes (outputs quoted under Defects).

## Expected versus actual

**Dimension 1 — classification/decision precedence (correct).** `classify_workload` precedence is `declared_class → graph_stale → no-features → oversized → main → cohesive → unknown`, matching the directive intent, with a conservative "never optimistically cohesive" fallthrough (`cohesion_unproven`). `decide_spawn` precedence is `oversized→split-first`, `unknown→recon-first`, `main→stay-main`, cohesive `resume-healthy` / never-resume-confused / `fork` only clean+beneficial / bloated-parent-not-forked / else `spawn-new` — faithful to s6. The `single_small_edit + write_owner_count=2` case resolves to `oversized-split-at-seams` (oversized is checked before the main-session branch): **defensible and correct** — two write owners can never be one small edit, so splitting at seams is the safe outcome regardless of the "small" flag (confirmed from source lines 190-225; existing `test_oversized_cross_boundary_splits_at_seams` already pins write_owner_count=2 → OVERSIZED_SPLIT). Nit: `classify_workload`'s in-function numbered precedence docstring starts at "1. Stale graph…" and omits the `declared_class` short-circuit that actually runs first (rule 0).

**Dimension 3 — API/contract quality (solid).** `validate_assignment/validate_envelope/validate_pair` are complete for the required fields (ids, role↔scope↔lease consistency both directions, closed vocabularies for role/size_class/telemetry sources/confidence, `model_context_window` positive-int-or-None). `_digest` is deterministic (`json.dumps(asdict, sort_keys=True, ensure_ascii=True)`; nested dataclasses flatten via `asdict`; the explicit `to_dict` re-conversion of `health_bands`/`detectors` is redundant but harmless). Error-class convention (code+message ValueError subclass) is consistent per module; one cross-module quirk noted in Defects (minor).

**Dimension 4 — integration honesty (verified, matches real shapes).** Leaf-package claim holds: no new module imports index/graph machinery; the only `from tools import` is the lazy `context_pack_budget` inside `_budget()`. The `neighborhood_from_view` adapter **correctly matches** the real `repo_views.neighborhood_edges` output: out-edge rows carry key `"to"`, in-edge rows carry key `"from"` (plus `type/confidence/line`); the adapter iterates both `("from","to")` ends per edge (skipping the absent one) and derives importers from in-edge `"from"` only — no misparse. `in_edge_count` (full, untruncated) is used as `dependency_breadth`. Tier reuse is genuine (`select_tier` fields consumed directly). Minor: the adapter uses direct in-edge count as the breadth proxy, whereas the tier thresholds (`NORMAL_BREADTH_MAX=8`, `MEDIUM_BREADTH_MAX=40`) are described as calibrated on "importer closure + neighborhood" — a semantic proxy, advisory-only.

**Dimension 5 — startup_overhead (correct).** All six new measurement names (`startup_*`) are absent from `telemetry_records.MEASUREMENT_CATEGORY`, so they take the "unlisted-but-must-declare-a-category" path; each declares the legal category `cumulative` and a legal label (`estimated`/`unknown`). **No collision** with any listed name under a different category. `unknown`-never-zero honored (`Measurement.unknown("cumulative", …)` for unmeasured values). `OverheadLedger` eviction is oldest-first with a counted `evicted_observations`, bounded (`test_ledger_bounded_with_counted_eviction`). Minor: byte/count metrics (`packet_bytes`, `files_reopened`) are categorized `cumulative` and labeled `estimated` even though directly counted — the category vocabulary has only occupancy/cumulative/estimate and the label set has no generic "measured", so this is the conservative in-vocabulary choice, not a defect. Note `to_record()` fails closed if neither `now_utc_iso` nor `recorded_at_utc` is set (empty `timestamp_utc` raises) — honest, and every test passes a timestamp.

**Dimension 6 — eviction-order tests genuinely kill the pure-oldest-first mutant (verified).** For `SdkTaskTracker`, `_evict` is completed-first then oldest-first; `test_sdk_tracker_evicts_newer_completed_before_older_active` makes the *newer* task completed and the *older* active, so a pure-oldest-first mutant would evict `older-active` and fail the `high_water("older-active")==100` assertion. For `SubagentRegistry`, `_evict` evicts the oldest **closed** entry first; because a close event `pop`s and re-inserts the entry at the **end** of the `OrderedDict`, `test_subagent_registry_evicts_newer_closed_before_older_active` places the closed entry last and the active entry first — a pure-oldest-first mutant (`popitem(last=False)`) would drop `older-active` and fail. Both tests are red-on-mutant, green-on-actual. Correctly hosted here (sibling telemetry pack is outside this task's allowed paths; test-only, no production edit), placement recorded in the report §3.

**Dimension 7 — report accuracy (accurate).** SLOC table (238/587/218/239/260) equals the raw file line counts (`wc -l`), and 686 for the test pack — accurate, though "SLOC" is really raw line count (nit). "largest new module 587 SLOC, under the 600 warn line", "ruff … clean", "modularity_check … exit 0", "53 tests", leaf/no-graph-import claim, and lazy-`context_pack_budget` claim all reproduced true. "290 passed" for adjacent packs is in the same ballpark as my 305-pass run over a slightly different file set.

## Evidence paths

- `tools/agent_supervisor/workload_classifier.py`, `subagent_contracts.py`, `startup_overhead.py`, `spawn_decision.py`, `workload_sizing.py`
- `tools/test_agent_supervisor_bounded_contracts.py`
- `project-control/reports/M0-T090-bounded-contracts.md`
- Integration targets verified: `tools/repo_views.py` (lines 178-207), `tools/context_pack_budget.py`, `tools/agent_supervisor/telemetry_records.py`, `telemetry_sdk.py`, `telemetry_hooks.py`

## Human-style walkthrough findings

N/A — no UI. Shadow-only governance code (nothing spawns, resumes, stops, or messages an agent; R595 activation gate untouched). Records-with-reasons only, as claimed.

## Regression/security/provenance findings

No regression: 305 adjacent supervisor/context-pack tests pass; the drift-locked context-pack budget suite passes (tier reuse did not disturb the frozen budget primitives). No new dependency; no forbidden path touched; no actuation surface. Supervisor-freeze citation duty satisfied. Digests are deterministic; the guards fail closed. No secrets/credentials handled.

## Defects

**MAJOR-1 — Envelope-leak guard false-positives on the common English words "observe" and "land".** `assert_no_envelope_leak` (subagent_contracts.py:549-553) does a plain lowercased substring test `for band in HEALTH_BAND_NAMES[1:]: if band in lowered`. `HEALTH_BAND_NAMES[1:] = ('observe','prepare_to_land','land','emergency_stop')`. The author deliberately skipped index 0 ("normal") as "common English", but `observe` and `land` are equally common and were not skipped — and "land" matches inside `landing`, `island`, `England`, `landmark`, `flatland`, etc. Any legitimate worker prompt containing those words is rejected as `envelope_leak`. Reproduced:
```
FINDING A (bands matched in plain text):
 [('Fix the landing page', ['land']), ('Observe the failing test', ['observe']),
  ('Add island lookup', ['land']), ('Ship it now', [])]
```
So `render_worker_prompt` would raise `ContractError("envelope_leak")` for a "Fix the landing page…" or "Observe the failing test…" assignment. Direction is safe (over-block, never leak), but it breaks valid use. Recommend anchoring on the band **vocabulary tokens** (e.g., `prepare_to_land`, `emergency_stop`, whole-word/word-boundary match, or a controller-specific prefix) rather than substring-matching the bare words `observe`/`land`.

**MAJOR-2 — R045 quota guard misses paraphrased percentage/conserve pressure.** `_QUOTA_PATTERNS` catches numeric-token and the canonical phrasings, but paraphrases that R045 also prohibits slip through. Reproduced (`[]` = no pattern fired = accepted):
```
FINDING B (quota-guard MISSES):
 [('Keep it under 70 % if you can', []),        # space before % → percent_of_window needs %+context/budget/window/capacity
  ('Use about 70 percent of context', []),       # spelled 'percent' → no literal %
  ('Please save tokens', []),                     # 'save' ≠ 'conserve'; no number
  ('Be economical with the budget', [])]          # bare 'budget' unmatched
```
Notably the test pack's own INDEPENDENT scan (`_INDEPENDENT_QUOTA_SCAN`, lines 262-270) includes bare `budget` and `\d{1,3}\s*%` patterns — i.e. the test's notion of "quota language" is stricter than the production guard, which is exactly where these slip. Defense-in-depth (the controller authors the text; canonical phrasings are caught), so non-blocking, but before this contract machinery is ever activated the guard should also cover space-separated `%`, spelled "percent", and conserve synonyms (`save/economical/frugal/ration`-adjacent budget/context/token pressure).

**MINOR-3 — `numeric_strings` leak set omits space/spelled percent forms.** `HealthBands.numeric_strings()` yields `('0.5','50%','0.7','70%','0.85','85%','0.95','95%')`. A threshold written as `70 %` (space) or `70 percent` is not in the set and is not caught by MAJOR-2's guard either, so a band threshold could leak in those forms. (`0.70` is still caught, since `'0.7'` is a substring.) Reproduced: `'70 %' in numeric_strings() → False`.

**MINOR-4 — `_scopes_overlap` under-matches a root `/` lease.** `_normalized_lease(("/",))` strips to `""`; `_scopes_overlap(("/",),("tools/x.py",))` returns `None`, and `assert_grantable` would therefore grant a `tools/x.py` lease alongside a `/` lease. Nonsensical input (a root write-lease), safe to ignore in practice, but the guard silently fails to conflict on it (the empty-string return is also falsy).

**MINOR-5 — cross-module error-class/code inconsistency.** `StartupObservation.__post_init__` and `OverheadLedger.calibration` raise `WorkloadError("bad_declared_class", …)` for an invalid `size_class` (delegating to the workload vocabulary), while `validate_envelope` raises `ContractError("bad_size_class", …)` for the same concept. A caller catching `OverheadError` would miss the size-class error, and the code name differs across modules. Intentional (single vocabulary owner) and pinned by `test_observation_validation_fail_closed`, but worth a consistency note.

**NIT-6** — `classify_workload` docstring's numbered precedence omits the `declared_class` rule-0 short-circuit. **NIT-7** — report labels raw line counts as "SLOC". **NIT-8** — `subagent_contracts.py` (587 lines) cohesively bundles schema definition, validation guards, lease arbitration (`assert_grantable`/`_scopes_overlap`), and prompt rendering; under threshold and cohesive today, but the lease-arbitration and rendering responsibilities are the natural split lines if it grows past 600.

## Required rework

None blocking for this shadow-only G3. Recommended before any future R595 activation of the contract machinery: fix MAJOR-1 (word-boundary/vocabulary-token match for the leak guard) and broaden MAJOR-2/MINOR-3 (paraphrased percent/conserve pressure). MINOR-4/5 and the nits are optional polish.

## Reviewer conclusion

**PASS (with findings).** The core logic is correct and faithful to D-024 s5.5/s6/s13/s16.2 and R045/R080/R081/R100/R101: the structural classifier precedence, the Goldilocks spawn decision, the two-linked-records contract, private health bands, startup-overhead measurement/calibration, and graph-based sizing are well-designed, with genuine reuse of the accepted tier table and telemetry pipeline (leaf-package preserved), an adapter that actually matches the real `repo_views.neighborhood_edges` shape, deterministic digests, and eviction-order tests that provably kill a pure-oldest-first mutant. 53/53 new tests pass, 305 adjacent tests show no regression, ruff/modularity clean, and the supervisor-freeze D-024-R101 citation duty is met across packet, docstrings, and commit. The two major findings are guard-quality gaps in shadow-only code that err in the safe direction (leak guard over-blocks; quota guard is a backstop with canonical phrasings covered) and do not block acceptance, but should be corrected before this machinery is ever activated. Full 46-requirement directive compliance remains the independent `directive-compliance-verifier` pass, which the orchestrator records separately.
