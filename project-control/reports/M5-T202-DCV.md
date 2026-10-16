# M5-T202 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `e10c674505bfb97ff4e96a6bcdec99f05b42de67` (branch `task/wave29-scenario-drawings`, review copy `git plumbing at the frozen head`). Directives D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R088, R091, R092, R093, R094, R095, R096, R247.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - R247 orphaned-mounting binding (control-plane, orchestrator action — blocks calling D-094/R247 complete, NOT M5-T202's deliverable): R247's mounting obligation is unmet at this head and R247.applicability names no task that actually mounts (only D-094-BOOTSTRAP and M5-T202, which stays unmounted by design). When M5-T174 is contracted, append it to R247's applicability.task_ids (with the digest resync + provisional verification row), and keep R247 recorded as NOT discharged until M5-T174's mount is independently verified. Do NOT mark R247 "satisfied" for M5-T202 in a way that implies the component is mounted. (The qa-engineer raised the same coordination point.) - None required in the delivered code or tests of M5-T202.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in two transmissions (the first wrote the R247 row state outside the five states; on the orchestrator's request the verifier re-sent the whole return with that one line restated as PASS for this task's share; the first transmission is kept in the session folder as return-dcv-M5-T202-v1.txt), received 2026-10-16 02:03:39 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T202 (directive D-094, 8 bound rows)
VERDICT: PASS
(brief header said "9 rows"; the packet directive_refs, requirements.json applicability and verification.json all show exactly 8 rows cite M5-T202 — R088, R091, R092, R093, R094, R095, R096, R247. There is no 9th bound row. PASS here means M5-T202's deliverable is verified and acceptable; it does NOT mean R247's mounting obligation is discharged — see ROW R247 and REQUIRED CORRECTIONS.)
I am an AI agent; this is an independent, read-only verification, not a human or professional review.

(1) HEAD VERIFIED
 - I read the frozen head e10c674505bfb97ff4e96a6bcdec99f05b42de67 (branch task/wave29-scenario-drawings, /root/project/w-wave29) through git plumbing; working-tree HEAD advanced to b561450e (M5-T173 binding correction) while I worked, so every row/file read was pinned with `git show e10c6745:<path>`.
 - Submit head c4422294 is an ancestor of e10c6745; CI run 38836291821 at c4422294 = 21/21 jobs success (read-only gh).
 - The 6 behavior files are byte-identical (same blob ids) across the round-2 material commit f88bdc86 → submit head c4422294 → frozen head e10c6745.

(2) ROWS

ROW D-094-R088 — PASS (this task's share)
 - area-allocation.ts areaAllocationView returns kind "fitted_zones" for the benchmark, and AreaAllocation.tsx renders ZonesDrawing (two zones + one division inside the footprint), replacing the nothing-drawn state; S1 test asserts one area_zone_apartment/other/footprint/division each and data-apartment-fraction≈0.6.
 - The worked-scenario fixture recorded_215_16_northern_journey carries fitted:true and a placed 100.76×66.66 outline; the kernel-derived golden (report-parity-area-zones.json) is division_x 60.456, fraction 0.6, area 6716.6616 (I recomputed 0.6×100.76=60.456 and 100.76×66.66=6716.6616 by hand).
 - The authorization is the owner's "> Yes, add a simple two-zone illustration" (source-003-amendment.md), which this component now draws.
 - Stays open: the illustration is shown to users only once M5-T174 mounts the component (unmounted at the frozen head — S7 confirmed below).

ROW D-094-R091 — PASS (this task's share)
 - percent = Math.round(share*100) is read from the block (area-allocation.ts), never hardcoded; AreaAllocation.tsx renders exactly one "{percent}% apartment area" beside the drawing.
 - The drawn proportion (apartmentFraction) equals the share within 1e-6 (lib S1 test on the benchmark and the 82×82 square; qa-engineer reproduced bit-parity on concave L / triangle / negative-coordinate rings).
 - share is held to the 60–75% band (AREA_ALLOCATION_SHARE_MIN 0.6 / MAX 0.75, enforced before any draw); one explicitly stated percentage, drawing and calculation consistent — the owner's R091 words.
 - Stays open: user-visible only after the mount (M5-T174); a latent Math.round-vs-Python-round() half-integer divergence (code-reviewer finding 1) does not trigger at the benchmark or at any 2-decimal share, but is a web-vs-PDF parity item to carry to M5-T173/M5-T174.

ROW D-094-R092 — PASS (this task's share)
 - The methodology detail shows "Measure: Residential floor area" (AREA_MEASURE_WORDS = kernel _MEASURE_WORDS) and the conversion statement "plate = zoning floor area per storey; no gross-up, exclusions or wall-thickness conversion worked" — byte-equal to kernel _CONVERSION and to results-contract-checks.ts:64–66.
 - It also prints "Not checked: Physical floor plate (gross-up, exclusions, wall thickness)", so zoning floor area is explicitly NOT equated to the physical floor plate (the owner's R092 prohibition).
 - measure field AREA_ALLOCATION_MEASURE "residential_floor_area" == kernel _MEASURE; the component test pins the conversion byte-equal and asserts the caption does not contain it.
 - Stays open: the FINAL measure wording is owned by the not-yet-accepted M5-T173 sheet (kept as the kernel's bare words here, per packet path_notes); user-visible after the mount.

ROW D-094-R093 — PASS
 - ZonesDrawing emits exactly one data-role="area_division" line and one data-role="area_footprint" edge; S5 test asserts querySelectorAll("text") length 0 inside the zones SVG — no rooms, unit walls, counts, stairs or elevators are drawn.
 - Both zones carry one neutral fill var(--pt-color-selected); they are told apart by hatch, not colour (S5 asserts equal fills + two distinct pattern transforms); the FORBIDDEN-mark regex (room/unit wall/stair/elevator/apartments/units) finds nothing in either the bar or zones state.
 - The selector computes only the footprint split; it invents no apartment count or interior feature — matching the owner's R093 prohibition exactly.
 - Nothing stays open.

ROW D-094-R094 — PASS (this task's share)
 - area-allocation.ts draws zones ONLY when fitted===true AND placedRing returns a drawable ring; fitted===false returns kind "bar"; fitted===true with no/undrawable outline returns "unavailable" with the kernel's plain reason — never a bar mislabelled fitted (owner's R094 sequencing).
 - S3 test: fitted:false→bar (65%/35%, no footprint/zones), fitted:true placed→zones; S2 tests: not-placed / withheld / <3 vertices → AREA_REASON_NOT_PLACED, nothing drawn, one test per state.
 - The fail-closed branch strings are byte-equal to the kernel (I read both; api test reads 5 reasons from the kernel and asserts them verbatim in the TS source).
 - Stays open: the "simple proportional bar beside the building diagram" is positioned in the flow only when M5-T174 mounts the component.

ROW D-094-R095 — PASS (this task's share)
 - AreaAllocation.tsx renders one short caption `<p data-testid="area-allocation-caption">` = "Illustrative area allocation—not a floor plan" (one line, em dash, no full stop — S4 test); the methodology (measure/conversion/not-checked) sits in an expandable `<details>`, not the caption.
 - The conversion test asserts the caption text does not contain the conversion statement, so the explanation beside the drawing is the single caption only.
 - This satisfies "keep the explanation to one short caption" for the website surface.
 - Stays open: the literal "put methodology in the appendix" placement belongs to the report/PDF assembly + export (M0-T195 / M5-T173); on the unmounted website component the expandable detail is the analogue.

ROW D-094-R096 — PASS (this task's website share)
 - Geometry byte-equal: area-allocation.ts polyArea/clipX/divisionX (100-step bisection) and placedRing caps (1000 vertices, |coord|≤1e9 & finite, closing-vertex de-dup, <3→not_placed, zero-area→no_area) mirror kit/area_allocation.py _poly_area/_clip_x/_division_x/_placed_ring line-for-line (I diffed both sources); the golden is regenerated FROM the kit code (UPDATE_GOLDEN), never hand-written; qa reproduced bit-identical concave/triangle/negative-coord parity.
 - All 13 refusal reason strings are byte-equal between TS constants and the kernel's Unavailable text (I compared each; the api test reads the 5 outline/not-placed reasons from the kernel and matches them verbatim in the web selector).
 - Wording byte-equal across surfaces: AREA_ZONE_APARTMENT / AREA_ZONE_OTHER / AREA_ILLUSTRATION_CAPTION == docs/design/presentation-tokens.json wording == kernel presentation_tokens.py WORDING; hatch directions apartment rotate(-45) / other rotate(-135) equal the kernel's _defs (round-2 made the legend swatches reuse the zones' own SVG patterns, so swatch==zone==kernel by construction; the CSS bar is the chromium mirror, confirmed by the visual reviewer's render).
 - Stays open: the PDF/wiring side of "apply consistently" is M5-T173; the website is user-visible only after M5-T174 mounts; the only identified web-vs-PDF gap is the latent percent-rounding note (R091), which does not trigger at realistic shares.

ROW D-094-R247 — PASS (this task's share: the fitted branch built and ready to mount)
 - This task's share of R247 — the fitted branch built, tested and ready to mount — is real and verified: the fitted_zones branch renders correctly and both round-2 reviewers independently confirmed the component and that it is mounted nowhere.
 - The share is correctly scoped as preparation only: the packet title ("edits M5-T187's unmounted component only") and path_notes ("stays unmounted (M5-T174 mounts it)") make the mount M5-T174's deliverable, and "a component file alone does not establish website parity" is the owner's own R247 wording (source-028-amendment.md).
 - At the frozen head the component is mounted NOWHERE (git grep over apps/web/src: AreaAllocation imported only by its own test; areaAllocationView consumed only by the component + its test; the one other "AreaAllocation" hit is the pre-existing checkAreaAllocation schema validator) — so no part of the mounting obligation is, or should be, claimed here.
 - Stays open: the ENTIRE mounting obligation ("mounted under the flags" / "connect the appropriate existing components under the established feature flags"). R247.applicability currently lists only [D-094-BOOTSTRAP, M5-T202]; M5-T174 is not yet contracted/bound (the orchestrator has noted it will bind M5-T174 at its contract), so R247 must stay un-discharged until M5-T174's mount is independently verified — see REQUIRED CORRECTIONS.

(3) BINDING B1–B5
 - B1 (M5-T202 appended; no row text changed): VERIFIED. All 8 rows carry M5-T202 in applicability.task_ids at e10c6745. Each row's text quotes the owner's verbatim words unchanged (R088–R096 from source-003-amendment.md "owner-message-verbatim"; R247 from source-028-amendment.md), and the requirements body digest matches the manifest (see B2), so no body was silently edited. Caveat: I did not diff the exact contract commit that appended M5-T202 (digest + presence establish the binding; the control-plane CI job enforces append-only).
 - B2 (digest): VERIFIED at the frozen head. requirements_content_digest_sha256 recomputed (LF-normalized) = 4d6b292328bda425bc6395421e130e527c8732defbec5e96af8f137f9f7d6955 == manifest; requirements_id_digest_sha256 = 36f3b1e3902340b3f230249e0c47cc996d39a20424b4aab97a3147f1c1602ada == manifest; no locked id deleted (315 rows).
 - B3 (verification.json): VERIFIED. Exactly one M5-T202 row; applicable_requirement_ids = the 8; producer "frontend-engineer"; verifier ""; all 8 requirement states "pending"; reviewed_sha null. Correct provisional/pending shape awaiting this verdict.
 - B4 (evaluate_task_refs: applicable == cited): VERIFIED. The D-094 rows whose applicability includes M5-T202 are exactly {R088,R091,R092,R093,R094,R095,R096,R247} — identical to the packet's cited set.
 - B5 (nothing else applies uncited; gates): VERIFIED. Scanning every directive's requirements.json at e10c6745, only D-094 cites M5-T202 (the same 8 rows); no other active directive applies uncited. Gate records all PASS: G0 (orchestrator, administrative, reviewed_sha 47351b92 = contract head), G2/G3/G4 all at reviewed_sha c4422294 and the SAME content_manifest_sha256 08a3b3a9 (one content identity); G3 reviewer = visual-quality-reviewer (reviews.md holds the round-1 FAIL and the round-2 delta PASS); G4 reviewer = code-reviewer (round-2 code-and-test delta PASS), with the qa-engineer's round-1 G4 PASS also recorded. No open blocker references M5-T202. Observation (not a gap in the mechanism): R089 (zone labels) and R090 (caption text) are RENDERED by this component but are bound to the wording-owning tasks (M5-T187/M5-T193), not M5-T202; the component reuses the unchanged token constants and the S4 test pins them byte-equal to the JSON, so no uncited obligation is created — defensible, flagged for awareness.

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT a new review iff the blob-level predicate holds: the 6 behavior files keep these exact blob ids —
   AreaAllocation.tsx 58512ee597b40d2918d2cc87f70ceca58bddafb9;
   area-allocation.ts 0ab5e938490236303994cf394ede58929ea58179;
   __tests__/area-allocation.test.tsx 1d674be4f3575d251b2d0f489aec83e71a7f27a1;
   __tests__/area-allocation.test.ts b447d4446dc6bd970b3135f718a12fbf7677a5c3;
   test-support/report-parity-area-zones.json 9c2b66ee418e3f3421ea892ce0036f78ebdf5607;
   services/api/tests/drawings/kit/test_web_parity_area_zones.py 252a911b3706d7b39f79414b38b5eb58c1afe74d —
   AND the 8 rows' text and their M5-T202 binding stay unchanged (content digest 4d6b29…955, id digest 36f3b1…ada).
 - BROAD DISJOINT-PEER TOLERANCE: later commits may touch any OTHER file (other tasks' files under services/, apps/, packages/, docs/, .claude/, their packets/gates/reports; OTHER tasks appended to these same rows' applicability — e.g. binding M5-T174 or M5-T173 — with the digest resync and provisional verification rows that brings; new rows appended to D-094; ledger state), plus this task's own acceptance records and a main-line merge that changes none of the predicate files.
 - Already observed within tolerance: while I worked, b561450e (M5-T173 binding correction) touched rows R198/R200/R203/R204/R205/R277/R278 and resynced the directive digest — disjoint from M5-T202's rows and files; validate_directive_compliance.py --check returned exit 0 at that head.

(5) REQUIRED CORRECTIONS
 - R247 orphaned-mounting binding (control-plane, orchestrator action — blocks calling D-094/R247 complete, NOT M5-T202's deliverable): R247's mounting obligation is unmet at this head and R247.applicability names no task that actually mounts (only D-094-BOOTSTRAP and M5-T202, which stays unmounted by design). When M5-T174 is contracted, append it to R247's applicability.task_ids (with the digest resync + provisional verification row), and keep R247 recorded as NOT discharged until M5-T174's mount is independently verified. Do NOT mark R247 "satisfied" for M5-T202 in a way that implies the component is mounted. (The qa-engineer raised the same coordination point.)
 - None required in the delivered code or tests of M5-T202.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - I did not drive the web vitest or the api parity test to green myself (brief forbids the full api suite / test_directive_compliance.py and discourages heavy runs); I relied on reading the sources + the kit-derived golden + the byte-equality I reproduced, and on CI run 38836291821 (21/21 at c4422294) plus the two code reviewers' and qa-engineer's recorded reproductions. My geometry/reason/wording byte-equality findings come from reading both surfaces, not from executing them.
 - I did not perform a chromium pixel render of the component; the CSS-bar-vs-SVG-swatch "mirror" fact (apartment "/", other "\") is empirically the visual-quality-reviewer's gate — I verified only that the fitted swatches reuse the zones' own SVG patterns (so swatch==zone==kernel by construction) and that the bar derives its angle from the same diagonal constants.
 - I recomputed the content/id digests and confirmed the gate records' reviewed_sha and shared content_manifest_sha256, but I did not independently recompute the path-scoped content-identity manifest hash (08a3b3a9) from first principles; its consistency is enforced by validate_directive_compliance.py (exit 0) and the control-plane CI job, which I read green.
 - I did not diff the precise contract commit that appended M5-T202 to the 8 rows; presence in applicability + the matching content/id digests cover body integrity.
 - The latent Math.round-vs-Python-round() percentage divergence (R091/R096) is a reasoned edge case I did not exhaustively bound against the share schema's decimal precision; it does not affect the benchmark or any 2-decimal share.
END-OF-REPORT
```
