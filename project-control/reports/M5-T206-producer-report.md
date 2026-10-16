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

Note vs. the planner's spec: the capture set grew between b561450e (planner: 181 section pages)
and this head `2ceb416a` (**200 section pages**). The golden is server-written, so it reflects
200 at this head; the parity test fails closed if the capture set changes again.

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
