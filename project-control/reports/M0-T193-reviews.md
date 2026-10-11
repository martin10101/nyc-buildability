# M0-T193 reviews (every return kept unchanged)

- G3 product-design-director (design share): PASS at a3690424 (3 advisories; A1, A2 applied as [ORCH-CORRECTED] in 1dac23f2; A3 left: scenario wording); delta attestation: PASS carries to 1dac23f2.
- G3 code-reviewer (instruction-files share): PASS at a3690424 (1 advisory, applied in 1dac23f2); delta attestation: PASS carries to 1dac23f2 (below-marker sha256 and the owner-guidance block byte-identical).

Every reviewer is an AI agent; none is a human or professional review.

## G3-design

G3 DESIGN REVIEW (product-design-director) — M0-T193, contract change at a36904243 (`/root/project/w-wave20`, task/wave24-report-v3).

VERDICT: PASS for G3. No REQUIRED findings; 3 ADVISORY. Acceptance may proceed on my lens; S7 and S8/S11/S12 remain for the shell-capable reviewers (see limitations).

WHAT I CHECKED (design lens):
Read the packet + scenarios, producer report, the whole contract, the bound D-094 rows (R009/R010/R012/R014/R018-R021/R025-R029/R047-R054/R066/R071/R074/R078/R081/R087-R098/R109-R113), source-003-amendment, and evidence records NB-01/03/04/05.

- S1 PASS. The six R066 principles (contract lines 30-37) carry R066's six items verbatim in substance, each tagged to its rows.
- S2 PASS. Page-type table rows 1-6 all tagged "(change 2026-10-11)"; types 5 and 6 both titled "Appendix: …" under one Appendix heading; six types remain; eleven options preserved (row 3, R007/R084).
- S3 PASS. The not-placed sentence (R939) kept word-for-word, prints once on the scenario sheet, site drawing takes a "No building placed" legend (lines 20, 60, row 4); floor stack "schematic, not to scale" (line 64).
- S4 PASS. Supersession (line 58) names R014/R074 and 2026-10-11, the superseded parts (second co-equal map, "among its surroundings", the two scope-list lines) and the kept parts (no-photo/E1, one-outline check, lot-only fallback, R939).
- S5 PASS. Print scale (line 82) = title 22-23 / headline 28-32 / headings 14 / body 10.5 / table ≥9.5 / drawing labels ≥8.5 / footer 8.5-9 / 14 mm A4; every value lies in the intersection of brief §5 (printed col) and R047, and the old "Type" paragraph is marked superseded with bracketed old values (line 98).
- S6 PASS. Checks (lines 86-90): budget 2,993 hard / 2,713 target / page-1 ≤220, per-section HTML tests; repeats 3 sentences/7 printings→0; H0-H3 with H2 mapped to §12 UX-01/02/05/07/10/11/12/13/14; all inside existing gates, no new framework (R064).
- S9 PASS. Distinction line (line 41) and allowance phrase (line 42) each quoted once; nine basis labels defined once (line 84); none contains a double quote or backslash. (Labels are also *applied* in examples — intended per "used wherever a figure names its basis"; token definitions are single-source via presentation-tokens.json, so no drift. See ADVISORY-3.)
- S10 PASS. Two-zone section (lines 66-78) matches R087-R098: exact labels/caption without the owner's closing full stops, em dash kept; one percentage "60 % apartment area" with its basis (share_low 0.60, D-090 R540); bar-until-fitted rule (R094); the G-14 statement "plate = zoning floor area per storey; no gross-up, exclusions or wall-thickness conversion worked"; R093 prohibitions; method in appendix; website=PDF; rendered check. "wait on H1" appears nowhere (grep confirmed).

PROVENANCE / HONESTY (no overstatement vs the records):
- NB-01: the page-1 zoning-lot example "the city's register lists a zoning lot description recorded 2022-02-08 against lots 1 and 70" names the INDEX entry (ACRIS ZONE 2022020201551002, recorded 2022-02-08, indexed vs lots 1&70), not the instrument; faithful to NB-01 (zoning_lot_unconfirmed) and R029/R030.
- NB-03: the rear-yard "open check" names 23-344(b) and (c)(3) as "not yet checked, draws no conclusion" — this is MORE conservative than NB-03's conditional draft and matches the result's 1.4.0 state (rule encodes (a) only) and R037/R079. No overstatement.
- NB-04: page-2 examples "10,075 sq ft recorded lot area" (administrative_record) and "103.88 ft, city map outline, not surveyed" (gis 103.87921) are source-exact; recorded-for-calc / outline-for-display kept.
- NB-05: the contract makes NO special-density/Manhattan-Core claim (grep clean), so no NB-05 overstatement; those rows (R033/R034) are M5-T157's, not bound here.
Decisions recorded with basis: 60 % (producer decision + line 70), labels without closing full stops (American-punctuation rationale), number-free distinction line (one-token rationale; does NOT weaken R078 since figures sit beside it per page-1 item 3), plain-word basis labels (defined).

ADVISORY (non-blocking):
1. Appendix/evidence spec (line 80; table row 6) states "readable source titles" + worked arithmetic but does not restate R026's "actual source identifiers and DATES (not 'City records')". Covered by the still-standing 2026-10-10 notes rule (line 24, "Sources: <title> (edited <date>)") and R028, and re-bound to build task M5-T164 — recommend M5-T164 carry the source-date requirement explicitly.
2. The floor-stack label is "schematic, not to scale" (comma); R021's brief text used "schematic / not to scale" (slash). Meaning identical; flagging only for label-token exactness at build time.
3. "Each appear once" (S9) is met as single token *definitions*; the same words recur as intended applications in examples — worth a one-line clarifying note in the contract if desired, but not a defect.

WHAT I COULD NOT CHECK:
- S7 (sha256 of everything from the BEGIN ADOPTED BRIEF marker, line 117, down, before/after): I have no shell/hash/diff tool in this read-only session, so I could not run the diff aac892fc→a36904243 or recompute the digest. STRUCTURAL evidence supports PASS — every 2026-10-11 edit is above line 117 and the adopted brief (118-542) reads intact/byte-consistent — but byte-identity must be confirmed by the code-reviewer/DCV (producer reports sha256 225354013f…).
- S8 (validate_directive_compliance.py), S11 (CLAUDE.md/SKILL.md/PROGRAM_KNOWLEDGE quick-resume), S12 (context_budget_check.py): outside my design lens and tool reach; defer to code-reviewer and directive-compliance-verifier.

END-OF-REPORT

M0-T193 G3 delta attestation (design share) — CONFIRMED; PASS carries to 1dac23f2e.

A1 (line 80): "the inputs with their basis in plain words and their actual source identifiers and dates (never just \"City records\"; R026) [ORCH-CORRECTED per M0-T193 G3 design A1]" — carries R026 exactly (actual source identifiers AND dates, not "City records"); no weakening, no addition.

A2 (line 64): floor stack labelled "schematic, not to scale" (the fixed label for R021's "schematic / not to scale") [ORCH-CORRECTED per M0-T193 G3 design A2] — fixes the canonical label and cites R021; no weakening, no addition.

Both sit at the A1/A2 locations I flagged; surrounding design content reads unchanged from a36904243. I could not run a full diff (read-only, no shell), so I rely on re-reading the edited sentences and their sections; byte-identity below the marker is the code reviewer's check. My G3 design PASS carries to 1dac23f2e.

END-OF-REPORT

## G3-code

## G3 Gate Report — M0-T193 (code-reviewer; INSTRUCTION-FILES share)

Reviewed worktree /root/project/w-wave20 at pinned material head a36904243 (worktree HEAD is 2098b0431; its one later commit touches only M0-T194's report, not any M0-T193 file — confirmed by the diff stat, M0-T193's seven files are unchanged at HEAD).

### VERDICT: PASS (my share)

### What I checked (reproducible)
1. **CLAUDE.md start-of-session routine** (lines 83-93 at head): the new preamble says exactly that — after a planned handoff read the handoff + every file it names, start its exact next action, "no reconcile checks, tests or READY TO RESUME round (owner, D-094 R109-R113)". The five existing numbered steps are PRESERVED verbatim and now sit under "After a crash or forced stop:". "Do not begin untracked work" (step 5) and the /replan-project trigger (step 4) are intact. This matches R110/R112/R113 (keep all handoff info; drop only between-session checks; checks remain for crash/forced stop).
2. **Owner-guidance block byte-identical**: `sed -n '39,/## Source of truth/p'` sha256 = `5b6b534f…` identical base↔head; permanent-principles block (lines 1-38) sha256 = `22bc9724…` identical. No owner text changed.
3. **Routing-table pointer** (CLAUDE.md line 113): updated to "report page types as changed 2026-10-11 (D-094: page 1 rebuilt, one locator plus a dimensioned close-up, the two-zone area illustration, one print type scale)" — accurate reference to the contract change (design content itself is the product-design reviewer's share).
4. **SKILL.md section F** (lines 106-118): successor prompt keeps its information, drops only resume checks + READY TO RESUME after a planned handoff, and keeps verify/reconcile/READY-TO-RESUME-or-BLOCKED after a crash/forced stop. Diff touched ONLY section F. No contradiction with section C (handoff holds full info — consistent with R112) or section D (writer-side HANDOFF READY/BLOCKED validation of the handoff just written — a different activity from the successor's between-session checks R113 drops).
5. **PROGRAM_KNOWLEDGE.md** (lines 138-143): D-070 line correctly changed "only verifies+launches" → "only launches (no resume checks, D-094 R109-R113; same full handoff and prompt); crash/forced turnover = … the only case for the reconcile checks." New R639 pointer accurate: R639 source text explicitly covers "before a gate or an acceptance is recorded and before a merge"; adding "handoff" matches the task's own paraphrase and existing memory. No contradiction with other pointers.
6. **Two `.claude/rules` pointer edits**: drawings-report-presentation.md names "change of 2026-10-11, D-094" and "rewritten 2026-10-11"; frontend-web.md adds "its change of 2026-10-11, D-094, governs; website and PDF show the same figures and the same area illustration" — both accurate and consistent with the contract (website = PDF).
7. **No lingering instruction** across .claude/, CLAUDE.md, SESSION_HANDOFF.md tells a session to run resume checks after a *planned* handoff. The only remaining "Reconcile" (CLAUDE.md step 3) and READY-TO-RESUME (SKILL.md F) references are now explicitly scoped to the crash/forced-stop branch. Routing row for /replan-project ("on resume") is a general skill pointer, condition-gated, not a planned-handoff obligation.
8. **Contract below BEGIN ADOPTED BRIEF (line 51)**: sha256 from the marker down = `225354013f46a1b2…` identical base↔head (matches producer claim). S7 confirmed.

### Tool runs (direct exit codes, from /root/project/w-wave20)
- `python3 tools/validate_directive_compliance.py --check` → exit 0 (S8).
- `python3 tools/context_budget_check.py` → "PASS", exit 0; eager total 43962B ~10933 tok (S12; matches producer).

### Findings
- **ADVISORY (A1)**: CLAUDE.md lines 90-93 — "Do not begin untracked work" and the /replan-project trigger now live only under the "After a crash or forced stop:" list; after a planned handoff only "start its exact next action" applies. This is consistent with R110/R113 (jump straight in) and the next action is tracked via the handoff, so not a defect — noted for orchestrator awareness.
- No REQUIRED findings.

### Research & verification (D-093)
I agree: this change edits instruction/design-contract rules and the resume routine only; it changes no property fact, rule applicability, calculation input, result, or certainty label. The 60% illustration figure is cited to existing D-090 R540 (share_low=0.60) and is a drawing assumption, not a new calculation result.

### Could not check
Nothing blocked within my share. Design content of the contract change (page types, zone labels, print scale) is the product-design reviewer's share, per the task split; the directive-to-evidence map for the full D-094 requirement list is the directive-compliance-verifier's pass.

END-OF-REPORT

## G3 Delta Attestation — M0-T193 instruction-files share (a36904243 → 1dac23f2e)

Confirmed (read-only, worktree /root/project/w-wave20):

1. **CLAUDE.md**: the ONLY change in my share is the planned-handoff sentence (line 86), adding "; do not begin untracked work" after "R109-R113)". This directly applies my advisory A1 — the untracked-work guardrail now also covers the planned-handoff path. Owner-guidance block sha256 = `5b6b534f…`, byte-identical to a36904243. No other change to CLAUDE.md, PROGRAM_KNOWLEDGE.md, SKILL.md, or the two `.claude/rules` pointers.

2. **Contract**: changes are above the marker only; text from BEGIN ADOPTED BRIEF down sha256 = `225354013f46a1b2…`, byte-identical to a36904243 (and to base aac892fc).

3. **Verdict carries**: my G3 PASS carries forward to 1dac23f2e for the instruction-files share; A1 is now resolved and no finding remains.

END-OF-REPORT
