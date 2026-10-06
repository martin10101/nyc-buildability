# M4-T024 producer report - the R6B reference cases as files of their own (step R0)

Producer: rules-engineer. Worktree: `/root/project/nyc-buildability/.claude/worktrees/agent-a06409f10d1e19781`.
Claim-seam head: `1fdd6d9980c03ee0d516e480d4fa1c5142f2f11f`. This is producer evidence only; a different
agent reviews the work and re-derives every number.

## What was built

The four independently worked reference cases moved into files of their own, each as one structured
data file plus one page rendered from it, with the helper's two returns kept unchanged as provenance, a
stdlib checker/renderer/loader under the test tree (no engine import), and a test that recomputes every
arithmetic step, checks every capture digest and proves no case file carries a program result.

Files written:

- `docs/reference-cases/R6B/README.md` - what a reference case is and is worth, the change rule, the
  list of cases, the not-captured sections (waiting for step P1), how a test uses a case.
- `docs/reference-cases/R6B/cases/real-lot.json`, `interior-lots.json`, `corner-reach.json`,
  `suffix.json` - the four structured data files.
- `docs/reference-cases/R6B/real-lot.md`, `interior-lots.md`, `corner-reach.md`, `suffix.md` - one page
  per case, rendered from the data file (byte-identical to the renderer's output).
- `docs/reference-cases/R6B/provenance/return-independent-hand-calculation-1.md` and
  `return-independent-hand-calculation-2.md` - the helper's two returns, unchanged, each under a short
  header (what it is, when, under which rules).
- `services/api/tests/rules/reference_cases/r6b_reference_cases_lib.py` (loader + exact-decimal
  arithmetic engine + paths), `r6b_reference_cases_check.py` (checker), `r6b_reference_cases_render.py`
  (renderer + `--write`/`--check` CLI), `test_r6b_reference_cases.py` (the acceptance pack).

Each data file is one JSON object with fixed-key rows. A row carries: the facts used with their source;
the citations (captured = snapshot id, file, content digest, official page, the quote, and a table
assertion where the value is a table cell; not_captured = official page, date read, status note, the
read text); why the rule applies; the arithmetic steps (operands, operation, rounding, result); the
expected value or kind `not_known` with its reason; where the value stands in the independent reading;
and what the row does not establish. Each case also carries prepared_by, checked_by, sources and a
change log (first entry = creation, 2026-10-06).

## Row count, by case

| Case | Rows | Numeric expected values | `not_known` rows | Other (categorical / conclusion) |
|---|---|---|---|---|
| real-lot (table A, L1-L15) | 15 | 3 (L1, L2, L6) | 6 (L5, L7, L8, L12, L14, L15) | 6 (L3, L4, L9, L10, L11, L13) |
| interior-lots (table B) | 9 | 8 (4 floor-area, 4 units) | 0 | 1 (interior-coverage) |
| corner-reach (table C) | 12 | 0 (expected values are prose; the diagonals/strip are recomputed inside the rows) | 5 (real-lot-coverage, real-lot-rear-yard, C1-rear-yard, C3-coverage, C3-rear-yard) | 7 (the reach rows and the settled coverage/rear-yard conclusions) |
| suffix (table D) | 5 | 0 | 0 | 5 (the suffix conclusions) |

## Every row, its expected value, and where it stands

### real-lot (table A). Source = `return-independent-hand-calculation-1.md`.
| Row | Expected value | Helper return | Work order |
|---|---|---|---|
| L1 | 20,150 sq ft | Task 1(c) "2.00 x 10,075 = 20,150 sf" | A L1 (20,150) |
| L2 | 24,180 sq ft | Task 1(c) "2.40 x 10,075 = 24,180 sf" | A L2 (24,180) |
| L3 | base 30 to 45 ft; building 55 ft | Task 1(d) | A L3 (30/45/55) |
| L4 | base 30 to 45 ft; building 65 ft | Task 1(d) | A L4 (30/45/65) |
| L5 | not known (coverage) | Task 1(e) + return 2 Q1 | A L5 (not known, K1) |
| L6 | 29 dwelling units | Task 1(g) "20,150/680 = 29.63 -> 29 DU" | A L6 (29) |
| L7 | not known (qualifying affordable units) | Task 1(g) "35" + Task 3 item 9 | A L7 (indep 35 / first screen not known, K13) **DIFFERENCE 1** |
| L8 | not known (qualifying senior units) | Task 1(g) "no applicable dwelling unit factor" | A L8 (not set by this formula) |
| L9 | corner | Task 1(a) "89.7 deg <= 135 -> corner" | A L9 (corner) |
| L10 | Northern Boulevard 103.9 ft; 215 Place 100.0 ft | Task 1(a) | A L10 |
| L11 | Northern wide (100 ft), 215 Place narrow (60 ft); no R6B effect | Task 1(b) | A L11 |
| L12 | not known (rear yard beyond the corner area) | Task 1(f) + return 2 Q1(c) | A L12 (not known, K4) |
| L13 | 10 ft on the wide street; 15 ft on the narrow street | Task 1(d) | A L13 (10/15) |
| L14 | not known (ordinary rear-yard depth) | Task 1(f), Task 3 item 4 | A L14 (not known) |
| L15 | not known (building option, floor plates, floors) | (no independent example) | A L15 (no independent example) |

### interior-lots (table B). Source = `return-independent-hand-calculation-1.md`, Task 2.
| Row | Expected value | Work order |
|---|---|---|
| P1-floor-area / P1-units | 10,000 sq ft / 14 | B P1 (10,000 / 14) |
| P3-floor-area / P3-units | 10,700 sq ft / 15 | B P3 (10,700 / 15) |
| P4-floor-area / P4-units | 10,720 sq ft / 16 | B P4 (10,720 / 16) |
| P5-floor-area / P5-units | 10,710 sq ft / 16 (15.75 exactly -> rounds up) | B P5 (10,710 / 16) |
| interior-coverage | 80 percent | B note (ZR 23-362(a)) |

### corner-reach (table C). Source = `return-independent-hand-calculation-2.md`.
| Row | Expected value | Helper return |
|---|---|---|
| real-lot-reach | 99.97 ft (Northern Blvd line); 103.93 ft (215 Place line); 144.60 ft (corner); strip ~390 sq ft, wedge ~2,560 sq ft | Q1(a)-(c) |
| real-lot-coverage | not known | Q1(a)-(b) |
| real-lot-rear-yard | not known (beyond the corner area) | Q1(c) |
| C1-reach | 100.00 / 40.00 ft; diagonal 107.70 ft | Q2 C1 |
| C1-coverage | 100 percent | Q2 C1(i) |
| C1-rear-yard | not known (beyond the corner area) | Q2 C1(ii) |
| C2-reach | 80.00 / 60.00 ft; diagonal 100.00 ft | Q2 C2 |
| C2-coverage | 100 percent | Q2 C2(i) |
| C2-rear-yard | no rear yard required anywhere | Q2 C2(ii) |
| C3-reach | 100.00 / 150.00 ft; strip 50 ft x 100 ft = 5,000 sq ft; diagonal 180.28 ft | Q2 C3 |
| C3-coverage | not known (no single figure) | Q2 C3(i) |
| C3-rear-yard | not known (beyond the corner area) | Q2 C3(ii) |

### suffix (table D). Source = `return-independent-hand-calculation-2.md`, Q3.
| Row | Expected value |
|---|---|
| 23-362 | applies to R6B, through ZR 11-25 |
| 23-52 | applies to R6B, through ZR 11-25 |
| 23-344 | applies to R6B, through ZR 11-25 |
| 23-22 | lists R6B directly; no suffix step needed |
| 23-432 | lists R6B directly; no suffix step needed |

## Differences found between the work order's tables and the helper's returns (reported, not resolved silently)

**DIFFERENCE 1 - L7, qualifying-affordable units.** The helper's return (Task 1(g)) and the work order's
table A "Independent value" column both give **35** (24,180 / 680 = 35.56, dropping a fraction below
three-quarters). But the helper's own Task 3 item 9 flags that the definition of "qualifying affordable
housing" is not in the sealed folder, so whether this lot may use the 2.40 ratio at all is not settled;
the work order's gap K13 and first-screen column, and the packet scenario S7, record qualifying-housing
unit counts as **not known**. The case records L7 as `not_known` (no number) and preserves the
24,180 / 680 = 35.56 -> 35 arithmetic inside the row's reason as a conditional illustration. This
tension is reported here and noted in the row; it is not resolved silently.

**DIFFERENCE 2 - the "P2" interior probe is dropped.** The helper's first return (Task 2 table) includes
a "P2 corner 4,000 sq ft" probe (8,000 sq ft floor area, 100 percent coverage, 11.76 -> 12 units). The
work order dropped it from table B and replaced it with C1 in table C (its note: "The first version's
row 'P2, corner, 4,000 sq ft, 100 percent' gave no shape. It is replaced by C1."). The packet (S1)
lists table B as P1, P3, P4, P5 only. The case follows the packet and the work order: P2's 12-unit value
is not carried in the interior-lots case; the 40 ft x 100 ft corner lot C1 is in the corner-reach case.
Reported.

**Not a value difference, noted for completeness:** (a) the helper shows the division quotients to four
decimals (14.7059, 15.7353, 15.7647) while the work order shows three (14.706, 15.735, 15.765); the
final unit counts are identical and the pages show the quotient truncated to two decimals with the same
result. (b) The helper also gives "alternate" figures from the 10,388 sq ft outline area (20,776;
24,931; 30; 36). The cases use the 10,075 sq ft city-record area, per the work order's section 6 (the
outline area is a drawing measure and is never used in a calculation); the alternate is recorded only as
context in L1's "does not establish". (c) L10 frontage uses the helper's independent 103.9 ft, not the
raw edge length 103.88 ft that the work order shows in its "Program today" column.

## Sections cited that are not captured (named in the README as waiting for step P1)

- **ZR 12-10** lot-type ("lot, corner") definition and the corner-lot-portion clause - the repository
  capture of ZR 12-10 holds only the wide-street and narrow-street definitions. Cited `not_captured`
  (official page read 2026-10-06) in real-lot L5 and L9 and in the corner-reach coverage rows.
- **ZR 23-342** rear-yard requirements (the ordinary rear-yard depth). Cited `not_captured` in L14.
- **ZR 23-363** special coverage rules for some interior and through lots. Named in prose
  (interior-coverage "does not establish") and in the README; not a formal citation (the helper did not
  read it).

The captured sections the cases rely on - ZR 23-22, 23-432, 23-362, 23-52, 23-344, 23-433, 11-25 and the
wide/narrow part of 12-10 - each match the live snapshot's `content_digest_sha256`, and the quoted words
are present in the capture (the checker verifies both).

## Checks (one at a time, with direct exit codes)

| Check (from `services/api` unless noted) | Result | Exit |
|---|---|---|
| `python -m ruff check tests/rules/reference_cases` | All checks passed | 0 |
| `python -m pytest -q -p no:cacheprovider tests/rules/reference_cases` | 30 passed | 0 |
| `python tests/rules/reference_cases/r6b_reference_cases_render.py --check` | reference-case check PASSED (no issues) | 0 |
| `python3 tools/modularity_check.py --check` (repo root) | pass; warnings only on pre-existing `tools/agent_supervisor/*` files, none of mine | 0 |
| `python3 scripts/lanes/check_lane_paths.py --coverage` (repo root) | LANE COVERAGE PASS: 8762 file(s) | 0 |
| mutation proofs (`pytest -k mutation_proof`) | 4 passed | 0 |
| `python -m pytest -q -p no:cacheprovider` (full api suite) | 8074 passed, 8 skipped | 0 |

New source files, line counts (all under the 600-line warning threshold): lib 248, check 390, render
290, test 319.

## The two mutation proofs

- **S5 (arithmetic).** A deep copy of real-lot L1 with the lot-area operand changed from 10,075 to
  10,076 recomputes to 20,152, so `recompute_row_errors` returns an error naming `real-lot/L1`
  (and a second proof changes P5-units' result from 16 to 15 and fails naming `P5-units`).
- **S6 (capture).** A deep copy of real-lot L1 with the ZR 23-22 content digest changed to sixty-four
  zeros makes `citation_errors` fail with a digest-mismatch message (and a second proof replaces the
  quote with text absent from the capture and fails with "not found in the capture").

## One row, exactly as rendered (real-lot L6)

```
### L6 - Maximum dwelling units, standard residences

Facts used:

- Maximum residential floor area, standard = 20,150 sq ft (source: row L1)
- Dwelling-unit factor = 680 (source: ZR 23-52(b))

Law relied on:

- ZR 23-52 (Maximum Number of Dwelling Units) - captured.
  - Capture: snapshot `zr-23-52`, file `docs/research/zr-snapshots/v1/zr-23-52.snapshot.json`.
  - Content digest: `f48f1ddc189866ea7fae015edb983411c6de5032d0f9ce98a47cdca4d7b908ac`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52.
  - Quoted: "the applicable dwelling unit factor shall be 680. Fractions equal to or greater than three-quarters resulting from this calculation shall be considered to be one dwelling unit"

Why the rule applies: ZR 23-52 divides the maximum residential floor area by the dwelling-unit factor; for standard multiple-dwelling residences the factor is 680, and a fraction of three-quarters or more counts as one unit, otherwise it is dropped.

Working, step by step:

- maximum dwelling units, standard: 20,150 (maximum residential floor area, standard (sq ft), from row L1) / 680 (dwelling-unit factor (ZR 23-52(b))) = 29.63...; a fraction below three-quarters is dropped -> 29

Expected value: 29 dwelling units

Where this stands in the independent reading: return-independent-hand-calculation-1.md, Task 1(g): '20,150/680 = 29.63 -> frac 0.63 <0.75 -> 29 DU'.

What this row does not establish: It is the legal unit limit for a new all-residential building and rests on the standard floor area (row L1), hence on the city-record lot area. Whether the lot is in a special density area, where the factor does not apply, is not settled by the captured text.
```

## Doubts / things not done

- L7 was recorded as `not_known` (DIFFERENCE 1). A reviewer should confirm that treating the
  qualifying-affordable unit count as not known (eligibility not captured), rather than as the
  arithmetic value 35, is the intended reading; both the helper's number and the eligibility caveat are
  disclosed in the row and above.
- The corner-reach reach distances for the real lot (99.97, 103.93, 144.60 ft and the ~390 / ~2,560
  sq ft areas) are the helper's coordinate-geometry measurements, taken as given and cited to return 2;
  they are not recomputed by the test (the C1/C2/C3 diagonals and the C3 strip are recomputed). The
  program was not run to fill, check or confirm any value.
- No rule file, rule engine, capture, plan or review register changed; the checker, renderer, loader and
  test import nothing from the rule or scenario engine (verified by an AST import scan in the test).
