# M5-T004 — Five-Gate RE-REVIEW (G1, G3, G4, G5, DCV)

**Task:** M5-T004 — Compare (Step 3) UI
**Reviewed SHA:** `9b417875` — the reworked chain `527528ae → f9736660 → 22b80eae → f8ec0f11 → c666ef87`, rebased onto the control branch. Content identical to `c666ef87`.
**Prior verdict:** FAIL 4–1 at `84815a76` (silent projection). See `M5-T004-G1.md`, `-G3.md`, `-G4.md`, `-G5.md`, `-DCV.md`.
**This verdict:** **PASS 5–0.**
**Reviewed at:** 2026-09-11. Five independent reviewers, read-only, none authored the code.
**Not executed:** `apps/web/node_modules` is absent under the thin-client policy. No reviewer ran the suite; **no green is claimed.** CI is the authority. Verification is code reading, direct evaluation of pure functions, and one transcribed re-implementation (G4).

This single record covers all five gates because it documents one review wave. Each gate's verdict is recorded separately in `project-control/gates/`.

---

## Headline

| Measure | At `84815a76` | At `9b417875` |
|---|---|---|
| Leaves transported | 191 / 515 | **656 / 665** (effective 659) |
| Authored legal/numeric values | 0 | **0** |
| Constraint leaves, conflict fixture | 0 / 96 | **96 / 96** |
| Preliminary fixture | 103 / 188 | **188 / 188** |
| Schema leaves rendering (G1) | — | **45 / 45** |
| Tests | ~13 | **57+** |

The silent projection is closed. Transport was always clean — the defect was omission at the render layer, which is why this was rework and not rebuild.

---

## G1 — Source and Data-Contract. PASS

All 8 original findings verified fixed. 10 new findings, all MEDIUM/LOW.

`checkTokenRepresentable` (`scenario-contract-checks.ts:209-215`) is `(boundedToken(value, MAX_TOKEN_LENGTH) ?? "") !== value` — a genuine **identity check, not a charset test**, so it cannot drift if the allowlist or 64-cap moves. Wired to exactly 9 fields.

**Over-rejection not reachable today.** Every identifier in all four fixtures machine-checked: zero violations. Builder traced — `constraint_family`, `output_name`, constraint keys and coverage families are constant-sourced; `rule_id`/`rule_version`/`snapshot_id` propagate as ASCII kebab-case; contract versions as dotted semver.

**The relaxation holds end to end.** `boundedToken("")` → `""` → `null` → `?? ""` → `"" !== ""` is false, so empty passes representability and emptiness is decided separately by `checkString`. Without that carve-out the new check would have silently re-imposed the non-empty rule the relaxation removed — the two batch items would have cancelled each other.

### Correction to the first-round report
Finding 9 was reported HIGH ("the DRAFT label vanishes"). **Withdrawn on re-read, corrected to MEDIUM** — `ScenarioCard.tsx:47-49` is an unconditional static prefix no server field can switch off.

---

## G3 — Human-Style Walkthrough. PASS

All five blocking findings cleared; the rework fixed causes, not symptoms.

Top-level `data_completeness` renders in a `role="status"` banner with the exact enum, **above** the coverage label so `missing_critical` cannot be outranked by the milder gloss. `PracticalRangeBlock` now derives from `blocks_buildable_envelope` — and a test **mutates every blocking row to `draft` and asserts the sentence changes**, so it fails on exactly the regression hard-coded prose could never fail on.

`.status-label` defined (`globals.css:285-296`): 700 weight against the number's 600, caution ground, 4px rule at 6.36:1. Shape beats weight for peripheral detection; survives forced-colors. Heading outline fully resolved. `aria-live="polite"` on the loading section, and the two regions are mutually exclusive **by construction**, so they provably cannot double-announce.

The "value above" clause was fixed by **rewording, not gating** — a gate would have deleted the definitional framing from precisely the three branches where a reader most needs to know what a cap is *not*.

**Tracked, not required:** chip overload (same treatment marks IDENTITY MISMATCH, the routine DRAFT label, and the reassuring "No assumptions are declared"); coverage-matrix duplication; no browser journey drives a failure state or the conflict display.

---

## G4 — Integration and Regression. PASS

**Verified empirically rather than by inspection:** `validateScenarioDocument` was transcribed into Python and all four fixtures run through it — **4/4 PASS**, re-run after the validator changed. 100 identifier fields exercised, longest 32 chars against a 64 cap.

### The near-miss
The fail-closed guard rejects an absent `Content-Length`, and **in a browser that header is read cross-origin.** It holds: `Content-Length` is CORS-safelisted, so it stays readable even though `expose_headers` lists only `X-Correlation-ID` (that header *adds* to the safelist rather than replacing it); no GZip in the stack; Starlette's `JSONResponse` always sets it; `notFoundResponse()` was updated to carry it so the flag-off path still classifies. **This is the one item in G4's call resting on spec knowledge rather than repo evidence.**

**The two `TS2339`s are noise** — `@types/react` 19.2.17 is in `package.json` and the lockfile; they were artifacts of probing against a hand-written stub. `web` stays green.

`fixture_api.py` breaks none of the 18 existing specs (router already mounted unconditionally; the flag is a per-request guard). `globals.css` reaches no accepted screen — purely additive, all 16 usages under `components/compare/`. **Modularity measured:** 385 files, 0 failures, 16 warnings byte-identical to pre-rework; `ScenarioCard.tsx` **shrank** 137→119 while gaining content.

**HIGH-1 (transport-shell clone) correctly deferred** — `rule-evaluation.ts` was outside `allowed_paths`. Not worse: three copies before, three after, the third now extracted into a vocabulary-free module that gives the consolidation task a home it lacked. **New observation:** `scenario-api.ts` is now the strongest of the three clients; the profile and rule-eval clients neither size-bound a response before parsing nor bound success-path strings.

**Residual (LOW):** `error.tsx` coverage discharges behavior but not installation — a stand-in boundary cannot prove Next's own wiring.

---

## G5 — Security and Privacy. PASS

Spec item met. `scenario-api.ts:285-291` rejects absent, blank, non-numeric, signed and over-budget before parse. Arrays reject at 64; free text truncates visibly at 600; identifiers now **reject** rather than being silently sanitized; `checkCapProvenance` per-field. Zero dependencies added. Every `checkTokenRepresentable` call site is paired with a string check, so the non-string early return cannot let a value slip past.

**Shadowing the fixture helper loses no fidelity** — the undeclared-length case is tested by deliberately building raw `Response`s that bypass the shadow, and the real server always sets the header, so a helper that sets it models production *more* faithfully than the shared one. `TextEncoder` over `String.length` is correct: a non-ASCII quote would under-declare and turn a genuine over-budget body into an accepted one.

**Reject-not-sanitize, for a stronger reason than display:** a silently sanitized identifier is a **wrong pointer** — `rule_id: "ZR 23-21"` quietly becoming `"ZR23-21"` names a different record, which on a legal-provenance product is worse than showing nothing.

### CARRY-FORWARD — corrects the orchestrator's recorded reasoning
**`Content-Length` is the on-the-wire COMPRESSED byte count, and `.json()` decompresses transparently.** A 256 KiB gzip/br body can decompress to hundreds of MB, fully buffered and parsed. Because `response.body` yields **decoded** bytes, a streaming counter measures post-decompression size — so **the streaming read is strictly BETTER than the header check, not merely more permissive**, which is how the orchestrator framed it when requiring the one-line fix. Same precondition (requires controlling the response), so it belongs with the auth carry-forwards.

Also carried: no web-layer gate on `/property/compare`; `apiBaseUrl()` scheme unvalidated; BBL in the query string; no CSP.

---

## DCV — Data-Contract Verification. PASS

Counts in the headline table. **Reject-not-mutate confirmed:** exactly 9 `identifier()` applications against exactly 9 `checkTokenRepresentable` guards — 1:1, no bounded field unguarded. All three routes to the DOM traced; none can carry an altered identifier.

Citations render **strictly better than the sibling precedent**, which hand-picks two fields — this walks the nested provenance blob generically. The BBL fix carries a *separate* null notice, so "the document doesn't say" never collapses into "they match".

**`PracticalRangeBlock` is faithful — selection, not derivation.** Filters two server booleans verbatim, names families with the server's own strings, computes no value. Two things settle it: the claim is **attributed** ("this document records N…") rather than asserted, and **the zero branch does not flip** — no blockers explicitly does not become "a practical range is available". That inversion was the failure mode worth worrying about.

### The substantive item of the final round
`"present"` → `"end not stated"` is a **RECLASSIFICATION, not tidier copy.** It was the single instance in its group authoring a *legal* claim rather than marking absence — asserting a competing draft rule is in effect now, which no source says. It moves from AUTHORED-MATERIAL to AUTHORED-PRESENTATIONAL. In a block whose purpose is refusing to say which rule governs, rendering both competitors as running "to present" leans toward asserting both currently do.

### Invisible coupling — RECORDED because it will rot quietly
The `pair_class` omission reads as absence **only because** the authoritative rendering of that leaf is the unconditional `provenanceLeaves` walk at `ScenarioConstraints.tsx:117`. The leaf still reaches the DOM, which is why the count is unchanged. **Anyone who later narrows `provenanceLeaves`** — tightens `MAX_PROVENANCE_LEAVES`, adds a key filter, curates it the way the sibling curates citations — **re-opens this without touching `NoScenarioBlock.tsx`.** The coupling is invisible at both call sites.

---

## Items carried out of this packet (not defects in it)

1. **Live defect on an ACCEPTED screen.** `RuleEvaluationResult.tsx:251` renders `{rule.effective_from ?? "unknown start"} to {rule.effective_to ?? "present"}` — the same authored temporal claim, plus the same `??` empty-string half-blindness. Outside `allowed_paths` (`components/property/**` is in `forbidden_paths`), so the producer correctly left it. Recorded in `docs/MVP_AGENDA.md` §C1.
2. **Dormant landmine.** `assumptions[].key` is caller-supplied and unnormalized (`builder.py:199-202`); the new representability check rejects a schema-valid key containing a space or colon. Dormant only because the endpoint never passes `assumptions`. Fix is server-side normalization, **not** client relaxation. `docs/MVP_AGENDA.md` §C2.
3. **Transport-shell consolidation** — three copies of the envelope client; `scenario-contract-checks.ts` is now the right home. Propagate the response bounding to the profile and rule-eval clients, which are now the weaker two.
4. **Compressed-response bound** — the streaming read, per G5's carry-forward above.
5. **Acceptance-criteria sufficiency.** All 8 of this packet's acceptance scenarios PASSED at `84815a76` while four of five gates FAILED. The criteria under-specified the honesty bar. M4-T009's packet was written against this lesson.

## Orchestrator errors recorded

- The `allowed_paths` widening was made in the working copy before the rework was dispatched and **not committed** until G4's re-review flagged it. Every reviewer correctly read the 6-path packet. Ratified at `ab7478e1`. Not a producer violation.
- The brief given to reviewers wrongly stated the API caps responses at 64 KiB / 200 legs; those bound the POST analysis *request*. Corrected by G5 in the first round.
- The one-line header check was described as "sufficient and lower risk" than a streaming read. G5 corrected this: the streaming read is strictly stronger.
