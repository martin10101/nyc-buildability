# M5-T073 producer report — DB-045(a) real-parcel bridge-ring precondition validation

Task: M5-T073 (D-084-R002; advisory DB-045(a), M5-T065 wave G3-F1)
Producer: backend-engineer
Base HEAD: `bc126fc77922284e2f90b4cbe674a495c8f51cd6`
Scope (allowed paths): `services/api/tests/connectors/test_bridge_ring_preconditions.py`,
`services/api/tests/connectors/fixtures/bridge_ring_pairs/**`, this report.

## STATUS — BLOCKED (the AS-1/AS-2/AS-3 runtime evidence is producible only by the routed supervisor/CI capture)

The producer-environment broker runs documented commands from the **worktree root only**; it
rejected the `cd services/api`-wrapped and non-documented `-s` variants when they were attempted
earlier this task (transcripts in §2, rows 2–4). Per the current directive those rejected broker
variants are **not re-attempted**; the scoped run is left to the already-routed supervisor/CI
harvest. Consequently no runtime evidence for this task is produced in the producer environment.

What this unit can and cannot stand behind, kept strictly separate (convention below):

- **[OBSERVED] static facts** — the test-file imports/symbols resolve at the frozen head (§3),
  the harness selects the documented authoritative byte basis in code (§4), the fixture bodies
  are single-line JSON and the manifest binds 8 pairs / 5 boroughs (§4–§5), and only two files
  changed this unit with no production edit (§1). These are file/tool reads, not runtime results.
- **[PREDICTED] runtime behavior (NOT a guarantee)** — that pytest collects cleanly, that the
  provenance digest equality and the three synthetic AS-2 assertions pass, and that the
  `services/api`-scoped ruff is clean. Each is *inferred* from the static facts but was **not
  executed here**; the routed run confirms or falsifies each.
- **[PENDING-HARVEST] numeric values** — every per-pair measured column in §5 and the recorded
  == computed digest comparisons. Never guessed.

Outstanding to clear this task: the two routed commands in §6 (`services/api`-scoped `ruff` then
`pytest -q -s`) with their **actual output and exit codes** retained. No completion is claimed; do
not accept, merge, or mount.

## Evidence-status convention

- **[OBSERVED]** — a command actually run through the broker this unit (result seen here), or a
  static fact read directly from repo files/tools this unit (a symbol is defined at a line; a body
  is single-line; a digest is recorded in the manifest). It never covers runtime behavior that was
  not executed.
- **[PREDICTED]** — a runtime outcome (collection success, an assertion's pass/fail, a
  scoped-config lint result) inferred from the [OBSERVED] static facts but **not executed** this
  unit. A prediction, not a guarantee; confirmed or falsified only by the routed run.
- **[BLOCKED]** — a command the producer environment cannot run; routed with the exact command.
- **[PENDING-HARVEST]** — a concrete value (a per-pair number, a digest-equality result) produced
  only by the routed run; never guessed.

## 1. What changed (the harness/test patch — the deliverable)

`services/api/tests/connectors/test_bridge_ring_preconditions.py` — offline, deterministic
measurement harness + 14 tests. It **imports** the accepted bridge's real precondition
(`app.api.v1.outline_bridge`: `fit_correspondence`, `BRIDGE_MAX_RMS_RESIDUAL_FT=2.0`,
`BRIDGE_AMBIGUITY_SEPARATION_FT=2.0`, `BRIDGE_MIN_CONTROL_POINTS=4`, `ParcelRing`, `_open_ring`,
`_exterior_ring_from_geojson`, `_CorrespondenceError`) and reconstructs each ring the way
the bridge's production adapters do, but from recorded fixture bytes:

- display 4326 ring via `outline.build_lot_outline` → `_exterior_ring_from_geojson` → `_open_ring`
  (harness `:176–199`);
- authoritative 2263 ring via `geom.analyze_lot_geometry` → `canonical_geometry[0][0]` → `_open_ring`
  (harness `:202–232`).

`classify_ring_pair` (`:107–168`) routes each pair through the bridge's OWN decision path —
vertex-count equality → `fit_correspondence` RMS vs the 2.0-ft bound → ambiguity separation vs the
2.0-ft bound — and records a typed `refusal_class` on refusal. **[OBSERVED static]** this code path
mirrors the bridge's own consumer at `outline_bridge.py:737–802` symbol-for-symbol
(`fit = correspondence.fit`; `fit.rms_residual`; `correspondence.runner_up_rms_residual`;
`correspondence.separation`). Whether the reconstructed rings and the fit actually produce the
bridge's measured values on the real pairs is **[PENDING-HARVEST]** — that is what the routed run
measures.

No production edit (AS-4): both connectors and the bridge are imported read-only; no new dependency.

Working-tree state, `git status --porcelain` **[OBSERVED]** — two files modified this unit:
`test_bridge_ring_preconditions.py` (the harness) and this report. The fixtures pack
(`bridge_ring_pairs/**`: manifest, P05–P08 bodies, `HARVEST_SPEC.md`, `PROVENANCE.md`) is already
committed at base `bc126fc7`.

## 2. Verification evidence — real transcripts this unit

| # | command (as documented) | who / cwd | status | result |
|---|---|---|---|---|
| 1 | `python -m ruff check .` | producer / worktree root | **[OBSERVED]** exit 1 | 45 errors, ALL in `project-control/reports/M0-T054-protected-config/doctor_proof.py` + `tools/*`; the test file did **not** appear in any finding of THIS run. This is a **worktree-root** invocation — different config resolution and file selection from the `services/api`-scoped CI job. It therefore does NOT establish the scoped result; the authoritative `services/api`-scoped ruff is **[PREDICTED]** clean and **[PENDING-HARVEST]** (routed, §6). Root findings are pre-existing and out of scope — left untouched per directive/AS-4. |
| 2 | `cd services/api && python -m ruff check .` | producer / services/api | **[BLOCKED]** | broker: "not an enumerated read-only git command and is not a packet-documented test command". Routed; **not re-attempted** per directive. |
| 3 | `python -m pytest tests/connectors/test_bridge_ring_preconditions.py -q -s` | producer / services/api | **[BLOCKED]** | broker rejects the non-documented `-s` variant (same message as #2). Routed; **not re-attempted**. The `-s` capture (verdict-table print) is what surfaces the §5 numbers. |
| 4 | `python -m pytest tests/connectors/test_bridge_ring_preconditions.py -q` | producer / worktree root | **[BLOCKED]** exit 4 | `file or directory not found: tests/connectors/…` — the documented relative path resolves under `services/api`; the broker runs from root. A cwd artifact, **not** a test outcome. Routed. |
| 5 | `python tools/modularity_check.py --check` | producer / repo root | **[OBSERVED]** | `selected 475 files; failures 0; warnings 22` — all 22 warnings are pre-existing production files; the test file is not among them. No new failure, no oversized growth. |
| 6 | static symbol/attr resolution at frozen head | producer (Grep/Read) | **[OBSERVED static]** | every imported bridge/connector symbol + attribute + doc key is defined at the frozen head — see §3. This **[PREDICTS]** clean collection; it does not prove it (collection also runs module-level code — see §3). |
| 7 | fixture completeness | producer (git ls-files / Grep) | **[OBSERVED]** | all 8 P01–P04 source fixtures tracked; all 8 P05–P08 bodies single-line minified JSON — see §4. |

## 3. Static harness-correctness verification [OBSERVED static] — collection is [PREDICTED] clean, not guaranteed

The base commit noted the file was RED on unfinished imports (NameError `build_outline_query_url`
etc.). Those names are present in the current working-tree file, each reached through the
already-imported `outline.`/`geom.` module aliases, and each **[OBSERVED]** to be defined at the
frozen head:

| name used by harness | defined at |
|---|---|
| `BRIDGE_MIN_CONTROL_POINTS` / `_MAX_RMS_RESIDUAL_FT` / `_AMBIGUITY_SEPARATION_FT` | `outline_bridge.py:111 / :117 / :121` |
| `ParcelRing` / `_open_ring` / `_exterior_ring_from_geojson` / `_CorrespondenceError` / `fit_correspondence` | `outline_bridge.py:150 / :180 / :192 / :369 / :429` |
| `Correspondence.fit` / `.runner_up_rms_residual` / `.separation`; `fit.rms_residual` / `.max_residual`; `_CorrespondenceError.reason` | `outline_bridge.py:353 / :366 / :366 / :479 / :802 / :375` |
| `outline.build_outline_query_url` / `build_lot_outline` / `LotOutlineTransport` / `SOURCE_ID` | `mappluto_lot_outline.py:218 / :576 / :206 / :63 (re-export)` |
| `geom.SOURCE_ID` / `CRS_STAMP` / `require_authoritative_crs` / `analyze_lot_geometry` | `mappluto_geometry_arcgis.py:182 / :196 / :471 / :768` |
| `GeometryAssessment.status` / `.normalized_digest` / `.canonical_geometry` | `mappluto_geometry_arcgis.py:622 / :627 / :628` |
| `build_lot_outline` doc keys `outcome` / `geometry` / `source.dataset_version`; `"single_lot"` | `mappluto_lot_outline.py:481 / :484 / :495 / :103` |
| `normalize_bbl(...).canonical` | `bbl.py:127 / :71` |

**Scope of this observation:** it shows no *unresolved symbol* on the measurement path. It does
**not** exercise import-time execution — the module runs `_PAIRS = load_pairs()` and the
`@pytest.mark.parametrize` binding at collection (`:442–443, :458–459`), and each pair drives
`normalize_bbl`, `build_lot_outline`, `analyze_lot_geometry`, `_open_ring`, and `PairVerdict`
construction. A defined symbol with an incompatible signature, a manifest that fails to parse, or a
ring the adapters reject would surface only when that code runs. Clean collection is therefore
**[PREDICTED]** from this static basis, not observed; the routed run in §6 is the confirmation, and
its exit code plus the §5 numbers — not only the per-pair numbers — are the outstanding evidence.

## 4. Provenance / byte-basis verification (AS-1) — basis is [OBSERVED static]; equality is [PENDING-HARVEST]

The harness re-hashes each authoritative body and asserts recorded == computed
(`test_real_pair_measured_offline_with_roundtrip_provenance`, `:466–467`). The two connectors use
**different documented byte bases**; **[OBSERVED static]** the code selects the correct basis for
each via `_auth_response_body` (`:271–279`) + `_sha256` (`:238–242`):

- **P01–P04 authoritative** — `kind = "provenance_envelope.response_body_raw"`: the M2-T009 pack
  records `response_body_sha256` over `response_body_raw`; the harness unwraps
  `envelope["response_body_raw"]` and hashes exactly that basis. **[OBSERVED: the code selects this basis.]**
- **P05–P08 authoritative** — `kind = "raw_esri_body"`: the orchestrator harvest recorded
  `response_body_sha256` over the raw esri body; the harness returns the file verbatim and hashes
  it. **[OBSERVED: the code selects this basis.]**

`_read_body` uses `read_text(encoding="utf-8")` (universal newlines). **[OBSERVED]** all 8 P05–P08
bodies are single-line minified JSON with no embedded newlines (`Grep` line-count = 1 each), so the
newline translation is a content no-op and the digest is byte-stable across checkout. Recorded
authoritative digests (referenced from the manifest, not re-embedded):

| pair | authoritative body (source pack) | recorded `response_body_sha256` |
|---|---|---|
| P01 | `mappluto_geometry/MPG02_lot_single_1008350041.json` (M2-T009) | `…a67289b4` |
| P02 | `mappluto_geometry/MPG06_lot_holes_1000010010.json` (M2-T009) | `…d5b2e095` |
| P03 | `mappluto_geometry/MPG04_lot_condo_billing_1000157501.json` (M2-T009) | `…b67a6fcb…` |
| P04 | `mappluto_geometry/MPG07_lot_multipolygon_4142600001.json` (M2-T009) | `…5b159f3a` |
| P05 | `bridge_ring_pairs/P05_regular_small_bronx_2022610022/authoritative_2263.json` (raw esri) | `…8906835e` |
| P06 | `bridge_ring_pairs/P06_regular_small_brooklyn_3000350007/authoritative_2263.json` (raw esri) | `…a0d3d35c4` |
| P07 | `bridge_ring_pairs/P07_irregular_corner_si_5000050039/authoritative_2263.json` (raw esri) | `…f74407c` |
| P08 | `bridge_ring_pairs/P08_curved_manyvertex_si_5000040010/authoritative_2263.json` (raw esri) | `…f748cdd3f4` |

(Full digests live in `pairs_manifest.json`.) The **actual** recorded == computed equality is
asserted inside the routed pytest (#4/§6) and is **[PENDING-HARVEST]**; the producer verified only
the basis and file shape and cannot compute sha256 through the documented-command broker.
**Residual risk explicitly identified:** a trailing-newline-at-EOF mismatch would surface only at
that assertion — the routed run confirms or falsifies it.

## 5. Real-parcel sample + AS-3 verdict table (identity [OBSERVED]; measured [PENDING-HARVEST])

Eight real single-lot ring pairs across **5 boroughs** / **7 geometry classes** — at/above the
packet floor (≥8 pairs / ≥3 boroughs / regular-small-lot). Identity columns are [OBSERVED] from
`pairs_manifest.json`. Bytes are verbatim official captures; nothing fabricated. The measured
columns are produced only by the routed pytest and are shown as `⧗ pending-harvest` — **not
guessed**.

| pair | BBL | borough (code) | geometry class | display vtx | auth vtx | counts eq | RMS (ft) | max (ft) | runner-up RMS | separation (ft) | verdict | refusal class |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P01 | 1008350041 | Manhattan (1) | regular single-exterior block lot | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ |
| P02 | 1000010010 | Manhattan (1) | many-vertex irregular holed waterfront | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ |
| P03 | 1000157501 | Manhattan (1) | large assemblage condo-billing merged | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ |
| P04 | 4142600001 | Queens (4) | true multipolygon shoreline-clipped | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ |
| P05 | 2022610022 | Bronx (2) | regular small residential lot | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ |
| P06 | 3000350007 | Brooklyn (3) | regular small residential lot | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ |
| P07 | 5000050039 | Staten Island (5) | irregular corner lot | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ |
| P08 | 5000040010 | Staten Island (5) | curved-edge densification stress | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ | ⧗ |

Transcription rule for the harvest fill: where a pair refuses before the fit runs
(`counts_equal=false` → `vertex_count_mismatch`), the RMS/max/runner-up/separation cells are the
explicit unavailable value `—` (the affine fit never executes on unequal counts), `verdict=refuse`,
`refusal_class=vertex_count_mismatch`. Fill every cell from the routed run's **actual printed
output and exit code**, marking the filled columns [OBSERVED].

**Refusals are preserved as findings, not failures.** The parametrized test asserts a definite
`pass`/`refuse` with a non-null `refusal_class` on refusal (`:470–472`) and never drops a pair; a
precondition violation is a finding, never a test failure by itself. AS-2 pins this numerically
offline: a corresponding synthetic pair → `pass` (RMS < 1e-3), a densification mismatch →
`refuse`/`vertex_count_mismatch`, a non-corresponding same-count pair → `refuse`/`residual_too_high`
(`:374–436`). Those three assertions run inside the routed pytest and their pass/fail is
**[PREDICTED]**, confirmed only there.

## 6. Exact routed capture (supervisor/CI, from `services/api`)

Run from `services/api`, `ruff` first, then `pytest`, retaining the **actual stdout/stderr and exit
code of each**:

```
cd services/api
python -m ruff check .
python -m pytest tests/connectors/test_bridge_ring_preconditions.py -q -s
```

Then, from the observed output only: (a) record the `ruff` exit code (clears the scoped-lint
[PREDICTED] item); (b) record whether pytest collected and its exit code (clears the collection
[PREDICTED] item); (c) paste the emitted per-pair numbers into the §5 measured columns (marking
them [OBSERVED]), applying the `—`-for-refused-before-fit rule; (d) confirm the digest-equality and
the three AS-2 assertions from the run; then record the §7 bounded verdict at the observed branch.
`-s` surfaces `test_verdict_table_builds_over_every_real_pair`'s printed JSON table (`:478–487`).

## 7. Bounded disposition (D-051) — resolves at the routed capture

Bounded to this sample of **8 real pairs / 5 boroughs / 7 geometry classes**, measured by the
mounted bridge's own precondition (imported `fit_correspondence` + the 2.0-ft RMS and 2.0-ft
ambiguity bounds; EPSG:2263 US survey feet). The numeric verdict is **[PENDING-HARVEST]** and
resolves to exactly one of the following, with the requirement stated per the **observed refusal
classes** (never generalized beyond the measured sample):

- **(a) preconditions hold on the sample** — every pair `counts_equal=true`, `rms_residual_ft ≤ 2.0`,
  `separation ≥ 2.0` → `pass`. The mount-seam precondition is cleared **on this bounded sample**; no
  ring normalization is implied by these pairs; **or**
- **(b) one or more pairs refuse** — for each refusing pair, state which refusal class was observed
  (`vertex_count_mismatch`, `residual_too_high`, or `ambiguous_correspondence`), the residual/
  separation floats for fit-level refusals, and `—` for count-level refusals. The implied mount-seam
  requirement then follows the class actually observed: a `vertex_count_mismatch` implies ring
  normalization / densification alignment between the 4326 display ring and the 2263 authoritative
  ring BEFORE any mount (the exact DB-045(a) risk); a `residual_too_high` or
  `ambiguous_correspondence` implies a correspondence-quality/registration requirement at the seam.
  A-priori risk candidates (not a prediction of outcome): P02 holed waterfront, P04 multipolygon
  member-ordering, P08 curved densification stress.

The mount itself is OUT OF SCOPE (AS-4); this unit measures reality before that seam. The conclusion
never generalizes beyond the measured sample, and no numeric verdict is asserted until it is observed.

## 8. Bounded review packet for the next review (assess AS-1 and AS-2 self-contained)

So the next reviewer can assess AS-1 (provenance / byte basis) and AS-2 (synthetic known-outcome)
without re-running discovery, the supervisor should bundle, at the reviewed head:

1. **Complete test patch + harness** — `services/api/tests/connectors/test_bridge_ring_preconditions.py`
   (whole file; it is the deliverable). Key spans: ring reconstruction `:176–232`; `_sha256` /
   `_auth_response_body` `:238–279`; `classify_ring_pair` `:107–168`; AS-2 synthetic tests
   `:366–436`; AS-1 real-pair provenance/round-trip test `:446–487`.
2. **Production correspondence / adapter excerpts** (read-only, to cross-check the mirror in §1/§3) —
   `app/api/v1/outline_bridge.py`: `fit_correspondence` + `Correspondence.fit/.separation/
   .runner_up_rms_residual`, the constants (`:111/:117/:121`), `_open_ring`,
   `_exterior_ring_from_geojson`, `_CorrespondenceError`, and the bridge's own consumer `:737–802`;
   `app/connectors/mappluto_lot_outline.py`: `build_lot_outline`, `_exterior_ring_from_geojson`,
   `build_outline_query_url`, `LotOutlineTransport`, `SOURCE_ID`;
   `app/connectors/mappluto_geometry_arcgis.py`: `analyze_lot_geometry`, `require_authoritative_crs`,
   `CRS_STAMP`, `canonical_geometry`, `normalized_digest`, `status`.
3. **Fixture manifest + body evidence** — `fixtures/bridge_ring_pairs/pairs_manifest.json`, the
   P05–P08 `display_4326.json` / `authoritative_2263.json` bodies, `HARVEST_SPEC.md`, `PROVENANCE.md`,
   and the referenced P01–P04 source packs (`tests/fixtures/mappluto_lot_outline`,
   `tests/fixtures/mappluto_geometry`) with their recorded digests.
4. **Routed capture output** — once the §6 commands run: their verbatim stdout/stderr and exit codes.

## 9. Note for integration

Working-tree changes (report + harness) are uncommitted; the fixtures pack is committed at
`bc126fc7`. The orchestrator runs git, records gates (G0/G2/G3/G4), and integrates (ADR-005). This
unit claims no completion: status is BLOCKED pending the routed supervisor/CI capture (`services/api`-
scoped ruff + pytest, §6). Do not accept, merge, or mount before that capture's actual output is
[OBSERVED] and the §5/§7 verdict is recorded.
