# M5-T070 — security review (VERBATIM, joined transmission)

TRANSMISSION HISTORY (orchestrator note, not reviewer text): delivered across six
transmissions on 2026-09-23 (05:42:34Z head; 05:45:48Z F1 continuation — that resume's own
stream then died mid-delivery on a provider safeguards error; 05:47:08Z the long resume
carrying the F1 remainder + F2 + most of F3, joined at "with the reason sil(ently)"; a
condensed F1-remediation/F2 micro-chunk at 05:47:44Z, consistent with the fuller text and
not duplicated below; 05:48:12Z F3-tail + F4; 05:48:26Z F5-F7 + closing + END-OF-REPORT).
Joins are verbatim at the stated cut phrases. The reviewer's own text follows, unedited.

---

# G5 SECURITY REVIEW — M5-T070 (Preliminary development limits panel)

**VERDICT: PASS** (no blocking findings; 1 medium and 6 low/advisory findings, all recorded below with exact reproduction and remediation)

Reviewer: security-reviewer (read-only). Repo `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch `candidate/D-024-mrl-option-b`, HEAD `c1e3efc3cd1d67c3a7e4982ea63dd1f638e84bc4`.

## Part 1 — Identity verification

I verified the pinned identity myself rather than accepting the dispatch prose. All twelve packet files are byte-identical from `395d6727` to the current head, by blob SHA:

| File | blob SHA (identical at both) |
|---|---|
| `apps/web/src/lib/architect/max-envelope-api.ts` | `06a2df29aa407eba6fe35f2c289253899ee9ced4` |
| `apps/web/src/components/architect/MaxEnvelopePanel.tsx` | `b3e8fc1ace06ff3f28dc9394ce5b895adac32fbb` |
| `apps/web/src/components/architect/ArchitectEntry.tsx` | `2479ec73f67794bd752a492791524e9965525ab3` |
| `apps/web/src/components/architect/ProposalEditor.tsx` | `66798eba711f01389c6b840be2abc69c33ed213b` |
| `apps/web/src/lib/architect/proposal-draft.ts` | `59864e24f5284bd70e4487a54d2ac31b015be9ef` |
| `apps/web/e2e/proposal-editor.spec.ts` | `0f2eb2a4f1e4caef96d763a7e53bfa65fa6f6f0a` |
| `.../__tests__/max-envelope-panel.test.tsx` | `b98e5238fa341e9fe104725a8f04749080b6944f` |
| `.../__tests__/max-envelope-api.test.ts` | `5eeb013d5ad255cef39ba87b76c0e67ceb5582c3` |
| `.../__tests__/entry.test.tsx` | `f80fd5685e881aaef7b928585068a5cb6ee39728` |
| `.../__tests__/proposal-editor.test.tsx` | `8c5b807aba932ce4227c83119c062acd75be581f` |
| `.../__tests__/proposal-draft.test.ts` | `da7352089185ec17cc9648636db6fb357fffce58` |
| `project-control/reports/M5-T070-producer-report.md` | `7e6d20b10097cba5baee0a7683ce2162b087dcf3` |

Material commits `51ffc5cb` (10 files), `075e9149` (3 files), `0625c19b` (8 files) touch only packet paths plus the orchestrator-owned `docs/DISCOVERY_BACKLOG.md` and `project-control/reports/M5-T070-evidence-map.json`. `services/api/` is untouched by all three — the route stays unmounted, as claimed. I confirmed `apps/web/src/lib/architect/development-limits.ts` (which contains a `location.hash` read and would otherwise be worth reviewing) is **not** touched by this packet; it last changed at `7d02eddc` (M5-T058) and is out of scope.

I did not run `npm`/`node` (thin-client rule), so every claim below is from source reading plus the CI evidence pinned in the dispatch. Where a defect needs execution to demonstrate, I give the exact test recipe rather than asserting an observed result.

## Part 2 — Findings

### F1 — MEDIUM (advisory for this packet; **blocking for the mount packet**): a server-supplied string is used as an object index key, so the prototype chain can return a non-string into a `string`-typed function

`apps/web/src/components/architect/MaxEnvelopePanel.tsx:56-66`:

```ts
const GAP_REASON_COPY: Record<string, string> = {
  no_applicable_rule: "no applicable rule was found for this dimension",
  allowance_unresolved: "the governing allowance could not be resolved",
  family_unsupported: "this rule family is not supported by the engine yet",
  non_commensurable_with_massing: "the rule does not translate to this massing dimension",
};

function gapReasonCopy(token: string | null): string {
  if (token === null || token === "") return "the reason was not stated";
  return GAP_REASON_COPY[token] ?? token;
}
```

`GAP_REASON_COPY` is an object literal, so it inherits from `Object.prototype`. `token` is the server's `gap_reason`, carried through `stringOrNull(record.gap_reason, 64)` — bounded in length and stripped of control characters, but its *value* is unconstrained. For the inherited keys, the lookup is never `undefined`, so `?? token` never falls through and a non-string escapes a function declared to return `string`:

- `gap_reason: "__proto__"` → returns `Object.prototype` (an object). Rendered at line 85 as a React child, React 19 throws `Objects are not valid as a React child`. The architect surface is under the `/property` route segment, which has an error boundary at `apps/web/src/app/property/error.tsx`, so the throw replaces the **entire property page** — including the accepted proposal editor the packet promises stays intact. That directly contradicts AS-6's "never a dead surface" degradation guarantee.
- `gap_reason: "constructor"` (also `"toString"`, `"valueOf"`, `"hasOwnProperty"`, `"isPrototypeOf"`, `"propertyIsEnumerable"`, `"toLocaleString"`) → returns a function. React treats a function child as invalid, logs an error, and renders nothing — so the row reads `Could not check — ` with the reason silently missing. That is an honesty failure on the exact surface the D-083 gap rule governs.

Why both gates missed it: `apps/web/tsconfig.json` sets `"strict": true` but **not** `noUncheckedIndexedAccess`, so `GAP_REASON_COPY[token]` is typed `string` and TypeScript sees nothing wrong. And the copy map was introduced by the `[ORCH-CORRECTED per G3-F3/G4-F3]` correction in `0625c19b` — after the wave-1 reviews — with no test for an unrecognized token. The G4 delta endorsed "the fail-honest raw-token fallback" as correct behavior, but that fallback is **untested**: `max-envelope-panel.test.tsx` exercises only `"allowance_unresolved"` and `null` (verified by grep; the only `gap_reason` literals in the file are at lines 34 and 56).

Why this is not blocking here: the payload cannot arrive today. `POST /api/v1/max-envelope` is unmounted, so in production the fetch returns a generic 404 and classifies as `feature_unavailable`; a 200 envelope — the only thing that can carry a `gap_reason` — is unreachable. The defect is latent and ships in the bundle, and becomes live the moment the mount packet lands.

Reproduction (unit level, in `apps/web/src/components/architect/__tests__/max-envelope-panel.test.tsx`): render the panel with a stub whose envelope body sets `dimensions[1].gap_reason = "__proto__"` (everything else unchanged from `gapDimension()`), and assert `screen.getByTestId("envelope-gap-max_height_ft")` has text content `__proto__`. Today the render throws instead. Repeat with `"constructor"` and assert the token renders verbatim.

Remediation (one line, plus the two tests above):

```ts
return Object.prototype.hasOwnProperty.call(GAP_REASON_COPY, token)
  ? GAP_REASON_COPY[token]
  : token;
```

Equivalent alternatives: build the map with `Object.create(null)`, or use a `Map<string, string>` with `.get(token) ?? token`. I recommend the `hasOwnProperty.call` form over `Object.hasOwn` because `tsconfig` targets ES2017 (`lib` includes `esnext`, so `Object.hasOwn` would type-check but is a newer runtime API than the rest of this file assumes). Enabling `noUncheckedIndexedAccess` app-wide would prevent the whole class, but that is a separate, larger change and I am not recommending it inside this packet.

## Part 2b — F2 through F4

### F2 — LOW (advisory): the byte ceiling trusts a declared Content-Length; the body actually read is unbounded

`max-envelope-api.ts:443-459`. The client requires `Content-Length` to be a plain digit string within `MAX_RESPONSE_BYTES` (512,000) and fails closed to `unexpected_response` on absent, blank, non-numeric, or over-budget — then calls `response.json()`, which reads however many bytes actually arrive. A server declaring `Content-Length: 100` while streaming 50 MB would be fully parsed and walked. This is identical to the accepted `outline-bridge-api.ts` precedent (lines 392-401, byte-for-byte the same logic and comment), so it is a consistent, reviewed posture rather than a regression, and the threat requires a compromised first-party same-origin API. Noting it so the pattern is not mistaken for a hard byte bound. A true bound would need `response.body.getReader()` with an accumulating byte counter; I am not recommending that change here.

### F3 — LOW (advisory): no element-count bounds on the envelope's arrays

`boundEnvelope` caps every *string* but nothing caps how *many* items arrive: `dimensions` (unbounded array, each rendering a `<li>`), `out_competed_rule_ids`, `rule_citations`, `candidate_notes`, and the candidate's `vertices`/`levels`/`exterior_walls`. A 512 KB body can carry on the order of tens of thousands of minimal dimension rows, each producing DOM. The `MAX_RESPONSE_BYTES` ceiling is the only backstop. Remediation if the mount packet wants defense in depth: slice `dimensions` and the per-dimension arrays to a stated cap in `boundEnvelope`, with an explicit "showing N of M" disclosure rather than a silent truncation (the repo's no-silent-default rule). The adopted candidate's vertex count is already bounded downstream by `validateDraft`'s `MIRROR_ROUTE_MAX_TOTAL_OUTLINE_POSITIONS`.

### F4 — LOW (advisory): three security-relevant client behaviors are asserted nowhere

The Content-Length fail-closed branch is tested only for the over-large case (`max-envelope-api.test.ts:272`); absent, blank, and non-numeric headers have no test. `client_timeout` and `aborted` have no test at all. The panel's superseded-request guard (`MaxEnvelopePanel.tsx:235-245`) has no test. All three are correct by reading — the gap is proof, on exactly the fail-closed paths.

## Part 2c — F5 through F7 and closing

F5 — LOW: `maxEnvelopeRequestForProfile` (`max-envelope-api.ts:546`) interpolates `profile.identity.bbl` into `label` unbounded, while the sibling district is bounded. Outbound-only and refused fail-closed server-side by `_require_label`. Fix for consistency: `boundedToken(bbl, 32)`.

F6 — LOW, human-journey's lane: with the route unmounted, every production proposal-view load 404s into the `role="alert"` failure card (`MaxEnvelopePanel.tsx:278-297`) — an assertive announcement for a permanent expected state, plus a POST that cannot succeed.

F7 — informational: the panel renders only static announcement copy, discarding the server's bounded `message`/`field`. Good for security; re-verify bounding if ever surfaced.

Closing: **PASS.** Mount seam must add authN/tenancy (already dispositioned in `max_envelope_api.py`), a rate limit on an engine-backed POST fired per page load, a real-deployment `Content-Length` assertion, and the F1 fix.

END-OF-REPORT
