# Delta-Attestation — M4-T021 rework, head `432ed8f3` (G3 / code-reviewer)

> Saved VERBATIM by the orchestrator from the same code-reviewer agent that produced the
> original M4-T021 G3 report, resumed with its full context (2026-09-14; transport
> entity-decoding only). Reviewer ≠ producer.

Verified `git rev-parse HEAD` == `432ed8f3` (matches the coordinator's pinned head). Cherry-pick verified byte-identical: `git diff c48bfd80 432ed8f3 -- <3 allowed_paths files>` → empty. Scope verified unchanged across the **entire** `d7c22f3e..432ed8f3` range (not just the rework commit): the 6 forbidden connector files, `services/api/app/rules/**`, `pyproject.toml`, `requirements.in/.txt` all diff empty; exactly the 3 allowed_paths files changed anywhere in the task's history. Reproduced live: `40 passed` (engine-only), `792 passed` (full connectors: 752 + 40), `ruff check .` → `All checks passed!`, `modularity_check.py --check` → `failures 0; warnings 18`.

## F1 (EC-5 gate) — RESOLVED

Read the actual diff, not the description. `_ec5_precondition_failures` (wide_street_buffer_engine.py:523-543) is a direct mirror of `dcm_street_width_policy._precondition_failures`, and the gate at :628-661 fires when either attested field is `False`, returning `STATUS_PRECONDITIONS_NOT_ATTESTED` with every buffer/intersection field `None`/empty and the reason named in `ec5_not_attested_notice` — placed after lot CRS/geometry validation, before the EC-6 empty check, before any segment is touched. This is exactly what my original finding required: a caller can no longer get a `STATUS_COMPUTED`-shaped answer on an unverified legal precondition. Confirmed via 5 new tests, all reproduced green, including the important ordering proof (`test_ec5_gate_refuses_even_with_an_empty_wide_segment_set`, proving EC-5 outranks EC-6) and that only the actually-failing field is named in the refusal reason (not a blanket message). I also independently read the orchestrator's ruling (`project-control/reports/M4-T021-rework-ruling.md`, RULING 1) — its reasoning matches what I verified from source myself, not a restatement I'm taking on faith. **F1 confirmed resolved.**

## F2 (quad_segs) — RESOLVED

`BUFFER_QUAD_SEGS` is now `16`, and the comment states the corrected, verified fact (`BaseGeometry.buffer` — the method actually called — defaults to 16; the unused top-level `shapely.buffer()` defaults to 8). I did not take the "no existing S1–S4 value changed" claim from the message — I independently recomputed all of S1/S3/S4's fixture geometries in a standalone Python probe at both `quad_segs=8` and `quad_segs=16`:

```
within_area:  10000.0 (both)      beyond_empty: True (both)      tangent_area: 0.0 (both)
S3 corner aggregate: 17500.0 (both)
end-cap fixture (248.0,-64.0)/(900.0,-424.0): 373.6219486597519 (q8) vs 382.9260890749891 (q16)
```

This exactly matches the producer's claimed numbers, confirming (a) the correction is real and non-cosmetic, (b) no prior test's expected value silently drifted, and (c) the new end-cap fixture genuinely exercises the previously-untested rounded-cap path via an independent flat-cap-probe proof that the straight sides never reach the lot. `test_line_probe_matches_the_hand_derived_expected_values` was updated to use `BUFFER_QUAD_SEGS` instead of a hardcoded `8`, so it no longer silently pins the wrong value. **F2 confirmed resolved.**

## G4's finding (source_retrieved_at/source_raw_digest) — new to me, independently checked, correct

I confirmed at the pre-rework head (`git show 7dc56112:...`) that `source_retrieved_at`/`source_raw_digest` existed only on the two input dataclasses and on no output field — a real gap I did not catch in my original review. The rework threads them onto `SegmentContribution.segment_source_retrieved_at/.segment_source_raw_digest` and `WideStreetBufferResult.lot_source_retrieved_at/.lot_source_raw_digest`, populated in all three branches (verified by direct diff read of every `return WideStreetBufferResult(...)` site, not just the new tests). This is a legitimate G4 catch and the fix is correctly scoped and complete.

## Untouched dimensions — earlier PASS rulings carry forward

CRS fail-closed discipline, the 100.0-ft/planar/foot-CRS buffer semantics, union-before-intersect ordering (still literally `buffers` collected in the loop then `unary_union` after), per-segment/aggregate portions exposure, EC-1/EC-3/EC-6 handling, error taxonomy consistency, zero new dependencies, and D-045-R009 scope preservation are all unchanged by this diff and remain PASS on inspection of the actual (unmodified) surrounding code. A1/A2/A3 advisories from my original report still apply unchanged (A2 is explicitly narrower now that EC-5 refusal exists, but no consumer for `ec5_preconditions` still exists until B7).

## Modularity advisory (17→18, wide_street_buffer_engine.py crossed WARN_SLOC)

Ruling: **leave as-is now; do not split.** Raw line count is 754 against thresholds of 600 (warn)/750 (justify)/1000 (hard, CI-enforced); the checker reports 0 failures, so it hasn't even reached the justification tier, and the true SLOC the tool measures excludes the file's heavy docstring content (module + every class/function is documented at length), so the file sits comfortably below 750 on the metric that matters. All growth this rework added was strictly corrective — one new gate function directly serving the module's pre-existing EC-5 concern, one corrected constant/comment, four provenance fields threaded onto existing dataclasses — not a new unrelated responsibility. The module's single responsibility (CRS-gated buffer/intersection geometry for one lot) is intact; nothing here mixes in transport, rule-wiring, or override-table lookup. The forward-looking boundary judgement CLAUDE.md principle 16 asks for is already decided by the existing decomposition, not newly needed: EC-5's actual named-street override table and B7's rule-wiring are explicitly out of this module's scope by design (`.claude/rules` sibling precedent: DCM parsing/classification/policy already live in four separate files rather than one monolith) — when B7 and the override table are built, they must land as their own module(s) that consume this one, never be added into `wide_street_buffer_engine.py`. No split needed now or "before B7" in the sense of restructuring this file; the constraint that matters is keeping B7 OUT of this file, which is already the design.

## Final verdict

**CONFIRMED.** F1 and F2 are genuinely resolved by the rework, reproduced independently rather than taken on trust; G4's provenance finding is independently verified correct and its fix complete; scope, regression, and tooling evidence all reproduce exactly as claimed at `432ed8f3`. Original PASS-with-corrections rulings on all untouched dimensions carry forward unchanged.
