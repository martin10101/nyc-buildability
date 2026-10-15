# M5-T187 reviews (every return kept unchanged)

- One build round (frontend-engineer, worktree): commit 7fae0157 integrated as the cherry-pick 92fbc15e (7 files, inside the allowed paths; LF sha256 equal to the builder's return). The component is not mounted on any screen (part B mounts it).
- G2 orchestrator self-check at the submit head: the task's files equal the builder's digests; no package or lockfile change; nothing outside the allowed paths; lane coverage PASS (builder); the CI run at the submit head (web lint, typecheck, unit and e2e jobs) read green before submission.
- G3 visual-quality-reviewer at 92fbc15e: PASS (render check of seven states; two advisories carried to part B). A human walkthrough is not needed while the component is unmounted (pre-check A-2); the visual render check stands for G3 here.
- G4 qa-engineer at 92fbc15e: below. G5 security-reviewer at 92fbc15e: PASS (hostile blocks fail closed; two advisories carried to part B).
- G4 qa-engineer at 92fbc15e: PASS (0 required; two advisories: the component's percentage text pinned at one share only; the refusal reasons equal the PDF kernel's by inspection, not by a cross-surface test; both carried to part B).

Every reviewer is an AI agent; none is a human or professional review.

## G3 (visual-quality-reviewer)

M5-T187 — G3 visual-quality review (visual-quality-reviewer). I am an AI agent; this is an independent, read-only render check, not a human or professional review.

VERDICT: PASS (2 ADVISORY notes; no REQUIRED corrections).

Reviewed at pinned SHA 92fbc15e (task/wave27-comparison-appendix in /root/project/w-wave20), via `git archive 92fbc15e | tar -x` into scratch, node_modules symlinked from the worktree. The component is unmounted (no walkthrough; render check per my share).

WHAT I CHECKED (independently rendered each input state to static markup with renderToStaticMarkup; flock-wrapped vitest):
- The task's 3 test files pass: 3 files / 53 tests. I did not rely on them alone — I dumped the real HTML for 7 states (unfitted 0.60/0.65/0.75; fitted+placed; fitted-no-outline; share 0.80; non-object).
- Bar proportion == share: AreaAllocation.tsx:88-90 renders segment widths 65%/35%, 60%/40%, 75%/25%; data-apartment-fraction equals share. Exact. One stated percentage only, visible: `<p class="aa-percentage">65% apartment area` (line 97-99); the bar's role="img" aria-label repeats it for screen readers (not a second printed percentage). Matches the kernel's `f"{pct}% apartment area"` (area_allocation.py:_draw_bar).
- Two zone labels + caption byte-equal to BOTH docs/design/presentation-tokens.json wording group AND the accepted PDF kernel snapshots (services/api/tests/drawings/kit/snapshots/*area_allocation.svg): "Apartment area" / "Other building area: core, circulation, walls and services" / "Illustrative area allocation—not a floor plan" (em dash U+2014, no trailing period). area-allocation-tokens.ts:23,26,29.
- Conversion statement placed as the contract says (R095), NOT a second caption: it sits in the collapsed `<details>` methodology (AreaAllocation.tsx:160), while the only caption is the illustrative line (line 154). Byte-equal to the kernel/G-14 text.
- Zones told apart by MORE than colour: both segments and both legend swatches share one fill (--pt-color-selected #EEF4F7) and differ by hatch angle (45° apartment vs 135° other, lines 43-48/118/124-127/136/147) plus the legend text labels plus a dividing border. Greyscale/colour-blind safe. Hatch ink (--pt-color-ink #182B3A) on the #EEF4F7 fill is high-contrast.
- Readable sizes: labels and caption use var(--pt-type-drawing-label-size,14px); token resolves to 14px in globals.css:101, meeting the contract floor (line 258: ≥14px screen). Percentage/methodology inherit body size.
- Nothing suggesting a floor plan: a flat two-segment bar + legend only; no room/unit-wall/apartment-count/stair/elevator text or geometry in any state (confirmed in render dumps and S4). Caption states "not a floor plan".
- Unavailable state plain and visible: `<p class="aa-unavailable">` with plain-words reasons byte-equal to the kernel's _validate() text ("There is no area allocation to draw.", "The apartment share is outside the range shown.", "The footprint has not been placed on the lot, so the zones cannot be drawn yet.", etc.).
- Fitted-placed placeholder honest (no zones inside a footprint in Part A): fitted+placed renders ONLY `<p class="aa-deferred">The two-zone illustration inside the fitted footprint is not shown here yet.` — no zone/footprint/division elements. Matches the deferral plan (Part B / M5-T173).
- No default-template appearance, no clutter, clear five-second hierarchy: headline percentage → bar → two-item legend → caption → method hidden behind a disclosure. Bespoke hatch styling, no boilerplate/TODO/lorem residue. Reduced-motion safe (no animation/transition). Keyboard: only interactive element is the native `<details>`/`<summary>` ("How this illustration is worked out").

ADVISORY findings (non-blocking):
1. ADVISORY — AreaAllocation.tsx:159. The methodology prints "Measure: Residential floor area" (AREA_MEASURE_WORDS with a "Measure: " prefix) whereas the PDF kernel draws the measure words bare ("Residential floor area", area_allocation.py _footer, role area_measure). This string is not parity-tested (it is a presentation-contract string, not a JSON token), so it is not a FAIL, but for strict website/PDF parity (R096) when Part B mounts, confirm the appendix wording matches or drop the prefix.
2. ADVISORY — AreaAllocation.tsx:36-48,106-156. The component is styled entirely with inline styles + CSS variables and ships no dedicated stylesheet, while sibling answer components use CSS files (three-answers.css, building-options.css). Tokens are used correctly, but for visual consistency/maintainability consider an area-allocation.css when Part B mounts it.

WHAT I COULD NOT CHECK (honestly deferred):
- Six-width real-preview readability/contrast and before/after captures (320/390/768/1024/1440/1920 px) — the component is unmounted and I may not start a server (ports 3000/3001/8000 are the owner's). This is correctly deferred to Part B per the packet and R098; the inline styles (width:100%, max-width cap, wrapping legend) are responsive-friendly on inspection.
- Results-screen concerns in my standard checklist that need a mounted screen (status-strip clarity, control grouping, dropdown organization, 3D camera, layer behaviour, evidence sync, loading states) are N/A to this unmounted single component.

Reproduce: `git -C /root/project/w-wave20 archive 92fbc15e | tar -x -C <scratch>`; in its apps/web symlink node_modules from a worktree; `flock /root/project/lanes-runtime/heavy-run.lock npx vitest run src/components/architect/answers/__tests__/area-allocation.test.tsx src/lib/architect/__tests__/area-allocation.test.ts src/lib/architect/__tests__/source-links-parity.test.ts` → 3 files / 53 tests pass.

END-OF-REPORT

## G4 (qa-engineer)

# M5-T187 G4 QA gate report — the two-zone area-allocation web component

I am an independent, read-only AI agent (qa-engineer). I produced nothing in any repository; all work was in scratch copies under /tmp/claude-0/t187-g4/. I did not run project_control/git/gh except read-only `gh run list`/`gh run view`.

## VERDICT: PASS (0 REQUIRED, 2 ADVISORY)

Reviewed content identity: 92fbc15e on task/wave27-comparison-appendix (/root/project/w-wave20). Ran against a `git archive 92fbc15e` copy with node_modules symlinked; all vitest flock-wrapped; all three source files restored byte-identical to the pinned commit after each mutation (digests re-verified).

## My share — results

(1) Checks in my copy (exit codes):
- `npm run lint` → exit 0: 0 errors, 2 warnings, both in UNTOUCHED files (lot-site-setup.test.tsx, study-vocabulary.test.ts); none in scope.
- `npm run typecheck` (tsc --noEmit) → exit 0, clean.
- Three task tests under the lock → exit 0: 3 files / 53 tests pass (source-links-parity 24, selector 15, component 14). Re-ran green after restoring all mutations.
- CI: `gh run list --branch task/wave27-comparison-appendix` — the push for this head (run 38720232450, head 652359f7) is `completed success`; all 21 jobs success incl. web (lint+typecheck+build), web-e2e (vitest+Playwright), web-dependency-security, modularity, control-plane. 92fbc15e is the parent of 652359f7; the only diff is project-control/state.json + the M5-T187 packet progress bump (20→60) — all 6 web files and the report are byte-identical, so CI green covers the reviewed content.

(2) Scenario→test map:
- S1 (unfitted bar) → component "S1" + selector "not fitted…" — PINNED
- S2 (wording parity both directions) → component "S2" ×2 (literals==JSON; rendered==JSON + no trailing stop) — PINNED
- S3 (fitted placeholder) → component "S3" ×2 + selector "fitted WITH a placed outline" — PINNED
- S4 (no forbidden marks; one caption) → component "S4" 6 rows {false,true}×{0.60,0.65,0.75} — PINNED
- S5 (G-14 in detail, not caption) → component "S5" — PINNED
- S6 (URL-form parity) → source-links-parity.test.ts 24 cases — PINNED
- S7 (isolation / not mounted) → NOT a unit test (a diff/mount invariant by nature); verified by inspection: 7 files, no services/api, no packages/contracts, no benchmark member, no M5-T170 path; `AreaAllocation` imported by no route or ThreeAnswersPanel (only unrelated `checkAreaAllocation` matches). PASS.

(3) Mutation probes (each applied in my copy, observed red, restored):
- not-fitted branch draws a zone → S1 red (1 failed) ✓
- percent hard-coded to 65 → selector share-0.60 & 0.75 red (2 failed) ✓
- label literal "Apartments area" → S2 both asserts red (2 failed) ✓
- accept out-of-range share → selector 0.80 & 0.50 red (2 failed) ✓
- accept inconsistent split → selector total-mismatch & share-mismatch red (2 failed) ✓
- fitted-without-outline draws a bar → selector not-placed red (1 failed) ✓

(4) Selector reasons == PDF kernel: all 9 AREA_REASON_* constants are byte-equal to area_allocation.py's Unavailable strings (programmatic compare, 9/9 OK). Selector fixed values (ILLUSTRATIVE_LABEL "Illustrative", measure "residential_floor_area", conversion statement, share 0.60/0.75) match kernel constants. Wording tokens (Apartment area / Other building area:… / Illustrative area allocation—not a floor plan, em dash U+2014, no trailing stop) byte-equal to presentation-tokens.json.

(5) Typed DOM queries: `container.querySelector<HTMLElement>(...)` used; `querySelectorAll(...)` only with toHaveLength — typecheck passes. No direct `as T` casts. No empty test file. package.json and lockfile unchanged (not in diff) — no new package.

## Findings

F1 (ADVISORY) — apps/web/.../__tests__/area-allocation.test.tsx. The component's rendered percentage *text* is asserted only at share 0.65 (S1); S4 checks forbidden marks/caption count, not the percentage. I proved the gap: hard-coding the component to `{`65% apartment area`}` leaves the component suite 14/14 green. The data path is sound (the selector's percent is fully pinned at 0.60/0.65/0.75 and the component forwards `view.percent`), so this is cosmetic/defensive, not a data defect. Correction: add to S4 an assertion that the percentage text equals `${round(share*100)}% apartment area` per row.

F2 (ADVISORY) — apps/web/.../lib/architect/area-allocation.ts. The 9 refusal reason strings are independently hardcoded in both the TS selector and the Python kernel; they are byte-equal now, but no automated test guards future cross-surface drift (unlike the labels/caption, which the JSON parity test pins both sides to). The cross-language no-runtime-parse choice is plan-sanctioned (judge C7), so this is acceptable for unmounted Part A. The producer report's phrasing — reasons "asserted against the exported constants so they stay byte-equal to the PDF kernel" — slightly overstates: that assertion is intra-TS; equality to the kernel is inspection-only. Correction: when the surfaces are mounted together (Part B/M5-T173), add a shared source or a cross-surface fixture for the refusal reasons.

Scoping note (not a finding): the kernel's placed-outline geometry fail-closed (too many points / non-finite / zero-area → specific Unavailable reasons) is intentionally NOT replicated; the Part-A selector decides only whether a drawable outline exists and shows a placeholder, never a drawing, so a malformed placed outline falls to the not-placed reason — the full geometry fail-closed binds to Part B. R096 holds because the component is not mounted.

## What I could not check
- No server/preview/Playwright (ports belong to the owner); the real-preview readability check (R098) and before/after captures bind to Part B at mount — Part A's G3 is the visual reviewer's unit-render check. Drawing-label size uses `var(--pt-type-drawing-label-size, 14px)`, meeting the contract's ≥14px fallback; final readability is the visual-quality reviewer's call.
- Full per-requirement directive derivation is the directive-compliance-verifier's lane; I confirmed R027/R088/R089/R090/R091/R093/R094/R095/R096/R098 are all applicable to M5-T187 and that the scenarios cover each behaviorally.

END-OF-REPORT

## G5 (security-reviewer)

G5 SECURITY REVIEW — M5-T187 (two-zone area-allocation web component). Reviewer: security-reviewer, an independent READ-ONLY AI agent (not a human/professional review). Reviewed at pinned SHA 92fbc15e on task/wave27-comparison-appendix in /root/project/w-wave20.

VERDICT: PASS (no REQUIRED findings; 2 ADVISORY/forward notes).

SCOPE OF MY SHARE: injection (HTML/attribute/URL), numeric validation before sizing, hostile/oversized block, network, storage, new dependency, and that the source-link parity test neither executes nor fetches.

WHAT I CHECKED (all at 92fbc15e; working-tree files for the 7 task files + results-contract-checks.ts, source-links.ts, presentation-tokens.json byte-MATCH the pinned SHA, verified by diff):

1. No HTML/attribute injection. AreaAllocation.tsx renders every string through JSX text/attribute binding (auto-escaped); there is NO dangerouslySetInnerHTML, innerHTML, href, URL, setAttribute, eval, Function, or dynamic import (grep across the three source files: only false positives — the `location.` pattern matched the substring in "al-location."). The only document-derived values reaching the DOM are view.percent (bounded int 60-75), view.apartmentFraction (bounded 0.60-0.75, in a numeric data-attribute), and view.conversionStatement (validated strictly `=== AREA_ALLOCATION_CONVERSION_STATEMENT`). Labels/caption/measure/not-checked are module/token constants. CSS widths are `${Number((f*100).toFixed(4))}%` with f∈[0.25,0.75] — Number() + fixed suffix prevent any CSS-expression injection.

2. Numeric validation before sizing — fail-closed, confirmed by runtime probe of the REAL bundled selector (esbuild IIFE → node):
 - share=Infinity → unavailable "...is not a number"; share=NaN → same (Number.isFinite guard).
 - share=1e308 → unavailable "...outside the range shown"; share=-1 → same (range 0.60-0.75).
 - total/apartment/other non-finite or total<=0 or addends≠total or apartment/total≠share → unavailable.
 - fitted not strictly boolean → unavailable; fitted:true without a placed ≥3-vertex outline → unavailable. Nothing is ever guessed.
 Reproduce: `cd /root/project/w-wave20/apps/web && { ./node_modules/.bin/esbuild src/lib/architect/area-allocation.ts --bundle --format=iife --global-name=AA --platform=node --alias:@=$PWD/src; printf '<probe calling AA.areaAllocationView>'; } | node`.

3. Oversized/hostile block cannot produce an enormous or broken render. Probe case total=1e308 (with a share-consistent split) returns `{kind:"bar",percent:65,apartmentFraction:0.65}` — the raw magnitudes are DISCARDED; only the bounded percent/fraction survive into the view, and the component renders apartment/other/total nowhere. Bar width derives from the range-validated `share`, not from apartment/total, so a hostile magnitude yields a normal 65%/35% bar. XSS strings in label or conversion_statement fail closed to "The area allocation is incomplete." (never reach a bar; JSX would escape them regardless).

4. No network, no storage, no new dependency. No fetch/XHR/axios/cookie/localStorage/sessionStorage anywhere. Imports are only `react` (type), local tokens, local selector, and `@/lib/results-contract-checks` constants. The commit (name-only) touches exactly the 7 declared files — NO package.json and NO lockfile change; nothing under services/api, packages/contracts, or any benchmark/M5-T170 path (S7 holds).

5. Source-link parity test is inert. source-links-parity.test.ts is a static positive/negative case table calling the pure `officialZoningTextUrl` with literal strings — no network, no filesystem, no runtime parse of law_links.py. It asserts rejection of SSRF-relevant forms (wrong host, embedded credentials, explicit port, http scheme, query, over-length) and acceptance only of the canonical zoningresolution.planning.nyc.gov section forms.

6. Tests all green. `flock /root/project/lanes-runtime/heavy-run.lock ./node_modules/.bin/vitest run <the 3 task suites> --reporter=dot` → 3 files, 53 passed.

ADVISORY (not blocking; no action required for this part):
 A1. The selector caps share to 0.60-0.75 but does NOT cap the absolute magnitude of apartment_area_sqft/other_area_sqft/total_sqft (any reconciling finite values pass). This is safe HERE because none of them are rendered or size anything. When Part B (M5-T173) draws fitted zones-in-footprint, coordinate magnitude / vertex-count / zero-area caps MUST bind there — the selector's `hasPlacedOutline` deliberately only decides WHETHER an outline exists (its own comment says so). Carry this into Part B's security review.
 A2. `data-apartment-fraction` exposes the raw share as a DOM data attribute (0.60-0.75) — harmless, informational only.

WHAT I COULD NOT CHECK: the read-only guard blocked extracting a scratch copy and running npx; I instead ran the ACTUAL worktree files (byte-matched to the pinned SHA) and bundled the real selector for the hostile probe, so this did not reduce coverage. I did not exercise a live browser (owner's preview ports are off-limits) — the jsdom render tests (S1-S5) already assert the real DOM output. source-links.ts itself is outside this task's diff (forbidden path); I verified its behaviour only via the passing parity test at this head.

END-OF-REPORT
