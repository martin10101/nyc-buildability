# M2-T009 - G4 Integration and Geospatial Review (geospatial-engineer)

*(Orchestrator note: saved verbatim from the reviewer's agent-return channel per the report-preservation rule; transport entity-decoding only. Orchestrator CI attestation referenced in section 1: task PR #45 all 8 jobs green on BOTH events at head 6f0992f.)*

## 1. Scope and method (what I ran)

Reviewed the committed state at `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M2-T009` (branch `task/M2-T009-mappluto-geometry`, commit 6f0992f). Read order per instructions: task packet, G4/geospatial-pack docs, research sections 2.5 (condo/CRS) and 4.3 (accuracy), then the full connector module (`services/api/app/connectors/mappluto_geometry_arcgis.py`, all 2,169 lines), the full test module (1,271 lines), fixtures + MANIFEST, dependency diffs, and the producer report LAST.

Executed independently in my sandbox (Windows, Python 3.11.9, shapely 2.0.7 / GEOS 3.11.4 already present — matching the exact pins):

- `python -m pytest -q` from `services/api` → **522 passed in 4.50s** (expected 522; producer baseline 442 + 80 new). Re-run of the new module alone → **80 passed in 0.39s**. `ruff check .` → All checks passed.
- **Independent from-spec digest reimplementation**: I rewrote the canonicalization from the `MPG_CANONICALIZATION_SPEC` prose alone (my own code, not importing the connector's canonicalization functions) and reproduced ALL FOUR anchors byte-identically: SQUARE `6fc369ac...`, SQUARE original `97e90356...`, ESB `ed47213e...`, HOLES `cdb23885...`, MULTI `054e72c4...`. The spec is genuinely self-describing and deterministic.
- **Shapely recomputations** of every spatial-scenario claim, repair characterization (make_valid on the bowtie), ring-role facts, hole-outside-shell fixture honesty, wrong-CRS fixture contents, and the MPG03/MPG05 digest question.
- Scope audit via `git diff main...HEAD --name-status`; duplicate-implementation grep; fixture-pack size measurement (556 KB).

CI-green on PR #45 (both events, Linux) is per the orchestrator's statement; I could not run `gh` (prohibited), but my local re-run plus the independent Windows/py3.11 digest reproduction is stronger evidence than re-reading CI logs — the anchors now reproduce on three environments (producer Windows, CI Linux/py3.12, reviewer Windows independently re-derived).

## 2. Findings per duty

**Duty 1 — Geometry math correctness: PASS.**
- Esri orientation (module lines 824-849): CW (negative shoelace) = exterior, CCW = hole — correct esri JSON semantics. I recomputed ring roles on the raw fixtures: MPG02 = 1 CW; MPG06 (Governors Island) = 1 CW + 2 CCW holes; MPG07 (4142600001) = **two CW exteriors, both preserved** (test asserts `exterior_ring_count == 2`, my recompute confirms and the MULTI digest matches).
- Hole assignment (lines 872-887): representative-point containment, smallest containing shell for nested cases — deterministic and standard. A hole outside every shell → `review_required` (never guessed); MPG88 verified honest: its hole's representative point genuinely lies outside the shell (my recompute: `contains = False`).
- A hole straddling a shell boundary would pass representative-point assignment but then fail GEOS validity ("hole lies outside shell" → `_classify_validity_reason` routes "hole"/"shell"/"nested" fragments to `review_required`, line 753) — layered fence confirmed.
- Bowtie with zero SIGNED area (lines 835-844): convex-hull disambiguation from genuinely collinear rings is correct; MPG80 is exactly this case (`explain_validity` = "Self-intersection", `area_before = 0.0`).
- Ring closure and consecutive-duplicate removal are the only structural repairs, each fully characterized and recorded (lines 692-721). Empty (`rings: []`) vs null geometry are distinct findings (`empty_geometry`/`null_geometry`), both `invalid_geometry`. Non-finite coordinates typed. `paths`/`points` payloads typed `geometry_collection`.

**Duty 2 — Repair policy: PASS.**
- Method is `make_valid` (line 913), not `buffer(0)` — the right choice for parcels: I verified `make_valid` on the MPG80 bowtie yields a MultiPolygon preserving BOTH lobes (area 5000.0), where `buffer(0)` can silently drop a lobe.
- Repair is gated to a whitelist of characterizable pathologies (lines 736-741); unknown `explain_validity` reasons, inverted orientation, non-polygonal/empty `make_valid` output, and GEOS failure all → `review_required`.
- Topology change is characterized: area before/after recorded in the repair record with shapely+GEOS versions; drift > 1% → `review_required` — except for self-intersection inputs where `area_before` is meaningless (verified: 0.0 for the bowtie), a documented and sound exemption with both areas still recorded.
- Can repair silently change district intersections? No: repaired geometry always carries status `repaired` (never `valid`), the original digest is ALWAYS preserved (computed at line 789 before any branch), and the result note states the geometry is "NOT the untouched official source". The risk is fenced by status visibility, and uncharacterizable repairs never produce a canonical geometry at all.

**Duty 3 — CRS and units: PASS.**
- EPSG:2263 US survey feet; `geom.area` in this projected CRS is planar square feet — correct. Cross-check against the official `Shape__Area` attribute (same CRS/units) passes within 1e-6 relative on the live ESB lot (97,113.6875), which is a genuine unit proof.
- Degrees-area path genuinely absent: the ONLY area function (`compute_area_sq_ft`, line 589) calls `require_authoritative_crs` first; negative tests prove 4326, 3857, `{}`, and `None` are all refused. `analyze_lot_geometry` gates CRS before touching any coordinate (line 786).
- A wkid 3857/4326 response is caught BEFORE coordinate math: metadata CRS validated at lines 1431-1442 (typed `WrongCRSError`); query-response `spatialReference` validated in `_validate_query_envelope` (lines 1621-1635), which runs before `analyze_lot_geometry` in `fetch_lot_geometry`. MPG99 (4326 query response) verified. One narrow gap noted as D1 (LOW) below.

**Duty 4 — Digest canonicalization: PASS.**
- The spec is sufficient for independent reproduction — proven by my from-scratch reimplementation matching all anchors. Ring rotation (lexicographic-min pivot), hole sorting, member sorting, half-even 0.01 ft quantization, negative-zero normalization, and open-cycle serialization are each unambiguous for valid geometry.
- 0.01 ft precision is sound against the source's ±20 ft accuracy: no false-precision claim (it is digest quantization, not an accuracy statement, and live coordinates already serialize at 2 decimals), and no collision risk at parcel scale.
- Three digests kept separate (raw bytes / verbatim original geometry / normalized canonical) with the rotation-invariance test proving separation (`test_s2_ring_rotation...`: normalized equal, original different).
- GEOS-upgrade fence: valid-geometry digests are GEOS-independent (coordinates pass through shapely untransformed), but repaired-geometry digests are GEOS-dependent — fenced three ways: exact `shapely==2.0.7` pin in both dependency files (verified: exactly a pin, nothing else in that diff), in-test version assertion (`test_s7_shapely_and_geos_versions_match_the_exact_pins`), and the hardcoded bowtie repair anchor that would fail on any behavioral change. Default WKB/WKT deliberately not used.

**Duty 5 — Spatial scenarios: PASS.**
I recomputed the geometric claims against the REAL M2-T007 R3-2 fixture (ZF03) and the REAL Governors Island holed lot:
- Deep point (997482.04, 163293.94): 393.58 ft inside the district boundary — the "fully inside" 50-ft box is genuinely within the 20-ft-eroded district (recomputed True).
- "Fully outside" box: 544.0 ft away — genuinely beyond tolerance.
- Boundary-touch box centered on the boundary midpoint: not within eroded, distance 0, zero eroded-intersection, zero dilated-difference → `boundary_uncertain` by construction — a boundary touch is correctly distinguished from material overlap and NEVER silently inside/outside. A lot poking < 20 ft past the boundary also lands in `boundary_uncertain`, not split — correct conservative semantics.
- Hole interaction: deep-in-hole box is 64.82 ft from the polygon (correctly `outside` — hole interior is exterior space); covering box has firm inside AND firm outside parts (`split_intersection` recomputed True).
- Tolerance is named (20.0 ft), its official basis quoted in every classification output, and repeated-run reproducibility is tested (3 identical runs). The classifier is explicitly test-level, not the production engine — matching the packet's scope fence.

**Duty 6 — Integration/regression: PASS.**
- Full suite 522 passed, 4.5 s — deterministic (injected clocks/sleeps; no wall-clock waits; `FIXED_CLOCK` and `FakeMonotonic` throughout).
- Scope audit: diff file list is exactly the allowed paths — new connector module, new test module, new fixture directory, registry-draft addition (additive third record, existing two untouched), producer report, and the shapely pin in pyproject+requirements (the one permitted shared touch, verified to be exactly `shapely==2.0.7` plus comments). Zero modifications to existing connectors, tests, contracts, profile (`git diff main...HEAD -- services/api/app/profile/` is empty; the `mappluto` mentions in `builder.py` are pre-existing doc references), resilience, or workflows. Read-only-reuse guard test present (`test_s12_no_pluto_module_state_is_modified`).
- No duplicate implementation: transport and `canonical_json_digest` are imported from `pluto_soda`; the per-module retry loop is the disclosed fourth instance of the accepted wave pattern (producer report §12.6, consolidation owner-sequenced post-wave). No competing lot-geometry code exists.
- Error taxonomy aligned with M2-T007/T008 plus the packet-required geometry states (`wrong_crs`, `result_mismatch`; validity states on the assessment, not exceptions — a sound design distinction). Budgets bounded (one unit per attempt, pre-I/O), Retry-After honored/capped, circuit fast-reject with no upstream I/O, malformed-never-empty proven.
- Low-storage: 556 KB fixture pack (KB-scale); shapely wheel size disclosed (~2.4 MB installed, report §7); 7 live GETs at capture; no persistent local artifacts.
- Two-staleness quartet verified in-test (all four source-age x transport-serve combinations, neither dimension writing the other's fields).

## 3. Defects

- **D1 (LOW)** — `fetch_layer_metadata` validates only `extent.spatialReference` (module lines 1426-1442), not the layer's top-level `spatialReference` key that the live metadata also carries (confirmed present in the MPG90 derivation: top-level stayed 2263 while extent was mutated to 4326). A drift where the layer SR changes but the extent SR is stale would pass metadata validation; the residual exposure requires the simultaneous absence of `spatialReference` on a feature-bearing query response (itself a drift signal, and live behavior always includes it), so the exposure is doubly contingent. Suggested (non-blocking): also assert the top-level `spatialReference` when present.
- **D2 (LOW)** — Producer report §8 table: the "Bytes" column shows fixture-FILE sizes (1,323 / 1,465 for MPG03/MPG05) beside body digests; the raw bodies are both identical 247-byte empty envelopes (I recomputed: both sha256 `437b1d00...`, matching MANIFEST). The report's own note explains the shared digest correctly, so this is a column-labeling imprecision in the report only; MANIFEST and the in-test digest verification are exact. No code change needed.

No Critical, Major, or Minor defects.

## 4. Observations

- **O1** — Canonical rotation pivot uses first-occurrence of the lexicographic minimum; if quantization ever collapsed two non-consecutive vertices onto the same minimal pair, two different source presentations of the same shape could canonicalize to different rotations. Same-input-bytes determinism (the load-bearing property) is unaffected, and self-touching rings are invalid upstream and repaired before canonicalization; theoretical only.
- **O2** — Multipolygon member sort ties (two polygons with byte-identical exterior serializations) fall back to input order; such geometry implies duplicate/overlapping shells, which are invalid and route through the repair path first. Theoretical.
- **O3** — `exceededTransferLimit=true` with exactly one returned feature would yield outcome `single_feature` with the flag surfaced in `exceeded_transfer_limit` but without `review_required`; only reachable via a self-contradictory server response (resultRecordCount=10). Worth a guard if ever observed live.
- **O4** — The classifier applies the named 20 ft tolerance once; both the lot and district geometries independently carry plus-or-minus 20 ft accuracy, so worst-case combined boundary uncertainty approaches ~40 ft. The packet requires exactly the source-stated named tolerance and this is a test-level diagnostic; the future production intersection task should decide explicitly whether to compound tolerances.
- **O5** — The `invalid_orientation` finding code is reused for hole-outside-shell (a distinct pathology); the state (`review_required`) is honest, the label slightly imprecise. Cosmetic.
- **O6** — The independent from-spec digest reproduction on a third environment (my Windows/py3.11 sandbox, distinct from both producer capture and CI Linux/py3.12) materially strengthens the cross-platform determinism claim beyond what CI alone proves.

## 5. G4 VERDICT: **PASS**

Full suite re-ran green (522) in my sandbox, all four digest anchors reproduced from an independent from-spec reimplementation, every spatial-scenario geometric claim recomputed true against the real fixtures, scope exactly within packet bounds with zero regression surface, and only two LOW findings (a doubly-contingent metadata-CRS gap and a report-table labeling imprecision), neither blocking.
