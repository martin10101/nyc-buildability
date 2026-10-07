# M5-T132 producer report — the decision module's explanations are true for every input state

Task: make every explanation text of the module that decides how each result appears true for
its input state. Texts only; no result changes the way it appears; no zoning number added.

Producer: scenario-optimization-engineer (isolated worktree). Claim-seam head reset to
`d8ad46a85b31923f5eee4553543b3f2e1a6eb22b` before any edit.

Scope touched (texts only): `result_ways.py`, `result_way_conditions.py`, `result_way_bridge.py`
(the two held-back strings of DB-175 f), and four test files.

## 0. Method and headline result

1. BEFORE any edit, a script OUTSIDE the repository (`inventory.py`, run with the venv against the
   untouched module) drove `decide_result_ways` across every input state of every result and
   every text `gather_result_ways` can return (facts statements, area statement, large-lot,
   held-back strings, overlay reading-owed), and printed the "before" columns and a
   `(key, way_type, gap_kind)` signature for every state.
2. The table (section 2) checks each row for (a) the reason names the condition that really
   fails, with the measured value where one exists, and names no condition that holds; (b) the
   "resolved by" asks for nothing the state already holds and nothing that could not resolve it;
   (c) the kind fits (missing information vs owed work).
3. 12 rows failed a check. Each was repaired, TEXTS ONLY (section 3).
4. **No result changed the way it appears, and no kind changed.** The full `(key, way_type,
   gap_kind)` signature across all 56 states is byte-identical before and after the repair
   (`diff` of the two script runs is empty). This is the S6 evidence; the way-pinning test
   `test_every_input_state_of_every_result` also pins the way of every row.
5. One test per row (62 cases in `test_result_ways_truth_table.py`), the guard battery extended
   (section 5), red proof for S1/S2 (section 4), one mutation proof per corrected branch
   (section 6).

## 1. The two faults the owner's outside reviewer named (confirmed, then fixed)

- `_unit_standard_way`, state EVIDENCE_NOT_IN_ONE (evidence records the lot OUTSIDE a special
  density area): fell through to the text written for "not given" — reason "There is no evidence
  …", "resolved by" "A sourced fact saying whether the lot is in a special density area" (a fact
  the state already holds). Confirmed red by `test_s1_…` on the untouched module (section 4).
- `_rear_yard_way`, state angle-fails-distance-holds (far corner 90 ft; angle 140°): one text
  served both waiver conditions and said the far corner is "beyond the rear-yard waiver area" and
  gave the distance, when the failing condition is the angle. Confirmed red by `test_s2_…`.

## 2. The complete table (every input state of every result + every gather text)

Way: S=settled, C=conditional, W=withheld. Kind: MI=missing_information, WO=work_owed, —=shown.
Checks a/b/c: ✓ pass. Verdict: PASS (true at the claim head, unchanged) or REPAIRED. "before"
columns were produced by the external script against the untouched module; full before→after
texts for the REPAIRED rows are in section 3. For PASS rows the reason text is byte-identical
before and after (proven by the empty signature diff and the reason assertions in the tests).

### 2.1 Blanket withholds (apply to every result; reading O2/O6/O11)
| State | Way | Kind | a/b/c | Verdict | Test id |
|---|---|---|---|---|---|
| B1 district not given | W | MI | ✓✓✓ | PASS | B1_district_none; test_o11_district_not_given… |
| B2 district not R6B | W | WO | ✓✓✓ | PASS | B2_district_not_r6b; test_o11_district_not_r6b… |
| B3 special purpose present | W | WO | ✓✓✓ | PASS | B3_special_purpose_present; test_h5_recorded… |
| B4 special purpose not read | W | MI | ✓✓✓ | PASS | B4_special_purpose_not_read; test_h5_special… |
| B5 split lot present | W | WO | ✓✓✓ | PASS | B5_split_present; test_h5_recorded… |
| B6 split lot not read | W | MI | ✓✓✓ | PASS | B6_split_not_read; test_h5_split_lot… |
| B7 a K20 condition present | W | WO | ✓✓✓ | PASS | B7_k20_present; test_each_k20_condition_present… |

### 2.2 Commercial-overlay block, per family (reading O5)
| State | Way | Kind | a/b/c | Verdict | Test id |
|---|---|---|---|---|---|
| OB1 overlay not read | W | MI | ✓✓✓ | PASS | OB1_overlay_not_read; test_f4_overlay_not_read |
| OB2 overlay present, no support map | W | WO | ✓✓✓ | PASS | OB2_overlay_present_no_map; test_s1_recorded_overlay_with_no_support |
| OB3 overlay present, family missing from map | W | WO | ✓✓✓ | PASS | OB3_overlay_family_missing; test_overlay_present_with_a_family_missing |
| OB4 overlay present, family supported | S/C | — | ✓✓✓ | PASS | OB4_overlay_supported; test_s8_supported_result |
| OB5 overlay present, not supported (named reading owed) | W | WO | ✓✓✓ | PASS | OB5_overlay_not_supported_named; test_s8_not_supported |
| OB6 overlay present, not supported (fallback) | W | WO | ✓✓✓ | PASS | OB6_overlay_not_supported_fallback; test_overlay_not_supported_without_reading_owed |

### 2.3 Floor area (4 keys)
| State | Way | Kind | a/b/c | Verdict | Test id |
|---|---|---|---|---|---|
| FA1 no recorded area | W | MI | ✓✓✓ | PASS | FA1_no_area; test_s5_no_recorded_area |
| FA2 inclusionary present | W | WO | ✓✓✓ | PASS | FA2_inclusionary_present; test_f1_inclusionary_present |
| FA3 inclusionary not read | W | MI | ✓✓✓ | PASS | FA3_inclusionary_not_read; test_f1_inclusionary_not_read |
| FA4 area agrees, K20 absent | S | — | ✓✓✓ | PASS | FA4_settled; test_s6_all_conditions_checked_and_absent |
| FA5 area agrees, K20 not checked | C | — | ✓✓✓ | PASS | FA5_conditional_k20; test_s6_not_checked |
| FA6 area disagrees | C | — | ✓✓✓ | PASS | FA6_area_disagrees; test_s5_figures_that_disagree |
| FA7 area could not be compared | C | — | ✓✓✓ | PASS | FA7_area_could_not_compare; test_s5_figure_that_could_not_be_compared |
| FA8 area agreement None | C | — | ✓✓✓ | PASS | FA8_area_agreement_none; test_g3f5_agreement_none |

### 2.4 Heights (6 keys)
| State | Way | Kind | a/b/c | Verdict | Test id |
|---|---|---|---|---|---|
| H1 flood present | W | WO | ✓✓✓ | PASS | H1_flood_present; test_f2_flood_present |
| H2 flood not read | W | MI | ✓✓✓ | PASS | H2_flood_not_read; test_f2_flood_not_read |
| H3 K20 absent | S | — | ✓✓✓ | PASS | H3_settled; test_s6_all_conditions_checked_and_absent |
| H4 K20 not checked | C | — | ✓✓✓ | PASS | H4_conditional; test_s6_not_checked |

### 2.5 Coverage
| State | Way | Kind | a/b/c | Verdict | Test id |
|---|---|---|---|---|---|
| C1 large lot | W | WO | ✓✓✓ | PASS | C1_large_lot; test_f5_large_lot_threshold |
| C2 lot type not given | W | MI | ✓✓✓ | PASS | C2_lot_type_none; test_f9_lot_type_not_given |
| C3 interior | W | WO | ✓✓✓ | PASS | C3_interior; test_h4_interior_coverage_withheld |
| C3b through | W | WO | ✓✓✓ | PASS | C3b_through; test_f7b_through_lot |
| C4 no outline | W | MI | ✓✓✓ | PASS | C4_no_outline; test_h5_no_outline |
| C4b a street-line reach unknown | W | MI | ✓✓✓ | PASS | C4b_street_reach_unknown; test_street_line_reach_unknown |
| C5 reaches beyond 100 ft | W | WO | ✓✓✓ | PASS | C5_reaches_beyond; test_h3_c3 |
| C6 large-lot answer not stated | W | MI | ✓✓✓ | PASS | C6_large_lot_none; test_o13_large_lot_not_stated |
| C7 within, K20 absent | S | — | ✓✓✓ | PASS | C7_settled; test_h3_c2 |
| C8 within, K20 not checked | C | — | ✓✓✓ | PASS | C8_conditional; test_h3_c1 |

### 2.6 Rear yard (the repaired surface)
| State | Way | Kind | a/b/c before | Verdict | Test id |
|---|---|---|---|---|---|
| RY1 lot type not given | W | MI | ✓✓✓ | PASS | RY1_lot_type_none; test_f9_lot_type_not_given |
| RY2 interior/through | W | WO | ✗ (c): reason framed owed work as inputs "not given" | **REPAIRED** | RY2_interior |
| RY3 no reach at all (no outline) | W | MI | ✓✓✓ | PASS | RY3_corner_none; test_h5_no_outline |
| RY4 corner reach not measured (angle known) | W | MI | ✗ (a): "no outline" text over-claims | **REPAIRED** | RY4_reach_unknown; test_corner_reach_unknown |
| RY5 angle not measured (reach KNOWN) | W | MI | ✗ (a): text says the reach is not measured when it is | **REPAIRED** | RY5_angle_unknown; test_corner_angle_unknown |
| RY6 reach and angle not measured | W | MI | ✗ (a): single "no outline" text | **REPAIRED** | RY6_both_unknown |
| RY7 distance fails, angle holds | W | WO | ✓ (true for this state) but shared buggy branch | **REPAIRED** (split) | RY7_distance_fails; test_h3_c1/c3 |
| RY8 angle fails, distance holds | W | WO | ✗ (a): blames distance as "beyond", omits angle | **REPAIRED** | RY8_angle_fails; test_s2_… |
| RY9 both fail | W | WO | ✗ (a): names distance only | **REPAIRED** | RY9_both_fail; test_s4_… |
| RY10 within both, K20 absent | S | — | ✓✓✓ | PASS | RY10_settled; test_h3_c2 |
| RY11 within both, K20 not checked | C | — | ✓✓✓ | PASS | RY11_conditional; test_h3_c2 |

### 2.7 Setback, unit limits, building option
| State | Way | Kind | a/b/c before | Verdict | Test id |
|---|---|---|---|---|---|
| SB1 setback above base | W | WO | ✓✓✓ | PASS | SB1_setback; test_f7c |
| US1 no recorded area | W | MI | ✓✓✓ | PASS | US1_no_area; test_h5_no_lot_area |
| US2 user statement (not in one) | C | — | ✓✓✓ | PASS | US2_user_statement; test_h9_user_statement |
| US3 evidence in one | W | WO | ✓✓✓ | PASS | US3_evidence_in_one; test_f3_density_evidence_in_one |
| US4 density not given | W | WO | ✗ (b)(c): "resolved by" asks for a fact that could not resolve it | **REPAIRED** | US4_not_given; test_us4_… |
| US5 evidence NOT in one | W | WO | ✗ (a)(b): "no evidence"; asks for a held fact | **REPAIRED** | US5_evidence_not_in_one; test_s1_… |
| UA1 qualifying affordable | W | WO | ✓✓✓ | PASS | UA1_affordable; test_s1_qualifying… |
| USR1 qualifying senior | W | WO | ✗ (a)(c): reason reads "no limit" while kind/resolved say owed | **REPAIRED** | USR1_senior; test_s1_qualifying… |
| BO1 building option (×4 keys) | W | WO | ✓✓✓ | PASS | BO1_option; test_s8_a_dependent_result |

### 2.8 Whole-answer not-available object (`_answer`)
| State | Way | Kind | a/b/c before | Verdict | Test id |
|---|---|---|---|---|---|
| WA1 every value withheld, one reason | (n/a) | per gap | ✓✓✓ | PASS | test_whole_answer_single_reason… |
| WA2 every value withheld, >1 distinct reason | (n/a) | per gap | ✗ (a): shows only the first value's reason | **REPAIRED** | test_whole_answer_reason_names_every_distinct_reason |

### 2.9 Gather texts (`gather_result_ways`)
| Text | a/b/c | Verdict | Test id |
|---|---|---|---|
| facts statements (6 conditions × present/absent/not-read = 18) | ✓✓✓ | PASS | test_every_text_a_user_may_see_is_plain_and_true_s7 |
| area statement (none / could-not-compare / agrees / disagrees) | ✓✓✓ | PASS | test_area_rule_s3; …_s7 |
| large-lot statement (not stated / at-or-above / below) | ✓✓✓ | PASS | test_large_lot_answer_o17; …_s7 |
| overlay reading-owed (rear yard) | ✓✓✓ | PASS | …_s7 |
| held-back: unrecognised lot type ("this piece") | ✗ (L3): internal name | **REPAIRED** | test_the_two_held_back_strings_are_plain_db175_f |
| held-back: statement the lot IS in a special density area | ✗ (L3 light): jargon | **REPAIRED** | test_the_two_held_back_strings_are_plain_db175_f |

S5 (a reviewer picks ten unnamed states): every state above has a row and a test.

## 3. The repair — before → after (texts only)

All 12 repairs keep the way and the kind; only reason / resolved_by / held-back text changed.

**RY2 interior/through** — before: "…the ordinary rear-yard depth (ZR 23-342) needs the building
type and lot width, **which are not given**, so the rear yard is withheld." after: "…and the
program **does not yet work out** the ordinary rear-yard depth (ZR 23-342), so the rear yard is
not known." (owed work named, not inputs "not given").

**RY4/RY5/RY6 corner measurements missing** — before (all three): the shared "no outline" text
"The lot outline and street-line reach are not measured…". after: RY4 "…the far corner's reach
from the point where the two street lines meet is not measured…"; RY5 "…the angle at which the
two street lines meet is not measured…" (never claims the KNOWN reach is unmeasured); RY6 names
both. New helper `rear_yard_unmeasured` in `result_way_conditions.py`.

**RY7/RY8/RY9 waiver fails** — before (one text for all three): "The far corner is {reach} from
the corner point, **beyond the rear-yard waiver area** (…); what the ordinary rear yard requires
beyond it is not settled." after (new helper `_rear_yard_outside_waiver`, three states):
- RY7 distance only: "…the far corner is {reach}…, beyond the rear-yard waiver area (…within
  {100 ft}…); the two street lines meet at {angle}, within the waiver's limit of {135 degrees}…"
- RY8 angle only (S2): "…the two street lines meet at {angle}, more than the rear-yard waiver's
  limit of {135 degrees}; the far corner is {reach}…, within {100 ft} of it…" (never "beyond").
- RY9 both: names both the distance beyond the area and the angle over the limit.
  Measured values come from the two legal-measure records and the measured reach/angle; no number
  is typed a second time (the numeric-literal guard still allows only 100.0 and 135.0).

**US4 density not given** — before resolved_by "A sourced fact saying whether the lot is in a
special density area." after reason adds "…how the legal dwelling-unit limit is shown once that is
known has not been worked out…"; resolved_by now names the owed work (not a bare fact), and keeps
"a user's statement … would show it only as a conditional result."

**US5 evidence NOT in one (O19, S1)** — before reason "There is no evidence…", resolved_by "A
sourced fact…". after reason "**Evidence records this lot outside a special density area**; how
the legal dwelling-unit limit is shown on that evidence has not been worked out and checked
against an independently worked example…"; resolved_by names that work, never a fact about the
density area.

**USR1 qualifying senior** — before "…so the program gives no unit limit for it: it is not set by
this formula." after "…**and the separate rule for qualifying senior housing is not worked out
yet**, so the legal dwelling-unit limit for it is not known: it is not set by this formula."
(keeps "not set by this formula"; now consistent with its work-owed kind and resolved_by).

**WA2 whole-answer, more than one reason** — before "Every value of this answer is withheld:
{first reason}". after when the distinct reasons differ: "Every value of this answer is withheld,
for more than one reason: {each distinct reason}". The single-reason wording is unchanged.

**Held-back HB1** — before "…is not one **this piece** decides from; the lot type is carried as
not given." after "…is not one **the program recognises**, so the lot type is carried as not
given."

**Held-back HB2** — before "…has no decided path; it is **held back** and the special density area
is carried as not given." after "A statement that the lot is in a special density area is **not
yet handled**, so the special density area is carried as not given."

### Kinds changed: NONE.
The `(key, way_type, gap_kind)` signature across all 56 states is byte-identical before and after
(empty diff). Every repaired withhold kept its kind (RY2/RY7/RY8/RY9/US4/US5/USR1 = work_owed;
RY4/RY5/RY6 = missing_information). No row needed a kind change.

## 4. Red proof (S1 and S2 against the untouched module)

The three source files were restored to the claim-seam head (`git checkout d8ad46a… -- <paths>`),
the two tests were run, then the edited sources were restored. Output:

```
FAILED test_s1_evidence_not_in_one_names_the_evidence_not_the_absence_of_it
  assert 'Evidence records this lot outside a special density area' in
    "There is no evidence of whether this lot is in a special density area, where the
     dwelling-unit formula does not apply, … a user's statement would show it only as a
     conditional result."
FAILED test_s2_corner_angle_fails_distance_holds_names_the_angle_not_the_distance
  assert '140 degrees' in
    'The far corner is 90 ft from the corner point, beyond the rear-yard waiver area
     (the whole lot is within 100 feet …); what the ordinary rear yard requires beyond it
     is not settled.'
2 failed in 0.71s    (direct exit code 1)
```

Both fail exactly on the documented faults. After the repair both pass (check b).

## 5. Tests and the guard battery

- `test_result_ways_truth_table.py` (new): 62 cases — 56 parametrised rows (one per table row,
  each with its own id) pinning the way + kind + meaning-bearing reason parts (condition named,
  measured value, ABSENCE of the words of a condition that holds); S1, S2, S3, S4; US4
  resolved_by; two whole-answer-reason tests. The parametrised test pins the WAY of every state
  (S6).
- `test_result_ways.py` `_battery()`: added the two states the claim-head battery missed
  (EVIDENCE_NOT_IN_ONE; a corner whose angle fails) so every invariant/guard sees them.
- `test_result_way_bridge.py`: the guard `_texts_of` now includes `held_back`, and a new test
  `test_the_two_held_back_strings_are_plain_db175_f` pins DB-175 (f) — no "this piece", plain.
- `test_result_ways_input_states.py` `_wide_text_battery` already covers the EVIDENCE_NOT_IN_ONE
  and angle-140 branches through the no-internal-name guard (unchanged; now true texts).

## 6. Mutation proofs (one per corrected branch, OUTSIDE the repository)

`mutate.py` copies the six module files into a throwaway `mutmod/` package (external `app.*`
resolves from the real checkout), then for each corrected branch applies one mutation that reverts
it to a wrong text and runs the branch's pinning assertion in a fresh subprocess. Clean baseline:
every assertion passes unmutated. Result:

```
ALL MUTATIONS CAUGHT: True
  US5_evidence_not_in_one     -> CAUGHT        RY8_angle_fails           -> CAUGHT
  US4_not_given_resolved_by   -> CAUGHT        USR1_senior               -> CAUGHT
  RY2_interior                -> CAUGHT        WA2_multi_reason          -> CAUGHT
  RY5_angle_unknown           -> CAUGHT        RY4_reach_unknown_helper  -> CAUGHT
  HB1_held_back_lot_type      -> CAUGHT        HB2_held_back_density      -> CAUGHT
```

## 7. Checks (direct exit codes)

| Check | Command (from) | Result | Exit |
|---|---|---|---|
| a | `python -m ruff check .` (services/api) | All checks passed | 0 |
| b | `pytest -q tests/scenario/three_answers` (services/api) | 229 passed, 2 skipped | 0 |
| c | `pytest -q tests/contracts tests/journey tests/spatial/test_lot_reach.py` | 572 passed | 0 |
| d | `python3 tools/modularity_check.py --check` (repo root) | failures 0; 29 warnings (none new) | 0 |
| e | red proof S1/S2 against claim-head module | 2 failed (expected) | 1 |
| e | mutation proofs (`mutate.py`, outside the repo) | all 10 caught | 0 |
| f | `git status --porcelain` / `git diff --name-status` | only allowed paths (section 8) | — |

The full api suite was NOT run (the orchestrator runs it on the wave's final candidate).

## 8. Modularity

`result_ways.py` 614 physical lines (≈557 source lines incl. docstrings); still below the
600-SLOC warning threshold — `modularity_check --check` does not list it (exit 0). Per the
packet's modularity answer the texts stay with the deciders that own them; the only new module-
level code in `result_way_conditions.py` is the two small shared helpers (`format_angle`,
`rear_yard_unmeasured`). WATCH: `result_ways.py` is approaching the warning threshold; the next
substantial growth should move the decider texts into a focused `result_way_*.py` module.

## 9. Open question (reading O19) — listed, NOT decided

Whether the legal dwelling-unit limit should be SHOWN (rather than withheld) when evidence records
the lot OUTSIDE a special density area is an open question. This task leaves US5 withheld as owed
work (O10/O19) and only corrects the explanation; the show/withhold decision is left to the
reviewers / a later task.

## 10. Texts a user may see (plain words, for the walkthrough)

- Rear yard, angle fails: "The rear-yard waiver does not apply: the two street lines meet at 140
  degrees, more than the rear-yard waiver's limit of 135 degrees; the far corner is 90 ft from
  the point where the two street lines meet, within 100 ft of it. What the ordinary rear yard
  requires where the waiver does not apply is not settled."
- Standard unit limit, evidence the lot is outside a special density area: "Evidence records this
  lot outside a special density area; how the legal dwelling-unit limit is shown on that evidence
  has not been worked out and checked against an independently worked example, so the legal
  dwelling-unit limit is not known."

## 11. Round 2 (orchestrator's reading of 795c29ee; same worktree, one more commit)

Four "resolved by" / truthfulness corrections. No way and no kind changed (the full
`(key, way_type, gap_kind)` signature across all states is still byte-identical to the claim
head). Corrected texts, one line each:

- RY4 (corner reach not measured, angle known) `resolved_by` → "Measuring the far corner's reach
  from the point where the two street lines meet, from the recorded outline and its street lines."
  (names only the missing reach, not the known angle).
- RY5 (angle not measured, reach KNOWN) `resolved_by` → "Measuring the angle at which the two
  street lines meet, from the recorded outline and its street lines." (names only the missing
  angle, not the known reach).
- RY6 (both missing) `resolved_by` → "Measuring the far corner's reach and the angle at which the
  two street lines meet, …" (names both). `rear_yard_unmeasured` now sets `need` per state.
- WA2 (`_answer`, values withheld for >1 reason) `resolved_by` → now names every distinct value's
  "resolved by" in value order (no duplicates); single text when all are the same.
- USR1 qualifying senior: reason no longer asserts a "separate rule" exists → "…sets no factor for
  qualifying senior housing (ZR 23-52(a)(2)), so this formula gives no unit limit for it; whether
  any other provision limits the number of units has not been checked, … it is not set by this
  formula." `resolved_by` → "Checking whether any other provision limits the number of units for
  qualifying senior housing and checking the result against an independently worked example."
- US4 (density not given): re-added the clause "where the dwelling-unit formula does not apply"
  (the rest of the round-1 text unchanged).

Table rows marked round 2: RY4, RY5, RY6 (resolved_by), WA2 (resolved_by), USR1 (reason +
resolved_by), US4 (reason).

Sharper check (b) swept over EVERY row's `resolved_by` (question: does it name anything the state
already holds?). Caught: RY4/RY5/RY6 (asked for a held measurement) and WA2 (named only the first).
No OTHER row caught. Considered and cleared: UA1 affordable ("Connecting the rule for qualifying
affordable housing …" — ZR 23-52 does set an affordable factor, so a rule is known; names nothing
held); C6 large-lot-not-stated ("Comparing the recorded lot area with the lot size …" — names the
recorded area only as the input to the owed comparison, does not ask the user to supply it); US2
`settled_by` ("A sourced fact …" — the state holds an unsourced user statement, not a sourced
fact).

Round-2 tests: USR1 and US4 table rows updated; three new tests — rear-yard-unmeasured resolved_by
per state, whole-answer resolved_by names every distinct text, senior text asserts no separate
rule. 232 cases in `tests/scenario/three_answers` now.

Round-2 checks: a `ruff` exit 0; b `pytest tests/scenario/three_answers` 232 passed, 2 skipped,
exit 0; c `pytest tests/contracts tests/journey tests/spatial/test_lot_reach.py` 572 passed, exit
0; d `modularity_check --check` exit 0; mutation proofs (outside the repo, `mutate2.py`) — 4 of 4
caught (RY5 resolved_by, WA2 resolved_by, senior "separate rule", US4 formula clause), exit 0.
