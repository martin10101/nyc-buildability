# M5-T177 reviews (every return kept unchanged)

- G2 orchestrator self-check at the material commit e3b0d8fa: the builder's commit touches 12 files, all inside the 13 allowed paths (the renderer untouched); LF sha256 of the files equal to the builder's return; lint clean; 163 tests passed (the reference cases and the two tests that read reference rows through the loader); the renderer's check passed; the size check has 0 failures; every file has one owner.
- G3 data-contract-verifier, pinned at e3b0d8fa: PASS, no required correction. It worked its own reading from the sealed folder before opening the case and reproduced the case's figures. One advisory: in the row real-lot-missing-facts, one missing fact that BOTH readings record (the block-frontage question of ZR 35-633(b) on 215 Place) is listed as reading 1's only.
- G4 qa-engineer, pinned at e3b0d8fa: PASS, no required correction. All seven scenarios reproduced in its own copy; its six mutation probes are caught. Two advisories: the work order's '33.32 (map outline)' back clearance for the later engine task (M5-T172, scenario S13) is given by neither reading (the case records 33.34 on the tax map and 35.31 on the city-map check); the two readings name different bases for the mapped street widths, so no street-width quantity is recorded.
- The three advisories are backlog DB-260 (not applied; none changes a recorded value).

Every reviewer is an AI agent; none is a human or professional review.

## G3 (data-contract-verifier)

G3 GATE REPORT — M5-T177 (data-contract-verifier), reference case `placement-building-b`, step P8

I am an AI agent (data-contract-verifier). This is an independent, read-only machine review, NOT a human or professional/legal review. Pinned head e3b0d8fa on task/wave24-report-v3 in /root/project/w-wave20 (verified an ancestor of live HEAD 9bef0b72; the working tree is clean and byte-identical to the pinned commit for the case, provenance, README, page and all reference_cases support/tests — empty `git diff e3b0d8fa` on those paths — so executed checks reflect the pinned content).

VERDICT: PASS (one ADVISORY finding; no REQUIRED corrections).

My own reading first (from the sealed folder alone, before opening the case/readings): plate = 20,150/3 = 6,716.67 sq ft/storey; tax-map footprint 100.76 x 66.66 = 6,716.66 (depth 66.66, 33.34 ft to the 100-ft back line), touching the NB front line + both relevant lines; GIS lot-70 area 10,387.99 sq ft (my shoelace matched), edges ~99.98 and ~103.88 → a ~3.12 ft frontage / ~313 sq ft area conflict, corner lot with NO rear lot line (settled), so the "back line" is basis-dependent; 60% split = apartment 12,090 (4,030/storey) + other 8,060 (2,686.67/storey) = 20,150. All of this reproduced the case exactly.

WHAT I CHECKED (all pass unless noted):
1. Provenance (check 1 / S1): provenance-17 body (header stripped, exactly 6 lines) sha256 = original return-reading-P8-1.md (65fe244c…); provenance-18 = P8-2 (cadbccf4…) — byte-for-byte. Headers state truly what readers had (sealed folder, 189 captures without notes, 18 settled answers, no program/repo/web) and name the pairing. Both end END-OF-REPORT. The step_p8 whole-file digest pins (7d6b923d… / 0e166f96…) match the committed files exactly, so a changed reading is caught.
2. Rule of agreement (check 2 / S3), row by row against both readings: plate 6,716.67; footprint 6,716.66/66.66; placement touches NB(full)/215 Place(66.66)/lot-1 side(66.66) at 0 ft, 33.34 ft clearance; GIS conflict 103.88 frontage / 99.97 depth / 64.66 plan depth / 35.31 back clearance / 64.66% share; lot-coverage 100% corner + 80% interior-or-through by portion; whole-lot coverage NOT KNOWN; rear yard NOT KNOWN (unresolved-law basis + missing adjoining lot-line fact); 60% allocation — every recorded value is given by BOTH readings on the same basis and precision. NOTE: the packet/S3 "33.32 map outline" was a stale pre-contract guess; both readings actually give 35.31 and the case correctly follows the readings. GIS frontage recorded 103.88 = reading 1 (103.88) and reading 2 (103.879→103.88 to the stated hundredth), transparently noted — acceptable. reading-2-only "66.67% of 10,075" is correctly attributed to reading 2 alone.
3. Law quotes (check 3): all 7 citations (23-322, 23-335, 23-362, 12-10-lot-corner, 23-344(a), 23-344(c)) are exact substrings of their canonical docs/research/zr-snapshots/v1 verbatim_excerpt and every content_digest matches (programmatic check, 0 problems). Nothing claims more than captured.
4. The measure (check 4 / S4): plate (6,716.67, ZFA/storey) and footprint (6,716.66, tax-map) are separate quantities, each recomputes exactly, 0.01 apart (within ±0.5), never forced to one; both rows carry the "plate = zoning floor area per storey; no gross-up, exclusions or wall-thickness conversion worked" label; physical floor plate is its own not_known row.
5. Placement/basis (check 5 / S6): placement on printed-tax-map; GIS used only as a conflict check (neither reading chooses a basis); every placement/coverage row names its basis and the Z1 condition; tax lot ≠ zoning lot stated repeatedly; "complies/feasible/buildable/optimal" appear only in negation; no program_result anywhere.
6. Area allocation (check 6 / S5): 60% of residential ZFA; 12,090+8,060=20,150; 4,030+2,686.67=6,716.67; all steps exact; no unit/room/wall/core placement (core/circulation named only as the composition of "other area").
7. Nine bases (check 7): every quantity carries exactly one of the nine bases; none mixes bases (programmatic check, 0 bad).
8. Older rows (check 8): `git diff e27bc2a0 e3b0d8fa -- cases/` shows ONLY placement-building-b.json changed (the other 11 case files byte-identical to the claim head). step-P7 PRIOR_ROWS_DIGEST moved (4285ac72→2b923207) solely because the new case joins the "prior" set, with a documented note that the 10 pre-existing non-short-block cases still hash to the old pin. Does not contradict the settled step-p3/p4/p6/short-block readings (corner lot, no rear lot line, 10,075 vs 10,387.99 conflict, by-portion coverage, Z1 rear-yard not known) — it carries them forward.
Suite/S7: reference_cases pytest 144 passed; render --check PASSED (byte-identical page); ruff clean; support .py all < 600 SLOC (check.py 520, lib 333, step_p8 176, render 313); modularity --check 0 failures / 796 files (no reference_cases file flagged).

FINDINGS:
1. ADVISORY — placement-building-b.json row `real-lot-missing-facts` (expected.value): the "215 Place whole-block-frontage Commercial-District" missing fact is attributed to "Reading 1 also records (reading 1)…", but BOTH readings record it (reading 1 Q7 and reading 2 Q7 each list §35-633(b) as NOT KNOWN). It should sit among the joint missing facts, not as a reading-1-only extra. This mis-buckets a shared qualitative observation; it creates no false settled value, no numeric effect, and does not feed M5-T172/T173 expected values. No other row has this issue; the symmetric reading-2-only extras (corner angle, ALLEY edge) are correctly attributed.

WHAT I COULD NOT CHECK: live re-fetch of the NYC DCP portal to re-verify the sealed/canonical captures (no web; captures are digest-pinned — I verified the case citations against the repo's pinned canonical snapshots instead); the full services/api pytest and full `ruff .` (ran the reference-case suite + render + modularity + scoped ruff, which is this task's scope — full CI is CI's job).

Recommendation: PASS. The single ADVISORY attribution fix is optional and may be folded into any later touch; it does not block acceptance.
END-OF-REPORT

## G4 (qa-engineer)

# M5-T177 — G4 QA gate report (qa-engineer, independent, read-only)

I am an AI agent acting as the independent G4 reviewer. This is an AI software/QA review of a draft AI reading, NOT a human or professional legal/zoning review. Agreement between AI readings is not proof.

VERDICT: **PASS** (no required corrections; two ADVISORY notes for the orchestrator).

Pinned head reviewed: `e3b0d8fa6a9548089218016f831c007d9315c412` (cherry-pick) on `task/wave24-report-v3` in `/root/project/w-wave20`; claim/base head `e27bc2a0`. Branch HEAD had already moved to `9bef0b72` — I worked from a `git archive e3b0d8fa` copy and git plumbing only. All work in my scratch `/tmp/claude-0/t177-g4/`; I wrote nothing to any repo, ran no server, touched no ports, ran no project_control except reads.

## Named checks (archive copy, lanes venv, PYTHONDONTWRITEBYTECODE=1, direct exit codes)
| Check | Result | Exit |
|---|---|---|
| `cd services/api && python -m ruff check .` | All checks passed! | 0 |
| `pytest -q -p no:cacheprovider tests/rules/reference_cases tests/spatial/test_lot_reach.py tests/scenario/three_answers/test_result_way_bridge_overlay.py` | 163 passed in 3.60s | 0 |
| `python tests/rules/reference_cases/r6b_reference_cases_render.py --check` | reference-case check PASSED (no issues) | 0 |

## Scenario results (independent)
| Scenario | How tested | Result | Exit |
|---|---|---|---|
| S1 provenance unchanged+pinned+changed caught | diff prov bodies vs raw returns; recompute LF-sha; mutation probe P4 | PASS | 0 |
| S2 both readings named + quotes in capture | independent re-derive all 7 citations; probe P1 | PASS | 0 |
| S3 not-settled stays not-known; value refused | probe P2 (lot-coverage-whole-lot) | PASS | 0 |
| S4 plate/footprint pinned, labelled, 9 bases | recompute + probes P3a/P3b; SLOC check | PASS | 0 |
| S5 allocation sums & recomputes; +1 caught | probe P5; recompute | PASS | 0 |
| S6 placement/coverage name basis+Z1 | probes P6a/P6b | PASS | 0 |
| S7 wired in; pages/rows byte-stable; <600 SLOC | git blob/dir diffs; digest reconstruction; suite | PASS | 0 |

## Eight brief checks (findings numbered)
1. **Provenance (PASS).** Files 17/18 are byte-for-byte equal to the raw returns `return-reading-P8-1/2.md` below a 6-line header (`diff` exit 0 both). LF-sha of each full file equals the digest pinned in `r6b_reference_cases_step_p8.py` (`7d6b923…`, `0e166f9…`). Header claims verified against the sealed folder: law captures = 189 (`ls law | wc -l`), facts = 8, `settled_by_earlier_readings.json` has exactly 18 answers, and `step-p6-worked#real-building-b` is absent — so "EIGHTEEN answers settled" and "real-building-b left out on purpose" are truthful. Probe P4 (one byte flipped below the header) → "digest changed" caught.
2. **Rule of agreement (PASS).** Independently confirmed every value row's figures appear in BOTH raw readings: plate 6,716.67; footprint 6,716.66 / 66.66 / 100.76; placement 0-ft touches + 33.34 back; coverage maxima 100%/80%; allocation 12,090/8,060/4,030/2,686.67. The four flagged difference points are handled correctly: (a) footprint whole-lot share → `lot-coverage-whole-lot` NOT SETTLED, per-basis shares 66.66% (tax)/64.66% (GIS) each kept separate, not smoothed; (b) GIS frontage 103.88 (r1)/103.879 (r2) recorded at 2 dp with both named, row NOT SETTLED; (c) coverage-by-portion → both reach same maxima, recorded as value `lot-coverage-max`. No value row rests on only one reading; no NOT SETTLED row is in fact jointly settleable (physical-plate, gis-conflict, whole-lot, rear-yard are each a genuine shared gap or unresolved basis).
3. **Law quotes (PASS).** Independently loaded each cited snapshot: all 7 citations are exact substrings (markup-stripped) of their `verbatim_excerpt`, with matching `content_digest_sha256` and `request_url`. Probe P1 (altered quote) caught, names the row.
4. **The measure (PASS).** `plate` 6,716.67 (20,150/3) and `footprint-tax-map` 6,716.66 (66.66×100.76) are separate rows/quantities, each recomputes exactly, 0.01 apart (≤ ±0.5), never forced into one; both carry the stated-measure label (probe confirms a dropped label is refused); `physical-plate-not-checked` is not_known; every quantity carries exactly one of the nine bases (probes P3a/P3b refuse missing/invalid basis; module set == `tools/research_record_check.py` QUANTITY_BASES).
5. **Placement (PASS).** Placement/coverage rows all name the printed-tax-map basis + Z1 (lot 70 alone); the GIS outline is a conflict check only (`gis-conflict-check` not_known, +3.12/+1.97/−2.00 subtractions recompute). `program_result_errors == []`. No positive compliance/feasibility wording — all five occurrences of complies/buildable/feasible/optimal are disclaimers/negations. "A tax lot is not a zoning lot" is stated.
6. **Area allocation (PASS).** 60% share on the 20,150 residential floor area: 12,090/8,060 total, 4,030/2,686.67 per storey; apt+other = total; per-storey = plate; all steps recompute; probe P5 (+1) caught. No unit/room/wall/core figure.
7. **One basis per quantity (PASS).** No quantity mixes bases; no mapped-street-width quantity is recorded (no `administrative_record`-basis quantity exists), so the reading1-vs-reading2 street-width basis-label disagreement does not surface as a recorded value.
8. **Older rows untouched (PASS).** The cherry-pick touches exactly 12 of the 13 allowed paths (render.py correctly left byte-identical), nothing outside scope. All 11 existing case JSONs and all existing rendered `.md` pages are byte-identical between claim head and pinned head (`diff -rq`; only the new case's 5 files differ, and the claim-head `placement-building-b.json` was a 100-byte placeholder). The step-P7 `PRIOR_ROWS_DIGEST` change is explained by the new case alone: I independently reconstructed the hash of the 10 pre-existing non-short-block cases and it still equals the claim-head pin `4285ac72…`. Support files all < 600 SLOC (check 591, lib 379, render 369, step_p8 196); none imports from `app`. `render.py` byte-identical to claim head (confirmed).

Extra verification: §23-341/23-343/23-434 ARE among the 189 captures, so the case's recharacterization of reading 1's imprecise "folder does not hold" into "in the folder but not read by reading 1" is factually correct; outer-court/MIH/Admin-Code are genuinely absent, matching reading 2. The joint "both readers did not have" list is correctly empty.

## ADVISORY (do not block T177)
- **A1 (33.32).** The case correctly records south offsets 33.34 ft (tax) / 35.31 ft (GIS) and the string "33.32" appears in neither reading (`grep` = 0 both). Downstream M5-T172 S13 anticipates 33.32 on the map-outline basis — a value this case does not support. Reconcile that scenario's expected value before M5-T172 runs; do not back-fill 33.32 here.
- **A2 (street-width basis label).** Reading 1 labels mapped widths "gis/administrative", reading 2 "administrative_record". Correctly not recorded as a case quantity; noted so later tasks don't adopt one label as settled.

## Could not check
- Full api suite / modularity / lane-path coverage are CI's / the producer's G2 job; I ran only the brief-named folders and verified SLOC directly. CI must read green on the accept head.

END-OF-REPORT
