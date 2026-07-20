# M2-T009 - G3 Independent Walkthrough (code-reviewer)

*(Orchestrator note: saved verbatim from the reviewer's agent-return channel per the report-preservation rule; transport entity-decoding only.)*

## 1. Scope and method

- Target: committed state at `6f0992f` on `task/M2-T009-mappluto-geometry` in the clean worktree `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M2-T009` (git status clean before and after review; only the task commit atop control merge `0ec0ff7`).
- Started from acceptance criteria: full read of `project-control/tasks/M2-T009.json` (safeguards 1-6, GEO-S1..S12, allowed/forbidden paths, risks), G3 duties in `docs/GATES_AND_CHECKPOINTS.md`, and the connector + geospatial scenario packs in `docs/ACCEPTANCE_SCENARIO_STANDARD.md`. Producer report read LAST.
- Full reads: `services/api/app/connectors/mappluto_geometry_arcgis.py` (all 2,169 lines), `services/api/tests/connectors/test_mappluto_geometry_arcgis.py` (all 1,271 lines), MANIFEST.json head + structure, fixture spot-checks (MPG01/02/03/04/05 manifest entries; MPG80, MPG96 file bodies), `build_fixture_pack.py` structure, pyproject/requirements diffs, registry-draft diff.
- Evidence RE-RUN from the worktree (my sandbox: Windows, Python 3.11.9, shapely 2.0.7 / GEOS 3.11.4 already installed — the task pin was satisfiable, so I executed rather than relying on stored evidence).

## 2. Findings

### Re-run evidence (exact commands, from `services/api` in the worktree)

| Command | Result |
|---|---|
| `python -m pytest tests/connectors/test_mappluto_geometry_arcgis.py -q` | **80 passed in 0.63s** |
| `python -m pytest tests -q` | **522 passed in 4.46s** (matches expected 522) |
| `python -m ruff check .` | **All checks passed!** |
| `python -c "import shapely; ..."` | `shapely 2.0.7 3.11.4` (matches PINNED constants) |

Notable: my re-run is on Windows/py3.11.9 while CI ran Linux/py3.12 — all six hardcoded digest anchors (SQUARE, ESB, HOLES, MULTI, BOWTIE-repaired, plus the original-digest anchor) reproduced byte-identically on BOTH platforms. That is a stronger cross-platform determinism proof than either environment alone.

### Scenario-by-scenario walkthrough (as a downstream service consumer)

- **GEO-S1 (single lot / identifier validation):** Non-vacuous. `normalize_bbl` runs before any I/O (`test_s10_invalid_bbl...` asserts `transport.calls == []`); BBL attribute equality mandatory (`ResultMismatchError`, MPG97); BoroCode/Block/Lot component disagreement surfaces via `check_identifier_consistency` with `review_required=True` and verbatim both values (MPG98). Provenance stamped: request URL byte-identical to the fixture capture URL, metadata URL, retrieval timestamp from injected clock, source edit timestamp, CRS, three digests. `REQUIRED_FIELDS` constants cross-checked against the live 103-field capture in-test (transcription guard).
- **GEO-S2 (multipolygon/holes canonical ordering):** Real live fixtures (Governors Island holed polygon MPG06; a genuine two-ring Queens multipolygon MPG07 — found live, not synthetic). Ring rotation and member reordering leave the normalized digest unchanged while original digests differ — the raw/original/normalized separation is demonstrated, not just asserted.
- **GEO-S3 (zero/one/multiple):** All three typed. Multiple = `review_required=True`, `attributes is None`, `geometry is None`, ALL features preserved — no first-pick, verified in test. The count==cap boundary is exercised: a full 10-feature page with `exceededTransferLimit=true` forces `multiple_features` with an explicit "more exist beyond" note.
- **GEO-S4 (condo semantics):** The hardest-to-fake case is LIVE-proven: billing lot 1000157501 returns the complex polygon (CondoNo 1025) while unit lot 1000151001 on the same block returns an empty features array captured live (MPG05). The "unit lot with a polygon" contradiction case is synthetic, flagged review-required plus a drift signal — never trusted. No per-unit-polygon claim exists anywhere.
- **GEO-S5 (validity taxonomy):** Nine parameterized fixtures plus null-key and NaN cases, each mapping to a distinct typed state and finding code; invalid/review states provably yield `normalized_digest is None` and `canonical_geometry is None` (nothing enters intersection). All synthetic fixtures labeled in-file (`capture_method: "SYNTHETIC: ..."`) and manifest-verified by a dedicated test.
- **GEO-S6 (no silent repair):** Original digest computed unconditionally before any pipeline step (line 789) and preserved in every terminal state. Repairs record method + detail; `shapely_make_valid` repairs additionally record shapely/GEOS versions and area before/after. Uncharacterizable cases (all-CCW orientation, hole outside every shell, unknown GEOS pathology, non-polygonal/empty make_valid output, >1% area drift) are `review_required` — verified for the two hardest fixtures that `shapely_make_valid` is NOT among the applied methods. Result-level note states repaired geometry "is NOT the untouched official source."
- **GEO-S7 (digest determinism):** Canonical spec is explicit (ordering for rings/holes/members, half-even 0.01 ft quantization, two-decimal string coordinates, negative-zero normalization, open cycles, lexicographic pivot rotation, CCW-exterior/CW-hole); WKB/WKT deliberately not used and asserted so. Hardcoded fixture-independent anchor + four fixture anchors; versions asserted in-test; digest recomputable from the published canonical form.
- **GEO-S8 (CRS safety):** Single gate `require_authoritative_crs` runs first in `analyze_lot_geometry` and `compute_area_sq_ft`; metadata CRS validated before any lot query; query-envelope CRS validated before geometry interpretation (typed `wrong_crs`, MPG90/MPG99). Negative proof present: 4326, 3857, `{}`, and `None` all refused by the only area function. The documented transformation test reproduces the official `Shape__Area` (97,113.6875 sq ft, ESB) within 1e-6 relative; divergence surfaces as a note, never reconciled.
- **GEO-S9 (spatial vs REAL M2-T007 fixtures):** Uses the actual accepted ZF03 R3-2 polygon fixture and the real holed lot. Tolerance named (20.0 ft) with the source-accuracy basis string in every classification output. Boundary-centered lot → `boundary_uncertain`, firm assertion. Split requires firmly-inside AND firmly-outside beyond the band. Hole interaction: deep-in-hole = outside, covering = split, hole-boundary = uncertain. Repeated-run and repaired-geometry classification reproducibility proven. The eroded-empty edge (small reference fully consumed by erosion) falls through to `boundary_uncertain` — safe direction.
- **GEO-S10 (allowlist/resilience):** All URLs originate from the pinned official root; callers cannot supply hosts, where clauses, fields, or paging; invalid BBL and non-canonical forms refused with zero transport calls. Timeout/429+Retry-After/network/5xx/budget/circuit all typed via M1-T009 primitives; ArcGIS error-object-with-HTTP-200 is a typed upstream error; two malformed shapes are typed `malformed_response` — never an empty valid result. Ten error types pairwise distinct; payloads carry correlation_id + source_id, no stack traces; keyless service, wider secret-needle scan over all fixtures, manifest, and every outgoing request.
- **GEO-S11 (two-staleness):** Full owner quartet: old-source+fresh (staleness None), current+fresh, old+cache-hit (stale False), old+LKG (stale True, upstream_error_type recorded, "two-staleness rule" note). `staleness` is stamped only by the resilient client; `source_data_last_edited` never influences it.
- **GEO-S12 (regression):** Full suite 522 green re-run; read-only-reuse guard test; metadata injection avoids refetch; correlation id minted when absent.

### Clarity, recovery, hidden defaults

Error payloads are actionable (typed `error_type`, message explaining the refusal rationale, URL, correlation id); untrusted upstream text is repr-sanitized via `_safe_text`/`_safe_field_name`. No result-changing hidden defaults found: transport knobs (timeout/attempts/backoff) do not alter data; `tolerance_ft` is overridable but echoed in every classification output with its basis. `condo.note` is None for standard non-condo lots — explicit, not omitted.

### Owner-PC storage

Fixture pack measured: 32 files, **556 KB** on disk (includes MANIFEST.json and build_fixture_pack.py) — consistent with the ~500 KB claim; largest file 115 KB (real multipolygon). No downloads, no litter: worktree `git status` clean after my full test runs. Shapely was already installed in my sandbox (no new install; producer disclosed ~2.4 MB wheel + numpy as the local footprint — within budget).

### Producer report and disclosed deviations (judged last)

Report matches the observed diff exactly (7 files, no forbidden-path touches; pluto_soda/bbl reused via import only). The three disclosed deviations are accurately characterized: (1) exact `shapely==2.0.7` pin vs the range convention — justified and packet-directed, since digests are GEOS-build-dependent, with in-test version assertions and re-pin instructions in both dependency files; (2) py3.11 sandbox vs 3.12 CI — pre-existing repo condition, CI green at 3.12 is authoritative and my re-run adds a second-platform pass; (3) fourth retry-loop instance — owner-acknowledged in the G0 dispatch, consolidation refactor recommended as next task. No undisclosed deviation found.

## 3. Defects

None blocking. No D1-level findings: every packet safeguard maps to real, non-vacuous, re-executed tests; no guessed schema (constants cross-checked against the live capture in-test); no silent repair path; no degrees-area path; no hidden defaults; no storage violations.

## 4. Observations (non-blocking; O5-O7 flagged for the G4 geospatial reviewer)

- **O1 (LOW, test weakness):** `test_s9_touching_lot_from_outside_is_uncertain` (test file lines 893-903) hedges with `relation in ("boundary_uncertain", "outside")` plus a conditional assertion. Inputs are deterministic, so exactly one branch always runs — the test cannot fail on a silent inside/outside misclassification of THIS placement. The firm boundary-centered test covers the core guarantee, so this is redundancy weakness, not a coverage hole. Could pin the expected relation for the fixed fixture.
- **O2 (LOW, redundant condition):** `mappluto_geometry_arcgis.py` line 1819: `len(pairs) == MAX_FEATURES_PER_LOT and exceeded` is unreachable as a distinct branch while `MAX_FEATURES_PER_LOT > 1` (the `> 1` arm already fires). Harmless; only matters if the cap were ever lowered to 1.
- **O3 (LOW):** MPG80's synthetic body retains the real Shape__Area (97,113.6875) alongside a tiny replaced bowtie geometry; tests use `analyze_lot_geometry` directly so the divergence note never fires. Fine as-is; just an internal-inconsistency quirk of the derivation.
- **O4 (documented policy nuance):** The repair-area-drift guard (>1% → review_required) is deliberately exempted when `self_intersection` is among the findings, because GEOS "area" of a self-crossing ring is the signed lobe difference and pre-repair area is meaningless. Consequence: a large self-intersection repair can materially change area while status remains `repaired` (not review_required). Both areas are recorded in the repair record and the result note flags non-original geometry — downstream consumers must treat `repaired` as "inspect repairs," not as `valid`. Documented in code; acceptable, but worth restating whenever geometry facts enter the profile.
- **O5 (for G4):** Uncached lot fetches via `ResilientMapPlutoGeometryClient` perform TWO upstream calls (metadata + query) and consume two budget units; the client does not cache the validated metadata across lots. Correct and visible (budget test proves the accounting), but request-volume/budget sizing for the future profile-builder should account for it, or a metadata TTL cache could be added under a later packet.
- **O6 (for G4):** `_validate_query_envelope` drift-signals (rather than fails) a missing response `spatialReference` when features are present, relying on the validated LAYER metadata CRS. Reasonable and visible, but the geospatial reviewer should confirm comfort with metadata-CRS governance in that degraded case.
- **O7 (for G4):** Hole-to-shell assignment for multi-shell inputs picks the smallest containing shell by representative point (lines 873-887). Pathological straddling holes are caught downstream by the GEOS validity check, but this even-odd interpretation is worth a geospatial eye.
- **O8:** Registry draft addition (`nyc-dcp-mappluto-arcgis`) is complete against the PRD section 8.2 field list, additive only (existing two records untouched), and encodes the condo semantics, 20 ft accuracy, and two-staleness rule correctly; one open question (dataLastEditDate vs minor releases) is properly tracked.
- **O9:** My Windows/py3.11.9 re-run reproducing all hardcoded digest anchors, combined with green CI on Linux/py3.12, constitutes two-platform digest-determinism evidence — record this alongside the gate result.
- **O10 (carry-forward):** Fourth `_request_with_retry` instance confirms the shared-transport consolidation refactor now has four consumers; keep it owner-sequenced next per the standing directive.

## 5. G3 VERDICT: PASS

All GEO-S1..S12 scenarios map to real, re-executed, non-vacuous tests (80/80 new, 522/522 suite, ruff clean, digests reproduced on a second platform); all six safeguards hold with zero blocking defects and only LOW observations, several routed to the G4 geospatial reviewer.

Key paths: `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M2-T009\services\api\app\connectors\mappluto_geometry_arcgis.py`, `...\services\api\tests\connectors\test_mappluto_geometry_arcgis.py`, `...\services\api\tests\fixtures\mappluto_geometry\MANIFEST.json`, `...\project-control\reports\M2-T009-producer-report.md`.
