# M5-T060 security review — rostered wave reviewer (verbatim return)

Reviewer: security-reviewer (opus-4-8 xhigh per D-064), dispatched by the orchestrator at the
c314a29a submit seam, pinned to material d7d45e84. The packet's required gates are G0/G2/G3/G4;
this rostered security verdict is recorded as a wave report — any blocking finding would block
acceptance regardless. Recorded by the orchestrator; reviewer is read-only.

---

Verification complete. Working tree matches the frozen material d7d45e84 for all reviewed files, no tracked working-tree modifications to apps/web, and package.json/package-lock.json were not touched in the material commit (no new dependency).

---

VERDICT: PASS

# G-Security Gate Report — M5-T060 (Phase B3 slice 2, proposal editor UI)

## Pinned identity
- Reviewed head (HEAD): `c314a29a` (submit seam; adds only evidence-map, gate records, `state.json`, task file — no material file change).
- Frozen material: `d7d45e84` (`d7d45e84ae81e16da6325827e1aef28977944ebf`), 18 files.
- Verified via read-only plumbing: `git diff --stat d7d45e84 -- <reviewed files>` is empty (working tree == frozen material); `git status --porcelain apps/web/` is empty; `apps/web/package.json` and `apps/web/package-lock.json` are absent from the `d7d45e84` change set. No disjoint T062/T063 peer touched any reviewed path.
- Scope: security-only, read-only. No writes, no ledger/git mutation.

## Walkthrough (the eight judged surfaces)

1. Rendering safety — PASS. Every server-echoed string is bounded in the client before it leaves the transport module: `boundReport` in `apps/web/src/lib/proposal-checks-api.ts` runs `boundedText`/`boundedToken` over `check_id`, `family`, `label`, `unit`, `direction`, `outcome`, `could_not_check_reason`, `detail`, `semantic_gap`, `rule_id`, `coverage_status`, `provided_input_ids`, `scenario_label`, `proposal_id`, `outline_digest`, `unmapped_lot_facts`, `message`, `field`, correlation id. `ProposalCheckReport.tsx` renders all of these as React-escaped JSX text (ids also flow only into `data-testid` attributes, which React escapes). `bounded.ts` caps length and strips C0/C1 control chars; XSS defense proper is React auto-escaping (documented, accepted M2-T002 precedent). Grep across the full packet found zero `dangerouslySetInnerHTML`/`innerHTML`/`insertAdjacentHTML`/`document.write`/`eval`/`new Function`; a CI grep-proof test (`proposal-editor.test.tsx` L104-118) asserts no `dangerouslySetInnerHTML` in the six production/fixture files; the markup-echo render test (`proposal-check-report.test.tsx` L66-72) proves `<img src=x onerror=alert(1)>` renders as text with `container.querySelector("img")`/`("script")` both null. Markup-shaped id echo requirement met.

2. No cap-widening / no client retry loop — PASS. `validateDraft` (`proposal-draft.ts`) only fails closed against mirrored route caps (each mirror names its route constant; drift tests guard it) and never relaxes them; the server refusal remains authority. `fetchProposalCheck` is a single POST guarded by one `AbortController` + `setTimeout`; there is no retry/backoff loop. Re-checks are user-initiated (the "Run check" button, `ProposalEditor.runCheck`), and `proposalCheckOutcomeIsRecoverable` deliberately excludes `payload_too_large`, `validation_error`, and `feature_unavailable` from the "safe to retry" affordance, so a refused payload is never presented as auto-retryable.

3. Draft/variation ephemerality — PASS. Drafts and variations live in React `useState` plus a module-scoped integer counter (`variationSeq`); `ProposalVariations.tsx` is pure props. No `localStorage`/`indexedDB`/`document.cookie` anywhere in the packet; the only `sessionStorage` hits are a pre-existing confirmed-address helper inside `entry.test.tsx` (test-only, not proposal data). Ephemerality copy present ("Kept in this browser session only — not saved").

4. Fetch discipline — PASS. The client targets exactly `${apiBaseUrl()}/api/v1/proposal-checks` — a fixed constant path, no interpolated/user-controlled URL, no new external endpoint. No `credentials` option is set (default same-origin), consistent with `api.ts`/`scenario-api.ts`. `apiBaseUrl()` reads the publishable `NEXT_PUBLIC_API_BASE_URL`. The request body is caller-attested draft numbers plus a hard-coded provenance object; no secrets, no service-role key, no user email/PII.

5. No new dependency — PASS. All imports resolve to `@/...`, relative paths, or standard react/next/vitest/@testing-library/@playwright/`node:fs` (test-only). `package.json`/`package-lock.json` are in `forbidden_paths` and untouched in the material commit.

6. Fixtures contain no secrets — PASS. `proposal-check-fixtures.ts` and the e2e inline fixture carry only test data: a zero-hash placeholder `outline_digest`, ids `test-correlation-id`/`e2e-corr`, and deliberate XSS probe strings (`<script>alert(1)</script>`, `<img src=x onerror=alert(1)>`, `<b>W-S</b>`) that exist to prove text-rendering. No credentials, keys, or tokens.

7. fetchImpl cannot leak into production — PASS. `fetchImpl` is an optional prop/option defaulting to the global `fetch`. The production mount (`ArchitectEntry.tsx` L143) renders `<ProposalEditor bbl={bbl}/>` with no `fetchImpl`. The e2e uses Playwright `page.route` network interception (not injection); only unit/component tests pass `stubFetch` through the prop. Injection is test-support only.

8. Navigation/shell no URL-driven injection — PASS. `readWorkspaceView` (`navigation.ts`) allowlists the `view` param against `WORKSPACE_VIEWS`, falling back to `"overview"` for anything unknown; `bbl` is validated by `validateBblInput` before use. Both are rendered only as React-escaped text (`VIEW_LABELS[view]`, the bbl span) and used in a `switch`. The additive `"proposal"` view is reachable only inside the existing server-flag-gated `ArchitectEntry` tree (comment L183: "no client flag can open it"); no new flag, no new page/route.

## Findings

- F-1 (Informational, non-blocking): `boundedText` (`bounded.ts`) caps length and strips control characters but does not strip `<`/`>`; XSS safety therefore depends entirely on React's automatic text escaping and on no raw-HTML sink ever being introduced. This is the accepted repo pattern (M2-T002), is proven safe here by the markup-echo render test, and is backstopped by the CI grep-proof test. No action required for this packet; noted so the invariant ("never add a raw-HTML sink to a component consuming these strings") stays visible.
- F-2 (Informational, non-blocking): `fetchImpl` remains part of the production `ProposalEditor` public signature rather than being stripped for prod. Current mount does not pass it, and this mirrors the accepted `LookupOptions.fetchImpl` precedent, so risk is low. If a future caller ever wires it, that call must be treated as test-only.

## Required corrections
None. No critical, high, or medium security findings. The two informational notes are advisory and do not block acceptance.

## Security posture summary
The editor is a correctly-scoped client over the accepted, flag-gated, server-enforced T057/T061 route: it transports and bounds, computes no legal value, mirrors (never widens) the server caps, fails closed on every off-contract response (over-budget Content-Length, non-JSON, undocumented status/state pair), renders all reflected strings as escaped text, keeps drafts/variations ephemeral in memory, adds no dependency, leaks no credentials or secrets, and confines fetch injection to tests. Cross-tenant isolation, service-role secrecy, private storage, and upload controls are not in this client packet's surface (the server is the enforcement boundary, unchanged here). Verdict PASS.
