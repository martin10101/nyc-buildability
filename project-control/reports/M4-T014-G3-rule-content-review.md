# G3 GATE REPORT — M4-T014 (R3/R4-series height/setback draft rule families)

> Preservation note: saved VERBATIM by the orchestrator from the reviewer's agent-return channel
> (transport entity-decoding only). Reviewer: independent code-reviewer agent (G3 walkthrough per
> the M4-T006 pilot precedent). A supplemental ruling on the 23-421(g) notes-provenance question
> was requested separately and is preserved as an addendum when returned.

**Reviewer:** independent G3 walkthrough reviewer (read-only; not the producer)
**Task:** M4-T014 — D-045:R001,R008,R009 + D-046:R001,R002; producer model per D-047
**Reviewed content identity:** material commit `c8d94f38`; CI authority run `34740497612` at `6fc8a878`
**Gate:** G3 (human-style rule-content walkthrough, source-first, per M4-T006 pilot precedent)

## VERDICT: PASS

No blocking corrections. Two ADVISORY notes (below), both already disclosed by the producer and appropriate to carry into G6. All six acceptance scenarios (S1–S6) plus the packet-correction parity check verify against source. The three new rulesets faithfully clone the accepted M4-T006 R5A pilot pattern and add the newer M4-T010 content-digest citation binding.

## Independent reproduction (this sandbox)

- `python -m pytest services/api/tests/rules/test_r3_r4_height.py -q` → **90 passed** (2.24s)
- `python -m pytest services/api/tests/rules -q` → **458 passed** (7.27s) — no regression
- `python tools/modularity_check.py --check` → **EXIT 0**
- `cmp -s` canonical vs bundle for all three snapshots → **PARITY OK** (byte-identical)
- `sha256(verbatim_excerpt) == content_digest_sha256` for all three snapshots → **OK**
- `git diff c8d94f38..6fc8a878 -- services/api docs/research/zr-snapshots` → **EMPTY** (CI run covers the exact frozen source state); `6fc8a878` is an ancestor of HEAD
- `git diff c8d94f38..HEAD --stat` → only control-plane + `docs/ARCHITECT_REVIEW_QUESTIONS.md` records (no source drift)

## Per-item findings (source-first)

**S1 — SOURCE FIDELITY: PASS.** Every numeric constraint traces verbatim to the snapshot text.
- §23-421 (`docs/research/zr-snapshots/v1/zr-23-421-r3-r4.snapshot.json:23`): "Perimeter walls … maximum height above the base plane of 25 feet … meet at a ridge line of 35 feet." Encoded as `perimeter_wall_height_ft=25` / `ridge_height_ft=35` (`r3_r4_pitched_height.rule.json:45-46`). Opening list `R1 R2 R3A R3X R3-1 R3-2 R4 R4-1 R4A R5A` (snapshot line 23/26); rule applicability scopes to the R3/R4 subset `R3A,R3X,R3-1,R3-2,R4,R4-1,R4A` (`r3_r4_pitched_height.rule.json:50`) — no variant added or dropped; R1/R2 (B-023) and R5A (pilot) correctly excluded.
- §23-422 (`zr-23-422-r3-r4.snapshot.json:23`): "R3-2 R4 … 35 feet" and "R4B … 25 feet." Encoded as flat `35` for `R3-2,R4` (`r3_2_r4_flat_height.rule.json:44,48`) and `25` for `R4B` (`r4b_height.rule.json:36,38`). Opening list `R3-2 R4 R4B R5 R5B R5D`; R5* left to the pilot. Variant×section asymmetry matches the snapshot matrix exactly.

**S2 — TYPED STRUCTURE: PASS.** Constraint kinds are separate typed outputs: pitched emits both `max_perimeter_wall_height` and `max_building_height` (`r3_r4_pitched_height.rule.json:40-42,59-62`); flat/R4B emit `max_building_height` only. The source states only maxima (no minima), so none were invented; no base-height/setback split fabricated where the source omits it. Units explicit (`"unit": "feet"`). DSL schema unchanged — no file under `services/api/app/rules/schemas` appears in `c8d94f38` (verified in the commit stat).

**S3 — HONEST GAPS: PASS.** Each gap names its section and states why deferred:
- Sloping-plane setback → exception `pitched_plane_setback_professional_review`, effect `documented_limitation`, cites §23-421 (`r3_r4_pitched_height.rule.json:65`); never a number.
- §23-424/425/426 + §23-44 overlay/special/historic → PRR exceptions (`r3_r4_pitched_height.rule.json:66-68`) + A2-gap limitations (`:81`); base-plane determination noted as a separate professional input (`:77`).
- `building_type` axis (values `attached`/`other`) is disclosed in the artifacts themselves (`r3_r4_pitched_height.rule.json:35`; `r3_2_r4_flat_height.rule.json:35,74`) as the engine's representation of §23-422's negative definition, NOT source-named, and fails closed to PRR when unavailable (proven by `test_nc4_*`). A qualified human reading the output is not misled: bare calls fail closed, and the numeric law is fully sourced. See ADVISORY-1.

**S4 — ISOLATION: PASS (90 tests genuinely bind).** Per-variant expectations differ where the source differs and cross-leakage is asserted:
- R4B 25 vs R3-2/R4 35 flat: `test_nc2_r4b_25_never_merges_with_r3_2_r4_35` (test file :452-472).
- Cross-variant isolation: `test_nc1_*` (:358-399) — pitched not-applicable to R5A/R4B/R1/R2/R5/R5B/R5D/R3; flat scoped to R3-2/R4; R4B scoped to R4B.
- Cross-section isolation (flat value never satisfies a pitched constraint and vice versa): `test_nc2_*` (:406-449).
- Negative controls: wrong district → not-applicable; R1/R2 absent (parametrized in `test_nc1`); unknown variant → not-applicable, never "nearest" (`:393`).
- Value binding (mutation-style): AS-1 asserts exact `{25.0}`, `{35.0}`, `{25.0/35.0}` output sets, so a swapped constant would fail.

**S5 — DRAFT POSTURE: PASS.** Every rule `status: needs_review` with `qualified_human_approval: pending` (`test_as5_*`). Snapshots carry `extraction_status: extracted_draft` and `raw_html_verified: false` with a `verification_required` note in the artifacts themselves (all three snapshots, `source` block) — producer disclosure 1 lives in the artifacts, not only the report. Banned-language grep over all three rulesets returned no `buildable envelope`/`feasible`/`massing`/`compliant`/`compliance determination`; the only "buildable" occurrences are the negated disclaimer "not a buildable-envelope result." See ADVISORY-2.

**S6 — CI/REGRESSION: PASS.** Stored CI evidence (`project-control/reports/M4-T014-ci-evidence.md`) reconciles with the diff: run `34740497612` at `6fc8a878`, 18/18 jobs green, `api (ruff+pytest)` = executable authority for the rules suite; 458 passed. Material identity independently confirmed empty (above). No run on this material ever FAILED (surviving run green; predecessors cancelled by shared-checkout pushes, not failures).

**Packet-correction / scope: PASS.** Canonical (`docs/research/zr-snapshots/v1/`) and bundle (`services/api/app/_zr_snapshots/v1/`) copies are byte-identical for all three snapshots. `docs/research/zr-snapshots` is present in `allowed_paths` (M4-T014.json:32) per the recorded pre-capture correction. Nothing landed outside allowed_paths for the producer: material-commit writes are the 3 rulesets, 3 canonical + 3 bundle snapshots, 1 test, 2 reports, and the producer's own `.claude/agent-memory/rules-engineer/*`. The `project-control/state.json` and `tasks/M4-T014.json` edits bundled in `c8d94f38` are orchestrator control-plane records (producer left work uncommitted), and the `docs/ARCHITECT_REVIEW_QUESTIONS.md` edits after `c8d94f38` are a peer session's owner-research records outside services/api — neither is producer scope creep. Engine/evaluator untouched (forbidden paths clean).

## Advisory corrections (non-blocking; carry to G6)

- **ADVISORY-1 (G6 legal attention):** the `building_type` modeling axis (`attached`/`other` ⇒ "residences not subject to §23-421") is engine-invented, not source-named. It is correctly disclosed (rule descriptions/inputs/limitations + producer disclosure 2) and fails closed to PRR, so it is not a defect — but the mapping of the §23-422 negative definition onto this enum is exactly the modeling choice a qualified zoning professional should confirm at G6 before publication.
- **ADVISORY-2 (test strength, cosmetic):** `test_as5_no_buildable_or_compliance_language_in_rulesets` (test file :315-326) bans the space form "buildable envelope"; the rulesets use the hyphenated "buildable-envelope" only inside negated disclaimers. Usage is honest and the test passes; the banned list could optionally include the hyphenated form for future-proofing. No action required for this gate.

**G3 verdict: PASS.** No blocking corrections. ADVISORY-1 and ADVISORY-2 are non-blocking and appropriate for G6/future maintenance. The independent directive-compliance verification of D-045 (R001/R008/R009) and D-046 (R001/R002) against `verification.json` remains the orchestrator/verifier's separate pass and is not re-adjudicated here.
