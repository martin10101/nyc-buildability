# G3 RE-REVIEW at 346f8535 — M4-T014 (R3/R4 height/setback draft rule families)

> Preservation note: saved VERBATIM by the orchestrator from the same G3 reviewer's agent-return
> channel (transport entity-decoding only). Supersedes the FAIL recorded from
> M4-T014-G3-supplemental-ruling.md; companions: M4-T014-G3-rule-content-review.md (original
> walkthrough, findings carried forward).

## VERDICT: PASS

My BLOCKING (g)-provenance correction is fully discharged as applied. The trigger-grouping discrepancy resolves correctly. No residuals. The re-review is scoped to the corrected rule-material delta; all previously-passing scenarios (S1–S6) are unaffected because `verbatim_excerpt`, `content_digest_sha256`, every rule value, and the tests are unchanged.

### Delta verified (rule material only)
`git diff --stat c8d94f38..346f8535 -- services/api docs/research/zr-snapshots project-control/reports` restricted to rule material shows exactly: canonical + bundle `zr-23-421-r3-r4.snapshot.json` (4 lines each), `M4-T014-source-capture.md`, `M4-T014-producer-report.md` (addendum). No rule/parameter/applicability/test file changed. (Other files in the full diff are control-plane gates/reports/state/task records and the owner `docs/ARCHITECT_REVIEW_QUESTIONS.md` source doc — not producer rule material.)

### (1) BLOCKING correction — DISCHARGED. All four required elements met, verified against the new note texts:
- **Channel-limitation disclosure:** snapshot notes[1]/notes[2] and the source-capture bullet now state the HTML curl channel "could NOT render" §23-421(a)–(g), citing `docs/ARCHITECT_REVIEW_QUESTIONS.md` lines 48-51 (owner-verified 2026-09-13); confirmed `9,500`/`(g)`/`five feet` still absent from `verbatim_excerpt`.
- **Named basis:** every (g)-content statement (the 5-ft provision, R1/R2-no-suffix scope, "(a) through (g)" lettering, apex-point/≤80° geometry) is attributed by name to the preserved `.claude/agent-memory/rules-engineer/zr-r1-r2-height-setback-source-facts.md` (in B-023) and the owner-verified `docs/ARCHITECT_REVIEW_QUESTIONS.md`, and explicitly marked "never as content read by THIS capture."
- **Accurate owner-verified conditions marked as such:** see (2).
- **No pseudo-verbatim quoting:** the quotation marks around the §23-421 passage in the source-capture report (former lines 53-55) are removed; the passage is reframed as a provenance-qualified description. The only remaining quotes are attributed quotes of the owner questions-doc (legitimate). The snapshot notes carry no §23-421 quote.

### (2) Trigger-grouping discrepancy — RESOLVED CORRECTLY (verified against the owner record myself)
Owner-verified source, `docs/ARCHITECT_REVIEW_QUESTIONS.md:42-44`: *"Conditions (either suffices)... (1) zoning-lot area ≥9,500 sq ft AND width ≥100 ft; or (2) slope ≥5%..."*; corroborated at lines 88-90. The applied text (snapshot note[2] and source-capture) states: `EITHER (a) area ≥9,500 sq ft AND width ≥100 ft, OR (b) slope ≥5% (street-wall-line to rear-wall-line)` — i.e. **(area AND width) OR (slope)**, either sufficing. This matches the source document exactly. The producer-report addendum ("Note on the trigger-condition phrasing") correctly discloses that the coordinator's forwarded paraphrase grouped it differently (`≥9,500 AND (≥100 width OR ≥5% slope)`) and that the producer used the source-document grouping (also consistent with the B-023 phrasing). Source-over-paraphrase, discrepancy disclosed — the right resolution.

### (3) Residuals: none (blocking or advisory that would hold the gate)
- Integrity intact: `content_digest_sha256 = 68e4d147…9459e046` unchanged and still equals `sha256(verbatim_excerpt)`; `verbatim_excerpt` untouched (637 chars); canonical == bundle byte-identical. M4-T010 fail-closed citation-digest binding therefore still holds.
- Regression: `python -m pytest services/api/tests/rules` → **458 passed** (7.52s) post-edit, including the digest-binding/tamper tests that read this snapshot; new file `test_r3_r4_height.py` → **90 passed**.
- The forward-looking "full-text (print/PDF) proof of §23-421 completeness owed before G6" note is a correct, honestly-recorded downstream G6/publication item (carried into the M4-T012 packet); it does not block G3 (nothing publishes at G3; all rules remain `needs_review`).
- The two prior ADVISORY notes (building_type modeling axis for G6; hyphenated banned-phrase cosmetic) remain non-blocking and unchanged.
- No rule value changed, so S1 R3/R4 value fidelity, S2 typed separation/schema-unchanged, S3 gaps, S4 isolation, S5 draft posture, and S6 CI/regression all continue to PASS as independently reproduced.

**G3 verdict at 346f8535: PASS.** The R3/R4 rule families are source-faithful and the (g)-provenance defect is remediated by a surgical, accurately-sourced, properly-attributed correction with no change to any encoded value.
