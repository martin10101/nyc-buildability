# M5-T078 + M5-T079 — human-journey re-walk after the reworks (human-journey-reviewer "hj-web2", read-only; fresh reviewer; joint)

> Transmission history: pinned at 6c79cd88, delivered as three SendMessage parts (1/3..3/3) ending with
> END-OF-REPORT; no truncation. Joined verbatim by the orchestrator (transport wrapper tags removed only);
> saved identically as M5-T078-HJ-rework.md and M5-T079-HJ-rework.md. Verdicts: M5-T078 HJ PASS (HJ-1
> closed), M5-T079 HJ (rework copy) PASS. CI proof cited: run 35989704760 at 6c79cd88, zero non-success jobs.

---

M5-T078/T079 HJ RE-WALK part 1/3 — identity + HJ-1 (the blocking re-check).

Fresh independent reviewer, read-only. Pinned HEAD 6c79cd88 (git). Rework commits 2e2bd536 (T078) and 912aa8d2 (T079) are both ancestors of HEAD, each touching only allowed_paths (source+specs+report). Walked from source, specs, copy tables; thin client (no npm/node).

EXECUTED PROOF: CI run 35989704760 at headSha 6c79cd88 is completed / conclusion=success, ZERO non-success jobs — "web (lint+typecheck+build)" and "web-e2e (vitest + Playwright)" both green. The 5 reworked source files differ from the last-green baseline 4c999e15 (314+/140-), so THIS run proves the rework, not an earlier green.

HJ-1 (was BLOCKING) — CLOSED. Journey (production-reachable feature_unavailable path):
1. 3 points, Convert -> the refusal card (role=alert, ProposalOutlineDraw.tsx:419-424) body is now announcementForOutlineBridge(outcome) (:464): "Outline not converted / Map-drawing conversion is not available in this environment. Enter coordinates in the table instead."
2. Delete a point -> 2 finite; Convert aria-disabled=true (:400), visibly dimmed (architect.css:45).
3. Press Convert -> onConvertActivate (:263-274): !canConvert takes the announcer clear-then-set path ONLY; NO setOutcome, NO fetch.
   - CARD unchanged: still the server "…not available… enter coordinates in the table" refusal; the misleading "Add 1 more point" is NOT in the card; the alert does not re-fire (content byte-stable).
   - ANNOUNCER (polite OutcomeAnnouncer :278) speaks "Add 1 more point to convert — an outline needs at least 3 points (you have 2)." exactly ONCE.
   - Nothing announced twice; no futile loop (card still says "enter coordinates in the table", never implies one more point will convert).

Spec proposal-outline-draw.test.tsx:530-576 pins exactly this: card textContent byte-equal (toBe(cardText)), NOT containing "Add 1 more point", fetchSpy===1, onAdopt never called; :610 also covers the "Conversion is already in progress." pending-press path (card text unchanged). CI-green.

=> HJ-1 CLOSED. (it.each also covers out_of_neighborhood 422, though only feature_unavailable is production-reachable — route unmounted.)

---

M5-T078 HJ RE-WALK part 2/3 — items 2-5 + verdict.

(2) HJ-3/HJ-7 landed clearly. ProposalOutlineMap.tsx:206-218 gates ALL map-gesture copy on mapSurface==="present": "absent" (condo/fallback) -> "…The reference map on this lot has no interactive drawing surface." (no "click"); "unknown" (loading) -> "Preparing the reference map…". Spec :431 (5 FALLBACK_STATES + loading): status/instructions never match /click/i and never say "ready". HJ-7 deselect: untyped selection (:214) now "Use its Deselect button in the table to clear the selection" (was "Click the point again"); finite selection (:210) keeps "Click the point again to deselect" (accurate — that point IS on the map). Half-typed rows exact via shared missingOrdinateLabel (:75): "has no latitude yet"/"type its latitude"; "coordinates" only when both missing (spec :512).

(3) HJ-2 — Convert looks disabled again. architect.css:45: `.architect-shell button:disabled,.architect-shell button[aria-disabled="true"] { cursor:not-allowed;opacity:.6; }` (the aria-disabled Convert now dims + not-allowed cursor).

(4) HJ-4/HJ-5 plain. HJ-4 convertHintCopy (:93-97): "Convert will include N points. M rows are missing their {label|coordinates} and will be left out — fill them in to include them, or delete them." — no "delete it to include it", no doubled "not filled in". HJ-5: a bridged conversion with omitted>0 appends omittedRowsClause to the announcement (:249-252); Convert aria-describedby -> hint (:401). Omission is both shown and spoken.

(5) NEW confusion — none blocking:
- HJ-A (ADVISORY, PRE-EXISTING — not introduced by this rework): on a REAL refusal the role=alert card (:424) and the polite announcer (:278) carry the SAME text, so it is announced ~twice. Unchanged from before the rework (card was role=alert already); same class as T079 HJ-6; violates OutcomeAnnouncer's own exactly-once contract (its failure cards are meant to omit role=alert). Route to D-086/mount.
- 100ms clear-then-set (:267): bounded; cancelled by convert start/result/unmount; a blocked reason is at most ~100ms stale only if state changes within that window — negligible.
- Ready-once state-during-render machine (:238-246): converges (each branch lands non-re-entrant); readiness is held while a point is selected (disclosed; arguably more correct). Spec :472 pins "spoken once"; no loop, no re-append.

M5-T078 HJ VERDICT (rework): PASS

---

M5-T079 HJ RE-WALK part 3/3 — item 6 (rework copy) + verdict.

Route stays UNMOUNTED (every state reached only via stubs) — pre-mount honesty; copy judged on its own terms.

(6) Withheld-row headline/detail/aggregate understandable to an architect, no jargon, honestly incomplete — YES.
- Headline (MaxEnvelopePanel.tsx:86, rendered :126): "Could not check — the service's answer for this limit was inconsistent or unreadable, so no value is shown." Plain; the old "broke the binding-or-gap data contract" jargon is gone.
- Detail (:151-155): "The service should send either a value or the reason it could not check this limit. It returned {both a value and a reason | neither a value nor a reason | no usable value or reason}, so nothing is shown for this limit and this preliminary picture stays incomplete." Plain; a single unusable field is "no usable value or reason", never mislabeled "neither".
- Aggregate (max-envelope-api.ts:657-677): "Could not check N of M development limits (W withheld because the service's answer was inconsistent or unreadable)[, and a rule conflict needs professional review]. [The service's own count listed X of Y as not checked.] This preliminary picture is incomplete." Counts SCREEN ROWS (gap+withheld); "Could not check N of M" only when N>0 (HJ-2: never "0 of N"); server's own count disclosed on disagreement, not dropped.
- Announcer (:701) now speaks the full aggregate line incl. the withheld clause + "incomplete" (HJ-1 closed) — SR users no longer hear a bare "0 of 2 could not be checked".
- D-083 honesty intact: heading "Preliminary development limits"; a withheld row NEVER renders a value (classifyDimensionRow emits no value span); announcer tail "…not a maximum permitted building". No maximum-permitted claim in any rendered string.

Residual T079 advisories (carryover, non-blocking, routed to mount/D-086):
- HJ-4: candidateIsAdoptable (:679-685) still ignores contract violations, so Adopt could appear with a withheld limit; latent-unreachable today (no candidate without lot geometry).
- HJ-6 / D4: failure card role="alert" and the aggregate role=status both repeat the announcer -> possible double-read at mount.

M5-T079 HJ VERDICT (rework copy): PASS

END-OF-REPORT
