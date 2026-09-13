# G3 SUPPLEMENTAL RULING — M4-T014 snapshot (g)-provenance question

> Preservation note: saved VERBATIM by the orchestrator from the same G3 reviewer's agent-return
> channel (transport entity-decoding only). This ruling REVISES the reviewer's earlier verdict in
> M4-T014-G3-rule-content-review.md: the recorded gate result is now FAIL pending one surgical
> correction. The earlier PASS was issued before the tooling-hazard evidence existed; the
> revision on new evidence is the review system working correctly.

I have independently grounded the hazard in the owner-verified record. `docs/ARCHITECT_REVIEW_QUESTIONS.md:48-51` confirms the HTML-extraction channel "could NOT render this paragraph on two official mirrors across four attempts — the zr site's HTML render loses §23-421(g) in text extraction," and directs that "The rules pipeline must prove section completeness from an artifact that provably contains the full text ... never from HTML extraction alone." The snapshot's `capture_method` is exactly that HTML curl channel, and `9,500` is absent snapshot-wide.

## RULING: NEEDS CORRECTION — BLOCKING

The notes assert paragraph (g) content **without a source that could actually have seen it**, and the companion source-capture report presents that content as an in-task **verbatim §23-421 quote**. Provenance is **not** adequate as committed.

### Exact note text at issue
- `docs/research/zr-snapshots/v1/zr-23-421-r3-r4.snapshot.json` notes[2]: *"The 23-421 special provision permitting the reference plane up to 5 ft above the base plane applies ONLY to R1 and R2 Districts without a letter suffix (large or sloped lots); it does NOT touch the R3/R4 series..."*
- Same file notes[1]: *"...the sloping-plane (apex-point, <=80-degree pitch) geometry set forth in **paragraphs (a) through (g)** of 23-421..."* (the "apex-point / ≤80°" detail and the (a)–(g) lettering are also beyond the readable excerpt).
- `project-control/reports/M4-T014-source-capture.md:53-55`, presented **inside quotation marks** as a §23-421 quote: *"In R1 and R2 Districts without a letter suffix … the reference plane … may be located up to five feet above the base plane."*

### Provable source basis (why provenance is inadequate)
1. The snapshot's own capture channel is HTML curl: `source.capture_method = "rules_engineer_in_task_curl_capture_2026-09-13"`, `official_channel = "html"`.
2. Owner-verified tooling hazard (`docs/ARCHITECT_REVIEW_QUESTIONS.md:48-51`): HTML extraction loses §23-421(g) on both mirrors across four attempts. So the capture channel **provably could not read (g)**.
3. Reproduced: `verbatim_excerpt` (637 chars) contains only the opening list + framing + 25/35 caps + generic sloping-plane sentence; `9,500`/`(g)`/`five feet` are absent snapshot-wide. The excerpt stops before (a)–(g).
4. The true basis is prior-task memory: `.claude/agent-memory/rules-engineer/zr-r3-r4-height-setback-source-facts.md:29` carries the "5 ft reference plane … R1/R2-without-suffix" fact, and its header (lines 9-10) says these are an analogue of the torn-down R1/R2 facts that "now live in blocker B-023." The snapshot cites **none** of this — no memory, no B-023, no print/PDF artifact.
5. The note is also **materially incomplete**: owner-verified (g) conditions it on `≥9,500 sq ft` AND (`≥100 ft width` OR `≥5% slope`) (`ARCHITECT_REVIEW_QUESTIONS.md:40-56, 88-90`); the note reduces those to an informal "(large or sloped lots)" and drops the quantitative thresholds — so a downstream B-023/G6 reader consulting this hash-guarded snapshot would be misled about the provision's actual triggers.

Why not "adequate as committed": the readable (a)–(f) + section framing do **not** support the specific (g) assertions (5-ft value, no-suffix scope, "(a) through (g)" lettering, ≤80°/apex-point geometry); the notes trace to unnamed prior-task memory whose own (g) provenance is the same unrenderable HTML portal; and the source-capture wraps it in quotation marks as a §23-421 quote — a provenance claim the channel cannot support. This is precisely the "never guess/assert source meanings" (principle 3) and "every material fact retains provenance" (principle 2) prohibition, and it contravenes the explicit owner directive to prove §23-421 completeness from a full-text artifact, never HTML extraction alone.

### Required correction (surgical; no R3/R4 value changes)
In `zr-23-421-r3-r4.snapshot.json` notes and `M4-T014-source-capture.md`: either (a) remove the (g)-content assertions, or (b) add an explicit provenance qualifier that §23-421(g) was **not** obtainable via this HTML capture channel (which loses (g)), name the actual basis, mark the 9,500/width/slope conditions as owner-verified-elsewhere (not captured here), and drop the quotation marks that imply an in-task §23-421 quote. Per the owner directive, §23-421 section-completeness must be evidenced from a full-text (print/PDF) artifact before any rule citing this snapshot advances toward G6.

## Revised M4-T014 G3 verdict

### VERDICT: FAIL (single BLOCKING provenance correction above; all other scenarios PASS)

My earlier PASS was issued before the tooling-hazard evidence was available. With that evidence independently reproduced, one deliverable of this task (the `zr-23-421-r3-r4` snapshot, plus the source-capture report) carries a BLOCKING provenance defect and cannot be accepted as-is. Everything else stands.

**Folded into S1/S5 (the coordinator's (a)/(b)/(c)):**
- **(a) Excerpt posture — ADVISORY (subsumed by the BLOCKING item):** the field name `verbatim_excerpt` and notes[1]'s reference to "paragraphs (a)–(g)" signal partiality, but the artifact nowhere discloses that the capture **omits/could-not-render** (a)–(g). A qualified reviewer could read the excerpt + notes as a full-section reading. This ambiguity is what makes the (c) assertions dangerous; fixing (c) with the disclosure above resolves it.
- **(b) No R3/R4 value depends on out-of-excerpt text — CONFIRMED / PASS.** The encoded caps (pitched 25/35; flat 35 for R3-2/R4; 25 for R4B) are all inside readable excerpts; (g)'s 5-ft provision is R1/R2-no-suffix only (out of scope, B-023) and is encoded nowhere; the sloping-plane geometry is a typed `documented_limitation` gap. **S1 value-fidelity for R3/R4 remains sound and needs no change.**
- **(c) Notes assert (g) content without a source that could see it — BLOCKING** (ruling above).

**Unchanged from my prior report (all PASS, independently reproduced):** S1 R3/R4 value fidelity; S2 typed separation / schema unchanged; S3 R3/R4 gaps + `building_type` fail-closed (ADVISORY-1 for G6); S4 isolation (90 tests bind: 90 passed, full rules suite 458 passed); S5 draft posture + no buildable/feasible/massing/compliance language (ADVISORY-2); S6 CI 18/18 green at material-identical `6fc8a878`, `modularity_check --check` EXIT 0; byte-identical canonical/bundle parity; no producer write outside allowed_paths.

**Net:** the R3/R4 rule families are well-built and source-faithful; the task fails this gate solely on the (g)-note provenance violation in the `zr-23-421-r3-r4` snapshot + source-capture report. The correction is a labeling/provenance fix (est. a few lines across two files) and requires no change to any encoded rule value. On re-submission with the qualifier added (and, per owner directive, §23-421 completeness evidenced from a full-text artifact), the item clears and the task returns to PASS.
