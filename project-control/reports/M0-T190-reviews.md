# M0-T190 review record

Every return below is unchanged, as each reviewer sent it. All reviewers are AI agents; none is a human or professional review.

## Heads and identity notes

- G1 reviewed the records and the evidence pack at `1b41c813`. Its one required correction (F1, NB-01's E1 excerpt) was applied at `882ffd43` as NB-01 revision 2, and the same reviewer confirmed that delta (G1 delta, below); the G1 reviews are recorded inside each record. Between `1b41c813` and the gate head, the other four records changed only by their added review block (G1 delta, item c).
- G3 and G5 reviewed `7ec7c5ec`. Later commits touch only the evidence records (`882ffd43`, `6f6d3a90`: the G1 correction and review blocks), the verification-sessions report (`6f6d3a90`), the producer report and the backlog (`77da21dd`) and project-control files; none of the files in G3's or G5's scope (the check and its tests, the hook and its tests, the budget check, the CI workflow, the data files) changed after `7ec7c5ec` (`git diff --stat 7ec7c5ec..<gate head> -- tools .claude/hooks .github docs/research/owner-research` is empty).
- G4 reviewed `6f6d3a90`; after it only the producer report, the backlog sweep and project-control files changed.
- Advisory findings not applied are recorded in the backlog as DB-235 (hardening notes) and DB-236 (a stale line in the handoff profile).

## G1 data and sources (data-contract-verifier), at 1b41c813

# G1 DATA & SOURCE REVIEW — M0-T190 (data-contract-verifier)

Frozen head reviewed: `1b41c813a92fd28f15c1c5677d825f4b99a2758d` on `task/research-verification-rules`. Worktree `/root/project/w-rv` HEAD verified equal to the frozen SHA. Read-only; no edits/commits/control-plane commands. Scope: the five evidence records + evidence pack (RQ-009). Method followed the brief in order; I opened every decisive official source myself before trusting any record.

**VERDICT: G1 = PASS with required corrections.** Per record: NB-01 agrees (one REQUIRED provenance-precision fix), NB-02 agrees, NB-03 agrees, NB-04 agrees, NB-05 agrees. No report number or product code changed.

---
## Step 1 — NB-05 worked INDEPENDENTLY, before reading the record or code
Sources I fetched live (browser UA): ZR 23-52 (zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52), ZR 12-10 (…/article-i/chapter-2/12-10), and PLUTO 64uk-42ks QN/7334/70.
- PLUTO lot 70: `zonedist1 R6B`, `overlay1 C2-2`, `cd 411` (Queens CD 11), `lotarea 10075`, `residfar 2.00`, `affresfar 2.40`; `spdist1/2/3` absent (null = no mapped special district).
- ZR 12-10 (live, verbatim): "special density areas … shall include: (a) the Manhattan Core; and (b) the Special Downtown Brooklyn District." "The 'Manhattan Core' is the area within Manhattan Community Districts 1, 2, 3, 4, 5, 6, 7 and 8."
- ZR 23-52 (live, verbatim): factor **680**; "Fractions equal to or greater than three-quarters … shall be considered to be one dwelling unit"; **no** factor for developments/enlargements in special density areas, qualifying senior housing, or the listed conversions.

My expected answer (written before reading NB-05):
1. **Special density area? NO.** Lot 70 is Queens CD 11, not Manhattan Core (CDs 1-8) and not the Special Downtown Brooklyn District; PLUTO shows no special district.
2. **Applicable 23-52 paragraph:** the "all other types" paragraph → factor 680, ≥0.75 rounding.
3. **Units at 20,150 sq ft** (= 10,075 × 2.0): 20150/680 = 29.63 → **29 DU** (0.63 < 0.75, rounds down).
4. **Boundary:** 20,230/680 = 29.75 → 30; 20,229/680 = 29.7485 → 29; 20,400/680 = 30 exactly.
5. **Exception:** qualifying senior housing → no factor (cap not applied). **Counterexample:** a Manhattan CD 9 lot is outside the Manhattan Core (CDs 1-8 only) → still subject to 680.

## Step 2 — NB-05 record vs my answer, and program behaviour
The record matches my independent answer on every point, including the identical boundary arithmetic (20,230/20,229/20,400). E1/E2/E3 excerpts are verbatim to the live ZR text; document_dates correct. Code checked:
- `services/api/app/scenario/three_answers/engine_conditions.py` `special_density()` (lines 171-178): `NOT_IN_ONE → (False, USER_STATEMENT)`; any other/no statement → `(True, NOT_KNOWN)` = "inside one". 
- `r6b_dwelling_units.rule.json`: applicability guard `{"not":{"equals special_density_area true}}` (so True → not applicable → withheld); factor 680; threshold 0.75; qualifying_senior_housing → not applicable; qualifying_affordable_housing → computed but professional_review_required.
Record's **current behaviour** description (no statement → "inside one" → rule not applicable → limit withheld) and **DB-231** future behaviour (derive flag from borough/special-district; still withhold if unread) are both accurate; DB-231 is OPEN in `docs/DISCOVERY_BACKLOG.md:361`. **Dependency assessment is right.** code_identity hashes in the record equal the current files (643137bb…, 404179f2…). Verdict: **agrees.**

## Step 3 — NB-01 to NB-04 (live re-fetch + per-entry checks)
Live re-fetches confirmed:
- ACRIS Legals 8h5j-fqxa doc **2022031600431001** → indexed against borough 4 block 7334 lots **1 and 70** (215-10 / 215-16 Northern Blvd), good_through 2022-03-31. Matches NB-01 E1.
- DOB **440608941** (ic3t-wcy2) → NB, PERMIT ISSUED, existing 0 / **proposed_zoning 39934** / **construction 45388**. Matches NB-02 E1 exactly.
- ACRIS Master (acris_master_all.json) confirms every doc fact: DECL 2022031600431001 dated 2022-03-16 recorded 2022-03-22 CRFN 2022000121661; CERT 2022020201551001 & ZONE 2022020201551002 (2022-02-08); 2016 CERT/ZONE; 2018 DEED.
- ZR 23-344 live: (b) "whenever a front lot line … coincides with the street line of the short dimension of a block, no rear yard shall be required within 100 feet …" and (c)(3) "In R6 through R12 Districts, no rear yard shall be required where such rear lot line coincides with a side lot line of an adjoining zoning lot." Both verbatim to NB-03 E1/E5; full (a)-(d) chain matches.
- ZR 12-10 live: "short dimension of a block" (< 230 ft, last amended 12/5/2024), "rear lot line" and "side lot line" (both last amended 12/15/1961) — all verbatim to NB-03 E2/E3/E4 with correct dates.

**NB-01 — agrees** (one REQUIRED fix, F1). research_status `access_blocked` is honest (searches name the blocked instrument + next step); `kind index_entry` honest; conclusion correctly says the zoning lot is unconfirmed and an index entry does not establish an instrument. Lot-area quantities (70=10,075; 1=9,925; sum 20,000 flagged "not a zoning-lot area") correct.

**NB-02 — agrees.** `searched_not_found` honest (searches name the missing ZD1/PW1 schedule + next step). E4 PW1 guide (saved_copy null) explicitly states it was NOT re-fetched/re-read by the orchestrator and its SHA is in the manifest — honest; I confirmed the SHA + URL are in source-manifest.json. Reading correctly stays `not_determined` (double-count risk stated, not asserted). Figures match live DOB.

**NB-03 — agrees with the conditional no-rear-yard reading.** The (b) reading is sound: the Northern Blvd blockfront (200.01 ft tax / 203.13 ft GIS, both < 230) is a short dimension of a block; with ~100 ft depth the lot sits within 100 ft of that street line, so no rear yard under (b). The ~0.03 ft depth margin (99.97 GIS vs 100) is honestly flagged as survey-dependent. The (c)(3) side-lot-line alternative for neighbours (lots 11/61) is a reasonable secondary path, properly conditioned on the neighbours' tax-lot lines being their zoning-lot lines; note (b) alone is dispositive for a ≤100-ft-deep lot and (c) only bites on any portion beyond 100 ft — the record's hedging captures this. `interpretation_awaiting_review` honest (non-empty interpretation; "not a DOB determination").

**NB-04 — agrees.** `conflicting_evidence` honest with real, non-empty conflicts (recorded area 10,075 vs GIS 10,387.99 = 3.11%; frontage 100.76 vs 103.88; appdate 2017-03-22 vs 2017-04-07). Correctly keeps GIS outline for display only and recorded area for zoning (consistent with the mappluto_geometry vs mappluto_lot_outline split); nice honesty note that 100.76×100=10,076≠10,075. Survey (Buckley 2017-02-21) correctly named as settling evidence.

## Step 4 — data-file integrity
All **33** `data/` files equal their plain-bytes SHA-256 in `source-manifest.json` (33 OK / 0 missing / 0 mismatch). Additionally: all **27** record `saved_copy` SHAs match (LF-normalized), null↔null consistent; all three not-kept PDF SHAs (PW1 guide; tax maps 2017 & 2021) are present in the manifest with URLs matching the records; all **10** record `code_identity` hashes equal the current files (`code_current` true for every record). VERIFICATION.md's 2026-10-10 re-check and the 2026-10-11 data-restore correction (33/33 equal) are accurate and match my checks. RQ-009 links NB-01…NB-05 with status labels matching each record.

## Step 5 — S8 (no report/product change)
`git diff --name-only origin/main..<head> -- services apps packages` = **0 files**. `.claude/settings.json` and `.claude/agents/` unchanged. The diff touches only the task's named governance/docs/data paths. **S8 PASS.**

---
## FINDINGS
- **F1 — REQUIRED (provenance precision), NB-01 E1** — `docs/research/evidence-records/NB-01-zoning-lot-instruments.json:25`. The E1 excerpt states document types (CERT/ZONE/DECL), "dated"/"recorded" dates, and CRFNs, but E1's URL (8h5j-fqxa) and saved_copy (`acris_legals_keydocs.json`) are the ACRIS **Legals** dataset, which contains none of those fields — they live only in E2's **Master** saved_copy (`acris_master_all.json`). All facts are independently verified TRUE against the Master, and the "indexed against lots 1, 70" claim IS fully supported by E1's own saved copy. Fix: attribute the type/date/CRFN to E2 (or trim E1's excerpt to Legals fields). Does not change the record's conclusion or honesty.
- **F2 — ADVISORY / completion context, README** — `docs/research/evidence-records/README.md:15` says the structural check "is `python3 tools/research_record_check.py --check` (run in CI)," but at this head that tool and `tools/test_research_record_check.py` are 1-line placeholders ("Placeholder (M0-T190)…") that produce no output, and `.github/workflows/ci.yml`/the hook/budget are not in the diff. This is expected: the packet is at **50% / status claimed** (orchestrator records committed; builder increment for the checker/hook/budget/CI still pending). Not a G1 data-review defect, but scenarios S1-S4 (G3/G4) and the README's "run in CI" claim are unmet until the builder increment lands — confirm before task acceptance.
- **F3 — ADVISORY (trivial), NB-02 E5** — the C-of-O excerpt is truncated mid-field ("06/03/26 1:"); honest raw dataset snippet, saved_copy SHA matches. No action required.

## G1 GATE VERDICT: PASS with required corrections
The five records are source-accurate (every decisive quote verbatim to the live official text), honestly labelled (statuses and `kind`s match the evidence; nothing claims more than it proves; nothing Verified), provenance-intact (all manifest/saved_copy/code SHAs verified), apply ZR 23-52 / 23-344 / 12-10 correctly, and change no report number (S8). Apply F1 before acceptance; address F2 via the pending builder increment; F3 optional.

END-OF-REPORT

## G1 delta (same reviewer), at 882ffd43

# Delta review — M0-T190 at head `882ffd431e9d` (data-contract-verifier)

Read-only; no edits/commits. The live worktree `/root/project/w-rv` HEAD is now exactly `882ffd431e9d`, and its `tools/research_record_check.py` + `docs/research/evidence-records/*` blobs are byte-identical to that commit (`git diff --stat 882ffd43 -- …` empty), so running in place is equivalent to a clean checkout. (`git worktree add` is blocked by the read-only guard, so I used the in-place HEAD instead.)

**(a) NB-01 revision 2 — PASS.**
- E1 (Legals, `acris_legals_keydocs.json`) excerpt now quotes only Legals fields: "indexed against lots 1, 70 (partial_lot E, easement N, air_rights N)" for each of the three 2022 documents. The saved copy carries exactly those values for all three docs (lots {1,70}, partial_lot E, easement N, air_rights N). Match.
- E2 (Master, `acris_master_all.json`) now carries type/document-date/recorded-date/CRFN for the three 2022 docs (CERT 2016-08-04/2022-02-08/…59133; ZONE 2016-08-09/2022-02-08/…59134; DECL 2022-03-16/2022-03-22/…121661) plus the 2016 CERT/ZONE and 2018 DEED; all equal the Master saved copy.
- The observed fact appends "(lots from E1; type, dates and CRFN from E2)". Nothing else in NB-01's meaning changed — the diff is only the revision bump (1→2), the E1/E2 excerpts, that provenance note, and the added review block.

**(b) Review entries NB-01..NB-05 — PASS.** Each records reviewer `data-contract-verifier`, `reviewed_revision` 1, verdict `agrees`, with `reviewed_code_identity` equal to the current code files (10/10 hashes verified LF-normalized). The findings faithfully state my review: NB-01 (F1 required, corrected in rev 2); NB-02 (DOB re-fetch, searched_not_found honest, PW1 not re-read, F3 truncated C-of-O); NB-03 (23-344(b)/(c)(3) + 12-10 defs verbatim, (b) decides a ≤100-ft lot, (c) only beyond 100 ft); NB-04 (conflicting_evidence, real conflicts, recorded-for-zoning/GIS-for-display); NB-05 (independent 29-unit/boundary/senior-housing/Manhattan-CD9 work + current and DB-231 behaviour). None misstates me.

**(c) NB-02..05 changed only by the review block — PASS.** For each, the sole removed line is `"agent_reviews": [],` and `revision` stays 1; no other field changed.

**(d) `python3 tools/research_record_check.py --check` at 882ffd43 — PASS.** Output: NB-01 `review_state=stale` (review covers revision 1, record is revision 2); NB-02..05 `review_state=current`; all `code_current=True`; final line "PASS: every record is structurally valid…"; exit code 0.

All of (a)-(d) PASS. Clear to record the second NB-01 review entry for revision 2 citing this delta.

END-OF-REPORT

## G3 code (code-reviewer), at 7ec7c5ec

# G3 code review — M0-T190 (code-reviewer)

Task: M0-T190 research-and-verification workflow (D-093). Frozen head reviewed: `7ec7c5ec2cee7de6a21b755f004e9a763642b8ab` on branch `task/research-verification-rules`, worktree `/root/project/w-rv` (verified `git rev-parse HEAD` == the frozen SHA). Read-only; no edits/commits/writes made. Mutation tests were run in-memory (no files written) because the read-only guard blocks shell file-writes even to /tmp.

## VERDICT: PASS

Every item in my scope is correct and reproducible. No REQUIRED defects. Three ADVISORY notes below.

## Required command runs (last lines, from worktree root)

1. `python3 tools/test_research_record_check.py` -> `Ran 29 tests in 3.079s` / `OK`
2. `python3 tools/research_record_check.py --check` -> `PASS: every record is structurally valid and no record claims the Verified label without meeting every condition.` (exit 0; 5 records NB-01..NB-05; each printed status + code_current=True + review_state=none + requested_label=None + the fixed "structural check only; not a professional verification"; none called verified — satisfies S1)
3. `python3 tools/test_directive_reminder.py` -> `Ran 22 tests in 2.095s` / `OK`
4. `python3 tools/test_context_budget_check.py` -> `Ran 20 tests in 0.217s` / `OK`
5. `python3 tools/context_budget_check.py` -> `PASS - automatic context budget within limits; no stale/duplicate/retired regressions.` (eager total ~10652 tok reported with `(no cap: owner D-093-R074)`; handoff/historical/retired/duplicate checks all still evaluated)
6. `python3 tools/modularity_check.py --check` -> exit 0. All `warn` lines are on pre-existing files (services/api connectors, scenario, tools/agent_supervisor); none of the new tools/hook files are flagged.

## Correctness vs README (`docs/research/evidence-records/README.md`)

Verified every required key and vocabulary in `tools/research_record_check.py` against the README Format table and Conditional/Derived/Promotion sections:
- All required keys enforced: schema (==`research_record/v1`, L164), record_id + filename prefix (L166-171), title/revision(int>=1)/last_changed(date) (L172-176), question.{text,property,lot_scope,site_scope,time_scope} (L191-202), evidence[] non-empty with id-uniqueness/kind/authority/title/reference/excerpt/document_date/url(http|https)/page-present/retrieved(date)/saved_copy+sha256 (L229-282), meaning_and_applicability (L284-294), measurement_basis incl. quantity basis enum + double_count_risk (L297-315), conclusion (L205-226), searches (L318-343), implementation incl. code_identity keys==code_paths (L346-388), review incl. reviewer!=producer + professional_review human fields (L391-434), freshness (L437-446), promotion label enum|null (L449-456). Vocabulary sets (L43-64) match the README enumerations exactly.
- Conditional rules all present: conflicting_evidence requires non-empty conflicts (L220-221); interpretation_awaiting_review requires non-empty interpretation (L222-225); saved_copy must exist and sha256 must match with LF normalization (`_validate_saved_copy`, `_sha256_lf` L74-77); every code_paths file must exist (L366-368); searched_not_found/access_blocked require a matching search entry naming missing_item+next_step (L335-343).
- Derived values match README: `code_current` and `review_state` (none/current/stale) computed in `derive` (L473-494); review_state keys on the latest-dated agent review's reviewed_revision==revision AND reviewed_code_identity==current code, exactly as the README states.
- All six promotion conditions present in `promotion_refusals` (L500-555): (1) covering record exists; (2) structurally valid; (3) status not in NON_PROMOTABLE_STATUSES and no open conflicts/conditions; (4) review_state current; (5) named professional review for current revision; (6) OWNER_C1_ANSWERED gate.

Note: README `document_date` is correctly required as a free string (not ISO), matching "as the source states it"; `retrieved` is correctly required as an ISO date. Good distinction.

## Fail-closed behaviour (all reproduced)

- Unreadable/invalid JSON -> `RecordLoadError` -> exit 2 (test_invalid_json_exits_2; reproduced design at L123-124, 574-576).
- Empty records dir -> exit 1, "no *.json ... never passes vacuously" (L577-580; test_empty_records_dir_exits_1).
- Unknown label -> refused (L507-508; test_unknown_label_is_refused).
- Path escape (absolute, drive-letter, `..`) -> refused for both code_paths and saved_copy via shared `_path_escape_error` (L89-97; test_code_path_with_dotdot).
- Missing code_paths / saved_copy files -> structural error (L366-368, 274-276).

## Code drift reported but never fails --check

Confirmed: drift prints a `NOTE` and `code_current=False` but does not add to `errors`, so `--check` still exits 0 (cmd_check L593-595). Reproduced by test_stale_record_refuses_promotion_but_check_still_passes (exit 0, "code_current=False", "NOTE" present). Promotion is still refused for the stale record.

## Verified can never pass while OWNER_C1_ANSWERED is False

`OWNER_C1_ANSWERED = False` is hard-coded (L37). `promotion_refusals` unconditionally appends `C1_REFUSAL` whenever label=="Verified" and the flag is False (L553-554), and `cmd_check` routes every Verified-requesting record's outputs through it (L598-603). Independently proven load-bearing: MUTATION 1 flipped the constant to True in an in-memory copy and `CompleteRecord.test_complete_record_promotion_blocked_only_by_c1` then FAILED (refusals went from `[C1_REFUSAL]` to `[]`).

## Hook docstring guarantees (`.claude/hooks/directive_reminder.py`)

Exercised the hook directly:
- SessionStart(startup/resume) -> research line FIRST (rule path + `sha256 f5d71c755fdb` + procedure + records folder + sanitized/capped handoff first line), then the directive pointer; exit 0.
- UserPromptSubmit -> UNCHANGED: only the one-line substance reminder, no research line; exit 0.
- Missing rule file (CLAUDE_RESEARCH_ROOT pointed at an empty dir) -> visible `WARNING (research-and-verification): ... is missing; the research rule is not loaded.`; exit 0.
- Non-blocking/bounded/inert-data confirmed: output is only `hookSpecificOutput.additionalContext` (never a permissionDecision, never exit 2); rule referenced by digest not body; handoff first line sanitized through the title allow-list and capped at HANDOFF_CAP; research line capped at RESEARCH_CAP. 22/22 tests pass.

## Budget change makes only the eager cap optional

Diff vs main is minimal: `tools/context_budget.json` sets `eager_token_budget: null` (with an explanatory `_comment_eager` citing D-093-R074); `tools/context_budget_check.py` only wraps the eager-cap branch so `None` reports-and-never-fails while an integer keeps the hard cap. Every other check (handoff cap, historical markers, retired sections, duplicate boards) is byte-for-byte unchanged and still fails closed. The new `NullEagerBudget` test class proves this directly: null cap passes with a huge rule, yet handoff-budget, retired-section, duplicate-board and historical-marker violations each still return exit 1.

## CI workflow (two new steps only)

`.github/workflows/ci.yml` diff adds exactly two steps in the control-plane job: "Validate research evidence records (D-093)" (`research_record_check.py --check`) and "Run research evidence-record check tests (D-093)" (`test_research_record_check.py`). No other CI change. Correct and scoped.

## Mutation testing (tests are load-bearing)

Ran three in-memory mutations (source string-replaced, exec'd into a module registered in sys.modules so the real test file exercised the mutant; no files written):
- MUT1 `OWNER_C1_ANSWERED=True` -> `test_complete_record_promotion_blocked_only_by_c1` FAILED.
- MUT2 disable the conflicting_evidence conflicts check -> `test_conflicting_evidence_needs_conflicts` FAILED.
- MUT3 disable the reviewer!=producer check -> `test_reviewer_equals_producer` FAILED.
All three mutants were correctly caught, so the key conditions are genuinely tested.

## Documents describe the code truthfully

- README promotion/derived/conditional text matches the code (verified key-by-key above).
- `docs/RESEARCH_AND_VERIFICATION.md` section 8 ("what is enforced, what remains procedural") is accurate: its enforced list (six parts, fields, vocabulary, sha256 match, code-path existence, reviewer!=producer, human professional review, status rules, drift-prints-not-fails, Verified gated incl. C1) matches the implementation; its procedural list honestly states the check certifies no legal reading. Its two supporting code claims spot-check true: `services/api/app/drawings/report/labels.py` defines `VERIFIED="Verified"` with the description "Not used in this report", and `services/api/app/rules/coverage.py` reaches `verified` only for a published rule with G6 approval attached.

## Modularity

`research_record_check.py` (657 lines) is a single cohesive responsibility (one schema's structural + promotion check), cleanly sectioned (helpers / loading / validation / derived / promotion / CLI) with small focused functions; it is not among the files the modularity check flags, and `--check` exits 0.

## Findings

- F1 (ADVISORY) `tools/research_record_check.py:197` — `question.property` object form accepts any non-empty dict; the README describes "an object with those parts" (address/borough/block/lot) but the sub-keys are not structurally enforced. No promotion impact (property is not a Verified gate); enforcing exact sub-keys would be brittle. No action required.
- F2 (ADVISORY) `tools/test_research_record_check.py` — `saved_copy` path-escape has no dedicated test, though it shares `_path_escape_error` with `code_paths`, which IS tested (test_code_path_with_dotdot). Coverage completeness only.
- F3 (ADVISORY) `tools/research_record_check.py:170` — the filename check uses `name.startswith(record_id)`, so e.g. `NB-1` would also prefix-match `NB-10...`. Harmless for the current NB-01..NB-05 ids; worth a note if ids ever become non-zero-padded.

## S1-S8 note

S1 (research check output), S2 (test refusals), S3 (hook), S4 (budget) are reproduced and PASS within my scope. S5 (rule has no frontmatter) spot-confirmed: the rule file begins `# Research and verification...` with no `---` block and is counted in the eager load, consistent with "unconditional". S6/S7 (disposable-session recovery, G1 source review) and the full per-requirement directive-compliance pass are outside this code review's scope and belong to qa-engineer / data-contract-verifier / directive-compliance-verifier.

END-OF-REPORT

## G5 security (security-reviewer), at 7ec7c5ec

# G5 SECURITY REVIEW — M0-T190 (research-and-verification workflow, directive D-093)

Reviewer role: security-reviewer (independent, read-only). Frozen head verified:
`git -C /root/project/w-rv rev-parse HEAD` = `7ec7c5ec2cee7de6a21b755f004e9a763642b8ab` (branch `task/research-verification-rules`) — matches the brief. All inspection and test runs were done in `/root/project/w-rv` at that head; no file was edited. Scratch-file writes were blocked by the read-only guard, so dynamic tests were run inline with `python3 -c` and by executing the committed test suites (execution is permitted).

## OVERALL VERDICT: PASS (no REQUIRED findings; 3 ADVISORY hardening notes)

Every one of the six security scope items is satisfied at the frozen content identity. Findings below are defense-in-depth only and do not block acceptance.

---

## Item 1 — `.claude/hooks/directive_reminder.py` (SessionStart line): PASS

Reproduced by reading the file at HEAD. The new `_research_line()` (lines 83-114) and SessionStart path (lines 190-207) behave as the docstring claims:
- Prompt-injection containment: the handoff first line is the only free text emitted; it passes through `_sanitize_title` (allow-list `[^A-Za-z0-9 ,.\-()/:+]` stripped, line 48/78-80), is capped at `HANDOFF_CAP=140`, and the whole research line is `_cap(..., RESEARCH_CAP=600)`. Newlines, backticks, quotes, braces/brackets, `#`, `@`, `{}` etc. are all stripped, so markup/escape-based injection and quote-breakout (the value is wrapped in `"..."`, line 112) are contained. The rule file is referenced only by a 12-char sha256 digest (line 99), never its body.
- Non-blocking / exit 0: every path in `main()` returns 0; the whole body is wrapped in `try/except Exception` returning 0 (lines 168-216); file reads use `try/except OSError` (lines 92-98, 101-106); the hook never emits `permissionDecision` and never exits 2. `_emit` only writes `hookSpecificOutput.additionalContext`. The two PreToolUse guards (`agent_dispatch_guard`, `readonly_agent_guard`) are not in the changed-files list — untouched, as claimed.
- `.claude/settings.json` unchanged: `git diff origin/main..HEAD -- .claude/settings.json` is empty (also see item 6). The hook was already registered pre-change.
- Root-override env var: `CLAUDE_RESEARCH_ROOT` (and the pre-existing `CLAUDE_DIRECTIVE_REGISTRY`) can redirect the read root, but only two FIXED relative subpaths are ever read (`.claude/rules/research-and-verification.md` → digest only; `docs/SESSION_HANDOFF.md` → sanitized first line). There is no arbitrary-file-read primitive; output is a digest plus a sanitized, capped, allow-listed line. The env var is a launcher-held trust boundary (the launcher already has filesystem access), so this is not an escalation.

ADVISORY F2 (LOW, item 1): `CLAUDE_RESEARCH_ROOT` lets the session launcher point the two fixed relative reads at any root. Impact is bounded to a 12-char digest and a 140-char allow-listed first line; no arbitrary path, no content beyond those two files. Acceptable as-is; if desired, assert the resolved root stays within `ROOT` for the non-test case.

ADVISORY F3 (LOW, item 1, `_sanitize_title` line 78): the sanitizer blocks markup/control chars but the allow-list still permits plain English. A party with repository write access to `docs/SESSION_HANDOFF.md` could place <=140 chars of benign-looking prose into session context. Mitigated because (a) it is framed as quoted inert DATA, (b) it is capped, and (c) writing the handoff already requires repo-write (the orchestrator maintains it). Residual, consistent with the stated "inert data" design; no change required.

## Item 2 — `tools/research_record_check.py` (path containment / no network / no exec / safe JSON): PASS

- No network, no code execution: the only imports are `argparse, hashlib, json, re, sys, pathlib` (lines 24-29). Grep for `import (os|subprocess|socket|urllib|requests|http)|eval(|exec(|__import__|os.system|os.popen|pickle|yaml.load|object_hook` returns nothing but `Path(__file__).resolve()` and `records_dir.resolve()`. JSON is parsed with plain `json.loads(raw.decode("utf-8"))` (line 122) — no `object_hook`, no deserialization gadget. Records are pure data; nothing from a record is executed or imported.
- Path containment for `saved_copy` and `code_paths`: both go through `_path_escape_error` (lines 89-97). Verified inline:
  - `/etc/passwd` → rejected (absolute);
  - `C:\Windows\win.ini` → rejected (drive-letter absolute);
  - `../../../etc/passwd` and `docs/../../etc/passwd` → rejected (`..` in parts);
  - `data/foo.json`, `docs/./foo.json` → accepted (in-repo);
  - empty / non-string → rejected.
- Empty records dir → exit 1 (never passes vacuously). `--check` exits 2 on unreadable/invalid JSON (`RecordLoadError`).

ADVISORY F1 (LOW, item 2, `_path_escape_error` + `_validate_saved_copy` lines 89-97, 258-281): containment is textual (`PurePosixPath(rel).parts`), not resolved-path-under-root. Two consequences: (a) a backslash form `..\..\etc\passwd` is NOT caught (verified inline → returns None) — harmless on Linux CI (becomes a literal nonexistent filename → "does not exist" error) but traversable on Windows; (b) a committed `saved_copy`/`code_path` that is itself a symlink pointing outside the repo would be followed by `target.is_file()` / `_sha256_lf` (I could not create the symlink to demonstrate because scratch writes are guard-blocked, but the code follows symlinks by construction). Impact is low: the tool emits NO file content — only a pass/fail sha256 comparison — so the worst case is "confirm whether an out-of-repo file matches a stored digest" or an incidental read during CI, and any such record is committed and reviewable. Recommended hardening (non-blocking): resolve the target and assert `Path(root).resolve() in target.resolve().parents` (or `os.path.realpath` prefix check).

## Item 3 — `.github/workflows/ci.yml`: PASS

`git diff origin/main..HEAD -- .github/workflows/ci.yml` is a single 6-line hunk adding exactly two steps:
- `Validate research evidence records (D-093)` → `python3 tools/research_record_check.py --check`
- `Run research evidence-record check tests (D-093)` → `python3 tools/test_research_record_check.py`

Both land inside the existing `control-plane` job (job declared at line 497; the new steps at lines 522-525 sit among the other control-plane steps). Grep of the added (`^+`) lines for `permission|secret|uses:|on:|token|schedule|workflow_|pull_request|push:|env:` returns nothing — no new action, permission, secret, or trigger. Both commands are stdlib-only Python already present in the tree.

## Item 4 — 33 force-added data files under `docs/research/owner-research/2026-10-10-215-16-northern-evidence/data/`: PASS

No `gitleaks`, `trufflehog`, or `detect-secrets` is installed in this environment (verified with `which`), so I ran the repository's fallback approach: manual pattern greps across all 33 files.
- Credential/token scan (`app_token|api_key|authorization|bearer|secret|password|private_key|AKIA|BEGIN RSA/OPENSSH/EC/PGP|aws_access`): the only hits were the case-insensitive substring "ssn" inside ordinary field names/values (`supportsSnapToData`, address strings). No real credentials, keys, tokens, auth/cookie headers (`grep "(authorization|x-app-token|cookie|set-cookie)":` → none).
- Stored URLs: no `app_token`/`$$app_token`/`api_key`/`token=`/`key=` query params in any URL. Distinct hosts referenced are all official/public: `www.nyc.gov`, `propertyinformationportal.nyc.gov`, `nycdcp-dcm-alteration-maps.nyc3.digitaloceanspaces.com` (NYC DCP's public alteration-map bucket).
- PII: no emails; no SSN-format `###-##-####`; the long digit strings (`1764617482382`, `20220316004310 01`, etc.) are epoch-millisecond timestamps and ACRIS/DOB public filing IDs (YYYYMMDD…), not SSNs or card numbers; no `email/phone/birth/dateofbirth/taxid/ein` field keys. The single phone number found, `(212) 386-0009`, is the NYC Board of Standards and Appeals public office line, embedded verbatim in the dataset's own metadata description ("contact the Board's office at (212) 386-0009").
- Content is ArcGIS/Socrata open-data API responses (ESRI field definitions, metadata, index entries). `VERIFICATION.md` states no instruments were read — index entries only — and all 33 files were SHA-256-matched (33/33) against `source-manifest.json`.

Conclusion: the files hold only public official NYC open-data responses; no credentials, tokens, or personal data beyond what the city publishes. (Note for the orchestrator: a proper `gitleaks`/`trufflehog` run was not possible here; findings rest on manual pattern greps.)

## Item 5 — eager token-cap removal (`tools/context_budget.json`, `tools/context_budget_check.py`): PASS

The JSON diff changes only `eager_token_budget: 10000` → `null` and adds an explanatory `_comment_eager`. The code diff is a single hunk: when `budget is None` the eager size is printed with "(no cap: owner D-093-R074)" and no `failures.append`; otherwise the original hard-cap behavior is retained. I read the full `context_budget_check.py` at HEAD and confirmed checks 2-5 are byte-for-byte unchanged and still fail closed via `failures.append(...)` + `return 1`: session-handoff cap (lines 160-170), historical-marker requirement (172-187), retired/superseded-section ban in unconditional rules (189-216), and duplicate current-status board detection (218-243). `python3 tools/context_budget_check.py` → PASS; `python3 tools/test_context_budget_check.py` → 20 tests OK. Only the eager cap was removed; no other check was weakened.

## Item 6 — no access/permission/MCP policy change: PASS

`git diff origin/main..7ec7c5ec2cee7de6a21b755f004e9a763642b8ab -- .claude/settings.json .mcp.json` is empty. Neither file changed. The dispatch/read-only guard hooks are not in the changed-files list either.

---

## Corroborating test runs at the frozen head (execution permitted; reproducible in `/root/project/w-rv`)
- `python3 tools/research_record_check.py --check` → exit 0, PASS; 5 records (NB-01..NB-05) all structurally valid, none requests the Verified label (and Verified is additionally gated closed by `OWNER_C1_ANSWERED = False`).
- `python3 tools/test_research_record_check.py` → Ran 29 tests, OK.
- `python3 tools/test_directive_reminder.py` → Ran 22 tests, OK.
- `python3 tools/test_context_budget_check.py` → Ran 20 tests, OK.
- `python3 tools/context_budget_check.py` → PASS.

## Scope note
My assignment is the six security items above. Independent re-derivation of every D-093 requirement ID against source (the in-regime directive-compliance pass recorded in `project-control/directives/D-093-research-and-verification-workflow/verification.json`) is the `directive-compliance-verifier`'s separate pass (producer != verifier) and is outside this security review.

## Recommendations (all ADVISORY, none blocking)
1. F1: add a resolved-path-under-root assertion (and/or reject symlinked targets) in `_path_escape_error`/`_validate_saved_copy` to close Windows-backslash and symlink traversal; impact today is low because no content is emitted and CI is Linux.
2. F2: optionally constrain `CLAUDE_RESEARCH_ROOT` to stay within `ROOT` outside tests.
3. F3: no change required; the allow-list + cap + data-framing is an appropriate posture given the handoff is repo-write-controlled.
4. Orchestrator: record that no dedicated secret scanner was available; the item-4 clearance rests on manual pattern greps of all 33 files.

VERDICT: PASS.

END-OF-REPORT

## G4 QA (qa-engineer), at 6f6d3a90

# Gate Report — G4 QA review of M0-T190 (owner directive D-093)

- Gate ID: G4
- Task ID: M0-T190
- Reviewer: qa-engineer (independent, read-only)
- Producer: orchestrator (+ one backend-engineer builder for tool/hook/tests/CI)
- Result: **PASS** (acceptance scenarios S1–S8 all PASS; owner "Evidence check" R069 proof reproduced; verification-sessions file backed by real transcripts). 0 REQUIRED defects; 3 ADVISORY findings.
- Clean environment/worktree used: reviewed at frozen head on worktree `/root/project/w-rv`. Verified `git -C /root/project/w-rv rev-parse HEAD` = `6f6d3a903512af14315322e6ac9a1e1182c65991` (matches the brief). The R069 proof was built in a scratch copy under `/tmp/claude-0/rv-review-qa/` (never the worktree); the scratch copy of `research_record_check.py` is LF-sha256-identical to the frozen tool.

## Documented test commands (run from `/root/project/w-rv`, last lines)
1. `python3 tools/research_record_check.py --check` → `PASS: every record is structurally valid and no record claims the Verified label without meeting every condition.` EXIT 0. Five records NB-01..NB-05 each printed with status / code_current=True / review_state=current / requested_label=None and the fixed disclaimer "structural check only; not a professional verification".
2. `python3 tools/test_research_record_check.py` → `Ran 29 tests ... OK` EXIT 0.
3. `python3 tools/test_directive_reminder.py` → `Ran 22 tests ... OK` EXIT 0.
4. `python3 tools/test_context_budget_check.py` → `Ran 20 tests ... OK` EXIT 0.
5. `python3 tools/context_budget_check.py` → `PASS - automatic context budget within limits; no stale/duplicate/retired regressions.` EXIT 0 (eager total ~10652 tok, "no cap: owner D-093-R074"; handoff ~1347 of 8000).
6. `python3 tools/validate_directive_compliance.py --check` → EXIT 0.
7. `python3 tools/modularity_check.py --check` → `selected 788 files; failures 0; warnings 31` EXIT 0 (all 31 warnings are pre-existing services/api & tools/agent_supervisor files, none in this task's scope).

## Acceptance scenarios
- **S1 PASS** — `--check` exits 0, prints each record's research status and whether its latest agent review applies to current code (code_current / review_state), and calls none professionally verified (disclaimer printed on every line).
- **S2 PASS** — 29 tests OK. Test names cover the required cases (incomplete refused promotion; stale refuses promotion but check still passes; reviewer==producer refused; absent-output/no-record; complete passes structural check reported as structurally complete). Independently corroborated by my R069 proof (below).
- **S3 PASS** — 22 tests OK **and** independently reproduced by running the hook directly: SessionStart sources startup/resume/compact/clear each emit one bounded research line naming the rule `[sha256 f5d71c755fdb]`, the procedure, `docs/research/evidence-records/`, and the handoff first line ("SESSION HANDOFF seq 156 ..."); a missing rule file → `WARNING (research-and-verification): ... is missing; the research rule is not loaded.` with EXIT 0; UserPromptSubmit carries no research line (unchanged); hook exit 0 (never blocks) in every case.
- **S4 PASS** — 20 tests OK + live run PASS. `tools/context_budget.json` has `eager_token_budget: null` (cap removed, comment cites R074 verbatim) while `handoff_token_budget: 8000` is preserved; tests `null_eager_still_enforces_{duplicate_board,handoff_budget,historical_marker,retired_section}` prove the other checks still fail closed.
- **S5 PASS (advisory F1)** — the installed `.claude/rules/research-and-verification.md` has **no frontmatter** (0 `---` lines, starts with the heading) and its 12 bullets differ from the brief's section-2 rule **only in added parenthetical path references** (word-diff reproduced). See F1 for the one non-path-reference addition.
- **S6 PASS** — `project-control/reports/M0-T190-verification-sessions.md` records disposable fresh/resume/compact(+after-compaction)/clear/fork sessions with prompts and results, each recovering the policy/handoff/records without the conversation; the transcript's loaded-instruction list is quoted; untested session types are named honestly (section 6). Independently verified (below).
- **S7 PASS** — the five NB records carry independent `data-contract-verifier` agent reviews (distinct from producer `orchestrator`) with findings (NB-01 rev2 has a delta review at reviewed_revision 2); `VERIFICATION.md` documents the orchestrator's re-check of decisive official sources (printed tax maps, MapPLUTO 26v2, ACRIS index, DOB jobs, ZR 12-10 / 23-344(b)); no report numbers changed (S8). The substantive "opened sources / worked the special-density example before code" attestation is the G1/data-contract-verifier gate's recorded verdict (present in the records), outside the QA re-derivation scope.
- **S8 PASS** — `git diff --name-only origin/main..6f6d3a90` shows **no file under services/, apps/, or packages/** and no `.claude/settings` or `.claude/agents` change. The only changes are the named task outputs plus control-plane ledger files (directives/, gates/M0-T190-G0, reports/, state.json, task JSON) expected for a governance task.

## Owner "Evidence check" proof (R069) — reproduced in `/tmp/claude-0/rv-review-qa/` (scratch copy of the tool + a records dir laid out as docs/research/evidence-records so root derives to the scratch root)
(a) **Deliberately incomplete record asking for `Verified`** → `--check` EXIT 1 with named reasons:
```
  QA-INCOMPLETE: key 'conclusion.observed_facts' must be a non-empty list.
  QA-INCOMPLETE: key 'evidence' must be a non-empty list.
  QA-INCOMPLETE: key 'meaning_and_applicability.provisions_read' must be a non-empty list.
  QA-INCOMPLETE: key 'meaning_and_applicability.reading' is required and must be a non-empty string.
  QA-INCOMPLETE: Verified promotion of 'demo.incomplete_output' refused: record ... is not structurally valid (4 issue(s)).
  QA-INCOMPLETE: Verified promotion of 'demo.incomplete_output' refused: owner question C1 ... is open; nothing is labelled Verified
```
(b) **Properly complete record** (current agent review: reviewer≠producer, reviewed_revision==revision, reviewed_code_identity==current code sha; named professional review for the current revision; status answered_from_primary_source, no conflicts/conditions; requested_label Conditional):
- `--check` → `PASS` EXIT 0; the record line reads `status=answered_from_primary_source code_current=True review_state=current requested_label=Conditional - structural check only; not a professional verification` (passes the structural check, **not** called professionally verified).
- `python3 tools/research_record_check.py --promotion demo.complete_output --records-dir ...` (defaults to label Verified) →
```
REFUSED to label 'demo.complete_output' as Verified (structural check only; not a professional verification):
  owner question C1 (what must be true before a result is labelled Verified) is open; nothing is labelled Verified
```
EXIT 1. The refusal is **only** owner question C1 (every other condition satisfied — otherwise extra lines would appear), and the output contains the exact words "not a professional verification". This is precisely the owner's R069 proof; it also fills the gap the verification-sessions file (section 5) explicitly delegated to "the G4 review."

## Verification-sessions file check (`project-control/reports/M0-T190-verification-sessions.md`)
- Each claimed disposable session (fresh, resume, compaction, after-compaction, clear, fork) is backed by prompt+result text in the file and by the raw outputs in `/root/project/lanes-runtime/owner-docs/session-2026-10-11a/verify-candidate/` (p1-fresh.json … p5-fork.json, transcript-extract.txt, sessionstart-sources.log). The fresh-session result I spot-read from `p1-fresh.json` is byte-for-byte what the file quotes.
- The loaded-instruction list it quotes (CLAUDE.md + expansion-hold + CODING_RULES + research-and-verification + PROGRAM_KNOWLEDGE + AutoMem memory index) matches `transcript-extract.txt` exactly.
- I independently opened the cited transcript `~/.claude/projects/-root-project-w-rv/9cbe059a-...jsonl`: it exists, contains the SessionStart hook research line with digest `f5d71c755fdb`, the full CLAUDE.md instruction block, and the compact_boundary. All five cited session ids exist as transcripts.
- The hook digest `f5d71c755fdb` equals the LF-sha256 of the frozen rule file (`f5d71c755fdba1ca...`), and `git show` confirms the rule is byte-identical at the run-head `7ec7c5ec` and the frozen head `6f6d3a90` — so the session loaded exactly the frozen rule.
- Untested session types are named honestly (interactive terminal, cloud/remote, another machine/Windows, another account), and resume/fork hook-line *delivery* is marked "not proven" in print mode. Honest, within policy.

## Modularity (handwritten source changed)
`modularity_check --check` passes (failures 0). `tools/research_record_check.py` is 556 SLOC (under the 600 warn threshold), split into focused `_validate_*` helpers — cohesive, not a dumping ground; the builder flagged the ~350-line soft-guidance overage explicitly. No boundary/coupling concerns for a check tool + hook + tests.

## Findings
- **F1 (ADVISORY, S5) — `.claude/rules/research-and-verification.md:3`**: the installed rule adds one line beyond path references — `"Owner directive D-093 (2026-10-11). Always loaded: no `paths:` frontmatter. Only the path references are adapted from the owner's text."` This is a provenance/authority note, not a path reference, so it is a minor deviation from S5's literal "differs only in path references." It is consistent with CLAUDE.md principle 2 (provenance) and does not alter the rule's twelve substantive bullets. Also: the producer report (Part 1) *asserts* "the rule (only path references adapted)" but does not paste the literal word-diff that S5's parenthetical references; I reproduced the word-diff myself and it confirms the claim apart from this one line. Not blocking.
- **F2 (ADVISORY) — verification-sessions file, instruction char-counts**: the file quotes Claude Code's listing counts (e.g. rule "2452 chars", CLAUDE.md "14561 chars"), which are off-by-one from the frozen files (2453 / 14562 chars). This is a Claude Code listing quirk, not a content change — the load-bearing digest `f5d71c755fdb` matches the frozen rule exactly and the file states its earlier candidate head `7ec7c5ec` in its header. Immaterial.
- **F3 (NOTE, integration) — producer report Part 2**: the builder flagged that the commit trailer used `Co-Authored-By: Claude Opus 5.5` while the environment attribution is Opus 4.8. This is a commit-message cosmetic for the orchestrator to reconcile on integration; outside the acceptance-scenario scope and not a code/behavior defect.

## Reviewer conclusion
G4 QA scope (acceptance scenarios S1–S8, the owner's R069 "Evidence check" proof, and the verification-sessions file) is satisfied. All seven documented test commands pass; the owner's incomplete-vs-complete promotion proof reproduces exactly (complete record passes the structural check without being called professionally verified, and Verified is refused only by owner question C1 with "not a professional verification" in the output); the disposable-session claims are backed by real, independently-opened transcripts whose loaded rule is byte-identical to the frozen rule. No reproducible defect found. Verdict: **PASS** with 3 advisory notes (F1–F3). Full 73-requirement directive re-derivation remains the directive-compliance-verifier's pass (verification.json present).

Scratch evidence: `/tmp/claude-0/rv-review-qa/` (tool copy, brief-rule.md, installed-rule.md, QA-COMPLETE-demo.json and the earlier QA-INCOMPLETE-demo.json).

END-OF-REPORT
