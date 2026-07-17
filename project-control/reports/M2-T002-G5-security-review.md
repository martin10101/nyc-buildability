<!-- Verbatim reviewer return (agent-return channel; agentId a301d9dc3a3558f9d, security-reviewer, 2026-07-17). Saved by the orchestrator per the report-preservation rule. Verdict: G5 PASS (zero blocking; L1/L2 LOW, I1/I2 INFO). -->

# G5 Security & Privacy Gate Report — M2-T002

**Task:** M2-T002 — Confirm screen (step 2) + hardened API client (M2-T001 D1–D5 carry-forwards)
**Gate:** G5 (security and privacy)
**Reviewer:** security-reviewer (independent; did not produce the work)
**Review target:** worktree `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M2-T002`, branch `task/M2-T002-confirm-screen`, HEAD `6d9fbd4` (incl. rework)
**Diff basis:** `git diff main...HEAD` — 40 files, all under `apps/web/**` plus `project-control/reports/M2-T002-producer-report.md`. No `services/**`, `packages/**`, `render.yaml`, or `.github/workflows/ci.yml` changes (verified empty diffs). Implementation not modified by this review (read-only per ADR-005).
**Prior baselines applied:** M0-T015 CORS/header baseline (agent-memory `cors-header-baseline-review.md`); B-001 unauthenticated INTERNAL/DEV no-deploy stand.

---

## Area 1 — Reflected-content safety: PASS

**Sanitizer** (`apps/web/src/lib/bounded.ts`): `boundedText` — 600-char cap, C0/C1 + DEL control-strip via `fromCharCode` regex (bounded.ts:26-29), CR/LF/TAB normalized to spaces, explicit `… [truncated]` marker, non-string → caller fallback (never coerced). `boundedToken` — 64-char cap, `[A-Za-z0-9._-]` allowlist, empty → `null` (bounded.ts:58-67). Unit-tested incl. `abc<script>def` → `abcscriptdef` (bounded.test.ts:43).

**Application at every error-path reflection point** (`apps/web/src/lib/api.ts`): correlation id `boundedToken` at api.ts:209; unexpected-state token `boundedToken(state,48)` at api.ts:244; no_match bbl `boundedToken(...,32)` and message `boundedText` at api.ts:269-274; validation_error code/message at api.ts:282-283; upstream/server-contract/internal messages at api.ts:293/302/313; validation problems `boundedText` per item at api.ts:256-258. Every outcome component in `FailureState.tsx` renders only these pre-bounded fields or static copy; correlation ids render as `<code>{correlationId}</code>` text nodes (FailureState.tsx:27).

**Sink grep across `apps/web/src`:** zero hits for `dangerouslySetInnerHTML`, `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `eval(`, `new Function`, string-arg `setTimeout` (only match is the comment at bounded.ts:5). All reflection is React text interpolation (auto-escaped).

## Area 2 — Pair-matrix spoofing defense: PASS

`contract-matrix.ts:38-49` mirrors the backend's 10-pair STATUS_STATE_MATRIX; `isDocumentedPair` is exact set membership (contract-matrix.ts:60-62). `api.ts:232` extracts the **RAW** state (deliberately unsanitized for comparison — sanitize-before-compare laundering is explicitly avoided, api.ts:229-231); `api.ts:240-247` rejects any undocumented pair to `unexpected_response` **before** any state-based routing. Consequences verified by reading the control flow:
- 500 + `state=no_match` (recorded adversarial fixture `packages/contracts/fixtures/client_regression/http500_state_no_match.json`, verified present with correct incoherent-pair provenance note) → `unexpected_response`; the body's message is never rendered — e2e asserts its absence (client-hardening.spec.ts:52).
- Documented state on wrong status (503 + `timeout`) → `unexpected_response` (e2e client-hardening.spec.ts:55-68).
- A 200 carrying a spoofed `state` string (e.g. `no_match`) → key `200:no_match` not in set → `unexpected_response`.
- Non-JSON body → `unexpected_response` with state null (api.ts:221-227).
- A state containing HTML/URLs can only reach the screen through `boundedToken(...,48)` (strips `<>/:` etc.) at api.ts:244, rendered as escaped `<code>` text (FailureState.tsx:278).
The S2 e2e replays the recorded fixture at the network layer with faithful status/headers/body (client-hardening.spec.ts:18-53).

## Area 3 — Runtime validation before render (S3): PASS

`api.ts:249-262`: every 200 runs `validateProfileDocument` before any outcome carrying profile data exists; failure yields only the bounded problem list. `validate-profile.ts` checks every documented key, all enums against contract-locked arrays, and the closed `SUPPORTED_CONTRACT_VERSIONS` set; failure is total (`{ok:false}` never returns a profile, validate-profile.ts:500-503). Problem list is bounded at source (`MAX_REPORTED_PROBLEMS = 20` + one omission marker, validate-profile.ts:40-56) **and** each string is re-capped by `boundedText` in api.ts:256-258 — server-derived key names inside problem paths cannot flood. `ValidationFailureState` renders only that bounded list and static copy (FailureState.tsx:187-223); e2e proves nothing partial renders (`profile-view`/`identity-card` count 0, no fact values, no zoning chips — client-hardening.spec.ts:88-97) and an unpublished `contract_version` fails closed (spec:100-118).

## Area 4 — Secrets / bundle hygiene: PASS

Only env read in `apps/web/src` is `process.env.NEXT_PUBLIC_API_BASE_URL` (api.ts:153). Secret-pattern grep (`secret|api[_-]?key|service[_-]?role|token|password|bearer|authorization`) across src: only benign matches (bounded.ts "token allowlist" naming, CSS comment). No Authorization header is ever sent (api.ts:188-193 sends only `Accept`). `apps/web/.env.example` remains names-only with the service-role prohibition text. No package.json/lockfile diff (Area 9), so no new bundle surface.

## Area 5 — Browser storage discipline (PRD §14.3): PASS

Zero hits for `localStorage|sessionStorage|indexedDB|document.cookie|window.open` in `apps/web/src`. Profile/outcome state lives only in React component state (PropertyLookup.tsx:145-147, ConfirmScreen.tsx:372-374); re-fetched from the API on every visit — the browser is never the sole location of any record. Zero `console.*` calls in src — no sensitive payloads logged.

## Area 6 — URL/query handling: PASS

`ConfirmEntry` (ConfirmScreen.tsx:427-453) reads `?bbl=`, runs `validateBblInput` (bbl.ts:36-72: digits-only, exactly 10, borough 1–5) before **any** fetch or render use; the raw parameter is never reflected — the invalid-param card renders only client-constructed messages (the only dynamic fragment is the digit count, bbl.ts:58). The fetch URL wraps the canonical BBL in `encodeURIComponent` (api.ts:168) and both call sites pass validator output only. The only dynamic href in the app is the relative `/property/confirm?bbl=${encodeURIComponent(...)}` link (PropertyLookup.tsx:131); all way-back links are hard-coded `/property`. No `window.location`, no open-redirect surface.

## Area 7 — Request hygiene: PASS

No client auto-retry exists anywhere: every retry is a user click (`RetryButton`, FailureState.tsx:32-38; ConfirmScreen retry increments `attempt` only via onClick, ConfirmScreen.tsx:391). Supersession actively aborts the prior request plus a monotonic sequence guard (PropertyLookup.tsx:150-171); unmount aborts (PropertyLookup.tsx:154, ConfirmScreen.tsx:388); the 12s timeout aborts the socket (api.ts:180-183) and yields the recoverable `client_timeout` state. Timer and listener are cleaned up in `finally` (api.ts:316-319). No storm vector; e2e covers cancellation/timeout (client-hardening.spec.ts:148-210).

## Area 8 — CORS posture: PASS (carry-forward intact)

- `services/**` untouched (empty `git diff main...HEAD -- services/`); the real API retains the M0-T015 baseline exactly (exact-origin allowlist, deny-all when unset, `allow_credentials=True` — services/api/app/main.py:95-101) and still has **no** `expose_headers` for `X-Correlation-ID`.
- The e2e harness (`apps/web/e2e/harness/fixture_api.py:158-164`, pre-existing, unchanged in this diff) adds CORS only in test infra: localhost origins only, `GET` only, `Accept` only, **no credentials**, `expose_headers=["X-Correlation-ID"]`. It is not deployed and is outside `services/**`.
- The client does not use credentialed CORS (`fetch` default `same-origin` credentials; no cookies/Authorization).
- **D8/CORS carry-forward confirmed still open, not silently resolved:** in any real cross-origin deployment the browser would hide `X-Correlation-ID` (no expose header) and the origin would be denied until the reviewed CORS/proxy decision lands; the harness docstring and the S2 spec comment (client-hardening.spec.ts:27-32) both flag this honestly. Deploy-blocking decision remains with the standing B-001/no-deploy posture.

## Area 9 — Dependency surface: PASS

`git diff main...HEAD -- apps/web/package.json apps/web/package-lock.json package.json` is empty. Zero new dependencies. `.github/workflows/ci.yml` unchanged (permitted-additive path unused; new specs picked up by the existing web-job glob — CI on PR #21 green per orchestrator, Playwright count 41→43 in rework commit).

**Prompt-injection posture (frontend leg):** official-source-derived strings (PLUTO values, messages) render exclusively as escaped React text data — a hostile instruction string in government data displays as inert text; no AI invocation exists in this client. Least privilege: the client can only GET one versioned endpoint with a format-validated identifier.

---

## Findings

| ID | Severity | Blocking | Finding | Evidence | Remediation |
|----|----------|----------|---------|----------|-------------|
| L1 | LOW | No | `isDocumentedPair` encodes the 200-no-state pair as key `"200:"` (`state ?? ""`), so a 200 body carrying `state: ""` aliases the documented (200, null) pair instead of being rejected as "state present on a 200". Not exploitable: the body must still pass full profile validation to render, and a valid profile with a stray empty `state` key is harmless (extra keys tolerated, never read). | contract-matrix.ts:51-53,60-62; api.ts:232 | When the matrix module is next touched, use a sentinel that cannot collide with a real string (e.g. tuple check or `state === null` guard for the 200 row). Repro: `isDocumentedPair(200, "")` returns `true`. |
| L2 | LOW | No | Length caps do not extend to string fields **inside a validated 200 profile**: `identity.geometry.type` is rendered with no validation beyond the parent `isRecord` (ConfirmScreen.tsx:203-205; validate-profile.ts:212-214); `fieldLabel()` unknown-key fallback echoes the raw server key (format.ts:231); `formatValue()` JSON.stringify is unbounded (format.ts:23); `fact.units` / `missing_inputs[].reason` are type-checked but uncapped. React escaping prevents XSS in all cases; residual risk is UI flooding by a compromised first-party API — an adversary in that position already controls all displayed facts. | files/lines cited | Optionally route profile-path leaf strings through `boundedText` (larger cap) or add maxLength checks to `validate-profile.ts` when next extended. |
| I1 | INFO | No | Harness docstring says the deployed API "has no CORS policy"; precisely, it has the M0-T015 deny-all-by-default allowlist. Effective claim (no cross-origin allowed today) is correct and the follow-up decision is properly flagged. | fixture_api.py:38-43 | Wording fix at next harness touch. |
| I2 | INFO | No | D8/CORS deploy-blocking carry-forward remains open (real API: no configured origins, no `X-Correlation-ID` expose header). This task correctly did not resolve it — `services/**` verified untouched. | main.py:95-101; diff | Resolve via the reviewed CORS/proxy decision before any real cross-origin deployment (existing carry-forward, not a new defect). |

No CRITICAL, HIGH, or MEDIUM findings. No blocking defects.

## Verdict rationale

The hardened client meets every G5 requirement in scope: exact pair-matrix enforcement on raw state with the owner-directed 500+no_match regression structurally unreachable and e2e-proven against the recorded fixture; total validate-before-render on 200s with a doubly bounded problem list; bounded/token-allowlisted reflection at every error-path render point with zero dangerous sinks; no secrets, no storage APIs, no console logging; validated URL parameter handling with no reflection of raw input; user-initiated-only retries with abort/timeout cleanup; no CORS widening of the real API and no credentialed-CORS dependence; zero dependency changes. Residual findings are LOW/INFO and non-blocking, recorded above and in reviewer memory for the next re-review. Cross-tenant isolation, RLS, private storage, and upload controls are structurally out of scope for this frontend-only diff (no tenancy, storage, or upload surface exists yet; API remains INTERNAL/DEV behind B-001, and the internal banner is present on both screens — InternalBanner.tsx:6-15).

Per ADR-005 this report is returned to the orchestrator for verbatim preservation and ledger recording; no gate CLI or git writes were performed by this reviewer.

**G5: PASS**
