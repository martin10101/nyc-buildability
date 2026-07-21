# M2-T013 Producer Report (AOS §6)

**Task:** M2-T013 Production spatial-intersection engine with explicit uncertainty model
**Producer:** orchestrator (lead session; owner-authorized 2026-07-21 — no producer agent)
**Status requested:** `awaiting_gate`
**Branch:** `task/M2-T013-spatial` · **Base:** `f433c2c` (green main)

## What was built
A deterministic per-(lot,district) spatial-intersection engine emitting
facts-with-uncertainty, implementing the owner-approved policy advisory verbatim
(C1 linear-sum band, C2 conditional-only ZTLDB upgrade, C3 no sliver suppression,
C4 point+range shares) plus the coverage-family invariants. It consumes the accepted
MapPLUTO / zoning-features / ZTLDB connector domain models READ-ONLY and touches no
contract, profile, connector, or frontend code.

## Files changed (all additive, within allowed scope)
- `services/api/app/spatial/` (new module): `__init__.py`, `policy.py`, `models.py`,
  `geometry.py`, `coverage.py`, `crosscheck.py`, `engine.py`, `adapter.py`
- `services/api/tests/spatial/`: `__init__.py`, `test_spatial_intersection.py` (26 tests)
- `docs/research/M2-T013-accuracy-verification.md` (V1/V2 evidence)
- `project-control/reports/M2-T013-*` + G0/claim ledger transitions

## Contracts / schema changed
**NONE.** No `packages/contracts/**`, no `services/api/app/_contract_schemas/**`, no
`services/api/app/profile/**`. The coverage-audit status is an INTERNAL dataclass field,
deliberately not a published profile-contract field (SI-CF7). M2-T012 integrates later.

## Acceptance scenarios created (mapped to packet)
SI-S1 interior · SI-S2 split+ranges · SI-S3 near-boundary conditional-at-most ·
SI-S4 sliver_ambiguous + minor_portion · SI-S5 agreement/ordering/set-conflict+vintage ·
SI-S6/CF3 base gap→unassigned · SI-CF1 cross-family-not-overlap · SI-CF2 overlay-absence ·
SI-CF4 same-family overlap · SI-CF5/S9 no-Verified (value + source regex) · SI-CF6 no
renormalize · SI-CF7 internal audit + no-contract-import · SI-S7 degenerate band +
invalid lot · SI-S8 sensitivity fail-safe + documented/assumed provenance · SI-S10
reproducibility + pins + policy version · SI-S11 missing input · plus 2 real-fixture
(ZF03 nyzd R3-2, MPG06 holed lot) + 2 adapter tests.

## Commands run + results (local, exact pins shapely 2.0.7 / GEOS 3.11.4 / py3.11)
- `python -m pytest tests/spatial/ -q` → **26 passed**
- `python -m ruff check .` → **All checks passed!**
- `python -m pytest -q` (full API suite) → **564 passed** (26 new + 538 existing; no regression)

CI (authoritative, pytest 9.0.3 from the tooling lock) will re-run on push; SI-S12 =
full-suite green on both CI events is completed there and re-checked at the frozen SHA.

## Expected vs actual
All 26 scenarios: expected == actual. Key invariants proven:
- No `verified` value in any classification field or serialized record; no bare
  `"verified"` string literal in the module source (regex-provable).
- No uncertain case (near_boundary / sliver / data_conflict) collapses to a definitive
  assignment; ZTLDB agreement upgrades DISPLAY to `conditional` at most, never the class.
- Shares never renormalized (share_point == raw/lot_area; point shares not forced to 100%).
- Same inputs + same pins → byte-identical `as_dict()` across runs (incl. real holed lot).

## Source / API evidence (V1/V2)
`docs/research/M2-T013-accuracy-verification.md`: MapPLUTO metadata publishes NO
positional-accuracy figure (pypdf extract) → lot `assumed`; nyzd documented +/-20 ft;
nysp per-layer PDF has no extractable accuracy statement + www.nyc.gov mirrors 403 →
5 non-nyzd layers stay `assumed` (fail-safe active). Conservative direction preserved.

## Assumptions / defaults
- Compound band = 40 ft (20+20 linear sum) per C1; policy constants versioned as
  `M2-T013-spatial-policy-1` and stamped on every record.
- `assumed`-basis accuracies drive the 2×-band sensitivity fail-safe.
- ZTLDB `zoning_districts` (position 1 = greatest area) is the SET/ORDER authority;
  geometry is the only percentage source.

## Known limitations
- Per-layer `documented` upgrade for nyco/nysp_sd/nylh/nyzma deferred (per-layer PDFs
  not text-verifiable in-task; dataset-level +/-20 ft recorded as supporting evidence).
- Engine emits records only; profile integration + any contract field is M2-T012.
- `Verified` labeling and split-lot legal thresholds are M4 rule + G6 (out of scope).

## Security / provenance impact
Read-only offline computation; no network, secrets, storage, or auth. Every result
carries full accuracy provenance (source, basis, citation), policy version, geometry
pins, and source digests via `feature_ref`. No PII/logs.

## New risks / dependencies
None new. Acceptance remains blocked on the M0-T019 sequencing exception (implementation
only) + final integration reconcile with latest main.

## Recommended next tasks
Unchanged: M2-T012 (integrate these records into profile 1.4.0) and M4-T001 (rules
consume the uncertainty taxonomy) become eligible on M2-T013 acceptance.

## Report path
`project-control/reports/M2-T013-producer-report.md`
