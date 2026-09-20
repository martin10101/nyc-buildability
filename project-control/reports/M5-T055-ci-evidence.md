# M5-T055 CI evidence record (orchestrator-captured; thin-client evidence division)

## Run 1 — FAILURE that proved the spec works (run 35493851185, head 848703a7)

The new DB-035 CLS spec FAILED at phone-360 and tablet-768 (desktop-1280 passed):
`Error: CTA moved from 1872.1875 to 1899.1875 at phone-360` and
`from 1918.921875 to 1945.921875 at tablet-768` — exactly 27px both. Root cause
(from the downloaded failure artifacts' page snapshot + source): the LotOutlineMap
basemap/labels status line (`LotOutlineMap.tsx:471`, `.architect-map-status`,
rendered ABOVE the CTA only once map context exists, its text moving from
"Preparing…/loading" to "loaded") settled BETWEEN the two CTA measurements. The
record-note insert was innocent: the rider-b placement assertions passed, and the
G4 review's advisory G4-1 had predicted precisely this environmental class. All
vitest suites and every other Playwright test were green in the same run.

## Correction (tagged, spec-only)

`[ORCH-CORRECTED per G4-1 + CI 35493851185]` commit `05f1aea2`: a terminal-map-state
`expect.poll` (any fallback surface terminal; else `.architect-map-status` must exist
and contain neither "Preparing" nor "loading") + a 500ms double-read CTA quiescence
gate, both BEFORE `releaseRecord()`; the exact-equality assertion, the component, and
the unit tests byte-unchanged. Task walked awaiting_gate → rework → in_progress →
resubmitted at `05f1aea2`.

## Run 2 — SUCCESS on the corrected head (run 35494571792, head bd408ab9)

CI conclusion: **success** — the hardened CLS spec green at 360/768/1280, all web
suites green, api suites green, context-budget + secret-scan green. This run also
constitutes the web proof for the M5-T056 material (same tree). AS-6 satisfied.

## Delta-attestations (all four reviewers carry PASS to 05f1aea2)

G3, G4, G5, HJ each independently reviewed `git diff db0cf0f8..05f1aea2` and
confirmed: material identity byte-stable outside the spec; the fix targets the
measurement environment, not the component; the exact-equality assertion is not
weakened (both new gates run before the release, so they cannot mask an insert
shift); G4 rules its G4-1/G4-2 CLOSED. Verbatim texts appended to the respective
gate reports (M5-T055-G3/G4/G5/HJ.md, "Delta-attestation" sections).
