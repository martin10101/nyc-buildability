# CODING_RULES — terse do/don't (D-068; auto-injected; append at discovery, one line per rule)

- DO type DOM queries in web tests: `querySelectorAll<HTMLElement>(...)`; getByRole returns
  HTMLElement — mixing with element-typed arrays fails strict-TS in CI.
- DO write deliberate invalid-shape test probes as `as unknown as T`, never a direct cast.
- DON'T `.focus()` a ref synchronously in a handler whose state change remounts the target —
  bump a nonce state and focus in a `useEffect`.
- DON'T commit an empty `.test.ts`/`.test.tsx` — vitest fails on "no suite"; seed one trivial
  passing test. Empty python test files are fine.
- DON'T run or document npm/npx/node locally (thin client) — web tests prove ONLY in CI on the
  pushed head; never mark web behavior verified from local reasoning.
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
