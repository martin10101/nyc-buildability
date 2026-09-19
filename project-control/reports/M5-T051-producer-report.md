# M5-T051 producer report — phase B1 deterministic proposal-derivation

One concise evidence pass (reference + line anchors; no long verbatim blocks). Directives
bound: D-066-R001, D-076-R001, D-076-R002.

## Implementation (what landed, where)

- **`services/api/app/scenario/derivation.py`** (new) — pure, typed, bounded derivation of
  proposal FACTS from an already-validated `proposed_massing` block plus a CALLER-SUPPLIED
  `LotContext`. Public entry `derive_proposal` (`derivation.py:685`). Stdlib only
  (`math`, `hashlib`, `json`) + the B0 validator `validate_proposed_massing` re-called as
  defense in depth (`derivation.py:704`). No network / connector / file I/O; every input is
  a parameter.
  - footprint area — shoelace on the base 2263 ring (`_derive_footprint`, `derivation.py:421`);
  - lot coverage — footprint / caller lot area, lot-area provenance carried through
    (`_derive_coverage`, `derivation.py:435`);
  - per-level areas — own outline where present else base, choice recorded EXPLICITLY on each
    record (`_derive_level_areas`, `derivation.py:462`);
  - gross floor-area TREATMENT — declared inclusions/exclusions vocabulary, enum
    `GrossFloorAreaTreatment.PER_LEVEL_GROSS_NO_DEDUCTIONS`; never "zoning floor area"
    (`derivation.py:85`, `_derive_gross` `derivation.py:506`);
  - wall setbacks — min segment distance to caller lot lines, and to a caller-attested street
    line where supplied, else a typed honest ABSENCE (`_derive_wall_setbacks` `derivation.py:661`,
    `_street_line_setback` `derivation.py:617`);
  - per-level + cumulative height (`_derive_heights`, `derivation.py:532`).
  - Every value returned in a frozen `EvidenceRecord` (`derivation.py:138`) carrying
    value/unit/method/input_ids/detail and the literal `source_class = "proposed_derivation"`
    (`SOURCE_CLASS`, `derivation.py:79`) — a PROVIDED value, never an allowance.
  - Fail-closed: `ProposalDerivationError` names the exact dotted field on any geometric
    degeneracy (`_area_or_refuse` `derivation.py:402`, `_wall_segment` `derivation.py:568`,
    non-finite/non-positive lot area `derivation.py:438`).

- **`services/api/app/scenario/proposal.py`** — DB-034(c) closure ONLY (B0 semantics otherwise
  byte-preserved): a wall whose two distinct indices collapse to the same ring point once the
  repeated closing vertex is folded (`index % ring_length`) is refused typed at
  `proposed_massing.exterior_walls[i]` (`proposal.py:408`–`427`).

## Tests / fixtures

- **`tests/scenario/test_scenario_derivation.py`** (new) — property + hand-computed-fixture pack
  over `fixtures/derivation/**`. Fixtures are HAND-COMPUTED with arithmetic shown in
  `fixtures/derivation/README.md`; expectations are never produced by running the module
  (`_derive_fixture` loads data + `expected` from JSON, `test_scenario_derivation.py:81`).
- Fixtures: `rectangle_100x80.json` (8000 sf / 0.5 / 24000 gross / 32 ft / 15-ft frame /
  40-ft south street), `l_shape_multilevel.json` (concave shoelace 12800→6400 / own upper
  1600 / 11200 gross / 45 ft / 10-ft south lot line), `wall_setback.json` (1500 sf /
  front 18-ft lot + 25-ft derived street / rear 48-ft lot + typed absence).
- **`tests/scenario/test_scenario_proposal.py`** — additive: DB-034(c) closing-vertex wall
  refusal both directions (`:604`, `:620`) + the not-degenerate control (`:633`); DB-034(e)
  collinear/180°-reversal outline binds the `cross==0 and dot<0` branch of `_ring_is_simple`
  (`:650`).

## Verification (documented commands; offline; this run)

- `python -m ruff check .` (cwd `services/api`) → **All checks passed!**
- `python -m pytest tests/scenario -q` (cwd `services/api`) → **568 passed** (3.75s)
- `python -m pytest tests/api -q` (cwd `services/api`) → **439 passed** (15.14s)
- `python tools/modularity_check.py --check` (repo root) → **failures 0**; 20 warnings, none
  on the files in this packet (`derivation.py` below the warn tier).

## Acceptance-scenario coverage

AS-1 rectangle (`test_rectangle_is_the_primary_as1_case`); AS-2 concave + multi-level
(`test_l_shape_concavity_area_exact`); AS-3 setbacks incl. derived-street + typed absence
(`test_street_setback_derived_carries_attestation_identifiers`,
`test_street_setback_absent_is_typed_honest_absence`); AS-4 facts-not-allowances
(`test_no_allowance_language_in_output`, `test_source_class_literal_is_proposed_derivation`);
AS-5 invariance (`test_vertex_order_rotation_preserves_area`,
`test_translation_preserves_area_coverage_and_setbacks`); AS-6 fail-closed (collapsed outline,
DB-034(c) wall, non-finite/zero lot area, DB-034(e) collinear); AS-7 purity (stdlib-only
imports; parameters only); AS-8 proof (the four commands above).

## Discovery / out-of-scope (D-069)

- Fixed one in-scope lint miss left in the working tree: `test_scenario_derivation.py:164`
  E501 (>100 chars) → split to a local `treatment` binding; ruff now clean.
- No forbidden path touched: `spatial/`, `connectors/`, `rules/`, `contract.py`, `api/`
  untouched — lot geometry and street attestation arrive as caller parameters only.
- DB-034(a)/(b) (global vertex budget; string ceilings) remain for the B3/route wiring packet;
  not fixed here (out of this packet's named scope).
