# M5-T079 producer report — DB-050(c)-(m) max-surface hardening

Scope: the accepted Preliminary-development-limits panel and its client. Closes DB-050 cluster
items (c)(d)(f)(g)(h)(i)(j)(l)(m). Route stays UNMOUNTED; `services/api` untouched; no forbidden
file edited; no new dependency. Web behavior proves ONLY in CI on the pushed head — every
per-spec claim below is `[PREDICTED]` (I reasoned it against the code + existing fixtures; I did
not run vitest/playwright, thin client). The one local check is modularity.

## Changed files (all inside allowed_paths)

- `apps/web/src/lib/architect/max-envelope-api.ts` — gap-reason union + XOR row-kind predicate
- `apps/web/src/components/architect/MaxEnvelopePanel.tsx` — typed contract-violation row, exhaustive
  gap-copy map, dead read removed, aborted guard
- `apps/web/src/components/architect/__tests__/max-envelope-panel.test.tsx` — walls + XOR + loading/retry/superseded
- `apps/web/src/lib/architect/__tests__/max-envelope-api.test.ts` — timeout/aborted/XOR/no-CRS-math
- `apps/web/src/components/architect/__tests__/entry.test.tsx` — default max-envelope fetch stub
- `apps/web/e2e/proposal-editor.spec.ts` — capture-then-assert contract stub
- `project-control/reports/M5-T079-producer-report.md` — this report

## Local check (the only runnable one; thin client)

cwd `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t079`:
`python tools/modularity_check.py --check`  →  `selected 484 files; failures 0; warnings 22`  (exit 0).
No warning names a changed web file.

Wall self-verification (allowed: python replica of the strengthened matcher over the 5 real
scanned files, cwd as above): all 5 files PASS (no banned rendered copy); injected variants
`Maximum-allowed building` / `MAXIMUM ALLOWED BUILDING` / `demonstrated   maximum` /
`demonstrated-maximum` all caught=True; a comment-only `// never a maximum allowed building`
caught=False. This is the OBSERVED evidence that the strengthened wall (l) still passes the
accepted copy while gaining teeth.

## Per-AS evidence

### AS-1 (typed outcomes) — DB-050(c)(i)
- Loading card: panel `MaxEnvelopePanel.tsx` loading branch (`envelope-loading`, role=status, aria-busy)
  unchanged; spec `max-envelope-panel.test.tsx:396`.
- client_timeout / aborted: classified in `max-envelope-api.ts fetchMaxEnvelope` (timeout branch, and
  the pre-flight `externalSignal.aborted` early-return); specs `max-envelope-api.test.ts:411` (both).
- payload_too_large / invalid_request: existing api specs at `max-envelope-api.test.ts:243` retained.
- Aborted never renders a reasonless card (c): NEW guard `MaxEnvelopePanel.tsx:288`
  (`if (result.kind === "aborted") return;`) — an aborted outcome is never stored, so the
  request-cleared→re-set transient can never flash the empty-reason failure card. Covered by the
  superseded spec (`:429`, latest-state-stays, mutation-sensitive on the active-token guard) plus a
  render-invariant spec that the failure card's reason `<p>` is always non-empty (`:454`), plus the
  api invariant `announcementForMaxEnvelope({kind:"aborted"}) === ""` (`:371`, existing). See
  Limitations for why the guard itself is not directly RTL-observable.
- Retry issues exactly one new request: spec `max-envelope-panel.test.ts:412` counts fetch calls
  across two clicks (1→2→3, exactly +1 per click).
- [PREDICTED] each spec above red/greens on the branch it names.

### AS-2 (XOR fail-closed) — DB-050(d)
- Predicate `dimensionRowKind` (`max-envelope-api.ts:591`): `hasValue === hasGap → contract_violation`,
  else value/gap. `envelopeHasContractViolation` (`:601`) folds it into `envelopeAggregateIsComplete`
  (`:605`) so a both/neither row keeps the aggregate visibly incomplete.
- Render: `MaxEnvelopePanel.tsx:87` drives a three-way row; a violation renders
  `envelope-contract-violation-<id>` (`:113`) and NEVER `envelope-value-<id>`; the contract detail
  states `returned both`/`returned neither`.
- Specs: unit `max-envelope-api.test.ts:447` (value/gap/both/neither + aggregate-with-violation);
  render `max-envelope-panel.test.ts:355` (BOTH: no value testid, aggregate `data-complete=false`;
  NEITHER: no `null` value).
- [PREDICTED] MUTATION: deleting the `hasValue === hasGap` branch collapses both/neither to value/gap
  → the unit spec (`:458`) and the render specs (`:356`,`:378`) redden; dropping the violation term
  from `envelopeAggregateIsComplete` reddens `:465`.

### AS-3 (walls) — DB-050(f)(l)(m)
- Claim wall (l): `containsBannedClaim` (`max-envelope-panel.test.ts:287`) strips block+line comments,
  lowercases, collapses `[-\s]+`, then substring-matches. Passes the 5 real files (`:298`), HAS TEETH
  on case/hyphen/space variants (`:314`), exempts comment-only phrases + accepted copy (`:322`).
  Comments MUST be stripped or `MaxEnvelopePanel.tsx:33`'s negation ("...maximum-allowed-building
  claim") false-positives — verified with the python replica above.
- gap-copy exhaustiveness (m): `GAP_REASON_COPY: Record<EnvelopeGapReason, string>`
  (`MaxEnvelopePanel.tsx:62`) over the union `ENVELOPE_GAP_REASONS` mirrored from the server enum
  (`max-envelope-api.ts:70`, EXACT four tokens verified against `max_envelope.py:132-146`). Spec
  iterates every token asserting analyst prose (not the raw token, no `_`) at
  `max-envelope-panel.test.ts:334`; the SEC-F1 own-property guard preserved via `isKnownGapReason`
  (`:74`).
- no-client-CRS-math (f): `max-envelope-api.test.ts:506` greps the panel + api + proposal-draft
  sources for projection-library/transform markers (comment-safe: not the bare word "transform").
- [PREDICTED] MUTATION: adding a token to the union without copy fails `tsc` (exhaustive Record);
  injecting `import proj4`/a transform call reddens `:506`; a `Maximum-allowed building` variant in
  rendered copy reddens `:298`.

### AS-4 (e2e + entry) — DB-050(g)(h)
- e2e (g): `proposal-editor.spec.ts:553` captures method+body and ALWAYS fulfills, then asserts the
  full `toEqual` contract AFTER the panel consumes the response (`:584`). A mismatch now fails with an
  explicit diff, never a timeout-only hang (the prior assert-inside-handler threw before fulfilling).
  The other e2e stubs (proposal-checks/outline-bridge) are out of scope and untouched.
- entry (h): default max-envelope fetch stub installed in `beforeEach` (`entry.test.tsx:32`,
  feature-unavailable 404 with explicit Content-Length); the panel-mounting test now awaits its
  settle (`:205`) and a dedicated spec asserts the panel fetched the max-envelope route through the
  STUB, never real network (`:209`).
- [PREDICTED] the e2e AS-5 dimension assertions still pass under the XOR change (max_far → value row,
  max_height → gap row); entry suite no longer makes an unstubbed call (suite-time creep removed).

### AS-5 (dead read + compatibility) — DB-050(j)
- Dead `street_width_class` read removed from the adopt seed (`MaxEnvelopePanel.tsx:189`, now an
  unconditional `""`). Seed is BYTE-IDENTICAL: the prior expression
  `streetWidth === "wide" || "narrow" ? streetWidth : ""` always evaluated to `""` because
  `maxEnvelopeRequestForProfile` never sets `lot_rule_facts.street_width_class` (G4 A5). Existing
  adoption specs (`max-envelope-panel.test.ts` AS-4 block; `entry.test.tsx` adoption; e2e AS-5) do not
  assert `street_width_class`, so the byte-identical seed keeps them green.
- Compatibility: exactly the allowed_paths changed; no new dependency; modularity exit 0;
  `services/api` untouched; D-083 heading "Preliminary development limits" and "Generated building
  option" unchanged; server disclosure still rendered verbatim.
- [PREDICTED] all accepted panel/api/entry/proposal-editor-unit/e2e specs pass in CI on the pushed head.

## Copy table (before → after; every changed user-visible string)

| # | Before (accepted) | After | Meaning it protects |
|---|---|---|---|
| 1 | — (none) | Row headline (violation): "Could not check — this development limit's response broke the binding-or-gap data contract and was withheld." | XOR fail-closed: a both/neither row never shows a value (DB-050(d)) |
| 2 | — (none) | Row detail (violation): "The engine must return exactly one of a binding value or a typed gap reason for each development limit; this response returned both/neither, so the value is withheld and this preliminary picture stays incomplete." | Names WHY the value is withheld; keeps the picture honestly incomplete |
| 3 | `Could not check {gap} of {total} development limits{, advisory clause}. This preliminary picture is incomplete.` | Same, plus an appended clause ", and a development limit response broke the binding-or-gap data contract and was withheld" ONLY when a violation is present | Aggregate stays visibly incomplete + discloses the contract breach (D-083-R004) |

No existing disclosure, honest-gap statement, provenance note, or professional-review string was
deleted or weakened. The complete-aggregate message, the gap-reason copy, the disclosure, the
heading/option claim-class strings, and the adoption announcement are all unchanged. No status is
remapped; no number is computed in the presentation layer.

## Limitations / honest gaps

- The `aborted` `.then` guard (`MaxEnvelopePanel.tsx:288`) is a real hardening for the browser
  (it prevents a one-frame reasonless-card flash on request-cleared→re-set), but it is not directly
  observable in an RTL unit test: the only paths that produce an `aborted` outcome on the ACTIVE
  token are supersession (already caught earlier by the active-token guard) and unmount (no DOM to
  assert), and RTL flushes effects so the transient frame is never rendered synchronously. It is
  therefore covered INDIRECTLY: the superseded spec proves latest-state-stays, the render-invariant
  spec proves the failure card is never reasonless, and the api spec pins `announcement(aborted) === ""`.
  I did not manufacture a direct observation I cannot honestly make.
- All web-behavior claims are `[PREDICTED]` — CI on the pushed head is the proving context.

## DISCOVERIES (route to docs/DISCOVERY_BACKLOG.md at the seam; not fixed in-packet)

- D1 (advisory, DB-050(a) family): one-action adoption remains production-UNREACHABLE until the
  server-side BBL→2263 geometry seam (M5-T076) lands; this packet does not change that — the
  contract-violation and aborted hardenings are pre-mount honesty, not the mount.
- D2 (test-infra, low): `entry.test.tsx` now installs a global fetch stub in `beforeEach` for the
  whole file. It is scoped safely (per-test stubs in the additive block still override; non-proposal
  views don't fetch), but if a future entry test needs a different global-fetch contract it must
  re-stub. Noting so the shared stub isn't a surprise.
- D3 (product copy, low): the contract-violation aggregate clause reads "Could not check 0 of N
  development limits, and a development limit response broke the binding-or-gap data contract…" when
  gap=0 — the "0 of N" is technically honest but slightly awkward; a future copy pass on the mount
  packet could special-case a violation-only aggregate. Out of scope here (meaning-preserving
  additive clause chosen to avoid touching the accepted gap/advisory message).

END-OF-REPORT

## Rework (G3 F1-F2 + G4 F1-F2 cluster)

Appended after the original report (above left byte-identical). Base `a57bb8de`, worktree
`C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t079`. One correction cluster, allowed_paths only:
`max-envelope-api.ts`, `MaxEnvelopePanel.tsx`, their two specs, this report. `entry.test.tsx`,
`e2e/proposal-editor.spec.ts` and `services/api` untouched; route still UNMOUNTED; no dependency
change. Every web claim is `[PREDICTED]` (thin client: no npm/node/vitest/playwright run) — CI on
the pushed head is the proving context.

### Local evidence (cwd = worktree root)

- `python tools/modularity_check.py --check` → `selected 486 files; failures 0; warnings 23`, exit 0
  `[OBSERVED]`; no warning names a changed file. `max-envelope-api.ts` 532 SLOC / 40 exported
  symbols (ceiling 40; a first run at 42 raised `symbol_ceiling`, so two one-line helpers were
  inlined); `MaxEnvelopePanel.tsx` 267 SLOC.
- A Python replica of the new classifier + aggregate line + announcement (scratchpad only, not the
  TS) reproduced every literal the new specs pin, for all fixtures `[OBSERVED — replica only]`.
- Claim-wall and CRS-marker replicas over the wall's 5 files / the guard's 3 files: no banned claim,
  no marker `[OBSERVED — replica only]`.

### Per-finding closure (file:line at the rework head)

- **G3-F1 (BLOCKING)** — raw presence recorded before bounding: `max-envelope-api.ts:118-119`
  (view fields) and `:354-355` (`binding_value`/`gap_reason` non-null/undefined, not truthiness).
  `classifyDimensionRow` `:606-615`: both present → violation `both`; neither → `neither`; exactly
  one present but unusable (bounded to null) → `unreadable`; only a present-AND-usable single field
  is `value`/`gap`. `dimensionRowKind` `:617` delegates. Panel detail no longer says "neither" for a
  malformed field (`MaxEnvelopePanel.tsx:88-92`, `:151-155`). Specs: panel `:455` (value + `""`,
  `" "`, `7`, `{}` gap_reason → withheld BOTH, row text has no `20000`, aggregate never complete),
  panel `:483` (a blank / non-string gap_reason alone, a string binding_value alone → "It returned
  no usable value or reason", never "neither", no `null`), panel `:499` (binding_value `0` → value
  row "0 ft", complete); api `:590` (13-row raw table through the real decode), api `:605`
  (presence flags), api `:515` (`dimOf(0, null)` → value).
- **G3-F2 / G4-F1 (BLOCKING)** — AS-1 panel cards: panel `:665` it.each (413 payload_too_large, 422
  invalid_request: exact first-`<p>` literal, Retry presence = hardcoded `false` AND cross-checked
  with `maxEnvelopeOutcomeIsRecoverable`), panel `:673` client_timeout (`vi.useFakeTimers`,
  abort-honoring pending fetch, `act(advanceTimersByTimeAsync(DEFAULT_TIMEOUT_MS))`, synchronous
  asserts: exact literal, Retry present, loading gone; `useRealTimers` in the describe's
  `afterEach`). boundCandidate non-srid rejects: api `:337` it.each, 13 isolated probes covering
  `max-envelope-api.ts:275` (empty; missing), `:278` (object-shaped vertex), `:281` (x; y), `:287`
  (levels `""`), `:294` (each of the 3 level fields), `:298` (walls `""`), `:304` (id; start; end),
  plus a control spec `:358` that the same candidate survives unpatched.
- **G3-F2(3) / G4-F2 (BLOCKING)** — panel `:599`: render(REQ) with an abort-honoring pending fetch
  → `rerender(null)` → flush inside `act` (setTimeout 0) → MutationObserver(childList, subtree) on
  the container → `rerender(REQ2)` → `takeRecords()` → no added node is/contains
  `data-testid="envelope-failure"`; loading card present after. Guard comment re-anchored at
  `MaxEnvelopePanel.tsx:283-289` (the reachable path is request→null, not supersession/unmount).
- **G3-A1** — `envelopeAggregateIsComplete` also requires no gap ROW (`max-envelope-api.ts:628-636`).
  Specs api `:614`, panel `:514`, and the "gap only" row of api `:590`.
- **HJ-1 / G3-A3** — the announcer speaks the same aggregate line (`max-envelope-api.ts:697-706`):
  "Preliminary development limits loaded. {aggregate line} A rules-derived estimate … not a maximum
  permitted building." Specs api `:410` (exact), api `:643`, panel `:389` (announcer has the
  withheld clause + "incomplete", never "0 of 2 could not be checked").
- **HJ-2 / G4-A9** — `envelopeAggregateMessage` (`max-envelope-api.ts:647-677`, rendered at
  `MaxEnvelopePanel.tsx:218`): screen-row counts; "Could not check N of M" only when N > 0; withheld
  rows counted in a parenthetical; the server's own count disclosed when it disagrees. Specs api
  `:627` (accepted lines unchanged), `:643`, `:664`, `:676`; panel `:389`.
- **HJ-3 / HJ-5** — plain-words headline + detail (`MaxEnvelopePanel.tsx:86-92`, `:126`, `:151-155`).
- **G4-A1** — row-text negatives: panel `:389` block (`not "20000"`), `:426` block (`not "null"`),
  plus the same negatives in `:455` / `:483`.
- **G4-A4** — four gap-copy literals hardcoded and rendered: panel `:374`.
- **G4-A7** — `draft.street_width_class === ""`: panel `:223` block.

### Mutation traces (static; mutant → the assertion that reddens)

1. Classify on BOUNDED fields again (ignore the presence flags) → value + `""`/`" "`/`7`/`{}` reads
   `value`: panel `:455` `findByTestId("envelope-contract-violation-max_far_floor_area")` throws and
   `queryByTestId("envelope-value-…")).toBeNull()` fails; api `:590` rows 5-8 `toEqual` fail.
2. Delete the both-present line (`:609`) → the same rows fall through to `value`: same reds.
3. Drop the value usability check (`:612` always `value`) → `"60"` alone renders "null ft": panel
   `:483` row 3 (value testid present, violation absent); api `:590` last row.
4. Drop the gap usability check (`:614` always `gap`) → `""`/`7` alone read `gap`: panel `:483` rows
   1-2 (`envelope-gap-…` present; violation absent); api `:590` rows 11-12.
5. Truthiness presence at `:354` (`Boolean(record.binding_value)`) → `0` reads `neither`: panel
   `:499` `findByTestId("envelope-value-max_height_ft")` throws; api `:590` row 2. Truthiness
   usability at `:612` → api `:515`.
6. Detail says "neither" for `unreadable` → panel `:483` `not.toHaveTextContent("neither")`.
7. `announcementForMaxEnvelope` returns "" for payload_too_large / invalid_request / client_timeout
   → panel `:665` / `:673` `textContent).toBe(<literal>)`.
8. Retry predicate drift (`maxEnvelopeOutcomeIsRecoverable` gains payload_too_large/invalid_request
   or loses client_timeout) → panel `:665` both Retry asserts / `:673` `getByTestId("envelope-retry")`.
9. `timedOut` branch dropped → timeout classifies `aborted`, guard drops it, loading persists →
   panel `:673` `getByTestId("envelope-failure")` throws.
10. Any single boundCandidate guard/disjunct deleted → its api `:337` row returns a non-null
    candidate → `expect(envelope.candidate).toBeNull()` fails (the "vertices missing" probe reddens by
    a thrown TypeError instead of the assertion). Exception: the `raw.length < 2` disjunct at `:278`
    is an equivalent mutant — every JSON array shorter than 2 has `raw[1] === undefined`, which the
    finite-y check at `:281` rejects; no probe can separate it.
11. Delete the aborted guard `MaxEnvelopePanel.tsx:289` → after request→null the `aborted` outcome
    is stored (loading false); REQ2's first commit inserts the reasonless failure card before the
    effect sets loading → panel `:599` `expect(failureCommitted).toBe(false)` fails. (G4's own
    predicted executed mutant: green at HEAD, red with the guard deleted.)
12. Drop the gap-row term (`:633`) → api `:614`, panel `:514`, api `:590` row 3.
13. Announcement reverts to "loaded, but {gap} of {total} could not be checked" → api `:410`, `:643`,
    panel `:389` announcer asserts.
14. "Could not check 0 of" reintroduced (`notShown >= 0`) → api `:664`, panel `:389`.

### Copy table delta (before → after; meaning protected)

| # | Before | After | Meaning protected |
|---|---|---|---|
| R1 | Row headline (T079 v1): "Could not check — this development limit's response broke the binding-or-gap data contract and was withheld." | "Could not check — the service's answer for this limit was inconsistent or unreadable, so no value is shown." | Still withheld, still "Could not check"; plain words (HJ-3) |
| R2 | Row detail (T079 v1): "The engine must return exactly one of a binding value or a typed gap reason for each development limit; this response returned {both\|neither}, so the value is withheld and this preliminary picture stays incomplete." | "The service should send either a value or the reason it could not check this limit. It returned {both a value and a reason \| neither a value nor a reason \| no usable value or reason}, so nothing is shown for this limit and this preliminary picture stays incomplete." | Exact about what was sent (G3-F1, HJ-5); "incomplete" kept |
| R3 | Aggregate with a violation (T079 v1): "Could not check {summary.gap} of {total} development limits[, and a rule conflict needs professional review], and a development limit response broke the binding-or-gap data contract and was withheld. This preliminary picture is incomplete." | "Could not check {gap rows + withheld rows} of {rows} development limits ({W} withheld because the service's answer was inconsistent or unreadable)[, and a rule conflict needs professional review]. [The service's own count listed {summary.gap} of {summary.total} as not checked.] This preliminary picture is incomplete." | Counts the withheld rows; never "0 of N" (HJ-2); server count disclosed, not dropped |
| R4 | Advisory-only aggregate (accepted T070): "Could not check 0 of {total} development limits, and a rule conflict needs professional review. This preliminary picture is incomplete." | "A rule conflict needs professional review. This preliminary picture is incomplete." | Same meaning without the false-sounding "0 of N" |
| R5 | Gap row while summary.gap = 0 (accepted T070): read complete — "All {total} preliminary development limits were checked — …" | "Could not check {gap rows} of {rows} development limits. The service's own count listed 0 of {total} as not checked. This preliminary picture is incomplete." | No unrestricted "all checked" over a visible gap (G3-A1, D-083-R004) |
| R6 | Summary.gap > 0 with no gap row (accepted T070): "Could not check {gap} of {total} development limits. …" | "The service's own count listed {gap} of {total} as not checked. This preliminary picture is incomplete." | Server count kept; no claim the page shows a gap it does not |
| R7 | Announcement, incomplete (accepted T070): "Preliminary development limits loaded, but {gap} of {total} could not be checked. A rules-derived estimate requiring professional review, not a maximum permitted building." | "Preliminary development limits loaded. {aggregate line} A rules-derived estimate requiring professional review, not a maximum permitted building." | Screen-reader users hear the withheld clause and "incomplete" (HJ-1); D-083 tail kept |

Unchanged byte-for-byte: the gap-only and gap+advisory aggregate lines, the complete aggregate
line, the complete announcement, every failure-card reason, the gap-reason copy, the disclosure,
"Preliminary development limits", "Generated building option", and the adoption announcement.
Count-source note: the "Could not check" numerator is now the count of rows shown without a value
(gap + withheld) and the denominator the row count; for every consistent server response (all panel,
entry and e2e fixtures) these equal `summary.gap`/`summary.total`, so the accepted text is identical.
The counts are derived in the client lib, not in React, and are screen-row counts, not zoning numbers.

### Not closed / honest limits

- **G3-A2 not implemented (deliberate).** Bumping the active token in the null branch or in cleanup
  would make the `aborted` guard unreachable: request→null would then be dropped by the token check
  first, and unmount leaves no DOM. The blocking G3-F2(3)/G4-F2 demands a spec that FAILS without
  that guard, which would then be impossible (the guard would become an equivalent mutant). So the
  guard stays load-bearing and the null branch stays as it was. The A2 defect remains: a fetch that
  IGNORES its abort signal (the panel's own test stubs; not the browser's fetch) or a result already
  resolved at abort time is stored after request→null, announced as loaded while the panel shows
  "cannot be computed", and could briefly show the old result on the next request's first commit.
  Unreachable in production today (route unmounted). Routed as D5.
- `raw.length < 2` (`max-envelope-api.ts:278`) is an equivalent mutant (trace 10).
- `gapReasonCopy`'s "the reason was not stated" fallback can no longer be reached from a rendered row
  (a gap row now always carries a usable, non-blank token); kept exported and unit-tested.
- Not in this rework's list, left as standing advisories: G3-A4/A5/A6/A7/A8, G4-A3/A5/A6/A8, HJ-4, HJ-6.

### DISCOVERIES (for docs/DISCOVERY_BACKLOG.md at the seam)

- D4 (a11y, low; pre-existing structure): the aggregate `<p role="status">` and the always-mounted
  announcer now carry the same line; a screen reader that also announces a newly mounted status
  region may read it twice. Route to the mount / D-086 a11y pass together with HJ-6.
- D5 (G3-A2 residual, above): decide at mount whether to bump the token on request→null/cleanup (and
  accept the aborted guard as defense-in-depth with a two-guard spec) or keep the current split.

END-OF-REPORT
