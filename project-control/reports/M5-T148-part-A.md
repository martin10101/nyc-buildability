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
