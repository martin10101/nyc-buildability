# M5-T133 producer report

Producer: scenario-optimization-engineer (builder), isolated worktree
`/root/project/nyc-buildability/.claude/worktrees/agent-a43b13d52cb335264`, reset to the
claim-seam head `d8ad46a85b31923f5eee4553543b3f2e1a6eb22b`. No estimator was built and no
program code changed; the only code is the examples' own test helpers. Standing label kept:
this is a draft reading of the law and a guideline by an AI, not professionally reviewed and
not a legal or professional determination (ADR-007). Nothing is written "complies" or
"legally correct".

## A/B. The fit check written first, run on the examples AS THEY ARE (red proof)

The fit check is `services/api/tests/scenario/measurement_basis/measurement_basis_fit.py`
(new). On every floor it requires a stated outside outline, the components (the exterior wall
ring among them) adding up to exactly the outline by exact decimal arithmetic, consistency
between the per-floor statement and the schedule, and that the apartment rooms do not fill the
inside outline with other interior components on top. It was written BEFORE any repair and run
on the three examples as they stood at the reset head (floor data added only to state today's
figures). Output:

```
example-a-standard-residential: PASS (fits)
    floor typical: outline=2000 components=2000
example-b-allowances-conditions-shown: FAIL (1 problem(s))
    floor typical: NO stated outline
    - .../typical: the floor has no stated outside outline
example-c-mixed-use: FAIL (1 problem(s))
    floor typical-res: outline=1260 components=1743  <-- OVERFLOW by 483
    floor ground: NO stated outline
    - .../typical-res: the components on this floor add up to 1743 sq ft but the stated
      outside outline is 1260 sq ft (difference 483)
    - .../typical-res: the apartment rooms (1120 sq ft) already fill the inside outline
      (1120 sq ft = outline 1260 minus the exterior wall ring 140) while 483 sq ft of other
      interior components are listed on the same floor (the floor cannot hold them)
    - .../ground: the floor has no stated outside outline
```

This reproduces the reviewer's figures (1,743 vs 1,260, 483 over; B states no floor outline).

## Repaired examples: per floor the outline, the sum of components, the difference (zero)

Each example now states every floor's outside outline; on each floor the components (ring
among them) add up to it exactly. `fit_errors` is [] for all three.

| Example | Floor | Outline (sq ft) | Sum of components (sq ft) | Difference |
|---|---|---|---|---|
| A | typical (x4) | 2,000 | 2,000 | 0 |
| B | cellar | 2,000 | 2,000 | 0 |
| B | ground | 2,640 | 2,640 | 0 |
| B | typical (x4) | 2,640 | 2,640 | 0 |
| C | ground | 3,080 | 3,080 | 0 |
| C | typical-res (x4) | 2,552 | 2,552 | 0 |

## Old and new ratios (nothing replaced silently)

| Example | Residential zoning FA | HPD unit area | Old ratio | New ratio |
|---|---|---|---|---|
| A (unchanged) | 8,000 | 6,032 | 0.7540 | 0.7540 |
| B (rebuilt) | 12,001 | 7,780 | 0.6022 WITHDRAWN | 0.6483 |
| C (rebuilt, residential exclusive) | 10,428 | 7,120 | 0.6676 WITHDRAWN | 0.6828 |

The withdrawn 0.6022 and 0.6676 are named in each example's change log and in the record
(section 7). The three ratios differ because each depends on its own made-up layout; the
record states the examples establish no range and that 0.60-0.75, if adopted, is only a
chosen sensitivity range labelled unvalidated (never realistic/expected/validated), and no
sentence starts the estimate from the allowed or permitted floor area.

## C (C3). Example C and shared floor area

Example C marks every component exclusive to one use (residential or commercial) or shared.
It has one small shared component (a 120 sq ft utility room, portion `shared`). The ZR 23-20
attribution is carried as a reconciliation line and applied exactly as the captured sentence
words it: residential share = residential exclusive 10,428 / (total 12,848 - shared 120 =
base 12,728) = 0.8193; attributed to residential 98.32 sq ft, to commercial 21.68 sq ft. The
outcome is labelled CONDITIONAL: how a mixed building in a Commercial District combines its
floor areas (reviewer names ZR 35-31) is not captured yet (M4-T034), so the effect on the
residential figure is withheld and the ratio uses the residential exclusive area only.

## Each statement of law, with the capture it quotes (word for word)

All quotes verified present in the named capture by the coverage script (52/52 example
captured citations; 10/10 record law block-quotes; 8/8 digests; R6B table numbers): 0 misses.

- ZR 12-10 floor-area definition, dwelling floor space, exterior-face measurement, stairwell/
  elevator, accessory mechanical, cellar, parking, energy exclusion -> `zr-12-10-floor-area`
  (digest e14ecafc...).
- "Qualifying exterior wall thickness" (wall exclusion eligibility) ->
  `zr-12-10-qualifying-exterior-wall-thickness` (119324c8...).
- "mixed building" definition -> `zr-12-10-mixed-building` (6eb9a389...).
- Shared floor area attributed proportionately -> `zr-23-20` (0685a2e4...).
- ZR 23-23 conditional allowances -> `zr-23-23` (6dd17af0...).
- Amenity 5% base "the residential floor area of the building", circulation excluded,
  accessible to residents -> `zr-23-231` (81eb95e8...).
- Corridor 50%+50% -> `zr-23-232` (0a79cda6...); refuse 3 sq ft/DU -> `zr-23-233` (36b8c7da...).
- R6B base/building heights (30/45/55; qualifying 45/65) and the setback trigger -> `zr-23-432`
  (9fab7be8...); setback depth 10 ft wide / 15 ft narrow -> `zr-23-433` (4fecf4d2...).
- Dwelling-unit factor 680 -> `zr-23-52` (f48f1ddc...).
- HPD unit-area measurement -> HPD Design Guidelines 2026, UNIT AREA CALCULATION (guideline,
  not law; embedded verbatim, pdf sha256 309d1863...).

## What is written "not captured yet"

- The mixed-building floor-area combination rule the reviewer names as ZR 35-31 (captured by
  M4-T034; not read here): the effect of the shared attribution on the residential figure is
  withheld.
- The ZR 12-10 definitions of "fully electrified building" and "ultra low energy building"
  (captured by M4-T034; not read here): the energy exclusion's eligibility is withheld and no
  example takes it.

## Section 8 as two lists

- **8a Choices for the owner** (design assumptions / display): the apartment-area ratio (one
  figure or a low/high sensitivity range labelled unvalidated); the apartment size (700 sq ft,
  HPD basis); the floor heights (10 ft / 15 ft, editable); "not known" until a shape and
  floors exist, then "preliminary capacity estimate"; what the user must see and edit. Each
  carries: recommended by the owner's reviewer on 2026-10-07; NOT decided until the owner says
  so.
- **8b Questions of law** (settled by capture and reading, never by preference): THREE items -
  the order of the amenity 5% calculation; how a mixed building combines residential +
  commercial floor areas (ZR 35-31 not captured yet); the eligibility of the energy and wall
  exclusions. (Round 2: the fourth item, "the dwelling-unit factor and where the current text
  sits", was REMOVED - it is not a question of law and it repeated a misreading, since
  corrected in backlog DB-178 point (g), that the reviewer's ZR 23-22 link differed from the
  repository; no difference exists, and section 5 already states the factor from capture
  `zr-23-52`.) Former points 5, 6, 7 moved here.
- **8c** unequal floors (R6B 45 ft base / 55 ft building; setback above base per ZR 23-432/
  23-433; the program does not work out the setback yet). **8d** what the estimator would need.

## Checks (direct exit codes), from `services/api` with the lanes venv, PYTHONDONTWRITEBYTECODE=1

- (a) `python -m ruff check .` -> `All checks passed!` exit **0**.
- (b) `python -m pytest -q -p no:cacheprovider tests/scenario/measurement_basis` -> `35 passed`
  exit **0**. (Full api suite NOT run - orchestrator runs it on the wave candidate.)
- (c) three mutations on copies OUTSIDE the repo (one dimension changed by a foot; one floor's
  outline removed; rooms filling the inside outline with a corridor on top): each FAILS the fit
  check, exit **0**.
- (d) coverage script OUTSIDE the repo: every quoted provision found in the capture it names -
  52 example captured citations, 10 record law block-quotes, 8 digests, R6B table numbers;
  **0 misses**, exit **0**.
- (e) `git status --porcelain` and `git diff --name-status d8ad46a8..HEAD`: only
  `docs/measurement-basis/**`, `services/api/tests/scenario/measurement_basis/**` and this
  report, exit **0**.

## Assumptions / limitations

- Floor types carry a `count` (identical floors represented once); the fit check proves each
  floor type and ties it to the schedule, so each identical floor is checked. Stated.
- The made-up layouts draw equal floorplates for simplicity; section 8c and each example's
  assumptions note say a real R6B building would set back above the 45 ft base height.
- Example B states 13 dwelling units by design (for the refuse cap arithmetic); this is a
  design input of the made-up layout, not an estimated capacity. No apartment count is computed
  anywhere.
- The wall-thickness and energy quotes in the record are abridged with "..."; each fragment is
  verbatim (confirmed by the coverage script); the HPD quote is a guideline, not law.
