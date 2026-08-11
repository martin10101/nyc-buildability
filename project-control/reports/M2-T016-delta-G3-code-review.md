# G3 INDEPENDENT DELTA CODE REVIEW — M2-T016 orchestrator fix commits

> VERBATIM capture of the independent `code-reviewer` return (session 14, 2026-08-11), preserved by the
> orchestrator under `.claude/rules/project-control.md` report-preservation. Transport decoding only;
> no condensation, no editing. Verdict recorded as gate G3 = PASS with BLOCKING required corrections
> (F4, F10) per the gate-verdict semantics rule.

**Task:** M2-T016 (survey review UI + review-action API)
**Delta reviewed:** `d45f330..5a684fc` on `task/M2-T016-survey-review` (commits `80252d3`, `749f9dd`, `5a684fc`)
**Worktree inspected:** `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M2-T016-integrate` (HEAD = `5a684fcd7d1414fd59112cadfba983cc6423ac72`, clean)
**Reviewer:** independent of the producer (delta authored by the orchestrator; reviewed by a separate read-only agent)
**Scope:** 4 files, +97/-3 — two route files, `lib/surveyReview/api.ts`, `lib/surveyReview/__tests__/api.test.ts`. No other files touched; no dependency, migration, schema, or control-plane change.

**VERDICT: PASS** — with two required corrections (F4, F10). Both are evidence/coverage defects, not code defects. Every code change in the delta is correct, correctly motivated, and at the right layer. The diff was fully visible to me; nothing blocked the review.

## What I could not execute

No `node_modules` anywhere in the repo (verified: both `apps/web/node_modules` and `./node_modules` absent) and local npm installs are prohibited, so I could NOT run vitest, `tsc`, eslint, `next build`, or Playwright. I did not use `gh` (orchestrator-only), so I did not read CI logs directly. Consequences:

- The pre-fix vitest failure IS reproducible by inspection — the assertion at `apps/web/src/lib/surveyReview/__tests__/api.test.ts:160` is exactly the one the commit message quotes, and the old code provably produced `sevdocp13`. Claim verified without executing anything.
- The pre-fix Playwright failures for changes 2 and 3 could not be independently observed (Playwright never ran at `d45f330`). I verified their mechanisms structurally instead.
- **OPEN SUB-QUESTION (does not affect the verdict):** I could not determine which Next 15.5.21 internal mechanism produced the pre-fix 404 on the *dynamic* `[documentId]` route — build-time prerender, or full-route-cache retention of the first render. No build output was available. Either way the `force-dynamic` declaration is correct; this is a curiosity, not a risk.

---

## Change 1 — `80252d3`, `boundedEvidenceId` for `rejected_fact_ids`

**F1 — INFO (claim VERIFIED).** `apps/web/src/lib/bounded.ts:65` strips everything outside `[A-Za-z0-9._-]`, which includes `:`. Evidence ids are colon-delimited (`sev:doc:p1:3`, `api.test.ts:19-21`, produced by the fixtures). So `sev:doc:p1:3` -> `sevdocp13` is real, and the product consequence is real: `ConfirmDocumentPanel` matches returned ids against `document.facts` at `apps/web/src/components/survey-review/ConfirmDocumentPanel.tsx:40-41`, so a corrupted id falls through to rendering the raw token instead of the fact's label, and the jump-link at line 191 (`onSelectEvidence(id)`) selects nothing. Product defect, not a test artifact, as claimed.

**F2 — INFO (claim VERIFIED).** The helper at `apps/web/src/lib/surveyReview/api.ts:80-87` preserves each defensive property one-for-one against `boundedToken`: non-string -> `null` (line 84), hostile characters stripped (85), length bounded to 128 (85), empty -> `null` (86). The character class differs by exactly one character, `:`. I checked the widening for a security consequence — adding `:` makes a URL scheme expressible (`javascript:...`), but these ids never reach an `href`, `src`, or any URL: the only consumers are a React key, a `data-testid` attribute, a label lookup, and a selection callback (`ConfirmDocumentPanel.tsx:186-194`), all positions React escapes. No exploitable widening.

**F3 — INFO (claim VERIFIED; your reachability point CONFIRMED and it strengthens the case).** I reached `ConfirmDocumentPanel.tsx:41` and `:194` independently — `document.facts.find(f => f.evidence_id === id)?.display_label ?? id` printed the unmatched id verbatim, so the `?? String(id)` fallback was a live reflection sink, not a theoretical one. Two refinements to add to your reading: (a) it is a text node, so React escapes it — no XSS, the harm is a garbage/hostile string shown to a reviewer inside a legal-review surface, plus an unbounded length (`String(id)` applied no cap at all); (b) it was worse than the commit message says, because `String(id)` also coerced *non-strings*, so an object entry rendered as `[object Object]`. Removing it is a real hardening.

**F4 — REQUIRED-CORRECTION. The drop behavior has no test, and the test that claims to cover it does not.** `api.test.ts:236-256` is titled "drops unsanitizable entries from rejectedFactIds instead of emitting them raw", but it drives the mock backend, which only ever emits ids from its own fixtures (`apps/web/src/test-support/survey-review/mockBackend.ts:261` maps `f.evidence_id`). Those always sanitize cleanly, so `boundedEvidenceId` never returns `null` and the `.filter(...)` never removes anything. Revert only the drop half (restore `?? String(id)`, keep `boundedEvidenceId`) and this test stays green. Its one substantive assertion, `toContain(NORTH)` at line 252, duplicates the pre-existing assertion at line 160; the loop at 253-255 asserts sanitizer idempotency over already-clean input, which is vacuous here. Given F3 — the fallback was reachable and reflected to a reviewer — the unpinned half is the security-relevant half, under a test name that asserts otherwise. That is misleading gate evidence, hence required rather than minor.

The file already has the pattern needed (`createHttpSurveyReviewClient()` + stubbed `fetchImpl`, `api.test.ts:51-59`). One test pins both halves:

```ts
it("keeps sanitizable ids and drops the rest", async () => {
  const out = await createHttpSurveyReviewClient().confirmDocument(
    { documentDigest: "sha256:x" },
    { fetchImpl: async () => new Response(JSON.stringify({
        reject_code: "confirmation_rejected",
        message: "blocked",
        detail: { rejected_fact_ids: ["sev:doc:p1:3", "<<<>>>", 42, { a: 1 }] },
      }), { status: 422, headers: { "Content-Type": "application/json" } }) },
  );
  expect(out.kind).toBe("error");
  if (out.kind !== "error") return;
  expect(out.rejectedFactIds).toEqual(["sev:doc:p1:3"]);
});
```

Under the pre-delta code that yields `["sevdocp13", "<<<>>>", "42", "[object Object]"]` — it fails on both the charset and the raw-fallback regressions.

**F5 — MINOR. Dropping is right; dropping *silently* is not, quite.** Direct answer to your question: dropping beats a placeholder and is unambiguously better than the old raw fallback — keep it. But the count should surface. The reviewer is never misled into thinking confirmation succeeded (the refusal copy still renders at `ConfirmDocumentPanel.tsx:179-183`), so exposure is limited to a shorter jump-link list than the server reported, and in practice the backend's id scheme always sanitizes. Still, the standing rule here is that nothing material is dropped silently. Suggested: record `rejectedFactIdsUnrenderable: rejected.length - error.rejectedFactIds.length` in `decodeError` and have the panel append "...and N further blocking facts whose identifiers could not be displayed." Not blocking.

**F6 — INFO (claim VERIFIED).** `boundedToken` is still used in `api.ts` at line 171 (correlation id) and line 406 (`target_bbl`), so the import at line 28 is still needed. Leaving those on the narrow charset is correct and lossless — verified against the backend rather than assumed: correlation ids are `uuid.uuid4().hex` (`services/api/app/api/v1/properties.py:314`, `services/api/app/api/v1/rule_evaluation.py:147`), pure hex, no colon; a BBL is ten digits. Not widening the shared helper is the right call.

**F7 — MINOR (suggestion).** Exporting `boundedEvidenceId` only for the test is acceptable — the module already exports `apiBaseUrl` (`api.ts:111`) and `DEFAULT_TIMEOUT_MS` (55). If F4 lands as suggested the export is no longer needed (the test drives the client), and I'd mildly prefer the helper next to `boundedToken` in `apps/web/src/lib/bounded.ts` so charset policy lives in one reviewable place. Either home is defensible.

## Change 2 — `749f9dd`, `force-dynamic` on both survey-review routes

**F8 — INFO (claim VERIFIED structurally).** The root cause holds up. `.github/workflows/ci.yml:97-99` runs `npm run build` with a job env of only `NEXT_TELEMETRY_DISABLED` (lines 63-64) — `INTERNAL_SURVEY_REVIEW_ENABLED` is set ONLY on the `npm run start` webServer in `apps/web/playwright.config.ts:60-64`. So the flag is genuinely unset at build and set at serve, exactly the split described. The `/dashboard` precedent is real (`apps/web/src/app/dashboard/page.tsx:10`) and, importantly, *exercised*: `apps/web/e2e/dashboard.spec.ts:11-12` navigates to `/dashboard` in this same build-then-start harness and passes, which demonstrates empirically in this repo that `force-dynamic` is what makes a non-public runtime flag work. Both survey routes now match (`survey/review/page.tsx:17`, `survey/review/[documentId]/page.tsx:17`).

**F9 — INFO (security posture UNCHANGED, marginally improved).** All three sub-claims verified. Gate still fail-safe OFF (`apps/web/src/lib/surveyReview/config.ts:11-17`: non-string -> `false`, allowlist of true tokens). Flag has no `NEXT_PUBLIC_` prefix, and `surveyReviewEnabled` is imported by nothing except the two Server Components and its own unit test — I grepped every importer in `src/`; no client-component reference, so nothing inlines it into the browser bundle. `force-dynamic` changes WHEN the gate runs, never WHETHER: flag unset still hits `notFound()` at `page.tsx:27` / `[documentId]/page.tsx:32`. Slightly safer than before, since a cached route could otherwise hold a stale "enabled" decision after the flag is switched off at runtime.

**F10 — REQUIRED-CORRECTION. The inbox route's `force-dynamic` has no executed evidence.** All seven survey-review e2e specs navigate to `/survey/review/${encodeURIComponent(digest)}`; none visits the bare inbox `/survey/review` (verified across `survey-review-journey.spec.ts:23,73`, `survey-review-authorization.spec.ts:19,33`, `survey-review-recovery-a11y.spec.ts:17,30,47`). So the "all 7 specs 404'd" evidence pertains solely to the `[documentId]` route, and the change to `apps/web/src/app/survey/review/page.tsx:17` — the route that is UNAMBIGUOUSLY statically prerenderable, no dynamic segment, no dynamic API — is justified purely by analogy and exercised by nothing. That is the wrong way round for a security gate. Add one spec:

```ts
test("the review inbox is reachable when the runtime flag is set", async ({ page }) => {
  await installSurveyReviewMock(page);
  await page.goto("/survey/review");
  await expect(page.getByTestId("internal-banner")).toBeVisible();
});
```

Without `force-dynamic` on that file this fails against a production build; with it, it passes. It also closes an unrelated hole — the inbox screen has no e2e at all today.

**F11 — MINOR (caching, for the record).** `force-dynamic` opts both routes out of the full route cache, so every request re-renders the server shell. Negligible: the pages render a banner plus a client provider and do no server data fetching, and document data is already fetched client-side with `cache: "no-store"` (`api.ts:157`). No ISR/revalidation behavior affected.

## Change 3 — `5a684fc`, decode the route digest param

**F12 — INFO (claim VERIFIED against the harness).** Mechanism confirmed end to end. The client builds `${documentsBase()}/${encodeURIComponent(documentDigest)}/review` (`api.ts:347`); the mock splits the path and decodes each segment exactly once (`mockBackend.ts:159`); the store is keyed on the literal `sha256:<hex>` form. An already-encoded param therefore yields `sha256%3A...` after the single decode, matching no key, returning the 404 body at `mockBackend.ts:170` — verbatim the string the commit reports from the Playwright artifact. The mock is faithful to production here: Starlette/FastAPI also decodes a path parameter exactly once, so the fix addresses the real contract, not a harness quirk.

**F13 — INFO (double-decode hazard assessed, contained).** `+` is a non-issue: `decodeURIComponent` does not translate `+` to space (that is query-string semantics), so nothing is lost. `%25` is the real case: if Next already decoded, a crafted `...%2525...` or `...%252F...` decodes a second time here, producing a string the user never typed, possibly containing `/`, `?`, `#`. Contained, because every consumer re-encodes through `encodeURIComponent` (`api.ts:347, 474, 479, 494, 499, 505, 510`), which escapes `/ ? # % :` — the digest can never break out of its path segment. No traversal, no SSRF, no injected query; worst case is a 404 for a nonexistent digest. Caveat: that containment is a whole-file invariant enforced only by convention. The first future consumer that interpolates a digest into a URL without encoding turns this into a path-injection vector — the strongest argument for F14.

**F14 — MINOR (recommended). Validate the digest shape at the route.** `if (!/^sha256:[0-9a-f]{64}$/.test(documentDigest)) notFound();` after the decode would enforce the documented contract at the boundary, make F13 moot, and stop garbage digests reaching the API. Not required, because exposure today is small: the raw param is never reflected into the DOM (checked — `SurveyReviewScreen` passes it only to client calls and renders `document.document_digest` from the *response* at line 337; `ReadFailureState` renders only bounded copy from `errorCopy`), and `encodeURIComponent` bounds the request. It is the correction I would most like to see land.

**F15 — INFO. `notFound()` is the right failure mode.** A malformed percent-sequence is not a document, and on an internal, flag-gated, unauthenticated-by-design route, 404 is the correct information posture: identical to the flag-off response, so a probe learns nothing about whether the feature exists. A typed validation error would add a code path and a user-visible state for an input no legitimate navigation can produce. Endorsed as written.

**F16 — MINOR. `let documentDigest = documentId;` is correct but representable-wrong.** At `[documentId]/page.tsx:40-45` the un-decoded value can never be used: `decodeURIComponent` throws before the assignment, and `notFound()` — typed `(): never` in `next/navigation` — throws out of the catch. I confirmed there is no code between the catch and the return. But the initializer exists only to satisfy the compiler and makes a wrong state representable. The stricter form makes the compiler prove it:

```ts
let documentDigest: string;
try {
  documentDigest = decodeURIComponent(documentId);
} catch {
  notFound();
}
```

`notFound()` returning `never` makes the end of the catch unreachable, so TS still treats `documentDigest` as definitely assigned — this compiles, and any future edit adding a fallback path becomes a type error instead of a silent regression. Not blocking.

**F17 — INFO. All three fixes are at the right layer.** Change 3 belongs in the route: that is where transport encoding ends and the domain digest begins. In the client it would be wrong (the client's `encodeURIComponent` is correct and must stay); in the mock or the e2e helper it would have hidden a real production defect behind test-only leniency — the commit is right that the jsdom component tests missed this because they hand `SurveyReviewScreen` a raw digest and bypass the param round-trip. Change 1 belongs in `decodeError`, the single decode seam. Change 2 belongs in the route files. There IS a shallow contract gap underneath: `documentDigest` travels as a bare `string` with its shape documented only in comments (`api.ts:10`, `[documentId]/page.tsx:22-23`), which is how the encoding responsibility got lost between route, client, and backend. F14 is the cheap mitigation; a branded `DocumentDigest` type would be the thorough one, out of scope here.

## F18 — Your explicit question: is e2e-only pinning adequate G3 evidence for fixes 2 and 3?

**Adequate. Not a required correction.** Three reasons, then one caveat.

1. A unit test could not have caught either defect, and demanding one would be demanding the wrong test. Both are integration-boundary bugs: fix 2 lives in the interaction between `next build`, `next start`, and the process env; fix 3 lives in the route/client/backend encoding round-trip. Your own commit message makes the point correctly — the jsdom component tests missed the digest bug precisely because they inject a raw digest and bypass the param round-trip. Adding a unit test that asserts `export const dynamic === "force-dynamic"` would pin the string, not the behavior, and would pass even if Next changed its semantics.
2. The e2e specs genuinely exercise the production configuration: a real `next build` with the flag unset, `next start` with it set, and a real navigation to a percent-encoded digest. That is a stronger proof than any unit test of the same code.
3. The regressions are actually caught. Revert either fix and the suite goes red — that is the property G3 needs.

**Caveat (MINOR, not required):** the pinning is *incidental*. No spec is named or written to assert "the runtime flag governs this route" or "an encoded digest resolves"; the fixes are pinned as a side effect of seven journey specs. If someone reverts `force-dynamic` later, the signal is seven unrelated-looking journey failures rather than a targeted diagnostic, and the next engineer pays the debugging cost you just paid. Cheap mitigations, either one: a one-line comment in each route file noting that the e2e suite is what proves the flag is live, or make the F10 spec explicitly named for the flag so at least one test failure names the cause.

**This is exactly why F10 is required and F18 is not.** The required correction is not "add unit tests for fixes 2 and 3" — it is "the inbox route has NO test at any level, e2e included." Fix that gap and the e2e-only strategy is sound as it stands.

## Which test pins which fix

| Fix | Pinned by | Fails on revert? |
|---|---|---|
| 1 — colon charset | `api.test.ts:160` (pre-existing) + table at `api.test.ts:217-230` | Yes, both. Line 160 is what CI reported. |
| 1 — drop instead of `String(id)` | nothing | **No.** See F4. |
| 2 — force-dynamic, `[documentId]` | all 7 survey-review e2e specs | Yes, per the reported pre-fix run |
| 2 — force-dynamic, inbox | nothing | **No.** See F10. |
| 3 — decode digest param | all 7 specs, via `encodeURIComponent` in the helpers + single decode at `mockBackend.ts:159` | Yes |

## Required corrections (record as PASS with blocking corrections)

1. **F4** — replace or supplement `api.test.ts:236-256` with a test that exercises the drop path (recipe above), so the raw-fallback removal is pinned and the test name matches what it verifies.
2. **F10** — add one Playwright spec that loads `/survey/review` (the inbox), so `force-dynamic` on the statically-prerenderable route has executed evidence.

Recommended, not required: F14 (validate `^sha256:[0-9a-f]{64}$`), F5 (surface a dropped-id count), F16 (definite-assignment form), F7 (co-locate the sanitizer), F18 caveat (make the e2e coupling explicit).

## Note on CI evidence

Green CI at `5a684fc` on the required checks, including `web-e2e` (277 vitest + 73 Playwright), is consistent with everything I verified by inspection and is the only executable evidence available for changes 2 and 3. I did not verify the run myself. The red `web-dependency-security` check (`nanoid`, GHSA-2v37-7h3g-55p8) is outside this delta — no dependency or lockfile is touched — so it does not affect this G3 verdict. Whether a red dependency-security check may be treated as non-required for merge is a policy call for you, not a G3 finding; I note only that the standing policy describes that gate as fail-closed with no agent waiver, so the tension is worth resolving explicitly rather than implicitly.
