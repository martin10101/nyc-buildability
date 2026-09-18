# M5-T035 — Producer report (DB-015: live wide-street determination provider)

**Task:** M5-T035 · **Type:** backend · **Producer:** backend-engineer ·
**Worktree:** `wt-m5t035` · **Branch:** `task/M5-T035-live-wide-street-provider`

> Honesty framing (read first). This is a producer's evidence return, not an
> acceptance. The producer is not the verifier; the G1–G5 gates and the
> qualified-human G6 decide, not this report. Observations are stated separately
> from conclusions. No claim of exhaustiveness or "the only cause" is made.
> Every material claim carries its evidence (a test name, a `file:line`, or a
> command output). What I ran this session is stated separately from what CI
> will prove. Items I could not verify from primary evidence are marked
> **UNVERIFIED**. Nothing here declares the task complete or compliant.

---

## 0. Attribution — who ran what

- **This session (run 41) I executed** the commands in §2 and observed their
  outputs directly. Those outputs are mine.
- **The prior run (run 40) built most of the implementation** already present in
  this worktree (the provider module, the connector envelope predicate, the
  DB-013 engine ceilings, the endpoint M5-T035 tests, and the deploy-checklist
  rows). Any passing runs recorded before this session were produced under the
  **supervisor**, not by me; I did not re-attribute them to myself. This session
  I re-ran the documented suites fresh (§2) and built only the increment in §1.
- **CI on the pushed head is the executable authority for AS-7.** I did not push
  and I do not claim CI-green; the orchestrator captures CI at the seam. My local
  suite runs (§2) are corroborating, not the CI authority.
- **This is a revision pass** responding to a producer-return review. Its edits
  are confined to THIS report file: (1) I removed an unsupported inference about
  the local interpreter version from §2 (see §2, last bullet); (2) I demonstrated
  from the response-contract source whether the wide-row/provenance assertions can
  be satisfied through the *existing* `rule_evaluation @ 1.0.0` contract, and kept
  the AS-3 structured-provenance sub-criterion **unresolved** rather than closing
  or waiving it (§4); and (3) I rewrote §7 into a bounded, evidence-bound packet
  for the supervisor seam. No production or test file changed in this pass; the §2
  outcomes are therefore unchanged, and I re-ran all six documented commands this
  session to confirm (§2).

---

## 1. The producer increment (on top of the run-40 build)

These two edits were made in the producer pass (both inside `allowed_paths`) and
are present in the worktree; this revision pass did not change them or any other
production/test file (§0):

1. **`services/api/tests/api/test_rule_evaluation_api.py` — import ordering.**
   The `app.rules.wide_street_wiring` import block sat *after* the `app.spatial`
   imports (a deliberate placement in run 40, with an explanatory comment inside
   the import section) and failed `ruff`'s isort (`I001`). I relocated the
   `app.rules.wide_street_wiring` statements into sorted position (after
   `app.rules.snapshots`, before `app.spatial`) and moved the explanatory comment
   out of the import block to just below it. Evidence: `ruff` now clean (§2, item 1).
   - *Observation:* ruff config has no `[tool.ruff.lint.isort]` override
     (`services/api/pyproject.toml:77-82`), so defaults apply (combine-as-imports
     false → aliased imports stay as separate statements; order-by-type true).
     That is why the block is 7 separate `from … import` statements, ordered by
     imported name.

2. **`services/api/tests/spatial/test_wide_street_live_provider.py` — payload-only
   logging coverage.** Added `import logging` and two tests asserting the provider's
   fail-safe log *line*, complementing the existing `None`-return assertions:
   - `test_typed_connector_error_logs_payload_only_never_str_exc` — a typed
     `UpstreamError` whose message is a **canary** (`"canary-wide-street-detail"`);
     asserts exactly one `fail_safe` line containing `event=segment_connector_error`,
     `error_type=UpstreamError`, `correlation_id=<the request cid>`, and that the
     canary text is **absent** (exception-text exclusion; `str(exc)` is never logged).
   - `test_zero_segment_fail_safe_logs_payload_only_with_correlation_id` — the
     no-exception honest-absence branch; asserts one line with
     `event=no_segments_in_envelope`, `error_type=none`, and the correlation id.
   - *Basis in source:* `app/spatial/wide_street_live_provider.py:231-239`
     (`_fail_safe` logs `event`, `type(exc).__name__` or `"none"`, and
     `correlation_id`; never `str(exc)`).

Everything else in `outputs` was authored in run 40 and is present in the
worktree. Those files were **verified** (reads + the §2 suites) and not
re-authored; where claims about them are made below they are backed by a test or a
`file:line`.

---

## 2. Commands I ran this session, and their actual outcomes

Run from the worktree root (`wt-m5t035`); these are exactly the packet's
`documented_test_commands`:

| # | Command | Outcome (observed) |
|---|---------|--------------------|
| 1 | `python -m ruff check services/api` | `All checks passed!` |
| 2 | `python -m pytest services/api/tests/spatial -q` | `76 passed` |
| 3 | `python -m pytest services/api/tests/connectors/test_dcm_street_centerline_arcgis.py -q` | `69 passed` |
| 4 | `python -m pytest services/api/tests/connectors/test_wide_street_buffer_engine.py -q` | `54 passed` |
| 5 | `python -m pytest services/api/tests/api/test_rule_evaluation_api.py -q` | `38 passed` |
| 6 | `python tools/modularity_check.py --check` | `selected 440 files; failures 0; warnings 19` |

- Suite 2 includes the two logging tests (§1) and the full provider suite; it
  passed with no failures, so both those tests pass.
- **The exact local interpreter version is UNVERIFIED.** I did not capture
  `python --version` this session. I draw **no** inference about the running
  interpreter from ruff's `target-version = "py312"`: that setting selects the
  Python version ruff *lints against*, not the interpreter that executed the
  suites, so it is not evidence of the local runtime version. Likewise a passing
  `pytest` collection does not by itself pin the interpreter to a specific
  version. The authority for the interpreter AS-7 runs under is the api CI job
  (`python-version: "3.12"`), captured by the orchestrator at the seam; the
  **local** interpreter version stays UNVERIFIED here.

---

## 3. Acceptance scenarios — observations then conclusions

For each scenario: the **observation** (what a named test / file line shows),
then the **conclusion**. AS-7 and one sub-criterion of AS-3 are NOT closed here.

- **AS-1 (flag off → None, zero connector calls, byte-identical endpoint).**
  *Observation:* `test_flag_off_returns_none_with_zero_connector_calls` and
  `test_disabled_when_absent` / `test_disabled_for_non_true_token` (provider suite);
  `test_m5t035_flag_off_default_wide_provider_zero_calls_byte_identical`
  (endpoint suite) asserts `json.dumps(live_default)==json.dumps(baseline)` and
  `recording.calls == {"lot":0,"segments":0,"geometries":0}`.
  *Conclusion:* AS-1 is exercised by passing tests (§2 suites 2, 5).

- **AS-2 (envelope predicate; guards preserved; DisallowedRequestError on bad
  envelopes).** *Observation:* the envelope test group in
  `tests/connectors/test_dcm_street_centerline_arcgis.py`
  (`test_envelope_is_mutually_exclusive_with_attribute_predicates`,
  `test_envelope_rejects_nonfinite_coordinates`, `…_absurd_magnitude`,
  `…_inverted_bounds`, `…_boolean_component`,
  `test_fetch_street_segments_refuses_bad_envelope_before_any_network_io`,
  `test_envelope_fetch_runs_metadata_first_and_returns_segments`,
  `test_envelope_fetch_preserves_the_wrong_crs_gate`,
  `…_preserves_the_paging_pathology_guard`). Source: `build_segment_query_url`
  enforces XOR predicate style (`dcm_street_centerline_arcgis.py:413-431`);
  `_validate_envelope` runs before any network I/O (`:334-390`); in
  `fetch_street_segments` the first-page URL (and thus envelope validation) is
  built **before** `fetch_layer_metadata` (`:991-1002`).
  *Conclusion:* AS-2 is exercised by passing tests (§2 suite 3); envelope
  validation precedes metadata I/O.

- **AS-3 (happy path + endpoint wide-row / professional-review).** See §4 — the
  effect surfaces, the **structured provenance does not**; one sub-criterion is
  **UNMET** and routed, not closed.

- **AS-4 (every failure/insufficiency → None + payload-only typed log; zero-segment
  is honest absence).** *Observation:* provider suite
  `test_zero_segments_in_envelope_returns_none_never_confident_not_within`,
  `test_partial_segment_page_returns_none`, `…partial_wide_geometry_page…`,
  `test_lot_connector_error_returns_none`, `test_segment_connector_error_returns_none`,
  `test_unexpected_lot_error_returns_none`, `test_unexpected_segment_error_returns_none`,
  `test_wide_geometry_connector_error_returns_none`, `test_multiple_feature_lot_returns_none`,
  plus the two new logging tests (§1).
  *Conclusion:* AS-4 is exercised by passing tests (§2 suite 2), including the
  exception-text-exclusion and correlation-id assertions.

- **AS-5 (DB-013 ceilings; typed fail-closed; modularity passes).** *Observation:*
  `wide_street_buffer_engine.py` adds `MAX_LOT_VERTICES=200_000` and
  `MAX_PATHS_PER_SEGMENT=2_000` (`:268-269`) with `_check_lot_vertex_count`
  (`:744`) run before `canonical_to_shapely` and `_check_segment_path_count`
  (`:761`) run before the MultiLineString build (`:904`); engine tests
  `test_lot_vertex_bound_beyond_raises_input_bounds`,
  `…_at_bound_is_allowed`, `test_segment_path_count_bound_beyond_raises_input_bounds`,
  `…_at_bound_is_allowed`, `test_db013_ceilings_are_above_real_world_sizes`.
  Modularity: `failures 0` (§2 suite 6).
  *Conclusion:* AS-5 is exercised by passing tests (§2 suites 4, 6); no split, no
  wiring added to the engine.

- **AS-6 (deploy-checklist rows; no real URLs; DRAFT preserved).** *Observation:*
  `docs/RENDER_INTERNAL_WEB_DEPLOY_CHECKLIST.md` §6c
  (`LIVE_WIDE_STREET_PROVIDER_ENABLED`, true-token rule, fail-safe default,
  "flag reading + typed logs decide, never the response shape alone", DRAFT/
  D-045-R009 honesty note) and §6d (`PYTHON_VERSION = 3.12.11`, DB-004 rationale).
  No real deploy URLs (placeholders only).
  *Conclusion:* the two AS-6 rows are present. *(Content review of their accuracy
  is a reviewer judgment, not asserted here.)*

- **AS-7 (ruff + suites pass; CI green on the pushed head).** *Observation:* ruff
  and the four suites pass locally (§2). *Conclusion:* the **local** half is
  green this session; **CI-green on the pushed head is NOT claimed** and is the
  orchestrator's to capture at the seam.

- **AS-8 (report meets the honesty bar).** This report is the artifact; the
  reviewers judge it.

---

## 4. AS-3 — precisely what the endpoint tests expose (and the unmet sub-criterion)

**What the two endpoint tests do.** A real typed `WideStreetDetermination` (the
same object a live provider returns) is driven through the route's DEFAULT
`get_wide_street_determination_provider` seam via a dependency override (the way
`get_spatial_substrate_provider` is overridden), closing the M5-T034 disclosed
gap that no test exercised a provider *returning* a determination through the
full endpoint:

- `test_m5t035_within_wide_determination_fires_wide_row_via_endpoint`
- `test_m5t035_professional_review_determination_escalates_coverage_via_endpoint`

**What reaches the frozen `rule_evaluation @ 1.0.0` response (observed by the
passing tests):**

- `coverage_status` — `conditional` for the within-wide case,
  `professional_review_required` for the professional-review case.
- `professional_review_required` boolean.
- A `reasons[]` entry that names the **governing FAR and the DRAFT marker**. The
  within-wide test asserts the exact string
  `"wide-street determination within_100ft_of_wide_street: the wide-street
  (higher) conditional-FAR row governs (max_residential_far 3.0); DRAFT pending
  G6. …"` (an exact reconstruction, not a substring probe).
- The rule's own DSL trace output stays the **conservative** R6 value
  (`trace["outputs"]["max_residential_far"] == 2.2`): the higher wide-street FAR
  is selected only server-side and surfaces only in `reasons`, never as the
  rule's computed output.

**What does NOT reach the response (observed by the passing tests):** the
structured wide-street row, the governing FAR, and the D-052 provenance summary.
`test_m5t035_within_wide_determination_fires_wide_row_via_endpoint` asserts:

```
for absent in ("wide_street_far_row", "wide_street_governing_far",
               "wide_street_determination"):
    assert absent not in doc
```

The test passing is direct evidence that these three keys are **absent** from the
document (`app.rules.integration.PropertyRuleEvaluation.as_dict` does not emit them).

### 4.1 Demonstration — can the wide-row/provenance assertions be satisfied through the EXISTING contract?

The returned question is whether AS-3's "wide row **with provenance surfaced**"
can be met without expanding the frozen contract. I answer it from the contract
source, separating what the existing contract *can* carry from what it *cannot*.

**Observation A — the structured block IS computed, then dropped at
serialization.** `evaluate_property` populates `wide_street_far_row`,
`wide_street_governing_far`, and a `wide_street_determination` provenance summary
on the in-memory `PropertyRuleEvaluation`
(`app/rules/integration.py:820-822`; the summary is built by `_wide_street_summary`
at `:539-560` and carries the D-052 quintuple — `source_versions`,
`matched_geometry_refs`, `interpreted_bounds_summaries`, `classification_reasons`,
plus `policy_decision_states`/`original_labels`/`draft_label`). But
`PropertyRuleEvaluation.as_dict()` — the frozen serialization surface —
**deliberately omits all three** (`:158-182`; the dataclass comment states this at
`:150-153`). `serialize_rule_evaluation` maps `as_dict()` onto the document
(`app/rules/response.py:146-165`), so the three keys never reach the response.

**Observation B — the contract is strict and closed; adding the keys is not
possible within it.** The response is validated before send by
`validate_rule_evaluation_document` against the bundled
`rule_evaluation.schema.json` (`app/rules/response.py:202-219`). That schema's
root is `"additionalProperties": false`
(`app/_contract_schemas/v1/rule_evaluation.schema.json:7`) over a fixed
`properties`/`required` set that contains **no** wide-street key, and
`contract_version` is a **CLOSED enum `["1.0.0"]`** whose own description says
"New versions are admitted only by an accepted contract task that appends to this
enum; arbitrary versions are rejected" (`:31-34`). Consequence: emitting
`wide_street_far_row` / `wide_street_governing_far` / `wide_street_determination`
at top level would fail strict validation and the endpoint would return a typed
`internal_contract_error` 500 (`app/api/v1/rule_evaluation.py:344-364`) — an
invalid 200 is impossible by design. So the structured block cannot be added under
`@ 1.0.0`.

**Observation C — `reasons[]` is not a lawful home for the structured
provenance.** `reasons` is the only open-ended array in the contract, and its own
schema description is explicit: "Human-readable reasons for the outcome … **Never
a substitute for the machine-readable fields above**"
(`rule_evaluation.schema.json:134-136`). Flattening the provenance quintuple into
`reasons` strings would (i) contradict that field's documented contract intent and
(ii) still not provide the machine-readable `wide_street_far_row` /
`wide_street_governing_far` / structured-provenance block that "the wide row with
provenance surfaced" denotes. It is not an in-contract path to the assertion.

**Conclusion of the demonstration.** Split AS-3's endpoint criterion in two:

- The determination's **effect/decision** — which row governs, professional-review
  escalation, and a human-readable reason naming the governing FAR + DRAFT — **CAN
  be and IS** satisfied through the existing contract via `coverage_status`,
  `professional_review_required`, and `reasons[]` (proven by the two passing
  endpoint tests above; this also closes the M5-T034 disclosed gap that no test
  exercised a provider *returning* a determination through the full endpoint).
- The **structured wide row + D-052 provenance quintuple** **CANNOT** be satisfied
  through the existing `@ 1.0.0` contract (Observations B and C). Surfacing it
  requires appending a new `contract_version` and additive properties — an accepted
  contract task, i.e. **DB-014**, which the packet freezes OUT of scope. **This
  sub-criterion of AS-3 is UNMET and remains UNRESOLVED here.**

**Precise conflict for orchestrator disposition (DB-014).** AS-3 requires "the wide
row **with provenance surfaced**." The frozen contract (packet-scoped as immutable;
DB-014/DB-016 listed as scope-magnets to route, never fix in-packet) provides no
machine-readable slot for that block and forbids adding one without a version bump.
The two readings of AS-3 cannot both be honored inside this packet: (1) if "wide
row surfaced" means the *decision effect* is observable, AS-3's endpoint half is
met and the structured block is a separate DB-014 deliverable; (2) if it means the
*structured block* must appear in the response, AS-3 cannot pass until DB-014 lands.
I do **not** expand the contract and I do **not** unilaterally waive AS-3; choosing
between (1) and (2) — and whether DB-014 blocks acceptance or is scheduled as
follow-on — is the orchestrator's disposition. The endpoint test's
`assert … not in doc` lines deliberately **pin the absence** so the gap stays
visible rather than being silently papered over.

---

## 5. Cohesion justifications — the two warned connector modules (modularity policy §6)

`python tools/modularity_check.py --check` (§2 suite 6) reports `failures 0` and,
among 19 warnings, flags both modules I grew this task as **above the
justification threshold** (the policy's 750-SLOC "record a cohesion justification
in review" band; both remain **below** the 1000-SLOC hard threshold, hence
`failures 0`). Recorded justifications:

- **`services/api/app/connectors/dcm_street_centerline_arcgis.py`** (~1112 raw
  lines; modularity signal: `review_signal … above the justification threshold`).
  *Single responsibility:* one official DCM street-centerline **connector** —
  URL/predicate building over fixed allowlists, metadata-first freshness pin +
  schema-drift/CRS guard, deterministic paging with pathology guards
  (repeated OBJECTIDs, byte-identical pages, page/byte ceilings), and typed
  parsing. The **envelope-intersects predicate** added here is a new *selection
  dimension of the same connector*, not a new responsibility: it reuses the
  connector's existing validation (`_validate_envelope` feeds the one
  `build_segment_query_url`), transport, paging, CRS, and freshness/drift paths
  unchanged (`:435-446`, `:982-1002`). Extracting it would fracture the connector's
  fail-closed guarantees (a predicate that bypassed the shared metadata/paging
  guards would be exactly the defect the module exists to prevent). *Cohesive;
  keep whole.* The line count and threshold classification are from the
  modularity_check output; the "no weakened guard" claim is backed by the AS-2
  tests in §3.

- **`services/api/app/connectors/wide_street_buffer_engine.py`** (~968 raw lines;
  modularity signal: `review_signal … above the justification threshold`).
  *Single responsibility:* the B4 100.0-ft-buffer ∩ lot geometry **engine** and
  its typed input-bounds / EC-precondition gates. The **DB-013 ceilings** added
  here (`MAX_LOT_VERTICES`, `MAX_PATHS_PER_SEGMENT`) are size bounds that guard
  *this engine's own* O(vertices) shapely operations before they run — they are
  cohesive with the engine's existing extent/segment/vertex bounds, not a new
  domain. Per the M5-T034 G3 ruling this task adds **only** the bounds — **no
  split, no wiring** into the engine — which the modularity `failures 0` and the
  AS-5 tests corroborate. *Cohesive; keep whole.*

*(The other 17 warnings are pre-existing modules outside this task's scope.)*

---

## 6. Discovery routing (D-069) — surfaced, not fixed in-packet

Per the packet, out-of-scope discoveries are surfaced here for the orchestrator
to record in `docs/DISCOVERY_BACKLOG.md`; I did not fix any in-packet.

- **DB-014 — wide-street contract-surface bump (SUPPORTED by source evidence;
  precise conflict in §4.1).** The frozen `rule_evaluation @ 1.0.0` response omits
  `wide_street_far_row`, `wide_street_governing_far`, and the
  `wide_street_determination` provenance block; the contract's root is
  `additionalProperties: false`, its `contract_version` is a closed enum, and its
  `reasons[]` is contractually barred from substituting for machine-readable
  fields (§4.1, Observations B–C; evidenced by the passing `assert … not in doc`).
  So the structured D-052 provenance cannot be surfaced without an **additive**
  contract bump (new `contract_version` + new properties). This is the unmet AS-3
  sub-criterion's home and the precise orchestrator-disposition conflict is stated
  in §4.1; it must not be resolved by expanding the contract in this packet.
- **DB-010 — ZR 12-10 named-street override table (existing known scope, per the
  packet risks).** The accepted stack does not implement the named-street /
  alternate-width override, so the provider leaves the B4 EC-5 preconditions
  unattested and any wide-disposed segment resolves to professional review — a
  live `within_100ft` is never fabricated (source: provider docstring `:43-57`;
  `_UNATTESTED_EC5` `:138-147`; `_NAMED_OVERRIDE_STATUS` `:153-161`). This is a
  documented boundary, not a new finding.

The following adjacent items are **UNVERIFIED** — I have not established them from
primary source evidence this session and they must not be treated as confirmed:

- **UNVERIFIED — envelope-margin adequacy.** `ENVELOPE_MARGIN_FT = 50.0` on top of
  `BUFFER_FT (100.0)` is asserted (provider `:126-132`) to make the candidate
  gather a safe superset covering rounded buffer end-caps and the sources' stated
  "±20-ft positional accuracy." I did **not** verify that the ±20-ft figure or the
  50-ft margin is a *strict geometric superset* for all lot shapes; treat the
  superset property as an assumption pending a geometric/source check.
- **UNVERIFIED — real-world size headroom of the DB-013 ceilings.** The comments
  state real NYC lots carry "at most a few thousand vertices" and DCM segments "a
  handful of paths." I did not confirm these magnitudes against a dataset; the
  ceilings are defensive bounds, and `test_db013_ceilings_are_above_real_world_sizes`
  only asserts the *constants* are large, not the real-world distribution.
- **UNVERIFIED — DB-016 (context-panel parity) and DB-001 (split-lot
  apportionment).** Named in the packet as out-of-scope scope-magnets; not
  investigated here. Listed only so they are not lost.

---

## 7. Bounded evidence packet for the supervisor seam

Provided **in place of** a broad worktree/status listing. "Bound" here means each
production change is tied to the exact test assertions and named source symbols a
read-only reviewer can verify at the frozen head — not that I computed git-object
hashes (see §7.4). The complete `allowed_paths` change set is the ten files listed
in the checkpoint `changed_files`.

### 7.1 Production changes → binding test assertions

| Production file | Change (responsibility) | Origin | Binding tests (suite → §2 result) | Source symbols |
|---|---|---|---|---|
| `app/spatial/wide_street_live_provider.py` | NEW settings-gated, orchestration-only provider; fail-safe `None` on every failure/insufficiency; payload-only typed logging (never `str(exc)`) | run 40 build + the producer-increment 2 logging tests (§1) | `tests/spatial/test_wide_street_live_provider.py` (suite 2 → **76 passed**): `test_flag_off_returns_none_with_zero_connector_calls`, `test_zero_segments_in_envelope_returns_none_never_confident_not_within`, `test_*_connector_error_returns_none`, `test_typed_connector_error_logs_payload_only_never_str_exc`, `test_zero_segment_fail_safe_logs_payload_only_with_correlation_id` | module `_fail_safe` (payload-only log: `event`, `type(exc).__name__`/`"none"`, `correlation_id`); docstring fail-safe contract `:30-57` (verified this session) |
| `app/connectors/dcm_street_centerline_arcgis.py` | NEW envelope-intersects predicate preserving the XOR-predicate rule, metadata-first freshness + schema-drift + CRS guards, paging/byte ceilings, `DisallowedRequestError` on invalid/non-finite/absurd envelopes | run 40 | `tests/connectors/test_dcm_street_centerline_arcgis.py` (suite 3 → **69 passed**): `test_envelope_is_mutually_exclusive_with_attribute_predicates`, `test_envelope_rejects_nonfinite_coordinates`/`…_absurd_magnitude`/`…_inverted_bounds`/`…_boolean_component`, `test_fetch_street_segments_refuses_bad_envelope_before_any_network_io`, `test_envelope_fetch_runs_metadata_first_and_returns_segments`, `…_preserves_the_wrong_crs_gate`, `…_preserves_the_paging_pathology_guard` | `build_segment_query_url` (XOR predicate), `_validate_envelope` (pre-I/O), envelope validation before `fetch_layer_metadata` (anchors per §3 AS-2, run-40-authored) |
| `app/connectors/wide_street_buffer_engine.py` | DB-013 ceilings `MAX_LOT_VERTICES` + `MAX_PATHS_PER_SEGMENT`, typed fail-closed, **no split, no wiring** added | run 40 | `tests/connectors/test_wide_street_buffer_engine.py` (suite 4 → **54 passed**): `test_lot_vertex_bound_beyond_raises_input_bounds`/`…_at_bound_is_allowed`, `test_segment_path_count_bound_beyond_raises_input_bounds`/`…_at_bound_is_allowed`, `test_db013_ceilings_are_above_real_world_sizes` | `_check_lot_vertex_count` (before shapely build), `_check_segment_path_count` (before MultiLineString build); constants block (anchors per §3 AS-5) |
| `app/api/v1/rule_evaluation.py` | Default provider wired to the settings-gated live provider exactly as `get_spatial_substrate_provider` wires the substrate; flag off = byte-identical endpoint behavior | run 40 | `tests/api/test_rule_evaluation_api.py` (suite 5 → **38 passed**): `test_m5t035_flag_off_default_wide_provider_zero_calls_byte_identical`, `test_m5t035_within_wide_determination_fires_wide_row_via_endpoint`, `test_m5t035_professional_review_determination_escalates_coverage_via_endpoint` | `get_wide_street_determination_provider` `:165-171`, `_default_wide_street_determination` `:150-162`, provider call + wiring `:335-338` (verified this session) |
| `docs/RENDER_INTERNAL_WEB_DEPLOY_CHECKLIST.md` | §6c `LIVE_WIDE_STREET_PROVIDER_ENABLED` row (flag + typed logs decide, never response shape) + §6d `PYTHON_VERSION = 3.12.11` pin (DB-004) | run 40 | no test — content review (AS-6); rows present at `:382` (§6c) and `:411` (§6d), verified this session; no real deploy URLs | — |

The two endpoint tests carry the **AS-3 contract-limitation annotation** and the
`assert absent not in doc` lines that pin the structured block's absence (§4.1).

### 7.2 Full cohesion justifications

The two modules the modularity checker warns (`review_signal … above the
justification threshold`, both **below** the 1000-SLOC hard bar → `failures 0`,
§2 suite 6) are `dcm_street_centerline_arcgis.py` and `wide_street_buffer_engine.py`.
Their full per-module cohesion justifications are recorded in **§5** (single
responsibility, why the new predicate / ceilings are the same responsibility, and
why extraction would fracture the module's fail-closed guarantees). Modularity
`failures 0`; no split and no wiring were added to the engine.

### 7.3 Authoritative attribution of the task-file modification

`project-control/tasks/M5-T035.json` shows **MODIFIED** in the working tree and is
**NOT** in my `allowed_paths`. Under ADR-005 the control plane
(`project-control/**` task files + `state.json`) is writable **only by the
orchestrator/controller**; producers are barred from it. The recorded lifecycle
write is the seam commit **`623e34eb`** ("claimed by backend-engineer, progress 20
(state.json staged with the claim)"). Because a producer cannot and did not touch
this file, its working-tree modification is attributable to the
**orchestrator/controller lifecycle**, not to this producer. I did **not** stage
or alter it and will not; it is left untouched.

### 7.4 Digest authority and checkpoint envelope

Authoritative content digests (sha256, LF-normalized per the checkout-CRLF-smudge
rule) of the files above are the **orchestrator's to compute at the seam**: as a
producer under the native-tool broker I cannot run `git hash-object` / `sha256sum`
(they are not this packet's `documented_test_commands`, so proposing them would
stall the run). Accordingly, per the S8.3 envelope discipline, this unit's
checkpoint leaves `starting_sha` / `current_sha` / `branch` / `worktree` **blank**
for the controller to fill with authoritative values. Reviewable-commit request
(avoid aggregate patch truncation): please carry the substantive production diffs
(the four `services/api` files) + the four test files + this report in the
reviewable commit rather than an aggregate that truncates them.

---

## 8. What is NOT claimed (open at the seam)

- **AS-7 CI-green on the pushed head** — not claimed; orchestrator-captured.
- **AS-3 structured-provenance surfacing** — UNMET at the frozen contract and
  **UNRESOLVED**; demonstrated non-satisfiable within `@ 1.0.0` (§4.1) and routed
  as DB-014 for orchestrator disposition; neither fixed, closed, nor waived here.
  (The AS-3 *effect* half and the M5-T034 disclosed-gap closure ARE met and
  tested — §4.1.)
- **Gates G1–G5 and acceptance** — for the independent reviewers and the
  orchestrator; this report is producer evidence only. The wide-street rules stay
  `needs_review` DRAFT pending G6 (D-045-R009); no published/verified/compliance
  claim is made anywhere.
