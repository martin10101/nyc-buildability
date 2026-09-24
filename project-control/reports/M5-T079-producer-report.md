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
