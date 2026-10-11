# M0-T193 producer report (orchestrator; governance task)

Task: design contract revision for D-094 and the quick-resume routine after a planned handoff (D-094 R109-R113).
Producer: the orchestrator (session 0dfe2ecc, claude-opus-5-5). Contract base `aac892fc` on `task/wave24-report-v3`.
Material commits: `ea689ea0` (the six files) and the commit carrying this report (it was left as the placeholder in
`ea689ea0` by a tool slip and is added on its own; no other file changes in it).

## What changed

1. **`docs/design/ARCHITECT_PRESENTATION_CONTRACT.md`**, above the BEGIN ADOPTED BRIEF marker only:
   - New section "Change 2026-10-11: the report's next pass (D-094 source-001, source-002 and source-003)": the six
     R066 principles; the fixed wordings quoted once (the distinction line, the R029 allowance phrase, the two zone
     labels and the caption); page 1's four kinds of content and its named furniture, including the zoning-lot
     sentence that names the register's index entry, never the instrument; the 1.4.0 rear-yard open-check wording
     (23-344(b) and (c)(3) not yet checked, no conclusion); page 2 (one locator plus a large dimensioned close-up);
     the supersession of the 2026-10-10 block close-up, the "among its surroundings" composition and the two
     scope-list parts by R014/R074, with the kept parts named; the not-placed sentence (R939) kept for the unplaced
     state and printed once; page 3 (comparison first, three measures); page 4 (section, reconciled schedule,
     not-checked list); the two-zone area illustration (R087-R098; 60 % apartment area with its basis); the appendix
     (types 5 and 6 under one heading); one print type scale; the wording additions and the plain-word labels of the
     nine measurement bases; the checks (text budget, repeats, H0-H3 mapped to the section 12 UX ids, inside the
     existing gates).
   - The page-type table rows 1-6 rewritten to the change (row 2 now says "city map outline", not "tax-map
     outline", per G-10); the heading notes "changed 2026-10-11, D-094".
   - Marks on the 2026-10-10 location change: superseded parts (the "Where is the lot?" sheet's second map and
     composition; the two scope-list lines) and the amended not-placed sentence.
   - The 2026-10-10 "Type" paragraph marked superseded, with its old values kept in brackets.
   - The forbidden-words list gains "buildable", "achievable", "can be built".
2. **`CLAUDE.md`**: the routing row for the contract names the change of 2026-10-11; the start-of-session routine says
   that after a planned handoff the session reads the handoff and every file it names and starts its next action with
   no reconcile checks, tests or READY TO RESUME round, and that the five steps apply after a crash or forced stop.
   The owner-guidance block is untouched.
3. **`.claude/rules/drawings-report-presentation.md`** and **`.claude/rules/frontend-web.md`**: pointers to the change
   of 2026-10-11.
4. **`.claude/rules/PROGRAM_KNOWLEDGE.md`**: the D-070 line ("the successor only launches", with the R109-R113 note);
   a new pointer "read CI green at the exact head before every gate, accept, merge and handoff (D-090 R639)".
5. **`.claude/skills/session-handoff/SKILL.md`** section F: the successor prompt keeps its information but carries no
   resume checks and no READY TO RESUME round after a planned handoff; the checks remain for a handoff written after
   a crash or forced stop.

## Decisions taken in this task (orchestrator)

- **The illustration's one percentage: 60 % apartment area.** Basis: the low end of the owner's existing 60-75 %
  share assumption (D-090 R540; `services/api/app/scenario/three_answers/preliminary_apartment_estimate.py`
  `share_low = 0.60`), so the drawn apartment area never exceeds what the estimate's low end uses. It is an
  assumption the owner can change; the next owner update names it.
- **Label and caption text without the closing full stops.** The owner's sentences end with a full stop inside the
  closing quotation mark (American punctuation); the full stop belongs to the sentence, not to the label or caption.
  The wording is otherwise byte-equal to R089 and R090, including the em dash.
- **The distinction line is number-free** ("The ceiling is a conditional zoning limit; the estimate is an unvalidated
  apartment-yield range; neither is a demonstrated layout.") so one token serves every property; the figures come
  from the result beside it. It carries no double quote or backslash (the token generator refuses both; round-3
  critic C2).
- **Plain-word basis labels:** law "zoning law"; deed "deed"; survey "survey"; printed_tax_map "printed tax map";
  approved_plan "approved plan"; filing_attribute "building filing"; administrative_record "city record" (a lot area
  on it reads "recorded lot area"); gis "city map outline" (drawings: "map outline"); derived "worked from other
  values".

## Self-checks (scenarios)

| Scenario | Result | Evidence |
|---|---|---|
| S1 six principles | present | the change's "Six principles (R066)" list, each with rows |
| S2 rows 1-6 rewritten | done | the table; page 1's furniture in the change text; six types remain; types 5 and 6 labelled "Appendix: ..." |
| S3 Y8 kept, once; stack schematic | done | "The not-placed sentence (R939)" paragraph; row 4; the amended 2026-10-10 bullet |
| S4 supersession recorded | done | "Supersession (R014, R074; 2026-10-11)" paragraph; marks on the 2026-10-10 lines |
| S5 one type scale | done | "Print type scale" paragraph; the "Type" paragraph marked superseded |
| S6 budget and repeat check | done | "Checks" paragraph (2,993 hard, 2,713 target, page 1 at most 220; 3 sentences / 7 printings) |
| S7 brief byte-identical below the marker | PASS | sha256 of the text from the marker down `225354013f46a1b2...` before and after |
| S8 validator | exit 0 | `python3 tools/validate_directive_compliance.py --check`, direct exit code |
| S9 fixed wordings once, no `"` or `\` inside | PASS | counts above the marker: distinction line 1, allowance phrase 1, each basis label 1 |
| S10 item 9 | PASS | labels and caption 1 each; "60 % apartment area" 1; the bar-or-zones rule, the G-14 statement, the R093 prohibitions present; "wait on H1" 0 |
| S11 quick resume | done | CLAUDE.md routine, SKILL.md section F, PROGRAM_KNOWLEDGE D-070 line and the R639 pointer |
| S12 context budget | exit 0 | `python3 tools/context_budget_check.py`: eager total 43,962 B, ~10,933 tokens (no cap) |

## Not claimed

The rows bound to this task are verified as recorded rules in the canonical contract and the instruction files, not
as built pages; the page tasks (M5-T165, M5-T166, M5-T169, M5-T171 to M5-T174) build them. Nothing is labelled
Verified. No legal reading was made here beyond the wording the evidence records already carry (NB-01, NB-03, NB-04,
NB-05 read for wording only).
