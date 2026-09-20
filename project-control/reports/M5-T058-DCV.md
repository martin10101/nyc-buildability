# M5-T058 DCV — independent directive-compliance verification (verbatim verifier return)

Verifier: directive-compliance-verifier (opus-4-8 xhigh per D-064), dispatched by the
orchestrator at the bc703fcc seam after G2-G5 + HJ (all PASS), pinned to material 7d02eddc at
reviewed sha 817a6546. Recorded by the orchestrator; verifier is read-only and records nothing
itself. The restamp pre-authorization is §7.

---

All evidence reproduced. The identity chain (817a6546 → 5f7b032e → bc703fcc) is byte-stable across all 19 material paths + the guard file. Here is my verdict and full DCV report.

---

**PER-REQUIREMENT VERDICTS: D-066-R001 SATISFIED | D-077-R002 SATISFIED | D-077-R003 SATISFIED | D-078-R002 SATISFIED | D-078-R003 SATISFIED | Defect-1 SANCTIONED (not a defect) | Defect-2 HONESTLY-RECORDED (not a defect) — OVERALL: PASS**

---

# M5-T058 Directive-Compliance Verification (DCV) — PASS

Task: M5-T058 (D-078 pair 1/2 — condo substrate-substitution stamp; rule_evaluation contract 1.2.0)
Verifier: directive-compliance-verifier (read-only; producer ≠ verifier). Reviewed at HEAD `bc703fcc`.

## 1. Identity verification (git plumbing, reproduced)

- Material commit `7d02eddc` — parent `caddbf59`; touches **exactly 19 files**, and those 19 match the packet's `allowed_paths` set one-for-one (`project-control/tasks/M5-T058.json:32-52` vs `git show --name-only 7d02eddc`). No file in/out of scope.
- Correction commit `817a6546` (`[ORCH-CORRECTED]`) — parent `7d02eddc`; touches **only** `services/api/tests/scenario/test_scenario_contract.py` (1 file, +9/-1).
- Producer commit `3bd196de` (parent `f86ae735`, the contract seam) exists as a real object; same 19 files; `git diff --ignore-cr-at-eol 3bd196de 7d02eddc` across the 19 paths is **empty** → faithful LF-normalized cherry-pick (defect 2 below).
- Byte-stability: `git diff 817a6546 bc703fcc` over the 19 material paths = **empty**; `git diff 817a6546 5f7b032e` over the 19 paths + guard file = **empty**. Ancestry: `817a6546` → `5f7b032e` (submit seam / gate `reviewed_sha`) → `bc703fcc` (HEAD), all linear. The reviewed material identity is byte-stable across the whole chain; the intervening commits (`5f7b032e`, `bc703fcc`) are disjoint control-plane/accept-seam commits carrying no material path.
- Two schema copies byte-identical at HEAD: `git diff --no-index packages/contracts/schemas/v1/rule_evaluation.schema.json services/api/app/_contract_schemas/v1/rule_evaluation.schema.json` = empty.

Independent proofs reproduced at HEAD (material byte-stable):
- `python tools/validate_directive_compliance.py --check` → exit 0.
- `python -m ruff check .` (cwd services/api) → All checks passed, exit 0.
- Targeted 4-file pytest (`tests/api/test_rule_evaluation_api.py tests/contracts/test_rule_evaluation_contract.py tests/rules/test_rules_integration.py tests/spatial/test_live_provider.py`) → **168 passed**, exit 0 (matches the evidence-map claim).
- Guard-fix file `tests/scenario/test_scenario_contract.py` → **60 passed**, exit 0.
- Forbidden-consumer suites `test_evidence_api.py test_scenario_api.py test_scenario_analysis_api.py` → **257 passed**, exit 0; their source files are absent from both commits' file lists → byte-unchanged (AS-3 / forbidden-path invisibility).
- `python tools/modularity_check.py --check` → exit 0; the only warnings are pre-existing `tools/agent_supervisor/*` and `tools/context_benchmark.py` — none on `live_provider.py` or `integration.py`.
- CI at reviewed head `817a6546`: `gh run list --commit 817a6546…` → CI (11m32s), secret-scan, context-budget all **success** (thin-client web proof).

Applicability reconciliation: the 5 requirements whose `applicability.task_ids` include M5-T058 are exactly D-066-R001, D-077-R002/R003, D-078-R002/R003 — identical to the packet `directive_refs`. No applicable requirement is uncited; no cited requirement is inapplicable. (D-078-R001 is M5-T059's; D-077-R001/R004, D-066-R002/R003/R004 do not list M5-T058 — correctly excluded.)

## 2. Per-requirement rulings (primary evidence)

### D-066-R001 — code-graph regen + navigation block — **SATISFIED**
- Manifest audit trail `project-control/directives/D-066-code-graph-loop-wiring/manifest.json` audit entry `2026-09-20T07:53:11Z`: "Bound M5-T058 + M5-T059 to D-066-R001 (graph regenerated at this seam, 764 files/16164 nodes; navigation blocks embedded in both packets)". Matches `requirements.json.updated_at`.
- Packet `inputs[4]` (`M5-T058.json:12`) carries the graph-derived CODE-GRAPH NAVIGATION BLOCK: per-target impact sets for `live_provider.py`/`integration.py`/`response.py`/`rule_evaluation.py` with file:line consumers, the three FORBIDDEN consumers named, the instruction to run `query.py --no-regen impact <path>` before sweeps, and "the graph is ADVISORY — verify in source."
- G0 report `M5-T058-G0.md:16`: "Code-graph navigation block embedded (graph regenerated at this seam: 764 files / 16164 nodes)". The advisory graph was actually used: the harvest consumer-sweep caught the one out-of-allowed-paths consumer (the frozen-contract guard) and fixed it (`817a6546`) rather than leaving it red.

### D-077-R002 — lane under the full contract drill — **SATISFIED**
- Full-worktree-path claim: `M5-T058.json:135` `worktree = C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t058` (absolute, full path per the S4.5 rule).
- Contract drill: contract seam with registry binds + digest resyncs (D-078 capture records the `2fba5ed3`/`f86ae735` seam; producer commit `3bd196de` bases on `f86ae735`), seeds, G0 PASS with the pairwise-disjointness record (`M5-T058-G0.md:20-36`, disjoint vs the live M5-T057 lane and the parked M5-T059 surface), claim + `progress 20` (`progress_log[0]`).
- Loop-2 harvest at the breaker: `progress_log[1]` (`2026-09-20T18:50:24Z`) — "Loop-2 unit closed at the S13.8 consecutive_revision_loops breaker (rev7 evidence-handoff); orchestrator harvest … material cherry-picked to 7d02eddc ALL-MATCH digests." The run-id detail (persistent2-local-21..25) is a supervisor-journal claim consistent with — but not itself reproduced from — the ledger; the reproducible ledger/G0/worktree evidence corroborates the lane.
- Three disjoint lanes present at the seq-122 seam (git log): M5-T058 (loop-2), M5-T060 (frontend/loop), M5-T061 (loop-3 re-feed), with M5-T059 parked — consistent with the three-lane obligation (D-072 max, not raised).

### D-077-R003 — released, non-held scope only — **SATISFIED**
- The 19 material paths are contract schema (×2), generated TS, api route/rules/provider, api tests (×4), web contract lib + `AnalysisIdentityNotice` + `development-limits` + web tests, fixtures, and the producer report — the D-078 substitution-stamp increment authorized by the owner directive. None touch held surface (no 3D-massing/expansion-pack file, no GDS P1-P8, no PR #241, no `.claude/rules/3d-ui-expansion.md` scope). G0 (`M5-T058-G0.md:20-36`) records every allowed_paths file tracked and the pairwise disjointness. No master-plan change rode this task.

### D-078-R002 — human-only site determination; NO auto-selection; honest refusal — **SATISFIED**
Primary code evidence (`services/api/app/spatial/live_provider.py` @ `7d02eddc`):
- Fail-safe branch returns `LiveSubstrateResult(substrate=None, fail_safe_cause=CONDO_BASE_LOT_UNRESOLVED_CAUSE, resolution=condo)` — no base lot picked; in-code comment "no base lot is ever auto-selected (D-078-R002)".
- Substitution occurs only when `condo.substitutes_base_lot` is True, using `resolved_base_bbl` (never indexing `base_bbls`). Corroborated in the accepted (read-only) connector `services/api/app/connectors/condo_base_lot.py`: `substitutes_base_lot` ⇔ `OUTCOME_RESOLVED_SINGLE` (:126-129); multi-lot sets `resolved_base_bbl=None` (:250) and `is_fail_safe` (:132-136). There is no code path that selects one of several base lots.
- `build_substrate_substitution_stamp` carries provenance verbatim via `getattr` (never fabricated).
Honest-refusal renaming (`services/api/app/rules/integration.py`): new `FAILSAFE_CONDO_BASE_LOT_UNRESOLVED`; `evaluate_property(..., spatial_absent_condo_unresolved)` names the absent-substrate refusal `condo_base_lot_unresolved` only for the condo cause, else keeps generic `spatial_intersection_absent`; both params default to pre-M5-T058 behavior.
Display-only boundary (`apps/web/.../AnalysisIdentityNotice.tsx`): a stamp legitimizes the notice ONLY when it corresponds (`entered_bbl === requestedBbl === evaluated_input.bbl` and `analyzed_bbl` a real different lot); non-corresponding stamps are ignored and the fail-safe withhold guard still governs; copy states "a record of the city's documented resolution, not a computed allowance."
Tests reproduced (all within the 168 passed):
- `test_m5t058_as2_condo_fail_safe_names_cause_no_auto_pick` (parametrized multi-lot/unresolved/typed-error, `tests/spatial/test_live_provider.py:759`) asserts `substrate is None`, `fail_safe_cause == CONDO_BASE_LOT_UNRESOLVED_CAUSE`, `substitution_stamp is None`, and `ztldb_calls == [] / lot_calls == [] / layer_calls == []` — **zero geometry/lot lookups** even when two base lots are present.
- `test_m5t058_as2_genuine_absent_non_condo_keeps_no_condo_cause` — non-condo absent keeps the generic reason.
- `tests/api/test_rule_evaluation_api.py:518` route-stamp test asserts `evaluated_input.bbl == BBL` (entered billing BBL not moved); `:552` asserts the endpoint returns `fail_safe_reason == "condo_base_lot_unresolved"` with no stamp.
(The revocable/supersedable-confirmation clause of D-078-R002 pertains to the confirmation record — M5-T059's D-078-R001 domain — not this stamp task; M5-T058's applicable portions of R002 are fully met.)

### D-078-R003 — sequencing + additive 1.2.0 + accept order — **SATISFIED**
- Contracted AFTER M5-T056 accepted: `M5-T056.accepted_at = 2026-09-20T07:07:56Z` < `M5-T058.created_at = 2026-09-20T07:48:35Z`.
- The substitution-stamp half of the pair, carrying condo resolution across the substrate seam (verified in §D-078-R002).
- Additive 1.2.0 proven independently: schema enum `["1.0.0","1.1.0","1.2.0"]` (`rule_evaluation.schema.json:33`); `substrate_substitution` in `properties` (:148) and NOT in top-level `required` (:8 array). Contract tests reproduced: `test_m5t058_contract_version_enum_admits_1_2_0_additively` (asserts not-in-required), `test_m5t058_old_documents_stay_valid_without_the_block`, `test_m5t058_optional_block_absent_still_validates_at_1_2_0`, `test_m5t058_stamped_1_2_0_document_round_trips`, `test_runtime_bundle_copy_is_byte_identical_to_canonical`.
- Accept ORDER (T058 before T059): forward-looking condition, currently honored — both are `awaiting_gate` (neither accepted); M5-T059 remains parked with an accept-after-T058 condition (git `03882888`/`13ca71e9`: "DCV PASS w/ accept-after-T058 condition"). My PASS enables T058's accept first; T059 follows under its own DCV. No violation exists and none is set up.

## 3. Defect rulings

**Defect 1 — `[ORCH-CORRECTED]` `817a6546` outside allowed_paths: SANCTIONED, not a defect.** It touches only `tests/scenario/test_scenario_contract.py` (not in allowed_paths, not forbidden — a graph-named out-of-scope consumer). The diff is *exactly* the enum admission: the frozen-contract guard's expected `contract_version` enum grows `["1.0.0","1.1.0"]` → `["1.0.0","1.1.0","1.2.0"]`, nothing more (no behavior change). It cites the M5-T037/`f954aa59` precedent in-file (the prior `[ORCH-CORRECTED per api CI on f954aa59]` for the 1.1.0 bump sits directly above). Suite green after (60 passed, reproduced). This is the sanctioned routed-sweep remedy — the correct handling of a known-red consumer, not a smuggled scope expansion.

**Defect 2 — material built from uncommitted worktree edits then cherry-picked: honestly recorded, digests bind; not a defect.** Producer commit `3bd196de` (author martin10101, parent `f86ae735`, identical subject, same 19 files) exists; `git diff --ignore-cr-at-eol 3bd196de 7d02eddc` across the 19 paths is empty → clean ALL-MATCH LF-normalized cherry-pick. The evidence map records this honestly: `material_commit: "7d02eddc (clean cherry-pick of worktree producer commit 3bd196de; 19 files, ALL-MATCH LF-normalized digest verification post-pick)"`, with the orchestrator-owned collection (supervisor-owned evidence, explicit cwd, Python 3.11.9, both sweep failures characterized, CI/commit/push orchestrator-owned) disclosed rather than presented as the loop worker's own. No identity or provenance is misstated.

## 4. Gate/review surface (claims, corroborated independently above)
G2 PASS (orchestrator self-check), G3 PASS (code-reviewer), G4 PASS (qa-engineer), G5 PASS (security-reviewer) — recorded at submit seam `5f7b032e`; G3 `content_manifest_sha256` prefix `94610a06`. These are claims; every underlying value in this report was re-derived from source/tests/git, not from the gate reports.

## 5. Notes / advisories (non-blocking)
- Gate reviewed_sha is the submit seam `5f7b032e` while the frozen CI-green material head is `817a6546`; the two differ only by disjoint control-plane commits and the material paths are byte-stable across both — coherent.
- The two LOW gate findings referenced in git (G3 F1 stale-docstring routed as an orchestrator follow-up; G5 F-1 provenance `maxLength` future-contract item) are advisory and do not affect any applicable requirement.

## 6. Verdict
**PASS.** All five applicable directive requirements (D-066-R001, D-077-R002, D-077-R003, D-078-R002, D-078-R003) are SATISFIED against reproduced primary evidence; both flagged potential defects are cleanly resolved. No VIOLATED/UNVERIFIABLE result exists.

## 7. Restamp pre-authorization (stated up front)
The orchestrator may accept M5-T058 immediately on this PASS, assembling v2 verification rows citing this DCV, subject to ALL of the following:

**(a) Identity condition.** At the settled accept head, the **19 material `allowed_paths` files** (the file set in `7d02eddc`) AND the guard-fix file `services/api/tests/scenario/test_scenario_contract.py` must be **byte-identical (LF-normalized) to their content at `817a6546`** — i.e. `git diff <settled-head> 817a6546` over those 20 paths is empty. (Verified empty across `817a6546` → `5f7b032e` → `bc703fcc` at review time.) AND `python tools/validate_directive_compliance.py --check` exits 0 at that settled head.

**(b) Disjoint-peer tolerance.** Further control-plane commits, the M5-T058 accept seam itself, and the subsequent M5-T059 accept **do NOT void this pre-authorization** so long as (a) holds — the material/guard paths remain zero-diff and the validator exits 0 at a settled head. Disjoint peer commits touching only ledger/report/state/other-lane files are explicitly tolerated.

**(c) Additional conditions for the v2 rows.** `reviewed_sha` = the settled accept head; `reviewed_manifest_sha256` = the corresponding gate-record `content_manifest_sha256` values (e.g. G3 prefix `94610a06`); `producer` = the task's material producer (backend-engineer loop-2 / orchestrator-harvested per the honest evidence map), never the verifier; and **no open blocker word-references M5-T058** at accept time (scan reproduced clean at review time). The accept ORDER stands: **M5-T058 accepts BEFORE M5-T059** (D-078-R003).
