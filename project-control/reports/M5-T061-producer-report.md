# M5-T061 producer report — DB-039 proposal-checks route hardening

Producer: backend-engineer. Scope: `services/api/app/api/v1/proposal_checks_api.py`,
`services/api/app/api/v1/_proposal_fact_domains.py`,
`services/api/tests/api/test_proposal_checks_api.py` only. All other paths read-only. No new
dependency, no new flag. The `(200,None)/(404,None)/(413)/(422)/(500)` matrix is unchanged.

## This checkpoint (report-only) — what THIS unit changed

**Delta scope — THREE nested layers, kept distinct.** This unit is a REPORT-ONLY reconciliation
checkpoint. Its own delta is *claimed* to be EXACTLY ONE file — this report
(`project-control/reports/M5-T061-producer-report.md`) — and to have authored no test and no
production change. **That report-only authorship is a CLAIM, not a corroborated fact:** this unit
captured no checkpoint-start baseline (the pre-edit working-tree digests of all four files), so an
independent reviewer cannot confirm from this report alone that the two production modules and the
test file are byte-unchanged by this checkpoint. Because no pre-edit baseline was captured for this
checkpoint, its single-file authorship cannot be proven — and no later baseline can prove it
retroactively either: a baseline taken in a future packet binds only that packet's forward changes;
it cannot attest what this checkpoint did or did not touch. Single-file authorship therefore stays an
uncorroborated CLAIM for this checkpoint — not a fact any subsequent evidence will settle. The three
layers an independent reviewer must keep separate are:

1. **This report-only checkpoint (1 file, claimed):** `M5-T061-producer-report.md` only. This unit
   reconciled the report's delta-scope, validation-identity, evidence, and handoff sections; it
   claims to have touched no code and no test (see the authorship caveat above).
2. **The earlier two-file rework (2 files):** `tests/api/test_proposal_checks_api.py` + this report,
   authored by the prior loop-3 re-feed rework unit (the AS-4/AS-5 test changes described below).
3. **The four-file cumulative working tree (4 files):** the two above PLUS the two production
   modules `proposal_checks_api.py` and `_proposal_fact_domains.py`, which carry the prior
   implementation changes from earlier in this task — neither this checkpoint nor the two-file
   rework re-authored them.

This report does not assert that any of the carried-over changes are "accepted": M5-T061 is
`in_progress`, not accepted; acceptance is the orchestrator's ledger record, not claimed here absent
an authoritative reference. Every later use of "accepted" in this report refers to the
prior-accepted route baseline's established coverage/rectangle-arithmetic contract, never to this
task's own implementation.

**Validation identity — working tree AND HEAD.** HEAD at this checkpoint is the claim-seam commit
`a444708d`, which still carries the PLACEHOLDER report and none of the four-file delta. The content
under review therefore lives in the (uncommitted) WORKING TREE, not at HEAD. Independent validation
must bind to the reviewed working-tree contents of all four files AS WELL AS HEAD — a HEAD-only diff
would see only the placeholder. Any digest binding in the next packet must pin the working-tree
bytes (LF-normalized) of the reviewed files, not the HEAD blobs.

The earlier two-file rework replaced the two weaker "at-cap-exact" wall/street tests (which asserted
only that the cap constant was ABSENT from the response) with fixtures that assert a real end-to-end
**HTTP 200** at EXACTLY the cap — walls=500, street_lines=400, and body==`MAX_BODY_BYTES` — each
carrying a valid payload that runs the full derivation + engine (see AS-5). Above-cap typed-refusal
coverage is retained unchanged. This report's AS-5 and Evidence sections describe those actual
assertions and record the intended per-command working directories (the actual invocation cwds are
unrecorded) and the exact authoritative supervisor exit outcomes
(ruff exit 1, pytest exit 4 / no tests found, modularity exit 0); a green ruff, any pytest
pass/fail count, full-suite preservation, and CI on the pushed head are all marked PENDING the next
packet's documented transcripts (thin client — local runs prove only the working tree; CI proves the
pushed head).

## What changed (DB-039 items a/b/d/e/g/h/i)

The BP-5 caller-fact vocabulary discipline was extracted into the sibling module
`app/api/v1/_proposal_fact_domains.py` (permitted by the packet once the numeric-bound derivation
crossed the route's modularity tier). The route imports every name it needs from there; nothing in
that module imports the route (no import cycle), and a single `_FieldRefusal` identity now crosses
both modules so the handler's `except` catches refusals raised inside the extracted validators.

- **(a) DB-039(a)/G3-F5 — memoized derivation.** `_proposal_fact_domains.input_domains_for()`
  memoizes the per-registry derivation in a `weakref.WeakKeyDictionary` keyed by the registry
  object (`_INPUT_DOMAIN_CACHE`, module lines ~332–354). Once per registry object; the
  test-injected registry keys its own entry; evicts on GC. `clear_input_domain_cache()` lets tests
  start cold.
- **(b) DB-039(b)/G3-F6 — import-time guard blast-radius note.** Module docstring lines ~11–18
  document that `_assert_fact_type_table_covers_vocabulary()` runs at import and, because
  `app/main.py` imports the route unconditionally, a drift fails the WHOLE app at boot (deliberate,
  fail-closed, exceeds the feature flag).
- **(d) DB-039(d)/G5-F3 — registry-DERIVED numeric bounds.** `derive_input_domains()` (module lines
  ~258–329) extends the enum discipline to the declared `minimum/maximum/exclusive_*` `InputSpec`
  fields, with the SAME every-declaring-rule-constrains conservatism per direction and the
  MOST-PERMISSIVE kept bound (`_rule_lower/_rule_upper/_combine_lower/_combine_upper`,
  `_NumericBounds.refusal_reason`). Every kept bound is copied from an `InputSpec` field — never an
  invented limit. An out-of-bounds numeric fact refuses typed naming the field before feeding.
- **(e) DB-039(e)/G5-F5 — domain check BEFORE the O(n²) gate.** In `post_proposal_checks` the
  registry is now resolved and `_validate_lot_rule_fact_domains()` runs immediately after the
  value-type check and BEFORE `validate_proposed_massing_input` (route lines ~549–582). An
  out-of-domain/out-of-bounds fact refuses without paying the gate; the registry-unavailable path
  stays a bounded 500 recorded at this new, earlier position.
- **(h) DB-039(h)/G3-delta-charset — wall-id charset alignment.** `_validate_exterior_wall_ids()`
  (route lines ~321–335) applies the BP-2 label discipline to `proposed_massing.exterior_walls[].id`
  so a block wall id and a street line's `wall_id` (which is already charset-bound) cannot diverge.
  It narrows STRING ids only; a non-string/missing id is left to the B0 validator's own shape
  refusal (the gate's wider 512-char ceiling remains upstream). Refusal echoes length only.
  **Narrowing named:** a pre-existing block id outside the label charset now refuses at THIS
  internal, flag-gated route — no public caller exists yet.
- **(i) DB-039(i) — registry-before-threadpool note.** `_effective_registry()` docstring + the
  call-site comment (route lines ~549–556) record that the lazy global `_PRODUCTION_REGISTRY` is
  resolved on the event loop and MUST NOT resolve inside a `run_in_threadpool` hop (first-touch
  race would load/cache it twice).
- **(g) DB-039(g)/G4-gaps-3-4 — coverage closure.** New tests below.

## Acceptance scenarios → tests (all in `tests/api/test_proposal_checks_api.py`)

- **AS-1 (numeric bounds):** `test_derive_input_domains_numeric_bounds_are_registry_derived`,
  `test_derive_input_domains_exclusive_bounds_reject_the_endpoint`,
  `test_numeric_bound_only_when_every_declaring_rule_bounds_the_direction`,
  `test_numeric_input_left_unbounded_has_no_window`,
  `test_route_numeric_fact_out_of_bounds_refused_before_engine`. Each bound direction
  mutation-flips a `refusal_reason` assertion; a rule that leaves a direction open feeds the value
  unchanged (no invented limit).
- **AS-2 (ordering):** `test_domain_check_runs_before_the_input_gate` (gate spy records ZERO calls
  on an out-of-domain fact), `test_registry_unavailable_500_is_recorded_before_the_gate`.
- **AS-3 (memoization):** `test_domain_derivation_memoized_once_per_registry` (derivation spy = 1
  across 3 requests), `test_test_injected_registry_derives_its_own_domains`.
- **AS-4 (wall-id charset):** `test_wall_id_bad_charset_refused`,
  `test_wall_id_over_length_refused_length_only`, `test_wall_id_non_string_left_to_the_validator`
  (ordering spy proves the route guard skipped the non-string id — validator names the same field),
  `test_wall_id_conforming_round_trips_the_accepted_arithmetic` (coverage still 0.625/0.125).
- **AS-5 (coverage closure):** all four remaining boundaries now assert a real end-to-end **HTTP
  200** at EXACTLY the cap, each carrying a valid payload that runs the full derivation + engine
  (a real report body, not a downstream refusal):
  - `test_at_wall_cap_exact_returns_200_for_a_valid_solid` — a valid solid with EXACTLY
    `ROUTE_MAX_EXTERIOR_WALLS` (500) B0-valid walls (each unique-id, indices `0→1` into the base
    outline — distinct, in range, non-collapsing) → 200 with the accepted rectangle arithmetic
    (coverage `provided_value` 0.625 / shortfall 0.125); asserts the count cap did NOT trip.
  - `test_at_street_line_cap_exact_returns_200` — a valid lot with EXACTLY `ROUTE_MAX_STREET_LINES`
    (400) attested street lines (each finite EPSG:2263 geometry naming the fixture's `W-S`
    frontage; 400 ≤ the engine's `MAX_STREET_LINES` 500) → 200 with coverage 0.625.
  - `test_body_at_exact_ceiling_valid_payload_returns_200` — a valid attested payload padded with
    trailing JSON whitespace to EXACTLY `MAX_BODY_BYTES` (262144) → 200 (`json.loads` ignores the
    trailing spaces; `==ceiling` passes the size gate, `>ceiling` is the retained 413).
  - `test_at_cap_scenario_label_accepted` — `scenario_label` at EXACTLY `MAX_LABEL_LEN` (200) → 200.

  Above-cap typed refusals are RETAINED so each boundary is bracketed at-cap-200 ↔ above-cap-refusal
  (mutation-flips-red: a cap of 499/399 or a `>=` size gate would flip the at-cap test):
  `test_bp4_over_wall_cap_refused` (501→422), `test_bp4_over_street_line_cap_refused` (401→422),
  `test_oversized_body_is_413_before_parse` (MAX_BODY_BYTES+1→413),
  `test_bp2_over_length_scenario_label_refused` (201→422).
  `test_body_at_exact_ceiling_passes_the_size_gate` still binds the whitespace-only `==ceiling`→422
  (empty-body) path. Shape branches: `test_lot_rule_facts_not_object_is_422` +
  `test_build_lot_context_shape_refusals_each_bound` name every `_build_lot_context` field. The
  pre-existing `test_bp4_at_lot_line_cap_completes` still proves an at-cap 200 for lot lines.
- **AS-6 (preservation):** no existing test was narrowed (see below). Of the three documented
  commands, only **modularity exit 0** is corroborated by this packet's supervisor run. The
  authoritative supervisor outcomes for this packet are **ruff exit 1** and **pytest exit 4 (no
  tests found)** — the earlier local "ruff-clean"/"pytest passed" notes are retained only as
  UNCORROBORATED prior claims (see Evidence). Ruff-clean, full-suite preservation ("all pre-existing
  tests still green"), and CI at the pushed head are therefore all PENDING the next packet's
  documented-command transcripts / the pushed-head CI check — not asserted here.

## Why the reorder is safe for existing behavior (AS-6)

The domain check now runs before the gate. Many `client` tests use the PRODUCTION registry with
`lot_rule_facts={"zoning_district":"R5"}`. Every production rule declares `zoning_district` as a
free string with NO enum (scope is enforced by applicability, not an input enum — verified across
all 18 `app/rules/rulesets/*.rule.json` that declare it), so `zoning_district` is never narrowed in
production and the reorder cannot make those tests refuse the fact instead of the intended
gate/derivation error. No numeric caller input (`lot_depth_ft`) is fed by any existing test with a
valid in-range-relevant value, and the synthetic fixture rules declare no numeric bounds, so AS-1
fixtures are unaffected. No existing test required a comment-tagged narrowing.

## Evidence — authoritative supervisor outcomes vs uncorroborated history

Evidence COLLECTION for this rework belongs to the SUPERVISOR, not this producer. The AUTHORITATIVE
outcomes for this packet are the supervisor's own runs of the three documented commands; this
producer does not self-attest fresh full-suite evidence. Those authoritative outcomes are recorded
first; the earlier local notes are retained SEPARATELY below as uncorroborated history and are NOT
collapsed into the authoritative row.

**Authoritative — this packet's supervisor outcomes (the record of truth here).** The exact exit
outcomes are the observed evidence and are retained verbatim. The supervisor's ACTUAL invocation cwd
for each command was NOT captured, so the cwd column below states the INTENDED context only, never a
recorded fact. Where an observed exit conflicts with the intended cwd (row 2), the cause can only be
INFERRED, not asserted.

| # | command | intended cwd (actual invocation cwd unrecorded) | supervisor exit / outcome (observed evidence, retained) |
|---|---|---|---|
| 1 | `python -m ruff check .` | `services/api` (intended; not recorded) | **exit 1** — lint reported. NOT repaired in this report-only checkpoint (repairing unrelated lint is out of scope); the failing rules/files stay to be characterized by the next packet's verbatim transcript. |
| 2 | `python -m pytest tests/api -q` | **unrecorded** — intended `services/api`; the actual invocation cwd was not captured | **exit 4 — no tests found** (exact exit outcome retained). Because the cwd is unrecorded, the cause is an INFERENCE, not observed fact: exit 4 is a pytest usage error and is *consistent with* the command running from a cwd other than `services/api` (from `services/api` the path resolves; from repo root `tests/api` does not exist) — inferred, not confirmed. The next packet MUST run it with an explicit, RECORDED cwd `services/api`. Collection infrastructure is NOT modified here to work around it. |
| 3 | `python tools/modularity_check.py --check` | repository root (intended; not recorded) | **exit 0** — the modularity check reports neither `proposal_checks_api.py` nor `_proposal_fact_domains.py` in the warning list. |

**Uncorroborated history (prior local notes — retained, NOT verified, NOT authoritative).** These
earlier working-tree observations predate and conflict with the authoritative supervisor outcomes
above; they are kept only so the record is complete, and carry NO evidentiary weight until the next
packet's transcripts either reproduce or overturn them:

| # | command | cwd | previously recorded (uncorroborated) |
|---|---|---|---|
| 1 | `python -m ruff check .` | `services/api` | "All checks passed!" — conflicts with the authoritative **exit 1**; treat as unverified. |
| 2a | `python -m pytest tests/api -q` (run 1) | `services/api` | "FAILED — 1 failed: `test_wall_id_non_string_left_to_the_validator`", then corrected to an ordering-spy discriminator. Kept as a distinct historical outcome. |
| 2b | `python -m pytest tests/api -q` (run 2) | `services/api` | "passed" — conflicts with the authoritative **exit 4 (no tests found)**; treat as unverified. |

**Test-count reconciliation.** `tests/api/test_proposal_checks_api.py` defines **67** `def test_`
functions in the reviewed working-tree file (several parametrized, so the collected case count is
higher than 67). The full `tests/api` suite total previously written as "590 passed" is **PENDING**
the next packet's documented `python -m pytest tests/api -q` (cwd `services/api`) — not asserted as
verified here, and unsupportable while the current authoritative pytest outcome is exit 4.

**PENDING until corroborated:** (1) a green ruff (authoritative outcome is exit 1); (2) any pytest
pass/fail count and full-suite preservation ("all pre-existing tests still green") — authoritative
outcome is exit 4 / no tests found; (3) the CI conclusion on the pushed head. All three require the
next packet's documented-command transcripts (explicit cwd) and/or the CI check on the pushed head;
none is provable from this local working tree.

Prior local notes recorded two in-scope ruff fixes in `_proposal_fact_domains.py` (E501 docstring
reflow, UP037 redundant quotes on the `WeakKeyDictionary` annotation); those are part of the
uncorroborated history and do not by themselves make ruff clean — the authoritative outcome is still
exit 1. No unrelated repository lint is touched in this checkpoint.

## Next-packet handoff (digest-bound review sections)

The implementation and tests are PRESERVED as-is; this report-only checkpoint changes neither. To
resume implementation review, the next bounded packet must include, as SEPARATE artifacts:

1. **The implementation patch and the test patch, separately included** — the two production-module
   changes (`proposal_checks_api.py`, `_proposal_fact_domains.py`) and the test change
   (`tests/api/test_proposal_checks_api.py`) as distinct patches, not folded into one blob.
2. **The complete report** (this file in full, not excerpts of it).
3. **Command transcripts with explicit, RECORDED cwd and working-tree content binding** — each
   documented command captured verbatim (argv, cwd, exit code, output tail) with the cwd recorded,
   and pinned to the LF-normalized digests of the reviewed working-tree files. Required contexts:
   `services/api` for `python -m ruff check .` and the API `python -m pytest tests/api -q`;
   repository root for `python tools/modularity_check.py --check`.

The next review packet must not rely on this prose. It must also carry digest-bound, bounded excerpts
(sha256-pinned line ranges) so an independent reviewer verifies the code directly, covering:

- the COMPLETE helper changes in `_proposal_fact_domains.py` — `derive_input_domains` /
  `input_domains_for`, the numeric-bound combinators (`_rule_lower`/`_rule_upper`/`_combine_lower`/
  `_combine_upper`, `_NumericBounds.refusal_reason`), and the `_INPUT_DOMAIN_CACHE` /
  `clear_input_domain_cache` memoization;
- the COMPLETE route changes in `proposal_checks_api.py` — the early `_validate_lot_rule_fact_domains`
  ordering ahead of the O(n²) gate, `_validate_exterior_wall_ids`, and the `_effective_registry`
  registry-before-threadpool notes;
- the relevant tests in `tests/api/test_proposal_checks_api.py`, with bounded excerpts covering:
  exact-cap **HTTP-200** assertions (walls=500, street_lines=400, label=200, body==`MAX_BODY_BYTES`),
  above-cap typed refusals, registry-derived numeric bounds, domain-check-before-gate ordering,
  per-registry memoization, wall-id charset alignment, and `_build_lot_context` shape-refusal
  coverage;
- **documented-command transcripts with explicit cwd and REAL outcomes, bound to the reviewed
  working-tree contents AND HEAD** — the supervisor's fresh recollection of `python -m ruff check .`
  (cwd `services/api`) and `python -m pytest tests/api -q` (cwd `services/api` — explicit, so exit
  4 / no-tests-found does not recur), plus `python tools/modularity_check.py --check` (cwd
  repository root), each captured verbatim (argv, cwd, exit code, output tail) and pinned to the
  LF-normalized digests of the four reviewed files at the recollection head. This packet's
  authoritative outcomes (ruff exit 1, pytest exit 4 / no tests found, modularity exit 0) and the
  uncorroborated history (rows 2a/2b and the "All checks passed"/"passed" notes) stay PENDING that
  recollection and remain DISTINCT outcomes — never collapsed into a single green line. The next
  packet characterizes the ruff exit-1 findings; it must not repair unrelated lint or modify
  collection infrastructure to force a green.

**Authority.** Evidence COLLECTION (recollecting the documented commands at the frozen head) and any
suite/collection changes stay with the SUPERVISOR; acceptance, push, and merge stay with the
ORCHESTRATOR. This report claims none of those actions and records no acceptance of this task's
implementation.

## Notes / discovery (D-069)

- The route's public surface (`__all__`, `router`, `MAX_LABEL_LEN`, `MAX_BODY_BYTES`, the ROUTE
  caps, `get_proposal_check_registry`, `MAX_FIELD_LEN`, `MAX_PROVENANCE_BYTES`) is unchanged; the
  code-graph seam (consumed by `main.py` mount + this test file only) stays closed.
- No out-of-scope findings surfaced. The M5-T058 rule_evaluation/live_provider surface was not
  touched.
- Thin client: no npm/node; all evidence is CI-reproducible on the pushed head.
