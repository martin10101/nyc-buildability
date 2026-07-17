<!--
PROVENANCE: This is the human-journey-reviewer's G3 return for M2-T001, saved VERBATIM by the
orchestrator from the agent-return channel (transport entity-decoding only, per the
report-preservation rule in .claude/rules/project-control.md). Reviewer agent id
adee1eb3cffdeb01e (a first attempt, agent a7048a42816c14868, died on a network error mid-review
and returned nothing). Review performed read-only against worktree .claude/worktrees/M2-T001
@ dd34c7b and the downloaded CI playwright-evidence artifact. Saved 2026-07-16 by the orchestrator.
-->
# G3 Independent Human-Journey Walkthrough Report — M2-T001

- **Task:** M2-T001 — Priority 4: first browser Property screen (real BBL lookup against accepted property-profile API v1.1)
- **Gate:** G3 (independent human-style walkthrough, UI human-journey pack)
- **Reviewer:** human-journey-reviewer (independent; did not produce the work; read-only)
- **Producer:** frontend-engineer
- **Code under review:** worktree `.claude/worktrees/M2-T001`, branch `task/M2-T001-property-screen` @ `dd34c7b`
- **Date:** 2026-07-16 (local) / 2026-07-17 UTC evidence
- **Verdict: PASS** — zero blocking defects; 5 non-blocking carry-forwards (D1–D5) and 5 informational notes (D6–D10) recorded below.

## 0. Review method and evidence basis

The owner PC is below the disk floor (~1.67 GB free); no local browser, node_modules, or installs were used or permitted. Per the ADR-005 evidence-capture division of labor, the real browser interaction happened in CI (GitHub Actions run 29548158336, ubuntu, Chromium, all 6 jobs green per orchestrator-verified `project-control/reports/M2-T001-G2-evidence.md`): 22 Playwright journeys against the production `next build`/`next start` bundle talking to the REAL FastAPI service (`apps/web/e2e/harness/fixture_api.py` — the real app with only the accepted `get_pluto_fetcher` seam overridden, replaying committed official PLUTO captures). I judged that evidence as a first-time analyst would, from:

1. Every e2e spec, read adversarially (`apps/web/e2e/*.spec.ts`, `helpers.ts`, `playwright.config.ts`, harness).
2. The full implementation (`src/app/property/page.tsx`, all 11 `src/components/property/*.tsx`, all `src/lib/*.ts`, `layout.tsx`, `globals.css`, `ci.yml`, `.env.example`).
3. Visual frames extracted from the downloaded CI artifact (`%TEMP%\m2t001-playwright`, 10.7 MB). Note: the config uses `screenshot: "only-on-failure"` and all tests passed, so there are no standalone PNGs; I extracted and viewed the `resources/page@*.jpeg` screencast frames inside `trace.zip` for 10 traces (~75 frames), covering: banner + form, staged loading, full lot-facts table with opened provenance drill-down, expanded missing-inputs list, 500 state with correlation id, keyboard focus ring on the provenance summary, mapped-features table, and the PRD §29 footer.
4. The binding packet `project-control/tasks/M2-T001.json` (S1–S8), design standards, and — last — the producer report.

No network calls were needed; no `gh` failures to report. Nothing outside `.claude/agent-memory/human-journey-reviewer/` was written except review scratch extraction under the already-downloaded artifact folder in `%TEMP%` (~5 MB, deletable).

## 1. Journey-by-journey findings (input → expected → actual → evidence)

### J1 — S1 primary flow (BBL 1000010010, split-zone F05 official capture)
- **Input:** `1000010010` typed into the BBL field, "Look up property".
- **Expected:** staged loading → profile with identity, facts+units, PRD §12 coverage labels, completeness banner, both split-zone districts, provenance drill-down (source/dataset/version/original value/retrieved_at).
- **Actual:** PASS. Loading card shows three truthful stages ("✓ BBL format checked" / "… Retrieving the official property record and building the canonical profile" / "Rendering official facts" pending) — seen in frames for 1000041001 and 3000010004; no fake progress bars. Profile renders "BBL 1000010010", "140 CARDER ROAD, Manhattan 10004", reproducibility line (nyc-dcp-pluto-soda · 64uk-42ks · release 26v1 · retrieved 2026-07-16T12:00:00Z · data.cityofnewyork.us · correlation id). Frame `primary-journey-S1-provena.../…706987.jpeg` shows the lot-facts table: human labels ("Lot area", "Lot frontage", "Tax block"), value **7,577,714 square feet** with units in muted type, `◐ conditional` badges, and the opened drill-down listing Source / Original field `lotarea` / Original value `7577714` verbatim / Normalized `7,577,714` / Units / Dataset version `26v1` / Retrieved at / Effective date ("not published by the source (shown explicitly, not omitted)") / Conflict status / Dataset id / Retrieved from host. Spec additionally asserts R3-2, C4-1, and GI special district chips, the exact enum `missing_noncritical` in the banner, the explicit empty-conflicts statement, and the always-visible "Missing official inputs (24)" total.
- **Coverage wording:** `src/lib/coverage.ts` renders the exact PRD §12 enums (`verified`, `conditional`, `professional_review_required`, `data_conflict`, `unsupported`, `not_applicable`; `complete`/`missing_noncritical`/`missing_critical`) verbatim, each with a symbol and a plain-language gloss — never color-only (symbol + text in the badge, gloss via `title` + screen-reader text).

### J2 — S3 malformed input
- **Input:** `1-00001-0100` and `123`.
- **Expected:** client-side rejection before any network traffic; helpful message.
- **Actual:** PASS. Spec counts API calls via route interception and asserts **zero**; messages are genuinely helpful ("A BBL contains digits only — no dashes, spaces, or letters. Example: 1000010010."; "A BBL is exactly 10 digits; you entered 3."; borough message names all five boroughs). The server-422 path stays honestly reachable: the client mirror deliberately omits the all-zero-block check (documented in `bbl.ts`), and `1000000000` renders the real API's `invalid_block` code + "tax block" message — no test-only bypass flag in app code.

### J3 — S4 no-match / condo billing lot
- **Input:** `1000041001` (F02b condo unit lot) and `5999999999` (borough-5 boundary, no record).
- **Expected:** a result, not an error; the actionable billing-lot explanation.
- **Actual:** PASS. `NoMatchState` says "valid format… no record… This is a result from the official source, not a system error" and renders the API's explanation verbatim; spec asserts "BILLING lot" and the "7501-7599" lot range. Recovery is obvious: the lookup form stays on screen above the state.

### J4 — S5 failure states
- **Input:** control BBLs 3000010001–5 driving the REAL error-mapping code (429×3 → `rate_limited` 503, timeout×3 → 504, network×3 → `source_unavailable` 503, drift fixture → `schema_drift` 502, raised exception → generic 500), plus browser-level connection-refused with unroute-then-retry.
- **Expected:** distinct, typed, plain-language states; retry affordance; 500 shows correlation id, no internals.
- **Actual:** PASS. Each state has its own copy stating what failed, that the user's input was fine, and whether retry is safe; `schema_drift` is explicitly distinguished ("not a temporary outage… connector must be updated"). Screenshot of the 500 state shows "Something went wrong on our side", Retry lookup button, and "Reference id for support and server logs: cf859f97…". Spec asserts no "Traceback"/"RuntimeError" leakage. The connection-failure journey proves recovery end-to-end: retry after unroute reaches the real profile. Stale-response protection exists (monotonic `requestSeq`).

### J5 — S6 partial data + conflicts
- **Input:** `1000010101` (F04, `numfloors` omitted by the source) and `1000010103` (labeled SYNTHETIC borocode conflict derived from official F01 — same technique as the accepted M1-T005 S4 test; derivation documented in the harness).
- **Expected:** no crash; documented missing-inputs policy with nothing silently dropped; conflict shows both values with sources, unresolved.
- **Actual:** PASS. Frame `partial-and-conflict-S6-pa.../…703060.jpeg` shows surfaced feasibility-relevant gaps with NONCRITICAL tags and reasons, the "Hide 14 additional missing fields" toggle expanded, and the grouped administrative columns all visible. The policy itself is a real documented record (`src/lib/missing-inputs.ts`): critical never collapsed, feasibility-relevant list grounded in the accepted builder's fact buckets, presentation-only, total always shown. Conflict spec asserts "Borough code", "resolution: unresolved", exactly two values each with `nyc-dcp-pluto-soda`/derivation, `data_conflict` badge on the affected fact while others stay `conditional`, and — visible in the frame for 1000010103 — the identity card shows "CARDER ROAD" with **no borough asserted** under conflict (honest, matches the M1-T005 tolerance rules). Empty-conflicts rendering is explicitly asserted in J1 (not silently absent).

### J6 — S2/D5 provenance fallback
- **Input:** `1000010100` (F01, live contract-1.0.0 profile, no district-provenance maps).
- **Expected:** district provenance still renders, honestly labeled.
- **Actual:** PASS. Chip drill-down asserts "Linked by source column name" + `zonedist1` + source id. The fallback join in `provenance.ts` never assumes map coverage (map → column-name fallback → explicit "Provenance not linkable… shown, never hidden"). Zero-valued boundary fact `lotfront 0 feet` is asserted rendered (never dropped). Map-present path is unit-tested on a documented derived v1.1 fixture (disclosed; the live builder emits 1.0.0, so e2e cannot exercise it — legitimate).

### J7 — S7 honesty
- **Actual:** PASS on all four checks. INTERNAL DEVELOPMENT BUILD banner is the first element in every screenshot; PRD §29 disclaimer footer (verbatim from `disclaimer.ts`) is visible in-frame and asserted. Address input is rendered, visibly disabled, with honest copy ("credentials are still pending… this screen will not pretend to resolve addresses") — seen in every frame. `verified`/`best` are asserted absent from rendered text on a live profile (the collapsed coverage-policy quote legitimately contains the word inside a drill-down; `innerText` correctly excludes collapsed content, and the visible check is the right one). The "only through the real API" journey blocks the API and proves no mocked success path exists; grep confirms `src/test-support/fixtures.ts` is imported only by tests. The ProfessionalReviewPanel is honestly scoped: states the review obligation and that the structured workflow arrives with the rule-review milestone — no pretend submission flow.

### J8 — S8 keyboard and accessibility
- **Actual:** PASS for what it claims. The keyboard spec is genuinely mouse-free: Tab-to-input (by id), type, Enter submits, Tab-to-"Source for Lot area", Enter opens the native `<details>`, then a computed-style check proves a visible focus indicator. The final frame shows the focus ring clearly around the summary. Code review of aria usage is sane: `aria-describedby` on the input pointing at hint + always-present error container, `aria-live="polite"` on error and loading regions, `role="status"` on the completeness banner, `aria-expanded` on the grouped toggle, `aria-labelledby` section headings, `scope` on table headers, `visually-hidden` glosses, `:focus-visible` ring token, `prefers-reduced-motion` honored. Limits noted in D2/D3.

## 2. Design quality vs docs/PREMIUM_PRODUCT_DESIGN_SYSTEM.md

Judged from the frames: calm single-accent (navy) palette, quiet borders, restrained radii from central tokens, tabular numerals, uppercase micro-headers, generous card spacing, one primary action, no clutter walls, no default-template look — this reads as an intentional, restrained product screen, comfortably above "generic scaffold" for a first internal slice. Status system follows §8 (label + symbol + color + gloss). Loading follows §12 (actual pipeline, no fake stages). Two deviations recorded: raw dataset column keys shown to users (D1, §15) and no responsive behavior (D2, §13). The single-column card stack (no top bar/nav shell per §3) is acceptable for the first screen of the Property stage.

## 3. Hidden assumptions / what the tests did NOT prove (adversarial reading)

- No responsive/viewport evidence at all — Desktop Chrome only; `globals.css` has no narrow-width handling; the four-column facts tables will be cramped or overflow on tablet/phone (D2).
- The grouped-missing toggle and retry buttons were operated by mouse in e2e; keyboard operability rests on native `<button>` semantics + unit tests (fold under D2).
- The schema-drift and no-match final states have no captured frame (screencast timing); their content is proven by DOM assertions plus the identical `FailureState` component seen rendered for the 500 case (D9 — informational, evidence sufficient).
- `unexpected_response` (routing 404 / undocumented body) is unit-tested only — disclosed and reasonable, since the UI cannot construct that request itself.
- S1's packet wording "conflicts section (split-zone fixture shows zonedist values from both sources)" did not happen literally: the official F05 capture yields two districts from two source *columns* and an empty conflicts array; the conflict UI was proven with the labeled synthetic borocode variant instead (D7 — the packet's assumption was wrong about the data, the producer disclosed it, and the intent is fully covered).
- Loading stages are honest but static (stage 3 never visibly activates because render is instantaneous) — acceptable, not cosmetic deception.

## 4. Low-storage check (question 8)

PASS. The feature writes nothing persistent to the user device: no `localStorage`/`sessionStorage`/`indexedDB`/cookie usage anywhere in `src` (grep-verified). All installs/builds/browser runs happened in CI; the worktree contains no node_modules/.next; the only local by-product is the producer's `e2e/harness/__pycache__/*.pyc` (KB-scale, git-ignored, not committed — verified via `git ls-files`). `.env.example` is names-only; `NEXT_PUBLIC_API_BASE_URL` is a URL, not a credential.

## 5. Defects

**Blocking: none.**

| # | Severity | Finding | Disposition |
|---|----------|---------|-------------|
| D1 | Medium | Raw PLUTO column keys shown as primary user-facing labels in the missing-inputs section (`overlay1`, `spdist1`, `zonedist2–4`, and grouped admin columns like `basempdate`, `dcasdate` — visible in the S6 screenshot). `FIELD_LABELS` in `src/lib/format.ts` lacks entries for ~20 keys that `FEASIBILITY_RELEVANT_FIELDS` deliberately surfaces (`residfar`, `commfar`, `facilfar`, `affresfar`, `mnffar`, `zonedist1–4`, `overlay1–2`, `spdist1–3`, `ltdheight`, `mih_opt1–4`, `edesignum`, `appbbl`, `appdate`, `condono`). Conflicts with design-system §15 ("Raw GIS layer names shown to end users" prohibited) and the UI pack's no-unexplained-jargon rule. Tolerable in an INTERNAL DEV build. | Carry-forward to the Confirm-screen task: extend FIELD_LABELS to cover every surfaced key. |
| D2 | Medium | No responsive-layout evidence (UI human-journey pack item): single Desktop Chrome project, no CSS breakpoints, tables likely degrade at tablet/phone widths; grouped-toggle/retry keyboard operation not exercised in e2e (unit-level only). Packet S1–S8 did not demand it, so non-blocking. | Carry-forward: add viewport journeys (and toggle-by-keyboard) when the Confirm screen lands. |
| D3 | Low | Coverage-badge plain-language gloss is reachable only via mouse-hover `title` and screen-reader text; a sighted keyboard/touch analyst sees the bare enum (`conditional`, `professional_review_required`) with no visible explanation. PRD §12 exact wording is correctly preserved; the gap is the missing always-visible explanation affordance (e.g., a legend or tap-to-expand). | Carry-forward. |
| D4 | Low | Missing-inputs reasons are the API's verbatim boilerplate repeated on every row ("column absent from the SODA record (null-omission semantics)…" ×24) — honest but visually dense against the "calm/spacious" standard. Consider stating the shared reason once. | Carry-forward. |
| D5 | Low | Submitting a client-invalid BBL after a successful lookup unmounts the rendered profile entirely (screen state replaces `done`); the previous result vanishes though the user only mistyped a follow-up query. Also the inline client error persists while the user retypes until next submit. Minor UX surprise, no stale/wrong data ever shown. | Carry-forward. |
| D6 | Info | Producer report §8 and G2 evidence say "14 Playwright journeys"; the artifact and specs contain **22** test cases (3+3+2+6+3+1+4). Undercount only — bookkeeping inaccuracy, evidence is stronger than claimed. | Note for orchestrator records. |
| D7 | Info | S1 packet wording assumed the split-zone fixture produces cross-source conflicts; the real official capture does not (empty conflicts array). Conflict UI fully proven via the documented, clearly-labeled synthetic borocode variant. Disclosed by the producer. | Accepted as-is. |
| D8 | Info | CORS: the deployed API has no CORS policy; the browser design fetches cross-origin. Test-origin-only middleware lives in the harness. A reviewed proxy/CORS decision is REQUIRED before any real cross-origin deployment (B-001/B-002 already prevent deploy today). | Must be tracked as an explicit follow-up task before any deploy task. |
| D9 | Info | No captured frame of the final schema-drift/no-match render (trace frame timing); content proven by DOM assertions + the same component photographed in the 500 journey. | No action. |
| D10 | Info | Commit `dd34c7b` is an orchestrator "mechanical lint fix" (dropped one unused import) on the producer branch — documented in G2 evidence, content-neutral. | Process note only. |

## 6. Verdict

**PASS.** The primary S1 journey reads clearly to a non-engineer walking the screen: honest banner, one obvious action, staged truthful loading, labeled facts with units, exact PRD §12 coverage vocabulary never carried by color alone, always-visible conflict/missing/unsupported sections with explicit empty states, and a provenance drill-down that answers source/dataset/version/original value/retrieved-at in one click (also keyboard-only). Every documented failure is a distinct, recoverable, plain-language state; the 500 shows a correlation id; the condo no-match is a genuinely actionable result. Honesty checks all hold — no mocked success path, no pretend address search, no invented "verified"/"best", disclaimer present. Evidence is real-browser, real-API, recorded-official-fixture CI evidence with traces I inspected visually.

**Nothing blocks acceptance of M2-T001.** D1–D5 are carry-forwards for the Confirm-screen/auth follow-on tasks; D8 (CORS/proxy decision) must be tracked as an explicit blocker for any future deployment task.

*Reviewer artifacts consulted:* `.claude/worktrees/M2-T001/apps/web/**` @ dd34c7b; `%TEMP%\m2t001-playwright\{playwright-report,test-results}` (frames extracted under `%TEMP%\m2t001-playwright\extract\`, deletable); `project-control/tasks/M2-T001.json`; `project-control/reports/M2-T001-G2-evidence.md`; `docs/PREMIUM_PRODUCT_DESIGN_SYSTEM.md`; producer report read last.
