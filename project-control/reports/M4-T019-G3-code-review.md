# M4-T019 G3 gate report — independent code review, D-052 fidelity (verbatim reviewer return)

Recorded by the orchestrator from the independent reviewer's return (reviewer != producer;
reviewer read-only; pinned review HEAD confirmed). HTML entities transport-decoded
(&gt;/&lt;/&amp;&amp; → >/</&&); no other change.

---

**Reviewer:** code-reviewer (independent, read-only)
**Date:** 2026-09-13
**Pinned review HEAD:** `859b34c926360e9800b3ce76bd71fc504d2eff7f` — **CONFIRMED**.
**Scope reviewed:** `services/api/app/connectors/dcm_street_width_policy.py`,
`services/api/tests/connectors/test_dcm_street_width_policy.py`; consumed (read-only)
`services/api/app/connectors/dcm_street_width_classifier.py`; directives D-052 (source-001 +
R001–R008) and D-051 (R002/R003).

## VERDICT: PASS (with non-blocking advisories for the B7 wiring task)

The module implements the owner's D-052 text faithfully — not a paraphrase. Every material
clause is enforced structurally, all four forbidden moves are impossible in this module by
construction, the 24-class interpreted-bounds table is correct row-by-row against the
accepted classifier's real parsing semantics, and the tests pin the owner's worked examples
verbatim. No FAIL findings.

## Reproduction (all read-only, reproduced by the reviewer)

- `git rev-parse HEAD` → `859b34c9…` (matches pin).
- `git show --stat 2eaba13d` and `git show --stat a6c73ec0` → each touches exactly the two
  in-scope files; the parent state of the policy file was a contract-time PLACEHOLDER stub.
  `a6c73ec0` is an ancestor of HEAD (`2eaba13d` is a byte-identical superseded twin — same
  stat/message, not on the HEAD lineage; the reviewed working-tree content is at HEAD).
  Classifier last modified at its own accept commit `8538c272` — **unchanged** by this task.
- `cd services/api && python -m pytest tests/connectors/test_dcm_street_width_policy.py -q`
  → **93 passed in 0.10s**.
- `python -m ruff check <both files>` → **All checks passed!**
- `python tools/modularity_check.py --check` → 402 files; failures 0; warnings 17; EXIT 0.
  The policy module is not among the warned files.

## Requirement-by-requirement findings

**1. D-052-R001 — ordinary threshold + exceptions-before-thresholding. PASS.**
- Threshold exactly 75: `WIDE_THRESHOLD_FT = 75.0` imported from the accepted classifier;
  `clean_numeric_ge_75` (value ≥ 75) → wide, so **exactly 75 is wide**. Tests pin `"75"`,
  `"75.0"` → WIDE; `"74.99"` → NARROW (policy.py:200, table rows 211/225; test lines 61–72).
- Precondition gate precedes thresholding on **every** path
  (`classify_street_width_policy`, policy.py:367–464: bounds → `_precondition_failures` →
  UNRESOLVED on any failure → only then derivability → one-sided → classification). No route
  where data short-circuits the gate. `exceptions_checked` in `_precondition_failures`
  (policy.py:359). Unchecked exception → UNRESOLVED, never thresholded
  (`test_missing_exceptions_checked_refuses_never_silently_thresholded` uses `"100"` →
  UNRESOLVED, lines 171–178).

**2. D-052-R002 — no defaulted preconditions; nearest-centerline refusal; assumption
wording; no DCP-guarantee. PASS.**
- `AttestedPreconditions` (policy.py:114–143): frozen dataclass, six required fields, zero
  defaults; booleans checked with `if not …`; `frontage_match_method` validated by exact
  allow-value — fails on `NEAREST_CENTERLINE_ONLY` AND any unrecognized string
  (policy.py:348–358); only the literal `coverage_established` passes.
  `test_preconditions_dataclass_has_no_defaults` proves `AttestedPreconditions()` raises
  `TypeError` (test lines 201–205). The `_ok_preconditions` kwargs defaults are test-only.
- Bare nearest-centerline match structurally a refusal (policy.py:348–352;
  `test_bare_nearest_centerline_match_is_refused`, lines 155–162).
- Every ISSUED classification carries `OWNER_APPROVED_ASSUMPTION_NOTICE` (explicitly "never a
  verified NYC DCP guarantee", policy.py:105–111); UNRESOLVED/UNKNOWN carry
  `assumption_notice=None`. No DCP-guarantee phrasing anywhere.

**3. D-052-R003 — one-sided-bound rule + CLASS_INTERPRETED_BOUNDS correctness. PASS.**
All 24 rows verified against the classifier's actual parsing code/semantics:
- Wide one-sided: `clean_numeric_ge_75`, `range_both_endpoints_ge_75`,
  `gt_inequality_ge_75` — none can admit a value <75.
- Narrow one-sided: `clean_numeric_lt_75`, `range_both_endpoints_lt_75` (classifier requires
  hi<75), `lt_inequality_at_or_below_75_confident_narrow` ((−∞,bound) sup≤75 exclusive →
  entirely <75), `le_inequality_below_75_confident_narrow` (max<75) — none can admit ≥75
  (strict/inclusive boundaries checked explicitly).
- Straddling → UNRESOLVED: `range_straddles_cutoff`, `gt_inequality_below_75_ambiguous`,
  `lt_inequality_above_75_ambiguous`, `le_inequality_at_or_above_75_ambiguous` — correctly
  non-one-sided.
- Non-derivable → UNKNOWN: the 13 remaining classes; notably `unknown_hedged_below_75`/
  `above_75` correctly NOT classified (the hedge is prose per the classifier's own
  semantics — a subtle trap navigated correctly).
- Owner examples pinned verbatim (`test_r003_owner_examples_verbatim`, lines 80–94):
  `<75`→narrow; `>75`/`>=75`/`75-90`→wide (wide precisely because 75 is on the wide side);
  `<=75` straddles (includes 75) → UNRESOLVED, distinguished from `<75` (excludes 75) →
  narrow; `60-75`/`70-80` → UNRESOLVED.
- The packet's FAIL condition (a class treated one-sided whose parses could cross 75) does
  not occur in any row. Import-time exhaustiveness assert (policy.py:329–334) + len==24 test
  keep the table in lockstep with the classifier.

**4. D-052-R004 — forbidden moves structurally absent; negatives pinned. PASS.**
- The module performs no arithmetic on widths at all — it reads the class label and a static
  table; no tolerance constant exists (grep-clean), no averaging, no rounding, no endpoint
  selection possible. Approximations → UNKNOWN; straddling → UNRESOLVED with no endpoint.
- Negative tests genuinely pin each: `test_approximation_never_gets_an_invented_tolerance`
  (`~75`,`~80`,`~60`,`Around 100`,`Probably between 80 - 90`,`approx 80` → UNKNOWN),
  `test_straddling_range_is_never_endpoint_picked` (`60-75`,`70-80`,`74-75.3`,`60-90` →
  UNRESOLVED), `test_no_rounding_across_the_threshold` (`74.99`→NARROW); `"60-90"` explicitly
  noted as not averaged to wide (test line 123).

**5. D-052-R005 — provenance quintuple + the producer's flagged question. PASS.**
- `PolicyDecision` (policy.py:162–185) carries all five fields and all four return paths
  populate all five (391–402, 411–422, 432–443, 453–464). Tests confirm on a wide decision
  and on a refusal.
- **EXPLICIT R005 RULING (part of the verdict):** the qualitative `InterpretedBounds`
  representation (derivable/one_sided/side/interval_description) **SATISFIES** R005's
  "interpreted bounds" provenance intent; NO correction required. Rationale: (a) the literal
  numeric content is preserved verbatim in `original_label`; (b) the owner's "interpreted
  bounds" means the interpretation relative to the 75-ft threshold — side, derivability,
  shape — exactly what `InterpretedBounds` records; (c) `ambiguity_class` is carried on every
  decision, a stable machine link to the classifier's semantics; (d) re-parsing raw text here
  would duplicate the accepted classifier's private parsing logic and create a second parser
  that can drift from the byte-immutable accepted one — declining to re-parse is the correct
  engineering choice, not a provenance gap. (Advisory A3: optional belt-and-suspenders at the
  persistence layer.)

**6. D-052-R006 / D-051-R002 / D-051-R003 — state separation; no fallback. PASS.**
- Three states genuinely distinct (distinct constants; distinct routing: UNKNOWN →
  `map_resolution`, UNRESOLVED → `None`). The policy never reads the classifier's
  `disposition` field — only `ambiguity_class` and `raw_text` — so `narrow_fail_closed`
  cannot leak into a policy `narrow`. The dedicated non-leak test
  (`test_unknown_is_a_first_class_state_distinct_from_narrow`, lines 311–322) proves exactly
  what it claims. The module never emits a fallback classification; per-rule fallback
  justification correctly left to consuming rules (Advisory A4).

**7. D-052-R007 — DRAFT labeling; maintainability; modularity; scope. PASS.**
- `draft_label=DRAFT_LABEL_NOTICE` (contains "DRAFT" + "G6") on all four paths;
  `test_draft_label_present_on_every_decision_state` verifies all states. Style mirrors the
  accepted classifier; single responsibility; no I/O/network; imports only `dataclasses` +
  the accepted classifier; exactly the two in-scope files changed; modularity EXIT 0.

## Advisories for the B7 wiring task (non-blocking)

- **A1 (R001 end-to-end — important, elevate to a B7 acceptance criterion):** this module
  honors R001 via the `exceptions_checked` attestation; B7/B3/B4 must set
  `exceptions_checked=True` only when exceptions were checked AND (none apply OR every
  applicable one is implemented/resolved) — an applicable-but-unimplemented exception MUST
  drive `exceptions_checked=False`. Likewise `frontage_match_method=coverage_established`
  only after genuine multi-feature collection/coverage (the E 96 St segmentation case).
- **A2 (minor):** add three concrete raw-value→decision cases
  (`<=74`→narrow; `<80`→UNRESOLVED; `>60`→UNRESOLVED) to close a small end-to-end gap (side
  assignments already verified manually + bound by property/exhaustiveness tests + the
  classifier's own 131-test suite).
- **A3 (optional):** consider persisting the classifier's `basis` string alongside the
  provenance record for richer audit (fully reconstructable today).
- **A4 (behavioral note):** when preconditions fail AND the value is non-derivable, the
  module returns UNRESOLVED (routed_to=None), not UNKNOWN — the more conservative ordering;
  B7 should treat any non-{wide,narrow} decision as "not classified" rather than keying
  map-resolution routing solely off routed_to.

## Pinned-HEAD confirmation
Reviewed at `859b34c926360e9800b3ce76bd71fc504d2eff7f`. Uncommitted files are control-plane /
agent-memory / scratchpad only (expected frozen-head pattern); the reviewed code is committed
at `a6c73ec0` (ancestor of HEAD).

**Recommended gate action: record G3 = PASS.** No blocking corrections. Advisories A1–A4
attach to the B7 wiring task, with A1 elevated to an explicit B7 acceptance criterion.
