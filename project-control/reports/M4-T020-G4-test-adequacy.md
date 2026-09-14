# Gate Report — G4 Test Adequacy

> Saved VERBATIM by the orchestrator from the qa-engineer agent return (2026-09-14;
> transport entity-decoding only, per the report-preservation rule). Reviewer ≠ producer.
> Orchestrator note: the "CI in flight" acceptance hold cleared after the return — run
> 34817436542 on the pinned head 16272c05 concluded success (all jobs incl. modularity).

- Gate ID: G4 (test adequacy)
- Task ID: M4-T020 — B3 DCM centerline geometry parse-and-expose
- Reviewer: qa-engineer (independent; not the producer)
- Producer: D-053 loop worker (backend-engineer role, run persistent-local-34)
- Result: **PASS**
- Clean environment/worktree used: reviewer landed in isolated worktree `agent-ae8803760b6570171` (HEAD d8b3899f ≠ pin); all pinned content read via `git show 16272c05:<path>` from the shared object store; all executions performed on a byte-exact `git archive 16272c05` extraction in the session scratchpad (no repo file touched; no git/gh/project_control verbs run)

## 0. Content-identity check (first)

Material commit ba301b67 vs producer worktree commit d7766b8d vs pinned review head 16272c05 — per-file blob SHAs, identical across all three:

| File | Blob SHA (all three commits) |
|---|---|
| project-control/reports/M4-T020-producer-report.md | e7f319482dd0a5fd3fc538c6bfdd5dfa54e1e6b2 |
| services/api/app/connectors/dcm_street_centerline_geometry.py | b066c742c3b3d555a32ab1ae49b80bc8e67c618f |
| services/api/tests/connectors/test_dcm_street_centerline_geometry.py | 3f848c2a2401c46505461fb87fd5c96dda650c9d |

`git diff --name-status ba301b67~1 ba301b67` = exactly the 3 allowed files (all `M` — pre-commit content was the standard seeded one-line placeholders, so both production files are NEW in substance). ba301b67 is a byte-identical cherry-pick of d7766b8d for the material surface. **Identity: CONFIRMED.**

## 1. Acceptance criteria reviewed

Packet `project-control/tasks/M4-T020.json` at 16272c05, scenarios S1–S5 (S5 is the scope/regression scenario; S1–S4 are the test-file scenarios under this gate).

## 2. Coverage table (reviewer's own audit, file = test file at pin; module = dcm_street_centerline_geometry.py at pin)

### S1 — wire-format parse and typing: ADEQUATE
| Aspect | Evidence | Verdict |
|---|---|---|
| Real recorded fixture drives multi-path parse | test:167–189 uses accepted M4-T015 fixture `west_100_st_two_segments.json`; I independently parsed the pinned fixture: OBJECTID 7719 = 3 paths/6 vertices, 14471 = 3 paths/12 vertices, first vertex `[992185.54514055, 229943.965358555]`, widths "60"/"100" — every test literal matches the wire | PASS |
| Typed polylines (tuple-of-tuple finite float pairs) | test:181–188 asserts tuple types at all 3 levels + float components + exact first-vertex equality | PASS |
| Pairing with attributes from the SAME body | test:191–198 (streetwidth_raw/street_name/feature_index); also re-proven under refusal at test:431–433; module pairs by document position with `zip(strict=True)` + pairing guard (module:422–431) | PASS |
| AST-import-allowlist + no-URL-building non-vacuous | test:233–268. Verified NOT vacuous: (a) it reads `geometry_module.__file__` live and computes the import set via `ast.walk` with two-sided set equality; I ran the test's own logic on mutated copies — adding `import urllib.request` or `from urllib.parse import urlencode` breaks equality (False/False); (b) token scan catches plain URL/`FeatureServer`/`outSR`/`pyproj`/conversion-constant literals. Cross-check: `parse_segment_page` in the accepted module (arcgis.py:768–799) does NO page-level CRS/geometryType work, so the new module's gates are the only thing making S2/S3 pass — the scan tests real content | PASS |
| Counting-fetch-seam: each page transported exactly once | test:520–534 (metadata+1 page → `len(calls)==2`), test:558–568 (metadata+2 pages → `len(calls)==3`), `calls[0]==build_metadata_url()`; module's recording seam (module:504–536) has a typed pairing guard | PASS |
| Transport failures typed via reuse | test:271–280 (HTTP 502 → UpstreamError; ArcGIS error object w/ 200 → UpstreamError; missing features → MalformedResponseError) | PASS |
| Empty page / exceededTransferLimit | test:213–224 | PASS |

### S2 — CRS fail-closed: ADEQUATE
| Aspect | Evidence | Verdict |
|---|---|---|
| 8-variant refusal matrix | test:288–317, exactly the 8 dispatched variants: key-absent, JSON-null, wkid-absent `{}`, WGS84 4326, bare-2263 (wire wkid must be 102718, not the EPSG number), latestWkid-absent, wrong-latestWkid 9999, non-object string. Each verified refusable against module:154–181 (strict `wkid==102718 AND latestWkid==2263` conjunction) | PASS |
| Matrix necessarily exercises the NEW module | asserts `error_type=="wrong_crs"` AND `detail["expected"]=={"wkid":102718,"latestWkid":2263}` — the accepted module's only WrongCRSError (metadata check, arcgis.py:574–581) has detail keys `url`/`spatial_reference`, no `expected`; upstream could not satisfy these assertions | PASS |
| Expected-vs-received named | test:311–317 ("102718"/"2263" in message + `received` in detail) | PASS |
| CRS gate ordering before geometry-type check | test:320–323 — body missing BOTH spatialReference and geometryType must raise WrongCRSError, not SchemaDriftError; discriminates module order (module:404 before 407–420) | PASS |
| Paged fetch fails closed on wrong-CRS page | test:571–576 (wkid 3857 page after good metadata) | PASS |
| Non-polyline / absent geometryType = typed schema drift | test:326–331 | PASS |

### S3 — malformed-geometry taxonomy: ADEQUATE
| Aspect | Evidence | Verdict |
|---|---|---|
| 13 parametrized conditions, each a distinct typed state | test:339–436. Audit: 13 conditions → 13 distinct (status, finding-fragment) pairs over 7 typed statuses (statuses repeat where the packet groups conditions — e.g. `null_geometry` covers key-missing vs JSON-null — distinctness carried by the typed finding, which the test asserts per condition). NaN, Infinity, and boolean-coordinate (`bool`-is-`int` trap, module:260) all covered | PASS |
| Visible, never dropped | each param asserts `features_total==1`, entry present, identity+attributes still paired (`object_id==1`, `streetwidth_raw=="60"`), `usable==0`/`refused==1` | PASS |
| Neighbor preservation | test:438–455 (good/bad/good page → order preserved, statuses `[OK, NULL, OK]`, counts 2/1) | PASS |
| No partial repair | test:458–465 — intact first path NOT salvaged when path 1 is degenerate (`paths is None`) | PASS |
| Extra z/m components visible | test:468–473 — status OK, pair truncated to (x,y), `extra_components:1` finding recorded | PASS |

### S4 — passthrough + provenance: ADEQUATE
| Aspect | Evidence | Verdict |
|---|---|---|
| Exact-wire equality via independent json.loads | test:201–210 — recomputes expected paths from the raw fixture bytes, never from the module | PASS |
| High-precision / integer / negative passthrough | test:481–495 (992185.54514055 exact; 1000→1000.0; -0.000001 exact) | PASS |
| Page provenance schema complete | test:498–512 (raw_digest, request_url, retrieved_at, correlation_id, source_id, layer, attribution, crs, wkid/latest_wkid, geometry_type, units, contract_version) | PASS |
| Paged-query provenance complete | test:537–555 (metadata_request_url, source freshness ms + RFC3339 — I independently verified 1764617995374 ms == 2025-12-01T19:39:55Z and that the fixture's `editingInfo.dataLastEditDate` is exactly that value — raw_digests, page_urls, drift_signals, crs, per-page linkage, exceeded flag) | PASS |

## 3. Tautology verdict: **CLEAN**

All expected values are literals hand-derived from the wire: I re-derived every fixture-driven literal (OBJECTIDs, path/vertex counts, first-vertex floats, streetwidths, metadata lastEditDate, geometryType, spatialReference, units) by independently parsing the pinned fixture bytes — all match. The exact-wire test computes its expectation from raw `json.loads` of the body, not from the code under test. `raw_body_digest` is used as oracle for digest passthrough — that helper is accepted M4-T015 surface, not under review, so this proves passthrough rather than self-confirming. No test derives an expectation by calling the module under test.

## 4. Isolation/hygiene verdict: **CLEAN**

- **Fully offline, proven**: I re-ran the 39 tests with `socket.socket.connect`/`connect_ex` monkeypatched to raise — 39 passed (exit 0). `default_fetch` is imported only for the identity assertion; every parse consumes an in-memory `DcmTransport`; paged tests inject the counting fetcher.
- **No fixture mutation**: fixtures opened read-only (test:56–58); sha256 of both fixture files after all my runs == pre-run extraction copies (True/True). Material commit touches no `tests/fixtures/**` path.
- **Order independence**: 39 passed with collection order fully reversed (exit 0).
- **No shared mutable state**: helpers build fresh dicts per call; `AUTHORITATIVE_SR` is copied via `dict()` (test:123); parametrize-time feature dicts are only ever serialized via `json.dumps`, never mutated.

## 5. Count + regression audit

- `--collect-only -q` → **39 tests collected**; hand count 18 plain + 8 CRS params + 13 taxonomy params = 39. Claim matches.
- Full connectors suite at pinned content: **752 passed** (see §6 for the one extraction artifact).
- Accepted suites untouched: material commit's name-status = exactly the 3 allowed files; accepted transport `dcm_street_centerline_arcgis.py`, all other connectors, and all fixtures byte-unchanged by ba301b67.

## 6. What I executed vs inspected

Executed (all on a byte-exact `git archive 16272c05` extraction of `services/api` + `packages/contracts` in the scratchpad; local Python 3.11.9, pytest 8.4.2, shapely 2.0.7, ruff 0.13.0):
- `python -m pytest tests/connectors/test_dcm_street_centerline_geometry.py -q` → **39 passed in 0.27s**
- `python -m pytest tests/connectors -q` → first run 751 passed + 1 error (`test_pluto_soda` reads `packages/contracts/schemas/v1/source_fact.schema.json` from repo root, absent from my partial extraction — **my artifact, not a defect**); after extracting `packages/contracts`: **752 passed in 2.51s**
- `python -m ruff check .` from services/api → ruff 0.13.0, **All checks passed!**, exit 0
- Socket-blocked run (39 passed), reversed-order run (39 passed), collect-only (39), AST-mutation non-vacuity demo, fixture-hash immutability, fixture fact re-derivation.

Inspected only: module (573 lines), test file (577 lines), accepted transport module (parse_segment_page, metadata validator, error taxonomy), packet, producer report count claims (consistent with my runs), pre-commit placeholders.

Not executable in my sandbox: `python tools/modularity_check.py --check` (requires a live git checkout — `git ls-files` fails on an extraction; primary-checkout git redirection is guard-blocked). Producer reports 0 failures / 17 pre-existing warnings; **CI on the pinned head is the authoritative confirm** — orchestrator already holds acceptance on CI. By inspection the new module is a single-responsibility 573-line sibling (the mappluto_lot_outline precedent), no modularity concern.

Deviation disclosed: local interpreter is 3.11.9 vs the repo's `requires-python >=3.12`; the entire connectors tree collected and passed regardless. CI (3.12) on 16272c05 remains the authoritative environment run.

## 7. Directive/requirement verification (this lane's observations; DCV owns the authoritative pass)

| Requirement ID | Reviewed SHA / content identity | Verdict (this lane) | Reproduced evidence |
|---|---|---|---|
| D-045-R002 | 16272c05 / blobs §0 | PASS | Harness expectation "never a rule computing on guessed geometry / absence stays honest" is proven executable: CRS 8-variant fail-closed matrix necessarily exercising the new gate; 13-condition typed-absence taxonomy with visible refused entries; no repair/coercion; passthrough integrity — all reproduced green |
| D-045-R008 | 16272c05 | PASS | Bounded single-family packet under G0/G3/G4; material commit = exactly the 3 contracted files |
| D-045-R009 | 16272c05 | PASS | Scope-limit preserved from this lane: no rule/ruleset touched, accepted connectors byte-unchanged, zero new dependencies (import allowlist proven), nothing published |
| D-046-R001 | 16272c05 | PASS | Producer ran in isolated worktree wt-m4t020; material surface = its own disjoint scope |
| D-046-R002 | 16272c05 | PASS | Commit's file set ⊆ allowed_paths exactly; no shared surface edited |

## 8. Findings

**Blocking (F):** none.

**Non-blocking:**
- **NB-1** — Untested taxonomy branch: a `paths` entry that is itself not a list (e.g. `{"paths": ["abc"]}`) → `GEOMETRY_MALFORMED_OBJECT` / `path_0_not_a_list:str` (module:236–241) has no parametrized case. The packet's S3 list doesn't name it (it's a producer-added extra branch), so non-blocking; a follow-up param case would close the branch.
- **NB-2** — The three documented "unreachable in practice" pairing guards (module:422–431, 524–536, 545–554) are untested; they cannot be reached without violating the accepted module's own invariants. Acceptable as defensive fail-closed code; noted only.
- **NB-3** — `units` fallback to `None` on absent/non-dict `geometryProperties` (module:453–459) untested. Trivial.
- **NB-4** — The forbidden-token scan can in principle be dodged by split string literals; defense in depth closes it (import allowlist blocks any HTTP client, counting seam proves transport counts). Informational.
- **NB-5** — Dispatch wording "13 conditions each land on a DISTINCT typed status": strictly the 13 map onto 7 statuses; distinctness holds at the typed (status, finding) level, 13/13 distinct, matching the packet's "distinct TYPED state or error". Clarification, not a defect.

## 9. Required rework

None for this gate. NB-1/NB-3 are candidates for an ordinary follow-up, not rework of M4-T020.

## 10. Reviewer conclusion

Content identity confirmed (ba301b67 ≡ d7766b8d ≡ pin 16272c05 on all three material blobs; only the 3 allowed files changed). The 39-test file is genuinely adequate for S1–S4: every fixture literal independently re-derived from the wire, the guard tests demonstrably non-vacuous (mutation-checked), the CRS matrix provably exercises the new module (not the upstream transport), the taxonomy is distinct/visible/no-repair, and the suite is offline, order-independent, and fixture-immutable — all reproduced executable by this reviewer at pinned content (39 / 752 / ruff clean). Local runs are the interim check; CI on 16272c05 (in flight) remains the acceptance hold.

**Verdict: PASS**
