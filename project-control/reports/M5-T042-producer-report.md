# M5-T042 — producer report

**Task:** DTM condo billing-BBL → base-lot-set resolver (module only, no wiring).
**Producer:** backend-engineer. **Directive:** D-066-R001 (code-graph navigation block).
**Sole source:** `docs/research/condo-base-lot-resolution-sources.md` (DB-002, retrieved 2026-09-18).

## What was built (file references, not verbatim)

- `services/api/app/connectors/dtm_condo_soda.py` — deterministic, typed, fail-closed
  resolver. Public API: `resolve(bbl)` (`dtm_condo_soda.py:538`), `resolve_by_condo_key(condo_key)`
  (`:705`), `classify_lot(bbl)` (`:326`), result type `CondoBaseLotResult` (`:256`), error
  taxonomy `DtmCondoConnectorError`+subclasses (`:202`). Leaf module — no consumer imports.
- `services/api/tests/connectors/test_dtm_condo_soda.py` — offline suite, **26 tests**. Fixtures are
  the research raw responses embedded INLINE (packet scope is three files; no fixtures dir in
  allowed_paths), byte-faithful from research §3.3 / §4.2 / §4.3, with `condo_key=301313` derived
  faithfully (§3.3 rows both carry key 301313; §4.3 confirms {32,33}). Two synthetic fixtures
  (drift-decimal, null-billing scenario) are labeled as such and never presented as official.
  This pass added `test_c3_unit_split_matches_resolved_base_lot_set` (`test_dtm_condo_soda.py:234`) and
  `test_c6_null_billing_condo_resolves_via_condo_key_synthetic` (`:344`).

## Verified path (research §3/§4/§7)

- Billing lot 7501–7599 → `p8u6-a6it?condo_billing_bbl=` → SET of `condo_base_bbl` (never collapsed).
- Unit lot 1001–6999 → `eguu-7ie3?unit_bbl=` → base + `condo_key`, then `p8u6-a6it?condo_key=`
  expansion so a multi-lot condo returns the full set, not just the lot the unit sits on.
- `resolve_by_condo_key` = the null-billing fallback (§7 step 4a) for the 28 null-billing condos.
- else → `NOT_A_CONDO` (zero lookups). Empty/exhausted → typed `condo_base_lot_unresolved`
  (never a fabricated lot, never an exception for a well-formed input).
- Every returned base BBL is validated `^\d{10}$`; the PLUTO decimal serialization fails closed.
  PLUTO `appbbl` is NEVER consulted (banned as source, §6.1). No zoning determination; every
  resolved result carries `DIVERGENT_ZONING_NOTICE` (§7 step 6, qualified-human legal surface).

## Evidence — WORKING-TREE validation (uncommitted; committed-head CI and gates PENDING)

**Validation context (corrected):** the full module and suite live in this worktree's WORKING TREE;
HEAD carries only the M5-T042 contract-seam stubs (module stub + one passing test + report). The results
below are therefore **working-tree validation of uncommitted changes**, NOT committed-head evidence.
Committed-head CI (AS-7) and the required gates (G0–G5) are **PENDING**: the orchestrator captures them
after it commits and pushes this working tree (evidence-capture division of labor,
`.claude/rules/project-control.md`). No CI or gate pass is claimed here.

**Recaptured this pass (2026-09-18; exact cwd per the packet COMMAND-CWD binding):**
- `python -m ruff check .` — cwd `services/api` → **All checks passed!**
- `python -m pytest tests/connectors/test_dtm_condo_soda.py -q` — cwd `services/api` → **26 passed** in 0.06s.
- `python -m pytest tests/connectors -q` — cwd `services/api` → **852 passed** in 3.93s (no regression; leaf isolation).
- `python tools/modularity_check.py --check` — cwd **repo root** → **selected 443 files; failures 0; warnings 21**;
  `dtm_condo_soda.py` is one `review_signal` **warn** ("above the warning threshold") — see the cohesion note.

**CWD discipline / scope boundary (preserved, not rewritten):** the first three commands run from
`services/api` (the suites do not collect from the repo root — a known invocation artifact); the modularity
check runs from the repo root. `ruff check .` is deliberately scoped to `services/api`: running it from the
repo root would surface **pre-existing, unrelated root-level lint findings outside this packet's three-file
scope**, which are NOT this task's to fix (D-069 discovery routing) and are left untouched. Any earlier
wrong-cwd execution is preserved as-is, not overwritten by this recapture.

## Inspectability & digest-bound evidence

A read-only reviewer at HEAD sees only the contract-seam stubs, so the material implementation must be
inspectable from committed evidence. Per the evidence-capture division of labor and the "probe cannot
self-bind" rule, the producer does NOT fabricate a digest or run a non-documented hashing command: the
authoritative **sha256 (LF-normalized) full-file digest binding** for the complete connector and test —
and the byte-faithful full-content digest-bound sections — are **supplied by the supervisor/orchestrator
at commit** (they hold the committed bytes and the hashing/git authority). This section gives the reviewer
a complete inspection map and the byte-faithful research fixture excerpts so no material implementation is
truncated.

### Files (digest bound at commit)

| File | Working-tree lines | sha256 (LF-normalized) |
|---|---|---|
| `services/api/app/connectors/dtm_condo_soda.py` | 850 | supervisor-supplied at commit |
| `services/api/tests/connectors/test_dtm_condo_soda.py` | 430 | supervisor-supplied at commit |

### Connector inspection map — `dtm_condo_soda.py`

- Module docstring + permanent boundaries (billing/unit/condo_key paths; no zoning; `appbbl` banned; ArcGIS out): `:1-46`
- Public `__all__` surface: `:73-98`
- Dataset identities + `RESEARCH_OBSERVED_ROWS_UPDATED_AT` (provenance hint, never asserted fresh): `:102-117`
- Lot classification constants + `classify_lot` (fail-closed `^\d{10}$`): `:119-125`, `:326-346`
- Status/path vocab + schema-shape guards (9-col / 16-col frozensets; strict BBL + condo_key regex): `:127-186`
- `DIVERGENT_ZONING_NOTICE` (legal boundary carried on every resolved result): `:188-195`
- Error taxonomy (`DtmCondoConnectorError` + RateLimited/SchemaDrift/Timeout/Unavailable; no secrets in payloads): `:202-249`
- `CondoBaseLotResult` typed result (FULL set, never collapsed): `:255-283`
- `_request` / `_fetch_rows` (bounded retry on 429/5xx/timeout; no-such-column 400 = typed drift; JSON-array guard): `:349-464`
- `_collect_base_lots` (`^\d{10}$` per base BBL, PLUTO decimal rejected; unknown-column advisory): `:467-508`
- `_provenance_entry` (dataset id, url, retrieved_at, record_count, rows_updated_at): `:511-532`
- `resolve` (classify → billing/unit paths; condo_key expansion; honest unresolved): `:538-702`
- `resolve_by_condo_key` (null-billing fallback, research §7 step 4a): `:705-797`
- `_resolved` / `_unresolved` result builders: `:800-849`

### Test inspection map — `test_dtm_condo_soda.py` (26 tests)

- Module docstring (fixtures byte-faithful; synthetics labeled; no network I/O): `:1-24`
- Byte-faithful research fixtures + labeled synthetic fixtures: `:57-125`
- URL-routed fake transport + hermetic app-token fixture (proves no PLUTO URL requested): `:134-175`
- C1 + rows_updated_at injection: `:184-209`; C2 unit + condo_key expansion: `:212-230`; C3 unit-split cross-check: `:233-248`
- C4 / C5 / NOT_A_CONDO zero-lookup: `:251-276`; C7 shape + decimal-reject: `:279-293`; C9 appbbl independence: `:296-306`
- C10 schema-shape guard: `:309-321`; C6 mechanism + C6 synthetic null-billing: `:324-364`
- condo_key no-match / invalid-shape: `:367-383`; malformed / non-string fail-closed: `:386-403`
- determinism: `:406-410`; divergent-zoning notice + no-zoning-fields: `:413-430`

### Byte-faithful research fixture excerpts (sole source DB-002)

- **§3.3 billing** `p8u6-a6it?condo_billing_bbl=3022647515` (HTTP 200) → fixture `BILLING_3022647515_BODY` (`test:63-70`):

  ```json
  [{"condo_base_boro":"3","condo_base_block":"2264","condo_base_lot":"32","condo_base_bbl":"3022640032","condo_base_bbl_key":"3022640032301313","condo_key":"301313","condo_number":"1313","condo_billing_bbl":"3022647515"},
   {"condo_base_boro":"3","condo_base_block":"2264","condo_base_lot":"33","condo_base_bbl":"3022640033","condo_base_bbl_key":"3022640033301313","condo_key":"301313","condo_number":"1313","condo_billing_bbl":"3022647515"}]
  ```

- **§4.2 unit** `eguu-7ie3?unit_bbl=3022642601` → fixture `UNIT_3022642601_BODY` (`test:73-79`):

  ```json
  [{"condo_base_boro":"3","condo_base_block":"2264","condo_base_lot":"32","condo_base_bbl":"3022640032","condo_number":"1313","condo_key":"301313","condo_base_bbl_key":"3022640032301313","unit_boro":"3","unit_block":"2264","unit_lot":"2601","unit_bbl":"3022642601","unit_designation":"1A","model":"T","geometry_type":"Table"}]
  ```

- **§4.3 unit split** `?condo_key=301313&$select=condo_base_bbl,count(unit_bbl)&$group=condo_base_bbl` → fixture `C3_UNIT_SPLIT_BODY` (`test:104-107`):

  ```json
  [{"condo_base_bbl":"3022640032","count_unit_bbl":"14"},
   {"condo_base_bbl":"3022640033","count_unit_bbl":"6"}]
  ```

- **§3.4 null-billing:** the research records only the **aggregate count 28** of null-billing condos — it embeds
  **NO** byte-faithful raw `p8u6-a6it?condo_key=<null-billing condo>` response for any specific null-billing
  condo. That is the null-billing official-fixture gap, routed to the orchestrator below.

## Acceptance scenarios

- AS-1 → `test_c1_multi_lot_billing_resolve` (set `{3022640032,3022640033}`, path=billing, provenance).
- AS-2 → `test_c2_unit_reverse_resolve_expands_to_full_set` (base 3022640032, path=unit, condo_key expansion → full set).
- AS-3 → `test_c4_nonexistent_billing_lot_is_unresolved`, `test_c5_land_lot_is_not_a_condo_zero_lookups`.
- AS-4 → `test_malformed_bbl_fails_closed` (param), `test_non_string_bbl_fails_closed`, NOT_A_CONDO tests.
- AS-5 → `test_c7_decimal_serialization_rejected_fail_closed`, `test_c9_appbbl_independence`.
- AS-6 → ruff/suite/modularity above; no consumer file touched (leaf).
- AS-7 → CI green on pushed head — **orchestrator-captured** (thin client; not proven locally).

## Contract-test rows (research §9)

Implemented and passing: **C1, C2, C3, C4, C5, C7, C9, C10**, and **C6** (both facets).

- **C3** (unit split 14/6, total 20) — **now implemented** from the verified §4.3 grouped response
  (`test_c3_unit_split_matches_resolved_base_lot_set`). It is a units-side aggregate, so the module
  does not issue that query; the test uses the byte-faithful fixture to assert the counts (14+6=20,
  = PLUTO `unitstotal`) and cross-checks that the resolver's billing SET equals exactly the set of
  base lots the units span — corroborating C1 from the units side. No fabrication.
- **C6** (null-billing fallback) — covered two ways:
  1. **Mechanism** (`test_c6_condo_key_fallback_resolves_full_set`): the real `condo_key=301313`
     response proves `resolve_by_condo_key` returns the full set.
  2. **Null-billing scenario** (`test_c6_null_billing_condo_resolves_via_condo_key_synthetic`): a
     **clearly-labeled SYNTHETIC** fixture (`condo_billing_bbl: null`, schema-faithful) exercises the
     null-billing code path.
  - **Source limitation → ROUTED TO THE ORCHESTRATOR (owner-decision item in this checkpoint):** the
    research embeds **no** byte-faithful raw `p8u6-a6it?condo_key=<null-billing condo>` response — only
    the aggregate count **28** (§3.4). Producing an *official* null-billing fixture would require a live
    retrieval, which is out of this offline module packet; the producer must **not** fabricate official
    data or perform unauthorized live retrieval. The orchestrator resolves the contract before
    acceptance by exactly one of: (a) **authorize a one-shot research increment** to capture one real
    null-billing `condo_key` response, or (b) make an **explicit contract disposition** — accept the
    mechanism + labeled-synthetic-scenario coverage now and carry the official null-billing fixture as a
    live-era row (C-class). Flagged, not faked, not silently dropped.
- **C8, C11, C12, C13, C14** — loop-closure to ZTLDB, freshness, rate-limit, ArcGIS failover, and
  divergent-zoning surfacing are wiring/live-era rows (packet says record deferred; no fixtures faked).

## Cohesion / modularity note (warn recorded per code-architecture rule §6)

The module is a single cohesive responsibility — deterministic condo→base-lot resolution
(classification + billing/unit/condo_key query paths + one typed result). Line count is
docstring/comment-heavy (provenance and legal-boundary discipline for a legally-sensitive
connector); the checker reports it at the review-signal **warn** tier (>600 SLOC), under the 750
justification and 1,000 hard thresholds, and comparable to the accepted sibling SODA connectors
(`pluto_soda.py`, `ztldb_soda.py`). No responsibility mixing; keep as one module. The connector's
full 850-line working-tree content is new relative to the contract-seam stub at HEAD; the most recent
editing pass changed only the test file and this report.

## Deferred to the later wiring packet (out of scope here; discovery routing D-069)

- `source_registry` record + live `/api/views` freshness fetch (rowsUpdatedAt is injectable now;
  `RESEARCH_OBSERVED_ROWS_UPDATED_AT` carries the 2026-09-18 observed values as a provenance hint).
- ArcGIS failover (research §5), PLUTO `appbbl` optional cross-check flag (§6.1), property-lookup /
  ZTLDB pipeline wiring, and the divergent-zoning qualified-human surface (§7 step 6).

## Scope confirmation

Only the three allowed-path files changed. No pipeline/route wiring, no ArcGIS failover, no zoning
logic — the lane stays disjoint from the live M5-T040 wiring lane (D-066-R001 G0 disjointness).
