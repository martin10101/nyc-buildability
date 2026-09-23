# M5-T070 — G4 DELTA attestation (VERBATIM, two-part transmission)

TRANSMISSION HISTORY (orchestrator note, not reviewer text): delivered 2026-09-23 in two
parts (05:35:11Z head; 05:35:25Z the nit tail joined at "carry contained: null and both
rectangle fields null ("). Supplements the wave-1 FAIL report (M5-T070-G4.md). The
reviewer's own text follows, unedited.

---

# G4 DELTA ATTESTATION — M5-T070 correction set

## VERDICT: **ATTESTED-PASS**

**Identity (verified myself).** CI run 35822387368 = `success`/`completed` at headSha `395d6727eb270dd4a3ce7bf60fac84bfbc109304`, branch `candidate/D-024-mrl-option-b`, 18/18 jobs green, zero non-success jobs. All twelve packet files are byte-identical across `395d6727`, live head `75e14da4`, and the working tree. Six blobs moved from the prior submission (MaxEnvelopePanel `f2392abc→b3e8fc1a`, max-envelope-panel.test `31c7ba86→b98e5238`, max-envelope-api.test `3ce5da2c→5eeb013d`, entry.test `569cad4a→f80fd568`, proposal-editor.spec `735847c4→0f2eb2a4`, producer-report `4cb40ac6→7e6d20b1`); six are unchanged, including `max-envelope-api.ts` (`06a2df29`) — correctly, since F1 required disclosure plus a test, not a request-builder behavior change.

**(1) F1 — attested.** The new spec at `max-envelope-panel.test.tsx` pins exactly what I specified: `candidate: null`, `status: "lot_geometry_unsupported"`, `detail` carrying the server's own prose from `max_envelope.py:632-637`, asserting the card reads "No building option can be adopted", contains "no lot-line geometry was supplied", and that `adopt-candidate` is absent. The producer report's new "AS-4 NAMED LIMITATION" section states the reachability truth plainly with the `:632-637 → :795-800` proof chain and says outright that every fitted-candidate fixture models *future* server behavior, not a state the shipped request can elicit today — that is the honest framing, not a hedge. The evidence map carries the same limitation under D-082-R001, and DB-050(a) records the geometry-threading seam with the right design direction (server-side derivation from `mappluto_geometry_arcgis` by BBL, never client-sent display geometry).

**(2) F2/F3 — attested, with one wording correction.** Zero residual `no_fit` or prose `gap_reason` anywhere in `apps/web` (I grepped). Every `gap_reason` in the repo is now `allowance_unresolved`; placement statuses in use are `fitted` (4), `footprint_exceeds_lot` (2), `lot_geometry_unsupported` (1) — all real `CandidatePlacementStatus` members. The panel's `GAP_REASON_COPY` map covers exactly the four `EnvelopeGapReason` members, and `detail` below is untouched. Teeth are real: the gap test now asserts both the mapped copy *and* `not.toHaveTextContent("allowance_unresolved")`. One correction to the brief's phrasing: a *recognized* token never leads, but an **unrecognized** token deliberately renders raw in the headline (`GAP_REASON_COPY[token] ?? token`). That is the right choice — fail-honest beats invented copy — and it is documented as such; I attest it as correct behavior, not as "raw token never in the headline".

**(3) F4 — attested.** The three D-083 rows now match my row-by-row table: R002 = three claim classes (wall + "Generated building option" adoption labeling + demonstrated-maximum withheld), R003 = answer-first (with the `compareDocumentPosition` ordering assertions, and the anchors `entry.test.tsx:328` / e2e `:592-601` are correct), R004 = incomplete-aggregate alone with the adoption gate moved out to R002.

**(4) Nothing weakened; regression green.** I audited every removed line in `apps/web/`: nine deletions, all replaced — four prose fixture values, two `no_fit` values, two assertions swapped for equivalent-or-stronger ones, and one production line replaced by the mapped call. No assertion was removed or loosened; net +1 spec and +2 files inside the AS-2 wall (A1 folded in). In run 35822387368: `max-envelope-panel.test.tsx` 13 tests (was 12), `max-envelope-api.test.ts` 23, `entry.test.tsx` 41, `Test Files 55 passed`, Playwright `120 passed`.

**Residual nits (advisory, no action required at this gate; both fall inside the DB-050 cluster).** (i) The new fixtures use `contained: false` and omit `lot_rectangle`/`footprint`, whereas the real `lot_geometry_unsupported` and `footprint_exceeds_lot` serializations carry `contained: null` and both rectangle fields `null` (`CandidatePlacement` defaults, `max_envelope.py:330-337`). Outcome-identical — `boundEnvelope` maps a non-boolean `contained` to `null` and `candidateIsAdoptable` requires `=== true` — so there is no false pass, but it is a trace of the same fidelity class F2 addressed.

(ii) The F1 spec's `SERVER_DETAIL` constant is faithful to the server string, but the assertion binds only the prefix substring (`toHaveTextContent("no lot-line geometry was supplied")`), so byte-identity to the server prose is not actually pinned the way the disclosure constant is.

(iii) A6 drifted further: the D-083-R001 evidence row's `MaxEnvelopePanel.tsx:223` / `:154` anchors are now off by roughly 34/35 lines after the panel gained 19 — already carried as DB-050(k) and correctly not claimed closed.

**Closing.** All four of my blocking findings (F1–F4) are closed at `395d6727`; A1 is folded into the extended AS-2 wall; A2–A6 are carried as DB-050 riders (f)/(h)/(i)/(j)/(k) and are correctly *not* claimed closed. The three residual nits above are advisory only and require no action at this gate.

**VERDICT: ATTESTED-PASS**

END-OF-REPORT
