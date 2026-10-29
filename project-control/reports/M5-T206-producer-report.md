# M5-T206 (builder) producer report — website exact-section law links (unmounted parity build)

Task: the web-side exact-section law-link primitive that mirrors the report's own
`services/api/app/drawings/report/law_links.py` (`section_url`/`_section_index`) and
`sources.py` (`zr_section_page_number`), with a Python-written parity golden both surfaces
read. Directives: D-094 R027 (every law link resolves to its exact current section, never the
host homepage; a citation with no snapshot shows plain text) and R246 (website and PDF agree,
same source bases). Unmounted by design — M5-T174 mounts it in the Results flow.

Worktree: `/root/project/nyc-buildability/.claude/worktrees/agent-aac39de2ef36bc49c`
Reset to claim head `2ceb416a` (clean tree; non-destructive `checkout -B` because
`reset --hard` was blocked by the local-destruction guard and there was nothing to discard).

## What now resolves (the answer)

The website previously had only the URL *validator* (`source-links.ts`
`officialZoningTextUrl`) and linked a citation only when the data carried a per-citation URL.
It now also has the *resolver* the report uses:

- `apps/web/src/lib/architect/zr-section-urls.ts`
  - `ZR_SECTION_URLS` — committed section-page -> exact-official-URL map (200 entries at this
    head), derived from `law_links._section_index()` and frozen by the parity golden. Every
    value is re-validated at module load through `officialZoningTextUrl` (defence in depth), so
    a bad or host-only URL is dropped (its page resolves to null), never the homepage.
  - `zrSectionPageNumber(cited)` — TS port of `sources.zr_section_page_number`: strip a leading
    "ZR" (case-insensitive, trimmed), then the start-anchored `/^\d{1,3}-\d{1,4}/` (matching
    Python `re.match`), sub-paragraph dropped; no number -> `""`.
  - `sectionUrl(cited)` — `ZR_SECTION_URLS[zrSectionPageNumber(cited)] ?? null`.
- `apps/web/src/components/architect/ZrSectionLinks.tsx` — presentational: each resolvable
  label is an anchor to its exact section (`target="_blank"`, `rel="noopener noreferrer"`,
  visible text = the label verbatim incl. sub-paragraph); each unresolvable label is plain
  text; a blank/missing citation renders nothing; an empty/all-blank list renders nothing.
- `services/api/tests/drawings/report/test_web_parity_links.py` — writes the golden FROM the
  server code under `UPDATE_GOLDEN=1` and asserts the committed golden equals the freshly
  computed `section_index` + `zr_section_page_number`/`section_url` case tables (fails closed on
  drift). Mirrors the accepted `test_web_parity_area_zones.py` pattern.
- `apps/web/src/test-support/report-parity-law-links.json` — the golden (server-written).
- Two web tests read the SAME golden and assert `ZR_SECTION_URLS === golden.section_index` and
  every case; editing one golden number reddens both surfaces.

Note vs. the planner's spec (CORRECTED in round 2 — see the Round 2 section): the capture set did
**not** grow. `law_links._section_index()` returns **200** at BOTH b561450e and this head
`2ceb416a` (the `_zr_snapshots/v1` tree is byte-identical between them); the packet's "181" was a
planner miscount. The golden is server-written and reflects the real 200-entry index; the parity
test fails closed if the capture set ever does change.

All pinned cases match the server at this head (`ZR 23-52(b)`->`23-52`, `12-10`->`12-10`,
`ZR 23-344(c)(3)`->`23-344`, `ZR 23-362`->`23-362`; null/123/""/"Appendix A"/LAW_SITE_TITLE
->`""`; `ZR 11-25` parses to page `11-25` but is ABSENT from the index, so `section_url` is
null -> plain text, matching the PDF; bare host -> null).

## Checks (all run with the lanes venv; heavy runs under the heavy-run.lock)

- `npm run lint` (eslint .) — PASS, exit 0; 0 errors (2 pre-existing warnings in files I do not
  own: lot-site-setup.test.tsx, study-vocabulary.test.ts).
- `npm run typecheck` (tsc --noEmit) — PASS, exit 0.
- `npx vitest run src/lib/architect/__tests__/zr-section-urls.test.ts
  src/components/architect/__tests__/zr-section-links.test.tsx` — PASS, exit 0; 2 files, 22
  tests.
- `python -m ruff check .` (services/api) — PASS, exit 0 ("All checks passed!").
- `pytest -q tests/drawings/report/test_web_parity_links.py` — PASS, exit 0; 2 passed.
- `tools/modularity_check.py --check` — PASS, exit 0 (warnings only, none on my new files).
- `tools/research_record_check.py --check` — PASS, exit 0 (no record pins my files; NB-04
  code_current=False is pre-existing and reported, not failed).
- `scripts/lanes/check_lane_paths.py --coverage` — PASS, exit 0 (11060 files, each one lane).

## Mutation proofs (reverted after each)

1. Golden parity (the brief's disconfirming check). Hand-edited one golden URL
   (`.../chapter-1/11-23` -> `/11-99`): Python parity test FAILED (exit 1, 1 failed) AND the web
   resolver test FAILED (exit 1, `ZR_SECTION_URLS.toEqual(golden.section_index)` at
   zr-section-urls.test.ts:64). Restored by `UPDATE_GOLDEN=1` regeneration; both green again.
2. Resolver function. Replaced the leading-ZR strip with `const bare = text;`: web resolver test
   FAILED (exit 1, 8 of 18 failed — every ZR-prefixed case). Restored from backup; green.
3. Component. Dropped `target="_blank"` from the anchor: component test FAILED (exit 1, 1 of 4
   failed — the `toHaveAttribute("target","_blank")` assertion). Restored from backup; green.

## Human-style walkthrough (unmounted → component render, since there is no live mount)

Rendered `ZrSectionLinks` with the real page-8 citations
`["ZR 23-362","ZR 12-10","ZR 23-52(b)","ZR 11-25","","Appendix A"]` via a transient scratch
test (deleted, never staged). Produced HTML: the first three are anchors to
`.../article-ii/chapter-3/23-362`, `.../article-i/chapter-2/12-10`,
`.../article-ii/chapter-3/23-52` (each `target="_blank" rel="noopener noreferrer"`, label
verbatim); `ZR 11-25` and `Appendix A` are `<span>` plain text; the blank entry rendered
nothing. This matches the PDF's page-8 link/plain-text split.

## Scope / provenance

- Diff is exactly the 7 allowed_paths (6 code/test/golden + this report). No `services/api/app`
  or `packages/contracts` edit; `source-links.ts`, the Results-flow components, the e2e specs,
  `report-parity-area-zones.json`, and the `_zr_snapshots` set are byte-unchanged. Component is
  NOT mounted anywhere. No internal/development language in any web-authored string.
- D-093: no fact, rule, calculation or verification label changed — the golden is parity to the
  report's own code; correctness is the reference cases + snapshot captures. No evidence record
  pins `law_links.py`/`source-links.ts`/`zr-section-*` (confirmed: no hits under
  docs/research/evidence-records for these). No `*.rule.json` touched -> no review_register or
  zoning-rule-review change.

## Not checked / limits

- No report print (no report page changed — correct for this unmounted part).
- The full api pytest suite and the full web suite run in CI, not here (thin-client policy);
  I ran ruff + the touched test file + the two touched web suites locally.
- Correctness of the underlying captures (which section pages exist, their URLs) is owned by the
  snapshots/reference cases, not this part; this part only reproduces the server's resolution.

---

# Round 2 (builder) — close the visual REQUIRED finding + the two advisories

Round 2 rebases the round-1 work (cherry-picked onto claim head `2ceb416a`) and adds one change set
that closes the G3 visual REQUIRED finding and the code/qa advisories. The scope is still exactly the
7 allowed_paths; no new file, no forbidden path touched.

Continuity note: a first round-2 builder produced this change set and confirmed it visually but was
stopped by a usage limit before committing. The committing builder (fresh) re-applied that saved work,
then independently re-ran every check and every mutation proof and re-rendered in chromium before
committing. Every exit code, count and mutation result below is from that fresh re-verification, not
carried over.

## a. REQUIRED (G3 visual) — grouped citations now read like the PDF

Before, `ZrSectionLinks` mapped each label straight to an `<a>`/`<span>` with nothing between them,
so the real page-8 group rendered as one run-together, mutually-touching-underline string
(`ZR 23-344(b)ZR 23-344(c)(3)…`). Now the component interleaves the PDF's `"; "` separator between
rendered items (a `<span data-testid="zr-section-separator" aria-hidden="true">; </span>`), with
**nothing before the first item or after the last**. Blanks are filtered out *before* the map, so a
skipped blank never leaves a double separator (`"; ;"`). The page-8 group now reads:

> ZR 23-344(b); ZR 23-344(c)(3); ZR 23-52(a); ZR 23-52(a)(2); ZR 23-433; ZR 23-335; ZR 34-232

Every item (links and plain text alike) is separated; adjacent links no longer run together. New test
(`zr-section-links.test.tsx`): two adjacent resolvable links render with a visible `"; "` separator
between them, exactly two separators for three visible items with a blank in the middle (no `"; ;"`),
and no separator at the start or end. The existing order test's `textContent` assertion was updated to
expect the `"; "` join.

## b. Start-anchoring now guarded (code/qa advisory)

Added a buried-number case to BOTH surfaces: `_PAGE_CASES` in `test_web_parity_links.py` carries
`"see 23-52" -> ""` (so the server-written golden pins it; regenerated with `UPDATE_GOLDEN=1`), and the
web `zr-section-urls.test.ts` adds three buried-number cases (`"see 23-52"`, `"Appendix 23-52"`,
`"note 12-10 applies"` -> `""`). The golden's `section_index` size is unchanged at 200 (diff is only
the new `page_number_cases` entry), confirming no capture change. Mutation proof below.

## c. Round-1 narrative correction (the capture set did NOT grow)

The round-1 commit message / report said the capture set "grew" from the planner's 181 to 200. That is
**wrong**: `law_links._section_index()` returns **200 at both b561450e and 2ceb416a** — the
`_zr_snapshots/v1` tree is byte-identical between the two heads and `law_links.py`/`sources.py`/
`snapshots.py` are unchanged between them, so nothing grew. The packet's "181" was a planner miscount.
The deliverable is unaffected (the golden is server-written and reflects the real 200-entry index). The
round-1 "Note vs. the planner's spec" paragraph above has been corrected in place; no future reader
should chase a non-existent capture change.

## d. Advisory (a11y) — "opens in a new tab" cue

Each resolvable anchor now carries `aria-label={`${label} (opens in a new tab)`}`. The **visible** label
is unchanged (still the verbatim citation, `textContent === label`); only the accessible name gains the
new-tab cue for screen-reader/keyboard users (WCAG 3.2.5). New test asserts the aria-label and the
unchanged visible text.

## Checks (round 2; lanes venv; heavy runs under heavy-run.lock)

- `npm run lint` — PASS, exit 0 (0 errors; the same 2 pre-existing warnings in files I do not own:
  lot-site-setup.test.tsx, study-vocabulary.test.ts).
- `npm run typecheck` (tsc --noEmit) — PASS, exit 0.
- `npx vitest run` (the two touched suites) — PASS, exit 0; **2 files, 27 tests** (22 round-1 + 5 new:
  the a11y cue test, the separator test, and three buried-number `it.each` cases).
- `python -m ruff check .` (services/api) — PASS, exit 0 ("All checks passed!").
- `UPDATE_GOLDEN=1 pytest -q test_web_parity_links.py` (under lock) — PASS, exit 0; regenerated golden
  adds only `{"cited":"see 23-52","page":""}`; section_index unchanged at 200.
- `pytest -q test_web_parity_links.py` (verification run, under lock) — PASS, exit 0; 2 passed.
- `tools/modularity_check.py --check` — PASS, exit 0 (warnings only, none on my files).
- `tools/research_record_check.py --check` — PASS, exit 0 (NB-04 code_current=False is a pre-existing
  NOTE, reported not failed; no record pins my files).
- `scripts/lanes/check_lane_paths.py --coverage` — PASS, exit 0 (11060 files, each one lane).

## Mutation proofs (reverted after each; all suites green again afterwards)

1. **Anchoring (item b) — RED on BOTH surfaces.** (a) *Web:* dropped the `^` from the TS
   `SECTION_PAGE_RE` (`/^\d{1,3}-\d{1,4}/` -> `/\d{1,3}-\d{1,4}/`): web suite RED — **4 failed** = the
   three buried-number inline cases (e.g. `"see 23-52"` now parses the embedded `23-52`) + the
   server-written golden `page_number_cases` loop (`expected '23-52' to be ''`). Restored -> green.
   (b) *Python parity:* the server's anchoring is the `re.match` in `sources.zr_section_page_number`
   (unanchored pattern `\d{1,3}-\d{1,4}`). `services/api/app/` is a forbidden path, so rather than
   edit `sources.py` I dropped the anchor at RUNTIME via a throwaway pytest plugin (scratch, not
   committed; `pytest_configure` swaps in a `re.search` version) and ran the REAL
   `test_web_parity_links.py`: `test_web_parity_law_links_golden_matches_server` went RED
   (`AssertionError: golden drifted ...`; computed `"see 23-52" -> "23-52"` != committed `""`),
   1 failed / 1 passed. `git status` confirmed `sources.py` byte-unchanged. This proves the golden
   fails closed on a server anchoring change; the committed golden pins `"see 23-52" -> ""`.
2. **Separator (item a).** Disabled the interleaved separator (`index > 0` -> `false`): the component
   suite went RED on exactly the two separator-dependent tests — the new separator test
   (`toHaveLength(2)`) and the order test (`expected 'ZR 11-23(a)ZR 999-99' to be
   'ZR 11-23(a); ZR 999-99'`, i.e. the exact run-together defect). Restored -> green.
3. **a11y cue (item d).** Removed the `aria-label`: the component suite went RED on exactly the a11y
   test. Restored -> green.

## Chromium render (item a) — renderToStaticMarkup, headless chromium, no server/port, under the lock

Bundled the REAL component with esbuild (CJS, platform node, `@/` resolved to the worktree `src`),
`renderToStaticMarkup` of three citation sets (the real page-8 group, a mixed link/plain/blank set, and
a single citation), loaded the HTML in headless chromium (`playwright-core` 1.61.1, chromium-1228) under
the heavy-run lock, and read the on-screen text + screenshotted. The on-screen text of the page-8 group
is `ZR 23-344(b); ZR 23-344(c)(3); ZR 23-52(a); ZR 23-52(a)(2); ZR 23-433; ZR 23-335; ZR 34-232` with
6 visible `"; "` separators (7 links); the mixed set shows the three links, then `ZR 11-25` and
`Appendix A` as plain text, blank skipped, all separated by `"; "`. Each anchor's `aria-label` ends in
`(opens in a new tab)`. The underlines no longer touch; nothing reads as a single merged link. The
screenshot (`render.png`) was opened and inspected: in the page-8 row each blue underlined link is
separated by a plain `"; "`, so no two links share one underline. Scratch (not committed):
`/tmp/claude-0/M5-T206-builder-r2bz7k/` (entry.tsx, build.mjs, entry.cjs, out.html, shot.mjs,
render.png, deanchor_plugin.py).

## Round-2 limits / not checked

- `services/api/app/sources.py` was NOT edited (forbidden path). The server-side anchoring guard was
  still proven RED: the anchor was dropped at RUNTIME via a scratch pytest plugin and the real parity
  test went red (see mutation proof 1b), with `sources.py` verified byte-unchanged afterwards.
- Still unmounted (no report page / Results-flow change) — M5-T174 mounts it; no report print needed.
- Where M5-T174 mounts the component and which results field feeds it stays UNKNOWN (per the brief).
