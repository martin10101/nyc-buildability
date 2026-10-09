# M4-T024 - an independent reviewer's ruling on row L7 (before submission)

Asked 2026-10-06 by the orchestrator of a `code-reviewer` agent, read-only, at branch head `12c1c5d2` (the builder's files as committed at `2675a9d3`). The question was put without the orchestrator's own reading: by the packet's scenarios and the sources, should row L7 of the real-lot case (maximum dwelling units, qualifying affordable housing) be "not known" as the builder recorded it, a value conditional on the housing qualifying, or something else. The return below is unchanged. It is an AI agent's review, not a professional review. What followed: scope correction 2 in the packet (scenario S7) and a builder's change to row L7.

## The reviewer's return (unchanged)

```
GATE (narrow): row L7 of real-lot case — VERDICT: FAIL as recorded. Ruling: (b) a numeric value 35, recorded as kind "value" conditional on the housing qualifying, exactly as L2/L4 are.

Three deciding facts:
1. The helper did NOT flag L7 as not-known. provenance/return-independent-hand-calculation-1.md line 46 marks it "[C] Qualifying AFFORDABLE (24,180 sf): 24,180/680 = 35.56 -> 35 DU" — [C]=calculation. Only the SENIOR row (L8) is "[?]" = NOT KNOWN (line 47; legend line 7). So by S4 (task M4-T024.json line 61: "follows the helper's return unless the work order records a reasoned correction") L7 = 35.
2. The work order's INDEPENDENT-value column gives L7 = 35 (docs/plans/...WORK_ORDER...md line 450); "not known (K13)" sits in the FIRST-SCREEN column, i.e. the program's presentation (K13 line 211; H2 line 344). The objective and S3 (task JSON line 6; S3 line 55) keep "Program today"/"First screen" in the work order; the case file records the independent value, which is 35.
3. L7 = L2 / 680 and carries the identical qualifying-eligibility caveat (Task 3 item 9, line 71 — the same caveat covers L2's 2.40 column, L4's 65-ft, and L7). L2 is recorded "value" 24180 (real-lot.json lines 202-209) and L4 "value" (lines 302-309).

Consistency: L2, L4, L7 are NOT treated consistently today — L2/L4 are "value", L7 is "not_known" (lines 464-468). It matters: L7 is the one in dispute and the inconsistency is unjustified. L8 is genuinely different (no factor at all; helper "[?]") and is CORRECT as recorded (lines 516-521).

Smallest change: real-lot.json L7 only — expected.kind "value", value 35, unit "dwelling units", reason "" ; add the arithmetic step 24180/680, rounding dwelling_unit_three_quarters, result 35 (mirror L6); move the eligibility caveat into does_not_establish (as L2). Re-render docs/reference-cases/R6B/real-lot.md (S10 byte-identity). No schema/checker change: r6b_reference_cases_check.py already accepts a numeric "value" backed by arithmetic or quoted basis (lines 254-261). Packet S7 (task JSON line 79) DOES contradict S4 for L7 and needs an orchestrator correction: drop L7 from the not-known list (keep L8), or state it means the program's first-screen presentation, not the independent value. Producer cannot edit project-control/; orchestrator owns S7.

Could not determine: whether the orchestrator intends S7 to govern the independent value or only first-screen — genuinely ambiguous; S4 + the work order's independent column resolve it to 35. I did not re-verify real-lot.md render or the other three cases (out of scope).
END-OF-REPORT
```
