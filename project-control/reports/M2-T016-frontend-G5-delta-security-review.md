# G5 SECURITY GATE REPORT — M2-T016 (final acceptance head)

Saved verbatim by the orchestrator (transport entity-decoding only). Reviewer: `security-reviewer`
(independent, read-only; ≠ producers frontend-engineer + backend-engineer). This is the outstanding
frontend G5 delta at the final acceptance head; the backend G5 PASS (`M2-T016-backend-G5-security-review.md`,
`-backend-G5-delta-review.md`) carries forward unchanged.

## VERDICT: PASS

**Gate:** G5 (security review) — DELTA at final acceptance head
**Task:** M2-T016 (survey-review screen + backend review actions)
**Reviewed SHA:** `65adc7c3e9033a41cbdf526ccdffceb50940979d` (confirmed: `git rev-parse HEAD` == 65adc7c)
**Reviewer role:** Independent security-reviewer (NOT the producer; producers were frontend-engineer + backend-engineer)
**Method:** Source reading at HEAD + git range diffs. The worktree has no `node_modules` and local npm is prohibited (CLAUDE.md #14, dependency policy), so I did **not** execute vitest/Playwright/tsc locally. I relied on reading the source and the added regression tests, plus the producer's CI evidence (G3/G4 reports on file). This is stated plainly per the gate protocol; no defect below depends on an unrun command.

---

## 1. Backend-unchanged proof (backend G5 PASS carries forward)

The backend slice was already G5-reviewed PASS by an independent reviewer at `57d8574`
(reports on file: `project-control/reports/M2-T016-backend-G5-security-review.md`,
`…-backend-G5-delta-review.md`). I proved those files are unchanged at the accept head:

```
$ git diff --stat 57d8574 65adc7c -- services/api/app/documents/
(empty)
$ git diff 57d8574 65adc7c -- .../review_actions.py .../review_authz.py .../review_events.py | wc -l
0        # byte-identical
```

The three backend files (`review_actions.py`, `review_authz.py`, `review_events.py`) are byte-identical between the prior G5 PASS SHA and the accept head. **The backend G5 PASS carries forward unmodified.** No backend re-review was required and none of the backend authority/RLS/state-machine controls changed.

## 2. Frontend delta in scope

```
$ git diff --stat d45f330 65adc7c -- apps/web/src apps/web/e2e
 apps/web/e2e/survey-review-inbox.spec.ts                    | 29 +   (new)
 apps/web/src/app/survey/review/[documentId]/page.tsx        | 26 +
 apps/web/src/app/survey/review/page.tsx                     |  6 +
 apps/web/src/lib/surveyReview/__tests__/api.test.ts         | 52 +
 apps/web/src/lib/surveyReview/api.ts                        | 26 +
```

Two production source files (`api.ts`, `[documentId]/page.tsx`), one `dynamic` export added to the inbox `page.tsx`, plus a unit-test and an e2e-test. No new dependencies, no lockfile change, no backend change.

---

## 3. Frontend security findings (item-by-item)

### F-1 — Evidence-id sanitizer `boundedEvidenceId` (api.ts:80-87) — PASS
`boundedEvidenceId(value)` rejects non-strings (`typeof value !== "string" → null`), strips every character outside `[A-Za-z0-9._:-]` (colon preserved so colon-delimited ids like `sev:doc:p1:3` survive), bounds to 128 chars, and returns `null` for an empty result. The character class is linear (no ReDoS); `-` is trailing so it is a literal hyphen, not a range. `<script>` collapses to `script` (angle brackets stripped), matching the test at api.test.ts:259. Correct, tight, defensive.

### F-2 — Hostile `rejected_fact_ids` cannot be reflected raw; DROP not coerce (api.ts:210-219) — PASS
The old code was `rejected.map((id) => boundedToken(id, 128) ?? String(id))` — the `?? String(id)` fallback reflected the **raw** hostile value for exactly the inputs the sanitizer exists to bound. The fix maps through `boundedEvidenceId` and `.filter((id): id is string => id !== null)`, so an entry that sanitizes to empty (`"<<<>>>"`, `""`), a number, an object, or `null` is **dropped**, never reflected. A 422/confirmation-blocked response with hostile `rejected_fact_ids` therefore can never reach the DOM as a raw value. The regression test (api.test.ts "keeps sanitizable ids and drops the rest") stubs a 422 body of `[NORTH, "<<<>>>", 42, {a:1}, "sev:doc:<script>:2"]` and asserts the result is exactly `[NORTH, "sev:doc:script:2"]` — both the survive-half and the drop-half are pinned.

### F-3 — Dropping rejected ids cannot flip BLOCKED → OFFERED/all-clear — PASS (key security property)
`rejectedFactIds` lives only on the **error** outcome of a *confirm attempt* (`ReviewActionError`, types.ts:293); it is never an input to the confirm-offer decision. The offer decision is `canOfferConfirm(document)` (model.ts:88), which is a pure function of `capabilities.can_confirm_document && CONFIRMABLE_SOURCE_STATES.has(state) && confirm_precondition_met` — none of which is derived from `rejectedFactIds`. In `ConfirmDocumentPanel.handleConfirm` (ConfirmDocumentPanel.tsx:43-55), `confirmError` is set **unconditionally** on the error path (lines 50-51) before `rejectedFactIds` is even consulted; so even if *every* rejected id were dropped, the reviewer still sees the "could not be confirmed" alert and the confirm was refused by the backend (no re-read to a settled state on `confirmation_rejected`). Dropping malformed ids only trims the per-fact remediation list — a UX degradation for a hostile-server case, never a security downgrade. **No forged/auto-cleared confirmation is reachable.**

### F-4 — `blocking_fact_ids` is NOT drop-sanitized (masking check) — PASS
As the packet required, `blocking_fact_ids` is passed through unmodified at mapReviewDocument (api.ts:328, `Array.isArray(...) ? (... as string[]) : []`) — it is **not** run through `boundedEvidenceId`/`filter`, so a malformed entry cannot be silently dropped. Consumers use it two ways, both safe against masking:
- `dominantAction` (model.ts:139) tests `document.blocking_fact_ids.length > 0` to emit "Rejected facts block confirmation…" — a malformed entry still counts, so a real block is never hidden.
- `factsBlockingConfirmation` (model.ts:75-78) intersects the id set with real `fact.evidence_id`s, so only ids that correspond to a validated, rendered fact appear in the blocking list — the intersection is what protects the DOM, while the raw length preserves the honest block signal. Correct division of concerns.

### F-5 — Rendering of ids to the DOM (ConfirmDocumentPanel.tsx) — PASS
`rejectedFactIds` (now sanitized) renders as React `key`, `data-testid={`rejected-blocking-${id}`}`, `onSelectEvidence(id)` (local selection state only), and `labelFor(id)` text (falls back to the sanitized `id`). `blocking` facts render `f.evidence_id` (already `String()`-mapped from a validated non-empty string) and `f.display_label`. All are React-escaped text/attributes; the app uses no `dangerouslySetInnerHTML` (grep confirms zero occurrences in `apps/web/src`). No id feeds a URL, filesystem path, or HTML sink. No XSS.

### F-6 — Read-view capability/precondition consumed from server, never client-recomputed — PASS
`confirm_precondition_met` is read strictly (`raw.confirm_precondition_met === true`, api.ts:327 — defaults false when absent/malformed). Capabilities come from `mapPrincipal` (server principal); absent/malformed principal falls back to `SERVER_ENFORCED_PRINCIPAL` with `capabilities_known:false` (AWAITING-BACKEND surfaces actions but the server's typed refusal is the authority). The client performs no writes of its own — every mutation is a server POST and the settled state is RE-READ from the server (`reReadAsAction`). Client is never the source of authority.

### F-7 — Digest boundary validation in `[documentId]/page.tsx` — PASS
`export const dynamic = "force-dynamic"` is added so `surveyReviewEnabled()` is evaluated at request time, not baked at build (correct fail-safe behavior). The param is decoded **once** (`decodeURIComponent(documentId)` in a try; on `URIError` the `catch` calls `notFound()` → fail-closed, no throw leaks). It is then validated against `^sha256:[0-9a-f]{64}$` before use; anything else → `notFound()`. This means: (a) no arbitrary decoded string is forwarded to the client/backend; (b) no path-traversal or SSRF into the backend request URL is possible — the digest is lowercase-hex only, and the client additionally `encodeURIComponent`s it (single-decode/single-encode, no double-decode gap). `notFound()` keeps the information posture identical to the flag-off 404 (no typed-error oracle). `notFound()`'s `never` return satisfies definite-assignment of `documentDigest`.

### F-8 — Feature flag stays fail-safe OFF; `force-dynamic` leaks nothing — PASS
`surveyReviewEnabled()` (config.ts) reads `INTERNAL_SURVEY_REVIEW_ENABLED` fresh each call, returns `false` for any non-string or non-true-token value (fail-safe OFF), and is **never** `NEXT_PUBLIC_`-prefixed, so it is never inlined into the client bundle. `force-dynamic` makes the Server Component re-evaluate the flag per request; it does not expose the flag value to the browser (evaluation is server-side; the route either renders or 404s). The new e2e spec `survey-review-inbox.spec.ts` is a regression guard proving the runtime flag governs the statically-prerenderable inbox route: CI **builds with the flag unset** and **serves `npm run start` with `INTERNAL_SURVEY_REVIEW_ENABLED:"1"`** (playwright.config.ts webServer `env`), so merely reaching the inbox proves the 404 was not baked at build. This strengthens, not weakens, the internal-only gate.

---

## 4. Standard G5 questions

- **Injection / adversarial input handling:** PASS. Sanitizer bounds charset+length and drops unsanitizable ids; digest route validated to strict hex; React escapes all reflected text; no `dangerouslySetInnerHTML`; no id reaches a URL/path/HTML sink; regex is linear (no ReDoS).
- **No forged confirmation / no auto-"verified":** PASS. Offer decision consumes server `confirm_precondition_met` + server capabilities, never client-recomputed; client does no writes and re-reads server state; `validate.ts` rejects any `confirmation_state` outside {unconfirmed, confirmed, rejected} (a forged "verified" → `validation_failure` → nothing rendered).
- **Principal integrity (client never the authority):** PASS. Capabilities from server principal; AWAITING-BACKEND default surfaces the server refusal honestly; backend re-enforces every action (unchanged, carried-forward G5).
- **Immutability / provenance not weakened:** PASS. Evidence ids preserved intact (the whole point of the colon-preserving sanitizer vs. the old `boundedToken` flatten); `blocking_fact_ids` preserved un-dropped.
- **Audit / downstream honesty (blocked/provisional never silently cleared):** PASS (F-3, F-4). Dropping malformed rejected ids trims a remediation list only; the generic error, the read-view block state, and `dominantAction`'s length-based block signal all remain.
- **Secrets / logging:** PASS. No service-role key, no secret, no `Authorization`/`Bearer`, no `console.*` in the survey-review surface. Only `NEXT_PUBLIC_API_BASE_URL` (public by design) and the non-public **server-only** flag are referenced.
- **Dependency / exposure:** PASS. Delta adds source + tests only — no new package, no lockfile change. `force-dynamic` does not inline the flag; flag never `NEXT_PUBLIC_`.

---

## 5. Non-blocking advisories

- **(Non-blocking, pre-existing, out of delta)** The AWAITING-BACKEND `SERVER_ENFORCED_PRINCIPAL` shows all actions enabled with `capabilities_known:false`. This predates this delta and is safe because the backend re-enforces every action and the confirm offer still requires `confirm_precondition_met`. No change requested; noted for context only. (Matches human-journey J1 follow-up — bind the capability surface to the B-001 route/read-model task.)
- **(Non-blocking, informational)** I could not execute the vitest/Playwright suites locally (no `node_modules`; local npm prohibited). The security properties above were verified by reading the source and the added regression tests, which encode exactly the DROP-path and force-dynamic-flag behaviors; the producer's G3/G4 CI evidence is on file (`M2-T016-G4-integration.md`, `M2-T016-frontend-*`). If the orchestrator wants belt-and-suspenders, capture CI output of `apps/web` vitest (`boundedEvidenceId` suite) and the `survey-review-inbox` Playwright spec — neither is required to reach this verdict.

---

## Conclusion

The backend slice is byte-identical to its prior independent G5 PASS and carries forward. The frontend delta hardens the security posture: the evidence-id sanitizer preserves legitimate colon-delimited ids while dropping (not coercing) hostile/malformed ones, hostile `rejected_fact_ids` can never be reflected raw and can never flip a BLOCKED confirmation into an all-clear, `blocking_fact_ids` is deliberately left un-dropped so real blocks are never masked, the digest route validates and fails closed, and the internal-only feature flag remains fail-safe OFF and server-only under `force-dynamic`. No critical/high/medium/low security defect found.

**VERDICT: PASS**
