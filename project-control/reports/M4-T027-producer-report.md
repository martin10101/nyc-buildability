# M4-T027 producer report - the R6B reference cases worked from the text captured in step P1

Producer: rules-engineer (isolated worktree
`/root/project/nyc-buildability/.claude/worktrees/agent-ae2e998ca0665ce16`).
Contract head reset to `8dd39c9f0d2c09bc596063eaf259dc658f29b1c5`.
Nothing comes from a program run; no `services/api/app/**` was read or changed. Values come only from
the two independent step-P1 readings and the pinned law captures; a value is recorded only where both
readings agree on the same basis.

## 1. Provenance saved unchanged (allowed path `docs/reference-cases/R6B/provenance/`)

Each reading saved below a short header, byte-for-byte below a `---` separator. The embedded body was
verified byte-identical to the source `.txt`.

| File | source | file sha256 (pinned in the checker) |
|---|---|---|
| `return-independent-hand-calculation-3.md` (reading 1) | return-reading-1.txt | `8e0fb09e6d7f4fa946fdf1e4bd5ef8a2c5847fa6ff981779a84a91aff40ff64b` |
| `return-independent-hand-calculation-4.md` (reading 2) | return-reading-2.txt | `5bf5ab28a65af7635e4ea72808e609f4559cfa1f695bcbaf2150164c03f6d639` |

Each reading says it was made from the sealed folder with no access to the program/repository
(`check.step_p1_reading_errors()` verifies marker + END-OF-REPORT + "sealed folder" + the digest).

## 2. Existing rows changed (no expected VALUE changed; citations upgraded, reasons refined)

Step P1 (task M4-T025) captured ZR 12-10 (lot-type, lot-area, special-density definitions), ZR 23-342
and ZR 23-363, so the "not captured" citations/reasons were corrected. Reason for every entry below:
**newly captured text (M4-T025)** - never a program disagreement. A dated change-log entry was added
to each affected case.

`real-lot.json`:
- **L5** maximum lot coverage: not known -> not known (unchanged). 12-10 citation not-captured ->
  captured `zr-12-10-lot-corner`; reason now records per-portion 100% (corner) / 80% (remaining
  interior), no single whole-lot figure.
- **L9** lot type: `corner` -> `corner` (unchanged). 12-10 citation not-captured -> captured
  `zr-12-10-lot-corner`; both step-P1 readings confirm corner.
- **L12** rear yard: not known -> not known (unchanged). Added captured `zr-23-342`; reason no longer
  says 23-342 is uncaptured (depth needs building type/lot width; beyond-100-ft needs neighbour).
- **L14** ordinary rear-yard depth: not known -> not known (unchanged). 23-342 citation not-captured
  -> captured `zr-23-342`; reason: depth is 20/30 ft by building type and lot width, not given.

`corner-reach.json`:
- **real-lot-coverage**: not known -> not known. 12-10 -> captured; per-portion 100/80 recorded.
- **real-lot-rear-yard**: not known -> not known. Added captured `zr-23-342`.
- **C1-coverage** (40x100): `100 percent` -> `100 percent`. 12-10 -> captured.
- **C2-coverage** (60x80): `100 percent` -> `100 percent`. 12-10 -> captured.
- **C3-coverage** (150x100): not known -> not known. 12-10 -> captured; noted the step-P1 readings'
  150x100 lot (their C2) reads the same per-portion 100/80.
- **C1-rear-yard** (40x100): not known -> not known. Added captured `zr-23-342`.
- **C3-rear-yard** (150x100): not known -> not known. Added captured `zr-23-342`.

`interior-lots.json`:
- **interior-coverage**: `80 percent` -> `80 percent`. Added captured `zr-23-363`; does-not-establish
  now says 23-363 may only INCREASE (to 90% shallow, or 100% near a corner/short block dimension),
  never decrease, and does not change the 80% on bare facts.

## 3. Rows added (new case `docs/reference-cases/R6B/cases/step-p1-worked.json` + `.md`)

Twelve rows; each names both readings; value only where both agree on the same basis.

| row | expected | basis |
|---|---|---|
| lot-area-definition | value: "the area of a zoning lot" | both: ZR 12-10 lot area |
| corner-100x100-coverage | value: 100 percent (whole lot) | both: whole lot = corner portion (S4 geometry shown) |
| corner-150x100-coverage | not known (per portion: 100% / 80%) | both: ZR 12-10 corner portion + 23-362(a) |
| corner-150x100-rear-yard | not known | both: 344(a) within 100 ft; beyond not settled |
| corner-200x120-coverage | not known (per portion: 100% / 80%) | both |
| corner-200x120-rear-yard | not known | both |
| interior-40x100-coverage | value: 80 percent | both: 23-362(a); 23-363 no change on bare facts |
| interior-40x100-rear-yard | not known | **readings DIFFER** (see sec 4) |
| through-40x200-coverage | value: 80 percent | both: 23-362(a) through lot; not shallow |
| through-40x200-rear-yard | not known | both: governed by ZR 23-343, not captured |
| special-density-areas-list | value: lists (a) Manhattan Core and (b) Special Downtown Brooklyn District | both |
| special-density-real-lot | not known | both: Queens strongly implies no; boundary defs not captured |

New corner lots use the step-P1 readings' labels C1=100x100, C2=150x100, C3=200x120; ids are
dimension-based (`corner-100x100` ...) to avoid colliding with corner-reach's own C1/C2/C3 (40x100,
60x80, 150x100). S4 respected: a whole-lot 100% is stated only for the 100x100 lot, whose geometry
shows the corner provision covers the whole lot; the 150x100 and 200x120 lots are per portion.

## 4. Where the two readings differ (recorded as not known, both named; no winner picked)

- **40x100 interior-lot rear-yard depth** (row `interior-40x100-rear-yard`): reading 1
  (calc-3, Q3b) leaves the depth NOT KNOWN (building type not given; which dimension is the lot width
  not stated). Reading 2 (calc-4, Q3b), assuming 40 ft is the lot width, reads ZR 23-342 to give 20 ft
  at/below 75 ft (30 ft above) because at width >=40 both building-type branches give 20 ft. They
  differ and rest on different assumptions -> row is not known, naming both.

Two side nuances that are NOT disagreements (same conclusion, recorded as the agreed value with the
nuance noted in does-not-establish): (a) special-density exhaustiveness - reading 1 says "shall
include" may be non-exhaustive, reading 2 treats the list as closed, but both list the same two areas;
(b) 40x200 through-lot shallow test - reading 1 calls the depth ambiguous, reading 2 says 200>=190 not
shallow, but both conclude 23-363 does not change the 80% on bare facts.

## 5. What stays "not known"

Real lot: whole-lot coverage (per portion only), rear yard beyond 100 ft of the corner, ordinary
rear-yard depth (building type/lot width). Made-up corner lots C2/C3 (both the old and the new sets):
whole-lot coverage and rear yard beyond the corner. 40x100 interior rear-yard depth (readings differ).
40x200 through-lot rear yard (ZR 23-343 not captured). Special-density membership of the real lot
(boundary definitions of the Manhattan Core and Special Downtown Brooklyn District not captured).
Operative lot-area figure (PLUTO 10,075 vs outline ~10,388, unreconciled by the captures).

README "law text not captured" rewritten: ZR 12-10 (lot types, special density), ZR 23-342, ZR 23-363
now captured; still uncaptured and named: ZR 23-343, ZR 23-434, the ZR 12-10 front/rear/side lot-line
and lot-width definitions, the Manhattan Core / Special Downtown Brooklyn District boundary
definitions, the R6-R12 base plane, and the step-P2 commercial-overlay sections.

## 6. Support code (test support only; imports nothing from the rule/scenario engine)

`lib.py` (253 lines): added the fifth case to `CASE_IDS` and `REQUIRED_BASE_IDS`. `check.py` (475):
`NOT_CAPTURED_SECTIONS` -> ("23-343","23-434"); added `STEP_P1_READINGS` (digests), `step_p1_reading_errors`,
`both_readings_errors`, `readings_differ_errors`, wired into `validate_case`. `test_*.py` (414): 5-case
assertion, `NOT_KNOWN` extended, added S1 digest tests and S2 readings-differ / both-readings tests.
`render.py` unchanged (data-driven). All four files < 600 lines.

## 7. Checks (each exit code captured directly with `echo $?`)

| check | command | exit | result |
|---|---|---|---|
| a | `python -m ruff check .` (services/api) | 0 | All checks passed |
| b | `python -m pytest -q -p no:cacheprovider tests/rules/reference_cases` | 0 | 37 passed |
| c | renderer `--check` (pages byte-identical to data) | 0 | reference-case check PASSED |
| d1 | `python3 tools/modularity_check.py --check` (repo root) | 0 | 715 files, 0 failures, 29 pre-existing warnings (none in my files) |
| d2 | `python3 scripts/lanes/check_lane_paths.py --coverage` | 0 | 8855 files, each owned by one lane |
| e | two mutation proofs in a temp copy outside the repo | 0 | both pass |

Mutation proof details (temp copy under the session scratchpad, repo files untouched):
1. changed operand 150->151 in `corner-150x100-coverage` lot-area step -> `recompute_row_errors` fails
   naming `step-p1-worked/corner-150x100-coverage` (recomputes 15100 vs recorded 15000).
2. gave `interior-40x100-rear-yard` (readings differ) a value -> `readings_differ_errors` fails naming
   `step-p1-worked/interior-40x100-rear-yard` ("a value needs both readings to agree").

The FULL `services/api` pytest was NOT run (the orchestrator runs it once at the wave's final candidate).

## 8. Scope

Changed only allowed paths: `docs/reference-cases/R6B/**` (README, 3 case JSONs updated + 1 new,
7 rendered pages, 2 new provenance files), `services/api/tests/rules/reference_cases/**` (lib, check,
test), and this report. No rule file, engine, capture, register, plan, screen, other test, or
dependency file changed. `git status --porcelain` clean after the single commit.
