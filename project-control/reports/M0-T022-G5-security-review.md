# G5 Security Gate Report — M0-T022 (Owner Mission-Control Dashboard)

_Verbatim independent reviewer return (security-reviewer); transport entities decoded only._

- **Gate ID:** G5
- **Task ID:** M0-T022
- **Reviewer:** security-reviewer (independent, read-only)
- **Producer:** frontend-engineer
- **Result:** PASS
- **Frozen SHA:** `7ea8b0d22a8300938f85452be19b85f8a8cc8e3a` (verified via `git rev-parse HEAD`). Read-only; no `project_control.py`, git-write, or `gh` invoked.

## Acceptance criteria reviewed
AS-13 (read-only + internal + no-secrets + XSS-safe + least-privilege + no-SSRF), AS-11 (stale-safety half), AS-4 (gate independence not bypassed), AS-17 (GitHub never corrupts canonical state).

## Steps independently executed
1. Enumerated every dashboard file (lib/dashboard, app/dashboard, components/dashboard, test-support, e2e spec, playwright.config).
2. Grep dangerous sinks `dangerouslySetInnerHTML|innerHTML|outerHTML|eval|new Function|document.write|insertAdjacentHTML|__html` across apps/web/src → no matches.
3. Grep write/network/mutation `writeFile|appendFile|createWriteStream|POST|PUT|PATCH|DELETE|method:|exec|spawn|child_process|unlink|rmSync|mkdir` across lib/dashboard → only `method: string;` in types.ts:120 (a formula field, not an HTTP method).
4. Grep secrets `token|secret|service.?role|api.?key|Authorization|Bearer|password|credential|SUPABASE|NEXT_PUBLIC` → no secret material; only comments asserting none, the `TRUE_TOKENS` flag allowlist, and unrelated fixtures.
5. Grep `href|<a |target=|window.open|location.|.url` across components/dashboard → no matches (GitHub PR url parsed but never rendered as a link).
6. Confirmed only three impure edges: config.ts (process.env), loader.server.ts (node:fs/path), githubClient.ts (globalThis.fetch); all other engine modules pure.
7. Read all presentational components + ui.tsx + ProductMap.tsx line-by-line; 100% JSX text interpolation.
8. Traced import graph of dashboardEnabled/loader.server/getDashboardModel → imported only by page.tsx (server) + the engine test; never by a client component.
9. `git diff --stat origin/main...HEAD` → all changes confined to allowed paths; render.yaml, next.config.ts, package.json, package-lock.json, .env* NOT in the diff.
10. Read ci.yml diff → additive product-map job only; secret-scan + existing jobs untouched.
11. Grepped python tools for writes/network/subprocess → none.

## Expected vs actual (all confirmed)
- Read-only: only fs.stat/readFile/readdir; githubClient GET-only; no child_process/exec; engine core pure.
- Internal gate fail-safe OFF: config.ts returns false unless value ∈ {1,true,yes,on}; page.tsx notFound() before model build; flag name has no NEXT_PUBLIC_ prefix; render.yaml unchanged ⇒ unset in prod ⇒ 404 by default.
- Secrets: none; GH request sends only Accept + User-Agent; e2e flag is CI-test-only, non-public.
- Injection/XSS: zero dangerouslySetInnerHTML; SVG uses <text>{...}</text>; no href/anchors ⇒ no javascript:-scheme vector.
- SSRF: fixed host `https://api.github.com` + DEFAULT_REPO constant; opts.repo override test-only (prod passes none); 6s AbortController timeout.
- Error handling: loader never throws; raw fs/GH error strings live in model.issues/github.error and are never rendered; UI shows generic "unavailable"/"stale".

## Findings
None blocking. Non-blocking informational:
- N1 · loader.server.ts:49,81 — Issue messages embed (e as Error).message which for fs errors can include an absolute server-side path; stored in model.issues but NOT rendered by any component (verified). Keep raw issue.message out of any future rendered output.
- N2 · githubClient.ts:24 — fetch follows redirects by default; harmless (fixed trusted host).
- N3 · page.tsx — sole production exposure control is the fail-safe-off runtime flag (app has no auth yet, B-001). Acceptable for internal V1 and signposted by InternalBanner; place behind auth once it lands.

## Reviewer conclusion
VERDICT: PASS. Strictly read-only, internal-only observability layer. No fs writes, GET-only GitHub, fail-safe-off non-public flag → 404 by default (render.yaml unchanged), no secrets, no dangerouslySetInnerHTML/raw HTML, fixed-host/fixed-repo client with bounded timeout (no SSRF), fail-safe error handling that never renders tracebacks/paths/secrets. Cross-tenant/service-role/storage/upload/prompt-injection not applicable to this surface. AS-13, AS-11 (stale-safety), AS-4 satisfied. Three non-blocking notes; none affects the verdict.

---

## Carry-forward to b2de479 (orchestrator note) — G5 PASS holds

After the G1 wave, a honesty correction was applied at b2de479 (3 files: model.ts accepted-task gate-display short-circuit, engine.test.ts new test, fixtures.ts test cap-target). This G5 review's scope is unaffected: the delta is pure display/derivation logic for accepted-task gate state and a test fixture — it introduces **no new IO, no fs writes, no network, no secret, no new render sink, no dangerouslySetInnerHTML, and no change to the flag gate, the GitHub client host/timeout, or error-handling redaction**. `git diff 7ea8b0d..b2de479` touches none of the files or patterns central to this review. CI run 29977738748 is green on all 11 jobs incl. secret-scan at b2de479. The G5 PASS therefore carries forward to b2de479 without re-review.
