# M5-T148 - producers' report (assembled by the orchestrator from the part reports, each unchanged below)

Task: shared presentation (the presentation contract's step 2): one token source with generated CSS and Python and parity checks; pure presentation adapters. Built on one branch with tasks M5-T148, M5-T149 and M5-T150 (wave 20), reviewed at one head and merged as one pull request. Every builder was an AI agent in its own worktree; the orchestrator integrated each commit, read it, and sent back what was wrong (the packet's rulings V1 to V12 and its `scope_corrections` say what and why).

## Builders' run times (from the task notifications)

```
Wave 20 builders (run times from the task notifications' duration_ms; every builder an AI agent in its own worktree):
M5-T148 part A tokens (frontend-engineer): 18.0 min (1,077,741 ms) -> 11d69391 (integrated b6c92236)
M5-T148 part B adapters (frontend-engineer): 19.3 min (1,157,511 ms) -> 36887c5c (integrated a2cffc97); made no report file, its return kept as the part report
M5-T150 outline (geospatial-engineer): 46.0 min (2,761,819 ms) -> 7fd1982c (integrated d183c487); made no report file; its memory-note commit not integrated
M5-T149 part B (frontend-engineer): 28.0 min (1,678,703 ms) -> fbbeb252 (integrated 4f9ea1b1)
M5-T149 part C (frontend-engineer): 26.8 min (1,610,119 ms) -> 99a93361 (integrated 63e0daca); made no report file
M5-T149 part A (frontend-engineer): 46.7 min (2,799,505 ms) -> 9fb1aca4 (integrated 923f3905 without two agent-memory files)
M5-T149 part C, layout-test measures V10: 4.2 min (249,486 ms) -> 4312f1ca (integrated b4126d55)
CORRECTION ROUND (ruling V11):
M5-T150 server wording (rules-engineer): 13.7 min (822,396 ms) -> 0476d78c (integrated bcc5a2ac)
M5-T149 part B: 17.8 min (1,070,780 ms) -> 894f1f53 (integrated 873c87dc)
M5-T149 part A: 25.6 min (1,538,519 ms) -> fb14daba (integrated 553c09fe)
M5-T149 part C: 26.6 min (1,595,811 ms) -> 385295de (integrated c8551767)
orchestrator: gapKindLine -> propertyInfoTag (dec878c2)
M5-T149 part C assertion: 1.9 min (116,037 ms) -> adf3e551 (integrated d22ddd78)
M5-T149 part A V12 order: 5.4 min (322,303 ms) -> ece3f9ce (integrated da1fea97)
M5-T149 part C one-line inputs: 4.5 min (271,182 ms) -> 6ff29e62 (integrated 13c8bd16)
after one diagnostic run (deficit convergence):
M5-T149 part C phone height: 6.4 min (383,714 ms) -> 650596b1 (integrated ad786e43)
M5-T149 part A one-result conditions: 12.8 min (769,296 ms) -> e731cc7a (integrated d745b635)
```


---

## Part A report (unchanged)

# M5-T148 part A — the presentation tokens (producer report)

Author: an AI agent (frontend-engineer producer).
Worktree: `/root/project/nyc-buildability/.claude/worktrees/agent-ab4df313da6218dc9`.
Contract head reset to and built on: `42fc2ae11e6b90084972e7ca32816cc50b8a085a`.

## What this part does

One source of presentation tokens from the presentation contract's section 5
(`docs/design/ARCHITECT_PRESENTATION_CONTRACT.md`). The JSON is the only file
edited by hand; a Node generator renders the CSS block and the Python module and
checks their parity. No screen and no number change: a new `--pt-*` block is
added inside `:root`; every existing token stays; no component, adapter or
`styles.py` was touched.

## Files changed (6)

- `docs/design/presentation-tokens.json` — the one source.
- `apps/web/scripts/presentation-tokens.mjs` — generator (Node standard library
  only); `--check` exits non-zero when an output differs from a fresh render.
- `apps/web/scripts/tests/presentation-tokens.test.mjs` — S1 parity, S2 values,
  S3 contrast.
- `apps/web/src/app/globals.css` — one generated block inside `:root`, between
  BEGIN/END comments (45 `--pt-*` custom properties); all prior tokens kept.
- `services/api/app/drawings/kit/presentation_tokens.py` — generated module
  (`TOKENS` plus group aliases); every line <= 100 chars.
- `services/api/tests/drawings/test_presentation_tokens.py` — JSON<->module
  parity, section-5 values, font stack, status words.

## Token count by group (JSON source)

- spacing: 7 (4, 8, 12, 16, 24, 32, 48 px).
- palette colours: 9 (ink, supporting, action, page, surface, divider,
  selected, caution-ink, caution-surface).
- shape: control height 44 px, control radius 6 px, panel radius 8 px (3).
- font: 1 (family = the application stack from `layout.tsx`, ruling V4:
  `system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif`).
- type roles: 7 (property-title, headline-value, section-title, body, compact,
  source-note, drawing-label); each carries screen px, line height, weight,
  print pt; body adds print line height; drawing-label adds preferred print pt.
- status: 3 (settled = no marker; conditional and not-known carry a marker and a
  secondary colour pair; no Verified token, ruling V3).
- contrast pairs (test input only, not emitted): 15 (11 text, 2 control edge,
  2 divider).
- Generated CSS custom properties: 45.

Each type size sits inside the contract's screen/print range. Line heights that
the contract table does not state for a role are chosen defaults, recorded in the
JSON `meta.typeNotes` (source-note 1.4, drawing-label 1.2).

## S3 contrast ratios (computed by the Node test, WCAG 2.2)

Text needs >= 4.5:1; a control boundary needs >= 3:1; the quiet divider is
marked never a control edge (no minimum, ratio reported).

| Pair | Ratio | Role | Result |
|---|---|---|---|
| ink on page | 13.26 | text | PASS |
| ink on surface | 14.53 | text | PASS |
| ink on selected | 13.09 | text | PASS |
| supporting on page | 5.83 | text | PASS |
| supporting on surface | 6.39 | text | PASS |
| supporting on selected | 5.76 | text | PASS |
| action on page | 7.14 | text | PASS |
| action on surface | 7.83 | text | PASS |
| action on selected | 7.05 | text | PASS |
| caution ink on caution surface | 6.27 | text | PASS |
| caution ink on surface | 6.85 | text | PASS |
| action control edge on surface | 7.83 | control | PASS |
| action control edge on page | 7.14 | control | PASS |
| quiet divider on surface | 1.34 | divider | no min (never an edge) |
| quiet divider on page | 1.22 | divider | no min (never an edge) |

## S1 parity proof in a scratch copy outside the repository

Scratch tree: `.../scratchpad/s1proof` (session scratchpad, not the repo).
Baseline (in sync): Node test PASS (10/10), `--check` PASS, api test PASS (6/6).
After changing `color.ink` to `#000000` in the scratch JSON **without
regenerating**:

- `node --test` -> exit 1 (both S1 parity tests fail: CSS block and Python
  module no longer equal a fresh render; the S2 palette test also fails).
- `node presentation-tokens.mjs --check` -> exit 1 (globals.css and the Python
  module reported out of date).
- api `pytest` -> exit 1 (`test_module_mirrors_the_json_source` fails).

A changed JSON colour without regeneration fails both tests and the check.

## Checks (each with its direct exit code)

In `apps/web`:
- `node --test scripts/tests/*.test.mjs` -> exit 0 (50 pass, 0 fail; 10 are this
  task's).
- `node scripts/presentation-tokens.mjs --check` -> exit 0.
- `npm run lint` -> exit 0 (0 errors; 2 pre-existing warnings in files not
  touched here).
- `npm run typecheck` -> exit 0.

In `services/api`:
- `python -m ruff check .` -> exit 0.
- `python -m pytest -q -p no:cacheprovider tests/drawings/test_presentation_tokens.py tests/drawings`
  -> exit 0 (753 passed, 6 skipped; the 6 new tests pass).

From the root:
- `python3 tools/modularity_check.py --check` -> exit 0 (only pre-existing
  warnings on other files).
- `python3 scripts/lanes/check_lane_paths.py --coverage` -> exit 0 (9810 files,
  each owned by one lane).

## Assumptions and limitations

- Ruling V4 governs the font token: it equals the `layout.tsx` stack, not the
  reference `Arial, Helvetica, sans-serif`. The Node and api tests read
  `layout.tsx` (read only) and assert equality, so a future font change there is
  caught.
- The type sizes are single concrete values chosen inside the contract ranges;
  the review should confirm the chosen points.
- Contrast is computed arithmetically from the palette, not from rendered pixels;
  rendered-pixel and real-screen checks remain the browser walkthrough's job
  (part of M5-T149 and the orchestrator's browser run, not this part).
- No computation, label or screen was changed. Part B's adapters under
  `apps/web/src/lib/architect/` were not touched.


---

## Part B report (unchanged)

# M5-T148 part B - producer's report

The builder (frontend-engineer, an AI agent) made no report file in its commit; its return is kept here unchanged, saved by the orchestrator from the session transcript (`return-builder-w20-T148B.txt`).

```
I am an AI agent (frontend-engineer producer). M5-T148 PART B — presentation adapters — is built, all checks pass, one commit made. No STOP; no file outside my scope changed.

WORKTREE: /root/project/nyc-buildability/.claude/worktrees/agent-af7926118fdbbbbbe
COMMIT: 36887c5cf90d4392fe2e569cff02c8092bf78839  PARENT: 42fc2ae11e6b90084972e7ca32816cc50b8a085a (contract head). `git status --porcelain` empty.

FILES CHANGED (10; 880+/30-): the five adapters metric-format.ts, result-status.ts, result-identity.ts, presented-results.ts, presented-notices.ts under apps/web/src/lib/architect/, and their five tests under its __tests__/. The placeholders were replaced. Nothing else.

WHAT EACH ADAPTER GIVES ON THE BENCHMARK (recorded_215_16_northern_journey):
- metric-format: reads values for display — "20,150 sq ft", "0 sq ft" (0 is a value, never Not known), "1,234,567.89 sq ft"; null/undefined/non-finite → the not-known state, never a digit; an unknown unit → the bare number. The value is only read, never changed.
- result-status: the benchmark's 6 withheld states → "Not known" with the document reason and no numeric field; its 10 conditional states → "Conditional"; settled/absent → no marker. No code path to "Verified".
- presented-results: floor-area allowance values + the three withheld legal unit limits → allowance; the envelope heights + withheld lot coverage/rear yard/setback → envelope; building B → a SCHEDULED option, display "20,150 sq ft", status Conditional, note "Site fit not verified", never "achieved"; the capacity estimate → an estimate, the document's range "17.27 to 21.59" (ruling V9). A thin layer over the existing contract types.
- presented-notices: the two conditions repeated across the document (the lot-area-confirmed condition and the four-unchecked-conditions condition) are listed once as C1/C2; many results refer to them (floor-area values both, heights one, building B both); none lost (set-equal to an independent collection). capNotices(5 notices) → 3 shown + "2 more"; ≤3 → all shown, no count.
- result-identity: a known identity — lotBbl 4073340070, lotDisplay "Queens block 7334, lot 70", resultsId res-215-16-northern-journey, an 8-hex revision fingerprint (changes when the revision changes, so a stale export is caught); another lot → mismatch; a document with no scope (synthetic_all_answers_available) → unknown, never a guessed lot.

CHECKS (in apps/web unless noted; direct exit codes):
- `npx vitest run src/lib/architect` → EXIT 0; Test Files 24 passed (24), Tests 380 passed (380).
- `npm run lint` → EXIT 0 (2 warnings, both in pre-existing files I did not touch: lot-site-setup.test.tsx, study-vocabulary.test.ts; 0 from my files).
- `npm run typecheck` → EXIT 0.
- root `python3 tools/modularity_check.py --check` → EXIT 0 (warnings are all pre-existing services/api & tools files; none of my adapters flagged).
- root `python3 scripts/lanes/check_lane_paths.py --coverage` → EXIT 0, "LANE COVERAGE PASS: 9810 file(s), each owned by exactly one lane."

MUTATION PROOFS (in a scratch copy OUTSIDE the repo; reverted/deleted; repo untouched):
1. Zero turned into not-known: changed the guard `value == null` → `!value` in metric-format.ts. CAUGHT by metric-format.test.ts › "formats exactly 0 as '0 sq ft', never 'Not known'".
2. A withheld value given a number: changed the withheld branch display from the no-digit NOT_KNOWN_DISPLAY to `{ kind:"value", text:"999" }` in presented-results.ts. CAUGHT by presented-results.test.ts › "never gives a withheld value a digit, and only uses the four known kinds" (and two benchmark S6 tests).

ASSUMPTIONS / DECISIONS (please verify at the gate):
- ResultKind is "allowance" | "envelope" | "scheduled" | "estimate" — deliberately NO "achieved" member. Rulings V5/V8 ("nothing is called achieved"; a schedule whose site fit is not established is the scheduled area) override the §8 sketch's "achieved". Every building option (the building_alternatives AND, on legacy fixtures, the single building_option answer) is tagged "scheduled" with the note "Site fit not verified".
- A result's label is read from the document verbatim (the established three-answers pattern). Some legacy fixtures carry the canonical label "Achieved zoning floor area" on the single building_option answer's value; that is document text the adapter reads, not adapter wording. The "no achieved/verified" test asserts only adapter-controlled fields (resultKind, note, status, constants), never pass-through document labels.
- These adapters are pure libraries; no component consumes them yet (no component changed this task, per the brief and ruling V2). The draft-value hiding gate stays the component's / three-answers' responsibility; presented-results does not re-implement it.
- metric-format also maps a non-finite number (NaN/Infinity) to the not-known state (a defensive extension of the null/undefined rule; it never shows "NaN"). displayQuantity, quantityText, conditionList and twoDp are reused from three-answers/first-building-options unchanged.

NO SERVER STARTED; ports 3000/3001/8000 untouched.

REPORT FILE: per my session's no-report-file override I did NOT create project-control/reports/M5-T148-part-B.md, and the commit contains only the 10 code files (matching its message). Please save THIS return verbatim as that report at the submit seam.

REQUESTED STATUS: awaiting_gate (G0 already PASS at the contract head; this increment is ready for G2 self-check / G3 / G4).
END-OF-REPORT

```
