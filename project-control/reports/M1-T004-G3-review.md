# M1-T004 G3 — reviewer's return (verbatim preservation)

> Provenance: complete final return of the code-reviewer for M1-T004 G3, received 2026-07-16 via the agent-return channel; saved verbatim by the orchestrator (transport entity-decoding only) per the report-preservation rule in `.claude/rules/project-control.md`.

---

# M1-T004 — G3 Independent Human-Style Walkthrough Gate Report

- **Task:** M1-T004 — Official-source research: NYC Zoning Resolution text corpus
- **Gate:** G3 (independent walkthrough)
- **Reviewer:** code-reviewer (independent; did not produce the work; did not run G1)
- **Review date / live re-run date:** 2026-07-16
- **Commit reviewed:** ddebcca (main checkout; post-C1–C9)
- **Verdict:** **PASS** — zero defects
- **Method:** Read order per G3 discipline — task packet S1–S5 first, deliverables second, G1 report third, producer report LAST. Verified all nine G1 corrections against the G1 §5 specs with line evidence in both deliverables; ran the stale-marker/OQ coherence pass (the M1-T001 D1–D3 defect class); re-ran the G1-recommended live probes from this sandbox (KB-scale only; giant §12-10 print route not touched); assessed downstream M3 contractability.

## 1. Corrections C1–C9 — ALL APPLIED (verified against G1 report §5, exact locations)

| C | Verified applied at | Result |
|---|---|---|
| **C1** | Doc §2.1:40 (corrected rendering bullet); §3.3:122–127 (full endpoint spec + OQ-9/OQ-10 mis-cite fixed); §3.2:116 (OQ-3 narrowing); §4.4:186 (third namespace); §8:260/266. Registry `fields_available.structure`:32; `open_questions`:63/69 | ✅ |
| **C2** | Doc §3.4:133–138; §2.6:94; §5.6 item 5:218; §8 OQ-2:259; §9 E18:294 (marker removed); header:7 post-G1 note. Registry `known_limitations`:50; `fallback_source`:59; `open_questions`:62 | ✅ |
| **C3** | Doc §2.4:69; §5.5:210 full rewrite. Registry `known_limitations`:56 | ✅ |
| **C4** | Doc §2.3:61; §9 E14:290 | ✅ |
| **C5** | Doc §1:19; §3.3:120; §8 OQ-10:267. Registry structure:31; `open_questions`:70 | ✅ |
| **C6** | Doc §6 ZR-F8:235 | ✅ |
| **C7** | Doc §2.2:49; §9 E2:278 | ✅ |
| **C8** | Doc §4.3:168 (quotes); §4.3:170 (FROM variants ×95/×5/×1/×4/×6 + node identity); §6 ZR-F3:230 | ✅ |
| **C9** | Doc §1:16; §8 OQ-7:264. Registry `known_limitations`:54; `open_questions`:67 | ✅ |

The M1-T003 D1 lesson (correction applied to doc but not the machine-consumable registry) was checked correction-by-correction: **every registry-relevant correction (C1, C2, C3, C5, C9) is present in `zoning-resolution.json`**, not just the doc.

## 2. Coherence pass

- Stale-marker grep: `NEEDS G1 RE-VERIFICATION` hits the M1-T004 doc at exactly one place — line 7, the discipline definition, with the post-G1 "none remain outstanding" note. Zero hits in `zoning-resolution.json`. (Producer report retains markers at :33/:56 as the intentional historical record, superseded explicitly by its §10:107.)
- OQ ledger: doc §8 and registry agree entry-for-entry — OQ-2/OQ-9 RESOLVED, OQ-3/OQ-7 NARROWED, OQ-10 PARTIALLY RESOLVED, OQ-1/4/5/6/8/11/12 OPEN — exactly the G1 §4 adjudication. No marker contradicts a resolved OQ; the M1-T001 D1–D3 defect class is absent.
- Non-defect observation: registry `known_limitations`:47 could cross-reference the OQ-3 narrowing at `open_questions`:63 — cosmetic; no supersession, no contradiction.

## 3. Live re-run results (2026-07-16; KB-scale only)

| # | Probe | Expected | Actual | Result |
|---|---|---|---|---|
| R1 | Homepage banner grep | banner verbatim, May 20 2026 | Byte-identical | ✅ |
| R2 | /article-i/chapter-1/11-02 Last-Amended | time element, 1961-12-15 | Byte-identical markup | ✅ |
| R3 | /jsonapi | 404 | 404 | ✅ |
| R4 | /node/18523?_format=json | 406 | 406 | ✅ |
| R5 | HEAD Chapter 1.pdf | 200, 149,858 B, LM 2026-06-23 00:00:38 | Exact | ✅ |
| R6 | amendment endpoint id 22740 | 200, application/json, 4,230 B; CoY / N240290ZRY / "Effective Date" | 200, 4,230 B (byte-identical size); all three strings present | ✅ |
| R7 | /article-xv (missing case) | 404 | 404 | ✅ |
| R8 | nyc.gov zoning-text.page (failure case) | 403 | 403 | ✅ |

§12-10 print route deliberately not requested. Coverage: normal (R1/R2/R5), boundary (R6), missing (R3/R7), failure (R4/R8).

## 4. Owner-directive check — PASS

Registry `known_limitations`:53 carries the directive: amendment-history AJAX endpoint is monitored OPTIONAL ENRICHMENT with graceful fallback only; truth chain = server-rendered section HTML + /recently-adopted + dated snapshots; never sole source; health-monitored like entity-print. Doc §3.3:127 consistent ("never a guaranteed API"); §5.6 M3 priority order does NOT include the endpoint in any truth channel; registry structure:32 repeats the caveat. No text anywhere promotes the endpoint to a dependency. **Consistent.**

## 5. Downstream usability (M3 contractability) — YES

M3 legal-corpus ingestion can be contracted without re-research: channels enumerated and tiered, hierarchy model complete for Article I depth (full inventory deferred to OQ-5 at crawler build), version-pinning contract defined, 14-fixture pack with C6/C8 refinements, connector plan (§7), honest 7-item residual set.

## 6. Hygiene — PASS

Deliverables KB-scale text (~30 KB + ~13 KB); zero repo binaries; PDF claims HEAD-only; this review fetched ~150 KB transiently, temp file deleted. OQ-11 correctly remains OPEN for qualified-human/legal review — no agent closed it.

## 7. Scenario verdicts

S1 PASS (channel set complete incl. enrichment-only endpoint); S2 PASS (banner/stamps live-reproduced; OQ-3 narrowed not closed); S3 PASS (hierarchy + §12-01(j) + FROM variants + per-definition nodes; gaps ledgered); S4 PASS (discrepancies + PRD §8 priority order argued from evidence); S5 PASS (403s/404s honest; nothing promoted).

## 8. Defects

**None.**

## 9. M3 carry-forwards (must appear in the M3 legal-corpus ingestion packet)

1. Amendment-endpoint framing (OWNER DIRECTIVE): optional enrichment, graceful fallback, truth chain = HTML + feed + snapshots; health-monitored; never a dependency.
2. Hierarchy model: article → chapter → section; CC-NN[N[N]] numbering, 3-digit prefixes from 101-00; ALL-CAPS heads; chapter gaps real (OQ-5 at crawler build; do not infer continuity); appendices B–K + Preamble /node/79; no Appendix A (OQ-1).
3. §12-01(j) cross-reference scope rule (4-digit = subtree, 5-digit = exact; shifted for 101-00+) + §12-01(b) text-controls-over-tables in every extraction path.
4. FROM-variant parsing: 5 prefix variants with sec-link-inline span wrap; ZR-F3 asserts all.
5. Per-definition nodes: node--type-defined-term with about="/node/{nid}", id="term-{name}", own Last Amended + applicability notes.
6. Three identifier namespaces: section number, Drupal node ID, section-entity ID — never conflate.
7. Snapshot archiving: zr-snapshot-archiver downloads each new /zr-downloads snapshot (72–85 MB) on a Render worker into source-pdfs; filename-tolerant manifest diff (ZR-F11); OQ-12 verified at archiver build; banner date = legal currency, PDF Last-Modified = generation timestamp.
8. OQ-11 is human/legal: gates any "verified" labeling policy; never closed by agents.
9. Fixture discipline: raw-capture only (summarizer hazard, C3); search connector uses search_term with results-region assertions + positive control (C6); rate discipline on the 504-prone shared Pantheon host; OQ-4 and OQ-8 block their respective M3 sub-tasks.

---

**VERDICT: PASS** — C1–C9 all confirmed applied in both deliverables; live re-runs R1–R8 all reproduced, several byte-exact; owner-directive check PASS; defects: none; M3 carry-forwards enumerated. Recommend the orchestrator record G3 PASS and proceed to acceptance, injecting §9 into the M3 packet.
