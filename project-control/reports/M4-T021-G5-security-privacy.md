# G5 Security & Privacy Gate Report — M4-T021

> Saved VERBATIM by the orchestrator from the security-reviewer agent return (2026-09-14;
> transport entity-decoding only, per the report-preservation rule). Reviewer ≠ producer.
> **Orchestrator note:** advisory A1 below is carried forward as a BINDING PRECONDITION on the
> future B7 packet (recorded in docs/WORKING_KNOWLEDGE.md alongside the G3 reviewer's
> "B7 must land as its own module" ruling), so it is not rediscovered as a fresh problem when
> B7 is scoped.

- Gate ID: G5
- Task ID: M4-T021 — B4 wide-street 100-ft buffer/intersection engine
- Reviewer: security-reviewer (independent, read-only)
- Producer: backend-engineer (orchestrator-dispatched, model claude-sonnet-5 per D-047/D-060)
- Result: **PASS**
- Clean environment/worktree used: primary checkout at pinned HEAD (no worktree needed; read-only review)

## HEAD verification

`git rev-parse HEAD` = `d9ac95968995e7094de1ed769e8f3a7a63b25902` — matches the pinned review head exactly. All content read directly from the working tree at this commit (no `git show` redirection needed).

## Acceptance criteria reviewed

Task packet `project-control/tasks/M4-T021.json` (S1–S5), module docstring, and both new files read in full: `services/api/app/connectors/wide_street_buffer_engine.py` (762 lines) and `services/api/tests/connectors/test_wide_street_buffer_engine.py` (947 lines, 40 test functions — counted and matches the packet's claimed count). This G5 pass is scoped to security/privacy per the orchestrator's charter; directive-requirement-level (D-045/D-046) compliance is not re-derived here — that is the directive-compliance-verifier's remit and is out of this review's assignment.

## Surface-by-surface: in-scope vs. demonstrably untouched

| Surface | Status | Evidence |
|---|---|---|
| Network/external calls (transport, URL building) | **IN-SCOPE, verified clean** | No `urllib`/`requests`/`socket`/`http.client` import anywhere; module imports only `shapely`, `dataclasses`, `collections.abc`, and the two accepted connectors' pure-python type/constant surfaces (wide_street_buffer_engine.py:104–137). Real AST/token-scan test exists and is genuine, not a stub — `test_module_never_reimplements_transport_or_reprojection` (test file:867–920) parses the module's own source with `ast.walk`, asserts `imported_modules` equals an exact 9-item allowlist (no transport module in it), and scans raw source text for `urllib`, `to_crs`, unit-conversion literals. I independently confirmed the same result via `grep` for `import |subprocess|socket|urllib|requests\.|eval\(|exec\(` — only the legitimate `import` lines matched. |
| Filesystem/storage access | **Demonstrably untouched** | No `open()`/file I/O in the module under test. (The test file's `open(engine.__file__, ...)` reads the *test's own target source* for the AST self-scan — that is test-harness introspection, not behavior of the module being reviewed.) |
| Secrets | **Demonstrably untouched** | No env var access, no credential/token reference; module is a pure geometry function — matches its own docstring claim ("no network I/O occurs in this module; there is nothing to leak", line 262). |
| Logging of parcel/owner-identifying values | **IN-SCOPE, verified clean** | `grep -n "logging|logger\.|print\("` over the module returned **zero matches** — there is no logging call anywhere in this file. Exception `detail=` payloads (`WrongCRSError`, `InvalidGeometryError`, `MalformedAttestationError`) carry only CRS values, status codes, field names, and static labels (e.g. `"lot polygon"`, `f"segment object_id={...}"`) — never `lot.lot_identity` (a BBL-derived label), coordinates, or `classification_basis`. Confirmed by direct read of every `detail={...}` construction (lines 494–498, 511, 526–528, 567, 585, 594–596). |
| Auth/tenancy | **N/A, demonstrably untouched** | Pure in-process function; only parameter resembling identity is `correlation_id` (an opaque string, not a credential or tenant key). No DB/Supabase import, no user/session context. |
| Deserialization of untrusted input | **N/A, demonstrably untouched** | No `json.loads`/`pickle`/`eval` in this module. All wire-format JSON parsing happens in the already-accepted, read-only upstream connectors (`dcm_street_centerline_geometry.py`, `mappluto_geometry_arcgis.py`) before this module ever receives a typed dataclass. |
| Admin/deployment behavior | **N/A, demonstrably untouched** | No config/infra changes. |
| Cross-tenant isolation, service-role secrecy, private storage, SSRF, SQL/command injection, upload controls, prompt-injection defenses, least privilege | **N/A — no such surface exists in this module** | Deterministic geometry-only function (CLAUDE.md principle 1: "no AI... deterministic code calculates"); no Supabase client, no service-role key, no storage bucket, no outbound request capability, no SQL/shell/template construction, no file upload path, no LLM call anywhere in the file. Confirmed by the same import/grep sweep above — these are legitimate N/As, not skipped checks. |
| **Untrusted-input handling (geometry from ArcGIS)** | **IN-SCOPE — substantive finding below (A1)** | See judgement below. |
| Provenance/audit-field integrity | **IN-SCOPE, verified** | See findings below. |
| Attestation-gate fail-closed correctness | **IN-SCOPE, verified — no bypass found** | See findings below. |
| Dependency/lockfile/config changes | **IN-SCOPE, verified clean** | See findings below. |

## Findings

### F-series (blocking): none found.

### A1 (advisory, non-blocking) — no input-size/complexity bound at this module's own layer; relies entirely on upstream transport caps

This is my explicit judgement on item 2 of the charter.

**What I traced:** coordinates entering this module have already passed the upstream connectors' own validation — `dcm_street_centerline_geometry.py:_extract_paths` (lines 271–280) and `mappluto_geometry_arcgis.py:_structural_rings` (lines 684–698) both reject non-numeric and non-finite (`NaN`/`Infinity`) coordinates via `math.isfinite`/`isfinite` before a `SegmentPolyline`/`GeometryAssessment` can reach `GEOMETRY_OK`/`valid`/`repaired` status. `wide_street_buffer_engine.py` then trusts that gate and performs no additional coordinate-level validation of its own — `_segment_linework` (lines 554–569) and `_lot_shapely` (lines 572–597) check only `status`/`assessment.status`, never re-inspect vertex counts or coordinate magnitude.

**What is NOT bounded at this module's own layer:**
- `len(wide_segments)` passed to `compute_wide_street_buffer_intersection` — no cap; a caller can pass an arbitrarily long sequence and the module will `.buffer()` and `unary_union()` all of them (line 718).
- Vertex count per segment path / per lot ring — no cap inside this module.
- Coordinate magnitude — validated for **finiteness only**, not for plausible EPSG:2263 NYC extent (real values are roughly x∈[900000,1080000], y∈[120000,275000]); an extreme-but-finite value (e.g. `1e15`) from a corrupted/compromised upstream response would pass the `isfinite` check and flow unchecked into `.buffer()`/`intersection()`.

**Mitigating factors I verified, not assumed:**
1. The transport layer this module's dependencies sit on top of already bounds total payload size — `app/resilience/transport.py:62` `MAX_RESPONSE_BYTES = 10 * 1024 * 1024` (10 MB per response, hard-refused above that), plus `dcm_street_centerline_arcgis.py:168` `MAX_RESULT_RECORD_COUNT = 2000` records/page and a `HARD_MAX_PAGES` page-count ceiling (`dcm_street_centerline_arcgis.py:851`). These bound the realistic worst case.
2. This exact pattern (finite-check only, no magnitude/vertex-count ceiling at the computation layer, reliance on transport-layer size caps) is the established, previously-accepted precedent in the sibling modules this task was explicitly told to reuse read-only (`mappluto_geometry_arcgis.py`, `dcm_street_centerline_geometry.py`) — this module is not introducing a new pattern, it is following the repo's existing one.
3. **This module is not yet reachable from any HTTP/request-handling path.** B7 (the rule-layer caller that would wire this into a live request) is explicitly out of scope and not yet built (task packet, "B7 wires them LAST"). There is currently no external-attacker-reachable surface at all — this is a pure library function called only in-process by future, not-yet-written code.
4. I did not execute an adversarial-input stress test (out of the permitted command set); I inspected the code paths only. No unhandled-exception path was *found* by inspection — GEOS `buffer`/`unary_union`/`intersection` do not raise on large-but-finite inputs, they degrade in performance, which is a resource-exhaustion concern rather than a crash/exception concern.

**Judgement:** advisory, not blocking, for the reasons above (no live attacker-reachable path yet; upstream transport-layer bounds exist; consistent with accepted precedent). It **should be closed before B7** wires this module behind a request handler — recommend either (a) an explicit, typed, fail-closed bound on `len(wide_segments)` and per-path vertex count at this module's own boundary (matching its own established idiom of typed refusal rather than silent computation), and/or (b) a plausible-EPSG:2263-extent magnitude sanity check alongside the existing finiteness check, made a binding requirement of B7's contract if not added here. Flagging this now so it isn't rediscovered as a fresh problem when B7 is scoped.

### Provenance/audit integrity (item 3) — verified, no gap

`source_retrieved_at`/`source_raw_digest` are carried verbatim, not recomputed or coerced, in every branch:
- Per-segment: `SegmentContribution.segment_source_retrieved_at`/`segment_source_raw_digest` assigned directly from `segment.source_retrieved_at`/`segment.source_raw_digest` in the loop (wide_street_buffer_engine.py:713–714).
- Lot-level, `STATUS_PRECONDITIONS_NOT_ATTESTED` branch: `lot_source_retrieved_at=lot.source_retrieved_at, lot_source_raw_digest=lot.source_raw_digest` (lines 667–668) — **the refusal branch still carries provenance**, closing exactly the "a refusal that loses provenance is an audit gap" risk named in the charter.
- Lot-level, `STATUS_NO_WIDE_SEGMENTS_PROVIDED` (EC-6) branch: same fields at lines 691–692.
- Lot-level, `STATUS_COMPUTED` branch: same fields at lines 741–742.

Tests are non-tautological: `test_segment_contribution_carries_source_provenance_passthrough` (test file:269–283) and the three `test_result_carries_lot_source_provenance_passthrough_when_*` tests (302–342) assert equality against the **input fixture's own field** (with an explicit sanity assertion that the fixture value is non-null first), not a hardcoded literal, and a fourth test proves explicit `None` is preserved rather than coerced (285–299). I read these assertions directly rather than trusting the producer's claim.

### Attestation-gate fail-closed correctness (item 4) — verified, no bypass found

Traced the full call order in `compute_wide_street_buffer_intersection` (lines 603–743):
1. `_validate_ec5_preconditions` (line 630) runs first — rejects non-`Ec5AttestedPreconditions` instances and non-strict-`bool` field values (`isinstance(value, bool)`, lines 519) with `MalformedAttestationError`, **before any geometry is touched**. This closes the "truthy non-bool stand-in" bypass I specifically tried to find (e.g. passing `1`/`"yes"` for a checked field) — a non-`bool` is caught here, not silently treated as truthy in the later value check.
2. Lot CRS/geometry validated (lines 632–634).
3. `_ec5_precondition_failures` (line 636) — the **value** gate: if either `named_street_override_checked` or `alternate_width_clause_checked` is `False`, the function returns `STATUS_PRECONDITIONS_NOT_ATTESTED` immediately (lines 637–669), **before any segment is examined**.
4. Only after both gates pass does execution reach the EC-6 empty check and then the segment loop; `STATUS_COMPUTED` is returned only at the single terminal `return` (lines 722–743), which is unreachable unless both prior gates passed.

I could not construct an input shape that reaches `STATUS_COMPUTED` with a `False` or malformed attestation field. The dataclass has no defaults (confirmed live: `Ec5AttestedPreconditions()` raises `TypeError` per `test_ec5_preconditions_dataclass_has_no_defaults`, test file:533–535), so omission is also structurally impossible, not just logically gated.

### Dependency/lockfile/config (item 5) — verified clean

`git log --oneline` over the three allowed_paths shows exactly 4 commits for the full task lineage (contract → producer → rework → G4-delta); `git show --stat` on each confirms the file set touched is exactly the 3 allowed_paths plus orchestrator-owned control-plane files (task packet, directive manifests, gate/producer reports) — never `services/api/pyproject.toml`, `requirements.in`/`requirements.txt`, or `packages/**`. A direct `git diff --stat` over those paths across the lineage returned no output (no changes). Shapely is imported and used but not newly declared anywhere; it is the already-admitted 2.0.7 pin, consistent with the module's own import-time version assertion (lines 753–762) against `PINNED_SHAPELY_VERSION`/`PINNED_GEOS_VERSION_STRING` re-exported from the accepted `mappluto_geometry_arcgis` module.

## Steps independently executed

- `git rev-parse HEAD` → `d9ac9596...` (matches pinned head).
- `python -m pytest services/api/tests/connectors -q` → **792 passed** (matches expected count; includes the 40 new M4-T021 tests).
- `python -m ruff check .` (from `services/api`) → **All checks passed!**
- `python tools/modularity_check.py --check` (from repo root) → **failures 0; warnings 18**, including `warn review_signal: services/api/app/connectors/wide_street_buffer_engine.py - above the warning threshold`. This is non-blocking (0 failures) and is a G3/modularity-policy signal, not a G5 security matter; noting it for completeness only — it was already disclosed in the producer's progress log and does not affect this verdict.
- `grep` sweeps for network/subprocess/eval/logging tokens across the module (zero hits beyond legitimate `import` statements).
- Full read of both new files (762 + 947 lines) and the two upstream connector files this module imports from, to independently verify their own coordinate-validation behavior (finite-only, no magnitude bound) rather than trusting the module's docstring claims.
- `git show --stat` on all 4 commits in the M4-T021 lineage to verify file-scope discipline.

## Evidence paths

- `services/api/app/connectors/wide_street_buffer_engine.py` (reviewed in full)
- `services/api/tests/connectors/test_wide_street_buffer_engine.py` (reviewed in full)
- `services/api/app/connectors/mappluto_geometry_arcgis.py` (upstream dependency, read for validation behavior — lines 1–1365)
- `services/api/app/connectors/dcm_street_centerline_geometry.py` (upstream dependency, read in full)
- `services/api/app/resilience/transport.py` (transport-layer size bound, grepped)
- `services/api/app/connectors/dcm_street_centerline_arcgis.py` (page/record bounds, grepped)
- `project-control/tasks/M4-T021.json`

## Reviewer conclusion

No blocking security or privacy findings. The module is a pure, deterministic, network-free, log-free, secret-free geometry function whose only genuine security-relevant surfaces (untrusted-geometry handling, provenance passthrough, and the legal-precondition attestation gate) were each independently traced to source and hold up: the attestation gate is provably fail-closed with no bypass found; provenance fields are threaded verbatim into every return branch including refusals; no parcel/owner-identifying value reaches any log (there is no logging in this module at all); and no new dependency or config change rides along. One advisory (A1) is recorded — this module has no size/complexity bound of its own against adversarially-large upstream geometry, relying entirely on upstream transport-layer caps and matching existing repo precedent — non-blocking today because the module has no live attacker-reachable path yet, but it should be closed before the future B7 packet wires this engine behind a request handler.

**Verdict: PASS.**
