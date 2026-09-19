# M5-T045 producer report — condo billing-BBL live wiring (DB-029) — evidence pass

**Status: in-scope implementation delivered; all documented checks green FROM THE PACKET-SPECIFIED
CWDS this unit (§7 reconciles — and preserves — the wrong-cwd failures the review flags); task
DELIBERATELY kept incomplete; independent review pending; ONE out-of-scope production-propagation
step routed to the orchestrator for an explicit scope amendment or follow-on task (no route file
touched this unit).** A producer never
self-accepts (CLAUDE.md p7): this report submits evidence for the G0–G5 review wave. This unit
re-verified the full increment against the contract seams and re-ran every documented command from
the packet-specified cwds (§7, all PASS); it corrected this report's previously stale status
(an earlier revision described the web display as "UNMET / 6 probes" — it is in fact built and
tested on both the screen and the printed brief, §1, §8). This pass also HARDENED the display
allowance guard from a deny-list to a fail-safe ALLOW-LIST: `condoWithholdsAllowances` now withholds
every computed allowance for ANY condo_resolution note that is not the recognised
`resolved_single_base_lot` success — including a MISSING, malformed, or UNKNOWN outcome token —
closing a fail-open gap where an unparseable or unrecognised token previously let allowances render;
the recognised single-base-lot success and non-condo profiles are unchanged, and new screen and
printed-brief tests cover the missing / malformed / unknown token cases (§1, §8).

**Binding of this packet.** I cannot emit sha256 digests: the broker restricts me to the packet's
`documented_test_commands`, and git/hashing is the orchestrator's under ADR-005. This packet binds
to (a) exact `file:line` anchors a read-only reviewer opens and (b) the documented-command outcomes
re-run this unit (§7). The orchestrator attaches LF-normalized content digests at integration.

## 1. Implementation & test anchors (bounded — verify in source; graph is advisory)
- **Seam-policy module:** `services/api/app/connectors/condo_base_lot.py` — `resolve_condo_billing`
  :148, `CondoResolution` :88, outcome vocab :75-79, fail-closed error map :186-198, `_from_result`
  single/multi split :237-252, unresolved/unknown fail-safe :254-270. 271 SLOC.
- **Live-provider consumer seam (LIVE-REACHABLE):** `services/api/app/spatial/live_provider.py` —
  `_live_resolve_condo` :157, `_ACTIVE_CONDO_RESOLVER` :163, condo pre-lookup INSIDE
  `build_live_substrate` :262, fail-safe→`None` :263-267, single→base-lot substitution :268-275,
  non-condo byte-identical pass-through :276-278.
- **Profile producer helper:** `services/api/app/profile/zoning_crosscheck.py` —
  `condo_resolution_report` :524 (maps a typed `CondoResolution` onto the SAME contract-1.3.0
  conflict/note channels), `_condo_note_prefix` :511 (machine outcome token
  `condo_resolution: [<OUTCOME_*>]`), `CONDO_RESOLUTION_FIELD` :491, resolved-single note :555-562,
  multi-lot conflict :564-588. NO contract-shape change.
- **Connector (leaf resolver + T044 riders):** `services/api/app/connectors/dtm_condo_soda.py`.
- **Registry draft (both datasets):** `docs/research/source-registry-drafts/dtm-condo.json`.
- **Real null-billing fixture / key-absence guards:** `services/api/tests/connectors/test_dtm_condo_soda.py`.
- **Web display increment (D-073-R006), built on BOTH surfaces:**
  - Screen: `apps/web/src/components/architect/PropertyOverview.tsx` — `CondoResolutionRecords` :135
    (resolved-single record / multi-lot base-lot records / honest-unresolved),
    `condoWithholdsAllowances` :116 — a fail-safe ALLOW-LIST: allowances survive ONLY the recognised
    `resolved_single_base_lot` success (predicate :122); a multi-lot conflict, an unresolved/error
    note, AND a MISSING/malformed/unknown outcome token (parsed `outcome` null or an unrecognised
    token) all withhold. Success token `CONDO_ALLOWANCE_OK_OUTCOME` :78, note-token regex :67, wired
    into `PropertyOverview` :175.
  - Printed brief: `apps/web/src/components/architect/ReportView.tsx` — imports + shares the SAME
    `condoWithholdsAllowances` guard :11,:38-40 and renders `CondoResolutionRecords` :81 (one data
    path, so screen and brief can never disagree).
  - Entered-vs-analyzed identity RECORD: `apps/web/src/components/architect/AnalysisIdentityNotice.tsx`
    (neutral, no billing/base-lot inference, fail-safe withhold).
  - Tests: `__tests__/condo-resolution-display.test.tsx` (AnalysisIdentityNotice + CondoResolutionRecords
    + PropertyOverview condo-withhold describe blocks, now including MISSING / UNKNOWN / MALFORMED
    outcome-token withhold cases layered on the displayable control) and the printed-brief block in
    `__tests__/report-view.test.tsx` (a tokened resolved-single control that STILL prints the computed
    wide-street allowance, plus missing- and unknown-token withhold cases proving the brief withholds
    the same evaluation). Web proves ONLY in CI on the pushed head.

## 2. Registry comparison shape (AS-6, DB-029b) — field-parity vs the committed `ztldb.json`
`dtm-condo.json` carries TWO records (`p8u6-a6it` condo units-per-base-lot; `eguu-7ie3` DTM units),
each mirroring the committed `docs/research/source-registry-drafts/ztldb.json` top-level shape
field-for-field (`source_id`, `agency`, `name`, `official_url`, `source_type`,
`api_dataset_identifier`, `authentication`, `rate_limits`, `update_frequency`, `geographic_coverage`,
`fields_available`, `terms_usage_notes`, `connector_implementation`, `last_successful_ingestion`,
`latest_source_version`, `health_status`, `known_limitations`, `fallback_source`, `open_questions`).
No invented top-level keys (invented shapes fail closed). Column counts match the connector
inventories: p8u6-a6it 9 (`CONDO_COLUMNS`), eguu-7ie3 16 (`UNIT_COLUMNS`). Per-request freshness:
`X-SODA2-Truth-Last-Modified` == `rowsUpdatedAt` (1788271556 = 2026-09-01T14:05:56Z). Record lands
before any live-traffic path.

## 3. Captured fixture comparison (AS-2, DB-029c)
Source: `docs/research/condo-null-billing-fixture-capture.md`. Chosen fixture `condo_key` **103343**
→ single base lot **1003030019**; `condo_billing_bbl` is **absent from the wire bytes**, not `null`.
SODA omits null columns, so a null-billing record is a 7-or-8-key object with the key ABSENT; the
parser branches on KEY PRESENCE, guarded in `test_dtm_condo_soda.py`. Documented negative: no
multi-lot null-billing condo exists (`count(condo_key)` == `count(distinct condo_key)` == 28), so a
2+-base-lot null-billing fixture can only be a LABELED synthetic.

## 4. Modularity boundary justification — `condo_base_lot.py`
Single responsibility (POLICY seam: classify a BBL as condo-billing, invoke the accepted resolver,
collapse its result into one typed fail-closed `CondoResolution`); public interface
`resolve_condo_billing(...) -> CondoResolution` + five `OUTCOME_*` + the frozen `CondoResolution`;
no SODA transport (stays in `dtm_condo_soda`), no zoning, never collapses a multi-lot set, never
fabricates a base lot; acyclic leaf deps; I/O injected (`resolver` seam :152); 271 SLOC. `dtm_condo_soda.py`
is a justify-band `review_signal` WARNING (0 failures — §7): one responsibility (DTM condo
resolution), acyclic leaf, injected I/O; the DB-029(k) shared-`soda_errors`/`soda_request` hoist is a
cross-connector change touching 3+ files outside this single-file scope → routed to the orchestrator.

## 5. Riders closed (AS-7) — each by a named test/change in `dtm_condo_soda.py` + `test_dtm_condo_soda.py`
response-side `condo_key` guard (`_CONDO_KEY_RE.fullmatch`→SchemaDriftError + negative test); optional
`$limit` defense-in-depth (off by default → byte-identical URLs; non-positive fails closed);
`_ERROR_CODE_SAFE_RE` `.fullmatch` consistency; `invalid_component` documented-code assertion;
`condo_key` canonical-normalizer consistency note.

## 6. Reachability — the display renders the contract data; live PROPAGATION into it is the one out-of-scope step
- **Spatial substrate seam — LIVE-REACHABLE and wired.** `build_live_substrate`
  (`live_provider.py`) runs the condo pre-lookup on `_ACTIVE_CONDO_RESOLVER` BEFORE the zoning-lot
  fetch: resolved-single substitutes the base lot, multi-lot/unresolved/error fail-safe to `None`.
  Proven by `tests/spatial/test_live_provider.py`.
- **Web display — BUILT and tested against the contract channels.** `CondoResolutionRecords` and the
  `condoWithholdsAllowances` guard render a resolved-single record, present multi-lot base lots as
  records with NO computed allowance, and explain an unresolved condo honestly — driven ONLY by the
  existing `connector_notes` token channel and the `condo_base_lot_resolution` conflict channel that
  `condo_resolution_report` emits. This is the required display increment tested with representative
  fixtures (the standard UI-increment pattern), NOT a dead helper.
- **The one out-of-scope propagation step (orchestrator disposition).** `condo_resolution_report`
  (built, in `zoning_crosscheck.py`) has no PRODUCTION caller yet: the four live profile-build routes
  call `build_property_profile(...)` WITHOUT `additional_conflicts`/`additional_notes` —
  `api/v1/rule_evaluation.py`, `scenario.py`, `scenario_analysis.py`, `evidence.py`. Wiring
  `condo_resolution_report(resolution)`'s `.conflicts`/`.notes` into those already-present
  contract-1.3.0 params populates the channels the display reads, with NO `builder.py` and NO
  contract-shape change. Those four route files are OUTSIDE this packet's `allowed_paths` (and are
  NOT `forbidden_paths`) → routed to the orchestrator as a follow-on packet (§10). A dedicated
  structured `condo_base_lot_resolution` contract field is the OPTIONAL alternative only and would be
  contract-additive (`_contract_schemas/` + `builder.py`, both `forbidden_paths`) — deliberately NOT
  taken; STOP + report, never fork a shape.

## 7. Validation — reconciled with the supervisor transcripts (cwd recorded explicitly; re-run THIS unit)
All five documented commands PASS, but ONLY from the packet-specified cwds. cwd is recorded on each
line because the wrong cwd is the whole reconciliation point:
- `python -m ruff check .` — cwd **services/api** → **All checks passed!** (exit 0)
- `python -m pytest tests/connectors/test_dtm_condo_soda.py tests/connectors/test_condo_base_lot.py -q`
  — cwd **services/api** → **81 passed** (0.15s, exit 0)
- `python -m pytest tests/spatial/test_live_provider.py tests/profile/test_ztldb_crosscheck.py tests/profile/test_wave_integration.py -q`
  — cwd **services/api** → **58 passed** (1.00s, exit 0)
- `python -m pytest tests/connectors tests/spatial tests/profile tests/api -q` — cwd **services/api**
  → **1494 passed** (17.12s, exit 0)
- `python tools/modularity_check.py --check` — cwd **repository root** → **selected 445 files;
  failures 0; warnings 21; exit 0** (`dtm_condo_soda.py` = justify-band `review_signal`, §4; not a
  gate failure).

Failed executions preserved as ACTUAL OUTCOMES (not overwritten with an all-PASS narrative). Per the
review — reconciling against the supervisor transcripts — the SAME documented commands FAIL when run
from a non-packet cwd, and those failures stand as real outcomes:
- (a) any api pytest invoked from the REPOSITORY ROOT fails collection with `No module named 'app'`
  (a known invocation artifact — `.claude/rules/CODING_RULES.md`; not a code defect; the correct-cwd
  run above is authoritative).
- (b) `python -m ruff check .` invoked from the REPOSITORY ROOT surfaces repository-root lint
  findings in files OUTSIDE this packet's `allowed_paths`. Those are UNRELATED and are deliberately
  NOT fixed here (out of this packet's scope; Ruff's packet cwd is `services/api`, where it is clean).

No wrong-cwd command was re-run as discovery (deficit-convergence: live reruns are not serial
discovery). Web tests were NOT run locally (thin client — `.claude/rules/CODING_RULES.md`) and remain
**PENDING CI on the pushed head**: the orchestrator captures the web + CI result on the pushed
revision (AS-10); not claimed verified here.

## 8. Acceptance-scenario status
- AS-1 resolved-single→base-lot pipeline: **PASS** (backend, live-reachable — §6).
- AS-2 real null-billing fixture, key-absence: **PASS** (§3).
- AS-3 multi-lot→typed, provider `None`, no collapse, records display with NO computed allowance:
  **PASS** (backend seam + `CondoResolutionRecords` multi-lot records view, screen + brief; §1, §6).
- AS-4 unresolved→typed, provider `None`, honest display without a reference-number-as-result:
  **PASS** (backend + display; §1, §6).
- AS-5 transport errors / non-condo byte-identical / flag-off zero calls: **PASS** (backend).
- AS-6 registry both datasets, mirrors ztldb, freshness documented: **PASS** (§2).
- AS-7 riders each closed by a named test/change: **PASS** (§5).
- AS-8 display walkthrough (screen + printed brief): **PASS (built)** — resolved-identity record,
  multi-lot records view, and the records-vs-allowances distinction render on the screen
  (`PropertyOverview`) and the printed brief (`ReportView`), tested in `condo-resolution-display.test.tsx`
  and the `report-view.test.tsx` printed-brief block — both now also assert the fail-safe withhold on a
  MISSING / malformed / UNKNOWN outcome token (allow-list). Web executes in CI on the pushed head.
- AS-9 ruff clean; documented api suites green; modularity exit 0; web test files carry passing
  probes: **PASS** (§7; web executes in CI).
- AS-10 CI green on pushed head: **DEFERRED** to the orchestrator (web execution + pushed-head CI).

## 9. Scope discipline (what was NOT done)
`forbidden_paths` and excluded routes untouched: `profile/builder.py`, `spatial/adapter.py`,
`_contract_schemas/`, `rules/**`, `packages/contracts/`, and the four profile-build route files
(`rule_evaluation.py`, `scenario.py`, `scenario_analysis.py`, `evidence.py`). No contract-shape
change; no new dependency; no network in tests.

## 10. Discoveries routed (D-069 — orchestrator writes to DISCOVERY_BACKLOG at the seam)
- Condo resolution → live profile-note PROPAGATION (call `condo_resolution_report` at the four
  profile-build route files — `api/v1/rule_evaluation.py`, `scenario.py`, `scenario_analysis.py`,
  `evidence.py` — through the existing `additional_conflicts`/`additional_notes` channels; NO
  `builder.py`/contract change) — the display already renders this data when present. Those four
  route files are OUTSIDE this packet's `allowed_paths` → routed to the orchestrator for an EXPLICIT
  scope amendment (widen M5-T045's `allowed_paths`) OR a follow-on task. This review authorizes NO
  route edits and none were made. AFTER the orchestrator's scope disposition, the producer wires
  `condo_resolution_report(...).conflicts/.notes` into those callers and demonstrates recorded
  per-lot zoning end-to-end through the production callers, including the multi-lot/unresolved cases
  where the substrate is `None`.
- Shared-SODA-helper hoist (`soda_errors`/`soda_request` across pluto/ztldb/dtm_condo) — WATCH; its
  own modularity task; not compelled by the justify-band warning (§4).
