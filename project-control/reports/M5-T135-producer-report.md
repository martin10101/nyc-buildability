# M5-T135 producer report - the measurement-basis record brought up to date

Producer: scenario-optimization-engineer (an AI agent), in an isolated worktree, reset to the
claim head `599f9b0ca0540212f3cdd670d1a4eb4aed78e093` before any edit. This is a draft reading
of the law by an AI, not professionally reviewed (ADR-007). Documents, one example's data +
page, and the examples' own test files only; no estimator, no program code, no rule file, no
reference case, no capture changed. No ledger command; no push.

## 1. The sentence-by-sentence change table (old -> new, with its source)

Source = an owner row quoted verbatim from
`project-control/directives/D-090-product-plan-2026-09-28-start-building/source-057-amendment.md`,
or a capture id + its `content_digest_sha256` read from the capture file under
`docs/research/zr-snapshots/v1/`. 14 changed statements.

### MEASUREMENT_BASIS.md

| # | Where | Old | New | Source |
|---|---|---|---|---|
| 1 | Intro "What this record does not do" | "...remain **unapproved assumptions**; this record validates none of them." | "...are **preliminary, editable assumptions** the owner approved only as a starting point on 2026-10-07 (section 8a); this record validates none of them, and the owner's approval validates neither the assumptions nor the worked examples (R545)." | owner R539, R545 |
| 2 | Section 4 | (no owner attribution) | added: 'This is the owner's decision of 2026-10-07 (R544): "Use the residential floor area the proposed building actually accommodates."' | owner R544 |
| 3 | Section 5 | (no owner attribution) | added: 'This is the owner's decision of 2026-10-07 (R544): "Keep the legal ceiling separate."' | owner R544 |
| 4 | Section 7 | "...remain unapproved assumptions, and these examples validate none of them." | "...remain preliminary, editable assumptions, and these examples validate none of them (the owner's approval validates neither the assumptions nor the worked examples, R545)." | owner R545 |
| 5 | Section 1d (energy) | "The energy exclusion's eligibility is **not captured yet** (R516)... the two defined terms... are **not captured yet** (M4-T034)... eligibility is withheld" | captured reading: a fully electrified building must exist on December 6, 2023 (so a new building cannot be one); an ultra low energy building is put forward at plan approval and confirmed only after construction; still not sure = Local Law 154 / the energy code (DB-188 item 7) | zr-12-10-floor-area `e14ecafc...d6f9`; zr-12-10-fully-electrified-building `2ea4afe2...9321c`; zr-12-10-ultra-low-energy-building `8a1d6418...0203`; DB-188 item 7 |
| 6 | Section 6 "What is not settled" -> "...now read from the captures" | "...the reviewer names as ZR 35-31 - is **not captured yet** (M4-T034)... withheld until the text is captured and read" | reading: ZR 35-30 title-only umbrella; ZR 35-31 per-use max FAR + one combined whole-lot cap + the shared-attribution (no comma before "less"); ZR 35-32/35-33 do not reach a C2-2 overlay within R6B | zr-35-30 `b1102df9...2def`; zr-35-31 `65e29c68...80fe`; zr-35-32 `d1aad127...c42a`; zr-35-33 `de947f0a...f8e4`; zr-12-10-mixed-building `6eb9a389...27e0` |
| 7 | Section 6 "What is still not sure" (new) | - | commercial FAR of Article III, Chapter 3 is **not captured yet** (DB-188 item 1), so the whole-building maximum is "not sure"; whether the attributed shared floor area is ADDED to the residential figure is a question of law | DB-188 item 1; R515 |
| 8 | Section 6 "Example C shows the step" | "...labelled **conditional** on the mixed-building text not yet read" | "...stays **conditional** ... because the commercial floor area ratio is still missing and the add-to-residential question of law is unsettled" | DB-188 item 1; R515 |
| 9 | Section 8 intro | "Nothing below is decided. The open points..." | "These were the **open points**... the **choices for the owner**... which the owner **decided on 2026-10-07**... the **questions of law**... an owner's choice is never written as law." | owner message 113; R515 |
| 10 | Section 8a heading + 5 items + floor-area note | each item "*Recommended by the owner's reviewer... NOT decided until the owner says so*" | each DECIDED BY THE OWNER on 2026-10-07, verbatim owner fragment + row id, framed preliminary/editable; R545 stated plainly | owner R539, R540, R541, R542, R543, R544, R545 |
| 11 | Section 8b-2 | "What is **not captured yet** is the mixed-building floor-area rule... (the reviewer names ZR 35-31)... withheld" | reading now in section 6; residual narrowed: commercial FAR (Article III Ch 3) **still not captured** (DB-188 item 1); add-to-residential is a question of law | DB-188 item 1; R515 |
| 12 | Section 8b-3 | energy terms "**not captured yet** (M4-T034); its eligibility is withheld" | energy terms now read (section 1d); residual = Local Law 154 / the energy code **still not captured** (DB-188 item 7) | DB-188 item 7 |
| 13 | Section 9 sources | "Not captured yet (captured by M4-T034, not read here): ... ZR 35-31, and the ... 'fully electrified building' and 'ultra low energy building'." | zr-35-30..33 + the two energy definitions listed as captured/read; "Still owed, not captured yet" = commercial FAR (Article III Ch 3) + Local Law 154 / the energy code | captures above; DB-188 items 1, 7 |

### example-c-mixed-use.json (+ re-rendered .md; NO figure changed)

| # | Field | Old | New | Source |
|---|---|---|---|---|
| 14a | `what_it_does_not_show[1]` | "...withheld until the mixed-building text (ZR 35-31) is captured and read." | "ZR 35-31 is now captured and read (M4-T035 step P5), but ... stays withheld because the maximum commercial floor area ratio (Article III, Chapter 3) is still not captured (DB-188) and whether the attributed shared floor area is added to the residential figure is a question of law." | DB-188 item 1; R515 |
| 14b | `shared_floor_area.conditional_note` | "...(the reviewer names ZR 35-31), which are not captured yet, so the effect ... is withheld." | "ZR 35-31 is now captured and read (M4-T035 step P5) ... stays WITHHELD because the maximum commercial floor area ratio (Article III, Chapter 3) is still not captured (DB-188) ... question of law, not an owner's preference." | DB-188 item 1; R515 |
| 14c | `change_log` | - | added 2026-10-08 entry naming the two corrected statements and that NO figure changed (ratio 0.6828; attribution 98.32 / 21.68) | this task |

No figure of any example changed: ratio stays 0.6828; attribution stays 98.32 sq ft residential /
21.68 commercial; residential exclusive zoning floor area stays 10,428. Examples A and B are
byte-unchanged (`git diff` touches neither). I found no further false statement in any example.

## 2. Red proof (new tests fail on the record as it stands)

`pytest -k "section_8a_records or now_read_text or new_law_quote"` against the UNEDITED claim-head
record: **3 failed, 38 deselected**, exit code **1**. The three new checkers, run (final form, with
whitespace/blockquote normalisation) against the claim-head record text extracted with
`git show 599f9b0c:...MEASUREMENT_BASIS.md` in a copy OUTSIDE the repository:

```
T1 section_8a_decisions_errors: 14 errors   (section 8a still says 'NOT decided')
T2 stale_not_captured_errors : 9 errors     (ZR 35-31 and the two energy definitions marked 'not captured yet')
T3 new_law_quote_errors      : 18 errors    (the new quotes/digests are absent)
```

Against the EDITED record all three return `[]`.

## 3. Mutation proofs (one per new test, in a copy OUTSIDE the repository)

```
T1  0.60 to 0.75 -> 0.50 to 0.90                     -> 1 error  ("...does not record the needle '0.60 to 0.75'")
T2  append "ZR 35-31 is not captured yet."           -> 1 error  ("...pairs now-read 'zr 35-31' with 'not captured yet'...")
T3  ZR 35-31 digest 65e29... -> 64 zeros             -> 3 errors ("...lacks the zr-35-31 digest 65e29...")
```

Each mutation makes its test's checker non-empty (bites). Script + copies:
`<scratchpad>/mb_proofs.py`, `record_claimhead.md`, `record_edited.md` (outside the repo).

## 4. What stays "not sure" (named, not captured)

- The maximum **commercial** floor area ratio of **Article III, Chapter 3** (DB-188 item 1), and
  therefore the whole-building maximum of a mixed building. ZR 35-31 sends the commercial ratio
  there; both step-P5 readers lacked it, so it is recorded "not sure".
- **Local Law 154 of 2021** and the **New York City Energy Conservation Code** (DB-188 item 7,
  outside the Zoning Resolution), on which both energy definitions rest.
- Whether the attributed shared floor area is **ADDED** to the residential floor area the estimate
  uses - a **question of law** (R515), not an owner's preference; the examples' figures do not
  depend on it.
- The order of the amenity 5 percent calculation when the cap binds (section 8b-1, unchanged).

## 5. Checks (each with its DIRECT exit code)

From `services/api`, lanes venv, `PYTHONDONTWRITEBYTECODE=1`, pytest `-p no:cacheprovider`:

- a. `python -m ruff check .` -> `All checks passed!` **exit 0**
- b. `python -m pytest -q -p no:cacheprovider tests/scenario/measurement_basis` -> **41 passed** **exit 0** (baseline 38 + T1/T2/T3)
- c. `python tests/scenario/measurement_basis/measurement_basis_render.py --check` -> `measurement-basis check PASSED (no issues)` **exit 0** (pages byte-identical to the renderer)
- d. (repo root) `python3 tools/modularity_check.py --check` -> `failures 0; warnings 29` **exit 0** (all 29 warnings are pre-existing, on files this task did not touch)
- e. red proof: pytest of the three new tests on the unedited record -> 3 failed **exit 1**; final-checker red proof + mutation proofs script -> **exit 0** (outputs in sections 2-3)
- f. `git status --porcelain` -> only the 7 allowed paths **exit 0**; `git diff --name-status 599f9b0c HEAD` -> the 6 material files (+ this report) **exit 0**

Support-file line counts stay focused: `measurement_basis_check.py` 594, `test_...py` 560,
`measurement_basis_fit.py` 289 (all < 600; `test_support_files_are_focused` passes).

## 6. Known-red consumers re-aimed (no silent red left)

- `measurement_basis_check.record_errors()`: the `'not captured yet'` needle description re-aimed
  to the still-owed texts; the `fully electrified` / `ultra low energy` needle descriptions marked
  now-read. The needles themselves are kept and still match.
- `measurement_basis_fit.shared_floor_area_errors()`: the old "must say ... not captured yet"
  check re-aimed to require the note NOT call ZR 35-31 "not captured yet" and to stay
  withheld/conditional on the commercial FAR or the question of law.
- `test_measurement_basis_examples.py` line ~315: the conditional-note assertion re-aimed the same
  way.

## 7. Stopped on / doubt

- Nothing blocked. One judgement recorded: the intro and section 7 said the starting values
  "remain **unapproved assumptions**", which the owner's 2026-10-07 approval (R539) made false and
  self-contradictory with the new section 8a; I corrected both to "preliminary, editable
  assumptions" while keeping, verbatim, that neither this record nor the owner's approval validates
  them (R545). This is beyond the three explicitly-enumerated out-of-date areas but keeps the record
  truthful and internally consistent (the M5-T133 lesson: sweep the whole record for stale phrases).
- Owner quotes reproduce the exact glyphs of source-057 (en-dash in "0.60–0.75", curly quotes in
  the R543 label sentence); the ASCII forms "0.60 to 0.75", "Not known", "Preliminary capacity
  estimate" also appear in the framing.

END-OF-REPORT
