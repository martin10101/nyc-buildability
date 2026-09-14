# M4-T019 G4 gate report — independent test-adequacy review (verbatim reviewer return)

Recorded by the orchestrator from the independent reviewer's return (reviewer != producer;
read-only against the repo; mutation probes run on an isolated scratch copy). HTML entities
transport-decoded; no other change. Per the project's gate-verdict semantics, "PASS with
required corrections" records as PASS with the corrections BLOCKING acceptance; the F1
correction was applied as a tagged ORCH-CORRECTED test addition immediately after this
verdict — the delta-attestations are appended at the end.

---

**Reviewer:** qa-engineer (independent; read-only) · **Gate:** G4 · **Date:** 2026-09-13
**Verdict: PASS — with one required (blocking) corrective test addition (Finding F1, Medium).**

## Pinned-HEAD confirmation
- Instruction pin: `859b34c926360e9800b3ce76bd71fc504d2eff7f`.
- The reviewer ran in an isolated worktree, so it verified the primary checkout's HEAD by
  reading git plumbing directly: `ctl24/.git` → gitdir → `HEAD` →
  `refs/heads/candidate/D-024-mrl-option-b` → **859b34c9…** Match confirmed. Uncommitted
  control-plane JSONs present as expected; the code under review is committed.
- Code provenance: the pinned commit is a control-plane integration commit; the reviewed code
  arrived at `a6c73ec0` (exactly the two in-scope files). The accepted classifier's last edit
  is M4-T015 (`8538c272`) — byte-unchanged by M4-T019 (S5 immutability satisfied).

## Required commands rerun (primary checkout, at the pin; no-bytecode/no-cache → zero repo writes)
- `python -m pytest tests/connectors/test_dcm_street_width_policy.py -q` → **93 passed in 0.09s**
- `python -m pytest tests/connectors -q` (regression) → **712 passed in 3.33s** — matches producer claim
- `python -m ruff check .` (api CI step 1) → **All checks passed!**

## 1. Coverage vs directive verification areas (R007)
- **Threshold boundaries** — `test_threshold_boundaries` parametrizes 74.99→narrow, 75→wide,
  75.0→wide, 75.01→wide. Covered.
- **Range handling** — all seven R003 owner examples as literal cases in
  `test_r003_owner_examples_verbatim`, each routed through the REAL classifier; straddling/
  threshold-touching extras (`74-75.3`, `60-90`, `50-60`, `80-90`, `166-192`) plus a
  structural property test over the whole table (one_sided ⇔ side∈{wide,narrow}). Covered.
- **Frontage mismatches** — nearest-centerline refusal + unrecognized-method fail-closed.
  Covered for the attested-precondition surface (real geometry matching scoped to B3/B4 —
  see F2).
- **Applicable exceptions** — `test_missing_exceptions_checked_refuses_never_silently_thresholded`
  uses `"100"` with exceptions_checked=False → UNRESOLVED + reason + assumption_notice None.
  Covered.

## 2. Negative-test strength (R004)
Forbidden-move tests are genuinely discriminating, not tautological — proven by the mutation
battery (endpoint-pick, side-flip, straddle-collapse, UNKNOWN-collapse,
precondition-removal all fail the suite). No invented tolerance (approximations/hedges →
UNKNOWN); no averaging / endpoint-pick (straddlers must be UNRESOLVED; `60-90` avg=75
explicitly not resolved wide); no rounding across 75 (74.99→narrow); conflicting/unrecognized
→ UNKNOWN.

## 3. Mutation probes (10 run on an isolated scratch copy; baseline 93 pass)
| # | Single-line mutation | Result |
|---|---|---|
| M1 | `clean_numeric_ge_75` side WIDE→NARROW | CAUGHT (3 failed) |
| M2 | `gt_inequality_ge_75` side WIDE→NARROW | CAUGHT (2 failed) |
| M3 | `range_straddles_cutoff` made one-sided WIDE (endpoint-pick) | CAUGHT (9 failed) |
| M4 | Drop `assumption_notice` on issued classification | CAUGHT (2 failed) |
| M5 | Collapse UNKNOWN→UNRESOLVED (not-derivable branch) | CAUGHT (15 failed) |
| M6 | `exceptions_checked: bool = True` (default a precondition) | **SURVIVED (93 pass)** |
| M7 | Remove `exceptions_checked` failure branch | CAUGHT (3 failed) |
| M8 | Accept bare nearest-centerline as coverage | CAUGHT (2 failed) |
| M9 | Drop `routed_to` on UNKNOWN | CAUGHT (16 failed) |
| M10 | `le_inequality_at_or_above_75` (`<=75`) one-sided WIDE | CAUGHT (1 failed) |

9/10 caught; M6 survived.

## 4. Test hygiene
Tests exercise the REAL accepted classifier; only two legitimately hand-built inputs (schema
drift; the non-leak test uses the real classifier). Exhaustiveness re-assert present
(set-equality AND len==24) plus the module's import-time assert. Assertions specific; no
order dependence; fully deterministic.

## Findings
- **F1 — Medium — REQUIRED CORRECTION (blocking acceptance).** Surviving mutation M6.
  `test_preconditions_dataclass_has_no_defaults` only proves zero-arg construction raises;
  it does not prove each field individually lacks a default. Because `exceptions_checked` is
  the LAST dataclass field, `exceptions_checked: bool = True` compiles, zero-arg construction
  still raises, and all 93 tests stay green — a silent default on the R001 zoning-exceptions
  gate would pass. This is precisely the packet's named "precondition theater" risk. Missing
  test: iterate `dataclasses.fields(AttestedPreconditions)` asserting `default is MISSING`
  and `default_factory is MISSING` per field. (Middle/first-field defaults raise at class
  definition; only the last field is silently defaultable, so this one assertion closes the
  whole hole.)
- **F2 — Low — Advisory (for the B7 wiring task).** Genuine multi-feature / wrong-street /
  cross-feature-conflict cases are untested here and must be added when geometry/consumer
  wiring lands (they cannot be exercised against a single WidthClassification; the in-scope
  `100-90` proxy is not equivalent).
- **F3 — Info/nit.** One tautological assert line in the draft-label test (harmless; real
  checks follow); no dedicated provenance-quintuple test for a narrow decision specifically
  (schema covered by wide + refusal; narrow shares the identical issued path). Cosmetic.

## Scope / regression (S5)
Exactly two new files; accepted classifier & centerline connector byte-unchanged; ruff EXIT 0;
connectors suite 712 green; zero new dependencies. Satisfied.

## Verdict rationale
The suite is comprehensive and its negative tests are empirically discriminating. The shipped
production code fully satisfies S1–S5 and R001–R007. The single test-adequacy gap (F1) leaves
the most safety-critical precondition unguarded against a one-line regression, so the verdict
is **PASS with F1 as a blocking required correction** (recorded PASS; acceptance held until
F1's assertion is added, validated, committed). F2 advisory for B7; F3 cosmetic.

## Advisory test additions for the B7 wiring task
1. With a real multi-feature frontage: refuse on nearest-centerline-only; classify only when
   coverage is established across ALL touching features (E 96 St segmentation case).
2. A genuine conflicting-records test (two matched features, incompatible widths) → UNKNOWN
   routed to map resolution.
3. Per-consuming-rule fallback-justification tests (D-052-R006 / D-051-R003): UNKNOWN/
   UNRESOLVED propagate; no universal narrow-fallback downstream.
4. Carry the `dataclasses.fields()` no-default assertion forward as the standard guard for
   any new attestation/precondition dataclass in the geometry lane.

---

## F1 correction record (orchestrator)

Applied immediately after the verdict as a tagged ORCH-CORRECTED test addition:
`test_no_precondition_field_has_a_default` in
`services/api/tests/connectors/test_dcm_street_width_policy.py` — iterates
`dataclasses.fields(AttestedPreconditions)` asserting `default is MISSING` and
`default_factory is MISSING` per field (exactly the reviewer-prescribed shape). Suite now
94 passed; ruff whole-tree EXIT 0. Production module UNCHANGED.

## Delta-attestations (appended on receipt)

PENDING at file-creation time — the same G4 reviewer's attestation over exactly this delta,
and the G3 reviewer's attestation that its PASS carries to the corrected identity (the G3
review surface includes the test file), are recorded below when received.
