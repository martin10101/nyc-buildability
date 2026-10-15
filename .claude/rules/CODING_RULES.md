# CODING_RULES — terse do/don't (D-068; auto-injected; append at discovery, one line per rule)

- DO type DOM queries in web tests: `querySelectorAll<HTMLElement>(...)`; getByRole returns
  HTMLElement — mixing with element-typed arrays fails strict-TS in CI.
- DO write deliberate invalid-shape test probes as `as unknown as T`, never a direct cast.
- DON'T `.focus()` a ref synchronously in a handler whose state change remounts the target —
  bump a nonce state and focus in a `useEffect`.
- DON'T commit an empty `.test.ts`/`.test.tsx` — vitest fails on "no suite"; seed one trivial
  passing test. Empty python test files are fine.
- DO keep every seeded placeholder line <= 100 chars — ruff E501 lints app/ placeholders and is
  the api CI job's first step (wave-10 seam 06db6449 reddened CI until 580d1125).
- DO run focused web checks on the Linux dev server while developing (owner D-090-R170/R171, R639):
  in `apps/web`, `npx --yes npm@11.18.0 ci --no-audit --no-fund` (once per worktree), `npm run lint`,
  `typecheck`, touched tests; e2e with the lanes venv first on PATH and
  `PYTHONPATH=<checkout>/services/api`. Full suites + security checks must PASS IN CI on the exact
  head accepted or merged; later code changes need them again. Lockfile packages only; never mark web
  behavior verified from reasoning alone. NEVER on the owner's PC (thin client).
- DO run `python -m ruff check services/api` before any api checkpoint/commit — it is the api
  CI job's first step; a lint miss costs a CI round.
- DON'T read jsdom `getContext`/WebGL console noise as the failure (MapLibre components spam
  it) — read the vitest FAIL summary lines only.
- DO sweep consumers of a changed behavior contract beyond your file list (code-graph
  `query.py --no-regen impact <path>`); route out-of-scope test updates to the orchestrator —
  never leave a known-red consumer silent.
- DO LF-normalize before hashing checkout files (CRLF smudge changes digests); strip `\r`
  from CLI-piped digests on Windows.
- DON'T grow a file past its responsibility — check `python tools/modularity_check.py --check`
  before substantially expanding any production file; split with a compatibility facade.
- DO keep new JSON/config records to the exact schema shape already in the repo (mirror a
  committed example) — invented shapes fail closed in control-plane CI.
- DON'T put `&&`, quotes-in-`git commit -m`, or heredocs through PowerShell 5.1 — use the Bash
  tool; write multi-line content with the Write tool.
- DO run api pytest from `services/api` cwd — the rules suite ALONE from repo root fails
  collection with `No module named 'app'` (invocation artifact, not a defect; it has faked a
  16-error red twice).
- DON'T match focus by `activeElement.textContent` without excluding body/documentElement -
  a Tab wrap parks focus on `<body>` whose textContent is the WHOLE page, so any textContains
  false-matches with nothing focused (e2e tabUntil trap, fixed a3173987).
- DO check stubbed-route fixtures against the server's real enum vocabulary AND confirm the
  asserted request can actually elicit the stubbed response from the real engine - CI green
  surfaces neither (T070 G3/G4 wave: invented no_fit + a fitted candidate the geometry-free
  request can never produce).
- DO make a "fix does not corrupt X" test assert the field the bug displaces: revert to the
  literal pre-fix code and confirm the asserted value moves (M5-T083 G4-F6: points[0] was invariant).
- DON'T enable eslint-plugin-react-hooks 7.x `configs.recommended` / `recommended-latest` wholesale — they add every
  React-Compiler rule at ERROR; register the plugin and name `rules-of-hooks` (error) + `exhaustive-deps` (warn) (M0-T180).
- DO expect `@eslint/js` recommended, when first enabled, to flag intentional control-char regexes (`no-control-regex`), a
  literal U+FEFF in a regex (`no-irregular-whitespace`) and double spaces in test regexes — fix behavior-identically
  (line-scoped justified disable, `\uFEFF`, ` {2}`), never by weakening the config (M0-T180 S3).
- DO have the FULL `pytest -q` of services/api PASS IN CI on the exact head accepted or merged (R639);
  locally: ruff + touched folders, plus tests/cad and tests/drawings when a shared
  `packages/contracts/fixtures/valid/<schema>/` fixture changes (snapshot per fixture; #387 F1).
- DO run `python .github/scripts/validate_contracts.py` + `pytest .github/scripts/tests` before pushing a
  contract schema: it fails closed on any keyword outside KNOWN_KEYWORDS (M5-T128: `minProperties`).
- DON'T write the text `result_way` anywhere under services/api/app outside the guard's permitted list, docstrings
  included: test_result_ways.py scans file TEXT (a page-1 docstring reddened api + exact-production-install, wave 24).
- DO put every test that pins a tuple or list the task extends (e.g. test_r6b_reference_cases.py pins CASE_IDS
  literally) into the packet's allowed paths at the contract seam; a missed pin costs a scope correction (M5-T176).
- DO make a new browser spec ask the results route at most ~3 times (show results once, then setViewportSize and
  re-measure): results_read.py allows 30 requests per window for ALL specs; 13 extra reddened results.flag-on:68 (M5-T181).
- DON'T accept 'fits in the first screen' from CSS reasoning: measure on the real preview (capture_six.mjs) and assert
  the value's bottom inside the dialog's visible area; toBeInViewport passes on a sliver (M5-T181 r1 missed by 30 px).
- DO list a benchmark regeneration's consumer tests in the contract (wiring S12, register S13 date, constraint_rows and
  report_benchmark benchmark cases, web results-contract-checks pin): M5-T167 needed scope correction 2 for them.
- DO list the RULE-FILE fan-out at the contract seam when a task adds a lane-A rule file: tests/rules/test_r6b_a02b_golden.py and
  test_r6b_other_districts_unchanged.py pin the rule set, and the register calc pages re-render (M5-T170 scope correction 1).
- DO diff EVERY page of a report print against main's (pdftotext per page) before the reviews, not only the pages the task
  names: M5-T167's page-6/8 fix silently emptied two page-3 rows (DB-266), caught only in the next PDF.
- DO put every evidence record whose code_paths a packet edits into its allowed paths at the contract seam (forbidding NB-03
  while M5-T170 edited rear_yard_checks.py left the record stale and cost scope correction 2 and a round 3, 2026-10-15).
