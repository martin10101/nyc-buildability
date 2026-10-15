# M5-T187 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `fdd0b7398ac6f225f4fc7ffc9d77fe151b71dca3` (branch `task/wave27-comparison-appendix`, review copy `git plumbing at the frozen head`). Directives D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R027, R088, R089, R090, R091, R093, R094, R095, R096, R098.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None. All 10 rows PASS for this task's share; B1-B5 and the gate records are consistent. The G3/G4/G5 advisories (the methodology "Measure:" prefix vs the PDF's bare words; inline styles vs a stylesheet; no cross-surface automated test for the refusal reasons; a per-row percentage-text assertion; the geometry caps that must bind where Part B draws zones) are non-blocking and are correctly carried to Part B / M5-T173.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-15T11:05:13Z, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T187 (directive D-094, 10 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier), read-only. This is an independent machine verification, not a human or professional review. I produced none of the work or records; I reproduced every item below from primary evidence (owner source files, the code/tests at the frozen head, git objects, gate records, the registry tools, and CI).

(1) HEAD VERIFIED
 - I read the frozen head fdd0b7398ac6f225f4fc7ffc9d77fe151b71dca3 on branch task/wave27-comparison-appendix in /root/project/w-wave20 (git rev-parse HEAD confirms it).
 - The 7 allowed-path material files are byte-identical across build 92fbc15e, submit 5625f420 and frozen fdd0b739 (git diff --stat empty), so the reviews conducted at 92fbc15e and the gate records stamped at 5625f420 describe the frozen-head content.
 - The branch is NOT merged to main and the task status is awaiting_gate (progress 95), so nothing was accepted, merged or deployed — no prohibited action.

(2) ROWS

ROW D-094-R027 — PASS (this task's share: web-validator URL-form parity only)
 - Owner source (source-001.md line 102/232): every page-8 law link must resolve to its exact section, not the zoning homepage; destinations checked in the exported PDF.
 - source-links-parity.test.ts is a self-contained 24-case table: officialZoningTextUrl accepts only /article-<roman>/chapter-<n>[/<section>][#<section>] on zoningresolution.planning.nyc.gov and rejects bare-host homepage, wrong host, http, query, port, credentials, non-roman article, 3-digit chapter, malformed section, extra segment, bad anchor, space, backslash, over-length and non-string.
 - I independently compared apps/web/src/lib/architect/source-links.ts against services/api/app/drawings/report/law_links.py official_zoning_text_url: identical https/host/no-query/no-port/no-credentials rules, identical path regex ^/article-[ivxlcdm]+/chapter-\d{1,2}(?:/\d{2}-\d{2,4})?$ and anchor rule — a genuine parity test, not a runtime parse.
 - OPEN: resolving each live law link to its section, connecting affected results to review-register entries, and checking destinations in the exported PDF — carried to M5-T159 / M5-T169 / Part B (this component is unmounted and renders no link).

ROW D-094-R088 — PASS (this task's share)
 - Owner source (source-003-amendment.md line 22): "Yes, add a simple two-zone illustration, with these requirements:".
 - The illustration now exists as the website component AreaAllocation.tsx with its selector areaAllocationView (area-allocation.ts), tested across every input state (area-allocation.test.ts input-state table, 15 cases; component 14; parity 24 — all green in CI).
 - It exists only in the form R089-R095 allow (bar when unfitted, honest placeholder when fitted, plain unavailable line on a garbled/out-of-range/inconsistent block), replacing the "nothing drawn" meanwhile state.
 - OPEN: mounting it on the scenario screen (Part B / M5-T174) and the PDF-kernel side (M5-T183).

ROW D-094-R089 — PASS (this task's share)
 - Owner source (line 24): label the zones "Apartment area" and "Other building area: core, circulation, walls and services."
 - area-allocation-tokens.ts: AREA_ZONE_APARTMENT="Apartment area" and AREA_ZONE_OTHER="Other building area: core, circulation, walls and services" — I confirmed both are byte-equal to docs/design/presentation-tokens.json wording.area_zone_apartment / area_zone_other.
 - The owner's sentence-final period is dropped per the design contract (label is not the sentence punctuation); this is faithful, not a weakening. S2 asserts parity in both directions (literal==JSON, rendered==JSON).
 - OPEN: the same labels read from the rendered PDF sheet is M5-T183's share.

ROW D-094-R090 — PASS (this task's share)
 - Owner source (line 25): caption it "Illustrative area allocation—not a floor plan."
 - AREA_ILLUSTRATION_CAPTION="Illustrative area allocation—not a floor plan" (em dash U+2014, no trailing period) is byte-equal to presentation-tokens.json wording.area_illustration_caption and to the owner's words.
 - S2/S4 assert the rendered caption equals the token and that exactly one caption appears (zero in the fitted placeholder).
 - OPEN: the caption on the rendered PDF sheet is M5-T183's share.

ROW D-094-R091 — PASS (this task's share)
 - Owner source (lines 26): one explicitly stated percentage from the 60-75% assumption; drawing and calculation consistent; shown beside it.
 - The selector returns percent=round(share*100) and apartmentFraction=share read from the block, never hardcoded (selector tests at 0.60/0.65/0.75; G4's mutation hardcoding percent to 65 reddened the 0.60/0.75 cases); the component prints one "N% apartment area" and the bar width equals the share (G3 measured 65/35, 60/40, 75/25).
 - Consistency fails closed: share<0.60 or >0.75 → unavailable, and apartment/total deviating from share by >0.5% → unavailable (verified in area-allocation.ts and its tests).
 - OPEN: the worked example against the settled 60% reading and the PDF geometry are M5-T177/M5-T183/Part B; the component is figure-agnostic (reads share from the block) so it cannot contradict placement-building-b.json's settled 60% share.

ROW D-094-R093 — PASS (this task's share)
 - Owner source (line 28): no rooms, unit walls, apartment counts, or invented stair/elevator locations.
 - S4 asserts, for every row {fitted∈[false,true] × share∈[0.60,0.65,0.75]}, the DOM contains no room / unit-wall / stair / elevator / apartments / units text; the bar state draws only two hatched segments, a legend and one caption (no footprint/zone/division element in the bar, confirmed in S1).
 - The zone label word "walls and services" is the owner's own R089 wording and is correctly not matched by the "unit wall" guard.
 - OPEN: nothing stays open for this task's web share; the PDF-kernel prohibition is M5-T183's share.

ROW D-094-R094 — PASS (this task's share)
 - Owner source (line 29): place zones inside the footprint only when the footprint is actually fitted; until then show a simple proportional bar beside the diagram.
 - The selector returns a bar when fitted:false; a marked placeholder (fitted_deferred) when fitted:true WITH a placed ≥3-vertex outline; and unavailable "...not been placed..." when fitted:true WITHOUT an outline (never a bar mislabelled fitted) — both states are tested (selector + component S3).
 - The component draws no footprint/zone/division in the unfitted bar state (S1), so no zone is ever drawn inside an unfitted footprint.
 - OPEN: the actual zones-inside-the-fitted-footprint drawing is deferred to Part B / M5-T173 (here an honest placeholder).

ROW D-094-R095 — PASS (this task's share)
 - Owner source (line 30): keep the explanation to one short caption; put methodology in the appendix.
 - The component renders exactly one caption (aa-caption); the measure, the G-14 conversion statement and the "not checked" line sit in a collapsed <details> methodology. S5 asserts the conversion statement is in the detail and NOT in the caption; S4 asserts exactly one caption.
 - OPEN: "methodology in the appendix" (the report's evidence appendix) is M5-T169's share; here the method sits in expandable on-screen detail.

ROW D-094-R096 — PASS (this task's share)
 - Owner source (line 32): apply the illustration rules consistently to the website and the PDF.
 - I compared the web surface with the PDF kernel services/api/app/drawings/kit/area_allocation.py: identical labels/caption tokens, identical percentage text "N% apartment area", identical conversion statement, and all 9 selector refusal reasons byte-equal to the kernel's Unavailable strings (I diffed each) — same words and same fail-closed behaviour.
 - The component is deliberately unmounted so the website never shows an illustration the PDF lacks until Part B mounts both in lockstep.
 - OPEN: the mounted same-placement/same-state parity (screenshots) and the "Measure:" prefix advisory (web "Measure: Residential floor area" vs the kernel's bare "Residential floor area", a non-parity-tested presentation string) are carried to Part B / M5-T173.

ROW D-094-R098 — PASS (this task's share)
 - Owner source (line 32): verify the rendered result for readability and consistency before marking it complete.
 - G3 (visual-quality-reviewer, M5-T187-reviews.md) independently rendered seven states to static markup and checked bar proportions, the single percentage, labels at the 14px contract floor, hatch-plus-text (zones distinguished by more than colour), the honest placeholder and the plain unavailable lines — recorded before completion; G4 and G5 also PASS.
 - The check is recorded in the gate reports at one content identity (reviewed_sha 5625f420) and predates any completion claim.
 - OPEN: the six-width real-preview readability check, before/after captures and the exported-PDF export-check record are Part B's at mount (ports and server are off-limits here).

(3) BINDING B1–B5
 - B1 PASS: contract commit b84b30b2 appended "M5-T187" to exactly the 10 cited rows' applicability.task_ids; the requirements.json diff shows only the 10 task_ids appends plus updated_at — no row "text" line changed.
 - B2 PASS: I computed directive_registry.sha256_text_artifact(requirements.json)=97029fcd1e0233f33c479d0ccf02f7b4bd30736bc71dd828d784d00402c1045d, which equals manifest.requirements_content_digest_sha256; validate_directive_compliance.py --check exited 0 at the frozen head.
 - B3 PASS: verification.json has exactly one M5-T187 row; applicable_requirement_ids == the 10 ids; every requirement state is "pending"; verifier is "" (producer frontend-engineer).
 - B4 PASS: reg.evaluate_task_refs(M5-T187) returned ok=True, applicable_ids == cited_ids == the 10 ids, with empty missing_ids/invalid_refs/unresolved.
 - B5 PASS: I scanned every directive's requirements.json — only D-094's 10 cited rows reference M5-T187; the packet cites only D-094; nothing else applies uncited.
 - Gates PASS: G0 PASS at contract head b84b30b2; G2 (orchestrator self-check), G3 (visual-quality-reviewer), G4 (qa-engineer), G5 (security-reviewer) all PASS at one content identity (reviewed_sha 5625f420, content_manifest_sha256 a7f68524057cbb8154e7c555a9946b114b0d9a98c3a5202536626d8db73119c4). CI run 38722562053 at 5625f420: 21/21 jobs success, including web (lint+typecheck+build), web-e2e (vitest+Playwright), modularity and control-plane. modularity_check.py --check exited 0 (this task's 3 source files are 168/166/36 lines; the warnings are pre-existing unrelated files).

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT a new review while this blob-level predicate holds: the 7 allowed-path files keep their frozen-head blob ids — AreaAllocation.tsx 3758bda868737ea4b5b837eb5663b6c24d0a2f7d; answers/__tests__/area-allocation.test.tsx 4047c5ce7e905d972a2e2737c410ab687d9238be; lib/architect/area-allocation.ts 3f5bc719d4e4d70de8175e03bf7d2d5a2dbe30c2; area-allocation-tokens.ts 519861752be2bda72af9e43c14ad756df70aeabf; lib/architect/__tests__/area-allocation.test.ts 925eb1a3cc8530c46959f02dabe8cd6b6bd7a62d; __tests__/source-links-parity.test.ts 4385a49bb73739222d69604698393e59ddf4afc4; reports/M5-T187-producer-report.md 4d692278156df3fd6991066644971db02c74df43 — AND the 10 rows' text and their M5-T187 binding are unchanged.
 - BROAD DISJOINT-PEER TOLERANCE: later commits may touch any other file (other tasks' files under services/, apps/, packages/, docs/, .claude/, their packets, gates, reports, other tasks' directive bindings, new rows appended to D-094, ledger state), plus this task's own acceptance records (verification.json M5-T187 row, gate records, state), plus a merge of the main line that changes none of the predicate files.

(5) REQUIRED CORRECTIONS
 - None. All 10 rows PASS for this task's share; B1-B5 and the gate records are consistent. The G3/G4/G5 advisories (the methodology "Measure:" prefix vs the PDF's bare words; inline styles vs a stylesheet; no cross-surface automated test for the refusal reasons; a per-row percentage-text assertion; the geometry caps that must bind where Part B draws zones) are non-blocking and are correctly carried to Part B / M5-T173.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - I did not run the web vitest/Playwright/lint/typecheck myself (the read-only guard blocks shell file-writes and I may not start servers); I relied on CI run 38722562053 (21/21 success at the byte-identical submit head) and read the test SOURCE to confirm the assertions match the code.
 - The rendered real-preview items (six-width readability, before/after captures, exported-PDF link destinations) are unmounted and the preview ports are off-limits; these are correctly deferred to Part B.
 - I did not recompute the gates' content_manifest_sha256 a7f68524 (no manifest-building tool run); I confirmed the four gate records carry one identical manifest and reviewed_sha and that the material blobs are byte-stable to the frozen head.
 - CI at the exact frozen head fdd0b739 (run 38723534585, CI workflow) was still in_progress at review time; fdd0b739 adds only control-plane records and the 7 material files are byte-identical to the green submit head 5625f420, so the green CI covers the reviewed content.
 - The settled independent R6B readings (placement-building-b.json etc.) I used as a consistency reference only (real share 60%); I did not re-derive them, per the brief.
END-OF-REPORT
```
