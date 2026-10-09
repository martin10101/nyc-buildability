# M5-T034 DCV verification (verbatim reviewer return; directive-compliance-verifier, read-only, frozen 22724f02)

Saved verbatim by the orchestrator.

---

# DCV report — M5-T034 (B7 wide-street FAR wiring)

**Frozen HEAD:** `22724f02171826cac711270b67309327bb540e7c` (confirmed via `git rev-parse HEAD`).
**Verdict: PASS** (one required evidence-record correction; no requirement VIOLATED/UNVERIFIABLE).

All four cited requirements independently SATISFIED at the frozen head. Every test suite reproduced GREEN from the `services/api` cwd by me (not taken from the producer's claims).

## Reproduced executable evidence (my runs, services/api cwd)
- `pytest tests/rules/test_wide_street_wiring.py` → **20 passed**
- `pytest tests/connectors/test_wide_street_buffer_engine.py` → **49 passed**
- `pytest tests/rules/test_rules_integration.py` → **46 passed**
- `pytest tests/api/test_rule_evaluation_api.py` → **35 passed**
- `pytest tests/rules` → **599 passed**
- `ruff check .` → All checks passed; `tools/modularity_check.py --check` → exit 0 (failures 0); `validate_directive_compliance.py --check` → exit 0.

## Per-requirement verdicts

**D-045-R002 (A2 geometry-dependent rule mechanics) — SATISFIED.**
Primary evidence: `services/api/app/rules/wide_street_wiring.py` is the first production consumer, importing `dcm_street_width_policy` + `wide_street_buffer_engine` read-only through public interfaces (L73-88), routing keyed off `PolicyDecision.decision_state` never `routed_to` (L331-356, `ROUTED_TO_NOT_USED_NOTICE` L137-142). No guessed geometry: every typed engine failure / non-{wide,narrow} outcome → `professional_review_required` with `far_row=none` (L338-356, 466-480). FAR values never invented — `integration.py select_conditional_far_row` (L476-536) reads the rule's own byte-checked `standard_far_by_district`/`wide_street_far_by_district` params; `evaluate_property` fold is additive (L755-790). B4 gap closed in the engine: `InputBoundsError`/`input_bounds_exceeded` (L339-346), `MAX_WIDE_SEGMENTS=512`, `MAX_VERTICES_PER_PATH=5000`, `EXTENT_ABS_MAX_FT=5e6` (L245-247), checks wired lot-extent L754, segment-count L816, per-path vertex L826 (before linework), linework-extent L828 (before buffer). D-051 direction validated for these rows: `FALLBACK_DIRECTION_NOTICE` (wiring L144-152) + AS-5 test `test_fallback_direction_lower_far_is_conservative_for_these_rows` (passes).

**D-045-R008 (sequencing — one reviewed family, bounded task) — SATISFIED.**
Single bounded packet M5-T034, 9 files in `allowed_paths`, cites `D-045-R002`; normal G0–G5 gate set. Out-of-scope items deferred as tracked follow-ups in `docs/DISCOVERY_BACKLOG.md`: DB-010 (named-street override), DB-011 (EC-4), DB-013/014/015 — reproduced (grep). No merge of multiple rule families.

**D-045-R009 (preservation / DRAFT-until-G6, no verified/published) — SATISFIED** (with required correction below).
`rule.json` status `needs_review` (L7); `release.independent_review`/`qualified_human_approval` = pending (L13-14) — unchanged. FAR parameter *values* and the zr-23-22 `content_digest_sha256` (L23) byte-stable. Wiring carries `DRAFT_LABEL_NOTICE` on every determination (L130-135, `_determination` L282) + D-052 provenance quintuple (`_provenance` L210-223). AS-6 tests `test_provenance_quintuple_present_*`, `test_draft_marker_present_and_never_claims_verified_or_published` pass. No dependency/lockfile file touched (verified). No published/verified language introduced — new prose reinforces "NOT a Verified determination … awaiting G6".

**D-066-R001 (code-graph navigation block + query.py citation) — SATISFIED.**
Packet input carries the seam-regenerated navigation block (`M5-T034.json` inputs L12: 728 files/15271 nodes/6762 edges; producers, rule target, evaluator seam, first-consumer fact) and instructs `python tools/code_graph/query.py --no-regen impact <path>` (2 occurrences). Graph advisory discipline honored: producer report §7 states the disjoint-applicability conclusion was verified in source, not from the graph.

## Deviation ruling (item a)
The flagged framing is itself **inaccurate**: `rule.json` is **NOT byte-unchanged** — the material commit `ae478563` changed it **+4/-4** (prose in `description`, the `wide_street_far_by_district` note, the `conditional_alternative` note, and one `limitations` entry). What is true and load-bearing: the rule's **DSL/status/values/citations are unchanged**, and the wide-street determination is consumed at the **evaluator seam** (`integration.py`), not by a DSL primitive (the DSL has none). Ruling:
- **D-045-R009 preservation: SATISFIED** — but *not* on the "did not touch the rule file" rationale (the file's prose was edited). It holds because the preservation obligation is DRAFT/needs_review lifecycle + no verified/published declarations, both independently confirmed; a draft rule file is not required to be byte-frozen, and the edits are documentation-only and reinforce draft status. Not "strengthened by not touching the file."
- **D-045-R002 mechanics via the seam: MET** — the directive mandates a geometry-dependent mechanic shipping with its inputs, no guessed geometry, honest not-assessed on missing input; the evaluator-seam architecture satisfies all of these and never invents a FAR. The deviation from packet output line #3 ("rule.json updated to consume the real determination") is acceptable and violates no requirement.

## Evidence-map accuracy
Accurate except one material misstatement, repeated in three places, which the orchestrator should correct before recording:
- `M5-T034-evidence-map.json` D-045-R009 row: "rule.json **byte-unchanged**" — **FALSE** (+4/-4 prose diff).
- `M5-T034-orchestrator-seam-evidence.md`: "`…rule.json` is **byte-UNCHANGED**" — FALSE.
- `M5-T034-producer-report.md` §3.3: "rule.json is **NOT modified**" — FALSE.
Required correction (evidence-record prose only, outside material identity — moves no material SHA): replace "byte-unchanged/NOT modified" with "prose-only edits (description/notes/limitations); status `needs_review`, FAR values, and citation digest byte-stable; determination consumed at the evaluator seam." All other evidence-map claims reproduced true (counts, own-module ruling, bounds constants, D-051 notice, deferrals).

## Prohibited-action evidence
Nothing merged/accepted/deployed/installed: material `ae478563` and integration `54e1da7a` are on `candidate/D-024-mrl-option-b` + `task/M5-T034-…`, **NOT on origin/main**; packet `status: awaiting_gate` (not accepted); no dependency/lockfile change; no purchase/dispatch artifact.

## Restamp pre-authorization (answer up front)
**AUTHORIZED** to carry this verification to a target head **iff** `git diff --name-only 22724f02 <target>` returns **only `project-control/**` paths** — zero `services/**` and zero `docs/**` (I examined `docs/DISCOVERY_BACKLOG.md`, so any `docs/**` change voids the carry). Permitted target content: gate records, `verification.json` rows, `state.json`/task files, and the evidence-record wording correction above (all under `project-control/**`). Any change outside `project-control/**` requires re-review.
