---
name: zr-height-setback-extraction-mechanism
description: Reusable mechanism for adding ZR draft rule families - snapshot canonical+bundle sync, digest binding, DSL patterns, building_type fail-closed, district-grouping precedent, sandbox network access
metadata:
  type: reference
---

How to add a `needs_review` ZR height/setback (or FAR) rule family. Confirmed on M4-T014.

## Snapshots (two locations, kept byte-identical)
- CANONICAL source of authority: `docs/research/zr-snapshots/v1/*.snapshot.json`.
- Runtime bundle (packaged, loaded via importlib.resources): `services/api/app/_zr_snapshots/v1/`.
- Write the canonical file, then run `python services/api/scripts/sync_zr_snapshots.py`
  (write) to copy into the bundle. `--check` must EXIT 0. CI guard `test_zr_snapshot_bundle`
  fails closed on any drift / orphan / missing membership. **Trap:** a packet whose
  `allowed_paths` lists only the bundle path still REQUIRES writing the canonical file
  (docs/research is not forbidden) or the bundle guard fails - disclose this scope note.
- `content_digest_sha256` MUST equal `sha256(verbatim_excerpt.encode("utf-8"))` (the digest
  guards ONLY `verbatim_excerpt`, not the whole file; `table`/`district_enumeration` are
  extra structured fields outside the digest). `SnapshotStore.load()` raises on mismatch.

## Rule DSL (schema `services/api/app/rules/schemas/v1/rule_definition.schema.json`)
- Loader `dsl.build_rule_definition`: JSON-Schema + lifecycle (`status` never > needs_review)
  + ref checks. Every citation `snapshot_id` and parameter `citation_ref` must resolve; an
  optional citation `content_digest_sha256` (64 lowercase hex) is fail-closed-bound to the
  snapshot at load (M4-T010) - include it to bind transcription provenance.
- Ops: computation `identity/add/subtract/multiply/divide/min/max/round/clamp`; predicate
  `equals/in_set/exists/compare` with `all/any/not`; exception effects
  `conditional_alternative|professional_review_required|documented_limitation`.
- Evaluator coverage decisions (`app/rules/evaluator.py`): missing REQUIRED input →
  `professional_review_required` + `missing_critical` (even if it gates applicability);
  wrong district / non-matching applicability with all required inputs present →
  `not_applicable`; before `effective_from` → `not_applicable`; applicable draft →
  `conditional`; exceptions/geometry only DOWNGRADE. DF-6: an OMITTED optional modifier flag
  is UNKNOWN → if an exception condition reads it and would skip, escalates to PRR (tests must
  pass explicit `overlay_present/special_district_present/historic_district=False` to get a
  confident `conditional`).

## Patterns proven
- **building_type** fail-closed axis (no canonical property_profile field ⇒ PRR in practice):
  source-named pitched forms `["detached","semi_detached","zero_lot_line"]` (verbatim in
  §23-421). For a NEGATIVE definition ("residences not subject to §23-421"), use engine axis
  values `["attached","other"]` and DISCLOSE they are not source-named; keep both pitched and
  flat rules gating on the SAME building_type axis with DISJOINT enum subsets so they are
  mutually exclusive (no same-family conflict for a dual-section district).
- **District grouping precedent:** group multiple districts under one rule via
  `in_set` when the source gives them ONE value (accepted `r1_r2_r3_residential_far`,
  `r3_r4_pitched_height`); split into separate rules where VALUES differ (R5 pilot).
- **Family isolation:** a NEW family name (e.g. `residential_height_setback_r3_r4`) keeps the
  R5 pilot's hardcoded `family_coverage` membership tests green. `integration.evaluate_property`
  only targets `residential_far`, so new height families don't perturb integration tests.
- Typed A2 gaps (D-045-R008): sloping-plane setback → `documented_limitation`; overlay/special/
  historic → PRR exceptions; qualifying-site/large-site increases → limitations. Only genuinely
  numeric caps become numeric constraints, min/max separate, units explicit.

## Local verification
`python -m pytest services/api/tests/rules` and `python tools/modularity_check.py --check`
(EXIT 0). Rules suite COLLECTS on 3.11 in this sandbox (no PEP 695 block); CI `api` job is the
authority. Sandbox HAS outbound network: `curl -A "Mozilla/5.0" https://zr.planning.nyc.gov/...`
returns 200; legal text in the `field--name-body` container, district separators are U+00A0.
See [[zr-r3-r4-height-setback-source-facts]] for a worked example.
